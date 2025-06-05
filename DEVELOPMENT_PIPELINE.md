# Development Pipeline Guide

## Overview
This guide outlines our development pipeline to ensure code quality and prevent CI/CD failures. All checks should pass locally before pushing to remote.

## 🎯 Core Principles
1. **Fail Fast, Fail Local** - Catch issues on developer machines, not in CI
2. **Automate Everything** - If it can be automated, it should be
3. **Consistency** - Same checks locally and in CI/CD
4. **Developer Experience** - Fast feedback loops and clear error messages

## 📋 Pre-Commit Hooks

### Currently Installed
- **Black** - Python code formatting
- **Flake8** - Python linting
- **ESLint** - TypeScript/JavaScript linting
- **Trailing whitespace** - Remove trailing spaces
- **End of file fixer** - Ensure files end with newline
- **YAML checker** - Validate YAML syntax
- **Large file checker** - Prevent accidental large file commits

### Installation
```bash
# Install pre-commit
pip install pre-commit  # or brew install pre-commit

# Install hooks
pre-commit install

# Run on all files (first time setup)
pre-commit run --all-files
```

## 🔧 Local Development Workflow

### 1. Before Starting Work
```bash
# Always start from latest main
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/your-feature-name

# Ensure dependencies are up to date
cd backend && pip install -r requirements.txt
cd ../frontend && npm install
```

### 2. During Development

#### Backend Development
```bash
# Format code
cd backend
black .

# Check linting
flake8 .

# Run tests
pytest -v

# Run specific test
pytest tests/test_auth.py::TestAuthEndpoints::test_login -v

# Check type hints (if using mypy)
mypy app/
```

#### Frontend Development
```bash
# Format code
cd frontend
npm run format  # (we should add this script)

# Check linting
npm run lint

# Fix linting issues automatically
npm run lint -- --fix

# Run tests
npm test -- --watchAll=false

# Build to check for errors
npm run build
```

### 3. Before Committing

#### Run All Checks
```bash
# Pre-commit will run automatically on commit, but you can test first
pre-commit run --all-files

# Or check specific files
pre-commit run --files backend/app/api/auth.py frontend/src/App.tsx
```

#### Manual Checks
```bash
# Backend
cd backend
black --check .
flake8 .
pytest -v

# Frontend
cd frontend
npm run lint
npm test -- --watchAll=false
npm run build
```

### 4. Committing Changes
```bash
# Stage changes
git add .

# Commit (pre-commit hooks will run automatically)
git commit -m "feat: add user authentication"

# If pre-commit fails, fix issues and try again
# To bypass hooks in emergency (NOT RECOMMENDED)
git commit -m "message" --no-verify
```

## 🚀 Continuous Integration Checks

Our CI pipeline runs the following checks:

### Backend (Python)
1. Black formatting check
2. Flake8 linting
3. Pytest with coverage
4. FastAPI import test

### Frontend (React/TypeScript)
1. ESLint
2. Jest tests
3. Production build

## 📝 Commit Message Convention

Follow conventional commits for clear history:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, semicolons, etc)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Build process, dependencies, etc

Examples:
```bash
git commit -m "feat(auth): add JWT refresh token support"
git commit -m "fix(draft): resolve pick order calculation bug"
git commit -m "docs: update API documentation"
git commit -m "test(leagues): add integration tests for league creation"
```

## 🛠️ Useful Scripts

Add these to your shell profile (.bashrc, .zshrc, etc):

```bash
# Run all checks
alias check-all='pre-commit run --all-files && cd backend && pytest && cd ../frontend && npm test -- --watchAll=false'

# Quick format
alias format-py='cd backend && black .'
alias format-js='cd frontend && npm run lint -- --fix'

# Run tests
alias test-back='cd backend && pytest -v'
alias test-front='cd frontend && npm test -- --watchAll=false'
```

## 🔍 Troubleshooting Common Issues

### Black and Flake8 Conflicts
- Ensure flake8 config has `extend-ignore = E203, W503`
- Line length should be 88 for both

### ESLint Errors
```bash
# Auto-fix what's possible
npm run lint -- --fix

# For specific rules, check .eslintrc
```

### Pre-commit Failures
```bash
# Update pre-commit hooks
pre-commit autoupdate

# Clear cache if hooks are misbehaving
pre-commit clean
pre-commit install --install-hooks
```

### Import Errors in Tests
- Ensure `__init__.py` files exist in all packages
- Check PYTHONPATH in test configuration

## 📊 Code Quality Metrics

### Target Metrics
- Python test coverage: >80%
- TypeScript strict mode: enabled
- Zero linting errors
- All tests passing

### Checking Coverage
```bash
# Backend
cd backend
pytest --cov=app --cov-report=html
open htmlcov/index.html

# Frontend
cd frontend
npm test -- --coverage --watchAll=false
```

## 🔄 Pull Request Checklist

Before creating a PR:
- [ ] All pre-commit hooks pass
- [ ] All tests pass
- [ ] Code coverage maintained/improved
- [ ] Documentation updated if needed
- [ ] Commit messages follow convention
- [ ] PR description explains changes
- [ ] Self-review completed

## 🚨 Emergency Procedures

If you need to push urgently:

1. **Create a hotfix branch**
   ```bash
   git checkout -b hotfix/critical-bug
   ```

2. **Document why checks are skipped**
   ```bash
   git commit -m "hotfix: emergency fix for production issue

   Skipping pre-commit due to critical production bug.
   TODO: Fix linting issues in follow-up PR" --no-verify
   ```

3. **Create follow-up issue immediately**

## 📚 Additional Resources

- [Black Documentation](https://black.readthedocs.io/)
- [Flake8 Rules](https://www.flake8rules.com/)
- [ESLint Rules](https://eslint.org/docs/rules/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Pre-commit Documentation](https://pre-commit.com/)