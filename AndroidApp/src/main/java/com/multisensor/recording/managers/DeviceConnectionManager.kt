package com.multisensor.recording.managers

import android.content.Context
import android.hardware.camera2.CameraManager
import android.view.SurfaceView
import android.view.TextureView
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.delay
import kotlinx.coroutines.withContext
import kotlinx.coroutines.Dispatchers
import com.multisensor.recording.recording.CameraRecorder
import com.multisensor.recording.recording.ThermalRecorder
import com.multisensor.recording.recording.ShimmerRecorder
import com.multisensor.recording.network.JsonSocketClient
import com.multisensor.recording.network.NetworkConfiguration
import com.multisensor.recording.network.ServerConfiguration
import com.multisensor.recording.util.Logger
import dagger.hilt.android.qualifiers.ApplicationContext
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class DeviceConnectionManager @Inject constructor(
    @ApplicationContext private val context: Context,
    private val cameraRecorder: CameraRecorder,
    private val thermalRecorder: ThermalRecorder,
    private val shimmerRecorder: ShimmerRecorder,
    private val jsonSocketClient: JsonSocketClient,
    private val networkConfiguration: NetworkConfiguration,
    private val logger: Logger
) {

    data class DeviceConnectionState(
        val cameraConnected: Boolean = false,
        val thermalConnected: Boolean = false,
        val shimmerConnected: Boolean = false,
        val pcConnected: Boolean = false,
        val isInitializing: Boolean = false,
        val isScanning: Boolean = false,
        val connectionError: String? = null,
        val deviceInfo: DeviceInfo = DeviceInfo()
    )

    data class DeviceInfo(
        val availableCameras: List<String> = emptyList(),
        val shimmerDevices: List<ShimmerDeviceInfo> = emptyList(),
        val pcServerAddress: String? = null,
        val thermalCameraModel: String? = null
    )

    data class ShimmerDeviceInfo(
        val macAddress: String,
        val deviceName: String,
        val connectionType: String,
        val isConnected: Boolean = false
    )

    private val _connectionState = MutableStateFlow(DeviceConnectionState())
    val connectionState: StateFlow<DeviceConnectionState> = _connectionState.asStateFlow()

    suspend fun initializeAllDevices(
        textureView: TextureView? = null,
        thermalSurfaceView: SurfaceView? = null
    ): Result<String> {
        return try {
            logger.info("Initializing all devices...")
            _connectionState.value = _connectionState.value.copy(isInitializing = true)

            val results = mutableListOf<String>()
            var successCount = 0
            var totalDevices = 0

            totalDevices++
            val cameraResult = initializeCamera(textureView)
            if (cameraResult.isSuccess) {
                successCount++
                results.add("Camera: OK")
            } else {
                results.add("Camera: ${cameraResult.exceptionOrNull()?.message ?: "Failed"}")
            }

            totalDevices++
            val thermalResult = initializeThermalCamera(thermalSurfaceView)
            if (thermalResult.isSuccess) {
                successCount++
                results.add("Thermal: OK")
            } else {
                results.add("Thermal: ${thermalResult.exceptionOrNull()?.message ?: "N/A"}")
            }

            totalDevices++
            val shimmerResult = initializeShimmerSensors()
            if (shimmerResult.isSuccess) {
                successCount++
                results.add("Shimmer: OK")
            } else {
                results.add("Shimmer: ${shimmerResult.exceptionOrNull()?.message ?: "N/A"}")
            }

            val summary = "Device initialization: $successCount/$totalDevices successful - ${results.joinToString(", ")}"

            _connectionState.value = _connectionState.value.copy(isInitializing = false)

            logger.info("Device initialization completed: $summary")
            Result.success(summary)

        } catch (e: Exception) {
            logger.error("Device initialization failed", e)
            _connectionState.value = _connectionState.value.copy(
                isInitializing = false,
                connectionError = "Initialization failed: ${e.message}"
            )
            Result.failure(e)
        }
    }

    private suspend fun initializeCamera(textureView: TextureView?): Result<Unit> {
        return try {
            if (textureView != null) {
                logger.info("Initializing camera...")
                val success = cameraRecorder.initialize(textureView)
                if (success) {
                    val previewSession = cameraRecorder.startSession(recordVideo = false, captureRaw = false)
                    _connectionState.value = _connectionState.value.copy(cameraConnected = true)
                    logger.info("Camera initialized successfully")
                    Result.success(Unit)
                } else {
                    Result.failure(RuntimeException("Camera initialization failed"))
                }
            } else {
                Result.failure(IllegalArgumentException("TextureView required"))
            }
        } catch (e: Exception) {
            logger.error("Camera initialization error", e)
            Result.failure(e)
        }
    }

    private suspend fun initializeThermalCamera(surfaceView: SurfaceView?): Result<Unit> {
        return try {
            logger.info("Initializing thermal camera...")
            val success = thermalRecorder.initialize(surfaceView)
            if (success) {
                val previewStarted = thermalRecorder.startPreview()
                _connectionState.value = _connectionState.value.copy(thermalConnected = success)
                logger.info("Thermal camera initialized")
                Result.success(Unit)
            } else {
                Result.failure(RuntimeException("Thermal camera not available"))
            }
        } catch (e: Exception) {
            logger.error("Thermal camera initialization error", e)
            Result.failure(e)
        }
    }

    private suspend fun initializeShimmerSensors(): Result<Unit> {
        return try {
            val success = shimmerRecorder.initialize()
            _connectionState.value = _connectionState.value.copy(shimmerConnected = success)
            if (success) {
                logger.info("Shimmer sensors initialized successfully")
                Result.success(Unit)
            } else {
                logger.warning("No Shimmer sensors available")
                Result.failure(RuntimeException("Shimmer sensors not available"))
            }
        } catch (e: Exception) {
            logger.error("Shimmer initialization error", e)
            Result.failure(e)
        }
    }

    suspend fun connectToPC(): Result<String> {
        return try {
            logger.info("Connecting to PC server...")

            // Try to discover server automatically first
            val discoveredServer = discoverPCServer()
            val serverConfig = if (discoveredServer != null) {
                logger.info("Discovered PC server at: ${discoveredServer.getJsonAddress()}")
                networkConfiguration.updateServerConfiguration(discoveredServer)
                discoveredServer
            } else {
                logger.info("Using configured server address")
                networkConfiguration.getServerConfiguration()
            }

            jsonSocketClient.configure(serverConfig.serverIp, serverConfig.jsonPort)
            jsonSocketClient.connect()

            delay(2000)

            val isConnected = jsonSocketClient.isConnected()

            if (isConnected) {
                val address = serverConfig.getJsonAddress()
                _connectionState.value = _connectionState.value.copy(
                    pcConnected = true,
                    deviceInfo = _connectionState.value.deviceInfo.copy(pcServerAddress = address)
                )
                val message = "Connected to PC at $address"
                logger.info(message)
                Result.success(message)
            } else {
                val message = "Failed to connect to PC at ${serverConfig.getJsonAddress()}"
                logger.error(message)
                Result.failure(RuntimeException(message))
            }

        } catch (e: Exception) {
            logger.error("PC connection error", e)
            _connectionState.value = _connectionState.value.copy(
                connectionError = "PC connection failed: ${e.message}"
            )
            Result.failure(e)
        }
    }

    suspend fun disconnectFromPC(): Result<Unit> {
        return try {
            logger.info("Disconnecting from PC server...")
            jsonSocketClient.disconnect()

            _connectionState.value = _connectionState.value.copy(
                pcConnected = false,
                deviceInfo = _connectionState.value.deviceInfo.copy(pcServerAddress = null)
            )

            logger.info("Disconnected from PC server")
            Result.success(Unit)

        } catch (e: Exception) {
            logger.error("PC disconnection error", e)
            Result.failure(e)
        }
    }

    suspend fun scanForDevices(): Result<DeviceInfo> {
        return try {
            logger.info("Scanning for devices...")
            _connectionState.value = _connectionState.value.copy(isScanning = true)

            val cameraManager = context.getSystemService(Context.CAMERA_SERVICE) as CameraManager
            val availableCameras = try {
                cameraManager.cameraIdList.toList()
            } catch (e: Exception) {
                logger.warning("Camera scan failed: ${e.message}")
                emptyList()
            }

            val shimmerDevices = try {
                shimmerRecorder.scanForDevices().map { (mac, name) ->
                    ShimmerDeviceInfo(
                        macAddress = mac,
                        deviceName = name,
                        connectionType = "Bluetooth",
                        isConnected = false
                    )
                }
            } catch (e: Exception) {
                logger.warning("Shimmer scan failed: ${e.message}")
                emptyList()
            }

            val thermalModel = try {
                if (thermalRecorder.isThermalCameraAvailable()) "Topdon Camera" else null
            } catch (e: Exception) {
                logger.warning("Thermal check failed: ${e.message}")
                null
            }

            val deviceInfo = DeviceInfo(
                availableCameras = availableCameras,
                shimmerDevices = shimmerDevices,
                thermalCameraModel = thermalModel
            )

            _connectionState.value = _connectionState.value.copy(
                isScanning = false,
                deviceInfo = deviceInfo
            )

            val summary = "Found: ${availableCameras.size} cameras, ${shimmerDevices.size} Shimmer devices, thermal: ${thermalModel != null}"
            logger.info("Device scan completed: $summary")

            Result.success(deviceInfo)

        } catch (e: Exception) {
            logger.error("Device scan error", e)
            _connectionState.value = _connectionState.value.copy(
                isScanning = false,
                connectionError = "Scan failed: ${e.message}"
            )
            Result.failure(e)
        }
    }

    suspend fun connectShimmerDevice(
        macAddress: String,
        deviceName: String,
        connectionType: com.shimmerresearch.android.manager.ShimmerBluetoothManagerAndroid.BT_TYPE
    ): Result<Unit> {
        return try {
            logger.info("Connecting to Shimmer device: $deviceName ($macAddress)")

            val success = shimmerRecorder.connectSingleDevice(macAddress, deviceName, connectionType)

            if (success) {
                val updatedDevices = _connectionState.value.deviceInfo.shimmerDevices.map { device ->
                    if (device.macAddress == macAddress) {
                        device.copy(isConnected = true)
                    } else device
                }

                _connectionState.value = _connectionState.value.copy(
                    shimmerConnected = true,
                    deviceInfo = _connectionState.value.deviceInfo.copy(shimmerDevices = updatedDevices)
                )

                logger.info("Successfully connected to Shimmer device: $deviceName")
                Result.success(Unit)
            } else {
                Result.failure(RuntimeException("Failed to connect to Shimmer device"))
            }

        } catch (e: Exception) {
            logger.error("Shimmer connection error", e)
            Result.failure(e)
        }
    }

    suspend fun refreshDeviceStatus(): Result<String> {
        return try {
            logger.info("Refreshing device status...")

            val cameraConnected = cameraRecorder.isConnected

            val thermalConnected = thermalRecorder.isThermalCameraAvailable()

            val shimmerStatus = shimmerRecorder.getShimmerStatus()
            val shimmerConnected = shimmerStatus.isConnected

            val pcConnected = jsonSocketClient.isConnected()

            _connectionState.value = _connectionState.value.copy(
                cameraConnected = cameraConnected,
                thermalConnected = thermalConnected,
                shimmerConnected = shimmerConnected,
                pcConnected = pcConnected
            )

            val summary = "Status: Camera=$cameraConnected, Thermal=$thermalConnected, Shimmer=$shimmerConnected, PC=$pcConnected"
            logger.info("Device status refreshed: $summary")

            Result.success(summary)

        } catch (e: Exception) {
            logger.error("Device status refresh error", e)
            Result.failure(e)
        }
    }

    fun getCurrentState(): DeviceConnectionState = _connectionState.value

    fun clearError() {
        _connectionState.value = _connectionState.value.copy(connectionError = null)
    }

    private suspend fun discoverPCServer(): ServerConfiguration? {
        return withContext(Dispatchers.IO) {
            try {
                logger.info("Discovering PC server on local network...")
                
                val currentConfig = networkConfiguration.getServerConfiguration()
                
                // List of common IPs to try based on current network
                val baseIp = currentConfig.serverIp.substringBeforeLast(".")
                val ipsToTry = listOf(
                    currentConfig.serverIp, // Try configured IP first
                    "$baseIp.100",
                    "$baseIp.101", 
                    "$baseIp.1",   // Router
                    "$baseIp.10",
                    "$baseIp.50",
                    "192.168.1.100",
                    "192.168.0.100",
                    "10.0.0.100"
                )
                
                for (ip in ipsToTry) {
                    try {
                        logger.debug("Trying PC server at: $ip:${currentConfig.jsonPort}")
                        
                        val socket = java.net.Socket()
                        socket.connect(
                            java.net.InetSocketAddress(ip, currentConfig.jsonPort), 
                            2000  // 2 second timeout
                        )
                        socket.close()
                        
                        logger.info("Found responsive server at: $ip:${currentConfig.jsonPort}")
                        return@withContext ServerConfiguration(
                            serverIp = ip,
                            legacyPort = currentConfig.legacyPort,
                            jsonPort = currentConfig.jsonPort
                        )
                        
                    } catch (e: Exception) {
                        logger.debug("No server found at $ip: ${e.message}")
                    }
                }
                
                logger.warning("No PC server discovered on local network")
                null
                
            } catch (e: Exception) {
                logger.error("Error during PC server discovery", e)
                null
            }
        }
    }

    suspend fun checkDeviceCapabilities(): Result<Map<String, Boolean>> {
        return try {
            val capabilities = mutableMapOf<String, Boolean>()

            try {
                capabilities["raw_stage3"] = cameraRecorder.isRawStage3Available()
            } catch (e: Exception) {
                capabilities["raw_stage3"] = false
            }

            try {
                capabilities["thermal_camera"] = thermalRecorder.isThermalCameraAvailable()
            } catch (e: Exception) {
                capabilities["thermal_camera"] = false
            }

            try {
                capabilities["shimmer_streaming"] = shimmerRecorder.isAnyDeviceStreaming()
                capabilities["shimmer_sd_logging"] = shimmerRecorder.isAnyDeviceSDLogging()
            } catch (e: Exception) {
                capabilities["shimmer_streaming"] = false
                capabilities["shimmer_sd_logging"] = false
            }

            logger.info("Device capabilities checked: $capabilities")
            Result.success(capabilities)

        } catch (e: Exception) {
            logger.error("Capability check error", e)
            Result.failure(e)
        }
    }
}
