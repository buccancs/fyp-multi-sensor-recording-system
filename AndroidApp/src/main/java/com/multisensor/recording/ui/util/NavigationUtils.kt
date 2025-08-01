package com.multisensor.recording.ui.util

import android.content.Context
import android.content.Intent
import androidx.fragment.app.Fragment
import androidx.navigation.NavController
import androidx.navigation.fragment.findNavController
import com.multisensor.recording.R

/**
 * Navigation utility class to simplify and standardize navigation operations
 * throughout the application, reducing code duplication and ensuring consistent
 * navigation behavior across all fragments and activities.
 */
object NavigationUtils {

    /**
     * Navigate to a specific fragment using the navigation controller with
     * proper error handling and state management.
     */
    fun navigateToFragment(fragment: Fragment, destinationId: Int) {
        try {
            val navController = fragment.findNavController()
            if (navController.currentDestination?.id != destinationId) {
                navController.navigate(destinationId)
            }
        } catch (e: Exception) {
            // Handle navigation errors gracefully
            android.util.Log.e("NavigationUtils", "Navigation failed to destination $destinationId", e)
        }
    }

    /**
     * Launch an activity with proper intent handling and error management.
     * This method provides a centralized way to start activities with consistent
     * error handling and logging.
     */
    fun launchActivity(context: Context, activityClass: Class<*>, extras: Map<String, String>? = null) {
        try {
            val intent = Intent(context, activityClass).apply {
                extras?.forEach { (key, value) ->
                    putExtra(key, value)
                }
            }
            context.startActivity(intent)
        } catch (e: Exception) {
            android.util.Log.e("NavigationUtils", "Failed to launch activity ${activityClass.simpleName}", e)
        }
    }

    /**
     * Handle drawer navigation with consistent behavior and proper error handling.
     * This method centralizes drawer navigation logic to ensure consistent behavior
     * across different parts of the application.
     */
    fun handleDrawerNavigation(navController: NavController, itemId: Int): Boolean {
        return try {
            when (itemId) {
                R.id.nav_recording -> {
                    navController.navigate(R.id.nav_recording)
                    true
                }
                R.id.nav_devices -> {
                    navController.navigate(R.id.nav_devices)
                    true
                }
                R.id.nav_calibration -> {
                    navController.navigate(R.id.nav_calibration)
                    true
                }
                R.id.nav_files -> {
                    navController.navigate(R.id.nav_files)
                    true
                }
                else -> false
            }
        } catch (e: Exception) {
            android.util.Log.e("NavigationUtils", "Drawer navigation failed for item $itemId", e)
            false
        }
    }

    /**
     * Get the current navigation destination name for logging and analytics purposes.
     * This provides a centralized way to track user navigation patterns.
     */
    fun getCurrentDestinationName(navController: NavController): String {
        return when (navController.currentDestination?.id) {
            R.id.nav_recording -> "Recording"
            R.id.nav_devices -> "Devices"
            R.id.nav_calibration -> "Calibration"
            R.id.nav_files -> "Files"
            else -> "Unknown"
        }
    }

    /**
     * Check if navigation to a specific destination is currently possible.
     * This helps prevent navigation errors and provides consistent state checking.
     */
    fun canNavigateToDestination(navController: NavController, destinationId: Int): Boolean {
        return try {
            navController.graph.findNode(destinationId) != null &&
                    navController.currentDestination?.id != destinationId
        } catch (e: Exception) {
            false
        }
    }
}