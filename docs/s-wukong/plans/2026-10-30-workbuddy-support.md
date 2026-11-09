# WorkBuddy 本机适配计划

目标：复用现有 79 个技能及调用政策，增加第四宿主 WorkBuddy，不恢复其他宿主；不修改用户真实全局配置或原生记忆。

## 实现与验收

1. `scripts/install_local_skills.ps1` 增加 `-HostName workbuddy`，默认 Codex 不变。以目录联接提供 `.codebuddy/skills`，复制共享说明。对共享文件记录 SHA256，仅更新内容仍符合记录的副本；用户改动及其他安装目标停止且保留。`scripts/test_host_support.py` 用临时仓库测试首次、重复、升级与冲突保护。
2. `setup-s-instructions/scripts/global_instructions.py` 增加宿主选择及 `~/.codebuddy/CODEBUDDY.md`。复用现有块更新、备份和编码保护；`scripts/test_global_instructions.py` 覆盖默认只读、显式写入、重复、保留原文和备份。
3. 增加 `s-router/references/workbuddy-tools.md`，依据官方项目/兼容目录说明定义安装、配置与工具回退。更新 HOSTS、setup 技能、README 与全景卡片图；不改技能显式/自动政策，不新增市场清单。
4. 版本更新为 1.7.20。执行 `python -X utf8 -m unittest discover -s scripts -p "test_*.py"`、`python scripts/check_marketplace.py` 和 diff 检查；核对 79 技能、58 自动/21 显式。自审完整差异和脚本调用方后派只读独立评审。尚未运行 WorkBuddy 客户端时不宣称会话发现与真实行为已验收。

提交、推送、安装到真实客户端与初始化用户配置需对应授权；本计划只实施仓库适配。
