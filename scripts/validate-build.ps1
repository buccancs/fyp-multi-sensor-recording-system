# Build Validation Script for Multi-Sensor Recording System
# This script validates the build environment and runs comprehensive tests

param(
    [switch]$SkipTests = $false,
    [switch]$Verbose = $false,
    [string]$LogFile = "build-validation.log"
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Initialize logging
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    Write-Host $logMessage
    Add-Content -Path $LogFile -Value $logMessage
}

function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

function Test-JavaVersion {
    try {
        $javaVersion = & java -version 2>&1 | Select-String "version" | ForEach-Object { $_.ToString() }
        Write-Log "Java version: $javaVersion"
        
        # Extract version number
        if ($javaVersion -match '"(\d+)\.') {
            $majorVersion = [int]$matches[1]
            if ($majorVersion -ge 17 -and $majorVersion -le 21) {
                Write-Log "Java version is compatible (Java $majorVersion)" "SUCCESS"
                return $true
            } elseif ($majorVersion -eq 24) {
                Write-Log "Java 24 detected - this may cause compatibility issues with Gradle 8.4" "WARNING"
                Write-Log "Please use Java 17 or Java 21 for best compatibility" "WARNING"
                return $false
            } else {
                Write-Log "Java version $majorVersion is not in the recommended range (17-21)" "ERROR"
                return $false
            }
        }
        return $false
    } catch {
        Write-Log "Failed to check Java version: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Test-PythonVersion {
    try {
        $pythonVersion = & python --version 2>&1
        Write-Log "Python version: $pythonVersion"
        
        if ($pythonVersion -match "Python (\d+)\.(\d+)") {
            $majorVersion = [int]$matches[1]
            $minorVersion = [int]$matches[2]
            if ($majorVersion -eq 3 -and $minorVersion -ge 8) {
                Write-Log "Python version is compatible" "SUCCESS"
                return $true
            } else {
                Write-Log "Python version must be 3.8 or higher" "ERROR"
                return $false
            }
        }
        return $false
    } catch {
        Write-Log "Failed to check Python version: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Test-GradleWrapper {
    if (Test-Path "gradlew.bat") {
        Write-Log "Gradle wrapper found" "SUCCESS"
        try {
            $gradleVersion = & .\gradlew.bat --version 2>&1 | Select-String "Gradle" | Select-Object -First 1
            Write-Log "Gradle version: $gradleVersion"
            return $true
        } catch {
            Write-Log "Failed to execute Gradle wrapper: $($_.Exception.Message)" "ERROR"
            return $false
        }
    } else {
        Write-Log "Gradle wrapper not found" "ERROR"
        return $false
    }
}

function Test-AndroidSDK {
    $androidHome = $env:ANDROID_HOME
    if ([string]::IsNullOrEmpty($androidHome)) {
        $androidHome = $env:ANDROID_SDK_ROOT
    }
    
    if ([string]::IsNullOrEmpty($androidHome)) {
        Write-Log "ANDROID_HOME or ANDROID_SDK_ROOT not set" "WARNING"
        Write-Log "Android SDK may not be available for building" "WARNING"
        return $false
    } else {
        Write-Log "Android SDK found at: $androidHome" "SUCCESS"
        return $true
    }
}

function Validate-BuildFiles {
    Write-Log "Validating build configuration files..."
    
    $requiredFiles = @(
        "build.gradle",
        "settings.gradle",
        "gradle.properties",
        "AndroidApp\build.gradle",
        "PythonApp\build.gradle"
    )
    
    $allFilesExist = $true
    foreach ($file in $requiredFiles) {
        if (Test-Path $file) {
            Write-Log "Found: $file" "SUCCESS"
        } else {
            Write-Log "Missing: $file" "ERROR"
            $allFilesExist = $false
        }
    }
    
    return $allFilesExist
}

function Run-AndroidBuild {
    Write-Log "Running Android build validation..."
    try {
        Write-Log "Building Android debug APK..."
        & .\gradlew.bat AndroidApp:assembleDebug --stacktrace
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Android build successful" "SUCCESS"
            return $true
        } else {
            Write-Log "Android build failed with exit code $LASTEXITCODE" "ERROR"
            return $false
        }
    } catch {
        Write-Log "Android build failed: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Run-PythonBuild {
    Write-Log "Running Python build validation..."
    try {
        Write-Log "Installing Python dependencies..."
        & .\gradlew.bat PythonApp:pipInstall
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Python dependency installation failed" "ERROR"
            return $false
        }
        
        Write-Log "Testing Python environment..."
        & .\gradlew.bat PythonApp:testPythonSetup
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Python build successful" "SUCCESS"
            return $true
        } else {
            Write-Log "Python build failed with exit code $LASTEXITCODE" "ERROR"
            return $false
        }
    } catch {
        Write-Log "Python build failed: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Run-Tests {
    if ($SkipTests) {
        Write-Log "Skipping tests as requested"
        return $true
    }
    
    Write-Log "Running comprehensive tests..."
    $testsPassed = $true
    
    # Run Android unit tests
    try {
        Write-Log "Running Android unit tests..."
        & .\gradlew.bat AndroidApp:testDebugUnitTest --stacktrace
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Android unit tests failed" "ERROR"
            $testsPassed = $false
        } else {
            Write-Log "Android unit tests passed" "SUCCESS"
        }
    } catch {
        Write-Log "Failed to run Android unit tests: $($_.Exception.Message)" "ERROR"
        $testsPassed = $false
    }
    
    # Run Python tests
    try {
        Write-Log "Running Python tests..."
        & .\gradlew.bat PythonApp:runPythonTests
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Python tests failed" "ERROR"
            $testsPassed = $false
        } else {
            Write-Log "Python tests passed" "SUCCESS"
        }
    } catch {
        Write-Log "Failed to run Python tests: $($_.Exception.Message)" "ERROR"
        $testsPassed = $false
    }
    
    return $testsPassed
}

