# Headless Operation Guide

## Problem
The Multi-Sensor Recording System application uses PyQt5 for its GUI interface. In headless environments (servers, Docker containers, CI/CD pipelines, SSH sessions without X11 forwarding), the application would crash with errors like:

```
qt.qpa.xcb: could not connect to display
This application failed to start because no Qt platform plugin could be initialized.
```

## Solutions

### 1. Virtual Display (Recommended for Full Functionality)
Use `xvfb-run` to create a virtual X11 display server:

```bash
# Install xvfb (if not already installed)
sudo apt-get install xvfb

# Run the application with virtual display
cd PythonApp
xvfb-run -a python src/main.py
```

### 2. Headless Mode (No GUI)
Set the `MSR_HEADLESS` environment variable to run without GUI:

```bash
cd PythonApp
export MSR_HEADLESS=true
python src/main.py
```

### 3. Automatic Launcher Script (Easiest)
Use the provided launcher script that automatically detects your environment:

```bash
cd PythonApp
./run_app.sh
```

The script will:
- Check if a display is available
- Use virtual display if xvfb is available
- Fall back to headless mode if necessary

## Environment Setup

### Prerequisites
1. **Conda Environment**: Install dependencies first
   ```bash
   conda env create -f environment.yml
   conda activate gsr-env
   ```

2. **For Virtual Display**: Install xvfb
   ```bash
   sudo apt-get install xvfb
   ```

### Environment Variables
- `MSR_HEADLESS=true`: Forces headless mode (no GUI)
- `MSR_LOG_LEVEL`: Controls logging verbosity (DEBUG, INFO, WARNING, ERROR)
- `QT_QPA_PLATFORM=offscreen`: Forces Qt to use offscreen rendering

## Troubleshooting

### Common Errors and Solutions

1. **"could not connect to display"**
   - Use: `xvfb-run -a python src/main.py`
   - Or: `export MSR_HEADLESS=true && python src/main.py`

2. **"no Qt platform plugin could be initialized"**
   - Install Qt platform packages: `sudo apt-get install qt5-default`
   - Use virtual display: `xvfb-run -a python src/main.py`

3. **"ModuleNotFoundError: No module named 'PyQt5'"**
   - Activate conda environment: `conda activate gsr-env`
   - Or install dependencies: `conda env create -f environment.yml`

### Verifying Setup
Test different scenarios:

```bash
# Test with virtual display
xvfb-run -a python src/main.py

# Test headless mode
export MSR_HEADLESS=true
python src/main.py

# Test automatic detection
./run_app.sh
```

## CI/CD Integration

For automated testing and deployment:

```bash
# In your CI/CD pipeline
export MSR_HEADLESS=true
conda activate gsr-env
python PythonApp/src/main.py

# Or with virtual display for GUI testing
apt-get install -y xvfb
xvfb-run -a python PythonApp/src/main.py
```

## Docker Support

In Dockerfile:
```dockerfile
# Install xvfb for GUI applications
RUN apt-get update && apt-get install -y xvfb

# Set headless mode by default
ENV MSR_HEADLESS=true

# Use virtual display when needed
CMD ["xvfb-run", "-a", "python", "PythonApp/src/main.py"]
```