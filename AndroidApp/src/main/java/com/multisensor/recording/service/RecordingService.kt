package com.multisensor.recording.service

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.IBinder
import androidx.core.app.NotificationCompat
import com.multisensor.recording.MainActivity
import com.multisensor.recording.R
import com.multisensor.recording.network.SocketController
import com.multisensor.recording.recording.CameraRecorder
import com.multisensor.recording.recording.ShimmerRecorder
import com.multisensor.recording.recording.ThermalRecorder
import com.multisensor.recording.streaming.PreviewStreamer
import com.multisensor.recording.util.Logger
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.cancel
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * Foreground service responsible for managing multi-sensor recording sessions.
 * This service ensures recording continues even when the app is in the background
 * and provides a persistent notification to the user.
 */
@AndroidEntryPoint
class RecordingService : Service() {
    
    @Inject
    lateinit var cameraRecorder: CameraRecorder
    
    @Inject
    lateinit var thermalRecorder: ThermalRecorder
    
    @Inject
    lateinit var shimmerRecorder: ShimmerRecorder
    
    @Inject
    lateinit var sessionManager: SessionManager
    
    @Inject
    lateinit var socketController: SocketController
    
    @Inject
    lateinit var previewStreamer: PreviewStreamer
    
    @Inject
    lateinit var logger: Logger
    
    private val serviceScope = CoroutineScope(Dispatchers.Default + Job())
    private var isRecording = false
    private var currentSessionId: String? = null
    
    companion object {
        const val ACTION_START_RECORDING = "com.multisensor.recording.START_RECORDING"
        const val ACTION_STOP_RECORDING = "com.multisensor.recording.STOP_RECORDING"
        const val ACTION_GET_STATUS = "com.multisensor.recording.GET_STATUS"
        
        private const val NOTIFICATION_ID = 1001
        private const val CHANNEL_ID = "recording_channel"
        private const val CHANNEL_NAME = "Recording Service"
    }
    
