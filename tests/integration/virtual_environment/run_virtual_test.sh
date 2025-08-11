#!/bin/bash
# Virtual Test Environment Runner Script
#
# This script provides an easy way to run the virtual test environment
# both locally and in CI. It handles Docker setup, test execution,
# and result collection.

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
RESULTS_DIR="$SCRIPT_DIR/test_results"
CONFIGS_DIR="$SCRIPT_DIR/test_configs"

# Default values
TEST_SCENARIO="quick"
DEVICE_COUNT=3
DURATION_MINUTES=3.0
USE_DOCKER=false
VERBOSE=false
CI_MODE=false
CLEANUP=true

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_info() { echo -e "${BLUE}INFO:${NC} $1"; }
print_success() { echo -e "${GREEN}SUCCESS:${NC} $1"; }
print_warning() { echo -e "${YELLOW}WARNING:${NC} $1"; }
print_error() { echo -e "${RED}ERROR:${NC} $1"; }

# Usage function
usage() {
    cat << EOF
Virtual Test Environment Runner

Usage: $0 [OPTIONS]

Options:
    -s, --scenario SCENARIO    Test scenario: quick, stress, sync, ci (default: quick)
    -d, --devices COUNT        Number of virtual devices (default: 3)
    -t, --duration MINUTES     Test duration in minutes (default: 3.0)
    -D, --docker               Run using Docker
    -v, --verbose              Enable verbose output
    -c, --ci                   Run in CI mode (shorter timeouts, less output)
    -o, --output DIR           Output directory (default: ./test_results)
    --no-cleanup               Don't clean up containers after test
    -h, --help                 Show this help message

Examples:
    $0 --scenario quick --devices 2 --duration 1.0
    $0 --docker --scenario stress --devices 5 --duration 10.0
    $0 --ci --scenario ci --devices 3

Environment Variables:
    GSR_TEST_DEVICE_COUNT      Override device count
    GSR_TEST_DURATION_MINUTES  Override test duration
    GSR_TEST_LOG_LEVEL         Set log level (DEBUG, INFO, WARNING, ERROR)
    GSR_TEST_OUTPUT_DIR        Override output directory
    GSR_TEST_CI_MODE           Set CI mode (true/false)

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--scenario)
            TEST_SCENARIO="$2"
            shift 2
            ;;
        -d|--devices)
            DEVICE_COUNT="$2"
            shift 2
            ;;
        -t|--duration)
            DURATION_MINUTES="$2"
            shift 2
            ;;
        -D|--docker)
            USE_DOCKER=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -c|--ci)
            CI_MODE=true
            shift
            ;;
        -o|--output)
            RESULTS_DIR="$2"
            shift 2
            ;;
        --no-cleanup)
            CLEANUP=false
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Apply environment variable overrides
DEVICE_COUNT=${GSR_TEST_DEVICE_COUNT:-$DEVICE_COUNT}
DURATION_MINUTES=${GSR_TEST_DURATION_MINUTES:-$DURATION_MINUTES}
CI_MODE=${GSR_TEST_CI_MODE:-$CI_MODE}

# Validate scenario
case $TEST_SCENARIO in
    quick|stress|sync|ci)
        ;;
    *)
        print_error "Invalid scenario: $TEST_SCENARIO"
        print_info "Valid scenarios: quick, stress, sync, ci"
        exit 1
        ;;
esac

# Setup directories
mkdir -p "$RESULTS_DIR"
mkdir -p "$CONFIGS_DIR"

print_info "Virtual Test Environment Runner"
print_info "Scenario: $TEST_SCENARIO, Devices: $DEVICE_COUNT, Duration: ${DURATION_MINUTES}m"
print_info "Docker: $USE_DOCKER, CI Mode: $CI_MODE, Verbose: $VERBOSE"
print_info "Results directory: $RESULTS_DIR"

# Function to check dependencies
check_dependencies() {
    if [[ "$USE_DOCKER" == "true" ]]; then
        if ! command -v docker &> /dev/null; then
            print_error "Docker is required but not installed"
            exit 1
        fi
        
        if ! command -v docker-compose &> /dev/null; then
            print_error "Docker Compose is required but not installed"
            exit 1
        fi
    else
        if ! command -v python3 &> /dev/null; then
            print_error "Python 3 is required but not installed"
            exit 1
        fi
        
        # Check if virtual environment is available
        cd "$PROJECT_ROOT"
        if ! python3 -c "import PythonApp.network.android_device_manager" &> /dev/null; then
            print_warning "Project dependencies may not be installed"
            print_info "Consider running: pip install -e ."
        fi
    fi
}

