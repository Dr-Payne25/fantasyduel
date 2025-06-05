#!/bin/bash

echo "🔧 Setting up pre-commit hooks..."

# Check if pre-commit is installed
if ! command -v pre-commit &> /dev/null; then
    echo "📦 Installing pre-commit..."
    pip install pre-commit
fi

# Install the git hooks
pre-commit install

echo "✅ Pre-commit hooks installed successfully!"
echo ""
echo "Pre-commit will now run automatically on every commit to:"
echo "  - Format Python code with Black"
echo "  - Lint Python code with flake8"
echo "  - Lint TypeScript/React code with ESLint"
echo "  - Check for trailing whitespace and large files"
echo ""
echo "To run pre-commit manually on all files:"
echo "  pre-commit run --all-files"
