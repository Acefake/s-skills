本技能译自 Jesse Vincent 的 Superpowers（MIT）。许可证见上一级文件夹的 `LICENSE-superpowers`。

# 测试反模式

**在这些时候加载本参考：** 编写或修改测试、添加 mock，或者忍不住要往生产代码里加只给测试用的方法时。

## 概述

测试必须验证真实行为，而不是 mock 的行为。mock 是用来隔离的手段，不是被测对象。

**核心原则：** 测代码做了什么，不要测 mock 做了什么。

**严格遵循 TDD 就能避免这些反模式。**

## 铁律

```
1. NEVER test mock behavior
2. NEVER add test-only methods to production classes
3. NEVER mock without understanding dependencies
```

## 反模式 1：测试 mock 的行为

**违规：**
```typescript
// ❌ BAD: Testing that the mock exists
test('renders sidebar', () => {
  render(<Page />);
  expect(screen.getByTestId('sidebar-mock')).toBeInTheDocument();
});
```

**为什么这是错的：**
- 你在验证 mock 能工作，而不是组件能工作
- mock 在的时候测试通过，不在的时候测试失败
- 对真实行为一无所知

**你的人类搭档的纠正：**「我们是在测一个 mock 的行为吗？」

**修正：**
```typescript
// ✅ GOOD: Test real component or don't mock it
test('renders sidebar', () => {
  render(<Page />);  // Don't mock sidebar
  expect(screen.getByRole('navigation')).toBeInTheDocument();
});

// OR if sidebar must be mocked for isolation:
// Don't assert on the mock - test Page's behavior with sidebar present
```

### 门禁函数

```
BEFORE asserting on any mock element:
  Ask: "Am I testing real component behavior or just mock existence?"

  IF testing mock existence:
    STOP - Delete the assertion or unmock the component

  Test real behavior instead
```

## 反模式 2：生产代码里的只给测试用的方法

**违规：**
```typescript
// ❌ BAD: destroy() only used in tests
class Session {
  async destroy() {  // Looks like production API!
    await this._workspaceManager?.destroyWorkspace(this.id);
    // ... cleanup
  }
}

// In tests
afterEach(() => session.destroy());
```

**为什么这是错的：**
- 生产类被只给测试用的代码污染了
- 如果在生产中被意外调用，会很危险
- 违反 YAGNI 和关注点分离
- 把对象生命周期和实体生命周期混在一起

**修正：**
```typescript
// ✅ GOOD: Test utilities handle test cleanup
// Session has no destroy() - it's stateless in production

// In test-utils/
export async function cleanupSession(session: Session) {
  const workspace = session.getWorkspaceInfo();
  if (workspace) {
    await workspaceManager.destroyWorkspace(workspace.id);
  }
}

// In tests
afterEach(() => cleanupSession(session));
```

### 门禁函数

```
BEFORE adding any method to production class:
  Ask: "Is this only used by tests?"

  IF yes:
    STOP - Don't add it
    Put it in test utilities instead

  Ask: "Does this class own this resource's lifecycle?"

  IF no:
    STOP - Wrong class for this method
```

## 反模式 3：不理解就 mock

**违规：**
```typescript
// ❌ BAD: Mock breaks test logic
test('detects duplicate server', () => {
  // Mock prevents config write that test depends on!
  vi.mock('ToolCatalog', () => ({
    discoverAndCacheTools: vi.fn().mockResolvedValue(undefined)
  }));

  await addServer(config);
  await addServer(config);  // Should throw - but won't!
});
```

**为什么这是错的：**
- 被 mock 的方法有测试所依赖的副作用（写入配置）
- 为了「保险」而过度 mock，破坏了实际行为
- 测试因错误原因通过，或者莫名其妙地失败

**修正：**
```typescript
// ✅ GOOD: Mock at correct level
test('detects duplicate server', () => {
  // Mock the slow part, preserve behavior test needs
  vi.mock('MCPServerManager'); // Just mock slow server startup

  await addServer(config);  // Config written
  await addServer(config);  // Duplicate detected ✓
});
```

### 门禁函数

