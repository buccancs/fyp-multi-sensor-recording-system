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
import com.multisensor.recording.databinding.FragmentRecordingBinding
import com.multisensor.recording.ui.MainViewModel
import com.multisensor.recording.ui.MainUiState
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch

/**
 * Recording Fragment
 * 
 * Handles recording controls, camera preview, and recording status
 */
@AndroidEntryPoint
class RecordingFragment : Fragment() {

    private var _binding: FragmentRecordingBinding? = null
    private val binding get() = _binding!!
    
    private val viewModel: MainViewModel by activityViewModels()

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
        
        setupUI()
        observeViewModel()
    }

    private fun setupUI() {
        binding.apply {
            // Recording controls
            startRecordingButton.setOnClickListener {
                viewModel.startRecording()
            }
            
            stopRecordingButton.setOnClickListener {
                viewModel.stopRecording()
            }
            
            pauseRecordingButton.setOnClickListener {
                viewModel.pauseRecording()
            }
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
        binding.apply {
            // Update recording status
            recordingStatusText.text = when {
                state.isRecording -> "Recording in progress..."
                state.isPaused -> "Recording paused"
                else -> "Ready to record"
            }
            
            // Update button states
            startRecordingButton.isEnabled = !state.isRecording && !state.isPaused
            stopRecordingButton.isEnabled = state.isRecording || state.isPaused
            pauseRecordingButton.isEnabled = state.isRecording
            
            // Update session info
            sessionDurationText.text = state.sessionDuration
            currentFileSizeText.text = state.currentFileSize
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}