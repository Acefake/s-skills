# 问题清单

> 翻译自 Compound Engineering 插件（编号 680）的 `去AI腔` skill 参考文件，原作者 Kieran Klaassen 和 Trevin Chow（版权 © 2025 Every），许可证 MIT，仅供自用。引号里的英文例句是要识别的英文写法，保留原文。

规则编号是固定的编号。删掉的规则会留下空号，不要重新编号。每条规则写明问题和改法。一段文字算不算问题，由 `SKILL.md` 里的检查项决定；这份清单只说明要找什么、改成什么。

**误报底线。** 单独出现一次某种写法，只是作者的选择，不算 AI 痕迹。多种问题叠在一起时才标出来（SKILL.md 检查项 5）。以下情况永远不标：引号、标题或代码里的文字；某个领域里有确切含义的术语；为了强调而故意的重复；范围说明、安全提示或真正的更正；用来强调的一个短句；信件里的标题或落款。

## 内容

1. **吹捧。** 给普通事实硬加上"很重要"的说法："marks a turning point"、"plays a vital role"、"a testament to"、"in today's landscape"。删掉吹捧，保留事实。
2. **句尾 -ing 分析。** 句子末尾硬接一个解释意义的从句："highlighting"、"ensuring"、"reflecting"、"showcasing"、"underscoring"。删掉这个从句，句子照样成立。
3. **宣传形容词。** "Vibrant"、"seamless"、"robust"、"groundbreaking"、"stunning"、"thoughtfully designed"、"powerful yet simple"。说出具体特性，或者删掉这个说法。
4. **模糊出处。** "Experts believe"、"industry reports suggest"、"widely regarded"、"studies show"。写出具体来源，或者删掉这个说法。绝不能编造来源。
5. **套路式展望。** "Despite challenges, continues to thrive"；结尾一段讲光明的未来。保留一个真实的局限或计划，直白地说出来，最后停在最后一个具体事实上。
6. **先铺垫再反转的文案。** "Ten features. Zero headaches." "Everything changed. Your invoice didn't." 直接说这个东西做什么；如果整句话全靠反转撑着，说明这句话本来就没有内容。
7. **假装有洞见。** "The part everyone misses"、"what nobody tells you"、"the real question is"、"at its core"。删掉铺垫，让观点自己站住。
8. **自我评论。** "This matters more than it sounds"、"the key point is"、"as you can see"，或者明明没什么不清楚却说 "in other words"。删掉这些旁白；如果观点确实不清楚，就补充支撑内容。
9. **否定一个没人提过的选项。** "A tempting approach would be"、"some might say"、"this isn't about X"。去掉这个假选项，直接说真正的限制。

## 语言

10. **模型爱用的词。** Delve、tapestry、testament、underscore、showcase、garner、interplay、intricate、enduring、foster、crucial、pivotal、additionally、moreover、enhance、leverage、utilize、facilitate，以及把 landscape、realm、journey 当抽象概念用。换成能表达实际意思的普通词。
11. **花哨的系动词。** 句子本意是"是"或"有"，却写成 "Acts as"、"functions as"、"serves as"、"offers"、"boasts"、"represents"。用简短的动词。
12. **不是 X 而是 Y。** "It's not just a linter, it's a system." "The question isn't A, it's B." 没人说过 X；直接说 Y。
13. **硬凑三个。** 本来一两个就够，却凑出三个形容词、三个例子、三个节拍。只保留真实、具体的那几个。
14. **换着说法指同一个东西。** 同一个东西在一段里有三个叫法。选一个词反复用；在技术写作里，重复就是准确。
15. **看似范围、其实是列举。** "From onboarding to billing"，其实 onboarding 和 billing 只是两个项目，并不是某个范围的两端。直接列出这些项目。
16. **废话。** "In order to" 就是 "to"。"Due to the fact that" 就是 "because"。"It is important to note that" 什么都不是。"At this point in time" 就是 "now"。
17. **层层叠加的含糊词。** "Could potentially possibly" 就是 "may"。只用一个含糊词，而且只在确实不确定时才用。
18. **用副词代替动词干活。** "Runs quickly" 改成 "finishes in 40 ms"；"significantly improves" 改成实际测量到的变化。当意思全靠副词表达时，换个动词或者给出数字。
19. **名词化。** "The demotion of the grid is the change" 就是 "demote the grid"。优先用动词。
20. **借来的比喻代替普通操作。** 用物理、战略或机械方面的词来指一个普通的代码操作：其实是方法却叫 "vector"，其实是 API 却叫 "surface"，其实是函数却叫 "primitive"，其实是一个改动却叫 "lever" 或 "wedge"，其实是目标却叫 "north star"，其实是反馈循环却叫 "flywheel"，代码只是被移走却说 "evacuating"。直接说出操作或东西本身。
21. **用感觉代替机制。** "Deploys feel effortless"、"errors are handled gracefully"、"the API gets out of your way"。说出读者能做什么或能检查什么："a failed deploy rolls back within one minute"、"a malformed row is skipped and logged with its line number"。

