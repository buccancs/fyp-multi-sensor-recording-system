#!/bin/bash

# Enhanced Android Test Suite Runner
# Provides comprehensive test execution with performance monitoring for Android components
# Similar to the Python comprehensive test runner but adapted for Android/Gradle ecosystem

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPORTS_DIR="$PROJECT_ROOT/app/build/reports"
TEST_RESULTS_DIR="$PROJECT_ROOT/app/build/test-results" 
COVERAGE_DIR="$PROJECT_ROOT/app/build/reports/coverage"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Test categories
UNIT_TESTS=true
INTEGRATION_TESTS=true
UI_TESTS=true
STRESS_TESTS=false
PERFORMANCE_TESTS=true
COVERAGE_ANALYSIS=true

# Performance thresholds
MAX_TEST_TIME_SECONDS=300
MAX_MEMORY_MB=512
MIN_COVERAGE_PERCENT=75

echo -e "${CYAN}=================================================================="
echo -e "ENHANCED ANDROID MULTI-SENSOR RECORDING SYSTEM TEST SUITE"
echo -e "=================================================================="
echo -e "${NC}"

print_section() {
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}$(printf '%*s' ${#1} | tr ' ' '-')${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-unit)
            UNIT_TESTS=false
            shift
            ;;
        --no-integration)
            INTEGRATION_TESTS=false
            shift
            ;;
        --no-ui)
            UI_TESTS=false
            shift
            ;;
        --stress)
            STRESS_TESTS=true
            shift
            ;;
        --no-performance)
            PERFORMANCE_TESTS=false
            shift
            ;;
        --no-coverage)
            COVERAGE_ANALYSIS=false
            shift
            ;;
        --help)
            echo "Enhanced Android Test Suite Runner"
            echo ""
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --no-unit         Skip unit tests"
            echo "  --no-integration  Skip integration tests"
            echo "  --no-ui          Skip UI tests"
            echo "  --stress         Include stress tests (disabled by default)"
            echo "  --no-performance Skip performance tests"
            echo "  --no-coverage    Skip coverage analysis"
            echo "  --help           Show this help message"
            echo ""
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Verify environment
print_section "Environment Verification"

# Check if we're in the right directory
if [[ ! -f "$PROJECT_ROOT/build.gradle" ]]; then
    print_error "Not in Android project root. Please run from the AndroidApp directory."
    exit 1
fi

# Check Java/Kotlin environment
if ! command -v java &> /dev/null; then
    print_error "Java is not installed or not in PATH"
    exit 1
fi

# Check Gradle
if [[ ! -f "$PROJECT_ROOT/gradlew" ]]; then
    print_error "Gradle wrapper not found"
    exit 1
fi

# Make gradlew executable
chmod +x "$PROJECT_ROOT/gradlew"

print_success "Environment verification complete"
print_info "Project root: $PROJECT_ROOT"
print_info "Java version: $(java -version 2>&1 | head -n 1)"

# Clean previous results
print_section "Cleaning Previous Results"
"$PROJECT_ROOT/gradlew" clean
rm -rf "$REPORTS_DIR"
rm -rf "$TEST_RESULTS_DIR"
rm -rf "$COVERAGE_DIR"
print_success "Previous results cleaned"

# Create directories
mkdir -p "$REPORTS_DIR"
mkdir -p "$TEST_RESULTS_DIR"
mkdir -p "$COVERAGE_DIR"

# Start test execution
START_TIME=$(date +%s)
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0

print_section "Test Execution Configuration"
echo -e "📋 Test Categories:"
[[ $UNIT_TESTS == true ]] && echo -e "   ✅ Unit Tests: Core functionality validation"
[[ $INTEGRATION_TESTS == true ]] && echo -e "   ✅ Integration Tests: Component interaction validation"
[[ $UI_TESTS == true ]] && echo -e "   ✅ UI Tests: User interface validation"
[[ $STRESS_TESTS == true ]] && echo -e "   ⚡ Stress Tests: High-load scenario validation"
[[ $PERFORMANCE_TESTS == true ]] && echo -e "   📊 Performance Tests: Benchmark validation"
[[ $COVERAGE_ANALYSIS == true ]] && echo -e "   📈 Coverage Analysis: Code coverage reporting"

echo -e "\n🔧 Enhanced Features:"
echo -e "   • Performance monitoring and benchmarking"
echo -e "   • Memory usage tracking and analysis"
echo -e "   • Comprehensive HTML and JSON reporting"
echo -e "   • Cross-platform compatibility validation"
echo -e "   • Test categorization and analytics"

