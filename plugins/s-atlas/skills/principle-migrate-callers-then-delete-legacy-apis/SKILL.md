---
name: principle-migrate-callers-then-delete-legacy-apis
description: "「迁完调用方再删旧接口」「别留兼容层」。引入新的内部 API 时，同一轮迁完调用方并删掉旧的。Use when a new internal API is introduced while old callers still exist."
disable-model-invocation: false
---
# 先迁移调用方，再删掉旧 API

- 更新测试，让它们断言新的约定；删掉那些只保护重构前实现细节的测试

**什么时候适用：**
- 没有外部用户依赖向后兼容
- 项目能承受一次协调好的不兼容改动
- 新 API 是一次简化或重构工作的一部分
