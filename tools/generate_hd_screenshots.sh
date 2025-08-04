#!/bin/bash

# High-Definition Screenshot Generation Script
# Multi-Sensor Recording System - Android Application
#
# This script automates the generation of high-definition screenshots
# for the Android application and organizes them for documentation.
#
# Usage:
#   ./generate_hd_screenshots.sh [options]
#
# Options:
#   --quick       Generate only essential screenshots (faster)
#   --pull-only   Only pull existing screenshots from device
#   --clean       Clean local screenshots directory before generating
#   --help        Show this help message
#
# Requirements:
#   - Android device or emulator connected via ADB
#   - Device unlocked and developer options enabled
#   - Android app built and test APK installed

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SCREENSHOTS_DIR="$PROJECT_ROOT/screenshots"
DEVICE_SCREENSHOTS_PATH="/sdcard/Android/data/com.multisensor.recording/files/Pictures/screenshots"
BUILD_SCREENSHOTS_DIR="$PROJECT_ROOT/AndroidApp/build/screenshots"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
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

# Function to show help
show_help() {
    cat << EOF
High-Definition Screenshot Generation Script
Multi-Sensor Recording System - Android Application

USAGE:
    $0 [options]

OPTIONS:
    --quick       Generate only essential screenshots (faster execution)
    --pull-only   Only pull existing screenshots from device (no generation)
    --clean       Clean local screenshots directory before generating new ones
    --help        Show this help message and exit

DESCRIPTION:
    This script automates the generation of high-definition screenshots for all major
    screens and UI states in the Multi-Sensor Recording Android application.

REQUIREMENTS:
    - Android device or emulator connected via ADB
    - Device unlocked with developer options enabled
    - USB debugging enabled
    - Android app built with test APK installed

OUTPUT:
    Screenshots are saved to: $SCREENSHOTS_DIR
    Organized by timestamp and screen type for easy documentation use.

EXAMPLES:
    $0                    # Generate all screenshots
    $0 --quick           # Generate essential screenshots only
    $0 --clean --quick   # Clean directory and generate essential screenshots
    $0 --pull-only       # Pull existing screenshots from device

EOF
}

# Function to check ADB connection
check_adb_connection() {
    print_info "Checking ADB connection..."
    
    if ! command -v adb &> /dev/null; then
        print_error "ADB not found in PATH. Please install Android SDK tools."
        exit 1
    fi
    
    local device_count=$(adb devices | grep -c "device$" || true)
    
    if [ "$device_count" -eq 0 ]; then
        print_error "No Android devices connected. Please connect a device or start an emulator."
        print_info "Make sure USB debugging is enabled on your device."
        exit 1
    elif [ "$device_count" -gt 1 ]; then
        print_warning "Multiple devices connected. Using the first available device."
    fi
    
    print_success "ADB connection verified"
}

# Function to check if app is installed
check_app_installation() {
    print_info "Checking if app and test APK are installed..."
    
    local app_installed=$(adb shell pm list packages | grep -c "com.multisensor.recording" || true)
    
    if [ "$app_installed" -eq 0 ]; then
        print_error "App not installed on device. Please build and install the app first."
        print_info "Run: ./gradlew :AndroidApp:installDebug"
        exit 1
    fi
    
    print_success "App installation verified"
}

# Function to build APKs if needed
build_apks() {
    print_info "Building Android APKs..."
    
    cd "$PROJECT_ROOT"
    
    if ! ./gradlew :AndroidApp:assembleDebug :AndroidApp:assembleDebugAndroidTest; then
        print_error "Failed to build APKs"
        exit 1
    fi
    
    print_success "APKs built successfully"
}

# Function to install APKs
install_apks() {
    print_info "Installing APKs to device..."
    
    cd "$PROJECT_ROOT"
    
    if ! ./gradlew :AndroidApp:installDebug :AndroidApp:installDebugAndroidTest; then
        print_error "Failed to install APKs"
        exit 1
    fi
    
    print_success "APKs installed successfully"
}

# Function to create screenshots directory
create_screenshots_dir() {
    if [ "$CLEAN" = true ]; then
        print_info "Cleaning existing screenshots directory..."
        rm -rf "$SCREENSHOTS_DIR"
    fi
    
    mkdir -p "$SCREENSHOTS_DIR"
    mkdir -p "$BUILD_SCREENSHOTS_DIR"
    print_info "Screenshots directory ready: $SCREENSHOTS_DIR"
}

