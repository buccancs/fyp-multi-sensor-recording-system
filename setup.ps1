# Multi-Sensor Recording System - Setup Script
# This script initializes the development environment for Windows

Write-Host "=== Multi-Sensor Recording System Setup ===" -ForegroundColor Green
Write-Host "Setting up development environment..." -ForegroundColor Yellow

# Check prerequisites
Write-Host "`n1. Checking prerequisites..." -ForegroundColor Cyan

# Check Java
try {
    $null = Get-Command "java" -ErrorAction Stop
    $javaVersion = java -version 2>&1 | Select-String "version" | Select-Object -First 1
    Write-Host "✓ Java found: $javaVersion" -ForegroundColor Green
}
catch {
    Write-Host "✗ Java not found. Please install Java 8+ or Android Studio." -ForegroundColor Red
    exit 1
}

# Check Python
try {
    $null = Get-Command "python" -ErrorAction Stop
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "✗ Python not found. Please install Python 3.8+." -ForegroundColor Red
    exit 1
}

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

# Final instructions
Write-Host "`n=== Setup Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Open the project in Android Studio" -ForegroundColor White
Write-Host "2. Wait for Gradle sync to complete" -ForegroundColor White
Write-Host "3. Install Python plugin in Android Studio" -ForegroundColor White
Write-Host ""
Write-Host "Available commands:" -ForegroundColor Yellow
Write-Host "  .\gradlew.bat :AndroidApp:assembleDebug    # Build Android app" -ForegroundColor White
Write-Host "  .\gradlew.bat :PythonApp:runDesktopApp     # Run Python desktop app" -ForegroundColor White
Write-Host "  .\gradlew.bat :PythonApp:testPythonSetup   # Test Python environment" -ForegroundColor White
Write-Host ""
Write-Host "For more information, see README.md" -ForegroundColor Gray