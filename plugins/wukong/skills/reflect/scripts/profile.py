#!/usr/bin/env python3
"""Personal rules for the wukong learning layer: collect, validate, apply, undo.

The model does the judgment (grouping corrections into rules and citing the
journal events behind each one); this script does everything that must be
exact. It decides each rule's source and evidence from the cited events, so a
draft cannot claim them; it enforces admission, expiry, safety and size; it
keeps backups; and it writes the personal block through setup-s-instructions.

    profile.py collect [--since YYYY-MM-DD]
    profile.py validate DRAFT.json
    profile.py apply DRAFT.json --host HOST
    profile.py add --id ID --kind KIND --text TEXT [--project NAME] --host HOST
    profile.py show | render
    profile.py forget RULE_ID --host HOST
    profile.py undo --host HOST
    profile.py off --host HOST | on --host HOST

Data lives in ~/.wukong (or $WUKONG_HOME): profile.json is the source of truth,
history/ keeps the 20 most recent versions. Every command prints one JSON object.
"""
import argparse
import json
import os
import re
import sys
import tempfile
import unicodedata
from contextlib import contextmanager
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

try:
    import fcntl
except ImportError:  # Windows
    fcntl = None
    try:
        import msvcrt
    except ImportError:
        msvcrt = None

PLUGIN = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PLUGIN / "hooks"))
sys.path.insert(0, str(PLUGIN / "skills/setup-s-instructions/scripts"))
import journal  # noqa: E402
import global_instructions as gi  # noqa: E402

SCHEMA_VERSION = 1
# 与 scripts/context_budget.py 的 PERSONAL_LIMIT 保持一致（有测试核对）。
PERSONAL_LIMIT = 500
EXPIRE_DAYS = 56
HISTORY_KEEP = 20
MIN_SESSIONS = 2
MAX_RULE_CHARS = 120
USED_REFS_KEEP = 50
COLLECT_LIMIT = 60
KINDS = ("style", "route", "verify", "habit")
KIND_TITLES = {"style": "回复", "route": "技能", "verify": "验证与审查", "habit": "习惯"}
EVIDENCE_EVENTS = ("correction", "explicit")
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,39}$")
CJK = re.compile(r"[\u3000-\u303f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff00-\uffef]")
MARKERS = (gi.START, gi.END, gi.PREVIOUS_START, gi.PREVIOUS_END, gi.LEGACY_START, gi.LEGACY_END,
           gi.PERSONAL_START, gi.PERSONAL_END)

# 下面三组只在规范化（NFKC、去零宽、转小写）之后的文字上匹配。
# 放宽权限、跳过确认、发布部署、碰密钥和权限的规则不能从对话里学，只能用户用 add 亲口加。
SENSITIVE = re.compile(
    r"推送|强制|跳过(钩子|hook|检查|确认)|删除(文件|分支|目录|数据|仓库)"
    r"|(不用|不必|无需|无须|不需要|别|不要|勿)再?(问|确认|询问|请示|等|审批|批准)"
    r"|直接(提交|推送|合并|删除|发布|部署|上线)|自动(提交|推送|合并|发布|部署|上线)|发布|部署|上线|生产环境"
    r"|密钥|密码|凭据|权限|安全(检查|审查)"
    r"|\bpush|\bforce\b|--force|--no-verify|reset\s+--hard|git\s+clean|rm\s+-rf|\bdeploy|\bpublish|\bmerge\b"
    r"|\bdelete\b|\bship\b|\bprod(uction)?\b|without\s+(ask|confirm|approv|check)|no\s+need\s+to\s+(ask|confirm)"
    r"|don'?t\s+(ask|confirm|wait)|(never|not?)\s+wait\s+for\s+(approval|confirmation|me)"
    r"|skip\s+(the\s+)?(confirm|check|hook|approv)|straight\s+to\s+(main|master)|(main|master)\s+directly"
    r"|auto-?\s*(commit|push|merge|deploy)|commit\s+directly|api[\s_-]?key|access[\s_-]?token|secret[\s_-]?key"
    r"|password|credential|\bsudo\b|permission"
)
URL = re.compile(r"https?://|www\.")
COMMAND = re.compile(
    r"`[^`]*\b(git|npm|pnpm|yarn|pip|curl|wget|sudo|chmod|chown|docker|kubectl|rm)\b[^`]*`"
    r"|\b(curl|wget|sudo|chmod|chown|kubectl)\s+\S|\brm\s+-|\bgit\s+(push|reset|clean|rebase|checkout|tag|branch\s+-)"
    r"|\b(npm|pnpm|yarn)\s+(publish|install|add|run|exec)\b|\bpip\s+install\b|\bdocker\s+(run|push|rm|exec)\b"
)
# 放松验证或审查：只接受用户明说（日志里的 explicit 事件），不从纠正里推断。
LOOSEN = re.compile(
    r"不跑|别跑|不用跑|跳过|不派|别派|不用派|不审|不用审|不用测|少测|不写测试|不测"
    r"|skip\s+(the\s+)?(test|review)|no\s+(test|review)|don'?t\s+(run\s+)?(test|review)|without\s+(test|review)"
)


