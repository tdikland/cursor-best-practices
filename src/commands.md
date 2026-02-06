# Commands

Cursor commands are custom instructions you can invoke from the chat (e.g. `/commit`). They live as Markdown files in `.cursor/commands/`. Each command describes what the agent should do when you run it, so you get consistent behavior without repeating the same prompt.

## Example: commit command

This repo defines a **commit** command so you can type `/commit` to stage and commit your changes. The command file (`.cursor/commands/commit.md`) is:

```markdown
---
description: When the user asks to commit modifications, stage and commit with an appropriate message
alwaysApply: true
---

# Commit modifications

When the user asks to commit modifications, commit changes, or similar:

1. Run `git status` to see what is modified.
2. Stage changes: `git add -A` (or `git add .`), or stage specific paths if the user specified files.
3. Commit with a message:
   - If the user provided a message, use it: `git commit -m "user message"`.
   - Otherwise, propose a short, conventional commit message based on the changes (e.g. "docs: add prompt tips to book") and run `git commit -m "..."`.

Do not run `git push` unless the user explicitly asks to push.
```

When you run `/commit`, the agent follows these steps: checks status, stages changes, then commits with your message or a suggested conventional one. It does not push unless you ask.
