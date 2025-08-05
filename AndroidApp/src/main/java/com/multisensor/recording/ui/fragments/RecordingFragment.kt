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
import com.multisensor.recording.recording.CameraRecorder
import com.multisensor.recording.ui.MainViewModel
import com.multisensor.recording.ui.MainUiState
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch
import javax.inject.Inject

@AndroidEntryPoint
class RecordingFragment : Fragment() {

    private var _binding: FragmentRecordingBinding? = null
    private val binding get() = _binding!!

    private val viewModel: MainViewModel by activityViewModels()

    @Inject
    lateinit var cameraRecorder: CameraRecorder

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
        setupCameraPreview()
        observeViewModel()
    }

    private fun setupUI() {
        binding.apply {
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

    private fun setupCameraPreview() {
        lifecycleScope.launch {
            try {
                val textureView = binding.rgbCameraPreview
                val initialized = cameraRecorder.initialize(textureView)

                if (initialized) {
                    binding.rgbCameraPreview.visibility = View.VISIBLE
                    binding.previewPlaceholderText.visibility = View.GONE
                } else {
                    binding.rgbCameraPreview.visibility = View.GONE
                    binding.previewPlaceholderText.apply {
                        visibility = View.VISIBLE
                        text = "Camera initialization failed"
                    }
                }
            } catch (e: Exception) {
                binding.rgbCameraPreview.visibility = View.GONE
                binding.previewPlaceholderText.apply {
                    visibility = View.VISIBLE
                    text = "Camera preview unavailable: ${e.message}"
                }
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
            recordingStatusText.text = when {
                state.isRecording -> "Recording in progress..."
                state.isPaused -> "Recording paused"
                else -> "Ready to record"
            }

            startRecordingButton.isEnabled = !state.isRecording && !state.isPaused
            stopRecordingButton.isEnabled = state.isRecording || state.isPaused
            pauseRecordingButton.isEnabled = state.isRecording

            sessionDurationText.text = state.sessionDuration
            currentFileSizeText.text = state.currentFileSize
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}