# Custom Commands

Custom commands (slash commands) extend Claude Code and Cursor with project-specific functionality accessible via `/command-name`.

## What Are Custom Commands?

Custom commands are reusable workflows triggered by typing `/` followed by the command name. They're useful for:
- Standardizing common tasks
- Automating repetitive workflows
- Enforcing project conventions
- Providing quick access to project-specific actions

## Creating Custom Commands

### Command Structure

Create a `.cursor/commands/` or `.claude/skills/` directory with markdown files:

```
.cursor/commands/
├── commit.md
├── test.md
└── deploy.md
```

### Basic Command Format

**`.cursor/commands/example.md`**
```markdown
---
name: example
description: Short description of what this command does
---

# Example Command

Instructions for the AI assistant on what to do when this command is invoked.

## Steps

1. First do this
2. Then do that
3. Finally do this

## Rules

- Always follow this rule
- Never do this thing
- Consider this edge case
```

## Common Custom Commands

### Commit Command

**`.cursor/commands/commit.md`**
```markdown
---
name: commit
description: Create a well-formatted git commit with Co-Authored-By line
---

# Commit Command

Create a git commit following project conventions.

## Steps

1. Check git status to see staged files
2. Review the changes with git diff --cached
3. Generate a descriptive commit message that:
   - Summarizes the changes in imperative mood
   - Focuses on "why" not "what"
   - Is concise (1-2 sentences)
   - Follows conventional commits format if applicable
4. Add Co-Authored-By line:
   ```
   Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
   ```
5. Execute the commit
6. Show git log to confirm

## Rules

- Never use git add . or git add -A (be specific about files)
- Always review changes before committing
- Never commit files with hardcoded secrets
- Use heredoc format for multi-line commit messages
```

### Test Command

**`.cursor/commands/test.md`**
```markdown
---
name: test
description: Run tests and analyze results
---

# Test Command

Run the project's test suite and provide analysis.

## Steps

1. Identify test framework (pytest, jest, etc.)
2. Run appropriate test command:
   - Python: `pytest tests/ -v`
   - Node: `npm test`
   - Databricks: `pytest tests/ --dbr`
3. Analyze test results
4. If failures occur:
   - Show failed test details
   - Identify likely causes
   - Suggest fixes

## Rules

- Always show test output
- Don't modify tests without explicit request
- Provide clear explanation of failures
- Consider running specific test files if all tests would take too long
```

### Deploy Command

**`.cursor/commands/deploy.md`**
```markdown
---
name: deploy
description: Deploy to Databricks following project conventions
---

# Deploy Command

Deploy code or workflows to Databricks environment.

## Steps

1. Check current git branch
2. Verify environment configuration:
   - Check config.yml for environment settings
   - Verify Databricks profile is set
3. Ask user which environment to deploy to (dev/staging/prod)
4. Validate deployment prerequisites:
   - All tests passing
   - No uncommitted changes (for prod)
   - Correct environment variables set
5. Execute deployment:
   - Use `databricks bundle deploy` if using Asset Bundles
   - Or appropriate deployment method
6. Verify deployment success
7. Provide deployment summary

## Rules

- Never deploy to prod without user confirmation
- Always validate tests pass before deployment
- Check for environment-specific configuration
- Provide rollback instructions if deployment fails
```

### Schema Command

**`.cursor/commands/schema.md`**
```markdown
---
name: schema
description: Generate PySpark schema from sample data or JSON
---

# Schema Command

Generate PySpark StructType schema definition.

## Steps

1. Ask user for input format:
   - Sample JSON data
   - Existing DataFrame
   - CSV with headers
   - Table description
2. Generate StructType schema with:
   - Explicit field types (not all strings)
   - Appropriate nullability
   - Proper nested structures for complex types
3. Provide schema as Python code
4. Suggest usage example

## Rules

- Use proper PySpark types (IntegerType, DateType, etc.)
- Set nullable=False for required fields
- Use StructType for nested objects
- Use ArrayType for repeated elements
- Include from pyspark.sql.types import statement
```

