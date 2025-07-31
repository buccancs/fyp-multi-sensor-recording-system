package com.multisensor.recording.handsegmentation

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Color
import android.util.Log
import kotlinx.coroutines.runBlocking
import java.io.File

/**
 * Hand Segmentation Demo Test
 * 
 * Simple test to validate hand segmentation functionality on Android
 */
class HandSegmentationDemo(private val context: Context) {
    
    companion object {
        private const val TAG = "HandSegmentationDemo"
    }
    
    fun runDemo(): Boolean {
        Log.i(TAG, "Starting hand segmentation demo")
        
        return try {
            // Create hand segmentation engine
            val engine = HandSegmentationEngine(context)
            
            // Initialize engine
            if (!engine.initialize()) {
                Log.e(TAG, "Failed to initialize hand segmentation engine")
                return false
            }
            
            // Create a test bitmap simulating a hand
            val testBitmap = createTestHandBitmap()
            
            // Process the test bitmap
            val result = runBlocking {
                engine.processFrame(testBitmap)
            }
            
            Log.i(TAG, "Demo processing result:")
            Log.i(TAG, "- Detected hands: ${result.detectedHands.size}")
            Log.i(TAG, "- Processing time: ${result.processingTimeMs}ms")
            Log.i(TAG, "- Mask bitmap created: ${result.maskBitmap != null}")
            Log.i(TAG, "- Processed bitmap created: ${result.processedBitmap != null}")
            
            // Test dataset functionality
            val stats = engine.getDatasetStats()
            Log.i(TAG, "Dataset stats: $stats")
            
            // Test saving dataset
            val datasetDir = engine.saveCroppedDataset("demo_test")
            if (datasetDir != null) {
                Log.i(TAG, "Dataset saved successfully to: ${datasetDir.absolutePath}")
            }
            
            // Cleanup
            engine.cleanup()
            
            Log.i(TAG, "Hand segmentation demo completed successfully")
            true
            
        } catch (e: Exception) {
            Log.e(TAG, "Hand segmentation demo failed", e)
            false
        }
    }
    
    /**
     * Create a test bitmap that simulates a hand (skin-colored region)
     */
    private fun createTestHandBitmap(): Bitmap {
        val width = 640
        val height = 480
        val bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
        
        // Fill with background color
        bitmap.eraseColor(Color.rgb(200, 200, 200))
        
        // Draw a hand-like shape in skin color
        val skinColor = Color.rgb(220, 180, 140) // Skin tone
        
        // Create a simple hand shape (rectangle with rounded "fingers")
        for (y in 150..350) {
            for (x in 200..400) {
                // Main palm area
                if (x in 200..350 && y in 200..350) {
                    bitmap.setPixel(x, y, skinColor)
                }
                // Fingers (simplified as rectangles)
                if (x in 220..240 && y in 150..200) bitmap.setPixel(x, y, skinColor) // Index finger
                if (x in 250..270 && y in 140..200) bitmap.setPixel(x, y, skinColor) // Middle finger
                if (x in 280..300 && y in 150..200) bitmap.setPixel(x, y, skinColor) // Ring finger
                if (x in 310..330 && y in 160..200) bitmap.setPixel(x, y, skinColor) // Pinky
                if (x in 180..220 && y in 240..280) bitmap.setPixel(x, y, skinColor) // Thumb
            }
        }
        
        return bitmap
    }
}