package com.multisensor.recording.firebase

import com.google.firebase.analytics.FirebaseAnalytics
import com.google.firebase.analytics.ktx.logEvent
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Firebase Analytics service for tracking app usage and research events
 */
@Singleton
class FirebaseAnalyticsService @Inject constructor(
    private val firebaseAnalytics: FirebaseAnalytics
) {

    /**
     * Log recording session start
     */
    fun logRecordingSessionStart(sessionId: String, deviceCount: Int) {
        firebaseAnalytics.logEvent("recording_session_start") {
            param("session_id", sessionId)
            param("device_count", deviceCount.toLong())
        }
    }

    /**
     * Log recording session end
     */
    fun logRecordingSessionEnd(sessionId: String, durationMs: Long, dataSize: Long) {
        firebaseAnalytics.logEvent("recording_session_end") {
            param("session_id", sessionId)
            param("duration_ms", durationMs)
            param("data_size_bytes", dataSize)
        }
    }

    /**
     * Log GSR sensor connection
     */
    fun logGSRSensorConnected(sensorId: String) {
        firebaseAnalytics.logEvent("gsr_sensor_connected") {
            param("sensor_id", sensorId)
        }
    }

    /**
     * Log thermal camera usage
     */
    fun logThermalCameraUsed(cameraModel: String, resolution: String) {
        firebaseAnalytics.logEvent("thermal_camera_used") {
            param("camera_model", cameraModel)
            param("resolution", resolution)
        }
    }

    /**
     * Log calibration event
     */
    fun logCalibrationPerformed(calibrationType: String, success: Boolean) {
        firebaseAnalytics.logEvent("calibration_performed") {
            param("calibration_type", calibrationType)
            param("success", if (success) 1L else 0L)
        }
    }

    /**
     * Log data export
     */
    fun logDataExport(format: String, fileSizeBytes: Long) {
        firebaseAnalytics.logEvent("data_export") {
            param("export_format", format)
            param("file_size_bytes", fileSizeBytes)
        }
    }

    /**
     * Set user properties for research context
     */
    fun setUserProperty(property: String, value: String) {
        firebaseAnalytics.setUserProperty(property, value)
    }
}