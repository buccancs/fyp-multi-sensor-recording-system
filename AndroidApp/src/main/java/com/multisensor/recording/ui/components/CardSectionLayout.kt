package com.multisensor.recording.ui.components

import android.content.Context
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
                // TODO: Detect background color and set appropriate text color
                header.setLightTheme() // Default to light theme
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
}