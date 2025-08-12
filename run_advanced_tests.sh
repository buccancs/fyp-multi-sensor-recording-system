#!/bin/bash

# Advanced Testing Framework Execution Script
# ==========================================
# 
# Comprehensive test execution script for the Multi-Sensor Recording System
# supporting all advanced testing capabilities including Appium E2E, Visual
# Regression, Load Testing, Browser Compatibility, and Hardware-in-the-Loop.
#
# Usage:
#   ./run_advanced_tests.sh [test_suite] [options]
#
# Test Suites:
#   all         - Run all test suites (default)
#   unit        - Unit tests only
#   integration - Integration tests
#   e2e         - End-to-end tests with Appium
#   visual      - Visual regression tests
#   load        - Load and stress tests
#   browser     - Cross-browser compatibility tests
#   hardware    - Hardware-in-the-loop tests
#
# Options:
#   --headless  - Run in headless mode (default)
#   --headed    - Run with GUI (for debugging)
#   --verbose   - Verbose output
#   --quick     - Quick test run (reduced timeouts)
#   --ci        - CI mode (optimized for CI/CD)

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
PYTHON_VERSION="3.11"
NODE_VERSION="18"

# Test suite selection
TEST_SUITE="${1:-all}"
shift || true

# Parse options
HEADLESS=true
VERBOSE=false
QUICK=false
CI_MODE=false
ANDROID_TESTS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --headless)
            HEADLESS=true
            shift
            ;;
        --headed)
            HEADLESS=false
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --quick)
            QUICK=true
            shift
            ;;
        --ci)
            CI_MODE=true
            HEADLESS=true
            shift
            ;;
        --android)
            ANDROID_TESTS=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running in CI
if [[ "${CI:-false}" == "true" ]]; then
    CI_MODE=true
    HEADLESS=true
    log_info "Running in CI mode"
fi

# Validate environment
validate_environment() {
    log_info "Validating test environment..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 not found"
        exit 1
    fi
    
    PYTHON_VER=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
    log_info "Python version: $PYTHON_VER"
    
    # Check Node.js for browser/e2e tests
    if [[ "$TEST_SUITE" == "all" || "$TEST_SUITE" == "e2e" || "$TEST_SUITE" == "browser" ]]; then
        if ! command -v node &> /dev/null; then
            log_warning "Node.js not found - E2E and browser tests may fail"
        else
            NODE_VER=$(node --version)
            log_info "Node.js version: $NODE_VER"
        fi
    fi
    
    # Check Java for Android tests
    if [[ "$TEST_SUITE" == "all" || "$TEST_SUITE" == "integration" || "$TEST_SUITE" == "e2e" || "$ANDROID_TESTS" == "true" ]]; then
        if ! command -v java &> /dev/null; then
            log_warning "Java not found - Android tests may fail"
        else
            JAVA_VER=$(java --version 2>&1 | head -n1 | cut -d' ' -f2)
            log_info "Java version: $JAVA_VER"
        fi
        
        # Check Android SDK for Android tests
        if [[ -n "${ANDROID_HOME:-}" ]]; then
            log_info "Android SDK found: $ANDROID_HOME"
        else
            log_warning "ANDROID_HOME not set - Android emulator tests may fail"
        fi
    fi
    
    log_success "Environment validation complete"
}

# Install dependencies
install_dependencies() {
    log_info "Installing Python dependencies..."
    
    cd "$PROJECT_ROOT"
    
    # Install main dependencies
    python3 -m pip install --upgrade pip setuptools wheel
    python3 -m pip install -e ".[dev]"
    
    # Install additional test dependencies based on test suite
    case $TEST_SUITE in
        "all"|"e2e")
            log_info "Installing Appium dependencies..."
            python3 -m pip install Appium-Python-Client selenium
            ;;
        "all"|"load")
            log_info "Installing load testing dependencies..."
            python3 -m pip install locust websocket-client aiohttp
            ;;
        "all"|"browser")
            log_info "Installing browser testing dependencies..."
            python3 -m pip install playwright
            if command -v playwright &> /dev/null; then
                playwright install chromium firefox webkit
            fi
            ;;
        "all"|"hardware")
            log_info "Installing hardware testing dependencies..."
            python3 -m pip install pybluez pyusb pyserial || log_warning "Some hardware dependencies failed to install"
            ;;
    esac
    
    # Install Android-specific dependencies if needed
    if [[ "$ANDROID_TESTS" == "true" || "$TEST_SUITE" == "all" || "$TEST_SUITE" == "e2e" ]]; then
        log_info "Installing Android testing dependencies..."
        python3 -m pip install Appium-Python-Client selenium
        python3 -m pip install pillow numpy  # For visual regression
        python3 -m pip install psutil  # For performance monitoring
    fi
    
    log_success "Dependencies installed"
}

