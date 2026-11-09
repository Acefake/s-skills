# T3 编排首版实现计划

基线：`75208ca5ed74d8f0ba1019c5b05a0e4ecf9a0798`。主代理在当前检出实施，保留已有未跟踪方案；不创建子任务工作区，不提交、不发布、不修改用户配置。

## 交付接口

新增 `plugins/s-wukong/skills/setup-s-models/scripts/t3_targets.py`，只做本地配置解析，不直接调用 T3。输入为角色文件、项目目标 JSON、T3 能力快照。输出为版本化 JSON、有效 target 和执行路径；能力快照不能证明认证或运行成功。

- `check --rules <file> --project <root> --capabilities <json>`：校验全部角色与目标。
- `resolve --rules <file> --project <root> --capabilities <json> --role <name>`：解析一个角色；`--native-model` 可重复，声明原生工具实际支持的模型；`--worktree` 或 `--delegate` 强制 T3。
- `configure --rules <file> --project <root> --capabilities <json> --block <candidate> --targets <candidate> [--apply]`：默认预览完整双文件差异，显式 apply 才写入；事务记录支持中断恢复。
- `recover --project <root>`：恢复中断的双文件事务；发现第三方修改则拒绝覆盖。

## 任务 1 配置行为与测试

新增 `scripts/test_t3_targets.py`。先验证缺失实现导致失败，再实现目标 schema、提供商能力、模型和参数校验、预算与显式档位、旧角色解析及原生/T3 路由。特殊模型 ID 原样保存在 JSON。旧 `s_models.py resolve` 遇到 T3 引用应明确要求新入口，避免把别名作为模型派发。

运行 `python -m unittest discover -s scripts -p test_t3_targets.py`，应全部通过。

## 任务 2 预览写入

在同一模块实现双文件预览、同目录原子替换、写前并发检查、备份与恢复记录。候选文件先整体校验；预览不写文件，写入失败恢复原内容，硬中断可显式 recover。不提供自动授权入口。

测试预览无副作用、正式写入保留标记外内容、重复应用不变化、第二文件失败回滚、恢复拒绝覆盖外部编辑。

## 任务 3 技能适配与校验

新增 `skills/s-router/references/t3-code-tools.md`，统一能力发现、派发规则、完整任务说明、next 等待、取消、输入请求及 worktree 规则。在 HOSTS、setup-s-models、subagents、host-fallback、开发和评审技能中引用。修改 `scripts/check_marketplace.py` 允许 T3，保留其他退役宿主限制，更新 `test_host_support.py` 和 README。

不新增技能入口，不修改本机安装缓存；第二阶段的持续台账、PR watch 不实施。插件内容哈希校验要求同步补丁版本和清单锁文件，代码最终确定后使用现有 bump 脚本统一更新，不执行发布。

## 任务 4 验证与交付

运行 `python scripts/check_marketplace.py` 和 `python -m unittest discover -s scripts -p 'test_*.py'`。审阅全部任务 diff、新文件、旧解析调用方和配置失败路径。派一个只读评审者，模型按判断和写作角色，禁止写文件、测试和外部操作；修复有效发现。

真实 T3 委派验证可用独立评审任务覆盖同提供商派发；跨提供商认证、取消与独立 worktree 的真实运行分别记录，未执行则明确边界，不将本地测试冒充端到端通过。

## 首版执行结果

- 已实现目标解析器与 check/resolve/configure/recover，旧 resolve 明确拒绝 T3 别名。
- 新增 20 项测试；使用仓库 `.venv/Scripts/python.exe`（Python 3.12）运行全量 164 项通过。系统默认 Python 3.8 不满足仓库校验要求，未安装新环境。
- marketplace 校验通过，82 个技能；按内容哈希规则同步源码清单版本到 1.0.5，未安装或发布。
- 自审覆盖全部差异、关键调用方、配置失败恢复与参数继承；独立只读评审未发现阻塞问题。
- 独立评审使用原生同提供商代理，没有把它当成 T3 委派验证。真实跨提供商认证、取消、完成唤醒和 worktree 绑定仍未验证。
- 变更保留在原工作区 main 的未提交状态，未修改用户实际模型配置或插件缓存。
