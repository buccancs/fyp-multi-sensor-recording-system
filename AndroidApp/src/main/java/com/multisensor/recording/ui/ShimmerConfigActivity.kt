package com.multisensor.recording.ui

import android.Manifest
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothManager
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.View
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.multisensor.recording.R
import com.multisensor.recording.recording.DeviceConfiguration
import com.multisensor.recording.recording.DeviceConfiguration.SensorChannel
import com.multisensor.recording.recording.ShimmerRecorder
import com.multisensor.recording.util.Logger
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.*
import javax.inject.Inject

/**
 * Shimmer Device Configuration Activity
 * Provides comprehensive UI for shimmer device settings based on ShimmerAndroidInstrumentDriver patterns
 * Features: device discovery, pairing, sensor configuration, real-time monitoring
 */
@AndroidEntryPoint
class ShimmerConfigActivity : AppCompatActivity() {

    @Inject
    lateinit var shimmerRecorder: ShimmerRecorder
    
    @Inject
    lateinit var logger: Logger

    // UI Components
    private lateinit var deviceStatusText: TextView
    private lateinit var batteryLevelText: TextView
    private lateinit var samplingRateSpinner: Spinner
    private lateinit var sensorCheckboxes: Map<SensorChannel, CheckBox>
    private lateinit var connectButton: Button
    private lateinit var disconnectButton: Button
    private lateinit var scanButton: Button
    private lateinit var startStreamingButton: Button
    private lateinit var stopStreamingButton: Button
    private lateinit var deviceListView: ListView
    private lateinit var configurationPresetSpinner: Spinner
    private lateinit var realTimeDataText: TextView
    private lateinit var progressBar: ProgressBar

    // State management
    private var isConnected = false
    private var isStreaming = false
    private var discoveredDevices = mutableListOf<String>()
    private var selectedDeviceAddress: String? = null
    private val activityScope = CoroutineScope(Dispatchers.Main + SupervisorJob())
    private val statusUpdateHandler = Handler(Looper.getMainLooper())
    private var statusUpdateRunnable: Runnable? = null

