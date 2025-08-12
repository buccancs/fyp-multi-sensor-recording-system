package com.multisensor.recording.controllers.demo

import android.content.Context
import com.multisensor.recording.controllers.RecordingController

class RecordingControllerDemo {

    private val recordingController = RecordingController()

    fun demonstrateStatePersistence(context: Context) {
        println("=== State Persistence Demo ===")

        recordingController.initializeStatePersistence(context)

        val state = recordingController.getCurrentState()
        println("Initial state: $state")

        recordingController.setRecordingQuality(RecordingController.RecordingQuality.HIGH)
        val newState = recordingController.getCurrentState()
        println("State after quality change: $newState")
    }

    fun demonstrateQualityManagement() {
        println("\n=== Quality Management Demo ===")

        val qualities = recordingController.getAvailableQualities()
        println("Available qualities: ${qualities.map { it.displayName }}")

        for (quality in qualities) {
            val details = recordingController.getQualityDetails(quality)
            println("Quality ${quality.displayName}:")
            details.forEach { (key, value) ->
                println("  $key: $value")
            }
        }

        println("Current quality: ${recordingController.getCurrentQuality().displayName}")
    }

    fun demonstrateServiceMonitoring() {
        println("\n=== Service Connection Monitoring Demo ===")

        val initialState = recordingController.serviceConnectionState.value
        println("Initial service state: $initialState")

        recordingController.handleServiceConnectionStatus(true)
        println("After connecting: ${recordingController.serviceConnectionState.value}")

        recordingController.updateServiceHeartbeat()
        println("Service healthy: ${recordingController.isServiceHealthy()}")

        recordingController.handleServiceConnectionStatus(false)
        println("After disconnecting: ${recordingController.serviceConnectionState.value}")
    }

    fun demonstrateSessionMetadata() {
        println("\n=== Session Metadata Demo ===")

        val metadata = recordingController.getSessionMetadata()
        println("Session metadata:")
        metadata.forEach { (key, value) ->
            println("  $key: $value")
        }
    }

    fun demonstrateRecordingStatus() {
        println("\n=== Recording Status Demo ===")

        val status = recordingController.getRecordingStatus()
        println("Recording status:")
        println(status)
    }

    fun demonstrateAnalyticsIntegration(context: Context) {
        println("\n=== Analytics Integration Demo ===")

        val performanceMetrics = recordingController.getCurrentPerformanceMetrics()
        println("Current Performance Metrics:")
        println("  Memory Usage: ${performanceMetrics.memoryUsageMB} MB")
        println("  CPU Usage: ${performanceMetrics.cpuUsagePercent}%")
        println("  Storage Write Rate: ${performanceMetrics.storageWriteRateMBps} MB/s")
        println("  Frame Drop Rate: ${performanceMetrics.frameDropRate}")
        println("  Thermal State: ${performanceMetrics.thermalState}")

        val qualityMetrics = recordingController.getCurrentQualityMetrics()
        println("\nCurrent Quality Metrics:")
        println("  Overall Quality Score: ${qualityMetrics.overallQualityScore}")
        println("  Recording Efficiency: ${qualityMetrics.recordingEfficiency}")
        println("  Frame Stability: ${qualityMetrics.frameStability}")

        val (recommendedQuality, reasoning) = recordingController.getIntelligentQualityRecommendation(context)
        println("\nIntelligent Quality Recommendation:")
        println("  Recommended Quality: ${recommendedQuality.displayName}")
        println("  Reasoning: $reasoning")

        val healthCheck = recordingController.performSystemHealthCheck(context)
        println("\nSystem Health Check:")
        healthCheck.forEach { (key, value) ->
            println("  $key: $value")
        }

        val optimisations = recordingController.optimizeRecordingSession(context)
        println("\nSession Optimisation Recommendations:")
        if (optimisations.containsKey("analytics_disabled")) {
            println("  Analytics is disabled")
        } else {
            optimisations.forEach { (key, value) ->
                println("  $key: $value")
            }
        }
    }

    fun demonstrateAdvancedAnalytics() {
        println("\n=== Advanced Analytics Demo ===")

        val analyticsData = recordingController.getAnalyticsData()
        println("Analytics Data Summary:")

        if (analyticsData.containsKey("analytics_disabled")) {
            println("  Analytics is currently disabled")
        } else {
            analyticsData.forEach { (category, data) ->
                println("\n$category:")
                when (data) {
                    is Map<*, *> -> {
                        data.forEach { (key, value) ->
                            println("    $key: $value")
                        }
                    }

                    else -> println("    $data")
                }
            }
        }
    }

    fun runCompleteDemo(context: Context) {
        println("RecordingController Enhanced Features Demo")
        println("==========================================")

        try {
            demonstrateQualityManagement()
            demonstrateServiceMonitoring()
            demonstrateSessionMetadata()
            demonstrateRecordingStatus()
            demonstrateStatePersistence(context)
            demonstratePrerequisiteValidation(context)
            demonstrateAnalyticsIntegration(context)
            demonstrateAdvancedAnalytics()

            println("\n=== Demo Complete ===")
            println("All enhanced features including advanced analytics demonstrated successfully!")

        } catch (e: Exception) {
            println("Demo error: ${e.message}")
            e.printStackTrace()
        }
    }

    fun demonstratePrerequisiteValidation(context: Context) {
        println("\n=== Prerequisite Validation Demo ===")

        val isValid = recordingController.validateRecordingPrerequisites(context)
        println("Prerequisites valid: $isValid")

        val recommendedQuality = recordingController.getRecommendedQuality(context)
        println("Recommended quality: ${recommendedQuality.displayName}")
    }
}
