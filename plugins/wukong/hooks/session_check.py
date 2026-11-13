#!/usr/bin/env python3
"""Claude Code SessionStart hook: record the plugin source and check the global rules once.

Prints one JSON object whose additionalContext tells the model which wukong
build is loaded and whether the global skill instructions are current. It runs
the read-only check in setup-s-instructions (no --apply), never writes
configuration, and exits silently on any error so a session always starts.
"""
import json
import subprocess
import sys
from pathlib import Path

try:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import journal
except Exception:
    journal = None

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
CHECK = PLUGIN_ROOT / "skills/setup-s-instructions/scripts/global_instructions.py"

STATUS_TEXT = {
    "configured": "全局技能提示词已是最新，本会话不必再自检。",
    "missing": "全局技能提示词缺失，可显式调用 setup-s-instructions 初始化；只提醒一次，不阻塞原任务。",
    "outdated": "全局技能提示词需更新，可显式调用 setup-s-instructions 更新；只提醒一次，不阻塞原任务。",
}
UNKNOWN_TEXT = "暂时无法确认全局技能提示词。"


def run_check():
    """Return the parsed check result, or None when it cannot be read."""
    try:
        result = subprocess.run(
            [sys.executable, "-B", str(CHECK), "--host", "claude-code"],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            timeout=10,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        return json.loads(result.stdout.decode("utf-8"))
    except Exception:
        return None


def plugin_version():
    try:
        return json.loads((PLUGIN_ROOT / "plugin.json").read_text(encoding="utf-8"))["version"]
    except Exception:
        return "未知版本"


def build_message(check, root=PLUGIN_ROOT, version=None):
    status = (check or {}).get("status")
    version = (check or {}).get("version") or version or plugin_version()
    return "wukong {}（{}）。{}".format(version, root, STATUS_TEXT.get(status, UNKNOWN_TEXT))


def main():
    try:
        raw = sys.stdin.buffer.read()
        message = build_message(run_check())
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": message}}), flush=True)
        if journal:
            try:
                journal.record(json.loads(raw.decode("utf-8")))
            except Exception:
                pass
    except Exception:
        pass


if __name__ == "__main__":
    main()
