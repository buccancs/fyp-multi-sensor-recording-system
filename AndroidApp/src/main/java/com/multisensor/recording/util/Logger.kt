package com.multisensor.recording.util

import android.util.Log

/**
 * Simplified logger for time synchronization functionality
 */
class Logger {
    companion object {
        private const val TAG = "MultiSensorRecording"
        
        // For unit testing - when true, logging is disabled
        var isTestMode = false
    }

    fun verbose(message: String, throwable: Throwable? = null) {
        if (!isTestMode) {
            Log.v(TAG, message, throwable)
        }
    }

    fun debug(message: String, throwable: Throwable? = null) {
        if (!isTestMode) {
            Log.d(TAG, message, throwable)
        }
    }

    fun info(message: String, throwable: Throwable? = null) {
        if (!isTestMode) {
            Log.i(TAG, message, throwable)
        }
    }

    fun warning(message: String, throwable: Throwable? = null) {
        if (!isTestMode) {
            Log.w(TAG, message, throwable)
        }
    }

    fun error(message: String, throwable: Throwable? = null) {
        if (!isTestMode) {
            Log.e(TAG, message, throwable)
        }
    }
}