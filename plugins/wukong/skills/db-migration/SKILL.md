---
name: db-migration
description: "「/db-migration」「写数据库迁移」「加字段改表结构」「零停机迁移」。审查或编写 DDL 与数据迁移脚本：排查大表锁表、非空列默认值、索引并发创建、expand-contract 零停机拆步、数据回填分批与回滚方案。Use when writing or reviewing database schema migrations, DDL changes, data backfills, or zero-downtime expand-contract rollouts."
disable-model-invocation: true
---

本会话首次使用本库技能时，按[全局提示词自检](../wukong-init/references/daily-check.md)只读检查一次。
## 运行环境适配

涉及宿主工具或子代理时，按需阅读[宿主适配](../../HOSTS.md)。

# 数据库迁移守护

在编写或审查 DDL、ORM 迁移脚本与数据回填前，先排除锁表、破坏性变更与不可逆数据丢失风险。

## 1. 先查清数据库与现状

动笔前先从代码库确认以下事实，不要猜：

- **数据库引擎与版本**：PostgreSQL、MySQL（5.7 / 8.0）、SQLite 或其他（锁行为差异极大）。
- **迁移工具**：Prisma、Flyway、Liquibase、Alembic、golang-migrate、Rails ActiveRecord 或裸 SQL。
- **表规模与访问模式**：是否核心热表/大表、是否存在长事务、应用是否滚动发布（新旧版本代码会短暂共存）。

## 2. 高危操作清单

逐条检查，命中任意一项必须给出安全改法：

| 高危操作 | 风险 | 安全做法 |
|---|---|---|
| 大表直接 `CREATE INDEX` | 阻塞写入甚至读写 | PostgreSQL 用 `CREATE INDEX CONCURRENTLY`（需在事务外）；MySQL 确认 `ALGORITHM=INPLACE, LOCK=NONE` |
| 直接改列类型 / 改列名 / 删列 | 锁表 + 滚动发布期间旧代码直接报错 | 改走 Expand-Contract 拆步，绝不在同一发布窗口删旧列 |
| 新增 `NOT NULL` 列（无安全默认值或带易失表达式） | 重写整表锁表 | 先加可空列 → 分批回填 → `NOT VALID` 约束 + `VALIDATE CONSTRAINT`（PG）或确认在线 DDL |
| 一次性全表 `UPDATE` 回填 | 长事务、主从延迟、锁等待雪崩 | 按主键区间分批（如每批 1000–5000 行）+ 间隔限流，做成可断点续跑的幂等脚本 |
| 无 `lock_timeout` / `statement_timeout` | 拿不到锁时阻塞后续所有查询排队 | 在迁移脚本开头显式设置短 `lock_timeout`（如 `2s–5s`），失败重试而非拖垮线上 |

## 3. Expand-Contract 零停机拆步

涉及改列名、改类型、拆表、删列或语义切换时，拆成独立部署阶段：

1. **Expand（扩展）**：只做向后兼容的加法（新列可空、新表、新索引），应用开始双写（写旧 + 写新），读仍走旧字段。
2. **Backfill（回填）**：运行可重跑、分批限流的历史数据回填脚本，并校验新旧数据一致性。
3. **Switch（切读）**：验证一致后，应用切为读新字段（保留回退开关）。
4. **Contract（收缩）**：确认旧版本实例全部下线且观察期通过后，在后续独立迁移中再删旧列/旧表。

## 4. 回滚与验证

- **每份迁移都要说明回滚方式**：能安全 `down` 就写可验证的回滚脚本；不可逆操作（删数据/截断）必须标红并要求上线前备份或归档。
- **本地实跑验证**：至少在本地或测试库跑通「正序迁移 → 已有数据校验 →（如支持）回滚再重跑」，并核对生成 SQL（ORM 迁移务必检查实际生成的 DDL，不只看模型定义）。
