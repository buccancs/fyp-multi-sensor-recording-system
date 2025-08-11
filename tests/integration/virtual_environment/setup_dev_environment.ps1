# Virtual Test Environment Setup Script for Windows
# Provides automated setup for development and testing on Windows systems

param(
    [switch]$SkipDeps,
    [switch]$SkipVerification,
    [switch]$Help
)

# Colors for output (PowerShell compatible)
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Cyan"

function Write-ColorOutput {
    param($Message, $Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Write-Info {
    param($Message)
    Write-ColorOutput "[INFO] $Message" $Blue
}

function Write-Success {
    param($Message)
    Write-ColorOutput "[SUCCESS] $Message" $Green
}

function Write-Warning {
    param($Message)
    Write-ColorOutput "[WARNING] $Message" $Yellow
}

function Write-Error {
    param($Message)
    Write-ColorOutput "[ERROR] $Message" $Red
}

function Show-Help {
    Write-Host "Virtual Test Environment Setup for Windows"
    Write-Host "==========================================="
    Write-Host ""
    Write-Host "Usage: .\setup_dev_environment.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -SkipDeps         Skip dependency installation"
    Write-Host "  -SkipVerification Skip verification tests"
    Write-Host "  -Help             Show this help message"
    exit 0
}

function Test-PythonVersion {
    Write-Info "Checking Python version..."
    
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Python not found"
        }
        
        Write-Info "Found $pythonVersion"
        
        # Extract version number and check if >= 3.10
        $versionMatch = [regex]::Match($pythonVersion, "Python (\d+\.\d+)")
        if ($versionMatch.Success) {
            $version = [double]$versionMatch.Groups[1].Value
            if ($version -lt 3.10) {
                throw "Python 3.10 or higher is required. Found: $pythonVersion"
            }
        }
        
        Write-Success "Python version check passed"
        return $true
    }
    catch {
        Write-Error "Python 3.10 or higher is required. Please install from https://python.org"
        return $false
    }
}

function Setup-VirtualEnvironment {
    Write-Info "Setting up Python virtual environment..."
    
    $venvPath = ".\.venv"
    
    if (!(Test-Path $venvPath)) {
        Write-Info "Creating virtual environment at $venvPath"
        python -m venv $venvPath
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to create virtual environment"
        }
    } else {
        Write-Info "Virtual environment already exists"
    }
    
    # Activate virtual environment
    Write-Info "Activating virtual environment..."
    & "$venvPath\Scripts\Activate.ps1"
    
    # Upgrade pip
    Write-Info "Upgrading pip..."
    python -m pip install --upgrade pip setuptools wheel
    
    Write-Success "Virtual environment setup complete"
}

function Install-Dependencies {
    Write-Info "Installing project dependencies..."
    
    # Install main project in development mode
    pip install -e .
    
    # Install development dependencies
    Write-Info "Installing development dependencies..."
    pip install pytest pytest-asyncio pytest-cov psutil numpy opencv-python-headless
    
    # Install optional dependencies for virtual testing
    Write-Info "Installing virtual test environment dependencies..."
    pip install matplotlib pillow
    
    Write-Success "Dependencies installed successfully"
}

function New-IDEConfiguration {
    Write-Info "Creating IDE configuration files..."
    
    # Create VS Code configuration directory
    $vscodeDir = ".\.vscode"
    if (!(Test-Path $vscodeDir)) {
        New-Item -ItemType Directory -Path $vscodeDir | Out-Null
    }
    
    # Launch configuration for VS Code (Windows paths)
    $launchJson = @"
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Virtual Test Environment - Quick Test",
            "type": "python",
            "request": "launch",
            "program": "`${workspaceFolder}/tests/integration/virtual_environment/quick_test.py",
            "console": "integratedTerminal",
            "cwd": "`${workspaceFolder}/tests/integration/virtual_environment"
        },
        {
            "name": "Virtual Test Environment - Test Runner",
            "type": "python",
            "request": "launch",
            "program": "`${workspaceFolder}/tests/integration/virtual_environment/test_runner.py",
            "args": ["--scenario", "quick", "--devices", "2", "--duration", "0.5"],
            "console": "integratedTerminal",
            "cwd": "`${workspaceFolder}/tests/integration/virtual_environment"
        },
        {
            "name": "Run Pytest - Virtual Environment",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["tests/integration/virtual_environment/", "-v"],
            "console": "integratedTerminal",
            "cwd": "`${workspaceFolder}"
        }
    ]
}
"@
    $launchJson | Out-File -FilePath "$vscodeDir\launch.json" -Encoding UTF8
    
    # VS Code settings (Windows paths)
    $settingsJson = @"
{
    "python.defaultInterpreterPath": "./.venv/Scripts/python.exe",
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
"@
    $settingsJson | Out-File -FilePath "$vscodeDir\settings.json" -Encoding UTF8
    
    Write-Success "IDE configuration created"
}