def normalize(text):
    text = unicodedata.normalize("NFKC", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Cf")
    return text.lower()


def estimate(text):
    cjk = len(CJK.findall(text))
    return cjk + (len(text) - cjk + 3) // 4


def home():
    return journal.journal_dir()


def today():
    return date.today()


def empty_profile():
    return {"schemaVersion": SCHEMA_VERSION, "updated": None, "enabled": True, "rules": []}


def load_profile(directory=None):
    path = (directory or home()) / "profile.json"
    if not path.exists():
        return empty_profile()
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("rules"), list):
        raise ValueError("profile.json is not a profile")
    data.setdefault("enabled", True)
    return data


def _write_private(path, data):
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.chmod(temporary, 0o600)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@contextmanager
def locked(directory):
    """Serialize every write to profile.json and the personal block."""
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    handle = open(str(directory / "profile.lock"), "a+")
    try:
        if fcntl:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        elif msvcrt:
            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
        yield
    finally:
        try:
            if fcntl:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
            elif msvcrt:
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        finally:
            handle.close()


# ---------------------------------------------------------------- journal

def _open_journal(directory):
    path = directory / "journal.db"
    if journal.sqlite3 is None or not path.exists():
        return None
    return journal.sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True, timeout=journal.LOCK_TIMEOUT)


def collect(since=None, directory=None):
    """Summarize journal events since the last update for the model to group."""
    directory = directory or home()
    profile = load_profile(directory)
    if since is None:
        stamp = profile.get("updated")
        since = datetime.fromisoformat(stamp) if stamp else datetime.now(timezone.utc) - timedelta(days=30)
    elif isinstance(since, str):
        since = datetime.fromisoformat(since)
    if since.tzinfo is None:
        since = since.replace(tzinfo=timezone.utc)
    result = {"since": since.isoformat(timespec="seconds"), "enabled": profile["enabled"], "rules": profile["rules"],
              "corrections": [], "explicit": [], "sessions": 0, "skills": {}}
    conn = _open_journal(directory)
    if conn is None:
        return result
    try:
        at = int(since.timestamp())
        result["sessions"] = conn.execute(
            "SELECT count(DISTINCT session) FROM events WHERE at >= ? AND session != ''", (at,)).fetchone()[0]
        for kind, key in (("correction", "corrections"), ("explicit", "explicit")):
            rows = conn.execute(
                "SELECT id, ts, session, project, text FROM events WHERE event = ? AND at >= ? ORDER BY at DESC LIMIT ?",
                (kind, at, COLLECT_LIMIT)).fetchall()
            result[key] = [dict(zip(("id", "ts", "session", "project", "text"), row)) for row in reversed(rows)]
        result["skills"] = dict(conn.execute(
            "SELECT name, count(*) FROM events WHERE event = 'skill' AND at >= ? GROUP BY name ORDER BY count(*) DESC",
            (at,)).fetchall())
    finally:
        conn.close()
    return result


def load_events(ids, directory=None):
    """Return {id: (event, session, text)} for the cited journal events that exist."""
    ids = sorted({i for i in ids if isinstance(i, int) and not isinstance(i, bool)})
    conn = _open_journal(directory or home())
    if conn is None or not ids:
        if conn is not None:
            conn.close()
        return {}
    try:
        found = {}
        for start in range(0, len(ids), 500):
            chunk = ids[start:start + 500]
            rows = conn.execute("SELECT id, event, session, text FROM events WHERE id IN (%s)" % ",".join("?" * len(chunk)),
                                chunk).fetchall()
            found.update({row[0]: (row[1], row[2] or "event-%d" % row[0], row[3] or "") for row in rows})
        return found
    finally:
        conn.close()


