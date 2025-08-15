package com.multisensor.recording.camera

import android.content.Context
import android.hardware.usb.UsbManager
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.Mockito.*
import org.robolectric.annotation.Config
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertNotNull
import kotlin.test.assertTrue

/**
 * Unit tests for ThermalCamera focusing on fixed initialization semantics.
 * Tests the fixes from remediation checklist item #6.
 */
@RunWith(AndroidJUnit4::class)
@Config(manifest = Config.NONE)
class ThermalCameraTest {

    private lateinit var mockContext: Context
    private lateinit var mockUsbManager: UsbManager
    private lateinit var thermalCamera: ThermalCamera

    @Before
    fun setUp() {
        mockContext = mock(Context::class.java)
        mockUsbManager = mock(UsbManager::class.java)
        
        `when`(mockContext.getSystemService(Context.USB_SERVICE)).thenReturn(mockUsbManager)
        
        thermalCamera = ThermalCamera(mockContext)
    }

    @Test
    fun testInitialization_Success() {
        // Test successful initialization
        val result = thermalCamera.initialize()
        
        assertTrue("Initialization should succeed", result)
        assertTrue("Camera should be marked as initialized", thermalCamera.isConnected())
        assertTrue("Camera should be ready for operation", thermalCamera.isReady())
        assertEquals("Readiness status should be FULLY_READY or READY_NO_DEVICE", 
            ThermalCamera.ReadinessStatus.READY_NO_DEVICE, thermalCamera.getReadinessStatus())
    }

    @Test
    fun testInitialization_SecurityException() {
        // Mock a security exception during USB manager access
        `when`(mockContext.getSystemService(Context.USB_SERVICE))
            .thenThrow(SecurityException("USB permissions denied"))
        
        val result = thermalCamera.initialize()
        
        // FIXED: Should NOT mark as initialized on security failure
        assertFalse("Initialization should fail on security exception", result)
        assertFalse("Camera should NOT be marked as initialized on security failure", thermalCamera.isConnected())
        assertFalse("Camera should NOT be ready on security failure", thermalCamera.isReady())
        assertEquals("Readiness status should be NOT_INITIALIZED", 
            ThermalCamera.ReadinessStatus.NOT_INITIALIZED, thermalCamera.getReadinessStatus())
        
        val error = thermalCamera.getInitializationError()
        assertNotNull("Should have initialization error", error)
        assertTrue("Error should mention security", error.contains("Security permissions denied"))
    }

    @Test
    fun testInitialization_GeneralException() {
        // Mock a general exception during initialization
        `when`(mockContext.getSystemService(Context.USB_SERVICE))
            .thenThrow(RuntimeException("General initialization failure"))
        
        val result = thermalCamera.initialize()
        
        assertFalse("Initialization should fail on general exception", result)
        assertFalse("Camera should NOT be marked as initialized on failure", thermalCamera.isConnected())
        assertFalse("Camera should NOT be ready on failure", thermalCamera.isReady())
        assertEquals("Readiness status should be NOT_INITIALIZED", 
            ThermalCamera.ReadinessStatus.NOT_INITIALIZED, thermalCamera.getReadinessStatus())
        
        val error = thermalCamera.getInitializationError()
        assertNotNull("Should have initialization error", error)
        assertTrue("Error should mention failure", error.contains("Initialization failed"))
    }

    @Test
    fun testReadinessStatus_ExplicitStates() {
        val statuses = ThermalCamera.ReadinessStatus.values()
        
        // Ensure all expected states exist
        assertTrue("Should have NOT_INITIALIZED state", 
            statuses.contains(ThermalCamera.ReadinessStatus.NOT_INITIALIZED))
        assertTrue("Should have INITIALIZED_WITH_ERRORS state", 
            statuses.contains(ThermalCamera.ReadinessStatus.INITIALIZED_WITH_ERRORS))
        assertTrue("Should have INITIALIZED_NOT_READY state", 
            statuses.contains(ThermalCamera.ReadinessStatus.INITIALIZED_NOT_READY))
        assertTrue("Should have READY_NO_DEVICE state", 
            statuses.contains(ThermalCamera.ReadinessStatus.READY_NO_DEVICE))
        assertTrue("Should have FULLY_READY state", 
            statuses.contains(ThermalCamera.ReadinessStatus.FULLY_READY))
        
        // Verify each state has meaningful descriptions
        statuses.forEach { status ->
            assertTrue("Status ${status.name} should have non-empty description", 
                status.description.isNotBlank())
        }
    }

    @Test
    fun testIsReady_VersusIsConnected() {
        // Before initialization
        assertFalse("Should not be connected before init", thermalCamera.isConnected())
        assertFalse("Should not be ready before init", thermalCamera.isReady())
        
        // After successful initialization
        thermalCamera.initialize()
        
        // isConnected checks basic initialization + device presence
        // isReady is more strict - requires full functionality without errors
        val connected = thermalCamera.isConnected()
        val ready = thermalCamera.isReady()
        
        // If connected, should usually be ready (unless there were errors)
        if (connected) {
            assertTrue("If connected, should typically be ready", ready)
        }
        
        // Ready implies connected
        if (ready) {
            assertTrue("If ready, must be connected", connected)
        }
    }

    @Test
    fun testInitializationError_Tracking() {
        // Initially no error
        assertEquals("Should have no error initially", null, thermalCamera.getInitializationError())
        
        // After successful init, still no error
        thermalCamera.initialize()
        assertEquals("Should have no error after successful init", null, thermalCamera.getInitializationError())
        
        // After failed init with security exception
        `when`(mockContext.getSystemService(Context.USB_SERVICE))
            .thenThrow(SecurityException("Test security error"))
        
        val newCamera = ThermalCamera(mockContext)
        newCamera.initialize()
        
        val error = newCamera.getInitializationError()
        assertNotNull("Should track initialization error", error)
        assertTrue("Error should contain exception message", error.contains("Test security error"))
    }

    @Test
    fun testDeviceName_Default() {
        val deviceName = thermalCamera.getDeviceName()
        assertEquals("Should return default device name", "No Device", deviceName)
    }

    @Test
    fun testPreviewAndRecording_InitialState() {
        assertFalse("Preview should not be active initially", thermalCamera.isPreviewRunning())
        assertFalse("Recording should not be active initially", thermalCamera.isRecordingActive())
    }

    @Test
    fun testReadinessFlow_Comprehensive() {
        // Initial state
        assertEquals(ThermalCamera.ReadinessStatus.NOT_INITIALIZED, thermalCamera.getReadinessStatus())
        
        // After successful initialization
        thermalCamera.initialize()
        val status = thermalCamera.getReadinessStatus()
        assertTrue("After init, should be ready or ready with no device", 
            status == ThermalCamera.ReadinessStatus.FULLY_READY || 
            status == ThermalCamera.ReadinessStatus.READY_NO_DEVICE)
        
        // Create camera with security failure
        `when`(mockContext.getSystemService(Context.USB_SERVICE))
            .thenThrow(SecurityException("Security test"))
        
        val failedCamera = ThermalCamera(mockContext)
        failedCamera.initialize()
        
        assertEquals("Failed camera should be NOT_INITIALIZED", 
            ThermalCamera.ReadinessStatus.NOT_INITIALIZED, failedCamera.getReadinessStatus())
    }
}