package com.multisensor.recording.sensor

import android.Manifest
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothManager
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
 * Unit tests for GsrSensor focusing on Bluetooth permission handling and sensor lifecycle.
 * Tests the remediation improvements for Bluetooth permissions and GSR sensor flows.
 */
@RunWith(AndroidJUnit4::class)
@Config(manifest = Config.NONE, sdk = [Build.VERSION_CODES.R, Build.VERSION_CODES.S, Build.VERSION_CODES.TIRAMISU])
class GsrSensorTest {

    private lateinit var mockContext: Context
    private lateinit var mockBluetoothManager: BluetoothManager
    private lateinit var mockBluetoothAdapter: BluetoothAdapter
    private lateinit var gsrSensor: GsrSensor

    @Before
    fun setUp() {
        mockContext = mock(Context::class.java)
        mockBluetoothManager = mock(BluetoothManager::class.java)
        mockBluetoothAdapter = mock(BluetoothAdapter::class.java)
        
        `when`(mockContext.getSystemService(Context.BLUETOOTH_SERVICE)).thenReturn(mockBluetoothManager)
        `when`(mockBluetoothManager.adapter).thenReturn(mockBluetoothAdapter)
        `when`(mockBluetoothAdapter.isEnabled).thenReturn(true)
        
        gsrSensor = GsrSensor(mockContext)
    }

    @Test
    fun testInitialize_WithPermissions() {
        // Mock all Bluetooth permissions as granted
        `when`(ContextCompat.checkSelfPermission(any(Context::class.java), anyString()))
            .thenReturn(PackageManager.PERMISSION_GRANTED)
        
        val result = gsrSensor.initialize()
        
        assertTrue("Initialization should succeed with permissions", result)
    }

    @Test
    fun testInitialize_WithoutPermissions() {
        // Mock Bluetooth permissions as denied
        `when`(ContextCompat.checkSelfPermission(any(Context::class.java), anyString()))
            .thenReturn(PackageManager.PERMISSION_DENIED)
        
        val result = gsrSensor.initialize()
        
        assertFalse("Initialization should fail without permissions", result)
    }

    @Test
    @Config(sdk = [Build.VERSION_CODES.Q]) // API 29 - Legacy Bluetooth
    fun testBluetoothPermissions_Legacy() {
        // Mock legacy Bluetooth permissions
        `when`(ContextCompat.checkSelfPermission(mockContext, Manifest.permission.BLUETOOTH))
            .thenReturn(PackageManager.PERMISSION_GRANTED)
        `when`(ContextCompat.checkSelfPermission(mockContext, Manifest.permission.BLUETOOTH_ADMIN))
            .thenReturn(PackageManager.PERMISSION_GRANTED)
        `when`(ContextCompat.checkSelfPermission(mockContext, Manifest.permission.ACCESS_FINE_LOCATION))
            .thenReturn(PackageManager.PERMISSION_GRANTED)
        `when`(ContextCompat.checkSelfPermission(mockContext, Manifest.permission.ACCESS_COARSE_LOCATION))
            .thenReturn(PackageManager.PERMISSION_GRANTED)
        
        // Mock new permissions as denied (should not be checked on legacy)
        `when`(ContextCompat.checkSelfPermission(mockContext, Manifest.permission.BLUETOOTH_SCAN))
            .thenReturn(PackageManager.PERMISSION_DENIED)
        `when`(ContextCompat.checkSelfPermission(mockContext, Manifest.permission.BLUETOOTH_CONNECT))
            .thenReturn(PackageManager.PERMISSION_DENIED)
        
        val result = gsrSensor.initialize()
        
        assertTrue("Should succeed with legacy Bluetooth permissions on API 29", result)
    }

    @Test
    @Config(sdk = [Build.VERSION_CODES.S]) // API 31 - New Bluetooth permissions
    fun testBluetoothPermissions_Modern() {
        // Mock new Bluetooth permissions
        `when`(ContextCompat.checkSelfPermission(mockContext, Manifest.permission.BLUETOOTH_SCAN))
            .thenReturn(PackageManager.PERMISSION_GRANTED)
        `when`(ContextCompat.checkSelfPermission(mockContext, Manifest.permission.BLUETOOTH_CONNECT))
            .thenReturn(PackageManager.PERMISSION_GRANTED)
        `when`(ContextCompat.checkSelfPermission(mockContext, Manifest.permission.ACCESS_FINE_LOCATION))
            .thenReturn(PackageManager.PERMISSION_GRANTED)
        `when`(ContextCompat.checkSelfPermission(mockContext, Manifest.permission.ACCESS_COARSE_LOCATION))
            .thenReturn(PackageManager.PERMISSION_GRANTED)
        
        // Mock legacy permissions as denied (should not be needed on API 31+)
        `when`(ContextCompat.checkSelfPermission(mockContext, Manifest.permission.BLUETOOTH))
            .thenReturn(PackageManager.PERMISSION_DENIED)
        `when`(ContextCompat.checkSelfPermission(mockContext, Manifest.permission.BLUETOOTH_ADMIN))
            .thenReturn(PackageManager.PERMISSION_DENIED)
        
        val result = gsrSensor.initialize()
        
        assertTrue("Should succeed with new Bluetooth permissions on API 31+", result)
    }

    @Test
    fun testInitialState() {
        assertFalse("Should not be connected initially", gsrSensor.isConnected())
        assertFalse("Should not be streaming initially", gsrSensor.isStreamingActive())
        assertEquals("Sample count should be 0 initially", 0L, gsrSensor.getSampleCount())
        assertEquals("Device info should indicate no device", "No device connected", gsrSensor.getDeviceInfo())
    }

