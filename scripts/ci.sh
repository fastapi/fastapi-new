#!/usr/bin/env bash
# CI script - runs all checks (lint, format, test)

set -e

echo "🔍 Running CI checks..."
echo ""

echo "1️⃣  Running linters..."
./scripts/lint.sh
echo ""

echo "2️⃣  Running tests with coverage..."
./scripts/test.sh
echo ""

echo "3️⃣  Generating coverage report..."
./scripts/coverage.sh
echo ""

echo "✅ All CI checks passed!"
