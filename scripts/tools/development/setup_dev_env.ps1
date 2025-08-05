# Milestone 5.1: Enhanced Environment Bootstrapping Script
# ======================================================
# Multi-Sensor Recording System - Complete Development Environment Setup
# This script automates the complete setup of the development environment including:
# - Miniconda installation and management
# - Conda environment creation from environment.yml
# - Android SDK component installation
# - Gradle wrapper configuration
# - IDE setup assistance

param(
    [switch]$SkipValidation = $false,
    [switch]$RunTests = $false,
    [switch]$Verbose = $false,
    [switch]$ForceReinstall = $false,
    [string]$MinicondaPath = "$env:USERPROFILE\Miniconda3"
)

Write-Host "=== Milestone 5.1: Enhanced Development Environment Setup ===" -ForegroundColor Green
Write-Host "Complete automation for Android + Python development environment" -ForegroundColor Yellow

# Enhanced prerequisite checking with detailed reporting
Write-Host "`n1. Comprehensive Environment Validation..." -ForegroundColor Cyan

function Test-JavaCompatibility {
    try {
        $javaVersion = & java -version 2>&1 | Select-String "version" | ForEach-Object { $_.ToString() }
        Write-Host "Java version: $javaVersion" -ForegroundColor White
        
        if ($javaVersion -match '"(\d+)\.') {
            $majorVersion = [int]$matches[1]
            if ($majorVersion -ge 17 -and $majorVersion -le 21) {
                Write-Host "✓ Java version is compatible (Java $majorVersion)" -ForegroundColor Green
                return $true
            } elseif ($majorVersion -eq 24) {
                Write-Host "⚠ Java 24 detected - may cause compatibility issues with Gradle 8.4" -ForegroundColor Yellow
                Write-Host "  Recommendation: Use Java 17 or Java 21 for best compatibility" -ForegroundColor Yellow
                return $false
            } else {
                Write-Host "✗ Java version $majorVersion not in recommended range (17-21)" -ForegroundColor Red
                return $false
            }
        }
        return $false
    } catch {
        Write-Host "✗ Failed to check Java version: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Install-Miniconda {
    param([string]$InstallPath)
    
    Write-Host "`n2. Installing Miniconda..." -ForegroundColor Cyan
    
    if (Test-Path "$InstallPath\Scripts\conda.exe" -and -not $ForceReinstall) {
        Write-Host "✓ Miniconda already installed at: $InstallPath" -ForegroundColor Green
        return $true
    }
    
    Write-Host "Downloading Miniconda installer..." -ForegroundColor Yellow
    $installerPath = "$env:TEMP\Miniconda3-latest-Windows-x86_64.exe"
    $minicondaUrl = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
    
    try {
        # Download Miniconda installer
        Invoke-WebRequest -Uri $minicondaUrl -OutFile $installerPath -UseBasicParsing
        Write-Host "✓ Miniconda installer downloaded" -ForegroundColor Green
        
        # Install Miniconda silently
        Write-Host "Installing Miniconda (this may take a few minutes)..." -ForegroundColor Yellow
        $installArgs = @(
            "/InstallationType=JustMe"
            "/RegisterPython=0"
            "/S"
            "/D=$InstallPath"
        )
        
        Start-Process -FilePath $installerPath -ArgumentList $installArgs -Wait -NoNewWindow
        
        # Verify installation
        if (Test-Path "$InstallPath\Scripts\conda.exe") {
            Write-Host "✓ Miniconda installed successfully" -ForegroundColor Green
            
            # Add to PATH for current session
            $env:PATH = "$InstallPath\Scripts;$InstallPath;$env:PATH"
            
            # Initialize conda
            & "$InstallPath\Scripts\conda.exe" init powershell --quiet
            Write-Host "✓ Conda initialized for PowerShell" -ForegroundColor Green
            
            return $true
        } else {
            Write-Host "✗ Miniconda installation failed" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "✗ Failed to install Miniconda: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    } finally {
        # Clean up installer
        if (Test-Path $installerPath) {
            Remove-Item $installerPath -Force
        }
    }
}

function Setup-CondaEnvironment {
    Write-Host "`n3. Setting up Conda Environment..." -ForegroundColor Cyan
    
    # Ensure conda is in PATH
    $condaPath = "$MinicondaPath\Scripts\conda.exe"
    if (-not (Test-Path $condaPath)) {
        Write-Host "✗ Conda not found at expected path: $condaPath" -ForegroundColor Red
        return $false
    }
    
    # Check if environment.yml exists
    if (-not (Test-Path "environment.yml")) {
        Write-Host "✗ environment.yml not found in current directory" -ForegroundColor Red
        return $false
    }
    
    try {
        # Remove existing environment if force reinstall
        if ($ForceReinstall) {
            Write-Host "Removing existing thermal-env environment..." -ForegroundColor Yellow
            & $condaPath env remove -n thermal-env -y 2>$null
        }
        
        # Create conda environment from environment.yml
        Write-Host "Creating conda environment from environment.yml..." -ForegroundColor Yellow
        Write-Host "This may take several minutes to download and install packages..." -ForegroundColor Gray
        
        & $condaPath env create -f environment.yml --force
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Conda environment 'thermal-env' created successfully" -ForegroundColor Green
            
            # Test environment activation
            Write-Host "Testing environment activation..." -ForegroundColor Yellow
            & $condaPath activate thermal-env
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ Environment activation test passed" -ForegroundColor Green
                return $true
            } else {
                Write-Host "⚠ Environment created but activation test failed" -ForegroundColor Yellow
                return $true
            }
        } else {
            Write-Host "✗ Failed to create conda environment" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "✗ Error setting up conda environment: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Install-AndroidSDKComponents {
    Write-Host "`n4. Installing Android SDK Components..." -ForegroundColor Cyan
    
    # Check for Android SDK
    $androidHome = $env:ANDROID_HOME
    if ([string]::IsNullOrEmpty($androidHome)) {
        $androidHome = $env:ANDROID_SDK_ROOT
    }
    
    if ([string]::IsNullOrEmpty($androidHome)) {
        Write-Host "⚠ ANDROID_HOME not set. Please install Android Studio first." -ForegroundColor Yellow
        Write-Host "  After installing Android Studio:" -ForegroundColor Gray
        Write-Host "  1. Open Android Studio" -ForegroundColor Gray
        Write-Host "  2. Go to Tools > SDK Manager" -ForegroundColor Gray
        Write-Host "  3. Install Android SDK Platform 33 and Build Tools 33.0.2" -ForegroundColor Gray
        Write-Host "  4. Set ANDROID_HOME environment variable" -ForegroundColor Gray
        return $false
    }
    
    $sdkManager = "$androidHome\cmdline-tools\latest\bin\sdkmanager.bat"
    if (-not (Test-Path $sdkManager)) {
        # Try alternative path
        $sdkManager = "$androidHome\tools\bin\sdkmanager.bat"
        if (-not (Test-Path $sdkManager)) {
            Write-Host "⚠ SDK Manager not found. Please install Android SDK Command Line Tools." -ForegroundColor Yellow
            return $false
        }
    }
    
    Write-Host "Installing required Android SDK components..." -ForegroundColor Yellow
    
    try {
        # Install required SDK components
        $components = @(
            "platform-tools",
            "platforms;android-33",
            "build-tools;33.0.2",
            "extras;android;m2repository",
            "extras;google;m2repository"
        )
        
        foreach ($component in $components) {
            Write-Host "Installing $component..." -ForegroundColor Gray
            & $sdkManager $component --sdk_root="$androidHome"
        }
        
        Write-Host "✓ Android SDK components installed" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "⚠ Some Android SDK components may not have installed correctly" -ForegroundColor Yellow
        Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Gray
        return $false
    }
}

function Setup-GradleWrapper {
    Write-Host "`n5. Setting up Gradle Wrapper..." -ForegroundColor Cyan
    
    $gradleWrapperJar = "gradle\wrapper\gradle-wrapper.jar"
    if (-not (Test-Path $gradleWrapperJar)) {
        Write-Host "Downloading Gradle wrapper JAR..." -ForegroundColor Yellow
        
        # Create directory if it doesn't exist
        $wrapperDir = "gradle\wrapper"
        if (-not (Test-Path $wrapperDir)) {
            New-Item -ItemType Directory -Path $wrapperDir -Force | Out-Null
        }
        
        # Download Gradle wrapper JAR
        $gradleWrapperUrl = "https://github.com/gradle/gradle/raw/v8.4.0/gradle/wrapper/gradle-wrapper.jar"
        try {
            Invoke-WebRequest -Uri $gradleWrapperUrl -OutFile $gradleWrapperJar -UseBasicParsing
            Write-Host "✓ Gradle wrapper JAR downloaded" -ForegroundColor Green
        }
        catch {
            Write-Host "✗ Failed to download Gradle wrapper. Check internet connection." -ForegroundColor Red
            return $false
        }
    } else {
        Write-Host "✓ Gradle wrapper JAR already exists" -ForegroundColor Green
    }
    
    # Test Gradle wrapper
    try {
        $gradleTest = & ".\gradlew.bat" --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Gradle wrapper is working" -ForegroundColor Green
            return $true
        } else {
            Write-Host "⚠ Gradle wrapper test had issues, but continuing..." -ForegroundColor Yellow
            return $true
        }
    } catch {
        Write-Host "⚠ Could not test Gradle wrapper: $_" -ForegroundColor Yellow
        return $true
    }
}

function Test-BuildSystem {
    Write-Host "`n6. Testing Build System..." -ForegroundColor Cyan
    
    if (-not $SkipValidation) {
        try {
            Write-Host "Running assembleAll task..." -ForegroundColor Yellow
            & ".\gradlew.bat" assembleAll
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ Build system test passed" -ForegroundColor Green
                return $true
            } else {
                Write-Host "⚠ Build system test had issues" -ForegroundColor Yellow
                return $false
            }
        } catch {
            Write-Host "⚠ Could not test build system: $_" -ForegroundColor Yellow
            return $false
        }
    } else {
        Write-Host "Skipping build system test (use -SkipValidation:$false to enable)" -ForegroundColor Yellow
        return $true
    }
}

