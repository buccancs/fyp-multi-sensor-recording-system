package com.multisensor.recording.ui.fragments

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
import com.multisensor.recording.databinding.FragmentPreviewRecordBinding
import com.multisensor.recording.ui.MainViewModel
import com.multisensor.recording.ui.MainUiState
import dagger.hilt.android.AndroidEntryPoint

/**
 * Preview/Record Fragment
 * 
 * Main interface for live video preview and recording controls.
 * Features:
 * - Dual camera preview (regular + thermal)
 * - Recording start/stop controls
 * - Real-time status indicators
 * - One-handed operation optimized
 */
@AndroidEntryPoint
class PreviewRecordFragment : Fragment() {
    
    private var _binding: FragmentPreviewRecordBinding? = null
    private val binding get() = _binding!!
    
    private val viewModel: MainViewModel by activityViewModels()
    
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentPreviewRecordBinding.inflate(inflater, container, false)
        return binding.root
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        setupUI()
        observeViewModel()
    }
    
    private fun setupUI() {
        // Recording controls
        binding.startRecordingButton.setOnClickListener {
            viewModel.startRecording()
        }
        
        binding.stopRecordingButton.setOnClickListener {
            viewModel.stopRecording()
        }
        
        // Camera preview controls
        binding.switchCameraButton.setOnClickListener {
            viewModel.switchCamera()
        }
        
        binding.toggleThermalButton.setOnClickListener {
            viewModel.toggleThermalPreview()
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
        // Update recording button states
        binding.startRecordingButton.isEnabled = !state.isRecording && state.isReadyToRecord
        binding.stopRecordingButton.isEnabled = state.isRecording
        
        // Update connection status indicators
        updateConnectionIndicator(binding.pcConnectionIndicator, state.isPcConnected)
        updateConnectionIndicator(binding.shimmerConnectionIndicator, state.isShimmerConnected)
        updateConnectionIndicator(binding.thermalConnectionIndicator, state.isThermalConnected)
        updateConnectionIndicator(binding.gsrConnectionIndicator, state.isGsrConnected)
        updateConnectionIndicator(binding.networkConnectionIndicator, state.isNetworkConnected)
        
        // Update status text
        binding.pcConnectionStatus.text = if (state.isPcConnected) "PC: Connected" else "PC: Disconnected"
        binding.shimmerConnectionStatus.text = if (state.isShimmerConnected) "Shimmer: Connected" else "Shimmer: Disconnected"
        binding.thermalConnectionStatus.text = if (state.isThermalConnected) "Thermal: Connected" else "Thermal: Disconnected"
        binding.gsrConnectionStatus.text = if (state.isGsrConnected) "GSR: Connected" else "GSR: Disconnected"
        binding.networkConnectionStatus.text = if (state.isNetworkConnected) "Network: Connected" else "Network: Disconnected"
        
        // Update recording status
        binding.recordingStatusText.text = if (state.isRecording) "Recording in progress..." else "Ready to record"
        binding.recordingStatusIndicator.setBackgroundResource(
            if (state.isRecording) android.R.color.holo_red_light else android.R.color.darker_gray
        )
    }
    
    private fun updateConnectionIndicator(indicator: View, isConnected: Boolean) {
        indicator.setBackgroundResource(
            if (isConnected) android.R.color.holo_green_light else android.R.color.holo_red_light
        )
    }
    
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}