# TypeScript 写法示例

`SKILL.md` 里每条规则的代码示例。背后的原则和语言无关。见 **type-system-discipline** 和 **boundary-discipline** 这两个原则 skill。（代码和代码里的注释保持英文原样。）

## 品牌类型（Branded types）

给基本类型打上标记，让它们不会被混用。在边界上校验一次。下游代码信任这个类型。

```ts
type AgentId = string & { readonly __brand: "AgentId" };

function parseAgentId(input: string): AgentId {
  if (!isUUID(input)) throw new Error(`Invalid agent id: ${input}`);
  return input as AgentId;
}

function focusAgent(id: AgentId): void {
  /* input is trusted */
}
```

照着 `readonly __brand: 'X'` 这个形状写。不要发明新的约定。

## 可辨识联合类型（Discriminated unions）

用一个字面量判别字段来表示各种变体。每个变体都有同名的字段，而每个变体的值都不一样，所以不可能的组合无法被表示。

```ts
// Don't. Boolean + optionals lets contradictory states exist.
type DiffState = { loading: boolean; diff?: GitDiff; error?: string };

// Do. Only valid states exist.
type DiffState =
  | { kind: "loading" }
  | { kind: "ready"; diff: GitDiff }
  | { kind: "error"; error: string };
```

（注释意思：不要这样，布尔值加可选字段会让互相矛盾的状态存在；要这样，只有合法的状态存在。）

选一个判别字段名（`kind`、`type`、`tag`），一直用它。

## 构造式建模（Constructive modeling）

用全部合法的部件来搭建类型，而不是用运行时检查去限制一个宽松的类型。

非空，用可变长元组：

```ts
type NonEmpty<T> = [T, ...T[]];

// Don't: T[] plus a length check every caller must repeat
function pickWinner(entries: string[]): string {
  if (entries.length === 0) throw new Error("no entries");
  return entries[Math.floor(Math.random() * entries.length)];
}

// Do: an empty value of the type can't exist
function pickWinner(entries: NonEmpty<string>): string {
  return entries[Math.floor(Math.random() * entries.length)];
}
```

（注释意思：不要用 T[] 再加一个每个调用方都得重复的长度检查；要让这个类型的空值根本不可能存在。）

在拿到一个普通 `T[]` 的地方，用一个守卫收窄一次。之后这个事实就随着类型传递下去：

```ts
const isNonEmpty = <T>(arr: T[]): arr is NonEmpty<T> => arr.length > 0;
```

偶数长度，用成对的形式：

```ts
type Pairs<T> = [T, T][];
```

一个时间范围，用开始时间加时长：

```ts
// Don't: a comment holds the invariant
type TimeRange = { start: Date; end: Date }; // start <= end

// Do: a negative range can't be written; derive end when needed
type TimeRange = { start: Date; durationMs: number };
```

（注释意思：不要让一条注释来保存不变量；要让负的范围根本写不出来，需要时再推导出结束时间。）

`durationMs` 保持为普通数字。只有当一个原始数字可能被传到需要时长的地方时，才（按“品牌类型”那条）给它打标记，而不是条件反射地打。选那个让坏状态构造不出来的表示方式，然后在上面暴露你需要的读取方式（`pairs.flat()`、一个 `rangeEnd()` 辅助函数）。

## 最简单的完全类型（Simplest total type）

不要什么都加强。当对它的每个操作都是完全的时，保持 `T[]`：

```ts
const sum = (xs: number[]) => xs.reduce((a, b) => a + b, 0); // [] is 0, fine
```

（注释意思：空数组的和是 0，没问题。）

当宽松的类型迫使你在使用处撒谎时，再加强它。信号是 `!`、`arr[0] as T`，以及一个“不应该发生”的抛错：

```ts
// Don't: partiality smuggled past the compiler
function newestSession(sessions: Session[]): Session {
  return sessions.at(0)!;
}

// Do: strengthen the input; the assertion disappears
function newestSession(sessions: NonEmpty<Session>): Session {
  return sessions[0];
}
```

（注释意思：不要把“不完全”偷偷藏过编译器；要加强输入类型，断言就消失了。）

把结果放宽成 `Session | undefined`，是另一种完全的函数签名。

## 用 `unknown` 而不是 `any`

外部数据永远是 `unknown`。使用之前先收窄。

```ts
// Don't
function handle(input: any) {
  return input.foo.bar;
}

// Do
function handle(input: unknown) {
  if (typeof input === "object" && input !== null && "foo" in input) {
    // narrowed; compiler verifies access
  }
}
```

外部来源包括 RPC 数据、`JSON.parse`、`postMessage`、进程间通信、文件内容、环境变量、数据库查询结果。

## 先用 schema，再考虑手写守卫

在为外部数据写一个逐个属性检查的类型守卫之前，先找找仓库里的运行时 schema 库和已有的 schema。让一个 schema 负责校验，并从它推导出 TypeScript 类型。不要同时维护一个 schema、一个重复的 interface 和一个守卫，它们会慢慢对不上。

```ts
import { z } from "zod";

const UserSchema = z.object({
  id: z.string().uuid(),
  role: z.enum(["admin", "member"]),
});

type User = z.infer<typeof UserSchema>;

function parseUser(input: unknown): User {
  return UserSchema.parse(input);
}
```

当失败是一种预期中的分支时，用 `safeParse`。如果仓库用的是另一个 schema 库，就用它对应的类型推导工具。不要为了一个守卫就加一个新的 schema 依赖。这条规则偏向代码库已经信任的那套 schema 系统。

