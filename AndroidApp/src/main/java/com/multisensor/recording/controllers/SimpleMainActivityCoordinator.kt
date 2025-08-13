package com.multisensor.recording.controllers

import android.app.Activity
import android.content.Context
import android.view.TextureView
import com.multisensor.recording.ui.MainViewModel
import com.multisensor.recording.util.Logger
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class SimpleMainActivityCoordinator @Inject constructor(
    private val permissionController: PermissionController,
    private val recordingController: RecordingController,
    private val logger: Logger
) {

    data class CoordinatorState(
        val isInitialized: Boolean = false,
        val lastInitTimestamp: Long = 0
    )

    private var currentState = CoordinatorState()

    suspend fun initializeApp(
        activity: Activity,
        textureView: TextureView,
        viewModel: MainViewModel
    ): Boolean {
        return try {
            logger.info("Initializing app components")
            
            // Check permissions
            if (!permissionController.hasRequiredPermissions(activity)) {
                permissionController.requestPermissions(activity)
            }
            
            // Initialize view model with texture view
            viewModel.initializeSystem(textureView, null)
            
            currentState = CoordinatorState(
                isInitialized = true,
                lastInitTimestamp = System.currentTimeMillis()
            )
            
            logger.info("App initialization completed")
            true
        } catch (e: Exception) {
            logger.error("Failed to initialize app", e)
            false
        }
    }

    fun isInitialized(): Boolean = currentState.isInitialized

    suspend fun startRecording(sessionId: String): Boolean {
        return recordingController.startRecording(sessionId)
    }

    suspend fun stopRecording(): Boolean {
        return recordingController.stopRecording()
    }
}