# ---------------------------------------------------------------- checks

def shape_errors(rule):
    """Structure and rendering safety; applies to every rule, manual ones too."""
    reasons = []
    if not isinstance(rule, dict):
        return ["rule is not an object"]
    if not isinstance(rule.get("id"), str) or not ID_RE.match(rule["id"]):
        reasons.append("id must be lowercase letters, digits and dashes, at most 40 characters")
    if rule.get("kind") not in KINDS:
        reasons.append("kind must be one of " + ", ".join(KINDS))
    text = rule.get("text")
    if not isinstance(text, str) or not text.strip():
        return reasons + ["text is empty"]
    if len(text) > MAX_RULE_CHARS:
        reasons.append("text is longer than %d characters" % MAX_RULE_CHARS)
    if any(unicodedata.category(ch) in ("Cc", "Zl", "Zp") for ch in text):
        reasons.append("text must be one line without control characters")
    flat = normalize(text)
    if "<!--" in flat or "-->" in flat or any(normalize(marker) in flat for marker in MARKERS):
        reasons.append("text must not contain HTML comments or block markers")
    if flat.lstrip().startswith(("#", ">", "```", "---")):
        reasons.append("text must not start a heading, quote, fence or rule")
    project = rule.get("project")
    if project is not None and not (isinstance(project, str) and project.strip() and "\n" not in project):
        reasons.append("project must be null or a project name")
    return reasons


def safety_errors(text, source):
    """What may be learned from the journal; manual rules skip these."""
    if source == "manual":
        return []
    flat = normalize(text)
    # 再查一遍去掉空白的版本，拦「推 送」这类拆字写法。
    squeezed = re.sub(r"\s+", "", flat)
    reasons = []
    if SENSITIVE.search(flat) or SENSITIVE.search(squeezed):
        reasons.append("touches pushing, confirmation, publishing, secrets or permissions; only the user can add it (profile.py add)")
    if URL.search(flat) or COMMAND.search(flat):
        reasons.append("contains a URL or a command; only the user can add it (profile.py add)")
    if source == "learned" and LOOSEN.search(flat):
        reasons.append("loosening tests or review needs the user's own words (cite an explicit event)")
    return reasons


# ---------------------------------------------------------------- settle

def _day(value):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def _same_text(a, b):
    return normalize(a or "").split() == normalize(b or "").split()


def resolve(draft, current, events, on):
    """Turn a model draft into stored rules. Source, evidence and dates come from
    the stored profile and the cited journal events, never from the draft."""
    rules = draft.get("rules") if isinstance(draft, dict) else None
    if not isinstance(rules, list):
        return [], [{"id": None, "reason": "draft must be an object with a rules list"}]
    stored = {r["id"]: r for r in current}
    errors, out, seen = [], [], set()
    for item in rules:
        rid = item.get("id") if isinstance(item, dict) else None
        label = rid if isinstance(rid, str) else None
        problems = shape_errors(item)
        if label in seen:
            problems.append("duplicate id")
        seen.add(label)
        if problems:
            errors.extend({"id": label, "reason": p} for p in problems)
            continue
        old = stored.get(rid)
        refs = item.get("refs") or []
        if not isinstance(refs, list):
            errors.append({"id": rid, "reason": "refs must be a list of journal event ids"})
            continue
        rule = {"id": rid, "kind": item["kind"], "text": " ".join(item["text"].split()),
                "project": item.get("project") or None}
        same_text = bool(old) and _same_text(old["text"], item["text"])
        if same_text and not refs:
            rule.update({k: old[k] for k in ("source", "evidence", "created", "lastSeen")})
            rule["refs"] = list(old.get("refs") or [])
        elif old and old["source"] == "manual" and not same_text:
            errors.append({"id": rid, "reason": "rules the user added change only through add or forget"})
            continue
        else:
            used = set(old.get("refs") or []) if old else set()
            cited = [events.get(r) for r in refs]
            if not refs or any(c is None or c[0] not in EVIDENCE_EVENTS for c in cited):
                errors.append({"id": rid, "reason": "new or changed rules must cite existing correction or explicit events in refs"})
                continue
            if used & set(refs):
                errors.append({"id": rid, "reason": "refs already counted for this rule: %s" % sorted(used & set(refs))})
                continue
            sessions = {c[1] for c in cited}
            explicit = any(c[0] == "explicit" for c in cited)
            # 文字不变时只是加证据，来源保留；文字一改就按这次引用重算，不继承。
            earlier = old["evidence"] if same_text else 0
            if same_text and old["source"] in ("manual", "explicit"):
                source = old["source"]
            else:
                source = "explicit" if explicit else "learned"
            if source == "learned" and earlier + len(sessions) < MIN_SESSIONS:
                errors.append({"id": rid, "reason": "learned rules need corrections from at least %d sessions" % MIN_SESSIONS})
                continue
            rule.update({"source": source, "evidence": earlier + len(sessions),
                         "created": old["created"] if old else on.isoformat(), "lastSeen": on.isoformat(),
                         "refs": sorted(used | set(refs))[-USED_REFS_KEEP:],
                         "cited": [c[2] for c in cited]})
        problems = safety_errors(rule["text"], rule["source"])
        errors.extend({"id": rid, "reason": p} for p in problems)
        if not problems:
            out.append(rule)
    learnable = " ".join(r["text"] for r in out if r["source"] != "manual")
    if not errors and safety_errors(learnable, "explicit"):
        errors.append({"id": None, "reason": "taken together the rules touch pushing, confirmation, secrets or commands"})
    return out, errors


