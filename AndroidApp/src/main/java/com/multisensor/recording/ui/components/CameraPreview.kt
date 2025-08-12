package com.multisensor.recording.ui.components

import android.view.SurfaceView
import android.view.TextureView
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Camera
import androidx.compose.material.icons.filled.FiberManualRecord
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.multisensor.recording.ui.MainViewModel

@Composable
fun CameraPreview(
    isRecording: Boolean,
    modifier: Modifier = Modifier,
    onTextureViewReady: (TextureView) -> Unit = {}
) {
    val context = LocalContext.current
    val uiState by hiltViewModel<MainViewModel>().uiState.collectAsStateWithLifecycle()
    var textureView by remember { mutableStateOf<TextureView?>(null) }

    // Notify parent when TextureView is ready
    LaunchedEffect(textureView) {
        textureView?.let { onTextureViewReady(it) }
    }

    Card(
        modifier = modifier
            .fillMaxWidth()
            .height(250.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Box {
            // Camera TextureView
            AndroidView(
                factory = { context ->
                    TextureView(context).apply {
                        textureView = this
                        layoutParams = android.view.ViewGroup.LayoutParams(
                            android.view.ViewGroup.LayoutParams.MATCH_PARENT,
                            android.view.ViewGroup.LayoutParams.MATCH_PARENT
                        )
                    }
                },
                modifier = Modifier
                    .fillMaxSize()
                    .clip(RoundedCornerShape(12.dp))
            )

            // Recording indicator overlay
            if (isRecording) {
                RecordingIndicator(
                    modifier = Modifier.align(Alignment.TopEnd)
                )
            }

            // Camera info overlay
            CameraInfoOverlay(
                isConnected = uiState.isCameraConnected,
                isInitializing = uiState.isConnecting,
                modifier = Modifier.align(Alignment.BottomStart)
            )
        }
    }
}

@Composable
private fun RecordingIndicator(
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.padding(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = Color.Red.copy(alpha = 0.9f)
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 6.dp)
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(6.dp)
        ) {
            Icon(
                imageVector = Icons.Default.FiberManualRecord,
                contentDescription = "Recording",
                modifier = Modifier.size(12.dp),
                tint = Color.White
            )
            Text(
                text = "REC",
                style = MaterialTheme.typography.labelMedium,
                color = Color.White,
                fontWeight = FontWeight.Bold
            )
        }
    }
}

@Composable
private fun CameraInfoOverlay(
    isConnected: Boolean,
    isInitializing: Boolean,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.padding(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = when {
                isConnected -> Color.Green.copy(alpha = 0.9f)
                isInitializing -> Color(0xFFFF9800).copy(alpha = 0.9f) // Orange
                else -> MaterialTheme.colorScheme.surface.copy(alpha = 0.95f)
            }
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(6.dp)
        ) {
            Icon(
                imageVector = Icons.Default.Camera,
                contentDescription = "Camera",
                modifier = Modifier.size(16.dp),
                tint = when {
                    isConnected -> Color.White
                    isInitializing -> Color.White
                    else -> MaterialTheme.colorScheme.primary
                }
            )
            Text(
                text = when {
                    isConnected -> "Camera Connected"
                    isInitializing -> "Initializing..."
                    else -> "Camera Disconnected"
                },
                style = MaterialTheme.typography.labelMedium,
                fontWeight = FontWeight.Medium,
                color = when {
                    isConnected -> Color.White
                    isInitializing -> Color.White
                    else -> MaterialTheme.colorScheme.onSurface
                }
            )
        }
    }
}

@Composable
fun ThermalPreviewSurface(
    isRecording: Boolean,
    modifier: Modifier = Modifier,
    onSurfaceViewReady: (SurfaceView) -> Unit = {}
) {
    val context = LocalContext.current
    val uiState by hiltViewModel<MainViewModel>().uiState.collectAsStateWithLifecycle()
    var surfaceView by remember { mutableStateOf<SurfaceView?>(null) }

    // Notify parent when SurfaceView is ready
    LaunchedEffect(surfaceView) {
        surfaceView?.let { onSurfaceViewReady(it) }
    }

    Card(
        modifier = modifier
            .fillMaxWidth()
            .height(200.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Box {
            // Thermal SurfaceView
            AndroidView(
                factory = { context ->
                    SurfaceView(context).apply {
                        surfaceView = this
                        layoutParams = android.view.ViewGroup.LayoutParams(
                            android.view.ViewGroup.LayoutParams.MATCH_PARENT,
                            android.view.ViewGroup.LayoutParams.MATCH_PARENT
                        )
                        // Set a dark background for thermal view
                        setBackgroundColor(Color.Black.toArgb())
                    }
                },
                modifier = Modifier
                    .fillMaxSize()
                    .clip(RoundedCornerShape(12.dp))
            )

            // Placeholder overlay when no thermal data
            ThermalPlaceholderOverlay(
                isConnected = uiState.isThermalConnected,
                isInitializing = uiState.isConnecting,
                modifier = Modifier.align(Alignment.Center)
            )

            // Recording indicator overlay
            if (isRecording) {
                RecordingIndicator(
                    modifier = Modifier.align(Alignment.TopEnd)
                )
            }
        }
    }
}

@Composable
private fun ThermalPlaceholderOverlay(
    isConnected: Boolean,
    isInitializing: Boolean,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(
            containerColor = when {
                isConnected -> Color.Green.copy(alpha = 0.8f)
                isInitializing -> Color(0xFFFF9800).copy(alpha = 0.8f) // Orange
                else -> MaterialTheme.colorScheme.surface.copy(alpha = 0.8f)
            }
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Icon(
                imageVector = Icons.Default.Camera,
                contentDescription = "Thermal Camera",
                modifier = Modifier.size(32.dp),
                tint = when {
                    isConnected -> Color.White
                    isInitializing -> Color.White
                    else -> MaterialTheme.colorScheme.primary
                }
            )
            Text(
                text = when {
                    isConnected -> "Thermal Connected"
                    isInitializing -> "Initializing..."
                    else -> "Thermal Preview"
                },
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Medium,
                color = when {
                    isConnected -> Color.White
                    isInitializing -> Color.White
                    else -> MaterialTheme.colorScheme.onSurface
                }
            )
            Text(
                text = when {
                    isConnected -> "Thermal camera active"
                    isInitializing -> "Connecting to camera..."
                    else -> "Connect thermal camera"
                },
                style = MaterialTheme.typography.bodySmall,
                color = when {
                    isConnected -> Color.White.copy(alpha = 0.8f)
                    isInitializing -> Color.White.copy(alpha = 0.8f)
                    else -> MaterialTheme.colorScheme.onSurfaceVariant
                }
            )
        }
    }
}