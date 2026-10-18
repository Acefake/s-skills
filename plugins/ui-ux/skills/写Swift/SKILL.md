---
name: 写Swift
description: 怎样写好现代 Swift——用值类型建模，Swift 6 数据竞争安全和易上手的并发（@concurrent、默认主 actor、actor、任务组），协议和泛型（some 对比 any），API 设计，性能和 ARC，Swift Testing，宏，以及 AI 助手还不知道的现代语言特性。在编写、审查或迁移 Swift 代码时使用，或者在需要修复并发报错、卡顿、数据竞争、循环引用或性能问题时使用。
---

> 翻译自 Emil Kowalski 的仓库 https://github.com/emilkowalski/skills （skills/write-swift，commit 2d22863）的 `write-swift` skill，原作者 Emil Kowalski（版权 © 2026 Emil Kowalski），许可证 MIT（全文见上一级文件夹的 `LICENSE-emilkowalski-skills`），仅供自用。
> 说明：Swift 关键字、类型名、API 名和代码保持原样，代码注释的意思在后面用中文说明。表格里“Since”一列的意思是“从哪个 Swift 版本开始有”。原文写于 2026 年 8 月。
> 英文名备份：s-write-swift

# 写 Swift

## 第一次回应

当这个 skill 第一次被调用、而用户没有提具体问题时，只回复这一句：

> 我准备好帮你写现代 Swift 了，按这门语言希望的方式来写。

在用户提问之前，不要提供任何其他信息。

这里讲的是怎样按 Swift 这门语言希望的方式来写，内容更新到 Swift 6.4。

**工具链基准：Swift 6.3**（截至 2026 年 8 月的当前正式版）。除非标了 ⚠，这里的所有内容都能在 6.3 上编译；⚠ 表示还没发布的 Swift 6.4 特性。并发方面的建议以 Swift 6.2 的模型为前提——如果项目还在 6.1 或更早，第 3 节里关于 `async` 和 `@concurrent` 的规则不适用。

贯穿全文的主线：**Swift 是一门“渐进展开”的语言。先用最简单、最静态、最单线程、能工作的写法，只有在你能指出理由的地方，才去“买”动态性——并发、引用语义、存在类型（existential）、不安全指针。** 下面每一条规则都是这一点的应用。

按这个默认层级来建模。只有当你能说出理由时，才往下走一层：

| Need         | Reach for               | Move down only when                                        |
| ------------ | ----------------------- | ---------------------------------------------------------- |
| 数据         | `struct` / `enum`       | 你需要身份、共享或继承                                     |
| 抽象         | 具体类型                | 多个类型之间出现了重复代码                                 |
| 多态         | `some P`（泛型）        | 你需要存放不同类型 → `any P`                               |
| 执行         | 主 actor，同步          | 性能分析显示有卡顿 → `async` → `@concurrent` → `actor`     |
| 内存         | `Array`、`String`       | 性能分析显示出了开销 → `InlineArray`、`Span`               |
| 安全         | 安全的 API              | C 互操作或者测量过的热点路径 → `Unsafe*`                   |

（表头意思：Need = 需要什么；Reach for = 先用什么；Move down only when = 只有在这种情况下才往下走。）

---

## 1. 用值类型给数据建模

在 Swift 里，值类型是默认选择，不是特殊情况。

- **默认用 `struct` 和 `enum`。只有在需要身份、共享可变状态、继承或资源生命周期时才用 `class`。** 一个窗口、一个数据库连接、渲染引擎里存的一个实体——这些有身份。一个 `Point`、一个 `Drink`、一个 `Material` 没有。
- **默认 `let`；只有要修改时才用 `var`。** 这和“先 `some` 后 `any`”、“先值后引用”是同一个原则：先收窄，有理由再放宽。
- **一个带可变引用类型属性的 struct，既不是值也不是引用。** 副本会共享那个对象；修改会泄漏到其他副本。要么让被引用的类型不可变，要么只暴露转发给它的计算属性，要么把它做成一个 `private` 存储属性，配合写时复制。
- **写时复制（copy-on-write）是同时得到“外部存储”_和_值语义的办法。** 把一个 final class 包在 struct 里，修改前检查 `isKnownUniquelyReferenced(&storage)`；如果不是唯一引用，先复制。`Array`、`String` 和 `Dictionary` 正是这样工作的。
- **enum 是表达“一组固定的东西”和互斥状态的工具。** 把一堆可选的存储属性（`isSharing`、`selectedRows`、`shareTarget`）换成一个 `enum State`，能让无效的组合根本写不出来，并且让状态变化变成原子的，而不是一串你可能忘了写完的属性赋值。
- **值组合起来还是值。** 一个所有存储属性都是值类型的 struct，免费拥有值语义——这就是为什么撤销、差异比较和状态恢复可以只走一条代码路径，而不是每个属性一条。

```swift
struct Material {                       // value semantics preserved
  var roughness: Double
  private var _texture: Texture         // a class

  var color: Color {
    get { _texture.color }
    set {
      if !isKnownUniquelyReferenced(&_texture) { _texture = Texture(copying: _texture) }
      _texture.color = newValue
    }
  }
}
```

（代码注释意思：保留了值语义；`_texture` 是一个 class。）

