package com.multisensor.recording.ui.compose.screens

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DevicesScreen(
    viewModel: DevicesViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Device overview card
        DeviceOverviewCard(
            uiState = uiState,
            onRefreshClicked = { viewModel.refreshAllDevices() }
        )
        
        // Device list
        LazyColumn(
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            item {
                DeviceCard(
                    title = "PC Connection",
                    icon = Icons.Filled.Computer,
                    isConnected = uiState.isPcConnected,
                    isConnecting = uiState.isConnecting,
                    statusText = uiState.pcConnectionStatus,
                    details = listOf(
                        "IP: ${uiState.pcIpAddress}",
                        "Port: ${uiState.pcPort}",
                        "Last Seen: ${uiState.pcLastSeen}"
                    ).filter { it.contains(":") && !it.endsWith(": ") },
                    onConnect = { viewModel.connectPc() },
                    onDisconnect = { viewModel.disconnectPc() },
                    onTest = { viewModel.testPcConnection() }
                )
            }
            
            item {
                DeviceCard(
                    title = "Shimmer Device",
                    icon = Icons.Filled.Sensors,
                    isConnected = uiState.isShimmerConnected,
                    isConnecting = uiState.isConnecting,
                    statusText = if (uiState.isShimmerConnected) "Connected" else "Disconnected",
                    details = listOf(
                        "MAC: ${uiState.shimmerMacAddress}",
                        "Battery: ${uiState.shimmerBatteryLevel}%",
                        "Sensors: ${uiState.shimmerActiveSensors}",
                        "Sample Rate: ${uiState.shimmerSampleRate}",
                        "Last Seen: ${uiState.shimmerLastSeen}"
                    ).filter { it.contains(":") && !it.endsWith(": ") },
                    onConnect = { viewModel.connectShimmer() },
                    onDisconnect = { viewModel.disconnectShimmer() },
                    onTest = { viewModel.testShimmerConnection() }
                )
            }
            
            item {
                DeviceCard(
                    title = "Thermal Camera",
                    icon = Icons.Filled.Thermostat,
                    isConnected = uiState.isThermalConnected,
                    isConnecting = uiState.isConnecting,
                    statusText = if (uiState.isThermalConnected) "Connected" else "Disconnected",
                    details = listOf(
                        "Model: ${uiState.thermalCameraModel}",
                        "Temperature: ${uiState.thermalCurrentTemp}°C",
                        "Resolution: ${uiState.thermalResolution}",
                        "Frame Rate: ${uiState.thermalFrameRate}fps",
                        "Last Seen: ${uiState.thermalLastSeen}"
                    ).filter { it.contains(":") && !it.endsWith(": ") },
                    onConnect = { viewModel.connectThermal() },
                    onDisconnect = { viewModel.disconnectThermal() },
                    onTest = { viewModel.testThermalConnection() }
                )
            }
            
            item {
                DeviceCard(
                    title = "Network",
                    icon = Icons.Filled.Wifi,
                    isConnected = uiState.isNetworkConnected,
                    isConnecting = uiState.isConnecting,
                    statusText = if (uiState.isNetworkConnected) "Connected" else "Disconnected",
                    details = listOf(
                        "SSID: ${uiState.networkSsid}",
                        "IP: ${uiState.networkIpAddress}",
                        "Signal: ${uiState.networkSignalStrength}%",
                        "Type: ${uiState.networkType}"
                    ).filter { it.contains(":") && !it.endsWith(": ") },
                    onConnect = { viewModel.connectNetwork() },
                    onDisconnect = { viewModel.disconnectNetwork() },
                    onTest = { viewModel.testNetworkConnection() }
                )
            }
            
            // Test results
            if (uiState.testResults.isNotEmpty()) {
                item {
                    TestResultsCard(testResults = uiState.testResults)
                }
            }
        }
    }
}

