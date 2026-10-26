#!/usr/bin/env python3
"""Check marketplace manifests, plugin versions, and skill layout.

Schemas copied into scripts/schemas/:

- cursor marketplace and plugin: https://github.com/cursor/plugins/tree/main/schemas
  (fetched 2026-10-18 from raw.githubusercontent.com/cursor/plugins/main/schemas/)
- portable plugin: https://agent-plugins.org/schemas/1.0.0/plugin.schema.json

Claude Code and CodeBuddy do not publish a machine-readable marketplace
schema. Those checks follow the field rules in the official docs.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from jsonschema import Draft7Validator, Draft202012Validator, FormatChecker

from marketplace_lib import (
    AGENT_NAME_RE,
    CLAUDE_NAME_RE,
    RETIRED_SKILLS,
    EXPECTED_SKILL_COUNTS,
    KEBAB_RE,
    LOCK_PATH,
    MARKETPLACE_NAME,
    PLUGIN_ORDER,
    ROOT,
    SEMVER_RE,
    content_hash,
    frontmatter_name,
    load_lock,
    manifest_paths,
    manifest_version,
    plugin_dir,
    read_json,
    skill_dirs,
)

SCHEMAS = Path(__file__).resolve().parent / "schemas"
FORMAT_CHECKER = FormatChecker()


class Problems:
    def __init__(self) -> None:
        self.items: list[str] = []

    def add(self, message: str) -> None:
        self.items.append(message)

    def ok(self) -> bool:
        return not self.items


def validator_for(schema: dict):
    schema_id = schema.get("$schema", "")
    kind = Draft202012Validator if "2020-12" in schema_id else Draft7Validator
    return kind(schema, format_checker=FORMAT_CHECKER)


def validate_schema(problems: Problems, label: str, schema_name: str, instance: object) -> None:
    schema = json.loads((SCHEMAS / schema_name).read_text(encoding="utf-8"))
    errors = sorted(validator_for(schema).iter_errors(instance), key=lambda err: list(err.path))
    for err in errors:
        location = "/".join(str(part) for part in err.absolute_path) or "(root)"
        problems.add(f"{label} {location}: {err.message}")


def check_versions(problems: Problems) -> None:
    if not LOCK_PATH.is_file():
        problems.add("missing plugin-versions.lock.json")
        return
    try:
        lock = load_lock()
    except ValueError as exc:
        problems.add(str(exc))
        return
    locked = lock["plugins"]
    if tuple(locked) != PLUGIN_ORDER:
        problems.add(
            "plugin-versions.lock.json plugin order is "
            + ", ".join(locked)
            + "; expected "
            + ", ".join(PLUGIN_ORDER)
        )
    for name in PLUGIN_ORDER:
        entry = locked.get(name)
        if not isinstance(entry, dict):
            problems.add(f"{name}: lock entry missing")
            continue
        version = entry.get("version")
        recorded = entry.get("contentSha256")
        if not isinstance(version, str) or not SEMVER_RE.fullmatch(version):
            problems.add(f"{name}: lock version {version!r} is not X.Y.Z")
        actual_hash = content_hash(name)
        if recorded != actual_hash:
            problems.add(
                f"{name}: skill/content hash changed but the version lock was not updated. "
                f"Run: python3 scripts/bump_plugin_version.py {name}"
            )
        for path in manifest_paths(name):
            if not path.is_file():
                problems.add(f"missing {path.relative_to(ROOT)}")
                continue
            try:
                found = manifest_version(path)
            except ValueError as exc:
                problems.add(str(exc))
                continue
            if found != version:
                problems.add(
                    f"{path.relative_to(ROOT)} version is {found}, lock says {version}"
                )


def check_cursor_marketplace(problems: Problems) -> None:
    path = ROOT / ".cursor-plugin" / "marketplace.json"
    data = read_json(path)
    validate_schema(problems, "cursor marketplace", "cursor-marketplace.schema.json", data)
    if not isinstance(data, dict):
        return
    if data.get("name") != MARKETPLACE_NAME:
        problems.add("cursor marketplace name is not s-skills")
    plugins = data.get("plugins")
    if not isinstance(plugins, list):
        return
    names = [item.get("name") for item in plugins if isinstance(item, dict)]
    if names != list(PLUGIN_ORDER):
        problems.add(f"cursor marketplace plugin list is {names}")
    for item in plugins:
        if not isinstance(item, dict):
            continue
        source = item.get("source")
        if source != f"plugins/{item.get('name')}":
            problems.add(f"cursor source for {item.get('name')} is {source!r}")


def check_host_marketplace(problems: Problems, relative: str, label: str) -> None:
    path = ROOT / relative
    data = read_json(path)
    if not isinstance(data, dict):
        problems.add(f"{label} marketplace is not an object")
        return
    name = data.get("name")
    if name != MARKETPLACE_NAME or not isinstance(name, str) or not CLAUDE_NAME_RE.fullmatch(name) or ".." in name:
        problems.add(f"{label} marketplace name {name!r} is not an allowed identifier")
    owner = data.get("owner")
    if not isinstance(owner, dict) or not isinstance(owner.get("name"), str) or not owner.get("name"):
        problems.add(f"{label} marketplace owner.name is missing")
    plugins = data.get("plugins")
    if not isinstance(plugins, list):
        problems.add(f"{label} marketplace plugins is missing")
        return
    names = []
    for item in plugins:
        if not isinstance(item, dict):
            problems.add(f"{label} plugin entry is not an object")
            continue
        plugin_name = item.get("name")
        names.append(plugin_name)
        if not isinstance(plugin_name, str) or not CLAUDE_NAME_RE.fullmatch(plugin_name) or ".." in plugin_name:
            problems.add(f"{label} plugin name {plugin_name!r} is not allowed")
        source = item.get("source")
        expected = f"./plugins/{plugin_name}"
        if source != expected:
            problems.add(f"{label} source for {plugin_name} is {source!r}, expected {expected}")
        elif ".." in source:
            problems.add(f"{label} source {source} contains ..")
        description = item.get("description")
        if not isinstance(description, str) or not description.strip():
            problems.add(f"{label} plugin {plugin_name} is missing description")
        if "version" in item:
            problems.add(
                f"{label} plugin {plugin_name} sets version in the marketplace entry. "
                "Keep the version only in plugin.json."
            )
    if names != list(PLUGIN_ORDER):
        problems.add(f"{label} plugin list is {names}")


def check_codex_marketplace(problems: Problems) -> None:
    path = ROOT / ".agents" / "plugins" / "marketplace.json"
    data = read_json(path)
    if not isinstance(data, dict):
        problems.add("codex marketplace is not an object")
        return
    if data.get("name") != MARKETPLACE_NAME:
        problems.add("codex marketplace name is not s-skills")
    interface = data.get("interface")
    if not isinstance(interface, dict) or not interface.get("displayName"):
        problems.add("codex marketplace interface.displayName is missing")
    plugins = data.get("plugins")
    if not isinstance(plugins, list):
        problems.add("codex marketplace plugins is missing")
        return
    names = []
    for item in plugins:
        if not isinstance(item, dict):
            problems.add("codex plugin entry is not an object")
            continue
        plugin_name = item.get("name")
        names.append(plugin_name)
        if not isinstance(plugin_name, str) or not KEBAB_RE.fullmatch(plugin_name):
            problems.add(f"codex plugin name {plugin_name!r} is not kebab-case")
        source = item.get("source")
        expected_path = f"./plugins/{plugin_name}"
        if not isinstance(source, dict) or source.get("source") != "local" or source.get("path") != expected_path:
            problems.add(f"codex source for {plugin_name} is {source!r}")
        policy = item.get("policy")
        if not isinstance(policy, dict):
            problems.add(f"codex policy for {plugin_name} is missing")
        else:
            if policy.get("installation") != "AVAILABLE":
                problems.add(f"codex installation policy for {plugin_name} is {policy.get('installation')!r}")
            if policy.get("authentication") not in {"ON_INSTALL", "ON_USE"}:
                problems.add(f"codex auth policy for {plugin_name} is {policy.get('authentication')!r}")
        if item.get("category") != "Productivity":
            problems.add(f"codex category for {plugin_name} is {item.get('category')!r}")
    if names != list(PLUGIN_ORDER):
        problems.add(f"codex plugin list is {names}")


def check_plugin_manifests(problems: Problems) -> None:
    cursor_schema = "cursor-plugin.schema.json"
    agent_schema = "agent-plugin.schema.json"
    for name in PLUGIN_ORDER:
        cursor_path = plugin_dir(name) / ".cursor-plugin" / "plugin.json"
        claude_path = plugin_dir(name) / ".claude-plugin" / "plugin.json"
        codebuddy_path = plugin_dir(name) / ".codebuddy-plugin" / "plugin.json"
        portable_path = plugin_dir(name) / "plugin.json"
        cursor = read_json(cursor_path)
        validate_schema(problems, f"{name} cursor plugin", cursor_schema, cursor)
        portable = read_json(portable_path)
        validate_schema(problems, f"{name} portable plugin", agent_schema, portable)
        for label, path in (
            ("claude", claude_path),
            ("codebuddy", codebuddy_path),
            ("cursor", cursor_path),
            ("portable", portable_path),
        ):
            data = read_json(path)
            if not isinstance(data, dict):
                problems.add(f"{name} {label} manifest is not an object")
                continue
            if data.get("name") != name:
                problems.add(f"{name} {label} manifest name is {data.get('name')!r}")
            if label == "portable" and not AGENT_NAME_RE.fullmatch(str(data.get("name", ""))):
                problems.add(f"{name} portable name fails the agent plugin pattern")
            if label != "portable" and not KEBAB_RE.fullmatch(str(data.get("name", ""))):
                problems.add(f"{name} {label} name fails kebab-case")
        if isinstance(portable, dict):
            schema_id = portable.get("$schema")
            if schema_id != "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json":
                problems.add(f"{name} portable $schema is {schema_id!r}")
        # Claude and CodeBuddy manifests stay in lockstep, apart from nothing.
        if read_json(claude_path) != read_json(codebuddy_path):
            problems.add(f"{name}: claude and codebuddy plugin.json differ")


DESCRIPTION_RE = re.compile(
    r"^(?!中文：)(?!中文触发：)(?!Use when ).+[。！？]Use when .+[.!?]$"
)


def frontmatter_block(text: str) -> str:
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    return text[3:end] if end != -1 else ""


def frontmatter_description(text: str) -> str | None:
    match = re.search(r"^description:[ \t]*(.*)$", frontmatter_block(text), re.M)
    if not match:
        return None
    raw = match.group(1).strip()
    if len(raw) >= 2 and raw[0] == raw[-1] == '"':
        try:
            value = json.loads(raw)
        except json.JSONDecodeError:
            return raw
        return value if isinstance(value, str) else raw
    if len(raw) >= 2 and raw[0] == raw[-1] == "'":
        return raw[1:-1].replace("''", "'")
    return raw


def description_order_problem(desc: str) -> str | None:
    if not DESCRIPTION_RE.fullmatch(desc):
        return "description must start with the Chinese sentence, then Use when …."
    return None


def description_trigger_problem(desc: str) -> str | None:
    """Skill lists truncate. The phrases a person would say have to lead."""
    if not desc.startswith("「"):
        return "description must start with a quoted Chinese user phrase"
    if "」" not in desc[:100]:
        return "description must close a quoted user phrase within the first 100 characters"
    return None


def check_description(label: str, text: str, problems: Problems) -> None:
    desc = frontmatter_description(text)
    if desc is None:
        problems.add(f"{label}: SKILL.md is missing frontmatter description")
        return
    issue = description_order_problem(desc)
    if issue:
        problems.add(f"{label}: {issue}")


def check_agent_descriptions(problems: Problems) -> None:
    root = ROOT / "plugins" / "s-atlas" / "agents"
    found = sorted(path for path in root.glob("*.md")) if root.is_dir() else []
    if len(found) != 2:
        problems.add(f"plugins/s-atlas/agents: found {len(found)} agents, expected 2")
    for path in found:
        text = path.read_text(encoding="utf-8")
        check_description(f"plugins/s-atlas/agents/{path.name}", text, problems)


def check_skills(problems: Problems) -> None:
    seen_names: dict[str, str] = {}
    for name in PLUGIN_ORDER:
        found = skill_dirs(name)
        expected = EXPECTED_SKILL_COUNTS[name]
        if len(found) != expected:
            problems.add(f"{name}: found {len(found)} skills, expected {expected}")
        skills_root = plugin_dir(name) / "skills"
        for skill in found:
            text = (skill / "SKILL.md").read_text(encoding="utf-8")
            check_skill_resources(skill, text, problems)
            skill_name = frontmatter_name(text)
            check_description(f"{name}/{skill.name}", text, problems)
            desc = frontmatter_description(text)
            if desc and (issue := description_trigger_problem(desc)):
                problems.add(f"{name}/{skill.name}: {issue}")
            if not skill_name:
                problems.add(f"{name}/{skill.name}: SKILL.md is missing frontmatter name")
                continue
            if skill_name != skill.name:
                problems.add(
                    f"{name}/{skill.name}: frontmatter name is {skill_name!r}"
                )
            previous = seen_names.get(skill_name)
            if previous:
                problems.add(f"duplicate skill name {skill_name!r} in {previous} and {name}/{skill.name}")
            seen_names[skill_name] = f"{name}/{skill.name}"
            for match in __import__("re").finditer(r"上一级文件夹的 `([^`]+)`", text):
                license_name = match.group(1)
                if not (skills_root / license_name).is_file():
                    problems.add(
                        f"{name}/{skill.name} points at {license_name}, "
                        "which is not in the skill parent folder"
                    )


def check_skill_resources(skill: Path, text: str, problems: Problems) -> None:
    end = text.find("\n---", 3)
    frontmatter = text[3:end] if text.startswith("---") and end != -1 else ""
    disabled = bool(re.search(r"^disable-model-invocation:\s*true\s*$", frontmatter, re.M))
    policy = skill / "agents/openai.yaml"
    if not policy.is_file():
        problems.add(f"{skill.name}: missing Codex invocation policy")
    else:
        match = re.search(r"^  allow_implicit_invocation: (true|false)\s*$", policy.read_text(encoding="utf-8"), re.M)
        if not match or (match.group(1) == "true") == disabled:
            problems.add(f"{skill.name}: Codex and frontmatter invocation policies disagree")
    # 代码块和行内代码里的链接是示例，不当成本地文件检查。
    prose = re.sub(r"`[^`\n]*`", "", re.sub(r"```.*?```", "", text, flags=re.S))
    for target in re.findall(r"\]\(([^)]+)\)", prose):
        if "://" in target or target.startswith("#"):
            continue
        local = target.split("#", 1)[0]
        if local and not (skill / local).exists():
            problems.add(f"{skill.name}: broken local link {target}")


# A skill is named in backticks, in bold, or as a /s-atlas: command.
SKILL_NAME_RES = (
    re.compile(r"`([a-z0-9]+(?:-[a-z0-9]+)+)`"),
    re.compile(r"\*\*([a-z0-9]+(?:-[a-z0-9]+)+)\*\*"),
    re.compile(r"/s-atlas:([a-z0-9]+(?:-[a-z0-9]+)+)"),
)


def skill_reference_problems(text: str, active: set[str], archived: set[str]) -> list[str]:
    """Return references to retired skills, or principles missing their prefix."""
    found: list[str] = []
    for pattern in SKILL_NAME_RES:
        for match in pattern.finditer(text):
            name = match.group(1)
            if name in archived and name not in active:
                found.append(f"names retired skill `{name}`")
            elif name not in active and f"principle-{name}" in active:
                found.append(f"names `{name}` without the principle- prefix")
    return found


def check_skill_references(problems: Problems) -> None:
    skills_root = ROOT / "plugins" / "s-atlas" / "skills"
    active = {path.name for path in skills_root.iterdir() if path.is_dir()}
    archived = set(RETIRED_SKILLS)
    for path in sorted(skills_root.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        for problem in skill_reference_problems(text, active, archived):
            problems.add(f"{path.relative_to(ROOT)}: {problem}")


def main() -> int:
    problems = Problems()
    try:
        check_versions(problems)
        check_cursor_marketplace(problems)
        check_host_marketplace(problems, ".claude-plugin/marketplace.json", "claude")
        check_host_marketplace(problems, ".codebuddy-plugin/marketplace.json", "codebuddy")
        check_codex_marketplace(problems)
        check_plugin_manifests(problems)
        check_skills(problems)
        check_skill_references(problems)
        check_agent_descriptions(problems)
    except FileNotFoundError as exc:
        problems.add(f"missing file: {exc.filename}")
    except json.JSONDecodeError as exc:
        problems.add(f"invalid JSON: {exc}")
    if problems.ok():
        total = sum(EXPECTED_SKILL_COUNTS.values())
        print(f"marketplace check passed ({total} skills, {len(PLUGIN_ORDER)} plugins)")
        return 0
    print(f"marketplace check failed ({len(problems.items)} problems):", file=sys.stderr)
    for item in problems.items:
        print(f"- {item}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