**不可复制类型**（`~Copyable`）表达唯一所有权：一个文件描述符、一笔银行转账、一个打开的资源。禁止复制能把“你不能运行两次”从一个断言变成编译错误，也让 struct 上的 `deinit` 有了意义。把收尾的方法标成 `consuming`，让编译器证明那是最后一次使用。参数的所有权变得明确：`borrowing`（只读，默认）、`consuming`（拿走它）、`inout`/`mutating`（临时写权限）。

---

## 2. 错误和可选值——让失败的路径看得见

Swift 的错误处理基于三点：错误的来源被标出来，不会让你措手不及；错误带着足够的上下文让你能处理；以及**可恢复的错误和程序员的失误是两回事**。

- **可恢复 → `throw`。程序员失误 → `precondition`/`fatalError`。** 网络请求失败了，程序继续运行。下标越界意味着代码写错了，必须在 bug 变成安全问题之前停下来。
- **带关联值的 enum 是最好的错误类型。** `case duplicateFriend(String)` 比 `case duplicateFriend` 好——上下文才是关键。
- **错误条件用 `guard`**，因为它强制你写退出路径。普通的解包用 `if let`。
- **类型化的 throws（`throws(MyError)`）用于内部函数、转发错误的泛型代码和受限环境**，在这些地方把错误装箱成 `any Error` 代价太高。对公开 API，不带类型的 `throws` 保留了你以后更改错误类型的自由。注意这种统一：`throws` 就是 `throws(any Error)`，不抛错就是 `throws(Never)`——正因如此 `map` 才能同时适用于两者。
- **只在你能说出不变条件的地方强制解包**，并且比起光秃秃的 `!`，优先用一个带消息、会失败的 `#require`/`precondition`。

---

## 3. 并发：在性能分析证明需要之前，保持单线程

这是 AI 助手最常写错的一节，因为模型在 Swift 6.2 里变了。

每个应用一开始都完全跑在主线程上。单线程代码能走很远，大多数应用根本不需要离开它。

**按顺序推进。不要跳步。**

1. **在主 actor 上单线程运行。** 完全没有并发。对大多数应用来说就够了。
2. **用 `async`/`await`** 隐藏延迟（网络、磁盘）。你自己仍然没有引入并发——像 `URLSession.data(from:)` 这样的 SDK API 会替你把工作移到别处。
3. **用 `@concurrent`** 把_你自己的_耗时工作移出主线程——只在 Instruments 显示有卡顿之后才这样做。
4. **用 `actor`** 把_状态_移出主 actor——只在主 actor 上的状态太多、迫使任务不停地跳回来时才这样做。

**先打开正确的构建设置。** 在每个项目里启用 **Approachable Concurrency**（易上手的并发）。对于 app 模块和面向界面的模块，再把 **Default Actor Isolation**（默认 actor 隔离）设成 **MainActor**——这是 Xcode 26 里新建 app 项目的默认值，它能删掉你大部分的 `@MainActor` 标注。在 package 里：`swiftSettings: [.defaultIsolation(MainActor.self)]`。**不要给通用库设置默认主 actor**——库应该提供 `nonisolated` 的 API，让使用者决定工作在哪里运行。

### 变了的那条规则

**在 Swift 6.2 里，把一个函数标成 `async`，_不会_让它离开当前的 actor。** 它在被调用的地方运行。正是这一点让“最自然的写法”默认就没有数据竞争。

- **`@concurrent`**——总是切换到并发线程池。用在_你自己的_ CPU 密集型工作上。
- **`nonisolated`**——在哪里被调用就在哪里运行。**这是库 API 的正确默认值**，因为由调用者决定。在类型上写 `nonisolated` 会让它的所有成员都是 nonisolated（Swift 6.1+）。
- 两个都不写——留在调用者的 actor 上。

```swift
nonisolated struct PhotoProcessor {          // decoupled from the main actor
  @concurrent                                // guaranteed to run in the background
  func process(_ data: Data) async -> ProcessedPhoto {
    async let sticker = extractSticker(data)  // two independent jobs, in parallel
    async let colors  = extractColors(data)
    return await ProcessedPhoto(sticker: sticker, colors: colors)
  }
}
```

（代码注释意思：和主 actor 解耦；保证在后台运行；两个独立的工作，并行执行。）

- **先做性能分析，再移走工作。** 用 Instruments（Time Profiler、卡顿检测）。如果不用并发也能让代码变快，永远先那样做。并发有真实的代价——任务分配、调度，以及理解代码的难度。
- **不要为琐碎的工作开任务。** 开一个子任务去读一个 `UserDefaults` 值，花的比省的多。
- **一个端到端的操作用一个任务。** 必须按顺序发生的工作放在_一个_任务里；互相独立的操作用不同的任务，让运行时可以交错执行它们。
- **`await` 是一个挂起点，它会打破原子性。** 挂起期间状态可能会变，恢复时可能在另一个线程上。每次 `await` 之后都要重新检查假设。绝不要跨过它持有锁。绝不要跨过它依赖线程局部存储。

### Actor 的重入

Actor 保证互斥，不保证事务。在同一个 actor 上的两次 `await` 之间，会有别的工作运行。

