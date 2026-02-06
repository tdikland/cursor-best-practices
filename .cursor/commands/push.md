---
description: When the user asks to push, commit any uncommitted changes then push to GitHub
alwaysApply: true
---

# Commit and push to GitHub


When the user asks to push, push to GitHub, or similar:

1. Run `git status` to see the current state.
2. If there are uncommitted changes:
   - Stage: `git add -A` (or specific paths if the user specified files).
   - Commit: use the user's message if provided; otherwise propose a short, conventional commit message and run `git commit -m "..."`.
3. Push: `git push` (or `git push origin <branch>` if a branch was specified).

If there is nothing to commit and the working tree is clean, skip step 2 and run `git push` only.
