package com.multisensor.recording.ui

import android.content.Context
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.test.core.app.ApplicationProvider
import com.multisensor.recording.R
import com.multisensor.recording.network.NetworkConfiguration
import com.multisensor.recording.network.ServerConfiguration
import com.multisensor.recording.util.Logger
import dagger.hilt.android.testing.HiltAndroidRule
import dagger.hilt.android.testing.HiltAndroidTest
import dagger.hilt.android.testing.HiltTestApplication
import io.mockk.*
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.Robolectric
import org.robolectric.RobolectricTestRunner
import org.robolectric.Shadows.shadowOf
import org.robolectric.annotation.Config
import org.robolectric.shadows.ShadowToast
import javax.inject.Inject

/**
 * Comprehensive unit tests for NetworkConfigActivity
 * Tests all functionality including validation, saving, and error handling
 * Ensures 100% test coverage as required by guidelines
 */
@HiltAndroidTest
@RunWith(RobolectricTestRunner::class)
@Config(
    application = HiltTestApplication::class,
    manifest = Config.NONE,
    sdk = [28],
)
class NetworkConfigActivityTest {
    @get:Rule
    var hiltRule = HiltAndroidRule(this)

    @Inject
    lateinit var networkConfiguration: NetworkConfiguration

    @Inject
    lateinit var logger: Logger

    private lateinit var activity: NetworkConfigActivity
    private lateinit var mockNetworkConfiguration: NetworkConfiguration
    private lateinit var mockLogger: Logger

    @Before
    fun setup() {
        hiltRule.inject()

        // Create mocks
        mockNetworkConfiguration = mockk(relaxed = true)
        mockLogger = mockk(relaxed = true)

        // Setup default mock behavior
        every { mockNetworkConfiguration.getServerConfiguration() } returns
            ServerConfiguration(
                serverIp = "192.168.1.100",
                legacyPort = 8080,
                jsonPort = 9000,
            )
        every { mockNetworkConfiguration.isValidIpAddress(any()) } returns true
        every { mockNetworkConfiguration.isValidPort(any()) } returns true
        every { mockNetworkConfiguration.getConfigurationSummary() } returns "NetworkConfig[IP=192.168.1.100, Legacy=8080, JSON=9000]"

        // Create activity
        activity = Robolectric.buildActivity(NetworkConfigActivity::class.java).create().get()

        // Inject mocks using reflection
        val networkConfigField = NetworkConfigActivity::class.java.getDeclaredField("networkConfiguration")
        networkConfigField.isAccessible = true
        networkConfigField.set(activity, mockNetworkConfiguration)

        val loggerField = NetworkConfigActivity::class.java.getDeclaredField("logger")
        loggerField.isAccessible = true
        loggerField.set(activity, mockLogger)
    }

    @After
    fun tearDown() {
        clearAllMocks()
    }

    @Test
    fun `onCreate should initialize views and load configuration`() {
        // [DEBUG_LOG] Testing activity creation and initialization
        println("[DEBUG_LOG] Testing NetworkConfigActivity onCreate initialization")

        // Verify views are initialized
        val serverIpEditText = activity.findViewById<EditText>(R.id.edit_server_ip)
        val legacyPortEditText = activity.findViewById<EditText>(R.id.edit_legacy_port)
        val jsonPortEditText = activity.findViewById<EditText>(R.id.edit_json_port)
        val saveButton = activity.findViewById<Button>(R.id.btn_save_config)
        val resetButton = activity.findViewById<Button>(R.id.btn_reset_config)

        // Verify views exist
        assertTrue("Server IP EditText should be initialized", serverIpEditText != null)
        assertTrue("Legacy Port EditText should be initialized", legacyPortEditText != null)
        assertTrue("JSON Port EditText should be initialized", jsonPortEditText != null)
        assertTrue("Save Button should be initialized", saveButton != null)
        assertTrue("Reset Button should be initialized", resetButton != null)

        // Verify configuration is loaded
        verify { mockNetworkConfiguration.getServerConfiguration() }
        verify { mockLogger.info("NetworkConfigActivity created") }

        println("[DEBUG_LOG] Activity initialization test passed")
    }

