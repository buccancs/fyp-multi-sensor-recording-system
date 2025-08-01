package com.multisensor.recording.ui.fragments

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch
import com.multisensor.recording.databinding.FragmentCalibrationBinding
import com.multisensor.recording.ui.MainViewModel
import com.multisensor.recording.ui.util.UIUtils
import com.multisensor.recording.calibration.CalibrationCaptureManager
import dagger.hilt.android.AndroidEntryPoint
import javax.inject.Inject

/**
 * Calibration Fragment - Camera Calibration
 * 
 * Handles camera calibration functionality and status display.
 * Integrates with CalibrationCaptureManager for actual calibration operations.
 */
@AndroidEntryPoint
class CalibrationFragment : Fragment() {

    private var _binding: FragmentCalibrationBinding? = null
    private val binding get() = _binding!!
    
    private lateinit var viewModel: MainViewModel
    
    @Inject
    lateinit var calibrationCaptureManager: CalibrationCaptureManager

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentCalibrationBinding.inflate(inflater, container, false)
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
        binding.runCalibrationButton.setOnClickListener {
            runCalibration()
        }
        
        // Set initial status
        updateCalibrationStatus("Ready for calibration")
    }

    private fun observeViewModel() {
        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.uiState.collect { state ->
                updateUIFromState(state)
            }
        }
    }

    private fun updateUIFromState(state: com.multisensor.recording.ui.MainUiState) {
        // Update calibration button availability based on system state
        binding.runCalibrationButton.isEnabled = state.canRunCalibration
        
        // Show connection status affecting calibration
        val statusText = buildString {
            appendLine("Calibration System Status:")
            appendLine()
            appendLine("• Cameras: ${if (state.isThermalConnected) "Ready" else "Not connected"}")
            appendLine("• PC Connection: ${if (state.isPcConnected) "Connected" else "Waiting..."}")
            appendLine("• Recording: ${if (state.isRecording) "Active (calibration disabled)" else "Stopped"}")
            appendLine()
            appendLine("Calibration instructions and progress will appear here...")
        }
        
        updateCalibrationInstructions(statusText)
    }

    private fun runCalibration() {
        updateCalibrationStatus("Starting calibration capture...")
        UIUtils.showStatusMessage(requireContext(), "Starting calibration...")
        
        // Disable button during calibration
        binding.runCalibrationButton.isEnabled = false
        
        lifecycleScope.launch {
            try {
                // Use the actual CalibrationCaptureManager for calibration
                val result = calibrationCaptureManager.captureCalibrationImages(
                    calibrationId = null, // Auto-generate ID
                    captureRgb = true,
                    captureThermal = true,
                    highResolution = true
                )
                
                if (result.success) {
                    val successMessage = "✅ Calibration capture successful!\nCalibration ID: ${result.calibrationId}"
                    updateCalibrationStatus(successMessage)
                    UIUtils.showStatusMessage(requireContext(), "Calibration completed successfully!", true)
                } else {
                    val errorMessage = "❌ Calibration capture failed: ${result.errorMessage}"
                    updateCalibrationStatus(errorMessage)
                    UIUtils.showStatusMessage(requireContext(), "Calibration failed: ${result.errorMessage}", true)
                }
            } catch (e: Exception) {
                val errorMessage = "❌ Calibration error: ${e.message}"
                updateCalibrationStatus(errorMessage)
                UIUtils.showStatusMessage(requireContext(), "Calibration error: ${e.message}", true)
            } finally {
                // Re-enable button
                binding.runCalibrationButton.isEnabled = true
            }
        }
    }

    private fun updateCalibrationStatus(status: String) {
        binding.calibrationStatus.text = status
    }

    private fun updateCalibrationInstructions(instructions: String) {
        // Find the instructions TextView (the large placeholder area)
        // Use findViewById to find a known TextView ID instead of findViewsWithText
        val instructionsTextView = binding.root.findViewById<android.widget.TextView>(android.R.id.text1)
        if (instructionsTextView != null) {
            instructionsTextView.text = instructions
        } else {
            // Fallback - update any large text area found
            val allTextViews = binding.root.findViewById<android.view.ViewGroup>(android.R.id.content)
            findTextViewWithText(allTextViews, "Calibration instructions")?.text = instructions
        }
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