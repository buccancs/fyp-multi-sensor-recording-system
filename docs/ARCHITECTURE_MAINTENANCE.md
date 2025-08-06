# Architecture Maintenance Guidelines

## Overview

This document provides guidelines for maintaining architectural integrity as the Multi-Sensor Recording System evolves. The architecture enforcement mechanisms put in place help prevent architectural drift and ensure adherence to established design principles.

## Architecture Enforcement Mechanisms

### 1. Static Analysis (Detekt)

#### Configuration
The `detekt.yml` file includes architecture enforcement rules:

```yaml
style:
  ForbiddenImport:
    active: true
    imports: 
      - 'com.multisensor.recording.network.**'  # UI layer cannot import network
      - 'com.multisensor.recording.service.**'  # UI layer cannot import services
      - 'android.util.Log'                      # Use centralized logging
    excludes: 
      - '**/network/**'     # Network package can import these
      - '**/service/**'     # Service package can import these
      - '**/util/**'        # Utility package exceptions
      - '**/di/**'          # DI package exceptions
```

#### Running Checks
```bash
# Run detekt with architecture rules
./gradlew detekt

# Run detekt with specific focus on style rules
./gradlew detekt --continue

# Generate HTML report
./gradlew detekt --no-daemon
```

### 2. Architecture Tests (Android)

#### Location
`AndroidApp/src/test/java/com/multisensor/recording/util/SimpleArchitectureTest.kt`

#### Running Tests
```bash
# Run architecture tests specifically
./gradlew :AndroidApp:testDevDebugUnitTest --tests="*SimpleArchitectureTest*"

# Run all unit tests
./gradlew :AndroidApp:testDevDebugUnitTest
```

#### Test Coverage
- UI layer dependency validation
- Controller isolation checks
- Recording component separation
- Network layer independence
- Infrastructure utility usage
- Dependency injection scope validation

### 3. Python Architecture Tests

#### Location
`PythonApp/test_architecture_enforcement.py`

#### Running Tests
```bash
cd PythonApp
python test_architecture_enforcement.py

# Verbose output
python test_architecture_enforcement.py --verbose
```

#### Test Coverage
- GUI layer isolation
- Manager component separation
- Network layer independence
- Infrastructure utilities usage
- Error handling consistency
- Session management separation

## Maintenance Procedures

### 1. Weekly Architecture Reviews

#### Checklist
- [ ] Run architecture enforcement tests
- [ ] Review detekt reports for new violations
- [ ] Check for new cross-cutting concerns
- [ ] Validate layer separation in new components
- [ ] Review dependency injection scope usage

#### Commands
```bash
# Complete architecture validation
./gradlew detekt
./gradlew :AndroidApp:testDevDebugUnitTest --tests="*SimpleArchitectureTest*"
cd PythonApp && python test_architecture_enforcement.py
```

### 2. Code Review Guidelines

#### Architecture Review Checklist
```markdown
## Architecture Review Checklist

- [ ] **Layer Separation**: New code follows established layer boundaries
- [ ] **Dependency Direction**: Dependencies point toward lower layers only
- [ ] **Cross-Cutting Concerns**: Uses centralized utilities (logging, sync, error handling)
- [ ] **Dependency Injection**: Proper scope annotations (`@Singleton`, `@ActivityScoped`)
- [ ] **Test Coverage**: Architecture tests updated for new components
- [ ] **Documentation**: Updates to relevant architecture documentation

### Forbidden Patterns
- [ ] UI layer directly importing from `network.**` or `service.**`
- [ ] Controllers importing UI components (`Activity`, `Fragment`)
- [ ] Direct use of `android.util.Log` instead of centralized logger
- [ ] Manager classes importing GUI frameworks (`PyQt5.QtWidgets`)
```

#### Review Commands
```bash
# Check specific files for architecture violations
./gradlew detekt --include="**/YourNewFile.kt"

# Test specific architecture constraints
./gradlew :AndroidApp:testDevDebugUnitTest --tests="*SimpleArchitectureTest.UI_layer_should_not_directly_import*"
```

### 3. Adding New Components

#### Step-by-Step Process

1. **Identify Layer**
   ```kotlin
   // Determine appropriate architectural layer
   when (component_type) {
       "Activity", "Fragment", "ViewModel" -> UI_LAYER
       "Controller", "Manager", "UseCase" -> BUSINESS_LOGIC_LAYER  
       "Service", "Repository", "API" -> SERVICE_LAYER
       "Logger", "Security", "Utils" -> INFRASTRUCTURE_LAYER
   }
   ```

2. **Define Dependencies**
   ```kotlin
   // Use dependency injection for all external dependencies
   @Singleton  // or appropriate scope
   class NewController @Inject constructor(
       private val logger: Logger,  // Infrastructure dependency
       private val repository: DataRepository,  // Service dependency
       // NO UI dependencies here
   )
   ```

