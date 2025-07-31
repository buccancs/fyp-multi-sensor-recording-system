package com.multisensor.recording.ui.components

import android.content.Context
import android.util.AttributeSet
import android.view.LayoutInflater
import android.widget.LinearLayout
import com.multisensor.recording.databinding.HandSegmentationControlBinding
import com.multisensor.recording.handsegmentation.HandSegmentationManager

/**
 * Hand Segmentation Control Component
 * 
 * UI component for controlling hand segmentation functionality during recording sessions.
 * Provides controls for enabling/disabling hand detection and managing cropped datasets.
 */
class HandSegmentationControlView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : LinearLayout(context, attrs, defStyleAttr) {
    
    private val binding: HandSegmentationControlBinding
    
    interface HandSegmentationControlListener {
        fun onHandSegmentationToggled(enabled: Boolean)
        fun onRealTimeProcessingToggled(enabled: Boolean)
        fun onCroppedDatasetToggled(enabled: Boolean)
        fun onSaveDatasetClicked()
        fun onClearDatasetClicked()
    }
    
    private var listener: HandSegmentationControlListener? = null
    
    init {
        binding = HandSegmentationControlBinding.inflate(LayoutInflater.from(context), this, true)
        setupControls()
    }
    
    private fun setupControls() {
        binding.apply {
            // Hand segmentation toggle
            switchHandSegmentation.setOnCheckedChangeListener { _, isChecked ->
                updateControlsEnabled(isChecked)
                listener?.onHandSegmentationToggled(isChecked)
            }
            
            // Real-time processing toggle
            switchRealTimeProcessing.setOnCheckedChangeListener { _, isChecked ->
                listener?.onRealTimeProcessingToggled(isChecked)
            }
            
            // Cropped dataset toggle
            switchCroppedDataset.setOnCheckedChangeListener { _, isChecked ->
                updateDatasetControlsEnabled(isChecked)
                listener?.onCroppedDatasetToggled(isChecked)
            }
            
            // Dataset management buttons
            buttonSaveDataset.setOnClickListener {
                listener?.onSaveDatasetClicked()
            }
            
            buttonClearDataset.setOnClickListener {
                listener?.onClearDatasetClicked()
            }
            
            // Initialize state
            updateControlsEnabled(false)
            updateDatasetControlsEnabled(false)
        }
    }
    
    fun setListener(listener: HandSegmentationControlListener?) {
        this.listener = listener
    }
    
    /**
     * Update UI with current hand segmentation status
     */
    fun updateStatus(status: HandSegmentationManager.HandSegmentationStatus) {
        binding.apply {
            // Update switches without triggering listeners
            switchHandSegmentation.setOnCheckedChangeListener(null)
            switchRealTimeProcessing.setOnCheckedChangeListener(null)
            switchCroppedDataset.setOnCheckedChangeListener(null)
            
            switchHandSegmentation.isChecked = status.isEnabled
            switchRealTimeProcessing.isChecked = status.isRealTimeProcessing
            switchCroppedDataset.isChecked = status.isCroppedDatasetEnabled
            
            // Restore listeners
            setupControls()
            
            // Update controls state
            updateControlsEnabled(status.isEnabled)
            updateDatasetControlsEnabled(status.isCroppedDatasetEnabled)
            
            // Update dataset statistics
            updateDatasetStats(
                totalSamples = status.totalSamples,
                leftHands = status.leftHands,
                rightHands = status.rightHands,
                averageConfidence = status.averageConfidence
            )
        }
    }
    
    /**
     * Update hand detection status display
     */
    fun updateHandDetectionStatus(isEnabled: Boolean, handsDetected: Int) {
        binding.apply {
            if (isEnabled && handsDetected > 0) {
                textHandDetectionStatus.text = "Hands detected: $handsDetected"
                textHandDetectionStatus.setTextColor(context.getColor(android.R.color.holo_green_dark))
            } else if (isEnabled) {
                textHandDetectionStatus.text = "Hand detection active"
                textHandDetectionStatus.setTextColor(context.getColor(android.R.color.holo_orange_dark))
            } else {
                textHandDetectionStatus.text = "Hand detection disabled"
                textHandDetectionStatus.setTextColor(context.getColor(android.R.color.darker_gray))
            }
        }
    }
    
    /**
     * Update dataset progress display
     */
    fun updateDatasetProgress(totalSamples: Int, leftHands: Int, rightHands: Int) {
        updateDatasetStats(totalSamples, leftHands, rightHands, 0.0)
    }
    
    /**
     * Update dataset statistics display
     */
    private fun updateDatasetStats(totalSamples: Int, leftHands: Int, rightHands: Int, averageConfidence: Double) {
        binding.apply {
            textDatasetStats.text = buildString {
                append("Dataset: $totalSamples samples")
                if (totalSamples > 0) {
                    append("\nLeft: $leftHands, Right: $rightHands")
                    if (averageConfidence > 0) {
                        append("\nAvg confidence: ${"%.2f".format(averageConfidence)}")
                    }
                }
            }
            
            // Enable save button only if there are samples
            buttonSaveDataset.isEnabled = totalSamples > 0
        }
    }
    
    /**
     * Show dataset saved confirmation
     */
    fun showDatasetSaved(datasetPath: String, totalSamples: Int) {
        binding.textDatasetStats.text = "Dataset saved: $totalSamples samples\nPath: $datasetPath"
        binding.textDatasetStats.setTextColor(context.getColor(android.R.color.holo_green_dark))
        
        // Reset color after a delay
        postDelayed({
            binding.textDatasetStats.setTextColor(context.getColor(android.R.color.primary_text_light))
        }, 3000)
    }
    
    /**
     * Show error message
     */
    fun showError(error: String) {
        binding.textHandDetectionStatus.text = "Error: $error"
        binding.textHandDetectionStatus.setTextColor(context.getColor(android.R.color.holo_red_dark))
        
        // Reset after a delay
        postDelayed({
            updateHandDetectionStatus(false, 0)
        }, 5000)
    }
    
    /**
     * Enable/disable controls based on hand segmentation state
     */
    private fun updateControlsEnabled(enabled: Boolean) {
        binding.apply {
            switchRealTimeProcessing.isEnabled = enabled
            switchCroppedDataset.isEnabled = enabled
            
            if (!enabled) {
                updateDatasetControlsEnabled(false)
            } else {
                updateDatasetControlsEnabled(switchCroppedDataset.isChecked)
            }
        }
    }
    
    /**
     * Enable/disable dataset controls
     */
    private fun updateDatasetControlsEnabled(enabled: Boolean) {
        binding.apply {
            buttonSaveDataset.isEnabled = enabled
            buttonClearDataset.isEnabled = enabled
        }
    }
}