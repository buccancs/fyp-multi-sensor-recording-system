package com.multisensor.recording.ui.components

import android.content.Context
import android.graphics.Color
import android.graphics.drawable.ColorDrawable
import android.graphics.drawable.GradientDrawable
import android.util.AttributeSet
import android.util.TypedValue
import android.widget.LinearLayout
import androidx.core.content.ContextCompat

/**
 * Reusable card section layout component that consolidates redundant UI patterns.
 * Displays content in a card-like container with consistent styling.
 * 
 * Replaces multiple instances of LinearLayout containers used for:
 * - Configuration sections in ShimmerConfigActivity
 * - Form sections across activities
 * - Content grouping containers
 */
class CardSectionLayout @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : LinearLayout(context, attrs, defStyleAttr) {

    enum class CardStyle {
        DEFAULT,        // White background, standard padding, elevation
        COMPACT,        // White background, reduced padding, elevation
        FLAT,           // White background, standard padding, no elevation
        DARK            // Dark background, standard padding, elevation
    }

    init {
        // Set default styling
        setCardStyle(CardStyle.DEFAULT)
        orientation = VERTICAL
    }

    /**
     * Set the card style
     */
    fun setCardStyle(style: CardStyle) {
        when (style) {
            CardStyle.DEFAULT -> {
                setBackgroundColor(ContextCompat.getColor(context, android.R.color.white))
                setPadding(dpToPx(16), dpToPx(16), dpToPx(16), dpToPx(16))
                elevation = dpToPx(2).toFloat()
                setMargins(0, 0, 0, dpToPx(16))
            }
            CardStyle.COMPACT -> {
                setBackgroundColor(ContextCompat.getColor(context, android.R.color.white))
                setPadding(dpToPx(12), dpToPx(12), dpToPx(12), dpToPx(12))
                elevation = dpToPx(2).toFloat()
                setMargins(0, 0, 0, dpToPx(8))
            }
            CardStyle.FLAT -> {
                setBackgroundColor(ContextCompat.getColor(context, android.R.color.white))
                setPadding(dpToPx(16), dpToPx(16), dpToPx(16), dpToPx(16))
                elevation = 0f
                setMargins(0, 0, 0, dpToPx(16))
            }
            CardStyle.DARK -> {
                setBackgroundColor(ContextCompat.getColor(context, android.R.color.black))
                setPadding(dpToPx(16), dpToPx(16), dpToPx(16), dpToPx(16))
                elevation = dpToPx(2).toFloat()
                setMargins(0, 0, 0, dpToPx(16))
            }
        }
    }

    /**
     * Set custom background color
     */
    fun setCardBackgroundColor(colorRes: Int) {
        setBackgroundColor(ContextCompat.getColor(context, colorRes))
    }

    /**
     * Set custom padding
     */
    fun setCardPadding(paddingDp: Int) {
        val paddingPx = dpToPx(paddingDp)
        setPadding(paddingPx, paddingPx, paddingPx, paddingPx)
    }

    /**
     * Set custom elevation
     */
    fun setCardElevation(elevationDp: Int) {
        elevation = dpToPx(elevationDp).toFloat()
    }

    /**
     * Set margins for the card
     */
    private fun setMargins(left: Int, top: Int, right: Int, bottom: Int) {
        val params = layoutParams as? MarginLayoutParams ?: MarginLayoutParams(
            LayoutParams.MATCH_PARENT,
            LayoutParams.WRAP_CONTENT
        )
        params.setMargins(left, top, right, bottom)
        layoutParams = params
    }

    /**
     * Add a header to the card
     */
    fun addHeader(headerText: String, headerStyle: SectionHeaderView.HeaderStyle = SectionHeaderView.HeaderStyle.SECTION_HEADER) {
        val header = SectionHeaderView(context)
        header.setHeader(headerText, headerStyle)
        
        // Adjust header color based on card background
        when {
            background != null -> {
                // Detect background color and set appropriate text color
                val backgroundColor = extractBackgroundColor()
                if (isColorDark(backgroundColor)) {
                    header.setDarkTheme() // Light text on dark background
                } else {
                    header.setLightTheme() // Dark text on light background
                }
            }
            else -> header.setLightTheme()
        }
        
        addView(header, 0) // Add at the beginning
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

    /**
     * Extract the dominant color from the background drawable
     */
    private fun extractBackgroundColor(): Int {
        return when (val bg = background) {
            is ColorDrawable -> bg.color
            is GradientDrawable -> {
                // For gradient drawables, we can't easily extract the color
                // Default to a neutral assumption (light background)
                Color.WHITE
            }
            else -> {
                // For other drawables (e.g., images, shapes), default to light
                Color.WHITE
            }
        }
    }

    /**
     * Determine if a color is considered dark
     * Uses the relative luminance formula to determine darkness
     */
    private fun isColorDark(color: Int): Boolean {
        // Extract RGB components
        val red = Color.red(color)
        val green = Color.green(color)
        val blue = Color.blue(color)
        
        // Calculate relative luminance using the sRGB color space formula
        // https://www.w3.org/TR/WCAG20/#relativeluminancedef
        val luminance = (0.299 * red + 0.587 * green + 0.114 * blue) / 255.0
        
        // Consider dark if luminance is below 0.5 (50%)
        return luminance < 0.5
    }
}