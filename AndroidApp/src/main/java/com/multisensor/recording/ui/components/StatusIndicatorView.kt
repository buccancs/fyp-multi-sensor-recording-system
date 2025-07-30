package com.multisensor.recording.ui.components

import android.content.Context
import android.util.AttributeSet
import android.view.View
import android.widget.LinearLayout
import android.widget.TextView
import androidx.core.content.ContextCompat

/**
 * Reusable status indicator component that consolidates redundant UI patterns.
 * Displays a colored indicator dot with status text.
 * 
 * Replaces multiple instances of View + TextView combinations used for:
 * - Connection status indicators
 * - Recording status indicators  
 * - Device status displays
 */
class StatusIndicatorView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : LinearLayout(context, attrs, defStyleAttr) {

    private val indicatorView: View
    private val statusText: TextView

    enum class StatusType {
        CONNECTED,
        DISCONNECTED,
        RECORDING,
        STOPPED,
        WARNING,
        ERROR
    }

    init {
        orientation = HORIZONTAL
        gravity = android.view.Gravity.CENTER_VERTICAL
        
        // Create indicator dot programmatically
        indicatorView = View(context).apply {
            layoutParams = LayoutParams(
                resources.getDimensionPixelSize(android.R.dimen.app_icon_size) / 3, // 16dp equivalent
                resources.getDimensionPixelSize(android.R.dimen.app_icon_size) / 3
            ).apply {
                marginEnd = resources.getDimensionPixelSize(android.R.dimen.app_icon_size) / 6 // 8dp equivalent
            }
            setBackgroundColor(ContextCompat.getColor(context, android.R.color.holo_red_light))
        }
        
        // Create status text programmatically
        statusText = TextView(context).apply {
            layoutParams = LayoutParams(0, LayoutParams.WRAP_CONTENT, 1f)
            text = "Status: Disconnected"
            setTextColor(ContextCompat.getColor(context, android.R.color.white))
            textSize = 14f
        }
        
        addView(indicatorView)
        addView(statusText)
    }

    /**
     * Update the status indicator with new status and text
     */
    fun setStatus(status: StatusType, text: String) {
        statusText.text = text
        
        val colorRes = when (status) {
            StatusType.CONNECTED -> android.R.color.holo_green_light
            StatusType.DISCONNECTED -> android.R.color.holo_red_light
            StatusType.RECORDING -> android.R.color.holo_green_dark
            StatusType.STOPPED -> android.R.color.darker_gray
            StatusType.WARNING -> android.R.color.holo_orange_light
            StatusType.ERROR -> android.R.color.holo_red_dark
        }
        
        indicatorView.setBackgroundColor(ContextCompat.getColor(context, colorRes))
    }

    /**
     * Set custom text color
     */
    fun setTextColor(colorRes: Int) {
        statusText.setTextColor(ContextCompat.getColor(context, colorRes))
    }

    /**
     * Set custom text size
     */
    fun setTextSize(sizeSp: Float) {
        statusText.textSize = sizeSp
    }
}