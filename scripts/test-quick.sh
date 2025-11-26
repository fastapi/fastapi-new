#!/usr/bin/env bash
# Quick test script - runs tests without coverage for faster feedback

set -e

echo "🧪 Running tests..."
python -m pytest tests/ -v --tb=short

echo ""
echo "✅ All tests passed!"
