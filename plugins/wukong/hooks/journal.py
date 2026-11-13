#!/usr/bin/env python3
"""Record local usage events for the personal learning layer.

Appends one JSON line per event to ``~/.wukong/journal.jsonl`` (or
``$WUKONG_HOME/journal.jsonl``). It never prints, so it adds nothing to the
model context, and any error is swallowed so a session never breaks.

Events: ``session`` (SessionStart), ``skill`` (PreToolUse on Skill, or a slash
command), ``correction`` / ``explicit`` / ``task`` (UserPromptSubmit). Only a
short, redacted excerpt of the user's own message is kept; tool output, model
replies and file contents are never read. ``WUKONG_JOURNAL=0`` turns it off.
"""
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

MAX_BYTES = 2 * 1024 * 1024
KEEP_BYTES = 1536 * 1024
MAX_AGE = timedelta(days=90)
TASK_EXCERPT = 80
EXPLICIT_EXCERPT = 120
SHORT_LIMIT = 4

MACHINE_PREFIXES = (
    "<task-notification>",
    "<command-name>",
    "<command-message>",
    "<local-command-stdout>",
    "<local-command-stderr>",
    "<local-command-caveat>",
    "<system-reminder>",
)

CONFIRMATION = re.compile(
    r"^(可以|好|好的|行|嗯|对|是|是的|没问题|同意|确认|继续|开始|做吧|就这样|按你说的(做|来)?|ok|okay|yes|y|go|lgtm)[。.!！~～\s]*$",
    re.IGNORECASE,
)
# 用户明说的长期偏好：一次就算数。
EXPLICIT = re.compile(r"以后|每次都|不要再|别再|记住|从今往后|always|never again|from now on", re.IGNORECASE)
# 纠正用语只做粗筛，语义归类交给 reflect --me。
CORRECTION = re.compile(
    r"不对|错了|不是这样|别这样|说了多少次|又.{0,6}了|太长|太慢|太啰嗦|简单点|简洁点|^no[,，\s]|wrong|don'?t do",
    re.IGNORECASE,
)

REDACTIONS = (
    (re.compile(r"\b(sk|pk|rk|ghp|gho|ghu|ghs|github_pat|xox[abprs]|AKIA|AIza)[-_A-Za-z0-9]{8,}"), "[已隐藏]"),
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "[已隐藏]"),
    (re.compile(r"(https?://[^\s?#]+)\?\S*"), r"\1?[已隐藏]"),
    (re.compile(r"[A-Za-z0-9_\-+/=]{20,}"), "[已隐藏]"),
)


def journal_path():
    home = os.environ.get("WUKONG_HOME")
    return Path(home) if home else Path.home() / ".wukong"


def enabled():
    return os.environ.get("WUKONG_JOURNAL", "1").strip().lower() not in ("0", "false", "off", "no")


def redact(text):
    for pattern, replacement in REDACTIONS:
        text = pattern.sub(replacement, text)
    return text


def excerpt(text, limit):
    text = " ".join(text.split())
    return redact(text[:limit])


def classify_prompt(prompt):
    """Return (event, extra fields) for a user message, or None to skip it."""
    if not isinstance(prompt, str):
        return None
    stripped = prompt.strip()
    if not stripped or stripped.startswith(MACHINE_PREFIXES):
        return None
    if stripped[0] == "/":
        name = stripped[1:].split()[0] if len(stripped) > 1 else ""
        return ("skill", {"name": name, "via": "slash"}) if name else None
    if stripped[0] in "*#":
        return None
    if EXPLICIT.search(stripped):
        return "explicit", {"text": excerpt(stripped, EXPLICIT_EXCERPT)}
    if CORRECTION.search(stripped):
        return "correction", {"text": excerpt(stripped, TASK_EXCERPT)}
    if len("".join(stripped.split())) <= SHORT_LIMIT or CONFIRMATION.match(stripped):
        return None
    return "task", {"text": excerpt(stripped, TASK_EXCERPT)}


def build_event(data):
    """Map a hook payload to one journal record, or None."""
    event = data.get("hook_event_name")
    if event == "SessionStart":
        kind, extra = "session", {}
    elif event == "UserPromptSubmit":
        found = classify_prompt(data.get("prompt"))
        if not found:
            return None
        kind, extra = found
    elif event == "PreToolUse" and data.get("tool_name") == "Skill":
        name = (data.get("tool_input") or {}).get("skill")
        if not isinstance(name, str) or not name.strip():
            return None
        kind, extra = "skill", {"name": name.strip(), "via": "tool"}
    else:
        return None
    record = {
        "ts": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "event": kind,
        "session": str(data.get("session_id") or ""),
        "project": Path(str(data.get("cwd") or "")).name,
    }
    record.update(extra)
    return record


def _first_timestamp(path):
    with path.open("rb") as handle:
        line = handle.readline()
    try:
        return datetime.fromisoformat(json.loads(line)["ts"])
    except Exception:
        return None


def prune(path, now=None):
    """Drop lines older than MAX_AGE and keep the file under MAX_BYTES."""
    now = now or datetime.now(timezone.utc)
    size = path.stat().st_size
    first = _first_timestamp(path)
    if size <= MAX_BYTES and (first is None or now - first <= MAX_AGE):
        return
    kept, total = [], 0
    for line in reversed(path.read_bytes().splitlines(keepends=True)):
        try:
            stamp = datetime.fromisoformat(json.loads(line)["ts"])
        except Exception:
            continue
        if now - stamp > MAX_AGE or total + len(line) > KEEP_BYTES:
            break
        kept.append(line)
        total += len(line)
    temp = path.with_name(path.name + ".%d.tmp" % os.getpid())
    temp.write_bytes(b"".join(reversed(kept)))
    os.chmod(temp, 0o600)
    os.replace(temp, path)


def append(record, directory=None):
    directory = directory or journal_path()
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    path = directory / "journal.jsonl"
    line = (json.dumps(record, ensure_ascii=False) + "\n").encode("utf-8")
    fd = os.open(str(path), os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    try:
        os.write(fd, line)
    finally:
        os.close(fd)
    prune(path)


def record(data):
    """Record one hook payload. Safe to call from any hook; never raises."""
    try:
        if not enabled():
            return
        event = build_event(data)
        if event:
            append(event)
    except Exception:
        pass


def main():
    try:
        record(json.loads(sys.stdin.buffer.read().decode("utf-8")))
    except Exception:
        pass


if __name__ == "__main__":
    main()
