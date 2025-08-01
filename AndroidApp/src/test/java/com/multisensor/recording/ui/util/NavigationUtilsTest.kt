package com.multisensor.recording.ui.util

import android.content.Context
import android.content.Intent
import androidx.fragment.app.Fragment
import androidx.navigation.NavController
import androidx.navigation.NavDestination
import androidx.navigation.NavGraph
import androidx.test.core.app.ApplicationProvider
import com.multisensor.recording.R
import io.mockk.*
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [28])
class NavigationUtilsTest {

    private lateinit var mockFragment: Fragment
    private lateinit var mockNavController: NavController
    private lateinit var mockDestination: NavDestination
    private lateinit var mockNavGraph: NavGraph
    private lateinit var context: Context

    @Before
    fun setUp() {
        mockFragment = mockk()
        mockNavController = mockk()
        mockDestination = mockk()
        mockNavGraph = mockk()
        context = ApplicationProvider.getApplicationContext()

        // Setup common mock behaviors
        every { mockNavController.currentDestination } returns mockDestination
        every { mockNavController.graph } returns mockNavGraph
        every { mockDestination.id } returns R.id.nav_recording
    }

    @After
    fun tearDown() {
        clearAllMocks()
    }

    @Test
    fun `navigateToFragment should navigate when destination is different`() {
        // Given
        val destinationId = R.id.nav_devices
        every { mockFragment.findNavController() } returns mockNavController
        every { mockNavController.navigate(destinationId) } just Runs

        // When
        NavigationUtils.navigateToFragment(mockFragment, destinationId)

        // Then
        verify { mockNavController.navigate(destinationId) }
    }

    @Test
    fun `navigateToFragment should not navigate when destination is same`() {
        // Given
        val destinationId = R.id.nav_recording
        every { mockFragment.findNavController() } returns mockNavController

        // When
        NavigationUtils.navigateToFragment(mockFragment, destinationId)

        // Then
        verify(exactly = 0) { mockNavController.navigate(any<Int>()) }
    }

    @Test
    fun `navigateToFragment should handle navigation exceptions gracefully`() {
        // Given
        val destinationId = R.id.nav_devices
        every { mockFragment.findNavController() } throws RuntimeException("Navigation error")

        // When & Then - should not throw exception
        assertDoesNotThrow {
            NavigationUtils.navigateToFragment(mockFragment, destinationId)
        }
    }

    @Test
    fun `launchActivity should create correct intent without extras`() {
        // Given
        val activityClass = TestActivity::class.java
        mockkStatic(Intent::class)
        val mockIntent = mockk<Intent>(relaxed = true)
        every { Intent(context, activityClass) } returns mockIntent
        every { context.startActivity(any()) } just Runs

        // When
        NavigationUtils.launchActivity(context, activityClass)

        // Then
        verify { context.startActivity(mockIntent) }
        verify(exactly = 0) { mockIntent.putExtra(any<String>(), any<String>()) }
    }

    @Test
    fun `launchActivity should add extras when provided`() {
        // Given
        val activityClass = TestActivity::class.java
        val extras = mapOf("key1" to "value1", "key2" to "value2")
        mockkStatic(Intent::class)
        val mockIntent = mockk<Intent>(relaxed = true)
        every { Intent(context, activityClass) } returns mockIntent
        every { context.startActivity(any()) } just Runs

        // When
        NavigationUtils.launchActivity(context, activityClass, extras)

        // Then
        verify { context.startActivity(mockIntent) }
        verify { mockIntent.putExtra("key1", "value1") }
        verify { mockIntent.putExtra("key2", "value2") }
    }

    @Test
    fun `handleDrawerNavigation should navigate to recording`() {
        // Given
        every { mockNavController.navigate(R.id.nav_recording) } just Runs

        // When
        val result = NavigationUtils.handleDrawerNavigation(mockNavController, R.id.nav_recording)

        // Then
        assertTrue("Navigation should succeed", result)
        verify { mockNavController.navigate(R.id.nav_recording) }
    }

    @Test
    fun `handleDrawerNavigation should navigate to devices`() {
        // Given
        every { mockNavController.navigate(R.id.nav_devices) } just Runs

        // When
        val result = NavigationUtils.handleDrawerNavigation(mockNavController, R.id.nav_devices)

        // Then
        assertTrue("Navigation should succeed", result)
        verify { mockNavController.navigate(R.id.nav_devices) }
    }

