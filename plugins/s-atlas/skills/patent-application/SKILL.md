---
name: patent-application
description: "「写专利申请」「权利要求书」「说明书」「专利附图」。起草中国发明专利申请文件（摘要、权利要求书、说明书和附图）并输出 Word，或套用模板版式、修页眉页码、重画专利配图。Use when drafting a Chinese invention patent application, matching a template layout, fixing headers and page numbers, or redrawing patent figures."
---

本会话首次使用本库技能时，按[全局提示词自检](../setup-s-instructions/references/daily-check.md)只读检查一次。
## 运行环境适配

涉及宿主工具、模型配置或子代理时，按需阅读[宿主适配](../../HOSTS.md)。

> 来源：开源项目 [cnipa-patent-writer](https://github.com/fnjialun/cnipa-patent-writer)。
> 本 skill 的辅助文件（`references/`、`scripts/`）放在本 skill 所在的文件夹里，下文路径都相对于这个文件夹。

# 中国发明专利撰写（套用模板格式 / 无模板按国知局标准）

帮用户写一篇**新的**发明专利申请文件（`.docx`）。模板只提供版式和行文风格，**技术内容一律不抄**。

## 何时用 / 输入
- 有模板：用户给一份模板专利 `.docx` + 要写成专利的技术方案 → 用 `scripts/build_patent.py`，版式完全继承模板。
- 无模板：只给技术方案 → 用 `scripts/build_patent_cnipa.py`，按国知局标准版式生成。
- 产物：一篇排版规范、带配图的 `.docx`。

## 依赖
- 必装：`pip install python-docx matplotlib Pillow`。
- 可选：用 graphviz 画图时还要装系统的 `dot`（`sudo apt-get install -y graphviz`）。
- 中文字体：画图必须有中文字体（如 Noto Sans CJK），否则会出现方框乱码。
- 校验工具（强烈建议）：`libreoffice-writer`、`poppler-utils`、`fonts-noto-cjk`。

## 核心原则
1. **只借格式，绝不抄技术内容**：模板里的技术方案、架构、模块名、步骤、配图数量和种类都不能搬进新专利；所有文字和配图都根据用户自己的材料生成。
2. **结构对不等于看起来对**：完稿必须渲染成页面逐页看（见第 7 步）。
3. **权利要求写宽**：权利要求用上位概念，具体数值、型号、接口只在实施例里以“例如/优选”出现。
4. **术语锁定**：权利要求、发明内容、实施例三处用词必须一致；先定术语表再一口气写全文。
5. **最硬的创新点写进独立权利要求 1**。

## 工作流
1. **学格式**：读 `references/docx-format.md` 和 `references/cnipa-format-spec.md`。有模板就跑 `python scripts/inspect_template.py 模板.docx` 扫出全部版式（尤其确认四节四页眉：说明书摘要 / 权利要求书 / 说明书 / 说明书附图，以及页码怎么处理）；无模板直接用标准参数。
2. **动笔前与用户确认**：发明名称；独立权利要求 1 的落点（方法还是系统）；实施例写真实参数还是脱敏；是否生成配图。拿不准就问，别猜。
3. **来自真实系统时先取事实**：把要写进实施例的真实参数、接口、模型名连同出处扫出来。
4. **锁术语、写正文**：读 `references/writing-style.md`，定术语表，一口气写：摘要 → 权利要求书（独立 1 + 从属 + 系统）→ 说明书（技术领域 / 背景技术 / 发明内容 / 有益效果 / 附图说明 / 具体实施方式）。写完自查：从属是否引用父项、每个要素是否有实施例支撑、术语是否一致。
5. **生成配图**：读 `references/figures.md`（含六条硬规则）。配图数量和类型按内容定。流程图、模块图优先用 `scripts/make_figures.py` 的 `vflow` / `vmodules`；复杂图可用 `scripts/gen_figures_graphviz.py`。**每画完一张都要打开看**，核对纯黑、文字不溢出、字够大、不压线、图文匹配。
6. **装配 docx**：有模板用 `scripts/build_patent.py`（`PatentBuilder`），无模板用 `scripts/build_patent_cnipa.py`（区块 JSON）。用法见脚本顶部说明和 `references/docx-format.md`。
7. **可视化校验（不可跳过）**：用 `scripts/render_check.py` 渲染成逐页 PNG，逐页检查：四个页眉是否各就各位；权利要求书和说明书页码是否各自从 1 开始；发明名称有无方框乱码；正文宋体、两端对齐、首行缩进 2 字；配图清晰、不越界、图号正确；分页没有标题孤行。有问题就改了重渲染。
8. **完成**：把最终 .docx 交给用户，请其在 Word/WPS 里通览一遍。

## 易踩坑
- 中文方框：matplotlib 没注册中文字体，或用了 monospace。
- 发明名称方框：模板内嵌了字体子集；`build_patent.py` 的 `save()` 会自动剥离，绕过它存盘要自己处理。
- 图越界：嵌入宽度不要超过版心宽。
- 全篇同一个页眉：没按四节分别挂页眉。
- 文件臃肿：保存前清掉模板遗留、未被引用的图片。
- 提交前按 `references/writing-style.md` 第五节的反面清单逐条排查。