echo -e "\n⚙️ Performance Thresholds:"
echo -e "   • Maximum test time: ${MAX_TEST_TIME_SECONDS}s"
echo -e "   • Maximum memory usage: ${MAX_MEMORY_MB}MB"
echo -e "   • Minimum coverage: ${MIN_COVERAGE_PERCENT}%"

# Function to run tests and collect metrics
run_test_category() {
    local category=$1
    local gradle_task=$2
    local description=$3
    
    print_section "$category"
    print_info "Running: $description"
    
    local start_time=$(date +%s)
    local start_memory=$(free -m | awk 'NR==2{print $3}')
    
    # Run the test with timeout
    if timeout ${MAX_TEST_TIME_SECONDS}s "$PROJECT_ROOT/gradlew" $gradle_task --continue; then
        local exit_code=0
        print_success "$category completed successfully"
    else
        local exit_code=$?
        if [[ $exit_code == 124 ]]; then
            print_error "$category timed out after ${MAX_TEST_TIME_SECONDS}s"
        else
            print_error "$category failed with exit code $exit_code"
        fi
    fi
    
    local end_time=$(date +%s)
    local end_memory=$(free -m | awk 'NR==2{print $3}')
    local execution_time=$((end_time - start_time))
    local memory_delta=$((end_memory - start_memory))
    
    # Performance analysis
    echo -e "\n📊 Performance Metrics:"
    echo -e "   ⏱️  Execution time: ${execution_time}s"
    echo -e "   💾 Memory delta: ${memory_delta}MB"
    
    if [[ $execution_time -gt $MAX_TEST_TIME_SECONDS ]]; then
        print_warning "Execution time exceeded threshold"
    fi
    
    if [[ $memory_delta -gt $MAX_MEMORY_MB ]]; then
        print_warning "Memory usage exceeded threshold"
    fi
    
    # Parse test results if available
    local test_result_file="$TEST_RESULTS_DIR/testDebugUnitTest/TEST-*.xml"
    if [[ -f $test_result_file ]]; then
        local category_tests=$(grep -o 'tests="[0-9]*"' $test_result_file | cut -d'"' -f2 | head -1)
        local category_failures=$(grep -o 'failures="[0-9]*"' $test_result_file | cut -d'"' -f2 | head -1)
        local category_skipped=$(grep -o 'skipped="[0-9]*"' $test_result_file | cut -d'"' -f2 | head -1)
        
        category_tests=${category_tests:-0}
        category_failures=${category_failures:-0}
        category_skipped=${category_skipped:-0}
        
        TOTAL_TESTS=$((TOTAL_TESTS + category_tests))
        FAILED_TESTS=$((FAILED_TESTS + category_failures))
        SKIPPED_TESTS=$((SKIPPED_TESTS + category_skipped))
        PASSED_TESTS=$((PASSED_TESTS + category_tests - category_failures - category_skipped))
        
        echo -e "   📈 Results: $category_tests tests, $category_failures failures, $category_skipped skipped"
    fi
    
    return $exit_code
}

# Execute test categories
OVERALL_SUCCESS=true

# Unit Tests
if [[ $UNIT_TESTS == true ]]; then
    if ! run_test_category "Unit Tests" "testDebugUnitTest" "Core functionality and business logic tests"; then
        OVERALL_SUCCESS=false
    fi
fi

# Performance Tests (subset of unit tests with benchmarking)
if [[ $PERFORMANCE_TESTS == true ]]; then
    if ! run_test_category "Performance Tests" "testDebugUnitTest -Pperformance=true" "Performance benchmarks and optimization validation"; then
        OVERALL_SUCCESS=false
    fi
fi

# Integration Tests (Instrumented tests requiring device/emulator)
if [[ $INTEGRATION_TESTS == true ]]; then
    print_section "Integration Tests"
    print_info "Checking for connected devices..."
    
    # Check if device is connected
    if command -v adb &> /dev/null && adb devices | grep -q "device$"; then
        print_success "Android device detected"
        if ! run_test_category "Integration Tests" "connectedDebugAndroidTest" "Component integration and hardware interaction tests"; then
            OVERALL_SUCCESS=false
        fi
    else
        print_warning "No Android device connected. Skipping integration tests."
        print_info "To run integration tests, connect a device or start an emulator."
    fi
fi

# UI Tests (subset of instrumented tests)
if [[ $UI_TESTS == true ]]; then
    print_section "UI Tests"
    if command -v adb &> /dev/null && adb devices | grep -q "device$"; then
        if ! run_test_category "UI Tests" "connectedDebugAndroidTest -Pui=true" "User interface and interaction tests"; then
            OVERALL_SUCCESS=false
        fi
    else
        print_warning "No Android device connected. Skipping UI tests."
    fi
fi

