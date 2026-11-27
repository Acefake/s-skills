#!/usr/bin/env python3
"""Claude Code PreToolUse hook (Bash): ask before git commands the wukong rules forbid by default.

Covers skipping commit hooks, force pushes, ``reset --hard`` and ``git clean``.
It answers "ask", never "deny", so the user can still approve a command they
asked for. Anything it cannot parse exits silently without a decision.
"""
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

VALUE_OPTIONS = {"-c", "-C", "--git-dir", "--work-tree", "--namespace", "--exec-path"}
WRAPPERS = {"sudo", "env", "command", "time", "nohup", "exec", "builtin"}
ASSIGNMENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=")
HEREDOC = re.compile(r"<<-?\s*['\"]?([A-Za-z_][A-Za-z0-9_]*)['\"]?")
SHORT_OPTION = re.compile(r"-[^-\s]\S*")

# Short letters that take a value (the rest of the cluster, or the next argument),
# letters whose value is always attached, and long options that take the next argument.
VALUE_SHORT = {"commit": "mFCct", "push": "o", "clean": "e"}
ATTACHED_SHORT = {"commit": "Su"}
VALUE_LONG = {
    "commit": {"--message", "--file", "--reuse-message", "--reedit-message", "--template", "--author", "--date", "--cleanup", "--fixup", "--squash"},
    "push": {"--push-option", "--receive-pack", "--exec", "--repo"},
    "clean": {"--exclude"},
}

REASONS = {
    "no-verify": "commit-pr：不要用 --no-verify 跳过提交钩子，除非用户明确要求。",
    "force-push": "run-plan 执行边界：强制推送需要明确授权，覆盖具体分支和目标。",
    "reset-hard": "run-plan 执行边界：不以 reset --hard 作为同步或恢复手段，会丢掉未提交的改动。",
    "clean": "run-plan 执行边界：不以 git clean 作为清理手段，会删掉未跟踪文件。",
    "sensitive-file": "commit-pr：正在暂存疑似敏感文件（如 .env、密钥或凭据），请确认后再继续。",
}

SENSITIVE_NAMES = {".env", "id_rsa", "id_ed25519", "id_dsa", "id_ecdsa", "credentials.json", "secrets.json"}
SENSITIVE_EXTS = (".pem", ".key", ".p12", ".pfx", ".jks")
SAFE_ENV_SUFFIXES = (".example", ".sample", ".template", ".dist")
SECRET_PATTERNS = (
    ("私钥", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("AWS Access Key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GitHub Token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b")),
    ("API Key", re.compile(r"\b(?:sk-(?:proj-|ant-)?[A-Za-z0-9_-]{20,}|AIza[0-9A-Za-z_-]{35})\b")),
)
MAX_STAGED_FILE_BYTES = 5 * 1024 * 1024
MAX_DIFF_SCAN_BYTES = 512 * 1024


def strip_heredocs(command):
    """Drop heredoc bodies so their text is never read as commands."""
    kept, terminator = [], None
    for line in command.split("\n"):
        if terminator is not None:
            if line.strip() == terminator:
                terminator = None
            continue
        kept.append(line)
        found = HEREDOC.search(line)
        if found:
            terminator = found.group(1)
    return "\n".join(kept)


