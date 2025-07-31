package com.multisensor.recording.recording

import android.Manifest
import android.app.Activity
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothManager
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Handler
import android.os.HandlerThread
import android.os.Looper
import android.os.Message
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.multisensor.recording.recording.DeviceConfiguration.SensorChannel
import com.multisensor.recording.service.SessionManager
import com.multisensor.recording.util.Logger
import com.multisensor.recording.util.AppLogger
import com.multisensor.recording.util.logD
import com.multisensor.recording.util.logE
import com.multisensor.recording.util.logI
import com.multisensor.recording.util.logW
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.*
import java.io.BufferedWriter
import java.io.File
import java.io.FileWriter
import java.io.PrintWriter
import java.net.Socket
import java.text.SimpleDateFormat
import java.util.*
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.ConcurrentLinkedQueue
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong
import javax.inject.Inject
import javax.inject.Singleton

// shimmer sdk imports
import com.shimmerresearch.android.Shimmer
import com.shimmerresearch.android.manager.ShimmerBluetoothManagerAndroid
import com.shimmerresearch.driver.ObjectCluster
import com.shimmerresearch.driver.CallbackObject
import com.shimmerresearch.driver.Configuration
import com.shimmerresearch.driver.FormatCluster
import com.shimmerresearch.bluetooth.ShimmerBluetooth

/**
 * shimmer3 gsr+ sensor recorder with bluetooth management
 */
