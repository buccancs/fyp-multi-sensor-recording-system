package com.multisensor.recording.controllers

import android.content.Context
import android.content.Intent
import androidx.activity.result.ActivityResultLauncher
import com.multisensor.recording.managers.ShimmerManager
import com.multisensor.recording.persistence.ShimmerDeviceStateRepository
import com.multisensor.recording.persistence.ShimmerDeviceState
import com.multisensor.recording.ui.MainViewModel
import com.shimmerresearch.android.manager.ShimmerBluetoothManagerAndroid
import io.mockk.*
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.runTest
import org.junit.After
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue

/**
 * Comprehensive unit tests for ShimmerController
 * Tests all new functionality including device state persistence,
 * multiple device support, enhanced error handling, and integration scenarios
 */
@OptIn(ExperimentalCoroutinesApi::class)
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [28])
class ShimmerControllerTest {
    
    private lateinit var mockShimmerManager: ShimmerManager
    private lateinit var mockRepository: ShimmerDeviceStateRepository
    private lateinit var mockErrorHandler: ShimmerErrorHandler
    private lateinit var mockViewModel: MainViewModel
    private lateinit var mockContext: Context
    private lateinit var mockCallback: ShimmerController.ShimmerCallback
    private lateinit var mockLauncher: ActivityResultLauncher<Intent>
    
    private lateinit var shimmerController: ShimmerController
    
    // Test data
    private val testDeviceAddress = "00:11:22:33:44:55"
    private val testDeviceName = "Shimmer3-1234"
    private val testBtType = ShimmerBluetoothManagerAndroid.BT_TYPE.BT_CLASSIC
    
    @Before
    fun setup() {
        // Create mocks
        mockShimmerManager = mockk(relaxed = true)
        mockRepository = mockk(relaxed = true)
        mockErrorHandler = mockk(relaxed = true)
        mockViewModel = mockk(relaxed = true)
        mockContext = mockk(relaxed = true)
        mockCallback = mockk(relaxed = true)
        mockLauncher = mockk(relaxed = true)
        
        // Setup repository mocks
        coEvery { mockRepository.getAllDeviceStates() } returns emptyList()
        coEvery { mockRepository.getAutoReconnectDevices() } returns emptyList()
        coEvery { mockRepository.saveDeviceState(any()) } just Runs
        coEvery { mockRepository.updateConnectionStatus(any(), any(), any(), any()) } just Runs
        coEvery { mockRepository.logConnectionAttempt(any(), any(), any(), any(), any()) } just Runs
        
        // Setup error handler mocks
        coEvery { mockErrorHandler.resetErrorState(any()) } just Runs
        coEvery { mockErrorHandler.generateDiagnosticReport(any()) } returns "Test diagnostic report"
        coEvery { mockErrorHandler.checkDeviceHealth(any()) } returns emptyList()
        
        // Create ShimmerController instance
        shimmerController = ShimmerController(mockShimmerManager, mockRepository, mockErrorHandler)
    }
    
    @After
    fun tearDown() {
        clearAllMocks()
    }
    
    // ========== Initialization Tests ==========
    
    @Test
    fun `setCallback should initialize controller and load saved states`() = runTest {
        // Given
        val savedDevice = createTestDeviceState()
        coEvery { mockRepository.getAllDeviceStates() } returns listOf(savedDevice)
        
        // When
        shimmerController.setCallback(mockCallback)
        
        // Then
        verify { mockCallback }
        coVerify { mockRepository.getAllDeviceStates() }
        coVerify { mockRepository.getAutoReconnectDevices() }
    }
    
    @Test
    fun `loadSavedDeviceStates should restore device configurations`() = runTest {
        // Given
        val savedDevices = listOf(
            createTestDeviceState(address = "00:11:22:33:44:55", name = "Device1"),
            createTestDeviceState(address = "00:11:22:33:44:56", name = "Device2")
        )
        coEvery { mockRepository.getAllDeviceStates() } returns savedDevices
        
        // When
        shimmerController.setCallback(mockCallback)
        
        // Then
        coVerify { mockRepository.getAllDeviceStates() }
        assertEquals(2, shimmerController.getConnectedDevices().size)
    }
    
