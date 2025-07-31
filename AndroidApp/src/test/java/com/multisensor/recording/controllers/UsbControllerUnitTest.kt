package com.multisensor.recording.controllers

import android.content.Context
import android.content.Intent
import android.hardware.usb.UsbDevice
import android.hardware.usb.UsbManager
import com.multisensor.recording.managers.UsbDeviceManager
import io.mockk.*
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

/**
 * Comprehensive unit tests for UsbController.
 * Tests USB device integration controller, callback handling,
 * and coordination with UsbDeviceManager for bulletproof Topdon integration.
 */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [33])
class UsbControllerUnitTest {

    private lateinit var usbController: UsbController
    private lateinit var mockUsbDeviceManager: UsbDeviceManager
    private lateinit var mockCallback: UsbController.UsbCallback
    private lateinit var mockContext: Context

    @Before
    fun setup() {
        mockUsbDeviceManager = mockk(relaxed = true)
        mockCallback = mockk(relaxed = true)
        mockContext = mockk(relaxed = true)

        usbController = UsbController(mockUsbDeviceManager)
        usbController.setCallback(mockCallback)
    }

    @After
    fun teardown() {
        clearAllMocks()
    }

    @Test
    fun `setCallback should update callback reference`() {
        // Given
        val newCallback = mockk<UsbController.UsbCallback>(relaxed = true)

        // When
        usbController.setCallback(newCallback)

        // Then - verify new callback is used by triggering a USB event
        val mockDevice = createMockUsbDevice(vendorId = 0x0BDA, productId = 0x3901)
        val intent = createUsbDeviceIntent(UsbManager.ACTION_USB_DEVICE_ATTACHED, mockDevice)
        every { mockUsbDeviceManager.isSupportedTopdonDevice(mockDevice) } returns true

        usbController.handleUsbDeviceIntent(mockContext, intent)

        verify { newCallback.onSupportedDeviceAttached(mockDevice) }
        verify(exactly = 0) { mockCallback.onSupportedDeviceAttached(any()) }
    }

    @Test
    fun `handleUsbDeviceIntent should handle supported device attachment`() {
        // Given
        val mockDevice = createMockUsbDevice(vendorId = 0x0BDA, productId = 0x3901)
        val intent = createUsbDeviceIntent(UsbManager.ACTION_USB_DEVICE_ATTACHED, mockDevice)
        every { mockUsbDeviceManager.isSupportedTopdonDevice(mockDevice) } returns true
        every { mockCallback.areAllPermissionsGranted() } returns true

        // When
        usbController.handleUsbDeviceIntent(mockContext, intent)

        // Then
        verify { mockCallback.onSupportedDeviceAttached(mockDevice) }
        verify { mockCallback.updateStatusText(match { it.contains("thermal camera connected") }) }
        verify { mockCallback.initializeRecordingSystem() }
    }

    @Test
    fun `handleUsbDeviceIntent should handle supported device without permissions`() {
        // Given
        val mockDevice = createMockUsbDevice(vendorId = 0x0BDA, productId = 0x3901)
        val intent = createUsbDeviceIntent(UsbManager.ACTION_USB_DEVICE_ATTACHED, mockDevice)
        every { mockUsbDeviceManager.isSupportedTopdonDevice(mockDevice) } returns true
        every { mockCallback.areAllPermissionsGranted() } returns false

        // When
        usbController.handleUsbDeviceIntent(mockContext, intent)

        // Then
        verify { mockCallback.onSupportedDeviceAttached(mockDevice) }
        verify { mockCallback.updateStatusText(match { it.contains("Please grant permissions") }) }
        verify(exactly = 0) { mockCallback.initializeRecordingSystem() }
    }

    @Test
    fun `handleUsbDeviceIntent should handle unsupported device attachment`() {
        // Given
        val mockDevice = createMockUsbDevice(vendorId = 0x1234, productId = 0x5678)
        val intent = createUsbDeviceIntent(UsbManager.ACTION_USB_DEVICE_ATTACHED, mockDevice)
        every { mockUsbDeviceManager.isSupportedTopdonDevice(mockDevice) } returns false

        // When
        usbController.handleUsbDeviceIntent(mockContext, intent)

        // Then
        verify { mockCallback.onUnsupportedDeviceAttached(mockDevice) }
        verify(exactly = 0) { mockCallback.onSupportedDeviceAttached(any()) }
        verify(exactly = 0) { mockCallback.initializeRecordingSystem() }
    }