@Composable
private fun DeviceOverviewCard(
    uiState: DevicesUiState,
    onRefreshClicked: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Icon(
                imageVector = Icons.Filled.Devices,
                contentDescription = "Devices",
                modifier = Modifier.size(48.dp),
                tint = MaterialTheme.colorScheme.primary
            )
            Text(
                text = "Device Management",
                style = MaterialTheme.typography.headlineMedium,
                textAlign = TextAlign.Center
            )
            
            Row(
                horizontalArrangement = Arrangement.spacedBy(24.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(
                        text = "${uiState.totalConnectedDevices}",
                        style = MaterialTheme.typography.headlineSmall,
                        color = MaterialTheme.colorScheme.primary,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        text = "Connected",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Icon(
                        imageVector = if (uiState.allDevicesHealthy) Icons.Filled.CheckCircle else Icons.Filled.Error,
                        contentDescription = null,
                        tint = if (uiState.allDevicesHealthy) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.error,
                        modifier = Modifier.size(24.dp)
                    )
                    Text(
                        text = if (uiState.allDevicesHealthy) "Healthy" else "Issues",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
            
            Button(
                onClick = onRefreshClicked,
                enabled = !uiState.isConnecting
            ) {
                if (uiState.isConnecting) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(18.dp),
                        strokeWidth = 2.dp
                    )
                } else {
                    Icon(
                        imageVector = Icons.Filled.Refresh,
                        contentDescription = null,
                        modifier = Modifier.size(18.dp)
                    )
                }
                Spacer(modifier = Modifier.width(8.dp))
                Text("Refresh All Devices")
            }
        }
    }
}

