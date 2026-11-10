# wukong 名称统一

用户已确认：插件从 `s-wukong` 改为 `wukong`；仅将六个现有 `s-` 技能改成 `wukong-`，其他技能名保持原样。

## 实施与验收

1. 将插件目录迁至 `plugins/wukong`，同步三个宿主的插件与市场清单、脚本路径、文档链接及架构资源名。市场和仓库仍为 `s-skills`。
2. 将 agent、init、mode、proposal、review、router 六个技能的目录、frontmatter、引用改为 `wukong-*`；同步同名 agent 文件和声明。不增加旧技能别名。
3. 新生成的规则标记和模型目标文件使用 `wukong`。继续识别既有 `s-wukong`、`s-atlas` 外部配置，混合规则标记仍拒绝写入。只改仓库实现，不写用户全局配置。
4. 更新版本与内容哈希，执行 `.venv/Scripts/python.exe -B scripts/check_marketplace.py` 和 `.venv/Scripts/python.exe -B -m unittest discover -s scripts -p "test_*.py"`，预期通过。
5. 审阅相对任务前工作区快照的全部差异，保留原有修改。派一名只读独立评审。未获授权不提交、推送或发布。

这是目录与公开名称迁移；以资源发现、声明一致性、链接校验和旧配置迁移测试验证，不新增重复实现断言。
