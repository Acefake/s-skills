# s-init 一键初始化设计

## 目标

新机器或新宿主上，用一个入口按固定顺序完成 s-atlas 的两项全局配置：全局技能提示词，再到模型配置。现在要分别记住并调用 `setup-s-instructions` 和 `setup-s-models`。

## 范围

- 新增技能 `plugins/s-atlas/skills/s-init/SKILL.md`，只做编排。
- 不改 `setup-s-instructions`、`setup-s-models` 及其脚本的行为。
- 不做项目级初始化（与内置 `init` 重名且是另一类需求），不做只读体检（已由 `daily-check` 与各 `check` 子命令覆盖），不取代现有两个技能。

## 调用策略

显式调用。`SKILL.md` 头部写 `disable-model-invocation: true`，与 `setup-s-instructions` 一致；因为它会写用户的全局配置。触发词：「/s-init」「初始化 s」「新机器配置 s」「一键配置 s」。

## 流程

1. **识别宿主。** 沿用 `setup-s-instructions` 第 1 节的方法，只处理当前宿主。
2. **检查提示词。** 运行 `global_instructions.py --host <宿主>`，不带 `--apply`，以返回的 `status` 为准。
3. **按状态处理。**
   - `configured`：跳过写入，进入第 4 步。
   - `missing` 或 `outdated`：说明要改的位置，用户明确同意后，按 `setup-s-instructions` 第 2 节加 `--apply` 写入并复查。
   - Cursor 返回需核验时，按 `setup-s-instructions` 的 Cursor 分支，不假装完成。
4. **配置模型。** 加载 `setup-s-models`，按它的一次一问流程执行，写入仍需用户明确确认。
5. **汇总。** 各自跑 `check`，报告宿主、两项结果、备份位置、未完成项，并提示新会话才会加载。

## 边界与错误

- 每个写入动作单独取得确认；沉默或“随便”不算同意。
- 任一步失败或用户跳过，停下报告并说明另一项是否已完成，不静默继续，不回滚已完成的步骤。
- 脚本退出码按 `setup-s-instructions` 的约定解读（2 是检查结果，不是失败）。
- 全部具体做法留在两个现有技能里，`s-init` 只链接它们，不复制步骤文本。

## 数据与接口

无新数据结构、无新脚本。唯一新增文件是 `SKILL.md`，以相对链接引用现有技能与脚本。

## 随改动更新

- `README.md` 的技能表加一行 `s-init`（一键初始化全局提示词和模型配置），并在显式调用的说明里列上。
- `scripts/trigger_cases.json`：按现有规则为显式技能补一条用例，具体写法以 `test_trigger_cases.py` 的约束为准。
- 运行 `scripts/update_skill_policies.py` 生成 `agents/openai.yaml`（`allow_implicit_invocation: false`）。
- 版本号和 `plugin-versions.lock.json` 走仓库发布流程（`bump_plugin_version.py`），是否发布另行决定。

## 测试

- 跑 `scripts/` 下已有测试：`test_skill_resources.py`、`test_trigger_cases.py`、`test_host_support.py`、`test_version_docs.py`，确认链接、触发用例、策略文件和版本文档都通过。
- 人工走一遍：在已配置的机器上调用 `s-init`，应跳过提示词写入、进入模型配置，且不产生新备份。

## 待用户确认

- 名字用 `s-init`（已按用户要求）。
- README 加一行（默认加）。