@Composable
private fun DeviceCard(
    title: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    isConnected: Boolean,
    isConnecting: Boolean,
    statusText: String,
    details: List<String>,
    onConnect: () -> Unit,
    onDisconnect: () -> Unit,
    onTest: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    modifier = Modifier.size(32.dp),
                    tint = if (isConnected) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurfaceVariant
                )
                
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = title,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Medium
                    )
                    Text(
                        text = statusText,
                        style = MaterialTheme.typography.bodyMedium,
                        color = if (isConnected) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                
                Icon(
                    imageVector = if (isConnected) Icons.Filled.CheckCircle else Icons.Filled.Cancel,
                    contentDescription = null,
                    tint = if (isConnected) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.error,
                    modifier = Modifier.size(24.dp)
                )
            }
            
            if (details.isNotEmpty()) {
                Column(
                    verticalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    details.forEach { detail ->
                        Text(
                            text = detail,
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }
            
            Row(
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                if (isConnected) {
                    OutlinedButton(
                        onClick = onDisconnect,
                        enabled = !isConnecting
                    ) {
                        Text("Disconnect")
                    }
                    Button(
                        onClick = onTest,
                        enabled = !isConnecting
                    ) {
                        Text("Test")
                    }
                } else {
                    Button(
                        onClick = onConnect,
                        enabled = !isConnecting
                    ) {
                        if (isConnecting) {
                            CircularProgressIndicator(
                                modifier = Modifier.size(16.dp),
                                strokeWidth = 2.dp
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                        }
                        Text("Connect")
                    }
                }
            }
        }
    }
}

@Composable
private fun TestResultsCard(testResults: List<String>) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Icon(
                    imageVector = Icons.Filled.Assignment,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.primary
                )
                Text(
                    text = "Test Results",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Medium
                )
            }
            
            testResults.takeLast(5).forEach { result ->
                Text(
                    text = result,
                    style = MaterialTheme.typography.bodySmall,
                    color = if (result.contains("PASSED")) {
                        MaterialTheme.colorScheme.primary
                    } else if (result.contains("FAILED")) {
                        MaterialTheme.colorScheme.error
                    } else {
                        MaterialTheme.colorScheme.onSurfaceVariant
                    }
                )
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CalibrationScreen(
    viewModel: com.multisensor.recording.ui.CalibrationViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Calibration overview
        CalibrationOverviewCard(
            uiState = uiState,
            onValidateSystem = { viewModel.validateSystem() }
        )
        
        // Calibration items
        LazyColumn(
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            item {
                CalibrationItemCard(
                    title = "Camera Calibration",
                    icon = Icons.Filled.Camera,
                    isCalibrated = uiState.isCameraCalibrated,
                    isCalibrating = uiState.isCameraCalibrating,
                    progress = uiState.cameraCalibrationProgress,
                    details = listOf(
                        "Error: ${uiState.cameraCalibrationError}",
                        "Date: ${uiState.cameraCalibrationDate}"
                    ).filter { !it.endsWith(": ") && !it.endsWith(": 0.0") },
                    onStart = { viewModel.startCameraCalibration() },
                    onReset = { viewModel.resetCameraCalibration() }
                )
            }
            
            item {
                CalibrationItemCard(
                    title = "Thermal Camera",
                    icon = Icons.Filled.Thermostat,
                    isCalibrated = uiState.isThermalCalibrated,
                    isCalibrating = uiState.isThermalCalibrating,
                    progress = uiState.thermalCalibrationProgress,
                    details = listOf(
                        "Range: ${uiState.thermalTempRange}",
                        "Emissivity: ${uiState.thermalEmissivity}",
                        "Palette: ${uiState.thermalColorPalette}",
                        "Date: ${uiState.thermalCalibrationDate}"
                    ).filter { !it.endsWith(": ") },
                    onStart = { viewModel.startThermalCalibration() },
                    onReset = { viewModel.resetThermalCalibration() }
                )
            }
            
            item {
                CalibrationItemCard(
                    title = "Shimmer Sensor",
                    icon = Icons.Filled.Sensors,
                    isCalibrated = uiState.isShimmerCalibrated,
                    isCalibrating = uiState.isShimmerCalibrating,
                    progress = uiState.shimmerCalibrationProgress,
                    details = listOf(
                        "MAC: ${uiState.shimmerMacAddress}",
                        "Config: ${uiState.shimmerSensorConfig}",
                        "Rate: ${uiState.shimmerSamplingRate}",
                        "Date: ${uiState.shimmerCalibrationDate}"
                    ).filter { !it.endsWith(": ") },
                    onStart = { viewModel.startShimmerCalibration() },
                    onReset = { viewModel.resetShimmerCalibration() }
                )
            }
            
            // Validation results
            if (uiState.validationErrors.isNotEmpty()) {
                item {
                    ValidationResultsCard(validationErrors = uiState.validationErrors)
                }
            }
            
            // Calibration actions
            item {
                CalibrationActionsCard(
                    onSave = { viewModel.saveCalibrationData() },
                    onLoad = { viewModel.loadCalibrationData() },
                    onExport = { viewModel.exportCalibrationData() },
                    isAnyCalibrating = uiState.isAnyCalibrating
                )
            }
        }
    }
}

@Composable
private fun CalibrationOverviewCard(
    uiState: com.multisensor.recording.ui.CalibrationUiState,
    onValidateSystem: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Icon(
                imageVector = Icons.Filled.Tune,
                contentDescription = "Calibration",
                modifier = Modifier.size(48.dp),
                tint = MaterialTheme.colorScheme.primary
            )
            Text(
                text = "System Calibration",
                style = MaterialTheme.typography.headlineMedium,
                textAlign = TextAlign.Center
            )
            
            Row(
                horizontalArrangement = Arrangement.spacedBy(24.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                val calibratedCount = listOf(
                    uiState.isCameraCalibrated,
                    uiState.isThermalCalibrated,
                    uiState.isShimmerCalibrated
                ).count { it }
                
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(
                        text = "$calibratedCount/3",
                        style = MaterialTheme.typography.headlineSmall,
                        color = MaterialTheme.colorScheme.primary,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        text = "Calibrated",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Icon(
                        imageVector = if (uiState.isSystemValid) Icons.Filled.CheckCircle else Icons.Filled.Warning,
                        contentDescription = null,
                        tint = if (uiState.isSystemValid) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.error,
                        modifier = Modifier.size(24.dp)
                    )
                    Text(
                        text = if (uiState.isSystemValid) "Valid" else "Issues",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
            
            Button(
                onClick = onValidateSystem,
                enabled = !uiState.isValidating
            ) {
                if (uiState.isValidating) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(18.dp),
                        strokeWidth = 2.dp
                    )
                } else {
                    Icon(
                        imageVector = Icons.Filled.VerifiedUser,
                        contentDescription = null,
                        modifier = Modifier.size(18.dp)
                    )
                }
                Spacer(modifier = Modifier.width(8.dp))
                Text("Validate System")
            }
        }
    }
}