    // Bluetooth permissions
    private val bluetoothPermissions = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
        arrayOf(
            Manifest.permission.BLUETOOTH_SCAN,
            Manifest.permission.BLUETOOTH_CONNECT,
            Manifest.permission.ACCESS_FINE_LOCATION
        )
    } else {
        arrayOf(
            Manifest.permission.BLUETOOTH,
            Manifest.permission.BLUETOOTH_ADMIN,
            Manifest.permission.ACCESS_FINE_LOCATION
        )
    }

    companion object {
        private const val BLUETOOTH_PERMISSION_REQUEST_CODE = 1001
        private const val STATUS_UPDATE_INTERVAL_MS = 2000L
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_shimmer_config)
        
        initializeViews()
        setupClickListeners()
        setupSpinners()
        setupSensorCheckboxes()
        checkBluetoothPermissions()
        startStatusUpdates()
        
        logger.info("ShimmerConfigActivity created")
    }

    override fun onDestroy() {
        super.onDestroy()
        stopStatusUpdates()
        activityScope.cancel()
        logger.info("ShimmerConfigActivity destroyed")
    }

    private fun initializeViews() {
        deviceStatusText = findViewById(R.id.device_status_text)
        batteryLevelText = findViewById(R.id.battery_level_text)
        samplingRateSpinner = findViewById(R.id.sampling_rate_spinner)
        connectButton = findViewById(R.id.connect_button)
        disconnectButton = findViewById(R.id.disconnect_button)
        scanButton = findViewById(R.id.scan_button)
        startStreamingButton = findViewById(R.id.start_streaming_button)
        stopStreamingButton = findViewById(R.id.stop_streaming_button)
        deviceListView = findViewById(R.id.device_list_view)
        configurationPresetSpinner = findViewById(R.id.configuration_preset_spinner)
        realTimeDataText = findViewById(R.id.real_time_data_text)
        progressBar = findViewById(R.id.progress_bar)

        // Initialize sensor checkboxes map
        sensorCheckboxes = mapOf(
            SensorChannel.GSR to findViewById(R.id.checkbox_gsr),
            SensorChannel.PPG to findViewById(R.id.checkbox_ppg),
            SensorChannel.ACCEL to findViewById(R.id.checkbox_accel),
            SensorChannel.GYRO to findViewById(R.id.checkbox_gyro),
            SensorChannel.MAG to findViewById(R.id.checkbox_mag),
            SensorChannel.ECG to findViewById(R.id.checkbox_ecg),
            SensorChannel.EMG to findViewById(R.id.checkbox_emg)
        )

        updateUIState()
    }

    private fun setupClickListeners() {
        connectButton.setOnClickListener { connectToDevice() }
        disconnectButton.setOnClickListener { disconnectFromDevice() }
        scanButton.setOnClickListener { scanForDevices() }
        startStreamingButton.setOnClickListener { startStreaming() }
        stopStreamingButton.setOnClickListener { stopStreaming() }

        deviceListView.setOnItemClickListener { _, _, position, _ ->
            if (position < discoveredDevices.size) {
                selectedDeviceAddress = discoveredDevices[position]
                updateDeviceSelection()
            }
        }

        // Sensor checkbox listeners
        sensorCheckboxes.forEach { (channel, checkbox) ->
            checkbox.setOnCheckedChangeListener { _, _ ->
                updateSensorConfiguration()
            }
        }
    }

    private fun setupSpinners() {
        // Sampling rate spinner
        val samplingRates = arrayOf("25.6 Hz", "51.2 Hz", "128.0 Hz", "256.0 Hz", "512.0 Hz")
        val samplingRateAdapter = ArrayAdapter(this, android.R.layout.simple_spinner_item, samplingRates)
        samplingRateAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        samplingRateSpinner.adapter = samplingRateAdapter
        samplingRateSpinner.setSelection(1) // Default to 51.2 Hz

        samplingRateSpinner.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
                updateSamplingRate()
            }
            override fun onNothingSelected(parent: AdapterView<*>?) {}
        }

        // Configuration preset spinner
        val presets = arrayOf("Default", "High Performance", "Low Power", "Custom")
        val presetAdapter = ArrayAdapter(this, android.R.layout.simple_spinner_item, presets)
        presetAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        configurationPresetSpinner.adapter = presetAdapter

        configurationPresetSpinner.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
                applyConfigurationPreset(position)
            }
            override fun onNothingSelected(parent: AdapterView<*>?) {}
        }
    }

    private fun setupSensorCheckboxes() {
        // Set default configuration (GSR, PPG, ACCEL enabled)
        sensorCheckboxes[SensorChannel.GSR]?.isChecked = true
        sensorCheckboxes[SensorChannel.PPG]?.isChecked = true
        sensorCheckboxes[SensorChannel.ACCEL]?.isChecked = true
    }

    private fun checkBluetoothPermissions() {
        val missingPermissions = bluetoothPermissions.filter {
            ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED
        }

        if (missingPermissions.isNotEmpty()) {
            ActivityCompat.requestPermissions(this, missingPermissions.toTypedArray(), BLUETOOTH_PERMISSION_REQUEST_CODE)
        } else {
            initializeShimmerRecorder()
        }
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        
        if (requestCode == BLUETOOTH_PERMISSION_REQUEST_CODE) {
            val allGranted = grantResults.all { it == PackageManager.PERMISSION_GRANTED }
            if (allGranted) {
                initializeShimmerRecorder()
            } else {
                showError("Bluetooth permissions are required for shimmer device functionality")
            }
        }
    }

    private fun initializeShimmerRecorder() {
        activityScope.launch {
            try {
                progressBar.visibility = View.VISIBLE
                val initialized = shimmerRecorder.initialize()
                
                if (initialized) {
                    logger.info("ShimmerRecorder initialized successfully")
                    updateUIState()
                } else {
                    showError("Failed to initialize ShimmerRecorder")
                }
            } catch (e: Exception) {
                logger.error("Error initializing ShimmerRecorder", e)
                showError("Error initializing shimmer: ${e.message}")
            } finally {
                progressBar.visibility = View.GONE
            }
        }
    }

    private fun scanForDevices() {
        activityScope.launch {
            try {
                progressBar.visibility = View.VISIBLE
                scanButton.isEnabled = false
                
                logger.info("Starting device scan...")
                val devices = shimmerRecorder.scanAndPairDevices()
                
                discoveredDevices.clear()
                discoveredDevices.addAll(devices)
                
                updateDeviceList()
                
                if (devices.isNotEmpty()) {
                    showMessage("Found ${devices.size} shimmer device(s)")
                } else {
                    showMessage("No shimmer devices found")
                }
                
            } catch (e: Exception) {
                logger.error("Error scanning for devices", e)
                showError("Error scanning: ${e.message}")
            } finally {
                progressBar.visibility = View.GONE
                scanButton.isEnabled = true
            }
        }
    }

    private fun connectToDevice() {
        val deviceAddress = selectedDeviceAddress
        if (deviceAddress == null) {
            showError("Please select a device first")
            return
        }

        activityScope.launch {
            try {
                progressBar.visibility = View.VISIBLE
                connectButton.isEnabled = false
                
                logger.info("Connecting to device: $deviceAddress")
                val connected = shimmerRecorder.connectDevices(listOf(deviceAddress))
                
                if (connected) {
                    isConnected = true
                    showMessage("Connected to shimmer device")
                    updateUIState()
                } else {
                    showError("Failed to connect to device")
                }
                
            } catch (e: Exception) {
                logger.error("Error connecting to device", e)
                showError("Connection error: ${e.message}")
            } finally {
                progressBar.visibility = View.GONE
                connectButton.isEnabled = true
            }
        }
    }

    private fun disconnectFromDevice() {
        activityScope.launch {
            try {
                // Stop streaming if active
                if (isStreaming) {
                    shimmerRecorder.stopStreaming()
                    isStreaming = false
                }
                
                // Disconnect device
                shimmerRecorder.cleanup()
                isConnected = false
                
                showMessage("Disconnected from shimmer device")
                updateUIState()
                
            } catch (e: Exception) {
                logger.error("Error disconnecting from device", e)
                showError("Disconnect error: ${e.message}")
            }
        }
    }

    private fun startStreaming() {
        if (!isConnected) {
            showError("Please connect to a device first")
            return
        }

        activityScope.launch {
            try {
                progressBar.visibility = View.VISIBLE
                
                // Apply current sensor configuration
                updateSensorConfiguration()
                
                val started = shimmerRecorder.startStreaming()
                if (started) {
                    isStreaming = true
                    showMessage("Started data streaming")
                    updateUIState()
                } else {
                    showError("Failed to start streaming")
                }
                
            } catch (e: Exception) {
                logger.error("Error starting streaming", e)
                showError("Streaming error: ${e.message}")
            } finally {
                progressBar.visibility = View.GONE
            }
        }
    }

    private fun stopStreaming() {
        activityScope.launch {
            try {
                val stopped = shimmerRecorder.stopStreaming()
                if (stopped) {
                    isStreaming = false
                    showMessage("Stopped data streaming")
                    updateUIState()
                } else {
                    showError("Failed to stop streaming")
                }
                
            } catch (e: Exception) {
                logger.error("Error stopping streaming", e)
                showError("Stop streaming error: ${e.message}")
            }
        }
    }

    private fun updateSensorConfiguration() {
        val deviceAddress = selectedDeviceAddress ?: return
        
        val enabledSensors = sensorCheckboxes.filter { it.value.isChecked }.keys
        
        activityScope.launch {
            try {
                val configured = shimmerRecorder.setEnabledChannels(deviceAddress, enabledSensors)
                if (configured) {
                    logger.info("Sensor configuration updated: ${enabledSensors.size} sensors enabled")
                } else {
                    logger.warning("Failed to update sensor configuration")
                }
            } catch (e: Exception) {
                logger.error("Error updating sensor configuration", e)
            }
        }
    }

    private fun updateSamplingRate() {
        val selectedRate = when (samplingRateSpinner.selectedItemPosition) {
            0 -> 25.6
            1 -> 51.2
            2 -> 128.0
            3 -> 256.0
            4 -> 512.0
            else -> 51.2
        }
        
        // TODO: Apply sampling rate to shimmer device
        logger.info("Sampling rate updated to: ${selectedRate} Hz")
    }

    private fun applyConfigurationPreset(presetIndex: Int) {
        val config = when (presetIndex) {
            0 -> DeviceConfiguration.createDefault()
            1 -> DeviceConfiguration.createHighPerformance()
            2 -> DeviceConfiguration.createLowPower()
            else -> return // Custom - no changes
        }
        
        // Update UI to reflect preset
        updateUIFromConfiguration(config)
        
        // Apply to device if connected
        if (isConnected) {
            updateSensorConfiguration()
        }
    }

    private fun updateUIFromConfiguration(config: DeviceConfiguration) {
        // Update sensor checkboxes
        sensorCheckboxes.forEach { (channel, checkbox) ->
            checkbox.isChecked = config.isSensorEnabled(channel)
        }
        
        // Update sampling rate spinner
        val rateIndex = when (config.samplingRate) {
            25.6 -> 0
            51.2 -> 1
            128.0 -> 2
            256.0 -> 3
            512.0 -> 4
            else -> 1
        }
        samplingRateSpinner.setSelection(rateIndex)
    }

    private fun updateDeviceList() {
        val adapter = ArrayAdapter(this, android.R.layout.simple_list_item_single_choice, discoveredDevices)
        deviceListView.adapter = adapter
        deviceListView.choiceMode = ListView.CHOICE_MODE_SINGLE
    }

    private fun updateDeviceSelection() {
        val deviceAddress = selectedDeviceAddress
        if (deviceAddress != null) {
            val index = discoveredDevices.indexOf(deviceAddress)
            if (index >= 0) {
                deviceListView.setItemChecked(index, true)
            }
        }
    }

    private fun updateUIState() {
        connectButton.isEnabled = !isConnected && selectedDeviceAddress != null
        disconnectButton.isEnabled = isConnected
        startStreamingButton.isEnabled = isConnected && !isStreaming
        stopStreamingButton.isEnabled = isConnected && isStreaming
        
        // Update sensor checkboxes enabled state
        sensorCheckboxes.values.forEach { checkbox ->
            checkbox.isEnabled = isConnected && !isStreaming
        }
        
        samplingRateSpinner.isEnabled = isConnected && !isStreaming
        configurationPresetSpinner.isEnabled = isConnected && !isStreaming
        
        // Update status text
        val status = when {
            isStreaming -> "Streaming data"
            isConnected -> "Connected"
            else -> "Disconnected"
        }
        deviceStatusText.text = "Status: $status"
    }

    private fun startStatusUpdates() {
        statusUpdateRunnable = object : Runnable {
            override fun run() {
                updateRealTimeData()
                statusUpdateHandler.postDelayed(this, STATUS_UPDATE_INTERVAL_MS)
            }
        }
        statusUpdateHandler.post(statusUpdateRunnable!!)
    }

    private fun stopStatusUpdates() {
        statusUpdateRunnable?.let { statusUpdateHandler.removeCallbacks(it) }
    }

    private fun updateRealTimeData() {
        if (!isConnected) return
        
        activityScope.launch {
            try {
                val status = shimmerRecorder.getShimmerStatus()
                val readings = shimmerRecorder.getCurrentReadings()
                
                // Update battery level
                val batteryText = if (status.batteryLevel != null) {
                    "Battery: ${status.batteryLevel}%"
                } else {
                    "Battery: Unknown"
                }
                batteryLevelText.text = batteryText
                
                // Update real-time data
                if (readings != null && isStreaming) {
                    val dataText = "GSR: ${String.format("%.2f", readings.gsrConductance)} μS\n" +
                                  "PPG: ${String.format("%.2f", readings.ppgA13)}\n" +
                                  "Accel: X=${String.format("%.2f", readings.accelX)} " +
                                  "Y=${String.format("%.2f", readings.accelY)} " +
                                  "Z=${String.format("%.2f", readings.accelZ)}"
                    realTimeDataText.text = dataText
                } else {
                    realTimeDataText.text = "No data available"
                }
                
            } catch (e: Exception) {
                logger.error("Error updating real-time data", e)
            }
        }
    }

    private fun showMessage(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
    }

    private fun showError(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_LONG).show()
    }
}
