# wukong 评测

用 `claude plugin eval` 跑（需要 Claude Code 2.1.269 以上，会消耗你账号的额度）：

```bash
claude plugin eval plugins/wukong --runs 1 --max-cost-usd 2      # 全部，各跑 1 次
claude plugin eval plugins/wukong --tag smoke --runs 1            # 只跑便宜的
```

每个用例只有一条用户消息，不能模拟用户回答提问，所以交互流程只测第一轮。

| 用例 | 测什么 | 标签 |
|---|---|---|
| `no-init-on-unrelated` | 无关请求不会误触发 wukong-init | smoke |

结果目录 `evals/results/` 已被 `.gitignore` 忽略，也不计入插件内容哈希。
