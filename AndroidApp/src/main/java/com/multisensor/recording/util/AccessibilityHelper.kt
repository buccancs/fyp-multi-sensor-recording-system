package com.multisensor.recording.util

import android.content.Context
import android.view.View
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityManager
import androidx.core.view.ViewCompat
import androidx.core.view.accessibility.AccessibilityNodeInfoCompat
import androidx.core.view.accessibility.AccessibilityViewCommand
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Accessibility helper for improved app usability for users with disabilities.
 * Provides enhanced accessibility features for the multi-sensor recording app.
 */
@Singleton
class AccessibilityHelper @Inject constructor(
    private val context: Context
) {

    private val accessibilityManager = context.getSystemService(Context.ACCESSIBILITY_SERVICE) as AccessibilityManager

    /**
     * Check if accessibility services are enabled
     */
    val isAccessibilityEnabled: Boolean
        get() = accessibilityManager.isEnabled

    /**
     * Check if touch exploration is enabled (TalkBack)
     */
    val isTouchExplorationEnabled: Boolean
        get() = accessibilityManager.isTouchExplorationEnabled

    /**
     * Set up accessibility for recording status indicators
     */
    fun setupRecordingStatusAccessibility(
        view: View,
        isRecording: Boolean,
        duration: Long? = null
    ) {
        val statusText = if (isRecording) {
            if (duration != null) {
                val minutes = duration / 60000
                val seconds = (duration % 60000) / 1000
                "Recording in progress. Duration: ${String.format("%02d minutes %02d seconds", minutes, seconds)}"
            } else {
                "Recording in progress"
            }
        } else {
            "Recording stopped. Ready to start new recording."
        }

        ViewCompat.setAccessibilityDelegate(view, object : androidx.core.view.AccessibilityDelegateCompat() {
            override fun onInitializeAccessibilityNodeInfo(
                host: View,
                info: AccessibilityNodeInfoCompat
            ) {
                super.onInitializeAccessibilityNodeInfo(host, info)
                info.contentDescription = statusText
                info.addAction(
                    AccessibilityNodeInfoCompat.AccessibilityActionCompat(
                        AccessibilityNodeInfoCompat.ACTION_CLICK,
                        if (isRecording) "Stop recording" else "Start recording"
                    )
                )
            }
        })

        // Announce status changes
        announceForAccessibility(view, statusText)
    }

    /**
     * Set up accessibility for connection status indicators
     */
    fun setupConnectionStatusAccessibility(
        view: View,
        deviceName: String,
        isConnected: Boolean,
        signalStrength: Int? = null
    ) {
        val statusText = buildString {
            append(deviceName)
            append(if (isConnected) " connected" else " disconnected")
            
            signalStrength?.let { strength ->
                append(". Signal strength: ")
                append(when {
                    strength >= 80 -> "excellent"
                    strength >= 60 -> "good"
                    strength >= 40 -> "fair"
                    strength >= 20 -> "poor"
                    else -> "very poor"
                })
            }
        }

        view.contentDescription = statusText
        
        // Set up role information
        ViewCompat.setAccessibilityDelegate(view, object : androidx.core.view.AccessibilityDelegateCompat() {
            override fun onInitializeAccessibilityNodeInfo(
                host: View,
                info: AccessibilityNodeInfoCompat
            ) {
                super.onInitializeAccessibilityNodeInfo(host, info)
                info.contentDescription = statusText
                info.roleDescription = "Device status indicator"
                
                if (isConnected) {
                    info.addAction(
                        AccessibilityNodeInfoCompat.AccessibilityActionCompat(
                            AccessibilityNodeInfoCompat.ACTION_CLICK,
                            "View $deviceName settings"
                        )
                    )
                }
            }
        })
    }

    /**
     * Set up accessibility for battery status
     */
    fun setupBatteryStatusAccessibility(
        view: View,
        batteryLevel: Int,
        isCharging: Boolean
    ) {
        val statusText = buildString {
            append("Battery level: $batteryLevel percent")
            if (isCharging) {
                append(", charging")
            } else {
                append(", ")
                append(when {
                    batteryLevel >= 80 -> "excellent level"
                    batteryLevel >= 50 -> "good level"
                    batteryLevel >= 30 -> "moderate level"
                    batteryLevel >= 15 -> "low level, consider charging"
                    else -> "critically low, charging recommended"
                })
            }
        }

        view.contentDescription = statusText
        
        ViewCompat.setAccessibilityDelegate(view, object : androidx.core.view.AccessibilityDelegateCompat() {
            override fun onInitializeAccessibilityNodeInfo(
                host: View,
                info: AccessibilityNodeInfoCompat
            ) {
                super.onInitializeAccessibilityNodeInfo(host, info)
                info.contentDescription = statusText
                info.roleDescription = "Battery status indicator"
            }
        })
    }

    /**
     * Set up accessibility for camera preview
     */
    fun setupCameraPreviewAccessibility(
        view: View,
        isActive: Boolean,
        cameraType: String = "main camera"
    ) {
        val statusText = if (isActive) {
            "$cameraType preview active. Double tap to focus."
        } else {
            "$cameraType preview not available"
        }

        view.contentDescription = statusText
        
        ViewCompat.setAccessibilityDelegate(view, object : androidx.core.view.AccessibilityDelegateCompat() {
            override fun onInitializeAccessibilityNodeInfo(
                host: View,
                info: AccessibilityNodeInfoCompat
            ) {
                super.onInitializeAccessibilityNodeInfo(host, info)
                info.contentDescription = statusText
                info.roleDescription = "Camera preview"
                
                if (isActive) {
                    info.addAction(
                        AccessibilityNodeInfoCompat.AccessibilityActionCompat(
                            AccessibilityNodeInfoCompat.ACTION_CLICK,
                            "Focus camera"
                        )
                    )
                }
            }
        })
    }

    /**
     * Set up accessibility for control buttons with enhanced descriptions
     */
    fun setupControlButtonAccessibility(
        view: View,
        actionDescription: String,
        isEnabled: Boolean,
        additionalInfo: String? = null
    ) {
        val statusText = buildString {
            append(actionDescription)
            if (!isEnabled) {
                append(", disabled")
            }
            additionalInfo?.let { info ->
                append(". $info")
            }
        }

        view.contentDescription = statusText
        
        ViewCompat.setAccessibilityDelegate(view, object : androidx.core.view.AccessibilityDelegateCompat() {
            override fun onInitializeAccessibilityNodeInfo(
                host: View,
                info: AccessibilityNodeInfoCompat
            ) {
                super.onInitializeAccessibilityNodeInfo(host, info)
                info.contentDescription = statusText
                info.isEnabled = isEnabled
                
                if (isEnabled) {
                    info.addAction(
                        AccessibilityNodeInfoCompat.AccessibilityActionCompat(
                            AccessibilityNodeInfoCompat.ACTION_CLICK,
                            actionDescription
                        )
                    )
                }
            }
        })
    }

    /**
     * Announce important status changes to accessibility services
     */
    fun announceForAccessibility(view: View, message: String) {
        if (isAccessibilityEnabled) {
            view.announceForAccessibility(message)
        }
    }

    /**
     * Send accessibility event for important state changes
     */
    fun sendAccessibilityEvent(view: View, eventType: Int, message: String) {
        if (isAccessibilityEnabled) {
            val event = AccessibilityEvent.obtain(eventType)
            event.text.add(message)
            event.setSource(view)
            accessibilityManager.sendAccessibilityEvent(event)
        }
    }

    /**
     * Announce recording state changes
     */
    fun announceRecordingStateChange(view: View, isRecording: Boolean, sessionId: String? = null) {
        val message = if (isRecording) {
            "Recording started" + (sessionId?.let { " for session ${it.take(8)}" } ?: "")
        } else {
            "Recording stopped"
        }
        
        announceForAccessibility(view, message)
        sendAccessibilityEvent(view, AccessibilityEvent.TYPE_ANNOUNCEMENT, message)
    }

    /**
     * Announce device connection changes
     */
    fun announceConnectionChange(view: View, deviceName: String, isConnected: Boolean) {
        val message = "$deviceName ${if (isConnected) "connected" else "disconnected"}"
        announceForAccessibility(view, message)
        sendAccessibilityEvent(view, AccessibilityEvent.TYPE_ANNOUNCEMENT, message)
    }

    /**
     * Announce system errors with context
     */
    fun announceError(view: View, errorMessage: String) {
        val message = "Error: $errorMessage"
        announceForAccessibility(view, message)
        sendAccessibilityEvent(view, AccessibilityEvent.TYPE_ANNOUNCEMENT, message)
    }

    /**
     * Set up accessibility live region for dynamic content
     */
    fun setupLiveRegion(view: View, mode: Int = ViewCompat.ACCESSIBILITY_LIVE_REGION_POLITE) {
        ViewCompat.setAccessibilityLiveRegion(view, mode)
    }

    /**
     * Add accessibility hints for complex interactions
     */
    fun addAccessibilityHint(view: View, hint: String) {
        ViewCompat.setAccessibilityDelegate(view, object : androidx.core.view.AccessibilityDelegateCompat() {
            override fun onInitializeAccessibilityNodeInfo(
                host: View,
                info: AccessibilityNodeInfoCompat
            ) {
                super.onInitializeAccessibilityNodeInfo(host, info)
                info.hintText = hint
            }
        })
    }

    /**
     * Set up accessibility for progress indicators
     */
    fun setupProgressAccessibility(
        view: View,
        progressType: String,
        currentValue: Int,
        maxValue: Int = 100
    ) {
        val statusText = "$progressType: $currentValue of $maxValue"
        
        ViewCompat.setAccessibilityDelegate(view, object : androidx.core.view.AccessibilityDelegateCompat() {
            override fun onInitializeAccessibilityNodeInfo(
                host: View,
                info: AccessibilityNodeInfoCompat
            ) {
                super.onInitializeAccessibilityNodeInfo(host, info)
                info.contentDescription = statusText
                info.roleDescription = "Progress indicator"
                info.setRangeInfo(
                    AccessibilityNodeInfoCompat.RangeInfoCompat.obtain(
                        AccessibilityNodeInfoCompat.RangeInfoCompat.RANGE_TYPE_INT,
                        0f,
                        maxValue.toFloat(),
                        currentValue.toFloat()
                    )
                )
            }
        })
    }

    /**
     * Check if user prefers reduced animations (for accessibility)
     */
    fun shouldReduceAnimations(): Boolean {
        return try {
            val scale = android.provider.Settings.Global.getFloat(
                context.contentResolver,
                android.provider.Settings.Global.ANIMATOR_DURATION_SCALE,
                1.0f
            )
            scale == 0.0f
        } catch (e: Exception) {
            false
        }
    }

    /**
     * Get recommended timeout for accessibility interactions
     */
    fun getAccessibilityTimeout(): Long {
        return if (isTouchExplorationEnabled) {
            // Longer timeout for users with accessibility services
            10000L // 10 seconds
        } else {
            5000L // 5 seconds
        }
    }
}

/**
 * Extension functions for common accessibility operations
 */
fun View.setAccessibilityDescription(description: String) {
    this.contentDescription = description
}

fun View.announceAccessibility(message: String) {
    this.announceForAccessibility(message)
}

fun View.setAccessibilityRole(role: String) {
    ViewCompat.setAccessibilityDelegate(this, object : androidx.core.view.AccessibilityDelegateCompat() {
        override fun onInitializeAccessibilityNodeInfo(
            host: View,
            info: AccessibilityNodeInfoCompat
        ) {
            super.onInitializeAccessibilityNodeInfo(host, info)
            info.roleDescription = role
        }
    })
}