- **在同步方法里修改 actor 的状态。** actor 上的同步代码会不被打断地运行到底——那就是你的事务边界。
- **让 async 的 actor 方法保持轻薄**，由同步的事务性操作组合而成，并且在每个 `await` 处都让 actor 处于一致的状态。
- 经典 bug：检查缓存 → `await` 下载 → 写缓存。两个任务都没命中缓存，都去下载，第二个覆盖掉第一个。在 `await` 之后重新检查，或者对正在进行中的工作去重。
- **Actor 不是先进先出（FIFO）的。** 它们先运行优先级最高的工作，正是为了避免优先级反转。如果你需要顺序，用一个任务（它从头运行到尾）或者 `AsyncStream`，而不是 actor。

---

## 4. Sendable 和共享数据

`Sendable` 标记一个类型可以安全地在隔离域之间共享。编译器在每个任务和 actor 的边界上检查它。

- **值类型的存储是 Sendable 时，它就是 `Sendable`**——对非公开类型会自动推断。**公开类型永远不会被推断为可发送**：把公开类型标成 `Sendable` 是对使用者的承诺，所以 Swift 要你亲手写出来。
- **Actor 和 `@MainActor` 类隐式就是 `Sendable`**，因为它们的状态是隔离的。
- **大多数模型类既不应该是 `@MainActor`，也不应该是 `Sendable`。** 有意让它们保持非 `Sendable`——这能防止一半模型在主线程上被修改、另一半在后台被修改。如果它们需要离开主 actor，把它们标成 `nonisolated`，而不是 `Sendable`。
- **你仍然可以在域之间_发送_一个非 `Sendable` 对象**，只要发送方之后不再用它。在交出去_之前_做完所有修改；之后再碰它才是错误。
- 闭包也会捕获状态。只有当一个函数类型真的要跨域时，才把它标成 `@Sendable`。
- **`@unchecked Sendable` 是一个编译器无法检查的承诺。** 只留给内部有真正同步机制（一个 `Mutex`、一把锁）的类型。全局变量上的 `nonisolated(unsafe)` 也一样——是最后手段，不是消除警告的工具。

**遇到数据竞争错误时，按这个清单往下走：**

1. **不要共享它。** 把共享的对象移到一个局部变量里，让每个并发工作都有自己的实例。（真实遇到的错误里，绝大多数都是这样修的。）
2. **把它做成 `Sendable` 的值类型**，这样“共享”其实就是复制。
3. **把它隔离到一个 actor 上**——主 actor，或者你自己的。
4. 只有到这时，才去用 `Synchronization` 模块里的 `Mutex`/`Atomic`（存放在 `let` 属性里），或者 `@unchecked Sendable`。

**全局变量和静态变量是最常见的错误来源。** 按优先顺序：把它改成 `let`；把它放到 `@MainActor` 上；用 `Mutex` 包起来；`nonisolated(unsafe)`。注意 Swift 里的全局变量是延迟初始化_并且_原子初始化的——和 C 不一样。

**桥接老的回调式 API：** 如果 delegate 协议是你自己的，给它加上 `@MainActor` 标注。如果不是，把方法标成 `nonisolated`，并用 `MainActor.assumeIsolated { }`——它做的是断言而不是跳转，所以出问题时会大声崩溃，而不是悄悄地发生竞争。在遵循协议的地方写 `@preconcurrency` 是做同一件事的简写。用 `@preconcurrency import` 暂时消除还没迁移的模块带来的可发送性警告；等那个模块迁移完，警告会回来——这是对的。

---

## 5. 结构化并发

永远优先用结构化的任务。

结构化任务（`async let`、任务组）像局部变量一样有作用域：它们不能活得比代码块更久，会被自动等待，并且通过任务树继承取消状态、优先级和任务局部值。非结构化任务（`Task { }`、`Task.detached`）这些都不会自动给你。

- **`async let`** 用于数量固定、事先知道的并发子任务。
- 数量是动态的时候用 **`withTaskGroup`**。任务组遵循 `AsyncSequence`——结果一到就可以遍历。子任务不返回任何东西时，用 **`withDiscardingTaskGroup`**：它会立即释放每个子任务的资源，并在出现第一个错误时取消其他兄弟任务。
- **`Task { }`** 只在工作的生命周期不适合放进某个作用域时用——响应 delegate 回调、按钮点击、视图出现。它继承 actor 隔离和优先级；取消要你自己管理。
- **`Task.detached`** 几乎永远不用。它什么都不继承——隔离、优先级、任务局部值都没有。如果你需要一个分离的根任务，在它_里面_放一个任务组，而不是反复分离。

**取消是协作式的。** 取消只是设置一个标志；它不会停下任何东西。**在开始耗时工作之前**检查 `Task.isCancelled` 或 `try Task.checkCancellation()`，同步的辅助函数里也要检查。对于处于挂起而不是运行中的工作（一个 `AsyncSequence` 的 `next()`），用 `withTaskCancellationHandler`——并且记住这个处理器会立即运行、和主体并发执行，所以它碰到的状态需要真正的同步（一个原子量或一把锁，不是 actor——在 actor 上你无法保证顺序）。

**限制并发数量。** 不要对一个没有上限的列表每一项都开一个子任务。先开 N 个子任务，然后每完成一个再加一个新的。

**任务局部值**（`@TaskLocal`）沿着任务树往下传递上下文——一个请求 ID、一个追踪片段——不用在每个函数签名里都加一个参数。把它们做成可选的，这样没有绑定时读到的也是一个合理的默认值。

