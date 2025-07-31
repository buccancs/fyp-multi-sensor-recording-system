package com.multisensor.recording.managers

import android.content.Context
import android.content.Intent
import android.hardware.usb.UsbDevice
import android.hardware.usb.UsbManager
import io.mockk.*
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

/**
 * Comprehensive unit tests for UsbDeviceManager.
 * Tests Topdon TC001/Plus device detection, USB intent handling,
 * and device support validation to ensure bulletproof integration.
 */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [33])
class UsbDeviceManagerUnitTest {

    private lateinit var usbDeviceManager: UsbDeviceManager
    private lateinit var mockCallback: UsbDeviceManager.UsbDeviceCallback
    private lateinit var mockContext: Context
    private lateinit var mockUsbManager: UsbManager

    @Before
    fun setup() {
        usbDeviceManager = UsbDeviceManager()
        mockCallback = mockk(relaxed = true)
        mockContext = mockk(relaxed = true)
        mockUsbManager = mockk(relaxed = true)

        every { mockContext.getSystemService(Context.USB_SERVICE) } returns mockUsbManager
    }

    @After
    fun teardown() {
        clearAllMocks()
    }

    @Test
    fun `isSupportedTopdonDevice should return true for TC001 device`() {
        // Given - TC001 device with correct VID/PID
        val mockDevice = createMockUsbDevice(vendorId = 0x0BDA, productId = 0x3901)

        // When
        val isSupported = usbDeviceManager.isSupportedTopdonDevice(mockDevice)

        // Then
        assertTrue("TC001 device (PID 0x3901) should be supported", isSupported)
    }

    @Test
    fun `isSupportedTopdonDevice should return true for TC001 Plus device`() {
        // Given - TC001 Plus device
        val mockDevice = createMockUsbDevice(vendorId = 0x0BDA, productId = 0x5840)

        // When
        val isSupported = usbDeviceManager.isSupportedTopdonDevice(mockDevice)

        // Then
        assertTrue("TC001 Plus device (PID 0x5840) should be supported", isSupported)
    }

    @Test
    fun `isSupportedTopdonDevice should return true for all TC001 variants`() {
        // Given - all supported TC001 variant PIDs
        val supportedPids = listOf(0x3901, 0x5840, 0x5830, 0x5838)

        supportedPids.forEach { pid ->
            // Given
            val mockDevice = createMockUsbDevice(vendorId = 0x0BDA, productId = pid)

            // When
            val isSupported = usbDeviceManager.isSupportedTopdonDevice(mockDevice)

            // Then
            assertTrue("TC001 variant with PID 0x${pid.toString(16)} should be supported", isSupported)
        }
    }

    @Test
    fun `isSupportedTopdonDevice should return false for wrong vendor ID`() {
        // Given - correct product ID but wrong vendor ID
        val mockDevice = createMockUsbDevice(vendorId = 0x1234, productId = 0x3901)

        // When
        val isSupported = usbDeviceManager.isSupportedTopdonDevice(mockDevice)

        // Then
        assertFalse("Device with wrong vendor ID should not be supported", isSupported)
    }

    @Test
    fun `isSupportedTopdonDevice should return false for wrong product ID`() {
        // Given - correct vendor ID but unsupported product ID
        val mockDevice = createMockUsbDevice(vendorId = 0x0BDA, productId = 0x1234)

        // When
        val isSupported = usbDeviceManager.isSupportedTopdonDevice(mockDevice)

        // Then
        assertFalse("Device with unsupported product ID should not be supported", isSupported)
    }

    @Test
    fun `handleUsbDeviceIntent should handle device attached`() {
        // Given
        val mockDevice = createMockUsbDevice(vendorId = 0x0BDA, productId = 0x3901)
        val intent = createUsbDeviceIntent(UsbManager.ACTION_USB_DEVICE_ATTACHED, mockDevice)

        // When
        usbDeviceManager.handleUsbDeviceIntent(intent, mockCallback)

        // Then
        verify { mockCallback.onSupportedDeviceAttached(mockDevice) }
        verify(exactly = 0) { mockCallback.onUnsupportedDeviceAttached(any()) }
        verify(exactly = 0) { mockCallback.onError(any()) }
    }

    @Test
    fun `handleUsbDeviceIntent should handle unsupported device attached`() {
        // Given
        val mockDevice = createMockUsbDevice(vendorId = 0x1234, productId = 0x5678)
        val intent = createUsbDeviceIntent(UsbManager.ACTION_USB_DEVICE_ATTACHED, mockDevice)

        // When
        usbDeviceManager.handleUsbDeviceIntent(intent, mockCallback)

        // Then
        verify { mockCallback.onUnsupportedDeviceAttached(mockDevice) }
        verify(exactly = 0) { mockCallback.onSupportedDeviceAttached(any()) }
        verify(exactly = 0) { mockCallback.onError(any()) }
    }