    override fun onCreate() {
        super.onCreate()
        logger.info("RecordingService created")
        createNotificationChannel()
        
        // Initialize SocketController with callback
        socketController.setServiceCallback { command ->
            handleSocketCommand(command)
        }
        
        // Start socket connection
        socketController.startListening()
        
        // Inject PreviewStreamer into CameraRecorder (method injection for scoping compatibility)
        cameraRecorder.setPreviewStreamer(previewStreamer)
        
        logger.info("RecordingService initialization complete")
    }
    
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_START_RECORDING -> {
                startRecording()
            }
            ACTION_STOP_RECORDING -> {
                stopRecording()
            }
            ACTION_GET_STATUS -> {
                // TODO: Broadcast current status
                logger.info("Status requested - Recording: $isRecording, Session: $currentSessionId")
            }
        }
        
        return START_STICKY // Restart service if killed by system
    }
    
    override fun onBind(intent: Intent?): IBinder? {
        // This service doesn't support binding
        return null
    }
    
    override fun onDestroy() {
        super.onDestroy()
        logger.info("RecordingService destroyed")
        
        // Ensure recording is stopped
        if (isRecording) {
            serviceScope.launch {
                stopRecordingInternal()
            }
        }
        
        // Stop preview streaming
        previewStreamer.stopStreaming()
        
        // Stop socket connection
        socketController.stop()
        
        // Cancel all coroutines
        serviceScope.cancel()
        
        logger.info("RecordingService cleanup complete")
    }
    
    /**
     * Handle commands received from PC via SocketController
     */
    private fun handleSocketCommand(command: String) {
        logger.info("Processing socket command: $command")
        
        when (command.uppercase()) {
            "START" -> {
                if (!isRecording) {
                    startRecording()
                } else {
                    logger.warning("Recording already in progress - ignoring START command")
                }
            }
            
            "STOP" -> {
                if (isRecording) {
                    serviceScope.launch {
                        stopRecordingInternal()
                    }
                } else {
                    logger.warning("No recording in progress - ignoring STOP command")
                }
            }
            
            "CALIBRATE" -> {
                // TODO: Implement calibration trigger
                logger.info("Calibration command received - not yet implemented")
            }
            
            else -> {
                logger.warning("Unknown socket command: $command")
            }
        }
    }
    
    private fun startRecording() {
        if (isRecording) {
            logger.warning("Recording already in progress")
            return
        }
        
        serviceScope.launch {
            try {
                logger.info("Starting recording session...")
                
                // Create new session
                currentSessionId = sessionManager.createNewSession()
                logger.info("Created session: $currentSessionId")
                
                // Start foreground service with notification
                startForeground(NOTIFICATION_ID, createRecordingNotification())
                
                // Initialize and start all recorders
                val cameraSessionInfo = cameraRecorder.startSession(recordVideo = true, captureRaw = false)
                val thermalStarted = thermalRecorder.startRecording(currentSessionId!!)
                val shimmerStarted = shimmerRecorder.startRecording(currentSessionId!!)
                
                if (cameraSessionInfo != null) {
                    isRecording = true
                    
                    // Start preview streaming
                    previewStreamer.startStreaming()
                    
                    logger.info("Recording started successfully")
                    updateNotification("Recording in progress - Session: $currentSessionId")
                } else {
                    logger.error("Failed to start camera recording")
                    stopRecordingInternal()
                }
                
                logger.info("Recording status - Camera: ${cameraSessionInfo != null}, Thermal: $thermalStarted, Shimmer: $shimmerStarted")
                
            } catch (e: Exception) {
                logger.error("Error starting recording", e)
                stopRecordingInternal()
            }
        }
    }
    
    private fun stopRecording() {
        if (!isRecording) {
            logger.warning("No recording in progress")
            return
        }
        
        serviceScope.launch {
            stopRecordingInternal()
        }
    }
    
    private suspend fun stopRecordingInternal() {
        try {
            logger.info("Stopping recording session...")
            
            // Stop all recorders
            cameraRecorder.stopSession()
            thermalRecorder.stopRecording()
            shimmerRecorder.stopRecording()
            
            // Stop preview streaming
            previewStreamer.stopStreaming()
            
            // Finalize session
            currentSessionId?.let { sessionId ->
                sessionManager.finalizeCurrentSession()
                logger.info("Session finalized: $sessionId")
            }
            
            isRecording = false
            currentSessionId = null
            
            // Update notification
            updateNotification("Recording stopped")
            
            // Stop foreground service after a delay to show final notification
            kotlinx.coroutines.delay(2000)
            stopForeground(true)
            stopSelf()
            
            logger.info("Recording stopped successfully")
            
        } catch (e: Exception) {
            logger.error("Error stopping recording", e)
        }
    }
    
    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                CHANNEL_NAME,
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Notifications for multi-sensor recording sessions"
                setShowBadge(false)
            }
            
            val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            notificationManager.createNotificationChannel(channel)
        }
    }
    
    private fun createRecordingNotification(): Notification {
        val intent = Intent(this, MainActivity::class.java)
        val pendingIntent = PendingIntent.getActivity(
            this, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Multi-Sensor Recording")
            .setContentText("Preparing to record...")
            .setSmallIcon(android.R.drawable.ic_media_play) // TODO: Replace with custom icon
            .setContentIntent(pendingIntent)
            .setOngoing(true)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .build()
    }
    
    private fun updateNotification(message: String) {
        val intent = Intent(this, MainActivity::class.java)
        val pendingIntent = PendingIntent.getActivity(
            this, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        
        val notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Multi-Sensor Recording")
            .setContentText(message)
            .setSmallIcon(android.R.drawable.ic_media_play) // TODO: Replace with custom icon
            .setContentIntent(pendingIntent)
            .setOngoing(isRecording)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .build()
        
        val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        notificationManager.notify(NOTIFICATION_ID, notification)
    }
}
