# 经确认的经验学习实现计划

设计：../specs/2026-10-29-confirmed-learning-design.md。用户已授权实现；提交、推送、修改真实经验及重新初始化宿主全局规则不包含在本轮实现授权内。

1. 在 scripts/test_lessons.py 增加隔离目录行为测试；先运行并确认缺少模块而失败。
2. 新增 plugins/s-atlas/skills/learn/scripts/lessons.py，提供 save(record, home, project, confirmed) 和 search(query, home, project, limit=3)。save 返回 changed、id、path，search 返回相关的已确认记录。CLI search --query --project 与 save --record --confirmed；--home 用于隔离测试。保存前验证作用域和替代 ID，先写同目录临时文件再原子链接为不可覆盖目标；失败清理临时文件。
3. 新增 learn/SKILL.md 和 agents/openai.yaml。用技能步骤管理触发、去重、确认、来源、冲突与跨宿主边界；脚本只管理确定性的读写。保持 reflect 显式策略，增加边界说明。
4. 在插件 AGENTS.md 和 s-router 共用规则接入回读与建议条件。修改全局模板前保存现有完整正文为 setup-s-instructions/references 的兼容快照。现有技能不批量添加学习正文。
5. 更新 README、宿主参考、技能计数与市场描述，新增技能使总数为 79（自动 58、显式 21）；不改变已有技能的 frontmatter 和 policy。补丁版本递增并校验内容锁。
6. 执行 python -m unittest discover -s scripts -p test_*.py、scripts/check_marketplace.py 和 git diff --check。主任务自审完整差异及调用方，再派一个只读评审者；修复确认问题后只重跑受影响检查。

完成标准：候选未确认时无磁盘写入；确认后的经验可在新进程回读；重复确认不重复添加；项目 A 的记录不会被项目 B 读到；替代记录不会与旧记录同时生效；没有经验时不干扰原任务。不声称实现了后台学习或三端客户端已验收。
