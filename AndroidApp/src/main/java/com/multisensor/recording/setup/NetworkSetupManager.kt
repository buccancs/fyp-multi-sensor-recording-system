package com.multisensor.recording.setup

import android.content.Context
import android.util.Log
import com.multisensor.recording.calibration.CalibrationManager
import com.multisensor.recording.network.DataTransferManager
import com.multisensor.recording.network.FaultToleranceManager
import com.multisensor.recording.network.PcCommunicationClient
import com.multisensor.recording.network.SharedProtocolClient

/**
 * Manager for network setup (PC communication, fault tolerance, data transfer, calibration)
 * Extracted from MainActivity to follow Single Responsibility Principle
 */
class NetworkSetupManager(private val context: Context) {
    
    companion object {
        private const val TAG = "NetworkSetupManager"
    }
    
    // Functional requirement components
    lateinit var pcCommunicationClient: PcCommunicationClient
    lateinit var sharedProtocolClient: SharedProtocolClient
    lateinit var faultToleranceManager: FaultToleranceManager
    lateinit var dataTransferManager: DataTransferManager
    lateinit var calibrationManager: CalibrationManager
    
    private var isInitialized = false
    
    /**
     * Initialize all network and communication components
     */
    fun initializeNetwork(
        onPcConnectionChange: (Boolean, String) -> Unit,
        onSharedProtocolMessage: (com.multisensor.recording.network.SharedProtocolMessage) -> Unit,
        onSystemHealth: (Boolean, Map<String, Boolean>) -> Unit,
        onDataTransferComplete: (Boolean, String?, Map<String, Any>?) -> Unit
    ): Boolean {
        return try {
            Log.i(TAG, "Initializing network components")
            
            // Initialize functional requirement components
            pcCommunicationClient = PcCommunicationClient()
            sharedProtocolClient = SharedProtocolClient()
            faultToleranceManager = FaultToleranceManager(context)
            dataTransferManager = DataTransferManager(context)
            calibrationManager = CalibrationManager(context)
            
            // Setup callbacks
            setupNetworkCallbacks(
                onPcConnectionChange,
                onSharedProtocolMessage,
                onSystemHealth,
                onDataTransferComplete
            )
            
            isInitialized = true
            Log.i(TAG, "Network components initialized successfully")
            true
            
        } catch (e: Exception) {
            Log.e(TAG, "Failed to initialize network components", e)
            false
        }
    }
    
    /**
     * Setup callbacks for network components
     */
    private fun setupNetworkCallbacks(
        onPcConnectionChange: (Boolean, String) -> Unit,
        onSharedProtocolMessage: (com.multisensor.recording.network.SharedProtocolMessage) -> Unit,
        onSystemHealth: (Boolean, Map<String, Boolean>) -> Unit,
        onDataTransferComplete: (Boolean, String?, Map<String, Any>?) -> Unit
    ) {
        // PC Communication callbacks (legacy)
        pcCommunicationClient.setConnectionCallback { connected, message ->
            onPcConnectionChange(connected, message)
        }
        
        // Shared Protocol Communication callbacks (harmonized)
        sharedProtocolClient.setConnectionCallback { connected, message ->
            onPcConnectionChange(connected, message)
        }
        
        // Shared Protocol Command callbacks
        sharedProtocolClient.setCommandCallback { protocolMessage ->
            onSharedProtocolMessage(protocolMessage)
        }
        
        // Fault tolerance callbacks
        faultToleranceManager.setSystemHealthCallback { isHealthy, deviceHealthMap ->
            onSystemHealth(isHealthy, deviceHealthMap)
        }
        
        // Data transfer callbacks
        dataTransferManager.setTransferCompleteCallback { success, errorMessage, results ->
            onDataTransferComplete(success, errorMessage, results)
        }
    }
    
    /**
     * Check if network components are initialized
     */
    fun isNetworkReady(): Boolean {
        return isInitialized
    }
    
    /**
     * Check if system is healthy
     */
    fun isSystemHealthy(): Boolean {
        return if (::faultToleranceManager.isInitialized) {
            faultToleranceManager.isSystemHealthy()
        } else false
    }
    
    /**
     * Cleanup network resources
     */
    fun cleanup() {
        try {
            if (::pcCommunicationClient.isInitialized) pcCommunicationClient.cleanup()
            if (::faultToleranceManager.isInitialized) faultToleranceManager.cleanup()
            if (::dataTransferManager.isInitialized) dataTransferManager.cleanup()
            
            isInitialized = false
            Log.i(TAG, "Network components cleaned up")
        } catch (e: Exception) {
            Log.e(TAG, "Error during network cleanup", e)
        }
    }
}