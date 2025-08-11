package com.multisensor.recording.util
import androidx.compose.ui.graphics.Colour
enum class ThermalColorPalette(
    val displayName: String,
    val colours: List<Colour>
) {
    IRON(
        "Iron",
        listOf(
            Colour(0xFF000000),
            Colour(0xFF800080),
            Colour(0xFFFF0000),
            Colour(0xFFFF8000),
            Colour(0xFFFFFF00),
            Colour(0xFFFFFFFF)
        )
    ),
    RAINBOW(
        "Rainbow",
        listOf(
            Colour(0xFF000080),
            Colour(0xFF0000FF),
            Colour(0xFF00FFFF),
            Colour(0xFF00FF00),
            Colour(0xFFFFFF00),
            Colour(0xFFFF0000)
        )
    ),
    GRAYSCALE(
        "Grayscale",
        listOf(
            Colour(0xFF000000),
            Colour(0xFF404040),
            Colour(0xFF808080),
            Colour(0xFFC0C0C0),
            Colour(0xFFFFFFFF)
        )
    ),
    INFERNO(
        "Inferno",
        listOf(
            Colour(0xFF000004),
            Colour(0xFF3B0F70),
            Colour(0xFF8C2981),
            Colour(0xFFDD513A),
            Colour(0xFFFCA50A),
            Colour(0xFFFCFFA4)
        )
    ),
    VIRIDIS(
        "Viridis",
        listOf(
            Colour(0xFF440154),
            Colour(0xFF31688E),
            Colour(0xFF35B779),
            Colour(0xFFFDE725)
        )
    );
    companion object {
        fun fromDisplayName(name: String): ThermalColorPalette {
            return values().find { it.displayName.equals(name, ignoreCase = true) } ?: IRON
        }
    }
}