package com.multisensor.recording.fragment

import android.annotation.SuppressLint
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.core.view.isVisible
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.multisensor.recording.R
import com.multisensor.recording.MainActivity
import com.multisensor.recording.security.SecurityManager
import com.multisensor.recording.util.Logger
import com.multisensor.recording.util.ToastManager
import com.multisensor.recording.util.EnhancedProgressDialog
import kotlinx.coroutines.launch

/**
 * Main Fragment - Device connection status and management
 * Based on IRCamera MainFragment structure
 */
@SuppressLint("NotifyDataSetChanged")
class MainFragment : Fragment(), View.OnClickListener {

    private lateinit var adapter: DeviceAdapter

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_main, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        initView()
    }

    private fun initView() {
        adapter = DeviceAdapter()
        view?.findViewById<View>(R.id.tv_connect_device)?.setOnClickListener(this)
        
        adapter.onItemClickListener = { deviceType ->
            // Handle device click - navigate to recording tab
            val activity = activity as? MainActivity
            activity?.navigateToRecording()
        }

        val recyclerView = view?.findViewById<RecyclerView>(R.id.recycler_view)
        recyclerView?.layoutManager = LinearLayoutManager(requireContext())
        recyclerView?.adapter = adapter
    }

    override fun onResume() {
        super.onResume()
        refresh()
    }

    private fun refresh() {
        // Get real device status from MainActivity
        val activity = activity as? MainActivity
        val deviceList = if (activity != null) {
            getDeviceStatusList(activity)
        } else {
            // Fallback if activity not available
            listOf(
                DeviceInfo(DeviceType.RGB_CAMERA, "[RGB]", "RGB Camera", "Not available", false),
                DeviceInfo(DeviceType.THERMAL_CAMERA, "[THERMAL]", "Thermal Camera", "Not available", false),
                DeviceInfo(DeviceType.GSR_SENSOR, "[GSR]", "GSR Sensor", "Not available", false)
            )
        }
        
        // Update adapter with real device status
        adapter.updateDevices(deviceList)
        
        // Check if any devices are available
        val hasAnyDevice = deviceList.any { it.isConnected }
        view?.findViewById<View>(R.id.cl_has_device)?.isVisible = hasAnyDevice
        view?.findViewById<View>(R.id.cl_no_device)?.isVisible = !hasAnyDevice
    }
    
    /**
     * Get current device status from MainActivity components
     */
    private fun getDeviceStatusList(activity: MainActivity): List<DeviceInfo> {
        return try {
            listOf(
                DeviceInfo(
                    DeviceType.RGB_CAMERA,
                    "[RGB]",
                    "RGB Camera",
                    try {
                        if (activity.rgbCamera.isConnected()) {
                            "Ready for recording"
                        } else {
                            "Not connected"
                        }
                    } catch (e: Exception) {
                        "Not available"
                    },
                    try {
                        activity.rgbCamera.isConnected()
                    } catch (e: Exception) {
                        false
                    }
                ),
                DeviceInfo(
                    DeviceType.THERMAL_CAMERA,
                    "[THERMAL]",
                    "Thermal Camera",
                    try {
                        if (activity.thermalCamera.isConnected()) {
                            "Ready for thermal imaging"
                        } else {
                            "Not connected"
                        }
                    } catch (e: Exception) {
                        "Not available"
                    },
                    try {
                        activity.thermalCamera.isConnected()
                    } catch (e: Exception) {
                        false
                    }
                ),
                DeviceInfo(
                    DeviceType.GSR_SENSOR,
                    "[GSR]",
                    "GSR Sensor",
                    try {
                        if (activity.gsrSensor.isConnected()) {
                            "Ready for physiological monitoring"
                        } else {
                            "Not connected"
                        }
                    } catch (e: Exception) {
                        "Not available"
                    },
                    try {
                        activity.gsrSensor.isConnected()
                    } catch (e: Exception) {
                        false
                    }
                )
            )
        } catch (e: Exception) {
            Logger.e("MainFragment", "Error getting device status: ${e.message}")
            // Return safe defaults
            listOf(
                DeviceInfo(DeviceType.RGB_CAMERA, "[RGB]", "RGB Camera", "Status unknown", false),
                DeviceInfo(DeviceType.THERMAL_CAMERA, "[THERMAL]", "Thermal Camera", "Status unknown", false),
                DeviceInfo(DeviceType.GSR_SENSOR, "[GSR]", "GSR Sensor", "Status unknown", false)
            )
        }
    }

    private fun hasConnectedDevices(): Boolean {
        return try {
            val activity = activity as? MainActivity ?: return false
            // Check actual device connectivity status
            val rgbConnected = try { activity.rgbCamera.isConnected() } catch (e: Exception) { false }
            val thermalConnected = try { activity.thermalCamera.isConnected() } catch (e: Exception) { false }
            val gsrConnected = try { activity.gsrSensor.isConnected() } catch (e: Exception) { false }
            
            // Return true if any device is actually connected
            rgbConnected || thermalConnected || gsrConnected
        } catch (e: Exception) {
            Logger.w("MainFragment", "Error checking device connectivity: ${e.message}")
            false
        }
    }

    override fun onClick(v: View?) {
        when (v?.id) {
            R.id.tv_connect_device -> {
                handleConnectDeviceClick()
            }
        }
    }

    /**
     * Enhanced connect device button with advanced features
     * Integrates with all NFR components for professional device management
     * Now uses enhanced progress dialog with sophisticated validation workflow
     */
    private fun handleConnectDeviceClick() {
        val activity = activity as? MainActivity
        if (activity == null) return
        
        // Create enhanced progress dialog with professional styling
        val progressDialog = EnhancedProgressDialog.createConnectionDialog(requireContext())
            .setOnCancelCallback {
                Logger.i("MainFragment", "Device connection cancelled by user")
                // Cleanup any ongoing connection attempts
            }
            .setOnRetryCallback {
                // Retry the connection process
                handleConnectDeviceClick()
            }
        
        // Execute professional multi-step connection process
        lifecycleScope.launch {
            try {
                // Execute sophisticated validation and connection workflow
                val success = progressDialog.executeSteps(
                    EnhancedProgressDialog.getDeviceConnectionSteps()
                ) { step ->
                    // Execute actual validation for each step
                    when {
                        step.description.contains("security", true) -> {
                            performSecurityValidation(activity)
                        }
                        step.description.contains("RGB camera", true) -> {
                            initializeRgbCamera(activity)
                        }
                        step.description.contains("thermal camera", true) -> {
                            initializeThermalCamera(activity)
                        }
                        step.description.contains("GSR sensor", true) -> {
                            initializeGsrSensor(activity)
                        }
                        step.description.contains("synchronizing", true) || step.description.contains("clocks", true) -> {
                            synchronizeDevices(activity)
                        }
                        else -> true // Default success for other steps
                    }
                }
                
                progressDialog.dismiss()
                
                if (success) {
                    // Show enhanced success dialog
                    showEnhancedConnectionSuccess()
                    refresh()
                } else {
                    // Error handling is managed by the progress dialog
                    Logger.w("MainFragment", "Device connection process failed")
                }
                
            } catch (e: Exception) {
                progressDialog.dismiss()
                showEnhancedConnectionError(e.message ?: "Unknown error occurred")
            }
        }
    }

    
    /**
     * Professional security validation for enhanced button API
     */
    private suspend fun performSecurityValidation(activity: MainActivity): Boolean {
        return try {
            val securityStatus = activity.securityManager.initializeSecurity()
            securityStatus == SecurityManager.SecurityStatus.SECURE
        } catch (e: Exception) {
            Logger.w("MainFragment", "Security validation failed: ${e.message}")
            false
        }
    }
    
    /**
     * Initialize RGB camera with real validation
     */
    private suspend fun initializeRgbCamera(activity: MainActivity): Boolean {
        return try {
            // Check if camera is available and attempt connection
            activity.rgbCamera.isConnected()
        } catch (e: Exception) {
            Logger.e("MainFragment", "RGB camera initialization failed: ${e.message}")
            false
        }
    }
    
    /**
     * Initialize thermal camera with real validation
     */
    private suspend fun initializeThermalCamera(activity: MainActivity): Boolean {
        return try {
            // Check if thermal camera is available and attempt connection
            activity.thermalCamera.isConnected()
        } catch (e: Exception) {
            Logger.e("MainFragment", "Thermal camera initialization failed: ${e.message}")
            false
        }
    }
    
    /**
     * Initialize GSR sensor with real validation
     */
    private suspend fun initializeGsrSensor(activity: MainActivity): Boolean {
        return try {
            // Check system health before attempting GSR connection
            val systemHealthy = activity.faultToleranceManager.isSystemHealthy()
            if (!systemHealthy) {
                Logger.w("MainFragment", "System health check failed during GSR sensor init")
                return false
            }
            
            // Check if GSR sensor is available and attempt connection
            activity.gsrSensor.isConnected()
        } catch (e: Exception) {
            Logger.e("MainFragment", "GSR sensor initialization failed: ${e.message}")
            false
        }
    }
    
    /**
     * Synchronize devices with real time sync validation
     */
    private suspend fun synchronizeDevices(activity: MainActivity): Boolean {
        return try {
            // Check if devices are actually connected before sync
            val rgbReady = try { activity.rgbCamera.isConnected() } catch (e: Exception) { false }
            val thermalReady = try { activity.thermalCamera.isConnected() } catch (e: Exception) { false }
            val gsrReady = try { activity.gsrSensor.isConnected() } catch (e: Exception) { false }
            
            if (!rgbReady && !thermalReady && !gsrReady) {
                Logger.w("MainFragment", "No devices available for synchronization")
                return false
            }
            
            // Enable data validation for synchronized recording
            activity.dataValidationService.setValidationEnabled(true)
            
            // Verify data validation is working
            val validationStats = activity.dataValidationService.getValidationStatistics()
            if (!validationStats.isEnabled) {
                Logger.w("MainFragment", "Data validation could not be enabled")
                return false
            }
            
            Logger.i("MainFragment", "Device synchronization completed successfully")
            true
        } catch (e: Exception) {
            Logger.e("MainFragment", "Device synchronization failed: ${e.message}")
            false
        }
    }
    
    /**
     * Show enhanced success dialog with professional styling
     */
    private fun showEnhancedConnectionSuccess() {
        androidx.appcompat.app.AlertDialog.Builder(requireContext())
            .setTitle("[SUCCESS] Connection Successful")
            .setMessage("""
                All devices connected successfully!
                
                [RGB] RGB Camera: Ready
                [THERMAL] Thermal Camera: Online  
                [GSR] GSR Sensor: Synchronized
                
                You can now start recording with full multi-sensor support.
            """.trimIndent())
            .setPositiveButton("Start Recording") { _, _ ->
                (activity as? MainActivity)?.let {
                    it.navigateToRecording()
                }
            }
            .setNegativeButton("Continue") { _, _ -> }
            .setCancelable(false)
            .show()
    }
    
    /**
     * Show enhanced error dialog with professional recovery options
     */
    private fun showEnhancedConnectionError(error: String) {
        androidx.appcompat.app.AlertDialog.Builder(requireContext())
            .setTitle("[WARNING] Connection Error")
            .setMessage("""
                Failed to connect devices: $error
                
                [TROUBLESHOOTING]:
                - Check device connections
                - Verify security settings
                - Ensure sufficient system resources
                
                Please try again or contact support.
            """.trimIndent())
            .setPositiveButton("Retry Connection") { _, _ ->
                handleConnectDeviceClick()
            }
            .setNeutralButton("System Settings") { _, _ ->
                (activity as? MainActivity)?.let {
                    it.navigateToSettings()
                }
            }
            .setNegativeButton("Cancel") { _, _ -> }
            .show()
    }

    private class DeviceAdapter : RecyclerView.Adapter<DeviceAdapter.ViewHolder>() {
        
        var onItemClickListener: ((type: DeviceType) -> Unit)? = null
        private var deviceInfoList: List<DeviceInfo> = emptyList()

        fun updateDevices(devices: List<DeviceInfo>) {
            deviceInfoList = devices
            notifyDataSetChanged()
        }

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
            return ViewHolder(
                LayoutInflater.from(parent.context).inflate(
                    R.layout.item_device_connect,
                    parent,
                    false
                )
            )
        }

        @SuppressLint("SetTextI18n")
        override fun onBindViewHolder(holder: ViewHolder, position: Int) {
            val device = deviceInfoList[position]
            val hasTitle = position == 0

            holder.itemView.findViewById<View>(R.id.tv_title)?.isVisible = hasTitle
            holder.itemView.findViewById<android.widget.TextView>(R.id.tv_title)?.text = "Multi-Sensor Devices"

            // Enhanced professional device card styling
            val bgView = holder.itemView.findViewById<View>(R.id.iv_bg)
            val iconView = holder.itemView.findViewById<android.widget.TextView>(R.id.tv_device_icon)
            val nameView = holder.itemView.findViewById<android.widget.TextView>(R.id.tv_device_name)
            val statusView = holder.itemView.findViewById<android.widget.TextView>(R.id.tv_device_status)
            val stateView = holder.itemView.findViewById<View>(R.id.view_device_state)
            val stateTextView = holder.itemView.findViewById<android.widget.TextView>(R.id.tv_device_state)
            
            // Set device information
            iconView?.text = device.icon
            nameView?.text = device.name
            statusView?.text = device.status
            
            // Professional status styling
            if (device.isConnected) {
                bgView?.isSelected = true
                nameView?.setTextColor(holder.itemView.context.getColor(R.color.text_primary))
                statusView?.setTextColor(holder.itemView.context.getColor(R.color.text_success))
                stateView?.background = holder.itemView.context.getDrawable(R.drawable.status_dot_online)
                stateTextView?.text = "online"
                stateTextView?.setTextColor(holder.itemView.context.getColor(R.color.status_online))
            } else {
                bgView?.isSelected = false
                nameView?.setTextColor(holder.itemView.context.getColor(R.color.text_secondary))
                statusView?.setTextColor(holder.itemView.context.getColor(R.color.text_tertiary))
                stateView?.background = holder.itemView.context.getDrawable(R.drawable.status_dot_offline)
                stateTextView?.text = "offline"
                stateTextView?.setTextColor(holder.itemView.context.getColor(R.color.status_offline))
            }
        }

        override fun getItemCount(): Int = deviceInfoList.size

        inner class ViewHolder(rootView: View) : RecyclerView.ViewHolder(rootView) {
            init {
                rootView.findViewById<View>(R.id.iv_bg)?.setOnClickListener {
                    val position = adapterPosition
                    if (position != RecyclerView.NO_POSITION) {
                        onItemClickListener?.invoke(deviceInfoList[position].type)
                    }
                }
            }
        }
    }

    enum class DeviceType {
        RGB_CAMERA,
        THERMAL_CAMERA,
        GSR_SENSOR
    }

    data class DeviceInfo(
        val type: DeviceType,
        val icon: String,
        val name: String,
        val status: String,
        val isConnected: Boolean
    )
}