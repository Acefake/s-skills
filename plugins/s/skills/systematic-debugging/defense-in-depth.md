本技能译自 Jesse Vincent 的 Superpowers（MIT）。许可证见 [LICENSE-superpowers](../../LICENSE-superpowers)。

# 纵深防御校验

## 概述

修掉由无效数据引起的 bug 时，在一处加上校验会让人觉得够了。但不同代码路径、重构或 mock 都能绕过这一处检查。

**核心原则：** 数据经过的每一层都要校验。让这个 bug 在结构上不可能发生。

## 为什么要多层

单层校验：「我们修好了这个 bug」
多层校验：「我们让这个 bug 不可能发生」

不同层抓住不同情况：
- 入口校验抓住大多数 bug
- 业务逻辑抓住边界情况
- 环境保护阻止特定上下文中的危险操作
- 调试日志在其他层失效时提供帮助

## 四层

### 第 1 层：入口校验
**目的：** 在 API 边界拒绝明显无效的输入

```typescript
function createProject(name: string, workingDirectory: string) {
  if (!workingDirectory || workingDirectory.trim() === '') {
    throw new Error('workingDirectory cannot be empty');
  }
  if (!existsSync(workingDirectory)) {
    throw new Error(`workingDirectory does not exist: ${workingDirectory}`);
  }
  if (!statSync(workingDirectory).isDirectory()) {
    throw new Error(`workingDirectory is not a directory: ${workingDirectory}`);
  }
  // ... proceed
}
```

### 第 2 层：业务逻辑校验
**目的：** 确保数据对这次操作是合理的

```typescript
function initializeWorkspace(projectDir: string, sessionId: string) {
  if (!projectDir) {
    throw new Error('projectDir required for workspace initialization');
  }
  // ... proceed
}
```

### 第 3 层：环境保护
**目的：** 在特定上下文中阻止危险操作

```typescript
async function gitInit(directory: string) {
  // In tests, refuse git init outside temp directories
  if (process.env.NODE_ENV === 'test') {
    const normalized = normalize(resolve(directory));
    const tmpDir = normalize(resolve(tmpdir()));

    if (!normalized.startsWith(tmpDir)) {
      throw new Error(
        `Refusing git init outside temp dir during tests: ${directory}`
      );
    }
  }
  // ... proceed
}
```

### 第 4 层：调试埋点
**目的：** 捕获上下文，供事后排查

```typescript
async function gitInit(directory: string) {
  const stack = new Error().stack;
  logger.debug('About to git init', {
    directory,
    cwd: process.cwd(),
    stack,
  });
  // ... proceed
}
```

## 应用这个模式

找到 bug 时：

1. **追踪数据流** - 坏值从哪里来？在哪里被使用？
2. **标出所有检查点** - 列出数据经过的每一处
3. **在每一层加校验** - 入口、业务、环境、调试
4. **测试每一层** - 试着绕过第 1 层，确认第 2 层能抓住它

## 会话中的例子

Bug：空的 `projectDir` 导致在源代码里执行了 `git init`

**数据流：**
1. 测试准备 → 空字符串
2. `Project.create(name, '')`
3. `WorkspaceManager.createWorkspace('')`
4. `git init` 在 `process.cwd()` 中运行

**加上的四层：**
- 第 1 层：`Project.create()` 校验非空、存在、可写
- 第 2 层：`WorkspaceManager` 校验 projectDir 非空
- 第 3 层：`WorktreeManager` 在测试中拒绝 tmpdir 之外的 git init
- 第 4 层：在 git init 之前记录堆栈跟踪

**结果：** 全部 1847 个测试通过，这个 bug 无法再复现

## 关键洞察

四层都有必要。测试期间，每一层都抓住了其他层漏掉的 bug：
- 不同代码路径绕过了入口校验
- mock 绕过了业务逻辑检查
- 不同平台上的边界情况需要环境保护
- 调试日志识别出结构性误用

**不要停在一个校验点。** 在每一层都加上检查。