function Test-VerificationTests {
    Write-Info "Running verification tests..."
    
    # Test imports
    Write-Info "Testing virtual environment imports..."
    python -c "from tests.integration.virtual_environment import VirtualTestConfig, VirtualTestRunner, VirtualTestScenario; print('✓ Imports successful')"
    if ($LASTEXITCODE -ne 0) {
        throw "Import verification failed"
    }
    
    # Run basic pytest tests
    Write-Info "Running basic pytest tests..."
    python -m pytest tests/integration/virtual_environment/test_pytest_integration.py::TestPytestIntegration::test_synthetic_data_deterministic -v
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Some tests failed but continuing..."
    }
    
    Write-Success "All verification tests completed"
}

function New-QuickTestScript {
    Write-Info "Creating quick test script..."
    
    $quickTestBat = @"
@echo off
cd /d "%~dp0tests\integration\virtual_environment"
echo 🚀 Running quick virtual test...
python test_runner.py --scenario quick --devices 2 --duration 0.5 --verbose
echo.
echo 📊 Test completed. Check test_results\ directory for outputs.
pause
"@
    $quickTestBat | Out-File -FilePath ".\quick_virtual_test.bat" -Encoding ASCII
    
    Write-Success "Quick test script created as quick_virtual_test.bat"
}

function Show-UsageInstructions {
    Write-Success "🎉 Virtual Test Environment setup complete!"
    Write-Host ""
    Write-ColorOutput "📋 Usage Instructions:" $Blue
    Write-Host ""
    Write-Host "1. Activate virtual environment:"
    Write-Host "   .\.venv\Scripts\Activate.ps1"
    Write-Host ""
    Write-Host "2. Run quick test:"
    Write-Host "   .\quick_virtual_test.bat"
    Write-Host ""
    Write-Host "3. Run specific tests:"
    Write-Host "   cd tests\integration\virtual_environment"
    Write-Host "   python test_runner.py --scenario quick --devices 3 --duration 1.0"
    Write-Host ""
    Write-Host "4. Run pytest suite:"
    Write-Host "   pytest tests\integration\virtual_environment\ -v"
    Write-Host ""
    Write-Host "5. Run performance tests:"
    Write-Host "   pytest tests\integration\virtual_environment\test_performance_benchmarks.py -v -m performance"
    Write-Host ""
    Write-ColorOutput "🔧 Development:" $Blue
    Write-Host "- VS Code launch configurations are available in .vscode\launch.json"
    Write-Host "- Run 'code .' to open project in VS Code with proper configuration"
    Write-Host ""
    Write-ColorOutput "📚 Documentation:" $Blue
    Write-Host "- See tests\integration\virtual_environment\README.md for detailed usage"
    Write-Host "- Check IMPLEMENTATION_SUMMARY.md for technical details"
    Write-Host "- Review TROUBLESHOOTING.md for Windows-specific issues"
}

# Main execution
function Main {
    if ($Help) {
        Show-Help
    }
    
    Write-ColorOutput "🔧 Virtual Test Environment Setup (Windows)" $Blue
    Write-Host "=============================================="
    Write-Host ""
    
    try {
        # Setup steps
        if (!(Test-PythonVersion)) {
            exit 1
        }
        
        Setup-VirtualEnvironment
        
        if (!$SkipDeps) {
            Install-Dependencies
        } else {
            Write-Warning "Skipping dependency installation"
        }
        
        New-IDEConfiguration
        New-QuickTestScript
        
        if (!$SkipVerification) {
            Test-VerificationTests
        } else {
            Write-Warning "Skipping verification tests"
        }
        
        Show-UsageInstructions
        
    } catch {
        Write-Error "Setup failed: $_"
        Write-Host "Check TROUBLESHOOTING.md for Windows-specific solutions"
        exit 1
    }
}

# Run main function
Main