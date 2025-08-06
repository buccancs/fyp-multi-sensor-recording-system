# Developer Guide: Using the Refactored Architecture

## Overview

This guide explains how to use the newly refactored architecture components that follow clean MVVM principles and single responsibility patterns.

## Quick Start

### Using the New MainViewModel

```kotlin
class MainActivity : AppCompatActivity() {
    
    private val viewModel: MainViewModelRefactored by viewModels()
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Observe UI state changes
        lifecycleScope.launch {
            viewModel.uiState.collect { state ->
                updateUI(state)
            }
        }
        
        // Initialize system
        val textureView = findViewById<TextureView>(R.id.cameraPreview)
        val thermalSurfaceView = findViewById<SurfaceView>(R.id.thermalPreview)
        viewModel.initializeSystem(textureView, thermalSurfaceView)
    }
    
    private fun updateUI(state: MainUiState) {
        // Update UI based on reactive state
        recordButton.isEnabled = state.isInitialized && !state.isRecording
        stopButton.isEnabled = state.isRecording
        statusText.text = state.statusText
        
        // Handle errors
        if (state.showErrorDialog && state.errorMessage != null) {
            showErrorDialog(state.errorMessage)
            viewModel.clearError()
        }
    }
}
```

### Recording Operations

```kotlin
// Start recording
recordButton.setOnClickListener {
    viewModel.startRecording()
}

// Stop recording  
stopButton.setOnClickListener {
    viewModel.stopRecording()
}

// Capture RAW image during recording
rawCaptureButton.setOnClickListener {
    viewModel.captureRawImage()
}
```

### Device Management

```kotlin
// Connect to PC
connectPcButton.setOnClickListener {
    viewModel.connectToPC()
}

// Scan for devices
scanButton.setOnClickListener {
    viewModel.scanForDevices()
}

// Refresh device status
refreshButton.setOnClickListener {
    viewModel.refreshSystemStatus()
}
```

### File Operations

```kotlin
// Transfer files to PC
transferButton.setOnClickListener {
    viewModel.transferFilesToPC()
}

// Export data
exportButton.setOnClickListener {
    viewModel.exportData()
}

// Browse files
browseButton.setOnClickListener {
    viewModel.browseFiles()
}
```

### Calibration

```kotlin
// Run full system calibration
calibrateButton.setOnClickListener {
    viewModel.runCalibration()
}

// Camera-specific calibration
cameraCalibrationButton.setOnClickListener {
    viewModel.startCameraCalibration()
}

// Thermal calibration
thermalCalibrationButton.setOnClickListener {
    viewModel.startThermalCalibration()
}
```

## Working with Individual Controllers

### Direct Controller Usage (Advanced)

If you need to use controllers directly (e.g., in a service or for testing):

```kotlin
@AndroidEntryPoint
class RecordingService : Service() {
    
    @Inject
    lateinit var recordingController: RecordingSessionController
    
    @Inject
    lateinit var deviceManager: DeviceConnectionManager
    
    fun startBackgroundRecording() {
        lifecycleScope.launch {
            // Initialize devices first
            val result = deviceManager.initializeAllDevices()
            if (result.isSuccess) {
                // Start recording with specific config
                val config = RecordingSessionController.RecordingConfig(
                    recordVideo = true,
                    captureRaw = false,
                    enableThermal = true,
                    enableShimmer = true
                )
                recordingController.startRecording(config)
            }
        }
    }
}
```

### Observing Controller State

```kotlin
class CustomFragment : Fragment() {
    
    @Inject
    lateinit var recordingController: RecordingSessionController
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        // Observe recording state directly
        viewLifecycleOwner.lifecycleScope.launch {
            recordingController.recordingState.collect { state ->
                when {
                    state.isRecording -> showRecordingUI()
                    state.isPaused -> showPausedUI()
                    state.recordingError != null -> showError(state.recordingError)
                }
            }
        }
    }
}
```

## Testing Your Code

### Testing with Mock Controllers

```kotlin
class MyActivityTest {
    
    @Mock
    lateinit var mockRecordingController: RecordingSessionController
    
    @Mock 
    lateinit var mockDeviceManager: DeviceConnectionManager
    
    @Test
    fun `should start recording when button clicked`() = runTest {
        // Arrange
        val activity = createActivity()
        `when`(mockRecordingController.startRecording()).thenReturn(Result.success("Started"))
        
        // Act
        activity.findViewById<Button>(R.id.recordButton).performClick()
        
        // Assert
        verify(mockRecordingController).startRecording()
    }
}
```

### Integration Testing

```kotlin
@HiltAndroidTest
class RecordingIntegrationTest {
    
    @get:Rule
    val hiltRule = HiltAndroidRule(this)
    
    @Inject
    lateinit var recordingController: RecordingSessionController
    
    @Test
    fun `should coordinate recording across all devices`() = runTest {
        hiltRule.inject()
        
        val config = RecordingSessionController.RecordingConfig(
            recordVideo = true,
            enableThermal = true,
            enableShimmer = true
        )
        
        val result = recordingController.startRecording(config)
        assertTrue(result.isSuccess)
        
        val state = recordingController.getCurrentState()
        assertTrue(state.isRecording)
        assertTrue(state.deviceStatuses.cameraRecording)
    }
}
```

