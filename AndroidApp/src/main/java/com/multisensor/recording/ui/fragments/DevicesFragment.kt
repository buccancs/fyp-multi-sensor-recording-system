package com.multisensor.recording.ui.fragments

import android.content.Intent
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import kotlinx.coroutines.launch
import com.multisensor.recording.databinding.FragmentDevicesBinding
import com.multisensor.recording.ui.MainViewModel
import com.multisensor.recording.ui.MainUiState
import com.multisensor.recording.ui.NetworkConfigActivity
import com.multisensor.recording.ui.ShimmerConfigActivity
import dagger.hilt.android.AndroidEntryPoint

/**
 * Devices Fragment
 * 
 * Device management and configuration interface.
 * Features:
 * - Device connection status
 * - Device configuration access
 * - Connection troubleshooting
 * - Quick device actions
 */
@AndroidEntryPoint
class DevicesFragment : Fragment() {
    
    private var _binding: FragmentDevicesBinding? = null
    private val binding get() = _binding!!
    
    private val viewModel: MainViewModel by activityViewModels()
    
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
        
        setupUI()
        observeViewModel()
    }
    
    private fun setupUI() {
        // Device configuration buttons
        binding.configureShimmerButton.setOnClickListener {
            startActivity(Intent(requireContext(), ShimmerConfigActivity::class.java))
        }
        
        binding.configureNetworkButton.setOnClickListener {
            startActivity(Intent(requireContext(), NetworkConfigActivity::class.java))
        }
        
        // Device action buttons
        binding.connectPcButton.setOnClickListener {
            viewModel.connectToPC()
        }
        
        binding.disconnectPcButton.setOnClickListener {
            viewModel.disconnectFromPC()
        }
        
        binding.scanShimmerButton.setOnClickListener {
            viewModel.scanForShimmer()
        }
        
        binding.connectShimmerButton.setOnClickListener {
            viewModel.connectShimmer()
        }
        
        binding.disconnectShimmerButton.setOnClickListener {
            viewModel.disconnectShimmer()
        }
        
        binding.connectThermalButton.setOnClickListener {
            viewModel.connectThermal()
        }
        
        binding.disconnectThermalButton.setOnClickListener {
            viewModel.disconnectThermal()
        }
        
        binding.refreshDevicesButton.setOnClickListener {
            viewModel.refreshDevices()
        }
    }
    
    private fun observeViewModel() {
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    updateUI(state)
                }
            }
        }
    }
    
    private fun updateUI(state: MainUiState) {
        // Update connection status
        updateDeviceStatus(binding.pcConnectionStatus, binding.pcConnectionIndicator, state.isPcConnected, "PC Connection")
        updateDeviceStatus(binding.shimmerConnectionStatus, binding.shimmerConnectionIndicator, state.isShimmerConnected, "Shimmer Device")
        updateDeviceStatus(binding.thermalConnectionStatus, binding.thermalConnectionIndicator, state.isThermalConnected, "Thermal Camera")
        updateDeviceStatus(binding.gsrConnectionStatus, binding.gsrConnectionIndicator, state.isGsrConnected, "GSR Sensor")
        updateDeviceStatus(binding.networkConnectionStatus, binding.networkConnectionIndicator, state.isNetworkConnected, "Network")
        
        // Update button states
        binding.connectPcButton.isEnabled = !state.isPcConnected
        binding.disconnectPcButton.isEnabled = state.isPcConnected
        
        binding.connectShimmerButton.isEnabled = !state.isShimmerConnected
        binding.disconnectShimmerButton.isEnabled = state.isShimmerConnected
        
        binding.connectThermalButton.isEnabled = !state.isThermalConnected
        binding.disconnectThermalButton.isEnabled = state.isThermalConnected
        
        // Update device info
        binding.shimmerDeviceInfo.text = if (state.isShimmerConnected) "Shimmer ID: ${state.shimmerDeviceId}" else "No Shimmer device connected"
        binding.thermalDeviceInfo.text = if (state.isThermalConnected) "Thermal camera ready" else "No thermal camera connected"
        binding.networkDeviceInfo.text = if (state.isNetworkConnected) "Connected to: ${state.networkAddress}" else "No network connection"
    }
    
    private fun updateDeviceStatus(statusText: com.google.android.material.textview.MaterialTextView, 
                                   indicator: View, 
                                   isConnected: Boolean, 
                                   deviceName: String) {
        statusText.text = "$deviceName: ${if (isConnected) "Connected" else "Disconnected"}"
        indicator.setBackgroundResource(
            if (isConnected) android.R.color.holo_green_light else android.R.color.holo_red_light
        )
    }
    
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}