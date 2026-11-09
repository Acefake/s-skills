# 三档模型实施计划

> **执行方式：** 当前会话由主任务按 executing-plans 实现，结束后派只读独立评审。用户已授权初版实现。

**Goal:** 增加轻量角色，并让已有授权工作流按任务内容选用三档模型。

**Architecture:** 沿用角色行格式，新增 `--light` 和“检索和简单任务”。配置脚本负责生成、兼容及解析；公共派发说明负责任务分类，宿主参考负责实际模型与参数。

**Tech Stack:** Python 标准库、unittest、Markdown，沿用现有校验脚本，不增加依赖。

**验证与授权：** 接口与多使用方变更按第 3 档验证。先补能失败的配置测试，再实现；最后跑现有完整 Python 检查。未授权提交、推送、安装或修改用户全局配置。

## 全局约束

- 规格见 `../specs/2026-11-02-three-tier-models-design.md`。
- 基线为 `3ce0a38374662958f692a13ec61abf6232e6f16d`，当前分支 `chore/dev-deps-trigger-eval`。保留现有工作区与分支，不创建或切换其他检出。
- 既有未提交文件为 `.github/workflows/check-marketplace.yml`、`.gitignore`、`README.md`、`scripts/check_marketplace.py`、`requirements-dev.txt`、`scripts/eval_triggers.py`、`scripts/test_trigger_cases.py`、`scripts/trigger_cases.json`。README 仅追加相关说明与同步版本，不覆盖原有修改。
- `--third` 仍为额外评审模型。评审人数、原有角色默认模型、委派授权均保持原规则。
- 当前会话不实测改变用户模型配置；宿主真实换模没有证据时明确未验证。

## 任务一：配置与兼容

文件：`plugins/s-wukong/skills/setup-s-models/scripts/s_models.py`、`scripts/test_s_models.py`。

接口：`render_rows(..., light=None)` 保留现有位置参数；新增角色键 `检索和简单任务`，英文键 `lookup and simple tasks`。`--light` 缺省使用 `--fast`。`write` 默认保留已有角色，`--replace-roles` 明确选择重新生成，`--set` 始终优先。

- [x] 增加测试，覆盖三档生成、默认回落、旧配置、角色解析、显式覆盖、推理档位、写入保留与重新生成。
- [x] 运行 `python -B -m unittest discover -s scripts -p test_s_models.py`，确认新增测试因功能缺失失败。
- [x] 在角色元组加入 `(检索和简单任务, lookup and simple tasks, LIGHT)`；新增角色默认档位限制为不高于 medium，显式档位保留。
- [x] `block_from_args()` 在写入预览时读取原配置，将已有角色值叠加到新默认值，再叠加 `--set`；`--replace-roles` 跳过原配置叠加。继续通过 `check_text()` 拒绝不合法生成结果。
- [x] 修改 `resolve_role()` 的默认推理档位处理，让没有括号的轻量行也不高于 medium；旧配置缺轻量行由调用方保留原角色。
- [x] 运行同一模块测试，确认所有行为通过。模板契约测试在任务二同步文档后通过。

## 任务二：派发与宿主适配

文件：`setup-s-models/SKILL.md`、`setup-s-models/references/role-keys.md`、`s-mode/references/subagents.md`、`s-mode/SKILL.md`、`s-agent/SKILL.md`、`how/SKILL.md`、`why/SKILL.md`、`swarm/SKILL.md`、`plugins/s-wukong/HOSTS.md`、各 `s-router/references/*-tools.md` 以及 `README.md`。

- [x] 模板增为 18 行，旧 17 行配置继续有效；展示按宿主实际可用名单推荐的三档模型，不按型号前缀判断强弱。
- [x] 公共派发定义严格轻量条件、直接工具优先、显式用户模型优先、缺轻量行沿用原角色，以及复杂实现读取“最难的任务”。模型拒绝时返回主线程，不静默换模。
- [x] `how` 与 `why` 仅将范围明确的资料提取交给轻量角色，架构探索与历史解释保持原角色。`swarm` 按分片内容选择，不增加人数。
- [x] 宿主说明同步新增角色、实际参数与能力限制，Codex 文件名为 `s-lookup-and-simple-tasks.toml`，其余宿主沿用原标记段位置。
- [x] 更新 README 的三档说明。补充现有契约检查，防止模板或消费方遗漏新角色。

