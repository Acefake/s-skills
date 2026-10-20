本技能译自 Jesse Vincent 的 Superpowers（MIT）。许可证见上一级文件夹的 `LICENSE-superpowers`。

# 技能编写最佳实践

> 了解如何编写有效的技能，让代理能够发现并成功使用。

好的技能简洁、结构清楚，并且经过真实使用的检验。本指南给出实际的编写决策，帮助你写出代理能够发现并有效使用的技能。

关于技能如何工作的概念背景，见[技能概述](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)。

## 核心原则

### 简洁是关键

[上下文窗口](https://platform.claude.com/docs/en/build-with-claude/context-windows)是公共资源。你的技能与代理需要知道的其他一切共享上下文窗口，包括：

* 系统提示
* 对话历史
* 其他技能的元数据
* 你的实际请求

技能里并非每个 token 都会立刻产生代价。启动时，只会预加载所有技能的元数据（`name` 和 `description`）。代理只在技能变得相关时才阅读 SKILL.md，并且只在需要时才阅读额外文件。尽管如此，SKILL.md 仍然要简洁：一旦代理加载了它，每个 token 都在和对话历史及其他上下文竞争。

**默认假设**：代理已经非常聪明

只添加代理还没有的上下文。质疑每一条信息：

* 「代理真的需要这段解释吗？」
* 「我能假定代理已经知道这个吗？」
* 「这一段对得起它的 token 成本吗？」

**好例子：简洁**（大约 50 个 token）：

````markdown  theme={null}
## Extract PDF text

Use pdfplumber for text extraction:

```python
import pdfplumber

with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```
````

**坏例子：过于冗长**（大约 150 个 token）：

```markdown  theme={null}
## Extract PDF text

PDF (Portable Document Format) files are a common file format that contains
text, images, and other content. To extract text from a PDF, you'll need to
use a library. There are many libraries available for PDF processing, but we
recommend pdfplumber because it's easy to use and handles most cases well.
First, you'll need to install it using pip. Then you can use the code below...
```

简洁版本假定代理知道 PDF 是什么、库是如何工作的。

### 设置恰当的自由度

把具体程度匹配到任务的脆弱程度和变化程度。

**高自由度**（基于文本的指令）：

在这些时候使用：

* 多种做法都成立
* 决策取决于上下文
* 启发式引导做法

示例：

```markdown  theme={null}
## Code review process

1. Analyze the code structure and organization
2. Check for potential bugs or edge cases
3. Suggest improvements for readability and maintainability
4. Verify adherence to project conventions
```

**中等自由度**（带参数的伪代码或脚本）：

在这些时候使用：

* 存在一种首选模式
* 可以有一些变化
* 配置会影响行为

示例：

````markdown  theme={null}
## Generate report

Use this template and customize as needed:

```python
def generate_report(data, format="markdown", include_charts=True):
    # Process data
    # Generate output in specified format
    # Optionally include visualizations
```
````

**低自由度**（具体脚本，参数很少或没有）：

在这些时候使用：

* 操作脆弱、容易出错
* 一致性至关重要
* 必须遵循特定顺序

示例：

````markdown  theme={null}
## Database migration

Run exactly this script:

```bash
python scripts/migrate.py --verify --backup
```

Do not modify the command or add additional flags.
````

**类比**：把代理想成一个在探路的机器人：

* **两边是悬崖的窄桥**：向前只有一条安全的路。提供具体的护栏和精确指令（低自由度）。例如：必须按确切顺序运行的数据库迁移。
* **没有危险的开阔地**：很多路都能成功。给出大致方向，信任代理找到最好的路线（高自由度）。例如：由上下文决定最佳做法的代码审查。

### 用你计划使用的所有模型来测试

技能是加在模型上的，所以效果取决于底层模型。用你计划配合使用的所有模型来测试你的技能。

**按模型考虑的测试点**：

* **Claude Haiku**（快、省）：技能提供的指导够不够？
* **Claude Sonnet**（均衡）：技能清楚且高效吗？
* **Claude Opus**（推理能力强）：技能有没有解释过度？

对 Opus 完美适用的内容，对 Haiku 可能需要更多细节。如果你计划跨多个模型使用技能，目标是写出对它们都适用的指令。

## 技能结构

<Note>
  **YAML Frontmatter**：SKILL.md 的 frontmatter 需要两个字段：

  * `name` - 技能的人类可读名称（最多 64 个字符）
  * `description` - 一行描述，说明技能做什么、何时使用（最多 1024 个字符）

  完整的技能结构细节见[技能概述](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#skill-structure)。
</Note>

### 命名约定

使用一致的命名模式，让技能更容易引用和讨论。我们建议技能名使用**动名词形式**（动词 + -ing），因为这清楚地描述了技能提供的活动或能力。

**好的命名示例（动名词形式）**：

* "Processing PDFs"
* "Analyzing spreadsheets"
* "Managing databases"
* "Testing code"
* "Writing documentation"

**可以接受的替代**：

* 名词短语："PDF Processing"、"Spreadsheet Analysis"
* 面向动作："Process PDFs"、"Analyze Spreadsheets"

**避免**：

* 含糊的名字："Helper"、"Utils"、"Tools"
* 过于笼统："Documents"、"Data"、"Files"
* 你的技能集合内部模式不一致

一致的命名让这些事更容易：

* 在文档和对话中引用技能
* 一眼看懂技能做什么
* 组织和搜索多个技能
* 维持一个专业、连贯的技能库

### 编写有效的 description

`description` 字段让技能能被发现，应当同时包含技能做什么、以及何时使用。

<Warning>
  **始终用第三人称写**。description 会被注入系统提示，人称不一致会导致发现问题。

  * **好：** "Processes Excel files and generates reports"
  * **避免：** "I can help you process Excel files"
  * **避免：** "You can use this to process Excel files"
</Warning>

**要具体，并包含关键术语**。既要写技能做什么，也要写何时使用的具体触发和上下文。

每个技能恰好有一个 description 字段。description 对技能选择至关重要：代理用它从可能 100 个以上的可用技能里选出正确的那个。你的 description 必须提供足够细节，让代理知道何时选择这个技能，而 SKILL.md 的其余部分提供实现细节。

有效示例：

**PDF 处理技能：**

```yaml  theme={null}
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
```

**Excel 分析技能：**

```yaml  theme={null}
description: Analyze Excel spreadsheets, create pivot tables, generate charts. Use when analyzing Excel files, spreadsheets, tabular data, or .xlsx files.
```

**Git 提交说明助手技能：**

```yaml  theme={null}
description: Generate descriptive commit messages by analyzing git diffs. Use when the user asks for help writing commit messages or reviewing staged changes.
```

避免像这样含糊的 description：

```yaml  theme={null}
description: Helps with documents
```

```yaml  theme={null}
description: Processes data
```

```yaml  theme={null}
description: Does stuff with files
```

### 渐进式披露模式

SKILL.md 是一份概述，在需要时把代理指向详细材料，就像入门指南里的目录。渐进式披露如何工作的解释，见概述中的[技能如何工作](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#how-skills-work)。

**实用指导：**

* 为了最佳表现，把 SKILL.md 正文保持在 500 行以内
* 接近这个上限时，把内容拆到单独文件
* 用下面的模式有效地组织指令、代码和资源

#### 视觉概览：从简单到复杂

一个基本技能一开始只有一个 SKILL.md 文件，里面是元数据和指令：

<img src="https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-simple-file.png?fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=87782ff239b297d9a9e8e1b72ed72db9" alt="Simple SKILL.md file showing YAML frontmatter and markdown body" data-og-width="2048" width="2048" data-og-height="1153" height="1153" data-path="images/agent-skills-simple-file.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-simple-file.png?w=280&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=c61cc33b6f5855809907f7fda94cd80e 280w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-simple-file.png?w=560&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=90d2c0c1c76b36e8d485f49e0810dbfd 560w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-simple-file.png?w=840&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=ad17d231ac7b0bea7e5b4d58fb4aeabb 840w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-simple-file.png?w=1100&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=f5d0a7a3c668435bb0aee9a3a8f8c329 1100w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-simple-file.png?w=1650&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=0e927c1af9de5799cfe557d12249f6e6 1650w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-simple-file.png?w=2500&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=46bbb1a51dd4c8202a470ac8c80a893d 2500w" />

随着技能增长，你可以捆绑额外内容，代理只在需要时才加载：

<img src="https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-bundling-content.png?fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=a5e0aa41e3d53985a7e3e43668a33ea3" alt="Bundling additional reference files like reference.md and forms.md." data-og-width="2048" width="2048" data-og-height="1327" height="1327" data-path="images/agent-skills-bundling-content.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-bundling-content.png?w=280&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=f8a0e73783e99b4a643d79eac86b70a2 280w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-bundling-content.png?w=560&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=dc510a2a9d3f14359416b706f067904a 560w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-bundling-content.png?w=840&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=82cd6286c966303f7dd914c28170e385 840w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-bundling-content.png?w=1100&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=56f3be36c77e4fe4b523df209a6824c6 1100w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-bundling-content.png?w=1650&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=d22b5161b2075656417d56f41a74f3dd 1650w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-bundling-content.png?w=2500&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=3dd4bdd6850ffcc96c6c45fcb0acd6eb 2500w" />

完整的技能目录结构可能是这样：

```
pdf/
├── SKILL.md              # Main instructions (loaded when triggered)
├── FORMS.md              # Form-filling guide (loaded as needed)
├── reference.md          # API reference (loaded as needed)
├── examples.md           # Usage examples (loaded as needed)
└── scripts/
    ├── analyze_form.py   # Utility script (executed, not loaded)
    ├── fill_form.py      # Form filling script
    └── validate.py       # Validation script
```

#### 模式 1：带参考的高层指南


````markdown  theme={null}
---
name: PDF Processing
description: Extracts text and tables from PDF files, fills forms, and merges documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
---

# PDF Processing

## Quick start

Extract text with pdfplumber:
```python
import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```

## Advanced features

**Form filling**: See [FORMS.md](FORMS.md) for complete guide
**API reference**: See [REFERENCE.md](REFERENCE.md) for all methods
**Examples**: See [EXAMPLES.md](EXAMPLES.md) for common patterns
````

代理只在需要时才加载 FORMS.md、REFERENCE.md 或 EXAMPLES.md。

#### 模式 2：按领域组织

对于有多个领域的技能，按领域组织内容，避免加载无关上下文。当用户询问销售指标时，代理只需要读与销售相关的 schema，而不需要财务或营销数据。这样 token 用量保持很低，上下文保持聚焦。

```
bigquery-skill/
├── SKILL.md (overview and navigation)
└── reference/
    ├── finance.md (revenue, billing metrics)
    ├── sales.md (opportunities, pipeline)
    ├── product.md (API usage, features)
    └── marketing.md (campaigns, attribution)
```

````markdown SKILL.md theme={null}
# BigQuery Data Analysis

## Available datasets

**Finance**: Revenue, ARR, billing → See [reference/finance.md](reference/finance.md)
**Sales**: Opportunities, pipeline, accounts → See [reference/sales.md](reference/sales.md)
**Product**: API usage, features, adoption → See [reference/product.md](reference/product.md)
**Marketing**: Campaigns, attribution, email → See [reference/marketing.md](reference/marketing.md)

## Quick search

Find specific metrics using grep:

```bash
grep -i "revenue" reference/finance.md
grep -i "pipeline" reference/sales.md
grep -i "api usage" reference/product.md
```
````

#### 模式 3：有条件的细节

展示基本内容，把进阶内容链接出去：

```markdown  theme={null}
# DOCX Processing

## Creating documents

Use docx-js for new documents. See [DOCX-JS.md](DOCX-JS.md).

## Editing documents

For simple edits, modify the XML directly.

**For tracked changes**: See [REDLINING.md](REDLINING.md)
**For OOXML details**: See [OOXML.md](OOXML.md)
```

代理只在用户需要这些功能时才阅读 REDLINING.md 或 OOXML.md。

### 避免深层嵌套的引用

当文件是从其他被引用的文件再引用出来时，代理可能会只读一部分。遇到嵌套引用时，代理可能会用 `head -100` 这类命令预览内容，而不是阅读整个文件，从而导致信息不完整。

**从 SKILL.md 出发，引用只保持一层深**。所有参考文件都应当从 SKILL.md 直接链接，以确保代理在需要时读到完整文件。

**坏例子：太深**：

```markdown  theme={null}
# SKILL.md
See [advanced.md](advanced.md)...

# advanced.md
See [details.md](details.md)...

# details.md
Here's the actual information...
```

**好例子：只有一层深**：

```markdown  theme={null}
# SKILL.md

**Basic usage**: [instructions in SKILL.md]
**Advanced features**: See [advanced.md](advanced.md)
**API reference**: See [reference.md](reference.md)
**Examples**: See [examples.md](examples.md)
```

### 用目录组织较长的参考文件

对于超过 100 行的参考文件，在顶部放一个目录。这样即使代理用部分读取来预览，也能看到可用信息的完整范围。

**示例**：

```markdown  theme={null}
# API Reference

## Contents
- Authentication and setup
- Core methods (create, read, update, delete)
- Advanced features (batch operations, webhooks)
- Error handling patterns
- Code examples

## Authentication and setup
...

## Core methods
...
```

然后代理可以阅读完整文件，或按需跳到具体章节。

关于这种基于文件系统的架构如何实现渐进式披露的细节，见下面进阶部分中的[运行环境](#runtime-environment)一节。

## 工作流与反馈循环

### 为复杂任务使用工作流

把复杂操作拆成清楚的顺序步骤。对于特别复杂的工作流，提供一份检查清单，让代理复制到自己的响应里，并随着进展逐项勾掉。

**示例 1：研究综合工作流**（用于没有代码的技能）：

````markdown  theme={null}
## Research synthesis workflow

Copy this checklist and track your progress:

```
Research Progress:
- [ ] Step 1: Read all source documents
- [ ] Step 2: Identify key themes
- [ ] Step 3: Cross-reference claims
- [ ] Step 4: Create structured summary
- [ ] Step 5: Verify citations
```

**Step 1: Read all source documents**

Review each document in the `sources/` directory. Note the main arguments and supporting evidence.

**Step 2: Identify key themes**

Look for patterns across sources. What themes appear repeatedly? Where do sources agree or disagree?

**Step 3: Cross-reference claims**

For each major claim, verify it appears in the source material. Note which source supports each point.

**Step 4: Create structured summary**

Organize findings by theme. Include:
- Main claim
- Supporting evidence from sources
- Conflicting viewpoints (if any)

**Step 5: Verify citations**

Check that every claim references the correct source document. If citations are incomplete, return to Step 3.
````

这个例子说明工作流如何用于不需要代码的分析任务。检查清单模式适用于任何复杂的多步骤过程。

**示例 2：PDF 表单填写工作流**（用于带代码的技能）：

````markdown  theme={null}
## PDF form filling workflow

Copy this checklist and check off items as you complete them:

```
Task Progress:
- [ ] Step 1: Analyze the form (run analyze_form.py)
- [ ] Step 2: Create field mapping (edit fields.json)
- [ ] Step 3: Validate mapping (run validate_fields.py)
- [ ] Step 4: Fill the form (run fill_form.py)
- [ ] Step 5: Verify output (run verify_output.py)
```

**Step 1: Analyze the form**

Run: `python scripts/analyze_form.py input.pdf`

This extracts form fields and their locations, saving to `fields.json`.

**Step 2: Create field mapping**

Edit `fields.json` to add values for each field.

**Step 3: Validate mapping**

Run: `python scripts/validate_fields.py fields.json`

Fix any validation errors before continuing.

**Step 4: Fill the form**

Run: `python scripts/fill_form.py input.pdf fields.json output.pdf`

**Step 5: Verify output**

Run: `python scripts/verify_output.py output.pdf`

If verification fails, return to Step 2.
````

清楚的步骤防止代理跳过关键校验。检查清单帮助你和代理跟踪多步骤工作流的进度。

### 实现反馈循环

**常见模式**：运行校验器 → 修复错误 → 重复

这个模式能大幅提高输出质量。

**示例 1：风格指南符合性**（用于没有代码的技能）：

```markdown  theme={null}
## Content review process

1. Draft your content following the guidelines in STYLE_GUIDE.md
2. Review against the checklist:
   - Check terminology consistency
   - Verify examples follow the standard format
   - Confirm all required sections are present
3. If issues found:
   - Note each issue with specific section reference
   - Revise the content
   - Review the checklist again
4. Only proceed when all requirements are met
5. Finalize and save the document
```

这里展示的是用参考文档而不是脚本做校验循环。「校验器」是 STYLE\_GUIDE.md，代理通过阅读和对照来执行检查。

**示例 2：文档编辑过程**（用于带代码的技能）：

```markdown  theme={null}
## Document editing process

1. Make your edits to `word/document.xml`
2. **Validate immediately**: `python ooxml/scripts/validate.py unpacked_dir/`
3. If validation fails:
   - Review the error message carefully
   - Fix the issues in the XML
   - Run validation again
4. **Only proceed when validation passes**
5. Rebuild: `python ooxml/scripts/pack.py unpacked_dir/ output.docx`
6. Test the output document
```

校验循环能及早抓住错误。

## 内容准则

### 避免时效性信息

不要放入会过时的信息：

**坏例子：有时效**（将会变成错的）：

```markdown  theme={null}
If you're doing this before August 2025, use the old API.
After August 2025, use the new API.
```

**好例子**（使用「旧模式」一节）：

```markdown  theme={null}
## Current method

Use the v2 API endpoint: `api.example.com/v2/messages`

## Old patterns

<details>
<summary>Legacy v1 API (deprecated 2025-08)</summary>

The v1 API used: `api.example.com/v1/messages`

This endpoint is no longer supported.
</details>
```

旧模式一节提供历史上下文，又不把主要内容弄乱。

### 使用一致的术语

选定一个术语，并在整个技能中使用它：

**好——一致**：

* 始终用 "API endpoint"
* 始终用 "field"
* 始终用 "extract"

**坏——不一致**：

* 混用 "API endpoint"、"URL"、"API route"、"path"
* 混用 "field"、"box"、"element"、"control"
* 混用 "extract"、"pull"、"get"、"retrieve"

一致性帮助代理理解和遵循指令。

## 常见模式

### 模板模式

为输出格式提供模板。把严格程度匹配到你的需要。

**对于严格要求**（比如 API 响应或数据格式）：

````markdown  theme={null}
## Report structure

ALWAYS use this exact template structure:

```markdown
# [Analysis Title]

## Executive summary
[One-paragraph overview of key findings]

## Key findings
- Finding 1 with supporting data
- Finding 2 with supporting data
- Finding 3 with supporting data

## Recommendations
1. Specific actionable recommendation
2. Specific actionable recommendation
```
````

**对于灵活指导**（当变通有用时）：

````markdown  theme={null}
## Report structure

Here is a sensible default format, but use your best judgment based on the analysis:

```markdown
# [Analysis Title]

## Executive summary
[Overview]

## Key findings
[Adapt sections based on what you discover]

## Recommendations
[Tailor to the specific context]
```

Adjust sections as needed for the specific analysis type.
````

### 示例模式

对于输出质量取决于看到示例的技能，像常规提示那样提供输入/输出对：

````markdown  theme={null}
## Commit message format

Generate commit messages following these examples:

**Example 1:**
Input: Added user authentication with JWT tokens
Output:
```
feat(auth): implement JWT-based authentication

Add login endpoint and token validation middleware
```

**Example 2:**
Input: Fixed bug where dates displayed incorrectly in reports
Output:
```
fix(reports): correct date formatting in timezone conversion

Use UTC timestamps consistently across report generation
```

**Example 3:**
Input: Updated dependencies and refactored error handling
Output:
```
chore: update dependencies and refactor error handling

- Upgrade lodash to 4.17.21
- Standardize error response format across endpoints
```

Follow this style: type(scope): brief description, then detailed explanation.
````

示例比单独的描述更能帮助代理理解期望的风格和细节程度。

### 条件工作流模式

引导代理通过决策点：

```markdown  theme={null}
## Document modification workflow

1. Determine the modification type:

   **Creating new content?** → Follow "Creation workflow" below
   **Editing existing content?** → Follow "Editing workflow" below

2. Creation workflow:
   - Use docx-js library
   - Build document from scratch
   - Export to .docx format

3. Editing workflow:
   - Unpack existing document
   - Modify XML directly
   - Validate after each change
   - Repack when complete
```

<Tip>
  如果工作流变得很大或很复杂、步骤很多，考虑把它们推进单独的文件，并告诉代理根据手头的任务阅读相应文件。
</Tip>

## 评估与迭代

### 先建立评估

**在写大量文档之前先创建评估。** 这确保你的技能解决的是真实问题，而不是在记录想象出来的问题。

**评估驱动的开发：**

1. **识别缺口**：在没有技能的情况下，让代理跑有代表性的任务。记录具体的失败或缺失的上下文
2. **创建评估**：建立三个检验这些缺口的情景
3. **建立基线**：测量没有该技能时代理的表现
4. **写最少指令**：只写刚好够应对缺口并通过评估的内容
5. **迭代**：执行评估，与基线比较，然后改进

这种做法确保你在解决实际问题，而不是去预期也许永远不会出现的需求。

**评估结构**：

```json  theme={null}
{
  "skills": ["pdf-processing"],
  "query": "Extract all text from this PDF file and save it to output.txt",
  "files": ["test-files/document.pdf"],
  "expected_behavior": [
    "Successfully reads the PDF file using an appropriate PDF processing library or command-line tool",
    "Extracts text content from all pages in the document without missing any pages",
    "Saves the extracted text to a file named output.txt in a clear, readable format"
  ]
}
```

<Note>
  这个例子演示的是带简单测试量规的数据驱动评估。我们目前不提供内置方式来运行这些评估。用户可以建立自己的评估系统。评估是你衡量技能效果的事实来源。
</Note>

### 与代理一起迭代开发技能

最有效的技能开发过程会用到代理本身。与一个实例（「代理 A」）一起工作，创建一份将由其他实例（「代理 B」）使用的技能。代理 A 帮你设计和打磨指令，代理 B 在真实任务中测试它们。这之所以可行，是因为底层模型既理解如何写出有效的代理指令，也理解代理需要什么信息。

**创建新技能：**

1. **在没有技能的情况下完成一项任务**：用普通提示和代理 A 一起把一个问题解决完。工作过程中，你会自然地提供上下文、解释偏好、分享过程性知识。注意你反复提供的是什么信息。

2. **识别可复用的模式**：任务完成后，找出你提供的、对未来类似任务有用的上下文。

   **示例**：如果你做完了一次 BigQuery 分析，你可能提供了表名、字段定义、过滤规则（比如「始终排除测试账号」）以及常见查询模式。

3. **让代理 A 创建技能**：「创建一个技能，捕获我们刚刚使用的这个 BigQuery 分析模式。包括表 schema、命名约定，以及关于过滤测试账号的规则。」

   <Tip>
     现代代理原生理解技能的格式和结构。你不需要特殊的系统提示，也不需要一个「编写技能」的技能来获得创建技能的帮助。只要让代理创建技能，它就会生成结构正确的 SKILL.md 内容，并带上合适的 frontmatter 和正文。
   </Tip>

4. **检查简洁性**：检查代理 A 有没有加上不必要的解释。可以问：「删掉关于胜率是什么意思的解释——代理已经知道了。」

5. **改进信息架构**：让代理 A 把内容组织得更有效。例如：「把表 schema 组织到一个单独的参考文件里。我们以后可能会加更多表。」

6. **在类似任务上测试**：把技能交给代理 B（一个加载了该技能的新实例），用在相关用例上。观察代理 B 是否找到正确信息、正确应用规则，并成功处理任务。

7. **根据观察迭代**：如果代理 B 吃力或漏了什么，带着具体问题回到代理 A：「代理使用这个技能时，忘了按日期过滤第四季度。我们是否应该加一节讲日期过滤模式？」

**迭代已有技能：**

改进技能时，同样的分层模式继续。你在这几者之间交替：

* **与代理 A 一起工作**（帮助打磨技能的专家）
* **用代理 B 测试**（使用技能做真实工作的代理）
* **观察代理 B 的行为**，并把洞见带回给代理 A

1. **在真实工作流中使用技能**：给代理 B（已加载该技能）真实任务，而不是测试情景

2. **观察代理 B 的行为**：注意它在哪里吃力、哪里成功，或做出了意外选择

   **观察示例**：「当我让代理 B 做一份区域销售报告时，它写了查询，但忘了过滤掉测试账号，尽管技能提到了这条规则。」

3. **回到代理 A 寻求改进**：分享当前的 SKILL.md，并描述你观察到的情况。问：「我注意到，当我要一份区域报告时，代理 B 忘了过滤测试账号。技能提到了过滤，但也许不够突出？」

4. **审阅代理 A 的建议**：代理 A 可能会建议重新组织，让规则更突出，使用更强的语言，比如用 "MUST filter" 而不是 "always filter"，或者重构工作流一节。

5. **应用并测试改动**：用代理 A 的改进更新技能，然后在类似请求上再用代理 B 测试

6. **根据使用重复**：遇到新情景时，继续这个观察—打磨—测试的循环。每一轮都基于真实的代理行为改进技能，而不是基于假设。

**收集团队反馈：**

1. 与队友分享技能，并观察他们的使用
2. 问：技能会在预期时激活吗？指令清楚吗？缺了什么？
3. 纳入反馈，弥补你自己使用模式里的盲点

**为什么这种做法有效**：代理 A 理解代理的需要，你提供领域专长，代理 B 通过真实使用揭示缺口，迭代打磨基于观察到的行为而不是假设来改进技能。

### 观察代理如何在技能中导航

迭代技能时，注意代理在实践中实际上如何使用它们。留意：

* **意外的探索路径**：代理读文件的顺序是你没预料到的吗？这可能说明你的结构并不像你想的那样直观
* **错过的连接**：代理没有顺着指向重要文件的引用走吗？你的链接可能需要更明确或更突出
* **过度依赖某些章节**：如果代理反复读同一个文件，考虑那些内容是否应该放进主 SKILL.md
* **被忽略的内容**：如果代理从不访问某个捆绑文件，它可能不必要，或者在主指令里信号太弱

基于这些观察来迭代，而不是基于假设。技能元数据里的 'name' 和 'description' 尤其关键。代理用它们决定是否针对当前任务触发该技能。确保它们清楚地描述技能做什么、以及何时应该使用。

## 要避免的反模式

### 避免 Windows 风格的路径

文件路径始终使用正斜杠，即使在 Windows 上：

* ✓ **好**：`scripts/helper.py`、`reference/guide.md`
* ✗ **避免**：`scripts\helper.py`、`reference\guide.md`

Unix 风格的路径在所有平台上都能工作，而 Windows 风格的路径会在 Unix 系统上造成错误。

### 避免提供太多选项

除非必要，不要摆出多种做法：

````markdown  theme={null}
**Bad example: Too many choices** (confusing):
"You can use pypdf, or pdfplumber, or PyMuPDF, or pdf2image, or..."

**Good example: Provide a default** (with escape hatch):
"Use pdfplumber for text extraction:
```python
import pdfplumber
```

For scanned PDFs requiring OCR, use pdf2image with pytesseract instead."
````

## 进阶：带可执行代码的技能

下面几节聚焦于包含可执行脚本的技能。如果你的技能只用 markdown 指令，跳到[有效技能检查清单](#checklist-for-effective-skills)。

### 自己解决，不要甩给代理

为技能写脚本时，要处理错误条件，而不是把问题甩给代理。

**好例子：明确处理错误**：

```python  theme={null}
def process_file(path):
    """Process a file, creating it if it doesn't exist."""
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        # Create file with default content instead of failing
        print(f"File {path} not found, creating default")
        with open(path, 'w') as f:
            f.write('')
        return ''
    except PermissionError:
        # Provide alternative instead of failing
        print(f"Cannot access {path}, using default")
        return ''
```

**坏例子：甩给代理**：

```python  theme={null}
def process_file(path):
    # Just fail and let the agent figure it out
    return open(path).read()
```

配置参数也应当有理由并写进文档，以避免「巫毒常量」（voodoo constants，Ousterhout 定律）。如果你不知道正确的值，代理又怎么确定它？

**好例子：自解释**：

```python  theme={null}
# HTTP requests typically complete within 30 seconds
# Longer timeout accounts for slow connections
REQUEST_TIMEOUT = 30

# Three retries balances reliability vs speed
# Most intermittent failures resolve by the second retry
MAX_RETRIES = 3
```

**坏例子：魔术数字**：

```python  theme={null}
TIMEOUT = 47  # Why 47?
RETRIES = 5   # Why 5?
```

### 提供实用脚本

即使你的代理能自己写脚本，预先做好的脚本也有优势：

**实用脚本的好处**：

* 比生成的代码更可靠
* 节省 token（不需要把代码放进上下文）
* 节省时间（不需要生成代码）
* 确保各次使用一致

<img src="https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-executable-scripts.png?fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=4bbc45f2c2e0bee9f2f0d5da669bad00" alt="Bundling executable scripts alongside instruction files" data-og-width="2048" width="2048" data-og-height="1154" height="1154" data-path="images/agent-skills-executable-scripts.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-executable-scripts.png?w=280&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=9a04e6535a8467bfeea492e517de389f 280w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-executable-scripts.png?w=560&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=e49333ad90141af17c0d7651cca7216b 560w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-executable-scripts.png?w=840&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=954265a5df52223d6572b6214168c428 840w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-executable-scripts.png?w=1100&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=2ff7a2d8f2a83ee8af132b29f10150fd 1100w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-executable-scripts.png?w=1650&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=48ab96245e04077f4d15e9170e081cfb 1650w, https://mintcdn.com/anthropic-claude-docs/4Bny2bjzuGBK7o00/images/agent-skills-executable-scripts.png?w=2500&fit=max&auto=format&n=4Bny2bjzuGBK7o00&q=85&s=0301a6c8b3ee879497cc5b5483177c90 2500w" />

上图展示可执行脚本如何与指令文件一起工作。指令文件（forms.md）引用脚本，代理可以执行它，而不必把它的内容加载进上下文。

**重要区分**：在指令里说清楚，代理应该：

* **执行脚本**（最常见）：「运行 `analyze_form.py` 来提取字段」
* **当作参考来读**（用于复杂逻辑）：「见 `analyze_form.py` 中的字段提取算法」

对大多数实用脚本，优先执行，因为更可靠、也更高效。脚本执行如何工作的细节，见下面的[运行环境](#runtime-environment)一节。

**示例**：

````markdown  theme={null}
## Utility scripts

**analyze_form.py**: Extract all form fields from PDF

```bash
python scripts/analyze_form.py input.pdf > fields.json
```

Output format:
```json
{
  "field_name": {"type": "text", "x": 100, "y": 200},
  "signature": {"type": "sig", "x": 150, "y": 500}
}
```

**validate_boxes.py**: Check for overlapping bounding boxes

```bash
python scripts/validate_boxes.py fields.json
# Returns: "OK" or lists conflicts
```

**fill_form.py**: Apply field values to PDF

```bash
python scripts/fill_form.py input.pdf fields.json output.pdf
```
````

### 使用视觉分析

当输入可以渲染成图像时，让代理分析它们：

````markdown  theme={null}
## Form layout analysis

1. Convert PDF to images:
   ```bash
   python scripts/pdf_to_images.py form.pdf
   ```

2. Analyze each page image to identify form fields
3. The agent can see field locations and types visually
````

<Note>
  在这个例子里，你需要自己编写 `pdf_to_images.py` 脚本。
</Note>

代理的视觉能力有助于理解布局和结构。

### 创建可验证的中间输出

当代理执行复杂、开放式的任务时，它们会犯错。「计划—校验—执行」模式能及早抓住错误：让代理先用结构化格式创建一份计划，然后在执行前用脚本校验该计划。

**示例**：设想让代理根据一份电子表格更新 PDF 里的 50 个表单字段。没有校验时，它可能会引用不存在的字段、制造冲突的值、漏掉必填字段，或错误地应用更新。

**办法**：使用上面展示的工作流模式（PDF 表单填写），但增加一个中间文件 `changes.json`，在应用更改之前先校验它。工作流变成：分析 → **创建计划文件** → **校验计划** → 执行 → 核实。

**为什么这个模式有效：**

* **及早抓住错误**：校验在更改被应用之前发现问题
* **机器可验证**：脚本提供客观核实
* **可逆的计划**：代理可以在计划上迭代，而不触碰原件
* **调试清楚**：错误信息指向具体问题

**何时使用**：批量操作、破坏性更改、复杂校验规则、高风险操作。

**实现提示**：让校验脚本详细输出，带上具体错误信息，例如 "Field 'signature\_date' not found. Available fields: customer\_name, order\_total, signature\_date\_signed"，以帮助代理修复问题。

### 包依赖

技能运行在代码执行环境中，并带有平台特定的限制：

* **claude.ai**：可以从 npm 和 PyPI 安装包，并从 GitHub 仓库拉取
* **Anthropic API**：没有网络访问，也不能在运行时安装包

在你的 SKILL.md 里列出所需的包，并在[代码执行工具文档](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool)中核实它们可用。

<a id="runtime-environment"></a>

### 运行环境

技能运行在一个代码执行环境中，具有文件系统访问、bash 命令和代码执行能力。这一架构的概念解释，见概述中的[技能架构](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#the-skills-architecture)。

**这如何影响你的编写：**

**代理如何访问技能：**

1. **元数据预加载**：启动时，所有技能 YAML frontmatter 中的 name 和 description 被加载进系统提示
2. **按需读文件**：代理在需要时用它们的文件读取工具，从文件系统访问 SKILL.md 和其他文件
3. **高效执行脚本**：实用脚本可以通过 bash 执行，而不把全部内容加载进上下文。只有脚本的输出消耗 token
4. **大文件没有上下文惩罚**：参考文件、数据或文档在真正被阅读之前不消耗上下文 token

* **文件路径很重要**：代理像文件系统那样在你的技能目录里导航。使用正斜杠（`reference/guide.md`），不要用反斜杠
* **给文件起有描述性的名字**：用能表明内容的名字：`form_validation_rules.md`，而不是 `doc2.md`
* **为发现而组织**：按领域或功能组织目录
  * 好：`reference/finance.md`、`reference/sales.md`
  * 差：`docs/file1.md`、`docs/file2.md`
* **捆绑全面的资源**：放入完整的 API 文档、大量示例、大型数据集；在被访问之前没有上下文惩罚
* **确定性操作优先用脚本**：写 `validate_form.py`，而不是让代理去生成校验代码
* **把执行意图说清楚**：
  * 「运行 `analyze_form.py` 来提取字段」（执行）
  * 「见 `analyze_form.py` 中的提取算法」（当作参考来读）
* **测试文件访问模式**：用真实请求测试，核实代理能在你的目录结构中导航

**示例：**

```
bigquery-skill/
├── SKILL.md (overview, points to reference files)
└── reference/
    ├── finance.md (revenue metrics)
    ├── sales.md (pipeline data)
    └── product.md (usage analytics)
```

当用户询问收入时，代理阅读 SKILL.md，看到指向 `reference/finance.md` 的引用，并调用 bash 只读那个文件。sales.md 和 product.md 留在文件系统上，在需要之前消耗零上下文 token。这种基于文件系统的模型就是渐进式披露得以实现的原因。代理可以导航，并有选择地只加载每个任务所需的东西。

关于技术架构的完整细节，见技能概述中的[技能如何工作](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#how-skills-work)。

### MCP 工具引用

如果你的技能使用 MCP（Model Context Protocol）工具，始终使用完全限定的工具名，以避免 "tool not found" 错误。

**格式**：`ServerName:tool_name`

**示例**：

```markdown  theme={null}
Use the BigQuery:bigquery_schema tool to retrieve table schemas.
Use the GitHub:create_issue tool to create issues.
```

其中：

* `BigQuery` 和 `GitHub` 是 MCP 服务器名
* `bigquery_schema` 和 `create_issue` 是这些服务器内的工具名

没有服务器前缀时，代理可能无法定位工具，尤其是有多个 MCP 服务器可用时。

### 不要假定工具已经安装

不要假定包是可用的：

````markdown  theme={null}
**Bad example: Assumes installation**:
"Use the pdf library to process the file."

**Good example: Explicit about dependencies**:
"Install required package: `pip install pypdf`

Then use it:
```python
from pypdf import PdfReader
reader = PdfReader("file.pdf")
```"
````

## 技术说明

### YAML frontmatter 要求

SKILL.md 的 frontmatter 需要 `name`（最多 64 个字符）和 `description`（最多 1024 个字符）字段。完整结构细节见[技能概述](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#skill-structure)。

### Token 预算

为了最佳表现，把 SKILL.md 正文保持在 500 行以内。如果内容超过这个限度，用前面描述的渐进式披露模式把它拆到单独文件。架构细节见[技能概述](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#how-skills-work)。

<a id="checklist-for-effective-skills"></a>

## 有效技能检查清单

分享技能之前，核实：

### 核心质量

* [ ] description 具体，并包含关键术语
* [ ] description 同时包含技能做什么以及何时使用
* [ ] SKILL.md 正文少于 500 行
* [ ] 额外细节在单独文件里（如果需要）
* [ ] 没有时效性信息（或者放在「旧模式」一节）
* [ ] 全文术语一致
* [ ] 示例是具体的，不是抽象的
* [ ] 文件引用只有一层深
* [ ] 恰当地使用了渐进式披露
* [ ] 工作流有清楚的步骤

### 代码与脚本

* [ ] 脚本自己解决问题，而不是甩给代理
* [ ] 错误处理明确且有帮助
* [ ] 没有「巫毒常量」（所有值都有理由）
* [ ] 所需的包列在指令里，并核实可用
* [ ] 脚本有清楚的文档
* [ ] 没有 Windows 风格的路径（全部是正斜杠）
* [ ] 关键操作有校验/核实步骤
* [ ] 对质量关键的任务包含反馈循环

### 测试

* [ ] 至少创建了三个评估
* [ ] 用 Haiku、Sonnet 和 Opus 测试过
* [ ] 用真实使用情景测试过
* [ ] 纳入了团队反馈（如果适用）

## 下一步

<CardGroup cols={2}>
  <Card title="开始使用 Agent Skills" icon="rocket" href="https://platform.claude.com/docs/en/agents-and-tools/agent-skills/quickstart">
    创建你的第一个技能
  </Card>

  <Card title="在 Claude Code 中使用技能" icon="terminal" href="https://code.claude.com/docs/en/skills">
    在 Claude Code 中创建和管理技能
  </Card>

  <Card title="通过 API 使用技能" icon="code" href="https://platform.claude.com/docs/en/build-with-claude/skills-guide">
    以编程方式上传并使用技能
  </Card>
</CardGroup>
