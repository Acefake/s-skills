---
name: setup-models-first-turn
description: 配置模型的请求应选中 setup-s-models，并且第一轮只提问、不写文件、不谎称完成。
tags: [smoke, setup-s-models]
runs: 3
max_turns: 12
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, AskUserQuestion]
---
我在用 Claude Code，帮我配置一下 s 的模型和预算。
