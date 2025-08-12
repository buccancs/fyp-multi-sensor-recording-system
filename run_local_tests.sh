#!/bin/bash
#
# Local Test Runner for Multi-Sensor Recording System
# Provides easy local testing with the unified testing framework
#

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if unified testing framework is available
check_unified_framework() {
    if [ -f "tests_unified/runners/run_unified_tests.py" ]; then
        return 0
    else
        return 1
    fi
}

# Function to install dependencies
install_dependencies() {
    print_status "Installing test dependencies..."
    
    if [ -f "test-requirements.txt" ]; then
        pip install -r test-requirements.txt
    fi
    
    if [ -f "pyproject.toml" ]; then
        pip install -e .
    fi
    
    print_success "Dependencies installed"
}

# Function to run unified tests
run_unified_tests() {
    local mode="${1:-quick}"
    
    print_status "Running unified test suite in $mode mode..."
    
    case "$mode" in
        "quick")
            python tests_unified/runners/run_unified_tests.py --quick --verbose
            ;;
        "full")
            python tests_unified/runners/run_unified_tests.py --all-levels --verbose
            ;;
        "requirements")
            python tests_unified/runners/run_unified_tests.py --validate-requirements
            python tests_unified/runners/run_unified_tests.py --report-requirements-coverage
            ;;
        "performance")
            python tests_unified/runners/run_unified_tests.py --level performance --performance-benchmarks
            ;;
        "ci")
            python tests_unified/runners/run_unified_tests.py --mode ci
            ;;
        *)
            print_error "Unknown mode: $mode"
            print_status "Available modes: quick, full, requirements, performance, ci"
            exit 1
            ;;
    esac
}

# Function to run legacy tests as fallback
run_legacy_tests() {
    print_warning "Unified testing framework not found, falling back to legacy tests"
    
    # Check for pytest
    if command -v pytest &> /dev/null; then
        if [ -d "tests" ]; then
            print_status "Running pytest on tests/ directory..."
            pytest tests/ -v --tb=short
        else
            print_warning "No tests/ directory found"
        fi
    else
        print_error "pytest not available and no unified framework found"
        exit 1
    fi
}

# Function to show usage information
show_usage() {
    echo "Local Test Runner for Multi-Sensor Recording System"
    echo ""
    echo "Usage: $0 [MODE] [OPTIONS]"
    echo ""
    echo "MODES:"
    echo "  quick        Run quick test suite (default, ~2 minutes)"
    echo "  full         Run complete test suite (all levels)"
    echo "  requirements Validate functional and non-functional requirements"
    echo "  performance  Run performance benchmarks"
    echo "  ci           Run CI/CD mode tests"
    echo ""
    echo "OPTIONS:"
    echo "  --install-deps    Install test dependencies before running"
    echo "  --help, -h        Show this help message"
    echo ""
    echo "EXAMPLES:"
    echo "  $0                           # Quick test suite"
    echo "  $0 full                      # Complete test suite"
    echo "  $0 requirements              # Requirements validation"
    echo "  $0 quick --install-deps      # Install deps and run quick tests"
    echo ""
    echo "UNIFIED FRAMEWORK USAGE:"
    echo "  # Direct usage of unified framework"
    echo "  python tests_unified/runners/run_unified_tests.py --help"
    echo ""
    echo "  # Specific test levels"
    echo "  python tests_unified/runners/run_unified_tests.py --level unit"
    echo "  python tests_unified/runners/run_unified_tests.py --level integration"
    echo ""
    echo "  # Specific categories"
    echo "  python tests_unified/runners/run_unified_tests.py --category android"
    echo "  python tests_unified/runners/run_unified_tests.py --category hardware"
    echo ""
}

# Main execution
main() {
    local mode="quick"
    local install_deps=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --install-deps)
                install_deps=true
                shift
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            quick|full|requirements|performance|ci)
                mode="$1"
                shift
                ;;
            *)
                print_error "Unknown argument: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    print_status "Multi-Sensor Recording System - Local Test Runner"
    print_status "=================================================="
    
    # Check if we're in the right directory
    if [ ! -f "pyproject.toml" ] && [ ! -f "setup.py" ] && [ ! -d "PythonApp" ]; then
        print_error "Not in project root directory. Please run from the repository root."
        exit 1
    fi
    
    # Install dependencies if requested
    if [ "$install_deps" = true ]; then
        install_dependencies
    fi
    
    # Check for unified framework and run appropriate tests
    if check_unified_framework; then
        print_success "Unified testing framework found"
        run_unified_tests "$mode"
    else
        run_legacy_tests
    fi
    
    print_success "Test execution completed"
}

# Run main function with all arguments
main "$@"