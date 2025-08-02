#!/bin/bash
# Multi-Sensor Recording System - Application Launcher
# This script automatically detects the environment and runs the app appropriately

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Multi-Sensor Recording System - Application Launcher${NC}"
echo "============================================================"

# Check if conda environment exists
if ! conda env list | grep -q "gsr-env"; then
    echo -e "${RED}Error: gsr-env conda environment not found${NC}"
    echo "Please run: conda env create -f ../environment.yml"
    exit 1
fi

# Activate conda environment
echo -e "${YELLOW}Activating conda environment...${NC}"
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate gsr-env

# Change to source directory
cd "$(dirname "$0")/src"

# Check for display availability
if [ -n "$DISPLAY" ]; then
    echo -e "${GREEN}Display server detected: $DISPLAY${NC}"
    echo "Running with GUI..."
    python main.py
elif command -v xvfb-run &> /dev/null; then
    echo -e "${YELLOW}No display server found, using virtual display (xvfb)${NC}"
    echo "Running with virtual display..."
    xvfb-run -a python main.py
else
    echo -e "${YELLOW}No display server or xvfb found, running in headless mode${NC}"
    echo "Running without GUI..."
    export MSR_HEADLESS=true
    python main.py
fi