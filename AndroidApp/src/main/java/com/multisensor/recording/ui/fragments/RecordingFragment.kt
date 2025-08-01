package com.multisensor.recording.ui.fragments

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch
import com.multisensor.recording.databinding.FragmentRecordingBinding
import com.multisensor.recording.ui.MainViewModel
import com.multisensor.recording.ui.util.UIUtils
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
        
        // Initialize the recording system when this fragment is created
        initializeRecordingSystem()
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
    
    private fun initializeRecordingSystem() {
        // Initialize the recording system with the TextureView from this fragment
        val textureView = binding.texturePreview
        
        // Post to ensure the view is fully laid out
        textureView.post {
            try {
                viewModel.initializeSystem(textureView)
                UIUtils.showStatusMessage(requireContext(), "Recording system initialized")
            } catch (e: Exception) {
                UIUtils.showStatusMessage(requireContext(), "Initialization error: ${e.message}", true)
            }
        }
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
        
        // Update connection indicators using UIUtils
        UIUtils.updateConnectionIndicator(requireContext(), binding.pcConnectionIndicator, state.isPcConnected)
        UIUtils.updateConnectionIndicator(requireContext(), binding.shimmerConnectionIndicator, state.isShimmerConnected)
        UIUtils.updateConnectionIndicator(requireContext(), binding.thermalConnectionIndicator, state.isThermalConnected)
        
        // Update status texts using UIUtils
        binding.pcConnectionStatus.text = UIUtils.getConnectionStatusText("PC", state.isPcConnected)
        binding.shimmerConnectionStatus.text = UIUtils.getConnectionStatusText("Shimmer", state.isShimmerConnected)
        binding.thermalConnectionStatus.text = UIUtils.getConnectionStatusText("Thermal", state.isThermalConnected)
        
        // Update battery level using UIUtils
        binding.batteryLevelText.text = UIUtils.formatBatteryText(state.batteryLevel)
        
        // Update recording status using UIUtils
        updateRecordingStatus(state.isRecording)
        
        // Update streaming info using UIUtils
        binding.streamingDebugOverlay.text = UIUtils.formatStreamingText(
            state.isStreaming, 
            state.streamingFrameRate, 
            state.streamingDataSize
        )
        
        // Update overall status
        binding.statusText.text = state.statusText
        
        // Handle errors using UIUtils
        state.errorMessage?.let { errorMsg ->
            if (state.showErrorDialog) {
                UIUtils.showStatusMessage(requireContext(), errorMsg, true)
                viewModel.clearError()
            }
        }
    }

    private fun updateConnectionIndicator(indicator: View, isConnected: Boolean) {
        UIUtils.updateConnectionIndicator(requireContext(), indicator, isConnected)
    }

    private fun updateRecordingStatus(isRecording: Boolean) {
        binding.recordingStatusText.text = UIUtils.getRecordingStatusText(isRecording)
        UIUtils.updateRecordingIndicator(requireContext(), binding.recordingIndicator, isRecording)
    }

    private fun startRecording() {
        viewModel.startRecording()
        UIUtils.showStatusMessage(requireContext(), "Starting recording...")
    }

    private fun stopRecording() {
        viewModel.stopRecording()
        UIUtils.showStatusMessage(requireContext(), "Stopping recording...")
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}