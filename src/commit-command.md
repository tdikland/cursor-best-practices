# Commit Command

The `/commit` command standardizes the git commit workflow, ensuring consistent commit messages and proper staging practices.

## What Is the Commit Command?

The commit command is a custom Cursor/Claude Code command that automates the commit process following project conventions. Type `/commit` to:
- Review changes automatically
- Stage files appropriately
- Generate conventional commit messages
- Add Co-Authored-By attribution
- Avoid common commit mistakes

## Command File

The commit command is defined in `.cursor/commands/commit.md`:

```markdown
---
description: When the user asks to commit modifications, stage and commit with an appropriate message
alwaysApply: true
---

# Commit modifications

When the user asks to commit modifications, commit changes, or similar:

1. Run `git status` to see what is modified.
2. Review changes with `git diff --cached` (if staged) or `git diff` (if unstaged)
3. Stage changes:
   - Use `git add <specific-files>` for targeted staging
   - Avoid `git add -A` or `git add .` unless user explicitly requests
4. Generate commit message:
   - Follow conventional commits format: `type(scope): description`
   - Types: feat, fix, docs, style, refactor, test, chore
   - Focus on "why" not "what"
   - Keep under 72 characters
5. Commit with Co-Authored-By line:
   ```
   Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
   ```
6. Use heredoc format for multi-line messages:
   ```bash
   git commit -m "$(cat <<'EOF'
   feat: add new feature

   Detailed description if needed.

   Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
   EOF
   )"
   ```

Do not run `git push` unless the user explicitly asks to push.

## Rules

- Never commit files with hardcoded secrets
- Always review changes before committing
- Use specific file paths when staging (not git add -A)
- Check for merge conflicts before committing
- Verify tests pass before committing (if applicable)
- Never use --no-verify to skip git hooks
```

## Usage Examples

### Basic Commit

```
User: /commit
```

The AI will:
1. Run `git status` to see modified files
2. Review changes with `git diff`
3. Stage appropriate files
4. Generate a descriptive commit message
5. Commit with Co-Authored-By line

### Commit with Custom Message

```
User: /commit -m "fix: resolve authentication bug"
```

The AI uses your message but still adds Co-Authored-By attribution.

### Commit Specific Files

```
User: /commit src/main.py src/utils.py
```

The AI stages only the specified files and commits them.

## Conventional Commits Format

The commit command follows [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Common Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks
- **perf**: Performance improvements
- **ci**: CI/CD changes

### Examples

```bash
feat: add user authentication
fix(api): resolve timeout error
docs: update installation guide
refactor(db): optimize query performance
test: add unit tests for auth module
chore: update dependencies
```

## Best Practices

### 1. Review Before Committing

The command automatically runs `git status` and `git diff` so you can review changes before committing.

### 2. Stage Specific Files

Avoid blanket `git add -A`. The command intelligently stages relevant files based on context.

### 3. Meaningful Messages

Commit messages should:
- Be concise but descriptive
- Focus on "why" not "what"
- Use imperative mood ("add" not "added")
- Reference issues when applicable

**Good:**
```
feat: add password reset functionality for locked accounts
fix: prevent race condition in concurrent order processing
```

**Bad:**
```
updated files
fixed bug
changes
```

### 4. Atomic Commits

Each commit should represent a single logical change. The command helps by allowing specific file staging.

### 5. Co-Authored-By Attribution

Always include Co-Authored-By line when AI assists with code:

```
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

## Advanced Usage

### Multi-line Commit Messages

For detailed commits:

```bash
git commit -m "$(cat <<'EOF'
feat(api): add rate limiting middleware

Implement token bucket algorithm for API rate limiting.
Configurable limits per user tier with Redis backend.

Closes #123

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

### Interactive Staging

For partial file staging:

```
User: /commit - stage only the authentication changes from auth.py
```

The AI can guide interactive staging or create targeted commits.

### Amending Commits

```
User: amend the last commit to include the test file
```

The command can help amend commits when needed (with appropriate warnings).

## Commit Validation

The command includes checks for:

### Security
- Hardcoded secrets (passwords, API keys, tokens)
- Sensitive file patterns (.env, credentials.json)

### Quality
- Large files (> 5MB)
- Merge conflict markers
- Debug statements (console.log, debugger, print statements)

### PySpark-Specific
- RDD operations (serverless incompatibility)
- Two-level namespace (should be three-level)
- Missing explicit schemas

## Integration with Git Hooks

The commit command works with git hooks:

- **pre-commit hooks**: Run before commit is created
- **commit-msg hooks**: Validate commit message format
- **prepare-commit-msg**: Modify commit message template

The command respects hooks and will fail if hooks reject the commit.

## Troubleshooting

### Commit Rejected by Hook

If a pre-commit hook fails:

1. Review the hook error message
2. Fix the issue (linting, tests, etc.)
3. Re-run `/commit`

Never use `--no-verify` to bypass hooks.

### Merge Conflicts

If merge conflicts exist:

1. The command will detect them
2. Resolve conflicts manually
3. Stage resolved files
4. Run `/commit`

### Nothing to Commit

If no changes are staged:

```
User: /commit
AI: No changes to commit. Modified files: [list]
```

Stage files or make changes before committing.

## Comparison with Manual Commits

### Without /commit Command

```bash
git status                    # Manual check
git diff                      # Manual review
git add file1.py file2.py    # Manual staging
git commit -m "update code"  # Generic message, no attribution
```

### With /commit Command

```
User: /commit
```

AI automatically:
- Reviews status and changes
- Stages appropriate files
- Generates descriptive message
- Adds Co-Authored-By line
- Follows project conventions

## Customizing the Command

Edit `.cursor/commands/commit.md` to customize:

### Add Project-Specific Checks

```markdown
Before committing:
- Ensure all PySpark code uses three-level namespace
- Verify no hardcoded secrets
- Check that tests pass
- Validate serverless compatibility
```

### Change Commit Message Format

```markdown
Commit message format:
[TICKET-123] type: description

Example: [PROJ-456] feat: add authentication
```

### Add Automatic Testing

```markdown
Before committing:
1. Run tests: pytest tests/ -v
2. Only commit if tests pass
3. Include test results in commit message footer
```

## Example Workflow

```
User: /commit

AI: Let me review your changes...
    [Runs git status and git diff]

    Modified files:
    - src/pipeline.py (added Delta Lake optimization)
    - src/schema.py (updated schema with new fields)
    - tests/test_pipeline.py (added tests for optimization)

    I'll commit these changes:

    [Stages files with git add]

    Commit message:
    "feat(pipeline): add Delta Lake optimization with ZORDER

    Implement OPTIMIZE and ZORDER BY for frequently queried columns.
    Reduces query time by ~40% for filtered queries.

    Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

    [Commits with generated message]

    Committed successfully: a1b2c3d

User: great, now push it

AI: [Runs git push origin main]
    Pushed to origin/main successfully!
```

## Tips

1. **Review commits**: Always check `git log` after committing to verify message
2. **Commit often**: Small, atomic commits are better than large ones
3. **Use branches**: Create feature branches before making changes
4. **Test first**: Run tests before committing (or include in pre-commit hook)
5. **Sign commits**: Consider GPG signing for additional security

## Related Commands

- `/push` - Push commits to remote
- `/pr` - Create pull request
- `/review` - Review changes before committing
- `/test` - Run tests before committing
