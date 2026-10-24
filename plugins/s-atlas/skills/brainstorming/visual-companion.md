本技能译自 Jesse Vincent 的 Superpowers（MIT）。许可证见 [LICENSE-superpowers](../../LICENSE-superpowers)。

# 视觉伴侣指南

基于浏览器的视觉头脑风暴伴侣，用来展示草图、示意图和选项。

## 何时使用

按每一个问题来决定，而不是按整个会话来决定。检验标准是：**用户看一眼是否比读一段文字更容易理解？**

**用浏览器**，当内容本身是视觉的：

- **界面草图** — 线框、布局、导航结构、组件设计
- **架构图** — 系统组件、数据流、关系图
- **并排的视觉对比** — 比较两种布局、两套配色、两个设计方向
- **设计打磨** — 当问题关乎观感、间距、视觉层级
- **空间关系** — 状态机、流程图、画成图的实体关系

**用终端**，当内容是文字或表格：

- **需求和范围问题** — 「X 是什么意思？」「哪些功能在范围内？」
- **概念性的 A/B/C 选择** — 在用文字描述的做法之间挑选
- **取舍列表** — 优点/缺点、对比表
- **技术决策** — API 设计、数据建模、架构做法的选择
- **澄清问题** — 答案是文字、而不是视觉偏好的任何问题

一个*关于*界面话题的问题，并不自动就是视觉问题。「你想要什么样的向导？」是概念问题——用终端。「这几种向导布局，哪一个感觉对？」是视觉问题——用浏览器。

## 它如何工作

服务器监视一个目录里的 HTML 文件，并把最新的一个提供给浏览器。你把 HTML 内容写到 `screen_dir`，用户在浏览器里看到它，可以点击来选择选项。选择被记录到 `state_dir/events`，你在下一轮读取。

**内容片段与完整文档：** 如果你的 HTML 文件以 `<!DOCTYPE` 或 `<html` 开头，服务器按原样提供（只注入辅助脚本）。否则，服务器会自动用框架模板包住你的内容——加上页眉、CSS 主题、连接状态，以及全部交互基础设施。**默认写内容片段。** 只有在你需要完全控制页面时，才写完整文档。

## 开始一次会话

```bash
# Start AFTER the user approves the companion. --open auto-opens their browser on
# the first screen; --project-dir persists mockups and enables same-port restart.
scripts/start-server.sh --project-dir /path/to/project --open

# Returns: {"type":"server-started","port":52341,
#           "url":"http://localhost:52341/?key=ab12…",
#           "screen_dir":"/path/to/project/.superpowers/brainstorm/12345-1706000000/content",
#           "state_dir":"/path/to/project/.superpowers/brainstorm/12345-1706000000/state"}
```

从响应里保存 `screen_dir` 和 `state_dir`。加上 `--open` 时，你推送第一屏之后浏览器会自己打开——你不需要请用户去打开它，但仍然要把 URL 作为后备发给用户（无界面或远程环境不会自动打开）。

**URL 里含有会话密钥（`?key=…`）。** 没有它的请求，服务器会拒绝，所以始终把 `url` 字段里的**完整** URL 给用户——不要去掉查询字符串，也不要只给一个只有主机和端口的 `http://host:port`。这个密钥同时把守 HTTP 和 WebSocket，这样一个随便打开的浏览器标签，或同一网络上的另一台机器，就不能读取画面或注入事件。第一次加载之后，浏览器通过 cookie 记住密钥，所以刷新和 `/files/*` 资源不必再带一次。

**查找连接信息：** 服务器把自己的启动 JSON 写到 `$STATE_DIR/server-info`。如果你在后台启动了服务器，又没有捕获标准输出，读这个文件来拿到 URL 和端口。使用 `--project-dir` 时，到 `<project>/.superpowers/brainstorm/` 里找会话目录。

**注意：** 把项目根目录作为 `--project-dir` 传进去，这样草图会持久留在 `.superpowers/brainstorm/` 里，服务器重启之后还在。不传的话，文件会进 `/tmp`，然后被清掉。如果 `.gitignore` 里还没有，提醒用户把 `.superpowers/` 加进去。

**按平台启动服务器：**

**Claude Code：**
```bash
# Default mode works — the script backgrounds the server itself.
scripts/start-server.sh --project-dir /path/to/project --open
```