    @Test
    fun `loadCurrentConfiguration should populate fields with current values`() {
        // [DEBUG_LOG] Testing configuration loading
        println("[DEBUG_LOG] Testing loadCurrentConfiguration functionality")

        val serverIpEditText = activity.findViewById<EditText>(R.id.edit_server_ip)
        val legacyPortEditText = activity.findViewById<EditText>(R.id.edit_legacy_port)
        val jsonPortEditText = activity.findViewById<EditText>(R.id.edit_json_port)

        // Verify fields are populated with mock values
        assertEquals("192.168.1.100", serverIpEditText.text.toString())
        assertEquals("8080", legacyPortEditText.text.toString())
        assertEquals("9000", jsonPortEditText.text.toString())

        verify { mockLogger.debug(any()) }

        println("[DEBUG_LOG] Configuration loading test passed")
    }

    @Test
    fun `saveConfiguration should validate and save valid configuration`() {
        // [DEBUG_LOG] Testing valid configuration saving
        println("[DEBUG_LOG] Testing saveConfiguration with valid inputs")

        val serverIpEditText = activity.findViewById<EditText>(R.id.edit_server_ip)
        val legacyPortEditText = activity.findViewById<EditText>(R.id.edit_legacy_port)
        val jsonPortEditText = activity.findViewById<EditText>(R.id.edit_json_port)
        val saveButton = activity.findViewById<Button>(R.id.btn_save_config)

        // Set valid values
        serverIpEditText.setText("192.168.1.200")
        legacyPortEditText.setText("8081")
        jsonPortEditText.setText("9001")

        // Mock validation to return true
        every { mockNetworkConfiguration.isValidIpAddress("192.168.1.200") } returns true
        every { mockNetworkConfiguration.isValidPort(8081) } returns true
        every { mockNetworkConfiguration.isValidPort(9001) } returns true

        // Click save button
        saveButton.performClick()

        // Verify configuration is saved
        verify { mockNetworkConfiguration.setServerIp("192.168.1.200") }
        verify { mockNetworkConfiguration.setLegacyPort(8081) }
        verify { mockNetworkConfiguration.setJsonPort(9001) }
        verify { mockLogger.info(any()) }

        // Verify success toast
        assertEquals("Configuration saved successfully", ShadowToast.getTextOfLatestToast())

        println("[DEBUG_LOG] Valid configuration saving test passed")
    }

    @Test
    fun `saveConfiguration should reject empty server IP`() {
        // [DEBUG_LOG] Testing empty server IP validation
        println("[DEBUG_LOG] Testing saveConfiguration with empty server IP")

        val serverIpEditText = activity.findViewById<EditText>(R.id.edit_server_ip)
        val saveButton = activity.findViewById<Button>(R.id.btn_save_config)

        // Set empty IP
        serverIpEditText.setText("")

        // Click save button
        saveButton.performClick()

        // Verify error toast
        assertEquals("Server IP cannot be empty", ShadowToast.getTextOfLatestToast())

        // Verify configuration is not saved
        verify(exactly = 0) { mockNetworkConfiguration.setServerIp(any()) }

        println("[DEBUG_LOG] Empty server IP validation test passed")
    }

    @Test
    fun `saveConfiguration should reject invalid IP address`() {
        // [DEBUG_LOG] Testing invalid IP address validation
        println("[DEBUG_LOG] Testing saveConfiguration with invalid IP address")

        val serverIpEditText = activity.findViewById<EditText>(R.id.edit_server_ip)
        val saveButton = activity.findViewById<Button>(R.id.btn_save_config)

        // Set invalid IP
        serverIpEditText.setText("invalid.ip.address")

        // Mock validation to return false
        every { mockNetworkConfiguration.isValidIpAddress("invalid.ip.address") } returns false

        // Click save button
        saveButton.performClick()

        // Verify error toast
        assertEquals("Invalid IP address format", ShadowToast.getTextOfLatestToast())

        // Verify configuration is not saved
        verify(exactly = 0) { mockNetworkConfiguration.setServerIp(any()) }

        println("[DEBUG_LOG] Invalid IP address validation test passed")
    }

