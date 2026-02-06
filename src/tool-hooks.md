# Tool Hooks

Tool hooks run before or after specific tools are executed, allowing you to enforce rules or add context for specific operations.

## What Are Tool Hooks?

Tool hooks intercept tool calls (like Bash, Edit, Write, etc.) to:
- Validate inputs before execution
- Add safety checks
- Log operations
- Provide warnings or reminders
- Enforce project-specific rules

## Configuration

Configure tool hooks in your Claude Code or Cursor settings.

### Example Configuration

```json
{
  "hooks": {
    "beforeBash": {
      "command": "bash",
      "args": ["-c", ".cursor/hooks/before-bash.sh"]
    },
    "beforeEdit": {
      "command": "python",
      "args": [".cursor/hooks/validate-edit.py"]
    }
  }
}
```

## Common Tool Hook Examples

### Before Bash Hook

Validate bash commands before execution:

**`.cursor/hooks/before-bash.sh`**
```bash
#!/bin/bash

command="$1"

# Prevent destructive operations
if echo "$command" | grep -qE "rm -rf /|sudo rm|:(){ :|:& };:"; then
    echo "ERROR: Destructive command blocked"
    exit 1
fi

# Warn about production commands
if echo "$command" | grep -qE "prod|production" && [ -f ".env" ]; then
    env=$(grep "ENV=" .env | cut -d'=' -f2)
    if [ "$env" != "prod" ]; then
        echo "WARNING: Production command in non-prod environment"
    fi
fi

# Remind about serverless compatibility for databricks commands
if echo "$command" | grep -qE "databricks|spark-submit"; then
    echo "REMINDER: Ensure code is serverless-compatible"
fi

exit 0
```

### Before Edit Hook

Validate edits before they're applied:

**`.cursor/hooks/validate-edit.py`**
```python
#!/usr/bin/env python3
import sys
import json
import re

def validate_edit(file_path, old_string, new_string):
    """Validate edit operation."""

    # Check for hardcoded secrets
    secret_patterns = [
        r'password\s*=\s*["\'][\w]+["\']',
        r'api_key\s*=\s*["\'][\w]+["\']',
        r'secret\s*=\s*["\'][\w]+["\']',
    ]

    for pattern in secret_patterns:
        if re.search(pattern, new_string, re.IGNORECASE):
            print("ERROR: Hardcoded secret detected in edit")
            print("Use environment variables or Databricks Secrets")
            return False

    # Check for PySpark serverless compatibility
    if file_path.endswith('.py') and 'spark' in new_string.lower():
        if '.rdd' in new_string or 'sparkContext' in new_string:
            print("ERROR: RDD operations not serverless-compatible")
            print("Use DataFrame API instead")
            return False

    # Check for two-level namespace in Spark code
    if 'spark.table(' in new_string:
        # Look for spark.table("schema.table") pattern
        if re.search(r'spark\.table\(["\'][^.]+\.[^.]+["\']\)', new_string):
            print("WARNING: Two-level namespace detected")
            print("Consider using three-level: catalog.schema.table")
            # Just warn, don't block

    return True

if __name__ == "__main__":
    # Parse input (format depends on your setup)
    file_path = sys.argv[1] if len(sys.argv) > 1 else ""
    old_string = sys.argv[2] if len(sys.argv) > 2 else ""
    new_string = sys.argv[3] if len(sys.argv) > 3 else ""

    if not validate_edit(file_path, old_string, new_string):
        sys.exit(1)

    sys.exit(0)
```

### Before Write Hook

Validate file writes:

```bash
#!/bin/bash

file_path="$1"
content="$2"

# Check if writing to protected directory
if echo "$file_path" | grep -qE "^/etc/|^/usr/|^/sys/"; then
    echo "ERROR: Cannot write to system directory"
    exit 1
fi

# Warn about large files
size=${#content}
if [ $size -gt 1000000 ]; then
    echo "WARNING: Writing large file ($size bytes)"
    echo "Consider if this should be in version control"
fi

# Check Python files for common issues
if echo "$file_path" | grep -q "\.py$"; then
    # Check for hardcoded secrets
    if echo "$content" | grep -qE "password|secret|api_key"; then
        echo "WARNING: Potential secrets in Python file"
    fi

    # Check for missing shebang in scripts
    if echo "$content" | head -1 | grep -qE "^def |^import "; then
        if ! echo "$content" | head -1 | grep -q "^#!/"; then
            if [ "$file_path" != "*.py" ]; then
                echo "INFO: Consider adding shebang to Python script"
            fi
        fi
    fi
fi

exit 0
```

