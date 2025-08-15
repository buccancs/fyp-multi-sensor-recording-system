package com.multisensor.recording.setup

import android.content.Context
import android.util.Log
import com.multisensor.recording.config.ConfigurationManager
import com.multisensor.recording.performance.PerformanceMonitor
import com.multisensor.recording.scalability.ScalabilityManager
import com.multisensor.recording.security.SecurityManager
import com.multisensor.recording.util.Logger
import com.multisensor.recording.validation.DataValidationService

/**
 * Manager for application-level setup (configuration, security, validation, performance, scalability)
 * Extracted from MainActivity to follow Single Responsibility Principle
 */
class ApplicationSetupManager(private val context: Context) {
    
    companion object {
        private const val TAG = "ApplicationSetupManager"
    }
    
    // Application components
    lateinit var configurationManager: ConfigurationManager
    lateinit var securityManager: SecurityManager 
    lateinit var dataValidationService: DataValidationService
    lateinit var performanceMonitor: PerformanceMonitor
    lateinit var scalabilityManager: ScalabilityManager
    
    private var isInitialized = false
    
    /**
     * Initialize all application-level components
     */
    fun initializeApplication(
        onSecurityWarnings: (SecurityManager.SecurityReport) -> Unit,
        onPerformanceAlert: (PerformanceMonitor.PerformanceAlert) -> Unit
    ): Boolean {
        return try {
            Log.i(TAG, "Initializing application components")
            
            // Initialize configuration manager first (NFR8)
            configurationManager = ConfigurationManager(context)
            val configStatus = configurationManager.initializeConfiguration()
            if (configStatus != ConfigurationManager.ConfigurationStatus.LOADED) {
                Logger.w(TAG, "Configuration system not properly loaded")
            }
            
            // Initialize security manager (NFR5)
            securityManager = SecurityManager(context)
            val securityStatus = securityManager.initializeSecurity()
            if (securityStatus != SecurityManager.SecurityStatus.SECURE) {
                Logger.w(TAG, "Security system not properly configured")
                onSecurityWarnings(securityManager.generateSecurityReport())
            }
            
            // Initialize data validation service (NFR4)
            dataValidationService = DataValidationService(context)
            dataValidationService.setValidationEnabled(true)
            
            // Initialize performance monitor (NFR1)
            performanceMonitor = PerformanceMonitor(context)
            performanceMonitor.setPerformanceAlertCallback(onPerformanceAlert)
            performanceMonitor.startMonitoring()
            
            // Initialize scalability manager (NFR7)
            scalabilityManager = ScalabilityManager(context)
            val scalingStatus = scalabilityManager.initializeScaling()
            if (scalingStatus != ScalabilityManager.ScalingStatus.INITIALIZED) {
                Logger.w(TAG, "Scalability manager initialization failed")
            }
            
            isInitialized = true
            Log.i(TAG, "Application components initialized successfully")
            true
            
        } catch (e: Exception) {
            Log.e(TAG, "Failed to initialize application components", e)
            false
        }
    }
    
    /**
     * Check if application components are initialized
     */
    fun isApplicationReady(): Boolean {
        return isInitialized
    }
    
    /**
     * Get security report for diagnostics
     */
    fun getSecurityReport(): SecurityManager.SecurityReport? {
        return if (::securityManager.isInitialized) {
            securityManager.generateSecurityReport()
        } else null
    }
    
    /**
     * Cleanup application resources
     */
    fun cleanup() {
        try {
            if (::performanceMonitor.isInitialized) {
                performanceMonitor.stopMonitoring()
            }
            if (::scalabilityManager.isInitialized) {
                scalabilityManager.cleanup()
            }
            isInitialized = false
            Log.i(TAG, "Application components cleaned up")
        } catch (e: Exception) {
            Log.e(TAG, "Error during application cleanup", e)
        }
    }
}