function Generate-Report {
    Write-Log "Generating build validation report..."
    
    $reportPath = "build-validation-report.html"
    $reportContent = @"
<!DOCTYPE html>
<html>
<head>
    <title>Build Validation Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .success { color: green; }
        .error { color: red; }
        .warning { color: orange; }
        .section { margin: 20px 0; padding: 10px; border: 1px solid #ccc; }
    </style>
</head>
<body>
    <h1>Build Validation Report</h1>
    <p>Generated: $(Get-Date)</p>
    
    <div class="section">
        <h2>Environment Validation</h2>
        <p>See build-validation.log for detailed results</p>
    </div>
    
    <div class="section">
        <h2>Build Results</h2>
        <p>Check the log file for complete build output and test results</p>
    </div>
    
    <div class="section">
        <h2>Recommendations</h2>
        <ul>
            <li>Ensure Java 17 or Java 21 is installed for best compatibility</li>
            <li>Verify Android SDK is properly configured</li>
            <li>Run tests regularly to catch issues early</li>
        </ul>
    </div>
</body>
</html>
"@
    
    Set-Content -Path $reportPath -Value $reportContent
    Write-Log "Report generated: $reportPath"
}

# Main execution
Write-Log "Starting build validation for Multi-Sensor Recording System"
Write-Log "Log file: $LogFile"

$validationPassed = $true

# Environment validation
Write-Log "=== Environment Validation ==="
if (-not (Test-Command "java")) {
    Write-Log "Java not found in PATH" "ERROR"
    $validationPassed = $false
} else {
    if (-not (Test-JavaVersion)) {
        $validationPassed = $false
    }
}

if (-not (Test-Command "python")) {
    Write-Log "Python not found in PATH" "ERROR"
    $validationPassed = $false
} else {
    if (-not (Test-PythonVersion)) {
        $validationPassed = $false
    }
}

if (-not (Test-GradleWrapper)) {
    $validationPassed = $false
}

Test-AndroidSDK | Out-Null

# Build file validation
Write-Log "=== Build Configuration Validation ==="
if (-not (Validate-BuildFiles)) {
    $validationPassed = $false
}

# Build validation
if ($validationPassed) {
    Write-Log "=== Build Validation ==="
    if (-not (Run-AndroidBuild)) {
        $validationPassed = $false
    }
    
    if (-not (Run-PythonBuild)) {
        $validationPassed = $false
    }
    
    # Test execution
    if (-not (Run-Tests)) {
        $validationPassed = $false
    }
} else {
    Write-Log "Skipping build validation due to environment issues" "WARNING"
}

# Generate report
Generate-Report

# Final result
if ($validationPassed) {
    Write-Log "=== BUILD VALIDATION SUCCESSFUL ===" "SUCCESS"
    exit 0
} else {
    Write-Log "=== BUILD VALIDATION FAILED ===" "ERROR"
    Write-Log "Check the log file for detailed error information" "ERROR"
    exit 1
}