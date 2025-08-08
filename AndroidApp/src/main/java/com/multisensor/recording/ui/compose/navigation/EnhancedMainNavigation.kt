package com.multisensor.recording.ui.compose.navigation

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.dp
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.multisensor.recording.ui.compose.screens.*

/**
 * Enhanced navigation for single-activity pattern.
 * Consolidates all activities into a unified Compose navigation system.
 */
sealed class Screen(val route: String, val title: String, val icon: ImageVector) {
    // Main navigation screens
    object Recording : Screen("recording", "Recording", Icons.Filled.RadioButtonChecked)
    object ThermalPreview : Screen("thermal_preview", "Preview", Icons.Filled.Visibility)
    object Devices : Screen("devices", "Devices", Icons.Filled.Devices)
    object Calibration : Screen("calibration", "Calibration", Icons.Filled.Tune)
    object Files : Screen("files", "Files", Icons.Filled.Folder)
    
    // Additional screens that were previously separate activities
    object Settings : Screen("settings", "Settings", Icons.Filled.Settings)
    object About : Screen("about", "About", Icons.Filled.Info)
    object Diagnostics : Screen("diagnostics", "Diagnostics", Icons.Filled.BugReport)
    object ShimmerSettings : Screen("shimmer_settings", "Shimmer", Icons.Filled.Bluetooth)
    object ShimmerVisualization : Screen("shimmer_viz", "Visualization", Icons.Filled.Analytics)
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun EnhancedMainNavigation(
    navController: NavHostController = rememberNavController()
) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { 
                    val navBackStackEntry by navController.currentBackStackEntryAsState()
                    val currentScreen = getScreenFromRoute(navBackStackEntry?.destination?.route)
                    Text(currentScreen?.title ?: "Multi-Sensor Recording")
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer,
                    titleContentColor = MaterialTheme.colorScheme.onPrimaryContainer
                ),
                actions = {
                    // Settings menu action
                    IconButton(
                        onClick = {
                            navController.navigate(Screen.Settings.route)
                        }
                    ) {
                        Icon(
                            imageVector = Icons.Default.Settings,
                            contentDescription = "Settings"
                        )
                    }
                }
            )
        },
        bottomBar = {
            EnhancedBottomNavigation(navController = navController)
        },
        floatingActionButton = {
            // Context-aware FAB based on current screen
            val navBackStackEntry by navController.currentBackStackEntryAsState()
            val currentRoute = navBackStackEntry?.destination?.route
            
            when (currentRoute) {
                Screen.Recording.route -> {
                    FloatingActionButton(
                        onClick = { /* Start/Stop Recording */ }
                    ) {
                        Icon(
                            imageVector = Icons.Default.FiberManualRecord,
                            contentDescription = "Start Recording"
                        )
                    }
                }
                Screen.Files.route -> {
                    FloatingActionButton(
                        onClick = { /* Refresh files */ }
                    ) {
                        Icon(
                            imageVector = Icons.Default.Refresh,
                            contentDescription = "Refresh"
                        )
                    }
                }
            }
        }
    ) { paddingValues ->
        NavHost(
            navController = navController,
            startDestination = Screen.Recording.route,
            modifier = Modifier.padding(paddingValues)
        ) {
            // Core recording screens
            composable(Screen.Recording.route) {
                RecordingScreen(
                    onNavigateToPreview = {
                        navController.navigate(Screen.ThermalPreview.route)
                    }
                )
            }
            
            composable(Screen.ThermalPreview.route) {
                ThermalPreviewScreen(
                    onNavigateBack = {
                        navController.popBackStack()
                    }
                )
            }
            
            composable(Screen.Devices.route) {
                DevicesScreen()
            }
            
            composable(Screen.Calibration.route) {
                CalibrationScreen()
            }
            
            composable(Screen.Files.route) {
                FilesScreen()
            }
            
            // Additional screens (previously separate activities)
            composable(Screen.Settings.route) {
                SettingsScreen(
                    onNavigateBack = {
                        navController.popBackStack()
                    }
                )
            }
            
            composable(Screen.About.route) {
                AboutScreen(
                    onNavigateBack = {
                        navController.popBackStack()
                    }
                )
            }
            
            composable(Screen.Diagnostics.route) {
                DiagnosticsScreen(
                    onNavigateBack = {
                        navController.popBackStack()
                    }
                )
            }
            
            composable(Screen.ShimmerSettings.route) {
                ShimmerSettingsScreen(
                    onNavigateBack = {
                        navController.popBackStack()
                    }
                )
            }
            
            composable(Screen.ShimmerVisualization.route) {
                ShimmerVisualizationScreen(
                    onNavigateBack = {
                        navController.popBackStack()
                    }
                )
            }
        }
    }
}

@Composable
private fun EnhancedBottomNavigation(navController: NavHostController) {
    val items = listOf(
        Screen.Recording,
        Screen.Devices,
        Screen.Calibration,
        Screen.Files,
        Screen.About
    )
    
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentDestination = navBackStackEntry?.destination

    NavigationBar {
        items.forEach { screen ->
            NavigationBarItem(
                icon = { 
                    Icon(
                        imageVector = screen.icon,
                        contentDescription = screen.title
                    )
                },
                label = { Text(screen.title) },
                selected = currentDestination?.hierarchy?.any { it.route == screen.route } == true,
                onClick = {
                    navController.navigate(screen.route) {
                        // Pop up to the start destination to avoid building up a large stack
                        popUpTo(navController.graph.startDestinationId) {
                            saveState = true
                        }
                        // Avoid multiple copies of the same destination when reselecting the same item
                        launchSingleTop = true
                        // Restore state when reselecting a previously selected item
                        restoreState = true
                    }
                }
            )
        }
    }
}

private fun getScreenFromRoute(route: String?): Screen? {
    return when (route) {
        Screen.Recording.route -> Screen.Recording
        Screen.ThermalPreview.route -> Screen.ThermalPreview
        Screen.Devices.route -> Screen.Devices
        Screen.Calibration.route -> Screen.Calibration
        Screen.Files.route -> Screen.Files
        Screen.Settings.route -> Screen.Settings
        Screen.About.route -> Screen.About
        Screen.Diagnostics.route -> Screen.Diagnostics
        Screen.ShimmerSettings.route -> Screen.ShimmerSettings
        Screen.ShimmerVisualization.route -> Screen.ShimmerVisualization
        else -> null
    }
}