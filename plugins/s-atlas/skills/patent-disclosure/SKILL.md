---
name: patent-disclosure
description: "「写专利交底书」「专利挖掘」「查新」「保护点」。做中国发明专利挖掘、查新、写技术交底书，或修改已有交底书，按国知局质量要求输出 Markdown 和 Word。Use when mining Chinese invention patent points, searching prior art, or writing and revising a technical disclosure."
---
> 来源：开源项目 [cn-patent](https://github.com/Zaoqu-Liu/cn-patent)（MIT 许可）。
> 本 skill 的辅助文件（`prompts/`、`references/`、`tools/`、`requirements*.txt`）放在本 skill 所在的文件夹里。执行前先设置：`SKILL_DIR="<本 skill 文件夹的绝对路径>"`，下文所有 `${SKILL_DIR}` 都指它。

# 专利挖掘与交底书生成

本技能覆盖 **专利点挖掘** → **查新与差异化** → **交底书生成** → **自检完善** 全流程；分步指令在 `prompts/`，每步执行前先读对应文件。

## 环境与约定
- **语言**：默认用中文；专利与法律术语采用行业常用表述。
- **图示定稿（Step 7）**：3.2 系统框图和 3.4 流程图用 fenced mermaid，渲染方式见 `tools/README.md`。
- **质量门禁**：生成候选专利点、查新分析、第三至五章和最终自检时，按需读 `references/cn-patent-quality.md`。

## 触发条件
- 提到：专利挖掘、专利点、技术交底书、查新、现有技术对比等。
- **迭代模式**：用户明显是在已有交底书或上一轮输出上继续改（改章节、补实施例、补材料、修正参数），就读 `prompts/iteration_context.md`，再读 `prompts/merger.md`（补新材料）或 `prompts/correction_handler.md`（纠错），按文件开头的执行门禁做完，另存为 `{案件名}_{YYYYMMDDHHmmss}.md` 和同名 `.docx`，不覆盖旧稿。不要回到 Step 3–4 重新挖掘，除非用户要求。

## 工具与数据来源
| 任务 | 做法 |
|---|---|
| 加载分步指令 | 读 `${SKILL_DIR}/prompts/*.md` |
| Word 转 Markdown | `python3 ${SKILL_DIR}/tools/docx_to_md.py --input {path}.docx --output {dir}/{name}.md`（先 `pip install -r ${SKILL_DIR}/requirements.txt`） |
| PPT 转 Markdown | `python3 ${SKILL_DIR}/tools/pptx_to_md.py --input {path}.pptx --output {dir}/{name}.md`；旧版 .ppt 先另存为 .pptx |
| 联网查新（Step 5） | 先读 `prompts/prior_art_search.md`。优先运行 `tools/cnipa_epub_search.py` 查国知局公布公告：先归纳 2～8 个语义块，每次只传一个，自己按 `pub_number` 合并结果（需 `pip install -r tools/requirements-cnipa.txt` 和 `python -m playwright install chromium`）。出错或没结果再用网页搜索 |
| 定稿交付（.md + .docx 都要） | 运行 `tools/mermaid_render.py --strict` 把 mermaid 转 PNG 并生成 .docx；失败要修好再交付 |
| 保存路径 | 用户指定路径，否则 `./outputs/{案件标识}/`；文件名一律 `{案件名}_{YYYYMMDDHHmmss}` |
| 迭代留档 | 每轮合并或纠正后，在案件目录追加 `交底书修订对话记录.md`（可用 `tools/iteration_dialog_log.py`） |

## 主流程
1. 读 `prompts/intake.md`，执行 Step 1（确认边界与输入）。
2. 读 `prompts/project_scan.md`，执行 Step 2（扫描材料，Office 文件先转换）。
3. 读 `prompts/patent_points_analyzer.md`，执行 Step 3–4（候选专利点、融合与选定）。
4. 读 `prompts/prior_art_search.md`，执行 Step 5（查新）。
5. 读 `references/cn-patent-quality.md`，把“技术问题—技术方案—技术效果”闭环、充分公开、支持性、创造性三步法、软件/AI 客体要求纳入后续写作。
6. 读 `prompts/disclosure_preview.md`，执行 Step 6（全文前的摘要预览，用户可跳过）。
7. 读 `prompts/disclosure_builder.md` 和 `prompts/template_reference.md`，执行 Step 7（写交底书）；交付时按 `disclosure_builder.md` §7.6 在对话里给出“权利要求偏向点”建议（不写进正文）。
8. 读 `prompts/disclosure_self_check.md`，内部执行 Step 8 自检，修订后交付。

**禁止**：交底书正文里出现“自检清单”章节；自检只在内部做。

## 交付前检查
- 每步都读了对应 prompt；Office 文件已转换后再读。
- 修改已有交底书时走了迭代流程，另存新文件，并输出了合并摘要或纠正摘要。
- 查新结果已写进 1.1 和区别论述。
- 已按质量门禁检查闭环、充分公开、说明书支持、区别特征与技术效果的对应关系。
- 图示已渲染，.md 与 .docx 都已交付，文件名带时间戳，正文没有多余脚注。
