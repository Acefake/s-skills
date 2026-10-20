---
name: shadcn
description: "中文：管理 shadcn 组件和项目，包括添加、搜索、修、排查、样式和组合界面（也包括聊天界面）。项目里有 components.json，或用户说 shadcn、注册表、preset、做设计系统、套用 DESIGN.md 时使用。rules/ 仍是英文。Use when the project uses shadcn and you are adding, fixing, or composing those components."
---
## 运行环境适配

在 Codex 或 T3 Code 中，执行前先阅读[宿主适配规则](../../../plugins/s/HOSTS.md)；其中的模型、委派、浏览器和定时任务规则优先于下文的 Cursor 专用示例。


# shadcn/ui

一套用来做界面、组件和设计系统的框架。组件通过 CLI，以源码加进用户的项目。

> **先看包管理器。** 所有 CLI 命令都按项目的 `packageManager` 来跑：`npx shadcn@latest`、`pnpm dlx shadcn@latest`，或 `bunx --bun shadcn@latest`。下面的例子写的是 `npx shadcn@latest`，换成这个项目实际用的那个。

## 当前项目

```json
!`npx shadcn@latest info --json`
```

上面这段 JSON 是项目配置，以及已经装上的组件。要某个组件的文档和示例链接，用 `npx shadcn@latest docs <component>`。

## 在不同软件里怎么用

代码块里以 `!` 开头的那一行，只有 Claude Code 加载技能时会替你执行。Cursor、Codex、OpenCode、WorkBuddy 不会。这些软件里，自己在项目根目录跑 `npx shadcn@latest info --json`。项目用 pnpm 就用 `pnpm dlx shadcn@latest info --json`，用 bun 就用 `bunx --bun shadcn@latest info --json`。然后读输出。后面例子里的 `npx shadcn@latest` 也按项目的包管理器换。

## 原则

1. **先用现成组件。** 写自定义界面之前，用 `npx shadcn@latest search` 查注册表。社区注册表也要查。
2. **拼，不要重做一套。** 设置页就是 Tabs + Card + 表单控件。仪表盘就是 Sidebar + Card + Chart + Table。
3. **先用自带的 variant，再自己写样式。** 比如 `variant="outline"`、`size="sm"`。
4. **用语义颜色。** 用 `bg-primary`、`text-muted-foreground`。不要写 `bg-blue-500` 这种写死的颜色。

## 必须守的规则

这些规则一律要守。链出去的文件里有写错和写对的代码对照。这些附带说明仍是英文，里面的正误代码对照要按原文遵守。

### 样式和 Tailwind → [styling.md](./rules/styling.md)

- **`className` 用来排布局，不用来改样式。** 不要覆盖组件的颜色或字体排版。
- **不要用 `space-x-*` 或 `space-y-*`。** 用 `flex` 配 `gap-*`。竖着排就用 `flex flex-col gap-*`。
- **宽和高一样时用 `size-*`。** 写 `size-10`，不要写 `w-10 h-10`。
- **截断用 `truncate`。** 不要写 `overflow-hidden text-ellipsis whitespace-nowrap`。
- **不要手写 `dark:` 来改颜色。** 用语义 token，比如 `bg-background`、`text-muted-foreground`。
- **有条件才加上的类名，用 `cn()`。** 不要手写模板字符串里的三元表达式。
- **浮层组件不要手写 `z-index`。** Dialog、Sheet、Popover 这些自己管叠放顺序。

### 表单和输入 → [forms.md](./rules/forms.md)

