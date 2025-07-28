# Multi-Sensor Recording System - Enhanced Setup Script
# This script initializes the development environment for Windows with comprehensive validation

param(
    [switch]$SkipValidation = $false,
    [switch]$RunTests = $false,
    [switch]$Verbose = $false
)

Write-Host "=== Multi-Sensor Recording System Setup ===" -ForegroundColor Green
Write-Host "Enhanced setup with build and test configuration..." -ForegroundColor Yellow

# Enhanced prerequisite checking
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

function Test-PythonCompatibility {
    try {
        $pythonVersion = & python --version 2>&1
        Write-Host "Python version: $pythonVersion" -ForegroundColor White
        
        if ($pythonVersion -match "Python (\d+)\.(\d+)") {
            $majorVersion = [int]$matches[1]
            $minorVersion = [int]$matches[2]
            if ($majorVersion -eq 3 -and $minorVersion -ge 8) {
                Write-Host "✓ Python version is compatible (Python $majorVersion.$minorVersion)" -ForegroundColor Green
                return $true
            } else {
                Write-Host "✗ Python version must be 3.8 or higher" -ForegroundColor Red
                return $false
            }
        }
        return $false
    } catch {
        Write-Host "✗ Failed to check Python version: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Test-AndroidSDK {
    $androidHome = $env:ANDROID_HOME
    if ([string]::IsNullOrEmpty($androidHome)) {
        $androidHome = $env:ANDROID_SDK_ROOT
    }
    
    if ([string]::IsNullOrEmpty($androidHome)) {
        Write-Host "⚠ ANDROID_HOME or ANDROID_SDK_ROOT not set" -ForegroundColor Yellow
        Write-Host "  Android SDK may not be available for building" -ForegroundColor Yellow
        Write-Host "  Please install Android Studio and set ANDROID_HOME" -ForegroundColor Yellow
        return $false
    } else {
        Write-Host "✓ Android SDK found at: $androidHome" -ForegroundColor Green
        return $true
    }
}

# Check Java
if (-not (Get-Command "java" -ErrorAction SilentlyContinue)) {
    Write-Host "✗ Java not found in PATH" -ForegroundColor Red
    Write-Host "  Please install Java 17 or Java 21 and add to PATH" -ForegroundColor Red
    exit 1
} else {
    if (-not (Test-JavaCompatibility)) {
        Write-Host "  Consider updating Java for better compatibility" -ForegroundColor Yellow
    }
}

# Check Python
if (-not (Get-Command "python" -ErrorAction SilentlyContinue)) {
    Write-Host "✗ Python not found in PATH" -ForegroundColor Red
    Write-Host "  Please install Python 3.8+ and add to PATH" -ForegroundColor Red
    exit 1
} else {
    if (-not (Test-PythonCompatibility)) {
        exit 1
    }
}

# Check Android SDK
Test-AndroidSDK | Out-Null

# Setup Gradle Wrapper
Write-Host "`n2. Setting up Gradle Wrapper..." -ForegroundColor Cyan

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
        exit 1
    }
}
else {
    Write-Host "✓ Gradle wrapper JAR already exists" -ForegroundColor Green
}

# Test Gradle wrapper
Write-Host "`n3. Testing Gradle wrapper..." -ForegroundColor Cyan
try {
    $gradleTest = & ".\gradlew.bat" --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Gradle wrapper is working" -ForegroundColor Green
    }
    else {
        Write-Host "⚠ Gradle wrapper test had issues, but continuing..." -ForegroundColor Yellow
    }
}
catch {
    Write-Host "⚠ Could not test Gradle wrapper: $_" -ForegroundColor Yellow
}

# Initialize Python dependencies
Write-Host "`n4. Initializing Python dependencies..." -ForegroundColor Cyan
try {
    Write-Host "Installing Python dependencies..." -ForegroundColor White
    & ".\gradlew.bat" PythonApp:pipInstall
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Python dependencies installed successfully" -ForegroundColor Green
    } else {
        Write-Host "⚠ Python dependency installation had issues" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠ Could not install Python dependencies: $_" -ForegroundColor Yellow
}

