#!/bin/bash

# Quick Local Test Runner - GSR Virtual Test Environment
# Provides immediate testing capability without configuration

set -e

echo "🚀 GSR Virtual Test Environment - Quick Local Runner"
echo "=================================================="

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VIRTUAL_ENV_DIR="$SCRIPT_DIR/tests/integration/virtual_environment"

# Check if virtual environment exists
if [ ! -d "$VIRTUAL_ENV_DIR" ]; then
    echo "❌ Virtual test environment not found at: $VIRTUAL_ENV_DIR"
    echo "Please ensure you're running this from the project root directory."
    exit 1
fi

# Navigate to virtual environment
cd "$VIRTUAL_ENV_DIR"

echo "📁 Working directory: $VIRTUAL_ENV_DIR"
echo ""

# Check if setup is needed
if [ ! -f "setup_complete.marker" ]; then
    echo "🔧 First-time setup required. Running automated setup..."
    echo ""
    
    if [ -f "setup_dev_environment.sh" ]; then
        ./setup_dev_environment.sh
        echo "✅ Setup completed successfully"
        touch setup_complete.marker
    else
        echo "❌ Setup script not found. Please run manual setup:"
        echo "   cd tests/integration/virtual_environment"
        echo "   pip install pytest pytest-asyncio psutil numpy opencv-python-headless"
        exit 1
    fi
    echo ""
fi

# Run quick test
echo "🧪 Running quick virtual test (2 minutes)..."
echo "   - 2 virtual devices"
echo "   - 1 minute duration" 
echo "   - Quick validation scenario"
echo ""

if [ -f "run_virtual_test.sh" ]; then
    ./run_virtual_test.sh --scenario quick --devices 2 --duration 1.0 --verbose
else
    echo "Running fallback Python test..."
    python quick_test.py
fi

echo ""
echo "✅ Local test completed successfully!"
echo ""
echo "📚 For more options, see:"
echo "   - VIRTUAL_TEST_INTEGRATION_GUIDE.md (comprehensive guide)"
echo "   - TEST_RUNNER_README.md (detailed usage)"
echo "   - tests/integration/virtual_environment/README.md (technical docs)"
echo ""
echo "🚀 To run different scenarios:"
echo "   cd tests/integration/virtual_environment"
echo "   ./run_virtual_test.sh --scenario ci --devices 3      # CI test (3 min)"
echo "   ./run_virtual_test.sh --scenario stress --devices 5  # Stress test (30 min)"
echo "   pytest . -v                                          # Pytest integration"