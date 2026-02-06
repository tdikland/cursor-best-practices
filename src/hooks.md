# Hooks

Hooks are automated scripts that run at specific points in your development workflow. They help enforce standards, prevent mistakes, and automate repetitive tasks.

## Types of Hooks

### User Prompt Submit Hooks
Run automatically when you submit a prompt to the AI assistant. Useful for adding project context and enforcing standards.

**Use cases:**
- Add project-specific context automatically
- Remind about coding standards
- Inject current environment information
- Provide dynamic project state

### Git Hooks
Execute at specific points in your git workflow (before commit, before push, etc.).

**Use cases:**
- Validate code quality before commits
- Run tests before pushing
- Enforce commit message formats
- Prevent hardcoded secrets
- Check for serverless compatibility

### Tool Hooks
Intercept specific tool calls (Bash, Edit, Write, etc.) to validate or enhance operations.

**Use cases:**
- Validate bash commands before execution
- Check file edits for common issues
- Enforce file naming conventions
- Log operations for audit
- Add safety checks for destructive operations

### Custom Commands
Project-specific slash commands that provide quick access to common workflows.

**Use cases:**
- Standardize commit process
- Automate testing workflows
- Simplify deployment
- Generate boilerplate code
- Run project-specific validations

## Benefits of Using Hooks

1. **Consistency** - Ensure team follows same standards
2. **Prevention** - Catch issues before they become problems
3. **Automation** - Reduce manual, repetitive tasks
4. **Context** - Provide AI with project-specific information
5. **Safety** - Prevent destructive operations
6. **Quality** - Enforce code quality standards

## Getting Started

1. Choose the hook type that fits your need
2. Create hook scripts in appropriate directory
3. Configure hooks in your project settings
4. Test hooks with various scenarios
5. Document hooks for team members

## Best Practices

- **Keep Hooks Fast** - Slow hooks frustrate developers
- **Fail Gracefully** - Provide clear error messages
- **Make Them Optional** - Allow bypass for emergencies
- **Version Control** - Commit hooks to share with team
- **Document Purpose** - Explain what each hook does
- **Test Thoroughly** - Verify hooks work in all scenarios

