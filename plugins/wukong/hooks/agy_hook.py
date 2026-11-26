#!/usr/bin/env python3
"""Antigravity plugin hooks: SessionStart auto-update/journal and PreInvocation prompt-sharpen.

Prints a valid JSON object and exits 0 on every path so a session is never
blocked or broken.

- SessionStart: throttled background git pull (at most once per
  ``WUKONG_AUTO_UPDATE_INTERVAL`` seconds, default 24h, only on a clean named
  branch; ``WUKONG_AUTO_UPDATE=0`` disables) plus local journal entry.
- PreInvocation: evaluates ``lastUserInput`` with ``improve_hook.evaluate_prompt``
  once per distinct user turn per conversation (deduplicated so multi-step tool
  loops and background wakeups do not repeat), injecting a ``systemMessage``
  step when applicable, and records the prompt to the local journal.
"""
import hashlib
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]

try:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import journal
except Exception:
    journal = None

try:
    sys.path.insert(0, str(PLUGIN_ROOT / "skills" / "prompt-sharpen" / "scripts"))
    import improve_hook
except Exception:
    improve_hook = None

DEFAULT_INTERVAL = 24 * 3600
STALE_LOCK_SECONDS = 120
MAX_TRACKED_CONVERSATIONS = 64


def auto_update_enabled():
    return os.environ.get("WUKONG_AUTO_UPDATE", "1").strip().lower() not in ("0", "false", "off", "no")


def update_interval():
    raw = os.environ.get("WUKONG_AUTO_UPDATE_INTERVAL", "").strip()
    try:
        return max(0, int(raw)) if raw else DEFAULT_INTERVAL
    except ValueError:
        return DEFAULT_INTERVAL


def state_path():
    home = os.environ.get("WUKONG_HOME")
    base = Path(home) if home else Path.home() / ".wukong"
    return base / "agy-update.json"


def repo_root(plugin_root=PLUGIN_ROOT):
    candidate = Path(plugin_root).resolve().parents[1]
    return candidate if (candidate / ".git").exists() else None


def should_check(now=None, path=None):
    now = time.time() if now is None else now
    interval = update_interval()
    if interval == 0:
        return True
    path = path or state_path()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        last = float(data.get("lastCheck", 0))
        return (now - last) >= interval
    except Exception:
        return True


def _atomic_write_text(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.{os.getpid()}.{threading.get_ident()}.tmp")
    try:
        tmp.write_text(content, encoding="utf-8")
        os.replace(tmp, path)
    finally:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass


def record_check(now=None, path=None):
    now = time.time() if now is None else now
    path = path or state_path()
    try:
        _atomic_write_text(path, json.dumps({"lastCheck": int(now)}))
    except Exception:
        pass


def _acquire_lock(lock_path, now):
    """Atomically claim a short-lived lock file; reclaim if stale."""
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    for _ in range(2):
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            try:
                os.write(fd, str(os.getpid()).encode("ascii"))
            finally:
                os.close(fd)
            return True
        except FileExistsError:
            try:
                age = now - lock_path.stat().st_mtime
                if age >= STALE_LOCK_SECONDS:
                    lock_path.unlink(missing_ok=True)
                    continue
            except OSError:
                pass
            return False
        except OSError:
            return False
    return False


def _release_lock(lock_path):
    try:
        lock_path.unlink(missing_ok=True)
    except OSError:
        pass


def _git_output(repo, *args, timeout=3):
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=timeout,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    return result.returncode, result.stdout.strip()


def is_clean_branch(repo):
    code, status = _git_output(repo, "status", "--porcelain")
    if code != 0 or status:
        return False
    code, branch = _git_output(repo, "rev-parse", "--abbrev-ref", "HEAD")
    return code == 0 and bool(branch) and branch != "HEAD"


def trigger_background_pull(repo):
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) | getattr(subprocess, "DETACHED_PROCESS", 0)
    kwargs = {
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
        "close_fds": True,
    }
    if os.name == "nt":
        kwargs["creationflags"] = flags
    else:
        kwargs["start_new_session"] = True
    subprocess.Popen(["git", "-C", str(repo), "pull", "--ff-only", "--quiet"], **kwargs)


