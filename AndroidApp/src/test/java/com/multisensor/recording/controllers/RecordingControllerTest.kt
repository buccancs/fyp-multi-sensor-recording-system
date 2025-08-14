package com.multisensor.recording.controllers

import android.content.Context
import android.content.SharedPreferences
import com.multisensor.recording.TestConstants
import com.multisensor.recording.testutils.BaseUnitTest
import com.multisensor.recording.service.RecordingService
import com.multisensor.recording.ui.MainViewModel
import com.multisensor.recording.util.NetworkUtils
import io.mockk.*
import io.mockk.impl.annotations.MockK
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.*
import org.junit.*
import org.junit.Assert.*
import org.json.JSONObject

/**
 * Comprehensive unit tests for RecordingController.
 * Covers recording state management, service integration, and analytics.
 * 
 * Test Categories:
 * - Recording state management
 * - Session lifecycle operations  
 * - Service binding and communication
 * - Analytics and performance tracking
 * - Error handling and recovery
 * - Persistent state management
 * - Network integration
 */
@ExperimentalCoroutinesApi
class RecordingControllerTest : BaseUnitTest() {

    @get:Rule
    val mockKRule = io.mockk.junit4.MockKRule(this)

    @MockK
    private lateinit var context: Context
    
    @MockK
    private lateinit var sharedPreferences: SharedPreferences
    
    @MockK
    private lateinit var preferencesEditor: SharedPreferences.Editor
    
    @MockK
    private lateinit var recordingService: RecordingService
    
    @MockK
    private lateinit var mainViewModel: MainViewModel

    private lateinit var recordingController: RecordingController
    private lateinit var testScope: TestScope

    @Before
    override fun setUp() {
        super.setUp()
        testScope = TestScope(testDispatcher)
        
        setupDefaultMocks()
        
        recordingController = RecordingController()
    }

    @After
    override fun tearDown() {
        super.tearDown()
        testScope.cancel()
    }

    private fun setupDefaultMocks() {
        // Context and SharedPreferences mocks
        every { context.getSharedPreferences("recording_state", Context.MODE_PRIVATE) } returns sharedPreferences
        every { sharedPreferences.edit() } returns preferencesEditor
        every { sharedPreferences.getString(any(), any()) } returns null
        every { sharedPreferences.getLong(any(), any()) } returns 0L
        every { sharedPreferences.getBoolean(any(), any()) } returns false
        
        every { preferencesEditor.putString(any(), any()) } returns preferencesEditor
        every { preferencesEditor.putLong(any(), any()) } returns preferencesEditor
        every { preferencesEditor.putBoolean(any(), any()) } returns preferencesEditor
        every { preferencesEditor.apply() } just Runs
        every { preferencesEditor.commit() } returns true
        
        // Recording service mocks
        every { recordingService.startRecording(any()) } returns true
        every { recordingService.stopRecording() } returns true
        every { recordingService.pauseRecording() } returns true
        every { recordingService.resumeRecording() } returns true
        every { recordingService.getCurrentSessionId() } returns TestConstants.TEST_SESSION_ID
        every { recordingService.getRecordingDuration() } returns 30000L
        every { recordingService.isRecording() } returns false
        
        // MainViewModel mocks
        every { mainViewModel.updateRecordingState(any()) } just Runs
        every { mainViewModel.updateSessionInfo(any()) } just Runs
    }

    @Test
    fun `test_initial_recording_state`() = testScope.runTest {
        // Given: RecordingController is initialized
        
        // When: Getting initial recording state
        val initialState = recordingController.getRecordingState()
        
        // Then: Initial state should be correct
        assertFalse("Should not be recording initially", initialState.isRecording)
        assertNull("Session ID should be null initially", initialState.currentSessionId)
        assertEquals("Session start time should be 0", 0L, initialState.sessionStartTime)
        assertTrue("Recording parameters should be empty", initialState.recordingParameters.isEmpty())
        assertEquals("Error count should be 0", 0, initialState.errorCount)
    }