在 Windows 上，脚本会自动检测并切换到前台模式（这会卡住这次工具调用）。在 Bash 工具调用上设置 `run_in_background: true`，这样服务器才能在后续对话轮次里继续运行，然后在下一轮读取 `$STATE_DIR/server-info`，拿到 URL 和端口。

**Codex：**
```bash
# Codex reaps background processes. The script auto-detects CODEX_CI and
# switches to foreground mode. Run it normally — no extra flags needed.
scripts/start-server.sh --project-dir /path/to/project --open
```

**Copilot CLI：**
```bash
# Use --foreground and start the server via the bash tool with mode: "async"
# so the process survives across turns. Capture the returned shellId for
# read_bash / stop_bash if you need to interact with it later.
scripts/start-server.sh --project-dir /path/to/project --open --foreground
```

**其他环境：** 服务器必须在后台跨多个对话轮次一直运行。如果你的环境会回收已经脱离的进程，使用 `--foreground`，并用你这个平台的后台执行方式来启动命令。

如果从浏览器访问不到这个 URL（远程或容器环境里很常见），就绑定一个非回环地址：

```bash
scripts/start-server.sh \
  --project-dir /path/to/project \
  --host 0.0.0.0 \
  --url-host localhost
```

用 `--url-host` 控制返回的 URL JSON 里打印哪个主机名。

## 循环

1. **确认服务器还活着**，然后把 **HTML 写到** `screen_dir` 里的一个新文件：
   - **必需：在提到 URL 或推送画面之前，确认服务器还活着。** 检查 `$STATE_DIR/server-info` 存在，并且 `$STATE_DIR/server-stopped` 不存在。如果它已经停了，用 `start-server.sh` 和**同一个 `--project-dir`** 重新启动——它会复用同一个端口，所以用户打开的标签会自己重连（服务器停着的时候会显示一层 "paused" 遮罩），你不需要再发一个新 URL。服务器空闲 4 小时后会自动退出（可以用 `--idle-timeout-minutes` 配置）。
   - 使用有含义的文件名：`platform.html`、`visual-style.html`、`layout.html`
   - **不要复用文件名**——每一屏都用一个新文件
   - 用你的文件创建工具——**不要用 cat/heredoc**（会把噪声倒进终端）
   - 服务器会自动提供最新的文件

2. **告诉用户接下来会看到什么，然后结束你这一轮：**
   - 每一步都提醒他们 URL，不只是第一步
   - 用一句短文字概括屏幕上有什么（例如「正在展示首页的 3 种布局」）
   - 请他们在终端里回应：「看一下，然后告诉我你怎么想。如果愿意，可以点击选择一个选项。」

3. **到你的下一轮**——用户在终端里回应之后：
   - 如果 `$STATE_DIR/events` 存在，就读它——里面是用户浏览器交互（点击、选择）的 JSON 行
   - 和用户的终端文字合在一起，得到完整情况
   - 终端消息是主要反馈；`state_dir/events` 提供结构化的交互数据

4. **迭代，或者往下走**——如果反馈改变了当前画面，就写一个新文件（例如 `layout-v2.html`）。当前这一步被确认之后，才进入下一个问题。

5. **回到终端时卸掉画面**——下一步不需要浏览器时（例如一个澄清问题、一场取舍讨论），推送一个等待画面，把过时内容清掉：

   ```html
   <!-- filename: waiting.html (or waiting-2.html, etc.) -->
   <div style="display:flex;align-items:center;justify-content:center;min-height:60vh">
     <p class="subtitle">Continuing in terminal...</p>
   </div>
   ```

   这样用户就不会还盯着一个已经定了的选择，而对话其实已经往前走了。下一个视觉问题出现时，照常推送新的内容文件。

6. 重复，直到做完。

## 编写内容片段

只写放进页面里面的那部分内容。服务器会自动用框架模板把它包起来（页眉、主题 CSS、连接状态，以及全部交互基础设施）。

**最小例子：**

```html
<h2>Which layout works better?</h2>
<p class="subtitle">Consider readability and visual hierarchy</p>

<div class="options">
  <div class="option" data-choice="a" onclick="toggleSelect(this)">
    <div class="letter">A</div>
    <div class="content">
      <h3>Single Column</h3>
      <p>Clean, focused reading experience</p>
    </div>
  </div>
  <div class="option" data-choice="b" onclick="toggleSelect(this)">
    <div class="letter">B</div>
    <div class="content">
      <h3>Two Column</h3>
      <p>Sidebar navigation with main content</p>
    </div>
  </div>
</div>
```

