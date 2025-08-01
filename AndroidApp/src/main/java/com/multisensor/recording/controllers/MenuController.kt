package com.multisensor.recording.controllers

import com.multisensor.recording.util.AppLogger
import com.multisensor.recording.util.logI
import com.multisensor.recording.util.logE

import android.app.Activity
import android.app.AlertDialog
import android.content.Context
import android.content.Intent
import android.view.Menu
import android.view.MenuItem
import androidx.lifecycle.LifecycleCoroutineScope
import com.multisensor.recording.R
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Controller responsible for handling all menu and dialog system logic.
 * Extracted from MainActivity to improve separation of concerns and testability.
 * Manages options menu, menu item selections, and dialog displays.
 * 
 * TODO: Complete integration with MainActivity refactoring
 * TODO: Add comprehensive unit tests for menu scenarios
 * TODO: Implement menu state persistence across configuration changes
 * TODO: Add support for dynamic menu items and context menus
 * TODO: Implement menu accessibility features
 */
@Singleton
class MenuController @Inject constructor() {
    
    /**
     * Interface for menu-related callbacks to the UI layer
     */
    interface MenuCallback {
        fun onMenuItemSelected(itemId: Int): Boolean
        fun onAboutDialogRequested()
        fun onSettingsRequested()
        fun onNetworkConfigRequested()
        fun onFileBrowserRequested()
        fun onShimmerConfigRequested()
        fun onSyncTestRequested(testType: SyncTestType)
        fun onSyncStatusRequested()
        fun onMenuError(message: String)
        fun updateStatusText(text: String)
        fun showToast(message: String, duration: Int = android.widget.Toast.LENGTH_SHORT)
        fun getContext(): Context
    }
    
    /**
     * Sync test types for menu actions
     */
    enum class SyncTestType {
        FLASH_SYNC,
        BEEP_SYNC,
        CLOCK_SYNC
    }

    private var callback: MenuCallback? = null
    
    // Menu state tracking
    private val menuItemSelectionCount = mutableMapOf<Int, Int>()
    private val menuAccessHistory = mutableListOf<MenuAccessRecord>()
    private var lastMenuInteraction = 0L
    
    /**
     * Data class for tracking menu access patterns
     */
    data class MenuAccessRecord(
        val itemId: Int,
        val timestamp: Long,
        val itemTitle: String
    )
    
    /**
     * Set the callback for menu events
     */
    fun setCallback(callback: MenuCallback) {
        this.callback = callback
    }
    
    /**
     * Creates the options menu for MainActivity
     * Extracted from MainActivity.onCreateOptionsMenu()
     */
    fun createOptionsMenu(menu: Menu, activity: Activity): Boolean {
        android.util.Log.d("MenuController", "[DEBUG_LOG] Creating options menu")
        
        try {
            activity.menuInflater.inflate(R.menu.main_menu, menu)
            return true
        } catch (e: Exception) {
            android.util.Log.e("MenuController", "[DEBUG_LOG] Failed to create options menu: ${e.message}")
            callback?.onMenuError("Failed to create options menu: ${e.message}")
            return false
        }
    }
    
    /**
     * Handles options menu item selections
     * Extracted from MainActivity.onOptionsItemSelected()
     */
    fun handleOptionsItemSelected(item: MenuItem): Boolean {
        android.util.Log.d("MenuController", "[DEBUG_LOG] Menu item selected: ${item.itemId}")
        
        // Track menu item selection
        trackMenuItemSelection(item.itemId, item.title?.toString() ?: "Unknown")
        
        return when (item.itemId) {
            R.id.action_settings -> {
                handleSettingsAction()
                true
            }
            R.id.action_network_config -> {
                handleNetworkConfigAction()
                true
            }
            R.id.action_file_browser -> {
                handleFileBrowserAction()
                true
            }
            R.id.action_shimmer_config -> {
                handleShimmerConfigAction()
                true
            }
            R.id.action_test_flash_sync -> {
                handleSyncTestAction(SyncTestType.FLASH_SYNC)
                true
            }
            R.id.action_test_beep_sync -> {
                handleSyncTestAction(SyncTestType.BEEP_SYNC)
                true
            }
            R.id.action_test_clock_sync -> {
                handleSyncTestAction(SyncTestType.CLOCK_SYNC)
                true
            }
            R.id.action_sync_status -> {
                handleSyncStatusAction()
                true
            }
            R.id.action_about -> {
                handleAboutAction()
                true
            }
            else -> {
                android.util.Log.d("MenuController", "[DEBUG_LOG] Unhandled menu item: ${item.itemId}")
                false
            }
        }
    }
    