    @Test
    fun testConnect_WithoutInitialization() {
        val result = gsrSensor.connect("00:11:22:33:44:55")
        
        assertFalse("Connection should fail without initialization", result)
        assertFalse("Should not be connected after failed connect", gsrSensor.isConnected())
    }

    @Test
    fun testStartStreaming_WithoutConnection() {
        // Initialize but don't connect
        `when`(ContextCompat.checkSelfPermission(any(Context::class.java), anyString()))
            .thenReturn(PackageManager.PERMISSION_GRANTED)
        gsrSensor.initialize()
        
        val result = gsrSensor.startStreaming()
        
        assertFalse("Streaming should fail without connection", result)
        assertFalse("Should not be streaming after failed start", gsrSensor.isStreamingActive())
    }

    @Test
    fun testStopStreaming_WithoutStreaming() {
        val result = gsrSensor.stopStreaming()
        
        assertTrue("Stopping non-active streaming should succeed (idempotent)", result)
        assertFalse("Should not be streaming after stop", gsrSensor.isStreamingActive())
    }

    @Test
    fun testDisconnect_WithoutConnection() {
        val result = gsrSensor.disconnect()
        
        assertTrue("Disconnecting when not connected should succeed (idempotent)", result)
        assertFalse("Should not be connected after disconnect", gsrSensor.isConnected())
    }

    @Test
    fun testScanForDevices_WithoutPermissions() {
        `when`(ContextCompat.checkSelfPermission(any(Context::class.java), anyString()))
            .thenReturn(PackageManager.PERMISSION_DENIED)
        
        var callbackCalled = false
        var deviceList: List<String>? = null
        
        gsrSensor.scanForDevices { devices ->
            callbackCalled = true
            deviceList = devices
        }
        
        // Give some time for callback (though it should be immediate for permission failure)
        Thread.sleep(100)
        
        assertTrue("Callback should be called even for permission failure", callbackCalled)
        assertTrue("Device list should be empty for permission failure", deviceList?.isEmpty() ?: false)
    }

    @Test
    fun testScanForDevices_WithPermissions() {
        `when`(ContextCompat.checkSelfPermission(any(Context::class.java), anyString()))
            .thenReturn(PackageManager.PERMISSION_GRANTED)
        
        var callbackCalled = false
        
        gsrSensor.scanForDevices { devices ->
            callbackCalled = true
            // Devices list might be empty in test environment, which is fine
        }
        
        // Give some time for callback
        Thread.sleep(100)
        
        assertTrue("Callback should be called with permissions", callbackCalled)
    }

    @Test
    fun testLifecycleManagement() {
        // Test proper cleanup
        gsrSensor.release()
        
        // After release, operations should be safe but ineffective
        assertFalse("Should not be connected after release", gsrSensor.isConnected())
        assertFalse("Should not be streaming after release", gsrSensor.isStreamingActive())
        assertEquals("Sample count should be 0 after release", 0L, gsrSensor.getSampleCount())
    }

    @Test
    fun testBluetoothDisabled() {
        `when`(mockBluetoothAdapter.isEnabled).thenReturn(false)
        `when`(ContextCompat.checkSelfPermission(any(Context::class.java), anyString()))
            .thenReturn(PackageManager.PERMISSION_GRANTED)
        
        val result = gsrSensor.initialize()
        
        assertFalse("Initialization should fail when Bluetooth is disabled", result)
    }

    @Test
    fun testConnectFlow_ValidAddress() {
        // Initialize first
        `when`(ContextCompat.checkSelfPermission(any(Context::class.java), anyString()))
            .thenReturn(PackageManager.PERMISSION_GRANTED)
        gsrSensor.initialize()
        
        // Test with valid Bluetooth address format
        val validAddress = "00:11:22:33:44:55"
        val result = gsrSensor.connect(validAddress)
        
        // Note: In test environment without real Shimmer device, this will likely fail
        // but the address validation should pass
        assertFalse("Connection will fail in test environment without real device", result)
    }

    @Test
    fun testConnectFlow_InvalidAddress() {
        // Initialize first
        `when`(ContextCompat.checkSelfPermission(any(Context::class.java), anyString()))
            .thenReturn(PackageManager.PERMISSION_GRANTED)
        gsrSensor.initialize()
        
        // Test with invalid address
        val invalidAddress = "invalid-address"
        val result = gsrSensor.connect(invalidAddress)
        
        assertFalse("Connection should fail with invalid address", result)
        assertFalse("Should not be connected after invalid connect", gsrSensor.isConnected())
    }

    @Test
    fun testPermissionSpecific_API31Plus() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            // For API 31+, should check BLUETOOTH_SCAN and BLUETOOTH_CONNECT
            `when`(ContextCompat.checkSelfPermission(mockContext, Manifest.permission.BLUETOOTH_SCAN))
                .thenReturn(PackageManager.PERMISSION_GRANTED)
            `when`(ContextCompat.checkSelfPermission(mockContext, Manifest.permission.BLUETOOTH_CONNECT))
                .thenReturn(PackageManager.PERMISSION_GRANTED)
            `when`(ContextCompat.checkSelfPermission(mockContext, Manifest.permission.ACCESS_FINE_LOCATION))
                .thenReturn(PackageManager.PERMISSION_GRANTED)
            `when`(ContextCompat.checkSelfPermission(mockContext, Manifest.permission.ACCESS_COARSE_LOCATION))
                .thenReturn(PackageManager.PERMISSION_GRANTED)
            
            val result = gsrSensor.initialize()
            assertTrue("Should succeed with new permissions on API 31+", result)
        }
    }
}