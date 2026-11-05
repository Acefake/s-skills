#!/usr/bin/env python3
"""Claude Code hook: nudge the model to load prompt-sharpen on vague requests.

Ported from severity1/claude-code-prompt-improver (MIT, see LICENSE-prompt-improver).
Two events, both read the hook payload from stdin and print one JSON object:

- UserPromptSubmit: attach the evaluation note. Prompts starting with ``*``,
  ``#`` or ``/`` and harness-generated messages are left alone.
- PreToolUse (Bash): remind the model to run long-lived commands in the background.

The hook only adds context. It never rewrites a prompt, blocks a tool call, or
fails the turn: any error exits silently with no output.
"""
import json
import re
import sys

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

EVALUATION = """提示词评估

用户原话："{prompt}"

判断：这条需求是否清楚到可以直接执行，还是需要先补全？

满足任一条就直接做：
- 已经具体，或对话里的上下文足够，或能推断出意图。

只有确实含糊时才用技能（例如「把它修好」而没有任何上下文）：
1. 先用一句话说明：「提示词优化钩子判断你的需求有点含糊，因为[具体原因：范围不清/缺上下文/目标不明等]。」
2. 然后加载 s-atlas:prompt-sharpen 技能，按它的流程研究、提问、执行。加载之前不要先自行读代码，技能里的研究步骤照常做。
- 默认相信用户意图，用技能之前先看对话历史。

清楚就按原需求做；含糊就加载技能。"""

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
    escaped = prompt.replace("\\", "\\\\").replace('"', '\\"')
    return EVALUATION.format(prompt=escaped)


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
            print(json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}))
    except Exception:
        pass


if __name__ == "__main__":
    main()
