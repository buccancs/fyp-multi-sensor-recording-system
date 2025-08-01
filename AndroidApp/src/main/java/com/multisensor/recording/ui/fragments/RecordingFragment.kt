package com.multisensor.recording.ui.fragments

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch
import com.multisensor.recording.databinding.FragmentRecordingBinding
import com.multisensor.recording.ui.MainViewModel
import dagger.hilt.android.AndroidEntryPoint

/**
 * Simplified Recording Fragment
 * 
 * This fragment contains the core recording functionality in a clean,
 * organized layout as part of the navigation architecture redesign.
 */
@AndroidEntryPoint
class RecordingFragment : Fragment() {

    private var _binding: FragmentRecordingBinding? = null
    private val binding get() = _binding!!
    
    private lateinit var viewModel: MainViewModel

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentRecordingBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        // Get ViewModel from parent activity
        viewModel = ViewModelProvider(requireActivity())[MainViewModel::class.java]
        
        setupUI()
        observeViewModel()
    }

    private fun setupUI() {
        // Recording control buttons
        binding.startRecordingButton.setOnClickListener {
            startRecording()
        }
        
        binding.stopRecordingButton.setOnClickListener {
            stopRecording()
        }
        
        // Initialize status
        updateRecordingStatus(false)
    }

    private fun observeViewModel() {
        // Observe ViewModel state using the correct pattern for StateFlow
        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.uiState.collect { state ->
                updateUIFromState(state)
            }
        }
    }

    private fun updateUIFromState(state: com.multisensor.recording.ui.MainUiState) {
        // Update recording controls
        binding.startRecordingButton.isEnabled = state.canStartRecording
        binding.stopRecordingButton.isEnabled = state.canStopRecording
        
        // Update connection indicators
        updateConnectionIndicator(binding.pcConnectionIndicator, state.isPcConnected)
        updateConnectionIndicator(binding.shimmerConnectionIndicator, state.isShimmerConnected)
        updateConnectionIndicator(binding.thermalConnectionIndicator, state.isThermalConnected)
        
        // Update status texts
        binding.pcConnectionStatus.text = "PC: ${if (state.isPcConnected) "Connected" else "Waiting..."}"
        binding.shimmerConnectionStatus.text = "Shimmer: ${if (state.isShimmerConnected) "Connected" else "Off"}"
        binding.thermalConnectionStatus.text = "Thermal: ${if (state.isThermalConnected) "Connected" else "Off"}"
        
        // Update battery level
        val batteryText = if (state.batteryLevel >= 0) {
            "Battery: ${state.batteryLevel}%"
        } else {
            "Battery: ---%"
        }
        binding.batteryLevelText.text = batteryText
        
        // Update recording status
        updateRecordingStatus(state.isRecording)
        
        // Update streaming info
        if (state.isStreaming && state.streamingFrameRate > 0) {
            binding.streamingDebugOverlay.text = "Streaming: ${state.streamingFrameRate}fps (${state.streamingDataSize})"
        } else {
            binding.streamingDebugOverlay.text = "Ready to stream"
        }
        
        // Update overall status
        binding.statusText.text = state.statusText
        
        // Handle errors
        state.errorMessage?.let { errorMsg ->
            if (state.showErrorDialog) {
                Toast.makeText(context, errorMsg, Toast.LENGTH_LONG).show()
                viewModel.clearError()
            }
        }
    }

    private fun updateConnectionIndicator(indicator: View, isConnected: Boolean) {
        val colorRes = if (isConnected) {
            com.multisensor.recording.R.color.statusIndicatorConnected
        } else {
            com.multisensor.recording.R.color.statusIndicatorDisconnected
        }
        indicator.setBackgroundColor(requireContext().getColor(colorRes))
    }

    private fun updateRecordingStatus(isRecording: Boolean) {
        val statusText = if (isRecording) "Recording in progress..." else "Ready to record"
        binding.recordingStatusText.text = statusText
        
        val colorRes = if (isRecording) {
            com.multisensor.recording.R.color.recordingActive
        } else {
            com.multisensor.recording.R.color.recordingInactive
        }
        binding.recordingIndicator.setBackgroundColor(requireContext().getColor(colorRes))
    }

    private fun startRecording() {
        viewModel.startRecording()
        Toast.makeText(context, "Starting recording...", Toast.LENGTH_SHORT).show()
    }

    private fun stopRecording() {
        viewModel.stopRecording()
        Toast.makeText(context, "Stopping recording...", Toast.LENGTH_SHORT).show()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}