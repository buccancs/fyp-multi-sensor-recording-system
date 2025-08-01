package com.multisensor.recording.controllers

import android.content.Context
import android.content.Intent
import android.hardware.usb.UsbDevice
import android.view.TextureView
import android.view.View
import android.widget.TextView
import androidx.activity.result.ActivityResultLauncher
import androidx.lifecycle.LifecycleCoroutineScope
import com.multisensor.recording.ui.MainViewModel
import io.mockk.*
import org.junit.After
import org.junit.Before
import org.junit.Test
import org.junit.Assert.*
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

/**
 * Unit tests for MainActivityCoordinator
 * Tests basic coordinator scenarios and feature controller integration
 */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [28])
class MainActivityCoordinatorTest {

    // Mocked dependencies
    private val mockPermissionController = mockk<PermissionController>(relaxed = true)
    private val mockUsbController = mockk<UsbController>(relaxed = true)
    private val mockShimmerController = mockk<ShimmerController>(relaxed = true)
    private val mockRecordingController = mockk<RecordingController>(relaxed = true)
    private val mockCalibrationController = mockk<CalibrationController>(relaxed = true)
    private val mockNetworkController = mockk<NetworkController>(relaxed = true)
    private val mockStatusDisplayController = mockk<StatusDisplayController>(relaxed = true)
    private val mockUIController = mockk<UIController>(relaxed = true)
    private val mockMenuController = mockk<MenuController>(relaxed = true)

    // Mocked callback and related objects
    private val mockCallback = mockk<MainActivityCoordinator.CoordinatorCallback>(relaxed = true)
    private val mockContext = mockk<Context>(relaxed = true)
    private val mockView = mockk<View>(relaxed = true)
    private val mockTextView = mockk<TextView>(relaxed = true)

    // System under test
    private lateinit var coordinator: MainActivityCoordinator

    @Before
    fun setUp() {
        // Set up callback mock
        every { mockCallback.getContext() } returns mockContext
        every { mockCallback.getBatteryLevelText() } returns mockTextView
        every { mockCallback.getPcConnectionStatus() } returns mockTextView
        every { mockCallback.getPcConnectionIndicator() } returns mockView
        every { mockCallback.getThermalConnectionStatus() } returns mockTextView
        every { mockCallback.getThermalConnectionIndicator() } returns mockView

        // Create coordinator instance
        coordinator = MainActivityCoordinator(
            mockPermissionController,
            mockUsbController,
            mockShimmerController,
            mockRecordingController,
            mockCalibrationController,
            mockNetworkController,
            mockStatusDisplayController,
            mockUIController,
            mockMenuController
        )
    }

    @After
    fun tearDown() {
        unmockkAll()
    }

    @Test
    fun `test coordinator initialization`() {
        // When
        coordinator.initialize(mockCallback)

        // Then - verify all controllers were set up
        verify { mockPermissionController.setCallback(any()) }
        verify { mockUsbController.setCallback(any()) }
        verify { mockShimmerController.setCallback(any()) }
        verify { mockRecordingController.setCallback(any()) }
        verify { mockCalibrationController.setCallback(any()) }
        verify { mockNetworkController.setCallback(any()) }
        verify { mockStatusDisplayController.setCallback(any()) }
        verify { mockUIController.setCallback(any()) }
        verify { mockMenuController.setCallback(any()) }
    }

    @Test
    fun `test coordinated operations`() {
        // Given
        coordinator.initialize(mockCallback)
        val mockContext = mockk<Context>()
        val mockIntent = mockk<Intent>()
        val mockTextureView = mockk<TextureView>()
        val mockViewModel = mockk<MainViewModel>()
        val mockLifecycleScope = mockk<LifecycleCoroutineScope>()

        // When - test permission check
        coordinator.checkPermissions(mockContext)

        // Then
        verify { mockPermissionController.checkPermissions(mockContext) }

        // When - test USB device intent handling
        coordinator.handleUsbDeviceIntent(mockContext, mockIntent)

        // Then
        verify { mockUsbController.handleUsbDeviceIntent(mockContext, mockIntent) }

        // When - test recording initialization
        coordinator.initializeRecordingSystem(mockContext, mockTextureView, mockViewModel)

        // Then
        verify { mockRecordingController.initializeRecordingSystem(mockContext, mockTextureView, mockViewModel) }

        // When - test recording start
        coordinator.startRecording(mockContext, mockViewModel)

        // Then
        verify { mockRecordingController.startRecording(mockContext, mockViewModel) }
        verify { mockNetworkController.updateStreamingUI(mockContext, true) }

        // When - test recording stop
        coordinator.stopRecording(mockContext, mockViewModel)

        // Then
        verify { mockRecordingController.stopRecording(mockContext, mockViewModel) }
        verify { mockNetworkController.updateStreamingUI(mockContext, false) }

        // When - test calibration
        coordinator.runCalibration(mockLifecycleScope)

        // Then
        verify { mockCalibrationController.runCalibration(mockLifecycleScope) }
    }

    @Test
    fun `test system status summary`() {
        // Given
        coordinator.initialize(mockCallback)
        val mockContext = mockk<Context>()
        
        every { mockPermissionController.getPermissionRetryCount() } returns 2
        every { mockUsbController.getUsbStatusSummary(mockContext) } returns "USB Status: Connected"
        every { mockShimmerController.getConnectionStatus() } returns "Shimmer Status: Connected"
        every { mockRecordingController.getRecordingStatus() } returns "Recording Status: Ready"
        every { mockCalibrationController.getCalibrationStatus() } returns "Calibration Status: Ready"
        every { mockNetworkController.getStreamingStatus() } returns "Network Status: Connected"

        // When
        val statusSummary = coordinator.getSystemStatusSummary(mockContext)

        // Then
        assertNotNull("Status summary should not be null", statusSummary)
        assertTrue("Status summary should contain coordinator info", statusSummary.contains("Coordinator Initialized: true"))
        assertTrue("Status summary should contain permission info", statusSummary.contains("Permission Retries: 2"))
        assertTrue("Status summary should contain USB status", statusSummary.contains("USB Status: Connected"))
    }

    @Test
    fun `test reset all states`() {
        // Given
        coordinator.initialize(mockCallback)

        // When
        coordinator.resetAllStates()

        // Then
        verify { mockPermissionController.resetState() }
        verify { mockShimmerController.resetState() }
        verify { mockRecordingController.resetState() }
        verify { mockCalibrationController.resetState() }
        verify { mockNetworkController.resetState() }
    }

    @Test
    fun `test cleanup`() {
        // Given
        coordinator.initialize(mockCallback)

        // When
        coordinator.cleanup()

        // Then
        verify { mockCalibrationController.cleanup() }
    }

    @Test
    fun `test menu operations`() {
        // Given
        coordinator.initialize(mockCallback)
        val mockMenu = mockk<android.view.Menu>()
        val mockActivity = mockk<android.app.Activity>()
        val mockMenuItem = mockk<android.view.MenuItem>()

        // When
        val menuCreated = coordinator.createOptionsMenu(mockMenu, mockActivity)
        val menuHandled = coordinator.handleOptionsItemSelected(mockMenuItem)

        // Then
        verify { mockMenuController.createOptionsMenu(mockMenu, mockActivity) }
        verify { mockMenuController.handleOptionsItemSelected(mockMenuItem) }
    }
}