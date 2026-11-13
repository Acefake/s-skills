#!/usr/bin/env python3
"""Record local usage events for the personal learning layer.

Writes one row per event to the SQLite database ``~/.wukong/journal.db`` (or
``$WUKONG_HOME/journal.db``). Every write is a transaction, so a crash cannot
leave a half-written record, and concurrent sessions are serialized by SQLite's
own locking. The hook never prints, so it adds nothing to the model context,
and any error (including a lock it cannot get within two seconds) is swallowed
so a session never breaks.

Events: ``session`` (SessionStart), ``skill`` (PreToolUse on Skill, or a slash
command), ``correction`` / ``explicit`` / ``task`` (UserPromptSubmit). Only a
short, redacted excerpt of the user's own message is kept; tool output, model
replies and file contents are never read. ``WUKONG_JOURNAL=0`` turns it off.

    python3 journal.py --dump [--limit N]   print recent events as JSON lines
"""
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import sqlite3
except Exception:  # 少数精简版 Python 没有 _sqlite3：不记录，也不报错。
    sqlite3 = None

SCHEMA_VERSION = 1
MAX_AGE_SECONDS = 90 * 24 * 3600
MAX_ROWS = 50000
PRUNE_EVERY = 200
# 每条语句最多等这么久；一次记录最多几条语句，总等待仍远低于钩子的 5 秒超时。
LOCK_TIMEOUT = 0.5
TASK_EXCERPT = 80
EXPLICIT_EXCERPT = 120
SHORT_LIMIT = 4

SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    id      INTEGER PRIMARY KEY,
    at      INTEGER NOT NULL,
    ts      TEXT    NOT NULL,
    event   TEXT    NOT NULL,
    session TEXT    NOT NULL DEFAULT '',
    project TEXT    NOT NULL DEFAULT '',
    name    TEXT,
    via     TEXT,
    text    TEXT
);
CREATE INDEX IF NOT EXISTS events_at ON events(at);
CREATE INDEX IF NOT EXISTS events_event_at ON events(event, at);
"""
COLUMNS = ("at", "ts", "event", "session", "project", "name", "via", "text")

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


def journal_dir():
    home = os.environ.get("WUKONG_HOME")
    return Path(home) if home else Path.home() / ".wukong"


def enabled():
    return os.environ.get("WUKONG_JOURNAL", "1").strip().lower() not in ("0", "false", "off", "no")


def redact(text):
    for pattern, replacement in REDACTIONS:
        text = pattern.sub(replacement, text)
    return text


def excerpt(text, limit):
    return redact(" ".join(text.split())[:limit])


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


def build_event(data, now=None):
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
    now = time.time() if now is None else now
    record = {
        "at": int(now),
        "ts": datetime.fromtimestamp(now, timezone.utc).astimezone().isoformat(timespec="seconds"),
        "event": kind,
        "session": str(data.get("session_id") or ""),
        "project": Path(str(data.get("cwd") or "")).name,
    }
    record.update(extra)
    return record


def _restrict(path, mode):
    """Tighten permissions on files created elsewhere (e.g. by hand); best effort."""
    try:
        if os.name == "posix" and path.stat().st_mode & 0o777 != mode:
            os.chmod(str(path), mode)
    except OSError:
        pass


def connect(directory=None):
    """Open the journal, creating it with private permissions on first use."""
    directory = directory or journal_dir()
    path = directory / "journal.db"
    old_umask = os.umask(0o077)
    try:
        directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        _restrict(directory, 0o700)
        conn = sqlite3.connect(str(path), timeout=LOCK_TIMEOUT, isolation_level=None)
        _restrict(path, 0o600)
    finally:
        os.umask(old_umask)
    try:
        conn.execute("PRAGMA busy_timeout = %d" % int(LOCK_TIMEOUT * 1000))
        if conn.execute("PRAGMA user_version").fetchone()[0] != SCHEMA_VERSION:
            conn.execute("BEGIN IMMEDIATE")
            if conn.execute("PRAGMA user_version").fetchone()[0] != SCHEMA_VERSION:
                for statement in filter(None, (s.strip() for s in SCHEMA.split(";"))):
                    conn.execute(statement)
                conn.execute("PRAGMA user_version = %d" % SCHEMA_VERSION)
            conn.execute("COMMIT")
        if conn.execute("PRAGMA journal_mode").fetchone()[0].lower() != "wal":
            conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = FULL")
    except Exception:
        conn.close()
        raise
    return conn


def prune(conn, now=None, cap=True):
    """Delete events older than 90 days; with cap, keep at most MAX_ROWS newest rows."""
    now = time.time() if now is None else now
    conn.execute("BEGIN IMMEDIATE")
    try:
        conn.execute("DELETE FROM events WHERE at < ?", (int(now) - MAX_AGE_SECONDS,))
        if cap:
            conn.execute(
                "DELETE FROM events WHERE id <= (SELECT id FROM events ORDER BY id DESC LIMIT 1 OFFSET ?)",
                (MAX_ROWS,),
            )
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise


def append(record, directory=None):
    conn = connect(directory)
    try:
        values = tuple(record.get(column, "" if column in ("session", "project") else None) for column in COLUMNS)
        conn.execute("BEGIN IMMEDIATE")
        try:
            row = conn.execute(
                "INSERT INTO events (%s) VALUES (%s)" % (", ".join(COLUMNS), ", ".join("?" * len(COLUMNS))),
                values,
            ).lastrowid
            conn.execute("DELETE FROM events WHERE at < ?", (int(time.time()) - MAX_AGE_SECONDS,))
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise
        if row % PRUNE_EVERY == 0:
            prune(conn)
    finally:
        conn.close()


def record(data):
    """Record one hook payload. Safe to call from any hook; never raises."""
    try:
        if not enabled() or sqlite3 is None:
            return
        event = build_event(data)
        if event:
            append(event)
    except Exception:
        pass


def dump(limit=200, directory=None, out=sys.stdout):
    path = (directory or journal_dir()) / "journal.db"
    if sqlite3 is None or not path.exists():
        return
    conn = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True, timeout=LOCK_TIMEOUT)
    try:
        rows = conn.execute(
            "SELECT %s FROM events ORDER BY id DESC LIMIT ?" % ", ".join(COLUMNS[1:]), (limit,)
        ).fetchall()
    finally:
        conn.close()
    for row in reversed(rows):
        item = {key: value for key, value in zip(COLUMNS[1:], row) if value not in (None, "")}
        out.write(json.dumps(item, ensure_ascii=False) + "\n")


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["--dump"]:
        limit = int(argv[2]) if argv[1:2] == ["--limit"] and len(argv) > 2 else 200
        dump(limit)
        return
    try:
        record(json.loads(sys.stdin.buffer.read().decode("utf-8")))
    except Exception:
        pass


if __name__ == "__main__":
    main()