    @Test
    fun `handleUsbDeviceIntent should handle device detached`() {
        // Given
        val mockDevice = createMockUsbDevice(vendorId = 0x0BDA, productId = 0x3901)
        val intent = createUsbDeviceIntent(UsbManager.ACTION_USB_DEVICE_DETACHED, mockDevice)

        // When
        usbDeviceManager.handleUsbDeviceIntent(intent, mockCallback)

        // Then
        verify { mockCallback.onDeviceDetached(mockDevice) }
        verify(exactly = 0) { mockCallback.onSupportedDeviceAttached(any()) }
        verify(exactly = 0) { mockCallback.onUnsupportedDeviceAttached(any()) }
    }

    @Test
    fun `handleUsbDeviceIntent should handle missing device in intent`() {
        // Given - intent without device
        val intent = createUsbDeviceIntent(UsbManager.ACTION_USB_DEVICE_ATTACHED, null)

        // When
        usbDeviceManager.handleUsbDeviceIntent(intent, mockCallback)

        // Then
        verify { mockCallback.onError(match { it.contains("no device information available") }) }
    }

    @Test
    fun `handleUsbDeviceIntent should handle unknown action`() {
        // Given
        val mockDevice = createMockUsbDevice(vendorId = 0x0BDA, productId = 0x3901)
        val intent = createUsbDeviceIntent("android.hardware.usb.action.UNKNOWN", mockDevice)

        // When
        usbDeviceManager.handleUsbDeviceIntent(intent, mockCallback)

        // Then
        // Should not trigger any callbacks for unknown actions
        verify(exactly = 0) { mockCallback.onSupportedDeviceAttached(any()) }
        verify(exactly = 0) { mockCallback.onUnsupportedDeviceAttached(any()) }
        verify(exactly = 0) { mockCallback.onDeviceDetached(any()) }
        verify(exactly = 0) { mockCallback.onError(any()) }
    }

    @Test
    fun `getConnectedUsbDevices should return device list`() {
        // Given
        val mockDevice1 = createMockUsbDevice(vendorId = 0x0BDA, productId = 0x3901, deviceName = "/dev/bus/usb/001/002")
        val mockDevice2 = createMockUsbDevice(vendorId = 0x1234, productId = 0x5678, deviceName = "/dev/bus/usb/001/003")
        val deviceMap = mapOf(
            "device1" to mockDevice1,
            "device2" to mockDevice2
        )
        every { mockUsbManager.deviceList } returns deviceMap

        // When
        val devices = usbDeviceManager.getConnectedUsbDevices(mockContext)

        // Then
        assertEquals("Should return 2 connected devices", 2, devices.size)
        assertTrue("Should contain first device", devices.contains(mockDevice1))
        assertTrue("Should contain second device", devices.contains(mockDevice2))
    }

    @Test
    fun `getConnectedSupportedDevices should filter supported devices`() {
        // Given
        val supportedDevice = createMockUsbDevice(vendorId = 0x0BDA, productId = 0x3901)
        val unsupportedDevice = createMockUsbDevice(vendorId = 0x1234, productId = 0x5678)
        val deviceMap = mapOf(
            "supported" to supportedDevice,
            "unsupported" to unsupportedDevice
        )
        every { mockUsbManager.deviceList } returns deviceMap

        // When
        val supportedDevices = usbDeviceManager.getConnectedSupportedDevices(mockContext)

        // Then
        assertEquals("Should return 1 supported device", 1, supportedDevices.size)
        assertTrue("Should contain supported device", supportedDevices.contains(supportedDevice))
        assertFalse("Should not contain unsupported device", supportedDevices.contains(unsupportedDevice))
    }

    @Test
    fun `hasSupportedDeviceConnected should return true when supported device present`() {
        // Given
        val supportedDevice = createMockUsbDevice(vendorId = 0x0BDA, productId = 0x3901)
        val deviceMap = mapOf("supported" to supportedDevice)
        every { mockUsbManager.deviceList } returns deviceMap

        // When
        val hasSupported = usbDeviceManager.hasSupportedDeviceConnected(mockContext)

        // Then
        assertTrue("Should return true when supported device is connected", hasSupported)
    }

    @Test
    fun `hasSupportedDeviceConnected should return false when no supported devices`() {
        // Given
        val unsupportedDevice = createMockUsbDevice(vendorId = 0x1234, productId = 0x5678)
        val deviceMap = mapOf("unsupported" to unsupportedDevice)
        every { mockUsbManager.deviceList } returns deviceMap

        // When
        val hasSupported = usbDeviceManager.hasSupportedDeviceConnected(mockContext)

        // Then
        assertFalse("Should return false when no supported devices connected", hasSupported)
    }