就这些。不需要 `<html>`，不需要 CSS，也不需要 `<script>` 标签。这些都由服务器提供。

## 可用的 CSS 类

框架模板为你的内容提供这些 CSS 类：

### 选项（A/B/C 选择）

```html
<div class="options">
  <div class="option" data-choice="a" onclick="toggleSelect(this)">
    <div class="letter">A</div>
    <div class="content">
      <h3>Title</h3>
      <p>Description</p>
    </div>
  </div>
</div>
```

**多选：** 给容器加上 `data-multiselect`，用户就可以选多个选项。每点一次，就切换该项的选中样式。

```html
<div class="options" data-multiselect>
  <!-- same option markup — users can select/deselect multiple -->
</div>
```

### 卡片（视觉设计）

```html
<div class="cards">
  <div class="card" data-choice="design1" onclick="toggleSelect(this)">
    <div class="card-image"><!-- mockup content --></div>
    <div class="card-body">
      <h3>Name</h3>
      <p>Description</p>
    </div>
  </div>
</div>
```

### 草图容器

```html
<div class="mockup">
  <div class="mockup-header">Preview: Dashboard Layout</div>
  <div class="mockup-body"><!-- your mockup HTML --></div>
</div>
```

### 分栏（并排）

```html
<div class="split">
  <div class="mockup"><!-- left --></div>
  <div class="mockup"><!-- right --></div>
</div>
```

### 优点/缺点

```html
<div class="pros-cons">
  <div class="pros"><h4>Pros</h4><ul><li>Benefit</li></ul></div>
  <div class="cons"><h4>Cons</h4><ul><li>Drawback</li></ul></div>
</div>
```

### 草图元素（线框积木）

```html
<div class="mock-nav">Logo | Home | About | Contact</div>
<div style="display: flex;">
  <div class="mock-sidebar">Navigation</div>
  <div class="mock-content">Main content area</div>
</div>
<button class="mock-button">Action Button</button>
<input class="mock-input" placeholder="Input field">
<div class="placeholder">Placeholder area</div>
```

### 排版和分节

- `h2` — 页面标题
- `h3` — 小节标题
- `.subtitle` — 标题下面的次要文字
- `.section` — 带底部外边距的内容块
- `.label` — 小号大写标签文字

## 浏览器事件格式

用户在浏览器里点击选项时，交互会被记到 `$STATE_DIR/events`（一行一个 JSON 对象）。你推送新画面时，这个文件会自动清空。

```jsonl
{"type":"click","choice":"a","text":"Option A - Simple Layout","timestamp":1706000101}
{"type":"click","choice":"c","text":"Option C - Complex Grid","timestamp":1706000108}
{"type":"click","choice":"b","text":"Option B - Hybrid","timestamp":1706000115}
```

完整的事件流展示用户的探索路径——他们可能在定下来之前点过多个选项。最后一条 `choice` 事件通常就是最终选择，但点击的模式可能露出犹豫，或值得再问一句的偏好。

如果 `$STATE_DIR/events` 不存在，说明用户没有在浏览器里操作——只用他们的终端文字。

## 设计提示

- **保真度要配得上问题** — 布局问题用线框，打磨问题用打磨过的画面
- **每一页都把问题写清楚** — 「哪种布局感觉更专业？」而不只是「选一个」
- **往下走之前先迭代** — 如果反馈改变了当前画面，就写一个新版本
- 每屏**最多 2-4 个选项**
- **在要紧的时候用真实内容** — 摄影作品集就用真实图片（Unsplash）。占位内容会把设计问题盖住。
- **草图保持简单** — 聚焦布局和结构，而不是像素级设计

## 文件命名

- 使用有含义的名字：`platform.html`、`visual-style.html`、`layout.html`
- 不要复用文件名——每一屏都必须是一个新文件
- 迭代时：加上版本后缀，例如 `layout-v2.html`、`layout-v3.html`
- 服务器按修改时间提供最新的文件

## 清理

```bash
scripts/stop-server.sh $SESSION_DIR
```

如果这次会话用了 `--project-dir`，草图文件会留在 `.superpowers/brainstorm/` 里，以后还能看。只有 `/tmp` 里的会话会在停止时被删掉。

## 参考

- 框架模板（CSS 参考）：`scripts/frame-template.html`
- 辅助脚本（客户端）：`scripts/helper.js`
