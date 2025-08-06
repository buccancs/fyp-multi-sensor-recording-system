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

sealed class Screen(val route: String, val title: String, val icon: ImageVector) {
    object Recording : Screen("recording", "Recording", Icons.Filled.RadioButtonChecked)
    object Devices : Screen("devices", "Devices", Icons.Filled.Devices)
    object Calibration : Screen("calibration", "Calibration", Icons.Filled.Tune)
    object Files : Screen("files", "Files", Icons.Filled.Folder)
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MainComposeNavigation(
    navController: NavHostController = rememberNavController()
) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { 
                    Text("Multi-Sensor Recording") 
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer,
                    titleContentColor = MaterialTheme.colorScheme.onPrimaryContainer
                )
            )
        },
        bottomBar = {
            BottomNavigation(navController = navController)
        }
    ) { paddingValues ->
        NavHost(
            navController = navController,
            startDestination = Screen.Recording.route,
            modifier = Modifier.padding(paddingValues)
        ) {
            composable(Screen.Recording.route) {
                RecordingScreen()
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
        }
    }
}

@Composable
private fun BottomNavigation(navController: NavHostController) {
    val items = listOf(
        Screen.Recording,
        Screen.Devices,
        Screen.Calibration,
        Screen.Files
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
                        
                        popUpTo(navController.graph.startDestinationId) {
                            saveState = true
                        }
                        
                        launchSingleTop = true
                        
                        restoreState = true
                    }
                }
            )
        }
    }
}
