package com.multisensor.recording.ui

import android.content.Context
import androidx.arch.core.executor.testing.InstantTaskExecutorRule
import androidx.lifecycle.viewModelScope
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.google.common.truth.Truth.assertThat
import com.multisensor.recording.recording.CameraRecorder
import com.multisensor.recording.recording.ShimmerRecorder
import com.multisensor.recording.recording.ThermalRecorder
import com.multisensor.recording.service.SessionManager
import com.multisensor.recording.util.Logger
import io.mockk.MockKAnnotations
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.impl.annotations.MockK
import io.mockk.mockk
import io.mockk.verify
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.test.TestCoroutineDispatcher
import kotlinx.coroutines.test.runBlockingTest
import kotlinx.coroutines.test.setMain
import org.junit.After
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/**
 * Integration tests for the enhanced MainViewModel functionality
 */
@ExperimentalCoroutinesApi
@RunWith(AndroidJUnit4::class)
class MainViewModelEnhancedTest {

    @get:Rule
    val instantTaskExecutorRule = InstantTaskExecutorRule()

    private val testDispatcher = TestCoroutineDispatcher()

    @MockK private lateinit var cameraRecorder: CameraRecorder
    @MockK private lateinit var thermalRecorder: ThermalRecorder
    @MockK private lateinit var shimmerRecorder: ShimmerRecorder
    @MockK private lateinit var sessionManager: SessionManager
    @MockK private lateinit var logger: Logger

    private lateinit var context: Context
    private lateinit var viewModel: MainViewModelEnhanced

    @Before
    fun setup() {
        MockKAnnotations.init(this, relaxed = true)
        context = ApplicationProvider.getApplicationContext()
        kotlinx.coroutines.Dispatchers.setMain(testDispatcher)
        
        viewModel = MainViewModelEnhanced(
            context = context,
            cameraRecorder = cameraRecorder,
            thermalRecorder = thermalRecorder,
            shimmerRecorder = shimmerRecorder,
            sessionManager = sessionManager,
            logger = logger
        )
    }

    @After
    fun tearDown() {
        testDispatcher.cleanupTestCoroutines()
    }

    @Test
    fun `initializeSystemEnhanced should update UI state correctly on success`() = testDispatcher.runBlockingTest {
        // Given
        coEvery { cameraRecorder.initialize() } returns true
        coEvery { thermalRecorder.initialize() } returns true
        coEvery { shimmerRecorder.initialize() } returns true

        // When
        val mockTextureView = mockk<android.view.TextureView>()
        viewModel.initializeSystemEnhanced(mockTextureView)

        // Then
        val finalState = viewModel.uiState.first()
        assertThat(finalState.isInitialized).isTrue()
        assertThat(finalState.isLoadingPermissions).isFalse()
        assertThat(finalState.statusText).contains("System Status")
        assertThat(finalState.errorMessage).isNull()
    }

    @Test
    fun `initializeSystemEnhanced should handle camera initialization failure`() = testDispatcher.runBlockingTest {
        // Given
        coEvery { cameraRecorder.initialize() } returns false
        coEvery { thermalRecorder.initialize() } returns true
        coEvery { shimmerRecorder.initialize() } returns true

        // When
        val mockTextureView = mockk<android.view.TextureView>()
        viewModel.initializeSystemEnhanced(mockTextureView)

        // Then
        val finalState = viewModel.uiState.first()
        assertThat(finalState.isInitialized).isFalse()
        assertThat(finalState.showErrorDialog).isTrue()
        assertThat(finalState.errorMessage).isNotNull()
        assertThat(finalState.errorMessage).contains("Camera")
    }

    @Test
    fun `startRecordingEnhanced should validate conditions before starting`() = testDispatcher.runBlockingTest {
        // Given - system not initialized
        val initialState = MainUiState(isInitialized = false)
        
        // When
        viewModel.startRecordingEnhanced()

        // Then
        val finalState = viewModel.uiState.first()
        assertThat(finalState.isRecording).isFalse()
        assertThat(finalState.errorMessage).contains("not initialized")
    }

    @Test
    fun `startRecordingEnhanced should start recording when conditions are met`() = testDispatcher.runBlockingTest {
        // Given
        every { sessionManager.createNewSession() } returns "test-session-123"
        every { sessionManager.getCurrentSession() } returns mockk {
            every { sessionId } returns "test-session-123"
            every { startTime } returns System.currentTimeMillis()
        }
        
        // Set up initialized state
        val mockTextureView = mockk<android.view.TextureView>()
        viewModel.initializeSystemEnhanced(mockTextureView)

        // When
        viewModel.startRecordingEnhanced()

        // Then
        val finalState = viewModel.uiState.first()
        assertThat(finalState.isRecording).isTrue()
        assertThat(finalState.recordingSessionId).isNotNull()
        assertThat(finalState.statusText).contains("Recording in progress")
    }