- **表单用 `FieldGroup` + `Field`。** 表单布局不要用裸的 `div` 配 `space-y-*` 或 `grid gap-*`。
- **`InputGroup` 里面用 `InputGroupInput` 或 `InputGroupTextarea`。** 不要把裸的 `Input` 或 `Textarea` 放进 `InputGroup`。
- **输入框里面放按钮时，用 `InputGroup` + `InputGroupAddon`。**
- **一组选项（2 到 7 个）用 `ToggleGroup`。** 不要循环 `Button`，再自己管哪个是选中的。
- **相关的 checkbox 或 radio 要分组，用 `FieldSet` + `FieldLegend`。** 不要用一个带标题的 `div`。
- **字段校验用 `data-invalid` 和 `aria-invalid`。** `data-invalid` 放在 `Field` 上，`aria-invalid` 放在控件上。禁用也一样：`data-disabled` 放在 `Field` 上，`disabled` 放在控件上。

### 组件结构 → [composition.md](./rules/composition.md)

- **Item 一定放在自己的 Group 里。** `SelectItem` 放进 `SelectGroup`。`DropdownMenuItem` 放进 `DropdownMenuGroup`。`CommandItem` 放进 `CommandGroup`。
- **自定义触发器：radix 用 `asChild`，base 用 `render`。** `base` 是哪种，看 `npx shadcn@latest info` 的 `base` 字段。→ [base-vs-radix.md](./rules/base-vs-radix.md)
- **Dialog、Sheet、Drawer 一定要有标题。** 无障碍需要 `DialogTitle`、`SheetTitle`、`DrawerTitle`。不想让人看见，就加 `className="sr-only"`。
- **Card 用完整结构。** `CardHeader`、`CardTitle`、`CardDescription`、`CardContent`、`CardFooter` 都要用上。不要全堆进 `CardContent`。
- **Button 没有 `isPending`，也没有 `isLoading`。** 用 `Spinner` + `data-icon` + `disabled` 拼。
- **`TabsTrigger` 必须放在 `TabsList` 里面。** 不要把 trigger 直接放在 `Tabs` 里。
- **`Avatar` 一定要有 `AvatarFallback`。** 图片加载失败时显示它。

### 用组件，别自己写标记 → [composition.md](./rules/composition.md)

- **先找现成组件，再自己写标记。** 写一个带样式的 `div` 之前，先看有没有现成组件。
- **提示条用 `Alert`。** 不要自己做带样式的 div。
- **空状态用 `Empty`。** 不要自己写空状态的标记。
- **Toast 跟项目的 base 走。** Base UI 项目用 `toast` 组件里的 `toast`。Radix 和 React Aria 项目用 `sonner` 的 `toast()`。
- **用 `Separator`。** 不要用 `<hr>` 或 `<div className="border-t">`。
- **加载时的占位用 `Skeleton`。** 不要自己写带 `animate-pulse` 的 div。
- **用 `Badge`。** 不要自己做带样式的 span。

### 图标 → [icons.md](./rules/icons.md)

- **`Button` 里的图标用 `data-icon`。** 图标上写 `data-icon="inline-start"` 或 `data-icon="inline-end"`。
- **组件里面的图标不要加尺寸类。** 组件用 CSS 管图标大小。不要加 `size-4` 或 `w-4 h-4`。
- **图标当对象传，不要传字符串 key。** 写 `icon={CheckIcon}`，不要拿字符串去查。

### 聊天和消息 → [chat.md](./rules/chat.md)

- **聊天界面用现成的聊天组件来拼。** 整段对话用 `MessageScroller`，每一行用 `Message`，气泡用 `Bubble`。不要自己写气泡 `div`，也不要用一个普通的滚动容器。
- **滚动归 `MessageScroller` 管。** 跟着流式输出往下滚、钉住滚动位置、跳到最新（`MessageScrollerButton`）都是现成的。不要自己写 `useStickToBottom` 或 `ResizeObserver` 的 hook。
- **附件用 `Attachment`。系统说明和分隔用 `Marker`。** 不要用 `Item` 卡片，也不要用 `Separator` 再加一段文字。
- **助手正在做什么，用 `Trace`。** 推理、工具调用、来源和步骤，都是一个 `Trace` 里的 `TraceLine`。每一轮的消息片段共用一个 `Trace`。这一行外面再包上交互：`TraceCollapsible`、一个 sheet 的触发器，或者一个链接。不要自己写 `Collapsible`，也不要用 `Marker`。

