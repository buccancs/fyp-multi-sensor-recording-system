package com.multisensor.recording.network

import android.content.Context
import android.content.Intent
import android.os.BatteryManager
import android.os.Build
import android.os.StatFs
import com.multisensor.recording.recording.CameraRecorder
import com.multisensor.recording.recording.ThermalRecorder
import com.multisensor.recording.service.RecordingService
import com.multisensor.recording.service.SessionManager
import com.multisensor.recording.util.Logger
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.android.scopes.ServiceScoped
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import java.io.File
import javax.inject.Inject

/**
 * Command Processor for Milestone 2.6 Network Communication.
 * Processes incoming JSON commands from PC and executes corresponding actions.
 * 
 * Based on 2_6_milestone.md specifications:
 * - Handles start_record, stop_record, capture_calibration, set_stimulus_time commands
 * - Integrates with existing RecordingService for session management
 * - Sends acknowledgments and status updates back to PC
 * - Manages device state and validates command sequences
 */
@ServiceScoped
class CommandProcessor @Inject constructor(
    @ApplicationContext private val context: Context,
    private val sessionManager: SessionManager,
    private val cameraRecorder: CameraRecorder,
    private val thermalRecorder: ThermalRecorder,
    private val logger: Logger
) {
    
    private val processingScope = CoroutineScope(Dispatchers.Default + Job())
    private var jsonSocketClient: JsonSocketClient? = null
    private var isRecording = false
    private var currentSessionId: String? = null
    private var stimulusTime: Long? = null
    
    /**
     * Set the JsonSocketClient for sending responses
     */
    fun setSocketClient(client: JsonSocketClient) {
        jsonSocketClient = client
        logger.info("CommandProcessor connected to JsonSocketClient")
    }
    
    /**
     * Process incoming command from PC
     */
    fun processCommand(message: JsonMessage) {
        processingScope.launch {
            try {
                when (message) {
                    is StartRecordCommand -> handleStartRecord(message)
                    is StopRecordCommand -> handleStopRecord(message)
                    is CaptureCalibrationCommand -> handleCaptureCalibration(message)
                    is SetStimulusTimeCommand -> handleSetStimulusTime(message)
                    else -> {
                        logger.warning("Received unsupported command: ${message.type}")
                    }
                }
            } catch (e: Exception) {
                logger.error("Error processing command: ${message.type}", e)
                jsonSocketClient?.sendAck(message.type, false, "Processing error: ${e.message}")
            }
        }
    }
    
    /**
     * Handle start_record command from PC
     */
    private suspend fun handleStartRecord(command: StartRecordCommand) {
        logger.info("Processing start_record command: ${command.session_id}")
        
        try {
            // Validate state - don't start if already recording
            if (isRecording) {
                logger.warning("Already recording - ignoring start_record command")
                jsonSocketClient?.sendAck("start_record", false, "Already recording")
                return
            }
            
            // Start recording via RecordingService
            val intent = Intent(context, RecordingService::class.java).apply {
                action = RecordingService.ACTION_START_RECORDING
                putExtra("session_id", command.session_id)
                putExtra("record_video", command.record_video)
                putExtra("record_thermal", command.record_thermal)
                putExtra("record_shimmer", command.record_shimmer)
            }
            
            // Use appropriate service start method based on Android version
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                context.startForegroundService(intent)
            } else {
                context.startService(intent)
            }
            
            // Update state
            isRecording = true
            currentSessionId = command.session_id
            
            // Send acknowledgment
            jsonSocketClient?.sendAck("start_record", true)
            
            // Send status update
            sendStatusUpdate()
            
            logger.info("Recording started successfully: ${command.session_id}")
            
        } catch (e: Exception) {
            logger.error("Failed to start recording", e)
            jsonSocketClient?.sendAck("start_record", false, "Failed to start recording: ${e.message}")
        }
    }
    
    /**
     * Handle stop_record command from PC
     */
    private suspend fun handleStopRecord(command: StopRecordCommand) {
        logger.info("Processing stop_record command")
        
        try {
            // Validate state - don't stop if not recording
            if (!isRecording) {
                logger.warning("Not recording - ignoring stop_record command")
                jsonSocketClient?.sendAck("stop_record", false, "Not currently recording")
                return
            }
            
            // Stop recording via RecordingService
            val intent = Intent(context, RecordingService::class.java).apply {
                action = RecordingService.ACTION_STOP_RECORDING
            }
            
            context.startService(intent)
            
            // Update state
            isRecording = false
            currentSessionId = null
            
            // Send acknowledgment
            jsonSocketClient?.sendAck("stop_record", true)
            
            // Send status update
            sendStatusUpdate()
            
            logger.info("Recording stopped successfully")
            
        } catch (e: Exception) {
            logger.error("Failed to stop recording", e)
            jsonSocketClient?.sendAck("stop_record", false, "Failed to stop recording: ${e.message}")
        }
    }
    
    /**
     * Handle capture_calibration command from PC
     */
    private suspend fun handleCaptureCalibration(command: CaptureCalibrationCommand) {
        logger.info("Processing capture_calibration command")
        
        try {
            // Capture calibration images from both RGB and thermal cameras
            val calibrationResults = mutableListOf<String>()
            
            // Capture RGB calibration image
            try {
                val rgbCalibrationPath = captureRgbCalibrationImage()
                if (rgbCalibrationPath != null) {
                    calibrationResults.add("RGB calibration captured: $rgbCalibrationPath")
                }
            } catch (e: Exception) {
                logger.error("Failed to capture RGB calibration", e)
                calibrationResults.add("RGB calibration failed: ${e.message}")
            }
            
            // Capture thermal calibration image
            try {
                val thermalCalibrationPath = captureThermalCalibrationImage()
                if (thermalCalibrationPath != null) {
                    calibrationResults.add("Thermal calibration captured: $thermalCalibrationPath")
                }
            } catch (e: Exception) {
                logger.error("Failed to capture thermal calibration", e)
                calibrationResults.add("Thermal calibration failed: ${e.message}")
            }
            
            // Send acknowledgment with results
            val resultMessage = calibrationResults.joinToString("; ")
            jsonSocketClient?.sendAck("capture_calibration", true, resultMessage)
            
            logger.info("Calibration capture completed: $resultMessage")
            
        } catch (e: Exception) {
            logger.error("Failed to capture calibration", e)
            jsonSocketClient?.sendAck("capture_calibration", false, "Calibration capture failed: ${e.message}")
        }
    }
    
    /**
     * Handle set_stimulus_time command from PC
     * Implements scheduled stimulus actions and synchronization events
     */
    private suspend fun handleSetStimulusTime(command: SetStimulusTimeCommand) {
        logger.info("Processing set_stimulus_time command: ${command.time}")
        
        try {
            // Store stimulus time for synchronization
            stimulusTime = command.time
            val currentTime = System.currentTimeMillis()
            val timeOffset = command.time - currentTime
            
            // Log the stimulus time for data alignment
            logger.info("Stimulus time set: ${command.time} (offset: ${timeOffset}ms from current time)")
            
            // Schedule stimulus actions based on timing
            if (timeOffset > 0) {
                // Future stimulus - schedule actions
                scheduleStimulusActions(command.time, timeOffset)
                logger.info("Scheduled stimulus actions for future execution in ${timeOffset}ms")
            } else if (Math.abs(timeOffset) < 1000) {
                // Near-current time - execute immediately
                executeStimulusActions(command.time)
                logger.info("Executed immediate stimulus actions (time offset: ${timeOffset}ms)")
            } else {
                // Past time - log for synchronization only
                logger.info("Stimulus time is in the past (${Math.abs(timeOffset)}ms ago) - recorded for data alignment")
            }
            
            // Create synchronization marker for data analysis
            createSynchronizationMarker(command.time)
            
            // Send acknowledgment with timing information
            val statusMessage = "Stimulus time processed (offset: ${timeOffset}ms)"
            jsonSocketClient?.sendAck("set_stimulus_time", true, statusMessage)
            
        } catch (e: Exception) {
            logger.error("Failed to set stimulus time", e)
            jsonSocketClient?.sendAck("set_stimulus_time", false, "Failed to set stimulus time: ${e.message}")
        }
    }
    
    /**
     * Schedule stimulus actions for future execution
     */
    private fun scheduleStimulusActions(stimulusTime: Long, delayMs: Long) {
        processingScope.launch {
            try {
                // Wait until stimulus time
                kotlinx.coroutines.delay(delayMs)
                
                // Execute stimulus actions at the scheduled time
                executeStimulusActions(stimulusTime)
                
            } catch (e: Exception) {
                logger.error("Error executing scheduled stimulus actions", e)
            }
        }
    }
    
    /**
     * Execute stimulus actions at the specified time
     */
    private suspend fun executeStimulusActions(stimulusTime: Long) {
        try {
            logger.info("Executing stimulus actions at time: $stimulusTime")
            
            // 1. Create stimulus event marker in logs
            logger.info("STIMULUS_EVENT: timestamp=$stimulusTime, device_time=${System.currentTimeMillis()}")
            
            // 2. Send stimulus notification to PC
            sendStimulusNotification(stimulusTime)
            
            // 3. Trigger device-specific stimulus actions
            triggerDeviceStimulusActions(stimulusTime)
            
            // 4. Update recording metadata if recording is active
            if (isRecording) {
                updateRecordingMetadata(stimulusTime)
            }
            
            logger.info("Stimulus actions completed successfully")
            
        } catch (e: Exception) {
            logger.error("Error executing stimulus actions", e)
        }
    }
    
    /**
     * Send stimulus notification to PC
     */
    private fun sendStimulusNotification(stimulusTime: Long) {
        try {
            val statusMessage = StatusMessage(
                battery = getBatteryLevel(),
                storage = getAvailableStorage(),
                temperature = getDeviceTemperature(),
                recording = isRecording,
                connected = true
            )
            
            jsonSocketClient?.sendMessage(statusMessage)
            logger.debug("Sent stimulus notification to PC")
            
        } catch (e: Exception) {
            logger.error("Failed to send stimulus notification", e)
        }
    }
    
    /**
     * Trigger device-specific stimulus actions
     */
    private suspend fun triggerDeviceStimulusActions(stimulusTime: Long) {
        try {
            // Trigger visual stimulus (could be screen flash, LED, etc.)
            triggerVisualStimulus()
            
            // Trigger audio stimulus (could be beep, tone, etc.)
            triggerAudioStimulus()
            
            // Trigger haptic feedback
            triggerHapticFeedback()
            
            // Log stimulus triggers for analysis
            logger.info("STIMULUS_TRIGGERS: visual=true, audio=true, haptic=true, timestamp=$stimulusTime")
            
        } catch (e: Exception) {
            logger.error("Error triggering device stimulus actions", e)
        }
    }
    
    /**
     * Trigger visual stimulus with screen flash effect
     */
    private fun triggerVisualStimulus() {
        try {
            // Create a visual stimulus by manipulating screen brightness
            val intent = Intent("com.multisensor.recording.VISUAL_STIMULUS").apply {
                putExtra("stimulus_type", "screen_flash")
                putExtra("duration_ms", 200L)
                putExtra("timestamp", System.currentTimeMillis())
            }
            
            // Send broadcast to trigger visual stimulus in UI
            context.sendBroadcast(intent)
            
            logger.debug("Visual stimulus triggered - screen flash broadcast sent")
            
        } catch (e: Exception) {
            logger.error("Failed to trigger visual stimulus", e)
        }
    }
    
    /**
     * Trigger audio stimulus with tone generation
     */
    private fun triggerAudioStimulus() {
        try {
            // Generate audio stimulus using ToneGenerator
            val toneGenerator = android.media.ToneGenerator(
                android.media.AudioManager.STREAM_NOTIFICATION,
                80 // Volume (0-100)
            )
            
            // Play a short beep tone (1000Hz for 200ms)
            toneGenerator.startTone(android.media.ToneGenerator.TONE_PROP_BEEP, 200)
            
            // Schedule cleanup
            kotlinx.coroutines.CoroutineScope(kotlinx.coroutines.Dispatchers.IO).launch {
                kotlinx.coroutines.delay(300) // Wait for tone to finish
                try {
                    toneGenerator.release()
                } catch (e: Exception) {
                    logger.debug("ToneGenerator already released", e)
                }
            }
            
            logger.debug("Audio stimulus triggered - tone generated")
            
        } catch (e: Exception) {
            logger.error("Failed to trigger audio stimulus", e)
        }
    }
    
    /**
     * Trigger haptic feedback
     */
    private fun triggerHapticFeedback() {
        try {
            val vibrator = if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.S) {
                val vibratorManager = context.getSystemService(Context.VIBRATOR_MANAGER_SERVICE) as android.os.VibratorManager
                vibratorManager.defaultVibrator
            } else {
                @Suppress("DEPRECATION")
                context.getSystemService(Context.VIBRATOR_SERVICE) as android.os.Vibrator
            }
            
            if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
                vibrator.vibrate(android.os.VibrationEffect.createOneShot(100, android.os.VibrationEffect.DEFAULT_AMPLITUDE))
            } else {
                @Suppress("DEPRECATION")
                vibrator.vibrate(100)
            }
            
            logger.debug("Haptic feedback triggered")
            
        } catch (e: Exception) {
            logger.debug("Haptic feedback not available", e)
        }
    }
    
    /**
     * Update recording metadata with stimulus information
     */
    private fun updateRecordingMetadata(stimulusTime: Long) {
        try {
            // TODO: Add stimulus timestamp to recording metadata
            // This could involve writing to a metadata file or updating session info
            logger.info("RECORDING_METADATA: stimulus_time=$stimulusTime, session_id=$currentSessionId")
            
        } catch (e: Exception) {
            logger.error("Failed to update recording metadata", e)
        }
    }
    
    /**
     * Create synchronization marker for data analysis
     */
    private fun createSynchronizationMarker(stimulusTime: Long) {
        try {
            // Create synchronization marker file for post-processing
            val syncDir = File(context.getExternalFilesDir(null), "synchronization")
            syncDir.mkdirs()
            
            val syncFile = File(syncDir, "stimulus_sync_${System.currentTimeMillis()}.txt")
            syncFile.writeText(
                "STIMULUS_SYNC_MARKER\n" +
                "stimulus_time=$stimulusTime\n" +
                "device_time=${System.currentTimeMillis()}\n" +
                "session_id=$currentSessionId\n" +
                "recording_active=$isRecording\n"
            )
            
            logger.debug("Created synchronization marker: ${syncFile.absolutePath}")
            
        } catch (e: Exception) {
            logger.error("Failed to create synchronization marker", e)
        }
    }
    
    /**
     * Capture RGB calibration image using CameraRecorder
     */
    private suspend fun captureRgbCalibrationImage(): String? {
        return try {
            logger.info("Starting RGB calibration image capture...")
            
            // Create calibration directory
            val calibrationDir = File(context.getExternalFilesDir(null), "calibration")
            calibrationDir.mkdirs()
            
            val calibrationFile = File(calibrationDir, "rgb_calibration_${System.currentTimeMillis()}.jpg")
            
            // Capture still image using CameraRecorder
            val success = cameraRecorder.captureCalibrationImage(calibrationFile.absolutePath)
            
            if (success) {
                logger.info("RGB calibration image captured successfully: ${calibrationFile.absolutePath}")
                calibrationFile.absolutePath
            } else {
                logger.warning("RGB calibration image capture failed")
                null
            }
            
        } catch (e: Exception) {
            logger.error("Failed to capture RGB calibration image", e)
            null
        }
    }
    
    /**
     * Capture thermal calibration image using ThermalRecorder
     */
    private suspend fun captureThermalCalibrationImage(): String? {
        return try {
            logger.info("Starting thermal calibration image capture...")
            
            // Create calibration directory
            val calibrationDir = File(context.getExternalFilesDir(null), "calibration")
            calibrationDir.mkdirs()
            
            val calibrationFile = File(calibrationDir, "thermal_calibration_${System.currentTimeMillis()}.jpg")
            
            // Capture thermal calibration image using ThermalRecorder
            val success = thermalRecorder.captureCalibrationImage(calibrationFile.absolutePath)
            
            if (success) {
                logger.info("Thermal calibration image captured successfully: ${calibrationFile.absolutePath}")
                calibrationFile.absolutePath
            } else {
                logger.warning("Thermal calibration image capture failed")
                null
            }
            
        } catch (e: Exception) {
            logger.error("Failed to capture thermal calibration image", e)
            null
        }
    }
    
    /**
     * Send device status update to PC
     */
    private fun sendStatusUpdate() {
        try {
            val battery = getBatteryLevel()
            val storage = getAvailableStorage()
            val temperature = getDeviceTemperature()
            
            jsonSocketClient?.sendStatusUpdate(
                battery = battery,
                storage = storage,
                temperature = temperature,
                recording = isRecording
            )
            
        } catch (e: Exception) {
            logger.error("Failed to send status update", e)
        }
    }
    
    /**
     * Get current battery level
     */
    private fun getBatteryLevel(): Int? {
        return try {
            val batteryManager = context.getSystemService(Context.BATTERY_SERVICE) as BatteryManager
            batteryManager.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY)
        } catch (e: Exception) {
            logger.debug("Failed to get battery level", e)
            null
        }
    }
    
    /**
     * Get available storage space
     */
    private fun getAvailableStorage(): String? {
        return try {
            val externalDir = context.getExternalFilesDir(null)
            if (externalDir != null) {
                val stat = StatFs(externalDir.path)
                val availableBytes = stat.availableBytes
                val availableGB = availableBytes / (1024 * 1024 * 1024)
                "${availableGB}GB_free"
            } else {
                null
            }
        } catch (e: Exception) {
            logger.debug("Failed to get storage info", e)
            null
        }
    }
    
    /**
     * Get device temperature (if available)
     */
    private fun getDeviceTemperature(): Double? {
        return try {
            // Android doesn't provide easy access to device temperature
            // This would require thermal management APIs or hardware-specific implementations
            // For now, return null
            null
        } catch (e: Exception) {
            logger.debug("Failed to get device temperature", e)
            null
        }
    }
    
    /**
     * Get current recording state
     */
    fun isRecording(): Boolean = isRecording
    
    /**
     * Get current session ID
     */
    fun getCurrentSessionId(): String? = currentSessionId
    
    /**
     * Get stimulus time
     */
    fun getStimulusTime(): Long? = stimulusTime
}
