package com.multisensor.recording.ui.firebase

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.multisensor.recording.firebase.FirebaseAnalyticsService
import com.multisensor.recording.firebase.FirebaseFirestoreService
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*
import javax.inject.Inject

/**
 * ViewModel for Firebase status screen
 */
@HiltViewModel
class FirebaseStatusViewModel @Inject constructor(
    private val analyticsService: FirebaseAnalyticsService,
    private val firestoreService: FirebaseFirestoreService
) : ViewModel() {

    private val _uiState = MutableStateFlow(FirebaseStatusUiState())
    val uiState: StateFlow<FirebaseStatusUiState> = _uiState.asStateFlow()

    fun loadFirebaseStatus() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(
                analyticsEnabled = true, // Firebase Analytics is always enabled if properly configured
                firestoreEnabled = true, // Firestore is enabled if properly configured
                storageEnabled = true, // Storage is enabled if properly configured
                analyticsEventsCount = 0, // In a real app, this would come from local storage or API
                firestoreDocumentCount = 0, // In a real app, this would come from a Firestore query
                storageBytesUploaded = 0L // In a real app, this would come from storage metadata
            )
        }
    }

    fun testAnalytics() {
        viewModelScope.launch {
            try {
                // Test analytics event
                analyticsService.logRecordingSessionStart("test-session-${System.currentTimeMillis()}", 2)
                analyticsService.logGSRSensorConnected("test-sensor-001")
                analyticsService.logThermalCameraUsed("Test Camera", "640x480")
                
                // Update UI state
                val currentState = _uiState.value
                _uiState.value = currentState.copy(
                    analyticsEventsCount = currentState.analyticsEventsCount + 3,
                    recentActivities = listOf(
                        FirebaseActivity(
                            action = "Analytics test events logged",
                            timestamp = getCurrentTimestamp()
                        )
                    ) + currentState.recentActivities
                )
            } catch (e: Exception) {
                addErrorActivity("Analytics test failed: ${e.message}")
            }
        }
    }

    fun testFirestore() {
        viewModelScope.launch {
            try {
                // Test Firestore document creation
                val testSession = FirebaseFirestoreService.RecordingSession(
                    sessionId = "test-session-${System.currentTimeMillis()}",
                    startTime = Date(),
                    deviceCount = 2,
                    researcherId = "test-researcher",
                    experimentType = "firebase_integration_test"
                )
                
                val result = firestoreService.saveRecordingSession(testSession)
                
                if (result.isSuccess) {
                    val currentState = _uiState.value
                    _uiState.value = currentState.copy(
                        firestoreDocumentCount = currentState.firestoreDocumentCount + 1,
                        recentActivities = listOf(
                            FirebaseActivity(
                                action = "Test session saved to Firestore",
                                timestamp = getCurrentTimestamp()
                            )
                        ) + currentState.recentActivities
                    )
                } else {
                    addErrorActivity("Firestore test failed: ${result.exceptionOrNull()?.message}")
                }
            } catch (e: Exception) {
                addErrorActivity("Firestore test failed: ${e.message}")
            }
        }
    }

    private fun addErrorActivity(message: String) {
        val currentState = _uiState.value
        _uiState.value = currentState.copy(
            recentActivities = listOf(
                FirebaseActivity(
                    action = message,
                    timestamp = getCurrentTimestamp()
                )
            ) + currentState.recentActivities
        )
    }

    private fun getCurrentTimestamp(): String {
        val sdf = SimpleDateFormat("HH:mm:ss", Locale.getDefault())
        return sdf.format(Date())
    }
}

/**
 * UI state for Firebase status screen
 */
data class FirebaseStatusUiState(
    val analyticsEnabled: Boolean = false,
    val firestoreEnabled: Boolean = false,
    val storageEnabled: Boolean = false,
    val analyticsEventsCount: Int = 0,
    val firestoreDocumentCount: Int = 0,
    val storageBytesUploaded: Long = 0L,
    val recentActivities: List<FirebaseActivity> = emptyList(),
    val isLoading: Boolean = false,
    val errorMessage: String? = null
)

/**
 * Data class for Firebase activity log
 */
data class FirebaseActivity(
    val action: String,
    val timestamp: String
)