**桥接回调：** `withCheckedContinuation` / `withCheckedThrowingContinuation`。约定是**在每条路径上恰好恢复一次**——永不恢复会让调用者永远挂着；恢复两次是致命错误。对于之后才触发的 delegate API，把 continuation 存起来，恢复时把它置为 nil。（还没发布的 Swift 6.4 增加了一个 `Continuation` 类型，在编译期检查只恢复一次。）

**`AsyncSequence`：** 用 `for await` / `for try await` 遍历。用 `AsyncStream` / `AsyncThrowingStream` 适配已有的基于处理器或 delegate 的 API——在闭包里构造数据源，在处理器里 `yield`，在 `onTermination` 里清理。

---

## 6. SwiftUI 里的并发

- **`View` 是 `@MainActor` 隔离的**，它包含的一切也是，包括你的 `@State`。你几乎从来不需要在视图或视图模型上写 `@MainActor`——用了默认主 actor 之后，你可以删掉已经写的那些。
- **SwiftUI 会有意地把你的一部分代码放到主线程以外运行**，让每一帧保持轻量。信号是 API 签名里的 `@Sendable`：`visualEffect`、`Shape.path(in:)`、`Layout` 的要求、`onGeometryChange`。当你在这些闭包里碰到隔离错误时，**不要发送 `self`——把你需要的那一个值复制到闭包的捕获列表里。**

```swift
.visualEffect { [pulse] effect, proxy in    // copy the Bool, don't capture self
  effect.blur(radius: pulse ? 2 : 0)
}
```

（代码注释意思：复制那个 Bool 值，不要捕获 self。）

- **SwiftUI 的动作回调是有意设计成同步的。** 对时间敏感的界面更新——响应手势或滚动事件开始一个动画——必须和事件发生在同一帧。把 `withAnimation` 的状态变化放在同步回调里；只为之后那段长时间运行的工作开一个 `Task`。
- **把一块状态放在界面和异步工作的接缝处。** 视图启动一个任务；异步层完成时做一次同步修改；界面做出反应。这样能让视图逻辑保持同步，并且让异步逻辑不用导入 SwiftUI 就能测试。

---

## 7. 协议和泛型

不要一上来就写 class。**也不要一上来就写协议。**

工作流程：**写具体类型 → 注意到它们之间重复的代码 → 把共同的能力提取成一个协议 → 针对它写泛型代码。** 函数体几乎一样的重载，就是该泛化的信号。

- **一个没有任何按类型定制的协议，是一个浪费的协议。** 如果每个遵循者都会用同样的默认实现，就改为在已有的协议上写一个受约束的扩展。复杂的协议层级（“类型动物园”）耗编译时间和二进制大小，却什么也换不来。
- **优先“拥有”而不是“是一个”。** 如果一个协议的操作只有一部分对你的类型有意义，不要细化它——把它包进一个泛型 struct，只暴露你想要的 API。（用 `GeometricVector<Storage: SIMD>`，而不是 `GeometricVector: SIMD`。）
- **协议的要求是一个定制点**——它是动态派发的，遵循类型的实现在任何地方都会生效。**只在扩展里的方法是静态派发的**，所以遵循者自己的版本只会_遮蔽_它而不是覆盖它，只知道 `any P` 的代码调用的是扩展里的那个。如果一个类型应该能定制某件事，就把它做成要求。
- **组合优于继承。** 类继承是整块的（只有一个父类）、侵入性的（你会继承存储属性和初始化器的复杂度），还留下一堆没写出来的约定：什么能被覆盖、什么时候要调用 super。改为组合小的值。
- **强制向下转型是代码异味**——它通常意味着某个类型关系被类层级或存在类型弄丢了。

### `some` 对比 `any`

- **默认写 `some P`。当你需要存放任意类型时，再改成 `any P`。** 和“先 `let` 后 `var`”是同一个原则。
- `some P`——每个作用域里底层类型是固定的一个。你保留了所有类型关系，包括关联类型，编译器也能做特化。
- `any P`——类型擦除的盒子，动态类型在运行时会变。在存放不同类型的集合、底层类型需要可选、以及要完全隐藏抽象时需要它。你要为此付出代价：关联类型的关系被擦除到它们的上界，调用对优化器来说是不透明的。
- **你不能在 `any P` 上调用一个接收关联类型参数的方法。** 擦除在“产出”的位置可以用（结果被擦除到上界），在“消费”的位置不行。解决办法是把存在类型传给一个接收 `some P` 的函数——编译器会把它拆箱，在那个作用域里类型又是固定的了。
- **受约束的存在类型和不透明类型**——`some Collection<Element>`、`any Collection<any Animal>`——让你能隐藏 `LazyFilterSequence<[Animal]>`，同时仍然暴露元素类型。在你自己的协议上为调用者真正提供的那个类型声明主关联类型（`protocol Container<Item>`），而不是为 `Iterator` 这样的实现细节声明。
- **`where` 子句里的同类型要求**是跨协议确定关系的方式（`where Self.CropType.FeedType == Self`）。没有它们，“种下再收获”这种逻辑过不了类型检查，错误的遵循反而能编译通过。

---

## 8. API 设计——在使用的地方清晰

在使用的地方清晰，是这里比其他任何目标都重要的目标。

