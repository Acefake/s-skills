#!/usr/bin/env python3
"""Claude Code PreToolUse hook (Bash): ask before git commands the s-atlas rules forbid by default.

Covers skipping commit hooks, force pushes, ``reset --hard`` and ``git clean``.
It answers "ask", never "deny", so the user can still approve a command they
asked for. Anything it cannot parse exits silently without a decision.
"""
import json
import os
import re
import shlex
import sys

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
    "force-push": "s-mode 执行边界：强制推送需要明确授权，覆盖具体分支和目标。",
    "reset-hard": "s-mode 执行边界：不以 reset --hard 作为同步或恢复手段，会丢掉未提交的改动。",
    "clean": "s-mode 执行边界：不以 git clean 作为清理手段，会删掉未跟踪文件。",
}


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


def git_call(tokens):
    """Return (subcommand, args) when the segment itself runs git, else None."""
    index = 0
    while index < len(tokens) and (ASSIGNMENT.match(tokens[index]) or tokens[index] in WRAPPERS):
        index += 1
    if index < len(tokens) and tokens[index] == "timeout":
        index += 2
    if index >= len(tokens) or tokens[index].replace("\\", "/").rsplit("/", 1)[-1] not in ("git", "git.exe"):
        return None
    args, position = tokens[index + 1:], 0
    while position < len(args) and args[position].startswith("-"):
        position += 2 if args[position] in VALUE_OPTIONS else 1
    if position >= len(args):
        return None
    return args[position], args[position + 1:]


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


def main():
    try:
        data = json.loads(sys.stdin.buffer.read().decode("utf-8"))
        if data.get("tool_name") != "Bash":
            return
        found = find_risk(str((data.get("tool_input") or {}).get("command", "")))
        if found:
            print(json.dumps({"hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "ask",
                "permissionDecisionReason": REASONS[found],
            }}))
    except Exception:
        pass


if __name__ == "__main__":
    main()
