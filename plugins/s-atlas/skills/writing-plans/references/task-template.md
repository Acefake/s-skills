# 计划与任务模板

正文中的全局约束、任务接口和执行步骤都要完整填写，不能把示例占位符当作实际计划。

## 计划文档头部

**每份计划都必须以这个头部开始：**

```markdown
# [Feature Name] Implementation Plan

> **执行方式：** 按已确认方式使用 executing-plans；已授权子代理执行时使用 subagent-driven-development。仅要求写计划不授权实现。步骤使用复选框。

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

**验证与授权：** [验证档位、TDD 是否适用及替代检查、是否已授权提交。第0档只检查 diff。]

## Global Constraints

[The spec's project-wide requirements — version floors, dependency limits,
naming and copy rules, platform requirements — one line each, with exact
values copied verbatim from the spec. Every task's requirements implicitly
include this section.]

---
```

## 任务结构

````markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

**Interfaces:**
- Consumes: [what this task uses from earlier tasks — exact signatures]
- Produces: [what later tasks rely on — exact function names, parameter
  and return types. A task's implementer sees only their own task; this
  block is how they learn the names and types neighboring tasks use.]

- [ ] **Step 1: Write the failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "function not defined"

- [ ] **Step 3: Write minimal implementation**

```python
def function(input):
    return expected
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

- [ ] **Step 5: Commit only when authorized**

仅在用户已授权提交时执行；否则保留工作区修改并报告。

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
````

上面的步骤示例仅用于适用 TDD 的实现任务。不适用时，将测试步骤替换为实际可行的复现和验证；第0档只保留修改与 diff 检查，不新增或运行测试。
