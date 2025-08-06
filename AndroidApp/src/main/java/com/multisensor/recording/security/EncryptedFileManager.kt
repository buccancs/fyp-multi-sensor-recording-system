package com.multisensor.recording.security

import android.content.Context
import com.multisensor.recording.util.Logger
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.File
import java.io.FileInputStream
import java.io.FileOutputStream
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Manages encrypted file storage for sensitive recording data.
 * Provides transparent encryption/decryption for video files, sensor data, and metadata.
 */
@Singleton
class EncryptedFileManager @Inject constructor(
    @ApplicationContext private val context: Context,
    private val securityUtils: SecurityUtils,
    private val logger: Logger
) {
    
    companion object {
        private const val ENCRYPTED_EXTENSION = ".enc"
        private const val TEMP_EXTENSION = ".tmp"
    }
    
    init {
        // Initialize encryption on startup
        if (!securityUtils.initializeEncryptionKey()) {
            logger.error("Failed to initialize encryption for file storage")
        }
    }
    
    /**
     * Save data to an encrypted file
     */
    suspend fun saveEncryptedFile(data: ByteArray, file: File): Boolean = withContext(Dispatchers.IO) {
        return@withContext try {
            val tempFile = File(file.parentFile, file.name + TEMP_EXTENSION)
            val encryptedFile = File(file.parentFile, file.name + ENCRYPTED_EXTENSION)
            
            // Write to temp file first
            tempFile.writeBytes(data)
            
            // Encrypt the temp file
            val success = securityUtils.encryptFile(tempFile, encryptedFile)
            
            // Clean up temp file
            tempFile.delete()
            
            if (success) {
                logger.debug("File encrypted and saved: ${file.name}")
                // Remove unencrypted original if it exists
                file.delete()
            } else {
                logger.error("Failed to encrypt file: ${file.name}")
                // Clean up encrypted file if encryption failed
                encryptedFile.delete()
            }
            
            success
        } catch (e: Exception) {
            logger.error("Error saving encrypted file: ${file.name}", e)
            false
        }
    }
    
    /**
     * Read data from an encrypted file
     */
    suspend fun readEncryptedFile(file: File): ByteArray? = withContext(Dispatchers.IO) {
        return@withContext try {
            val encryptedFile = File(file.parentFile, file.name + ENCRYPTED_EXTENSION)
            
            if (!encryptedFile.exists()) {
                logger.warning("Encrypted file does not exist: ${encryptedFile.name}")
                return@withContext null
            }
            
            val tempFile = File(file.parentFile, file.name + TEMP_EXTENSION)
            
            // Decrypt to temp file
            val success = securityUtils.decryptFile(encryptedFile, tempFile)
            
            if (success && tempFile.exists()) {
                val data = tempFile.readBytes()
                tempFile.delete() // Clean up temp file
                logger.debug("File decrypted and read: ${file.name}")
                data
            } else {
                logger.error("Failed to decrypt file: ${file.name}")
                tempFile.delete() // Clean up temp file if it exists
                null
            }
        } catch (e: Exception) {
            logger.error("Error reading encrypted file: ${file.name}", e)
            null
        }
    }
    
    /**
     * Encrypt an existing file in place
     */
    suspend fun encryptExistingFile(file: File): Boolean = withContext(Dispatchers.IO) {
        return@withContext try {
            if (!file.exists()) {
                logger.warning("File does not exist for encryption: ${file.name}")
                return@withContext false
            }
            
            val encryptedFile = File(file.parentFile, file.name + ENCRYPTED_EXTENSION)
            
            // Don't re-encrypt if already encrypted
            if (encryptedFile.exists()) {
                logger.debug("File already encrypted: ${file.name}")
                return@withContext true
            }
            
            val success = securityUtils.encryptFile(file, encryptedFile)
            
            if (success) {
                // Remove original unencrypted file
                file.delete()
                logger.info("File encrypted in place: ${file.name}")
            } else {
                logger.error("Failed to encrypt existing file: ${file.name}")
            }
            
            success
        } catch (e: Exception) {
            logger.error("Error encrypting existing file: ${file.name}", e)
            false
        }
    }
    
    /**
     * Decrypt an encrypted file to its original location
     */
    suspend fun decryptFileToOriginal(file: File): Boolean = withContext(Dispatchers.IO) {
        return@withContext try {
            val encryptedFile = File(file.parentFile, file.name + ENCRYPTED_EXTENSION)
            
            if (!encryptedFile.exists()) {
                logger.warning("Encrypted file does not exist: ${encryptedFile.name}")
                return@withContext false
            }
            
            val success = securityUtils.decryptFile(encryptedFile, file)
            
            if (success) {
                logger.info("File decrypted to original location: ${file.name}")
            } else {
                logger.error("Failed to decrypt file to original location: ${file.name}")
            }
            
            success
        } catch (e: Exception) {
            logger.error("Error decrypting file to original location: ${file.name}", e)
            false
        }
    }
    
    /**
     * Check if a file exists in encrypted form
     */
    fun isFileEncrypted(file: File): Boolean {
        val encryptedFile = File(file.parentFile, file.name + ENCRYPTED_EXTENSION)
        return encryptedFile.exists()
    }
    
    /**
     * Get the encrypted version of a file
     */
    fun getEncryptedFile(file: File): File {
        return File(file.parentFile, file.name + ENCRYPTED_EXTENSION)
    }
    
    /**
     * Secure delete - overwrite file data before deletion
     */
    suspend fun secureDelete(file: File): Boolean = withContext(Dispatchers.IO) {
        return@withContext try {
            if (!file.exists()) {
                return@withContext true
            }
            
            // Overwrite file with random data
            val fileSize = file.length()
            val randomData = ByteArray(fileSize.toInt())
            java.security.SecureRandom().nextBytes(randomData)
            
            FileOutputStream(file).use { fos ->
                fos.write(randomData)
                fos.flush()
                fos.fd.sync() // Force write to disk
            }
            
            // Delete the file
            val deleted = file.delete()
            
            if (deleted) {
                logger.debug("File securely deleted: ${file.name}")
            } else {
                logger.warning("Failed to delete file after overwrite: ${file.name}")
            }
            
            deleted
        } catch (e: Exception) {
            logger.error("Error securely deleting file: ${file.name}", e)
            false
        }
    }
    
    /**
     * Clean up all temporary files
     */
    suspend fun cleanupTempFiles(directory: File) = withContext(Dispatchers.IO) {
        try {
            directory.listFiles { _, name ->
                name.endsWith(TEMP_EXTENSION)
            }?.forEach { tempFile ->
                tempFile.delete()
                logger.debug("Cleaned up temp file: ${tempFile.name}")
            }
        } catch (e: Exception) {
            logger.error("Error cleaning up temp files", e)
        }
    }
    
    /**
     * Encrypt all files in a directory
     */
    suspend fun encryptDirectory(directory: File, fileExtensions: Set<String> = setOf("mp4", "json", "csv")): Int = withContext(Dispatchers.IO) {
        var encryptedCount = 0
        
        try {
            directory.listFiles { _, name ->
                fileExtensions.any { ext -> name.endsWith(".$ext", ignoreCase = true) }
            }?.forEach { file ->
                if (encryptExistingFile(file)) {
                    encryptedCount++
                }
            }
            
            logger.info("Encrypted $encryptedCount files in directory: ${directory.name}")
        } catch (e: Exception) {
            logger.error("Error encrypting directory: ${directory.name}", e)
        }
        
        encryptedCount
    }
    
    /**
     * Get storage statistics
     */
    fun getStorageStats(directory: File): StorageStats {
        var totalFiles = 0
        var encryptedFiles = 0
        var totalSize = 0L
        var encryptedSize = 0L
        
        try {
            directory.walkTopDown().forEach { file ->
                if (file.isFile) {
                    totalFiles++
                    totalSize += file.length()
                    
                    if (file.name.endsWith(ENCRYPTED_EXTENSION)) {
                        encryptedFiles++
                        encryptedSize += file.length()
                    }
                }
            }
        } catch (e: Exception) {
            logger.error("Error calculating storage stats", e)
        }
        
        return StorageStats(totalFiles, encryptedFiles, totalSize, encryptedSize)
    }
    
    data class StorageStats(
        val totalFiles: Int,
        val encryptedFiles: Int,
        val totalSize: Long,
        val encryptedSize: Long
    ) {
        val encryptionPercentage: Float = 
            if (totalFiles > 0) (encryptedFiles.toFloat() / totalFiles) * 100f else 0f
    }
}