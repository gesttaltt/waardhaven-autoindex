#!/bin/bash
# Setup pre-commit hooks for the waardhaven-autoindex project

echo "Setting up pre-commit hooks..."

# Navigate to project root
cd "$(dirname "$0")/../../.."

# Install pre-commit (if not already installed)
if command -v pre-commit >/dev/null 2>&1; then
    echo "✓ pre-commit is already installed"
else
    echo "Installing pre-commit..."
    pip install pre-commit
fi

# Install the pre-commit hooks
echo "Installing pre-commit hooks..."
pre-commit install

# Run pre-commit on all files to ensure everything is working
echo "Running pre-commit on all files..."
pre-commit run --all-files

echo "✓ Pre-commit hooks setup complete!"
echo ""
echo "Usage:"
echo "  Run manually: pre-commit run --all-files"
echo "  Auto-format Python: cd apps/api && black ."
echo "  Auto-format Frontend: cd apps/web && npm run format"