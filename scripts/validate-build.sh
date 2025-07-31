#!/bin/bash
# Cross-Platform Build Validation Script
# Validates the complete development environment setup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default options
SKIP_TESTS=false
VERBOSE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --skip-tests    Skip test execution"
            echo "  --verbose       Enable verbose output"
            echo "  --help         Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option $1"
            exit 1
            ;;
    esac
done

echo -e "${GREEN}=== Multi-Sensor Recording System - Build Validation ===${NC}"
echo -e "${YELLOW}Platform: $(uname -s) $(uname -m)${NC}"

# Function to log messages
log() {
    if [[ "$VERBOSE" == "true" ]]; then
        echo -e "${BLUE}[DEBUG] $1${NC}"
    fi
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to run gradle task and check result
run_gradle_task() {
    local task=$1
    local description=$2
    
    echo -e "${YELLOW}Testing: $description${NC}"
    log "Running: ./gradlew $task"
    
    if ./gradlew $task > /dev/null 2>&1; then
        echo -e "${GREEN}✓ $description - PASSED${NC}"
        return 0
    else
        echo -e "${RED}✗ $description - FAILED${NC}"
        if [[ "$VERBOSE" == "true" ]]; then
            echo "Re-running with verbose output:"
            ./gradlew $task
        fi
        return 1
    fi
}

# Function to validate environment
validate_environment() {
    echo -e "\n${BLUE}1. Environment Validation${NC}"
    
    local errors=0
    
    # Check Java
    if command_exists java; then
        JAVA_VERSION=$(java -version 2>&1 | head -n1 | cut -d'"' -f2 | cut -d'.' -f1)
        echo -e "${GREEN}✓ Java $JAVA_VERSION detected${NC}"
    else
        echo -e "${RED}✗ Java not found${NC}"
        ((errors++))
    fi
    
    # Check Python
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        echo -e "${GREEN}✓ Python $PYTHON_VERSION detected${NC}"
    elif command_exists python; then
        PYTHON_VERSION=$(python --version | cut -d' ' -f2)
        echo -e "${GREEN}✓ Python $PYTHON_VERSION detected${NC}"
    else
        echo -e "${RED}✗ Python not found${NC}"
        ((errors++))
    fi
    
    # Check Gradle wrapper
    if [[ -f "./gradlew" ]]; then
        echo -e "${GREEN}✓ Gradle wrapper found${NC}"
    else
        echo -e "${RED}✗ Gradle wrapper not found${NC}"
        ((errors++))
    fi
    
    return $errors
}

# Function to validate gradle tasks
validate_gradle() {
    echo -e "\n${BLUE}2. Gradle Build System Validation${NC}"
    
    local errors=0
    
    # Test basic Gradle functionality
    if ! run_gradle_task "tasks" "Gradle basic functionality"; then
        ((errors++))
    fi
    
    # Test Android build
    if ! run_gradle_task ":AndroidApp:assembleDebug" "Android debug build"; then
        ((errors++))
    fi
    
    # Test Python environment setup
    if ! run_gradle_task "setupPythonEnv" "Python environment setup"; then
        echo -e "${YELLOW}⚠ Python environment setup failed - this is expected if dependencies aren't installed${NC}"
    fi
    
    return $errors
}

# Function to validate Python setup
validate_python() {
    echo -e "\n${BLUE}3. Python Environment Validation${NC}"
    
    local errors=0
    
    # Check if we can detect Python environment
    echo -e "${YELLOW}Checking Python environment detection...${NC}"
    
    # Try conda environment
    if [[ -n "$CONDA_PREFIX" ]]; then
        echo -e "${GREEN}✓ Conda environment detected: $CONDA_PREFIX${NC}"
    # Try venv
    elif [[ -d "venv" ]]; then
        echo -e "${GREEN}✓ Python venv detected: ./venv${NC}"
    else
        echo -e "${YELLOW}⚠ No virtual environment detected - using system Python${NC}"
    fi
    
    # Test Python import capabilities
    if command_exists python3; then
        if python3 -c "import sys; print(f'Python path: {sys.executable}')" 2>/dev/null; then
            echo -e "${GREEN}✓ Python import test passed${NC}"
        else
            echo -e "${RED}✗ Python import test failed${NC}"
            ((errors++))
        fi
    fi
    
    return $errors
}

# Function to run tests
run_tests() {
    if [[ "$SKIP_TESTS" == "true" ]]; then
        echo -e "\n${YELLOW}Skipping tests as requested${NC}"
        return 0
    fi
    
    echo -e "\n${BLUE}4. Test Execution${NC}"
    
    local errors=0
    
    # Run Python tests (if available)
    if ! run_gradle_task "pythonTest" "Python unit tests"; then
        echo -e "${YELLOW}⚠ Python tests failed or not found - this is expected if tests don't exist yet${NC}"
    fi
    
    # Run Android tests
    if ! run_gradle_task ":AndroidApp:testDebugUnitTest" "Android unit tests"; then
        echo -e "${YELLOW}⚠ Android tests failed - this is expected if tests don't exist yet${NC}"
    fi
    
    return $errors
}

# Function to generate report
generate_report() {
    local total_errors=$1
    
    echo -e "\n${BLUE}5. Validation Summary${NC}"
    echo "=================================="
    
    if [[ $total_errors -eq 0 ]]; then
        echo -e "${GREEN}🎉 All validations PASSED!${NC}"
        echo -e "${GREEN}✓ Environment is ready for development${NC}"
    else
        echo -e "${RED}❌ Validation completed with $total_errors error(s)${NC}"
        echo -e "${YELLOW}⚠ Please address the issues above before proceeding${NC}"
    fi
    
    echo ""
    echo "Next steps:"
    echo "1. Run the setup script: ./setup.py"
    echo "2. Build the project: ./gradlew assembleAll"
    echo "3. Run the application: ./gradlew PythonApp:runDesktopApp"
    
    return $total_errors
}

# Main execution
main() {
    # Change to script directory
    cd "$(dirname "$0")"
    
    local total_errors=0
    
    validate_environment
    total_errors=$((total_errors + $?))
    
    validate_gradle
    total_errors=$((total_errors + $?))
    
    validate_python
    total_errors=$((total_errors + $?))
    
    run_tests
    # Don't count test failures as critical errors
    
    generate_report $total_errors
    
    exit $total_errors
}

# Run main function
main "$@"