# Setup test environment
setup_test_environment() {
    log_info "Setting up test environment..."
    
    # Create test directories
    mkdir -p "$PROJECT_ROOT/test_results"
    mkdir -p "$PROJECT_ROOT/test_artifacts"
    
    # Set environment variables
    export GSR_TEST_CI_MODE="$CI_MODE"
    export GSR_TEST_HEADLESS="$HEADLESS"
    export GSR_TEST_LOG_LEVEL="INFO"
    
    if [[ "$VERBOSE" == "true" ]]; then
        export GSR_TEST_LOG_LEVEL="DEBUG"
    fi
    
    if [[ "$QUICK" == "true" ]]; then
        export GSR_TEST_QUICK_MODE="true"
    fi
    
    log_success "Test environment configured"
}

# Start required services
start_services() {
    log_info "Starting required services..."
    
    # Start Web dashboard for network tests
    if [[ "$TEST_SUITE" == "all" || "$TEST_SUITE" == "e2e" || "$TEST_SUITE" == "load" || "$TEST_SUITE" == "browser" ]]; then
        log_info "Starting Web dashboard..."
        cd "$PROJECT_ROOT/PythonApp"
        python3 -m web_ui.web_dashboard &
        WEB_DASHBOARD_PID=$!
        sleep 3
        
        # Check if dashboard started
        if curl -f http://localhost:5000/ &> /dev/null; then
            log_success "Web dashboard started (PID: $WEB_DASHBOARD_PID)"
        else
            log_warning "Web dashboard may not have started properly"
        fi
        cd "$PROJECT_ROOT"
    fi
    
    # Start Android emulator if needed for E2E tests
    if [[ "$TEST_SUITE" == "all" || "$TEST_SUITE" == "e2e" || "$ANDROID_TESTS" == "true" ]]; then
        if [[ -n "${ANDROID_HOME:-}" ]]; then
            log_info "Starting Android emulator for E2E tests..."
            
            # Check if emulator is already running
            if ! adb devices | grep -q emulator; then
                # Start emulator in background
                $ANDROID_HOME/emulator/emulator -avd test -no-snapshot-save -no-window -gpu swiftshader_indirect -noaudio -no-boot-anim -camera-back none &
                EMULATOR_PID=$!
                
                # Wait for emulator to be ready
                log_info "Waiting for Android emulator to be ready..."
                timeout 120 adb wait-for-device
                
                # Additional setup time
                sleep 10
                
                # Enable input and disable screen lock
                adb shell input keyevent 82 &
                
                log_success "Android emulator started and ready"
            else
                log_info "Android emulator already running"
            fi
        else
            log_warning "ANDROID_HOME not set - Android emulator will not be started"
        fi
    fi
}

# Stop services
cleanup_services() {
    log_info "Cleaning up services..."
    
    # Stop Web dashboard
    if [[ -n "${WEB_DASHBOARD_PID:-}" ]]; then
        kill $WEB_DASHBOARD_PID 2>/dev/null || true
        log_info "Stopped Web dashboard"
    fi
    
    # Stop Appium server
    if [[ -n "${APPIUM_PID:-}" ]]; then
        kill $APPIUM_PID 2>/dev/null || true
        log_info "Stopped Appium server"
    fi
    
    # Kill any remaining processes
    pkill -f "web_dashboard" 2>/dev/null || true
    pkill -f "appium" 2>/dev/null || true
}

# Trap to cleanup on exit
trap cleanup_services EXIT

