#!/usr/bin/env python3
"""Personal rules for the wukong learning layer: collect, validate, apply, undo.

The model does the judgment (grouping corrections into rules); this script does
everything that must be exact: reading the local journal, enforcing the
admission, expiry, safety and size rules, keeping backups, and writing the
personal block through setup-s-instructions.

    profile.py collect [--since YYYY-MM-DD]
    profile.py validate DRAFT.json
    profile.py apply DRAFT.json --host HOST
    profile.py show | render
    profile.py forget RULE_ID --host HOST
    profile.py undo --host HOST
    profile.py off --host HOST

Data lives in ~/.wukong (or $WUKONG_HOME): profile.json is the source of truth,
history/ keeps the 20 most recent versions. Every command prints one JSON object.
"""
import argparse
import json
import os
import re
import sys
import tempfile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PLUGIN / "hooks"))
sys.path.insert(0, str(PLUGIN / "skills/setup-s-instructions/scripts"))
import journal  # noqa: E402
import global_instructions  # noqa: E402

SCHEMA_VERSION = 1
# 与 scripts/context_budget.py 的 PERSONAL_LIMIT 保持一致（有测试核对）。
PERSONAL_LIMIT = 500
EXPIRE_DAYS = 56
HISTORY_KEEP = 20
MIN_EVIDENCE = 2
MAX_RULE_CHARS = 120
COLLECT_LIMIT = 60
KINDS = ("style", "route", "verify", "habit")
SOURCES = ("learned", "explicit", "manual")
KIND_TITLES = {"style": "回复", "route": "技能", "verify": "验证与审查", "habit": "习惯"}
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,39}$")
CJK = re.compile(r"[\u3000-\u303f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff00-\uffef]")

# 放宽权限、跳过确认、碰安全的规则不能从对话里学，只能用户亲口说（source=manual）。
SENSITIVE = re.compile(
    r"推送|\bpush\b|强制|--force|--no-verify|跳过(钩子|hook|检查|确认)|reset\s+--hard|git\s+clean|rm\s+-rf"
    r"|删除(文件|分支|目录|数据|仓库)|不用(问|确认|请示)|无需确认|别问我|直接(提交|推送|合并|删除|发布)"
    r"|自动(提交|推送|合并|发布)|密钥|secret|token|password|密码|凭据|权限|sudo|安全(检查|审查)",
    re.IGNORECASE,
)
URL = re.compile(r"https?://", re.IGNORECASE)
COMMAND = re.compile(r"`\s*(git|rm|curl|wget|npm|pnpm|yarn|pip|sudo|chmod|chown|docker|kubectl)\b", re.IGNORECASE)
# 验证与审查只能从纠正里学「收紧」；「放松」必须是用户明说。
LOOSEN = re.compile(r"不跑|别跑|不用跑|跳过|不派|别派|不用派|不审|不用审|不用测|少测|不写测试|不测")


def estimate(text):
    cjk = len(CJK.findall(text))
    return cjk + (len(text) - cjk + 3) // 4


def home():
    return journal.journal_dir()


def today():
    return date.today()


def empty_profile():
    return {"schemaVersion": SCHEMA_VERSION, "updated": None, "rules": []}


def load_profile(directory=None):
    path = (directory or home()) / "profile.json"
    if not path.exists():
        return empty_profile()
    data = json.loads(path.read_text(encoding="utf-8"))
    data.setdefault("rules", [])
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


# ---------------------------------------------------------------- collect

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
    result = {"since": since.isoformat(timespec="seconds"), "rules": profile["rules"],
              "corrections": [], "explicit": [], "sessions": 0, "skills": {}}
    path = directory / "journal.db"
    if journal.sqlite3 is None or not path.exists():
        return result
    conn = journal.sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True, timeout=journal.LOCK_TIMEOUT)
    try:
        at = int(since.timestamp())
        result["sessions"] = conn.execute(
            "SELECT count(DISTINCT session) FROM events WHERE at >= ? AND session != ''", (at,)).fetchone()[0]
        for kind, key in (("correction", "corrections"), ("explicit", "explicit")):
            rows = conn.execute(
                "SELECT ts, session, project, text FROM events WHERE event = ? AND at >= ? ORDER BY at DESC LIMIT ?",
                (kind, at, COLLECT_LIMIT)).fetchall()
            result[key] = [dict(zip(("ts", "session", "project", "text"), row)) for row in reversed(rows)]
        result["skills"] = dict(conn.execute(
            "SELECT name, count(*) FROM events WHERE event = 'skill' AND at >= ? GROUP BY name ORDER BY count(*) DESC",
            (at,)).fetchall())
    finally:
        conn.close()
    return result


