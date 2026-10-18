---
name: 原则-迁完再删旧API
description: "在引入一个新的内部 API、而旧的调用方还存在时使用。在同一轮里把调用方迁移过去并删掉旧 API，而不是保留兼容层。"
disable-model-invocation: true
---

> 翻译自 pstack 插件（编号 9717366）的 `principle-migrate-callers-then-delete-legacy-apis` skill，原作者 Lauren Tan（版权 © 2026 Lauren Tan），许可证 MIT（全文见上一级文件夹的 `LICENSE-pstack`），仅供自用。插件版本 0.15.25，原项目：https://github.com/cursor/plugins/tree/main/pstack 。
> 说明：`disable-model-invocation: true` 表示这个 skill 只能由用户主动调用，AI 不会自己调用它。原文正文就只有下面这些，照原样翻译。
> 英文名备份：s-principle-migrate-callers-then-delete-legacy-apis

# 先迁移调用方，再删掉旧 API

- 更新测试，让它们断言新的约定；删掉那些只保护重构前实现细节的测试

**什么时候适用：**
- 没有外部用户依赖向后兼容
- 项目能承受一次协调好的不兼容改动
- 新 API 是一次简化或重构工作的一部分
