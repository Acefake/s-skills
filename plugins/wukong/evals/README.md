# wukong 评测

用 `claude plugin eval` 跑（需要 Claude Code 2.1.269 以上，会消耗你账号的额度）：

```bash
claude plugin eval plugins/wukong --runs 1 --max-cost-usd 2      # 全部，各跑 1 次
claude plugin eval plugins/wukong --tag smoke --runs 1            # 只跑便宜的
```

每个用例只有一条用户消息，不能模拟用户回答提问，所以交互流程只测第一轮。

| 用例 | 测什么 | 标签 |
|---|---|---|
| `setup-models-first-turn` | 说「配置 s 模型」会选中 setup-s-models，先提问，不谎称已写入 | smoke |
| `no-setup-on-unrelated` | 无关请求不会误触发 setup-s-models | smoke |
| `interrogate-dispatch-effort` | 角色行写 `sonnet（medium）` 时，派审查者的 `model` 是干净的别名、`effort` 带上档位 | dispatch |

结果目录 `evals/results/` 已被 `.gitignore` 忽略，也不计入插件内容哈希。