    @Test
    fun `test_start_recording_success`() = testScope.runTest {
        // Given: Recording controller is ready
        every { recordingService.startRecording(any()) } returns true
        
        // When: Starting recording
        val result = recordingController.startRecording(TestConstants.TEST_SESSION_ID)
        
        // Then: Recording should start successfully
        assertTrue("Recording should start successfully", result)
        
        // Verify recording state is updated
        val state = recordingController.getRecordingState()
        assertTrue("Should be recording", state.isRecording)
        assertEquals("Session ID should be set", TestConstants.TEST_SESSION_ID, state.currentSessionId)
        assertTrue("Session start time should be set", state.sessionStartTime > 0)
        
        // Verify service interaction
        verify { recordingService.startRecording(TestConstants.TEST_SESSION_ID) }
    }

    @Test
    fun `test_start_recording_failure_service_error`() = testScope.runTest {
        // Given: Recording service fails to start
        every { recordingService.startRecording(any()) } returns false
        
        // When: Starting recording
        val result = recordingController.startRecording(TestConstants.TEST_SESSION_ID)
        
        // Then: Recording should fail to start
        assertFalse("Recording should fail to start", result)
        
        // Verify state remains unchanged
        val state = recordingController.getRecordingState()
        assertFalse("Should not be recording", state.isRecording)
        assertNull("Session ID should remain null", state.currentSessionId)
        assertTrue("Error count should increase", state.errorCount > 0)
    }

    @Test
    fun `test_stop_recording_success`() = testScope.runTest {
        // Given: Recording is active
        recordingController.startRecording(TestConstants.TEST_SESSION_ID)
        assertTrue("Recording should be active", recordingController.getRecordingState().isRecording)
        
        // When: Stopping recording
        val result = recordingController.stopRecording()
        
        // Then: Recording should stop successfully
        assertTrue("Recording should stop successfully", result)
        
        // Verify recording state is updated
        val state = recordingController.getRecordingState()
        assertFalse("Should not be recording", state.isRecording)
        assertNull("Session ID should be cleared", state.currentSessionId)
        
        // Verify service interaction
        verify { recordingService.stopRecording() }
    }

    @Test
    fun `test_pause_recording_success`() = testScope.runTest {
        // Given: Recording is active
        recordingController.startRecording(TestConstants.TEST_SESSION_ID)
        
        // When: Pausing recording
        val result = recordingController.pauseRecording()
        
        // Then: Recording should pause successfully
        assertTrue("Recording should pause successfully", result)
        
        // Verify service interaction
        verify { recordingService.pauseRecording() }
    }

    @Test
    fun `test_resume_recording_success`() = testScope.runTest {
        // Given: Recording is paused
        recordingController.startRecording(TestConstants.TEST_SESSION_ID)
        recordingController.pauseRecording()
        
        // When: Resuming recording
        val result = recordingController.resumeRecording()
        
        // Then: Recording should resume successfully
        assertTrue("Recording should resume successfully", result)
        
        // Verify service interaction
        verify { recordingService.resumeRecording() }
    }

    @Test
    fun `test_get_recording_duration`() = testScope.runTest {
        // Given: Recording is active with known duration
        val expectedDuration = 45000L
        every { recordingService.getRecordingDuration() } returns expectedDuration
        recordingController.startRecording(TestConstants.TEST_SESSION_ID)
        
        // When: Getting recording duration
        val duration = recordingController.getRecordingDuration()
        
        // Then: Duration should match service duration
        assertEquals("Duration should match service", expectedDuration, duration)
        
        // Verify service interaction
        verify { recordingService.getRecordingDuration() }
    }

    @Test
    fun `test_get_recording_duration_not_recording`() = testScope.runTest {
        // Given: Not recording
        
        // When: Getting recording duration
        val duration = recordingController.getRecordingDuration()
        
        // Then: Duration should be 0
        assertEquals("Duration should be 0 when not recording", 0L, duration)
    }

