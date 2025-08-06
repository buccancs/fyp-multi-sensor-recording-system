package com.multisensor.recording.security

import android.content.Context
import androidx.test.core.app.ApplicationProvider
import com.multisensor.recording.util.Logger
import io.mockk.mockk
import kotlinx.coroutines.runBlocking
import org.junit.Test
import org.junit.Assert.*
import org.junit.Before
import java.io.File

/**
 * Security features unit tests
 */
class SecurityTest {
    
    private lateinit var context: Context
    private lateinit var logger: Logger
    private lateinit var securityUtils: SecurityUtils
    private lateinit var encryptedFileManager: EncryptedFileManager
    private lateinit var privacyManager: PrivacyManager
    
    @Before
    fun setup() {
        context = ApplicationProvider.getApplicationContext()
        logger = mockk(relaxed = true)
        securityUtils = SecurityUtils(context, logger)
        encryptedFileManager = EncryptedFileManager(context, securityUtils, logger)
        privacyManager = PrivacyManager(context, logger)
    }
    
    @Test
    fun testEncryptionKeyInitialization() {
        // Test that encryption key can be initialized
        val result = securityUtils.initializeEncryptionKey()
        assertTrue("Encryption key should be initialized successfully", result)
    }
    
    @Test
    fun testDataEncryptionDecryption() {
        // Setup encryption key
        securityUtils.initializeEncryptionKey()
        
        // Test data
        val originalData = "This is sensitive test data that should be encrypted"
        val dataBytes = originalData.toByteArray()
        
        // Encrypt
        val encryptedData = securityUtils.encryptData(dataBytes)
        assertNotNull("Encrypted data should not be null", encryptedData)
        assertFalse("Encrypted data should not be empty", encryptedData!!.data.isEmpty())
        assertFalse("IV should not be empty", encryptedData.iv.isEmpty())
        
        // Decrypt
        val decryptedData = securityUtils.decryptData(encryptedData)
        assertNotNull("Decrypted data should not be null", decryptedData)
        
        val decryptedString = String(decryptedData!!)
        assertEquals("Decrypted data should match original", originalData, decryptedString)
    }
    
    @Test
    fun testAuthTokenGeneration() {
        val token = securityUtils.generateAuthToken()
        
        assertNotNull("Token should not be null", token)
        assertTrue("Token should be at least 32 characters", token.length >= 32)
        assertTrue("Token should be valid format", securityUtils.validateAuthToken(token))
    }
    
    @Test
    fun testAuthTokenValidation() {
        // Valid tokens
        val validToken = securityUtils.generateAuthToken()
        assertTrue("Generated token should be valid", securityUtils.validateAuthToken(validToken))
        
        // Invalid tokens
        assertFalse("Empty token should be invalid", securityUtils.validateAuthToken(""))
        assertFalse("Short token should be invalid", securityUtils.validateAuthToken("short"))
        assertFalse("Invalid format should be invalid", securityUtils.validateAuthToken("invalid!@#$%"))
    }
    
    @Test
    fun testFileEncryption() = runBlocking {
        // Setup
        securityUtils.initializeEncryptionKey()
        
        val testContent = "Test file content for encryption"
        val tempDir = File(context.cacheDir, "test_encryption")
        tempDir.mkdirs()
        
        val originalFile = File(tempDir, "test.txt")
        originalFile.writeText(testContent)
        
        // Encrypt file
        val success = encryptedFileManager.encryptExistingFile(originalFile)
        assertTrue("File encryption should succeed", success)
        
        // Check encrypted file exists
        val encryptedFile = encryptedFileManager.getEncryptedFile(originalFile)
        assertTrue("Encrypted file should exist", encryptedFile.exists())
        assertFalse("Original file should be deleted", originalFile.exists())
        
        // Decrypt file
        val decryptSuccess = encryptedFileManager.decryptFileToOriginal(originalFile)
        assertTrue("File decryption should succeed", decryptSuccess)
        assertTrue("Original file should be restored", originalFile.exists())
        
        val decryptedContent = originalFile.readText()
        assertEquals("Decrypted content should match original", testContent, decryptedContent)
        
        // Cleanup
        tempDir.deleteRecursively()
    }
    
    @Test
    fun testPrivacyManagerConsent() {
        // Initially no consent
        assertFalse("Should not have consent initially", privacyManager.hasValidConsent())
        
        // Record consent
        privacyManager.recordConsent("TEST_PARTICIPANT", "TEST_STUDY")
        assertTrue("Should have consent after recording", privacyManager.hasValidConsent())
        
        // Get consent info
        val consentInfo = privacyManager.getConsentInfo()
        assertEquals("Participant ID should match", "TEST_PARTICIPANT", consentInfo.participantId)
        assertEquals("Study ID should match", "TEST_STUDY", consentInfo.studyId)
        assertTrue("Consent should be given", consentInfo.consentGiven)
        
        // Withdraw consent
        privacyManager.withdrawConsent()
        assertFalse("Should not have consent after withdrawal", privacyManager.hasValidConsent())
    }
    
    @Test
    fun testDataAnonymization() = runBlocking {
        val originalMetadata = mapOf(
            "device_id" to "DEVICE123",
            "user_name" to "John Doe",
            "session_id" to "SESSION456",
            "ip_address" to "192.168.1.100",
            "measurement" to "heart_rate",
            "value" to 75.0
        )
        
        // Enable metadata stripping
        privacyManager.configureAnonymization(
            enableDataAnonymization = true,
            enableFaceBlurring = false,
            enableMetadataStripping = true
        )
        
        val anonymizedMetadata = privacyManager.anonymizeMetadata(originalMetadata)
        
        // Check that identifying information is removed
        assertFalse("Device ID should be removed", anonymizedMetadata.containsKey("device_id"))
        assertFalse("User name should be removed", anonymizedMetadata.containsKey("user_name"))
        assertFalse("IP address should be removed", anonymizedMetadata.containsKey("ip_address"))
        
        // Check that measurement data is preserved
        assertTrue("Measurement should be preserved", anonymizedMetadata.containsKey("measurement"))
        assertTrue("Value should be preserved", anonymizedMetadata.containsKey("value"))
        
        // Check that anonymous identifiers are added
        assertTrue("Participant ID should be added", anonymizedMetadata.containsKey("participant_id"))
        assertTrue("Session ID should be added", anonymizedMetadata.containsKey("session_id"))
    }
    
    @Test
    fun testSecureLogging() {
        val secureLogger = SecureLogger(context, logger, securityUtils)
        
        // Test messages with sensitive data
        val sensitiveMessage = "User token: abc123def456ghi789 connected from 192.168.1.100"
        
        // This should not throw and should sanitize the message internally
        secureLogger.info(sensitiveMessage)
        secureLogger.warning("Authentication failed for token: secretToken123")
        secureLogger.error("Database error for user john.doe@email.com")
        
        // Test security event logging
        secureLogger.logSecurityEvent(SecurityEvent.AUTHENTICATION_TOKEN_GENERATED, "Generated for user session")
        secureLogger.logAuthEvent(AuthEvent.AUTHENTICATION_SUCCESS, "192.168.1.100", true)
    }
}