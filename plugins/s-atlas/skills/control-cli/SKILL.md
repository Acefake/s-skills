---
name: control-cli
description: "搭一个本地的驾驭装置，驱动、查看并剖析交互式命令行或 TUI，不依赖外部服务。用于命令行体验、启动变慢、内存泄漏、卡住、提示流程，或录一段终端演示。Use when you need to drive a local CLI or TUI and inspect what it does."
---
## 运行环境适配

在 Codex 或 T3 Code 中，执行前先阅读[宿主适配规则](../../HOSTS.md)；其中的模型、委派、浏览器和定时任务规则优先于下文的 Cursor 专用示例。


# 操作命令行

用一套能重复跑的本地驾驭装置去操一个交互式命令行，不要用手一下一下戳。仓库里已经有测试或演示用的装置，就先用那个。没有，再用本机常见工具临时搭一个。

## 用来做什么

- 用确定的输入复现命令行或 TUI 的 bug。
- 核对按键流程、提示、中断、改变窗口大小和终端排版。
- 为修 bug 留下改前和改后的记录。
- 剖析启动时间、慢操作、卡住，或内存增长。
- 用户要看演示、而且画面比解释清楚时，录一段短的终端演示。

## 循环

1. 确定要测的命令，以及最小的、能复现的工作区。
2. 找仓库里已有的装置：包脚本、端到端测试、演示录制、expect 脚本，或 PTY 辅助。
3. 没有的话，用确定的环境变量，在一个隔离的终端会话里启动命令行。
4. 动手之前先抓当前画面。
5. 一次只送一个动作：文字、Enter、方向键、Escape、Ctrl-C、改变大小。
6. 等到一个具体的画面或提示出现，再送下一个动作。
7. 保存记录和剖析产物。
8. 干净地结束会话。

## 可以怎么搭

- 仓库自带的装置优先。它知道怎么启动、要什么环境变量、提示长什么样。
- `tmux`：管会话、`capture-pane`、`send-keys`、挂上和摘下。
- PTY 探测：没有 tmux 时，用一段短的 Python、Node 或 Expect。
- 运行时检查器：用 Node 或 Bun 的 inspector 做 CPU 剖析、堆快照和现场求值。
- 终端录制：用户要演示时，用仓库里的演示工具，或兼容 asciinema 的工具。

## 最小的 tmux 装置

```bash
SESSION="cli-harness-$(date +%s)"
tmux new-session -d -s "$SESSION" -- <command-under-test>
tmux capture-pane -pt "$SESSION"
tmux send-keys -t "$SESSION" "help" Enter
tmux capture-pane -pt "$SESSION"
tmux kill-session -t "$SESSION"
```

Node 写的命令行：

```bash
NODE_OPTIONS="--inspect=127.0.0.1:0" tmux new-session -d -s "$SESSION" -- <node-cli-command>
```

从终端输出里找出 inspector 的地址。需要剖析时，再用和 Chrome DevTools 兼容的工具。

## 最小的 PTY 装置

仓库没有 tmux、也没有演示装置，又需要确定的等待时，用 PTY 脚本。用户没要求收进仓库，就只放临时位置。

```python
import os
import pty
import select
import subprocess
import time

master_fd, slave_fd = pty.openpty()
proc = subprocess.Popen(
    ["<command>", "<arg>"],
    stdin=slave_fd,
    stdout=slave_fd,
    stderr=slave_fd,
    close_fds=True,
)
os.close(slave_fd)

deadline = time.time() + 30
buffer = b""
while time.time() < deadline:
    ready, _, _ = select.select([master_fd], [], [], 0.25)
    if not ready:
        continue
    chunk = os.read(master_fd, 4096)
    buffer += chunk
    if b"<ready text>" in buffer:
        os.write(master_fd, b"help\n")
        break

print(buffer.decode(errors="replace"))
proc.terminate()
os.close(master_fd)
```

命令行需要更完整的终端控制时，用 `pty.fork()`，或仓库里已经有的 PTY 库。

## 剖析

- 启动变慢：在同一台机器、同一套环境、同一条命令下，分别量基线和改动后的启动时间。
- 慢操作：开始 CPU 剖析，做那一步，停掉剖析，比较自身耗时最高的函数。
- 内存泄漏：能强制 GC 就先强制，拍一张堆快照，把操作重复多遍，再强制 GC，再拍一张。
- 卡住：打断之前，抓画面、还活着的句柄或资源，以及一份栈或 CPU 采样。

## 边界

- 优先等一个确定的信号，不要 `sleep`。必须睡的时候，说明为什么。
- 不要把凭证或破坏性命令送进受控会话。
- 装置放在 `/tmp`，除非仓库里已经有测试或演示装置。
- 不要写死别的仓库的路径。命令按当前仓库的脚本和运行时改。
- 做完清掉 tmux 会话、临时目录、inspector 进程和演示产物。用户要求留下的除外。

## 在不同软件里怎么用

装置跑在有这个命令行的那台机器上。Cursor、OpenCode、Codex 都用上面的 `tmux` 或 PTY。聊天软件如果把子智能体放在另一台机器上，而命令行只在用户电脑上，就在用户这台机器上跑装置，并在回复里写明跑在哪。

WorkBuddy 和 Claude Code 同样用本机的 `tmux` 或 PTY。没有 `tmux` 时用上面的 Python。不要发明一个聊天软件里的“control-cli”参数。