    /**
     * Track menu item selection for analytics and debugging
     */
    private fun trackMenuItemSelection(itemId: Int, itemTitle: String) {
        lastMenuInteraction = System.currentTimeMillis()
        
        // Update selection count
        menuItemSelectionCount[itemId] = (menuItemSelectionCount[itemId] ?: 0) + 1
        
        // Add to access history (keep last 50 records)
        menuAccessHistory.add(MenuAccessRecord(itemId, lastMenuInteraction, itemTitle))
        if (menuAccessHistory.size > 50) {
            menuAccessHistory.removeAt(0)
        }
        
        android.util.Log.d("MenuController", "[DEBUG_LOG] Menu tracking: $itemTitle selected ${menuItemSelectionCount[itemId]} times")
    }
    
    /**
     * Handle Settings menu action
     */
    private fun handleSettingsAction() {
        android.util.Log.d("MenuController", "[DEBUG_LOG] Opening Settings")
        
        try {
            val context = callback?.getContext() ?: throw IllegalStateException("Context not available")
            val intent = Intent(context, com.multisensor.recording.ui.SettingsActivity::class.java)
            context.startActivity(intent)
            callback?.onSettingsRequested()
        } catch (e: Exception) {
            android.util.Log.e("MenuController", "[DEBUG_LOG] Failed to open Settings: ${e.message}")
            callback?.onMenuError("Failed to open Settings: ${e.message}")
        }
    }
    
    /**
     * Handle Network Configuration menu action
     */
    private fun handleNetworkConfigAction() {
        android.util.Log.d("MenuController", "[DEBUG_LOG] Opening Network Configuration")
        
        try {
            val context = callback?.getContext() ?: throw IllegalStateException("Context not available")
            val intent = Intent(context, com.multisensor.recording.ui.NetworkConfigActivity::class.java)
            context.startActivity(intent)
            callback?.onNetworkConfigRequested()
        } catch (e: Exception) {
            android.util.Log.e("MenuController", "[DEBUG_LOG] Failed to open Network Configuration: ${e.message}")
            callback?.onMenuError("Failed to open Network Configuration: ${e.message}")
        }
    }
    
    /**
     * Handle File Browser menu action
     */
    private fun handleFileBrowserAction() {
        android.util.Log.d("MenuController", "[DEBUG_LOG] Opening File Browser")
        
        try {
            val context = callback?.getContext() ?: throw IllegalStateException("Context not available")
            val intent = Intent(context, com.multisensor.recording.ui.FileViewActivity::class.java)
            context.startActivity(intent)
            callback?.onFileBrowserRequested()
        } catch (e: Exception) {
            android.util.Log.e("MenuController", "[DEBUG_LOG] Failed to open File Browser: ${e.message}")
            callback?.onMenuError("Failed to open File Browser: ${e.message}")
        }
    }
    
    /**
     * Handle Shimmer Configuration menu action
     */
    private fun handleShimmerConfigAction() {
        android.util.Log.d("MenuController", "[DEBUG_LOG] Opening Shimmer Configuration")
        
        try {
            val context = callback?.getContext() ?: throw IllegalStateException("Context not available")
            val intent = Intent(context, com.multisensor.recording.ui.ShimmerConfigActivity::class.java)
            context.startActivity(intent)
            callback?.onShimmerConfigRequested()
        } catch (e: Exception) {
            android.util.Log.e("MenuController", "[DEBUG_LOG] Failed to open Shimmer Configuration: ${e.message}")
            callback?.onMenuError("Failed to open Shimmer Configuration: ${e.message}")
        }
    }
    