    @Test
    fun `handleUsbDeviceIntent should handle device detachment`() {
        // Given
        val mockDevice = createMockUsbDevice(vendorId = 0x0BDA, productId = 0x3901)
        val intent = createUsbDeviceIntent(UsbManager.ACTION_USB_DEVICE_DETACHED, mockDevice)
        every { mockUsbDeviceManager.isSupportedTopdonDevice(mockDevice) } returns true

        // When
        usbController.handleUsbDeviceIntent(mockContext, intent)

        // Then
        verify { mockCallback.onDeviceDetached(mockDevice) }
        verify { mockCallback.updateStatusText(match { it.contains("disconnected") }) }
    }

    @Test
    fun `handleUsbDeviceIntent should handle unsupported device detachment`() {
        // Given
        val mockDevice = createMockUsbDevice(vendorId = 0x1234, productId = 0x5678)
        val intent = createUsbDeviceIntent(UsbManager.ACTION_USB_DEVICE_DETACHED, mockDevice)
        every { mockUsbDeviceManager.isSupportedTopdonDevice(mockDevice) } returns false

        // When
        usbController.handleUsbDeviceIntent(mockContext, intent)

        // Then
        verify { mockCallback.onDeviceDetached(mockDevice) }
        verify(exactly = 0) { mockCallback.updateStatusText(match { it.contains("disconnected") }) }
    }

    @Test
    fun `handleUsbDeviceIntent should handle missing device in intent`() {
        // Given
        val intent = createUsbDeviceIntent(UsbManager.ACTION_USB_DEVICE_ATTACHED, null)

        // When
        usbController.handleUsbDeviceIntent(mockContext, intent)

        // Then
        verify { mockCallback.onUsbError(match { it.contains("no device information available") }) }
    }

    @Test
    fun `handleUsbDeviceIntent should handle unknown action`() {
        // Given
        val mockDevice = createMockUsbDevice(vendorId = 0x0BDA, productId = 0x3901)
        val intent = createUsbDeviceIntent("unknown.action", mockDevice)

        // When
        usbController.handleUsbDeviceIntent(mockContext, intent)

        // Then
        // Should not trigger any callbacks for unknown actions
        verify(exactly = 0) { mockCallback.onSupportedDeviceAttached(any()) }
        verify(exactly = 0) { mockCallback.onUnsupportedDeviceAttached(any()) }
        verify(exactly = 0) { mockCallback.onDeviceDetached(any()) }
    }

    @Test
    fun `getConnectedUsbDevices should delegate to UsbDeviceManager`() {
        // Given
        val expectedDevices = listOf(
            createMockUsbDevice(vendorId = 0x0BDA, productId = 0x3901),
            createMockUsbDevice(vendorId = 0x1234, productId = 0x5678)
        )
        every { mockUsbDeviceManager.getConnectedUsbDevices(mockContext) } returns expectedDevices

        // When
        val devices = usbController.getConnectedUsbDevices(mockContext)

        // Then
        assertEquals("Should return devices from UsbDeviceManager", expectedDevices, devices)
        verify { mockUsbDeviceManager.getConnectedUsbDevices(mockContext) }
    }

    @Test
    fun `getConnectedSupportedDevices should delegate to UsbDeviceManager`() {
        // Given
        val expectedDevices = listOf(
            createMockUsbDevice(vendorId = 0x0BDA, productId = 0x3901),
            createMockUsbDevice(vendorId = 0x0BDA, productId = 0x5840)
        )
        every { mockUsbDeviceManager.getConnectedSupportedDevices(mockContext) } returns expectedDevices

        // When
        val devices = usbController.getConnectedSupportedDevices(mockContext)

        // Then
        assertEquals("Should return supported devices from UsbDeviceManager", expectedDevices, devices)
        verify { mockUsbDeviceManager.getConnectedSupportedDevices(mockContext) }
    }

    @Test
    fun `hasSupportedDeviceConnected should delegate to UsbDeviceManager`() {
        // Given
        every { mockUsbDeviceManager.hasSupportedDeviceConnected(mockContext) } returns true

        // When
        val hasSupported = usbController.hasSupportedDeviceConnected(mockContext)

        // Then
        assertTrue("Should return true from UsbDeviceManager", hasSupported)
        verify { mockUsbDeviceManager.hasSupportedDeviceConnected(mockContext) }
    }