# Function to generate screenshots
generate_screenshots() {
    print_info "Generating high-definition screenshots..."
    print_info "Please ensure your device is unlocked and the screen is on"
    
    cd "$PROJECT_ROOT"
    
    local test_class="com.multisensor.recording.ScreenshotAutomationTest"
    local test_method=""
    
    if [ "$QUICK" = true ]; then
        print_info "Running quick screenshot generation..."
        test_method="#captureAllMainScreens"
    else
        print_info "Running comprehensive screenshot generation..."
    fi
    
    # Run the screenshot test
    if ! adb shell am instrument -w \
        -e class "${test_class}${test_method}" \
        com.multisensor.recording.test/androidx.test.runner.AndroidJUnitRunner; then
        print_error "Screenshot generation failed"
        exit 1
    fi
    
    print_success "Screenshot generation completed"
}

# Function to pull screenshots from device
pull_screenshots() {
    print_info "Pulling screenshots from device..."
    
    # Check if screenshots directory exists on device
    if ! adb shell "test -d $DEVICE_SCREENSHOTS_PATH"; then
        print_warning "No screenshots found on device at: $DEVICE_SCREENSHOTS_PATH"
        return 1
    fi
    
    # Create timestamp subdirectory for organization
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local local_dir="$SCREENSHOTS_DIR/android_app_screenshots_$timestamp"
    mkdir -p "$local_dir"
    
    # Pull screenshots
    if adb pull "$DEVICE_SCREENSHOTS_PATH/." "$local_dir/"; then
        print_success "Screenshots pulled to: $local_dir"
        
        # Count screenshots
        local screenshot_count=$(find "$local_dir" -name "*.png" | wc -l)
        print_success "Total screenshots: $screenshot_count"
        
        # List screenshots
        print_info "Generated screenshots:"
        find "$local_dir" -name "*.png" -exec basename {} \; | sort
        
    else
        print_error "Failed to pull screenshots from device"
        return 1
    fi
}

# Function to create documentation index
create_documentation_index() {
    local latest_dir=$(find "$SCREENSHOTS_DIR" -type d -name "android_app_screenshots_*" | sort | tail -1)
    
    if [ -z "$latest_dir" ]; then
        return 0
    fi
    
    local index_file="$latest_dir/README.md"
    
    cat > "$index_file" << EOF
# Android Application Screenshots

Generated on: $(date)
Device: $(adb shell getprop ro.product.model 2>/dev/null || echo "Unknown")
Android Version: $(adb shell getprop ro.build.version.release 2>/dev/null || echo "Unknown")

## Screenshot Collection

This directory contains high-definition screenshots of the Multi-Sensor Recording Android application, capturing all major screens and UI states.

### Screenshots

EOF
    
    # Add screenshot entries
    find "$latest_dir" -name "*.png" -exec basename {} \; | sort | while read screenshot; do
        local description=$(echo "$screenshot" | sed 's/^[0-9]*_//' | sed 's/_/ /g' | sed 's/.png$//')
        echo "- \`$screenshot\` - ${description^}" >> "$index_file"
    done
    
    cat >> "$index_file" << EOF

### Application Features Captured

1. **Main Interface** - Initial app state and navigation
2. **Recording Screen** - Recording controls and status indicators
3. **Devices Screen** - Device connection and management
4. **Calibration Screen** - Camera calibration interface
5. **Files Screen** - Data management and export
6. **Settings** - Configuration and preferences
7. **Navigation States** - Drawer and bottom navigation
8. **Material Design** - UI components and theming

### Usage

These screenshots can be used for:
- Documentation and user guides
- App store listings and marketing materials
- UI/UX design reference
- Bug reporting and issue tracking
- Development team communication

EOF
    
    print_success "Documentation index created: $index_file"
}

# Main execution
main() {
    # Parse command line arguments
    QUICK=false
    PULL_ONLY=false
    CLEAN=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --quick)
                QUICK=true
                shift
                ;;
            --pull-only)
                PULL_ONLY=true
                shift
                ;;
            --clean)
                CLEAN=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    print_info "Starting HD Screenshot Generation for Android App"
    print_info "Project: Multi-Sensor Recording System"
    
    # Create screenshots directory
    create_screenshots_dir
    
    if [ "$PULL_ONLY" = false ]; then
        # Pre-flight checks
        check_adb_connection
        check_app_installation
        
        # Build and install if needed
        build_apks
        install_apks
        
        # Generate screenshots
        generate_screenshots
        
        # Wait a moment for files to be written
        sleep 2
    fi
    
    # Pull screenshots from device
    if pull_screenshots; then
        create_documentation_index
        print_success "HD Screenshot generation completed successfully!"
        print_info "Screenshots location: $SCREENSHOTS_DIR"
    else
        print_error "Failed to retrieve screenshots from device"
        exit 1
    fi
}

# Run main function
main "$@"