# User Prompt Submit Hooks

User prompt submit hooks run automatically when you submit a prompt to the AI assistant. They're useful for enforcing project-specific rules and context.

## What Are User Prompt Submit Hooks?

These hooks execute before your prompt is sent to the AI, allowing you to:
- Add project-specific context automatically
- Enforce coding standards
- Inject reminders about best practices
- Provide dynamic information (current date, git status, etc.)

## Configuration

Create a hook in your project's `.clauderc` or Cursor settings:

```json
{
  "hooks": {
    "userPromptSubmit": {
      "command": "bash",
      "args": ["-c", "cat project-context.txt"]
    }
  }
}
```

## Example Hooks

### Project Context Hook

Automatically include project guidelines with every prompt:

**Script: `.cursor/hooks/project-context.sh`**
```bash
#!/bin/bash

cat << 'EOF'
PROJECT CONTEXT:
- This is a Databricks project using Unity Catalog
- All PySpark code must be serverless-compatible
- Use three-level namespace: catalog.schema.table
- Follow the PySpark rules in /docs/pyspark-rules.md

Current branch: $(git branch --show-current)
Last commit: $(git log -1 --oneline)
EOF
```

### Git Status Hook

Include git status with every prompt:

```bash
#!/bin/bash

echo "=== GIT STATUS ==="
git status --short
echo ""
echo "Current branch: $(git branch --show-current)"
```

### Environment Reminder Hook

Remind about environment-specific settings:

```bash
#!/bin/bash

if [ -f ".env" ]; then
  echo "REMINDER: .env file present - ensure secrets are not committed"
fi

if grep -r "password\|secret\|api_key" . --include="*.py" --exclude-dir=".git" -q; then
  echo "WARNING: Potential hardcoded secrets detected - use Databricks Secrets"
fi
```

### Code Quality Hook

Check for common issues before generating code:

```bash
#!/bin/bash

echo "CODE QUALITY REMINDERS:"
echo "- No hardcoded credentials"
echo "- Use explicit schemas for PySpark"
echo "- Add docstrings to functions"
echo "- Include type hints for Python functions"

# Check if tests exist
if [ ! -d "tests" ]; then
  echo "- NOTE: No tests/ directory found - consider adding tests"
fi
```

## Best Practices

1. **Keep Hooks Fast** - Hooks run on every prompt, so keep them lightweight (< 100ms)
2. **Fail Gracefully** - If a hook fails, it shouldn't block the user
3. **Be Relevant** - Only include information that helps the AI respond better
4. **Version Control** - Commit hooks to your repository so team members benefit
5. **Document Purpose** - Explain what each hook does and why it exists

## Common Use Cases

### Databricks Project Context
```bash
#!/bin/bash
cat << EOF
DATABRICKS PROJECT CONTEXT:
- Unity Catalog: $(yq -r '.catalog' config.yml)
- Environment: $(yq -r '.environment' config.yml)
- Serverless compute required
- All tables use three-level namespace
- Follow Delta Lake best practices
EOF
```

### Code Style Enforcement
```bash
#!/bin/bash
echo "CODE STYLE REQUIREMENTS:"
echo "- Black formatting for Python"
echo "- Type hints for function signatures"
echo "- Docstrings in Google style"
echo "- Max line length: 100 characters"
```

### Testing Reminders
```bash
#!/bin/bash
if [ "$1" != "" ]; then
  # Check if user is asking to write code
  if echo "$1" | grep -qi "create\|add\|implement\|write"; then
    echo "TESTING REMINDER: Include unit tests with pytest and chispa"
  fi
fi
```

## Debugging Hooks

If your hook isn't working:

1. **Check execution permissions**: `chmod +x .cursor/hooks/*.sh`
2. **Test manually**: Run the hook script directly to see output
3. **Check logs**: Look in Claude Code/Cursor logs for hook errors
4. **Verify configuration**: Ensure hook is properly configured in settings
5. **Check exit code**: Hooks should exit with 0 for success

## Disabling Hooks

Temporarily disable a hook:

```json
{
  "hooks": {
    "userPromptSubmit": {
      "enabled": false
    }
  }
}
```

Or use an environment variable in your script:

```bash
#!/bin/bash
if [ "$DISABLE_HOOKS" = "true" ]; then
  exit 0
fi
# ... rest of hook
```
