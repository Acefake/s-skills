---
name: web-design-guidelines
description: "按照《网页界面规范》（Web Interface Guidelines）检查界面代码是否合规。当用户说“帮我看看界面”、“检查无障碍”、“审一下设计”、“看看用户体验”或“按最佳做法检查我的网站”时使用。Use when checking interface code against web interface guidelines."
metadata:
  author: vercel
  version: "1.0.0"
  argument-hint: <file-or-pattern>
---
## 运行环境适配

在 Codex 或 T3 Code 中，执行前先阅读[宿主适配规则](../../../plugins/s/HOSTS.md)；其中的模型、委派、浏览器和定时任务规则优先于下文的 Cursor 专用示例。


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

用当前软件里能打开上面这个网址的方式获取最新规则。有的软件里这个工具叫 WebFetch。获取到的内容里包含了所有规则和输出格式说明。

## 用法

当用户提供了文件或匹配规则参数时：
1. 从上面的来源网址获取规范
2. 读取指定的文件
3. 应用获取到的规范里的所有规则
4. 按规范里规定的格式输出发现的问题

如果没有指定文件，就问用户要检查哪些文件。
