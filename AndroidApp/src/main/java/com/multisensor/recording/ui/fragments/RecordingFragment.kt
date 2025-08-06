package com.multisensor.recording.ui.fragments

import android.graphics.SurfaceTexture
import android.os.Bundle
import android.view.LayoutInflater
import android.view.TextureView
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import com.multisensor.recording.R
import com.multisensor.recording.databinding.FragmentRecordingBinding
import com.multisensor.recording.recording.CameraRecorder
import com.multisensor.recording.ui.MainUiState
import com.multisensor.recording.ui.MainViewModelRefactored
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch
import kotlinx.coroutines.flow.collect
import android.widget.Toast
import javax.inject.Inject

@AndroidEntryPoint
class RecordingFragment : Fragment() {

    private var _binding: FragmentRecordingBinding? = null
    private val binding get() = _binding!!

    private val viewModel: MainViewModelRefactored by activityViewModels()

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

        Toast.makeText(requireContext(), "Recording Fragment Loaded", Toast.LENGTH_SHORT).show()

        setupUI()
        setupCameraPreview()
        observeViewModel()
    }

    private fun setupUI() {
        binding.apply {
            startRecordingButton.setOnClickListener {
                Toast.makeText(requireContext(), "Start Recording clicked!", Toast.LENGTH_SHORT).show()
                viewModel.startRecording()
            }

            stopRecordingButton.setOnClickListener {
                Toast.makeText(requireContext(), "Stop Recording clicked!", Toast.LENGTH_SHORT).show()
                viewModel.stopRecording()
            }

            pauseRecordingButton.setOnClickListener {
                Toast.makeText(requireContext(), "Pause Recording clicked!", Toast.LENGTH_SHORT).show()
                viewModel.pauseRecording()
            }
        }
    }

    private fun setupCameraPreview() {
        lifecycleScope.launch {
            try {
                binding.previewPlaceholderText.apply {
                    visibility = View.VISIBLE
                    text = "Initializing camera..."
                }

                val textureView = binding.rgbCameraPreview

                textureView.surfaceTextureListener = object : TextureView.SurfaceTextureListener {
                    override fun onSurfaceTextureAvailable(surface: SurfaceTexture, width: Int, height: Int) {
                        lifecycleScope.launch {
                            initializeCameraWithRetry(textureView)
                        }
                    }

                    override fun onSurfaceTextureSizeChanged(surface: SurfaceTexture, width: Int, height: Int) {}
                    override fun onSurfaceTextureDestroyed(surface: SurfaceTexture): Boolean = true
                    override fun onSurfaceTextureUpdated(surface: SurfaceTexture) {}
                }

                if (textureView.isAvailable) {
                    initializeCameraWithRetry(textureView)
                }

            } catch (e: Exception) {
                binding.rgbCameraPreview.visibility = View.GONE
                binding.previewPlaceholderText.apply {
                    visibility = View.VISIBLE
                    text = "Camera setup error: ${e.message}"
                }
                Toast.makeText(requireContext(), "Camera setup failed: ${e.message}", Toast.LENGTH_LONG).show()
            }
        }
    }

    private suspend fun initializeCameraWithRetry(textureView: TextureView) {
        try {
            binding.previewPlaceholderText.text = "Connecting to camera..."

            val initialized = cameraRecorder.initialize(textureView)

            if (initialized) {
                binding.rgbCameraPreview.visibility = View.VISIBLE
                binding.previewPlaceholderText.visibility = View.GONE
                Toast.makeText(requireContext(), "Camera preview ready", Toast.LENGTH_SHORT).show()
            } else {

                binding.previewPlaceholderText.text = "Trying fallback camera mode..."
                kotlinx.coroutines.delay(1000)

                binding.rgbCameraPreview.visibility = View.GONE
                binding.previewPlaceholderText.apply {
                    visibility = View.VISIBLE
                    text = """Camera initialization failed

This device may not support:
• RAW image capture
• Advanced camera features
• High-end camera requirements

Basic recording may still work."""
                }
                Toast.makeText(requireContext(), "Camera preview unavailable - check device compatibility", Toast.LENGTH_LONG).show()
            }
        } catch (e: Exception) {
            binding.rgbCameraPreview.visibility = View.GONE
            binding.previewPlaceholderText.apply {
                visibility = View.VISIBLE
                text = """Camera error: ${e.message}

Possible issues:
• Camera permission denied
• Camera in use by another app
• Hardware compatibility issue

Try restarting the app or checking permissions."""
            }
            Toast.makeText(requireContext(), "Camera error: ${e.message}", Toast.LENGTH_LONG).show()
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

            updateSensorStatusIndicators()
        }
    }

    private fun updateSensorStatusIndicators() {
        // TODO: Re-implement with Compose UI components after migration
        // binding.apply {
        //     val cameraConnected = rgbCameraPreview.visibility == View.VISIBLE
        //     updateSensorStatus(
        //         cameraStatusIcon, cameraStatusText,
        //         cameraConnected, "Camera", "Connected", "Disconnected"
        //     )
        //     updateSensorStatus(
        //         thermalStatusIcon, thermalStatusText,
        //         false, "Thermal", "Connected", "Disconnected"
        //     )
        //     updateSensorStatus(
        //         gsrStatusIcon, gsrStatusText,
        //         false, "GSR", "Connected", "Disconnected"
        //     )
        //     updateSensorStatus(
        //         pcStatusIcon, pcStatusText,
        //         false, "PC", "Connected", "Disconnected"
        //     )
        // }
    }

    private fun updateSensorStatus(
        icon: ImageView,
        text: TextView,
        isConnected: Boolean,
        sensorName: String,
        connectedText: String,
        disconnectedText: String
    ) {
        val context = requireContext()
        if (isConnected) {
            icon.setColorFilter(androidx.core.content.ContextCompat.getColor(context, R.color.statusIndicatorConnected))
            text.text = "$sensorName\n$connectedText"
            text.contentDescription = "$sensorName sensor is $connectedText"
        } else {
            icon.setColorFilter(androidx.core.content.ContextCompat.getColor(context, R.color.statusIndicatorDisconnected))
            text.text = "$sensorName\n$disconnectedText"
            text.contentDescription = "$sensorName sensor is $disconnectedText"
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}