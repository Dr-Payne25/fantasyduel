# Quick Reference - FantasyDuel Development

## 🚀 Most Used Commands

### Starting Development
```bash
# First time setup
./scripts/setup-dev.sh

# Start everything
make dev-backend  # Terminal 1
make dev-frontend # Terminal 2

# Or use tmux/screen to run both
```

### Before Committing
```bash
# Run all checks
make check-all

# Or individually
make format      # Format code
make lint        # Check linting
make test        # Run tests
make build       # Build frontend
```

### Quick Fixes
```bash
# Fix Python formatting
cd backend && black .

# Fix TypeScript/React linting
cd frontend && npm run lint:fix

# Fix all with Make
make format
```

## 📝 Git Workflow

### Starting New Feature
```bash
# Create feature branch
make feature name=my-cool-feature

# Or manually
git checkout main
git pull origin main
git checkout -b feature/my-cool-feature
```

### Committing
```bash
# Stage changes
git add .

# Commit (pre-commit runs automatically)
git commit -m "feat(auth): add password reset"

# If pre-commit fails
# 1. Fix the issues
# 2. Stage fixes: git add .
# 3. Try commit again
```

### Common Commit Types
- `feat`: New feature
- `fix`: Bug fix  
- `docs`: Documentation
- `test`: Tests only
- `refactor`: Code restructuring
- `style`: Formatting only
- `chore`: Maintenance

## 🔍 Testing

### Backend Tests
```bash
# All tests
cd backend && pytest

# Specific test file
pytest tests/test_auth.py

# Specific test
pytest tests/test_auth.py::TestAuthEndpoints::test_login -v

# With coverage
pytest --cov=app --cov-report=html
```

### Frontend Tests
```bash
# All tests
cd frontend && npm test -- --watchAll=false

# Watch mode (interactive)
npm test

# With coverage
npm run test:coverage

# Specific file
npm test -- Auth.test.tsx
```

## 🐛 Common Issues & Fixes

### "Import not found" in Python
```bash
# Make sure you're in virtual environment
cd backend && source .venv/bin/activate
```

### ESLint errors
```bash
# Auto-fix most issues
cd frontend && npm run lint:fix
```

### Pre-commit failing
```bash
# Update hooks
pre-commit autoupdate

# Run manually
pre-commit run --all-files

# Skip in emergency (NOT recommended)
git commit -m "message" --no-verify
```

### Database issues
```bash
# Reset database
make db-reset

# Run migrations
cd backend && alembic upgrade head
```

## 🏃‍♂️ Quick Scripts

Add to your `.bashrc` or `.zshrc`:
```bash
# Quick navigation
alias fd='cd ~/code/fantasyduel'
alias fdb='cd ~/code/fantasyduel/backend'
alias fdf='cd ~/code/fantasyduel/frontend'

# Quick commands  
alias fdcheck='cd ~/code/fantasyduel && make check-all'
alias fdtest='cd ~/code/fantasyduel && make test'

# Activate backend venv
alias fdvenv='cd ~/code/fantasyduel/backend && source .venv/bin/activate'
```

## 📞 Getting Help

1. Check error message carefully
2. Run `make help` for available commands
3. Check `DEVELOPMENT_PIPELINE.md` for detailed guide
4. Search codebase for similar patterns
5. Check CI logs if pipeline fails

## 🎯 Daily Workflow

1. **Morning**
   ```bash
   git checkout main
   git pull origin main
   make feature name=todays-work
   ```

2. **Before Each Commit**
   ```bash
   make format
   make test
   git add .
   git commit -m "feat: description"
   ```

3. **End of Day**
   ```bash
   make check-all
   git push origin feature/todays-work
   # Create PR on GitHub
   ```

## 🔥 Hot Keys (VS Code)

- `Cmd+Shift+P` → "Python: Select Interpreter" (choose .venv)
- `Cmd+Shift+F` → Search across project
- `Cmd+P` → Quick file open
- `F12` → Go to definition
- `Shift+F12` → Find all references
- `Cmd+.` → Quick fix (auto-import, etc)