- **纯 Swift 的 API 不加类型前缀。** 模块会区分它们。只在 API 对应某个 Objective-C API 的地方保留前缀。但要避免在特定框架里用非常通用的名字——脱离上下文它们读起来很糟，还会逼人手动区分。
- **去掉开头的 `get`**，不管是 async 版本，还是任何直接返回结果的东西。写 `persistentPosts`，不写 `getPersistentPosts`。
- **访问控制就是文档。** `private`（文件内）、`internal`（模块内，默认）、`package`、`public`。在边界上写清楚，才会逼你做出上面那些关于可发送性和 API 演进的决定。
- **把模型设计成非法状态根本写不出来。** 私有 setter 加一个做校验的 mutating 方法；封闭的集合用 enum；用强类型的 `UUID` 而不是 `String`。
- **属性包装器**把一种_访问策略_提取出来（`@Argument`、`@Published`、防御性复制、延迟、线程局部），让声明处用一个词就说明策略。和基于 key path 的 `@dynamicMemberLookup` 结合，可以穿过包装器做投影（`$binding.title` 就是这样实现的）。
- 声明式的 DSL 用**结果构建器**。当样板代码是编译器本可以替你写的代码时，用**宏**（第 12 节）。

---

## 9. 性能——先测量，再选择

Swift 底层的性能主要由四种开销决定。要知道你在付哪一种。

1. **函数调用**——参数复制、静态和动态派发、调用帧分配，以及被阻碍的优化。
2. **内存布局**——内联存储和外部存储；动态大小的类型。
3. **分配**——全局（免费）、栈（便宜：一次减法）、堆（昂贵：查找加加锁）。
4. **复制**——retain/release，以及 struct 的递归复制。

**但先做算法上的功夫。** 每次写循环时，试着把它换成一个算法调用。最大的收益几乎从来不是微优化：

- **知道你调用的东西的复杂度。** `Array.remove(at:)` 是 O(n)；在循环里调用它就是 O(n²)。`removeAll(where:)` 总共是 O(n)。每个字节都重新切片来构建 `Data` 是 O(n²)；`popFirst()` 是 O(1)。这两个都是藏在干净代码背后的 100 倍以上的性能倒退。
- **链式的 `map`/`flatMap`/`filter` 每一步都会分配一个数组。** 优雅 ≠ 快。如果一条流水线在热循环里对每个像素或每个元素都运行，就一次性确定输出的大小，然后往里写。
- **然后做性能分析。** 用 Instruments 的 Time Profiler 和 Allocations，针对一个_测试_运行（右键点测试的运行按钮 → Profile），这样你测的正好是你关心的代码。火焰图里 `platform_memmove` 占大头，意味着意外的复制；上百万次短暂的分配，意味着中间数组；`swift_beginAccess` 意味着运行时的独占性检查；`swift_retain`/`swift_release` 意味着引用计数的开销。

**具体的手段，大致按收益排序：**

- **对不打算被继承的类加 `final`**，能把动态派发变成静态派发，并解锁内联。整模块优化在很多情况下能让编译器替你证明这一点——还能启用泛型特化，到这一步泛型就不再有任何开销。
- **struct 的存储是内联的；class 的存储是外部的。** 小 struct 免费；一个带三个引用类型字段的大 struct，_每次复制_要三次 retain，而 class 只要一次。如果你经常复制它，用写时复制。
- **一个 `any P` 存在类型有一个 3 个字长的内联缓冲区。** 放得下的值就内联存放；更大的值每次复制都要在堆上分配。同样的技巧适用：给大类型加上带写时复制的间接存储，它就又能放进缓冲区了。
- **同质的 `[MyModel]` 好过 `[any Model]`**——排列紧密，类型信息只传一次，可以特化。`[any Model]` 是灵活但不透明的选项；需要时再用它。
- **把泛型参数约束为 class**（`T: AnyObject`），即使没有特化，也能让编译器知道它的表示方式。
- **`InlineArray<N, T>`**（Swift 6.2）用于固定大小的存储：元素内联存放，大小通过值泛型写在类型里，没有堆分配、没有引用计数、没有唯一性或独占性检查。如果它会被复制或共享，就是错误的选择。
- **`Span` / `RawSpan` / `OutputSpan`**（Swift 6.2）取代 `withUnsafeBufferPointer`，用于直接访问连续存储。它们不能逃逸，所以编译器会把它们的生命周期和容器绑定——你得到指针级的性能，却没有生命周期 bug，retain/release 也消失了。
- **把存储属性从嵌套的 class 里移到外层的 struct 里**，能去掉运行时的独占性检查。
- Swift 6.3 已经提供的，在你测量过需要时再用：`@inline(always)`（方法上配合 `final`）和 `@specialized(where T == ...)`（SE-0460），为热点的具体类型预先特化泛型。
- Swift 6.4 里即将有的（**还没发布**——见第 15 节下面的说明）：对大的存储值用 `borrow`/`mutate` 访问器代替 `get`/`set`，`UniqueArray`/`UniqueBox`，以及用 `Ref`/`MutableRef` 把重复的查找提到循环外面。

**async 函数**把它们的状态放在每个任务的 slab 分配器上，而不是 C 栈上，并在每个挂起点拆成若干部分函数。开销情况和同步函数差不多，调用开销略高——这也是另一个理由：没有要等待的东西，就不要把它做成 `async`。

**跳到主 actor 和从主 actor 跳回来，要付出一次真正的上下文切换。** 要批量处理：把循环推_进_ `loadArticles`/`updateUI` 里，让它们接收数组，而不是每次迭代跳两次。