@Composable
private fun CalibrationItemCard(
    title: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    isCalibrated: Boolean,
    isCalibrating: Boolean,
    progress: Int,
    details: List<String>,
    onStart: () -> Unit,
    onReset: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    modifier = Modifier.size(32.dp),
                    tint = if (isCalibrated) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurfaceVariant
                )
                
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = title,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Medium
                    )
                    Text(
                        text = when {
                            isCalibrating -> "Calibrating... $progress%"
                            isCalibrated -> "Calibrated"
                            else -> "Not calibrated"
                        },
                        style = MaterialTheme.typography.bodyMedium,
                        color = when {
                            isCalibrating -> MaterialTheme.colorScheme.secondary
                            isCalibrated -> MaterialTheme.colorScheme.primary
                            else -> MaterialTheme.colorScheme.onSurfaceVariant
                        }
                    )
                }
                
                Icon(
                    imageVector = if (isCalibrated) Icons.Filled.CheckCircle else Icons.Filled.RadioButtonUnchecked,
                    contentDescription = null,
                    tint = if (isCalibrated) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.size(24.dp)
                )
            }
            
            if (isCalibrating) {
                LinearProgressIndicator(
                    progress = { progress / 100f },
                    modifier = Modifier.fillMaxWidth(),
                )
            }
            
            if (details.isNotEmpty()) {
                Column(
                    verticalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    details.forEach { detail ->
                        Text(
                            text = detail,
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }
            
            Row(
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Button(
                    onClick = onStart,
                    enabled = !isCalibrating
                ) {
                    Icon(
                        imageVector = Icons.Filled.PlayArrow,
                        contentDescription = null,
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Calibrate")
                }
                
                if (isCalibrated) {
                    OutlinedButton(
                        onClick = onReset,
                        enabled = !isCalibrating
                    ) {
                        Text("Reset")
                    }
                }
            }
        }
    }
}

@Composable
private fun ValidationResultsCard(validationErrors: List<String>) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.errorContainer
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Icon(
                    imageVector = Icons.Filled.Error,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.error
                )
                Text(
                    text = "Validation Issues",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Medium,
                    color = MaterialTheme.colorScheme.error
                )
            }
            
            validationErrors.forEach { error ->
                Text(
                    text = "• $error",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onErrorContainer
                )
            }
        }
    }
}