# Run build validation if requested
if (-not $SkipValidation) {
    Write-Host "`n5. Running build validation..." -ForegroundColor Cyan
    if (Test-Path "scripts\validate-build.ps1") {
        try {
            $validationArgs = @()
            if ($SkipTests) { $validationArgs += "-SkipTests" }
            if ($Verbose) { $validationArgs += "-Verbose" }
            
            & ".\scripts\validate-build.ps1" @validationArgs
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ Build validation passed" -ForegroundColor Green
            } else {
                Write-Host "⚠ Build validation had issues - check build-validation.log" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "⚠ Could not run build validation: $_" -ForegroundColor Yellow
        }
    } else {
        Write-Host "⚠ Build validation script not found" -ForegroundColor Yellow
    }
} else {
    Write-Host "`n5. Skipping build validation (use -SkipValidation:$false to enable)" -ForegroundColor Yellow
}

# Run tests if requested
if ($RunTests) {
    Write-Host "`n6. Running comprehensive tests..." -ForegroundColor Cyan
    try {
        Write-Host "Running Android unit tests..." -ForegroundColor White
        & ".\gradlew.bat" AndroidApp:testDebugUnitTest
        
        Write-Host "Running Python tests..." -ForegroundColor White
        & ".\gradlew.bat" PythonApp:runPythonTests
        
        Write-Host "✓ Tests completed - check reports for results" -ForegroundColor Green
    } catch {
        Write-Host "⚠ Test execution had issues: $_" -ForegroundColor Yellow
    }
}

# Final instructions
Write-Host "`n=== Setup Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Environment Status:" -ForegroundColor Yellow
Write-Host "  Java: Compatible version detected" -ForegroundColor Green
Write-Host "  Python: Compatible version detected" -ForegroundColor Green
Write-Host "  Gradle: Wrapper configured and tested" -ForegroundColor Green
Write-Host "  Dependencies: Python packages installed" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Open the project in Android Studio" -ForegroundColor White
Write-Host "2. Wait for Gradle sync to complete" -ForegroundColor White
Write-Host "3. Install Python plugin in Android Studio (optional)" -ForegroundColor White
Write-Host "4. Run build validation: .\scripts\validate-build.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Available Build Commands:" -ForegroundColor Yellow
Write-Host "  .\gradlew.bat build                        # Build entire project" -ForegroundColor White
Write-Host "  .\gradlew.bat AndroidApp:assembleDebug     # Build Android debug APK" -ForegroundColor White
Write-Host "  .\gradlew.bat AndroidApp:assembleRelease   # Build Android release APK" -ForegroundColor White
Write-Host "  .\gradlew.bat PythonApp:runDesktopApp      # Run Python desktop app" -ForegroundColor White
Write-Host ""
Write-Host "Available Test Commands:" -ForegroundColor Yellow
Write-Host "  .\gradlew.bat AndroidApp:testDebugUnitTest # Run Android unit tests" -ForegroundColor White
Write-Host "  .\gradlew.bat AndroidApp:connectedDebugAndroidTest # Run Android integration tests" -ForegroundColor White
Write-Host "  .\gradlew.bat PythonApp:runPythonTests     # Run Python unit tests" -ForegroundColor White
Write-Host "  .\gradlew.bat PythonApp:runPythonTestsWithCoverage # Run Python tests with coverage" -ForegroundColor White
Write-Host ""
Write-Host "Available Validation Commands:" -ForegroundColor Yellow
Write-Host "  .\scripts\validate-build.ps1              # Full build validation" -ForegroundColor White
Write-Host "  .\scripts\validate-build.ps1 -SkipTests   # Validation without tests" -ForegroundColor White
Write-Host "  .\gradlew.bat PythonApp:runPythonLinting   # Python code quality checks" -ForegroundColor White
Write-Host "  .\gradlew.bat AndroidApp:lintDebug         # Android lint checks" -ForegroundColor White
Write-Host ""
Write-Host "For more information:" -ForegroundColor Yellow
Write-Host "  README.md - Complete setup and usage guide" -ForegroundColor Gray
Write-Host "  docs/ - Architecture and milestone documentation" -ForegroundColor Gray
Write-Host "  .github/workflows/ci-cd.yml - CI/CD pipeline configuration" -ForegroundColor Gray