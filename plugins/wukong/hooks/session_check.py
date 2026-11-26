#!/usr/bin/env python3
"""Claude Code SessionStart hook: record the plugin source and check the global rules once.

Prints one JSON object whose additionalContext tells the model which wukong
build is loaded and whether the global skill instructions are current. It runs
the read-only check in wukong-init (no --apply), never writes
configuration, and exits silently on any error so a session always starts.
"""
import importlib.util
import json
import os
import sys
from pathlib import Path

try:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import journal
except Exception:
    journal = None

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
CHECK = PLUGIN_ROOT / "skills/wukong-init/scripts/global_instructions.py"

STATUS_TEXT = {
    "configured": "全局技能提示词已是最新，本会话不必再自检。",
    "missing": "全局技能提示词缺失，可显式调用 wukong-init 初始化；只提醒一次，不阻塞原任务。",
    "outdated": "全局技能提示词需更新，可显式调用 wukong-init 更新；只提醒一次，不阻塞原任务。",
}
UNKNOWN_TEXT = "暂时无法确认全局技能提示词。"


def run_check():
    """Return the check result by loading global_instructions in-process, or None on failure."""
    if not CHECK.is_file():
        return None
    prev_bytecode = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec = importlib.util.spec_from_file_location("wukong_global_instructions", CHECK)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        try:
            return module.sync_global(
                "claude-code",
                home=Path.home(),
                claude_config_dir=os.environ.get("CLAUDE_CONFIG_DIR") or None,
                apply=False,
            )
        except (module.ConfigurationError, OSError, UnicodeError) as error:
            return {"status": "error", "error": str(error)}
    except Exception:
        return None
    finally:
        sys.dont_write_bytecode = prev_bytecode


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