## 不用 `as` 断言

每一个 `as` 都是一个潜在的运行时崩溃。只在类型系统已经验证了这个说法之后才做断言。

```ts
import { z } from "zod";

// Don't
const user = data as User;

// Don't
function isUser(data: unknown): data is User {
  return typeof data === "object" && data !== null && "id" in data;
}

// Do
const userSchema = z.object({ id: z.string(), name: z.string() });
type User = z.infer<typeof userSchema>;

function parseUser(data: unknown): User {
  return userSchema.parse(data);
}
```

当先有类型时，给校验器标注上它所证明的类型。这样，如果校验器证明的比类型少，编译器就会拒绝它。把下面对象里的 `name` 去掉，这个赋值就会编译失败。

```ts
type User = { id: string; name: string };

const userSchema: z.ZodType<User> = z.object({ id: z.string(), name: z.string() });
```

从已有代码里重构掉一个 `as` 时，先弄清 TypeScript 为什么推导不出来：

- 缺少判别字段：加一个，改成可辨识联合类型。
- 来源类型太宽（例如 `Record<string, unknown>`）：把它收窄。
- 边界没有类型：用拥有这个形状的 schema 去解析。只在没有 schema 的地方才新加一个。
- 确实无法表达：用品牌类型或 `satisfies`。

## 收窄的优先顺序

从最好到最后的手段：

1. **可辨识联合类型的 switch / if。** 编译器自动收窄。
2. **`in` 运算符。** `"key" in obj` 会收窄到包含这个键的变体。
3. **`typeof` / `instanceof`。** 用于基本类型和类的实例。
4. **自定义类型守卫。** 上面这些都不够用时。
5. **`as` 断言。** 只在校验之后。

```ts
function area(s: Shape): number {
  if ("radius" in s) return Math.PI * s.radius ** 2; // narrowed to circle
  return s.width * s.height; // narrowed to rect
}
```

## 类型守卫

守卫必须真的验证它所声称的。一个撒谎的守卫比 `as` 更糟。

```ts
function isCircle(s: Shape): s is Shape & { kind: "circle" } {
  return s.kind === "circle";
}
```

能用判别字段收窄时，优先用它。

## 穷尽检查

在 default 分支里，把判别对象赋给一个类型为 `never` 的局部变量。

```ts
// Value-returning switch
function area(s: Shape): number {
  switch (s.kind) {
    case "circle":
      return Math.PI * s.radius ** 2;
    case "rect":
      return s.width * s.height;
    default: {
      const _exhaustive: never = s;
      return _exhaustive;
    }
  }
}

// Void switch
function handle(s: Shape): void {
  switch (s.kind) {
    case "circle":
      drawCircle(s);
      break;
    case "rect":
      drawRect(s);
      break;
    default: {
      const _exhaustive: never = s;
      void _exhaustive;
    }
  }
}
```

有返回值的 switch 用 return 的写法，语句式的 switch 用 void 的写法。

## 用 `satisfies` 而不是 `as`

`satisfies` 能做校验，又不会放宽字面量类型。

```ts
// Don't. Widens, loses literal types.
const config = { theme: "dark", cols: 3 } as Config;

// Do. Validates AND preserves literal types.
const config = { theme: "dark", cols: 3 } satisfies Config;
// config.theme is "dark" (literal), not string
```

（注释意思：不要这样，会放宽类型、丢掉字面量类型；要这样，既校验又保留字面量类型，config.theme 的类型是字面量 "dark"，而不是 string。）

## 边界校验

在数据进入的地方校验一次。在内部信任类型。见 **boundary-discipline** 原则 skill。

- **线上传输格式**（proto、JSON-RPC）：解析时用 `ignoreUnknownFields`，这样向前兼容的改动不会弄坏旧的客户端。
- **持久化的 JSON：** 用带版本号的数据块，解析时包一层 try/catch。
- **不要在调用链深处重复校验。**

## 从 schema 推导的类型

当某个 `.proto`、OpenAPI 规范、GraphQL schema 或数据库迁移已经定义了一个形状时，就从生成的类型推导，而不是重复定义一遍。

```ts
// Don't. Duplicate shape, drifts when the schema changes.
type CheckSummary = {
  totalCount: number;
  checks: { name: string; status: string }[];
};
function renderChecks(s: CheckSummary) {
  /* ... */
}

// Do. Derive from the generated schema type.
import type { ChecksMessage } from "<generated module>";
function renderChecks(s: Pick<ChecksMessage, "totalCount" | "checks">) {
  /* ... */
}
```

（注释意思：不要这样，重复的形状在 schema 变化时会对不上；要这样，从生成的 schema 类型推导。）

在写一个新的 interface 之前，先考虑 `Pick`、`Omit`、`Parameters`、`ReturnType`、`Awaited`、`typeof`。

## 对象参数

```ts
// Don't. Swap two args, still compiles.
openFile(uri, {
  startLineNumber: 10,
  startColumn: 1,
  endLineNumber: 10,
  endColumn: 1,
});

// Do. Order-independent, self-documenting.
openFile({
  uri,
  selection: {
    startLineNumber: 10,
    startColumn: 1,
    endLineNumber: 10,
    endColumn: 1,
  },
});
```

（注释意思：不要这样，两个参数换了位置照样能编译；要这样，和顺序无关，自己就说明了含义。）

在热路径上跳过这条：每帧渲染、分词器、解析器，以及任何在紧凑循环里、分配内存的开销很要紧的地方。
