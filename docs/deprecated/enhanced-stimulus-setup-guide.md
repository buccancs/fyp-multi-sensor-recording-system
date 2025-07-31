# Enhanced Stimulus Controller Setup Guide

## Overview

This guide provides comprehensive instructions for setting up the Enhanced Stimulus Controller with PsychoPy-inspired improvements, including VLC backend support, enhanced timing precision, and performance monitoring.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation Steps](#installation-steps)
3. [VLC Backend Setup](#vlc-backend-setup)
4. [Dependency Installation](#dependency-installation)
5. [Configuration and Testing](#configuration-and-testing)
6. [Troubleshooting](#troubleshooting)
7. [Performance Optimization](#performance-optimization)
8. [Advanced Features](#advanced-features)

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10/11, macOS 10.14+, or Linux Ubuntu 18.04+
- **Python**: 3.7 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space for dependencies
- **Graphics**: DirectX 11 compatible or OpenGL 3.3 support

### Recommended Requirements
- **RAM**: 16GB for optimal performance during simultaneous recording
- **CPU**: Multi-core processor (4+ cores) for concurrent video processing
- **Graphics**: Dedicated GPU with hardware acceleration support
- **Storage**: SSD for improved video loading and recording performance

### Supported Video Formats

#### Qt Multimedia Backend (Default)
- **Primary**: MP4 (H.264), AVI, MOV, WMV
- **Additional**: MKV, M4V, 3GP
- **Limitations**: Depends on system codecs

#### VLC Backend (Enhanced)
- **All Qt formats** plus:
- **Extended**: FLV, WebM, OGV, MPG, MPEG, TS, MTS, M2TS
- **Advantages**: Better codec compatibility, hardware acceleration

## Installation Steps

### Step 1: Python Environment Setup

```bash
# Create virtual environment (recommended)
python -m venv enhanced_stimulus_env

# Activate environment
# Windows:
enhanced_stimulus_env\Scripts\activate
# macOS/Linux:
source enhanced_stimulus_env/bin/activate

# Upgrade pip
python -m pip install --upgrade pip
```

### Step 2: Core Dependencies

```bash
# Install PyQt5 with multimedia support
pip install PyQt5 PyQt5-tools

# Install additional dependencies
pip install numpy opencv-python pillow

# Install optional performance monitoring
pip install psutil memory-profiler
```

### Step 3: Enhanced Features Dependencies

```bash
# For enhanced timing precision
pip install python-dateutil

# For performance monitoring
pip install matplotlib seaborn  # Optional: for performance graphs

# For advanced logging
pip install colorlog  # Optional: colored console output
```

## VLC Backend Setup

### Step 1: Install VLC Media Player

#### Windows
1. Download VLC from: https://www.videolan.org/vlc/
2. Run installer with **default settings**
3. Ensure VLC is added to system PATH
4. Verify installation: Open Command Prompt and run `vlc --version`

#### macOS
```bash
# Using Homebrew (recommended)
brew install --cask vlc

# Or download from website
# https://www.videolan.org/vlc/download-macosx.html
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install vlc

# For additional codecs
sudo apt install ubuntu-restricted-extras
```

### Step 2: Install Python VLC Bindings

```bash
# Install python-vlc
pip install python-vlc

# Verify installation
python -c "import vlc; print('VLC Python bindings installed successfully')"
```

**Note**: If you encounter `FileNotFoundError: Could not find module 'libvlc.dll'`, this means VLC Media Player is not installed. The python-vlc library requires the actual VLC application to be installed on your system.

### Step 3: Verify VLC Backend

1. Launch the Enhanced Stimulus Controller
2. Check status bar for "VLC Backend: Available"
3. Use **Stimulus → Switch Video Backend** menu to test switching
4. Load a test video and verify playback with both backends

## Dependency Installation

### Complete Installation Script

Create `install_enhanced_dependencies.py`:

```python
#!/usr/bin/env python3
"""
Enhanced Stimulus Controller Dependency Installer
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✓ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError:
        print(f"✗ Failed to install {package}")
        return False

def check_vlc_availability():
    """Check if VLC is available."""
    try:
        import vlc
        print("✓ VLC backend available")
        return True
    except ImportError:
        print("! VLC backend not available - install python-vlc for enhanced codec support")
        return False

def main():
    """Main installation function."""
    print("Enhanced Stimulus Controller - Dependency Installer")
    print("=" * 50)
    
    # Core dependencies
    core_packages = [
        "PyQt5",
        "PyQt5-tools", 
        "numpy",
        "opencv-python",
        "pillow"
    ]
    
    # Enhanced features
    enhanced_packages = [
        "python-vlc",
        "python-dateutil",
        "psutil",
        "memory-profiler"
    ]
    
    # Optional packages
    optional_packages = [
        "matplotlib",
        "seaborn",
        "colorlog"
    ]
    
    print("\nInstalling core dependencies...")
    for package in core_packages:
        install_package(package)
    
    print("\nInstalling enhanced features...")
    for package in enhanced_packages:
        install_package(package)
    
    print("\nInstalling optional packages...")
    for package in optional_packages:
        install_package(package)
    
    print("\nVerifying installation...")
    check_vlc_availability()
    
    print("\nInstallation complete!")
    print("Run the Enhanced Stimulus Controller to verify all features are working.")

if __name__ == "__main__":
    main()
```

Run the installer:
```bash
python install_enhanced_dependencies.py
```

## Configuration and Testing

### Step 1: Initial Configuration

1. **Launch Application**:
   ```bash
   python PythonApp/src/main.py
   ```

2. **Verify Enhanced Features**:
   - Check toolbar for backend status and performance indicator
   - Verify status bar shows timing precision
   - Confirm VLC availability in status

3. **Test Basic Functionality**:
   - Load a test video using "Load Stimulus" button
   - Test playback with both Qt and VLC backends
   - Verify full-screen mode and keyboard shortcuts

### Step 2: Timing Precision Test

1. **Access Timing Test**:
   - Menu: **Stimulus → Test Timing Precision**
   - Review timing calibration results
   - Verify clock offset is within acceptable range (< 5ms)

2. **Expected Results**:
   ```
   Timing Precision Test:
   Clock Offset: ±2.341ms
   System Time: 1690538765.123456
   Performance Time: 12345.678901
   Corrected Time: 1690538765.121115
   ```

### Step 3: Performance Monitoring Test

1. **Enable Performance Monitoring**:
   - Menu: **Stimulus → Performance Monitor** (check to enable)
   - Observe performance indicator in toolbar
   - Monitor frame timing during video playback

2. **Performance Metrics**:
   - **Green (90-100%)**: Excellent performance
   - **Yellow (70-89%)**: Good performance
   - **Red (<70%)**: Performance issues detected

### Step 4: Backend Switching Test

1. **Test Qt Backend**:
   - Load MP4 video file
   - Verify playback quality and controls
   - Note any codec limitations

2. **Test VLC Backend**:
   - Use **Stimulus → Switch Video Backend**
   - Test same video with VLC backend
   - Try additional formats (WebM, FLV, etc.)

3. **Compare Performance**:
   - Monitor performance indicators
   - Test full-screen mode with both backends
   - Verify keyboard shortcuts work correctly

## Troubleshooting

### Common Issues and Solutions

#### 1. VLC Backend Not Available

**Symptoms**:
- Status bar shows "VLC Backend: Not Available"
- Cannot switch to VLC backend
- Limited video format support

**Solutions**:
```bash
# Check VLC installation
vlc --version

# Reinstall python-vlc
pip uninstall python-vlc
pip install python-vlc

# Verify VLC in PATH (Windows)
where vlc

# Test VLC Python bindings
python -c "import vlc; print(vlc.Instance())"
```

#### 2. Video Playback Issues

**Symptoms**:
- DirectShow errors on Windows
- "Resource error - file not found or corrupted"
- Video loads but doesn't play

**Solutions**:
1. **Try VLC Backend**:
   - Switch backend via menu
   - VLC has better codec support

2. **Check Video Format**:
   ```python
   # Supported formats check
   from gui.enhanced_stimulus_controller import CodecInfo
   codec_info = CodecInfo()
   print("Qt supported:", codec_info.qt_supported)
   print("VLC supported:", codec_info.vlc_supported)
   ```

3. **Install Additional Codecs**:
   ```bash
   # Windows: Install K-Lite Codec Pack
   # macOS: Install additional QuickTime codecs
   # Linux: Install ubuntu-restricted-extras
   ```

#### 3. Performance Issues

**Symptoms**:
- Frame drops during playback
- Performance indicator shows red
- Stuttering video playback

**Solutions**:
1. **Check System Resources**:
   ```bash
   # Monitor CPU and memory usage
   python -c "import psutil; print(f'CPU: {psutil.cpu_percent()}%, RAM: {psutil.virtual_memory().percent}%')"
   ```

2. **Optimize Video Settings**:
   - Use lower resolution videos for testing
   - Prefer MP4 with H.264 codec
   - Close unnecessary applications

3. **Hardware Acceleration**:
   - Ensure graphics drivers are updated
   - Enable hardware acceleration in VLC settings
   - Use dedicated GPU if available

#### 4. Timing Precision Issues

**Symptoms**:
- Large clock offset (>10ms)
- Inconsistent timing measurements
- Synchronization problems

**Solutions**:
1. **System Optimization**:
   ```bash
   # Disable unnecessary services
   # Close background applications
   # Use high-performance power plan (Windows)
   ```

2. **Timing Calibration**:
   - Run timing test multiple times
   - Average results for better accuracy
   - Consider system load during testing

#### 5. Import Errors

**Symptoms**:
- ModuleNotFoundError for dependencies
- Import errors in IDE
- Missing functionality

**Solutions**:
```bash
# Verify Python environment
python -c "import sys; print(sys.path)"

# Reinstall dependencies
pip install --force-reinstall PyQt5 python-vlc numpy opencv-python

# Check virtual environment activation
which python  # Should point to venv if activated
```

## Performance Optimization

### System-Level Optimizations

#### Windows
```powershell
# Set high performance power plan
powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c

# Disable Windows Defender real-time scanning for project folder
# Add project folder to exclusions in Windows Security

# Increase process priority (run as administrator)
wmic process where name="python.exe" CALL setpriority "high priority"
```

#### macOS
```bash
# Increase file descriptor limits
ulimit -n 4096

# Disable App Nap for Python processes
defaults write NSGlobalDomain NSAppSleepDisabled -bool YES
```

#### Linux
```bash
# Increase process priority
sudo nice -n -10 python PythonApp/src/main.py

# Optimize video memory
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
```

### Application-Level Optimizations

#### Video Settings
```python
# Recommended video specifications for optimal performance
OPTIMAL_VIDEO_SPECS = {
    'resolution': '1920x1080',  # Full HD maximum
    'framerate': '30fps',       # Standard framerate
    'codec': 'H.264',          # Best compatibility
    'bitrate': '5-10 Mbps',    # Balanced quality/performance
    'format': 'MP4'            # Recommended container
}
```

#### Memory Management
```python
# Monitor memory usage during experiments
import psutil
import gc

def optimize_memory():
    """Optimize memory usage during experiments."""
    # Force garbage collection
    gc.collect()
    
    # Monitor memory usage
    memory = psutil.virtual_memory()
    if memory.percent > 80:
        print(f"Warning: High memory usage ({memory.percent}%)")
    
    return memory.percent
```

### Hardware Recommendations

#### For Standard Use
- **CPU**: Intel i5 or AMD Ryzen 5
- **RAM**: 8GB DDR4
- **Storage**: 256GB SSD
- **Graphics**: Integrated graphics sufficient

#### For Professional Use
- **CPU**: Intel i7/i9 or AMD Ryzen 7/9
- **RAM**: 16-32GB DDR4
- **Storage**: 512GB+ NVMe SSD
- **Graphics**: Dedicated GPU (GTX 1660 or better)

#### For Research/High-Performance
- **CPU**: Intel Xeon or AMD Threadripper
- **RAM**: 32-64GB ECC RAM
- **Storage**: 1TB+ NVMe SSD RAID
- **Graphics**: RTX 3070 or better with CUDA support

## Advanced Features

### Custom Backend Configuration

```python
# Create custom backend configuration
BACKEND_CONFIG = {
    'qt_multimedia': {
        'preferred_formats': ['.mp4', '.avi', '.mov'],
        'hardware_acceleration': True,
        'buffer_size': 1024 * 1024,  # 1MB buffer
    },
    'vlc': {
        'preferred_formats': ['.webm', '.flv', '.mkv'],
        'hardware_acceleration': True,
        'network_caching': 1000,  # 1 second
        'file_caching': 300,      # 300ms
    }
}
```

### Performance Monitoring Integration

```python
# Advanced performance monitoring
class AdvancedPerformanceMonitor:
    def __init__(self):
        self.metrics = {
            'frame_times': [],
            'cpu_usage': [],
            'memory_usage': [],
            'gpu_usage': []  # If available
        }
    
    def collect_metrics(self):
        """Collect comprehensive performance metrics."""
        import psutil
        import time
        
        # CPU and memory
        self.metrics['cpu_usage'].append(psutil.cpu_percent())
        self.metrics['memory_usage'].append(psutil.virtual_memory().percent)
        
        # Frame timing
        frame_time = time.perf_counter()
        if hasattr(self, 'last_frame_time'):
            frame_interval = frame_time - self.last_frame_time
            self.metrics['frame_times'].append(frame_interval * 1000)  # Convert to ms
        self.last_frame_time = frame_time
    
    def generate_report(self):
        """Generate performance report."""
        if not self.metrics['frame_times']:
            return "No performance data collected"
        
        avg_frame_time = sum(self.metrics['frame_times']) / len(self.metrics['frame_times'])
        max_frame_time = max(self.metrics['frame_times'])
        min_frame_time = min(self.metrics['frame_times'])
        
        return f"""
Performance Report:
- Average frame time: {avg_frame_time:.2f}ms
- Max frame time: {max_frame_time:.2f}ms  
- Min frame time: {min_frame_time:.2f}ms
- Frame drops: {len([t for t in self.metrics['frame_times'] if t > 33.33])}
- Average CPU usage: {sum(self.metrics['cpu_usage'])/len(self.metrics['cpu_usage']):.1f}%
- Average memory usage: {sum(self.metrics['memory_usage'])/len(self.metrics['memory_usage']):.1f}%
        """
```

### Custom Timing Logger

```python
# Enhanced timing logger with custom precision
class CustomTimingLogger:
    def __init__(self, precision_mode='high'):
        self.precision_mode = precision_mode
        self.calibration_samples = 100 if precision_mode == 'high' else 10
        
    def calibrate_precision(self):
        """Advanced timing calibration."""
        import time
        import statistics
        
        # Collect multiple calibration samples
        offsets = []
        for _ in range(self.calibration_samples):
            start_perf = time.perf_counter()
            start_time = time.time()
            time.sleep(0.001)  # 1ms sleep
            end_perf = time.perf_counter()
            end_time = time.time()
            
            perf_duration = end_perf - start_perf
            time_duration = end_time - start_time
            offset = time_duration - perf_duration
            offsets.append(offset)
        
        # Calculate statistics
        self.mean_offset = statistics.mean(offsets)
        self.std_offset = statistics.stdev(offsets)
        self.precision_estimate = self.std_offset * 1000  # Convert to ms
        
        return {
            'mean_offset_ms': self.mean_offset * 1000,
            'std_offset_ms': self.std_offset * 1000,
            'precision_estimate_ms': self.precision_estimate,
            'samples': len(offsets)
        }
```

## Conclusion

The Enhanced Stimulus Controller with PsychoPy-inspired improvements provides professional-grade video stimulus presentation capabilities with:

- **Dual Backend Support**: Qt Multimedia and VLC for maximum compatibility
- **Enhanced Timing Precision**: Multiple clock sources with calibration
- **Performance Monitoring**: Real-time performance tracking and optimization
- **Comprehensive Error Handling**: Detailed error reporting and recovery
- **Professional Features**: Frame-accurate timing, hardware acceleration, robust synchronization

For additional support or advanced configuration, refer to the project documentation or contact the development team.

---

**Version**: 3.5 Enhanced  
**Last Updated**: 2025-07-29  
**Author**: Multi-Sensor Recording System Team
