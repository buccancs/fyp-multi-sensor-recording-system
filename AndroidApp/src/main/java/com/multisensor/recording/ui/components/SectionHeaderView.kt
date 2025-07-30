package com.multisensor.recording.ui.components

import android.content.Context
import android.graphics.Typeface
import android.util.AttributeSet
import android.util.TypedValue
import androidx.appcompat.widget.AppCompatTextView
import androidx.core.content.ContextCompat

/**
 * Reusable section header component that consolidates redundant UI patterns.
 * Displays consistent section headers with standardized styling.
 * 
 * Replaces multiple instances of TextView headers used for:
 * - Configuration section headers
 * - Activity title headers
 * - Form section dividers
 */
class SectionHeaderView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : AppCompatTextView(context, attrs, defStyleAttr) {

    enum class HeaderStyle {
        MAIN_TITLE,     // 24sp, bold, center aligned
        SECTION_HEADER, // 18sp, bold, left aligned
        SUB_HEADER      // 16sp, bold, left aligned
    }

    init {
        // Set default styling
        setHeaderStyle(HeaderStyle.SECTION_HEADER)
    }

    /**
     * Set the header style and text
     */
    fun setHeader(text: String, style: HeaderStyle = HeaderStyle.SECTION_HEADER) {
        this.text = text
        setHeaderStyle(style)
    }

    /**
     * Apply styling based on header type
     */
    private fun setHeaderStyle(style: HeaderStyle) {
        when (style) {
            HeaderStyle.MAIN_TITLE -> {
                setTextSize(TypedValue.COMPLEX_UNIT_SP, 24f)
                setTypeface(null, Typeface.BOLD)
                textAlignment = TEXT_ALIGNMENT_CENTER
                setTextColor(ContextCompat.getColor(context, android.R.color.black))
                setPadding(0, 0, 0, dpToPx(16))
            }
            HeaderStyle.SECTION_HEADER -> {
                setTextSize(TypedValue.COMPLEX_UNIT_SP, 18f)
                setTypeface(null, Typeface.BOLD)
                textAlignment = TEXT_ALIGNMENT_TEXT_START
                setTextColor(ContextCompat.getColor(context, android.R.color.black))
                setPadding(0, 0, 0, dpToPx(8))
            }
            HeaderStyle.SUB_HEADER -> {
                setTextSize(TypedValue.COMPLEX_UNIT_SP, 16f)
                setTypeface(null, Typeface.BOLD)
                textAlignment = TEXT_ALIGNMENT_TEXT_START
                setTextColor(ContextCompat.getColor(context, android.R.color.black))
                setPadding(0, 0, 0, dpToPx(4))
            }
        }
    }

    /**
     * Set custom text color
     */
    fun setHeaderTextColor(colorRes: Int) {
        setTextColor(ContextCompat.getColor(context, colorRes))
    }

    /**
     * Set custom text color for dark backgrounds
     */
    fun setDarkTheme() {
        setTextColor(ContextCompat.getColor(context, android.R.color.white))
    }

    /**
     * Set custom text color for light backgrounds
     */
    fun setLightTheme() {
        setTextColor(ContextCompat.getColor(context, android.R.color.black))
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