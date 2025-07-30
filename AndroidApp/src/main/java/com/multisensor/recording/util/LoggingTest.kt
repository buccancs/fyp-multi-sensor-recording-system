package com.multisensor.recording.util

import android.content.Context
import android.os.Build

/**
 * Test class for AppLogger functionality
 * 
 * This class demonstrates and tests all logging features to verify
 * the centralized logging system is working correctly.
 */
object LoggingTest {
    
    fun runLoggingTest(context: Context) {
        AppLogger.i("LoggingTest", "=== Android Logging System Test Starting ===")
        AppLogger.i("LoggingTest", "Device: ${Build.MANUFACTURER} ${Build.MODEL}")
        AppLogger.i("LoggingTest", "Android Version: ${Build.VERSION.RELEASE} (API ${Build.VERSION.SDK_INT})")
        
        // Test all log levels
        AppLogger.v("LoggingTest", "This is a VERBOSE message")
        AppLogger.d("LoggingTest", "This is a DEBUG message")
        AppLogger.i("LoggingTest", "This is an INFO message")
        AppLogger.w("LoggingTest", "This is a WARNING message")
        AppLogger.e("LoggingTest", "This is an ERROR message")
        
        // Test exception logging
        try {
            throw RuntimeException("Test exception for logging")
        } catch (e: Exception) {
            AppLogger.logError("LoggingTest", "exception handling", e)
        }
        
        // Test method entry/exit logging
        AppLogger.logMethodEntry("LoggingTest", "testMethod", "param1", "param2")
        AppLogger.logMethodExit("LoggingTest", "testMethod", "success")
        
        // Test lifecycle logging
        AppLogger.logLifecycle("LoggingTest", "onCreate", "TestActivity")
        AppLogger.logLifecycle("LoggingTest", "onStart", "TestActivity")
        AppLogger.logLifecycle("LoggingTest", "onResume", "TestActivity")
        
        // Test network logging
        AppLogger.logNetwork("LoggingTest", "HTTP GET", "http://example.com", "200 OK")
        AppLogger.logNetwork("LoggingTest", "HTTP POST", "http://api.example.com", "403 Forbidden")
        
        // Test recording logging
        AppLogger.logRecording("LoggingTest", "start recording", "camera_front")
        AppLogger.logRecording("LoggingTest", "stop recording", "camera_front")
        
        // Test sensor logging
        AppLogger.logSensor("LoggingTest", "reading", "accelerometer", "x=1.2, y=0.8, z=9.8")
        AppLogger.logSensor("LoggingTest", "connected", "GSR sensor")
        
        // Test file logging
        AppLogger.logFile("LoggingTest", "save", "test_video.mp4", 1024L * 1024 * 50) // 50MB
        AppLogger.logFile("LoggingTest", "delete", "old_file.txt")
        
        // Test performance timing
        AppLogger.startTiming("LoggingTest", "video_processing")
        Thread.sleep(100) // Simulate work
        AppLogger.endTiming("LoggingTest", "video_processing")
        
        // Test memory usage
        AppLogger.logMemoryUsage("LoggingTest", "After test operations")
        
        // Test thread info
        AppLogger.logThreadInfo("LoggingTest", "Test thread status")
        
        // Test state changes
        AppLogger.logStateChange("LoggingTest", "CameraRecorder", "IDLE", "RECORDING")
        AppLogger.logStateChange("LoggingTest", "NetworkClient", "DISCONNECTED", "CONNECTED")
        
        // Test extension functions
        val testObject = TestClass()
        testObject.logI("Extension function test message")
        testObject.logD("Debug message from extension")
        testObject.logW("Warning message with extension")
        
        // Test log level changes
        AppLogger.i("LoggingTest", "Testing debug mode enable")
        AppLogger.setDebugEnabled(true)
        AppLogger.d("LoggingTest", "This debug message should be visible")
        
        AppLogger.setVerboseEnabled(true)
        AppLogger.v("LoggingTest", "This verbose message should be visible")
        
        AppLogger.setDebugEnabled(false)
        AppLogger.d("LoggingTest", "This debug message should be filtered out")
        
        AppLogger.setVerboseEnabled(false)
        AppLogger.v("LoggingTest", "This verbose message should be filtered out")
        
        // Reset to defaults
        AppLogger.setDebugEnabled(true)
        AppLogger.setVerboseEnabled(false)
        
        AppLogger.i("LoggingTest", "=== Android Logging System Test Completed ===")
    }
    
    /**
     * Test class for demonstrating extension functions
     */
    private class TestClass {
        // Extension functions are automatically available
    }
}