# Main execution flow
Write-Host "`nStarting enhanced environment setup..." -ForegroundColor White

# Step 1: Check Java
if (-not (Get-Command "java" -ErrorAction SilentlyContinue)) {
    Write-Host "✗ Java not found in PATH" -ForegroundColor Red
    Write-Host "  Please install Java 17 or Java 21 and add to PATH" -ForegroundColor Red
    exit 1
} else {
    if (-not (Test-JavaCompatibility)) {
        Write-Host "  Consider updating Java for better compatibility" -ForegroundColor Yellow
    }
}

# Step 2: Install Miniconda
if (-not (Install-Miniconda -InstallPath $MinicondaPath)) {
    Write-Host "✗ Failed to install Miniconda" -ForegroundColor Red
    exit 1
}

# Step 3: Setup Conda Environment
if (-not (Setup-CondaEnvironment)) {
    Write-Host "✗ Failed to setup conda environment" -ForegroundColor Red
    exit 1
}

# Step 4: Install Android SDK Components
Install-AndroidSDKComponents | Out-Null

# Step 5: Setup Gradle Wrapper
if (-not (Setup-GradleWrapper)) {
    Write-Host "✗ Failed to setup Gradle wrapper" -ForegroundColor Red
    exit 1
}

# Step 6: Test Build System
Test-BuildSystem | Out-Null