## 结构

22. **句子太密。** 读者要读两遍才能理解的句子。一句一个意思；一串分号连起来的句子改成列表。
23. **被动句藏起了执行者。** "Queries are validated" 让读者猜是谁在校验；"the compiler validates queries" 就不会。只有写出执行者没意义时，才保留被动句。
24. **结论埋在后面。** 结论出现在理由之后。顺序应该是：结论，然后理由，然后背景。
25. **第一句重复标题。** 删掉重复的部分，直接从内容开始。
26. **结尾总结复述。** "In conclusion"、"overall"，或者一整段重复全文。停在最后一个具体要点或下一步行动上。
27. **戏剧化的短句。** "No priors. No nostalgia. The old rules were gone." 一个短句可以点明观点；一连串短句就是在摆姿态。改写成完整的句子。
28. **冒号揭晓。** "The detail that makes it work: a separate grader." 冒号应该放在列表或引文前面，不是用来制造戏剧效果，也不是句子中间的连接词。

## 格式

29. **把破折号当节奏拐杖。** 每段好几个破折号，或者套路式的 "this isn't X — it's Y"。改用句号或逗号，或者拆句。代码、数值范围和表格里的破折号不用管。
30. **粗体标签只是重复这一行。** "**Performance:** performance improved." 改成普通句子。只有后面的句子说出了标签没说的内容时，才保留粗体开头。
31. **到处撒粗体来强调**，每个专有名词或缩写都加粗。只把读者必须找到的东西加粗。
32. **标题每个词首字母大写（Title Case）。** 改成只有句首大写（Sentence case）。
33. **装饰性的 emoji**，出现在标题和列表项里。删掉，除非调用方的约定规定要用。
34. **该用两句话的地方用了列表**；只有两句话的小节也加标题；短文档每节之间都加分隔线。格式要服从内容。
35. **弯引号**和直引号混用。技术文字里用直引号。

## 聊天痕迹

36. **聊天机器人式的开场和结尾。** "Certainly"、"Great question"、"Happy to help"、"Let me know if you need anything else"、"Want me to"。删掉，直接说内容。
37. **讨好。** 回答之前先说 "You're absolutely right"。直接回答。
38. **预告下一个要点。** "Let's dive in"、"here's what you need to know"、"without further ado"。直接说要点。
39. **在报告里讲过程。** 智能体做过的、但不影响读者下一步怎么做的步骤。已排除的原因或失败的修复要保留，作为发现写出来；智能体怎么花时间的经过要删掉。
40. **知识局限的免责声明和凭空补全。** "While details are limited, it likely..." 说明原文没有提到什么，或者删掉这句。绝不能把猜测当事实说。
41. **刻意显得周全。** 光秃秃的数字（"resolved 11 threads"）、评分表、检查过的所有东西的清单。说出做了什么决定、为什么；如果没有做出任何非例行的决定，就什么都不说。
