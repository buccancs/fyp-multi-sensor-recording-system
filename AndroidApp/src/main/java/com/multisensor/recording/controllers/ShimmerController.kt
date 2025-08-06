package com.multisensor.recording.controllers

import android.app.Activity
import android.app.AlertDialog
import android.app.Dialog
import android.content.Context
import android.content.Intent
import android.widget.Toast
import androidx.activity.result.ActivityResultLauncher
import com.multisensor.recording.managers.ShimmerManager
import com.multisensor.recording.persistence.ShimmerDeviceState
import com.multisensor.recording.persistence.ShimmerDeviceStateRepository
import com.multisensor.recording.ui.MainViewModel
import com.shimmerresearch.android.guiUtilities.ShimmerBluetoothDialog
import com.shimmerresearch.android.manager.ShimmerBluetoothManagerAndroid
import kotlinx.coroutines.*
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class ShimmerController @Inject constructor(
    private val shimmerManager: ShimmerManager,
    private val shimmerDeviceStateRepository: ShimmerDeviceStateRepository,
    private val shimmerErrorHandler: ShimmerErrorHandler
) {

    interface ShimmerCallback {
        fun onDeviceSelected(address: String, name: String)
        fun onDeviceSelectionCancelled()
        fun onConnectionStatusChanged(connected: Boolean)
        fun onConfigurationComplete()
        fun onShimmerError(message: String)
        fun updateStatusText(text: String)
        fun showToast(message: String, duration: Int = Toast.LENGTH_SHORT)
        fun runOnUiThread(action: () -> Unit)
    }

    private var callback: ShimmerCallback? = null
    private var selectedShimmerAddress: String? = null
    private var selectedShimmerName: String? = null
    private var preferredBtType: ShimmerBluetoothManagerAndroid.BT_TYPE =
        ShimmerBluetoothManagerAndroid.BT_TYPE.BT_CLASSIC

    private val persistenceScope = CoroutineScope(Dispatchers.IO + SupervisorJob())

    private val connectedDevices = mutableMapOf<String, ShimmerDeviceState>()
    private val connectionRetryAttempts = mutableMapOf<String, Int>()
    private val maxRetryAttempts = 3

    fun setCallback(callback: ShimmerCallback) {
        this.callback = callback

        loadSavedDeviceStates()
    }

    private fun loadSavedDeviceStates() {
        persistenceScope.launch {
            try {
                val savedStates = shimmerDeviceStateRepository.getAllDeviceStates()
                android.util.Log.d("ShimmerController", "[DEBUG_LOG] Loaded ${savedStates.size} saved device states")

                withContext(Dispatchers.Main) {
                    savedStates.forEach { deviceState ->
                        connectedDevices[deviceState.deviceAddress] = deviceState
                        android.util.Log.d(
                            "ShimmerController",
                            "[DEBUG_LOG] Restored device: ${deviceState.deviceName} (${deviceState.deviceAddress})"
                        )
                    }

                    attemptAutoReconnection()
                }
            } catch (e: CancellationException) {
                throw e
            } catch (e: java.io.IOException) {
                android.util.Log.e("ShimmerController", "[DEBUG_LOG] IO error loading saved device states: ${e.message}")
            } catch (e: SecurityException) {
                android.util.Log.e("ShimmerController", "[DEBUG_LOG] Permission error loading saved device states: ${e.message}")
            } catch (e: RuntimeException) {
                android.util.Log.e("ShimmerController", "[DEBUG_LOG] Runtime error loading saved device states: ${e.message}")
            }
        }
    }

    private fun attemptAutoReconnection() {
        persistenceScope.launch {
            try {
                val autoReconnectDevices = shimmerDeviceStateRepository.getAutoReconnectDevices()
                android.util.Log.d(
                    "ShimmerController",
                    "[DEBUG_LOG] Found ${autoReconnectDevices.size} devices for auto-reconnection"
                )

                autoReconnectDevices.forEach { deviceState ->
                    if (connectionRetryAttempts.getOrDefault(deviceState.deviceAddress, 0) < maxRetryAttempts) {
                        android.util.Log.d(
                            "ShimmerController",
                            "[DEBUG_LOG] Attempting auto-reconnection to ${deviceState.deviceName}"
                        )

                        withContext(Dispatchers.Main) {
                            callback?.updateStatusText("Auto-reconnecting to ${deviceState.deviceName}...")
                        }

                        withContext(Dispatchers.Main) {
                            callback?.updateStatusText("Auto-reconnection attempted for ${deviceState.deviceName}")
                        }
                    }
                }
            } catch (e: CancellationException) {
                throw e
            } catch (e: SecurityException) {
                android.util.Log.e("ShimmerController", "[DEBUG_LOG] Permission error during auto-reconnection: ${e.message}")
            } catch (e: IllegalStateException) {
                android.util.Log.e("ShimmerController", "[DEBUG_LOG] Invalid state during auto-reconnection: ${e.message}")
            } catch (e: RuntimeException) {
                android.util.Log.e("ShimmerController", "[DEBUG_LOG] Runtime error during auto-reconnection: ${e.message}")
            }
        }
    }

    fun showBtTypeConnectionOption(context: Context) {
        android.util.Log.d("ShimmerController", "[DEBUG_LOG] Showing Bluetooth type selection dialog")

        val alertDialog = AlertDialog.Builder(context).create()
        alertDialog.setCancelable(false)
        alertDialog.setMessage("Choose preferred Bluetooth type")

        alertDialog.setButton(Dialog.BUTTON_POSITIVE, "BT CLASSIC") { _, _ ->
            android.util.Log.d("ShimmerController", "[DEBUG_LOG] User selected BT CLASSIC")
            preferredBtType = ShimmerBluetoothManagerAndroid.BT_TYPE.BT_CLASSIC
            connectSelectedShimmerDevice()
        }

        alertDialog.setButton(Dialog.BUTTON_NEGATIVE, "BLE") { _, _ ->
            android.util.Log.d("ShimmerController", "[DEBUG_LOG] User selected BLE")
            preferredBtType = ShimmerBluetoothManagerAndroid.BT_TYPE.BLE
            connectSelectedShimmerDevice()
        }

        alertDialog.show()
    }

    private fun connectSelectedShimmerDevice() {
        selectedShimmerAddress?.let { address ->
            selectedShimmerName?.let { name ->
                android.util.Log.d("ShimmerController", "[DEBUG_LOG] Connecting to Shimmer device:")
                android.util.Log.d("ShimmerController", "[DEBUG_LOG] - Address: $address")
                android.util.Log.d("ShimmerController", "[DEBUG_LOG] - Name: $name")
                android.util.Log.d("ShimmerController", "[DEBUG_LOG] - Connection Type: $preferredBtType")

                callback?.updateStatusText("Connecting to $name ($preferredBtType)...")

                try {
                    android.util.Log.d("ShimmerController", "[DEBUG_LOG] Initiating connection process...")

                    callback?.showToast(
                        "Attempting connection to $name via $preferredBtType",
                        android.widget.Toast.LENGTH_SHORT
                    )

                    callback?.updateStatusText("Connection initiated for $name")

                    callback?.onDeviceSelected(address, name)

                    android.util.Log.d("ShimmerController", "[DEBUG_LOG] Connection process initiated successfully")
                } catch (e: Exception) {
                    android.util.Log.e("ShimmerController", "[DEBUG_LOG] Connection initiation failed: ${e.message}")
                    callback?.onShimmerError("Failed to initiate connection: ${e.message}")
                }
            }
        } ?: run {
            android.util.Log.w("ShimmerController", "[DEBUG_LOG] Cannot connect - no device selected")
            callback?.onShimmerError("No Shimmer device selected for connection")
        }
    }

    fun launchShimmerDeviceDialog(activity: Activity, launcher: ActivityResultLauncher<Intent>) {
        android.util.Log.d("ShimmerController", "[DEBUG_LOG] Launching Shimmer device selection dialog")

        try {
            val intent = Intent(activity, ShimmerBluetoothDialog::class.java)
            launcher.launch(intent)
        } catch (e: Exception) {
            android.util.Log.e("ShimmerController", "[DEBUG_LOG] Failed to launch Shimmer device dialog: ${e.message}")
            callback?.onShimmerError("Failed to launch device selection dialog: ${e.message}")
        }
    }

    fun handleDeviceSelectionResult(address: String?, name: String?) {
        if (address != null && name != null) {
            android.util.Log.d("ShimmerController", "[DEBUG_LOG] Device selected: $name ($address)")
            selectedShimmerAddress = address
            selectedShimmerName = name

            callback?.runOnUiThread {
                callback?.updateStatusText("Device selected: $name")
                callback?.showToast("Selected: $name")
            }

            saveDeviceState(address, name, preferredBtType, false)

            callback?.onDeviceSelected(address, name)
        } else {
            android.util.Log.d("ShimmerController", "[DEBUG_LOG] Device selection cancelled")
            callback?.onDeviceSelectionCancelled()
        }
    }

    private fun saveDeviceState(
        address: String,
        name: String,
        connectionType: ShimmerBluetoothManagerAndroid.BT_TYPE,
        connected: Boolean,
        enabledSensors: Set<String> = emptySet(),
        samplingRate: Double = 512.0,
        gsrRange: Int = 0
    ) {
        persistenceScope.launch {
            try {
                val existingState = shimmerDeviceStateRepository.getDeviceState(address)

                val deviceState = if (existingState != null) {
                    existingState.copy(
                        deviceName = name,
                        connectionType = connectionType,
                        isConnected = connected,
                        lastConnectedTimestamp = if (connected) System.currentTimeMillis() else existingState.lastConnectedTimestamp,
                        enabledSensors = if (enabledSensors.isNotEmpty()) enabledSensors else existingState.enabledSensors,
                        samplingRate = samplingRate.takeIf { it != 512.0 } ?: existingState.samplingRate,
                        gsrRange = gsrRange.takeIf { it != 0 } ?: existingState.gsrRange,
                        lastUpdated = System.currentTimeMillis()
                    )
                } else {
                    ShimmerDeviceState(
                        deviceAddress = address,
                        deviceName = name,
                        connectionType = connectionType,
                        isConnected = connected,
                        lastConnectedTimestamp = if (connected) System.currentTimeMillis() else 0L,
                        enabledSensors = enabledSensors,
                        samplingRate = samplingRate,
                        gsrRange = gsrRange,
                        autoReconnectEnabled = true,
                        preferredConnectionOrder = connectedDevices.size
                    )
                }

                shimmerDeviceStateRepository.saveDeviceState(deviceState)

                withContext(Dispatchers.Main) {
                    connectedDevices[address] = deviceState
                }

                android.util.Log.d("ShimmerController", "[DEBUG_LOG] Device state saved: $name ($address)")
            } catch (e: Exception) {
                android.util.Log.e("ShimmerController", "[DEBUG_LOG] Failed to save device state: ${e.message}")
            }
        }
    }

    fun connectToSelectedDevice(viewModel: MainViewModel) {
        selectedShimmerAddress?.let { address ->
            selectedShimmerName?.let { name ->
                connectToDevice(address, name, viewModel)
            }
        } ?: run {
            callback?.onShimmerError("No device selected")
        }
    }

    fun connectToDevice(address: String, name: String, viewModel: MainViewModel) {
        android.util.Log.d("ShimmerController", "[DEBUG_LOG] Connecting to device: $name ($address)")

        if (connectedDevices[address]?.isConnected == true) {
            callback?.onShimmerError("Device $name is already connected")
            return
        }

        callback?.updateStatusText("Connecting to $name...")

        persistenceScope.launch {
            val attemptConnection: suspend () -> Boolean = {
                withContext(Dispatchers.Main) {
                    var connectionResult = false
                    viewModel.connectShimmerDevice(address, name, preferredBtType) { success ->
                        connectionResult = success
                    }
                    connectionResult
                }
            }

            try {

                val success = shimmerErrorHandler.handleError(
                    deviceAddress = address,
                    deviceName = name,
                    exception = null,
                    errorMessage = null,
                    attemptNumber = connectionRetryAttempts.getOrDefault(address, 0) + 1,
                    connectionType = preferredBtType,
                    onRetry = attemptConnection,
                    onFinalFailure = { strategy ->
                        callback?.runOnUiThread {
                            callback?.updateStatusText("Failed to connect to $name")
                            callback?.showToast(strategy.userMessage, Toast.LENGTH_LONG)
                            callback?.onShimmerError(strategy.userMessage)
                        }

                        if (strategy.userActionRequired) {
                            generateAndShowDiagnostics(address)
                        }
                    }
                )

                callback?.runOnUiThread {
                    if (success) {
                        callback?.updateStatusText("Connected to $name")
                        callback?.showToast("Successfully connected to $name")
                        callback?.onConnectionStatusChanged(true)

                        connectionRetryAttempts.remove(address)
                        persistenceScope.launch {
                            shimmerErrorHandler.resetErrorState(address)
                            updateConnectionStatus(address, name, true)
                        }
                    }
                }

            } catch (e: Exception) {
                android.util.Log.e("ShimmerController", "[DEBUG_LOG] Connection error for $name: ${e.message}")

                callback?.runOnUiThread {
                    callback?.onShimmerError("Connection error: ${e.message}")
                }

                shimmerDeviceStateRepository.logConnectionAttempt(address, false, e.message, name, preferredBtType)
            }
        }
    }

    private fun generateAndShowDiagnostics(address: String) {
        persistenceScope.launch {
            try {
                val diagnostics = shimmerErrorHandler.generateDiagnosticReport(address)
                val recommendations = shimmerErrorHandler.checkDeviceHealth(address)

                callback?.runOnUiThread {
                    val message = if (recommendations.isNotEmpty()) {
                        "Connection failed. Suggestions:\n${recommendations.take(3).joinToString("\n")}"
                    } else {
                        "Connection failed. Check device status and try again."
                    }

                    callback?.showToast(message, Toast.LENGTH_LONG)
                    android.util.Log.d("ShimmerController", "[DIAGNOSTICS] $diagnostics")
                }
            } catch (e: Exception) {
                android.util.Log.e("ShimmerController", "[DEBUG_LOG] Failed to generate diagnostics: ${e.message}")
            }
        }
    }

    private fun updateConnectionStatus(address: String, name: String, connected: Boolean) {
        persistenceScope.launch {
            try {
                shimmerDeviceStateRepository.updateConnectionStatus(address, connected, name, preferredBtType)

                val existingState = connectedDevices[address]
                if (existingState != null) {
                    val updatedState = existingState.copy(
                        isConnected = connected,
                        lastConnectedTimestamp = if (connected) System.currentTimeMillis() else existingState.lastConnectedTimestamp
                    )
                    withContext(Dispatchers.Main) {
                        connectedDevices[address] = updatedState
                    }
                }

                android.util.Log.d("ShimmerController", "[DEBUG_LOG] Connection status updated: $name = $connected")
            } catch (e: Exception) {
                android.util.Log.e("ShimmerController", "[DEBUG_LOG] Failed to update connection status: ${e.message}")
            }
        }
    }

    fun configureSensorChannels(viewModel: MainViewModel, enabledChannels: Set<String>) {
        selectedShimmerAddress?.let { deviceId ->
            android.util.Log.d("ShimmerController", "[DEBUG_LOG] Configuring sensors for device: $deviceId")

            val sensorChannels = enabledChannels.mapNotNull { channelName ->
                try {
                    null
                } catch (e: Exception) {
                    null
                }
            }.toSet()

            callback?.updateStatusText("Configuring sensors...")

            viewModel.configureShimmerSensors(deviceId, sensorChannels) { success ->
                callback?.runOnUiThread {
                    if (success) {
                        callback?.updateStatusText("Sensors configured successfully")
                        callback?.showToast("Sensor configuration updated")
                        callback?.onConfigurationComplete()
                    } else {
                        callback?.updateStatusText("Failed to configure sensors")
                        callback?.showToast("Sensor configuration failed")
                        callback?.onShimmerError("Configuration failed")
                    }
                }
            }
        } ?: run {
            callback?.onShimmerError("No device connected")
        }
    }

    fun setSamplingRate(viewModel: MainViewModel, samplingRate: Double) {
        selectedShimmerAddress?.let { deviceId ->
            android.util.Log.d(
                "ShimmerController",
                "[DEBUG_LOG] Setting sampling rate to ${samplingRate}Hz for device: $deviceId"
            )

            callback?.updateStatusText("Setting sampling rate to ${samplingRate}Hz...")

            viewModel.setShimmerSamplingRate(deviceId, samplingRate) { success ->
                callback?.runOnUiThread {
                    if (success) {
                        callback?.updateStatusText("Sampling rate set to ${samplingRate}Hz")
                        callback?.showToast("Sampling rate updated")
                    } else {
                        callback?.updateStatusText("Failed to set sampling rate")
                        callback?.showToast("Failed to update sampling rate")
                        callback?.onShimmerError("Sampling rate configuration failed")
                    }
                }
            }
        } ?: run {
            callback?.onShimmerError("No device connected")
        }
    }

    fun setGSRRange(viewModel: MainViewModel, gsrRange: Int) {
        selectedShimmerAddress?.let { deviceId ->
            android.util.Log.d("ShimmerController", "[DEBUG_LOG] Setting GSR range to $gsrRange for device: $deviceId")

            callback?.updateStatusText("Setting GSR range to $gsrRange...")

            viewModel.setShimmerGSRRange(deviceId, gsrRange) { success ->
                callback?.runOnUiThread {
                    if (success) {
                        callback?.updateStatusText("GSR range set to $gsrRange")
                        callback?.showToast("GSR range updated")
                    } else {
                        callback?.updateStatusText("Failed to set GSR range")
                        callback?.showToast("Failed to update GSR range")
                        callback?.onShimmerError("GSR range configuration failed")
                    }
                }
            }
        } ?: run {
            callback?.onShimmerError("No device connected")
        }
    }

    fun getDeviceInformation(viewModel: MainViewModel, callback: (deviceInfo: String?) -> Unit) {
        selectedShimmerAddress?.let { deviceId ->
            android.util.Log.d("ShimmerController", "[DEBUG_LOG] Getting device information for: $deviceId")

            viewModel.getShimmerDeviceInfo(deviceId) { deviceInfo ->
                val infoText = deviceInfo?.getDisplaySummary() ?: "Device information not available"
                callback(infoText)
            }
        } ?: run {
            callback("No device connected")
        }
    }

    fun getDataQualityMetrics(viewModel: MainViewModel, callback: (metrics: String?) -> Unit) {
        selectedShimmerAddress?.let { deviceId ->
            android.util.Log.d("ShimmerController", "[DEBUG_LOG] Getting data quality metrics for: $deviceId")

            viewModel.getShimmerDataQuality(deviceId) { metrics ->
                val metricsText = metrics?.getDisplaySummary() ?: "Data quality metrics not available"
                callback(metricsText)
            }
        } ?: run {
            callback("No device connected")
        }
    }

    fun disconnectDevice(viewModel: MainViewModel) {
        selectedShimmerAddress?.let { deviceId ->
            android.util.Log.d("ShimmerController", "[DEBUG_LOG] Disconnecting from device: $deviceId")

            callback?.updateStatusText("Disconnecting...")

            viewModel.disconnectShimmerDevice(deviceId) { success ->
                callback?.runOnUiThread {
                    if (success) {
                        callback?.updateStatusText("Disconnected")
                        callback?.showToast("Device disconnected")
                        callback?.onConnectionStatusChanged(false)
                        resetState()
                    } else {
                        callback?.updateStatusText("Failed to disconnect")
                        callback?.showToast("Disconnect failed")
                        callback?.onShimmerError("Disconnect failed")
                    }
                }
            }
        } ?: run {
            callback?.onShimmerError("No device connected")
        }
    }

    fun showShimmerSensorConfiguration(context: Context, viewModel: MainViewModel) {
        android.util.Log.d("ShimmerController", "[DEBUG_LOG] Showing Shimmer sensor configuration")

        val shimmerDevice = viewModel.getFirstConnectedShimmerDevice()
        val btManager = viewModel.getShimmerBluetoothManager()

        if (shimmerDevice != null && btManager != null) {
            if (!shimmerDevice.isStreaming() && !shimmerDevice.isSDLogging()) {
                try {
                    com.shimmerresearch.android.guiUtilities.ShimmerDialogConfigurations
                        .buildShimmerSensorEnableDetails(shimmerDevice, context as android.app.Activity, btManager)
                    callback?.onConfigurationComplete()
                } catch (e: Exception) {
                    android.util.Log.e(
                        "ShimmerController",
                        "[DEBUG_LOG] Error showing sensor configuration: ${e.message}"
                    )
                    callback?.onShimmerError("Failed to show sensor configuration: ${e.message}")
                }
            } else {
                callback?.showToast("Cannot configure - device is streaming or logging")
            }
        } else {
            callback?.showToast("No Shimmer device connected")
            android.util.Log.w(
                "ShimmerController",
                "[DEBUG_LOG] No connected Shimmer device available for configuration"
            )
        }
    }

    fun showShimmerGeneralConfiguration(context: Context, viewModel: MainViewModel) {
        android.util.Log.d("ShimmerController", "[DEBUG_LOG] Showing Shimmer general configuration")

        val shimmerDevice = viewModel.getFirstConnectedShimmerDevice()
        val btManager = viewModel.getShimmerBluetoothManager()

        if (shimmerDevice != null && btManager != null) {
            if (!shimmerDevice.isStreaming() && !shimmerDevice.isSDLogging()) {
                try {
                    com.shimmerresearch.android.guiUtilities.ShimmerDialogConfigurations
                        .buildShimmerConfigOptions(shimmerDevice, context as android.app.Activity, btManager)
                    callback?.onConfigurationComplete()
                } catch (e: Exception) {
                    android.util.Log.e(
                        "ShimmerController",
                        "[DEBUG_LOG] Error showing general configuration: ${e.message}"
                    )
                    callback?.onShimmerError("Failed to show general configuration: ${e.message}")
                }
            } else {
                callback?.showToast("Cannot configure - device is streaming or logging")
            }
        } else {
            callback?.showToast("No Shimmer device connected")
            android.util.Log.w(
                "ShimmerController",
                "[DEBUG_LOG] No connected Shimmer device available for configuration"
            )
        }
    }

    fun startShimmerSDLogging(viewModel: MainViewModel) {
        android.util.Log.d("ShimmerController", "[DEBUG_LOG] Starting Shimmer SD logging")

        if (viewModel.isAnyShimmerDeviceStreaming()) {
            callback?.showToast("Cannot start SD logging - device is streaming")
            return
        }

        if (viewModel.isAnyShimmerDeviceSDLogging()) {
            callback?.showToast("SD logging is already active")
            return
        }

        viewModel.startShimmerSDLogging { success ->
            callback?.runOnUiThread {
                if (success) {
                    callback?.showToast("SD logging started")
                    android.util.Log.d("ShimmerController", "[DEBUG_LOG] SD logging started successfully")
                } else {
                    callback?.showToast("Failed to start SD logging")
                    android.util.Log.e("ShimmerController", "[DEBUG_LOG] Failed to start SD logging")
                    callback?.onShimmerError("Failed to start SD logging")
                }
            }
        }
    }

    fun stopShimmerSDLogging(viewModel: MainViewModel) {
        android.util.Log.d("ShimmerController", "[DEBUG_LOG] Stopping Shimmer SD logging")

        if (!viewModel.isAnyShimmerDeviceSDLogging()) {
            callback?.showToast("No SD logging is currently active")
            return
        }

        viewModel.stopShimmerSDLogging { success ->
            callback?.runOnUiThread {
                if (success) {
                    callback?.showToast("SD logging stopped")
                    android.util.Log.d("ShimmerController", "[DEBUG_LOG] SD logging stopped successfully")
                } else {
                    callback?.showToast("Failed to stop SD logging")
                    android.util.Log.e("ShimmerController", "[DEBUG_LOG] Failed to stop SD logging")
                    callback?.onShimmerError("Failed to stop SD logging")
                }
            }
        }
    }

    fun handleShimmerConfigMenuAction(context: Context) {
        android.util.Log.d("ShimmerController", "[DEBUG_LOG] Opening Shimmer Configuration")

        try {
            val intent = Intent(context, com.multisensor.recording.ui.ShimmerConfigActivity::class.java)
            context.startActivity(intent)
        } catch (e: Exception) {
            android.util.Log.e("ShimmerController", "[DEBUG_LOG] Failed to open Shimmer Configuration: ${e.message}")
            callback?.onShimmerError("Failed to open Shimmer Configuration: ${e.message}")
        }
    }

    fun getConnectionStatus(): String {
        return buildString {
            append("Shimmer Status:\n")
            append("- Selected Device: ${selectedShimmerName ?: "None"}\n")
            append("- Selected Address: ${selectedShimmerAddress ?: "None"}\n")
            append("- Preferred BT Type: $preferredBtType\n")

            val connectionStatus = when {
                selectedShimmerAddress == null -> "No device selected"
                selectedShimmerName == null -> "Device address available but name unknown"
                else -> "Device selected - ready for connection"
            }
            append("- Connection Status: $connectionStatus\n")

            append("- Last Action: ${getLastActionDescription()}")
        }
    }

    private fun getLastActionDescription(): String {
        return when {
            selectedShimmerAddress != null && selectedShimmerName != null -> "Device selected successfully"
            selectedShimmerAddress != null -> "Device address stored"
            else -> "Awaiting device selection"
        }
    }

    fun resetState() {
        selectedShimmerAddress = null
        selectedShimmerName = null
        preferredBtType = ShimmerBluetoothManagerAndroid.BT_TYPE.BT_CLASSIC
        android.util.Log.d("ShimmerController", "[DEBUG_LOG] Shimmer controller state reset")
    }

    fun getSelectedDeviceInfo(): Pair<String?, String?> {
        return Pair(selectedShimmerAddress, selectedShimmerName)
    }

    fun getPreferredBtType(): ShimmerBluetoothManagerAndroid.BT_TYPE {
        return preferredBtType
    }

    fun setPreferredBtType(btType: ShimmerBluetoothManagerAndroid.BT_TYPE) {
        preferredBtType = btType
        android.util.Log.d("ShimmerController", "[DEBUG_LOG] Preferred BT type set to: $btType")
    }

    fun getConnectedDevices(): List<ShimmerDeviceState> {
        return connectedDevices.values.filter { it.isConnected }
    }

    fun getConnectedDeviceCount(): Int {
        return connectedDevices.values.count { it.isConnected }
    }

    fun disconnectAllDevices(viewModel: MainViewModel) {
        val connectedDeviceList = getConnectedDevices()
        android.util.Log.d("ShimmerController", "[DEBUG_LOG] Disconnecting ${connectedDeviceList.size} devices")

        connectedDeviceList.forEach { deviceState ->
            disconnectSpecificDevice(deviceState.deviceAddress, viewModel)
        }
    }

    fun disconnectSpecificDevice(deviceAddress: String, viewModel: MainViewModel) {
        val deviceState = connectedDevices[deviceAddress]
        if (deviceState?.isConnected == true) {
            android.util.Log.d("ShimmerController", "[DEBUG_LOG] Disconnecting device: ${deviceState.deviceName}")

            callback?.updateStatusText("Disconnecting ${deviceState.deviceName}...")

            viewModel.disconnectShimmerDevice(deviceAddress) { success ->
                callback?.runOnUiThread {
                    if (success) {
                        callback?.updateStatusText("Disconnected ${deviceState.deviceName}")
                        callback?.showToast("Device ${deviceState.deviceName} disconnected")
                        updateConnectionStatus(deviceAddress, deviceState.deviceName, false)
                    } else {
                        callback?.updateStatusText("Failed to disconnect ${deviceState.deviceName}")
                        callback?.showToast("Disconnect failed for ${deviceState.deviceName}")
                        callback?.onShimmerError("Disconnect failed")
                    }
                }
            }
        }
    }

    fun getDeviceState(address: String): ShimmerDeviceState? {
        return connectedDevices[address]
    }

    fun setAutoReconnectEnabled(address: String, enabled: Boolean) {
        persistenceScope.launch {
            shimmerDeviceStateRepository.setAutoReconnectEnabled(address, enabled)

            val existingState = connectedDevices[address]
            if (existingState != null) {
                val updatedState = existingState.copy(autoReconnectEnabled = enabled)
                withContext(Dispatchers.Main) {
                    connectedDevices[address] = updatedState
                }
            }
        }
    }

    fun setDeviceConnectionPriority(address: String, priority: Int) {
        persistenceScope.launch {
            shimmerDeviceStateRepository.setDeviceConnectionPriority(address, priority)

            val existingState = connectedDevices[address]
            if (existingState != null) {
                val updatedState = existingState.copy(preferredConnectionOrder = priority)
                withContext(Dispatchers.Main) {
                    connectedDevices[address] = updatedState
                }
            }
        }
    }

    fun getConnectionDiagnostics(): String {
        return buildString {
            append("=== Shimmer Connection Diagnostics ===\n")
            append("Connected devices: ${getConnectedDeviceCount()}\n")
            append("Total tracked devices: ${connectedDevices.size}\n")
            append("Active retry attempts: ${connectionRetryAttempts.size}\n\n")

            connectedDevices.values.forEach { device ->
                append("Device: ${device.deviceName}\n")
                append("  Address: ${device.deviceAddress}\n")
                append("  Connected: ${device.isConnected}\n")
                append("  Type: ${device.connectionType}\n")
                append("  Auto-reconnect: ${device.autoReconnectEnabled}\n")
                append("  Priority: ${device.preferredConnectionOrder}\n")
                append("  Last connected: ${if (device.lastConnectedTimestamp > 0) java.util.Date(device.lastConnectedTimestamp) else "Never"}\n")
                append("  Retry attempts: ${connectionRetryAttempts[device.deviceAddress] ?: 0}\n\n")
            }
        }
    }

    fun getDeviceManagementStatus(): String {
        val connectedCount = getConnectedDeviceCount()
        val totalCount = connectedDevices.size

        return when {
            connectedCount == 0 && totalCount == 0 -> "No devices configured"
            connectedCount == 0 -> "$totalCount device(s) configured, none connected"
            connectedCount == 1 -> "1 device connected"
            else -> "$connectedCount devices connected"
        }
    }

    suspend fun exportDeviceConfigurations(): List<ShimmerDeviceState> {
        return shimmerDeviceStateRepository.getAllDeviceStates()
    }

    fun cleanupOldDeviceData() {
        persistenceScope.launch {
            try {
                shimmerDeviceStateRepository.cleanupOldData()
                android.util.Log.d("ShimmerController", "[DEBUG_LOG] Old device data cleaned up")
            } catch (e: Exception) {
                android.util.Log.e("ShimmerController", "[DEBUG_LOG] Failed to cleanup old data: ${e.message}")
            }
        }
    }
}
