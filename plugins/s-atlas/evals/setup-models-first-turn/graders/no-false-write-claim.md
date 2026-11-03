---
type: regex
pattern: '已写入|已经写入|写入完成|已保存到'
match: not_contains
target: last_message
weight: 2
---
