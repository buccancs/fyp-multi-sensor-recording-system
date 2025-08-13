package com.multisensor.recording.ui.firebase

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Analytics
import androidx.compose.material.icons.filled.CloudUpload
import androidx.compose.material.icons.filled.Storage
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import kotlinx.coroutines.launch

/**
 * Firebase status UI component showing integration status and statistics
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun FirebaseStatusScreen(
    viewModel: FirebaseStatusViewModel = hiltViewModel()
) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val uiState by viewModel.uiState.collectAsState()

    LaunchedEffect(Unit) {
        viewModel.loadFirebaseStatus()
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text(
            text = "Firebase Integration Status",
            style = MaterialTheme.typography.headlineMedium,
            modifier = Modifier.padding(bottom = 16.dp)
        )

        // Firebase services status cards
        LazyColumn(
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            item {
                FirebaseServiceCard(
                    title = "Analytics",
                    description = "Event tracking and user analytics",
                    icon = Icons.Default.Analytics,
                    isEnabled = uiState.analyticsEnabled,
                    eventsLogged = uiState.analyticsEventsCount
                )
            }

            item {
                FirebaseServiceCard(
                    title = "Firestore",
                    description = "Research data and session metadata",
                    icon = Icons.Default.Storage,
                    isEnabled = uiState.firestoreEnabled,
                    documentsStored = uiState.firestoreDocumentCount
                )
            }

            item {
                FirebaseServiceCard(
                    title = "Storage",
                    description = "Video and sensor data files",
                    icon = Icons.Default.CloudUpload,
                    isEnabled = uiState.storageEnabled,
                    bytesUploaded = uiState.storageBytesUploaded
                )
            }

            // Test Firebase functionality buttons
            item {
                Spacer(modifier = Modifier.height(16.dp))
                
                Text(
                    text = "Test Firebase Integration",
                    style = MaterialTheme.typography.titleMedium,
                    modifier = Modifier.padding(bottom = 8.dp)
                )
                
                Row(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Button(
                        onClick = {
                            scope.launch {
                                viewModel.testAnalytics()
                            }
                        },
                        modifier = Modifier.weight(1f)
                    ) {
                        Text("Test Analytics")
                    }
                    
                    Button(
                        onClick = {
                            scope.launch {
                                viewModel.testFirestore()
                            }
                        },
                        modifier = Modifier.weight(1f)
                    ) {
                        Text("Test Firestore")
                    }
                }
            }

            // Recent activities
            if (uiState.recentActivities.isNotEmpty()) {
                item {
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    Text(
                        text = "Recent Firebase Activities",
                        style = MaterialTheme.typography.titleMedium,
                        modifier = Modifier.padding(bottom = 8.dp)
                    )
                }

                items(uiState.recentActivities.take(5)) { activity ->
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        colors = CardDefaults.cardColors(
                            containerColor = MaterialTheme.colorScheme.surfaceVariant
                        )
                    ) {
                        Column(
                            modifier = Modifier.padding(12.dp)
                        ) {
                            Text(
                                text = activity.action,
                                style = MaterialTheme.typography.bodyMedium
                            )
                            Text(
                                text = activity.timestamp,
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun FirebaseServiceCard(
    title: String,
    description: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    isEnabled: Boolean,
    eventsLogged: Int? = null,
    documentsStored: Int? = null,
    bytesUploaded: Long? = null
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = if (isEnabled) 
                MaterialTheme.colorScheme.primaryContainer 
            else 
                MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                modifier = Modifier.size(40.dp),
                tint = if (isEnabled) 
                    MaterialTheme.colorScheme.primary 
                else 
                    MaterialTheme.colorScheme.onSurfaceVariant
            )
            
            Spacer(modifier = Modifier.width(16.dp))
            
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.titleMedium
                )
                Text(
                    text = description,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                
                // Show relevant statistics
                when {
                    eventsLogged != null -> {
                        Text(
                            text = "$eventsLogged events logged",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.primary
                        )
                    }
                    documentsStored != null -> {
                        Text(
                            text = "$documentsStored documents stored",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.primary
                        )
                    }
                    bytesUploaded != null -> {
                        val sizeStr = when {
                            bytesUploaded < 1024 -> "$bytesUploaded B"
                            bytesUploaded < 1024 * 1024 -> "${bytesUploaded / 1024} KB"
                            else -> "${bytesUploaded / (1024 * 1024)} MB"
                        }
                        Text(
                            text = "$sizeStr uploaded",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.primary
                        )
                    }
                }
            }
            
            // Status indicator
            Box(
                modifier = Modifier
                    .size(12.dp)
                    .padding(4.dp),
                contentAlignment = Alignment.Center
            ) {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .background(
                            if (isEnabled) {
                                MaterialTheme.colorScheme.primary
                            } else {
                                MaterialTheme.colorScheme.outline
                            },
                            CircleShape
                        )
                )
            }
        }
    }
}