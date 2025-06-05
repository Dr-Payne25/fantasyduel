#!/bin/bash
set -e

echo "🚀 Setting up FantasyDuel development environment..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print success
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check Python
echo "Checking Python installation..."
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    print_success "Python $PYTHON_VERSION found"
else
    print_error "Python 3 not found. Please install Python 3.9 or higher"
    exit 1
fi

# Check Node.js
echo "Checking Node.js installation..."
if command_exists node; then
    NODE_VERSION=$(node --version)
    print_success "Node.js $NODE_VERSION found"
else
    print_error "Node.js not found. Please install Node.js 16 or higher"
    exit 1
fi

# Check npm
echo "Checking npm installation..."
if command_exists npm; then
    NPM_VERSION=$(npm --version)
    print_success "npm $NPM_VERSION found"
else
    print_error "npm not found. Please install npm"
    exit 1
fi

# Check pre-commit
echo "Checking pre-commit installation..."
if ! command_exists pre-commit; then
    print_warning "pre-commit not found. Installing..."
    if command_exists brew; then
        brew install pre-commit
    elif command_exists pip3; then
        pip3 install pre-commit
    else
        print_error "Cannot install pre-commit. Please install manually"
        exit 1
    fi
fi

# Create virtual environment for backend
echo "Setting up Python virtual environment..."
cd backend
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    print_success "Virtual environment created"
else
    print_success "Virtual environment already exists"
fi

# Activate virtual environment
source .venv/bin/activate

# Install backend dependencies
echo "Installing backend dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install black flake8 pytest pytest-cov isort bandit
print_success "Backend dependencies installed"

# Go back to root
cd ..

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd frontend
npm install
print_success "Frontend dependencies installed"

# Go back to root
cd ..

# Install pre-commit hooks
echo "Installing pre-commit hooks..."
pre-commit install
pre-commit install --hook-type commit-msg
print_success "Pre-commit hooks installed"

# Update pre-commit hooks
echo "Updating pre-commit hooks..."
pre-commit autoupdate
print_success "Pre-commit hooks updated"

# Run initial checks
echo "Running initial checks..."
pre-commit run --all-files || true

# Database setup
echo "Setting up database..."
cd backend
if [ ! -f "fantasyduel.db" ]; then
    alembic upgrade head
    print_success "Database created and migrations applied"
else
    print_success "Database already exists"
fi
cd ..

# Create .env file if it doesn't exist
if [ ! -f "backend/.env" ]; then
    echo "Creating .env file..."
    cat > backend/.env << EOF
# Environment configuration
DATABASE_URL=sqlite:///./fantasyduel.db
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Sleeper API (no key needed for public endpoints)
SLEEPER_BASE_URL=https://api.sleeper.app/v1

# Development settings
DEBUG=True
RELOAD=True
EOF
    print_success ".env file created (remember to update SECRET_KEY!)"
else
    print_success ".env file already exists"
fi

echo ""
print_success "Development environment setup complete!"
echo ""
echo "📝 Next steps:"
echo "  1. Activate the Python virtual environment:"
echo "     cd backend && source .venv/bin/activate"
echo "  2. Start the backend server:"
echo "     make dev-backend"
echo "  3. In another terminal, start the frontend:"
echo "     make dev-frontend"
echo "  4. Run all checks before committing:"
echo "     make check-all"
echo ""
echo "📚 Useful commands:"
echo "  make help        - Show all available commands"
echo "  make test        - Run all tests"
echo "  make format      - Format all code"
echo "  make lint        - Run all linters"
echo ""
print_success "Happy coding! 🎉"