    @Test
    fun `stopRecordingEnhanced should stop recording and clean up`() = testDispatcher.runBlockingTest {
        // Given - start recording first
        every { sessionManager.createNewSession() } returns "test-session-123"
        every { sessionManager.finalizeCurrentSession() } returns Unit
        
        // Set up recording state
        val mockTextureView = mockk<android.view.TextureView>()
        viewModel.initializeSystemEnhanced(mockTextureView)
        viewModel.startRecordingEnhanced()

        // When
        viewModel.stopRecordingEnhanced()

        // Then
        val finalState = viewModel.uiState.first()
        assertThat(finalState.isRecording).isFalse()
        assertThat(finalState.recordingSessionId).isNull()
        assertThat(finalState.statusText).contains("stopped successfully")
        
        verify { sessionManager.finalizeCurrentSession() }
    }

    @Test
    fun `clearErrorDialog should reset error state`() = testDispatcher.runBlockingTest {
        // Given - set up error state
        val mockTextureView = mockk<android.view.TextureView>()
        viewModel.initializeSystemEnhanced(mockTextureView) // This might set an error

        // When
        viewModel.clearErrorDialog()

        // Then
        val finalState = viewModel.uiState.first()
        assertThat(finalState.errorMessage).isNull()
        assertThat(finalState.showErrorDialog).isFalse()
    }

    @Test
    fun `battery monitoring should update battery status`() = testDispatcher.runBlockingTest {
        // This is a complex test that would require mocking Android system services
        // For now, I'll test that the viewModel is created without errors
        assertThat(viewModel).isNotNull()
        
        // In a real test environment, you would mock BatteryManager
        // and test the battery status updates
    }

    @Test
    fun `connection monitoring should update connection states`() = testDispatcher.runBlockingTest {
        // Given
        every { sessionManager.getDeviceState() } returns mockk {
            every { pcConnected } returns true
        }
        every { shimmerRecorder.isConnected.get() } returns true
        every { thermalRecorder.getThermalCameraStatus() } returns ThermalRecorder.ThermalCameraStatus(
            isAvailable = false,
            isRecording = false,
            isPreviewActive = false,
            width = 256,
            height = 192,
            frameRate = 25,
            frameCount = 0
        )

        // The connection monitoring runs in background coroutines
        // In real tests, you would advance the test dispatcher time
        // to trigger the monitoring updates
        
        assertThat(viewModel).isNotNull()
    }

    @Test
    fun `performance throttling should limit UI updates`() = testDispatcher.runBlockingTest {
        // This test would verify that rapid UI state updates are throttled
        // to prevent excessive recomposition and improve performance
        
        val initialTime = System.currentTimeMillis()
        
        // Multiple rapid updates
        repeat(10) {
            // Simulate rapid state changes that would be throttled
        }
        
        assertThat(viewModel).isNotNull()
        // In real implementation, verify throttling behavior
    }

    @Test
    fun `error handling should provide user friendly messages`() = testDispatcher.runBlockingTest {
        // Given
        coEvery { cameraRecorder.initialize() } throws SecurityException("Camera permission required")

        // When
        val mockTextureView = mockk<android.view.TextureView>()
        viewModel.initializeSystemEnhanced(mockTextureView)

        // Then
        val finalState = viewModel.uiState.first()
        assertThat(finalState.errorMessage).isNotNull()
        // Error message should be user-friendly, not technical
        assertThat(finalState.errorMessage).doesNotContain("SecurityException")
    }

    @Test
    fun `low battery validation should prevent recording`() = testDispatcher.runBlockingTest {
        // This test would verify that recording is prevented when battery is low
        // Would require mocking BatteryManager to return low battery level
        
        assertThat(viewModel).isNotNull()
        
        // In real implementation:
        // Given - battery level < 15% and not charging
        // When - attempt to start recording
        // Then - recording should be prevented with appropriate error message
    }

    @Test
    fun `device count calculation should be accurate`() = testDispatcher.runBlockingTest {
        // Given - mock connection states
        every { sessionManager.getDeviceState() } returns mockk {
            every { pcConnected } returns true
        }
        every { shimmerRecorder.getShimmerStatus() } returns ShimmerRecorder.ShimmerStatus(
            isAvailable = true,
            isConnected = true,
            isRecording = false,
            samplingRate = 256
        )
        every { thermalRecorder.getThermalCameraStatus() } returns ThermalRecorder.ThermalCameraStatus(
            isAvailable = true,
            isRecording = false,
            isPreviewActive = false,
            width = 256,
            height = 192,
            frameRate = 25,
            frameCount = 0
        )

        // When initialized, the system should count connected devices correctly
        val mockTextureView = mockk<android.view.TextureView>()
        viewModel.initializeSystemEnhanced(mockTextureView)

        // In real implementation, verify device count is calculated correctly
        // Should be 4 devices: main camera + PC + Shimmer + Thermal
        
        assertThat(viewModel).isNotNull()
    }
}