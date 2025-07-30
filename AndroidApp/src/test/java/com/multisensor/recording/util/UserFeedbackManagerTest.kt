package com.multisensor.recording.util

import android.content.Context
import android.view.View
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.google.android.material.snackbar.Snackbar
import com.google.common.truth.Truth.assertThat
import io.mockk.MockKAnnotations
import io.mockk.mockk
import io.mockk.verify
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.test.runBlockingTest
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith

/**
 * Tests for UserFeedbackManager to ensure proper user feedback handling
 */
@ExperimentalCoroutinesApi
@RunWith(AndroidJUnit4::class)
class UserFeedbackManagerTest {

    private lateinit var context: Context
    private lateinit var userFeedbackManager: UserFeedbackManager
    private lateinit var mockView: View

    @Before
    fun setup() {
        MockKAnnotations.init(this, relaxed = true)
        context = ApplicationProvider.getApplicationContext()
        userFeedbackManager = UserFeedbackManager(context)
        mockView = mockk(relaxed = true)
    }

    @Test
    fun `getUserFriendlyErrorMessage should convert technical errors to user friendly messages`() {
        // Test camera permission error
        val cameraError = SecurityException("Camera permission required")
        val friendlyMessage = userFeedbackManager.getUserFriendlyErrorMessage(cameraError)
        assertThat(friendlyMessage).contains("Permission required")
        assertThat(friendlyMessage).doesNotContain("SecurityException")

        // Test camera busy error
        val cameraBusyError = IllegalStateException("Camera is in use by another app")
        val cameraBusyMessage = userFeedbackManager.getUserFriendlyErrorMessage(cameraBusyError)
        assertThat(cameraBusyMessage).contains("Camera is not available")

        // Test network error
        val networkError = RuntimeException("Network connection failed")
        val networkMessage = userFeedbackManager.getUserFriendlyErrorMessage(networkError)
        assertThat(networkMessage).contains("Network connection issue")

        // Test storage error
        val storageError = RuntimeException("Insufficient storage space")
        val storageMessage = userFeedbackManager.getUserFriendlyErrorMessage(storageError)
        assertThat(storageMessage).contains("Insufficient storage space")

        // Test generic error
        val genericError = RuntimeException("Unknown technical error")
        val genericMessage = userFeedbackManager.getUserFriendlyErrorMessage(genericError)
        assertThat(genericMessage).contains("unexpected error occurred")
    }

    @Test
    fun `getSystemStatusMessage should provide comprehensive status information`() {
        // All systems working
        val allGoodMessage = userFeedbackManager.getSystemStatusMessage(
            isCameraOk = true,
            isThermalOk = true,
            isShimmerOk = true,
            isPcConnected = true
        )
        assertThat(allGoodMessage).contains("All systems ready")

        // Single issue
        val singleIssueMessage = userFeedbackManager.getSystemStatusMessage(
            isCameraOk = false,
            isThermalOk = true,
            isShimmerOk = true,
            isPcConnected = true
        )
        assertThat(singleIssueMessage).contains("Issue with camera")
        assertThat(singleIssueMessage).contains("Some features may be limited")

        // Multiple issues
        val multipleIssuesMessage = userFeedbackManager.getSystemStatusMessage(
            isCameraOk = false,
            isThermalOk = false,
            isShimmerOk = true,
            isPcConnected = false
        )
        assertThat(multipleIssuesMessage).contains("Multiple system issues")
    }

    @Test
    fun `getBatteryStatusMessage should provide helpful battery information`() {
        // Excellent battery
        val excellentMessage = userFeedbackManager.getBatteryStatusMessage(85, false)
        assertThat(excellentMessage).contains("excellent")

        // Good battery
        val goodMessage = userFeedbackManager.getBatteryStatusMessage(65, false)
        assertThat(goodMessage).contains("good")

        // Low battery
        val lowMessage = userFeedbackManager.getBatteryStatusMessage(20, false)
        assertThat(lowMessage).contains("low")
        assertThat(lowMessage).contains("Consider charging")

        // Critical battery
        val criticalMessage = userFeedbackManager.getBatteryStatusMessage(10, false)
        assertThat(criticalMessage).contains("critical")
        assertThat(criticalMessage).contains("Charging recommended")

        // Charging
        val chargingMessage = userFeedbackManager.getBatteryStatusMessage(50, true)
        assertThat(chargingMessage).contains("charging")
    }

    @Test
    fun `getRecordingStatusMessage should provide clear recording information`() {
        // Recording active
        val recordingMessage = userFeedbackManager.getRecordingStatusMessage(
            isRecording = true,
            duration = 125000, // 2 minutes 5 seconds
            deviceCount = 3
        )
        assertThat(recordingMessage).contains("Recording active")
        assertThat(recordingMessage).contains("02:05")
        assertThat(recordingMessage).contains("3 devices")

        // Ready to record
        val readyMessage = userFeedbackManager.getRecordingStatusMessage(
            isRecording = false,
            duration = 0,
            deviceCount = 2
        )
        assertThat(readyMessage).contains("Ready to record")
        assertThat(readyMessage).contains("2 devices")
    }

    @Test
    fun `feedback events should be emitted correctly`() = runBlockingTest {
        // Test error event
        val errorEvent = FeedbackEvent.Error("Test error message")
        userFeedbackManager.emitFeedbackEvent(errorEvent)
        
        val receivedEvent = userFeedbackManager.feedbackEvents.first()
        assertThat(receivedEvent).isInstanceOf(FeedbackEvent.Error::class.java)
        assertThat((receivedEvent as FeedbackEvent.Error).message).isEqualTo("Test error message")
    }

    @Test
    fun `extension functions should work correctly`() {
        // Test recording started extension
        userFeedbackManager.showRecordingStarted(mockView, "session-123456789")
        // In real UI test, verify Snackbar is shown with correct message

        // Test recording stopped extension  
        userFeedbackManager.showRecordingStopped(mockView, 65000) // 1 minute 5 seconds
        // In real UI test, verify Snackbar shows "01:05"

        // Test device connected extension
        userFeedbackManager.showDeviceConnected(mockView, "Thermal Camera")
        // In real UI test, verify success message is shown

        // Test low battery warning extension
        userFeedbackManager.showLowBatteryWarning(mockView, 15)
        // In real UI test, verify warning message with action button is shown
    }

    @Test
    fun `error dialog should be created with proper configuration`() {
        // This test would verify MaterialAlertDialog creation
        // In instrumented tests, you could test the actual dialog behavior
        
        userFeedbackManager.showErrorDialog(
            context = context,
            title = "Test Error",
            message = "This is a test error message",
            positiveText = "OK",
            negativeText = "Cancel"
        )
        
        // In real UI test environment:
        // - Verify dialog is displayed
        // - Verify dialog has correct title and message
        // - Verify button actions work correctly
    }

    @Test
    fun `confirmation dialog should handle destructive actions properly`() {
        var confirmCalled = false
        var cancelCalled = false
        
        userFeedbackManager.showConfirmationDialog(
            context = context,
            title = "Delete Recording",
            message = "This action cannot be undone",
            confirmText = "Delete",
            cancelText = "Cancel",
            onConfirm = { confirmCalled = true },
            onCancel = { cancelCalled = true },
            isDestructive = true
        )
        
        // In real UI test environment:
        // - Verify dialog styling for destructive action
        // - Test confirm and cancel callbacks
        // - Verify proper button colors and emphasis
    }
}