# Function to run tests using Docker
run_docker_test() {
    print_info "Running virtual test using Docker..."
    
    cd "$SCRIPT_DIR"
    
    # Set environment variables for Docker
    export GSR_TEST_HEADLESS=true
    export GSR_TEST_CI_MODE=$CI_MODE
    export GSR_TEST_OUTPUT_DIR=/app/test_results
    
    if [[ "$VERBOSE" == "true" ]]; then
        export GSR_TEST_LOG_LEVEL=DEBUG
    elif [[ "$CI_MODE" == "true" ]]; then
        export GSR_TEST_LOG_LEVEL=WARNING
    else
        export GSR_TEST_LOG_LEVEL=INFO
    fi
    
    # Determine which Docker profile to use
    DOCKER_PROFILE=""
    case $TEST_SCENARIO in
        ci)
            DOCKER_PROFILE="--profile ci"
            ;;
        stress)
            DOCKER_PROFILE="--profile stress"
            ;;
    esac
    
    # Build and run the container
    print_info "Building Docker image..."
    docker-compose build virtual-test
    
    print_info "Starting virtual test container..."
    if [[ "$TEST_SCENARIO" == "ci" ]]; then
        docker-compose $DOCKER_PROFILE up --abort-on-container-exit ci-test
    elif [[ "$TEST_SCENARIO" == "stress" ]]; then
        docker-compose $DOCKER_PROFILE up --abort-on-container-exit stress-test
    else
        docker-compose up --abort-on-container-exit virtual-test
    fi
    
    # Copy results from container
    CONTAINER_NAME="gsr-virtual-test"
    if [[ "$TEST_SCENARIO" == "ci" ]]; then
        CONTAINER_NAME="gsr-ci-test"
    elif [[ "$TEST_SCENARIO" == "stress" ]]; then
        CONTAINER_NAME="gsr-stress-test"
    fi
    
    print_info "Copying test results from container..."
    docker cp "${CONTAINER_NAME}:/app/test_results/." "$RESULTS_DIR/" || true
    
    # Cleanup
    if [[ "$CLEANUP" == "true" ]]; then
        print_info "Cleaning up Docker containers..."
        docker-compose down --remove-orphans
    fi
}

# Function to run tests locally
run_local_test() {
    print_info "Running virtual test locally..."
    
    cd "$PROJECT_ROOT"
    
    # Set environment variables
    export GSR_TEST_HEADLESS=true
    export GSR_TEST_CI_MODE=$CI_MODE
    export GSR_TEST_OUTPUT_DIR="$RESULTS_DIR"
    
    if [[ "$VERBOSE" == "true" ]]; then
        export GSR_TEST_LOG_LEVEL=DEBUG
        VERBOSE_FLAG="--verbose"
    else
        VERBOSE_FLAG=""
    fi
    
    # Build command
    CMD=(
        python -m tests.integration.virtual_environment.test_runner
        --scenario "$TEST_SCENARIO"
        --devices "$DEVICE_COUNT"
        --duration "$DURATION_MINUTES"
        --output "$RESULTS_DIR"
        $VERBOSE_FLAG
    )
    
    print_info "Executing: ${CMD[*]}"
    "${CMD[@]}"
}

# Function to validate and summarize results
summarize_results() {
    print_info "Summarizing test results..."
    
    local report_files=("$RESULTS_DIR"/*_report.json)
    
    if [[ ! -f "${report_files[0]}" ]]; then
        print_warning "No test reports found in $RESULTS_DIR"
        return 1
    fi
    
    local total_tests=0
    local passed_tests=0
    local failed_tests=0
    
    for report_file in "${report_files[@]}"; do
        if [[ -f "$report_file" ]]; then
            total_tests=$((total_tests + 1))
            
            # Extract pass/fail status using basic JSON parsing
            local overall_passed=$(grep -o '"overall_passed": *[^,}]*' "$report_file" | cut -d: -f2 | tr -d ' "')
            
            if [[ "$overall_passed" == "true" ]]; then
                passed_tests=$((passed_tests + 1))
            else
                failed_tests=$((failed_tests + 1))
            fi
            
            # Show test summary
            local test_name=$(basename "$report_file" _report.json)
            if [[ "$overall_passed" == "true" ]]; then
                print_success "Test $test_name: PASSED"
            else
                print_error "Test $test_name: FAILED"
            fi
        fi
    done
    
    print_info "Test Summary: $passed_tests/$total_tests passed"
    
    if [[ $failed_tests -gt 0 ]]; then
        print_error "$failed_tests test(s) failed"
        return 1
    else
        print_success "All tests passed!"
        return 0
    fi
}

# Main execution
main() {
    local start_time=$(date +%s)
    
    # Check dependencies
    check_dependencies
    
    # Run tests
    if [[ "$USE_DOCKER" == "true" ]]; then
        run_docker_test
    else
        run_local_test
    fi
    
    local test_exit_code=$?
    
    # Summarize results
    summarize_results
    local summary_exit_code=$?
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    print_info "Total execution time: ${duration}s"
    
    # Exit with appropriate code
    if [[ $test_exit_code -eq 0 && $summary_exit_code -eq 0 ]]; then
        print_success "Virtual test environment completed successfully!"
        exit 0
    else
        print_error "Virtual test environment completed with errors"
        exit 1
    fi
}

# Run main function
main "$@"