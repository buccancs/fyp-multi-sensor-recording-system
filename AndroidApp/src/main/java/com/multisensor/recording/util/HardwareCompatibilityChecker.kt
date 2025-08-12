package com.multisensor.recording.util

import android.content.Context
import android.hardware.camera2.CameraCharacteristics
import android.hardware.camera2.CameraManager
import android.hardware.usb.UsbManager
import android.os.Build
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class HardwareCompatibilityChecker @Inject constructor(
    private val context: Context,
    private val logger: Logger
) {
    
    data class CompatibilityReport(
        val deviceModel: String,
        val androidVersion: Int,
        val cameraCompatibility: CameraCompatibility,
        val thermalCompatibility: ThermalCompatibility,
        val overallStatus: CompatibilityStatus,
        val recommendations: List<String>
    )
    
    data class CameraCompatibility(
        val basicCameraAvailable: Boolean,
        val advancedFeaturesAvailable: Boolean,
        val rawCaptureSupported: Boolean,
        val fourKVideoSupported: Boolean,
        val frontCameraAvailable: Boolean,
        val issues: List<String>
    )
    
    data class ThermalCompatibility(
        val usbHostSupported: Boolean,
        val supportedDevicesConnected: Int,
        val simulationModeRecommended: Boolean,
        val issues: List<String>
    )
    
    enum class CompatibilityStatus {
        EXCELLENT,    // All features work perfectly
        GOOD,         // Most features work, minor limitations
        COMPATIBLE,   // Basic functionality works
        LIMITED       // Significant limitations, but still usable
    }
    
    fun checkCompatibility(): CompatibilityReport {
        logger.info("Running hardware compatibility check...")
        
        val deviceModel = "${Build.MANUFACTURER} ${Build.MODEL}"
        val androidVersion = Build.VERSION.SDK_INT
        
        val cameraCompat = checkCameraCompatibility()
        val thermalCompat = checkThermalCompatibility()
        
        val overallStatus = determineOverallStatus(cameraCompat, thermalCompat)
        val recommendations = generateRecommendations(cameraCompat, thermalCompat, overallStatus)
        
        return CompatibilityReport(
            deviceModel = deviceModel,
            androidVersion = androidVersion,
            cameraCompatibility = cameraCompat,
            thermalCompatibility = thermalCompat,
            overallStatus = overallStatus,
            recommendations = recommendations
        )
    }
    
    private fun checkCameraCompatibility(): CameraCompatibility {
        val issues = mutableListOf<String>()
        var basicAvailable = false
        var advancedAvailable = false
        var rawSupported = false
        var fourKSupported = false
        var frontAvailable = false
        
        try {
            val cameraManager = context.getSystemService(Context.CAMERA_SERVICE) as CameraManager
            val cameraIds = cameraManager.cameraIdList
            
            if (cameraIds.isEmpty()) {
                issues.add("No cameras detected on device")
                return CameraCompatibility(false, false, false, false, false, issues)
            }
            
            for (cameraId in cameraIds) {
                try {
                    val characteristics = cameraManager.getCameraCharacteristics(cameraId)
                    val facing = characteristics.get(CameraCharacteristics.LENS_FACING)
                    
                    if (facing == CameraCharacteristics.LENS_FACING_FRONT) {
                        frontAvailable = true
                    }
                    
                    if (facing == CameraCharacteristics.LENS_FACING_BACK) {
                        basicAvailable = true
                        
                        val capabilities = characteristics.get(CameraCharacteristics.REQUEST_AVAILABLE_CAPABILITIES)
                        val hasBackwardCompat = capabilities?.contains(
                            CameraCharacteristics.REQUEST_AVAILABLE_CAPABILITIES_BACKWARD_COMPATIBLE
                        ) == true
                        
                        if (hasBackwardCompat) {
                            val hardwareLevel = characteristics.get(CameraCharacteristics.INFO_SUPPORTED_HARDWARE_LEVEL)
                            val isAdvanced = hardwareLevel == CameraCharacteristics.INFO_SUPPORTED_HARDWARE_LEVEL_3 ||
                                           hardwareLevel == CameraCharacteristics.INFO_SUPPORTED_HARDWARE_LEVEL_FULL
                            
                            if (isAdvanced) {
                                advancedAvailable = true
                            }
                            
                            val hasRaw = capabilities.contains(CameraCharacteristics.REQUEST_AVAILABLE_CAPABILITIES_RAW)
                            if (hasRaw) {
                                rawSupported = true
                            }
                            
                            val streamConfig = characteristics.get(CameraCharacteristics.SCALER_STREAM_CONFIGURATION_MAP)
                            val videoSizes = streamConfig?.getOutputSizes(android.media.MediaRecorder::class.java)
                            val has4K = videoSizes?.any { it.width >= 3840 && it.height >= 2160 } == true
                            if (has4K) {
                                fourKSupported = true
                            }
                        }
                    }
                } catch (e: Exception) {
                    logger.debug("Error checking camera $cameraId", e)
                    issues.add("Camera $cameraId access error: ${e.message}")
                }
            }
            
            if (!basicAvailable) {
                issues.add("No usable back camera found")
            }
            
        } catch (e: Exception) {
            logger.error("Error during camera compatibility check", e)
            issues.add("Camera system access error: ${e.message}")
        }
        
        return CameraCompatibility(
            basicCameraAvailable = basicAvailable,
            advancedFeaturesAvailable = advancedAvailable,
            rawCaptureSupported = rawSupported,
            fourKVideoSupported = fourKSupported,
            frontCameraAvailable = frontAvailable,
            issues = issues
        )
    }
    
    private fun checkThermalCompatibility(): ThermalCompatibility {
        val issues = mutableListOf<String>()
        var usbHostSupported = false
        var supportedDevicesConnected = 0
        var simulationRecommended = true
        
        try {
            // Check USB host support
            val packageManager = context.packageManager
            usbHostSupported = packageManager.hasSystemFeature("android.hardware.usb.host")
            
            if (!usbHostSupported) {
                issues.add("Device does not support USB host mode")
            }
            
            // Check for connected USB devices
            val usbManager = context.getSystemService(Context.USB_SERVICE) as UsbManager
            val connectedDevices = usbManager.deviceList
            
            // Check for supported thermal camera product IDs
            val supportedProductIds = intArrayOf(0x3901, 0x5840, 0x5830, 0x5838, 0x5841, 0x5842, 0x3902, 0x3903)
            
            connectedDevices.values.forEach { device ->
                if (supportedProductIds.contains(device.productId)) {
                    supportedDevicesConnected++
                    simulationRecommended = false
                }
            }
            
            if (connectedDevices.isEmpty()) {
                issues.add("No USB devices connected")
            } else if (supportedDevicesConnected == 0) {
                issues.add("No supported thermal cameras detected among ${connectedDevices.size} USB devices")
            }
            
        } catch (e: Exception) {
            logger.error("Error during thermal compatibility check", e)
            issues.add("USB system access error: ${e.message}")
        }
        
        return ThermalCompatibility(
            usbHostSupported = usbHostSupported,
            supportedDevicesConnected = supportedDevicesConnected,
            simulationModeRecommended = simulationRecommended,
            issues = issues
        )
    }
    
    private fun determineOverallStatus(
        camera: CameraCompatibility,
        thermal: ThermalCompatibility
    ): CompatibilityStatus {
        return when {
            camera.advancedFeaturesAvailable && thermal.supportedDevicesConnected > 0 -> CompatibilityStatus.EXCELLENT
            camera.basicCameraAvailable && thermal.usbHostSupported -> CompatibilityStatus.GOOD
            camera.basicCameraAvailable -> CompatibilityStatus.COMPATIBLE
            else -> CompatibilityStatus.LIMITED
        }
    }
    
    private fun generateRecommendations(
        camera: CameraCompatibility,
        thermal: ThermalCompatibility,
        status: CompatibilityStatus
    ): List<String> {
        val recommendations = mutableListOf<String>()
        
        when (status) {
            CompatibilityStatus.EXCELLENT -> {
                recommendations.add("✅ Device fully compatible - all features available")
                recommendations.add("🎥 RAW capture and 4K recording supported")
                recommendations.add("🌡️ Thermal camera functionality active")
            }
            CompatibilityStatus.GOOD -> {
                recommendations.add("✅ Device compatible - most features available")
                if (!camera.rawCaptureSupported) {
                    recommendations.add("⚠️ RAW capture not supported - using standard mode")
                }
                if (thermal.supportedDevicesConnected == 0) {
                    recommendations.add("🌡️ Connect Topdon thermal camera for full functionality")
                }
            }
            CompatibilityStatus.COMPATIBLE -> {
                recommendations.add("✅ Device compatible - basic features available")
                recommendations.add("📱 Camera recording works in standard mode")
                recommendations.add("🌡️ Thermal camera simulation mode recommended")
                if (!camera.fourKVideoSupported) {
                    recommendations.add("📹 4K recording not supported - using best available resolution")
                }
            }
            CompatibilityStatus.LIMITED -> {
                recommendations.add("⚠️ Limited compatibility - app works with restrictions")
                recommendations.add("📱 Enable simulation modes for missing hardware")
                recommendations.add("🔧 Check camera permissions in Android Settings")
                recommendations.add("💡 Many features still work without camera preview")
            }
        }
        
        // Add specific recommendations for common issues
        if (camera.issues.any { it.contains("permission") }) {
            recommendations.add("🔧 Grant camera permissions in Android Settings > Apps > MultiSensor Recording")
        }
        
        if (!thermal.usbHostSupported) {
            recommendations.add("🌡️ Thermal camera requires USB OTG support - use simulation mode")
        }
        
        return recommendations
    }
}