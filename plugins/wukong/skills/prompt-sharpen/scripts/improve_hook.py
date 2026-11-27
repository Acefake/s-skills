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
import os
import re
import sys
import threading
import time
from datetime import datetime, timezone
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
    "[T3 Code:",
    "Delegated task ",
)

WRAPPER_TAGS = re.compile(
    r"<(t3_code_instructions|runtime_info|ADDITIONAL_METADATA|USER_SETTINGS_CHANGE|SYSTEM_MESSAGE)>.*?</\1>",
    re.IGNORECASE | re.DOTALL,
)
OUTER_USER_REQUEST_BLOCK = re.compile(r"^\s*<USER_REQUEST>\s*(.*?)\s*</USER_REQUEST>\s*$", re.DOTALL)
USER_REQUEST_BLOCK = re.compile(r"^\s*<user_request>\s*(.*?)\s*</user_request>\s*$", re.DOTALL)

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
    "bug 走 debug、新功能走 spec，不重复澄清。"
)
USER_NOTICE = "[wukong] prompt-sharpen：需求可能不够具体，已提醒先澄清"

# 只决定要不要给用户显示一行提示，不改给模型的评估说明（它保持定长）；判断很粗，模型照常自己评估。
VAGUE_MAX = 30
VAGUE_VERBS = re.compile(
    r"优化|改进|完善|调整|处理|整理|重构|美化|提升|改善|看看|看一下|改一下|改改|弄一下|搞一下|搞定|弄好|做个|加个|弄个|好看点|更好"
    r"|\b(improve|optimi[sz]e|refactor|clean\s*up|polish|make\s+it\s+better|fix\s+it)\b",
    re.IGNORECASE,
)
QUESTION = re.compile(r"(吗|么|呢|[?？])[。.!！~～\s]*$")
CONCRETE_ANCHORS = re.compile(
    r"`[^`]+`"
    r"|[\w-]+\.[A-Za-z][A-Za-z0-9]{0,5}\b"
    r"|[/\\][\w.-]+"
    r"|https?://"
    r"|\b[a-z]+[A-Z]\w*"
    r"|\b\w+_\w+"
    r"|[「」“”\"']"
    r"|\d"
    r"|\b[A-Z]{2,}\b",
)
MAX_LOG_ENTRIES = 50
LOG_TRIM_THRESHOLD = 80
STALE_LOG_LOCK_SECONDS = 30

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


def extract_user_prompt(prompt):
    if journal is not None and hasattr(journal, "extract_user_prompt"):
        return journal.extract_user_prompt(prompt)
    if not isinstance(prompt, str):
        return ""
    cleaned = WRAPPER_TAGS.sub("", prompt).strip()
    outer = OUTER_USER_REQUEST_BLOCK.match(cleaned)
    if outer:
        cleaned = outer.group(1).strip()
    inner = USER_REQUEST_BLOCK.match(cleaned)
    if inner:
        cleaned = inner.group(1).strip()
    return cleaned


def notice_enabled():
    return os.environ.get("WUKONG_HOOK_NOTICE", "1").strip().lower() not in ("0", "false", "off", "no")


def hook_log_enabled():
    return os.environ.get("WUKONG_HOOK_LOG", "1").strip().lower() not in ("0", "false", "off", "no")


def hook_log_path():
    home = os.environ.get("WUKONG_HOME")
    base = Path(home) if home else Path.home() / ".wukong"
    return base / "prompt-hook-log.jsonl"


def _restrict_path_mode(path, mode):
    if os.name == "nt":
        return
    try:
        os.chmod(path, mode)
    except OSError:
        pass


def _acquire_log_lock(lock_path, timeout=0.3):
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    _restrict_path_mode(lock_path.parent, 0o700)
    deadline = time.monotonic() + timeout
    while True:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            try:
                os.write(fd, str(os.getpid()).encode("ascii"))
            finally:
                os.close(fd)
            return True
        except FileExistsError:
            try:
                if (time.time() - lock_path.stat().st_mtime) >= STALE_LOG_LOCK_SECONDS:
                    lock_path.unlink(missing_ok=True)
                    continue
            except OSError:
                pass
            if time.monotonic() >= deadline:
                return False
            time.sleep(0.01)
        except OSError:
            return False


def _release_log_lock(lock_path):
    try:
        lock_path.unlink(missing_ok=True)
    except OSError:
        pass


