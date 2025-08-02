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
import com.multisensor.recording.databinding.FragmentCalibrationBinding
import com.multisensor.recording.ui.MainViewModel
import com.multisensor.recording.ui.MainUiState
import dagger.hilt.android.AndroidEntryPoint

/**
 * Calibration Fragment
 * 
 * Calibration and system setup interface.
 * Features:
 * - Camera calibration procedures
 * - Sensor calibration
 * - System validation
 * - Calibration status monitoring
 */
@AndroidEntryPoint
class CalibrationFragment : Fragment() {
    
    private var _binding: FragmentCalibrationBinding? = null
    private val binding get() = _binding!!
    
    private val viewModel: MainViewModel by activityViewModels()
    
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
        
        setupUI()
        observeViewModel()
    }
    
    private fun setupUI() {
        // Camera calibration controls
        binding.startCameraCalibrationButton.setOnClickListener {
            viewModel.startCameraCalibration()
        }
        
        binding.stopCameraCalibrationButton.setOnClickListener {
            viewModel.stopCameraCalibration()
        }
        
        binding.resetCameraCalibrationButton.setOnClickListener {
            viewModel.resetCameraCalibration()
        }
        
        // Thermal calibration controls
        binding.startThermalCalibrationButton.setOnClickListener {
            viewModel.startThermalCalibration()
        }
        
        binding.stopThermalCalibrationButton.setOnClickListener {
            viewModel.stopThermalCalibration()
        }
        
        binding.resetThermalCalibrationButton.setOnClickListener {
            viewModel.resetThermalCalibration()
        }
        
        // Shimmer calibration controls
        binding.startShimmerCalibrationButton.setOnClickListener {
            viewModel.startShimmerCalibration()
        }
        
        binding.stopShimmerCalibrationButton.setOnClickListener {
            viewModel.stopShimmerCalibration()
        }
        
        binding.resetShimmerCalibrationButton.setOnClickListener {
            viewModel.resetShimmerCalibration()
        }
        
        // System validation
        binding.validateSystemButton.setOnClickListener {
            viewModel.validateSystem()
        }
        
        binding.runDiagnosticsButton.setOnClickListener {
            viewModel.runDiagnostics()
        }
        
        // Calibration data management
        binding.saveCalibrationButton.setOnClickListener {
            viewModel.saveCalibrationData()
        }
        
        binding.loadCalibrationButton.setOnClickListener {
            viewModel.loadCalibrationData()
        }
        
        binding.exportCalibrationButton.setOnClickListener {
            viewModel.exportCalibrationData()
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
        // Update calibration status indicators
        updateCalibrationStatus(binding.cameraCalibrationStatus, binding.cameraCalibrationIndicator, state.isCameraCalibrated)
        updateCalibrationStatus(binding.thermalCalibrationStatus, binding.thermalCalibrationIndicator, state.isThermalCalibrated)
        updateCalibrationStatus(binding.shimmerCalibrationStatus, binding.shimmerCalibrationIndicator, state.isShimmerCalibrated)
        
        // Update calibration progress
        binding.cameraCalibrationProgress.visibility = if (state.isCalibratingCamera) View.VISIBLE else View.GONE
        binding.thermalCalibrationProgress.visibility = if (state.isCalibratingThermal) View.VISIBLE else View.GONE
        binding.shimmerCalibrationProgress.visibility = if (state.isCalibratingShimmer) View.VISIBLE else View.GONE
        
        // Update button states
        updateCalibrationButtons(state)
        
        // Update system validation status
        binding.systemValidationStatus.text = when {
            state.isSystemValidated -> "System validated successfully"
            state.isValidating -> "Validating system..."
            else -> "System not validated"
        }
        
        binding.systemValidationIndicator.setBackgroundResource(
            if (state.isSystemValidated) android.R.color.holo_green_light 
            else android.R.color.holo_orange_light
        )
        
        // Update validation progress
        binding.systemValidationProgress.visibility = if (state.isValidating) View.VISIBLE else View.GONE
        binding.validateSystemButton.isEnabled = !state.isValidating
        
        // Update diagnostics status
        binding.diagnosticsStatus.text = when {
            state.isDiagnosticsRunning -> "Running diagnostics..."
            state.diagnosticsCompleted -> "Diagnostics completed"
            else -> "Ready to run diagnostics"
        }
        
        binding.runDiagnosticsButton.isEnabled = !state.isDiagnosticsRunning
        binding.diagnosticsProgress.visibility = if (state.isDiagnosticsRunning) View.VISIBLE else View.GONE
    }
    
    private fun updateCalibrationStatus(statusText: com.google.android.material.textview.MaterialTextView,
                                       indicator: View,
                                       isCalibrated: Boolean) {
        statusText.text = if (isCalibrated) "Calibrated" else "Not Calibrated"
        indicator.setBackgroundResource(
            if (isCalibrated) android.R.color.holo_green_light else android.R.color.holo_red_light
        )
    }
    
    private fun updateCalibrationButtons(state: MainUiState) {
        // Camera calibration buttons
        binding.startCameraCalibrationButton.isEnabled = !state.isCalibratingCamera && state.isCameraConnected
        binding.stopCameraCalibrationButton.isEnabled = state.isCalibratingCamera
        binding.resetCameraCalibrationButton.isEnabled = !state.isCalibratingCamera && state.isCameraCalibrated
        
        // Thermal calibration buttons
        binding.startThermalCalibrationButton.isEnabled = !state.isCalibratingThermal && state.isThermalConnected
        binding.stopThermalCalibrationButton.isEnabled = state.isCalibratingThermal
        binding.resetThermalCalibrationButton.isEnabled = !state.isCalibratingThermal && state.isThermalCalibrated
        
        // Shimmer calibration buttons
        binding.startShimmerCalibrationButton.isEnabled = !state.isCalibratingShimmer && state.isShimmerConnected
        binding.stopShimmerCalibrationButton.isEnabled = state.isCalibratingShimmer
        binding.resetShimmerCalibrationButton.isEnabled = !state.isCalibratingShimmer && state.isShimmerCalibrated
        
        // Calibration data management buttons
        val hasCalibrationData = state.isCameraCalibrated || state.isThermalCalibrated || state.isShimmerCalibrated
        binding.saveCalibrationButton.isEnabled = hasCalibrationData
        binding.exportCalibrationButton.isEnabled = hasCalibrationData
    }
    
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}