### CLI

- **不要自己解码 preset 代码，也不要手拼 preset 的 URL。** 用 `npx shadcn@latest preset decode <code>`、`preset url <code>` 或 `preset open <code>`。要按当前项目认出 preset，用 `npx shadcn@latest preset resolve`。
- **preset 代码直接交给 CLI。** 已有项目用 `npx shadcn@latest apply <code>`。初始化时用 `npx shadcn@latest init --preset <code>`。

## 常见写法

下面是最常见的写法，用来区分 shadcn/ui 代码写得对不对。边界情况看上面链出去的规则文件。

```tsx
// Form layout: FieldGroup + Field, not div + Label.
<FieldGroup>
  <Field>
    <FieldLabel htmlFor="email">Email</FieldLabel>
    <Input id="email" />
  </Field>
</FieldGroup>

// Validation: data-invalid on Field, aria-invalid on the control.
<Field data-invalid>
  <FieldLabel>Email</FieldLabel>
  <Input aria-invalid />
  <FieldDescription>Invalid email.</FieldDescription>
</Field>

// Icons in buttons: data-icon, no sizing classes.
<Button>
  <SearchIcon data-icon="inline-start" />
  Search
</Button>

// Spacing: gap-*, not space-y-*.
<div className="flex flex-col gap-4">  // correct
<div className="space-y-4">           // wrong

// Equal dimensions: size-*, not w-* h-*.
<Avatar className="size-10">   // correct
<Avatar className="w-10 h-10"> // wrong

// Status colors: Badge variants or semantic tokens, not raw colors.
<Badge variant="secondary">+20.1%</Badge>    // correct
<span className="text-emerald-600">+20.1%</span> // wrong
```

## 选哪个组件

| 要做什么 | 用什么 |
| --- | --- |
| 按钮或操作 | `Button`，选合适的 variant |
| 表单输入 | `Input`、`Select`、`Combobox`、`Switch`、`Checkbox`、`RadioGroup`、`Textarea`、`InputOTP`、`Slider` |
| 在 2 到 5 个选项之间切换 | `ToggleGroup` + `ToggleGroupItem` |
| 展示数据 | `Table`、`Card`、`Badge`、`Avatar` |
| 导航 | `Sidebar`、`NavigationMenu`、`Breadcrumb`、`Tabs`、`Pagination` |
| 浮层 | `Dialog`（模态框）、`Sheet`（侧边面板）、`Drawer`（底部面板）、`AlertDialog`（确认） |
| 反馈 | `toast`（Base UI）、`sonner`（Radix/Aria）、`Alert`、`Progress`、`Skeleton`、`Spinner` |
| 命令面板 | `Command`，放在 `Dialog` 里 |
| 图表 | `Chart`（包着 Recharts） |
| 布局 | `Card`、`Separator`、`Resizable`、`ScrollArea`、`Accordion`、`Collapsible` |
| 空状态 | `Empty` |
| 菜单 | `DropdownMenu`、`ContextMenu`、`Menubar` |
| 提示或说明 | `Tooltip`、`HoverCard`、`Popover` |
| 聊天或对话界面 | `MessageScroller`、`Message`、`Bubble`、`Attachment`、`Marker`、`Trace` |

## 关键字段

上面那段 JSON 里有这些字段：

