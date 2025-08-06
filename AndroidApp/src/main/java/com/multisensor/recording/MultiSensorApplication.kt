package com.multisensor.recording

import android.app.Application
import dagger.hilt.android.HiltAndroidApp

@HiltAndroidApp
class MultiSensorApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        android.util.Log.i("MultiSensorApp", "Multi-Sensor Recording Application started")
    }
}

