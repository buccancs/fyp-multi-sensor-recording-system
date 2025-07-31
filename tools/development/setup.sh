#!/bin/bash
# Multi-Sensor Recording System - Development Environment Setup
# Linux/macOS equivalent of setup_dev_env.ps1

set -e

echo "=== Multi-Sensor Recording System - Dev Environment Setup ==="
echo "Setting up development environment for Linux/macOS..."

# Check for required tools
echo
echo "1. Checking prerequisites..."

# Check for Java
if ! command -v java &> /dev/null; then
    echo "❌ Java not found. Please install Java 11 or higher."
    exit 1
fi

echo "✓ Java found: $(java -version 2>&1 | head -n 1)"

# Check for conda/miniconda
if ! command -v conda &> /dev/null; then
    echo "❌ Conda not found. Please install Miniconda or Anaconda."
    echo "   Download from: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

echo "✓ Conda found: $(conda --version)"

# Check for Git
if ! command -v git &> /dev/null; then
    echo "❌ Git not found. Please install Git."
    exit 1
fi

echo "✓ Git found: $(git --version)"

# Create conda environment from environment.yml
echo
echo "2. Setting up Python environment..."

if conda env list | grep -q "thermal-env"; then
    echo "📋 Conda environment 'thermal-env' already exists."
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🔄 Removing existing environment..."
        conda env remove -n thermal-env -y
        echo "🔨 Creating new conda environment..."
        conda env create -f environment.yml
    else
        echo "⏭️  Using existing environment."
    fi
else
    echo "🔨 Creating conda environment from environment.yml..."
    conda env create -f environment.yml
fi

echo "✓ Python environment ready"

# Test the setup
echo
echo "3. Testing the setup..."

echo "🧪 Activating environment and testing Python imports..."
eval "$(conda shell.bash hook)"
conda activate thermal-env

# Test key imports
python -c "
import sys
print(f'Python version: {sys.version}')

try:
    import PyQt5
    print('✓ PyQt5 imported successfully')
except ImportError as e:
    print(f'❌ PyQt5 import failed: {e}')
    
try:
    import cv2
    print('✓ OpenCV imported successfully')
except ImportError as e:
    print(f'❌ OpenCV import failed: {e}')
    
try:
    import numpy
    print('✓ NumPy imported successfully')
except ImportError as e:
    print(f'❌ NumPy import failed: {e}')
"

# Test Gradle
echo
echo "🧪 Testing Gradle setup..."
./gradlew tasks --console=plain > /dev/null 2>&1 && echo "✓ Gradle working" || echo "⚠️  Gradle test failed"

echo
echo "=== Setup Complete ==="
echo "To activate the environment: conda activate thermal-env"
echo "To run the application: ./gradlew :PythonApp:runDesktopApp"
echo "To run tests: ./gradlew :PythonApp:runPythonTests"
echo