## 任务三：整体验证与交付

- [x] 使用临时目录执行 render、write 预览、write 应用、check、resolve 和重复写入，核对旧配置及标记外文字。
- [x] 审阅完整任务 diff 与调用方，核对既有文件改动得到保留。
- [x] 为满足仓库内容哈希约束，运行 `python -B scripts/bump_plugin_version.py s-wukong` 同步本地版本和锁文件，不进行安装或发布。
- [x] 运行 `python -B scripts/check_marketplace.py` 和 `python -B -m unittest discover -s scripts -p 'test_*.py'`，记录结果。
- [x] 派只读独立评审，提供基线、规格、完整差异及验证证据。核实并修复任务内发现后完成必要复查。
- [x] 分别报告静态检查、CLI 行为验证和未验证的真实宿主换模。不提交、不推送。

## 实施验证记录

- 使用项目已有 `.venv/Scripts/python.exe`，Python 3.12.13，未安装新依赖。
- 新增测试先在旧实现失败，原因为缺少 `light` 参数、轻量角色和 CLI 参数。实现后模型模块 46 项测试通过。
- `.venv/Scripts/python.exe -X utf8 -B scripts/check_marketplace.py` 通过，79 个技能、1 个插件。
- `.venv/Scripts/python.exe -X utf8 -B -m unittest discover -s scripts -p 'test_*.py'` 通过，125 项。
- 独立 CLI 进程在临时目录验证 render、write 预览、应用、check、轻量与旧角色 resolve、重复应用。生成 18 行，旧模型与显式档位保留，标记外文字与 CRLF 保留，重复应用为 unchanged。测试型号是本地标识符，不表示真实模型调用。
- 本地插件版本从工作期间已有的 1.7.33 同步到 1.7.34，只更新仓库清单、文档版本及内容锁，未安装或发布。
- 完整 diff 与直接使用方自审已完成，补上生成边界的档位错误处理及写前模型名单校验。已有开发依赖和触发评估文件除 README 增补与版本同步外，与任务前备份逐字节一致；并发任务的 code-style 与 impeccable 改动保留。
- 真实宿主角色发现、模型切换和三档任务路由尚未验收。独立只读评审完成，无 P1 或阻塞项；发现 swarm 实际派发句仍指回旧角色的 P2 问题，已修正分派句与角色说明并自查，未为这处文案修正新派评审。

## 发布前核验

2026-11-02 用户另行授权提交和发版。其他任务的开发依赖、触发评估及插件规范改动已由其所有者撤出；本次只提交三档模型相关差异，保留 `.gitignore` 的本地 `.venv/` 忽略规则，不将它纳入提交。

按最终插件内容同步 1.7.34 内容哈希，保留版本号。最终发布树的现有 Python 测试为 120 项，已全部通过；先前的 125 项是包含当时触发评估测试的工作区结果。复用同一配置实现的自审、独立评审与 CLI 验证证据，真实宿主换模仍未验收。发布使用仓库源文件，不改用户全局配置。


发布时核对 `git archive` 产物发现，本地部分文本由 Windows 写入为 CRLF，Git 根据已有 `.gitattributes` 保存为 LF，导致此前本地内容锁与提交树不一致。已确认这些差异仅为换行，按仓库约定将本地对应文件写为 LF，并重算内容锁；插件源码的 Git 内容未改变。发版前另对干净的提交导出目录执行市场检查和完整测试。

GitHub Actions 运行 41381251380 的 job 没有启动，注释为账户因账单问题被锁定。它没有执行代码检查，不作为测试通过证据，也不改工作流绕过此限制。
