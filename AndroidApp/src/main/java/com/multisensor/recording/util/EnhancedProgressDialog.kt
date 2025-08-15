package com.multisensor.recording.util

import android.app.Dialog
import android.content.Context
import android.view.LayoutInflater
import android.view.View
import android.widget.Button
import android.widget.ProgressBar
import android.widget.TextView
import androidx.appcompat.app.AlertDialog
import com.multisensor.recording.R
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

/**
 * Enhanced Progress Dialog Manager for Professional Button API
 * Provides sophisticated progress tracking, error handling, and user feedback
 */
class EnhancedProgressDialog(private val context: Context) {
    
    private var dialog: AlertDialog? = null
    private var progressBar: ProgressBar? = null
    private var titleText: TextView? = null
    private var stepText: TextView? = null
    private var detailText: TextView? = null
    private var cancelButton: Button? = null
    private var retryButton: Button? = null
    private var actionButtonsContainer: View? = null
    
    private var onCancelCallback: (() -> Unit)? = null
    private var onRetryCallback: (() -> Unit)? = null
    
    /**
     * Professional progress step for advanced validation workflow
     */
    data class ProgressStep(
        val title: String,
        val description: String,
        val progress: Int,
        val isError: Boolean = false,
        val errorMessage: String? = null
    )
    
    /**
     * Show enhanced progress dialog with professional styling
     */
    fun show(title: String = "Processing...", cancelable: Boolean = false): EnhancedProgressDialog {
        val view = LayoutInflater.from(context).inflate(R.layout.dialog_enhanced_progress, null)
        
        progressBar = view.findViewById(R.id.progress_bar)
        titleText = view.findViewById(R.id.tv_progress_title)
        stepText = view.findViewById(R.id.tv_progress_step)
        detailText = view.findViewById(R.id.tv_progress_detail)
        cancelButton = view.findViewById(R.id.btn_cancel)
        retryButton = view.findViewById(R.id.btn_retry)
        actionButtonsContainer = view.findViewById(R.id.ll_action_buttons)
        
        titleText?.text = title
        
        // Setup button listeners
        cancelButton?.setOnClickListener {
            onCancelCallback?.invoke()
            dismiss()
        }
        
        retryButton?.setOnClickListener {
            hideActionButtons()
            onRetryCallback?.invoke()
        }
        
        dialog = AlertDialog.Builder(context)
            .setView(view)
            .setCancelable(cancelable)
            .create()
            
        dialog?.window?.setBackgroundDrawableResource(android.R.color.transparent)
        dialog?.show()
        
        return this
    }
    
    /**
     * Update progress with professional step information
     */
    fun updateProgress(step: ProgressStep) {
        titleText?.text = step.title
        stepText?.text = step.description
        progressBar?.progress = step.progress
        
        if (step.isError) {
            stepText?.setTextColor(context.getColor(R.color.text_error))
            detailText?.text = step.errorMessage ?: "An error occurred"
            detailText?.setTextColor(context.getColor(R.color.text_error))
            showActionButtons()
        } else {
            stepText?.setTextColor(context.getColor(R.color.text_secondary))
            detailText?.setTextColor(context.getColor(R.color.text_tertiary))
        }
    }
    
    /**
     * Set step description and detail text
     */
    fun setStep(step: String, detail: String = "") {
        stepText?.text = step
        if (detail.isNotEmpty()) {
            detailText?.text = detail
            detailText?.visibility = View.VISIBLE
        } else {
            detailText?.visibility = View.GONE
        }
    }
    
    /**
     * Set progress percentage
     */
    fun setProgress(progress: Int) {
        progressBar?.progress = progress.coerceIn(0, 100)
    }
    
    /**
     * Show action buttons for error scenarios
     */
    private fun showActionButtons() {
        actionButtonsContainer?.visibility = View.VISIBLE
    }
    
    /**
     * Hide action buttons during normal operation
     */
    private fun hideActionButtons() {
        actionButtonsContainer?.visibility = View.GONE
    }
    
    /**
     * Set cancel callback for professional error handling
     */
    fun setOnCancelCallback(callback: () -> Unit): EnhancedProgressDialog {
        onCancelCallback = callback
        return this
    }
    
    /**
     * Set retry callback for fault tolerance
     */
    fun setOnRetryCallback(callback: () -> Unit): EnhancedProgressDialog {
        onRetryCallback = callback
        return this
    }
    
    /**
     * Dismiss dialog
     */
    fun dismiss() {
        dialog?.dismiss()
        dialog = null
    }
    
    /**
     * Professional multi-step progress execution
     */
    suspend fun executeSteps(
        steps: List<ProgressStep>,
        onStepComplete: suspend (ProgressStep) -> Boolean = { true }
    ): Boolean {
        return withContext(Dispatchers.Main) {
            for ((index, step) in steps.withIndex()) {
                updateProgress(step)
                
                // Execute step in background - real validation only
                val success = withContext(Dispatchers.IO) {
                    try {
                        onStepComplete(step)
                    } catch (e: Exception) {
                        Logger.e("EnhancedProgressDialog", "Step failed: ${e.message}")
                        false
                    }
                }
                
                if (!success) {
                    updateProgress(step.copy(
                        title = "Error occurred",
                        description = "Step failed: ${step.title}",
                        isError = true,
                        errorMessage = "Please check system settings and try again"
                    ))
                    return@withContext false
                }
                
                // Update progress for completed step
                setProgress(((index + 1) * 100) / steps.size)
            }
            
            true
        }
    }
    
    companion object {
        /**
         * Quick builder for common validation scenarios
         */
        fun createValidationDialog(context: Context): EnhancedProgressDialog {
            return EnhancedProgressDialog(context).apply {
                show("System Validation", false)
            }
        }
        
        /**
         * Quick builder for device connection scenarios
         */
        fun createConnectionDialog(context: Context): EnhancedProgressDialog {
            return EnhancedProgressDialog(context).apply {
                show("Connecting Devices", true)
                setOnCancelCallback {
                    Logger.i("EnhancedProgressDialog", "Device connection cancelled by user")
                }
            }
        }
        
        /**
         * Real validation steps for system security
         */
        fun getSecurityValidationSteps(): List<ProgressStep> {
            return listOf(
                ProgressStep(
                    "Security Validation", 
                    "Checking authentication tokens...", 
                    20
                ),
                ProgressStep(
                    "Security Validation", 
                    "Validating TLS encryption...", 
                    50
                ),
                ProgressStep(
                    "Security Validation", 
                    "Verifying system permissions...", 
                    80
                ),
                ProgressStep(
                    "Security Validation Complete", 
                    "All security checks passed", 
                    100
                )
            )
        }
        
        /**
         * Real device connection steps
         */
        fun getDeviceConnectionSteps(): List<ProgressStep> {
            return listOf(
                ProgressStep(
                    "Connecting Devices", 
                    "Performing security validation...", 
                    10
                ),
                ProgressStep(
                    "Connecting Devices", 
                    "Initializing RGB camera...", 
                    25
                ),
                ProgressStep(
                    "Connecting Devices", 
                    "Establishing thermal camera connection...", 
                    50
                ),
                ProgressStep(
                    "Connecting Devices", 
                    "Configuring GSR sensor...", 
                    75
                ),
                ProgressStep(
                    "Connecting Devices", 
                    "Synchronizing device clocks...", 
                    90
                ),
                ProgressStep(
                    "Connection Complete", 
                    "All devices ready for recording", 
                    100
                )
            )
        }
    }
}