# Run specific test suite
run_test_suite() {
    local suite=$1
    local markers=""
    local test_dir=""
    local timeout="300"
    
    if [[ "$QUICK" == "true" ]]; then
        timeout="120"
    fi
    
    case $suite in
        "unit")
            markers="unit and not hardware_loop"
            test_dir="tests/"
            timeout="60"
            ;;
        "integration")
            markers="integration and not hardware_loop"
            test_dir="tests/"
            timeout="180"
            ;;
        "e2e")
            markers="e2e"
            test_dir="tests/e2e/"
            timeout="600"
            ;;
        "visual")
            markers="visual"
            test_dir="tests/visual/"
            timeout="300"
            ;;
        "load")
            markers="load"
            test_dir="tests/load/"
            timeout="900"
            ;;
        "browser")
            markers="browser"
            test_dir="tests/browser/"
            timeout="400"
            ;;
        "hardware")
            markers="hardware_loop"
            test_dir="tests/hardware/"
            timeout="600"
            ;;
        "android")
            markers="android"
            test_dir="tests/"
            timeout="900"
            ;;
        *)
            log_error "Unknown test suite: $suite"
            return 1
            ;;
    esac
    
    log_info "Running $suite tests..."
    
    # Prepare pytest command
    local pytest_cmd="pytest"
    local pytest_args=(
        "$test_dir"
        "-m" "$markers"
        "--timeout=$timeout"
        "--tb=short"
        "-v"
        "--junitxml=test_results/junit-$suite.xml"
    )
    
    if [[ "$VERBOSE" == "true" ]]; then
        pytest_args+=("-s")
    fi
    
    if [[ "$CI_MODE" == "true" ]]; then
        pytest_args+=(
            "--cov=PythonApp"
            "--cov-report=xml:test_results/coverage-$suite.xml"
            "--cov-report=html:test_results/htmlcov-$suite"
        )
    fi
    
    # Run tests with appropriate display setup
    if [[ "$HEADLESS" == "true" ]] && [[ "$suite" == "visual" || "$suite" == "e2e" || "$suite" == "browser" ]]; then
        if command -v xvfb-run &> /dev/null; then
            xvfb-run -a "$pytest_cmd" "${pytest_args[@]}"
        else
            log_warning "xvfb-run not available, running without virtual display"
            "$pytest_cmd" "${pytest_args[@]}"
        fi
    else
        "$pytest_cmd" "${pytest_args[@]}"
    fi
    
    local exit_code=$?
    
    if [[ $exit_code -eq 0 ]]; then
        log_success "$suite tests completed successfully"
    else
        log_error "$suite tests failed (exit code: $exit_code)"
    fi
    
    return $exit_code
}

# Generate test report
generate_report() {
    log_info "Generating test report..."
    
    cd "$PROJECT_ROOT"
    
    python3 -c "
import os
import xml.etree.ElementTree as ET
import glob
import json
from datetime import datetime
from pathlib import Path

# Collect test results
results = {}
total_tests = 0
total_passed = 0
total_failed = 0
total_skipped = 0

junit_files = glob.glob('test_results/junit-*.xml')

for junit_file in junit_files:
    try:
        tree = ET.parse(junit_file)
        root = tree.getroot()
        
        suite_name = Path(junit_file).stem.replace('junit-', '')
        
        tests = int(root.get('tests', 0))
        failures = int(root.get('failures', 0))
        errors = int(root.get('errors', 0))
        skipped = int(root.get('skipped', 0))
        time_taken = float(root.get('time', 0))
        
        passed = tests - failures - errors - skipped
        
        results[suite_name] = {
            'tests': tests,
            'passed': passed,
            'failed': failures + errors,
            'skipped': skipped,
            'time': time_taken,
            'success_rate': (passed / tests * 100) if tests > 0 else 0
        }
        
        total_tests += tests
        total_passed += passed
        total_failed += failures + errors
        total_skipped += skipped
        
    except Exception as e:
        print(f'Error processing {junit_file}: {e}')

# Generate summary report
summary = {
    'timestamp': datetime.now().isoformat(),
    'test_suite': '$TEST_SUITE',
    'environment': {
        'headless': '$HEADLESS',
        'ci_mode': '$CI_MODE',
        'quick_mode': '$QUICK'
    },
    'totals': {
        'tests': total_tests,
        'passed': total_passed,
        'failed': total_failed,
        'skipped': total_skipped,
        'success_rate': (total_passed / total_tests * 100) if total_tests > 0 else 0
    },
    'suites': results
}

# Save JSON report
with open('test_results/test-summary.json', 'w') as f:
    json.dump(summary, f, indent=2)

# Generate markdown report
with open('test_results/test-summary.md', 'w') as f:
    f.write('# Advanced Testing Framework Report\n\n')
    f.write(f'**Generated:** {summary[\"timestamp\"]}\n')
    f.write(f'**Test Suite:** {summary[\"test_suite\"]}\n')
    f.write(f'**Environment:** Headless={summary[\"environment\"][\"headless\"]}, CI={summary[\"environment\"][\"ci_mode\"]}\n\n')
    
    f.write('## Summary\n\n')
    f.write(f'- **Total Tests:** {summary[\"totals\"][\"tests\"]}\n')
    f.write(f'- **Passed:** {summary[\"totals\"][\"passed\"]}\n')
    f.write(f'- **Failed:** {summary[\"totals\"][\"failed\"]}\n')
    f.write(f'- **Skipped:** {summary[\"totals\"][\"skipped\"]}\n')
    f.write(f'- **Success Rate:** {summary[\"totals\"][\"success_rate\"]:.1f}%\n\n')
    
    f.write('## Test Suite Results\n\n')
    for suite, data in results.items():
        status = '✅' if data['failed'] == 0 else '❌'
        f.write(f'### {status} {suite.title()}\n')
        f.write(f'- Tests: {data[\"tests\"]} | Passed: {data[\"passed\"]} | Failed: {data[\"failed\"]} | Skipped: {data[\"skipped\"]}\n')
        f.write(f'- Success Rate: {data[\"success_rate\"]:.1f}%\n')
        f.write(f'- Duration: {data[\"time\"]:.2f}s\n\n')

print(f'Test report generated: {total_passed}/{total_tests} tests passed ({(total_passed/total_tests*100) if total_tests > 0 else 0:.1f}%)')
"
    
    log_success "Test report generated in test_results/"
}