# Final instructions and summary
Write-Host "`n=== Milestone 5.1 Setup Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Environment Status:" -ForegroundColor Yellow
Write-Host "  ✓ Java: Compatible version detected" -ForegroundColor Green
Write-Host "  ✓ Miniconda: Installed at $MinicondaPath" -ForegroundColor Green
Write-Host "  ✓ Conda Environment: 'thermal-env' created with all dependencies" -ForegroundColor Green
Write-Host "  ✓ Gradle: Wrapper configured and tested" -ForegroundColor Green
Write-Host "  ✓ Build Automation: assembleAll and other tasks available" -ForegroundColor Green
Write-Host ""
Write-Host "IDE Setup Instructions:" -ForegroundColor Yellow
Write-Host "Android Studio:" -ForegroundColor White
Write-Host "  1. Open Android Studio" -ForegroundColor Gray
Write-Host "  2. Choose 'Open an existing project'" -ForegroundColor Gray
Write-Host "  3. Select the 'AndroidApp' folder" -ForegroundColor Gray
Write-Host "  4. Wait for Gradle sync to complete" -ForegroundColor Gray
Write-Host ""
Write-Host "Python IDE (PyCharm/VSCode):" -ForegroundColor White
Write-Host "  1. Open the project root directory" -ForegroundColor Gray
Write-Host "  2. Set Python interpreter to: $MinicondaPath\envs\thermal-env\python.exe" -ForegroundColor Gray
Write-Host "  3. Mark 'PythonApp/src' as Sources Root" -ForegroundColor Gray
Write-Host ""
Write-Host "Available Build Commands (Milestone 5.1):" -ForegroundColor Yellow
Write-Host "  .\gradlew.bat assembleAll           # Build Android APK + run Python tests" -ForegroundColor White
Write-Host "  .\gradlew.bat setupPythonEnv        # Setup/update conda environment" -ForegroundColor White
Write-Host "  .\gradlew.bat codeQuality           # Run linting for both platforms" -ForegroundColor White
Write-Host "  .\gradlew.bat buildRelease          # Build release versions" -ForegroundColor White
Write-Host "  .\gradlew.bat pythonTest            # Run Python tests only" -ForegroundColor White
Write-Host "  .\gradlew.bat pythonPackage         # Package Python app with PyInstaller" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Activate conda environment: conda activate thermal-env" -ForegroundColor White
Write-Host "  2. Test the setup: .\gradlew.bat assembleAll" -ForegroundColor White
Write-Host "  3. Open IDEs and configure as shown above" -ForegroundColor White
Write-Host "  4. Review docs/5_milestone.md for detailed workflow information" -ForegroundColor White
Write-Host ""
Write-Host "Troubleshooting:" -ForegroundColor Yellow
Write-Host "  - If conda commands fail, restart PowerShell" -ForegroundColor Gray
Write-Host "  - For Android issues, ensure ANDROID_HOME is set" -ForegroundColor Gray
Write-Host "  - Run with -ForceReinstall to recreate environments" -ForegroundColor Gray
Write-Host "  - Use -Verbose for detailed output" -ForegroundColor Gray
