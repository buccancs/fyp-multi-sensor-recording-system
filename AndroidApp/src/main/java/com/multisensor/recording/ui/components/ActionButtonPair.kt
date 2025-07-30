package com.multisensor.recording.ui.components

import android.content.Context
import android.util.AttributeSet
import android.widget.Button
import android.widget.LinearLayout
import androidx.core.content.ContextCompat

/**
 * Reusable action button pair component that consolidates redundant UI patterns.
 * Displays two buttons side by side with consistent styling.
 * 
 * Replaces multiple instances of button pairs used for:
 * - Start/Stop recording buttons
 * - Connect/Disconnect buttons  
 * - Reset/Save configuration buttons
 * - Other action pairs throughout the app
 */
class ActionButtonPair @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : LinearLayout(context, attrs, defStyleAttr) {

    private val leftButton: Button
    private val rightButton: Button

    enum class ButtonStyle {
        PRIMARY,    // Green background
        SECONDARY,  // Red background  
        NEUTRAL,    // Gray background
        WARNING     // Orange background
    }

    init {
        orientation = HORIZONTAL
        
        // Create left button
        leftButton = Button(context).apply {
            layoutParams = LayoutParams(0, LayoutParams.WRAP_CONTENT, 1f).apply {
                marginEnd = resources.getDimensionPixelSize(android.R.dimen.app_icon_size) / 6 // 8dp
            }
            setTextColor(ContextCompat.getColor(context, android.R.color.white))
            setPadding(
                resources.getDimensionPixelSize(android.R.dimen.app_icon_size) / 4, // 12dp
                resources.getDimensionPixelSize(android.R.dimen.app_icon_size) / 4,
                resources.getDimensionPixelSize(android.R.dimen.app_icon_size) / 4,
                resources.getDimensionPixelSize(android.R.dimen.app_icon_size) / 4
            )
        }
        
        // Create right button
        rightButton = Button(context).apply {
            layoutParams = LayoutParams(0, LayoutParams.WRAP_CONTENT, 1f).apply {
                marginStart = resources.getDimensionPixelSize(android.R.dimen.app_icon_size) / 6 // 8dp
            }
            setTextColor(ContextCompat.getColor(context, android.R.color.white))
            setPadding(
                resources.getDimensionPixelSize(android.R.dimen.app_icon_size) / 4, // 12dp
                resources.getDimensionPixelSize(android.R.dimen.app_icon_size) / 4,
                resources.getDimensionPixelSize(android.R.dimen.app_icon_size) / 4,
                resources.getDimensionPixelSize(android.R.dimen.app_icon_size) / 4
            )
        }
        
        addView(leftButton)
        addView(rightButton)
    }

    /**
     * Configure the button pair with text and styles
     */
    fun setButtons(
        leftText: String,
        rightText: String,
        leftStyle: ButtonStyle = ButtonStyle.PRIMARY,
        rightStyle: ButtonStyle = ButtonStyle.SECONDARY
    ) {
        leftButton.text = leftText
        rightButton.text = rightText
        
        leftButton.backgroundTintList = ContextCompat.getColorStateList(context, getColorForStyle(leftStyle))
        rightButton.backgroundTintList = ContextCompat.getColorStateList(context, getColorForStyle(rightStyle))
    }

    /**
     * Set click listeners for the buttons
     */
    fun setOnClickListeners(
        leftClickListener: OnClickListener?,
        rightClickListener: OnClickListener?
    ) {
        leftButton.setOnClickListener(leftClickListener)
        rightButton.setOnClickListener(rightClickListener)
    }

    /**
     * Enable/disable buttons
     */
    fun setButtonsEnabled(leftEnabled: Boolean, rightEnabled: Boolean) {
        leftButton.isEnabled = leftEnabled
        rightButton.isEnabled = rightEnabled
    }

    /**
     * Get references to individual buttons for advanced customization
     */
    fun getLeftButton(): Button = leftButton
    fun getRightButton(): Button = rightButton

    private fun getColorForStyle(style: ButtonStyle): Int {
        return when (style) {
            ButtonStyle.PRIMARY -> android.R.color.holo_green_dark
            ButtonStyle.SECONDARY -> android.R.color.holo_red_dark
            ButtonStyle.NEUTRAL -> android.R.color.darker_gray
            ButtonStyle.WARNING -> android.R.color.holo_orange_dark
        }
    }
}