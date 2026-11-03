---
type: llm
focus: last_message
weight: 2
---
PASS if the assistant is still in the setup flow: it asks the user a question (directly or via AskUserQuestion) about the host or the budget (省/中/大/不限), or shows the candidate models and asks how to proceed. Asking only one step at a time is expected.
FAIL if it claims the configuration file was written or the setup is finished, if it shows a final 17-row block and treats it as accepted without asking, or if it never asks the user anything.