---

## 10. ARC 和对象生命周期

- **一个对象被保证的生命周期，在最后一次使用时结束，而不是在右花括号处。** 观察到的生命周期是优化器的副产品，_一定会_变。依赖 `deinit` 什么时候运行的代码，是一个潜在的 bug。
- **`weak`/`unowned` 只用来打破循环引用——别的都不用。** 在强引用持有者最后一次使用之后读取一个 `weak` 引用，合理地可能得到 `nil`。在那里用可选绑定，比强制解包_更糟_：它把一次响亮的崩溃变成一个悄无声息的错误结果。
- **比 `weak` 更好的是：不要造出循环。** 把共享的数据提取到一个双方都引用的第三个类型里，把循环变成一棵树。
- **次好的是：重新设计 API**，让这个对象只能通过强引用访问到。`withExtendedLifetime` 能用，但它把正确性的负担转给了你，并且会在代码库里扩散——把它当作补丁，而不是设计。
- **让 `deinit` 的副作用保持局部。** 在 `deinit` 里发布指标或触发全局效果，会让顺序取决于优化器的决定。改为在调用处用 `defer`，把 `deinit` 留给校验。
- Xcode 的 **Optimize Object Lifetimes**（优化对象生命周期）构建设置会把观察到的生命周期缩短到被保证的最小值，正好能暴露这些 bug。

---

## 11. 测试——默认用 Swift Testing

新测试用 **Swift Testing**。只有三件事仍然必须用 XCTest：界面自动化（`XCUIApplication`）、性能指标（`XCTMetric`），以及必须用 Objective-C 写或要捕获 Objective-C 异常的测试。

- **`@Test` 可以加在任何函数上**——全局、静态或实例方法；`async`、`throws` 和全局 actor 隔离的都行。
- **`#expect(...)` 接收普通的表达式。** 不用记一整套 `XCTAssertEqual` 风格的函数——`#expect(a == b)`、`#expect(list.isEmpty)`、`#expect(!x.contains(y))` 在失败时都会捕获并显示子表达式的值。
- **`try #require(...)`** 用来在失败时停止测试，也用来安全地解包可选值。它取代了 `continueAfterFailure = false`，并且让你可以逐个期望地选择。
- **测试套件是 `struct`。** 每个测试函数都会创建一个新实例，所以状态不会在测试之间泄漏。用 `init` 做准备；只有需要 `deinit` 做清理时才用 `class`/`actor`。嵌套套件来分组。
- **用参数化代替复制粘贴或循环。** `@Test(arguments: [...])` 让每个用例独立运行、并行、可以单独重跑，结果里还会写出失败的参数。两组参数会产生完整的笛卡尔积——想要一一配对时用 `zip()`。
- **特性（trait）表达意图：** 条件用 `.enabled(if:)` / `.disabled("reason")`（绝不要把测试注释掉——被禁用的测试仍然会编译），跟踪用 `.bug(url)`，跨文件和目标关联测试用 `.tags(...)`，还有 `.timeLimit`，测试确实不能并行时用 `.serialized`。用 `@available` 而不是运行时的 `#available` 检查，这样测试库能知道。
- **`withKnownIssue { }`** 用于因为你控制不了的原因而失败的测试——和 `.disabled` 不同，它会继续编译和运行，并在问题被修好时告诉你。
- 会触发 N 次的回调用 **`confirmation`**；没有 async 版本的一次性回调用 `withCheckedContinuation`。
- **测试默认并行运行，顺序随机。** 这是个特性：它能暴露测试之间隐藏的依赖。要重构，而不是去用 `.serialized`。
- **退出测试**——`#expect(processExitsWith: .failure) { ... }`——在隔离的子进程里覆盖 `precondition`/`fatalError` 路径。只支持 macOS、Linux、FreeBSD、Windows。
- 迁移：两个框架可以在同一个 target 里共存，所以逐步迁移，今天就开始用 Swift Testing 写新测试。**测试框架互操作**（swift-testing ST-0021；看你的 Xcode 版本是否支持）让包装了 `XCTFail` 的辅助函数能在 Swift Testing 测试里调用，反过来也行；把模式设成 **complete** 或 **strict**（不要 **limited**，绝不要 **none**），这样跨框架的问题仍然算错误，并会指引你用 `Issue.record` 替代。

---

## 12. 宏

当你在写编译器本可以推导出来的代码时，再用宏——只在这时。

- **宏在展开之前会做类型检查。** 参数会按宏声明的签名检查，所以用错了会在调用处得到一个清楚的错误，而不是生成代码里的一团乱。
- **独立宏（`#foo`）**产出一个表达式或声明。**附加宏（`@Foo`）**以五种角色之一增强一个声明：member、peer、accessor、member-attribute、conformance。角色可以组合——`@Observable` 就是 member + member-attribute + conformance。
- **把宏当作纯粹的语法树变换来测试**，用 `assertMacroExpansion`。这是最快的循环，也是避免“没人读的代码”里出 bug 的方法。在 `expansion` 里设个断点，`po` 一下语法节点，就能了解它的结构。
- **宏不适用时，发出真正的诊断。** 抛出错误，或者用 `context.addDiagnostic` 在具体位置给出警告和修复建议。绝不要让宏悄悄生成编译不过的代码。
- 展开后的代码就是普通的 Swift：可以查看（“Expand Macro”）、调试、单步执行。