def maybe_auto_update(plugin_root=PLUGIN_ROOT, now=None, path=None):
    """Return True if a background fast-forward pull was launched, else False."""
    if not auto_update_enabled():
        return False
    repo = repo_root(plugin_root)
    if repo is None:
        return False
    now = time.time() if now is None else now
    state = path or state_path()
    lock = state.with_suffix(".lock")
    if not _acquire_lock(lock, now):
        return False
    try:
        if not should_check(now=now, path=state):
            return False
        record_check(now=now, path=state)
        if not is_clean_branch(repo):
            return False
        trigger_background_pull(repo)
        return True
    finally:
        _release_lock(lock)


def prompt_state_path():
    return state_path().with_name("agy-prompt-state.json")


def _acquire_state_lock(lock_path, timeout=0.3):
    deadline = time.monotonic() + timeout
    while True:
        if _acquire_lock(lock_path, time.time()):
            return True
        if time.monotonic() >= deadline:
            return False
        time.sleep(0.01)


def _claim_user_turn(conversation_id, raw_input, path=None):
    """Return True if this (conversation_id, raw_input) has not been processed yet."""
    if not conversation_id:
        return True
    digest = hashlib.sha256(raw_input.encode("utf-8", errors="replace")).hexdigest()[:16]
    path = path or prompt_state_path()
    lock = path.with_suffix(".lock")
    locked = _acquire_state_lock(lock)
    try:
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
            entries = loaded if isinstance(loaded, dict) else {}
        except Exception:
            entries = {}
        if entries.get(conversation_id) == digest:
            return False
        # Refresh insertion order so the newest conversations stay within the cap.
        entries.pop(conversation_id, None)
        entries[conversation_id] = digest
        while len(entries) > MAX_TRACKED_CONVERSATIONS:
            entries.pop(next(iter(entries)))
        try:
            _atomic_write_text(path, json.dumps(entries))
        except Exception:
            pass
        return True
    finally:
        if locked:
            _release_lock(lock)


def handle_pre_invocation(data, state_file=None):
    """Return (output_dict, should_record_journal, outcome) for an Antigravity PreInvocation event."""
    raw_input = data.get("lastUserInput", "")
    if not isinstance(raw_input, str) or not raw_input.strip():
        return {}, False, None
    conv_id = str(data.get("conversationId") or "")
    if not _claim_user_turn(conv_id, raw_input, path=state_file):
        return {}, False, None
    if improve_hook:
        text, outcome = improve_hook.classify_evaluation({"prompt": raw_input})
    else:
        text, outcome = "", "skipped:missing_hook"
    if text:
        # Antigravity 当前宿主解析 systemMessage.metadata.user_markdown 会整条丢弃 injectSteps。
        out = {"injectSteps": [{"systemMessage": {"systemMessage": text}}]}
    else:
        out = {}
    return out, True, outcome


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["--status"]:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        limit = 10
        if argv[1:2] == ["--limit"] and len(argv) > 2:
            try:
                limit = int(argv[2])
            except ValueError:
                limit = 10
        if improve_hook:
            print(improve_hook.format_hook_status(limit=limit))
        else:
            print("improve_hook 不可用。")
        return
    try:
        raw = sys.stdin.buffer.read()
        data = json.loads(raw.decode("utf-8")) if raw.strip() else {}
    except Exception:
        data = {}
    event = data.get("hookEventName", "") if isinstance(data, dict) else ""
    if event == "PreInvocation":
        try:
            out, should_record, outcome = handle_pre_invocation(data)
        except Exception:
            out, should_record, outcome = {}, False, None
        print(json.dumps(out), flush=True)
        try:
            if should_record and improve_hook and outcome:
                improve_hook.record_hook_status(
                    "PreInvocation",
                    outcome,
                    via="agy_hook",
                    session_id=str(data.get("conversationId") or ""),
                    cwd=str(data.get("cwd") or ""),
                )
        except Exception:
            pass
        try:
            if should_record and journal:
                journal.record({
                    "hook_event_name": "UserPromptSubmit",
                    "prompt": data.get("lastUserInput", ""),
                    "session_id": str(data.get("conversationId") or ""),
                    "cwd": str(data.get("cwd") or ""),
                })
        except Exception:
            pass
        return

    print("{}", flush=True)
    try:
        if event == "SessionStart":
            maybe_auto_update()
            if journal:
                journal.record({
                    "hook_event_name": "SessionStart",
                    "session_id": str(data.get("conversationId") or ""),
                    "cwd": str(data.get("cwd") or ""),
                })
    except Exception:
        pass


if __name__ == "__main__":
    main()
