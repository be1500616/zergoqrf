#!/bin/bash

# ZERGO QR Frontend Test Coverage Script
# Generates comprehensive test coverage reports

set -e

echo "🧪 Running Flutter tests with coverage..."

# Clean previous coverage data
rm -rf coverage/

# Run tests with coverage
flutter test --coverage --test-randomize-ordering-seed random

# Check if coverage was generated
if [ ! -f "coverage/lcov.info" ]; then
    echo "❌ Coverage file not generated!"
    exit 1
fi

echo "✅ Coverage data generated successfully"

# Filter out generated files and test files from coverage
echo "🔧 Filtering coverage data..."
lcov --remove coverage/lcov.info \
    '*/test/*' \
    '*/integration_test/*' \
    '*/.dart_tool/*' \
    '*/lib/generated/*' \
    '*/lib/*.g.dart' \
    -o coverage/lcov_filtered.info

# Generate HTML report if lcov is available
if command -v genhtml &> /dev/null; then
    echo "📊 Generating HTML coverage report..."
    genhtml coverage/lcov_filtered.info -o coverage/html \
        --remove-function-coverage \
        --show-details \
        --title "ZERGO QR Frontend Coverage" \
        --num-spaces 4
    
    echo "✅ HTML coverage report generated: coverage/html/index.html"
else
    echo "⚠️  genhtml not found. Install lcov to generate HTML reports."
    echo "   On macOS: brew install lcov"
    echo "   On Ubuntu: sudo apt install lcov"
fi

# Calculate coverage percentage
if command -v lcov &> /dev/null; then
    COVERAGE=$(lcov --summary coverage/lcov_filtered.info 2>&1 | grep "lines" | grep -oE "[0-9]+\.[0-9]+%")
    echo "📈 Coverage: $COVERAGE"
    
    # Extract numeric value for comparison
    COVERAGE_NUM=$(echo $COVERAGE | grep -oE "[0-9]+\.[0-9]+")
    THRESHOLD=80.0
    
    if (( $(echo "$COVERAGE_NUM >= $THRESHOLD" | bc -l) )); then
        echo "✅ Coverage meets threshold ($THRESHOLD%)"
    else
        echo "❌ Coverage below threshold ($THRESHOLD%). Current: $COVERAGE_NUM%"
        exit 1
    fi
fi

echo "🎉 Test coverage analysis complete!"