---

## 13. 日志和调试

- **用 `os` 里的 `Logger`，不用 `print`。** 每个子系统和类别创建一个。消息以优化过的形式存储，只在显示时才渲染，所以日志足够便宜，可以留在代码里。
- **非数字的插值默认会被打码。** 只对真的不是个人信息的数据，逐个值用 `privacy: .public` 选择公开。需要关联值又不想暴露时，用 `.private(mask: .hash)`。
- **级别控制持久化和开销：** `debug`（从不持久化，最快——不在实时查看时，构造消息的代码会被完全优化掉）、`info`、`notice`（默认）、`error`、`fault`（持久化最久，最慢）。你会希望出现在 bug 报告里的东西，用 `error`/`fault` 级别记录。
- **记录一个关联 ID**（一个任务或请求的 UUID），你就能从设备日志归档里筛出一次失败的完整历史，不用复现。`log collect --device --start ...`，然后在“控制台”里按子系统筛选。
- `format:` 和 `align:` 是免费的——用它们让日志好读、可以按列选择。
- LLDB 理解 Swift 任务：它能跨线程单步越过 `await`，`swift task info` 显示优先级和子任务，有名字的任务在调试器和 Instruments 的 Swift Concurrency 模板里都会显示出来。

---

## 14. 不安全代码和互操作

- **“不安全”的意思是 API 无法完全校验它的输入，所以违反它的前提条件是未定义行为**——而不是会崩溃。安全的 API _确实_会有意地崩溃；一个干净的致命错误才是安全的结果。
- **优先用 `Span` 而不是 `Unsafe*Pointer`。** 从 Swift 6.2 开始，有了一种安全、不逃逸、同样快的方式来访问连续存储。原始指针留给 C 互操作。
- 如果一定要用指针：让不安全的区域尽量小，用 **buffer** 指针（地址 + 数量）而不是光秃秃的指针，这样边界能被跟踪；绝不让指针逃出提供它的那个闭包；并且运行 **Address Sanitizer**。
- 在对安全要求高的模块里启用 **strict memory safety**（严格内存安全）——它强制每一处不安全的用法都在源码里被承认，这才让审计成为可能。Swift 6.4 的 `@diagnose` 属性（还没发布）能让你对单个函数开启它。
- **互操作是双向的，可以逐步进行。** C、Objective-C 和 C++ 的类型能直接映射到 Swift（包括 C++ 的值语义、作为 Swift 集合的容器，以及作为 `~Copyable` 的只能移动的类型）。Swift 6.3 的 `@c` 属性能把 Swift 函数反过来暴露给 C（当声明已经在头文件里时，配合 `@implementation`）。一次一个文件地采用 Swift；不要重写。

---

## 15. 你应该用上的现代语法

AI 助手经常写出下面这些东西更老、更长的写法。

**标了 ⚠ 的行是 Swift 6.4，它还没发布。** 当前正式版是 6.3.x。它们的提案已被接受并在主分支里实现了，所以可以放心为它们做规划，但今天写出来是不安全的——用之前先检查项目的工具链，如果项目的目标是 6.3 或更早，就优先用老写法。

| Instead of                                                            | Write                                                                                                    | Since |
| --------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- | ----- |
| 嵌套的三元表达式；用一个立即调用的闭包来初始化 `let`                  | `if`/`switch` **表达式**                                                                                 | 5.9   |
| 为 1 个、2 个、3 个……参数写重载                                       | **参数包**（`each T`），以及对参数包用 `for`                                                             | 5.9   |
| `ObservableObject` + 每个属性都加 `@Published`                        | **`@Observable`**                                                                                        | 5.9   |
| 轮询一个对象看有没有变化                                              | **`Observations { ... }`**——一个提供事务性更新的 `AsyncSequence`                                         | 6.2   |
| 用字符串类型的 `userInfo` 的 `NotificationCenter`                     | 具体的通知类型（`MainActorMessage` / `AsyncMessage`）                                                    | 6.2   |
| 写脚本时用 `Process` + 管道                                           | **Subprocess** 包（逐行输出用 `AsyncBufferSequence.strings()`；1.0 随 6.4 发布）                         | 6.2+  |
| 手写字符串下标计算                                                    | **Swift Regex**——要简短用字面量，要结构用 `RegexBuilder`                                                 | 5.7   |
| 热点路径里固定大小的 `[String]`                                       | **`InlineArray<N, T>`**                                                                                  | 6.2   |
| `withUnsafeBufferPointer`                                             | **`.span`** / **`.bytes`**（`RawSpan`）/ `OutputSpan`                                                    | 6.2   |
| 为了写完一次写入而手动摆弄 `Task.isCancelled`                         | `Task` **取消护盾**（SE-0504）                                                                           | 6.4 ⚠ |
| 为了用到 key 而手动重建一个字典                                       | **`mapKeyedValues`**                                                                                     | 6.4 ⚠ |
| `@available(iOS ..., macOS ..., tvOS ..., watchOS ..., visionOS ...)` | **`@available(anyAppleOS ...)`**                                                                         | 6.4 ⚠ |
| 类型遮蔽了模块名时写 `Rocket.SaturnV`                                 | **模块选择器** `Rocket::SaturnV`                                                                         | 6.3   |
| 一刀切的“把警告当错误”                                                | 按声明 / 警告组用 **`@diagnose`**                                                                        | 6.4 ⚠ |
| 因为一个 `weak var` 而用 `@unchecked Sendable`                        | `weak let`；或者用 **`~Sendable`** 声明不可发送                                                          | 6.4 ⚠ |
| 用指针手动解析二进制格式                                              | **Swift Binary Parsing**（`ParserSpan`，带溢出检查的解析初始化器）                                       | 6.2   |
| 别扭的测试函数名                                                      | **原始标识符**：`` @Test func `fruits have a tropical climate`() ``                                      | 6.0   |