    @Test
    fun `isSupportedTopdonDevice should delegate to UsbDeviceManager`() {
        // Given
        val mockDevice = createMockUsbDevice(vendorId = 0x0BDA, productId = 0x3901)
        every { mockUsbDeviceManager.isSupportedTopdonDevice(mockDevice) } returns true

        // When
        val isSupported = usbController.isSupportedTopdonDevice(mockDevice)

        // Then
        assertTrue("Should return true from UsbDeviceManager", isSupported)
        verify { mockUsbDeviceManager.isSupportedTopdonDevice(mockDevice) }
    }

    @Test
    fun `getDeviceInfoString should delegate to UsbDeviceManager`() {
        // Given
        val mockDevice = createMockUsbDevice(vendorId = 0x0BDA, productId = 0x3901)
        val expectedInfo = "Device info string"
        every { mockUsbDeviceManager.getDeviceInfoString(mockDevice) } returns expectedInfo

        // When
        val info = usbController.getDeviceInfoString(mockDevice)

        // Then
        assertEquals("Should return info from UsbDeviceManager", expectedInfo, info)
        verify { mockUsbDeviceManager.getDeviceInfoString(mockDevice) }
    }

    @Test
    fun `initializeUsbMonitoring should scan and handle connected devices`() {
        // Given
        val supportedDevice = createMockUsbDevice(vendorId = 0x0BDA, productId = 0x3901)
        val unsupportedDevice = createMockUsbDevice(vendorId = 0x1234, productId = 0x5678)
        val allDevices = listOf(supportedDevice, unsupportedDevice)
        val supportedDevices = listOf(supportedDevice)

        every { mockUsbDeviceManager.getConnectedUsbDevices(mockContext) } returns allDevices
        every { mockUsbDeviceManager.getConnectedSupportedDevices(mockContext) } returns supportedDevices
        every { mockCallback.areAllPermissionsGranted() } returns true

        // When
        usbController.initializeUsbMonitoring(mockContext)

        // Then
        verify { mockCallback.onSupportedDeviceAttached(supportedDevice) }
        verify { mockCallback.initializeRecordingSystem() }
    }

    @Test
    fun `initializeUsbMonitoring should handle no devices connected`() {
        // Given
        every { mockUsbDeviceManager.getConnectedUsbDevices(mockContext) } returns emptyList()
        every { mockUsbDeviceManager.getConnectedSupportedDevices(mockContext) } returns emptyList()

        // When
        usbController.initializeUsbMonitoring(mockContext)

        // Then
        verify(exactly = 0) { mockCallback.onSupportedDeviceAttached(any()) }
        verify(exactly = 0) { mockCallback.initializeRecordingSystem() }
    }

    @Test
    fun `getUsbStatusSummary should provide comprehensive status information`() {
        // Given
        val supportedDevice = createMockUsbDevice(
            vendorId = 0x0BDA, 
            productId = 0x3901, 
            deviceName = "/dev/bus/usb/001/002"
        )
        val unsupportedDevice = createMockUsbDevice(
            vendorId = 0x1234, 
            productId = 0x5678, 
            deviceName = "/dev/bus/usb/001/003"
        )
        val allDevices = listOf(supportedDevice, unsupportedDevice)
        val supportedDevices = listOf(supportedDevice)

        every { mockUsbDeviceManager.getConnectedUsbDevices(mockContext) } returns allDevices
        every { mockUsbDeviceManager.getConnectedSupportedDevices(mockContext) } returns supportedDevices

        // When
        val summary = usbController.getUsbStatusSummary(mockContext)

        // Then
        assertTrue("Should contain total device count", summary.contains("Total connected devices: 2"))
        assertTrue("Should contain supported device count", summary.contains("Supported TOPDON devices: 1"))
        assertTrue("Should contain device details", summary.contains("/dev/bus/usb/001/002"))
        assertTrue("Should contain vendor/product IDs", summary.contains("VID: 0x0BDA"))
        assertTrue("Should contain vendor/product IDs", summary.contains("PID: 0x3901"))
    }

    @Test
    fun `error handling should be robust`() {
        // Given - UsbDeviceManager throws exception
        every { mockUsbDeviceManager.getConnectedUsbDevices(mockContext) } throws RuntimeException("USB error")

        // When
        val devices = usbController.getConnectedUsbDevices(mockContext)

        // Then
        // Should propagate the exception or handle gracefully
        // In this case, it will propagate since UsbController doesn't add error handling
        assertThrows("Should propagate exception", RuntimeException::class.java) {
            usbController.getConnectedUsbDevices(mockContext)
        }
    }

