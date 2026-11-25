# s 模型配置
# 六角色必须完整；inherit-parent 或 auto 可继承父会话。
# 逗号分隔的列表，每一项派一个子代理。
# 预算: 省（medium）
检索与探索: t3:lookup
方案设计: t3:design
开发实现: t3:implementation
专项攻坚: t3:hard
验证测试: t3:test
独立评审: t3:review
# s 模型配置结束

## 项目模型备用策略

本项目采用最终混合三档的省档方案。派发前读取 [首选与顺序备用](docs/project/s-model-fallbacks.md)，按其中的完整模型、参数与切换条件执行；次选不是额外并行代理。省档独立评审只有一个名额。项目首选以 wukong.t3.json 为准，不使用 Cursor 或 GLM。