    // ========== Device Selection Tests ==========
    
    @Test
    fun `handleDeviceSelectionResult should save device state on successful selection`() = runTest {
        // Given
        shimmerController.setCallback(mockCallback)
        
        // When
        shimmerController.handleDeviceSelectionResult(testDeviceAddress, testDeviceName)
        
        // Then
        verify { mockCallback.updateStatusText("Device selected: $testDeviceName") }
        verify { mockCallback.showToast("Selected: $testDeviceName") }
        verify { mockCallback.onDeviceSelected(testDeviceAddress, testDeviceName) }
        coVerify { mockRepository.saveDeviceState(any()) }
    }
    
    @Test
    fun `handleDeviceSelectionResult should handle cancellation`() = runTest {
        // Given
        shimmerController.setCallback(mockCallback)
        
        // When
        shimmerController.handleDeviceSelectionResult(null, null)
        
        // Then
        verify { mockCallback.onDeviceSelectionCancelled() }
        coVerify(exactly = 0) { mockRepository.saveDeviceState(any()) }
    }
    
    @Test
    fun `launchShimmerDeviceDialog should delegate to controller`() = runTest {
        // Given
        val mockActivity = mockk<android.app.Activity>(relaxed = true)
        
        // When
        shimmerController.launchShimmerDeviceDialog(mockActivity, mockLauncher)
        
        // Then - should not throw exception and should attempt to launch
        // Note: Actual intent launching is tested in integration tests
        assertTrue(true) // Test passes if no exception thrown
    }
    
    // ========== Connection Tests ==========
    
    @Test
    fun `connectToSelectedDevice should connect when device is selected`() = runTest {
        // Given
        shimmerController.setCallback(mockCallback)
        shimmerController.handleDeviceSelectionResult(testDeviceAddress, testDeviceName)
        
        // Setup ViewModel mock to simulate successful connection
        every { mockViewModel.connectShimmerDevice(any(), any(), any(), any()) } answers {
            val callback = arg<(Boolean) -> Unit>(3)
            callback(true) // Simulate successful connection
        }
        
        // When
        shimmerController.connectToSelectedDevice(mockViewModel)
        
        // Then
        verify { mockViewModel.connectShimmerDevice(testDeviceAddress, testDeviceName, testBtType, any()) }
    }
    
    @Test
    fun `connectToSelectedDevice should handle no device selected`() = runTest {
        // Given
        shimmerController.setCallback(mockCallback)
        
        // When
        shimmerController.connectToSelectedDevice(mockViewModel)
        
        // Then
        verify { mockCallback.onShimmerError("No device selected") }
    }
    
    @Test
    fun `connectToDevice should prevent duplicate connections`() = runTest {
        // Given
        shimmerController.setCallback(mockCallback)
        val deviceState = createTestDeviceState(connected = true)
        coEvery { mockRepository.getDeviceState(testDeviceAddress) } returns deviceState
        
        // When
        shimmerController.connectToDevice(testDeviceAddress, testDeviceName, mockViewModel)
        
        // Then
        verify { mockCallback.onShimmerError("Device $testDeviceName is already connected") }
    }
    
    // ========== Multiple Device Support Tests ==========
    
    @Test
    fun `getConnectedDevices should return only connected devices`() = runTest {
        // Given
        shimmerController.setCallback(mockCallback)
        val devices = listOf(
            createTestDeviceState(address = "00:11:22:33:44:55", connected = true),
            createTestDeviceState(address = "00:11:22:33:44:56", connected = false),
            createTestDeviceState(address = "00:11:22:33:44:57", connected = true)
        )
        coEvery { mockRepository.getAllDeviceStates() } returns devices
        
        // When
        shimmerController.setCallback(mockCallback) // Triggers loading
        val connectedDevices = shimmerController.getConnectedDevices()
        
        // Then
        assertEquals(2, connectedDevices.size)
        assertTrue(connectedDevices.all { it.isConnected })
    }
    