    /**
     * Handle sync test menu actions
     */
    private fun handleSyncTestAction(testType: SyncTestType) {
        val testName = when (testType) {
            SyncTestType.FLASH_SYNC -> "Flash Sync"
            SyncTestType.BEEP_SYNC -> "Beep Sync"
            SyncTestType.CLOCK_SYNC -> "Clock Sync"
        }
        
        android.util.Log.d("MenuController", "[DEBUG_LOG] Testing $testName - TODO: Implement via coordinator")
        callback?.onSyncTestRequested(testType)
        callback?.showToast("$testName test - Coming soon")
    }
    
    /**
     * Handle sync status menu action
     */
    private fun handleSyncStatusAction() {
        android.util.Log.d("MenuController", "[DEBUG_LOG] Showing Sync Status - TODO: Implement via coordinator")
        callback?.onSyncStatusRequested()
        callback?.showToast("Sync Status - Coming soon")
    }
    
    /**
     * Handle About menu action
     */
    private fun handleAboutAction() {
        android.util.Log.d("MenuController", "[DEBUG_LOG] Showing About dialog")
        callback?.onAboutDialogRequested()
        showAboutDialog()
    }
    
    /**
     * Shows About dialog with app information
     * Extracted from MainActivity.showAboutDialog()
     */
    private fun showAboutDialog() {
        val context = callback?.getContext()
        if (context == null) {
            android.util.Log.e("MenuController", "[DEBUG_LOG] Cannot show About dialog - context not available")
            callback?.onMenuError("Cannot show About dialog - context not available")
            return
        }
        
        try {
            val aboutMessage = """
                Multi-Sensor Recording System
                
                Version: 1.0.0
                Build: Milestone 2.7 Complete
                
                Features:
                • Real-time status monitoring
                • Manual recording controls
                • Calibration capture feedback
                • Comprehensive settings interface
                • Adaptive frame rate control
                
                Developed with ❤️ for multi-sensor data collection
            """.trimIndent()

            AlertDialog.Builder(context)
                .setTitle("About Multi-Sensor Recording")
                .setMessage(aboutMessage)
                .setIcon(R.drawable.ic_multisensor_idle)
                .setPositiveButton("OK") { dialog, _ -> dialog.dismiss() }
                .show()

            android.util.Log.d("MenuController", "[DEBUG_LOG] About dialog displayed")
        } catch (e: Exception) {
            android.util.Log.e("MenuController", "[DEBUG_LOG] Failed to show About dialog: ${e.message}")
            callback?.onMenuError("Failed to show About dialog: ${e.message}")
        }
    }
    
    /**
     * Get menu controller status for debugging
     */
    fun getMenuStatus(): String {
        return buildString {
            append("Menu Controller Status:\n")
            append("- Callback Set: ${callback != null}\n")
            append("- Context Available: ${callback?.getContext() != null}\n")
            append("- Total Menu Interactions: ${menuItemSelectionCount.values.sum()}\n")
            append("- Unique Items Used: ${menuItemSelectionCount.size}\n")
            append("- Last Interaction: ${if (lastMenuInteraction > 0) 
                java.text.SimpleDateFormat("HH:mm:ss", java.util.Locale.getDefault()).format(java.util.Date(lastMenuInteraction))
                else "Never"}\n")
            append("- Most Used Item: ${getMostUsedMenuItem()}")
        }
    }
    
    /**
     * Get the most frequently used menu item
     */
    private fun getMostUsedMenuItem(): String {
        return menuItemSelectionCount.maxByOrNull { it.value }?.let { entry ->
            val itemName = menuAccessHistory.findLast { it.itemId == entry.key }?.itemTitle ?: "Unknown"
            "$itemName (${entry.value} times)"
        } ?: "None"
    }
    
