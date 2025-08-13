package com.multisensor.recording.firebase

import com.google.firebase.analytics.FirebaseAnalytics
import com.google.firebase.analytics.ktx.logEvent
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Firebase Analytics service for tracking app usage and research events
 * Enhanced for comprehensive research workflow analytics
 */
@Singleton
class FirebaseAnalyticsService @Inject constructor(
    private val firebaseAnalytics: FirebaseAnalytics
) {

    // Research Session Events
    
    /**
     * Log recording session start
     */
    fun logRecordingSessionStart(sessionId: String, deviceCount: Int, experimentType: String? = null) {
        firebaseAnalytics.logEvent("recording_session_start") {
            param("session_id", sessionId)
            param("device_count", deviceCount.toLong())
            if (experimentType != null) {
                param("experiment_type", experimentType)
            }
        }
    }

    /**
     * Log recording session end
     */
    fun logRecordingSessionEnd(sessionId: String, durationMs: Long, dataSize: Long, participantCount: Int = 1) {
        firebaseAnalytics.logEvent("recording_session_end") {
            param("session_id", sessionId)
            param("duration_ms", durationMs)
            param("data_size_bytes", dataSize)
            param("participant_count", participantCount.toLong())
        }
    }

    /**
     * Log session pause/resume
     */
    fun logSessionPause(sessionId: String, reason: String) {
        firebaseAnalytics.logEvent("session_paused") {
            param("session_id", sessionId)
            param("pause_reason", reason)
        }
    }

    fun logSessionResume(sessionId: String, pauseDurationMs: Long) {
        firebaseAnalytics.logEvent("session_resumed") {
            param("session_id", sessionId)
            param("pause_duration_ms", pauseDurationMs)
        }
    }

    // Device and Sensor Events

    /**
     * Log GSR sensor connection
     */
    fun logGSRSensorConnected(sensorId: String, sensorType: String = "shimmer", connectionMethod: String = "bluetooth") {
        firebaseAnalytics.logEvent("gsr_sensor_connected") {
            param("sensor_id", sensorId)
            param("sensor_type", sensorType)
            param("connection_method", connectionMethod)
        }
    }

    /**
     * Log GSR sensor disconnection
     */
    fun logGSRSensorDisconnected(sensorId: String, reason: String, dataLoss: Boolean = false) {
        firebaseAnalytics.logEvent("gsr_sensor_disconnected") {
            param("sensor_id", sensorId)
            param("disconnect_reason", reason)
            param("data_loss", if (dataLoss) 1L else 0L)
        }
    }

    /**
     * Log thermal camera usage
     */
    fun logThermalCameraUsed(cameraModel: String, resolution: String, frameRate: Int? = null) {
        firebaseAnalytics.logEvent("thermal_camera_used") {
            param("camera_model", cameraModel)
            param("resolution", resolution)
            if (frameRate != null) {
                param("frame_rate", frameRate.toLong())
            }
        }
    }

    /**
     * Log camera calibration
     */
    fun logCameraCalibration(cameraType: String, success: Boolean, errorCount: Int = 0) {
        firebaseAnalytics.logEvent("camera_calibration") {
            param("camera_type", cameraType)
            param("success", if (success) 1L else 0L)
            param("error_count", errorCount.toLong())
        }
    }

    // Data Quality and Processing Events

    /**
     * Log calibration event
     */
    fun logCalibrationPerformed(calibrationType: String, success: Boolean, duration: Long? = null) {
        firebaseAnalytics.logEvent("calibration_performed") {
            param("calibration_type", calibrationType)
            param("success", if (success) 1L else 0L)
            if (duration != null) {
                param("duration_ms", duration)
            }
        }
    }

    /**
     * Log data quality assessment
     */
    fun logDataQualityCheck(sessionId: String, qualityScore: Float, issues: List<String> = emptyList()) {
        firebaseAnalytics.logEvent("data_quality_check") {
            param("session_id", sessionId)
            param("quality_score", (qualityScore * 100).toLong()) // Store as percentage
            param("issue_count", issues.size.toLong())
            if (issues.isNotEmpty()) {
                param("primary_issue", issues.first())
            }
        }
    }

    /**
     * Log synchronization events
     */
    fun logSynchronizationPerformed(deviceCount: Int, success: Boolean, timeDriftMs: Long? = null) {
        firebaseAnalytics.logEvent("synchronization_performed") {
            param("device_count", deviceCount.toLong())
            param("success", if (success) 1L else 0L)
            if (timeDriftMs != null) {
                param("time_drift_ms", timeDriftMs)
            }
        }
    }

    // Data Export and Analysis Events

    /**
     * Log data export
     */
    fun logDataExport(format: String, fileSizeBytes: Long, sessionCount: Int = 1, exportType: String = "manual") {
        firebaseAnalytics.logEvent("data_export") {
            param("export_format", format)
            param("file_size_bytes", fileSizeBytes)
            param("session_count", sessionCount.toLong())
            param("export_type", exportType)
        }
    }

    /**
     * Log analysis performed
     */
    fun logAnalysisPerformed(analysisType: String, sessionId: String, processingTime: Long) {
        firebaseAnalytics.logEvent("analysis_performed") {
            param("analysis_type", analysisType)
            param("session_id", sessionId)
            param("processing_time_ms", processingTime)
        }
    }

    // User and Research Context Events

    /**
     * Log user authentication
     */
    fun logUserAuthentication(method: String, researcherType: String) {
        firebaseAnalytics.logEvent("user_authentication") {
            param("auth_method", method)
            param("researcher_type", researcherType)
        }
    }

    /**
     * Log research project creation
     */
    fun logResearchProjectCreated(projectType: String, collaboratorCount: Int) {
        firebaseAnalytics.logEvent("research_project_created") {
            param("project_type", projectType)
            param("collaborator_count", collaboratorCount.toLong())
        }
    }

    /**
     * Log participant consent
     */
    fun logParticipantConsent(consentType: String, granted: Boolean) {
        firebaseAnalytics.logEvent("participant_consent") {
            param("consent_type", consentType)
            param("granted", if (granted) 1L else 0L)
        }
    }

    // Error and Performance Events

    /**
     * Log system errors
     */
    fun logSystemError(errorType: String, errorMessage: String, severity: String = "medium") {
        firebaseAnalytics.logEvent("system_error") {
            param("error_type", errorType)
            param("error_message", errorMessage.take(100)) // Limit message length
            param("severity", severity)
        }
    }

    /**
     * Log performance metrics
     */
    fun logPerformanceMetric(metricName: String, value: Long, unit: String) {
        firebaseAnalytics.logEvent("performance_metric") {
            param("metric_name", metricName)
            param("metric_value", value)
            param("metric_unit", unit)
        }
    }

    /**
     * Log battery usage for long sessions
     */
    fun logBatteryUsage(sessionId: String, batteryLevel: Int, duration: Long) {
        firebaseAnalytics.logEvent("battery_usage") {
            param("session_id", sessionId)
            param("battery_level", batteryLevel.toLong())
            param("session_duration_ms", duration)
        }
    }

    // Cloud Storage Events

    /**
     * Log cloud upload
     */
    fun logCloudUpload(fileType: String, fileSizeBytes: Long, success: Boolean, uploadTime: Long? = null) {
        firebaseAnalytics.logEvent("cloud_upload") {
            param("file_type", fileType)
            param("file_size_bytes", fileSizeBytes)
            param("success", if (success) 1L else 0L)
            if (uploadTime != null) {
                param("upload_time_ms", uploadTime)
            }
        }
    }

    /**
     * Log cloud download
     */
    fun logCloudDownload(fileType: String, fileSizeBytes: Long, success: Boolean) {
        firebaseAnalytics.logEvent("cloud_download") {
            param("file_type", fileType)
            param("file_size_bytes", fileSizeBytes)
            param("success", if (success) 1L else 0L)
        }
    }

    // Research Workflow Events

    /**
     * Log experiment workflow step
     */
    fun logWorkflowStep(step: String, sessionId: String, duration: Long? = null) {
        firebaseAnalytics.logEvent("workflow_step") {
            param("step_name", step)
            param("session_id", sessionId)
            if (duration != null) {
                param("step_duration_ms", duration)
            }
        }
    }

    // User Properties for Research Context

    /**
     * Set user properties for research context
     */
    fun setUserProperty(property: String, value: String) {
        firebaseAnalytics.setUserProperty(property, value)
    }

    /**
     * Set researcher type
     */
    fun setResearcherType(researcherType: String) {
        setUserProperty("researcher_type", researcherType)
    }

    /**
     * Set institution
     */
    fun setInstitution(institution: String) {
        setUserProperty("institution", institution)
    }

    /**
     * Set research area
     */
    fun setResearchArea(area: String) {
        setUserProperty("research_area", area)
    }

    /**
     * Set app version for analytics segmentation
     */
    fun setAppVersion(version: String) {
        setUserProperty("app_version", version)
    }
}