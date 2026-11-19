#!/usr/bin/env python3
"""Claude Code hook: nudge the model to load prompt-sharpen on vague requests.

Ported from severity1/claude-code-prompt-improver (MIT, see LICENSE-prompt-improver).
Two events, both read the hook payload from stdin and print one JSON object:

- UserPromptSubmit: attach the evaluation note. Prompts starting with ``*``,
  ``#`` or ``/``, harness-generated messages, confirmations such as "可以" or
  "继续", and prompts of at most four characters are left alone.
- PreToolUse (Bash): remind the model to run long-lived commands in the background.

The hook only adds context. It never rewrites a prompt, blocks a tool call, or
fails the turn: any error exits silently with no output.
"""
import json
import re
import sys
from pathlib import Path

try:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "hooks"))
    import journal
except Exception:
    journal = None

MACHINE_PREFIXES = (
    "<task-notification>",
    "<command-name>",
    "<command-message>",
    "<local-command-stdout>",
    "<local-command-stderr>",
    "<local-command-caveat>",
    "<system-reminder>",
)

LONG_RUNNING = re.compile(
    r"\b(npm|pnpm|yarn|bun)\s+(run\s+)?(dev|start|serve|watch)\b"
    r"|\b(vite|webpack(-dev-server)?|nodemon|next\s+dev|rails\s+server|flask\s+run|uvicorn|gunicorn)\b"
    r"|--watch\b|\btail\s+-[fF]\b|\b(http\.server|live-server)\b",
    re.IGNORECASE,
)

EVALUATION = (
    "提示词评估：结合对话判断是否有关键缺口——存在多个合理解释且会明显改变结果，"
    "或缺少的目标、作用对象、范围、约束、验收影响实现且上下文补不上。"
    "需求短、没文件名不算缺口；只说了动作也不等于信息足够。"
    "有缺口或用户要求澄清、优化提示词时，加载 wukong:prompt-sharpen（因缺口加载先点明缺口，不虚构）。"
    "信息足够、事实问答或对既定方案的确认直接执行；"
    "bug 走 systematic-debugging、新功能走 brainstorming，不重复澄清。"
)

# 确认、继续这类回复和极短消息没有可澄清的需求，附评估说明只会拖慢这一轮。
SHORT_LIMIT = 4
CONFIRMATION = re.compile(
    r"^(可以|好|好的|行|嗯|对|是|是的|没问题|同意|确认|继续|开始|做吧|就这样|按你说的(做|来)?|ok|okay|yes|y|go|lgtm)[。.!！~～\s]*$",
    re.IGNORECASE,
)

BACKGROUND = (
    "这看起来是长时间运行或不会退出的进程（开发服务器、watch、tail -f）。"
    "用 run_in_background 放到后台，不要卡住本轮。"
    "轮询时只取要紧的输出（错误、ready 行、你在等的信号），"
    "在源头用 grep、tail、--quiet 过滤，不要把整段日志灌进上下文。"
    "若命令很快就结束，忽略本条。"
)


def evaluate_prompt(data):
    prompt = data.get("prompt", "")
    if not isinstance(prompt, str) or not prompt.strip():
        return ""
    if prompt[0] in "*#/":
        return ""
    if prompt.lstrip().startswith(MACHINE_PREFIXES):
        return ""
    compact = "".join(prompt.split())
    if len(compact) <= SHORT_LIMIT or CONFIRMATION.match(prompt.strip()):
        return ""
    return EVALUATION


def remind_background(data):
    if data.get("tool_name") != "Bash":
        return ""
    command = (data.get("tool_input") or {}).get("command", "")
    if isinstance(command, str) and LONG_RUNNING.search(command):
        return BACKGROUND
    return ""


def build_context(data):
    event = data.get("hook_event_name")
    if event == "UserPromptSubmit":
        return event, evaluate_prompt(data)
    if event == "PreToolUse":
        return event, remind_background(data)
    return event, ""


def main():
    try:
        data = json.loads(sys.stdin.buffer.read().decode("utf-8"))
        event, text = build_context(data)
        if text:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}), flush=True)
        # 先交出提醒再记日志：记录变慢或失败都不影响这一轮的输出。
        if journal and event == "UserPromptSubmit":
            journal.record(data)
    except Exception:
        pass


if __name__ == "__main__":
    main()