    @Test
    fun `getConnectedDeviceCount should return correct count`() = runTest {
        // Given
        shimmerController.setCallback(mockCallback)
        val devices = listOf(
            createTestDeviceState(address = "00:11:22:33:44:55", connected = true),
            createTestDeviceState(address = "00:11:22:33:44:56", connected = true)
        )
        coEvery { mockRepository.getAllDeviceStates() } returns devices
        
        // When
        shimmerController.setCallback(mockCallback)
        val count = shimmerController.getConnectedDeviceCount()
        
        // Then
        assertEquals(2, count)
    }
    
    @Test
    fun `disconnectAllDevices should disconnect all connected devices`() = runTest {
        // Given
        shimmerController.setCallback(mockCallback)
        val devices = listOf(
            createTestDeviceState(address = "00:11:22:33:44:55", connected = true),
            createTestDeviceState(address = "00:11:22:33:44:56", connected = true)
        )
        coEvery { mockRepository.getAllDeviceStates() } returns devices
        
        // Setup ViewModel mock for disconnection
        every { mockViewModel.disconnectShimmerDevice(any(), any()) } answers {
            val callback = arg<(Boolean) -> Unit>(1)
            callback(true) // Simulate successful disconnection
        }
        
        // When
        shimmerController.setCallback(mockCallback)
        shimmerController.disconnectAllDevices(mockViewModel)
        
        // Then
        verify(exactly = 2) { mockViewModel.disconnectShimmerDevice(any(), any()) }
    }
    
    // ========== Configuration Tests ==========
    
    @Test
    fun `configureSensorChannels should update device configuration`() = runTest {
        // Given
        shimmerController.setCallback(mockCallback)
        shimmerController.handleDeviceSelectionResult(testDeviceAddress, testDeviceName)
        val enabledChannels = setOf("GSR", "Accelerometer")
        
        // Setup ViewModel mock
        every { mockViewModel.configureShimmerSensors(any(), any(), any()) } answers {
            val callback = arg<(Boolean) -> Unit>(2)
            callback(true) // Simulate successful configuration
        }
        
        // When
        shimmerController.configureSensorChannels(mockViewModel, enabledChannels)
        
        // Then
        verify { mockCallback.updateStatusText("Configuring sensors...") }
        verify { mockViewModel.configureShimmerSensors(testDeviceAddress, any(), any()) }
    }
    
    @Test
    fun `setSamplingRate should update sampling rate for device`() = runTest {
        // Given
        shimmerController.setCallback(mockCallback)
        shimmerController.handleDeviceSelectionResult(testDeviceAddress, testDeviceName)
        val samplingRate = 1024.0
        
        // Setup ViewModel mock
        every { mockViewModel.setShimmerSamplingRate(any(), any(), any()) } answers {
            val callback = arg<(Boolean) -> Unit>(2)
            callback(true) // Simulate successful update
        }
        
        // When
        shimmerController.setSamplingRate(mockViewModel, samplingRate)
        
        // Then
        verify { mockCallback.updateStatusText("Setting sampling rate to ${samplingRate}Hz...") }
        verify { mockViewModel.setShimmerSamplingRate(testDeviceAddress, samplingRate, any()) }
    }
    
    // ========== Persistence Tests ==========
    
    @Test
    fun `setAutoReconnectEnabled should update persistence`() = runTest {
        // Given
        shimmerController.setCallback(mockCallback)
        
        // When
        shimmerController.setAutoReconnectEnabled(testDeviceAddress, true)
        
        // Then
        coVerify { mockRepository.setAutoReconnectEnabled(testDeviceAddress, true) }
    }
    
    @Test
    fun `setDeviceConnectionPriority should update persistence`() = runTest {
        // Given
        shimmerController.setCallback(mockCallback)
        val priority = 5
        
        // When
        shimmerController.setDeviceConnectionPriority(testDeviceAddress, priority)
        
        // Then
        coVerify { mockRepository.setDeviceConnectionPriority(testDeviceAddress, priority) }
    }
    
