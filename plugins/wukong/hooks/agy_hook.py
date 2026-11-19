#!/usr/bin/env python3
"""Antigravity SessionStart hook: throttled background git pull and local journal entry.

Runs once per Antigravity session. Prints ``{}`` and exits 0 on every path so
a session is never blocked or broken.

Auto-update runs at most once per ``WUKONG_AUTO_UPDATE_INTERVAL`` seconds
(default 86400 = 24h) and ONLY when the plugin lives inside a clean Git
checkout on a named branch. Set ``WUKONG_AUTO_UPDATE=0`` to turn it off.
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

try:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import journal
except Exception:
    journal = None

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INTERVAL = 24 * 3600
STALE_LOCK_SECONDS = 120


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


def record_check(now=None, path=None):
    now = time.time() if now is None else now
    path = path or state_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(f"{path.name}.{os.getpid()}.tmp")
        tmp.write_text(json.dumps({"lastCheck": int(now)}), encoding="utf-8")
        os.replace(tmp, path)
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


def main():
    try:
        raw = sys.stdin.buffer.read()
        data = json.loads(raw.decode("utf-8")) if raw.strip() else {}
    except Exception:
        data = {}
    print("{}", flush=True)
    try:
        if data.get("hookEventName", "SessionStart") == "SessionStart":
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