    @Test
    fun `operations without callback should not crash`() {
        // Given - no callback set
        val controllerWithoutCallback = UsbController(mockUsbDeviceManager)
        val mockDevice = createMockUsbDevice(vendorId = 0x0BDA, productId = 0x3901)
        val intent = createUsbDeviceIntent(UsbManager.ACTION_USB_DEVICE_ATTACHED, mockDevice)

        // When/Then - should not crash
        controllerWithoutCallback.handleUsbDeviceIntent(mockContext, intent)
    }

    @Test
    fun `concurrent device events should be handled correctly`() {
        // Given - multiple device events
        val device1 = createMockUsbDevice(vendorId = 0x0BDA, productId = 0x3901, deviceName = "device1")
        val device2 = createMockUsbDevice(vendorId = 0x0BDA, productId = 0x5840, deviceName = "device2")
        val device3 = createMockUsbDevice(vendorId = 0x1234, productId = 0x5678, deviceName = "device3")

        val intent1 = createUsbDeviceIntent(UsbManager.ACTION_USB_DEVICE_ATTACHED, device1)
        val intent2 = createUsbDeviceIntent(UsbManager.ACTION_USB_DEVICE_ATTACHED, device2)
        val intent3 = createUsbDeviceIntent(UsbManager.ACTION_USB_DEVICE_ATTACHED, device3)

        every { mockUsbDeviceManager.isSupportedTopdonDevice(device1) } returns true
        every { mockUsbDeviceManager.isSupportedTopdonDevice(device2) } returns true
        every { mockUsbDeviceManager.isSupportedTopdonDevice(device3) } returns false
        every { mockCallback.areAllPermissionsGranted() } returns true

        // When - handle multiple events
        usbController.handleUsbDeviceIntent(mockContext, intent1)
        usbController.handleUsbDeviceIntent(mockContext, intent2)
        usbController.handleUsbDeviceIntent(mockContext, intent3)

        // Then
        verify { mockCallback.onSupportedDeviceAttached(device1) }
        verify { mockCallback.onSupportedDeviceAttached(device2) }
        verify { mockCallback.onUnsupportedDeviceAttached(device3) }
        verify(exactly = 2) { mockCallback.initializeRecordingSystem() }
    }

    @Test
    fun `device attachment and detachment sequence should work correctly`() {
        // Given
        val mockDevice = createMockUsbDevice(vendorId = 0x0BDA, productId = 0x3901)
        val attachIntent = createUsbDeviceIntent(UsbManager.ACTION_USB_DEVICE_ATTACHED, mockDevice)
        val detachIntent = createUsbDeviceIntent(UsbManager.ACTION_USB_DEVICE_DETACHED, mockDevice)

        every { mockUsbDeviceManager.isSupportedTopdonDevice(mockDevice) } returns true
        every { mockCallback.areAllPermissionsGranted() } returns true

        // When - attach then detach
        usbController.handleUsbDeviceIntent(mockContext, attachIntent)
        usbController.handleUsbDeviceIntent(mockContext, detachIntent)

        // Then
        verify { mockCallback.onSupportedDeviceAttached(mockDevice) }
        verify { mockCallback.onDeviceDetached(mockDevice) }
        verify { mockCallback.initializeRecordingSystem() }
        verify { mockCallback.updateStatusText(match { it.contains("connected") }) }
        verify { mockCallback.updateStatusText(match { it.contains("disconnected") }) }
    }

    // Helper methods for creating mock objects

    private fun createMockUsbDevice(
        vendorId: Int,
        productId: Int,
        deviceName: String = "/dev/bus/usb/001/002",
        deviceClass: Int = 14
    ): UsbDevice {
        return mockk<UsbDevice>(relaxed = true).apply {
            every { this@apply.vendorId } returns vendorId
            every { this@apply.productId } returns productId
            every { this@apply.deviceName } returns deviceName
            every { this@apply.deviceClass } returns deviceClass
        }
    }

    private fun createUsbDeviceIntent(action: String, device: UsbDevice?): Intent {
        return mockk<Intent>(relaxed = true).apply {
            every { this@apply.action } returns action
            every { getParcelableExtra<UsbDevice>(UsbManager.EXTRA_DEVICE) } returns device
        }
    }
}