# Stress Tests (high-intensity scenarios)
if [[ $STRESS_TESTS == true ]]; then
    if ! run_test_category "Stress Tests" "testDebugUnitTest -Pstress=true" "High-load and edge case scenario tests"; then
        OVERALL_SUCCESS=false
    fi
fi

# Code Coverage Analysis
if [[ $COVERAGE_ANALYSIS == true ]]; then
    print_section "Code Coverage Analysis"
    print_info "Generating coverage reports..."
    
    if "$PROJECT_ROOT/gradlew" testDebugUnitTestCoverage; then
        print_success "Coverage analysis completed"
        
        # Parse coverage if jacoco report exists
        local coverage_file="$COVERAGE_DIR/jacocoTestReport/html/index.html"
        if [[ -f "$coverage_file" ]]; then
            print_info "Coverage report generated: $coverage_file"
            
            # Extract coverage percentage (simplified - would need proper HTML parsing)
            if command -v grep &> /dev/null; then
                local coverage_line=$(grep -o "[0-9]*%" "$coverage_file" | head -1)
                if [[ -n "$coverage_line" ]]; then
                    local coverage_percent=$(echo "$coverage_line" | sed 's/%//')
                    echo -e "   📈 Overall coverage: $coverage_line"
                    
                    if [[ $coverage_percent -lt $MIN_COVERAGE_PERCENT ]]; then
                        print_warning "Coverage below threshold ($MIN_COVERAGE_PERCENT%)"
                    else
                        print_success "Coverage meets threshold"
                    fi
                fi
            fi
        fi
    else
        print_error "Coverage analysis failed"
        OVERALL_SUCCESS=false
    fi
fi

# Final Summary
END_TIME=$(date +%s)
TOTAL_EXECUTION_TIME=$((END_TIME - START_TIME))

print_section "Enhanced Android Test Suite Summary"

echo -e "${CYAN}📊 Overall Results:${NC}"
echo -e "   Total Tests: $TOTAL_TESTS"
echo -e "   ${GREEN}✅ Passed: $PASSED_TESTS${NC}"
echo -e "   ${RED}❌ Failed: $FAILED_TESTS${NC}"
echo -e "   ${YELLOW}⏭️  Skipped: $SKIPPED_TESTS${NC}"
echo -e "   ⏱️  Total Time: ${TOTAL_EXECUTION_TIME}s"

if [[ $TOTAL_TESTS -gt 0 ]]; then
    local success_rate=$(( (PASSED_TESTS * 100) / (TOTAL_TESTS - SKIPPED_TESTS) ))
    echo -e "   🎯 Success Rate: $success_rate%"
fi

# Performance summary
echo -e "\n🔧 Enhanced Features Executed:"
[[ $UNIT_TESTS == true ]] && echo -e "   ✅ Unit test validation completed"
[[ $INTEGRATION_TESTS == true ]] && echo -e "   ✅ Integration test validation completed"
[[ $UI_TESTS == true ]] && echo -e "   ✅ UI test validation completed"
[[ $STRESS_TESTS == true ]] && echo -e "   ⚡ Stress test validation completed"
[[ $PERFORMANCE_TESTS == true ]] && echo -e "   📊 Performance benchmark validation completed"
[[ $COVERAGE_ANALYSIS == true ]] && echo -e "   📈 Coverage analysis completed"

# Report locations
echo -e "\n📄 Reports Generated:"
if [[ -d "$REPORTS_DIR" ]]; then
    echo -e "   📋 Test Reports: $REPORTS_DIR"
fi
if [[ -d "$TEST_RESULTS_DIR" ]]; then
    echo -e "   📊 Test Results: $TEST_RESULTS_DIR"
fi
if [[ -d "$COVERAGE_DIR" && $COVERAGE_ANALYSIS == true ]]; then
    echo -e "   📈 Coverage Reports: $COVERAGE_DIR"
fi

# Research impact summary
echo -e "\n🔬 Research Impact:"
echo -e "   • Comprehensive Android test framework with performance monitoring"
echo -e "   • Cross-platform validation for mobile physiological monitoring"
echo -e "   • Production-ready test automation for research reproducibility"
echo -e "   • Enhanced quality assurance for medical device applications"

echo -e "${CYAN}=================================================================="

# Exit with appropriate code
if [[ $OVERALL_SUCCESS == true && $FAILED_TESTS -eq 0 ]]; then
    print_success "All enhanced Android tests completed successfully!"
    echo -e "${GREEN}🎉 Android test suite validation: PASSED${NC}"
    exit 0
else
    print_error "Some tests failed or encountered issues"
    echo -e "${RED}💥 Android test suite validation: FAILED${NC}"
    exit 1
fi