# Main execution
main() {
    log_info "Starting Advanced Testing Framework"
    log_info "Test suite: $TEST_SUITE"
    log_info "Options: headless=$HEADLESS, verbose=$VERBOSE, quick=$QUICK, ci=$CI_MODE"
    
    validate_environment
    install_dependencies
    setup_test_environment
    start_services
    
    # Run tests based on suite selection
    local overall_exit_code=0
    
    case $TEST_SUITE in
        "all")
            local test_suites=("unit" "integration" "e2e" "visual" "load" "browser")
            
            # Add hardware tests if not in CI or explicitly enabled
            if [[ "$CI_MODE" == "false" ]]; then
                test_suites+=("hardware")
            fi
            
            # Add Android tests if enabled
            if [[ "$ANDROID_TESTS" == "true" ]]; then
                test_suites+=("android")
            fi
            
            for suite in "${test_suites[@]}"; do
                if ! run_test_suite "$suite"; then
                    overall_exit_code=1
                fi
            done
            ;;
        *)
            if ! run_test_suite "$TEST_SUITE"; then
                overall_exit_code=1
            fi
            ;;
    esac
    
    generate_report
    
    if [[ $overall_exit_code -eq 0 ]]; then
        log_success "All tests completed successfully!"
    else
        log_error "Some tests failed. Check the report for details."
    fi
    
    return $overall_exit_code
}

# Show usage if requested
if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    echo "Advanced Testing Framework for Multi-Sensor Recording System"
    echo ""
    echo "Usage: $0 [test_suite] [options]"
    echo ""
    echo "Test Suites:"
    echo "  all         Run all test suites (default)"
    echo "  unit        Unit tests only"
    echo "  integration Integration tests"
    echo "  e2e         End-to-end tests with Appium"
    echo "  visual      Visual regression tests"
    echo "  load        Load and stress tests"
    echo "  browser     Cross-browser compatibility tests"
    echo "  hardware    Hardware-in-the-loop tests"
    echo "  android     Android-specific comprehensive tests"
    echo ""
    echo "Options:"
    echo "  --headless  Run in headless mode (default)"
    echo "  --headed    Run with GUI (for debugging)"
    echo "  --verbose   Verbose output"
    echo "  --quick     Quick test run (reduced timeouts)"
    echo "  --ci        CI mode (optimized for CI/CD)"
    echo "  --android   Enable Android-specific testing"
    echo ""
    echo "Examples:"
    echo "  $0                    # Run all tests in headless mode"
    echo "  $0 e2e --headed      # Run E2E tests with GUI"
    echo "  $0 load --verbose    # Run load tests with verbose output"
    echo "  $0 all --ci          # Run all tests in CI mode"
    echo "  $0 android --verbose # Run Android-specific tests with verbose output"
    exit 0
fi

# Execute main function
main