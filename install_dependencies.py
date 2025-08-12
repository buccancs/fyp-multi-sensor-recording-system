#!/usr/bin/env python3
"""
Dependency Installer for Multi-Sensor Recording System

Installs the missing dependencies identified in the functional reality check.
"""

import sys
import subprocess
import importlib.util

def run_command(cmd, description):
    """Run a shell command and report status."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ Success")
            return True
        else:
            print(f"   ❌ Failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def check_dependency(module_name):
    """Check if a module is available."""
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False

def install_dependencies():
    """Install missing dependencies."""
    print("=== DEPENDENCY INSTALLER ===")
    print("Installing missing dependencies for Multi-Sensor Recording System")
    print()
    
    # List of dependencies to install
    dependencies = [
        ("PyQt5", "PyQt5"),
        ("opencv-python", "cv2"),
        ("numpy", "numpy"),
        ("matplotlib", "matplotlib"),
        ("scipy", "scipy")
    ]
    
    # Check current status
    print("📋 CHECKING CURRENT STATUS:")
    missing = []
    for pip_name, import_name in dependencies:
        if check_dependency(import_name):
            print(f"   ✅ {pip_name} - Already installed")
        else:
            print(f"   ❌ {pip_name} - Missing")
            missing.append(pip_name)
    
    if not missing:
        print("\n🎉 All dependencies are already installed!")
        return True
    
    print(f"\n🔧 INSTALLING {len(missing)} MISSING DEPENDENCIES:")
    
    # Install via pip
    success = True
    for dep in missing:
        cmd = f"{sys.executable} -m pip install {dep}"
        if not run_command(cmd, f"Installing {dep}"):
            success = False
    
    print(f"\n📋 VERIFICATION:")
    all_good = True
    for pip_name, import_name in dependencies:
        if check_dependency(import_name):
            print(f"   ✅ {pip_name} - Working")
        else:
            print(f"   ❌ {pip_name} - Still missing")
            all_good = False
    
    if all_good:
        print(f"\n🎉 ALL DEPENDENCIES INSTALLED SUCCESSFULLY!")
        print("You can now run the application:")
        print("   python -m PythonApp.main")
        print("   python functional_reality_check.py")
    else:
        print(f"\n⚠️  SOME DEPENDENCIES STILL MISSING")
        print("You may need to install system packages:")
        print("   sudo apt-get update")
        print("   sudo apt-get install python3-pyqt5 python3-opencv")
    
    return all_good

if __name__ == "__main__":
    install_dependencies()