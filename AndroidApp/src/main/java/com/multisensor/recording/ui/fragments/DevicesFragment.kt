package com.multisensor.recording.ui.fragments

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch
import com.multisensor.recording.databinding.FragmentDevicesBinding
import com.multisensor.recording.ui.MainViewModel
import com.multisensor.recording.ui.util.UIUtils
import com.multisensor.recording.managers.ShimmerManager
import com.multisensor.recording.managers.UsbDeviceManager
import dagger.hilt.android.AndroidEntryPoint
import javax.inject.Inject

/**
 * Devices Fragment - Device Management
 * 
 * Handles device connection, status monitoring, and management functionality.
 * Integrates with ShimmerManager and UsbDeviceManager for comprehensive device control.
 */
@AndroidEntryPoint
class DevicesFragment : Fragment() {

    private var _binding: FragmentDevicesBinding? = null
    private val binding get() = _binding!!
    
    private lateinit var viewModel: MainViewModel
    
    @Inject
    lateinit var shimmerManager: ShimmerManager
    
    @Inject
    lateinit var usbDeviceManager: UsbDeviceManager

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentDevicesBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        // Get shared ViewModel from parent activity
        viewModel = ViewModelProvider(requireActivity())[MainViewModel::class.java]
        
        setupUI()
        observeViewModel()
    }

    private fun setupUI() {
        binding.connectDevicesButton.setOnClickListener {
            connectDevices()
        }

        binding.scanDevicesButton.setOnClickListener {
            scanForDevices()
        }
        
        // Set initial UI state
        updateDeviceStatus()
    }

    private fun observeViewModel() {
        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.uiState.collect { state ->
                updateUIFromState(state)
            }
        }
    }

    private fun updateUIFromState(state: com.multisensor.recording.ui.MainUiState) {
        // Update device connection status display
        val shimmerStatus = if (state.isShimmerConnected) {
            "✅ Shimmer: Connected"
        } else {
            "❌ Shimmer: Disconnected"
        }
        
        val thermalStatus = if (state.isThermalConnected) {
            "✅ Thermal: Connected"
        } else {
            "❌ Thermal: Disconnected" 
        }
        
        val pcStatus = if (state.isPcConnected) {
            "✅ PC: Connected"
        } else {
            "⏳ PC: Waiting..."
        }
        
        // Update device list view with current status
        updateDeviceStatusDisplay(shimmerStatus, thermalStatus, pcStatus)
        
        // Update button states based on connection status
        binding.connectDevicesButton.isEnabled = !state.isShimmerConnected || !state.isThermalConnected
        binding.scanDevicesButton.isEnabled = true
    }

    private fun connectDevices() {
        UIUtils.showStatusMessage(requireContext(), "Starting device connection...")
        
        // Connect Shimmer device
        if (!viewModel.uiState.value.isShimmerConnected) {
            connectShimmerDevice()
        }
        
        // Check for USB/Thermal devices
        if (!viewModel.uiState.value.isThermalConnected) {
            connectThermalDevice()
        }
    }

    private fun connectShimmerDevice() {
        UIUtils.showStatusMessage(requireContext(), "Scanning for Shimmer devices...")
        
        // Use ShimmerManager to start device selection
        // This would integrate with the existing Shimmer connection logic from MainActivity
        lifecycleScope.launch {
            try {
                // Note: The actual shimmerManager.startDeviceSelection method may not exist yet
                // This is a placeholder for future implementation
                UIUtils.showStatusMessage(requireContext(), "Shimmer device selection - Feature coming soon")
            } catch (e: Exception) {
                UIUtils.showStatusMessage(requireContext(), "Error connecting Shimmer: ${e.message}", true)
            }
        }
    }

    private fun connectThermalDevice() {
        UIUtils.showStatusMessage(requireContext(), "Checking for thermal camera...")
        
        // Check for connected USB thermal devices
        lifecycleScope.launch {
            try {
                // Note: The actual usbDeviceManager.getConnectedDevices method may not exist yet
                // This is a placeholder for future implementation
                UIUtils.showStatusMessage(requireContext(), "USB device scan - Feature coming soon")
            } catch (e: Exception) {
                UIUtils.showStatusMessage(requireContext(), "Error scanning USB devices: ${e.message}", true)
            }
        }
    }

    private fun scanForDevices() {
        UIUtils.showStatusMessage(requireContext(), "Scanning for all devices...")
        
        lifecycleScope.launch {
            try {
                // Refresh device status
                updateDeviceStatus()
                
                // Show scanning feedback
                UIUtils.showStatusMessage(requireContext(), "Device scan completed")
            } catch (e: Exception) {
                UIUtils.showStatusMessage(requireContext(), "Scan error: ${e.message}", true)
            }
        }
    }

    private fun updateDeviceStatus() {
        // Force update of device status display
        val currentState = viewModel.uiState.value
        updateUIFromState(currentState)
    }

    private fun updateDeviceStatusDisplay(shimmerStatus: String, thermalStatus: String, pcStatus: String) {
        // Update the placeholder text area with device status
        val statusText = buildString {
            appendLine("Device Status:")
            appendLine()
            appendLine(shimmerStatus)
            appendLine(thermalStatus) 
            appendLine(pcStatus)
            appendLine()
            appendLine("Connected devices will appear here...")
        }
        
        // Find the status TextView in the layout (the large placeholder area)
        val rootView = binding.root as? android.view.ViewGroup
        val statusTextView = findTextViewWithText(rootView, "Connected devices")
        statusTextView?.text = statusText
    }

    private fun findTextViewWithText(viewGroup: android.view.ViewGroup?, searchText: String): android.widget.TextView? {
        if (viewGroup == null) return null
        
        for (i in 0 until viewGroup.childCount) {
            val child = viewGroup.getChildAt(i)
            when (child) {
                is android.widget.TextView -> {
                    if (child.text.toString().contains(searchText, ignoreCase = true)) {
                        return child
                    }
                }
                is android.view.ViewGroup -> {
                    val found = findTextViewWithText(child, searchText)
                    if (found != null) return found
                }
            }
        }
        return null
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}