    @Test
    fun `handleDrawerNavigation should navigate to calibration`() {
        // Given
        every { mockNavController.navigate(R.id.nav_calibration) } just Runs

        // When
        val result = NavigationUtils.handleDrawerNavigation(mockNavController, R.id.nav_calibration)

        // Then
        assertTrue("Navigation should succeed", result)
        verify { mockNavController.navigate(R.id.nav_calibration) }
    }

    @Test
    fun `handleDrawerNavigation should navigate to files`() {
        // Given
        every { mockNavController.navigate(R.id.nav_files) } just Runs

        // When
        val result = NavigationUtils.handleDrawerNavigation(mockNavController, R.id.nav_files)

        // Then
        assertTrue("Navigation should succeed", result)
        verify { mockNavController.navigate(R.id.nav_files) }
    }

    @Test
    fun `handleDrawerNavigation should return false for unknown item`() {
        // Given
        val unknownItemId = 999999

        // When
        val result = NavigationUtils.handleDrawerNavigation(mockNavController, unknownItemId)

        // Then
        assertFalse("Navigation should fail for unknown item", result)
        verify(exactly = 0) { mockNavController.navigate(any<Int>()) }
    }

    @Test
    fun `handleDrawerNavigation should handle navigation exceptions`() {
        // Given
        every { mockNavController.navigate(any<Int>()) } throws RuntimeException("Navigation error")

        // When
        val result = NavigationUtils.handleDrawerNavigation(mockNavController, R.id.nav_recording)

        // Then
        assertFalse("Navigation should fail gracefully", result)
    }

    @Test
    fun `getCurrentDestinationName should return correct names`() {
        // Test Recording
        every { mockDestination.id } returns R.id.nav_recording
        assertEquals("Recording", NavigationUtils.getCurrentDestinationName(mockNavController))

        // Test Devices
        every { mockDestination.id } returns R.id.nav_devices
        assertEquals("Devices", NavigationUtils.getCurrentDestinationName(mockNavController))

        // Test Calibration
        every { mockDestination.id } returns R.id.nav_calibration
        assertEquals("Calibration", NavigationUtils.getCurrentDestinationName(mockNavController))

        // Test Files
        every { mockDestination.id } returns R.id.nav_files
        assertEquals("Files", NavigationUtils.getCurrentDestinationName(mockNavController))

        // Test Unknown
        every { mockDestination.id } returns 999999
        assertEquals("Unknown", NavigationUtils.getCurrentDestinationName(mockNavController))
    }

    @Test
    fun `canNavigateToDestination should return true when destination exists and different`() {
        // Given
        val destinationId = R.id.nav_devices
        every { mockNavGraph.findNode(destinationId) } returns mockDestination
        every { mockDestination.id } returns R.id.nav_recording

        // When
        val result = NavigationUtils.canNavigateToDestination(mockNavController, destinationId)

        // Then
        assertTrue("Should be able to navigate to different destination", result)
    }

    @Test
    fun `canNavigateToDestination should return false when destination is current`() {
        // Given
        val destinationId = R.id.nav_recording
        every { mockNavGraph.findNode(destinationId) } returns mockDestination
        every { mockDestination.id } returns R.id.nav_recording

        // When
        val result = NavigationUtils.canNavigateToDestination(mockNavController, destinationId)

        // Then
        assertFalse("Should not navigate to same destination", result)
    }

    @Test
    fun `canNavigateToDestination should return false when destination does not exist`() {
        // Given
        val destinationId = 999999
        every { mockNavGraph.findNode(destinationId) } returns null

        // When
        val result = NavigationUtils.canNavigateToDestination(mockNavController, destinationId)

        // Then
        assertFalse("Should not navigate to non-existent destination", result)
    }

    @Test
    fun `canNavigateToDestination should handle exceptions gracefully`() {
        // Given
        val destinationId = R.id.nav_devices
        every { mockNavGraph.findNode(destinationId) } throws RuntimeException("Graph error")

        // When
        val result = NavigationUtils.canNavigateToDestination(mockNavController, destinationId)

        // Then
        assertFalse("Should handle exceptions gracefully", result)
    }

    // Helper class for testing activity launching
    private class TestActivity
}