    @Test
    fun `hasSupportedDeviceConnected should return false when no devices connected`() {
        // Given
        every { mockUsbManager.deviceList } returns emptyMap()

        // When
        val hasSupported = usbDeviceManager.hasSupportedDeviceConnected(mockContext)

        // Then
        assertFalse("Should return false when no devices connected", hasSupported)
    }

    @Test
    fun `getDeviceInfoString should format device information correctly`() {
        // Given
        val mockDevice = createMockUsbDevice(
            vendorId = 0x0BDA,
            productId = 0x3901,
            deviceName = "/dev/bus/usb/001/002",
            deviceClass = 14
        )

        // When
        val infoString = usbDeviceManager.getDeviceInfoString(mockDevice)

        // Then
        assertTrue("Should contain device name", infoString.contains("/dev/bus/usb/001/002"))
        assertTrue("Should contain vendor ID", infoString.contains("Vendor ID: 0x0BDA"))
        assertTrue("Should contain product ID", infoString.contains("Product ID: 0x3901"))
        assertTrue("Should contain device class", infoString.contains("Device Class: 14"))
    }

    @Test
    fun `error handling should be robust`() {
        // Given - USB manager throws exception
        every { mockContext.getSystemService(Context.USB_SERVICE) } throws RuntimeException("USB service error")

        // When
        val devices = usbDeviceManager.getConnectedUsbDevices(mockContext)

        // Then
        assertTrue("Should return empty list on error", devices.isEmpty())
    }

    @Test
    fun `device detection should handle edge cases`() {
        // Test various edge cases for device detection

        // Case 1: Device with minimum vendor/product IDs
        val minDevice = createMockUsbDevice(vendorId = 0x0000, productId = 0x0000)
        assertFalse("Min VID/PID should not be supported", 
                   usbDeviceManager.isSupportedTopdonDevice(minDevice))

        // Case 2: Device with maximum vendor/product IDs
        val maxDevice = createMockUsbDevice(vendorId = 0xFFFF, productId = 0xFFFF)
        assertFalse("Max VID/PID should not be supported", 
                   usbDeviceManager.isSupportedTopdonDevice(maxDevice))

        // Case 3: Correct vendor, edge case product IDs
        val edgeDevice1 = createMockUsbDevice(vendorId = 0x0BDA, productId = 0x3900) // One less than supported
        val edgeDevice2 = createMockUsbDevice(vendorId = 0x0BDA, productId = 0x3902) // One more than supported
        assertFalse("Edge case PID (0x3900) should not be supported", 
                   usbDeviceManager.isSupportedTopdonDevice(edgeDevice1))
        assertFalse("Edge case PID (0x3902) should not be supported", 
                   usbDeviceManager.isSupportedTopdonDevice(edgeDevice2))
    }

    @Test
    fun `intent handling should be defensive`() {
        // Given - intent that could cause exceptions
        val malformedIntent = mockk<Intent>(relaxed = true)
        every { malformedIntent.action } returns UsbManager.ACTION_USB_DEVICE_ATTACHED
        every { malformedIntent.getParcelableExtra<UsbDevice>(UsbManager.EXTRA_DEVICE) } throws RuntimeException("Intent error")

        // When
        usbDeviceManager.handleUsbDeviceIntent(malformedIntent, mockCallback)

        // Then
        verify { mockCallback.onError(match { it.contains("Failed to handle USB device intent") }) }
    }

    @Test
    fun `multiple supported devices should be handled correctly`() {
        // Given - multiple supported devices
        val device1 = createMockUsbDevice(vendorId = 0x0BDA, productId = 0x3901, deviceName = "device1")
        val device2 = createMockUsbDevice(vendorId = 0x0BDA, productId = 0x5840, deviceName = "device2")
        val device3 = createMockUsbDevice(vendorId = 0x0BDA, productId = 0x5830, deviceName = "device3")
        val unsupportedDevice = createMockUsbDevice(vendorId = 0x1234, productId = 0x5678, deviceName = "unsupported")

        val deviceMap = mapOf(
            "device1" to device1,
            "device2" to device2,
            "device3" to device3,
            "unsupported" to unsupportedDevice
        )
        every { mockUsbManager.deviceList } returns deviceMap

        // When
        val supportedDevices = usbDeviceManager.getConnectedSupportedDevices(mockContext)

        // Then
        assertEquals("Should return 3 supported devices", 3, supportedDevices.size)
        assertTrue("Should contain TC001 device", supportedDevices.contains(device1))
        assertTrue("Should contain TC001 Plus device", supportedDevices.contains(device2))
        assertTrue("Should contain TC001 variant device", supportedDevices.contains(device3))
        assertFalse("Should not contain unsupported device", supportedDevices.contains(unsupportedDevice))
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