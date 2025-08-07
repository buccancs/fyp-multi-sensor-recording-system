package com.multisensor.recording.util

import androidx.compose.ui.graphics.Color

/**
 * Enumeration of thermal color palettes for enhanced thermal visualization
 * Each palette provides distinctive visual representations of temperature data
 */
enum class ThermalColorPalette(
    val displayName: String,
    val colors: List<Color>
) {
    IRON(
        "Iron", 
        listOf(
            Color(0xFF000000), // Black (cold)
            Color(0xFF800080), // Purple
            Color(0xFFFF0000), // Red
            Color(0xFFFF8000), // Orange
            Color(0xFFFFFF00), // Yellow
            Color(0xFFFFFFFF)  // White (hot)
        )
    ),
    
    RAINBOW(
        "Rainbow", 
        listOf(
            Color(0xFF000080), // Dark Blue (cold)
            Color(0xFF0000FF), // Blue
            Color(0xFF00FFFF), // Cyan
            Color(0xFF00FF00), // Green
            Color(0xFFFFFF00), // Yellow
            Color(0xFFFF0000)  // Red (hot)
        )
    ),
    
    GRAYSCALE(
        "Grayscale", 
        listOf(
            Color(0xFF000000), // Black (cold)
            Color(0xFF404040), // Dark Gray
            Color(0xFF808080), // Gray
            Color(0xFFC0C0C0), // Light Gray
            Color(0xFFFFFFFF)  // White (hot)
        )
    ),
    
    INFERNO(
        "Inferno", 
        listOf(
            Color(0xFF000004), // Almost Black
            Color(0xFF3B0F70), // Dark Purple
            Color(0xFF8C2981), // Purple
            Color(0xFFDD513A), // Orange
            Color(0xFFFCA50A), // Yellow-Orange
            Color(0xFFFCFFA4)  // Light Yellow
        )
    ),
    
    VIRIDIS(
        "Viridis", 
        listOf(
            Color(0xFF440154), // Dark Purple
            Color(0xFF31688E), // Blue
            Color(0xFF35B779), // Green
            Color(0xFFFDE725)  // Yellow
        )
    );
    
    companion object {
        /**
         * Get palette by name, defaulting to IRON if not found
         */
        fun fromDisplayName(name: String): ThermalColorPalette {
            return values().find { it.displayName.equals(name, ignoreCase = true) } ?: IRON
        }
    }
}