package com.multisensor.recording.controllers

import android.content.Context
import com.multisensor.recording.service.RecordingService
import com.multisensor.recording.util.Logger
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class SimpleRecordingController @Inject constructor(
    private val logger: Logger
) {

    data class RecordingState(
        val isRecording: Boolean = false,
        val currentSessionId: String? = null,
        val sessionStartTime: Long = 0,
        val lastUpdateTime: Long = System.currentTimeMillis()
    )

    private val _recordingState = MutableStateFlow(RecordingState())
    val recordingState: StateFlow<RecordingState> = _recordingState.asStateFlow()

    fun startRecording(sessionId: String): Boolean {
        return try {
            _recordingState.value = RecordingState(
                isRecording = true,
                currentSessionId = sessionId,
                sessionStartTime = System.currentTimeMillis()
            )
            logger.info("Recording started for session: $sessionId")
            true
        } catch (e: Exception) {
            logger.error("Failed to start recording", e)
            false
        }
    }

    fun stopRecording(): Boolean {
        return try {
            _recordingState.value = RecordingState()
            logger.info("Recording stopped")
            true
        } catch (e: Exception) {
            logger.error("Failed to stop recording", e)
            false
        }
    }

    fun isRecording(): Boolean = _recordingState.value.isRecording
}