# 开发 bot 目录

每个 bot 都用 Orca 自带的模板，名字和用途换成中文。模板自带的自动化和 Orca 自己的技能照常保留，本目录不改它们。

| 键 | name | 模板 id | 界面里的模板名 | 连接 | bot 技能 |
| --- | --- | --- | --- | --- | --- |
| `pr-review` | `pr-reviewer` | `pr-review` | Pull request review | GitHub | [wukong-pr-review](../assets/wukong-pr-review.md) |
| `bug-hunt` | `bug-hunter` | `bug-investigation` | Bug investigation | GitHub，用 Linear 时加 Linear | [wukong-bug-hunt](../assets/wukong-bug-hunt.md) |
| `ci-triage` | `ci-triage` | `ci-failures` | CI failures | GitHub | [wukong-ci-triage](../assets/wukong-ci-triage.md) |
| `deps` | `dep-updater` | `dependency-updates` | Dependency updates | GitHub | [wukong-deps](../assets/wukong-deps.md) |
| `release` | `release-guard` | `release` | Release readiness | GitHub | [wukong-release](../assets/wukong-release.md) |

## pr-review：PR 审查

- purpose：审查等我 review 的 PR，按风险列出问题和缺的测试，每条附文件和行号。
- watches：我选的仓库里等我 review 的 PR
- does：先写一句改动意图，再按严重、一般、建议列问题，附证据和文件行号，最后给能不能合并
- reports：在这个聊天里，有人请我 review 时
- 模板自带：被请求 review 时触发的自动化，Orca 的 `pr-review-checklist` 技能
- 提醒用户：bot 要在 GitHub 上发评论，得在它的聊天里明确同意。

## bug-hunt：Bug 排查

- purpose：复现我交给它的 bug，找到第一次出错的地方，我同意后再修。
- watches：我交给它的 bug 报告，以及指派给我的 Linear issue
- does：在新工作区里写出复现步骤，用证据定位根因，提出修法；修之前先等我同意
- reports：在这个聊天里，有复现和根因时
- 模板自带：Linear issue 指派给你时触发的自动化，Orca 的 `bug-reproduction` 技能
- 提醒用户：不用 Linear 时，Linear 的 Connect 卡片可以不点，只是指派自动化不会触发。

## ci-triage：CI 失败分诊

- purpose：检查挂了就说清原因，分开偶发失败和真失败，并维护偶发失败清单。
- watches：我选的仓库里的检查运行
- does：读失败日志，找出第一条真正的错误，判断偶发还是真失败并给出依据；我同意后再派 worker 修
- reports：在这个聊天里，检查失败时，以及每周一上午 9 点的偶发失败清单
- 模板自带：检查失败时触发、每周一汇总的自动化，Orca 的 `ci-failure-triage` 技能
- 提醒用户：收不到检查失败的事件时，在 bot 聊天里运行 `orca bot connectors` 看缺哪一项。

## deps：依赖升级

- purpose：每周列出过期和有漏洞的依赖，最急的在前，我同意后每组开一个 PR 升级。
- watches：我选的仓库里的依赖
- does：列出安全公告和过期依赖并分组，写明破坏性变更；我同意后每组派 worker 升级、跑测试、开 PR
- reports：在这个聊天里，每周一上午 9 点
- 模板自带：每周一上午 9 点的检查，Orca 的 `dependency-upgrade` 技能
- 提醒用户：仓库用 pnpm、Go modules、Maven 这类工具时，在 bot 第一次运行时说明。

## release：发版检查

- purpose：每个工作日早上告诉我下次发版还被什么挡着。
- watches：我选的仓库里的 PR、检查和工作区
- does：列出失败的检查、等审查的 PR、未解决的阻塞项，每项附链接和负责人；全部清空时说一句能发
- reports：在这个聊天里，工作日上午 9 点
- 模板自带：工作日上午 9 点的清单，Orca 的 `release-readiness` 技能
- 提醒用户：bot 第一次运行时说明发版分支，以及标记阻塞用的标签或里程碑。