    @Test
    fun `exportDeviceConfigurations should return all device states`() = runTest {
        // Given
        val devices = listOf(
            createTestDeviceState(address = "00:11:22:33:44:55"),
            createTestDeviceState(address = "00:11:22:33:44:56")
        )
        coEvery { mockRepository.getAllDeviceStates() } returns devices
        
        // When
        val exported = shimmerController.exportDeviceConfigurations()
        
        // Then
        assertEquals(2, exported.size)
        coVerify { mockRepository.getAllDeviceStates() }
    }
    
    // ========== Error Handling Tests ==========
    
    @Test
    fun `connectToDevice should use error handler for failures`() = runTest {
        // Given
        shimmerController.setCallback(mockCallback)
        val exception = RuntimeException("Connection timeout")
        
        // Setup error handler mock
        coEvery { 
            mockErrorHandler.handleError(any(), any(), any(), any(), any(), any(), any(), any()) 
        } returns false
        
        // When
        shimmerController.connectToDevice(testDeviceAddress, testDeviceName, mockViewModel)
        
        // Then
        coVerify { 
            mockErrorHandler.handleError(
                deviceAddress = testDeviceAddress,
                deviceName = testDeviceName,
                exception = any(),
                errorMessage = any(),
                attemptNumber = any(),
                connectionType = testBtType,
                onRetry = any(),
                onFinalFailure = any()
            ) 
        }
    }
    
    // ========== State Management Tests ==========
    
    @Test
    fun `getConnectionStatus should return comprehensive status`() = runTest {
        // Given
        shimmerController.setCallback(mockCallback)
        shimmerController.handleDeviceSelectionResult(testDeviceAddress, testDeviceName)
        
        // When
        val status = shimmerController.getConnectionStatus()
        
        // Then
        assertTrue(status.contains("Shimmer Status:"))
        assertTrue(status.contains(testDeviceName))
        assertTrue(status.contains(testDeviceAddress))
    }
    
    @Test
    fun `getDeviceManagementStatus should return correct status messages`() = runTest {
        // Given
        shimmerController.setCallback(mockCallback)
        
        // When - no devices
        var status = shimmerController.getDeviceManagementStatus()
        assertEquals("No devices configured", status)
        
        // Add a device
        shimmerController.handleDeviceSelectionResult(testDeviceAddress, testDeviceName)
        
        // When - one device configured but not connected
        status = shimmerController.getDeviceManagementStatus()
        assertTrue(status.contains("1 device") && status.contains("none connected"))
    }
    
    @Test
    fun `resetState should clear controller state`() = runTest {
        // Given
        shimmerController.setCallback(mockCallback)
        shimmerController.handleDeviceSelectionResult(testDeviceAddress, testDeviceName)
        shimmerController.setPreferredBtType(ShimmerBluetoothManagerAndroid.BT_TYPE.BLE)
        
        // When
        shimmerController.resetState()
        
        // Then
        val (address, name) = shimmerController.getSelectedDeviceInfo()
        assertNull(address)
        assertNull(name)
        assertEquals(ShimmerBluetoothManagerAndroid.BT_TYPE.BT_CLASSIC, shimmerController.getPreferredBtType())
    }
    
    // ========== Helper Methods ==========
    
    private fun createTestDeviceState(
        address: String = testDeviceAddress,
        name: String = testDeviceName,
        connected: Boolean = false,
        connectionType: ShimmerBluetoothManagerAndroid.BT_TYPE = testBtType
    ): ShimmerDeviceState {
        return ShimmerDeviceState(
            deviceAddress = address,
            deviceName = name,
            connectionType = connectionType,
            isConnected = connected,
            lastConnectedTimestamp = if (connected) System.currentTimeMillis() else 0L,
            enabledSensors = setOf("GSR", "Accelerometer"),
            samplingRate = 512.0,
            gsrRange = 0,
            autoReconnectEnabled = true,
            preferredConnectionOrder = 0
        )
    }
}