import asyncio
import json
import os
import shutil
import subprocess
import sys
import zipfile
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import platform
import hashlib
from ..utils.logging_config import get_logger


@dataclass
class BuildResult:
    component: str
    success: bool
    duration_seconds: float
    output_path: Optional[str] = None
    error_message: Optional[str] = None
    build_size_mb: Optional[float] = None
    checksum: Optional[str] = None


@dataclass
class DeploymentPackage:
    version: str
    build_timestamp: str
    components: List[BuildResult]
    total_size_mb: float
    package_path: str
    checksum: str
    deployment_instructions: List[str]


class DeploymentAutomation:

    def __init__(self, project_root: str, version: str=None):
        self.project_root = Path(project_root)
        self.version = version or self._generate_version()
        self.logger = get_logger(__name__)
        self.build_results: List[BuildResult] = []
        self.build_dir = self.project_root / 'dist'
        self.build_dir.mkdir(exist_ok=True)
        self.android_build_dir = self.build_dir / 'android'
        self.python_build_dir = self.build_dir / 'python'
        self.docs_build_dir = self.build_dir / 'docs'
        for build_subdir in [self.android_build_dir, self.python_build_dir,
            self.docs_build_dir]:
            build_subdir.mkdir(exist_ok=True)

    def _generate_version(self) ->str:
        timestamp = datetime.now().strftime('%Y.%m.%d.%H%M')
        return f'v{timestamp}'

    async def build_all_components(self) ->DeploymentPackage:
        start_time = datetime.now()
        self.logger.info(
            f'Starting production build for version {self.version}')
        await self._clean_previous_builds()
        await self._build_android_app()
        await self._build_python_app()
        await self._generate_documentation()
        await self._create_deployment_scripts()
        package = await self._create_deployment_package()
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        self.logger.info(f'Build completed in {duration:.2f} seconds')
        return package

    async def _clean_previous_builds(self):
        self.logger.info('Cleaning previous builds...')
        try:
            for item in self.build_dir.iterdir():
                if item.name != 'deployment.log':
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
            for build_subdir in [self.android_build_dir, self.
                python_build_dir, self.docs_build_dir]:
                build_subdir.mkdir(exist_ok=True)
        except Exception as e:
            self.logger.warning(f'Error cleaning previous builds: {e}')

    async def _build_android_app(self):
        self.logger.info('Building Android application...')
        start_time = datetime.now()
        try:
            android_project = self.project_root / 'AndroidApp'
            if platform.system() == 'Windows':
                gradle_cmd = str(self.project_root / 'gradlew.bat')
            else:
                gradle_cmd = str(self.project_root / 'gradlew')
            build_process = await asyncio.create_subprocess_exec(gradle_cmd,
                ':AndroidApp:assembleProdRelease', cwd=str(self.
                project_root), stdout=asyncio.subprocess.PIPE, stderr=
                asyncio.subprocess.PIPE)
            stdout, stderr = await build_process.communicate()
            if build_process.returncode == 0:
                apk_dir = (android_project / 'build' / 'outputs' / 'apk' /
                    'prod' / 'release')
                apk_files = list(apk_dir.glob('*.apk'))
                if apk_files:
                    source_apk = apk_files[0]
                    target_apk = (self.android_build_dir /
                        f'MultiSensorRecording-{self.version}.apk')
                    shutil.copy2(source_apk, target_apk)
                    size_mb = target_apk.stat().st_size / (1024 * 1024)
                    checksum = self._calculate_checksum(target_apk)
                    self.build_results.append(BuildResult(component=
                        'android_app', success=True, duration_seconds=(
                        datetime.now() - start_time).total_seconds(),
                        output_path=str(target_apk), build_size_mb=size_mb,
                        checksum=checksum))
                    self.logger.info(
                        f'Android APK built successfully: {target_apk.name} ({size_mb:.1f}MB)'
                        )
                    await self._build_debug_apk()
                else:
                    raise Exception('APK file not found after build')
            else:
                error_msg = stderr.decode() if stderr else 'Build failed'
                raise Exception(error_msg)
        except Exception as e:
            self.build_results.append(BuildResult(component='android_app',
                success=False, duration_seconds=(datetime.now() -
                start_time).total_seconds(), error_message=str(e)))
            self.logger.error(f'Android build failed: {e}')

    async def _build_debug_apk(self):
        self.logger.info('Building debug APK...')
        try:
            android_project = self.project_root / 'AndroidApp'
            if platform.system() == 'Windows':
                gradle_cmd = str(self.project_root / 'gradlew.bat')
            else:
                gradle_cmd = str(self.project_root / 'gradlew')
            build_process = await asyncio.create_subprocess_exec(gradle_cmd,
                ':AndroidApp:assembleDevDebug', cwd=str(self.project_root),
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            stdout, stderr = await build_process.communicate()
            if build_process.returncode == 0:
                apk_dir = (android_project / 'build' / 'outputs' / 'apk' /
                    'dev' / 'debug')
                apk_files = list(apk_dir.glob('*.apk'))
                if apk_files:
                    source_apk = apk_files[0]
                    target_apk = (self.android_build_dir /
                        f'MultiSensorRecording-{self.version}-debug.apk')
                    shutil.copy2(source_apk, target_apk)
                    self.logger.info(f'Debug APK built: {target_apk.name}')
        except Exception as e:
            self.logger.warning(f'Debug APK build failed: {e}')

    async def _build_python_app(self):
        self.logger.info('Building Python application...')
        start_time = datetime.now()
        try:
            python_src = self.project_root / 'PythonApp'
            python_dist = (self.python_build_dir /
                f'MultiSensorRecording-Python-{self.version}')
            python_dist.mkdir(exist_ok=True)
            src_dir = python_dist / 'src'
            shutil.copytree(python_src / 'src', src_dir)
            config_files = ['requirements.txt', 'environment.yml']
            for config_file in config_files:
                source_file = python_src / config_file
                if source_file.exists():
                    shutil.copy2(source_file, python_dist)
            protocol_src = self.project_root / 'protocol'
            if protocol_src.exists():
                shutil.copytree(protocol_src, python_dist / 'protocol')
            await self._create_python_startup_scripts(python_dist)
            await self._create_locked_requirements(python_dist)
            zip_path = (self.python_build_dir /
                f'MultiSensorRecording-Python-{self.version}.zip')
            await self._create_zip_archive(python_dist, zip_path)
            size_mb = zip_path.stat().st_size / (1024 * 1024)
            checksum = self._calculate_checksum(zip_path)
            self.build_results.append(BuildResult(component='python_app',
                success=True, duration_seconds=(datetime.now() - start_time
                ).total_seconds(), output_path=str(zip_path), build_size_mb
                =size_mb, checksum=checksum))
            self.logger.info(
                f'Python application packaged: {zip_path.name} ({size_mb:.1f}MB)'
                )
            await self._build_python_executable(python_dist)
        except Exception as e:
            self.build_results.append(BuildResult(component='python_app',
                success=False, duration_seconds=(datetime.now() -
                start_time).total_seconds(), error_message=str(e)))
            self.logger.error(f'Python build failed: {e}')

    async def _create_python_startup_scripts(self, python_dist: Path):
        windows_script = python_dist / 'start.bat'
        windows_script.write_text(
            """@echo off
echo Starting Multi-Sensor Recording System...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or later
    pause
    exit /b 1
)

REM Install requirements if needed
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\\Scripts\\activate.bat

echo Installing requirements...
pip install -r requirements.txt

echo Starting application...
python src\\application.py

pause
"""
            )
        unix_script = python_dist / 'start.sh'
        unix_script.write_text(
            """#!/bin/bash
echo "Starting Multi-Sensor Recording System..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.8 or later"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing requirements..."
pip install -r requirements.txt

echo "Starting application..."
python src/application.py
"""
            )
        try:
            unix_script.chmod(493)
        except:
            pass

    async def _create_locked_requirements(self, python_dist: Path):
        try:
            requirements_process = await asyncio.create_subprocess_exec('pip',
                'freeze', stdout=asyncio.subprocess.PIPE, stderr=asyncio.
                subprocess.PIPE)
            stdout, stderr = await requirements_process.communicate()
            if requirements_process.returncode == 0:
                locked_requirements = python_dist / 'requirements-locked.txt'
                locked_requirements.write_text(stdout.decode())
                self.logger.info('Created locked requirements file')
        except Exception as e:
            self.logger.warning(f'Could not create locked requirements: {e}')

    async def _build_python_executable(self, python_dist: Path):
        try:
            self.logger.info('Attempting to build Python executable...')
            pyinstaller_process = await asyncio.create_subprocess_exec(
                'pyinstaller', '--version', stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE)
            await pyinstaller_process.communicate()
            if pyinstaller_process.returncode == 0:
                main_script = python_dist / 'src' / 'application.py'
                if main_script.exists():
                    build_process = await asyncio.create_subprocess_exec(
                        'pyinstaller', '--onefile', '--windowed', '--name',
                        f'MultiSensorRecording-{self.version}',
                        '--distpath', str(self.python_build_dir), str(
                        main_script), cwd=str(python_dist), stdout=asyncio.
                        subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
                    stdout, stderr = await build_process.communicate()
                    if build_process.returncode == 0:
                        self.logger.info('Python executable built successfully'
                            )
                    else:
                        self.logger.warning('Python executable build failed')
        except Exception as e:
            self.logger.warning(f'Could not build Python executable: {e}')

    async def _generate_documentation(self):
        self.logger.info('Generating documentation...')
        start_time = datetime.now()
        try:
            docs_src = self.project_root / 'docs'
            if docs_src.exists():
                shutil.copytree(docs_src, self.docs_build_dir / 'docs')
            await self._generate_api_docs()
            await self._create_user_manuals()
            await self._create_deployment_guide()
            await self._create_distribution_readme()
            docs_zip = (self.build_dir /
                f'MultiSensorRecording-Docs-{self.version}.zip')
            await self._create_zip_archive(self.docs_build_dir, docs_zip)
            size_mb = docs_zip.stat().st_size / (1024 * 1024)
            checksum = self._calculate_checksum(docs_zip)
            self.build_results.append(BuildResult(component='documentation',
                success=True, duration_seconds=(datetime.now() - start_time
                ).total_seconds(), output_path=str(docs_zip), build_size_mb
                =size_mb, checksum=checksum))
            self.logger.info(
                f'Documentation generated: {docs_zip.name} ({size_mb:.1f}MB)')
        except Exception as e:
            self.build_results.append(BuildResult(component='documentation',
                success=False, duration_seconds=(datetime.now() -
                start_time).total_seconds(), error_message=str(e)))
            self.logger.error(f'Documentation generation failed: {e}')

    async def _generate_api_docs(self):
        try:
            python_src = self.project_root / 'PythonApp' / 'src'
            api_docs_dir = self.docs_build_dir / 'api'
            api_docs_dir.mkdir(exist_ok=True)
            api_overview = api_docs_dir / 'python_api.md'
            api_overview.write_text(
                """# Python API Documentation

## Core Modules

### Application (`src/application.py`)
Main application entry point and GUI management.

### Session Management (`src/session/`)
- `session_manager.py` - Recording session management
- `session_logger.py` - Session logging and persistence
- `session_synchronizer.py` - Cross-device synchronization

### Calibration (`src/calibration/`)
- `calibration_manager.py` - Camera calibration management
- `calibration_processor.py` - Calibration algorithms
- `calibration_result.py` - Calibration data structures

### Networking (`src/networking/`)
- `json_socket_server.py` - JSON-based socket server
- `device_server.py` - Device communication management

### Production (`src/production/`)
- `performance_benchmark.py` - Performance benchmarking tools
- `security_scanner.py` - Security assessment tools

## Configuration

See `protocol/config.json` for runtime configuration options.
See `protocol/message_schema.json` for network message definitions.

## Usage Examples

```python
from src.application import Application

# Start the application
app = Application()
app.run()
```

For detailed usage examples, see the user manual.
"""
                )
            self.logger.info('API documentation generated')
        except Exception as e:
            self.logger.warning(f'API documentation generation failed: {e}')

    async def _create_user_manuals(self):
        user_manual = self.docs_build_dir / 'USER_MANUAL.md'
        user_manual.write_text(
            f"""# Multi-Sensor Recording System User Manual

Version: {self.version}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview

The Multi-Sensor Recording System is a comprehensive solution for synchronized recording
across multiple devices including Android cameras, Shimmer sensors, and thermal cameras.

## System Requirements

### PC Application (Python)
- Windows 10/11, macOS 10.15+, or Linux Ubuntu 18.04+
- Python 3.8 or later
- 8GB RAM minimum, 16GB recommended
- 1GB free disk space
- Network connectivity (Wi-Fi or Ethernet)

### Android Application
- Android 7.0 (API level 24) or later
- 4GB RAM minimum
- Camera permission
- Network connectivity (Wi-Fi)
- 500MB free storage

## Installation

### PC Application
1. Extract the Python distribution zip file
2. Run the appropriate startup script:
   - Windows: Double-click `start.bat`
   - macOS/Linux: Run `./start.sh` in terminal
3. The application will automatically install dependencies

### Android Application
1. Enable "Unknown sources" in Android security settings
2. Install the APK file: `MultiSensorRecording-{self.version}.apk`
3. Grant camera and storage permissions when prompted

## Quick Start

1. Start the PC application
2. Install and start the Android app
3. Ensure both devices are on the same network
4. In the Android app, enter the PC's IP address
5. Tap "Connect" to establish connection
6. Use the PC interface to start/stop recordings

## Features

### Recording Capabilities
- Synchronized video recording across multiple Android devices
- Shimmer sensor data collection
- Thermal camera integration
- Automatic file organization and metadata

### Calibration
- Camera calibration using chessboard patterns
- Real-time calibration feedback
- Calibration result validation

### Session Management
- Session-based recording organization
- Automatic session recovery after crashes
- Session metadata and logging

### Network Communication
- Robust PC-Android communication
- Automatic reconnection handling
- Real-time status monitoring

## Troubleshooting

### Connection Issues
- Verify both devices are on the same network
- Check firewall settings on PC
- Ensure port 9000 is not blocked

### Performance Issues
- Close unnecessary applications
- Ensure adequate storage space
- Check network bandwidth

### Recording Issues
- Verify camera permissions on Android
- Check storage permissions
- Ensure adequate free space

## Support

For technical support and updates, please refer to the project documentation
or contact the development team.
"""
            )
        self.logger.info('User manual created')

    async def _create_deployment_guide(self):
        deployment_guide = self.docs_build_dir / 'DEPLOYMENT_GUIDE.md'
        deployment_guide.write_text(
            f"""# Deployment Guide

Version: {self.version}

## Production Deployment

### Pre-deployment Checklist

- [ ] All tests pass
- [ ] Security scan completed
- [ ] Performance benchmarks meet requirements
- [ ] Documentation is up-to-date
- [ ] Production configuration reviewed

### Android APK Deployment

1. **Production APK**: `MultiSensorRecording-{self.version}.apk`
   - Signed with release key
   - Optimized and obfuscated
   - Ready for distribution

2. **Debug APK**: `MultiSensorRecording-{self.version}-debug.apk`
   - For testing and development
   - Not for production use

### Python Application Deployment

1. **Source Distribution**: `MultiSensorRecording-Python-{self.version}.zip`
   - Complete source code
   - Startup scripts for all platforms
   - Requirements and configuration

2. **Installation Steps**:
   ```bash
   # Extract the distribution
   unzip MultiSensorRecording-Python-{self.version}.zip
   cd MultiSensorRecording-Python-{self.version}
   
   # Windows
   start.bat
   
   # Linux/macOS
   chmod +x start.sh
   ./start.sh
   ```

### Network Configuration

Default configuration in `protocol/config.json`:
- Port: 9000
- Host: 192.168.0.100 (update for your network)
- Protocol: TCP with JSON messages

### Security Considerations

- Enable firewall rules for port 9000
- Use encrypted networks (WPA2/WPA3)
- Regularly update dependencies
- Monitor for security updates

### Performance Optimization

- Allocate at least 8GB RAM for PC application
- Use SSD storage for better I/O performance
- Ensure stable network connectivity
- Monitor system resources during operation

### Monitoring and Maintenance

- Check log files regularly (`logs/` directory)
- Monitor disk space usage
- Backup recording sessions
- Update components as needed

### Troubleshooting

Common deployment issues:
1. Port conflicts - Change port in config.json
2. Permission errors - Run with appropriate privileges
3. Network connectivity - Check firewall and network settings
4. Missing dependencies - Run startup scripts to install

### Rollback Procedures

If deployment issues occur:
1. Stop all running applications
2. Restore previous version files
3. Verify configuration
4. Restart services

### Support and Updates

- Keep deployment guide with installation
- Document any configuration changes
- Maintain version compatibility between PC and Android apps
"""
            )
        self.logger.info('Deployment guide created')

    async def _create_distribution_readme(self):
        readme = self.build_dir / 'README.md'
        readme.write_text(
            f"""# Multi-Sensor Recording System - Production Release

Version: {self.version}
Build Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Package Contents

This distribution contains the complete Multi-Sensor Recording System for production deployment:

### Android Application
- `android/MultiSensorRecording-{self.version}.apk` - Production APK
- `android/MultiSensorRecording-{self.version}-debug.apk` - Debug APK

### Python PC Application
- `python/MultiSensorRecording-Python-{self.version}.zip` - Complete Python distribution

### Documentation
- `MultiSensorRecording-Docs-{self.version}.zip` - Complete documentation package
- `USER_MANUAL.md` - User installation and operation guide
- `DEPLOYMENT_GUIDE.md` - Production deployment instructions

### Installation Scripts
- `install.bat` - Windows installation script
- `install.sh` - Linux/macOS installation script

## Quick Installation

### Windows
1. Run `install.bat` as Administrator
2. Follow the on-screen instructions

### Linux/macOS
1. Make script executable: `chmod +x install.sh`
2. Run: `sudo ./install.sh`

### Manual Installation
1. Extract Python distribution: `python/MultiSensorRecording-Python-{self.version}.zip`
2. Install Android APK: `android/MultiSensorRecording-{self.version}.apk`
3. Follow the User Manual for detailed setup

## System Requirements

- **PC**: Windows 10+/macOS 10.15+/Ubuntu 18.04+, Python 3.8+, 8GB RAM
- **Android**: Android 7.0+, 4GB RAM, Camera access
- **Network**: Wi-Fi or Ethernet connection between devices

## Support

Refer to the documentation package for complete setup and troubleshooting guides.

## Verification

Package integrity can be verified using the provided checksums in `checksums.txt`.

---

Multi-Sensor Recording System v{self.version}
Phase 4: Production Ready
"""
            )
        self.logger.info('Distribution README created')

    async def _create_deployment_scripts(self):
        self.logger.info('Creating deployment scripts...')
        try:
            windows_installer = self.build_dir / 'install.bat'
            windows_installer.write_text(
                f"""@echo off
echo ============================================
echo Multi-Sensor Recording System Installer
echo Version: {self.version}
echo ============================================
echo.

echo Checking system requirements...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is required but not found
    echo Please install Python 3.8 or later from https://python.org
    echo.
    pause
    exit /b 1
)

echo Python found - OK

REM Check if ADB is available (optional)
adb version >nul 2>&1
if errorlevel 1 (
    echo Note: ADB not found - Android debugging will not be available
) else (
    echo ADB found - OK
)

echo.
echo Installing Python application...

REM Extract Python distribution
if exist "python\\MultiSensorRecording-Python-{self.version}.zip" (
    echo Extracting Python application...
    powershell -command "Expand-Archive -Path 'python\\MultiSensorRecording-Python-{self.version}.zip' -DestinationPath 'python\\' -Force"
    echo Python application extracted
) else (
    echo Error: Python distribution not found
    pause
    exit /b 1
)

echo.
echo Installation completed successfully!
echo.
echo To start the application:
echo 1. Navigate to: python\\MultiSensorRecording-Python-{self.version}\\
echo 2. Run: start.bat
echo.
echo To install Android app:
echo 1. Enable "Unknown sources" in Android settings
echo 2. Install: android\\MultiSensorRecording-{self.version}.apk
echo.
echo See USER_MANUAL.md for detailed instructions
echo.
pause
"""
                )
            unix_installer = self.build_dir / 'install.sh'
            unix_installer.write_text(
                f"""#!/bin/bash
echo "============================================"
echo "Multi-Sensor Recording System Installer"
echo "Version: {self.version}"
echo "============================================"
echo

echo "Checking system requirements..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not found"
    echo "Please install Python 3.8 or later"
    echo
    exit 1
fi

echo "Python found - OK"

# Check if unzip is available
if ! command -v unzip &> /dev/null; then
    echo "Error: unzip is required but not found"
    echo "Please install unzip utility"
    exit 1
fi

echo "Unzip found - OK"

# Check if ADB is available (optional)
if ! command -v adb &> /dev/null; then
    echo "Note: ADB not found - Android debugging will not be available"
else
    echo "ADB found - OK"
fi

echo
echo "Installing Python application..."

# Extract Python distribution
if [ -f "python/MultiSensorRecording-Python-{self.version}.zip" ]; then
    echo "Extracting Python application..."
    cd python
    unzip -o "MultiSensorRecording-Python-{self.version}.zip"
    cd ..
    echo "Python application extracted"
else
    echo "Error: Python distribution not found"
    exit 1
fi

echo
echo "Setting permissions..."
chmod +x "python/MultiSensorRecording-Python-{self.version}/start.sh"

echo
echo "Installation completed successfully!"
echo
echo "To start the application:"
echo "1. Navigate to: python/MultiSensorRecording-Python-{self.version}/"
echo "2. Run: ./start.sh"
echo
echo "To install Android app:"
echo "1. Enable 'Unknown sources' in Android settings"
echo "2. Install: android/MultiSensorRecording-{self.version}.apk"
echo
echo "See USER_MANUAL.md for detailed instructions"
echo
"""
                )
            try:
                unix_installer.chmod(493)
            except:
                pass
            self.logger.info('Deployment scripts created')
        except Exception as e:
            self.logger.error(f'Failed to create deployment scripts: {e}')

    async def _create_deployment_package(self) ->DeploymentPackage:
        self.logger.info('Creating deployment package...')
        total_size = 0
        for result in self.build_results:
            if result.success and result.build_size_mb:
                total_size += result.build_size_mb
        await self._create_checksums_file()
        package_name = f'MultiSensorRecording-{self.version}-Complete.zip'
        package_path = self.build_dir.parent / package_name
        await self._create_zip_archive(self.build_dir, package_path)
        package_checksum = self._calculate_checksum(package_path)
        deployment_instructions = [
            '1. Extract the complete package to your desired location',
            '2. Run the appropriate installer script (install.bat for Windows, install.sh for Linux/macOS)'
            , '3. Follow the on-screen instructions',
            '4. Refer to USER_MANUAL.md for detailed setup and usage',
            '5. Install the Android APK on target devices',
            '6. Configure network settings as needed']
        package = DeploymentPackage(version=self.version, build_timestamp=
            datetime.now().isoformat(), components=self.build_results,
            total_size_mb=total_size, package_path=str(package_path),
            checksum=package_checksum, deployment_instructions=
            deployment_instructions)
        manifest_file = (self.build_dir.parent /
            f'deployment_manifest_{self.version}.json')
        with open(manifest_file, 'w') as f:
            json.dump(asdict(package), f, indent=2, default=str)
        self.logger.info(f'Deployment package created: {package_name}')
        self.logger.info(
            f'Total package size: {package_path.stat().st_size / (1024 * 1024):.1f}MB'
            )
        return package

    async def _create_checksums_file(self):
        checksums_file = self.build_dir / 'checksums.txt'
        with open(checksums_file, 'w') as f:
            f.write(
                f'# Multi-Sensor Recording System {self.version} - File Checksums\\n'
                )
            f.write(f'# Generated: {datetime.now().isoformat()}\\n\\n')
            for result in self.build_results:
                if result.success and result.output_path and result.checksum:
                    filename = Path(result.output_path).name
                    f.write(f'{result.checksum}  {filename}\\n')
        self.logger.info('Checksums file created')

    async def _create_zip_archive(self, source_dir: Path, zip_path: Path):
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file_path in source_dir.rglob('*'):
                if file_path.is_file():
                    arc_name = file_path.relative_to(source_dir)
                    zip_file.write(file_path, arc_name)

    def _calculate_checksum(self, file_path: Path) ->str:
        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda : f.read(4096), b''):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()


async def main():
    project_root = Path(__file__).parent.parent.parent
    version = sys.argv[1] if len(sys.argv) > 1 else None
    print('Starting Phase 4 Production Deployment...')
    deployment = DeploymentAutomation(str(project_root), version)
    try:
        package = await deployment.build_all_components()
        print(f'\\nDeployment package created successfully!')
        print(f'Version: {package.version}')
        print(f'Package: {Path(package.package_path).name}')
        print(f'Total size: {package.total_size_mb:.1f}MB')
        print(
            f'Components built: {len([r for r in package.components if r.success])}/{len(package.components)}'
            )
        print(f'\\nComponent results:')
        for result in package.components:
            status = '✓' if result.success else '✗'
            size_info = (f' ({result.build_size_mb:.1f}MB)' if result.
                build_size_mb else '')
            print(f'  {status} {result.component}{size_info}')
        if any(not r.success for r in package.components):
            print(
                f'\\n⚠️  Some components failed to build. Check logs for details.'
                )
        print(f'\\nDeployment instructions:')
        for i, instruction in enumerate(package.deployment_instructions, 1):
            print(f'  {i}. {instruction}')
    except Exception as e:
        print(f'Deployment failed: {e}')
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(main())
