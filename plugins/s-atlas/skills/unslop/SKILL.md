---
name: unslop
description: "「/unslop」「去掉 AI 腔」「这段话太像机器」。改写文字，让它像人写的。Use when prose sounds like AI and should be rewritten in a plain voice."
disable-model-invocation: true
---
# 去掉 AI 腔

修改文字，去掉 AI 的写作套路。先按下面的套路扫一遍，然后重写。保留原意，符合想要的语气。

## 要找出并修掉的套路

规则编号是固定的 id，其他 skill 会引用它们。删掉的规则会留下一个空号。

### 内容

3. **浮于表面的 -ing 短语。** "highlighting..."（突出了……）、"ensuring..."（确保了……）、"reflecting..."（体现了……）、"showcasing..."（展示了……）、"fostering..."（促进了……）。删掉，或者用真实的来源展开。
5. **含糊的出处。** "Experts believe"（专家认为）、"Industry reports suggest"（行业报告显示）、"Some critics argue"（一些批评者认为）。说出来源，或者删掉。

### 用词

7. **AI 爱用的词。** Additionally（此外）、crucial（至关重要）、delve（深入探讨）、enduring（持久的）、enhance（增强）、fostering（促进）、garner（获得）、interplay（相互作用）、intricate（错综复杂）、landscape（抽象意义上的“格局”）、pivotal（关键性的）、showcase（展示）、tapestry（抽象意义上的“画卷”）、testament（证明）、underscore（凸显）、vibrant（充满活力的）。换成平常的词。
8. **把“是”说得花里胡哨。** "serves as"（充当）、"stands as"（作为）、"boasts"（拥有）、"features"（具备）。直接说 "is"（是）或 "has"（有）。
9. **“不只是 X，更是 Y。”** 直接说出要点。
10. **三的法则。** 不要硬把想法凑成三个一组。有几个就写几个。
11. **同义词轮换。** 在一段话里，主人公、主角、核心人物、英雄全用上了。挑一个，重复用它。
12. **假的范围。** “从 X 到 Y”，而 X 和 Y 并不在一个有意义的尺度上。直接列出话题。

### 风格

13. **滥用破折号（em dash）。** 完全不要用破折号。只用句号或逗号（不用括号，不用短破折号 en dash，也不用拿连字符当破折号）。如果一个想法需要隔开，就结束这句话，或者用逗号。
14. **滥用冒号。** 冒号放在列表或例子前面没问题，但不要用来在句子中间连接。"If you're coming from traditional automation: instead of registering event handlers, you describe conditions"（如果你习惯传统的自动化：你不是注册事件处理函数，而是描述条件）里的冒号什么也没增加。改写一下，让要点不靠对比的框架也能自己立住。"Describing when the scheduler should fire works best as plain English."（用平常的英文描述调度器什么时候触发，效果最好。）意思一样，不用靠标点撑着。
15. **滥用粗体。** 不要把每个专有名词或缩写都加粗。
16. **行内小标题式的列表。** 典型表现是一个粗体标签加冒号，而后面那句话又把标签重复了一遍："**Performance:** Performance improved..."（**性能：** 性能提升了……）。把这种改写成正常的段落。如果一个粗体开头以句号结尾、说出了这一项的名字、后面跟着真正的新细节（"**Schema in TypeScript.** Tables live in one file."，意思是“**用 TypeScript 写 schema。** 所有表都放在一个文件里。”），那就没问题，不算 AI 腔。
17. **标题每个词首字母大写（Title Case）。** 用句子式大小写（只有第一个词首字母大写）。
18. **装饰性的 emoji。** 从标题和要点里去掉。
19. **弯引号。** 用直引号。

### 交流痕迹

20. **聊天机器人用语。** "I hope this helps!"（希望这对你有帮助！）、"Let me know if..."（如果……请告诉我）、"Of course!"（当然！）、"Certainly!"（没问题！）、"Found the smoking gun!"（找到铁证了！）。删掉。
22. **讨好的语气。** "Great question! You're absolutely right!"（好问题！你说得完全对！）直接回答。