    @Test
    fun `saveConfiguration should reject invalid port numbers`() {
        // [DEBUG_LOG] Testing invalid port number validation
        println("[DEBUG_LOG] Testing saveConfiguration with invalid port numbers")

        val legacyPortEditText = activity.findViewById<EditText>(R.id.edit_legacy_port)
        val saveButton = activity.findViewById<Button>(R.id.btn_save_config)

        // Set invalid port
        legacyPortEditText.setText("99999")

        // Mock validation to return false for invalid port
        every { mockNetworkConfiguration.isValidPort(99999) } returns false

        // Click save button
        saveButton.performClick()

        // Verify error toast
        assertEquals("Legacy port must be between 1024 and 65535", ShadowToast.getTextOfLatestToast())

        println("[DEBUG_LOG] Invalid port number validation test passed")
    }

    @Test
    fun `saveConfiguration should reject same port numbers`() {
        // [DEBUG_LOG] Testing duplicate port number validation
        println("[DEBUG_LOG] Testing saveConfiguration with duplicate port numbers")

        val legacyPortEditText = activity.findViewById<EditText>(R.id.edit_legacy_port)
        val jsonPortEditText = activity.findViewById<EditText>(R.id.edit_json_port)
        val saveButton = activity.findViewById<Button>(R.id.btn_save_config)

        // Set same port numbers
        legacyPortEditText.setText("8080")
        jsonPortEditText.setText("8080")

        // Mock validation to return true for individual ports
        every { mockNetworkConfiguration.isValidPort(8080) } returns true

        // Click save button
        saveButton.performClick()

        // Verify error toast
        assertEquals("Legacy and JSON ports must be different", ShadowToast.getTextOfLatestToast())

        println("[DEBUG_LOG] Duplicate port number validation test passed")
    }

    @Test
    fun `resetToDefaults should reset configuration and reload fields`() {
        // [DEBUG_LOG] Testing reset to defaults functionality
        println("[DEBUG_LOG] Testing resetToDefaults functionality")

        val resetButton = activity.findViewById<Button>(R.id.btn_reset_config)

        // Click reset button
        resetButton.performClick()

        // Verify reset is called
        verify { mockNetworkConfiguration.resetToDefaults() }
        verify { mockNetworkConfiguration.getServerConfiguration() }
        verify { mockLogger.info("Network configuration reset to defaults") }

        // Verify success toast
        assertEquals("Configuration reset to defaults", ShadowToast.getTextOfLatestToast())

        println("[DEBUG_LOG] Reset to defaults test passed")
    }

    @Test
    fun `saveConfiguration should handle exceptions gracefully`() {
        // [DEBUG_LOG] Testing exception handling in saveConfiguration
        println("[DEBUG_LOG] Testing saveConfiguration exception handling")

        val saveButton = activity.findViewById<Button>(R.id.btn_save_config)

        // Mock exception during save
        every { mockNetworkConfiguration.setServerIp(any()) } throws RuntimeException("Test exception")

        // Click save button
        saveButton.performClick()

        // Verify error is logged and toast is shown
        verify { mockLogger.error("Failed to save network configuration", any()) }
        assertTrue("Toast should contain error message", ShadowToast.getTextOfLatestToast().contains("Failed to save configuration"))

        println("[DEBUG_LOG] Exception handling test passed")
    }

    @Test
    fun `resetToDefaults should handle exceptions gracefully`() {
        // [DEBUG_LOG] Testing exception handling in resetToDefaults
        println("[DEBUG_LOG] Testing resetToDefaults exception handling")

        val resetButton = activity.findViewById<Button>(R.id.btn_reset_config)

        // Mock exception during reset
        every { mockNetworkConfiguration.resetToDefaults() } throws RuntimeException("Test exception")

        // Click reset button
        resetButton.performClick()

        // Verify error is logged and toast is shown
        verify { mockLogger.error("Failed to reset network configuration", any()) }
        assertTrue("Toast should contain error message", ShadowToast.getTextOfLatestToast().contains("Failed to reset configuration"))

        println("[DEBUG_LOG] Reset exception handling test passed")
    }
}
