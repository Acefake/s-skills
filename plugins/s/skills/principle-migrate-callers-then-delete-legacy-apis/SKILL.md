---
name: principle-migrate-callers-then-delete-legacy-apis
description: "Use when a new internal API is introduced while old callers still exist. 中文触发：在引入一个新的内部 API、而旧的调用方还存在时使用。在同一轮里把调用方迁移过去并删掉旧 API，而不是保留兼容层。"
disable-model-invocation: false
---
## 运行环境适配

在 Codex 或 T3 Code 中，执行前先阅读[宿主适配规则](../../HOSTS.md)；其中的模型、委派、浏览器和定时任务规则优先于下文的 Cursor 专用示例。


# 先迁移调用方，再删掉旧 API

- 更新测试，让它们断言新的约定；删掉那些只保护重构前实现细节的测试

**什么时候适用：**
- 没有外部用户依赖向后兼容
- 项目能承受一次协调好的不兼容改动
- 新 API 是一次简化或重构工作的一部分
