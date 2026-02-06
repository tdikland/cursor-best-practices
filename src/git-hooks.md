# Git Hooks

Git hooks automate checks and actions in your git workflow. Useful for enforcing code quality and preventing common mistakes.

## Common Git Hooks

### Pre-commit Hook

Runs before a commit is created. Use to enforce code quality.

**Location**: `.git/hooks/pre-commit`

```bash
#!/bin/bash

echo "Running pre-commit checks..."

# Check for hardcoded secrets
if git diff --cached --name-only | xargs grep -E "password|secret|api_key" 2>/dev/null; then
    echo "ERROR: Potential secrets found in staged files"
    echo "Please remove hardcoded credentials"
    exit 1
fi

# Check Python files with ruff
if git diff --cached --name-only | grep "\.py$"; then
    echo "Checking Python files with ruff..."
    git diff --cached --name-only | grep "\.py$" | xargs ruff check
    if [ $? -ne 0 ]; then
        echo "ERROR: Ruff checks failed"
        exit 1
    fi
fi

# Check for debug statements
if git diff --cached | grep -E "console\.log|debugger|print\(.*DEBUG"; then
    echo "WARNING: Debug statements found in commit"
    echo "Consider removing them before committing"
    # Just warn, don't fail
fi

echo "Pre-commit checks passed!"
```

### Pre-push Hook

Runs before pushing to remote. Use to ensure code quality before sharing.

**Location**: `.git/hooks/pre-push`

```bash
#!/bin/bash

echo "Running pre-push checks..."

# Run tests
if [ -d "tests" ]; then
    echo "Running tests..."
    pytest tests/ -v
    if [ $? -ne 0 ]; then
        echo "ERROR: Tests failed"
        echo "Fix tests before pushing"
        exit 1
    fi
fi

# Check for large files
large_files=$(git diff --stat origin/main | awk '{if ($3 > 5000000) print $1}')
if [ -n "$large_files" ]; then
    echo "WARNING: Large files detected:"
    echo "$large_files"
    echo "Consider using Git LFS"
    read -p "Continue pushing? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "Pre-push checks passed!"
```

### Commit-msg Hook

Validates commit message format.

**Location**: `.git/hooks/commit-msg`

```bash
#!/bin/bash

commit_msg_file=$1
commit_msg=$(cat "$commit_msg_file")

# Check commit message format (conventional commits)
if ! echo "$commit_msg" | grep -qE "^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+"; then
    echo "ERROR: Commit message must follow conventional commits format"
    echo "Examples:"
    echo "  feat: add new feature"
    echo "  fix(auth): resolve login bug"
    echo "  docs: update README"
    exit 1
fi

# Check message length
first_line=$(echo "$commit_msg" | head -n1)
if [ ${#first_line} -gt 72 ]; then
    echo "ERROR: Commit message first line too long (max 72 chars)"
    exit 1
fi

echo "Commit message valid!"
```

## Installing Git Hooks

### Manual Installation

```bash
# Create hooks directory if it doesn't exist
mkdir -p .git/hooks

# Create hook file
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
echo "Running pre-commit hook..."
# Your hook code here
EOF

# Make executable
chmod +x .git/hooks/pre-commit
```

### Using Husky (Node.js projects)

```bash
npm install --save-dev husky
npx husky init

# Create pre-commit hook
echo "npm test" > .husky/pre-commit
```

### Using pre-commit Framework (Python)

**`.pre-commit-config.yaml`**:
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: detect-private-key

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

Install:
```bash
pip install pre-commit
pre-commit install
```

## Databricks-Specific Git Hooks

### Check Unity Catalog Namespace

Ensure all table references use three-level namespace:

```bash
#!/bin/bash

# Check Python files for two-level namespace
if git diff --cached --name-only | grep "\.py$"; then
    # Look for spark.table("schema.table") pattern
    if git diff --cached | grep -E 'spark\.table\(["\'][^.]+\.[^.]+["\']\)'; then
        echo "ERROR: Two-level namespace detected"
        echo "Use three-level namespace: catalog.schema.table"
        exit 1
    fi
fi
```

### Validate PySpark for Serverless

```bash
#!/bin/bash

# Check for serverless-incompatible patterns
if git diff --cached --name-only | grep "\.py$"; then
    echo "Checking PySpark serverless compatibility..."

    # Check for RDD operations
    if git diff --cached | grep -E '\.rdd\.|\.map\(|\.flatMap\(|\.reduceByKey\('; then
        echo "ERROR: RDD operations not compatible with serverless"
        echo "Use DataFrame API instead"
        exit 1
    fi

    # Check for SparkContext access
    if git diff --cached | grep -E 'spark\.sparkContext|sc\.broadcast'; then
        echo "ERROR: Direct SparkContext access not compatible with serverless"
        exit 1
    fi

    echo "Serverless compatibility check passed!"
fi
```

### Prevent Hardcoded Credentials

```bash
#!/bin/bash

echo "Checking for hardcoded credentials..."

# List of patterns to check
patterns=(
    "password\s*=\s*['\"]"
    "api_key\s*=\s*['\"]"
    "secret\s*=\s*['\"]"
    "token\s*=\s*['\"]"
    "aws_access_key"
    "aws_secret_key"
)

found_secrets=false

for pattern in "${patterns[@]}"; do
    if git diff --cached | grep -iE "$pattern"; then
        echo "ERROR: Potential hardcoded credential found: $pattern"
        found_secrets=true
    fi
done

if [ "$found_secrets" = true ]; then
    echo ""
    echo "Use Databricks Secrets instead:"
    echo "  dbutils.secrets.get(scope='my-scope', key='my-key')"
    exit 1
fi

echo "No hardcoded credentials found!"
```

## Bypassing Hooks

Sometimes you need to bypass hooks (use sparingly):

```bash
# Skip pre-commit hooks
git commit --no-verify -m "Emergency fix"

# Skip pre-push hooks
git push --no-verify
```

## Best Practices

1. **Keep Hooks Fast** - Developers will skip slow hooks
2. **Provide Clear Messages** - Explain what failed and how to fix it
3. **Make Them Skippable** - Allow --no-verify for emergencies
4. **Test Your Hooks** - Run them manually to verify they work
5. **Share With Team** - Commit hook scripts (not .git/hooks) to repo
6. **Document Hooks** - Explain what each hook does and why

## Troubleshooting

### Hook Not Running

```bash
# Check if hook exists and is executable
ls -l .git/hooks/pre-commit

# Make executable
chmod +x .git/hooks/pre-commit

# Check for errors
bash -x .git/hooks/pre-commit
```

### Hook Always Fails

```bash
# Test hook manually
.git/hooks/pre-commit

# Check exit code
echo $?  # Should be 0 for success
```

### Hook Skipped in IDE

Some IDEs bypass git hooks. Configure your IDE to use git CLI for commits.
