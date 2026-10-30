# WorkBuddy 宿主参考

仅在 WorkBuddy 需要安装、配置、执行工具或子代理时阅读。这里采用官方明确说明的项目与用户级兼容目录，不把其他宿主的工具参数当作 WorkBuddy 能力，也不声称已经上架 WorkBuddy 插件市场。

## 安装与作用域

- 推荐本仓库 Windows 项目安装：`powershell -NoProfile -File scripts/install_local_skills.ps1 -HostName workbuddy`，链接到项目 `.codebuddy/skills/<技能名>/`，共享说明放 `.codebuddy/HOSTS.md`。保留完整源码目录，不能移动或删除链接目标。
- 每个技能保留原始 frontmatter、正文和资源。脚本不修改用户全局规则；受管共享说明只有哈希仍匹配安装记录时才更新；遇到已有不同目标或未受管的不同内容时停止，先核对归属，不覆盖用户文件。
- 相对链接涉及插件根目录资料时，先解析技能链接的真实目标，使用完整插件的物理根路径。Python 工具会通过脚本真实路径定位自身资源。不要把项目 `.codebuddy/` 当成插件根目录去猜 `plugin.json` 的位置。
- 官方项目目录包括 `.codebuddy/skills`、`.codebuddy/agents`、`.codebuddy/rules`，并说明兼容用户级 `~/.codebuddy`。用户级技能兼容目录为 `~/.codebuddy/skills`；本仓库当前安装脚本只管理项目链接，不自动批量安装或覆盖用户全局技能。
- 官方技能界面也提供“添加技能 → 上传技能”；本库依赖共享资源与技能间引用，不能把任意单个目录 ZIP 当成已验证的独立分发包。不要声称对话安装可以直接安装未上架的本仓库插件。
- 客户端本地技能与云端个人技能库不同。本机目录链接、Python 脚本及 `~/.s-atlas/lessons` 只适用于有相应文件访问权的本机任务，不自动同步云端或其他机器。

## 全局提示词与经验

显式执行 setup-s-instructions 时选择 `--host workbuddy`，使用官方兼容的用户级 `~/.codebuddy/CODEBUDDY.md`。先只读检查，明确初始化或更新授权后才加 `--apply`；保留用户其他内容、首份备份和受管块边界，重复执行不重复添加。项目规则不是全局规则，不用项目文件冒充全局初始化。

日常按[全局自检](../../setup-s-instructions/references/daily-check.md)只读提醒。若当前 WorkBuddy 版本未加载兼容目录，不能因为文件写入成功就声称已在宿主生效；新会话回读核验，失败时报告文件层完成、宿主加载未验证，不写内部数据库或猜测其他全局路径。

模型角色正文可在用户明确配置时放入 `~/.codebuddy/rules/s-models.md` 的 s 标记段，使用普通 Markdown，保留其他内容。模型名仅来自当前会话实际支持的检测结果；不能为子代理独立选择时用 `inherit-parent`。不用 Cursor 模型名或其 `.mdc` frontmatter。

learn 继续使用独立的本机经验库及逐条确认流程。WorkBuddy 自带“记忆与进化”是另一套机制，本库不修改其开关或存储；不能声称本库的确认流程控制了宿主原生的记忆提取。

## 通用动作与能力回退

| 动作 | WorkBuddy 中的做法 |
|---|---|
| 读写文件、运行脚本 | 用当前会话实际提供的文件与终端工具；脚本需要已有 Python 3 / Node 运行时，不自动安装依赖 |
| 派实现者或只读评审者 | 仅使用当前会话暴露的代理工具和类型；只读范围写清，不假定存在 Cursor 的 `readonly` 参数 |
| 没有子代理工具 | 主任务顺序执行，标明缺少独立评审或并行，不把自身检查称为独立评审 |
| 模型与推理预算 | 检测可用项；无法单独指定则继承父会话，不虚构角色注册或模型参数 |
| 提问与确认 | 用宿主实际提供的提问工具；没有时在对话中提问，沉默不当作批准 |
| 浏览器或桌面操作 | 用已暴露且已授权的浏览器、桌面或 MCP 能力，不假定安装某客户端就具备所有工具 |
| 定时任务 | 只有任务实际创建且可回读才算持久调度；普通会话等待不算 |
| Git 与工作区 | 核实本机路径、分支和已有修改；提交、推送、清理仍按用户授权，不因新增宿主而扩权 |
| 显式技能 | 读取 `disable-model-invocation` 与全局调用规则；宿主不识别该元数据时仍遵守正文和用户授权，不自动启用显式流程 |
| 专属角色 | 使用已实际注册的角色；未注册时将对应技能阅读要求和职责写进合法通用代理的任务，不虚构 s-agent 类型 |

## 官方依据

- [项目配置与兼容目录](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Project)
- [用户级目录与加载顺序](https://www.workbuddy.cn/docs/cli/codebuddy-dir)
- [技能安装与上传入口](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market)
- [技能结构与脚本资源](https://open.workbuddy.cn/docs/skill)
- [原生记忆机制](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Memory)

验证状态分开记录：目录与脚本测试、会话发现、实际读取、真实任务行为。本适配不把静态检查或其他宿主的测试当作 WorkBuddy 客户端验收。
