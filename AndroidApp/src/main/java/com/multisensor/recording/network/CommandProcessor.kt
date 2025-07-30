package com.multisensor.recording.network

import android.content.Context
import android.content.Intent
import android.hardware.camera2.CameraManager
import android.media.AudioManager
import android.media.ToneGenerator
import android.os.BatteryManager
import android.os.Build
import android.os.StatFs
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager
import com.multisensor.recording.calibration.CalibrationCaptureManager
import com.multisensor.recording.calibration.SyncClockManager
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
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import java.io.File
import javax.inject.Inject

/**
 * Command Processor for Milestone 2.6 & 2.8 Network Communication.
 * Processes incoming JSON commands from PC and executes corresponding actions.
 *
 * Enhanced for Milestone 2.8 with:
 * - Calibration capture coordination with CalibrationCaptureManager
 * - Clock synchronization with SyncClockManager
 * - Sync signal support (flash, beep) for multi-device coordination
 * - Enhanced calibration capture with matching identifiers
 */
@ServiceScoped
class CommandProcessor
    @Inject
    constructor(
        @ApplicationContext private val context: Context,
        private val sessionManager: SessionManager,
        private val cameraRecorder: CameraRecorder,
        private val thermalRecorder: ThermalRecorder,
        private val calibrationCaptureManager: CalibrationCaptureManager,
        private val syncClockManager: SyncClockManager,
        private val fileTransferHandler: FileTransferHandler,
        private val logger: Logger,
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
            fileTransferHandler.initialize(client)
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
                        is FlashSyncCommand -> handleFlashSync(message)
                        is BeepSyncCommand -> handleBeepSync(message)
                        is SyncTimeCommand -> handleSyncTime(message)
                        is SendFileCommand -> handleSendFile(message)
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
                val intent =
                    Intent(context, RecordingService::class.java).apply {
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
                val intent =
                    Intent(context, RecordingService::class.java).apply {
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
         * Handle capture_calibration command from PC - Enhanced for Milestone 2.8
         */
        private suspend fun handleCaptureCalibration(command: CaptureCalibrationCommand) {
            logger.info("[DEBUG_LOG] Processing enhanced capture_calibration command")
            logger.info("[DEBUG_LOG] Calibration ID: ${command.calibration_id}")
            logger.info(
                "[DEBUG_LOG] Capture RGB: ${command.capture_rgb}, Thermal: ${command.capture_thermal}, High-res: ${command.high_resolution}",
            )

            try {
                // Use CalibrationCaptureManager for coordinated capture
                val result =
                    calibrationCaptureManager.captureCalibrationImages(
                        calibrationId = command.calibration_id,
                        captureRgb = command.capture_rgb,
                        captureThermal = command.capture_thermal,
                        highResolution = command.high_resolution,
                    )

                if (result.success) {
                    val resultMessage =
                        buildString {
                            append("Calibration capture successful: ${result.calibrationId}")
                            result.rgbFilePath?.let { append(", RGB: $it") }
                            result.thermalFilePath?.let { append(", Thermal: $it") }
                            append(", Synced timestamp: ${result.syncedTimestamp}")
                        }

                    jsonSocketClient?.sendAck("capture_calibration", true, resultMessage)
                    logger.info("[DEBUG_LOG] $resultMessage")
                } else {
                    val errorMessage = result.errorMessage ?: "Unknown calibration capture error"
                    jsonSocketClient?.sendAck("capture_calibration", false, "Calibration capture failed: $errorMessage")
                    logger.error("Calibration capture failed: $errorMessage")
                }
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
        private fun scheduleStimulusActions(
            stimulusTime: Long,
            delayMs: Long,
        ) {
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
                val statusMessage =
                    StatusMessage(
                        battery = getBatteryLevel(),
                        storage = getAvailableStorage(),
                        temperature = getDeviceTemperature(),
                        recording = isRecording,
                        connected = true,
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
                val intent =
                    Intent("com.multisensor.recording.VISUAL_STIMULUS").apply {
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
                val toneGenerator =
                    android.media.ToneGenerator(
                        android.media.AudioManager.STREAM_NOTIFICATION,
                        80, // Volume (0-100)
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
                val vibrator =
                    if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.S) {
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
         * Trigger visual stimulus with specified duration - Milestone 2.8
         */
        private fun triggerVisualStimulusWithDuration(durationMs: Long) {
            try {
                // Create a visual stimulus by manipulating screen brightness
                val intent =
                    Intent("com.multisensor.recording.VISUAL_STIMULUS").apply {
                        putExtra("stimulus_type", "screen_flash")
                        putExtra("duration_ms", durationMs)
                        putExtra("timestamp", System.currentTimeMillis())
                    }

                // Send broadcast to trigger visual stimulus in UI
                context.sendBroadcast(intent)

                logger.debug("Visual stimulus triggered - screen flash broadcast sent (${durationMs}ms)")
            } catch (e: Exception) {
                logger.error("Failed to trigger visual stimulus", e)
            }
        }

        /**
         * Trigger audio stimulus with specified parameters - Milestone 2.8
         */
        private fun triggerAudioStimulusWithParameters(
            frequencyHz: Int,
            durationMs: Long,
            volume: Float,
        ) {
            try {
                // Generate audio stimulus using ToneGenerator with specified parameters
                val volumePercent = (volume * 100).toInt().coerceIn(0, 100)
                val toneGenerator =
                    android.media.ToneGenerator(
                        android.media.AudioManager.STREAM_NOTIFICATION,
                        volumePercent,
                    )

                // Play tone with specified frequency and duration
                toneGenerator.startTone(android.media.ToneGenerator.TONE_PROP_BEEP, durationMs.toInt())

                // Schedule cleanup
                kotlinx.coroutines.CoroutineScope(kotlinx.coroutines.Dispatchers.IO).launch {
                    kotlinx.coroutines.delay(durationMs + 100) // Wait for tone to finish plus buffer
                    try {
                        toneGenerator.release()
                    } catch (e: Exception) {
                        logger.debug("ToneGenerator already released", e)
                    }
                }

                logger.debug("Audio stimulus triggered - tone generated (${frequencyHz}Hz, ${durationMs}ms, vol=$volume)")
            } catch (e: Exception) {
                logger.error("Failed to trigger audio stimulus", e)
            }
        }

        /**
         * Create flash sync marker for multi-device coordination - Milestone 2.8
         */
        private fun createFlashSyncMarker(
            syncId: String,
            durationMs: Long,
        ) {
            try {
                val syncDir = File(context.getExternalFilesDir(null), "synchronization")
                syncDir.mkdirs()

                val syncFile = File(syncDir, "flash_sync_${syncId}_${System.currentTimeMillis()}.txt")
                syncFile.writeText(
                    "FLASH_SYNC_MARKER\n" +
                        "sync_id=$syncId\n" +
                        "duration_ms=$durationMs\n" +
                        "device_time=${System.currentTimeMillis()}\n" +
                        "session_id=$currentSessionId\n" +
                        "recording_active=$isRecording\n",
                )

                logger.debug("Created flash sync marker: ${syncFile.absolutePath}")
            } catch (e: Exception) {
                logger.error("Failed to create flash sync marker", e)
            }
        }

        /**
         * Create beep sync marker for multi-device coordination - Milestone 2.8
         */
        private fun createBeepSyncMarker(
            syncId: String,
            frequencyHz: Int,
            durationMs: Long,
            volume: Float,
        ) {
            try {
                val syncDir = File(context.getExternalFilesDir(null), "synchronization")
                syncDir.mkdirs()

                val syncFile = File(syncDir, "beep_sync_${syncId}_${System.currentTimeMillis()}.txt")
                syncFile.writeText(
                    "BEEP_SYNC_MARKER\n" +
                        "sync_id=$syncId\n" +
                        "frequency_hz=$frequencyHz\n" +
                        "duration_ms=$durationMs\n" +
                        "volume=$volume\n" +
                        "device_time=${System.currentTimeMillis()}\n" +
                        "session_id=$currentSessionId\n" +
                        "recording_active=$isRecording\n",
                )

                logger.debug("Created beep sync marker: ${syncFile.absolutePath}")
            } catch (e: Exception) {
                logger.error("Failed to create beep sync marker", e)
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
                        "recording_active=$isRecording\n",
                )

                logger.debug("Created synchronization marker: ${syncFile.absolutePath}")
            } catch (e: Exception) {
                logger.error("Failed to create synchronization marker", e)
            }
        }

        /**
         * Handle flash_sync command from PC - Milestone 2.8
         */
        private suspend fun handleFlashSync(command: FlashSyncCommand) {
            logger.info("[DEBUG_LOG] Processing flash_sync command")
            logger.info("[DEBUG_LOG] Duration: ${command.duration_ms}ms, Sync ID: ${command.sync_id}")

            try {
                // Trigger visual stimulus (screen flash) with specified duration
                triggerVisualStimulusWithDuration(command.duration_ms)

                // Create sync marker for multi-device coordination
                command.sync_id?.let { syncId ->
                    createFlashSyncMarker(syncId, command.duration_ms)
                }

                // Send acknowledgment
                val resultMessage = "Flash sync triggered (${command.duration_ms}ms)"
                jsonSocketClient?.sendAck("flash_sync", true, resultMessage)

                logger.info("[DEBUG_LOG] Flash sync completed: $resultMessage")
            } catch (e: Exception) {
                logger.error("Failed to trigger flash sync", e)
                jsonSocketClient?.sendAck("flash_sync", false, "Flash sync failed: ${e.message}")
            }
        }

        /**
         * Handle beep_sync command from PC - Milestone 2.8
         */
        private suspend fun handleBeepSync(command: BeepSyncCommand) {
            logger.info("[DEBUG_LOG] Processing beep_sync command")
            logger.info(
                "[DEBUG_LOG] Frequency: ${command.frequency_hz}Hz, Duration: ${command.duration_ms}ms, Volume: ${command.volume}, Sync ID: ${command.sync_id}",
            )

            try {
                // Trigger audio stimulus (beep) with specified parameters
                triggerAudioStimulusWithParameters(
                    frequencyHz = command.frequency_hz,
                    durationMs = command.duration_ms,
                    volume = command.volume,
                )

                // Create sync marker for multi-device coordination
                command.sync_id?.let { syncId ->
                    createBeepSyncMarker(syncId, command.frequency_hz, command.duration_ms, command.volume)
                }

                // Send acknowledgment
                val resultMessage = "Beep sync triggered (${command.frequency_hz}Hz, ${command.duration_ms}ms, vol=${command.volume})"
                jsonSocketClient?.sendAck("beep_sync", true, resultMessage)

                logger.info("[DEBUG_LOG] Beep sync completed: $resultMessage")
            } catch (e: Exception) {
                logger.error("Failed to trigger beep sync", e)
                jsonSocketClient?.sendAck("beep_sync", false, "Beep sync failed: ${e.message}")
            }
        }

        /**
         * Handle send_file command from PC - Milestone 3.6
         */
        private suspend fun handleSendFile(command: SendFileCommand) {
            logger.info("Processing send_file command for: ${command.filepath}")

            try {
                // Delegate to FileTransferHandler
                fileTransferHandler.handleSendFileCommand(command)

                logger.info("File transfer request delegated to FileTransferHandler")
            } catch (e: Exception) {
                logger.error("Failed to handle send_file command", e)
                jsonSocketClient?.sendAck("send_file", false, "Failed to process file transfer: ${e.message}")
            }
        }

        /**
         * Handle sync_time command from PC - Milestone 2.8
         */
        private suspend fun handleSyncTime(command: SyncTimeCommand) {
            logger.info("[DEBUG_LOG] Processing sync_time command")
            logger.info("[DEBUG_LOG] PC timestamp: ${command.pc_timestamp}, Sync ID: ${command.sync_id}")

            try {
                // Use SyncClockManager for clock synchronization
                val success =
                    syncClockManager.synchronizeWithPc(
                        pcTimestamp = command.pc_timestamp,
                        syncId = command.sync_id,
                    )

                if (success) {
                    // Get sync status for detailed information
                    val syncStatus = syncClockManager.getSyncStatus()
                    val resultMessage =
                        buildString {
                            append("Clock sync successful: offset=${syncStatus.clockOffsetMs}ms")
                            command.sync_id?.let { syncId -> append(", sync_id=$syncId") }
                            append(", age=${syncStatus.syncAge}ms")
                        }

                    jsonSocketClient?.sendAck("sync_time", true, resultMessage)
                    logger.info("[DEBUG_LOG] $resultMessage")
                } else {
                    val errorMessage = "Clock synchronization failed - invalid PC timestamp or sync error"
                    jsonSocketClient?.sendAck("sync_time", false, "Clock sync failed: $errorMessage")
                    logger.error("Clock sync failed: $errorMessage")
                }
            } catch (e: Exception) {
                logger.error("Failed to sync time", e)
                jsonSocketClient?.sendAck("sync_time", false, "Clock sync failed: ${e.message}")
            }
        }

        /**
         * Capture RGB calibration image using CameraRecorder
         */
        private suspend fun captureRgbCalibrationImage(): String? =
            try {
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

        /**
         * Capture thermal calibration image using ThermalRecorder
         */
        private suspend fun captureThermalCalibrationImage(): String? =
            try {
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
                    recording = isRecording,
                )
            } catch (e: Exception) {
                logger.error("Failed to send status update", e)
            }
        }

        /**
         * Get current battery level
         */
        private fun getBatteryLevel(): Int? =
            try {
                val batteryManager = context.getSystemService(Context.BATTERY_SERVICE) as BatteryManager
                batteryManager.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY)
            } catch (e: Exception) {
                logger.debug("Failed to get battery level", e)
                null
            }

        /**
         * Get available storage space
         */
        private fun getAvailableStorage(): String? =
            try {
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

        /**
         * Get device temperature (if available)
         */
        private fun getDeviceTemperature(): Double? =
            try {
                // Android doesn't provide easy access to device temperature
                // This would require thermal management APIs or hardware-specific implementations
                // For now, return null
                null
            } catch (e: Exception) {
                logger.debug("Failed to get device temperature", e)
                null
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

        /**
         * Trigger visual stimulus (screen flash) with specified duration - Milestone 2.8
         */
        private suspend fun triggerVisualStimulusWithDuration(durationMs: Int) {
            try {
                logger.info("[DEBUG_LOG] Triggering visual stimulus for ${durationMs}ms")

                // Use camera flash if available
                val cameraManager = context.getSystemService(Context.CAMERA_SERVICE) as CameraManager
                val cameraIds = cameraManager.cameraIdList

                // Find back camera with flash
                var flashCameraId: String? = null
                for (cameraId in cameraIds) {
                    val characteristics = cameraManager.getCameraCharacteristics(cameraId)
                    val hasFlash = characteristics.get(android.hardware.camera2.CameraCharacteristics.FLASH_INFO_AVAILABLE) == true
                    val lensFacing = characteristics.get(android.hardware.camera2.CameraCharacteristics.LENS_FACING)

                    if (hasFlash && lensFacing == android.hardware.camera2.CameraCharacteristics.LENS_FACING_BACK) {
                        flashCameraId = cameraId
                        break
                    }
                }

                if (flashCameraId != null) {
                    // Turn on torch
                    cameraManager.setTorchMode(flashCameraId, true)
                    logger.debug("[DEBUG_LOG] Camera flash turned ON")

                    // Wait for specified duration
                    delay(durationMs.toLong())

                    // Turn off torch
                    cameraManager.setTorchMode(flashCameraId, false)
                    logger.debug("[DEBUG_LOG] Camera flash turned OFF")
                } else {
                    logger.warning("No camera flash available - visual stimulus not triggered")
                }
            } catch (e: Exception) {
                logger.error("Failed to trigger visual stimulus", e)
                throw e
            }
        }

        /**
         * Trigger audio stimulus (beep) with specified parameters - Milestone 2.8
         */
        private suspend fun triggerAudioStimulusWithParameters(
            frequencyHz: Int,
            durationMs: Int,
            volume: Float,
        ) {
            try {
                logger.info("[DEBUG_LOG] Triggering audio stimulus: ${frequencyHz}Hz, ${durationMs}ms, vol=$volume")

                // Create tone generator
                val toneGenerator =
                    ToneGenerator(
                        AudioManager.STREAM_MUSIC,
                        (volume * 100).toInt().coerceIn(0, 100),
                    )

                // Generate tone for specified duration
                // Note: ToneGenerator doesn't support custom frequencies directly
                // Using predefined tones based on frequency ranges
                val toneType =
                    when (frequencyHz) {
                        in 800..1200 -> ToneGenerator.TONE_CDMA_ALERT_CALL_GUARD
                        in 400..800 -> ToneGenerator.TONE_CDMA_EMERGENCY_RINGBACK
                        in 200..400 -> ToneGenerator.TONE_CDMA_HIGH_L
                        else -> ToneGenerator.TONE_CDMA_MED_L
                    }

                toneGenerator.startTone(toneType, durationMs)
                logger.debug("[DEBUG_LOG] Audio tone started")

                // Wait for tone duration
                delay(durationMs.toLong())

                // Stop tone and release resources
                toneGenerator.stopTone()
                toneGenerator.release()
                logger.debug("[DEBUG_LOG] Audio tone completed and resources released")
            } catch (e: Exception) {
                logger.error("Failed to trigger audio stimulus", e)
                throw e
            }
        }

        /**
         * Create flash sync marker file for multi-device coordination - Milestone 2.8
         */
        private fun createFlashSyncMarker(
            syncId: String,
            durationMs: Int,
        ) {
            try {
                val syncDir = File(context.getExternalFilesDir(null), "sync_markers")
                syncDir.mkdirs()

                val syncFile = File(syncDir, "flash_sync_${syncId}_${System.currentTimeMillis()}.txt")
                val currentTime = System.currentTimeMillis()
                val syncedTime = syncClockManager.getSyncedTimestamp(currentTime)

                syncFile.writeText(
                    "FLASH_SYNC_MARKER\n" +
                        "sync_id=$syncId\n" +
                        "duration_ms=$durationMs\n" +
                        "device_time=$currentTime\n" +
                        "synced_time=$syncedTime\n" +
                        "session_id=$currentSessionId\n" +
                        "recording_active=$isRecording\n",
                )

                logger.debug("[DEBUG_LOG] Created flash sync marker: ${syncFile.absolutePath}")
            } catch (e: Exception) {
                logger.error("Failed to create flash sync marker", e)
            }
        }

        /**
         * Create beep sync marker file for multi-device coordination - Milestone 2.8
         */
        private fun createBeepSyncMarker(
            syncId: String,
            frequencyHz: Int,
            durationMs: Int,
            volume: Float,
        ) {
            try {
                val syncDir = File(context.getExternalFilesDir(null), "sync_markers")
                syncDir.mkdirs()

                val syncFile = File(syncDir, "beep_sync_${syncId}_${System.currentTimeMillis()}.txt")
                val currentTime = System.currentTimeMillis()
                val syncedTime = syncClockManager.getSyncedTimestamp(currentTime)

                syncFile.writeText(
                    "BEEP_SYNC_MARKER\n" +
                        "sync_id=$syncId\n" +
                        "frequency_hz=$frequencyHz\n" +
                        "duration_ms=$durationMs\n" +
                        "volume=$volume\n" +
                        "device_time=$currentTime\n" +
                        "synced_time=$syncedTime\n" +
                        "session_id=$currentSessionId\n" +
                        "recording_active=$isRecording\n",
                )

                logger.debug("[DEBUG_LOG] Created beep sync marker: ${syncFile.absolutePath}")
            } catch (e: Exception) {
                logger.error("Failed to create beep sync marker", e)
            }
        }
    }
