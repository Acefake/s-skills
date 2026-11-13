#!/usr/bin/env python3
"""Estimate the tokens wukong keeps resident in every session, and cap them.

Resident means loaded whether or not any skill runs: the name and description
of every auto-invocable skill, the global rules block from AGENTS.md, the line
the SessionStart hook adds, and the note the prompt-sharpen hook adds to each
user message. Explicit skills cost nothing until named, so they are skipped.

The estimate counts one token per CJK character and one per four other
characters. It tracks trends between versions; it is not a tokenizer.

    python3 scripts/context_budget.py           # table, largest first
    python3 scripts/context_budget.py --json
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/wukong"
SKILLS = PLUGIN / "skills"

# 上限取 1.0.17 实测值（约 5380）加 5%。要调高，先说明多出来的常驻内容值不值。
RESIDENT_LIMIT = 5650
# 个人块（个人学习层）的上限，由 reflect 的 profile.py 校验，这里只登记。
PERSONAL_LIMIT = 500

CJK = re.compile(r"[\u3000-\u303f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff00-\uffef]")


def estimate(text: str) -> int:
    cjk = len(CJK.findall(text))
    other = len(text) - cjk
    return cjk + (other + 3) // 4


def _frontmatter(text: str) -> str:
    end = text.find("\n---", 3)
    return text[3:end] if text.startswith("---") and end != -1 else ""


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def measure() -> list[tuple[str, int]]:
    """Return (label, estimated tokens) for every resident part."""
    parts: list[tuple[str, int]] = []
    for path in sorted(SKILLS.glob("*/SKILL.md")):
        front = _frontmatter(path.read_text(encoding="utf-8"))
        if re.search(r"^disable-model-invocation:\s*true\s*$", front, re.M):
            continue
        match = re.search(r"^description:\s*(.*)$", front, re.M)
        description = match.group(1).strip().strip('"') if match else ""
        parts.append((f"skill {path.parent.name}", estimate(path.parent.name + ": " + description)))
    rules = _load(SKILLS / "setup-s-instructions/scripts/global_instructions.py", "wukong_global_instructions")
    parts.append(("global rules (AGENTS.md)", estimate(rules.load_template())))
    session = _load(PLUGIN / "hooks/session_check.py", "wukong_session_check")
    parts.append(("SessionStart hook line", estimate(session.build_message({"status": "configured", "version": "0.0.0"}))))
    improve = _load(SKILLS / "prompt-sharpen/scripts/improve_hook.py", "wukong_improve_hook")
    parts.append(("prompt-sharpen note (per message)", estimate(improve.EVALUATION.format(prompt=""))))
    return parts


def problems(limit: int = RESIDENT_LIMIT) -> list[str]:
    parts = measure()
    total = sum(tokens for _, tokens in parts)
    if total <= limit:
        return []
    largest = ", ".join(f"{label} {tokens}" for label, tokens in sorted(parts, key=lambda p: -p[1])[:5])
    return [f"resident context is about {total} tokens, over the {limit} cap. Largest: {largest}"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    parts = measure()
    total = sum(tokens for _, tokens in parts)
    if args.json:
        print(json.dumps({"total": total, "limit": RESIDENT_LIMIT, "personalLimit": PERSONAL_LIMIT,
                          "parts": [{"label": l, "tokens": t} for l, t in parts]}, ensure_ascii=False, indent=2))
    else:
        for label, tokens in sorted(parts, key=lambda p: -p[1]):
            print(f"{tokens:6d}  {label}")
        print(f"{total:6d}  total (cap {RESIDENT_LIMIT}; personal block cap {PERSONAL_LIMIT} on top)")
    return 0 if total <= RESIDENT_LIMIT else 1


if __name__ == "__main__":
    sys.exit(main())
