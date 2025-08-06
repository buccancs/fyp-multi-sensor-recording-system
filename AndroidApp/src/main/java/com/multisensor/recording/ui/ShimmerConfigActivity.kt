package com.multisensor.recording.ui

import android.Manifest
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.view.View
import android.widget.*
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import com.multisensor.recording.R
import com.multisensor.recording.recording.DeviceConfiguration.SensorChannel
import com.multisensor.recording.util.Logger
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch
import javax.inject.Inject

@AndroidEntryPoint
class ShimmerConfigActivity : AppCompatActivity() {
    private val viewModel: ShimmerConfigViewModel by viewModels()

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

    @Inject
    lateinit var logger: Logger

    private val bluetoothPermissions =
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            arrayOf(
                Manifest.permission.BLUETOOTH_SCAN,
                Manifest.permission.BLUETOOTH_CONNECT,
                Manifest.permission.ACCESS_FINE_LOCATION,
            )
        } else {
            arrayOf(
                Manifest.permission.BLUETOOTH,
                Manifest.permission.BLUETOOTH_ADMIN,
                Manifest.permission.ACCESS_FINE_LOCATION,
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
        observeViewModelState()
        checkBluetoothPermissions()

        logger.info("ShimmerConfigActivity created")
    }

    override fun onDestroy() {
        super.onDestroy()
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

        sensorCheckboxes =
            mapOf(
                SensorChannel.GSR to findViewById(R.id.checkbox_gsr),
                SensorChannel.PPG to findViewById(R.id.checkbox_ppg),
                SensorChannel.ACCEL to findViewById(R.id.checkbox_accel),
                SensorChannel.GYRO to findViewById(R.id.checkbox_gyro),
                SensorChannel.MAG to findViewById(R.id.checkbox_mag),
                SensorChannel.ECG to findViewById(R.id.checkbox_ecg),
                SensorChannel.EMG to findViewById(R.id.checkbox_emg),
            )

    }

    private fun setupClickListeners() {
        connectButton.setOnClickListener { viewModel.connectToDevice() }
        disconnectButton.setOnClickListener { viewModel.disconnectFromDevice() }
        scanButton.setOnClickListener { viewModel.scanForDevices() }
        startStreamingButton.setOnClickListener { viewModel.startStreaming() }
        stopStreamingButton.setOnClickListener { viewModel.stopStreaming() }

        deviceListView.setOnItemClickListener { _, _, position, _ ->
            val state = viewModel.uiState.value
            if (position < state.availableDevices.size) {
                viewModel.onDeviceSelected(position)
            }
        }

        sensorCheckboxes.forEach { (channel, checkbox) ->
            checkbox.setOnCheckedChangeListener { _, _ ->
                val enabledSensors = sensorCheckboxes.filter { it.value.isChecked }.keys.map { it.name }.toSet()
                viewModel.updateSensorConfiguration(enabledSensors)
            }
        }
    }

    private fun observeViewModelState() {
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    render(state)
                }
            }
        }
    }

    private fun render(state: ShimmerConfigUiState) {
        connectButton.isEnabled = state.canConnectToDevice
        disconnectButton.isEnabled = state.canDisconnectDevice
        startStreamingButton.isEnabled = state.canStartRecording
        stopStreamingButton.isEnabled = state.canStopRecording
        scanButton.isEnabled = state.canStartScan

        progressBar.visibility = if (state.isScanning || state.isLoadingConnection) View.VISIBLE else View.GONE

        deviceStatusText.text = "Status: ${state.connectionStatus}"
        batteryLevelText.text = if (state.batteryLevel >= 0) "Battery: ${state.batteryLevel}%" else "Battery: Unknown"

        val deviceNames = state.availableDevices.map { "${it.name} (${it.macAddress})" }
        val adapter = ArrayAdapter(this, android.R.layout.simple_list_item_single_choice, deviceNames)
        deviceListView.adapter = adapter
        deviceListView.choiceMode = ListView.CHOICE_MODE_SINGLE
        if (state.selectedDeviceIndex >= 0 && state.selectedDeviceIndex < state.availableDevices.size) {
            deviceListView.setItemChecked(state.selectedDeviceIndex, true)
        }

        sensorCheckboxes.values.forEach { checkbox ->
            checkbox.isEnabled = state.isDeviceConnected && !state.isConfiguring
        }

        if (state.isRecording && state.dataPacketsReceived > 0) {
            val duration = state.recordingDuration / 1000
            realTimeDataText.text =
                "Recording: ${duration}s\nPackets: ${state.dataPacketsReceived}\nSignal: ${state.signalStrength} dBm"
        } else if (state.isDeviceConnected) {
            realTimeDataText.text =
                "Connected\nBattery: ${if (state.batteryLevel >= 0) "${state.batteryLevel}%" else "Unknown"}\nSignal: ${state.signalStrength} dBm"
        } else {
            realTimeDataText.text = "No device connected"
        }

        state.errorMessage?.let { message ->
            if (state.showErrorDialog) {
                Toast.makeText(this, message, Toast.LENGTH_LONG).show()
                viewModel.onErrorMessageShown()
            }
        }

        findViewById<View>(R.id.configuration_section)?.visibility =
            if (state.showConfigurationPanel) View.VISIBLE else View.GONE
        findViewById<View>(R.id.streaming_section)?.visibility =
            if (state.showRecordingControls) View.VISIBLE else View.GONE
    }

    private fun setupSpinners() {
        val samplingRates = arrayOf("25.6 Hz", "51.2 Hz", "128.0 Hz", "256.0 Hz", "512.0 Hz")
        val samplingRateAdapter = ArrayAdapter(this, android.R.layout.simple_spinner_item, samplingRates)
        samplingRateAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        samplingRateSpinner.adapter = samplingRateAdapter
        samplingRateSpinner.setSelection(1)

        samplingRateSpinner.onItemSelectedListener =
            object : AdapterView.OnItemSelectedListener {
                override fun onItemSelected(
                    parent: AdapterView<*>?,
                    view: View?,
                    position: Int,
                    id: Long,
                ) {
                    val samplingRateValues = arrayOf(25.6, 51.2, 128.0, 256.0, 512.0)
                    if (position < samplingRateValues.size) {
                        viewModel.updateSamplingRate(samplingRateValues[position].toInt())
                    }
                }

                override fun onNothingSelected(parent: AdapterView<*>?) {}
            }

        val presets = viewModel.getAvailablePresets().toTypedArray()
        val presetAdapter = ArrayAdapter(this, android.R.layout.simple_spinner_item, presets)
        presetAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        configurationPresetSpinner.adapter = presetAdapter

        configurationPresetSpinner.onItemSelectedListener =
            object : AdapterView.OnItemSelectedListener {
                override fun onItemSelected(
                    parent: AdapterView<*>?,
                    view: View?,
                    position: Int,
                    id: Long,
                ) {
                    val selectedPreset = presets[position]
                    viewModel.applyConfigurationPreset(selectedPreset)
                }

                override fun onNothingSelected(parent: AdapterView<*>?) {}
            }
    }

    private fun setupSensorCheckboxes() {
        sensorCheckboxes[SensorChannel.GSR]?.isChecked = true
        sensorCheckboxes[SensorChannel.PPG]?.isChecked = true
        sensorCheckboxes[SensorChannel.ACCEL]?.isChecked = true
    }

    private fun checkBluetoothPermissions() {
        val missingPermissions =
            bluetoothPermissions.filter {
                ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED
            }

        if (missingPermissions.isNotEmpty()) {
            ActivityCompat.requestPermissions(
                this,
                missingPermissions.toTypedArray(),
                BLUETOOTH_PERMISSION_REQUEST_CODE
            )
        } else {
            logger.info("Bluetooth permissions already granted.")
        }
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray,
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)

        if (requestCode == BLUETOOTH_PERMISSION_REQUEST_CODE) {
            val allGranted = grantResults.all { it == PackageManager.PERMISSION_GRANTED }
            if (allGranted) {
                logger.info("Bluetooth permissions granted by user.")
            } else {
                Toast.makeText(
                    this,
                    "Bluetooth permissions are required for shimmer device functionality",
                    Toast.LENGTH_LONG
                ).show()
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