    /**
     * Reset menu controller state
     */
    fun resetState() {
        android.util.Log.d("MenuController", "[DEBUG_LOG] Menu controller state reset")
        
        // Reset menu tracking state
        menuItemSelectionCount.clear()
        menuAccessHistory.clear()
        lastMenuInteraction = 0L
        
        android.util.Log.d("MenuController", "[DEBUG_LOG] Menu tracking data cleared")
    }
    
    /**
     * Cleanup menu resources
     */
    fun cleanup() {
        try {
            callback = null
            android.util.Log.d("MenuController", "[DEBUG_LOG] Menu controller resources cleaned up")
        } catch (e: Exception) {
            android.util.Log.w("MenuController", "[DEBUG_LOG] Error during menu cleanup: ${e.message}")
        }
    }
    
    /**
     * Check if menu item should be enabled
     * TODO: Implement dynamic menu item state management
     */
    fun isMenuItemEnabled(itemId: Int): Boolean {
        return when (itemId) {
            R.id.action_settings,
            R.id.action_network_config,
            R.id.action_file_browser,
            R.id.action_shimmer_config,
            R.id.action_about -> true
            R.id.action_test_flash_sync,
            R.id.action_test_beep_sync,
            R.id.action_test_clock_sync,
            R.id.action_sync_status -> {
                // TODO: Check if sync features are available
                true
            }
            else -> false
        }
    }
    
    /**
     * Update menu item visibility based on app state
     * Implements dynamic menu updates
     */
    fun updateMenuVisibility(menu: Menu, isRecording: Boolean) {
        android.util.Log.d("MenuController", "[DEBUG_LOG] Menu visibility update - recording: $isRecording")
        
        try {
            // Disable certain menu items during recording
            menu.findItem(R.id.action_settings)?.isEnabled = !isRecording
            menu.findItem(R.id.action_network_config)?.isEnabled = !isRecording
            menu.findItem(R.id.action_shimmer_config)?.isEnabled = !isRecording
            
            // Sync test items should only be available when not recording
            menu.findItem(R.id.action_test_flash_sync)?.isEnabled = !isRecording
            menu.findItem(R.id.action_test_beep_sync)?.isEnabled = !isRecording
            menu.findItem(R.id.action_test_clock_sync)?.isEnabled = !isRecording
            
            // Sync status can be checked anytime
            menu.findItem(R.id.action_sync_status)?.isEnabled = true
            
            // File browser may be restricted during recording
            menu.findItem(R.id.action_file_browser)?.isEnabled = !isRecording
            
            // About dialog can be accessed anytime
            menu.findItem(R.id.action_about)?.isEnabled = true
            
            android.util.Log.d("MenuController", "[DEBUG_LOG] Menu items ${if (isRecording) "disabled" else "enabled"} for recording state")
            
        } catch (e: Exception) {
            android.util.Log.e("MenuController", "[DEBUG_LOG] Error updating menu visibility: ${e.message}")
        }
    }
    
    /**
     * Check if sync features are available
     */
    private fun areSyncFeaturesAvailable(): Boolean {
        // In a real implementation, this would check:
        // - Network connectivity
        // - Server availability
        // - Sync service status
        return true // Simplified for now
    }
    
    /**
     * Get menu item usage statistics
     */
    fun getMenuUsageStatistics(): Map<String, Any> {
        return mapOf(
            "total_interactions" to menuItemSelectionCount.values.sum(),
            "unique_items_used" to menuItemSelectionCount.size,
            "most_used_item" to getMostUsedMenuItem(),
            "last_interaction" to lastMenuInteraction,
            "interaction_history_size" to menuAccessHistory.size,
            "average_interactions_per_item" to if (menuItemSelectionCount.isNotEmpty()) 
                menuItemSelectionCount.values.average() else 0.0
        )
    }
}