package com.multisensor.recording.util

import android.content.Context
import android.os.Build
import org.junit.Before
import org.junit.Test
import org.junit.Assert.*
import org.mockito.Mock
import org.mockito.MockitoAnnotations

/**
 * Test for PermissionManager API-level gating and lifecycle safety fixes
 */
class PermissionManagerTest {

    @Mock
    private lateinit var mockContext: Context

    private lateinit var permissionManager: PermissionManager

    @Before
    fun setup() {
        MockitoAnnotations.openMocks(this)
        permissionManager = PermissionManager(mockContext)
    }

    @Test
    fun `test required permissions include base permissions`() {
        val permissions = permissionManager.getRequiredPermissions()
        
        // Base permissions should always be included
        assertTrue("Should include CAMERA permission", 
                  permissions.contains(android.Manifest.permission.CAMERA))
        assertTrue("Should include RECORD_AUDIO permission", 
                  permissions.contains(android.Manifest.permission.RECORD_AUDIO))
        assertTrue("Should include WRITE_EXTERNAL_STORAGE permission", 
                  permissions.contains(android.Manifest.permission.WRITE_EXTERNAL_STORAGE))
        assertTrue("Should include READ_EXTERNAL_STORAGE permission", 
                  permissions.contains(android.Manifest.permission.READ_EXTERNAL_STORAGE))
    }

    @Test
    fun `test bluetooth permissions are API level gated`() {
        val permissions = permissionManager.getRequiredPermissions()
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            // API 31+ should use new Bluetooth permissions
            assertTrue("Should include BLUETOOTH_CONNECT for API 31+", 
                      permissions.contains(android.Manifest.permission.BLUETOOTH_CONNECT))
            assertTrue("Should include BLUETOOTH_SCAN for API 31+", 
                      permissions.contains(android.Manifest.permission.BLUETOOTH_SCAN))
            assertTrue("Should include ACCESS_FINE_LOCATION for API 31+", 
                      permissions.contains(android.Manifest.permission.ACCESS_FINE_LOCATION))
        } else {
            // Legacy API should use old Bluetooth permissions
            assertTrue("Should include BLUETOOTH for legacy API", 
                      permissions.contains(android.Manifest.permission.BLUETOOTH))
            assertTrue("Should include BLUETOOTH_ADMIN for legacy API", 
                      permissions.contains(android.Manifest.permission.BLUETOOTH_ADMIN))
            assertTrue("Should include ACCESS_COARSE_LOCATION for legacy API", 
                      permissions.contains(android.Manifest.permission.ACCESS_COARSE_LOCATION))
            assertTrue("Should include ACCESS_FINE_LOCATION for legacy API", 
                      permissions.contains(android.Manifest.permission.ACCESS_FINE_LOCATION))
        }
    }

    @Test
    fun `test permission guidance message is helpful`() {
        val guidance = permissionManager.getPermissionGuidanceMessage()
        
        assertTrue("Guidance should mention required permissions", 
                  guidance.contains("required for full functionality"))
        assertTrue("Guidance should provide friendly names", 
                  guidance.contains("Camera access") || guidance.contains("Microphone access"))
        assertTrue("Guidance should suggest action", 
                  guidance.contains("grant these permissions") || guidance.contains("Settings"))
    }

    @Test
    fun `test initialization prevents illegal state`() {
        // Should throw IllegalStateException if not initialized
        try {
            permissionManager.requestAllPermissions { }
            fail("Should throw IllegalStateException when not initialized")
        } catch (e: IllegalStateException) {
            assertTrue("Exception message should mention initialization", 
                      e.message?.contains("not initialized") == true)
        }
    }
}