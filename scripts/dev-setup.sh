#!/usr/bin/env bash
# Development setup script - sets up the development environment

set -e

echo "🔧 Setting up development environment..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -e ".[dev]"

# Install pre-commit hooks if available
if [ -f ".pre-commit-config.yaml" ]; then
    echo "Installing pre-commit hooks..."
    pip install pre-commit
    pre-commit install
fi

echo ""
echo "✅ Development environment ready!"
echo ""
echo "Next steps:"
echo "  source .venv/bin/activate  # Activate the virtual environment"
echo "  ./scripts/test.sh          # Run tests with coverage"
echo "  ./scripts/lint.sh          # Run linters"
echo "  ./scripts/format.sh        # Format code"
