package com.multisensor.recording.camera

import android.content.Context
import android.util.Log
import org.junit.Before
import org.junit.Test
import org.junit.Assert.*
import org.mockito.Mock
import org.mockito.MockitoAnnotations

/**
 * Test for ThermalCamera security exception handling and state tracking fixes
 */
class ThermalCameraStateTest {

    @Mock
    private lateinit var mockContext: Context

    private lateinit var thermalCamera: ThermalCamera

    @Before
    fun setup() {
        MockitoAnnotations.openMocks(this)
        thermalCamera = ThermalCamera(mockContext)
    }

    @Test
    fun `test initial state is not ready`() {
        // Initially, camera should not be ready
        assertFalse("Camera should not be connected initially", thermalCamera.isConnected())
        assertFalse("Camera should not have permissions initially", thermalCamera.hasRequiredPermissions())
        assertFalse("Camera should not be fully ready initially", thermalCamera.isFullyReady())
        assertFalse("Preview should not be running initially", thermalCamera.isPreviewRunning())
        assertFalse("Recording should not be active initially", thermalCamera.isRecordingActive())
    }

    @Test
    fun `test camera status provides detailed information`() {
        val status = thermalCamera.getCameraStatus()
        
        assertTrue("Status should mention initialized state", status.contains("Initialized: false"))
        assertTrue("Status should mention permissions state", status.contains("Permissions: false"))
        assertTrue("Status should mention ready state", status.contains("Ready: false"))
        assertTrue("Status should mention no device", status.contains("Device: No Device"))
        assertTrue("Status should mention preview state", status.contains("Preview: false"))
        assertTrue("Status should mention recording state", status.contains("Recording: false"))
    }

    @Test
    fun `test start preview fails when not ready`() {
        // Should fail when camera is not initialized, has no permissions, or is not ready
        assertFalse("Preview should fail when camera not initialized", thermalCamera.startPreview())
        assertFalse("Preview should fail when camera not ready", thermalCamera.startPreview())
    }

    @Test
    fun `test start recording fails when preview not active`() {
        // Should fail when preview is not active
        assertFalse("Recording should fail when preview not active", thermalCamera.startRecording())
    }

    @Test
    fun `test device name returns default when no device`() {
        assertEquals("Should return 'No Device' when no device connected", "No Device", thermalCamera.getDeviceName())
    }

    @Test
    fun `test release cleans up all states`() {
        thermalCamera.release()
        
        // After release, all states should be reset
        assertFalse("Camera should not be connected after release", thermalCamera.isConnected())
        assertFalse("Camera should not have permissions after release", thermalCamera.hasRequiredPermissions())
        assertFalse("Camera should not be ready after release", thermalCamera.isFullyReady())
        assertFalse("Preview should not be running after release", thermalCamera.isPreviewRunning())
        assertFalse("Recording should not be active after release", thermalCamera.isRecordingActive())
        
        val status = thermalCamera.getCameraStatus()
        assertTrue("All states should be false in status after release", 
                  status.contains("Initialized: false") &&
                  status.contains("Permissions: false") &&
                  status.contains("Ready: false") &&
                  status.contains("Preview: false") &&
                  status.contains("Recording: false"))
    }
}