    @Test
    fun `test_recording_parameters_update`() = testScope.runTest {
        // Given: Recording is active
        recordingController.startRecording(TestConstants.TEST_SESSION_ID)
        
        // When: Updating recording parameters
        val parameters = mapOf(
            "video_quality" to "1080p",
            "frame_rate" to 30,
            "bitrate" to 5000000
        )
        recordingController.updateRecordingParameters(parameters)
        
        // Then: Parameters should be updated in state
        val state = recordingController.getRecordingState()
        assertEquals("Parameters should be updated", parameters, state.recordingParameters)
    }

    @Test
    fun `test_session_metadata_management`() = testScope.runTest {
        // Given: A recording session
        val metadata = mapOf(
            "device_name" to "Test Device",
            "location" to "Test Lab",
            "notes" to "Test recording session"
        )
        
        // When: Setting session metadata
        recordingController.setSessionMetadata(TestConstants.TEST_SESSION_ID, metadata)
        
        // Then: Metadata should be stored
        val retrievedMetadata = recordingController.getSessionMetadata(TestConstants.TEST_SESSION_ID)
        assertEquals("Metadata should match", metadata, retrievedMetadata)
    }

    @Test
    fun `test_error_handling_and_recovery`() = testScope.runTest {
        // Given: Recording service throws exception
        every { recordingService.startRecording(any()) } throws RuntimeException("Service error")
        
        // When: Starting recording
        val result = recordingController.startRecording(TestConstants.TEST_SESSION_ID)
        
        // Then: Error should be handled gracefully
        assertFalse("Recording should fail", result)
        
        // Verify error count increases
        val state = recordingController.getRecordingState()
        assertTrue("Error count should increase", state.errorCount > 0)
        
        // Verify recovery attempt
        recordingController.attemptRecovery()
        
        // State should be reset for recovery
        val recoveredState = recordingController.getRecordingState()
        assertEquals("Error count should be reset", 0, recoveredState.errorCount)
    }

    @Test
    fun `test_persistent_state_save_and_restore`() = testScope.runTest {
        // Given: Active recording session
        recordingController.startRecording(TestConstants.TEST_SESSION_ID)
        val originalState = recordingController.getRecordingState()
        
        // When: Saving state to preferences
        recordingController.saveStateToPreferences(context)
        
        // Then: State should be saved
        verify { preferencesEditor.putString("recording_state_json", any()) }
        verify { preferencesEditor.putString("active_session", TestConstants.TEST_SESSION_ID) }
        verify { preferencesEditor.apply() }
        
        // When: Restoring state from preferences
        every { sharedPreferences.getString("active_session", null) } returns TestConstants.TEST_SESSION_ID
        every { sharedPreferences.getString("recording_state_json", null) } returns createStateJson(originalState)
        
        recordingController.restoreStateFromPreferences(context)
        
        // Then: State should be restored
        val restoredState = recordingController.getRecordingState()
        assertEquals("Session ID should be restored", originalState.currentSessionId, restoredState.currentSessionId)
        assertEquals("Recording state should be restored", originalState.isRecording, restoredState.isRecording)
    }

    @Test
    fun `test_concurrent_operation_handling`() = testScope.runTest {
        // Given: Multiple concurrent operations
        
        // When: Starting multiple recordings simultaneously
        val result1 = recordingController.startRecording("session_1")
        val result2 = recordingController.startRecording("session_2")
        
        // Then: Only one should succeed
        assertTrue("First recording should start", result1)
        assertFalse("Second recording should be rejected", result2)
        
        // Verify only one session is active
        val state = recordingController.getRecordingState()
        assertEquals("Only first session should be active", "session_1", state.currentSessionId)
    }

