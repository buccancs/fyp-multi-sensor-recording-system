#!/bin/bash
# Cross-Platform Setup Script for Multi-Sensor Recording System
# Supports Linux and macOS development environments

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
SKIP_VALIDATION=false
FORCE_REINSTALL=false
VERBOSE=false
USE_CONDA=true
CONDA_ENV_NAME="thermal-env"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-validation)
            SKIP_VALIDATION=true
            shift
            ;;
        --force-reinstall)
            FORCE_REINSTALL=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --use-venv)
            USE_CONDA=false
            shift
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --skip-validation    Skip build validation tests"
            echo "  --force-reinstall    Force reinstall of all components"
            echo "  --verbose           Enable verbose output"
            echo "  --use-venv          Use Python venv instead of conda"
            echo "  --help              Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option $1"
            exit 1
            ;;
    esac
done

echo -e "${GREEN}=== Multi-Sensor Recording System - Cross-Platform Setup ===${NC}"
echo -e "${YELLOW}Platform: $(uname -s) $(uname -m)${NC}"

# Detect OS
OS=$(uname -s)
case "$OS" in
    Linux*)
        PLATFORM="linux"
        MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
        MINICONDA_INSTALLER="Miniconda3-latest-Linux-x86_64.sh"
        ;;
    Darwin*)
        PLATFORM="macos"
        if [[ $(uname -m) == "arm64" ]]; then
            MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh"
            MINICONDA_INSTALLER="Miniconda3-latest-MacOSX-arm64.sh"
        else
            MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh"
            MINICONDA_INSTALLER="Miniconda3-latest-MacOSX-x86_64.sh"
        fi
        ;;
    *)
        echo -e "${RED}Unsupported platform: $OS${NC}"
        echo "This script supports Linux and macOS. For Windows, use setup_dev_env.ps1"
        exit 1
        ;;
esac

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

# Function to check Java version
check_java() {
    echo -e "\n${BLUE}1. Checking Java installation...${NC}"
    
    if ! command_exists java; then
        echo -e "${RED}✗ Java not found. Please install Java 17 or 21.${NC}"
        echo "  Ubuntu/Debian: sudo apt install openjdk-17-jdk"
        echo "  macOS: brew install openjdk@17"
        return 1
    fi
    
    JAVA_VERSION=$(java -version 2>&1 | head -n1 | cut -d'"' -f2 | cut -d'.' -f1)
    if [[ $JAVA_VERSION -ge 17 && $JAVA_VERSION -le 21 ]]; then
        echo -e "${GREEN}✓ Java $JAVA_VERSION detected${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠ Java $JAVA_VERSION detected - recommend Java 17 or 21${NC}"
        return 0
    fi
}

# Function to setup Python environment
setup_python_env() {
    echo -e "\n${BLUE}2. Setting up Python environment...${NC}"
    
    if [[ "$USE_CONDA" == "true" ]]; then
        setup_conda_env
    else
        setup_venv
    fi
}

# Function to setup conda environment
setup_conda_env() {
    local conda_path="$HOME/miniconda3"
    
    # Check if conda exists
    if [[ "$FORCE_REINSTALL" == "true" ]] || ! command_exists conda; then
        echo -e "${YELLOW}Installing Miniconda...${NC}"
        
        # Download and install miniconda
        curl -L -o "/tmp/$MINICONDA_INSTALLER" "$MINICONDA_URL"
        bash "/tmp/$MINICONDA_INSTALLER" -b -p "$conda_path"
        rm "/tmp/$MINICONDA_INSTALLER"
        
        # Initialize conda
        source "$conda_path/etc/profile.d/conda.sh"
        conda init bash
        
        echo -e "${GREEN}✓ Miniconda installed successfully${NC}"
    else
        echo -e "${GREEN}✓ Conda already installed${NC}"
        source "$HOME/miniconda3/etc/profile.d/conda.sh"
    fi
    
    # Create or update environment
    if [[ "$FORCE_REINSTALL" == "true" ]] || ! conda env list | grep -q "$CONDA_ENV_NAME"; then
        echo -e "${YELLOW}Creating conda environment from environment.yml...${NC}"
        conda env create -f environment.yml --name "$CONDA_ENV_NAME" || \
        conda env update -f environment.yml --name "$CONDA_ENV_NAME"
    else
        echo -e "${YELLOW}Updating existing conda environment...${NC}"
        conda env update -f environment.yml --name "$CONDA_ENV_NAME"
    fi
    
    echo -e "${GREEN}✓ Conda environment '$CONDA_ENV_NAME' ready${NC}"
    echo -e "${BLUE}  Activate with: conda activate $CONDA_ENV_NAME${NC}"
}

