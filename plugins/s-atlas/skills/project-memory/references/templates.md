# 记录模板

`init` 建档时用。每份只写代码里看得见的内容，看不出来的标「待补」。

## README.md（索引）

```markdown
# 项目记录

| 主题 | 权威位置 |
| --- | --- |
| 架构 | [architecture.md](architecture.md) |
| 规范 | [conventions.md](conventions.md) |
| 决策 | [decisions/](decisions/) |

更新规则：改动代码后按 diff 判断是否影响这里；只写现状，不写更新日志。
```

## architecture.md

```markdown
# 架构

## 概览
一两句话：这个项目是什么，主要由哪几块组成。

## 模块
| 模块 | 位置 | 职责 | 依赖 |
| --- | --- | --- | --- |

## 入口与数据流
入口文件，一次典型请求或任务怎么流过各模块。

## 外部依赖
服务、数据库、第三方接口，各自用在哪。

## 构建与运行
安装、构建、测试、检查的实际命令。
```

## conventions.md

```markdown
# 规范

每条写「规则」和「依据」（文件路径或配置项）。

| 规则 | 依据 |
| --- | --- |
| 例：测试与源码放同一目录，命名为 `*.test.ts` | `src/api/users.test.ts` |
```

## decisions/NNNN-标题.md

```markdown
# NNNN 标题

状态：有效 / 已被 NNNN 取代

## 背景
当时遇到什么问题，有什么约束。

## 决定
选了什么。

## 取舍
放弃了哪些方案，为什么；这个决定带来的代价。
```

## 指针（CLAUDE.md、AGENTS.md）

只加一行：

```markdown
项目架构、规范和决策记录见 [docs/project/](docs/project/README.md)。
```
