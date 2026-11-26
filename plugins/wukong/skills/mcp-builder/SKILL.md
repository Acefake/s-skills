---
name: mcp-builder
description: "「写个 MCP Server」「把这个 API 接成 MCP 工具」。设计工具契约、实现服务端并用 MCP 客户端联调。Use when creating an MCP server or exposing a service through MCP tools."
disable-model-invocation: true
---

本会话首次使用本库技能时，按[全局提示词自检](../wukong-init/references/daily-check.md)只读检查一次。

# 构建 MCP 服务

改编自 [Anthropic 的 mcp-builder](https://github.com/anthropics/skills/tree/main/skills/mcp-builder)，本文已中文化并按 wukong 的工作流调整。版权和许可见 [LICENSE.txt](LICENSE.txt)。

## 确定接口

1. 列出目标助手需要完成的任务，核对上游 API 的认证、权限、分页、限流和响应结构。从常用操作开始。只有多步操作经常一起执行并且能减少调用或出错时，才加组合工具。
2. 检查项目和目标客户端支持的 SDK 版本与传输。保留现有 SDK 主版本。进程由本机客户端启动时用 stdio，并把日志写到 stderr。远程服务用目标客户端支持的 Streamable HTTP，按部署方式配置认证。
3. 给工具起能看出动作和对象的名字，例如 `issues_list`。输入 schema 写明必填项、格式、可选过滤条件和分页参数。客户端支持时提供输出 schema 和结构化结果，分页返回可继续使用的游标。工具注解须与真实副作用一致，权限由服务端校验。

按需核对 [MCP 协议](https://modelcontextprotocol.io/specification/)、[TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk) 或 [Python SDK](https://github.com/modelcontextprotocol/python-sdk)。示例的导入路径和注册 API 应与项目使用的版本匹配。

## 实现和联调

1. 在工具边界验证参数和调用者权限，复用项目已有的 API 客户端与错误处理。对限流、超时、上游错误和权限不足返回足够定位问题的信息，去掉凭证和敏感响应内容。写操作只有在具备幂等保障时才自动重试。
2. 启动服务，用 [MCP Inspector](https://github.com/modelcontextprotocol/inspector) 或目标客户端验证连接、工具发现和实际调用。覆盖正常请求、参数错误及权限不足。有分页时验证下一页，有写操作时在测试账户或隔离环境核对副作用。
3. 用固定测试数据设计几条问题，覆盖工具选择、过滤和多步调用。预先记录可核对的答案，再检查助手能否靠工具完成任务。交付时给出启动方式、传输方式、授权配置项和实际联调结果。
