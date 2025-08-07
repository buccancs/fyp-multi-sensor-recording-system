package com.multisensor.recording.ui.compose.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.multisensor.recording.recording.DeviceStatus
import com.multisensor.recording.ui.MainUiState
import com.multisensor.recording.ui.MainViewModelRefactored
import com.multisensor.recording.ui.components.AnimatedRecordingButton
import com.multisensor.recording.ui.components.ColorPaletteSelector
import com.multisensor.recording.ui.components.EnhancedThermalPreview
import com.multisensor.recording.ui.components.SessionStatusCard
import com.multisensor.recording.ui.theme.ConnectionGreen
import com.multisensor.recording.ui.theme.DisconnectedRed
import com.multisensor.recording.ui.theme.RecordingActive
import com.multisensor.recording.ui.theme.RecordingInactive

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RecordingScreen(
    viewModel: MainViewModelRefactored = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val context = LocalContext.current

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
            // Enhanced session status
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

            // Enhanced thermal preview
            EnhancedThermalPreview(
                thermalBitmap = uiState.currentThermalFrame,
                isRecording = uiState.isRecording,
                temperatureRange = uiState.temperatureRange,
                colorPalette = uiState.colorPalette,
                onPaletteChange = { /* TODO: Add to viewModel */ },
                onTemperatureRangeChange = { /* TODO: Add to viewModel */ }
            )

            // Color palette selector
            ColorPaletteSelector(
                currentPalette = uiState.colorPalette,
                onPaletteSelect = { /* TODO: Add to viewModel */ }
            )
        }
    }
}


