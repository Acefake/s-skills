#!/usr/bin/env python3
"""Ask a model which skill each request in trigger_cases.json should load.

The model sees the same name and description list a host shows, minus the
meta-router, and must answer with one skill name. A case passes when the answer
is one of its expected skills. This calls a real model, so it is not part of
the unit tests; run it after changing descriptions.

    python scripts/eval_triggers.py --model haiku --jobs 4
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from check_marketplace import frontmatter_block, frontmatter_description
from marketplace_lib import skill_dirs

CASES_PATH = Path(__file__).resolve().parent / "trigger_cases.json"
EXCLUDED = frozenset({"wukong-router"})
NONE = "none"


def load_candidates(plugin: str = "wukong") -> dict[str, str]:
    """
    读取宿主会自动选用的技能
    @param plugin 插件名
    @returns 技能名到描述的映射，不含点名才用的技能和路由技能
    """
    found: dict[str, str] = {}
    for path in skill_dirs(plugin):
        text = (path / "SKILL.md").read_text(encoding="utf-8")
        if re.search(r"^disable-model-invocation:\s*true\s*$", frontmatter_block(text), re.M):
            continue
        if path.name not in EXCLUDED:
            found[path.name] = frontmatter_description(text) or ""
    return found


def load_cases(path: Path = CASES_PATH) -> list[dict]:
    """
    读取评测用例
    @param path 用例文件
    @returns 每条含 prompt 和 expect 的用例
    """
    return json.loads(path.read_text(encoding="utf-8"))


def build_prompt(candidates: dict[str, str], request: str) -> str:
    """
    拼出让模型选技能的提示词
    @param candidates 技能名到描述的映射
    @param request 用户原话
    @returns 提示词
    """
    listing = "\n".join(f"- {name}: {desc}" for name, desc in candidates.items())
    return (
        "You route a user request to the single most specific skill.\n"
        "Skills:\n"
        f"{listing}\n\n"
        f"Request: {request}\n\n"
        f"Answer with only the skill name, or {NONE} if no skill fits."
    )


def parse_choice(output: str, names: set[str]) -> str:
    """
    从模型输出里取出技能名
    @param output 模型原始输出
    @param names 合法技能名
    @returns 技能名或 none；无法识别时返回输出最后一行
    """
    lines = [line.strip().strip("`'\"*. ").lower() for line in output.splitlines() if line.strip()]
    if not lines:
        return ""
    # 先认首行或末行的单独作答，再退回全文里最先出现的技能名
    for line in (lines[0], lines[-1]):
        if line in names or line == NONE:
            return line
    text = output.lower()
    positions = {}
    for name in names:
        match = re.search(rf"(?<![\w-]){re.escape(name)}(?![\w-])", text)
        if match:
            positions[name] = match.start()
    return min(positions, key=positions.get) if positions else lines[-1]


def ask_claude(prompt: str, model: str) -> str:
    """
    用 Claude Code 命令行单次提问，不加载技能、工具和 MCP
    @param prompt 提示词
    @param model 模型别名或 ID
    @returns 模型标准输出
    """
    executable = shutil.which("claude")
    if not executable:
        sys.exit("claude CLI not found on PATH")
    command = [
        executable, "-p", "--model", model,
        "--disable-slash-commands", "--strict-mcp-config", "--tools", "",
        "--no-session-persistence", "--system-prompt", "You are a precise classifier.",
    ]
    try:
        result = subprocess.run(
            command, input=prompt, capture_output=True, text=True, encoding="utf-8",
            check=False, timeout=180,
        )
    except subprocess.TimeoutExpired:
        return ""
    if result.returncode != 0:
        sys.exit(f"claude exited {result.returncode}: {result.stderr.strip()[-500:]}")
    return result.stdout


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--model", default="haiku")
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--filter", default="", help="only run cases whose expect contains this text")
    parser.add_argument("--repeat", type=int, default=1, help="ask each case N times; pass on a strict majority")
    args = parser.parse_args(argv)
    if args.repeat < 1:
        parser.error("--repeat must be at least 1")
    sys.stdout.reconfigure(encoding="utf-8")

    candidates = load_candidates()
    names = set(candidates)
    cases = [c for c in load_cases() if any(args.filter in e for e in c["expect"])]
    jobs = [case for case in cases for _ in range(args.repeat)]

    def run(case: dict) -> str:
        return parse_choice(ask_claude(build_prompt(candidates, case["prompt"]), args.model), names)

    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        choices = list(pool.map(run, jobs))

    failed = 0
    for index, case in enumerate(cases):
        answers = choices[index * args.repeat:(index + 1) * args.repeat]
        hits = sum(answer in case["expect"] for answer in answers)
        if hits * 2 <= args.repeat:
            failed += 1
            wrong = ", ".join(a or "(empty)" for a in answers if a not in case["expect"])
            print(f"FAIL {case['prompt']}\n     expect {'/'.join(case['expect'])}, {hits}/{args.repeat} hits, got {wrong}")
    print(f"{len(cases) - failed}/{len(cases)} cases routed as expected ({args.model}, repeat {args.repeat})")
    return 1 if failed else 0

if __name__ == "__main__":
    sys.exit(main())
