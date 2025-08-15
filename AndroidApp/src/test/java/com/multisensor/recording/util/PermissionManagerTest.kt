package com.multisensor.recording.util

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.os.Build
import androidx.core.content.ContextCompat
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.Mockito.*
import org.robolectric.annotation.Config
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue

/**
 * Unit tests for PermissionManager focusing on API-level aware permission handling.
 * Tests the fixes from remediation checklist item #2 and #3.
 */
@RunWith(AndroidJUnit4::class)
@Config(sdk = [Build.VERSION_CODES.R, Build.VERSION_CODES.S, Build.VERSION_CODES.TIRAMISU])
class PermissionManagerTest {

    private lateinit var mockContext: Context
    private lateinit var permissionManager: PermissionManager

    @Before
    fun setUp() {
        mockContext = mock(Context::class.java)
        permissionManager = PermissionManager(mockContext)
    }

    @Test
    @Config(sdk = [Build.VERSION_CODES.Q]) // API 29 - Legacy
    fun testGetRequiredPermissions_Legacy() {
        val permissions = PermissionManager.getRequiredPermissions()
        
        // Should include legacy storage permissions
        assertTrue(permissions.contains(Manifest.permission.WRITE_EXTERNAL_STORAGE))
        assertTrue(permissions.contains(Manifest.permission.READ_EXTERNAL_STORAGE))
        
        // Should include legacy Bluetooth permissions
        assertTrue(permissions.contains(Manifest.permission.BLUETOOTH))
        assertTrue(permissions.contains(Manifest.permission.BLUETOOTH_ADMIN))
        
        // Should include both location permissions for legacy Bluetooth
        assertTrue(permissions.contains(Manifest.permission.ACCESS_COARSE_LOCATION))
        assertTrue(permissions.contains(Manifest.permission.ACCESS_FINE_LOCATION))
        
        // Should NOT include new permissions
        assertFalse(permissions.contains(Manifest.permission.BLUETOOTH_CONNECT))
        assertFalse(permissions.contains(Manifest.permission.BLUETOOTH_SCAN))
    }

    @Test
    @Config(sdk = [Build.VERSION_CODES.R]) // API 30 - Scoped Storage
    fun testGetRequiredPermissions_ScopedStorage() {
        val permissions = PermissionManager.getRequiredPermissions()
        
        // Should NOT include deprecated storage permissions for API 30+
        assertFalse(permissions.contains(Manifest.permission.WRITE_EXTERNAL_STORAGE))
        assertFalse(permissions.contains(Manifest.permission.READ_EXTERNAL_STORAGE))
        
        // Still using legacy Bluetooth for API 30
        assertTrue(permissions.contains(Manifest.permission.BLUETOOTH))
        assertTrue(permissions.contains(Manifest.permission.BLUETOOTH_ADMIN))
        
        // Core permissions always present
        assertTrue(permissions.contains(Manifest.permission.CAMERA))
        assertTrue(permissions.contains(Manifest.permission.RECORD_AUDIO))
    }

    @Test
    @Config(sdk = [Build.VERSION_CODES.S]) // API 31 - New Bluetooth permissions
    fun testGetRequiredPermissions_NewBluetooth() {
        val permissions = PermissionManager.getRequiredPermissions()
        
        // Should NOT include deprecated storage permissions
        assertFalse(permissions.contains(Manifest.permission.WRITE_EXTERNAL_STORAGE))
        assertFalse(permissions.contains(Manifest.permission.READ_EXTERNAL_STORAGE))
        
        // Should use new Bluetooth permissions for API 31+
        assertTrue(permissions.contains(Manifest.permission.BLUETOOTH_CONNECT))
        assertTrue(permissions.contains(Manifest.permission.BLUETOOTH_SCAN))
        
        // Should NOT include legacy Bluetooth permissions
        assertFalse(permissions.contains(Manifest.permission.BLUETOOTH))
        assertFalse(permissions.contains(Manifest.permission.BLUETOOTH_ADMIN))
        
        // Should only require coarse location for API 31+
        assertTrue(permissions.contains(Manifest.permission.ACCESS_COARSE_LOCATION))
        assertFalse(permissions.contains(Manifest.permission.ACCESS_FINE_LOCATION))
    }

    @Test
    @Config(sdk = [Build.VERSION_CODES.TIRAMISU]) // API 33
    fun testGetRequiredPermissions_Latest() {
        val permissions = PermissionManager.getRequiredPermissions()
        
        // Verify minimal permission set for latest API
        val expectedPermissions = setOf(
            Manifest.permission.CAMERA,
            Manifest.permission.RECORD_AUDIO,
            Manifest.permission.BLUETOOTH_CONNECT,
            Manifest.permission.BLUETOOTH_SCAN,
            Manifest.permission.ACCESS_COARSE_LOCATION
        )
        
        assertEquals(expectedPermissions.size, permissions.size)
        expectedPermissions.forEach { permission ->
            assertTrue("Expected permission $permission", permissions.contains(permission))
        }
    }

    @Test
    fun testHasAllPermissions_AllGranted() {
        // Mock all permissions as granted
        `when`(ContextCompat.checkSelfPermission(any(Context::class.java), anyString()))
            .thenReturn(PackageManager.PERMISSION_GRANTED)
        
        assertTrue(permissionManager.hasAllPermissions())
    }

    @Test
    fun testHasAllPermissions_SomeGranted() {
        // Mock camera granted, others denied
        `when`(ContextCompat.checkSelfPermission(mockContext, Manifest.permission.CAMERA))
            .thenReturn(PackageManager.PERMISSION_GRANTED)
        `when`(ContextCompat.checkSelfPermission(mockContext, any()))
            .thenReturn(PackageManager.PERMISSION_DENIED)
        
        assertFalse(permissionManager.hasAllPermissions())
    }

    @Test
    fun testPermissionCount_ReducedForNewerAPIs() {
        val legacyPermissions = PermissionManager.REQUIRED_PERMISSIONS
        val modernPermissions = PermissionManager.getRequiredPermissions()
        
        // Modern API should have fewer permissions due to scoped storage and refined Bluetooth permissions
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            assertTrue("Modern permissions should be fewer than legacy", 
                modernPermissions.size < legacyPermissions.size)
        }
    }

    @Test
    fun testCorePermissions_AlwaysRequired() {
        val permissions = PermissionManager.getRequiredPermissions()
        
        // These permissions should always be required regardless of API level
        assertTrue(permissions.contains(Manifest.permission.CAMERA))
        assertTrue(permissions.contains(Manifest.permission.RECORD_AUDIO))
        assertTrue(permissions.contains(Manifest.permission.ACCESS_COARSE_LOCATION))
    }

    @Test
    fun testMinimalPermissionSet_NoRedundancy() {
        val permissions = PermissionManager.getRequiredPermissions()
        val permissionSet = permissions.toSet()
        
        // Ensure no duplicate permissions
        assertEquals(permissions.size, permissionSet.size)
        
        // Ensure mutually exclusive permissions don't coexist
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            // New Bluetooth permissions should not coexist with old ones
            assertFalse(permissions.contains(Manifest.permission.BLUETOOTH) && 
                       permissions.contains(Manifest.permission.BLUETOOTH_CONNECT))
        }
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            // Storage permissions should not be requested for scoped storage
            assertFalse(permissions.contains(Manifest.permission.WRITE_EXTERNAL_STORAGE))
        }
    }
}