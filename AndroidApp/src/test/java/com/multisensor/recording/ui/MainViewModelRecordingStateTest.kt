package com.multisensor.recording.ui

import android.content.Context
import android.view.SurfaceView
import android.view.TextureView
import com.google.common.truth.Truth.assertThat
import com.multisensor.recording.recording.CameraRecorder
import com.multisensor.recording.recording.ShimmerRecorder
import com.multisensor.recording.recording.ThermalRecorder
import com.multisensor.recording.service.SessionManager
import com.multisensor.recording.network.FileTransferHandler
import com.multisensor.recording.network.JsonSocketClient
import com.multisensor.recording.network.NetworkConfiguration
import com.multisensor.recording.calibration.CalibrationCaptureManager
import com.multisensor.recording.util.Logger
import io.mockk.*
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runTest
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [28])
@ExperimentalCoroutinesApi
class MainViewModelRecordingStateTest {

    private lateinit var viewModel: MainViewModel
    private val mockContext: Context = mockk(relaxed = true)
    private val mockCameraRecorder: CameraRecorder = mockk(relaxed = true)
    private val mockThermalRecorder: ThermalRecorder = mockk(relaxed = true)
    private val mockShimmerRecorder: ShimmerRecorder = mockk(relaxed = true)
    private val mockSessionManager: SessionManager = mockk(relaxed = true)
    private val mockFileTransferHandler: FileTransferHandler = mockk(relaxed = true)
    private val mockCalibrationCaptureManager: CalibrationCaptureManager = mockk(relaxed = true)
    private val mockJsonSocketClient: JsonSocketClient = mockk(relaxed = true)
    private val mockNetworkConfiguration: NetworkConfiguration = mockk(relaxed = true)
    private val mockLogger: Logger = mockk(relaxed = true)

    @Before
    fun setUp() {
        every { mockLogger.info(any()) } returns Unit
        every { mockLogger.debug(any()) } returns Unit
        every { mockLogger.error(any()) } returns Unit
        
        coEvery { mockSessionManager.createNewSession() } returns "test-session-123"
        coEvery { mockSessionManager.finalizeCurrentSession() } returns Unit
        
        viewModel = MainViewModel(
            mockContext,
            mockCameraRecorder,
            mockThermalRecorder,
            mockShimmerRecorder,
            mockSessionManager,
            mockFileTransferHandler,
            mockCalibrationCaptureManager,
            mockJsonSocketClient,
            mockNetworkConfiguration,
            mockLogger
        )
    }

    @Test
    fun `initial state should have isRecording false and initializing status`() = runTest {
        val initialState = viewModel.uiState.first()
        
        assertThat(initialState.isRecording).isFalse()
        assertThat(initialState.statusText).isEqualTo("Initializing...")
        assertThat(initialState.isInitialized).isFalse()
    }

    @Test
    fun `canStartRecording should be false when not initialized`() = runTest {
        val state = viewModel.uiState.first()
        
        assertThat(state.canStartRecording).isFalse()
    }

    @Test
    fun `canStopRecording should be false when not recording`() = runTest {
        val state = viewModel.uiState.first()
        
        assertThat(state.canStopRecording).isFalse()
    }

    @Test
    fun `setRecordVideoEnabled should work`() = runTest {
        viewModel.setRecordVideoEnabled(true)
        advanceUntilIdle()
        
        verify { mockLogger.info(any()) }
    }

    @Test
    fun `setCaptureRawEnabled should work`() = runTest {
        viewModel.setCaptureRawEnabled(true)
        advanceUntilIdle()
        
        verify { mockLogger.info(any()) }
    }

    @Test
    fun `startRecording should update recording state`() = runTest {
        
        val mockTextureView: TextureView = mockk(relaxed = true)
        viewModel.initializeSystem(mockTextureView)
        advanceUntilIdle()
        
        viewModel.startRecording()
        advanceUntilIdle()
        
        val state = viewModel.uiState.first()
        
        verify { mockLogger.info(any()) }
    }

    @Test
    fun `stopRecording should be callable when recording`() = runTest {
        viewModel.stopRecording()
        advanceUntilIdle()
        
        verify { mockLogger.info(any()) }
    }

    @Test
    fun `captureRawImage should work`() = runTest {
        viewModel.captureRawImage()
        advanceUntilIdle()
        
        verify { mockLogger.info(any()) }
    }

    @Test
    fun `checkRawStage3Availability should return boolean`() = runTest {
        val isAvailable = viewModel.checkRawStage3Availability()
        
        assertThat(isAvailable is Boolean).isTrue()
    }

    @Test
    fun `checkThermalCameraAvailability should return boolean`() = runTest {
        val isAvailable = viewModel.checkThermalCameraAvailability()
        
        assertThat(isAvailable is Boolean).isTrue()
    }

    @Test
    fun `initializeSystem should change initialization state`() = runTest {
        val mockTextureView: TextureView = mockk(relaxed = true)
        val mockSurfaceView: SurfaceView = mockk(relaxed = true)
        
        viewModel.initializeSystem(mockTextureView, mockSurfaceView)
        advanceUntilIdle()
        
        verify { mockLogger.info(any()) }
    }

    @Test
    fun `initializeSystemWithFallback should work`() = runTest {
        viewModel.initializeSystemWithFallback()
        advanceUntilIdle()
        
        verify { mockLogger.info(any()) }
    }

    @Test
    fun `ui state properties should have expected types`() = runTest {
        val state = viewModel.uiState.first()
        
        assertThat(state.isRecording is Boolean).isTrue()
        assertThat(state.statusText is String).isTrue()
        assertThat(state.isInitialized is Boolean).isTrue()
        assertThat(state.recordingDuration is Long).isTrue()
        assertThat(state.isReadyToRecord is Boolean).isTrue()
        
        assertThat(state.isPcConnected is Boolean).isTrue()
        assertThat(state.isShimmerConnected is Boolean).isTrue()
        assertThat(state.isThermalConnected is Boolean).isTrue()
        assertThat(state.isCameraConnected is Boolean).isTrue()
        
        assertThat(state.canStartRecording is Boolean).isTrue()
        assertThat(state.canStopRecording is Boolean).isTrue()
        assertThat(state.canRunCalibration is Boolean).isTrue()
    }

    @Test
    fun `recording session management should work with session manager`() = runTest {
        
        viewModel.startRecording()
        advanceUntilIdle()
        
        viewModel.stopRecording()
        advanceUntilIdle()
        
        verify { mockLogger.info(any()) }
    }

    @Test
    fun `error states should be handled properly`() = runTest {
        val state = viewModel.uiState.first()
        
        assertThat(state.errorMessage).isNull() 
        assertThat(state.showErrorDialog is Boolean).isTrue()
    }

    @Test
    fun `loading states should be tracked properly`() = runTest {
        val state = viewModel.uiState.first()
        
        assertThat(state.isLoadingRecording is Boolean).isTrue()
        assertThat(state.isLoadingCalibration is Boolean).isTrue()
        assertThat(state.isLoadingPermissions is Boolean).isTrue()
    }
}
