# Hooks


Cursor hooks are scripts that run at defined stages of the agent loop (e.g. before/after file edits, shell execution). They are configured in `.cursor/hooks.json` and receive JSON over stdin. Project hooks run from the project root and apply to everyone who opens the repo in a trusted workspace.

Use hooks to run formatters after edits, audit actions, or enforce policies without repeating instructions in chat.

## Example: format Markdown after edit


This repo defines an **afterFileEdit** hook that formats and cleans Markdown files whenever the agent creates or modifies them. That keeps docs consistent without extra prompts.

**Configuration** (`.cursor/hooks.json`):

```json
{
  "version": 1,
  "hooks": {
    "afterFileEdit": [
      {
        "command": "python3 .cursor/hooks/format-markdown.py"
      }
    ]
  }
}
```

**Script** (`.cursor/hooks/format-markdown.py`): reads the hook payload from stdin, and if the edited file is a `.md` or `.markdown` file, it applies common Markdown best practices:

- Single trailing newline at end of file
- No trailing whitespace on lines
- Blank line before and after ATX headings (`#`, `##`, …)
- Space between `#` and the heading text
- At most one consecutive blank line

So you can ask the agent to create or change Markdown and get consistent formatting automatically. To change or extend the rules, edit `.cursor/hooks/format-markdown.py`.

For more hook types and options (e.g. `beforeShellExecution`, matchers, timeouts), see [Hooks \| Cursor Docs](https://cursor.com/docs/agent/hooks).

## Hook types and benefits


Hooks can run at different points: session start/end, before/after tool use (e.g. shell, file edit, MCP), before prompt submit, and more. They help enforce standards, prevent mistakes, and automate repetitive tasks—e.g. validate commands, format files, add context, or block risky operations. Keep hooks fast, fail gracefully, and document them for the team.