def record_hook_status(event, outcome, *, via="improve_hook", session_id="", cwd="", path=None):
    """Append one compact, prompt-free status entry so users can verify hook firing."""
    if not hook_log_enabled():
        return
    try:
        target = path or hook_log_path()
        target.parent.mkdir(parents=True, exist_ok=True)
        _restrict_path_mode(target.parent, 0o700)
        entry = {
            "ts": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
            "via": via,
            "event": event,
            "outcome": outcome,
            "session": str(session_id or ""),
            "project": Path(str(cwd or "")).name,
        }
        line = json.dumps(entry, ensure_ascii=False) + "\n"
        lock = target.with_suffix(".lock")
        locked = _acquire_log_lock(lock)
        try:
            fd = os.open(str(target), os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
            with os.fdopen(fd, "a", encoding="utf-8") as handle:
                handle.write(line)
            _restrict_path_mode(target, 0o600)
            if not locked:
                return
            lines = target.read_text(encoding="utf-8").splitlines()
            if len(lines) > LOG_TRIM_THRESHOLD:
                tmp = target.with_name(f"{target.name}.{os.getpid()}.{threading.get_ident()}.tmp")
                try:
                    tmp_fd = os.open(str(tmp), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
                    with os.fdopen(tmp_fd, "w", encoding="utf-8") as handle:
                        handle.write("\n".join(lines[-MAX_LOG_ENTRIES:]) + "\n")
                    _restrict_path_mode(tmp, 0o600)
                    os.replace(tmp, target)
                finally:
                    try:
                        tmp.unlink(missing_ok=True)
                    except OSError:
                        pass
        finally:
            if locked:
                _release_log_lock(lock)
    except Exception:
        pass


def format_hook_status(limit=10, path=None):
    target = path or hook_log_path()
    notice = "开启" if notice_enabled() else "关闭（WUKONG_HOOK_NOTICE=0）"
    logging_state = "开启" if hook_log_enabled() else "关闭（WUKONG_HOOK_LOG=0）"
    header = f"prompt-sharpen 钩子状态 | 界面提示：{notice} | 状态日志：{logging_state} | 日志：{target}"
    if not target.exists():
        return header + "\n暂无触发记录。"
    lines = [line for line in target.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        return header + "\n暂无触发记录。"
    rows = [header]
    for raw in lines[-max(1, limit):]:
        try:
            item = json.loads(raw)
        except Exception:
            continue
        if not isinstance(item, dict):
            continue
        ts = str(item.get("ts") or "")
        via = str(item.get("via") or "")
        event = str(item.get("event") or "")
        outcome = str(item.get("outcome") or "")
        project = str(item.get("project") or "-")
        session = str(item.get("session") or "-")[:8]
        rows.append(f"  {ts}  {outcome:<20}  {via}/{event}  project={project}  session={session}")
    return "\n".join(rows)


def classify_evaluation(data):
    """Return (evaluation_text, outcome_reason) for a user prompt payload."""
    prompt = extract_user_prompt(data.get("prompt", ""))
    if not prompt:
        return "", "skipped:empty"
    if prompt[0] in "*#/":
        return "", "skipped:prefix"
    if prompt.startswith(MACHINE_PREFIXES):
        return "", "skipped:machine"
    if CONFIRMATION.match(prompt):
        return "", "skipped:confirmation"
    compact = "".join(prompt.split())
    if len(compact) <= SHORT_LIMIT:
        return "", "skipped:short"
    return EVALUATION, "injected"


def looks_vague(prompt):
    """
    粗判一条提示词是否笼统：很短、只有泛化动作、没有任何具体锚点；问句不算
    @param prompt 已剥掉宿主包装的用户原话
    @returns 是否值得给用户显示一行澄清提示
    """
    compact = "".join(prompt.split())
    if len(compact) > VAGUE_MAX or QUESTION.search(prompt) or CONCRETE_ANCHORS.search(prompt):
        return False
    return bool(VAGUE_VERBS.search(prompt))


def evaluate_prompt(data):
    return classify_evaluation(data)[0]


QUOTED = re.compile(r"'[^']*'|\"(?:\\.|[^\"\\])*\"")
HEREDOC = re.compile(r"<<-?\s*['\"]?(\w+)['\"]?.*?^\s*\1\s*$", re.DOTALL | re.MULTILINE)


SHELL_C = re.compile(r"\b(?:ba|z|da|k)?sh\s+(?:-\w+\s+)*-\w*c\s+(['\"])(.*?)\1", re.DOTALL)


def executable_text(command):
    """去掉引号里的字符串和 heredoc 正文，只留真正会被执行的部分；`sh -c '…'` 里的脚本照样算。"""
    without_heredoc = HEREDOC.sub("", command)
    scripts = [executable_text(match.group(2)) for match in SHELL_C.finditer(without_heredoc)]
    return " ; ".join([QUOTED.sub("''", without_heredoc), *scripts])


def remind_background(data):
    if data.get("tool_name") != "Bash":
        return ""
    command = (data.get("tool_input") or {}).get("command", "")
    if isinstance(command, str) and LONG_RUNNING.search(executable_text(command)):
        return BACKGROUND
    return ""


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
        print(format_hook_status(limit=limit))
        return
    try:
        data = json.loads(sys.stdin.buffer.read().decode("utf-8"))
        event = data.get("hook_event_name")
        outcome = None
        if event == "UserPromptSubmit":
            text, outcome = classify_evaluation(data)
        elif event == "PreToolUse":
            text = remind_background(data)
        else:
            text = ""
        if text:
            payload = {"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}
            if (event == "UserPromptSubmit" and notice_enabled()
                    and looks_vague(extract_user_prompt(data.get("prompt", "")))):
                payload["systemMessage"] = USER_NOTICE
            print(json.dumps(payload), flush=True)
        if event == "UserPromptSubmit" and outcome:
            record_hook_status(
                event,
                outcome,
                via="improve_hook",
                session_id=data.get("session_id", ""),
                cwd=data.get("cwd", ""),
            )
        # 先交出提醒再记日志：记录变慢或失败都不影响这一轮的输出。
        if journal and event == "UserPromptSubmit":
            journal.record(data)
    except Exception:
        pass


if __name__ == "__main__":
    main()
