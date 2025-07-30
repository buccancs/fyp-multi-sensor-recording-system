package com.multisensor.recording.ui.components

import android.content.Context
import android.graphics.Color
import android.util.AttributeSet
import android.util.TypedValue
import androidx.appcompat.widget.AppCompatTextView
import androidx.core.content.ContextCompat

/**
 * Reusable label text component that consolidates redundant UI patterns.
 * Displays consistent form labels and descriptive text with standardized styling.
 * 
 * Replaces multiple instances of TextView labels used for:
 * - Form field labels
 * - Configuration option descriptions
 * - Help text and instructions
 */
class LabelTextView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : AppCompatTextView(context, attrs, defStyleAttr) {

    enum class LabelStyle {
        FORM_LABEL,         // 14sp, gray, standard margin
        DESCRIPTION,        // 12sp, light gray, smaller margin
        INSTRUCTION,        // 14sp, darker gray, larger margin
        ERROR,              // 14sp, red, standard margin
        SUCCESS             // 14sp, green, standard margin
    }

    init {
        // Set default styling
        setLabelStyle(LabelStyle.FORM_LABEL)
    }

    /**
     * Set the label style and text
     */
    fun setLabel(text: String, style: LabelStyle = LabelStyle.FORM_LABEL) {
        this.text = text
        setLabelStyle(style)
    }

    /**
     * Apply styling based on label type
     */
    private fun setLabelStyle(style: LabelStyle) {
        when (style) {
            LabelStyle.FORM_LABEL -> {
                setTextSize(TypedValue.COMPLEX_UNIT_SP, 14f)
                setTextColor(Color.parseColor("#666666"))
                setPadding(0, 0, 0, dpToPx(4))
            }
            LabelStyle.DESCRIPTION -> {
                setTextSize(TypedValue.COMPLEX_UNIT_SP, 12f)
                setTextColor(Color.parseColor("#888888"))
                setPadding(0, 0, 0, dpToPx(2))
            }
            LabelStyle.INSTRUCTION -> {
                setTextSize(TypedValue.COMPLEX_UNIT_SP, 14f)
                setTextColor(Color.parseColor("#444444"))
                setPadding(0, 0, 0, dpToPx(8))
            }
            LabelStyle.ERROR -> {
                setTextSize(TypedValue.COMPLEX_UNIT_SP, 14f)
                setTextColor(ContextCompat.getColor(context, android.R.color.holo_red_dark))
                setPadding(0, 0, 0, dpToPx(4))
            }
            LabelStyle.SUCCESS -> {
                setTextSize(TypedValue.COMPLEX_UNIT_SP, 14f)
                setTextColor(ContextCompat.getColor(context, android.R.color.holo_green_dark))
                setPadding(0, 0, 0, dpToPx(4))
            }
        }
    }

    /**
     * Set custom text color
     */
    fun setLabelTextColor(colorRes: Int) {
        setTextColor(ContextCompat.getColor(context, colorRes))
    }

    /**
     * Set custom text color using hex string
     */
    fun setLabelTextColor(hexColor: String) {
        setTextColor(Color.parseColor(hexColor))
    }

    /**
     * Set label for dark backgrounds
     */
    fun setDarkTheme() {
        setTextColor(Color.parseColor("#CCCCCC"))
    }

    /**
     * Set label for light backgrounds
     */
    fun setLightTheme() {
        setTextColor(Color.parseColor("#666666"))
    }

    /**
     * Set as required field indicator (adds asterisk)
     */
    fun setRequired(isRequired: Boolean) {
        if (isRequired && !text.toString().endsWith("*")) {
            text = "${text}*"
            // Make the asterisk red
            val spannableText = android.text.SpannableString(text)
            spannableText.setSpan(
                android.text.style.ForegroundColorSpan(Color.RED),
                text.length - 1,
                text.length,
                android.text.Spannable.SPAN_EXCLUSIVE_EXCLUSIVE
            )
            setText(spannableText, BufferType.SPANNABLE)
        }
    }

    /**
     * Set as clickable help text
     */
    fun setClickableHelp(clickListener: OnClickListener?) {
        isClickable = true
        setOnClickListener(clickListener)
        // Add underline to indicate clickability
        paintFlags = paintFlags or android.graphics.Paint.UNDERLINE_TEXT_FLAG
    }

    /**
     * Convert dp to pixels
     */
    private fun dpToPx(dp: Int): Int {
        return TypedValue.applyDimension(
            TypedValue.COMPLEX_UNIT_DIP,
            dp.toFloat(),
            resources.displayMetrics
        ).toInt()
    }
}