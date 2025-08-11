#!/bin/bash

# Virtual Test Environment Setup Script
# Provides automated setup for development and testing

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
VENV_DIR="$PROJECT_ROOT/.venv"
PYTHON_VERSION="3.10"

# Functions
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

check_python_version() {
    log_info "Checking Python version..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        log_error "Python not found. Please install Python $PYTHON_VERSION or higher."
        exit 1
    fi
    
    PYTHON_VER=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
    log_info "Found Python $PYTHON_VER"
    
    # Check if version is at least 3.10
    if [[ "$(printf '%s\n' "$PYTHON_VER" "3.10" | sort -V | head -n1)" != "3.10" ]]; then
        log_error "Python $PYTHON_VERSION or higher is required. Found: $PYTHON_VER"
        exit 1
    fi
    
    log_success "Python version check passed"
}

setup_virtual_environment() {
    log_info "Setting up Python virtual environment..."
    
    if [[ ! -d "$VENV_DIR" ]]; then
        log_info "Creating virtual environment at $VENV_DIR"
        $PYTHON_CMD -m venv "$VENV_DIR"
    else
        log_info "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip
    log_info "Upgrading pip..."
    pip install --upgrade pip setuptools wheel
    
    log_success "Virtual environment setup complete"
}

install_dependencies() {
    log_info "Installing project dependencies..."
    
    # Install main project in development mode
    cd "$PROJECT_ROOT"
    pip install -e .
    
    # Install development dependencies
    log_info "Installing development dependencies..."
    pip install pytest pytest-asyncio pytest-cov psutil numpy opencv-python-headless
    
    # Install optional dependencies for virtual testing
    log_info "Installing virtual test environment dependencies..."
    pip install matplotlib pillow
    
    log_success "Dependencies installed successfully"
}

create_ide_configuration() {
    log_info "Creating IDE configuration files..."
    
    # Create VS Code configuration
    mkdir -p "$PROJECT_ROOT/.vscode"
    
    # Launch configuration for VS Code
    cat > "$PROJECT_ROOT/.vscode/launch.json" << 'EOF'
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Virtual Test Environment - Quick Test",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/tests/integration/virtual_environment/quick_test.py",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}/tests/integration/virtual_environment"
        },
        {
            "name": "Virtual Test Environment - Test Runner",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/tests/integration/virtual_environment/test_runner.py",
            "args": ["--scenario", "quick", "--devices", "2", "--duration", "0.5"],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}/tests/integration/virtual_environment"
        },
        {
            "name": "Run Pytest - Virtual Environment",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["tests/integration/virtual_environment/", "-v"],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        }
    ]
}
EOF
    
    # VS Code settings
    cat > "$PROJECT_ROOT/.vscode/settings.json" << 'EOF'
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "tests/"
    ],
    "python.testing.unittestEnabled": false,
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".pytest_cache": true,
        "htmlcov": true,
        ".coverage": true
    }
}
EOF
    
    log_success "IDE configuration created"
}

run_verification_tests() {
    log_info "Running verification tests..."
    
    cd "$PROJECT_ROOT"
    
    # Test imports
    log_info "Testing virtual environment imports..."
    python -c "from tests.integration.virtual_environment import VirtualTestConfig, VirtualTestRunner, VirtualTestScenario; print('✓ Imports successful')"
    
    # Run basic pytest tests
    log_info "Running basic pytest tests..."
    python -m pytest tests/integration/virtual_environment/test_pytest_integration.py::TestPytestIntegration::test_synthetic_data_deterministic -v
    
    # Test synthetic data generation
    log_info "Testing synthetic data generation..."
    python -c "
from tests.integration.virtual_environment import SyntheticDataGenerator
gen = SyntheticDataGenerator(seed=42)
gsr = gen.generate_gsr_batch(10)
rgb = gen.generate_rgb_frame()
thermal = gen.generate_thermal_frame()
print(f'✓ Generated {len(gsr)} GSR samples, RGB frame ({len(rgb)} bytes), thermal frame ({len(thermal)} bytes)')
"
    
    # Test configuration validation
    log_info "Testing configuration validation..."
    python -c "
from tests.integration.virtual_environment import VirtualTestConfig
import tempfile
with tempfile.TemporaryDirectory() as temp_dir:
    config = VirtualTestConfig(
        test_name='verification_test',
        device_count=2,
        test_duration_minutes=0.1,
        output_directory=temp_dir
    )
    issues = config.validate()
    if issues:
        raise Exception(f'Configuration validation failed: {issues}')
    print('✓ Configuration validation passed')
"
    
    log_success "All verification tests passed"
}

