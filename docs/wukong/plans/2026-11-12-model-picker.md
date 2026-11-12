# 角色模型弹窗选择 实现计划

规格：[2026-11-12-model-picker-design.md](../specs/2026-11-12-model-picker-design.md)。执行方式：主任务在当前会话直接执行。

## 全局约束

- Python 3.10+（仓库用 `X | None` 语法），本机用 `py -3.14`。不加第三方依赖。
- 测试命令：`py -3.14 scripts/test_t3_targets.py` 与 `py -3.14 scripts/test_s_models.py`，全部 OK 才算通过。
- 用户可见的报错保持中文，沿用 `ConfigError`。
- 不改 `s_models.py`、事务记录（journal）格式。

## 文件结构

| 文件 | 职责 |
|---|---|
| `setup-s-models/references/model-allowlist.json` | 新增：白名单、角色偏好顺序、`providerOnly` |
| `setup-s-models/scripts/t3_catalog.py` | 新增：读白名单、合并快照、按本机算推荐、校验编号选择，自带 `catalog`、`pick` 命令 |
| `setup-s-models/scripts/t3_targets.py` | schemaVersion 2 与 `fallback` |
| `scripts/test_t3_catalog.py` | 新增：目录与推荐测试 |
| `scripts/test_t3_targets.py` | 补 v2 / fallback 测试 |
| `setup-s-models/SKILL.md`、`references/t3-config.md`、`references/mixed-budget-profiles.md` | 弹窗流程与 v2 说明 |

## 接口

```python
# t3_catalog.py
def load_allowlist(data: dict) -> dict            # 校验后原样返回；不合规抛 ConfigError
def merge_snapshots(snapshots: list[dict]) -> dict # 第一份为基础快照，其余按 providerInstanceId+model 去重并入
def build(allowlist: dict, caps: dict, show_all: bool = False) -> dict
    # -> {'schemaVersion': 1, 'entries': [...], 'recommend': {角色: {'items': [n 或 'inherit-parent'], 'fallbackToFull': bool}},
    #     'missing': [{'key', 'model', 'maybeTruncated', 'search'}]}
    # entry: {'n', 'key'(白名单外为 None), 'providerInstanceId', 'model', 'label', 'options'}
def pick(catalog: dict, choice: str, options: dict) -> dict
    # choice 为编号或模型 ID；返回 {'providerInstanceId','model','options'}；不在目录内或档位非法抛 ConfigError
```

`t3_targets.py`：

- `validate_targets` 接受 schemaVersion 1/2；仅 v2 允许 `fallback`（字段同首选、不可嵌套、不可与首选相同）。
- `check` 同时校验 `fallback` 的模型和参数。
- `resolve` 每项增加 `fallback`（无则 `None`）。
- `configure` 写入时统一输出 schemaVersion 2。
- CLI 在 `t3_catalog.py`（避免与 `t3_targets.py` 循环引用）：`catalog --capabilities <文件> [--capabilities ...] [--allowlist] [--all]`；`pick` 在此基础上加 `--choice`、`--option key=value`。

## 任务

### 任务 1：白名单文件 + `t3_catalog.py` + 测试
1. 写 `scripts/test_t3_catalog.py`：覆盖三种机器（全有 / 没有 Cursor 和 Claude / 只有 Codex）的推荐结果；识别词匹配 displayName；同一模型只走 `providers` 列出的提供商；跳过不可运行的提供商；`providerOnly` 在 `--all` 和零匹配退回下都生效；多份快照去重；截断提示；白名单校验错误；`pick` 的编号、模型 ID、非法档位、Cursor 其他模型被拒绝。
2. 运行，确认因模块不存在而失败。
3. 写 `model-allowlist.json` 和 `t3_catalog.py`。
4. 运行 `py -3.14 scripts/test_t3_catalog.py`，预期 OK。

### 任务 2：schemaVersion 2 与 fallback
1. 在 `test_t3_targets.py` 加测试：v2 首选和次选合法时 `check` 通过；次选模型不存在、参数非法、与首选相同、嵌套、v1 带 `fallback` 时报错；`resolve` 返回次选；没有次选时为 `None`；`configure` 把 v1 写成 v2。
2. 运行，确认新测试失败。
3. 修改 `t3_targets.py`。
4. 运行两个测试文件，全部 OK。

### 任务 3：CLI 子命令
1. 加测试：`catalog` 读两份快照输出推荐；`pick` 返回目标；错误时返回码为 1。
2. 在 `t3_catalog.py` 实现 `catalog`、`pick` 命令，运行测试。

### 任务 4：文档
- `SKILL.md` 分步确认第 3 步改为弹窗流程（总开关 → 编号表 → 每角色 4 题），并注明调用 `catalog`、`pick`。
- `t3-config.md` 的目标 JSON 示例改为 v2 并说明 `fallback`；`mixed-budget-profiles.md` 的「持久化与解析边界」改为次选写进 `fallback`，删掉「schemaVersion 1 没有备用字段」。
- 只检查 diff。

## 不在本计划内

- 本项目 `docs/project/s-model-fallbacks.md` 迁进 JSON：需要用户单独确认后再按新流程写入。
- `evals/setup-models-first-turn` 的提示词是 Claude Code 原生宿主，不走 T3 目录，不加针对弹窗推荐的检查项。
