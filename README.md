# s 中文技能

一个独立维护的中文 AI 技能插件，包含 85 个技能，覆盖代码开发、调试、审查、界面设计、动画和技术写作。插件统一使用 `s`，不需要安装上游插件。

## 安装

### Codex 本项目开发

克隆仓库后，在 Windows PowerShell 中运行：

```powershell
git clone https://github.com/Acefake/s-skills.git
cd s-skills
powershell -NoProfile -File scripts/install_local_skills.ps1
```

脚本把技能链接到本项目的 `.agents/skills/`。重新打开项目会话后使用；修改源文件后无需重复复制技能。该方式只对本项目生效。

### 插件市场

Claude Code 和 WorkBuddy 在聊天中运行：

```text
/plugin marketplace add Acefake/s-skills
/plugin install s@s-skills
```

Codex 在终端添加市场，再在应用的插件管理入口安装 `s`：

```text
codex plugin marketplace add Acefake/s-skills
```

Cursor 从插件市场导入 `https://github.com/Acefake/s-skills`，选择 `s`。各宿主的中文命令支持与入口以实际界面为准。安装或更新后开启新会话，确认技能路径和版本。

## 使用

直接点名中文技能，并说明目标和完成条件：

```text
用 poteto工作模式 修复这个问题，复现后定位原因，修完运行实际流程验证。
用 代码怎么工作 解释这个模块的入口、数据流和关键文件。
用 精致界面设计 检查这个设置页，并给出具体改进。
```

支持插件命令的宿主也可以使用 `/s:技能名`，例如 `/s:poteto工作模式`。Codex 可在技能选择器中选择相应技能。

TypeScript 规范、原则和部分设计技能允许按任务自动选择。工作模式、并行审查等复杂流程需要点名调用。自动选择不表示每轮执行；可用性还取决于宿主提供的工具。

- [全部技能](plugins/s/skills/)
- [工作模式](plugins/s/skills/poteto工作模式/SKILL.md)
- [使用帮助](plugins/s/skills/s使用帮助/SKILL.md)
- [模型设置](plugins/s/skills/设置s模型/SKILL.md)
- [Codex、T3 与 Cursor 适配规则](plugins/s/HOSTS.md)

## 维护

技能源文件只放在 `plugins/s/skills/<中文名>/SKILL.md`。修改后同步调用策略、更新版本并检查：

```text
python scripts/update_skill_policies.py
python scripts/bump_plugin_version.py s
python scripts/check_marketplace.py
python -m unittest discover -s scripts -p "test_*.py"
```

校验覆盖市场清单、版本锁、技能名称、调用策略和本地链接。技能是否实际触发、模型是否按配置委派，仍需通过真实会话验证。

## 来源与许可证

保留各技能的原作者署名、许可证及通知文件。来源包括工作流、设计和动画等多个开源项目，详见 [LICENSE](plugins/s/LICENSE)、插件目录下的 `LICENSE-*`、`NOTICE-*` 和各技能内的来源说明。