### 废话

23. **填充短语。** "In order to" 改成 "To"（为了）。"Due to the fact that" 改成 "Because"（因为）。删掉 "It is important to note that"（值得注意的是）。
24. **过度含糊其辞。** "could potentially possibly be argued that it might"（或许有可能可以认为它也许）改成 "may"（可能）。
25. **空泛的结尾。** "The future looks bright."（未来一片光明。）说出具体的计划或事实。

### 行话

26. **抽象的比喻名词。** Substrate（改用 base，基础）、wedge、wedge in（改用 add，加入）、vector（改用 way、method，方式、方法）、locus、vantage、nexus、作名词用的 primitive、作比喻用的 harness、"API surface" 这种用法里的 surface、bedrock、作比喻用的 scaffolding、modality、paradigm、gold-plating（改说“超出工作需要”）、作比喻用的 ratchet（改用这个机制的真名，或者“只会收紧的限制”）、用来说移动代码的 evacuate（改用 move out，移出去）、endgame（改说“最后阶段”）、north star、flywheel。这些词读起来很有技术感，但通常都有一个更平常、更具体的词。挑那个具体的词。

### 说人话

27. **说它做了什么，而不是它给人什么感觉。** "the database stays close at hand"（数据库触手可及）、"SQL you can read"（你能读懂的 SQL）、"types that follow your schema"（跟着你的 schema 走的类型），这些说的是一种感觉。修法是说出机制或者一个数字："`.toSQL()` returns the exact string sent to the database"（`.toSQL()` 返回发给数据库的那个确切字符串）、"a column rename fails the build"（改了列名，构建就会失败）。问问这句话告诉读者要做什么或知道什么，然后就写那个。如果你没法把它改写成一个具体的指示、事实或数字，就删掉。再多一个检查：如果这句话原封不动地放进另一个项目的文档里也说得通，那它对这个项目什么也没说。删掉。
28. **缩短或拆开太密的句子。** 如果读者要回头重读才能理清一句话，就把它拆成两句，或者去掉一些从句。一句话一个意思。
29. **主动语态。** 优先用它。找出“is/are/was/were + 过去分词”，说出动作的执行者："queries are validated"（查询被校验）改成 "the compiler validates queries"（编译器校验查询），"the file is parsed by the loader"（文件被加载器解析）改成 "the loader parses the file"（加载器解析文件）。只有在执行者未知、或者确实无所谓时，被动语态才可以。
30. **删掉副词，或者用一个更有力的动词。** "runs quickly"（运行得很快）改成 "is fast"（很快）或者直接给数字，"significantly improves"（显著提升）改成测出来的差值。需要一个副词来撑着的弱动词，说明动词选错了。
31. **优先用平常的词。** "utilize" 和 "leverage" 改成 "use"（用），"facilitate" 改成 "help"（帮助），"numerous" 改成 "many"（很多），"in the event that" 改成 "if"（如果）。更花哨的同义词很少会更清楚。
32. **矫揉造作的文风。** 明明有直白的说法，却用比喻或修饰：格言（"wire it or delete it"，接上它或删掉它）、为了效果而用的修辞性短句、拟人化的代码（"the plan holds it"，计划托住了它）、比喻性的动词（"rides along" 跟着走、"stands on" 站在……之上）、套路化的开场白。"A dial worth turning"（一个值得拧一拧的旋钮）改成 "a parameter worth varying"（一个值得调整的参数）。有什么就说什么。比喻名词见第 26 条。
33. **过度压缩。** 省掉冠词、没有动词的片段、用符号说话、用缩写，让读者不是在读而是在解码。"Parser rejects bad date → exit 2, no write"（解析器拒绝坏日期 → 退出码 2，不写入）改成 "The parser rejects a bad date, exits with code 2, and writes nothing."（解析器拒绝一个错误的日期，以代码 2 退出，并且什么都不写入。）写完整的句子，带上冠词和动词，把箭头和缩写都写出来。
