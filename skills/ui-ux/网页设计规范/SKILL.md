---
name: 网页设计规范
description: 按照《网页界面规范》（Web Interface Guidelines）检查界面代码是否合规。当用户说“帮我看看界面”、“检查无障碍”、“审一下设计”、“看看用户体验”或“按最佳做法检查我的网站”时使用。
metadata:
  author: vercel
  version: "1.0.0"
  argument-hint: <file-or-pattern>
---

> 翻译自 Vercel 官方仓库 https://github.com/vercel-labs/agent-skills （skills/web-design-guidelines，commit 063bee9）的 `web-design-guidelines` skill，原作者 Vercel，许可证 MIT（仓库没有单独的 LICENSE 文件，是 README 里写的 MIT，见上一级文件夹的 `LICENSE-vercel-agent-skills`），仅供自用。
> 说明：这个 skill 每次运行时会去网上下载最新的规范原文（英文），所以检查规则本身是英文的。命令、网址、文件路径都保持原样。
> 英文名备份：s-web-design-guidelines

# 网页界面规范

检查文件是否符合《网页界面规范》。

## 怎么运作

1. 从下面的来源网址获取最新的规范
2. 读取指定的文件（或者问用户要检查哪些文件/匹配规则）
3. 对照获取到的规范里的所有规则逐条检查
4. 用简洁的 `file:line`（文件:行号）格式输出发现的问题

## 规范来源

每次检查前都重新获取最新规范：

```
https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md
```

用 WebFetch（网页抓取工具）获取最新规则。获取到的内容里包含了所有规则和输出格式说明。

## 用法

当用户提供了文件或匹配规则参数时：
1. 从上面的来源网址获取规范
2. 读取指定的文件
3. 应用获取到的规范里的所有规则
4. 按规范里规定的格式输出发现的问题

如果没有指定文件，就问用户要检查哪些文件。