### Optimize Command

**`.cursor/commands/optimize.md`**
```markdown
---
name: optimize
description: Analyze and optimize PySpark code for Databricks
---

# Optimize Command

Analyze PySpark code and suggest optimizations.

## Analysis Areas

1. **Caching**: Check for repeated DataFrame usage
2. **Shuffles**: Identify unnecessary shuffle operations
3. **Partitioning**: Review partition strategy
4. **Joins**: Analyze join patterns (broadcast opportunities)
5. **File Format**: Ensure Delta Lake is used
6. **Schema**: Verify explicit schemas
7. **Serverless Compatibility**: Check for incompatible patterns

## Output

For each optimization opportunity:
1. Identify the issue
2. Explain performance impact
3. Provide optimized code example
4. Estimate potential improvement

## Rules

- Only suggest optimizations that maintain correctness
- Explain trade-offs (e.g., memory vs speed)
- Prioritize by impact (high/medium/low)
- Consider Databricks serverless constraints
```

## Databricks-Specific Commands

### Bundle Deploy Command

**`.cursor/commands/bundle-deploy.md`**
```markdown
---
name: bundle-deploy
description: Deploy Databricks Asset Bundle to specified environment
---

# Bundle Deploy Command

Deploy Databricks Asset Bundle with validation.

## Steps

1. Verify bundle configuration exists (databricks.yml)
2. Check current git status
3. Ask for target environment (dev/staging/prod)
4. Validate bundle:
   ```bash
   databricks bundle validate -e <environment>
   ```
5. Deploy bundle:
   ```bash
   databricks bundle deploy -e <environment>
   ```
6. Show deployment summary
7. Provide links to deployed resources

## Rules

- Require clean git state for prod deployments
- Validate before deploying
- Use --force flag only if user explicitly requests
- Show what will be deployed before executing
```

### DLT Pipeline Command

**`.cursor/commands/dlt-pipeline.md`**
```markdown
---
name: dlt-pipeline
description: Create Delta Live Tables pipeline configuration
---

# DLT Pipeline Command

Generate Delta Live Tables pipeline code and configuration.

## Steps

1. Gather requirements:
   - Source tables/files
   - Transformation logic
   - Target tables
   - Quality expectations
2. Generate DLT notebook code with:
   - @dlt.table decorators
   - @dlt.expect expectations
   - Proper pipeline structure (bronze/silver/gold)
3. Generate pipeline configuration JSON
4. Provide deployment instructions

## Rules

- Use @dlt.expect_or_drop for data quality
- Include schema evolution settings
- Add table comments and properties
- Follow medallion architecture pattern
```

## Best Practices

1. **Clear Names** - Use descriptive command names (not single letters)
2. **Good Descriptions** - Help users know when to use the command
3. **Structured Steps** - Break complex workflows into clear steps
4. **Explicit Rules** - Document constraints and requirements
5. **Error Handling** - Include what to do when things go wrong
6. **Examples** - Provide code examples in the command
7. **Validation** - Check prerequisites before executing
8. **User Input** - Ask for clarification when needed

## Using Custom Commands

In Claude Code or Cursor, type:

```
/commit
/test
/deploy dev
/schema
```

The AI will follow the instructions in the corresponding command file.

## Command Discovery

List available commands:
```
/help
```

Or check the `.cursor/commands/` directory:
```bash
ls -la .cursor/commands/
```

## Debugging Commands

### Test Command Logic

Create a test prompt:
```
Act as if I invoked /commit command. Show me what steps you would take.
```

### Validate Command File

Check markdown syntax:
```bash
# Check if file is valid markdown
python -c "import markdown; markdown.markdownFromFile('`.cursor/commands/commit.md')"
```

### Check Command Registration

Verify commands are loaded:
- Restart Claude Code/Cursor
- Type `/` and see if your command appears in autocomplete
- Check logs for command loading errors
