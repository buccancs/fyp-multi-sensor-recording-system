package com.multisensor.recording

import android.app.Application
import dagger.hilt.android.HiltAndroidApp

/**
 * Application class for the Multi-Sensor Recording System.
 * This class is annotated with @HiltAndroidApp to enable Hilt dependency injection
 * throughout the application.
 */
@HiltAndroidApp
class MultiSensorApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        // Initialize application-level components here if needed
        // For example: crash reporting, analytics, etc.

        // Log application startup
        android.util.Log.i("MultiSensorApp", "Multi-Sensor Recording Application started")
    }
}