@Composable
private fun CalibrationActionsCard(
    onSave: () -> Unit,
    onLoad: () -> Unit,
    onExport: () -> Unit,
    isAnyCalibrating: Boolean
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Text(
                text = "Calibration Data",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Medium
            )
            
            Row(
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                OutlinedButton(
                    onClick = onSave,
                    enabled = !isAnyCalibrating,
                    modifier = Modifier.weight(1f)
                ) {
                    Icon(
                        imageVector = Icons.Filled.Save,
                        contentDescription = null,
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text("Save")
                }
                
                OutlinedButton(
                    onClick = onLoad,
                    enabled = !isAnyCalibrating,
                    modifier = Modifier.weight(1f)
                ) {
                    Icon(
                        imageVector = Icons.Filled.FolderOpen,
                        contentDescription = null,
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text("Load")
                }
                
                OutlinedButton(
                    onClick = onExport,
                    enabled = !isAnyCalibrating,
                    modifier = Modifier.weight(1f)
                ) {
                    Icon(
                        imageVector = Icons.Filled.Upload,
                        contentDescription = null,
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text("Export")
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun FilesScreen(
    viewModel: com.multisensor.recording.ui.FileViewViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    
    LaunchedEffect(Unit) {
        viewModel.loadInitialData()
    }
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Files overview
        FilesOverviewCard(
            uiState = uiState,
            onRefresh = { viewModel.refreshSessions() },
            onDeleteAll = { viewModel.deleteAllSessions() }
        )
        
        // Search bar
        OutlinedTextField(
            value = uiState.searchQuery,
            onValueChange = { viewModel.onSearchQueryChanged(it) },
            label = { Text("Search sessions...") },
            leadingIcon = {
                Icon(Icons.Filled.Search, contentDescription = null)
            },
            modifier = Modifier.fillMaxWidth()
        )
        
        if (uiState.isLoadingSessions) {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(32.dp),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator()
            }
        } else if (uiState.showEmptyState) {
            EmptyStateCard()
        } else {
            // Sessions list
            LazyColumn(
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(uiState.filteredSessions) { session ->
                    SessionCard(
                        session = session,
                        isSelected = uiState.selectedSession?.sessionId == session.sessionId,
                        onClick = { viewModel.selectSession(session) }
                    )
                }
                
                // Selected session files
                if (uiState.selectedSession != null && uiState.sessionFiles.isNotEmpty()) {
                    item {
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            text = "Files in ${uiState.selectedSession!!.sessionId}",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Medium,
                            modifier = Modifier.padding(vertical = 8.dp)
                        )
                    }
                    
                    items(uiState.sessionFiles) { file ->
                        FileCard(
                            file = file,
                            onDelete = { viewModel.deleteFile(file) }
                        )
                    }
                }
            }
        }
        
        // Error/Success messages
        uiState.errorMessage?.let { error ->
            LaunchedEffect(error) {
                // Show snackbar or handle error
                viewModel.clearError()
            }
        }
        
        uiState.successMessage?.let { success ->
            LaunchedEffect(success) {
                // Show snackbar or handle success
                viewModel.clearSuccess()
            }
        }
    }
}

@Composable
private fun FilesOverviewCard(
    uiState: com.multisensor.recording.ui.FileViewUiState,
    onRefresh: () -> Unit,
    onDeleteAll: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Icon(
                imageVector = Icons.Filled.Folder,
                contentDescription = "Files",
                modifier = Modifier.size(48.dp),
                tint = MaterialTheme.colorScheme.primary
            )
            Text(
                text = "File Management",
                style = MaterialTheme.typography.headlineMedium,
                textAlign = TextAlign.Center
            )
            
            Row(
                horizontalArrangement = Arrangement.spacedBy(24.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(
                        text = "${uiState.sessions.size}",
                        style = MaterialTheme.typography.headlineSmall,
                        color = MaterialTheme.colorScheme.primary,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        text = "Sessions",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(
                        text = "${uiState.totalFileCount}",
                        style = MaterialTheme.typography.headlineSmall,
                        color = MaterialTheme.colorScheme.primary,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        text = "Files",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(
                        text = formatFileSize(uiState.totalStorageUsed),
                        style = MaterialTheme.typography.headlineSmall,
                        color = MaterialTheme.colorScheme.primary,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        text = "Used",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
            
            Row(
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                OutlinedButton(
                    onClick = onRefresh,
                    enabled = !uiState.isLoadingSessions
                ) {
                    Icon(
                        imageVector = Icons.Filled.Refresh,
                        contentDescription = null,
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Refresh")
                }
                
                if (uiState.sessions.isNotEmpty()) {
                    Button(
                        onClick = onDeleteAll,
                        enabled = !uiState.isLoadingSessions,
                        colors = ButtonDefaults.buttonColors(
                            containerColor = MaterialTheme.colorScheme.error
                        )
                    ) {
                        Icon(
                            imageVector = Icons.Filled.DeleteSweep,
                            contentDescription = null,
                            modifier = Modifier.size(16.dp)
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("Clear All")
                    }
                }
            }
        }
    }
}

@Composable
private fun SessionCard(
    session: com.multisensor.recording.ui.SessionItem,
    isSelected: Boolean,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onClick() },
        elevation = CardDefaults.cardElevation(defaultElevation = if (isSelected) 4.dp else 2.dp),
        colors = CardDefaults.cardColors(
            containerColor = if (isSelected) {
                MaterialTheme.colorScheme.primaryContainer
            } else {
                MaterialTheme.colorScheme.surface
            }
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Icon(
                    imageVector = when (session.status) {
                        com.multisensor.recording.ui.SessionStatus.COMPLETED -> Icons.Filled.CheckCircle
                        com.multisensor.recording.ui.SessionStatus.PROCESSING -> Icons.Filled.Sync
                        com.multisensor.recording.ui.SessionStatus.CORRUPTED -> Icons.Filled.Error
                        com.multisensor.recording.ui.SessionStatus.INTERRUPTED -> Icons.Filled.Warning
                    },
                    contentDescription = null,
                    tint = when (session.status) {
                        com.multisensor.recording.ui.SessionStatus.COMPLETED -> MaterialTheme.colorScheme.primary
                        com.multisensor.recording.ui.SessionStatus.PROCESSING -> MaterialTheme.colorScheme.secondary
                        com.multisensor.recording.ui.SessionStatus.CORRUPTED -> MaterialTheme.colorScheme.error
                        com.multisensor.recording.ui.SessionStatus.INTERRUPTED -> MaterialTheme.colorScheme.error
                    }
                )
                
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = session.sessionId,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Medium
                    )
                    Text(
                        text = "${session.formattedDuration} • ${session.fileCount} files • ${formatFileSize(session.totalSize)}",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                
                Icon(
                    imageVector = if (isSelected) Icons.Filled.ExpandLess else Icons.Filled.ExpandMore,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            
            // Device types
            Row(
                horizontalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                session.deviceTypes.forEach { deviceType ->
                    AssistChip(
                        onClick = { },
                        label = { Text(deviceType) },
                        modifier = Modifier.padding(horizontal = 2.dp)
                    )
                }
            }
        }
    }
}

@Composable
private fun FileCard(
    file: com.multisensor.recording.ui.FileItem,
    onDelete: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Icon(
                imageVector = when (file.type) {
                    com.multisensor.recording.ui.FileType.VIDEO -> Icons.Filled.VideoFile
                    com.multisensor.recording.ui.FileType.RAW_IMAGE -> Icons.Filled.Image
                    com.multisensor.recording.ui.FileType.THERMAL -> Icons.Filled.Thermostat
                    com.multisensor.recording.ui.FileType.GSR -> Icons.Filled.Sensors
                    com.multisensor.recording.ui.FileType.METADATA -> Icons.Filled.Description
                    com.multisensor.recording.ui.FileType.LOG -> Icons.Filled.TextSnippet
                },
                contentDescription = null,
                tint = MaterialTheme.colorScheme.primary
            )
            
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = file.file.name,
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.Medium
                )
                Text(
                    text = "${file.type.displayName} • ${formatFileSize(file.file.length())}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            
            IconButton(onClick = onDelete) {
                Icon(
                    imageVector = Icons.Filled.Delete,
                    contentDescription = "Delete file",
                    tint = MaterialTheme.colorScheme.error
                )
            }
        }
    }
}

@Composable
private fun EmptyStateCard() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(32.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Icon(
                imageVector = Icons.Filled.FolderOpen,
                contentDescription = null,
                modifier = Modifier.size(64.dp),
                tint = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Text(
                text = "No recordings found",
                style = MaterialTheme.typography.titleMedium,
                textAlign = TextAlign.Center
            )
            Text(
                text = "Start a recording session to see files here",
                style = MaterialTheme.typography.bodyMedium,
                textAlign = TextAlign.Center,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

private fun formatFileSize(bytes: Long): String {
    val units = arrayOf("B", "KB", "MB", "GB")
    var size = bytes.toDouble()
    var unitIndex = 0
    
    while (size >= 1024 && unitIndex < units.size - 1) {
        size /= 1024
        unitIndex++
    }
    
    return "%.1f %s".format(size, units[unitIndex])
}