def split_segments(command):
    """Split a shell command line into token lists, one per simple command."""
    lexer = shlex.shlex(strip_heredocs(command).replace("\n", ";"), posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    segments, current = [], []
    for token in lexer:
        if token and set(token) <= set("&|;()"):
            if current:
                segments.append(current)
            current = []
        else:
            current.append(token)
    if current:
        segments.append(current)
    return segments


def is_sensitive_path(path):
    """Return True when a filename looks like a secret/env/key file."""
    name = path.replace("\\", "/").rsplit("/", 1)[-1].lower()
    if name in SENSITIVE_NAMES:
        return True
    if name.startswith(".env.") and not name.endswith(SAFE_ENV_SUFFIXES):
        return True
    return name.endswith(SENSITIVE_EXTS)


def git_call_with_dir(tokens):
    """Return (subcommand, args, repo_dir) when the segment runs git, else None."""
    index = 0
    while index < len(tokens) and (ASSIGNMENT.match(tokens[index]) or tokens[index] in WRAPPERS):
        index += 1
    if index < len(tokens) and tokens[index] == "timeout":
        index += 2
    if index >= len(tokens) or tokens[index].replace("\\", "/").rsplit("/", 1)[-1] not in ("git", "git.exe"):
        return None
    args, position, repo_dir = tokens[index + 1:], 0, None
    while position < len(args) and args[position].startswith("-"):
        if args[position] == "-C" and position + 1 < len(args):
            repo_dir = args[position + 1]
        position += 2 if args[position] in VALUE_OPTIONS else 1
    if position >= len(args):
        return None
    return args[position], args[position + 1:], repo_dir


def git_call(tokens):
    """Return (subcommand, args) when the segment itself runs git, else None."""
    parsed = git_call_with_dir(tokens)
    return (parsed[0], parsed[1]) if parsed else None


def parse_args(subcommand, args):
    """Return (short letters, long options, positionals), skipping option values."""
    value_short = VALUE_SHORT.get(subcommand, "")
    attached = ATTACHED_SHORT.get(subcommand, "")
    value_long = VALUE_LONG.get(subcommand, set())
    shorts, longs, positionals = set(), [], []
    skip_next = after_separator = False
    for arg in args:
        if skip_next:
            skip_next = False
        elif after_separator:
            positionals.append(arg)
        elif arg == "--":
            after_separator = True
        elif arg.startswith("--"):
            longs.append(arg)
            skip_next = arg in value_long
        elif SHORT_OPTION.fullmatch(arg):
            for position, letter in enumerate(arg[1:], 1):
                shorts.add(letter)
                if letter in attached:
                    break
                if letter in value_short:
                    skip_next = position == len(arg) - 1
                    break
        else:
            positionals.append(arg)
    return shorts, longs, positionals


def risk(subcommand, args):
    """Return a REASONS key when the git call needs the user's approval."""
    shorts, longs, positionals = parse_args(subcommand, args)
    if subcommand == "commit" and ("--no-verify" in longs or "n" in shorts):
        return "no-verify"
    if subcommand == "push":
        forced = any(o == "--force" or o.startswith(("--force-with-lease", "--force-if-includes")) for o in longs)
        if forced or "f" in shorts or any(p.startswith("+") and len(p) > 1 for p in positionals):
            return "force-push"
    if subcommand == "reset" and "--hard" in longs:
        return "reset-hard"
    if subcommand == "clean" and not ("--dry-run" in longs or "n" in shorts):
        return "clean"
    if subcommand == "add" and not ("--dry-run" in longs or "n" in shorts):
        if any(is_sensitive_path(p) for p in positionals):
            return "sensitive-file"
    return None


def inspect_staged_commit(repo_dir=None):
    """Inspect currently staged files for secrets, sensitive names, or large files."""
    cwd = repo_dir or os.getcwd()
    try:
        root_res = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=cwd, capture_output=True, text=True, encoding="utf-8", timeout=2, check=False,
        )
        if root_res.returncode != 0:
            return None
        repo_root = Path(root_res.stdout.strip())
        names_res = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
            cwd=repo_root, capture_output=True, text=True, encoding="utf-8", timeout=2, check=False,
        )
        if names_res.returncode != 0:
            return None
        staged_files = [line.strip() for line in names_res.stdout.splitlines() if line.strip()]
        if not staged_files:
            return None

        sensitive = [f for f in staged_files if is_sensitive_path(f)]
        large = []
        for rel in staged_files:
            candidate = repo_root / rel
            try:
                size = candidate.stat().st_size
                if size > MAX_STAGED_FILE_BYTES:
                    large.append(f"{rel} ({size / (1024 * 1024):.1f}MB)")
            except OSError:
                continue

        secret_hits = []
        diff_res = subprocess.run(
            ["git", "diff", "--cached", "-U0", "--diff-filter=ACMR"],
            cwd=repo_root, capture_output=True, timeout=2, check=False,
        )
        if diff_res.returncode == 0:
            diff_text = diff_res.stdout[:MAX_DIFF_SCAN_BYTES].decode("utf-8", errors="ignore")
            current_file = ""
            for line in diff_text.splitlines():
                if line.startswith("+++ b/"):
                    current_file = line[6:]
                    continue
                if not line.startswith("+") or line.startswith("+++"):
                    continue
                added = line[1:]
                for label, pattern in SECRET_PATTERNS:
                    if pattern.search(added):
                        hit = f"{current_file or 'staged'}: {label}"
                        if hit not in secret_hits:
                            secret_hits.append(hit)
                        break

        findings = []
        if sensitive:
            findings.append(f"疑似敏感文件（{', '.join(sensitive[:3])}）")
        if secret_hits:
            findings.append(f"疑似密钥内容（{', '.join(secret_hits[:3])}）")
        if large:
            findings.append(f"超过 5MB 的大文件（{', '.join(large[:3])}）")
        if findings:
            return f"commit-pr：暂存区发现{'、'.join(findings)}，请确认后再提交。"
    except Exception:
        return None
    return None


def find_risk(command):
    try:
        segments = split_segments(command)
    except ValueError:
        return None
    for tokens in segments:
        call = git_call(tokens)
        found = risk(*call) if call else None
        if found:
            return found
    return None


def find_staged_commit_risk(command, cwd=None):
    try:
        segments = split_segments(command)
    except ValueError:
        return None
    for tokens in segments:
        parsed = git_call_with_dir(tokens)
        if not parsed:
            continue
        subcommand, args, repo_dir = parsed
        if subcommand != "commit":
            continue
        shorts, longs, _ = parse_args(subcommand, args)
        if "--dry-run" in longs or "n" in shorts:
            continue
        target_dir = repo_dir
        if target_dir and cwd and not os.path.isabs(target_dir):
            target_dir = os.path.join(cwd, target_dir)
        reason = inspect_staged_commit(target_dir or cwd)
        if reason:
            return reason
    return None


def main():
    try:
        data = json.loads(sys.stdin.buffer.read().decode("utf-8"))
        # Antigravity PreToolUse (run_command)
        tool_call = data.get("toolCall")
        if isinstance(tool_call, dict):
            if tool_call.get("name") != "run_command":
                return
            args = tool_call.get("args") or {}
            command = str(args.get("CommandLine", ""))
            found = find_risk(command)
            reason = REASONS[found] if found else find_staged_commit_risk(command, cwd=data.get("cwd"))
            if reason:
                print(json.dumps({"decision": "force_ask", "reason": reason}))
            return
        # Claude Code / Codex PreToolUse (Bash)
        if data.get("tool_name") != "Bash":
            return
        command = str((data.get("tool_input") or {}).get("command", ""))
        found = find_risk(command)
        reason = REASONS[found] if found else find_staged_commit_risk(command, cwd=data.get("cwd"))
        if reason:
            print(json.dumps({"hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "ask",
                "permissionDecisionReason": reason,
            }}))
    except Exception:
        pass


if __name__ == "__main__":
    main()
