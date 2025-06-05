# FantasyDuel Development Makefile
.PHONY: help install install-backend install-frontend install-hooks format format-backend format-frontend lint lint-backend lint-frontend test test-backend test-frontend build check-all clean dev-backend dev-frontend dev

# Default target
help:
	@echo "FantasyDuel Development Commands:"
	@echo "  make install        - Install all dependencies"
	@echo "  make format         - Format all code"
	@echo "  make lint           - Run all linters"
	@echo "  make test           - Run all tests"
	@echo "  make build          - Build frontend"
	@echo "  make check-all      - Run all checks (format, lint, test, build)"
	@echo "  make dev            - Start development servers"
	@echo "  make clean          - Clean generated files"

# Installation targets
install: install-backend install-frontend install-hooks
	@echo "✅ All dependencies installed"

install-backend:
	@echo "📦 Installing backend dependencies..."
	@cd backend && pip install -r requirements.txt
	@cd backend && pip install black flake8 pytest pytest-cov

install-frontend:
	@echo "📦 Installing frontend dependencies..."
	@cd frontend && npm install

install-hooks:
	@echo "🪝 Installing pre-commit hooks..."
	@pre-commit install
	@echo "✅ Pre-commit hooks installed"

# Formatting targets
format: format-backend format-frontend
	@echo "✅ All code formatted"

format-backend:
	@echo "🎨 Formatting Python code..."
	@cd backend && black .

format-frontend:
	@echo "🎨 Formatting TypeScript/JavaScript code..."
	@cd frontend && npm run lint -- --fix

# Linting targets
lint: lint-backend lint-frontend
	@echo "✅ All linting passed"

lint-backend:
	@echo "🔍 Linting Python code..."
	@cd backend && flake8 .

lint-frontend:
	@echo "🔍 Linting TypeScript/JavaScript code..."
	@cd frontend && npm run lint

# Testing targets
test: test-backend test-frontend
	@echo "✅ All tests passed"

test-backend:
	@echo "🧪 Running backend tests..."
	@cd backend && pytest -v

test-frontend:
	@echo "🧪 Running frontend tests..."
	@cd frontend && npm test -- --watchAll=false

# Build target
build:
	@echo "🏗️ Building frontend..."
	@cd frontend && npm run build
	@echo "✅ Build successful"

# Run all checks
check-all:
	@echo "🚀 Running all checks..."
	@echo "1️⃣ Running pre-commit hooks..."
	@pre-commit run --all-files
	@echo "2️⃣ Running backend tests..."
	@cd backend && pytest -v
	@echo "3️⃣ Running frontend tests..."
	@cd frontend && npm test -- --watchAll=false
	@echo "4️⃣ Building frontend..."
	@cd frontend && npm run build
	@echo "✅ All checks passed!"

# Development servers
dev-backend:
	@echo "🚀 Starting backend server..."
	@cd backend && python main.py

dev-frontend:
	@echo "🚀 Starting frontend server..."
	@cd frontend && npm start

dev:
	@echo "🚀 Starting all development servers..."
	@echo "Run 'make dev-backend' in one terminal and 'make dev-frontend' in another"

# Clean targets
clean:
	@echo "🧹 Cleaning generated files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@rm -rf backend/.pytest_cache
	@rm -rf backend/htmlcov
	@rm -rf backend/.coverage
	@rm -rf frontend/build
	@rm -rf frontend/coverage
	@echo "✅ Clean complete"

# Database targets
db-upgrade:
	@echo "📊 Running database migrations..."
	@cd backend && alembic upgrade head

db-downgrade:
	@echo "📊 Reverting last migration..."
	@cd backend && alembic downgrade -1

db-reset:
	@echo "📊 Resetting database..."
	@rm -f backend/fantasyduel.db
	@cd backend && alembic upgrade head
	@echo "✅ Database reset complete"

# Quick commit with checks
commit:
	@echo "📝 Running checks before commit..."
	@make format
	@make lint
	@make test
	@echo "✅ All checks passed! Ready to commit."

# Git helpers
pull-latest:
	@echo "📥 Pulling latest changes..."
	@git checkout main
	@git pull origin main
	@git checkout -
	@git rebase main

# Setup new feature branch
feature:
	@if [ -z "$(name)" ]; then \
		echo "❌ Please provide a feature name: make feature name=my-feature"; \
		exit 1; \
	fi
	@git checkout main
	@git pull origin main
	@git checkout -b feature/$(name)
	@echo "✅ Created feature branch: feature/$(name)"