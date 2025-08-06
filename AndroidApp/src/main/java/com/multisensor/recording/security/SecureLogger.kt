package com.multisensor.recording.security

import android.content.Context
import com.multisensor.recording.util.Logger
import dagger.hilt.android.qualifiers.ApplicationContext
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Secure logger wrapper that sanitizes sensitive information before logging.
 * Prevents PII and sensitive data from being written to log files.
 */
@Singleton
class SecureLogger @Inject constructor(
    @ApplicationContext private val context: Context,
    private val baseLogger: Logger,
    private val securityUtils: SecurityUtils
) {
    
    companion object {
        private val SENSITIVE_PATTERNS = listOf(
            // Authentication tokens and passwords
            Regex("(?i)(token|password|secret|key|auth)\\s*[:=]\\s*[\"']?([^\\s\"']{8,})[\"']?") { matchResult ->
                "${matchResult.groupValues[1]}=***"
            },
            
            // MAC addresses
            Regex("([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})") { "**:**:**:**:**:**" },
            
            // IP addresses (but preserve localhost)
            Regex("\\b(?!127\\.0\\.0\\.1|localhost)(?:[0-9]{1,3}\\.){3}[0-9]{1,3}\\b") { "***.***.***.***" },
            
            // Phone numbers (international format)
            Regex("\\+?[1-9]\\d{1,14}\\b") { "***-***-****" },
            
            // Email addresses
            Regex("\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b") { "***@***.***" },
            
            // Base64 encoded data (likely tokens or encrypted data)
            Regex("[A-Za-z0-9+/]{20,}={0,2}") { "***[base64]***" },
            
            // Hex strings that could be keys or hashes
            Regex("\\b[0-9A-Fa-f]{32,}\\b") { "***[hex]***" },
            
            // Device serial numbers (keeping only first and last 2 chars)
            Regex("\\bserial[\"'\\s]*[:=][\"'\\s]*([A-Za-z0-9]{2})([A-Za-z0-9]+)([A-Za-z0-9]{2})[\"'\\s]*") { matchResult ->
                "serial=${matchResult.groupValues[1]}***${matchResult.groupValues[3]}"
            },
            
            // Stack traces from sensitive packages (remove line numbers and method details)
            Regex("at\\s+(com\\.multisensor\\.recording\\.security\\.[^\\s]+)\\([^)]+\\)") { matchResult ->
                "at ${matchResult.groupValues[1].substringBeforeLast('.')}.**(***)"
            }
        )
    }
    
    fun verbose(message: String, throwable: Throwable? = null) {
        baseLogger.verbose(sanitizeMessage(message), sanitizeThrowable(throwable))
    }
    
    fun debug(message: String, throwable: Throwable? = null) {
        baseLogger.debug(sanitizeMessage(message), sanitizeThrowable(throwable))
    }
    
    fun info(message: String, throwable: Throwable? = null) {
        baseLogger.info(sanitizeMessage(message), sanitizeThrowable(throwable))
    }
    
    fun warning(message: String, throwable: Throwable? = null) {
        baseLogger.warning(sanitizeMessage(message), sanitizeThrowable(throwable))
    }
    
    fun error(message: String, throwable: Throwable? = null) {
        baseLogger.error(sanitizeMessage(message), sanitizeThrowable(throwable))
    }
    
    /**
     * Log security-related events with additional context
     */
    fun logSecurityEvent(event: SecurityEvent, details: String = "") {
        val sanitizedDetails = sanitizeMessage(details)
        val logMessage = "SECURITY EVENT: ${event.name} - $sanitizedDetails"
        
        when (event.severity) {
            SecurityEventSeverity.LOW -> info(logMessage)
            SecurityEventSeverity.MEDIUM -> warning(logMessage)
            SecurityEventSeverity.HIGH -> error(logMessage)
            SecurityEventSeverity.CRITICAL -> error(logMessage)
        }
    }
    
    /**
     * Log authentication events with sanitized information
     */
    fun logAuthEvent(event: AuthEvent, remoteAddress: String? = null, success: Boolean = false) {
        val sanitizedAddress = remoteAddress?.let { sanitizeMessage(it) } ?: "unknown"
        val status = if (success) "SUCCESS" else "FAILURE"
        val logMessage = "AUTH EVENT: ${event.name} from $sanitizedAddress - $status"
        
        if (success) {
            info(logMessage)
        } else {
            warning(logMessage)
        }
    }
    
    /**
     * Sanitize a message by removing or masking sensitive information
     */
    private fun sanitizeMessage(message: String): String {
        var sanitized = securityUtils.sanitizeForLogging(message)
        
        // Apply additional patterns specific to our application
        SENSITIVE_PATTERNS.forEach { (pattern, replacement) ->
            sanitized = when (replacement) {
                is String -> pattern.replace(sanitized, replacement)
                is (MatchResult) -> String -> pattern.replace(sanitized, replacement)
                else -> pattern.replace(sanitized, "***")
            }
        }
        
        return sanitized
    }
    
    /**
     * Sanitize throwable by removing sensitive information from stack traces
     */
    private fun sanitizeThrowable(throwable: Throwable?): Throwable? {
        if (throwable == null) return null
        
        // For security-related exceptions, create a sanitized version
        if (throwable.message?.contains("password", ignoreCase = true) == true ||
            throwable.message?.contains("token", ignoreCase = true) == true ||
            throwable.message?.contains("secret", ignoreCase = true) == true) {
            
            val sanitizedMessage = sanitizeMessage(throwable.message ?: "")
            return RuntimeException(sanitizedMessage, null) // Remove original stack trace
        }
        
        return throwable
    }
    
    /**
     * Log network communication events with sanitized data
     */
    fun logNetworkEvent(event: NetworkEvent, remoteAddress: String? = null, dataSize: Long = 0) {
        val sanitizedAddress = remoteAddress?.let { sanitizeMessage(it) } ?: "unknown"
        val logMessage = "NETWORK EVENT: ${event.name} with $sanitizedAddress, ${dataSize} bytes"
        
        when (event.severity) {
            NetworkEventSeverity.INFO -> info(logMessage)
            NetworkEventSeverity.WARNING -> warning(logMessage)
            NetworkEventSeverity.ERROR -> error(logMessage)
        }
    }
    
    /**
     * Log file operations with sanitized paths
     */
    fun logFileEvent(event: FileEvent, filePath: String, success: Boolean = true) {
        // Only log filename, not full path to avoid exposing directory structure
        val fileName = filePath.substringAfterLast('/')
        val status = if (success) "SUCCESS" else "FAILURE"
        val logMessage = "FILE EVENT: ${event.name} - $fileName - $status"
        
        if (success) {
            debug(logMessage)
        } else {
            warning(logMessage)
        }
    }
    
    // Delegate other methods to base logger
    fun getCurrentLogFilePath(): String? = baseLogger.getCurrentLogFilePath()
    fun getLogStatistics(): Logger.LogStatistics = baseLogger.getLogStatistics()
    fun logSystemInfo() = baseLogger.logSystemInfo()
    fun cleanup() = baseLogger.cleanup()
}