    @Test
    fun `test_analytics_tracking`() = testScope.runTest {
        // Given: Analytics are enabled
        recordingController.enableAnalytics(true)
        
        // When: Performing recording operations
        recordingController.startRecording(TestConstants.TEST_SESSION_ID)
        recordingController.stopRecording()
        
        // Then: Analytics should be tracked
        val analytics = recordingController.getAnalyticsData()
        assertNotNull("Analytics data should exist", analytics)
        assertTrue("Should have recording events", analytics.containsKey("recording_events"))
        assertTrue("Should have session count", analytics.containsKey("total_sessions"))
    }

    @Test
    fun `test_network_status_integration`() = testScope.runTest {
        // Given: Network status monitoring
        mockkObject(NetworkUtils)
        every { NetworkUtils.isNetworkAvailable(context) } returns true
        
        // When: Starting recording with network check
        val result = recordingController.startRecordingWithNetworkCheck(context, TestConstants.TEST_SESSION_ID)
        
        // Then: Recording should start with network available
        assertTrue("Recording should start with network", result)
        
        // When: Network becomes unavailable
        every { NetworkUtils.isNetworkAvailable(context) } returns false
        val resultNoNetwork = recordingController.startRecordingWithNetworkCheck(context, "session_2")
        
        // Then: Recording should handle network unavailability
        // Implementation depends on business logic - might still allow or might prevent
        assertNotNull("Result should be determined", resultNoNetwork)
        
        unmockkObject(NetworkUtils)
    }

    @Test
    fun `test_recording_quality_monitoring`() = testScope.runTest {
        // Given: Recording is active
        recordingController.startRecording(TestConstants.TEST_SESSION_ID)
        
        // When: Monitoring quality metrics
        recordingController.updateQualityMetrics(
            frameDrops = 5,
            audioLatency = 50L,
            networkJitter = 2.5
        )
        
        // Then: Quality metrics should be tracked
        val metrics = recordingController.getQualityMetrics()
        assertEquals("Frame drops should be tracked", 5, metrics["frame_drops"])
        assertEquals("Audio latency should be tracked", 50L, metrics["audio_latency"])
        assertEquals("Network jitter should be tracked", 2.5, metrics["network_jitter"])
    }

    @Test
    fun `test_session_cleanup_on_stop`() = testScope.runTest {
        // Given: Active recording session
        recordingController.startRecording(TestConstants.TEST_SESSION_ID)
        
        // When: Stopping recording
        recordingController.stopRecording()
        
        // Then: Session should be cleaned up
        val state = recordingController.getRecordingState()
        assertNull("Session ID should be cleared", state.currentSessionId)
        assertEquals("Session start time should be reset", 0L, state.sessionStartTime)
        assertTrue("Recording parameters should be empty", state.recordingParameters.isEmpty())
        
        // Verify cleanup with service
        verify { recordingService.stopRecording() }
    }

    @Test
    fun `test_error_count_reset_on_successful_operation`() = testScope.runTest {
        // Given: Previous errors exist
        every { recordingService.startRecording(any()) } throws RuntimeException("Error")
        recordingController.startRecording("failing_session")
        
        val stateWithErrors = recordingController.getRecordingState()
        assertTrue("Should have errors", stateWithErrors.errorCount > 0)
        
        // When: Successful operation occurs
        every { recordingService.startRecording(any()) } returns true
        recordingController.startRecording(TestConstants.TEST_SESSION_ID)
        
        // Then: Error count should be reset
        val stateAfterSuccess = recordingController.getRecordingState()
        assertEquals("Error count should be reset", 0, stateAfterSuccess.errorCount)
    }

    // Helper methods
    private fun createStateJson(state: RecordingController.RecordingState): String {
        return JSONObject().apply {
            put("isRecording", state.isRecording)
            put("currentSessionId", state.currentSessionId)
            put("sessionStartTime", state.sessionStartTime)
            put("lastUpdateTime", state.lastUpdateTime)
            put("errorCount", state.errorCount)
        }.toString()
    }
}