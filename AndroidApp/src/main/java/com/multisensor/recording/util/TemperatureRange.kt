package com.multisensor.recording.util
data class TemperatureRange(
    val min: Float,
    val max: Float
) {
    init {
        require(min <= max) { "Minimum temperature must be less than or equal to maximum temperature" }
    }
    val span: Float get() = max - min
    fun contains(temperature: Float): Boolean = temperature in min..max
    fun normalize(temperature: Float): Float {
        if (span == 0f) return 0f
        return ((temperature - min) / span).coerceIn(0f, 1f)
    }
    fun fromNormalized(normalized: Float): Float {
        return min + (normalized.coerceIn(0f, 1f) * span)
    }
    companion object {
        val BODY_TEMPERATURE = TemperatureRange(30f, 40f)
        val ENVIRONMENT = TemperatureRange(0f, 50f)
        val GENERAL = TemperatureRange(-20f, 120f)
        fun centered(center: Float, span: Float): TemperatureRange {
            val halfSpan = span / 2f
            return TemperatureRange(center - halfSpan, center + halfSpan)
        }
    }
}