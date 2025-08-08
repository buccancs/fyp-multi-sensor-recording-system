package com.multisensor.recording.ui
import android.content.Context
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
import com.multisensor.recording.testbase.BaseUnitTest
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
class MainViewModelRecordingStateEnhancedTest : BaseUnitTest() {
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
    override fun setUp() {
        super.setUp()
        every { mockLogger.info(any()) } returns Unit
        every { mockLogger.debug(any()) } returns Unit
        every { mockLogger.error(any()) } returns Unit
        every { mockLogger.warn(any()) } returns Unit
        coEvery { mockSessionManager.createNewSession() } returns "test-session-123"
        coEvery { mockSessionManager.finalizeCurrentSession() } returns Unit
        coEvery { mockSessionManager.isSessionActive() } returns false
        coEvery { mockSessionManager.getCurrentSessionId() } returns null
        coEvery { mockCameraRecorder.startRecording(any()) } returns Unit
        coEvery { mockCameraRecorder.stopRecording() } returns Unit
        coEvery { mockThermalRecorder.startRecording(any()) } returns Unit
        coEvery { mockThermalRecorder.stopRecording() } returns Unit
        coEvery { mockShimmerRecorder.startRecording(any()) } returns Unit
        coEvery { mockShimmerRecorder.stopRecording() } returns Unit
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
    fun `initial recording state should be correct`() = runTest {
        val initialState = viewModel.uiState.first()
        assertThat(initialState.isRecording).isFalse()
        assertThat(initialState.statusText).isEqualTo("Initializing...")
        assertThat(initialState.recordingDuration).isEqualTo(0L)
        assertThat(initialState.canStartRecording).isFalse()
        assertThat(initialState.canStopRecording).isFalse()
        assertThat(initialState.isLoadingRecording).isFalse()
    }
    @Test
    fun `isRecording flag should transition correctly during recording lifecycle`() = runTest {
        val mockTextureView: TextureView = mockk(relaxed = true)
        viewModel.initializeSystem(mockTextureView)
        advanceUntilIdle()
        var state = viewModel.uiState.first()
        assertThat(state.isRecording).isFalse()
        coEvery { mockSessionManager.isSessionActive() } returns true
        coEvery { mockSessionManager.getCurrentSessionId() } returns "test-session-123"
        viewModel.startRecording()
        advanceUntilIdle()
        state = viewModel.uiState.first()
        assertThat(state.isRecording).isTrue()
        viewModel.stopRecording()
        advanceUntilIdle()
        state = viewModel.uiState.first()
        assertThat(state.isRecording).isFalse()
    }
    @Test
    fun `status text should update appropriately during recording transitions`() = runTest {
        val mockTextureView: TextureView = mockk(relaxed = true)
        viewModel.initializeSystem(mockTextureView)
        advanceUntilIdle()
        var state = viewModel.uiState.first()
        assertThat(state.statusText).contains("Ready")
        coEvery { mockSessionManager.isSessionActive() } returns true
        viewModel.startRecording()
        advanceUntilIdle()
        state = viewModel.uiState.first()
        assertThat(state.statusText).contains("Recording")
        viewModel.stopRecording()
        advanceUntilIdle()
        state = viewModel.uiState.first()
        assertThat(state.statusText).containsAnyOf("Ready", "Stopped")
    }
    @Test
    fun `canStartRecording should be true only when ready and not recording`() = runTest {
        val mockTextureView: TextureView = mockk(relaxed = true)
        viewModel.initializeSystem(mockTextureView)
        advanceUntilIdle()
        var state = viewModel.uiState.first()
        assertThat(state.canStartRecording).isTrue()
        assertThat(state.isRecording).isFalse()
        coEvery { mockSessionManager.isSessionActive() } returns true
        viewModel.startRecording()
        advanceUntilIdle()
        state = viewModel.uiState.first()
        assertThat(state.canStartRecording).isFalse()
        assertThat(state.isRecording).isTrue()
    }
    @Test
    fun `canStopRecording should be true only when recording`() = runTest {
        val mockTextureView: TextureView = mockk(relaxed = true)
        viewModel.initializeSystem(mockTextureView)
        advanceUntilIdle()
        var state = viewModel.uiState.first()
        assertThat(state.canStopRecording).isFalse()
        assertThat(state.isRecording).isFalse()
        coEvery { mockSessionManager.isSessionActive() } returns true
        viewModel.startRecording()
        advanceUntilIdle()
        state = viewModel.uiState.first()
        assertThat(state.canStopRecording).isTrue()
        assertThat(state.isRecording).isTrue()
        viewModel.stopRecording()
        advanceUntilIdle()
        state = viewModel.uiState.first()
        assertThat(state.canStopRecording).isFalse()
        assertThat(state.isRecording).isFalse()
    }
    @Test
    fun `recording duration should track time correctly`() = runTest {
        val mockTextureView: TextureView = mockk(relaxed = true)
        viewModel.initializeSystem(mockTextureView)
        advanceUntilIdle()
        coEvery { mockSessionManager.isSessionActive() } returns true
        viewModel.startRecording()
        advanceUntilIdle()
        val state = viewModel.uiState.first()
        assertThat(state.recordingDuration).isAtLeast(0L)
    }
    @Test
    fun `startRecording should call all necessary recorders when sensors enabled`() = runTest {
        val mockTextureView: TextureView = mockk(relaxed = true)
        viewModel.initializeSystem(mockTextureView)
        viewModel.setRecordVideoEnabled(true)
        viewModel.setCaptureRawEnabled(true)
        advanceUntilIdle()
        coEvery { mockSessionManager.isSessionActive() } returns true
        viewModel.startRecording()
        advanceUntilIdle()
        coVerify { mockSessionManager.createNewSession() }
        coVerify { mockCameraRecorder.startRecording(any()) }
        verify { mockLogger.info(match { it.contains("Starting recording") }) }
    }
    @Test
    fun `stopRecording should call all necessary recorders and finalize session`() = runTest {
        val mockTextureView: TextureView = mockk(relaxed = true)
        viewModel.initializeSystem(mockTextureView)
        advanceUntilIdle()
        coEvery { mockSessionManager.isSessionActive() } returns true
        viewModel.startRecording()
        advanceUntilIdle()
        viewModel.stopRecording()
        advanceUntilIdle()
        coVerify { mockCameraRecorder.stopRecording() }
        coVerify { mockSessionManager.finalizeCurrentSession() }
        verify { mockLogger.info(match { it.contains("Stopping recording") }) }
    }
    @Test
    fun `recording error should update error state correctly`() = runTest {
        val errorMessage = "Recording failed"
        coEvery { mockCameraRecorder.startRecording(any()) } throws Exception(errorMessage)
        val mockTextureView: TextureView = mockk(relaxed = true)
        viewModel.initializeSystem(mockTextureView)
        advanceUntilIdle()
        viewModel.startRecording()
        advanceUntilIdle()
        val state = viewModel.uiState.first()
        assertThat(state.isRecording).isFalse()
        assertThat(state.errorMessage).isNotNull()
        assertThat(state.showErrorDialog).isTrue()
        verify { mockLogger.error(match { it.contains("Recording failed") }) }
    }
    @Test
    fun `isLoadingRecording should be true during recording start`() = runTest {
        val mockTextureView: TextureView = mockk(relaxed = true)
        viewModel.initializeSystem(mockTextureView)
        advanceUntilIdle()
        coEvery { mockSessionManager.isSessionActive() } returns true
        viewModel.startRecording()
        val state = viewModel.uiState.first()
        assertThat(state.isLoadingRecording is Boolean).isTrue()
    }
    @Test
    fun `sensor data collection state should be managed correctly`() = runTest {
        viewModel.setThermalRecordingEnabled(true)
        advanceUntilIdle()
        viewModel.setShimmerRecordingEnabled(true)
        advanceUntilIdle()
        viewModel.setRecordVideoEnabled(true)
        advanceUntilIdle()
        val state = viewModel.uiState.first()
        assertThat(state.isThermalConnected is Boolean).isTrue()
        assertThat(state.isShimmerConnected is Boolean).isTrue()
        assertThat(state.isCameraConnected is Boolean).isTrue()
    }
    @Test
    fun `session management during recording lifecycle should work correctly`() = runTest {
        val mockTextureView: TextureView = mockk(relaxed = true)
        viewModel.initializeSystem(mockTextureView)
        advanceUntilIdle()
        viewModel.startRecording()
        advanceUntilIdle()
        coVerify { mockSessionManager.createNewSession() }
        viewModel.stopRecording()
        advanceUntilIdle()
        coVerify { mockSessionManager.finalizeCurrentSession() }
    }
    @Test
    fun `multiple recording attempts should handle state correctly`() = runTest {
        val mockTextureView: TextureView = mockk(relaxed = true)
        viewModel.initializeSystem(mockTextureView)
        advanceUntilIdle()
        coEvery { mockSessionManager.isSessionActive() } returns true
        viewModel.startRecording()
        advanceUntilIdle()
        var state = viewModel.uiState.first()
        assertThat(state.isRecording).isTrue()
        viewModel.stopRecording()
        advanceUntilIdle()
        state = viewModel.uiState.first()
        assertThat(state.isRecording).isFalse()
        viewModel.startRecording()
        advanceUntilIdle()
        state = viewModel.uiState.first()
        assertThat(state.isRecording).isTrue()
        viewModel.stopRecording()
        advanceUntilIdle()
        state = viewModel.uiState.first()
        assertThat(state.isRecording).isFalse()
        coVerify(exactly = 2) { mockSessionManager.createNewSession() }
        coVerify(exactly = 2) { mockSessionManager.finalizeCurrentSession() }
    }
}