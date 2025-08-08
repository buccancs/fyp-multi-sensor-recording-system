package com.multisensor.recording.ui.components
import android.graphics.Bitmap
import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.FiberManualRecord
import androidx.compose.material.icons.filled.Thermostat
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.multisensor.recording.util.ThermalColorPalette
import com.multisensor.recording.util.TemperatureRange
@Composable
fun ThermalPreview(
    thermalBitmap: Bitmap?,
    isRecording: Boolean,
    temperatureRange: TemperatureRange,
    colorPalette: ThermalColorPalette,
    onPaletteChange: (ThermalColorPalette) -> Unit = {},
    onTemperatureRangeChange: (TemperatureRange) -> Unit = {},
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .aspectRatio(4f / 3f),
        elevation = CardDefaults.cardElevation(defaultElevation = 8.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
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
                ThermalPreviewPlaceholder()
            }
            TemperatureOverlay(
                temperatureRange = temperatureRange,
                modifier = Modifier.align(Alignment.TopStart)
            )
            thermalBitmap?.let { 
                if (isRecording) {
                    RecordingIndicator(
                        modifier = Modifier.align(Alignment.TopEnd)
                    )
                }
            }
            ColorPaletteIndicator(
                palette = colorPalette,
                modifier = Modifier.align(Alignment.BottomStart)
            )
        }
    }
}
@Composable
private fun ThermalPreviewPlaceholder(
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
            .fillMaxSize()
            .background(
                color = MaterialTheme.colorScheme.surface,
                shape = RoundedCornerShape(12.dp)
            ),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Icon(
                imageVector = Icons.Default.Thermostat,
                contentDescription = "No thermal data",
                modifier = Modifier.size(64.dp),
                tint = MaterialTheme.colorScheme.primary
            )
            Text(
                text = "No Thermal Data",
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.onSurface,
                fontWeight = FontWeight.Medium
            )
            Text(
                text = "Connect thermal camera to view",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}
@Composable
private fun TemperatureOverlay(
    temperatureRange: TemperatureRange,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.padding(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface.copy(alpha = 0.95f)
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
    ) {
        Column(
            modifier = Modifier.padding(12.dp),
            verticalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(6.dp)
            ) {
                Box(
                    modifier = Modifier
                        .size(8.dp)
                        .background(Color.Red, RoundedCornerShape(4.dp))
                )
                Text(
                    text = "${temperatureRange.max.toInt()}°C",
                    style = MaterialTheme.typography.labelMedium,
                    color = Color.Red,
                    fontWeight = FontWeight.SemiBold
                )
            }
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(6.dp)
            ) {
                Box(
                    modifier = Modifier
                        .size(8.dp)
                        .background(Color.Blue, RoundedCornerShape(4.dp))
                )
                Text(
                    text = "${temperatureRange.min.toInt()}°C",
                    style = MaterialTheme.typography.labelMedium,
                    color = Color.Blue,
                    fontWeight = FontWeight.SemiBold
                )
            }
        }
    }
}
@Composable
private fun RecordingIndicator(
    modifier: Modifier = Modifier
) {
    val alpha by animateFloatAsState(
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(1000, easing = LinearEasing),
            repeatMode = RepeatMode.Reverse
        )
    )
    Card(
        modifier = modifier.padding(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = Color.Red.copy(alpha = alpha * 0.9f + 0.1f)
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 6.dp)
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(6.dp)
        ) {
            Box(
                modifier = Modifier
                    .size(8.dp)
                    .background(Color.White, shape = RoundedCornerShape(4.dp))
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
private fun ColorPaletteIndicator(
    palette: ThermalColorPalette,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.padding(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface.copy(alpha = 0.95f)
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
    ) {
        Text(
            text = palette.displayName,
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
            style = MaterialTheme.typography.labelMedium,
            fontWeight = FontWeight.Medium
        )
    }
}