# ---------------------------------------------------------------- validate

def _parse_day(value):
    return date.fromisoformat(value) if isinstance(value, str) else None


def check_rule(rule):
    """Return a list of reasons this rule cannot be stored."""
    reasons = []
    if not isinstance(rule, dict):
        return ["rule is not an object"]
    if not ID_RE.match(str(rule.get("id", ""))):
        reasons.append("id must be lowercase letters, digits and dashes, at most 40 characters")
    if rule.get("kind") not in KINDS:
        reasons.append("kind must be one of " + ", ".join(KINDS))
    source = rule.get("source")
    if source not in SOURCES:
        reasons.append("source must be one of " + ", ".join(SOURCES))
    text = rule.get("text")
    if not isinstance(text, str) or not text.strip():
        reasons.append("text is empty")
        text = ""
    elif len(text) > MAX_RULE_CHARS:
        reasons.append("text is longer than %d characters" % MAX_RULE_CHARS)
    evidence = rule.get("evidence")
    if not isinstance(evidence, int) or evidence < 1:
        reasons.append("evidence must be a positive integer")
    elif source == "learned" and evidence < MIN_EVIDENCE:
        reasons.append("learned rules need evidence from at least %d sessions" % MIN_EVIDENCE)
    for field in ("created", "lastSeen"):
        try:
            if _parse_day(rule.get(field)) is None:
                raise ValueError
        except ValueError:
            reasons.append(field + " must be YYYY-MM-DD")
    project = rule.get("project")
    if project is not None and not (isinstance(project, str) and project.strip()):
        reasons.append("project must be null or a project name")
    if source != "manual":
        if SENSITIVE.search(text):
            reasons.append("touches permissions, confirmation or security; only the user can add it (source manual)")
        if URL.search(text) or COMMAND.search(text):
            reasons.append("contains a URL or a command; only the user can add it (source manual)")
    if rule.get("kind") == "verify" and source == "learned" and LOOSEN.search(text):
        reasons.append("loosening verification or review needs the user's explicit words (source explicit)")
    return reasons


def render(rules):
    """Render the personal block body from global (project-less) rules."""
    active = [r for r in rules if not r.get("project")]
    if not active:
        return ""
    lines = ["## 个人习惯（自动学习，/reflect --show 查看来源）",
             "优先级：当次指令 > 项目规则 > 本节 > 上方通用规则。"]
    for kind in KINDS:
        texts = [r["text"].strip() for r in active if r.get("kind") == kind]
        if texts:
            lines.append("")
            lines.append("### " + KIND_TITLES[kind])
            lines.extend("- " + text for text in texts)
    return "\n".join(lines)


def _strength(rule):
    return (rule.get("evidence") or 0, rule.get("lastSeen") or "")


def settle(draft, on=None):
    """Validate a draft profile and apply expiry and the size cap.

    Returns (rules to store, errors, dropped). Errors block writing; dropped
    rules are removed automatically (expired, or the weakest learned rules
    when the rendered block is over PERSONAL_LIMIT).
    """
    on = on or today()
    rules = draft.get("rules") if isinstance(draft, dict) else None
    if not isinstance(rules, list):
        return [], [{"id": None, "reason": "draft must be an object with a rules list"}], []
    errors, seen = [], set()
    for rule in rules:
        rid = rule.get("id") if isinstance(rule, dict) else None
        for reason in check_rule(rule):
            errors.append({"id": rid, "reason": reason})
        if rid in seen:
            errors.append({"id": rid, "reason": "duplicate id"})
        seen.add(rid)
    if errors:
        return rules, errors, []
    dropped, kept = [], []
    for rule in rules:
        stale = (on - _parse_day(rule["lastSeen"])).days > EXPIRE_DAYS
        if rule["source"] == "learned" and stale:
            dropped.append({"id": rule["id"], "reason": "no new evidence for %d days" % EXPIRE_DAYS})
        else:
            kept.append(rule)
    while estimate(render(kept)) > PERSONAL_LIMIT:
        learned = [r for r in kept if r["source"] == "learned" and not r.get("project")]
        if not learned:
            errors.append({"id": None, "reason": "explicit and manual rules alone exceed %d tokens; shorten them" % PERSONAL_LIMIT})
            break
        weakest = min(learned, key=_strength)
        kept.remove(weakest)
        dropped.append({"id": weakest["id"], "reason": "over the %d token cap, weakest learned rule" % PERSONAL_LIMIT})
    return kept, errors, dropped


