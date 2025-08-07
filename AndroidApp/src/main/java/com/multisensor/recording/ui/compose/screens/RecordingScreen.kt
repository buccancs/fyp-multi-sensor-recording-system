package com.multisensor.recording.ui.compose.screens

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
    onNavigateToPreview: () -> Unit = {},
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

            // Quick thermal preview card with navigation to full preview
            ThermalPreviewCard(
                thermalBitmap = uiState.currentThermalFrame,
                isRecording = uiState.isRecording,
                onNavigateToPreview = onNavigateToPreview
            )

            // Color palette selector
            ColorPaletteSelector(
                currentPalette = uiState.colorPalette,
                onPaletteSelect = { /* TODO: Add to viewModel */ }
            )
        }
    }
}

@Composable
private fun ThermalPreviewCard(
    thermalBitmap: android.graphics.Bitmap?,
    isRecording: Boolean,
    onNavigateToPreview: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .height(200.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
        onClick = onNavigateToPreview
    ) {
        Box {
            thermalBitmap?.let { bitmap ->
                Image(
                    bitmap = bitmap.asImageBitmap(),
                    contentDescription = "Thermal Preview",
                    modifier = Modifier
                        .fillMaxSize()
                        .clip(RoundedCornerShape(12.dp)),
                    contentScale = ContentScale.Crop
                )
            } ?: run {
                // Placeholder for thermal preview
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .background(
                            color = MaterialTheme.colorScheme.surfaceVariant,
                            shape = RoundedCornerShape(12.dp)
                        ),
                    contentAlignment = Alignment.Center
                ) {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Default.Visibility,
                            contentDescription = "View thermal preview",
                            modifier = Modifier.size(32.dp),
                            tint = MaterialTheme.colorScheme.primary
                        )
                        Text(
                            text = "Tap to View Thermal Preview",
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurface
                        )
                    }
                }
            }
            
            // Recording indicator overlay
            if (isRecording) {
                Box(
                    modifier = Modifier
                        .align(Alignment.TopEnd)
                        .padding(8.dp)
                        .background(
                            color = RecordingActive.copy(alpha = 0.9f),
                            shape = RoundedCornerShape(4.dp)
                        )
                        .padding(horizontal = 8.dp, vertical = 4.dp)
                ) {
                    Text(
                        text = "REC",
                        style = MaterialTheme.typography.labelSmall,
                        color = Color.White,
                        fontWeight = FontWeight.Bold
                    )
                }
            }
            
            // Navigation hint overlay
            Box(
                modifier = Modifier
                    .align(Alignment.BottomEnd)
                    .padding(8.dp)
                    .background(
                        color = MaterialTheme.colorScheme.surface.copy(alpha = 0.9f),
                        shape = RoundedCornerShape(4.dp)
                    )
                    .padding(horizontal = 8.dp, vertical = 4.dp)
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.OpenInFull,
                        contentDescription = "View full screen",
                        modifier = Modifier.size(12.dp),
                        tint = MaterialTheme.colorScheme.onSurface
                    )
                    Text(
                        text = "Full View",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurface
                    )
                }
            }
        }
    }
}


