"""Shared layout rules for the s-skills plugin marketplace.

Plugin versions live only in each plugin's manifest files. Marketplace
entries do not repeat the version: Claude Code and CodeBuddy use the copy
in plugin.json, and they warn if the two disagree.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGINS_DIR = ROOT / "plugins"
LOCK_PATH = ROOT / "plugin-versions.lock.json"

PLUGIN_ORDER = ("s",)

EXPECTED_SKILL_COUNTS = {
    "s": 60,
}

# Skills kept under archive/<plugin>/, outside the plugin package.
EXPECTED_ARCHIVED_COUNTS = {
    "s": 39,
}

MANIFEST_REL_PATHS = (
    "plugin.json",
    ".cursor-plugin/plugin.json",
    ".claude-plugin/plugin.json",
    ".codebuddy-plugin/plugin.json",
)

SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
KEBAB_RE = re.compile(r"^[a-z0-9]([a-z0-9.-]*[a-z0-9])?$")
CLAUDE_NAME_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?$")
AGENT_NAME_RE = re.compile(r"^(?!.*(?:--|\\.\\.))[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$")

REPO_URL = "https://github.com/Acefake/s-skills"
MARKETPLACE_NAME = "s-skills"


def plugin_dir(name: str) -> Path:
    return PLUGINS_DIR / name


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def content_hash(name: str) -> str:
    """Hash everything in the plugin except the four manifest files.

    Manifests hold the version string. Leaving them out means a version bump
    does not look like a content change, and a content change does not hide
    inside a manifest edit.
    """
    root = plugin_dir(name)
    excluded = set(MANIFEST_REL_PATHS)
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if rel in excluded:
            continue
        files.append(path)
    digest = hashlib.sha256()
    for path in sorted(files, key=lambda item: item.relative_to(root).as_posix()):
        rel = path.relative_to(root).as_posix()
        data = path.read_bytes()
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return digest.hexdigest()


def manifest_paths(name: str) -> list[Path]:
    return [plugin_dir(name) / rel for rel in MANIFEST_REL_PATHS]


def manifest_version(path: Path) -> str:
    data = read_json(path)
    if not isinstance(data, dict) or not isinstance(data.get("version"), str):
        raise ValueError(f"{path} is missing a string version")
    return data["version"]


def set_manifest_version(path: Path, version: str) -> None:
    data = read_json(path)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    data["version"] = version
    write_json(path, data)


def load_lock() -> dict:
    data = read_json(LOCK_PATH)
    if not isinstance(data, dict) or not isinstance(data.get("plugins"), dict):
        raise ValueError("plugin-versions.lock.json is missing a plugins object")
    return data


def bump_patch(version: str) -> str:
    match = SEMVER_RE.fullmatch(version)
    if not match:
        raise ValueError(f"version {version!r} is not X.Y.Z")
    major, minor, patch = (int(part) for part in match.groups())
    return f"{major}.{minor}.{patch + 1}"


def frontmatter_name(text: str) -> str | None:
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    block = text[3:end]
    match = re.search(r"^name:\s*(.+?)\s*$", block, re.M)
    if not match:
        return None
    value = match.group(1)
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        value = value[1:-1]
    return value


def skill_dirs(name: str) -> list[Path]:
    skills_root = plugin_dir(name) / "skills"
    found = []
    if not skills_root.is_dir():
        return found
    for child in sorted(skills_root.iterdir(), key=lambda item: item.name):
        if child.is_dir() and (child / "SKILL.md").is_file():
            found.append(child)
    return found