def diff(old_rules, new_rules):
    old = {r["id"]: r for r in old_rules}
    new = {r["id"]: r for r in new_rules}
    return {
        "added": [new[i] for i in new if i not in old],
        "changed": [{"id": i, "before": old[i]["text"], "after": new[i]["text"]}
                    for i in new if i in old and old[i]["text"] != new[i]["text"]],
        "removed": [old[i] for i in old if i not in new],
    }


def validate(draft, directory=None):
    current = load_profile(directory)["rules"]
    kept, errors, dropped = settle(draft)
    body = render(kept) if not errors else ""
    return {"ok": not errors, "errors": errors, "dropped": dropped,
            "diff": diff(current, kept) if not errors else None,
            "projectRules": [r for r in kept if r.get("project")],
            "tokens": estimate(body), "limit": PERSONAL_LIMIT, "block": body}


# ---------------------------------------------------------------- write

def _history(directory):
    return directory / "history"


def backup(directory):
    path = directory / "profile.json"
    if not path.exists():
        return None
    folder = _history(directory)
    folder.mkdir(mode=0o700, parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    target = folder / ("profile-%s.json" % stamp)
    target.write_bytes(path.read_bytes())
    os.chmod(str(target), 0o600)
    for old in sorted(folder.glob("profile-*.json"))[:-HISTORY_KEEP]:
        old.unlink()
    return target


def write_block(rules, host, **paths):
    return global_instructions.sync_personal(host, render(rules), apply=True, home=paths.get("home") or Path.home(),
                                             codex_home=paths.get("codex_home"),
                                             claude_config_dir=paths.get("claude_config_dir"))


def store(rules, host, directory=None, **paths):
    directory = directory or home()
    saved = backup(directory)
    profile = {"schemaVersion": SCHEMA_VERSION,
               "updated": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
               "rules": rules}
    _write_private(directory / "profile.json", profile)
    result = write_block(rules, host, **paths)
    result["backup"] = str(saved) if saved else None
    result["rules"] = len(rules)
    return result


def apply(draft, host, directory=None, **paths):
    report = validate(draft, directory)
    if not report["ok"]:
        return dict(report, applied=False)
    kept, _, _ = settle(draft)
    return dict(report, applied=True, write=store(kept, host, directory, **paths))


def forget(rule_id, host, directory=None, **paths):
    rules = load_profile(directory)["rules"]
    remaining = [r for r in rules if r.get("id") != rule_id]
    if len(remaining) == len(rules):
        return {"ok": False, "error": "no rule with id %s" % rule_id}
    return {"ok": True, "write": store(remaining, host, directory, **paths)}


def undo(host, directory=None, **paths):
    directory = directory or home()
    versions = sorted(_history(directory).glob("profile-*.json")) if _history(directory).exists() else []
    if not versions:
        return {"ok": False, "error": "no earlier version"}
    latest = versions[-1]
    data = json.loads(latest.read_text(encoding="utf-8"))
    _write_private(directory / "profile.json", data)
    latest.unlink()
    return {"ok": True, "restored": latest.name, "write": write_block(data.get("rules", []), host, **paths)}


def off(host, **paths):
    result = global_instructions.sync_personal(host, "", apply=True, home=paths.get("home") or Path.home(),
                                               codex_home=paths.get("codex_home"),
                                               claude_config_dir=paths.get("claude_config_dir"))
    return {"ok": True, "write": result}


# ---------------------------------------------------------------- cli

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    collect_cmd = sub.add_parser("collect")
    collect_cmd.add_argument("--since")
    sub.add_parser("show")
    sub.add_parser("render")
    for name, extra in (("validate", "draft"), ("apply", "draft"), ("forget", "rule_id"), ("undo", None), ("off", None)):
        command = sub.add_parser(name)
        if extra:
            command.add_argument(extra)
        if name != "validate":
            command.add_argument("--host", required=True, choices=("codex", "claude-code", "cursor", "workbuddy"))
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
            result = {"block": render(load_profile()["rules"])}
        elif args.command in ("validate", "apply"):
            draft = json.loads(Path(args.draft).read_text(encoding="utf-8"))
            result = validate(draft) if args.command == "validate" else apply(draft, args.host, **paths)
        elif args.command == "forget":
            result = forget(args.rule_id, args.host, **paths)
        elif args.command == "undo":
            result = undo(args.host, **paths)
        else:
            result = off(args.host, **paths)
    except (global_instructions.ConfigurationError, OSError, ValueError) as error:
        result = {"ok": False, "error": str(error)}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok", True) is not False else 1


if __name__ == "__main__":
    sys.exit(main())