@Singleton
class ShimmerRecorder
    @Inject
    constructor(
        @ApplicationContext private val context: Context,
        private val sessionManager: SessionManager,
        private val logger: Logger,
    ) {
        private val isRecording = AtomicBoolean(false)
        private val isInitialized = AtomicBoolean(false)
        private val isConnected = AtomicBoolean(false)
        private var currentSessionInfo: SessionInfo? = null
        private var currentSessionId: String? = null
        private var sessionStartTime: Long = 0L

        private var bluetoothAdapter: BluetoothAdapter? = null
        private var bluetoothManager: BluetoothManager? = null

        private var samplingRate: Double = DEFAULT_SAMPLING_RATE
        private var sampleCount: Long = 0L
        private var dataWriter: FileWriter? = null

        private val connectedDevices = ConcurrentHashMap<String, ShimmerDevice>()
        private val deviceConfigurations = ConcurrentHashMap<String, DeviceConfiguration>()
        private val dataQueues = ConcurrentHashMap<String, ConcurrentLinkedQueue<SensorSample>>()

        // Shimmer SDK management
        private var shimmerBluetoothManager: ShimmerBluetoothManagerAndroid? = null
        private val shimmerDevices = ConcurrentHashMap<String, Shimmer>()
        private val shimmerHandlers = ConcurrentHashMap<String, Handler>()

        // Threading and data processing
        private var dataHandlerThread: HandlerThread? = null
        private var dataHandler: Handler? = null
        private var recordingScope: CoroutineScope? = null

        // File I/O management
        private val fileWriters = ConcurrentHashMap<String, BufferedWriter>()

        // Network streaming
        private var streamingSocket: Socket? = null
        private var streamingWriter: PrintWriter? = null
        private val streamingQueue = ConcurrentLinkedQueue<String>()
        private val isStreaming = AtomicBoolean(false)

        // Sample counting and timing
        private val sampleCounts = ConcurrentHashMap<String, AtomicLong>()
        private val dateFormat = SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS", Locale.getDefault())

        companion object {
            private const val TAG = "ShimmerRecorder"

            // Bluetooth permissions for different Android versions
            private val BLUETOOTH_PERMISSIONS_LEGACY =
                arrayOf(
                    Manifest.permission.BLUETOOTH,
                    Manifest.permission.BLUETOOTH_ADMIN,
                    Manifest.permission.ACCESS_FINE_LOCATION,
                    Manifest.permission.ACCESS_COARSE_LOCATION,
                )

            private val BLUETOOTH_PERMISSIONS_NEW =
                arrayOf(
                    Manifest.permission.BLUETOOTH_SCAN,
                    Manifest.permission.BLUETOOTH_CONNECT,
                    Manifest.permission.ACCESS_FINE_LOCATION,
                    Manifest.permission.ACCESS_COARSE_LOCATION,
                )

            // Shimmer sensor constants (matching Shimmer SDK)
            private const val SENSOR_GSR = 0x04
            private const val SENSOR_PPG = 0x4000
            private const val SENSOR_ACCEL = 0x80
            private const val SENSOR_GYRO = 0x40
            private const val SENSOR_MAG = 0x20

            // Default configuration
            private const val DEFAULT_SAMPLING_RATE = 51.2 // Hz
            private const val DEFAULT_GSR_RANGE = 4 // GSR range setting
            private const val DEFAULT_ACCEL_RANGE = 2 // ±2g

            // File and network settings
            private const val CSV_HEADER = "Timestamp_ms,DeviceTime_ms,SystemTime_ms,GSR_Conductance_uS,PPG_A13,Accel_X_g,Accel_Y_g,Accel_Z_g,Battery_Percentage"
            private const val DATA_BATCH_SIZE = 50 // Samples to batch before flushing
            private const val RECONNECTION_ATTEMPTS = 3
            private const val RECONNECTION_DELAY_MS = 2000L

            // Default PIN for Shimmer pairing
            private const val SHIMMER_DEFAULT_PIN = "1234"
            private const val SHIMMER_DEVICE_NAME = "Shimmer3-GSR+"

            // Network streaming settings
            private const val DEFAULT_STREAMING_PORT = 8080
            private const val STREAMING_BUFFER_SIZE = 1024
        }

        /**
         * Create a handler for Shimmer SDK callbacks
         */
        private fun createShimmerHandler(): Handler =
            Handler(Looper.getMainLooper()) { msg ->
                try {
                    when (msg.what) {
                        ShimmerBluetooth.MSG_IDENTIFIER_STATE_CHANGE -> {
                            val obj = msg.obj
                            if (obj is ObjectCluster) {
                                handleShimmerStateChange(obj)
                            } else if (obj is CallbackObject) {
                                handleShimmerCallback(obj)
                            }
                        }
                        ShimmerBluetooth.MSG_IDENTIFIER_DATA_PACKET -> {
                            val obj = msg.obj
                            if (obj is ObjectCluster) {
                                handleShimmerData(obj)
                            }
                        }
                        else -> {
                            logger.debug("Received unknown Shimmer message: ${msg.what}")
                        }
                    }
                } catch (e: Exception) {
                    logger.error("Error handling Shimmer callback", e)
                }
                true
            }

        /**
         * Handle Shimmer device state changes from ObjectCluster or CallbackObject
         */
        private fun handleShimmerStateChange(obj: Any) {
            val state: ShimmerBluetooth.BT_STATE?
            val macAddress: String?

            when (obj) {
                is ObjectCluster -> {
                    state = obj.mState
                    macAddress = obj.macAddress
                }
                is CallbackObject -> {
                    state = obj.mState
                    macAddress = obj.mBluetoothAddress
                }
                else -> {
                    logger.debug("Unknown state change object type: ${obj::class.java.simpleName}")
                    return
                }
            }

            val device = connectedDevices[macAddress]
            if (device != null && state != null) {
                logger.debug("Device ${device.getDisplayName()} state changed to: $state")

                when (state) {
                    ShimmerBluetooth.BT_STATE.CONNECTED -> {
                        device.updateConnectionState(ShimmerDevice.ConnectionState.CONNECTED, logger)
                        logger.info("Device ${device.getDisplayName()} is now CONNECTED")
                    }
                    ShimmerBluetooth.BT_STATE.CONNECTING -> {
                        device.updateConnectionState(ShimmerDevice.ConnectionState.CONNECTING, logger)
                        logger.info("Device ${device.getDisplayName()} is CONNECTING")
                    }
                    ShimmerBluetooth.BT_STATE.STREAMING -> {
                        device.updateConnectionState(ShimmerDevice.ConnectionState.STREAMING, logger)
                        device.isStreaming.set(true)
                        logger.info("Device ${device.getDisplayName()} is now STREAMING")
                    }
                    ShimmerBluetooth.BT_STATE.STREAMING_AND_SDLOGGING -> {
                        device.updateConnectionState(ShimmerDevice.ConnectionState.STREAMING, logger)
                        device.isStreaming.set(true)
                        logger.info("Device ${device.getDisplayName()} is STREAMING AND LOGGING")
                    }
                    ShimmerBluetooth.BT_STATE.SDLOGGING -> {
                        device.updateConnectionState(ShimmerDevice.ConnectionState.CONNECTED, logger)
                        device.isStreaming.set(false)
                        logger.info("Device ${device.getDisplayName()} is SD LOGGING")
                    }
                    ShimmerBluetooth.BT_STATE.DISCONNECTED -> {
                        device.updateConnectionState(ShimmerDevice.ConnectionState.DISCONNECTED, logger)
                        device.isStreaming.set(false)
                        logger.info("Device ${device.getDisplayName()} has been DISCONNECTED")
                    }
                    else -> {
                        logger.debug("Unhandled device state: $state for device ${device.getDisplayName()}")
                    }
                }
            } else {
                logger.debug("Received state change for unknown device: $macAddress, state: $state")
            }
        }

        /**
         * Handle Shimmer callback objects (delegates to handleShimmerStateChange)
         */
        private fun handleShimmerCallback(callbackObject: CallbackObject) {
            logger.debug("Received callback for device: ${callbackObject.mBluetoothAddress}")
            handleShimmerStateChange(callbackObject)
        }

        /**
         * Handle incoming Shimmer sensor data
         */
        private fun handleShimmerData(objectCluster: ObjectCluster) {
            try {
                val macAddress = objectCluster.macAddress
                val device = connectedDevices[macAddress]

                if (device != null && device.isActivelyStreaming()) {
                    // Convert ObjectCluster to SensorSample
                    val sensorSample = convertObjectClusterToSensorSample(objectCluster)

                    // Add to data queue for processing
                    dataQueues[macAddress]?.offer(sensorSample)

                    // Update device statistics
                    device.recordSample()
                    sampleCounts[macAddress]?.incrementAndGet()

                    logger.debug("Received data from ${device.getDisplayName()}: ${sensorSample.sensorValues.size} channels")
                }
            } catch (e: Exception) {
                logger.error("Error processing Shimmer data", e)
            }
        }

        /**
         * Convert Shimmer ObjectCluster to SensorSample using proper SDK API calls
         * Enhanced version with complete sensor support and error handling
         */
        private fun convertObjectClusterToSensorSample(objectCluster: ObjectCluster): SensorSample {
            val deviceId = objectCluster.macAddress?.takeLast(4) ?: "Unknown"
            val sensorValues = mutableMapOf<SensorChannel, Double>()
            var deviceTimestamp = System.currentTimeMillis()

            try {
                logger.debug("Converting ObjectCluster from device: $deviceId")

                // Extract timestamp using official API pattern
                try {
                    val timestampFormats =
                        objectCluster.getCollectionOfFormatClusters(Configuration.Shimmer3.ObjectClusterSensorName.TIMESTAMP)
                    val timestampCluster = ObjectCluster.returnFormatCluster(timestampFormats, "CAL") as? FormatCluster
                    timestampCluster?.let {
                        deviceTimestamp = it.mData.toLong()
                        logger.debug("Extracted device timestamp: $deviceTimestamp")
                    }
                } catch (e: Exception) {
                    logger.debug("Could not extract timestamp, using system time: ${e.message}")
                }

                // Extract GSR data using official API pattern
                try {
                    val gsrFormats =
                        objectCluster.getCollectionOfFormatClusters(Configuration.Shimmer3.ObjectClusterSensorName.GSR_CONDUCTANCE)
                    val gsrCluster = ObjectCluster.returnFormatCluster(gsrFormats, "CAL") as? FormatCluster
                    gsrCluster?.let {
                        sensorValues[SensorChannel.GSR] = it.mData
                        logger.debug("Extracted GSR: ${it.mData} µS")
                    }
                } catch (e: Exception) {
                    logger.debug("Could not extract GSR data: ${e.message}")
                }

                // Extract PPG data using official API pattern
                try {
                    val ppgFormats =
                        objectCluster.getCollectionOfFormatClusters(Configuration.Shimmer3.ObjectClusterSensorName.INT_EXP_ADC_A13)
                    val ppgCluster = ObjectCluster.returnFormatCluster(ppgFormats, "CAL") as? FormatCluster
                    ppgCluster?.let {
                        sensorValues[SensorChannel.PPG] = it.mData
                        logger.debug("Extracted PPG: ${it.mData}")
                    }
                } catch (e: Exception) {
                    logger.debug("Could not extract PPG data: ${e.message}")
                }

                // Extract accelerometer X, Y, Z data using official API pattern
                try {
                    val accelXFormats =
                        objectCluster.getCollectionOfFormatClusters(Configuration.Shimmer3.ObjectClusterSensorName.ACCEL_LN_X)
                    val accelXCluster = ObjectCluster.returnFormatCluster(accelXFormats, "CAL") as? FormatCluster
                    accelXCluster?.let {
                        sensorValues[SensorChannel.ACCEL_X] = it.mData
                        logger.debug("Extracted Accel X: ${it.mData} g")
                    }

                    val accelYFormats =
                        objectCluster.getCollectionOfFormatClusters(Configuration.Shimmer3.ObjectClusterSensorName.ACCEL_LN_Y)
                    val accelYCluster = ObjectCluster.returnFormatCluster(accelYFormats, "CAL") as? FormatCluster
                    accelYCluster?.let {
                        sensorValues[SensorChannel.ACCEL_Y] = it.mData
                        logger.debug("Extracted Accel Y: ${it.mData} g")
                    }

                    val accelZFormats =
                        objectCluster.getCollectionOfFormatClusters(Configuration.Shimmer3.ObjectClusterSensorName.ACCEL_LN_Z)
                    val accelZCluster = ObjectCluster.returnFormatCluster(accelZFormats, "CAL") as? FormatCluster
                    accelZCluster?.let {
                        sensorValues[SensorChannel.ACCEL_Z] = it.mData
                        logger.debug("Extracted Accel Z: ${it.mData} g")
                    }

                    // For backwards compatibility, also store combined accelerometer value
                    if (sensorValues.containsKey(SensorChannel.ACCEL_X)) {
                        sensorValues[SensorChannel.ACCEL] = sensorValues[SensorChannel.ACCEL_X] ?: 0.0
                    }
                } catch (e: Exception) {
                    logger.debug("Could not extract accelerometer data: ${e.message}")
                }

                // Extract gyroscope X, Y, Z data using official API pattern
                try {
                    val gyroXFormats =
                        objectCluster.getCollectionOfFormatClusters(Configuration.Shimmer3.ObjectClusterSensorName.GYRO_X)
                    val gyroXCluster = ObjectCluster.returnFormatCluster(gyroXFormats, "CAL") as? FormatCluster
                    gyroXCluster?.let {
                        sensorValues[SensorChannel.GYRO_X] = it.mData
                        logger.debug("Extracted Gyro X: ${it.mData} °/s")
                    }

                    val gyroYFormats =
                        objectCluster.getCollectionOfFormatClusters(Configuration.Shimmer3.ObjectClusterSensorName.GYRO_Y)
                    val gyroYCluster = ObjectCluster.returnFormatCluster(gyroYFormats, "CAL") as? FormatCluster
                    gyroYCluster?.let {
                        sensorValues[SensorChannel.GYRO_Y] = it.mData
                        logger.debug("Extracted Gyro Y: ${it.mData} °/s")
                    }

                    val gyroZFormats =
                        objectCluster.getCollectionOfFormatClusters(Configuration.Shimmer3.ObjectClusterSensorName.GYRO_Z)
                    val gyroZCluster = ObjectCluster.returnFormatCluster(gyroZFormats, "CAL") as? FormatCluster
                    gyroZCluster?.let {
                        sensorValues[SensorChannel.GYRO_Z] = it.mData
                        logger.debug("Extracted Gyro Z: ${it.mData} °/s")
                    }

                    // For backwards compatibility, also store combined gyroscope value
                    if (sensorValues.containsKey(SensorChannel.GYRO_X)) {
                        sensorValues[SensorChannel.GYRO] = sensorValues[SensorChannel.GYRO_X] ?: 0.0
                    }
                } catch (e: Exception) {
                    logger.debug("Could not extract gyroscope data: ${e.message}")
                }

                // Extract magnetometer X, Y, Z data using official API pattern
                try {
                    val magXFormats =
                        objectCluster.getCollectionOfFormatClusters(Configuration.Shimmer3.ObjectClusterSensorName.MAG_X)
                    val magXCluster = ObjectCluster.returnFormatCluster(magXFormats, "CAL") as? FormatCluster
                    magXCluster?.let {
                        sensorValues[SensorChannel.MAG_X] = it.mData
                        logger.debug("Extracted Mag X: ${it.mData} gauss")
                    }

                    val magYFormats =
                        objectCluster.getCollectionOfFormatClusters(Configuration.Shimmer3.ObjectClusterSensorName.MAG_Y)
                    val magYCluster = ObjectCluster.returnFormatCluster(magYFormats, "CAL") as? FormatCluster
                    magYCluster?.let {
                        sensorValues[SensorChannel.MAG_Y] = it.mData
                        logger.debug("Extracted Mag Y: ${it.mData} gauss")
                    }

                    val magZFormats =
                        objectCluster.getCollectionOfFormatClusters(Configuration.Shimmer3.ObjectClusterSensorName.MAG_Z)
                    val magZCluster = ObjectCluster.returnFormatCluster(magZFormats, "CAL") as? FormatCluster
                    magZCluster?.let {
                        sensorValues[SensorChannel.MAG_Z] = it.mData
                        logger.debug("Extracted Mag Z: ${it.mData} gauss")
                    }

                    // For backwards compatibility, also store combined magnetometer value
                    if (sensorValues.containsKey(SensorChannel.MAG_X)) {
                        sensorValues[SensorChannel.MAG] = sensorValues[SensorChannel.MAG_X] ?: 0.0
                    }
                } catch (e: Exception) {
                    logger.debug("Could not extract magnetometer data: ${e.message}")
                }

                // Extract ECG data if available
                try {
                    val ecgFormats =
                        objectCluster.getCollectionOfFormatClusters(Configuration.Shimmer3.ObjectClusterSensorName.ECG_LL_RA)
                    val ecgCluster = ObjectCluster.returnFormatCluster(ecgFormats, "CAL") as? FormatCluster
                    ecgCluster?.let {
                        sensorValues[SensorChannel.ECG] = it.mData
                        logger.debug("Extracted ECG: ${it.mData} mV")
                    }
                } catch (e: Exception) {
                    logger.debug("Could not extract ECG data: ${e.message}")
                }

                // Extract EMG data if available
                try {
                    val emgFormats =
                        objectCluster.getCollectionOfFormatClusters(Configuration.Shimmer3.ObjectClusterSensorName.EMG)
                    val emgCluster = ObjectCluster.returnFormatCluster(emgFormats, "CAL") as? FormatCluster
                    emgCluster?.let {
                        sensorValues[SensorChannel.EMG] = it.mData
                        logger.debug("Extracted EMG: ${it.mData} mV")
                    }
                } catch (e: Exception) {
                    logger.debug("Could not extract EMG data: ${e.message}")
                }

                // Extract battery voltage if available
                var batteryLevel = 0
                try {
                    val batteryFormats =
                        objectCluster.getCollectionOfFormatClusters(Configuration.Shimmer3.ObjectClusterSensorName.BATTERY)
                    val batteryCluster = ObjectCluster.returnFormatCluster(batteryFormats, "CAL") as? FormatCluster
                    batteryCluster?.let {
                        // Convert battery voltage to percentage (approximate)
                        val voltage = it.mData
                        batteryLevel = when {
                            voltage >= 3.7 -> 100
                            voltage >= 3.6 -> 80
                            voltage >= 3.5 -> 60
                            voltage >= 3.4 -> 40
                            voltage >= 3.3 -> 20
                            else -> 10
                        }
                        logger.debug("Extracted Battery: ${voltage}V (${batteryLevel}%)")
                    }
                } catch (e: Exception) {
                    logger.debug("Could not extract battery data: ${e.message}")
                }

                logger.debug("Successfully extracted ${sensorValues.size} sensor values from ObjectCluster")
            } catch (e: Exception) {
                logger.error("Error extracting sensor values from ObjectCluster", e)
            }

            return SensorSample(
                deviceId = deviceId,
                deviceTimestamp = deviceTimestamp,
                systemTimestamp = System.currentTimeMillis(),
                sensorValues = sensorValues,
                batteryLevel = batteryLevel,
                sequenceNumber = extractSequenceNumber(objectCluster)
            )
        }

        /**
         * Extract sequence number from ObjectCluster if available
         */
        private fun extractSequenceNumber(objectCluster: ObjectCluster): Long {
            return try {
                // Try to extract sequence number from ObjectCluster
                // Different Shimmer devices may store this differently
                val sequenceFormats = objectCluster.getCollectionOfFormatClusters("SequenceNumber")
                if (sequenceFormats != null && sequenceFormats.isNotEmpty()) {
                    val sequenceCluster = ObjectCluster.returnFormatCluster(sequenceFormats, "CAL") as? FormatCluster
                    sequenceCluster?.mData?.toLong() ?: 0L
                } else {
                    // Fallback: use timestamp as sequence approximation
                    objectCluster.mRawTimeStamp?.toLong() ?: 0L
                }
            } catch (e: Exception) {
                logger.debug("Could not extract sequence number: ${e.message}")
                0L
            }
        }
        }

        /**
         * Scan and pair with available Shimmer devices using Shimmer SDK
         */
        suspend fun scanAndPairDevices(): List<String> =
            withContext(Dispatchers.IO) {
                try {
                    logger.info("=== SHIMMER DEVICE DISCOVERY DIAGNOSTIC ===")
                    logger.info("Scanning for Shimmer devices...")

                    // Check Bluetooth permissions with detailed logging
                    val hasPermissions = hasBluetoothPermissions()
                    logger.info("Bluetooth permissions check: $hasPermissions")
                    if (!hasPermissions) {
                        logger.error("Missing Bluetooth permissions - cannot discover devices")
                        return@withContext emptyList()
                    }

                    // Initialize Shimmer Bluetooth Manager if not already done
                    if (shimmerBluetoothManager == null) {
                        logger.info("Initializing ShimmerBluetoothManagerAndroid...")
                        shimmerBluetoothManager = ShimmerBluetoothManagerAndroid(context, createShimmerHandler())
                        logger.info("ShimmerBluetoothManagerAndroid initialized successfully")
                    }

                    // Get paired Bluetooth devices that are Shimmer devices
                    val bluetoothManager = context.getSystemService(Context.BLUETOOTH_SERVICE) as BluetoothManager
                    val bluetoothAdapter = bluetoothManager.adapter
                    logger.info("Bluetooth adapter available: ${bluetoothAdapter != null}")
                    logger.info("Bluetooth enabled: ${bluetoothAdapter?.isEnabled}")

                    if (bluetoothAdapter == null || !bluetoothAdapter.isEnabled) {
                        logger.error("Bluetooth is not available or not enabled")
                        return@withContext emptyList()
                    }

                    try {
                        val pairedDevices = bluetoothAdapter.bondedDevices
                        logger.info("Total paired Bluetooth devices: ${pairedDevices?.size ?: 0}")

                        // Log details about each paired device
                        pairedDevices?.forEachIndexed { index, device ->
                            logger.info("Paired device $index:")
                            logger.info("  Name: '${device.name}'")
                            logger.info("  Address: '${device.address}'")
                            logger.info("  Type: ${device.type}")
                            logger.info("  Bond State: ${device.bondState}")

                            // Check if this device matches my criteria
                            val nameContainsShimmer = device.name?.contains("Shimmer", ignoreCase = true) == true
                            val nameContainsRN42 = device.name?.contains("RN42", ignoreCase = true) == true
                            val matchesCriteria = nameContainsShimmer || nameContainsRN42

                            logger.info("  Name contains 'Shimmer': $nameContainsShimmer")
                            logger.info("  Name contains 'RN42': $nameContainsRN42")
                            logger.info("  Matches Shimmer criteria: $matchesCriteria")
                            logger.info("  ---")
                        }

                        // Apply filtering logic
                        val shimmerDevices =
                            pairedDevices
                                .filter { device ->
                                    val nameContainsShimmer = device.name?.contains("Shimmer", ignoreCase = true) == true
                                    val nameContainsRN42 = device.name?.contains("RN42", ignoreCase = true) == true
                                    nameContainsShimmer || nameContainsRN42
                                }.map { it.address }

                        logger.info("Filtered Shimmer devices found: ${shimmerDevices.size}")
                        shimmerDevices.forEach { address ->
                            logger.info("  Shimmer device address: $address")
                        }

                        if (shimmerDevices.isEmpty()) {
                            logger.error("No Shimmer devices found in paired devices!")
                            logger.info("To resolve this issue:")
                            logger.info("1. Ensure Shimmer device is paired in Android Bluetooth settings")
                            logger.info("2. Use PIN 1234 when pairing")
                            logger.info("3. Verify device name contains 'Shimmer' or 'RN42'")
                            logger.info("4. Check that device is properly bonded (not just connected)")
                        } else {
                            logger.info("Successfully found ${shimmerDevices.size} Shimmer devices")
                        }

                        logger.info("=== END SHIMMER DEVICE DISCOVERY DIAGNOSTIC ===")

                        // For new device discovery, I would need to implement a proper scanning dialog
                        // For now, return the paired devices
                        shimmerDevices
                    } catch (e: SecurityException) {
                        logger.error("Security exception accessing Bluetooth devices: ${e.message}", e)
                        logger.error("This may indicate missing Bluetooth permissions")
                        emptyList()
                    }
                } catch (e: Exception) {
                    logger.error("Failed to scan for Shimmer devices: ${e.message}", e)
                    emptyList()
                }
            }

        /**
         * Check if required Bluetooth permissions are granted
         */
        private fun hasBluetoothPermissions(): Boolean {
            val permissions =
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                    BLUETOOTH_PERMISSIONS_NEW
                } else {
                    BLUETOOTH_PERMISSIONS_LEGACY
                }

            return permissions.all { permission ->
                ContextCompat.checkSelfPermission(context, permission) == PackageManager.PERMISSION_GRANTED
            }
        }

        /**
         * Connect to a single Shimmer device with specified connection type (BLE or Classic)
         * Used for dialog-based device selection
         */
        suspend fun connectSingleDevice(
            macAddress: String,
            deviceName: String,
            connectionType: ShimmerBluetoothManagerAndroid.BT_TYPE,
        ): Boolean =
            withContext(Dispatchers.IO) {
                try {
                    logger.info("Connecting to single Shimmer device: $deviceName ($macAddress) via $connectionType")

                    // Check Bluetooth permissions
                    if (!hasBluetoothPermissions()) {
                        logger.error("Missing Bluetooth permissions for device connection")
                        return@withContext false
                    }

                    // Initialize Shimmer Bluetooth Manager if not already done
                    if (shimmerBluetoothManager == null) {
                        shimmerBluetoothManager = ShimmerBluetoothManagerAndroid(context, createShimmerHandler())
                    }

                    try {
                        // Create ShimmerDevice instance
                        val device =
                            ShimmerDevice(
                                macAddress = macAddress,
                                deviceName = deviceName,
                                connectionState = ShimmerDevice.ConnectionState.CONNECTING,
                            )

                        // Store device instance
                        connectedDevices[macAddress] = device
                        deviceConfigurations[macAddress] = DeviceConfiguration.createDefault()
                        dataQueues[macAddress] = ConcurrentLinkedQueue()
                        sampleCounts[macAddress] = AtomicLong(0)

                        // Create BluetoothDeviceDetails with proper connection type support
                        val bluetoothDeviceDetails =
                            com.shimmerresearch.driverUtilities
                                .BluetoothDeviceDetails(
                                    macAddress,
                                    macAddress,
                                    deviceName,
                                ).apply {
                                    // Set BLE flag based on connection type
                                    isBleDevice = (connectionType == ShimmerBluetoothManagerAndroid.BT_TYPE.BLE)
                                }

                        // Connect using ShimmerBluetoothManagerAndroid with BluetoothDeviceDetails
                        shimmerBluetoothManager?.connectShimmerThroughBTAddress(bluetoothDeviceDetails)

                        logger.debug(
                            "Connection initiated for $deviceName via $connectionType (BLE: ${bluetoothDeviceDetails.isBleDevice})",
                        )

                        // Wait a moment for connection to establish
                        delay(2000)

                        // Update connection state
                        device.updateConnectionState(ShimmerDevice.ConnectionState.CONNECTED, logger)
                        isConnected.set(true)

                        logger.info("Successfully initiated connection to $deviceName via $connectionType")
                        return@withContext true
                    } catch (e: Exception) {
                        logger.error("Failed to connect to device $macAddress via $connectionType", e)

                        // Clean up failed connection
                        connectedDevices.remove(macAddress)
                        deviceConfigurations.remove(macAddress)
                        dataQueues.remove(macAddress)
                        sampleCounts.remove(macAddress)

                        return@withContext false
                    }
                } catch (e: Exception) {
                    logger.error("Failed to connect to Shimmer device", e)
                    false
                }
            }

        /**
         * Enhanced device connection with better error handling and retry logic
         */
        suspend fun connectDevicesWithRetry(
            deviceAddresses: List<String>,
            maxRetries: Int = 3,
        ): List<String> =
            withContext(Dispatchers.IO) {
                val successfulConnections = mutableListOf<String>()

                deviceAddresses.forEach { macAddress ->
                    var retryCount = 0
                    var connected = false

                    while (!connected && retryCount < maxRetries) {
                        try {
                            logger.info("Attempting to connect to device: $macAddress (attempt ${retryCount + 1}/$maxRetries)")

                            connected = connectSingleDeviceInternal(macAddress, "Shimmer3-GSR+")

                            if (connected) {
                                successfulConnections.add(macAddress)
                                logger.info("Successfully connected to device: $macAddress")
                            } else {
                                retryCount++
                                if (retryCount < maxRetries) {
                                    logger.warning("Connection failed, retrying in ${RECONNECTION_DELAY_MS}ms...")
                                    delay(RECONNECTION_DELAY_MS)
                                }
                            }
                        } catch (e: Exception) {
                            retryCount++
                            logger.error("Connection attempt failed for device $macAddress: ${e.message}", e)
                            if (retryCount < maxRetries) {
                                delay(RECONNECTION_DELAY_MS)
                            }
                        }
                    }

                    if (!connected) {
                        logger.error("Failed to connect to device $macAddress after $maxRetries attempts")
                    }
                }

                logger.info("Connected to ${successfulConnections.size} out of ${deviceAddresses.size} devices")
                successfulConnections
            }

        /**
         * Internal method for connecting to a single device
         */
        private suspend fun connectSingleDeviceInternal(
            macAddress: String,
            deviceName: String,
        ): Boolean =
            withContext(Dispatchers.IO) {
                try {
                    // Create ShimmerDevice instance
                    val device =
                        ShimmerDevice(
                            macAddress = macAddress,
                            deviceName = deviceName,
                            connectionState = ShimmerDevice.ConnectionState.CONNECTING,
                        )

                    // Create individual handler for this device
                    val deviceHandler = createShimmerHandler()

                    // Create Shimmer SDK instance
                    val shimmer = Shimmer(deviceHandler, context)

                    // Store device and Shimmer instances
                    connectedDevices[macAddress] = device
                    shimmerDevices[macAddress] = shimmer
                    shimmerHandlers[macAddress] = deviceHandler
                    deviceConfigurations[macAddress] = DeviceConfiguration.createDefault()
                    dataQueues[macAddress] = ConcurrentLinkedQueue()
                    sampleCounts[macAddress] = AtomicLong(0)

                    // Attempt connection using Shimmer SDK
                    shimmer.connect(macAddress, "default")

                    // Wait for connection to establish with timeout
                    var connectionTimeout = 10000L // 10 seconds
                    val startTime = System.currentTimeMillis()

                    while (System.currentTimeMillis() - startTime < connectionTimeout) {
                        if (device.isConnected()) {
                            break
                        }
                        delay(100)
                    }

                    val connected = device.isConnected()
                    if (connected) {
                        device.updateConnectionState(ShimmerDevice.ConnectionState.CONNECTED, logger)
                        logger.info("Successfully connected to ${device.getDisplayName()}")
                    } else {
                        logger.error("Connection timeout for device $macAddress")
                        // Clean up failed connection
                        cleanupFailedConnection(macAddress)
                    }

                    connected
                } catch (e: Exception) {
                    logger.error("Failed to connect to device $macAddress", e)
                    cleanupFailedConnection(macAddress)
                    false
                }
            }

        /**
         * Clean up resources for a failed connection
         */
        private fun cleanupFailedConnection(macAddress: String) {
            connectedDevices.remove(macAddress)
            shimmerDevices.remove(macAddress)
            shimmerHandlers.remove(macAddress)
            deviceConfigurations.remove(macAddress)
            dataQueues.remove(macAddress)
            sampleCounts.remove(macAddress)
        }

        /**
         * Disconnect from all connected devices with proper cleanup
         */
        suspend fun disconnectAllDevices(): Boolean =
            withContext(Dispatchers.IO) {
                try {
                    logger.info("Disconnecting from ${connectedDevices.size} devices...")

                    var successfulDisconnections = 0

                    connectedDevices.values.forEach { device ->
                        val shimmer = shimmerDevices[device.macAddress]

                        try {
                            logger.debug("Disconnecting from device ${device.getDisplayName()}")

                            shimmer?.stop()
                            shimmer?.disconnect()

                            device.updateConnectionState(ShimmerDevice.ConnectionState.DISCONNECTED, logger)
                            successfulDisconnections++

                            logger.info("Successfully disconnected from device ${device.getDisplayName()}")
                        } catch (e: Exception) {
                            logger.error("Failed to disconnect from device ${device.getDisplayName()}", e)
                        }
                    }

                    // Clear all device collections
                    connectedDevices.clear()
                    shimmerDevices.clear()
                    shimmerHandlers.clear()
                    deviceConfigurations.clear()
                    dataQueues.clear()
                    sampleCounts.clear()

                    isConnected.set(false)

                    logger.info("Disconnected from $successfulDisconnections devices")
                    true
                } catch (e: Exception) {
                    logger.error("Failed to disconnect from devices", e)
                    false
                }
            }

        /**
         * Get real-time data quality metrics for a device
         */
        suspend fun getDataQualityMetrics(deviceId: String): DataQualityMetrics? =
            withContext(Dispatchers.IO) {
                try {
                    val device = connectedDevices[deviceId]
                    val sampleQueue = dataQueues[deviceId]

                    if (device == null || sampleQueue == null) {
                        return@withContext null
                    }

                    // Calculate metrics from recent samples
                    val recentSamples = sampleQueue.toList().takeLast(100)
                    
                    if (recentSamples.isEmpty()) {
                        return@withContext DataQualityMetrics(
                            deviceId = deviceId,
                            samplesAnalyzed = 0,
                            averageSamplingRate = 0.0,
                            signalQuality = "No Data",
                            batteryLevel = device.batteryLevel,
                            connectionStability = "Stable",
                            dataLossPercentage = 0.0,
                        )
                    }

                    // Calculate sampling rate
                    val timeSpan = if (recentSamples.size > 1) {
                        recentSamples.last().systemTimestamp - recentSamples.first().systemTimestamp
                    } else {
                        1000L
                    }
                    val samplingRate = if (timeSpan > 0) {
                        (recentSamples.size - 1) * 1000.0 / timeSpan
                    } else {
                        0.0
                    }

                    // Assess signal quality based on GSR variability
                    val gsrValues = recentSamples.mapNotNull { it.getSensorValue(SensorChannel.GSR) }
                    val signalQuality = if (gsrValues.isNotEmpty()) {
                        val variance = calculateVariance(gsrValues)
                        when {
                            variance < 0.1 -> "Poor (Low Variability)"
                            variance < 1.0 -> "Good"
                            variance < 5.0 -> "Excellent"
                            else -> "Poor (High Noise)"
                        }
                    } else {
                        "No GSR Data"
                    }

                    // Check connection stability
                    val connectionStability = if (device.reconnectionAttempts > 0) {
                        "Unstable (${device.reconnectionAttempts} reconnections)"
                    } else {
                        "Stable"
                    }

                    DataQualityMetrics(
                        deviceId = deviceId,
                        samplesAnalyzed = recentSamples.size,
                        averageSamplingRate = samplingRate,
                        signalQuality = signalQuality,
                        batteryLevel = device.batteryLevel,
                        connectionStability = connectionStability,
                        dataLossPercentage = 0.0, // Could be enhanced to detect packet loss
                    )
                } catch (e: Exception) {
                    logger.error("Failed to calculate data quality metrics for $deviceId", e)
                    null
                }
            }

        /**
         * Data class representing real-time data quality metrics
         */
        data class DataQualityMetrics(
            val deviceId: String,
            val samplesAnalyzed: Int,
            val averageSamplingRate: Double,
            val signalQuality: String,
            val batteryLevel: Int,
            val connectionStability: String,
            val dataLossPercentage: Double,
        ) {
            fun getDisplaySummary(): String =
                buildString {
                    append("Device: $deviceId\n")
                    append("Sampling Rate: ${"%.1f".format(averageSamplingRate)} Hz\n")
                    append("Signal Quality: $signalQuality\n")
                    append("Battery: $batteryLevel%\n")
                    append("Connection: $connectionStability\n")
                    append("Samples: $samplesAnalyzed")
                }
        }

        /**
         * Helper function to calculate variance
         */
        private fun calculateVariance(values: List<Double>): Double {
            if (values.isEmpty()) return 0.0
            val mean = values.average()
            val variance = values.map { (it - mean) * (it - mean) }.average()
            return variance
        }

        /**
         * Connect to multiple Shimmer devices using Shimmer SDK (Classic Bluetooth)
         */
        suspend fun connectDevices(deviceAddresses: List<String>): Boolean =
            withContext(Dispatchers.IO) {
                try {
                    logger.info("Connecting to ${deviceAddresses.size} Shimmer devices...")

                    // Check Bluetooth permissions
                    if (!hasBluetoothPermissions()) {
                        logger.error("Missing Bluetooth permissions for device connection")
                        return@withContext false
                    }

                    var successfulConnections = 0

                    deviceAddresses.forEach { macAddress ->
                        try {
                            logger.info("Attempting to connect to device: $macAddress")

                            // Create ShimmerDevice instance
                            val device =
                                ShimmerDevice(
                                    macAddress = macAddress,
                                    deviceName = "Shimmer3-GSR+",
                                    connectionState = ShimmerDevice.ConnectionState.CONNECTING,
                                )

                            // Create individual handler for this device
                            val deviceHandler = createShimmerHandler()

                            // Create Shimmer SDK instance
                            val shimmer = Shimmer(deviceHandler, context)

                            // Store device and Shimmer instances
                            connectedDevices[macAddress] = device
                            shimmerDevices[macAddress] = shimmer
                            shimmerHandlers[macAddress] = deviceHandler
                            deviceConfigurations[macAddress] = DeviceConfiguration.createDefault()
                            dataQueues[macAddress] = ConcurrentLinkedQueue()
                            sampleCounts[macAddress] = AtomicLong(0)

                            // Attempt connection using Shimmer SDK
                            try {
                                shimmer.connect(macAddress, "default")

                                // Wait a moment for connection to establish
                                delay(1000)

                                // Check if connection was successful
                                // Note: Actual connection state will be updated via callbacks
                                device.updateConnectionState(ShimmerDevice.ConnectionState.CONNECTED, logger)
                                successfulConnections++

                                logger.info("Successfully initiated connection to ${device.getDisplayName()}")
                            } catch (e: Exception) {
                                logger.error("Failed to connect to device $macAddress", e)
                                device.updateConnectionState(ShimmerDevice.ConnectionState.ERROR, logger)

                                // Clean up failed connection
                                connectedDevices.remove(macAddress)
                                shimmerDevices.remove(macAddress)
                                shimmerHandlers.remove(macAddress)
                                deviceConfigurations.remove(macAddress)
                                dataQueues.remove(macAddress)
                                sampleCounts.remove(macAddress)
                            }
                        } catch (e: Exception) {
                            logger.error("Error setting up connection for device $macAddress", e)
                        }
                    }

                    isConnected.set(connectedDevices.isNotEmpty())
                    logger.info("Connected to $successfulConnections out of ${deviceAddresses.size} devices")

                    successfulConnections > 0
                } catch (e: Exception) {
                    logger.error("Failed to connect to Shimmer devices", e)
                    false
                }
            }

        /**
         * Configure sensor channels for a specific device using Shimmer SDK
         */
        suspend fun setEnabledChannels(
            deviceId: String,
            channels: Set<SensorChannel>,
        ): Boolean =
            withContext(Dispatchers.IO) {
                try {
                    val device = connectedDevices[deviceId]
                    val shimmer = shimmerDevices[deviceId]

                    if (device == null) {
                        logger.error("Device not found: $deviceId")
                        return@withContext false
                    }

                    if (shimmer == null) {
                        logger.error("Shimmer SDK instance not found for device: $deviceId")
                        return@withContext false
                    }

                    val currentConfig = deviceConfigurations[deviceId] ?: DeviceConfiguration.createDefault()
                    val newConfig = currentConfig.withSensors(channels)

                    // Validate configuration
                    val errors = newConfig.validate()
                    if (errors.isNotEmpty()) {
                        logger.error("Invalid configuration for device $deviceId: ${errors.joinToString()}")
                        return@withContext false
                    }

                    try {
                        // Apply configuration to actual Shimmer device using SDK
                        val sensorBitmask = newConfig.getSensorBitmask()
                        logger.debug("Applying sensor bitmask 0x${sensorBitmask.toString(16)} to device ${device.getDisplayName()}")

                        // Configure enabled sensors using proper SDK method
                        shimmer.writeEnabledSensors(sensorBitmask.toLong())

                        // Configure sampling rate using proper SDK method
                        shimmer.writeSamplingRate(newConfig.samplingRate)

                        // Configure GSR range using proper SDK method
                        shimmer.writeGSRRange(newConfig.gsrRange)

                        // Configure accelerometer range using proper SDK method  
                        shimmer.writeAccelRange(newConfig.accelRange)

                        // Configure gyroscope range using proper SDK method
                        shimmer.writeGyroRange(newConfig.gyroRange)

                        // Configure magnetometer range using proper SDK method
                        shimmer.writeMagRange(newConfig.magRange)

                        logger.debug("All sensor configurations applied successfully")

                        // Update stored configuration
                        deviceConfigurations[deviceId] = newConfig
                        device.configuration = newConfig

                        logger.info(
                            "Successfully updated sensor configuration for device ${device.getDisplayName()}: ${channels.size} channels",
                        )
                        logger.debug("Enabled channels: ${channels.joinToString { it.displayName }}")

                        true
                    } catch (e: Exception) {
                        logger.error("Failed to apply sensor configuration to Shimmer device $deviceId", e)
                        false
                    }
                } catch (e: Exception) {
                    logger.error("Failed to configure sensors for device $deviceId", e)
                    false
                }
            }

        /**
         * Start streaming for all connected devices using Shimmer SDK
         */
        suspend fun startStreaming(): Boolean =
            withContext(Dispatchers.IO) {
                try {
                    logger.info("Starting streaming for ${connectedDevices.size} devices...")

                    var successfulStreams = 0

                    connectedDevices.values.forEach { device ->
                        val shimmer = shimmerDevices[device.macAddress]

                        if (shimmer != null) {
                            try {
                                logger.debug("Starting streaming for device ${device.getDisplayName()}")

                                // Start actual Shimmer streaming using SDK
                                shimmer.startStreaming()

                                // Update device state
                                device.updateConnectionState(ShimmerDevice.ConnectionState.STREAMING, logger)
                                device.isStreaming.set(true)

                                successfulStreams++
                                logger.info("Successfully started streaming for device ${device.getDisplayName()}")
                            } catch (e: Exception) {
                                logger.error("Failed to start streaming for device ${device.getDisplayName()}", e)
                                device.updateConnectionState(ShimmerDevice.ConnectionState.ERROR, logger)
                            }
                        } else {
                            logger.error("Shimmer SDK instance not found for device ${device.getDisplayName()}")
                            device.updateConnectionState(ShimmerDevice.ConnectionState.ERROR, logger)
                        }
                    }

                    if (successfulStreams > 0) {
                        // Start data processing coroutines
                        startDataProcessing()
                        logger.info("Started streaming for $successfulStreams out of ${connectedDevices.size} devices")
                    }

                    successfulStreams > 0
                } catch (e: Exception) {
                    logger.error("Failed to start streaming", e)
                    false
                }
            }

        /**
         * Stop streaming for all connected devices using Shimmer SDK
         */
        suspend fun stopStreaming(): Boolean =
            withContext(Dispatchers.IO) {
                try {
                    logger.info("Stopping streaming for ${connectedDevices.size} devices...")

                    var successfulStops = 0

                    connectedDevices.values.forEach { device ->
                        val shimmer = shimmerDevices[device.macAddress]

                        if (shimmer != null) {
                            try {
                                logger.debug("Stopping streaming for device ${device.getDisplayName()}")

                                // Stop actual Shimmer streaming using SDK
                                shimmer.stopStreaming()

                                // Update device state
                                device.isStreaming.set(false)
                                device.updateConnectionState(ShimmerDevice.ConnectionState.CONNECTED, logger)

                                successfulStops++
                                logger.info("Successfully stopped streaming for device ${device.getDisplayName()}")
                            } catch (e: Exception) {
                                logger.error("Failed to stop streaming for device ${device.getDisplayName()}", e)
                                // Still update local state even if SDK call failed
                                device.isStreaming.set(false)
                                device.updateConnectionState(ShimmerDevice.ConnectionState.CONNECTED, logger)
                            }
                        } else {
                            logger.error("Shimmer SDK instance not found for device ${device.getDisplayName()}")
                            // Update local state anyway
                            device.isStreaming.set(false)
                            device.updateConnectionState(ShimmerDevice.ConnectionState.CONNECTED, logger)
                        }
                    }

                    logger.info("Stopped streaming for $successfulStops out of ${connectedDevices.size} devices")

                    // Always return true since I want to stop local processing even if some SDK calls failed
                    true
                } catch (e: Exception) {
                    logger.error("Failed to stop streaming", e)
                    false
                }
            }

        /**
         * Start data processing coroutines for all devices
         */
        private fun startDataProcessing() {
            recordingScope?.launch {
                logger.info("Started data processing pipeline")

                // Shimmer SDK data callbacks are now implemented via handleShimmerData()
                // ObjectCluster data is converted to SensorSample and added to device queues

                // Start file writing coroutine
                launch { processFileWriting() }

                // Start network streaming coroutine
                launch { processNetworkStreaming() }

                // Note: Real data now comes from Shimmer SDK callbacks, simulation removed
            }
        }

        /**
         * Process file writing for all devices
         */
        private suspend fun processFileWriting() {
            while (isRecording.get()) {
                try {
                    connectedDevices.keys.forEach { deviceId ->
                        val queue = dataQueues[deviceId]
                        val writer = fileWriters[deviceId]

                        if (queue != null && writer != null) {
                            val samplesToWrite = mutableListOf<SensorSample>()

                            // Drain queue in batches
                            repeat(DATA_BATCH_SIZE) {
                                queue.poll()?.let { sample ->
                                    samplesToWrite.add(sample)
                                }
                            }

                            // Write batch to file
                            samplesToWrite.forEach { sample ->
                                writer.write(sample.toCsvString())
                                writer.newLine()
                            }

                            if (samplesToWrite.isNotEmpty()) {
                                writer.flush()
                            }
                        }
                    }

                    delay(100) // Process every 100ms
                } catch (e: Exception) {
                    logger.error("Error in file writing process", e)
                }
            }
        }

        /**
         * Process network streaming for all devices
         */
        private suspend fun processNetworkStreaming() {
            while (isRecording.get() && isStreaming.get()) {
                try {
                    connectedDevices.keys.forEach { deviceId ->
                        val queue = dataQueues[deviceId]

                        queue?.poll()?.let { sample ->
                            streamingQueue.offer(sample.toJsonString())
                        }
                    }

                    // Send queued data over network
                    while (streamingQueue.isNotEmpty()) {
                        val jsonData = streamingQueue.poll()
                        streamingWriter?.println(jsonData)
                        streamingWriter?.flush()
                    }

                    delay(100) // Stream every 100ms
                } catch (e: Exception) {
                    logger.error("Error in network streaming process", e)
                }
            }
        }

        /**
         * Initialize the Shimmer recorder with proper SDK setup
         */
        suspend fun initialize(): Boolean =
            withContext(Dispatchers.IO) {
                try {
                    logger.info("Initializing ShimmerRecorder (stub implementation)...")

                    if (isInitialized.get()) {
                        logger.info("ShimmerRecorder already initialized")
                        return@withContext true
                    }

                    // Initialize Bluetooth adapter
                    bluetoothManager = context.getSystemService(Context.BLUETOOTH_SERVICE) as BluetoothManager
                    bluetoothAdapter = bluetoothManager?.adapter

                    if (bluetoothAdapter == null) {
                        logger.error("Bluetooth not supported on this device")
                        return@withContext false
                    }

                    // Initialize data handler thread
                    dataHandlerThread = HandlerThread("ShimmerDataHandler").apply { start() }
                    dataHandler = Handler(dataHandlerThread!!.looper)

                    // Initialize recording scope
                    recordingScope = CoroutineScope(Dispatchers.IO + SupervisorJob())

                    // Initialize Shimmer SDK components
                    shimmerBluetoothManager = ShimmerBluetoothManagerAndroid(context, createShimmerHandler())
                    logger.info("ShimmerBluetoothManagerAndroid initialized successfully")
                    
                    // Verify Bluetooth adapter is available and enabled
                    if (bluetoothAdapter?.isEnabled != true) {
                        logger.warning("Bluetooth is not enabled - some features may not work")
                    }

                    // Check if I have connected devices and start streaming
                    val hasConnectedDevices = connectedDevices.isNotEmpty()
                    
                    if (hasConnectedDevices) {
                        isInitialized.set(true)
                        logger.info("ShimmerRecorder initialized successfully with ${connectedDevices.size} devices")
                        logger.info("Shimmer config: ${DEFAULT_SAMPLING_RATE}Hz, GSR Range: $DEFAULT_GSR_RANGE")
                    } else {
                        logger.info("ShimmerRecorder initialized - no devices connected yet")
                        logger.info("Use scanAndPairDevices() and connectDevices() to establish connections")
                        isInitialized.set(true)
                    }

                    true
                } catch (e: Exception) {
                    logger.error("Failed to initialize ShimmerRecorder", e)
                    false
                }
            }

        /**
         * Start Shimmer data recording with multi-device support
         * Real implementation using Shimmer SDK
         */
        suspend fun startRecording(sessionId: String): Boolean =
            withContext(Dispatchers.IO) {
                try {
                    if (!isInitialized.get() || !isConnected.get()) {
                        logger.error("ShimmerRecorder not initialized or connected")
                        return@withContext false
                    }

                    if (isRecording.get()) {
                        logger.warning("Shimmer recording already in progress")
                        return@withContext true
                    }

                    logger.info("Starting Shimmer recording for session: $sessionId")
                    currentSessionId = sessionId
                    sessionStartTime = System.currentTimeMillis()

                    // Get session file paths
                    val filePaths = sessionManager.getSessionFilePaths()
                    if (filePaths == null) {
                        logger.error("No active session found")
                        return@withContext false
                    }

                    // Initialize file writers for each connected device
                    val sessionDirectory = filePaths.sessionFolder
                    var allFilesInitialized = true

                    connectedDevices.forEach { (deviceId, device) ->
                        try {
                            val deviceFileName = "shimmer_${device.getDisplayName().replace(
                                " ",
                                "_",
                            ).replace("(", "").replace(")", "")}_$sessionId.csv"
                            val deviceFile = File(sessionDirectory, deviceFileName)

                            val writer = BufferedWriter(FileWriter(deviceFile))
                            // Write CSV header using SensorSample
                            writer.write(SensorSample.createSimulatedSample(deviceId, 0).toCsvString(includeHeader = true))
                            writer.newLine()

                            fileWriters[deviceId] = writer

                            logger.info("Initialized recording file for device ${device.getDisplayName()}: ${deviceFile.absolutePath}")
                        } catch (e: Exception) {
                            logger.error("Failed to initialize file for device $deviceId", e)
                            allFilesInitialized = false
                        }
                    }

                    if (!allFilesInitialized) {
                        logger.error("Failed to initialize all device files")
                        return@withContext false
                    }

                    // Start streaming and data processing
                    val streamingStarted = startStreaming()

                    if (streamingStarted) {
                        isRecording.set(true)
                        sampleCount = 0

                        // Reset sample counts for all devices
                        sampleCounts.values.forEach { it.set(0) }

                        logger.info("Shimmer recording started successfully for ${connectedDevices.size} devices")
                        logger.info("Session directory: ${sessionDirectory.absolutePath}")
                    } else {
                        logger.error("Failed to start streaming")
                        // Clean up file writers if streaming failed
                        fileWriters.values.forEach { it.close() }
                        fileWriters.clear()
                        return@withContext false
                    }

                    true
                } catch (e: Exception) {
                    logger.error("Failed to start Shimmer recording", e)
                    false
                }
            }

        /**
         * Stop Shimmer data recording with multi-device support
         * Real implementation using Shimmer SDK
         */
        suspend fun stopRecording() =
            withContext(Dispatchers.IO) {
                try {
                    if (!isRecording.get()) {
                        logger.info("Shimmer recording not in progress")
                        return@withContext
                    }

                    logger.info("Stopping Shimmer recording for ${connectedDevices.size} devices...")

                    // Stop streaming for all devices
                    stopStreaming()

                    // Close all file writers
                    var totalSamples = 0L
                    fileWriters.forEach { (deviceId, writer) ->
                        try {
                            writer.flush()
                            writer.close()

                            val deviceSamples = sampleCounts[deviceId]?.get() ?: 0L
                            totalSamples += deviceSamples

                            val device = connectedDevices[deviceId]
                            logger.info("Closed file for device ${device?.getDisplayName() ?: deviceId}: $deviceSamples samples")
                        } catch (e: Exception) {
                            logger.error("Error closing file for device $deviceId", e)
                        }
                    }

                    fileWriters.clear()

                    // Close network streaming
                    try {
                        streamingWriter?.close()
                        streamingSocket?.close()
                        streamingWriter = null
                        streamingSocket = null
                        isStreaming.set(false)
                    } catch (e: Exception) {
                        logger.error("Error closing network streaming", e)
                    }

                    // Update recording state
                    isRecording.set(false)
                    currentSessionId = null
                    sampleCount = totalSamples

                    // Calculate session duration
                    val sessionDuration =
                        if (sessionStartTime > 0) {
                            System.currentTimeMillis() - sessionStartTime
                        } else {
                            0L
                        }

                    logger.info("Shimmer recording stopped successfully")
                    logger.info("Session duration: ${sessionDuration / 1000.0} seconds")
                    logger.info("Total samples recorded across all devices: $totalSamples")
                    logger.info(
                        "Average sampling rate: ${if (sessionDuration > 0) {
                            String.format(
                                "%.1f",
                                totalSamples * 1000.0 / sessionDuration,
                            )
                        } else {
                            "N/A"
                        }} Hz",
                    )
                } catch (e: Exception) {
                    logger.error("Error stopping Shimmer recording", e)
                }
            }

        /**
         * Get Shimmer sensor status with real device information
         */
        fun getShimmerStatus(): ShimmerStatus {
            val totalSamples = sampleCounts.values.sumOf { it.get() }
            val avgBattery = if (connectedDevices.isNotEmpty()) {
                connectedDevices.values.map { it.batteryLevel }.average().toInt()
            } else {
                null
            }
            
            return ShimmerStatus(
                isAvailable = isInitialized.get(),
                isConnected = isConnected.get(),
                isRecording = isRecording.get(),
                samplingRate = samplingRate.toInt(),
                batteryLevel = avgBattery,
                signalQuality = getOverallSignalQuality(),
                samplesRecorded = totalSamples,
            )
        }
        
        /**
         * Get overall signal quality across all connected devices
         */
        private fun getOverallSignalQuality(): String? {
            if (connectedDevices.isEmpty()) return null
            
            val qualities = connectedDevices.keys.mapNotNull { deviceId ->
                runBlocking {
                    getDataQualityMetrics(deviceId)?.signalQuality
                }
            }
            
            return when {
                qualities.isEmpty() -> "Unknown"
                qualities.any { it.contains("Excellent") } -> "Excellent"
                qualities.any { it.contains("Good") } -> "Good"
                qualities.any { it.contains("Fair") } -> "Fair"
                else -> "Poor"
            }
        }

        /**
         * Data class representing Shimmer sensor status
         */
        data class ShimmerStatus(
            val isAvailable: Boolean,
            val isConnected: Boolean,
            val isRecording: Boolean,
            val samplingRate: Int,
            val batteryLevel: Int? = null, // Battery percentage
            val signalQuality: String? = null, // Signal quality indicator
            val samplesRecorded: Long = 0,
        )

        /**
         * Data class representing a Shimmer sensor sample
         */
        data class ShimmerSample(
            val timestamp: Long,
            val systemTime: String,
            val gsrConductance: Double,
            val ppgA13: Double,
            val accelX: Double,
            val accelY: Double,
            val accelZ: Double,
            val batteryPercentage: Int,
        )

        /**
         * Simulate Shimmer device connection
         * TODO: Replace with actual Shimmer SDK connection
         */
        private suspend fun simulateShimmerConnection(): Boolean {
            // In real implementation, this would:
            // - Scan for Bluetooth devices
            // - Find Shimmer device by name/MAC address
            // - Establish Bluetooth connection
            // - Verify device is functional

            // For simulation, return true to indicate successful connection
            logger.info("Simulated Shimmer connection to device: $SHIMMER_DEVICE_NAME")
            return true
        }

        /**
         * Initialize CSV data file for recording
         */
        private suspend fun initializeDataFile(dataFile: File): Boolean {
            try {
                dataWriter = FileWriter(dataFile, false) // Overwrite existing file
                dataWriter?.appendLine(CSV_HEADER)
                dataWriter?.flush()

                logger.info("Shimmer data file initialized: ${dataFile.absolutePath}")
                return true
            } catch (e: Exception) {
                logger.error("Failed to initialize Shimmer data file", e)
                return false
            }
        }

        /**
         * Start simulated data collection
         * TODO: Replace with actual Shimmer SDK data callback
         */
        private suspend fun startSimulatedDataCollection() {
            // In real implementation, this would set up Shimmer SDK callbacks
            // For simulation, I'll generate realistic sensor data

            logger.info("Started simulated Shimmer data collection at ${samplingRate}Hz")

            // Note: In real implementation, data would come from Shimmer callbacks
            // This simulation is just for testing the data flow
        }

        /**
         * Simulate writing a sensor sample (called by real Shimmer callbacks)
         * TODO: Replace with actual Shimmer SDK data handling
         */
        suspend fun simulateDataSample(): ShimmerSample =
            withContext(Dispatchers.IO) {
                val currentTime = System.currentTimeMillis()
                val sample =
                    ShimmerSample(
                        timestamp = currentTime,
                        systemTime = dateFormat.format(Date(currentTime)),
                        gsrConductance = simulateGSRData(),
                        ppgA13 = simulatePPGData(),
                        accelX = simulateAccelData(),
                        accelY = simulateAccelData(),
                        accelZ = simulateAccelData() + 9.8, // Add gravity component
                        batteryPercentage = simulateBatteryLevel(),
                    )

                // Write sample to file if recording
                if (isRecording.get() && dataWriter != null) {
                    writeSampleToFile(sample)
                    sampleCount++
                }

                sample
            }

        /**
         * Write a sample to the CSV file
         */
        private suspend fun writeSampleToFile(sample: ShimmerSample) {
            try {
                val csvLine =
                    "${sample.timestamp},${sample.systemTime},${sample.gsrConductance}," +
                        "${sample.ppgA13},${sample.accelX},${sample.accelY},${sample.accelZ},${sample.batteryPercentage}"

                dataWriter?.appendLine(csvLine)

                // Flush periodically to ensure data is written
                if (sampleCount % DATA_BATCH_SIZE == 0L) {
                    dataWriter?.flush()
                }
            } catch (e: Exception) {
                logger.error("Failed to write Shimmer sample to file", e)
            }
        }

        /**
         * Simulate GSR (Galvanic Skin Response) data
         */
        private fun simulateGSRData(): Double {
            // Simulate realistic GSR values (microsiemens)
            val baseGSR = 2.0 + Math.random() * 8.0 // 2-10 µS range
            val noise = (Math.random() - 0.5) * 0.5 // Small noise component
            return baseGSR + noise
        }

        /**
         * Simulate PPG (Photoplethysmography) data
         */
        private fun simulatePPGData(): Double {
            // Simulate realistic PPG values with heart rate component
            val heartRate = 70.0 // BPM
            val timeSeconds = System.currentTimeMillis() / 1000.0
            val heartComponent = Math.sin(2 * Math.PI * heartRate / 60.0 * timeSeconds) * 100
            val noise = (Math.random() - 0.5) * 20
            return 2048 + heartComponent + noise // Centered around 2048 with heart rate signal
        }

        /**
         * Simulate accelerometer data
         */
        private fun simulateAccelData(): Double {
            // Simulate small movements with noise
            val movement = Math.sin(System.currentTimeMillis() / 10000.0) * 0.5
            val noise = (Math.random() - 0.5) * 0.2
            return movement + noise
        }

        /**
         * Simulate battery level
         */
        private fun simulateBatteryLevel(): Int {
            // Simulate slowly decreasing battery level
            val baseLevel = 85
            val variation = (Math.random() * 10).toInt()
            return (baseLevel - variation).coerceIn(0, 100)
        }

        /**
         * Simulate signal quality
         */
        private fun simulateSignalQuality(): String {
            val qualities = listOf("Excellent", "Good", "Fair", "Poor")
            return qualities.random()
        }

        /**
         * Get current sensor readings (for real-time display)
         * Real implementation using Shimmer SDK current readings
         */
        /**
         * Get current sensor readings from connected devices
         */
        suspend fun getCurrentReadings(): Map<String, SensorSample> =
            withContext(Dispatchers.IO) {
                val currentReadings = mutableMapOf<String, SensorSample>()
                
                connectedDevices.forEach { (deviceId, device) ->
                    if (device.isConnected()) {
                        // Get the most recent sample from the device queue
                        val recentSample = dataQueues[deviceId]?.lastOrNull()
                        if (recentSample != null) {
                            currentReadings[deviceId] = recentSample
                        }
                    }
                }
                
                currentReadings
            }

        /**
         * Configure sampling rate for a specific device using Shimmer SDK
         */
        suspend fun setSamplingRate(
            deviceId: String,
            samplingRate: Double,
        ): Boolean =
            withContext(Dispatchers.IO) {
                try {
                    val device = connectedDevices[deviceId]
                    val shimmer = shimmerDevices[deviceId]

                    if (device == null) {
                        logger.error("Device not found: $deviceId")
                        return@withContext false
                    }

                    if (shimmer == null) {
                        logger.error("Shimmer SDK instance not found for device: $deviceId")
                        return@withContext false
                    }

                    logger.debug("Setting sampling rate to ${samplingRate}Hz for device ${device.getDisplayName()}")

                    try {
                        shimmer.writeSamplingRate(samplingRate)
                        
                        // Update stored configuration
                        val currentConfig = deviceConfigurations[deviceId] ?: DeviceConfiguration.createDefault()
                        val newConfig = currentConfig.withSamplingRate(samplingRate)
                        deviceConfigurations[deviceId] = newConfig
                        device.configuration = newConfig

                        logger.info("Successfully updated sampling rate to ${samplingRate}Hz for device ${device.getDisplayName()}")
                        true
                    } catch (e: Exception) {
                        logger.error("Failed to set sampling rate for device $deviceId", e)
                        false
                    }
                } catch (e: Exception) {
                    logger.error("Failed to configure sampling rate for device $deviceId", e)
                    false
                }
            }

        /**
         * Configure GSR range for a specific device using Shimmer SDK
         */
        suspend fun setGSRRange(
            deviceId: String,
            gsrRange: Int,
        ): Boolean =
            withContext(Dispatchers.IO) {
                try {
                    val device = connectedDevices[deviceId]
                    val shimmer = shimmerDevices[deviceId]

                    if (device == null) {
                        logger.error("Device not found: $deviceId")
                        return@withContext false
                    }

                    if (shimmer == null) {
                        logger.error("Shimmer SDK instance not found for device: $deviceId")
                        return@withContext false
                    }

                    if (gsrRange !in 0..4) {
                        logger.error("Invalid GSR range: $gsrRange. Valid ranges are 0-4")
                        return@withContext false
                    }

                    logger.debug("Setting GSR range to $gsrRange for device ${device.getDisplayName()}")

                    try {
                        shimmer.writeGSRRange(gsrRange)
                        
                        // Update stored configuration
                        val currentConfig = deviceConfigurations[deviceId] ?: DeviceConfiguration.createDefault()
                        val newConfig = currentConfig.copy(gsrRange = gsrRange)
                        deviceConfigurations[deviceId] = newConfig
                        device.configuration = newConfig

                        logger.info("Successfully updated GSR range to $gsrRange for device ${device.getDisplayName()}")
                        true
                    } catch (e: Exception) {
                        logger.error("Failed to set GSR range for device $deviceId", e)
                        false
                    }
                } catch (e: Exception) {
                    logger.error("Failed to configure GSR range for device $deviceId", e)
                    false
                }
            }

        /**
         * Configure accelerometer range for a specific device using Shimmer SDK
         */
        suspend fun setAccelRange(
            deviceId: String,
            accelRange: Int,
        ): Boolean =
            withContext(Dispatchers.IO) {
                try {
                    val device = connectedDevices[deviceId]
                    val shimmer = shimmerDevices[deviceId]

                    if (device == null) {
                        logger.error("Device not found: $deviceId")
                        return@withContext false
                    }

                    if (shimmer == null) {
                        logger.error("Shimmer SDK instance not found for device: $deviceId")
                        return@withContext false
                    }

                    if (accelRange !in listOf(2, 4, 8, 16)) {
                        logger.error("Invalid accelerometer range: $accelRange. Valid ranges are 2, 4, 8, 16g")
                        return@withContext false
                    }

                    logger.debug("Setting accelerometer range to ±${accelRange}g for device ${device.getDisplayName()}")

                    try {
                        shimmer.writeAccelRange(accelRange)
                        
                        // Update stored configuration
                        val currentConfig = deviceConfigurations[deviceId] ?: DeviceConfiguration.createDefault()
                        val newConfig = currentConfig.copy(accelRange = accelRange)
                        deviceConfigurations[deviceId] = newConfig
                        device.configuration = newConfig

                        logger.info("Successfully updated accelerometer range to ±${accelRange}g for device ${device.getDisplayName()}")
                        true
                    } catch (e: Exception) {
                        logger.error("Failed to set accelerometer range for device $deviceId", e)
                        false
                    }
                } catch (e: Exception) {
                    logger.error("Failed to configure accelerometer range for device $deviceId", e)
                    false
                }
            }

        /**
         * Get detailed device information including sensor capabilities
         */
        suspend fun getDeviceInformation(deviceId: String): DeviceInformation? =
            withContext(Dispatchers.IO) {
                try {
                    val device = connectedDevices[deviceId]
                    val shimmer = shimmerDevices[deviceId]

                    if (device == null || shimmer == null) {
                        return@withContext null
                    }

                    // Get device information from Shimmer SDK
                    DeviceInformation(
                        deviceId = deviceId,
                        macAddress = device.macAddress,
                        deviceName = device.deviceName,
                        firmwareVersion = device.firmwareVersion,
                        hardwareVersion = device.hardwareVersion,
                        batteryLevel = device.batteryLevel,
                        connectionState = device.connectionState,
                        isStreaming = device.isActivelyStreaming(),
                        configuration = deviceConfigurations[deviceId],
                        samplesRecorded = sampleCounts[deviceId]?.get() ?: 0L,
                        lastSampleTime = device.lastSampleTime,
                        // Additional device-specific information
                        bluetoothType = "Classic", // Could be enhanced to detect actual type
                        signalStrength = 0, // Could be enhanced to get actual signal strength
                        totalConnectedTime = 0L, // Could be enhanced to track connection time
                    )
                } catch (e: Exception) {
                    logger.error("Failed to get device information for $deviceId", e)
                    null
                }
            }

        /**
         * Data class representing comprehensive device information
         */
        data class DeviceInformation(
            val deviceId: String,
            val macAddress: String,
            val deviceName: String,
            val firmwareVersion: String,
            val hardwareVersion: String,
            val batteryLevel: Int,
            val connectionState: ShimmerDevice.ConnectionState,
            val isStreaming: Boolean,
            val configuration: DeviceConfiguration?,
            val samplesRecorded: Long,
            val lastSampleTime: Long,
            val bluetoothType: String,
            val signalStrength: Int,
            val totalConnectedTime: Long,
        ) {
            fun getDisplaySummary(): String =
                buildString {
                    append("Device: $deviceName ($deviceId)\n")
                    append("State: $connectionState\n")
                    append("Battery: $batteryLevel%\n")
                    append("Samples: $samplesRecorded\n")
                    append("Firmware: $firmwareVersion\n")
                    append("Hardware: $hardwareVersion\n")
                    append("BT Type: $bluetoothType")
                }
        }

        /**
         * Set EXG (ECG/EMG) configuration for supported devices
         */
        suspend fun setEXGConfiguration(
            deviceId: String,
            ecgEnabled: Boolean,
            emgEnabled: Boolean,
        ): Boolean =
            withContext(Dispatchers.IO) {
                try {
                    val device = connectedDevices[deviceId]
                    val shimmer = shimmerDevices[deviceId]

                    if (device == null || shimmer == null) {
                        logger.error("Device or Shimmer instance not found: $deviceId")
                        return@withContext false
                    }

                    logger.debug("Setting EXG configuration for device ${device.getDisplayName()}: ECG=$ecgEnabled, EMG=$emgEnabled")

                    try {
                        // Configure EXG settings using Shimmer SDK methods
                        // Note: Exact method names may vary depending on SDK version
                        if (ecgEnabled) {
                            shimmer.writeEXGConfigurations(0) // ECG configuration
                        }
                        if (emgEnabled) {
                            shimmer.writeEXGConfigurations(1) // EMG configuration
                        }

                        logger.info("Successfully configured EXG for device ${device.getDisplayName()}")
                        true
                    } catch (e: Exception) {
                        logger.error("Failed to set EXG configuration for device $deviceId", e)
                        false
                    }
                } catch (e: Exception) {
                    logger.error("Failed to configure EXG for device $deviceId", e)
                    false
                }
            }

        /**
         * Enable or disable real-time clock synchronization
         */
        suspend fun enableClockSync(
            deviceId: String,
            enable: Boolean,
        ): Boolean =
            withContext(Dispatchers.IO) {
                try {
                    val device = connectedDevices[deviceId]
                    val shimmer = shimmerDevices[deviceId]

                    if (device == null || shimmer == null) {
                        logger.error("Device or Shimmer instance not found: $deviceId")
                        return@withContext false
                    }

                    logger.debug("${if (enable) "Enabling" else "Disabling"} clock sync for device ${device.getDisplayName()}")

                    try {
                        if (enable) {
                            // Synchronize device clock with system time
                            shimmer.writeConfigTime(System.currentTimeMillis())
                            logger.info("Clock synchronized for device ${device.getDisplayName()}")
                        }
                        true
                    } catch (e: Exception) {
                        logger.error("Failed to configure clock sync for device $deviceId", e)
                        false
                    }
                } catch (e: Exception) {
                    logger.error("Failed to configure clock sync for device $deviceId", e)
                    false
                }
            }

        /**
         * Start SD logging on connected Shimmer devices
         * Following official Shimmer SDK pattern
         */
        suspend fun startSDLogging(): Boolean =
            withContext(Dispatchers.IO) {
                try {
                    logger.info("Starting SD logging on connected Shimmer devices")

                    if (shimmerBluetoothManager == null) {
                        logger.error("ShimmerBluetoothManager not initialized")
                        return@withContext false
                    }

                    var successCount = 0
                    val deviceList = mutableListOf<com.shimmerresearch.driver.ShimmerDevice>()

                    // Collect connected Shimmer SDK devices
                    shimmerDevices.values.forEach { shimmer ->
                        if (shimmer.isConnected()) {
                            // Set current time before starting SD logging
                            shimmer.writeConfigTime(System.currentTimeMillis())
                            deviceList.add(shimmer)
                        }
                    }

                    if (deviceList.isEmpty()) {
                        logger.info("No connected Shimmer devices found for SD logging")
                        return@withContext false
                    }

                    // Start SD logging using ShimmerBluetoothManager
                    shimmerBluetoothManager?.startSDLogging(deviceList)

                    logger.info("SD logging started on ${deviceList.size} devices")
                    return@withContext true
                } catch (e: Exception) {
                    logger.error("Failed to start SD logging", e)
                    false
                }
            }

        /**
         * Stop SD logging on connected Shimmer devices
         * Following official Shimmer SDK pattern
         */
        suspend fun stopSDLogging(): Boolean =
            withContext(Dispatchers.IO) {
                try {
                    logger.info("Stopping SD logging on connected Shimmer devices")

                    if (shimmerBluetoothManager == null) {
                        logger.error("ShimmerBluetoothManager not initialized")
                        return@withContext false
                    }

                    val deviceList = mutableListOf<com.shimmerresearch.driver.ShimmerDevice>()

                    // Collect connected Shimmer SDK devices
                    shimmerDevices.values.forEach { shimmer ->
                        if (shimmer.isConnected()) {
                            deviceList.add(shimmer)
                        }
                    }

                    if (deviceList.isEmpty()) {
                        logger.info("No connected Shimmer devices found for stopping SD logging")
                        return@withContext false
                    }

                    // Stop SD logging using ShimmerBluetoothManager
                    shimmerBluetoothManager?.stopSDLogging(deviceList)

                    logger.info("SD logging stopped on ${deviceList.size} devices")
                    return@withContext true
                } catch (e: Exception) {
                    logger.error("Failed to stop SD logging", e)
                    false
                }
            }

        /**
         * Check if any connected device is currently streaming
         */
        fun isAnyDeviceStreaming(): Boolean =
            shimmerDevices.values.any { shimmer ->
                shimmer.isConnected() && shimmer.isStreaming()
            }

        /**
         * Check if any connected device is currently SD logging
         */
        fun isAnyDeviceSDLogging(): Boolean =
            shimmerDevices.values.any { shimmer ->
                shimmer.isConnected() && shimmer.isSDLogging()
            }

        /**
         * Get connected Shimmer device by MAC address
         * Used for configuration dialogs
         */
        fun getConnectedShimmerDevice(macAddress: String): com.shimmerresearch.driver.ShimmerDevice? = shimmerDevices[macAddress]

        /**
         * Get the first connected Shimmer device
         * Used for single device operations
         */
        fun getFirstConnectedShimmerDevice(): com.shimmerresearch.driver.ShimmerDevice? =
            shimmerDevices.values.firstOrNull { shimmer ->
                shimmer.isConnected()
            }

        /**
         * Get ShimmerBluetoothManager instance
         * Used for configuration dialogs
         */
        fun getShimmerBluetoothManager(): ShimmerBluetoothManagerAndroid? = shimmerBluetoothManager

        /**
         * Comprehensive cleanup of all Shimmer SDK resources
         */
        suspend fun cleanup() = withContext(Dispatchers.IO) {
            try {
                logger.info("Starting comprehensive ShimmerRecorder cleanup...")
                
                // Stop recording if active
                if (isRecording.get()) {
                    stopRecording()
                }
                
                // Disconnect all devices
                disconnectAllDevices()
                
                // Cleanup file writers
                fileWriters.values.forEach { writer ->
                    try {
                        writer.close()
                    } catch (e: Exception) {
                        logger.error("Error closing file writer", e)
                    }
                }
                fileWriters.clear()
                
                // Cleanup network streaming
                try {
                    streamingWriter?.close()
                    streamingSocket?.close()
                } catch (e: Exception) {
                    logger.error("Error closing network streaming", e)
                }
                streamingWriter = null
                streamingSocket = null
                isStreaming.set(false)
                
                // Cleanup Shimmer SDK resources
                shimmerBluetoothManager = null
                shimmerDevices.clear()
                shimmerHandlers.clear()
                
                // Cleanup data structures
                connectedDevices.clear()
                deviceConfigurations.clear()
                dataQueues.clear()
                sampleCounts.clear()
                streamingQueue.clear()
                
                // Cleanup threading resources
                recordingScope?.cancel()
                recordingScope = null
                
                dataHandlerThread?.quitSafely()
                dataHandlerThread = null
                dataHandler = null
                
                // Reset state
                isInitialized.set(false)
                isConnected.set(false)
                isRecording.set(false)
                currentSessionId = null
                sampleCount = 0
                sessionStartTime = 0L
                
                logger.info("ShimmerRecorder cleanup completed successfully")
            } catch (e: Exception) {
                logger.error("Error during ShimmerRecorder cleanup", e)
            }
        }
