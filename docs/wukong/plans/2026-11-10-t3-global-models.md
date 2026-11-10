# T3 全局模型配置

目标：将已确认的全局默认、项目覆盖方案落实到源码，并按用户补充要求匹配各宿主。用户级通过 `--host` 明确底层宿主：Codex 使用 CODEX_HOME 的 AGENTS.md/非空 override；Claude 使用 CLAUDE_CONFIG_DIR/rules/s-models.md；Cursor 使用 ~/.cursor/rules/s-models.mdc 的首次 frontmatter；WorkBuddy 使用 ~/.codebuddy/rules/s-models.md；DSH 使用 DSH_HOME/AGENTS.md；Hermes 使用选中 HERMES_HOME/SOUL.md。目标 JSON 位于各宿主根目录，不改原生模型参数、认证或 YAML。`--global-dir` 仅覆盖已选宿主根目录。

优先级：项目存在模型段时整段覆盖全局；无模型段时使用全局。六角色保持完整，不按别名合并两个作用域。损坏的项目段、缺失目标、未完成事务均报错，不悄悄使用全局。旧文件名继续兼容读取。

评审修正：项目目录必须已经存在；Codex 项目也遵从非空 override 优先。Cursor 空白规则补 frontmatter。孤立目标文件报错，不悄悄继承全局；规则符号链接读取/写入统一拒绝并说明，保持事务白名单边界。

实现：在 `plugins/wukong/skills/setup-s-models/scripts/t3_targets.py` 增加 `--scope project|user`、`--host` 和 `--global-dir`；`t3_hosts.py` 集中解析宿主规则路径，写入和恢复共用白名单。check/resolve 返回所选 scope、rulesPath、targetsPath；configure/recover 对所选目录复用双文件事务。首次全局预览不创建目录，apply 验证成功后才建目录。未指定宿主且需要全局配置时报错，不推断目标 provider。

验证：扩展 `scripts/test_t3_targets.py`，覆盖两个项目继承、项目覆盖及别名隔离、错误不降级、首次预览、幂等写入和用户级恢复。运行 `python -m unittest discover -s scripts -p test_t3_targets.py`；跨模块交付运行完整 scripts 测试与 marketplace 检查。

文档：同步 setup-s-models、wukong-init、T3 编排参考、HOSTS 和混合预算说明，明确全局备用文档位置及机器相关 provider ID 的能力核对。

交付：自审完整差异和调用方，按项目省档派一名只读独立评审；不提交、不发布、不修改用户实际模型配置。
