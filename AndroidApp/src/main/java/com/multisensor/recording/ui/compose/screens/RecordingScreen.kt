package com.multisensor.recording.ui.compose.screens
import android.view.SurfaceView
import android.view.TextureView
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.multisensor.recording.recording.DeviceStatus
import com.multisensor.recording.ui.MainUiState
import com.multisensor.recording.ui.MainViewModel
import com.multisensor.recording.ui.components.AnimatedRecordingButton
import com.multisensor.recording.ui.components.CameraPreview
import com.multisensor.recording.ui.components.ColorPaletteSelector
import com.multisensor.recording.ui.components.ThermalPreview
import com.multisensor.recording.ui.components.ThermalPreviewSurface
import com.multisensor.recording.ui.components.SessionStatusCard
import com.multisensor.recording.ui.theme.ConnectionGreen
import com.multisensor.recording.ui.theme.DisconnectedRed
import com.multisensor.recording.ui.theme.RecordingActive
import com.multisensor.recording.ui.theme.RecordingInactive
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RecordingScreen(
    onNavigateToPreview: () -> Unit = {},
    viewModel: MainViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val context = LocalContext.current
    
    // Track preview components readiness
    var cameraTextureView by remember { mutableStateOf<TextureView?>(null) }
    var thermalSurfaceView by remember { mutableStateOf<SurfaceView?>(null) }
    var initializationAttempted by remember { mutableStateOf(false) }
    
    // Camera switching state - true for thermal/IR, false for RGB
    var showThermalCamera by remember { mutableStateOf(false) }

    // Initialize system when both preview components are ready
    LaunchedEffect(cameraTextureView, thermalSurfaceView) {
        if (cameraTextureView != null && !initializationAttempted) {
            initializationAttempted = true
            android.util.Log.d("RecordingScreen", "Starting device initialization with TextureView and SurfaceView")
            
            // Initialize the system with the actual views
            // Note: We need both views for full system initialization even if only one is displayed
            viewModel.initializeSystem(cameraTextureView!!, thermalSurfaceView)
            
            // Also try to connect to PC server automatically
            viewModel.connectToPC()
        }
    }

    // Show any errors that occur during initialization
    if (uiState.showErrorDialog && !uiState.errorMessage.isNullOrBlank()) {
        LaunchedEffect(uiState.errorMessage) {
            // Log the error for debugging
            android.util.Log.e("RecordingScreen", "Initialization error: ${uiState.errorMessage}")
        }
    }
    Scaffold(
        floatingActionButton = {
            AnimatedRecordingButton(
                isRecording = uiState.isRecording,
                onClick = {
                    if (uiState.isRecording) {
                        viewModel.stopRecording()
                    } else {
                        viewModel.startRecording()
                    }
                },
                enabled = uiState.canStartRecording || uiState.canStopRecording
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(16.dp)
                .verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            SessionStatusCard(
                sessionStatus = when {
                    uiState.isRecording -> "Recording"
                    uiState.isInitialized -> "Ready"
                    else -> "Initializing"
                },
                deviceConnections = mapOf(
                    "Camera" to if (uiState.isCameraConnected) DeviceStatus.CONNECTED else DeviceStatus.DISCONNECTED,
                    "Thermal" to if (uiState.isThermalConnected) DeviceStatus.CONNECTED else DeviceStatus.DISCONNECTED,
                    "GSR" to if (uiState.isGsrConnected) DeviceStatus.CONNECTED else DeviceStatus.DISCONNECTED,
                    "PC Connection" to if (uiState.isPcConnected) DeviceStatus.CONNECTED else DeviceStatus.DISCONNECTED
                )
            )
            
            // Camera Preview Switch
            Card(
                modifier = Modifier.fillMaxWidth(),
                elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "Camera Preview",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Text(
                            text = "RGB",
                            style = MaterialTheme.typography.bodyMedium,
                            color = if (!showThermalCamera) MaterialTheme.colorScheme.primary 
                                   else MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        Switch(
                            checked = showThermalCamera,
                            onCheckedChange = { showThermalCamera = it }
                        )
                        Text(
                            text = "Thermal",
                            style = MaterialTheme.typography.bodyMedium,
                            color = if (showThermalCamera) MaterialTheme.colorScheme.primary 
                                   else MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }

            // Camera Preview - Always create both views for initialization, but only display one
            Box {
                // RGB Camera Preview - Always present for initialization
                CameraPreview(
                    isRecording = uiState.isRecording,
                    onTextureViewReady = { textureView ->
                        cameraTextureView = textureView
                    },
                    modifier = if (!showThermalCamera) Modifier else Modifier.size(0.dp)
                )

                // Thermal Camera Preview - Always present for initialization
                ThermalPreviewSurface(
                    isRecording = uiState.isRecording,
                    onSurfaceViewReady = { surfaceView ->
                        thermalSurfaceView = surfaceView
                    },
                    modifier = if (showThermalCamera) Modifier else Modifier.size(0.dp)
                )
            }

            ColorPaletteSelector(
                currentPalette = uiState.colorPalette,
                onPaletteSelect = {  }
            )
        }
    }
}