create_quick_test_script() {
    log_info "Creating quick test script..."
    
    cat > "$PROJECT_ROOT/quick_virtual_test.sh" << 'EOF'
#!/bin/bash

# Quick Virtual Test Script
# Run a fast virtual test for development verification

cd "$(dirname "$0")/tests/integration/virtual_environment"

echo "🚀 Running quick virtual test..."
python test_runner.py --scenario quick --devices 2 --duration 0.5 --verbose

echo ""
echo "📊 Test completed. Check test_results/ directory for outputs."
EOF
    
    chmod +x "$PROJECT_ROOT/quick_virtual_test.sh"
    
    log_success "Quick test script created at $PROJECT_ROOT/quick_virtual_test.sh"
}

show_usage_instructions() {
    log_success "🎉 Virtual Test Environment setup complete!"
    echo ""
    echo -e "${BLUE}📋 Usage Instructions:${NC}"
    echo ""
    echo "1. Activate virtual environment:"
    echo "   source .venv/bin/activate"
    echo ""
    echo "2. Run quick test:"
    echo "   ./quick_virtual_test.sh"
    echo ""
    echo "3. Run specific tests:"
    echo "   cd tests/integration/virtual_environment"
    echo "   python test_runner.py --scenario quick --devices 3 --duration 1.0"
    echo ""
    echo "4. Run pytest suite:"
    echo "   pytest tests/integration/virtual_environment/ -v"
    echo ""
    echo "5. Run performance tests:"
    echo "   pytest tests/integration/virtual_environment/test_performance_benchmarks.py -v -m performance"
    echo ""
    echo "6. Use Docker:"
    echo "   cd tests/integration/virtual_environment"
    echo "   docker build -t gsr-virtual-test -f Dockerfile ../../.."
    echo "   docker run --rm gsr-virtual-test --scenario quick --devices 2"
    echo ""
    echo -e "${BLUE}🔧 Development:${NC}"
    echo "- VS Code launch configurations are available in .vscode/launch.json"
    echo "- Run 'code .' to open project in VS Code with proper configuration"
    echo ""
    echo -e "${BLUE}📚 Documentation:${NC}"
    echo "- See tests/integration/virtual_environment/README.md for detailed usage"
    echo "- Check IMPLEMENTATION_SUMMARY.md for technical details"
}

# Main execution
main() {
    echo "🔧 Virtual Test Environment Setup"
    echo "================================="
    echo ""
    
    # Parse command line arguments
    SKIP_DEPS=false
    SKIP_VERIFICATION=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-deps)
                SKIP_DEPS=true
                shift
                ;;
            --skip-verification)
                SKIP_VERIFICATION=true
                shift
                ;;
            --help|-h)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --skip-deps         Skip dependency installation"
                echo "  --skip-verification Skip verification tests"
                echo "  --help, -h          Show this help message"
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Setup steps
    check_python_version
    setup_virtual_environment
    
    if [[ "$SKIP_DEPS" != true ]]; then
        install_dependencies
    else
        log_warning "Skipping dependency installation"
    fi
    
    create_ide_configuration
    create_quick_test_script
    
    if [[ "$SKIP_VERIFICATION" != true ]]; then
        run_verification_tests
    else
        log_warning "Skipping verification tests"
    fi
    
    show_usage_instructions
}

# Run main function
main "$@"