# Function to setup Python venv
setup_venv() {
    local venv_path="./venv"
    
    if ! command_exists python3; then
        echo -e "${RED}✗ Python 3 not found. Please install Python 3.8+${NC}"
        return 1
    fi
    
    PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    echo -e "${GREEN}✓ Python $PYTHON_VERSION detected${NC}"
    
    if [[ "$FORCE_REINSTALL" == "true" ]] && [[ -d "$venv_path" ]]; then
        echo -e "${YELLOW}Removing existing venv...${NC}"
        rm -rf "$venv_path"
    fi
    
    if [[ ! -d "$venv_path" ]]; then
        echo -e "${YELLOW}Creating Python virtual environment...${NC}"
        python3 -m venv "$venv_path"
    fi
    
    source "$venv_path/bin/activate"
    pip install --upgrade pip
    
    # Install from requirements if available, otherwise from environment.yml
    if [[ -f "requirements.txt" ]]; then
        pip install -r requirements.txt
    else
        echo -e "${YELLOW}Installing packages from environment.yml (pip fallback)...${NC}"
        # Extract pip dependencies from environment.yml
        grep -A 100 "- pip:" environment.yml | grep "^[[:space:]]*-" | sed 's/^[[:space:]]*- //' | while read package; do
            if [[ -n "$package" ]]; then
                pip install "$package" || echo -e "${YELLOW}Warning: Failed to install $package${NC}"
            fi
        done
    fi
    
    echo -e "${GREEN}✓ Python venv ready at $venv_path${NC}"
    echo -e "${BLUE}  Activate with: source $venv_path/bin/activate${NC}"
}

# Function to setup Gradle
setup_gradle() {
    echo -e "\n${BLUE}3. Setting up Gradle...${NC}"
    
    if [[ -f "./gradlew" ]]; then
        chmod +x ./gradlew
        echo -e "${GREEN}✓ Gradle wrapper ready${NC}"
    else
        echo -e "${RED}✗ Gradle wrapper not found${NC}"
        return 1
    fi
}

# Function to validate setup
validate_setup() {
    if [[ "$SKIP_VALIDATION" == "true" ]]; then
        echo -e "\n${YELLOW}Skipping validation as requested${NC}"
        return 0
    fi
    
    echo -e "\n${BLUE}4. Validating setup...${NC}"
    
    # Test Gradle
    echo -e "${YELLOW}Testing Gradle build...${NC}"
    if ./gradlew tasks > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Gradle working${NC}"
    else
        echo -e "${RED}✗ Gradle test failed${NC}"
        return 1
    fi
    
    # Test Python environment
    echo -e "${YELLOW}Testing Python environment...${NC}"
    if [[ "$USE_CONDA" == "true" ]]; then
        conda activate "$CONDA_ENV_NAME"
        python -c "import sys; print(f'Python {sys.version}')"
    else
        source ./venv/bin/activate
        python -c "import sys; print(f'Python {sys.version}')"
    fi
    
    echo -e "${GREEN}✓ Setup validation completed${NC}"
}

# Function to print next steps
print_next_steps() {
    echo -e "\n${GREEN}=== Setup Complete! ===${NC}"
    echo -e "${BLUE}Next steps:${NC}"
    
    if [[ "$USE_CONDA" == "true" ]]; then
        echo -e "1. Activate environment: ${YELLOW}conda activate $CONDA_ENV_NAME${NC}"
    else
        echo -e "1. Activate environment: ${YELLOW}source ./venv/bin/activate${NC}"
    fi
    
    echo -e "2. Build project: ${YELLOW}./gradlew assembleAll${NC}"
    echo -e "3. Run Python app: ${YELLOW}./gradlew PythonApp:runDesktopApp${NC}"
    echo -e "4. Run tests: ${YELLOW}./gradlew pythonTest${NC}"
    
    echo -e "\n${BLUE}IDE Setup:${NC}"
    echo -e "- Set Python interpreter to your environment's python executable"
    if [[ "$USE_CONDA" == "true" ]]; then
        echo -e "  Conda: $HOME/miniconda3/envs/$CONDA_ENV_NAME/bin/python"
    else
        echo -e "  Venv: $(pwd)/venv/bin/python"
    fi
}

# Main execution flow
main() {
    # Change to script directory
    cd "$(dirname "$0")"
    
    check_java || exit 1
    setup_python_env || exit 1
    setup_gradle || exit 1
    validate_setup || exit 1
    print_next_steps
    
    echo -e "\n${GREEN}🎉 Development environment setup completed successfully!${NC}"
}

# Run main function
main "$@"