3. **Update Architecture Tests**
   ```kotlin
   @Test
   fun `new component should follow architecture constraints`() {
       val newComponentFiles = getKotlinFilesInPackage("new_component")
       // Add validation for new component
   }
   ```

4. **Update Documentation**
   - Add component to relevant architecture diagrams
   - Update layer descriptions in `docs/ARCHITECTURE.md`
   - Document any new cross-cutting concerns

### 4. Handling Architecture Violations

#### When Tests Fail

1. **Identify Violation Type**
   ```bash
   # Run specific test to see failure details
   ./gradlew :AndroidApp:testDevDebugUnitTest --tests="*UI_layer_should_not_directly_import*" --info
   ```

2. **Assess Legitimacy**
   - Is this a legitimate architectural violation?
   - Or is this an acceptable exception that needs documentation?

3. **Resolution Strategies**

   **Option A: Fix the Violation**
   ```kotlin
   // Before: UI directly accessing service
   class MainActivity @Inject constructor(
       private val networkService: NetworkService  // VIOLATION
   )
   
   // After: UI accessing through controller
   class MainActivity @Inject constructor(
       private val connectionController: ConnectionController  // CORRECT
   )
   ```

   **Option B: Document Exception**
   ```kotlin
   // If violation is justified, document in test
   @Test
   fun `UI layer exceptions for specific cases`() {
       // Document why specific files are allowed to violate rules
       val legitimateExceptions = listOf(
           "MainActivity.kt" // Needs direct access for initialization
       )
   }
   ```

   **Option C: Update Architecture**
   ```yaml
   # Update detekt.yml if architecture pattern changes
   style:
     ForbiddenImport:
       excludes:
         - '**/specific_case/**'  # Add new exception
   ```

### 5. Updating Architecture Documentation

#### When to Update
- New architectural layers introduced
- Significant changes to cross-cutting concerns
- Updates to scaling strategies
- Changes to dependency injection patterns

#### Update Process
1. **Identify Affected Documentation**
   - `docs/ARCHITECTURE.md` - Layer changes
   - `docs/CROSS_CUTTING_CONCERNS.md` - Infrastructure changes
   - `docs/SCALING_ARCHITECTURE.md` - Scaling changes
   - `README.md` - Overview changes

2. **Update Diagrams**
   ```bash
   # Check which diagrams need updates
   ls docs/diagrams/
   # Update relevant architecture diagrams
   ```

3. **Validate Documentation**
   - Ensure examples in documentation compile
   - Check that architecture tests match documentation
   - Verify consistency across all documentation

### 6. Continuous Integration Integration

#### Build Pipeline Integration
```yaml
# Example CI configuration
architecture_validation:
  runs-on: ubuntu-latest
  steps:
    - name: Run Architecture Tests
      run: |
        ./gradlew detekt
        ./gradlew :AndroidApp:testDevDebugUnitTest --tests="*SimpleArchitectureTest*"
        cd PythonApp && python test_architecture_enforcement.py
    
    - name: Fail on Architecture Violations
      run: |
        if [[ $? -ne 0 ]]; then
          echo "Architecture violations detected. Please fix before merging."
          exit 1
        fi
```

#### Automated Reporting
```bash
# Generate architecture compliance report
./gradlew detekt --output=build/reports/detekt/architecture-report.html
```

## Troubleshooting Common Issues

### 1. False Positives in Tests

**Problem**: Architecture test fails but violation seems legitimate

**Solution**: 
```kotlin
// Add specific exclusions to tests
private fun isLegitimateException(file: File): Boolean {
    val legitimateExceptions = listOf(
        "DaggerApplication.kt",  // DI bootstrap
        "TestUtilities.kt"       // Test infrastructure
    )
    return legitimateExceptions.any { file.name.contains(it) }
}
```

### 2. Performance Impact of Tests

**Problem**: Architecture tests slow down build

**Solution**:
```kotlin
// Cache file scanning results
private val fileCache = mutableMapOf<String, List<File>>()

private fun getCachedKotlinFiles(packageName: String): List<File> {
    return fileCache.getOrPut(packageName) {
        getKotlinFilesInPackage(packageName)
    }
}
```

### 3. Complex Dependency Patterns

**Problem**: Legitimate cross-layer communication needed

**Solution**:
```kotlin
// Use event-driven patterns for cross-layer communication
class EventBus @Inject constructor() {
    fun publishEvent(event: ArchitectureEvent) {
        // Safe cross-layer communication
    }
}
```

## Best Practices Summary

1. **Run architecture tests regularly** during development
2. **Update tests when adding new components** or layers
3. **Document exceptions** rather than disabling rules
4. **Keep documentation current** with implementation
5. **Use CI/CD integration** to prevent violations from being merged
6. **Regular architecture reviews** to assess and improve patterns
7. **Educate team members** on architectural principles and enforcement

This maintenance approach ensures that the Multi-Sensor Recording System maintains its architectural integrity while allowing for controlled evolution and growth.