- **`aliases`**：导入用实际的别名前缀，比如 `@/`、`~/`。不要写死。
- **`isRSC`**：是 `true` 的时候，用了 `useState`、`useEffect`、事件处理或浏览器 API 的组件，文件最上面要写 `"use client"`。要不要加这行，先看这个字段。
- **`tailwindVersion`**：`"v4"` 用 `@theme inline` 块。`"v3"` 用 `tailwind.config.js`。
- **`tailwindCssFile`**：定义自定义 CSS 变量的全局 CSS 文件。改这个文件，不要新建一个。
- **`style`**：组件长什么样。比如 `nova`、`vega`。
- **`base`**：底层组件库，`radix` 或 `base`。组件的 API 和有哪些 props，跟这个有关。
- **`iconLibrary`**：决定图标从哪导入。`lucide` 用 `lucide-react`，`tabler` 用 `@tabler/icons-react`，其他同理。不要默认当成 `lucide-react`。
- **`resolvedPaths`**：组件、utils、hooks 这些在文件系统里的准确位置。
- **`framework`**：路由和文件怎么放。比如 Next.js App Router，或 Vite 的单页应用。
- **`packageManager`**：装 shadcn 以外的依赖时按这个来。比如 `pnpm add date-fns`，或 `npm install date-fns`。
- **`preset`**：当前项目解析出来的 preset 代码和具体值。只要 preset 的信息，用 `npx shadcn@latest preset resolve --json`。

字段的完整说明见 [cli.md 里的 `info` 命令](./cli.md)。

## 组件文档、示例和用法

跑 `npx shadcn@latest docs <component>`，拿到这个组件的文档、示例和 API 参考的 URL。把这些 URL 抓下来看实际内容。

```bash
npx shadcn@latest docs button dialog select
```

**新建、修改、排查或使用一个组件时，都先跑 `npx shadcn@latest docs`，并把 URL 抓下来。** 这样用的是对的 API 和用法，不用猜。

## 步骤

