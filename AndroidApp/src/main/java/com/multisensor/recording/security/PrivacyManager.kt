package com.multisensor.recording.security

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import com.multisensor.recording.util.Logger
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.util.*
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Manages user privacy preferences, consent, and data anonymization features.
 * Implements GDPR compliance features and user privacy controls.
 */
@Singleton
class PrivacyManager @Inject constructor(
    @ApplicationContext private val context: Context,
    private val logger: Logger
) {
    
    companion object {
        private const val PREFS_FILE = "privacy_preferences"
        private const val KEY_CONSENT_GIVEN = "consent_given"
        private const val KEY_CONSENT_DATE = "consent_date"
        private const val KEY_CONSENT_VERSION = "consent_version"
        private const val KEY_DATA_ANONYMIZATION = "data_anonymization_enabled"
        private const val KEY_FACE_BLURRING = "face_blurring_enabled"
        private const val KEY_METADATA_STRIPPING = "metadata_stripping_enabled"
        private const val KEY_PARTICIPANT_ID = "participant_id"
        private const val KEY_STUDY_ID = "study_id"
        private const val KEY_DATA_RETENTION_DAYS = "data_retention_days"
        
        private const val CURRENT_CONSENT_VERSION = 1
        private const val DEFAULT_RETENTION_DAYS = 365
    }
    
    private val securePrefs: SharedPreferences by lazy {
        try {
            val masterKey = MasterKey.Builder(context)
                .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
                .build()
                
            EncryptedSharedPreferences.create(
                context,
                PREFS_FILE,
                masterKey,
                EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
                EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
            )
        } catch (e: Exception) {
            logger.error("Failed to create encrypted preferences, falling back to regular preferences", e)
            context.getSharedPreferences(PREFS_FILE, Context.MODE_PRIVATE)
        }
    }
    
    /**
     * Check if user has given valid consent
     */
    fun hasValidConsent(): Boolean {
        val consentGiven = securePrefs.getBoolean(KEY_CONSENT_GIVEN, false)
        val consentVersion = securePrefs.getInt(KEY_CONSENT_VERSION, 0)
        
        return consentGiven && consentVersion >= CURRENT_CONSENT_VERSION
    }
    
    /**
     * Record user consent
     */
    fun recordConsent(participantId: String? = null, studyId: String? = null) {
        securePrefs.edit()
            .putBoolean(KEY_CONSENT_GIVEN, true)
            .putLong(KEY_CONSENT_DATE, System.currentTimeMillis())
            .putInt(KEY_CONSENT_VERSION, CURRENT_CONSENT_VERSION)
            .apply {
                participantId?.let { putString(KEY_PARTICIPANT_ID, it) }
                studyId?.let { putString(KEY_STUDY_ID, it) }
            }
            .apply()
        
        logger.info("User consent recorded for study: ${studyId ?: "unknown"}")
    }
    
    /**
     * Withdraw consent and mark for data deletion
     */
    fun withdrawConsent(): Boolean {
        return try {
            securePrefs.edit()
                .putBoolean(KEY_CONSENT_GIVEN, false)
                .putLong("consent_withdrawn_date", System.currentTimeMillis())
                .apply()
            
            logger.info("User consent withdrawn - data should be deleted")
            true
        } catch (e: Exception) {
            logger.error("Failed to withdraw consent", e)
            false
        }
    }
    
    /**
     * Get consent information
     */
    fun getConsentInfo(): ConsentInfo {
        return ConsentInfo(
            consentGiven = securePrefs.getBoolean(KEY_CONSENT_GIVEN, false),
            consentDate = securePrefs.getLong(KEY_CONSENT_DATE, 0),
            consentVersion = securePrefs.getInt(KEY_CONSENT_VERSION, 0),
            participantId = securePrefs.getString(KEY_PARTICIPANT_ID, null),
            studyId = securePrefs.getString(KEY_STUDY_ID, null)
        )
    }
    
    /**
     * Configure data anonymization options
     */
    fun configureAnonymization(
        enableDataAnonymization: Boolean,
        enableFaceBlurring: Boolean,
        enableMetadataStripping: Boolean
    ) {
        securePrefs.edit()
            .putBoolean(KEY_DATA_ANONYMIZATION, enableDataAnonymization)
            .putBoolean(KEY_FACE_BLURRING, enableFaceBlurring)
            .putBoolean(KEY_METADATA_STRIPPING, enableMetadataStripping)
            .apply()
        
        logger.info("Data anonymization configured: anonymize=$enableDataAnonymization, blur=$enableFaceBlurring, strip=$enableMetadataStripping")
    }
    
    /**
     * Get current anonymization settings
     */
    fun getAnonymizationSettings(): AnonymizationSettings {
        return AnonymizationSettings(
            dataAnonymizationEnabled = securePrefs.getBoolean(KEY_DATA_ANONYMIZATION, false),
            faceBlurringEnabled = securePrefs.getBoolean(KEY_FACE_BLURRING, false),
            metadataStrippingEnabled = securePrefs.getBoolean(KEY_METADATA_STRIPPING, true)
        )
    }
    
    /**
     * Set data retention period
     */
    fun setDataRetentionPeriod(days: Int) {
        securePrefs.edit()
            .putInt(KEY_DATA_RETENTION_DAYS, days)
            .apply()
        
        logger.info("Data retention period set to $days days")
    }
    
    /**
     * Get data retention period
     */
    fun getDataRetentionDays(): Int {
        return securePrefs.getInt(KEY_DATA_RETENTION_DAYS, DEFAULT_RETENTION_DAYS)
    }
    
    /**
     * Generate anonymous participant ID
     */
    fun generateAnonymousParticipantId(): String {
        val uuid = UUID.randomUUID().toString()
        val anonymousId = "ANON_${uuid.substring(0, 8).uppercase()}"
        
        securePrefs.edit()
            .putString(KEY_PARTICIPANT_ID, anonymousId)
            .apply()
        
        return anonymousId
    }
    
    /**
     * Get current participant ID (anonymous or provided)
     */
    fun getParticipantId(): String? {
        return securePrefs.getString(KEY_PARTICIPANT_ID, null)
    }
    
    /**
     * Check if data should be deleted based on retention policy
     */
    fun shouldDeleteData(dataTimestamp: Long): Boolean {
        val retentionPeriodMs = getDataRetentionDays() * 24 * 60 * 60 * 1000L
        val currentTime = System.currentTimeMillis()
        
        return (currentTime - dataTimestamp) > retentionPeriodMs
    }
    
    /**
     * Anonymize metadata by removing or replacing identifying information
     */
    suspend fun anonymizeMetadata(metadata: Map<String, Any>): Map<String, Any> = withContext(Dispatchers.Default) {
        val anonymizedMetadata = metadata.toMutableMap()
        
        if (getAnonymizationSettings().metadataStrippingEnabled) {
            // Remove potentially identifying metadata
            val keysToRemove = listOf(
                "device_id", "serial_number", "mac_address", "imei",
                "phone_number", "email", "user_name", "device_name",
                "network_ssid", "ip_address", "location", "gps"
            )
            
            keysToRemove.forEach { key ->
                anonymizedMetadata.remove(key)
            }
            
            // Replace with anonymous versions
            anonymizedMetadata["participant_id"] = getParticipantId() ?: generateAnonymousParticipantId()
            anonymizedMetadata["session_id"] = "SESSION_${UUID.randomUUID().toString().substring(0, 8)}"
            anonymizedMetadata["device_type"] = android.os.Build.MODEL.replace(Regex("[0-9]+"), "X")
        }
        
        anonymizedMetadata.toMap()
    }
    
    /**
     * Create a privacy report for GDPR compliance
     */
    suspend fun generatePrivacyReport(): PrivacyReport = withContext(Dispatchers.Default) {
        val consentInfo = getConsentInfo()
        val anonymizationSettings = getAnonymizationSettings()
        
        PrivacyReport(
            consentInfo = consentInfo,
            anonymizationSettings = anonymizationSettings,
            dataRetentionDays = getDataRetentionDays(),
            reportGeneratedAt = System.currentTimeMillis(),
            dataCollectionPurpose = "Multi-sensor physiological research data collection",
            dataTypes = listOf(
                "Video recordings (RGB)",
                "Thermal camera data", 
                "Shimmer sensor data (GSR, accelerometer, etc.)",
                "Device metadata",
                "Session timestamps"
            ),
            dataProcessingBasis = "Research consent",
            dataStorageLocation = "Local device storage (encrypted)",
            thirdPartySharing = "None"
        )
    }
    
    /**
     * Clear all privacy-related data (for GDPR deletion requests)
     */
    suspend fun clearAllPrivacyData(): Boolean = withContext(Dispatchers.IO) {
        return@withContext try {
            securePrefs.edit().clear().apply()
            logger.info("All privacy data cleared successfully")
            true
        } catch (e: Exception) {
            logger.error("Failed to clear privacy data", e)
            false
        }
    }
    
    data class ConsentInfo(
        val consentGiven: Boolean,
        val consentDate: Long,
        val consentVersion: Int,
        val participantId: String?,
        val studyId: String?
    )
    
    data class AnonymizationSettings(
        val dataAnonymizationEnabled: Boolean,
        val faceBlurringEnabled: Boolean,
        val metadataStrippingEnabled: Boolean
    )
    
    data class PrivacyReport(
        val consentInfo: ConsentInfo,
        val anonymizationSettings: AnonymizationSettings,
        val dataRetentionDays: Int,
        val reportGeneratedAt: Long,
        val dataCollectionPurpose: String,
        val dataTypes: List<String>,
        val dataProcessingBasis: String,
        val dataStorageLocation: String,
        val thirdPartySharing: String
    )
}