### After Bash Hook

Log bash commands for audit:

```bash
#!/bin/bash

command="$1"
exit_code="$2"
output="$3"

# Log to audit file
echo "[$(date -Iseconds)] Command: $command" >> .cursor/bash-audit.log
echo "Exit code: $exit_code" >> .cursor/bash-audit.log

# Alert on errors
if [ $exit_code -ne 0 ]; then
    echo "Command failed with exit code $exit_code"
    echo "Command: $command"
fi

exit 0
```

## Databricks-Specific Tool Hooks

### Validate Databricks Commands

```bash
#!/bin/bash

command="$1"

# Check for databricks CLI usage
if echo "$command" | grep -q "databricks"; then
    # Ensure profile is specified
    if ! echo "$command" | grep -qE "--profile|DATABRICKS_CONFIG_PROFILE"; then
        echo "WARNING: No Databricks profile specified"
        echo "Set DATABRICKS_CONFIG_PROFILE or use --profile flag"
    fi

    # Warn about production operations
    if echo "$command" | grep -qE "delete|drop|destroy"; then
        echo "WARNING: Destructive Databricks operation"
        echo "Command: $command"
        read -p "Continue? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

exit 0
```

### Validate Unity Catalog Operations

```python
#!/usr/bin/env python3
import sys
import re

def validate_sql_command(command):
    """Validate SQL command for Unity Catalog compliance."""

    # Check for three-level namespace
    if re.search(r'\b(FROM|JOIN|INTO|TABLE)\s+\w+\.\w+\b', command, re.IGNORECASE):
        if not re.search(r'\b(FROM|JOIN|INTO|TABLE)\s+\w+\.\w+\.\w+\b', command, re.IGNORECASE):
            print("WARNING: Two-level namespace detected")
            print("Use three-level namespace: catalog.schema.table")
            return False

    # Check for DROP operations
    if re.search(r'\bDROP\s+(TABLE|SCHEMA|CATALOG)\b', command, re.IGNORECASE):
        print("WARNING: DROP operation detected")
        print("Ensure this is intentional and you have backups")
        # Allow but warn

    return True

if __name__ == "__main__":
    command = " ".join(sys.argv[1:])

    # Only validate SQL-like commands
    if any(keyword in command.upper() for keyword in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER']):
        if not validate_sql_command(command):
            sys.exit(1)

    sys.exit(0)
```

## Hook Best Practices

1. **Exit Codes Matter**
   - Exit 0 for success (allow operation)
   - Exit non-zero to block operation
   - Use exit codes 1-255 for different error types

2. **Performance**
   - Keep hooks fast (< 100ms)
   - Cache expensive checks
   - Run heavy validation async

3. **User Experience**
   - Provide clear error messages
   - Suggest how to fix issues
   - Allow bypass for emergencies

4. **Testing**
   - Test hooks with various inputs
   - Handle edge cases gracefully
   - Don't crash on unexpected input

5. **Security**
   - Sanitize inputs
   - Don't log sensitive data
   - Validate file paths

## Debugging Tool Hooks

### Test Hook Manually

```bash
# Test before-bash hook
.cursor/hooks/before-bash.sh "ls -la"
echo "Exit code: $?"

# Test with problematic command
.cursor/hooks/before-bash.sh "rm -rf /"
echo "Exit code: $?"
```

### Add Debug Logging

```bash
#!/bin/bash

# Enable debug mode
if [ "$DEBUG_HOOKS" = "true" ]; then
    set -x
    exec 2>> .cursor/hook-debug.log
fi

# Your hook code here
```

### Check Hook Output

```bash
# View hook logs
tail -f .cursor/bash-audit.log

# View debug logs
tail -f .cursor/hook-debug.log
```

## Disabling Tool Hooks

Temporarily disable hooks:

```bash
# Environment variable
export DISABLE_TOOL_HOOKS=true

# Or in configuration
{
  "hooks": {
    "beforeBash": {
      "enabled": false
    }
  }
}
```