```
BEFORE mocking any method:
  STOP - Don't mock yet

  1. Ask: "What side effects does the real method have?"
  2. Ask: "Does this test depend on any of those side effects?"
  3. Ask: "Do I fully understand what this test needs?"

  IF depends on side effects:
    Mock at lower level (the actual slow/external operation)
    OR use test doubles that preserve necessary behavior
    NOT the high-level method the test depends on

  IF unsure what test depends on:
    Run test with real implementation FIRST
    Observe what actually needs to happen
    THEN add minimal mocking at the right level

  Red flags:
    - "I'll mock this to be safe"
    - "This might be slow, better mock it"
    - Mocking without understanding the dependency chain
```

## 反模式 4：不完整的 mock

**违规：**
```typescript
// ❌ BAD: Partial mock - only fields you think you need
const mockResponse = {
  status: 'success',
  data: { userId: '123', name: 'Alice' }
  // Missing: metadata that downstream code uses
};

// Later: breaks when code accesses response.metadata.requestId
```

**为什么这是错的：**
- **局部 mock 掩盖了结构假设**——你只 mock 了自己知道的字段
- **下游代码可能依赖你没放进去的字段**——静默失败
- **测试通过但集成失败**——mock 不完整，真实 API 是完整的
- **虚假的信心**——测试对真实行为什么也没证明

**铁律：** mock 现实中存在的完整数据结构，而不是只 mock 你眼前这个测试用到的字段。

**修正：**
```typescript
// ✅ GOOD: Mirror real API completeness
const mockResponse = {
  status: 'success',
  data: { userId: '123', name: 'Alice' },
  metadata: { requestId: 'req-789', timestamp: 1234567890 }
  // All fields real API returns
};
```

### 门禁函数

```
BEFORE creating mock responses:
  Check: "What fields does the real API response contain?"

  Actions:
    1. Examine actual API response from docs/examples
    2. Include ALL fields system might consume downstream
    3. Verify mock matches real response schema completely

  Critical:
    If you're creating a mock, you must understand the ENTIRE structure
    Partial mocks fail silently when code depends on omitted fields

  If uncertain: Include all documented fields
```

## 反模式 5：把集成测试当成事后补的事

**违规：**
```
✅ Implementation complete
❌ No tests written
"Ready for testing"
```

**为什么这是错的：**
- 测试是实现的一部分，不是可选的后续步骤
- TDD 本来就会抓住这一点
- 没有测试就不能声称完成

**修正：**
```
TDD cycle:
1. Write failing test
2. Implement to pass
3. Refactor
4. THEN claim complete
```

## 当 mock 变得过于复杂

**警告信号：**
- mock 的准备比测试逻辑还长
- 为了让测试通过而 mock 一切
- mock 缺少真实组件拥有的方法
- mock 一变测试就坏

**你的人类搭档的问题：**「这里我们真的需要用 mock 吗？」

**考虑：** 用真实组件做集成测试，往往比复杂的 mock 更简单。

## TDD 能防止这些反模式

**为什么 TDD 有帮助：**
1. **先写测试** → 迫使你想清楚自己到底在测什么
2. **看着它失败** → 确认测试测的是真实行为，不是 mock
3. **最少实现** → 只给测试用的方法不会悄悄混进来
4. **真实依赖** → 在 mock 之前，你能看到测试实际上需要什么

**如果你在测 mock 的行为，你就已经违反了 TDD**——你加了 mock，却没有先看着测试对着真实代码失败。

## 速查

| 反模式 | 修正 |
|--------------|-----|
| 对 mock 元素做断言 | 测真实组件，或者取消 mock |
| 生产代码里的只给测试用的方法 | 移到测试工具里 |
| 不理解就 mock | 先理解依赖，再做最少的 mock |
| 不完整的 mock | 完整镜像真实 API |
| 测试当成事后补的事 | TDD——测试先行 |
| 过度复杂的 mock | 考虑集成测试 |

## 危险信号

- 断言在检查 `*-mock` 测试 ID
- 方法只在测试文件里被调用
- mock 准备占了测试的 50% 以上
- 去掉 mock 后测试就失败
- 说不清为什么需要 mock
- 「为了保险」而 mock

## 底线

**mock 是用来隔离的工具，不是用来测的对象。**

如果 TDD 揭示你正在测 mock 的行为，你已经走错了。

修正：测真实行为，或者追问你到底为什么要 mock。