enum class SecurityEvent(val severity: SecurityEventSeverity) {
    ENCRYPTION_KEY_GENERATED(SecurityEventSeverity.LOW),
    AUTHENTICATION_TOKEN_GENERATED(SecurityEventSeverity.MEDIUM),
    INVALID_AUTHENTICATION_ATTEMPT(SecurityEventSeverity.HIGH),
    ENCRYPTION_FAILURE(SecurityEventSeverity.HIGH),
    CERTIFICATE_VALIDATION_FAILED(SecurityEventSeverity.CRITICAL),
    UNAUTHORIZED_ACCESS_ATTEMPT(SecurityEventSeverity.CRITICAL)
}

enum class SecurityEventSeverity {
    LOW, MEDIUM, HIGH, CRITICAL
}

enum class AuthEvent {
    AUTHENTICATION_STARTED,
    AUTHENTICATION_SUCCESS,
    AUTHENTICATION_FAILURE,
    TOKEN_VALIDATION_FAILED,
    CONNECTION_AUTHENTICATED,
    CONNECTION_UNAUTHENTICATED
}

enum class NetworkEvent(val severity: NetworkEventSeverity) {
    CONNECTION_ESTABLISHED(NetworkEventSeverity.INFO),
    CONNECTION_LOST(NetworkEventSeverity.WARNING),
    TLS_HANDSHAKE_SUCCESS(NetworkEventSeverity.INFO),
    TLS_HANDSHAKE_FAILED(NetworkEventSeverity.ERROR),
    DATA_TRANSMITTED(NetworkEventSeverity.INFO),
    DATA_RECEIVED(NetworkEventSeverity.INFO),
    CERTIFICATE_PINNING_FAILED(NetworkEventSeverity.ERROR)
}

enum class NetworkEventSeverity {
    INFO, WARNING, ERROR
}

enum class FileEvent {
    FILE_ENCRYPTED,
    FILE_DECRYPTED,
    FILE_DELETED,
    FILE_CREATED,
    FILE_ACCESS_DENIED,
    FILE_CORRUPTION_DETECTED
}