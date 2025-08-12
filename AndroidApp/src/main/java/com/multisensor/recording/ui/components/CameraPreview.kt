package com.multisensor.recording.ui.components

import android.view.SurfaceView
import android.view.TextureView
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Camera
import androidx.compose.material.icons.filled.Thermostat
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

    PreviewCard(
        modifier = modifier,
        height = 250.dp
    ) {
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
        DeviceStatusOverlay(
            deviceName = "Camera",
            icon = Icons.Default.Camera,
            isConnected = uiState.isCameraConnected,
            isInitializing = uiState.isConnecting,
            modifier = Modifier.align(Alignment.BottomStart)
        )
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

    PreviewCard(
        modifier = modifier,
        height = 200.dp
    ) {
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
        DeviceStatusOverlay(
            deviceName = "Thermal",
            icon = Icons.Default.Thermostat,
            isConnected = uiState.isThermalConnected,
            isInitializing = uiState.isConnecting,
            detailText = when {
                uiState.isThermalConnected -> "Thermal camera active"
                uiState.isConnecting -> "Connecting to camera..."
                else -> "Connect thermal camera"
            },
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