def render(rules):
    """Render the personal block body from global (project-less) rules."""
    active = [r for r in rules if not r.get("project")]
    if not active:
        return ""
    lines = ["## 个人习惯（自动学习，/reflect --show 查看来源）",
             "优先级：当次指令 > 项目规则 > 本节 > 上方通用规则。"]
    for kind in KINDS:
        texts = [" ".join(r["text"].split()).replace("<!--", "").replace("-->", "")
                 for r in active if r.get("kind") == kind]
        if texts:
            lines += ["", "### " + KIND_TITLES[kind]] + ["- " + text for text in texts]
    return "\n".join(lines)


def _strength(rule):
    return (rule.get("evidence") or 0, rule.get("lastSeen") or "")


def settle(rules, on):
    """Apply expiry and the size cap. Returns (kept, dropped, errors)."""
    dropped, kept, errors = [], [], []
    for rule in rules:
        seen = _day(rule.get("lastSeen")) or on
        if rule.get("source") == "learned" and (on - seen).days > EXPIRE_DAYS:
            dropped.append({"id": rule["id"], "reason": "no new evidence for %d days" % EXPIRE_DAYS})
        else:
            kept.append(rule)
    while estimate(render(kept)) > PERSONAL_LIMIT:
        learned = [r for r in kept if r.get("source") == "learned" and not r.get("project")]
        if not learned:
            errors.append({"id": None, "reason": "explicit and manual rules alone exceed %d tokens; shorten them" % PERSONAL_LIMIT})
            break
        weakest = min(learned, key=_strength)
        kept.remove(weakest)
        dropped.append({"id": weakest["id"], "reason": "over the %d token cap, weakest learned rule" % PERSONAL_LIMIT})
    return kept, dropped, errors


def check_stored(rules):
    """Re-check rules loaded from disk (history, hand edits) before writing them."""
    errors = []
    for rule in rules:
        rid = rule.get("id") if isinstance(rule, dict) else None
        problems = shape_errors(rule)
        if not problems:
            if rule.get("source") not in ("learned", "explicit", "manual"):
                problems.append("unknown source")
            else:
                problems = safety_errors(rule["text"], rule["source"])
        errors.extend({"id": rid if isinstance(rid, str) else None, "reason": p} for p in problems)
    return errors


def diff(old_rules, new_rules):
    old = {r["id"]: r for r in old_rules}
    new = {r["id"]: r for r in new_rules}
    return {
        "added": [new[i] for i in new if i not in old],
        "changed": [{"id": i, "before": old[i]["text"], "after": new[i]["text"]}
                    for i in new if i in old and old[i]["text"] != new[i]["text"]],
        "removed": [old[i] for i in old if i not in new],
    }