1. **拿到项目上下文。** Claude Code 加载这个技能时，上面那段 JSON 已经跑过了。Cursor、Codex、OpenCode、WorkBuddy 按 [在不同软件里怎么用](#在不同软件里怎么用) 自己跑。要刷新，再跑一次 `npx shadcn@latest info`。
2. **先看已经装了哪些组件。** 跑 `add` 之前，先看项目上下文里的 `components` 列表，或者列出 `resolvedPaths.ui` 目录。没加过的组件不要导入。已经装了的不要再加一次。
3. **找组件。** `npx shadcn@latest search`。
4. **拿文档和示例。** 跑 `npx shadcn@latest docs <component>` 拿到 URL，再抓取。还没装的注册表项，用 `npx shadcn@latest view` 看。要预览已装组件的改动，用 `npx shadcn@latest add --diff`。
5. **安装或更新。** `npx shadcn@latest add`。更新已有组件时，先用 `--dry-run` 和 `--diff` 看会改什么（见下面的 [更新组件](#更新组件)）。
6. **改第三方组件里的导入。** 从社区注册表加了组件之后（比如 `@bundui`、`@magicui`），检查加进来的非 UI 文件，看有没有写死的导入路径，比如 `@/components/ui/...`。这些路径对不上项目实际的别名。用 `npx shadcn@latest info` 拿到正确的 `ui` 别名，比如 `@workspace/ui/components`，再把导入改成这个。CLI 会改它自己那些 UI 文件的导入。第三方注册表的组件可能用默认路径，跟项目对不上。
7. **检查加进来的组件。** 从任何注册表加了组件或 block 之后，**一定把加进来的文件读一遍，确认是对的**。查这几样：缺了子组件（比如有 `SelectItem` 没有 `SelectGroup`）、缺导入、组合不对、违反了 [必须守的规则](#必须守的规则)。图标导入也换成项目上下文里的 `iconLibrary`。注册表项用 `lucide-react`，项目用 `hugeicons` 的话，导入和图标名一起换。问题都修好，再继续。
8. **注册表必须写明。** 用户要加 block 或组件时，**不要猜注册表**。用户没指定（比如只说「加一个登录 block」，没说 `@shadcn`、`@tailark`、`owner/repo`），就问用哪个。不要替用户默认选一个。
9. **换 preset。** 先问用户要哪种：**覆盖**、**部分**、**合并**，还是**跳过**。
   - **看现在的 preset：** `npx shadcn@latest preset resolve`。要结构化的值，加上 `--json`。
   - **看要套进来的 preset：** `npx shadcn@latest preset decode <code>`。要分享，或者打开 preset 构建器，用 `preset url <code>` 或 `preset open <code>`。
   - **覆盖：** `npx shadcn@latest apply <code>`。会盖掉检测出来的组件、字体和 CSS 变量。
   - **部分：** `npx shadcn@latest apply <code> --only theme,font`。只更新选中的那几部分，不重装 UI 组件。支持的值是 `theme` 和 `font`，可以用逗号拼在一起。故意不支持 `icon`。换图标可能得把组件整个重装，还要做代码转换。
   - **合并：** 先跑 `npx shadcn@latest init --preset <code> --force --no-reinstall`，再跑 `npx shadcn@latest info` 列出已装组件，然后对每个已装组件用 `--dry-run` 和 `--diff`，按 [智能合并](#更新组件) 一个个处理。
   - **跳过：** `npx shadcn@latest init --preset <code> --force --no-reinstall`。只更新配置和 CSS，组件不动。
   - **preset 命令都在用户的项目目录里跑。** `apply` 只对已经有 `components.json` 的项目有效。CLI 会自动留下 `components.json` 里当前的 base（`base` 还是 `radix`）。如果一定要用临时目录（比如做 `--dry-run` 对比），显式传 `--base <current-base>`。preset 代码里不带 base。

## 按 DESIGN.md 做设计系统

用户要按一份 `DESIGN.md`（或品牌规范）做设计系统，有 preset 或者没有，都按 [design-system.md](./design-system.md) 从头做到尾：

1. `init --preset <code> --template <vite|next> --name <app> --no-monorepo -y`。没有 preset 代码时，挑最接近的 style，传 `--base base --preset <style>`。然后 `add --all -y`。
2. 动手改之前，先读 DESIGN.md 的 frontmatter、Do's and Don'ts、Known Gaps。
3. 把它的 token 对到 `tailwindCssFile` 里的 shadcn 变量上。圆角尺度、阴影、字体和 `type-*` 工具类都钉住。
4. 改组件的 `cva` variant 来重做样式。控件高度要一起改。
5. 按 [design-system-page.md](./design-system-page.md) 做设计系统页面：查过对比度的颜色角色、字体样本、钉住的状态矩阵、边界情况、该做和不该做的对照、配方。用 `scripts/showcase-coverage.mjs` 查覆盖到了没有。
6. 在浏览器里核对：类型检查能过，控制台没有报错，打开后停在页面顶部，没有横向溢出，暗色模式也看过。

## 更新组件

用户要更新上游的组件，又要留着本地改动时，用 `--dry-run` 和 `--diff` 做智能合并。**不要自己去 GitHub 拉原始文件。一律用 CLI。**

1. 跑 `npx shadcn@latest add <component> --dry-run`，看哪些文件会被碰到。
2. 对每个文件跑 `npx shadcn@latest add <component> --diff <file>`，看上游和本地差在哪。
3. 按 diff 一个文件一个文件决定：
   - 没有本地改动，就可以覆盖。
   - 有本地改动，就读本地文件，看 diff，把上游的更新补上，本地改过的地方留住。
   - 用户说全都更新就行，可以用 `--overwrite`，但先确认。
4. **用户没有明确同意，不要用 `--overwrite`。**

## 速查

```bash
# Create a new project.
npx shadcn@latest init --name my-app --preset base-nova
npx shadcn@latest init --name my-app --preset a2r6bw --template vite

# Create a design system app (then follow design-system.md).
npx shadcn@latest init --name my-ds --preset b0 --template vite --no-monorepo -y
npx shadcn@latest init --name my-ds --base base --preset maia --template vite --no-monorepo -y
npx shadcn@latest add --all -y

# Create a monorepo project.
npx shadcn@latest init --name my-app --preset base-nova --monorepo
npx shadcn@latest init --name my-app --preset base-nova --template next --monorepo

# Initialize existing project.
npx shadcn@latest init --preset base-nova
npx shadcn@latest init --defaults  # shortcut: --template=next --preset=nova (base style implied)

# Apply a preset to an existing project.
npx shadcn@latest apply a2r6bw
npx shadcn@latest apply a2r6bw --only theme
npx shadcn@latest apply a2r6bw --only font
npx shadcn@latest apply a2r6bw --only theme,font

# Inspect preset codes and project preset state.
npx shadcn@latest preset decode a2r6bw
npx shadcn@latest preset url a2r6bw
npx shadcn@latest preset open a2r6bw
npx shadcn@latest preset resolve
npx shadcn@latest preset resolve --json

# Add components.
npx shadcn@latest add button card dialog
npx shadcn@latest add @magicui/shimmer-button
npx shadcn@latest add owner/repo/item
npx shadcn@latest add --all

# Preview changes before adding/updating.
npx shadcn@latest add button --dry-run
npx shadcn@latest add button --diff button.tsx
npx shadcn@latest add @acme/form --view button.tsx
npx shadcn@latest add owner/repo/item --dry-run

# Search registries.
npx shadcn@latest search @shadcn -q "sidebar"
npx shadcn@latest search @tailark -q "stats"
npx shadcn@latest search owner/repo -q "login"
npx shadcn@latest search                          # all configured registries
npx shadcn@latest search @shadcn -q "menu" -t ui  # filter by item type

# Get component docs and example URLs.
npx shadcn@latest docs button dialog select

# View registry item details (for items not yet installed).
npx shadcn@latest view @shadcn/button
npx shadcn@latest view owner/repo/item
```

**有名字的 preset：** `nova`、`vega`、`maia`、`lyra`、`mira`、`luma`
**模板：** `next`、`vite`、`start`、`react-router`、`astro`（都支持 `--monorepo`），以及 `laravel`（不支持 monorepo）
**Preset 代码：** 带版本前缀的 base62 字符串（例如 `a2r6bw` 或 `b0`），来自 [ui.shadcn.com](https://ui.shadcn.com)。

## 更细的说明

- [rules/forms.md](./rules/forms.md)：FieldGroup、Field、InputGroup、ToggleGroup、FieldSet、校验状态
- [rules/composition.md](./rules/composition.md)：Group、浮层、Card、Tabs、Avatar、Alert、Empty、Toast、Separator、Skeleton、Badge、Button 的加载状态
- [rules/chat.md](./rules/chat.md)：MessageScroller、Message、Bubble、Attachment、Marker、Trace。流式跟随、钉住滚动位置、跳到最新、助手的活动行
- [rules/icons.md](./rules/icons.md)：data-icon、图标尺寸、图标当对象传
- [rules/styling.md](./rules/styling.md)：语义颜色、variant、className、间距、size、truncate、暗色模式、cn()、z-index
- [rules/base-vs-radix.md](./rules/base-vs-radix.md)：asChild 和 render、Select、ToggleGroup、Slider、Accordion
- [cli.md](./cli.md)：命令、参数、preset、模板
- [registry.md](./registry.md)：怎么写源注册表、`include`、条目怎么定义、依赖、GitHub 注册表的规则
- [customization.md](./customization.md)：主题、CSS 变量、扩展组件
- [design-system.md](./design-system.md)：从 DESIGN.md（有 preset 或没有）做到一个带主题的应用。选 style、把 token 对上、圆角、字体、字号阶梯、控件高度、展示页容易踩的坑、核对
- [design-system-page.md](./design-system-page.md)：设计系统页面上放什么、怎么放。基础、组件分层、钉住的状态矩阵、对比度配对、边界情况、该做和不该做、配方
