package com.multisensor.recording.util

import android.content.Context
import android.widget.Toast
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.Mockito.*
import org.robolectric.annotation.Config
import kotlin.test.assertFalse
import kotlin.test.assertTrue

/**
 * Unit tests for ToastManager focusing on ASCII-only message enforcement.
 * Tests the fixes from remediation checklist item #4.
 */
@RunWith(AndroidJUnit4::class)
@Config(manifest = Config.NONE)
class ToastManagerTest {

    private lateinit var mockContext: Context

    @Before
    fun setUp() {
        mockContext = mock(Context::class.java)
    }

    @Test
    fun testPredefinedMessages_ASCIIOnly() {
        val messages = listOf(
            ToastManager.Messages.USB_DEVICE_DETECTED,
            ToastManager.Messages.DEVICE_CONNECTION_SUCCESS,
            ToastManager.Messages.DEVICE_CONNECTION_ERROR,
            ToastManager.Messages.DEVICE_TROUBLESHOOTING,
            ToastManager.Messages.CONFIG_RELOAD_SUCCESS,
            ToastManager.Messages.CONFIG_RELOAD_FAILED,
            ToastManager.Messages.CONFIG_MANAGER_ERROR,
            ToastManager.Messages.CONFIG_MANAGER_UNAVAILABLE,
            ToastManager.Messages.CONFIG_ERROR_RELOADING,
            ToastManager.Messages.PC_CONNECTION_SUCCESS,
            ToastManager.Messages.PC_CONNECTION_FAILED,
            ToastManager.Messages.PERMISSIONS_GRANTED,
            ToastManager.Messages.PERMISSIONS_DENIED,
            ToastManager.Messages.FEATURE_COMING_SOON,
            ToastManager.Messages.OPERATION_SUCCESSFUL,
            ToastManager.Messages.OPERATION_FAILED,
            ToastManager.Messages.EXPORT_FUNCTIONALITY_COMING_SOON
        )

        messages.forEach { message ->
            assertTrue("Message '$message' should be ASCII-only", isASCIIOnly(message))
            assertFalse("Message '$message' should not contain emojis", containsEmojis(message))
        }
    }

    @Test
    fun testPredefinedMessages_UseProperTags() {
        // USB messages should use [USB] tag
        assertTrue("USB message should use [USB] tag", 
            ToastManager.Messages.USB_DEVICE_DETECTED.contains("[USB]"))
        
        // Troubleshooting messages should use [TROUBLESHOOTING] tag
        assertTrue("Troubleshooting message should use [TROUBLESHOOTING] tag", 
            ToastManager.Messages.DEVICE_TROUBLESHOOTING.contains("[TROUBLESHOOTING]"))
        
        // Success messages in showSuccess should get [SUCCESS] prefix
        // This will be tested in integration tests with actual calls
    }

    @Test
    fun testPredefinedMessages_NotEmpty() {
        val messagesClass = ToastManager.Messages::class.java
        val fields = messagesClass.declaredFields
        
        fields.forEach { field ->
            if (field.type == String::class.java) {
                field.isAccessible = true
                val value = field.get(null) as String
                assertTrue("Message field ${field.name} should not be empty", value.isNotBlank())
            }
        }
    }

    @Test
    fun testASCIIEnforcement_ValidMessages() {
        val validMessages = listOf(
            "[SUCCESS] Operation completed",
            "[WARNING] Check configuration", 
            "[ERROR] Connection failed",
            "[INFO] System status update",
            "[USB] Device detected",
            "[TROUBLESHOOTING] Check connections"
        )

        validMessages.forEach { message ->
            assertTrue("Valid message '$message' should be ASCII-only", isASCIIOnly(message))
        }
    }

    @Test
    fun testASCIIEnforcement_InvalidMessages() {
        val invalidMessages = listOf(
            "✅ Success message",
            "⚠️ Warning message",
            "❌ Error message", 
            "🔧 Troubleshooting",
            "📱 USB device",
            "🎉 Celebration"
        )

        invalidMessages.forEach { message ->
            assertFalse("Invalid message '$message' should not be ASCII-only", isASCIIOnly(message))
            assertTrue("Invalid message '$message' should contain emojis", containsEmojis(message))
        }
    }

    @Test
    fun testTaggedMessages_PropertyFormat() {
        val taggedMessages = listOf(
            "[SUCCESS] Config updated",
            "[WARNING] Low battery",
            "[ERROR] Network timeout",
            "[INFO] Status update",
            "[USB] Device attached",
            "[TROUBLESHOOTING] Check settings"
        )

        taggedMessages.forEach { message ->
            assertTrue("Tagged message should start with a tag in brackets", 
                message.matches(Regex("^\\[[A-Z_]+\\].*")))
            assertTrue("Tagged message should be ASCII-only", isASCIIOnly(message))
        }
    }

    @Test
    fun testCommonCharacters_Allowed() {
        val allowedChars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789" +
                "[]()-_.,!?:; " + "\n\r\t"
        
        assertTrue("All common ASCII characters should be allowed", isASCIIOnly(allowedChars))
    }

    @Test
    fun testSpecialSymbols_NotAllowed() {
        val notAllowedChars = "✅❌⚠️🔧📱🎉🌡️📊" // Common emojis used in the app
        
        assertFalse("Emoji characters should not be ASCII-only", isASCIIOnly(notAllowedChars))
        assertTrue("Should detect emojis", containsEmojis(notAllowedChars))
    }

    @Test
    fun testExtendedASCII_NotAllowed() {
        val extendedASCII = "café résumé naïve" // Contains accented characters
        
        assertFalse("Extended ASCII should not be allowed", isASCIIOnly(extendedASCII))
    }

    /**
     * Helper function to check if string contains only ASCII characters (0-127)
     */
    private fun isASCIIOnly(text: String): Boolean {
        return text.all { it.code <= 127 }
    }

    /**
     * Helper function to detect common emoji patterns
     */
    private fun containsEmojis(text: String): Boolean {
        // Check for common emoji ranges and specific emojis used in the app
        val emojiPattern = Regex("[\\u2600-\\u27BF\\uD83C-\\uD83E\\uDD00-\\uDDFF]|[✅❌⚠️🔧📱🎉🌡️📊]")
        return emojiPattern.containsMatchIn(text)
    }

    @Test
    fun testMessageConsistency() {
        // Ensure that similar message types use consistent formatting
        val successMessages = listOf(
            ToastManager.Messages.CONFIG_RELOAD_SUCCESS,
            ToastManager.Messages.PC_CONNECTION_SUCCESS,
            ToastManager.Messages.OPERATION_SUCCESSFUL
        )

        val errorMessages = listOf(
            ToastManager.Messages.CONFIG_MANAGER_ERROR,
            ToastManager.Messages.CONFIG_ERROR_RELOADING,
            ToastManager.Messages.OPERATION_FAILED
        )

        // All success messages should be positive and clear
        successMessages.forEach { message ->
            assertTrue("Success message should contain positive language", 
                message.contains("success") || message.contains("successful"))
        }

        // All error messages should indicate problems clearly
        errorMessages.forEach { message ->
            assertTrue("Error message should contain error language", 
                message.contains("error") || message.contains("failed"))
        }
    }
}