## Error Handling Patterns

### Reactive Error Handling

```kotlin
// In your UI class
viewModel.uiState.collect { state ->
    when {
        state.errorMessage != null -> {
            when {
                state.errorMessage.contains("recording") -> handleRecordingError(state.errorMessage)
                state.errorMessage.contains("connection") -> handleConnectionError(state.errorMessage)
                state.errorMessage.contains("calibration") -> handleCalibrationError(state.errorMessage)
                else -> handleGenericError(state.errorMessage)
            }
            viewModel.clearError()
        }
    }
}
```

### Controller-Level Error Handling

```kotlin
// When calling controller methods directly
lifecycleScope.launch {
    val result = recordingController.startRecording(config)
    
    result.fold(
        onSuccess = { message -> 
            showSuccessMessage(message)
        },
        onFailure = { exception ->
            when (exception) {
                is IllegalStateException -> showUserError("Cannot start recording: ${exception.message}")
                is RuntimeException -> showSystemError("Recording system error: ${exception.message}")
                else -> showGenericError("Unexpected error: ${exception.message}")
            }
        }
    )
}
```

## Best Practices

### 1. Always Use Reactive State
```kotlin
// ✅ Good - Reactive
viewModel.uiState.collect { state ->
    updateButton.isEnabled = !state.isTransferring
}

// ❌ Bad - Imperative
if (!viewModel.isTransferring()) {
    updateButton.isEnabled = true
}
```

### 2. Delegate Business Logic
```kotlin
// ✅ Good - Delegate to controller
class MyViewModel @Inject constructor(
    private val deviceManager: DeviceConnectionManager
) {
    fun connectDevices() {
        viewModelScope.launch {
            deviceManager.connectToPC()
        }
    }
}

// ❌ Bad - Business logic in ViewModel
class MyViewModel {
    fun connectDevices() {
        // Don't put device connection logic here
    }
}
```

### 3. Use Proper Scoping
```kotlin
// ✅ Good - Proper scoping for controllers
@Singleton
class MyController @Inject constructor(...)

// ✅ Good - ViewModel scoping
@HiltViewModel
class MyViewModel @Inject constructor(...)
```

### 4. Handle Lifecycles Properly
```kotlin
// ✅ Good - Lifecycle-aware collection
viewLifecycleOwner.lifecycleScope.launch {
    viewModel.uiState.collect { state ->
        updateUI(state)
    }
}

// ❌ Bad - Not lifecycle-aware
GlobalScope.launch {
    viewModel.uiState.collect { state ->
        updateUI(state) // May update UI after destruction
    }
}
```

## Migration Guide

### Migrating from Old MainViewModel

1. **Replace ViewModel Reference**:
```kotlin
// Old
private val viewModel: MainViewModel by viewModels()

// New  
private val viewModel: MainViewModelRefactored by viewModels()
```

2. **Update State Observation**:
```kotlin
// Old - Direct property access
if (viewModel.isRecording) { ... }

// New - Reactive state
viewModel.uiState.collect { state ->
    if (state.isRecording) { ... }
}
```

3. **Update Method Calls** (methods remain the same):
```kotlin
// These work the same in both versions
viewModel.startRecording()
viewModel.stopRecording()
viewModel.connectToPC()
// etc.
```

### Adding New Features

When adding new functionality:

1. **Identify the Domain**: Does this belong in recording, devices, files, or calibration?
2. **Add to Appropriate Controller**: Extend the relevant controller with new methods
3. **Update UI State**: Add new state properties if needed
4. **Create Tests**: Write focused unit tests for the new functionality
5. **Document**: Add KDoc documentation for new public APIs

## Common Patterns

### Configuration-Based Operations
```kotlin
val config = RecordingSessionController.RecordingConfig(
    recordVideo = userPreferences.recordVideo,
    captureRaw = userPreferences.captureRaw,
    enableThermal = deviceManager.getCurrentState().thermalConnected
)
recordingController.startRecording(config)
```

### Progress Tracking
```kotlin
calibrationManager.calibrationState.collect { state ->
    if (state.progress != null) {
        progressBar.progress = state.progress.progressPercent
        statusText.text = state.progress.currentStep
    }
}
```

### Multi-Controller Coordination
```kotlin
// Example: Only allow recording if devices are connected
combine(
    deviceManager.connectionState,
    recordingController.recordingState
) { deviceState, recordingState ->
    val canRecord = deviceState.cameraConnected && !recordingState.isRecording
    recordButton.isEnabled = canRecord
}.launchIn(lifecycleScope)
```

This architecture provides a solid foundation for maintainable, testable Android development following clean architecture principles.