def plan(draft, directory=None, on=None):
    """Everything validate shows and apply writes, computed once."""
    directory = directory or home()
    on = on or today()
    profile = load_profile(directory)
    refs = [r for item in (draft.get("rules") or []) if isinstance(draft, dict) and isinstance(item, dict)
            for r in (item.get("refs") or []) if isinstance(item.get("refs"), list)] if isinstance(draft, dict) else []
    resolved, errors = resolve(draft, profile["rules"], load_events(refs, directory), on)
    # 引用的原话只给用户确认时看：规则和它的依据是否真的相关，由用户判断。
    evidence = {r["id"]: r.pop("cited") for r in resolved if "cited" in r}
    kept, dropped, cap_errors = settle(resolved, on) if not errors else ([], [], [])
    errors += cap_errors
    body = render(kept) if not errors else ""
    return {"ok": not errors, "errors": errors, "dropped": dropped,
            "diff": diff(profile["rules"], kept) if not errors else None,
            "evidence": evidence if not errors else {},
            "projectRules": [r for r in kept if r.get("project")],
            "enabled": profile["enabled"], "tokens": estimate(body), "limit": PERSONAL_LIMIT,
            "block": body, "rules": kept}


def validate(draft, directory=None):
    report = plan(draft, directory)
    report.pop("rules")
    return report


# ---------------------------------------------------------------- write

def _history(directory):
    return directory / "history"


def _stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def snapshot(directory, prefix="profile", data=None):
    """Save a profile (default: the current one, empty on first use) into history."""
    folder = _history(directory)
    folder.mkdir(mode=0o700, parents=True, exist_ok=True)
    target = folder / ("%s-%s.json" % (prefix, _stamp()))
    _write_private(target, load_profile(directory) if data is None else data)
    for old in sorted(folder.glob(prefix + "-*.json"))[:-HISTORY_KEEP]:
        old.unlink()
    return target


def _sync(body, host, paths):
    return gi.sync_personal(host, body, apply=True, home=paths.get("home") or Path.home(),
                            codex_home=paths.get("codex_home"), claude_config_dir=paths.get("claude_config_dir"))


def store(rules, host, directory, paths, enabled=None, note=None, learned=False):
    """Write the global block first, then profile.json; roll the block back on failure.

    Only a learning run (apply) moves `updated`, which is where the next collect starts;
    add, forget, undo, off and on keep it so no journal window is skipped."""
    previous = load_profile(directory)
    enabled = previous["enabled"] if enabled is None else enabled
    write = _sync(render(rules) if enabled else "", host, paths)
    updated = (datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
               if learned else previous.get("updated"))
    profile = {"schemaVersion": SCHEMA_VERSION, "updated": updated, "enabled": enabled, "rules": rules}
    try:
        _write_private(directory / "profile.json", profile)
    except Exception:
        _sync(render(previous["rules"]) if previous["enabled"] else "", host, paths)
        raise
    saved = snapshot(directory, data=previous)
    write.update({"backup": str(saved), "rules": len(rules), "enabled": enabled})
    if note:
        write["note"] = note
    return write


def apply(draft, host, directory=None, **paths):
    directory = directory or home()
    with locked(directory):
        report = plan(draft, directory)
        if not report["ok"]:
            report.pop("rules")
            return dict(report, applied=False)
        note = None if report["enabled"] else "personal block is off; rules saved but not written. Run on to turn it back on."
        write = store(report.pop("rules"), host, directory, paths, note=note, learned=True)
        return dict(report, applied=True, write=write)


def add(rule_id, kind, text, host, project=None, directory=None, **paths):
    """Add a rule the user dictated. Only shape and the size cap apply."""
    directory = directory or home()
    with locked(directory):
        rules = load_profile(directory)["rules"]
        rule = {"id": rule_id, "kind": kind, "text": text or "", "project": project or None,
                "source": "manual", "evidence": 1, "created": today().isoformat(), "lastSeen": today().isoformat()}
        problems = shape_errors(rule) + (["id already exists"] if any(r["id"] == rule_id for r in rules) else [])
        if problems:
            return {"ok": False, "errors": [{"id": rule_id, "reason": p} for p in problems]}
        rule["text"] = " ".join(rule["text"].split())
        kept, dropped, errors = settle(rules + [rule], today())
        if errors:
            return {"ok": False, "errors": errors}
        return {"ok": True, "dropped": dropped, "write": store(kept, host, directory, paths)}


def forget(rule_id, host, directory=None, **paths):
    directory = directory or home()
    with locked(directory):
        rules = load_profile(directory)["rules"]
        remaining = [r for r in rules if r.get("id") != rule_id]
        if len(remaining) == len(rules):
            return {"ok": False, "error": "no rule with id %s" % rule_id}
        return {"ok": True, "write": store(remaining, host, directory, paths)}