（表头意思：Instead of = 不要写；Write = 改写成；Since = 从哪个版本开始。）

还值得知道：**Swift Regex 解析器能和 Foundation 真正的解析器组合**（`.date(...)`、`.currency(...)`）——绝不要在正则里手写日期或数字解析。把区域设置写明确，而不是继承系统的。并且用 `NegativeLookahead` 或 `Local`（原子组）阻止一个模式在整个输入上回溯。

---

## 16. 把现有代码库迁移到 Swift 6

顺序很重要，把步骤混在一起是迁移停滞的原因。

1. **先用新编译器构建。** 因为源码兼容，在 Swift 5 模式下这应该直接就能通过。
2. **逐个 target 启用完整的并发检查**（Swift 5 模式 + 所有 Swift 6 警告）。从**界面/app 层**开始，而不是它下面的框架——这一层很多已经被 SDK 标注为主 actor 了，所以修复率很高。
3. **修复警告，先修最便宜的。** 预计会有成百上千条警告，来自少数几个根本原因：应该是 `let` 的 `var` 全局变量、应该放在 `@MainActor` 上的自由函数、一个需要 `: Sendable` 的公开 struct。改一行就能清掉几十条。
4. **把 target 切换到 Swift 6 语言模式**，把成果锁定下来。
5. **换到下一个 target，重复。**
6. **之后再单独重构。** 绝不要把一次大的重构和启用数据竞争安全放在一起——你会不得不把两个都撤回。

你可以把严格检查重新关掉然后发布；你做的每一处修复都是真正的改进，会保留下来。在开始_之前_启用 **Approachable Concurrency**，对 app 模块还要启用默认主 actor——两者都能大幅减少你会看到的错误数量，而且 Xcode 自带的迁移工具能替你完成很多改动（swift.org/migration）。

---

## 速查表

| Need                               | Reach for                       | Not                                       |
| ---------------------------------- | ------------------------------- | ----------------------------------------- |
| 一个数据类型                       | `struct` / `enum`               | 没有身份或共享需求的 `class`              |
| 共享的可变状态                     | `actor`，或 `@MainActor` 类     | `class` + 一把你必须记得用的锁            |
| 把工作移出主线程                   | `@concurrent func … async`      | `Task.detached`、`DispatchQueue.global()` |
| 库 API 的隔离方式                  | `nonisolated`                   | `@MainActor`、`@concurrent`               |
| 数量固定的并行工作                 | `async let`                     | N 个非结构化的 `Task`                     |
| 数量动态的并行工作                 | `withTaskGroup`（限制数量）     | 每个元素一个任务，没有上限                |
| 不返回任何东西的子任务             | `withDiscardingTaskGroup`       | 从不读完结果的 `withTaskGroup`            |
| 和界面事件绑定的工作               | 回调里的 `Task { }`             | 把回调改成 `async`                        |
| 修复数据竞争                       | 停止共享那个对象                | `@unchecked Sendable`                     |
| 共享的模型类                       | 非 `Sendable`，或 `@MainActor`  | `Sendable` + 手动加锁                     |
| 跨 `await` 的阻塞原语              | 什么都不用——重新组织代码        | `DispatchSemaphore`、`NSCondition`        |
| 多态                               | `some P`                        | `any P`，除非你需要存放               |
| 存放不同类型的集合                 | `[any P]`                       | 一个类层级                                |
| 共同的行为，不需要定制             | 受约束的 `extension`            | 一个新协议                                |
| 一个定制点                         | 协议**要求**                    | 只在扩展里的方法                          |
| 打破循环引用                       | 重新组织成一棵树                | `weak` + `withExtendedLifetime`           |
| 删除匹配的元素                     | `removeAll(where:)`——O(n)       | 循环里 `remove(at:)`——O(n²)               |
| 直接访问连续内存                   | `.span`                         | `withUnsafeBufferPointer`                 |
| 热点路径里的固定大小缓冲区         | `InlineArray<N, T>`             | `Array`                                   |
| 一个新测试                         | `@Test` + `#expect`             | `XCTestCase` + `XCTAssertEqual`           |
| 同一个测试跑很多输入               | `@Test(arguments:)`             | 一个 `for` 循环，或者复制粘贴             |
| 失败时停止测试                     | `try #require`                  | `continueAfterFailure = false`            |
| 一个暂时坏掉的测试                 | `withKnownIssue`                | `.disabled`，或者把它注释掉               |
| 发布代码里的诊断信息               | `Logger` + 一个关联 ID          | `print`                                   |
| 决定要不要优化                     | 在被分析的测试上跑 Instruments  | 直觉                                      |

（表头意思：Need = 需要什么；Reach for = 用什么；Not = 不要用什么。）
