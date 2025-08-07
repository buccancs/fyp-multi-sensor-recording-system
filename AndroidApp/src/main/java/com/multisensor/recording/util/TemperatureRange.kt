package com.multisensor.recording.util

/**
 * Data class representing a temperature range for thermal visualization
 * Used for setting display limits and color mapping
 */
data class TemperatureRange(
    val min: Float,
    val max: Float
) {
    init {
        require(min <= max) { "Minimum temperature must be less than or equal to maximum temperature" }
    }
    
    /**
     * Calculate the temperature span
     */
    val span: Float get() = max - min
    
    /**
     * Check if a temperature is within this range
     */
    fun contains(temperature: Float): Boolean = temperature in min..max
    
    /**
     * Normalize a temperature value to 0.0-1.0 range
     */
    fun normalize(temperature: Float): Float {
        if (span == 0f) return 0f
        return ((temperature - min) / span).coerceIn(0f, 1f)
    }
    
    /**
     * Get a temperature value from a normalized 0.0-1.0 position
     */
    fun fromNormalized(normalized: Float): Float {
        return min + (normalized.coerceIn(0f, 1f) * span)
    }
    
    companion object {
        /**
         * Default temperature range for body temperature sensing
         */
        val BODY_TEMPERATURE = TemperatureRange(30f, 40f)
        
        /**
         * Extended range for environmental monitoring
         */
        val ENVIRONMENT = TemperatureRange(0f, 50f)
        
        /**
         * Wide range for general thermal imaging
         */
        val GENERAL = TemperatureRange(-20f, 120f)
        
        /**
         * Create a range centered around a temperature with specified span
         */
        fun centered(center: Float, span: Float): TemperatureRange {
            val halfSpan = span / 2f
            return TemperatureRange(center - halfSpan, center + halfSpan)
        }
    }
}