def undo(host, directory=None, **paths):
    """Restore the version before the last write. The undone version is kept as undone-*.json."""
    directory = directory or home()
    with locked(directory):
        folder = _history(directory)
        versions = sorted(folder.glob("profile-*.json")) if folder.exists() else []
        if not versions:
            return {"ok": False, "error": "no earlier version"}
        latest = versions[-1]
        data = json.loads(latest.read_text(encoding="utf-8"))
        rules = data.get("rules") if isinstance(data, dict) else None
        if not isinstance(rules, list):
            return {"ok": False, "error": "%s is not a profile" % latest.name}
        errors = check_stored(rules)
        if errors:
            # 移开它，下次撤销就能继续往前；文件保留，不删。
            aside = latest.with_name(latest.name.replace("profile-", "rejected-", 1))
            os.replace(str(latest), str(aside))
            return {"ok": False, "error": "%s does not pass the current checks; set aside as %s, run undo again to go further back"
                    % (latest.name, aside.name), "errors": errors}
        kept, dropped, cap_errors = settle(rules, today())
        if cap_errors:
            return {"ok": False, "errors": cap_errors}
        undone = snapshot(directory, prefix="undone")
        enabled = data.get("enabled", True)
        write = _sync(render(kept) if enabled else "", host, paths)
        _write_private(directory / "profile.json", dict(data, rules=kept, enabled=enabled,
                                                        updated=load_profile(directory).get("updated")))
        latest.unlink()
        return {"ok": True, "restored": latest.name, "undone": str(undone), "dropped": dropped, "write": write}


def switch(host, enabled, directory=None, **paths):
    directory = directory or home()
    with locked(directory):
        rules = load_profile(directory)["rules"]
        return {"ok": True, "write": store(rules, host, directory, paths, enabled=enabled)}


def off(host, directory=None, **paths):
    return switch(host, False, directory, **paths)


def on(host, directory=None, **paths):
    return switch(host, True, directory, **paths)


# ---------------------------------------------------------------- cli

HOSTS = ("codex", "claude-code", "cursor", "workbuddy")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("collect").add_argument("--since")
    sub.add_parser("show")
    sub.add_parser("render")
    sub.add_parser("validate").add_argument("draft")
    writers = {"apply": ["draft"], "forget": ["rule_id"], "undo": [], "off": [], "on": [], "add": []}
    for name, positional in writers.items():
        command = sub.add_parser(name)
        for argument in positional:
            command.add_argument(argument)
        if name == "add":
            command.add_argument("--id", required=True)
            command.add_argument("--kind", required=True, choices=KINDS)
            command.add_argument("--text", required=True)
            command.add_argument("--project")
        command.add_argument("--host", required=True, choices=HOSTS)
        command.add_argument("--home", type=Path, default=None)
        command.add_argument("--codex-home", type=Path, default=os.environ.get("CODEX_HOME") or None)
        command.add_argument("--claude-config-dir", type=Path, default=os.environ.get("CLAUDE_CONFIG_DIR") or None)
    args = parser.parse_args(argv)
    paths = {key: getattr(args, key, None) for key in ("home", "codex_home", "claude_config_dir")}
    try:
        if args.command == "collect":
            result = collect(args.since)
        elif args.command == "show":
            result = load_profile()
        elif args.command == "render":
            profile = load_profile()
            result = {"enabled": profile["enabled"], "block": render(profile["rules"])}
        elif args.command in ("validate", "apply"):
            draft = json.loads(Path(args.draft).read_text(encoding="utf-8"))
            result = validate(draft) if args.command == "validate" else apply(draft, args.host, **paths)
        elif args.command == "add":
            result = add(args.id, args.kind, args.text, args.host, args.project, **paths)
        elif args.command == "forget":
            result = forget(args.rule_id, args.host, **paths)
        elif args.command == "undo":
            result = undo(args.host, **paths)
        else:
            result = (off if args.command == "off" else on)(args.host, **paths)
    except (gi.ConfigurationError, OSError, ValueError, TypeError, KeyError) as error:
        result = {"ok": False, "error": "%s: %s" % (type(error).__name__, error)}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok", True) is not False else 1


if __name__ == "__main__":
    sys.exit(main())
