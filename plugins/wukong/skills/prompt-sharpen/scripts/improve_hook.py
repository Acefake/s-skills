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

先结合用户原话和对话历史，检查目标、作用对象、范围、约束或验收结果是否存在关键缺口。
不要因为需求短、没有文件名就判为含糊；也不要仅因为说了动作，或属于讨论，就认定信息足够。

以下情况加载 wukong:prompt-sharpen：
- 存在多个合理解释，选择不同解释会明显改变结果，而上下文无法确定；
- 缺失的信息会影响实现方向、修改范围或验收，而上下文无法补足；
- 用户明确要求优化提示词或先澄清需求。

因关键缺口加载时先指出具体缺口；用户明确点名时直接加载，不虚构缺口。然后按技能研究项目，不要求加载前先完成研究。
能从项目确认的自行补齐，合理推定的注明假设；只有无法确认且必须用户决定的关键问题才提问。
加载技能不等于必须提问，不为次要细节或常规实现选择阻塞执行。

目标与范围已明确、上下文足够、普通事实问答或对既定方案的简短确认，直接执行或回答，并按全局规则使用对口技能。
bug 的定位与复现由 systematic-debugging 主导，新功能设计由 brainstorming 主导；不要重复两套澄清流程。
只读诊断可先收集证据，不把所有未知都当成阻塞问题。"""

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
