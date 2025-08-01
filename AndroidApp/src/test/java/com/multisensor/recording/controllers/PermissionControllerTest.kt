package com.multisensor.recording.controllers

import android.app.Activity
import android.content.Context
import android.content.SharedPreferences
import com.multisensor.recording.managers.PermissionManager
import io.mockk.*
import kotlinx.coroutines.test.runTest
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

/**
 * Comprehensive unit tests for PermissionController
 * Tests all permission scenarios, state management, and callback handling
 */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [33])
class PermissionControllerTest {

    private lateinit var permissionController: PermissionController
    private lateinit var mockPermissionManager: PermissionManager
    private lateinit var mockCallback: PermissionController.PermissionCallback
    private lateinit var mockContext: Context
    private lateinit var mockActivity: Activity
    private lateinit var mockSharedPreferences: SharedPreferences
    private lateinit var mockEditor: SharedPreferences.Editor

    @Before
    fun setUp() {
        MockKAnnotations.init(this)
        
        // Create mocks
        mockPermissionManager = mockk(relaxed = true)
        mockCallback = mockk(relaxed = true)
        mockContext = mockk(relaxed = true)
        mockActivity = mockk(relaxed = true)
        mockSharedPreferences = mockk(relaxed = true)
        mockEditor = mockk(relaxed = true)

        // Setup SharedPreferences mocks
        every { mockContext.getSharedPreferences(any(), any()) } returns mockSharedPreferences
        every { mockSharedPreferences.edit() } returns mockEditor
        every { mockEditor.putBoolean(any(), any()) } returns mockEditor
        every { mockEditor.putInt(any(), any()) } returns mockEditor
        every { mockEditor.putLong(any(), any()) } returns mockEditor
        every { mockEditor.putStringSet(any(), any()) } returns mockEditor
        every { mockEditor.clear() } returns mockEditor
        every { mockEditor.apply() } just Runs

        // Initialize PermissionController
        permissionController = PermissionController(mockPermissionManager)
    }

    @After
    fun tearDown() {
        unmockkAll()
    }

    // ========== Initialization Tests ==========

    @Test
    fun `setCallback should initialize state storage when callback is Context`() {
        // Given
        every { mockContext.getSharedPreferences(any(), any()) } returns mockSharedPreferences
        every { mockSharedPreferences.getBoolean(any(), any()) } returns false
        every { mockSharedPreferences.getInt(any(), any()) } returns 0
        every { mockSharedPreferences.getLong(any(), any()) } returns 0L

        // When
        permissionController.setCallback(mockContext as PermissionController.PermissionCallback)

        // Then
        verify { mockContext.getSharedPreferences("permission_controller_prefs", Context.MODE_PRIVATE) }
    }

    @Test
    fun `setCallback should not initialize state storage when callback is not Context`() {
        // When
        permissionController.setCallback(mockCallback)

        // Then
        verify(exactly = 0) { mockContext.getSharedPreferences(any(), any()) }
    }

    // ========== Permission Check Tests ==========

    @Test
    fun `areAllPermissionsGranted should delegate to PermissionManager`() {
        // Given
        every { mockPermissionManager.areAllPermissionsGranted(mockContext) } returns true

        // When
        val result = permissionController.areAllPermissionsGranted(mockContext)

        // Then
        assertTrue(result)
        verify { mockPermissionManager.areAllPermissionsGranted(mockContext) }
    }

    @Test
    fun `checkPermissions should call onAllPermissionsGranted when permissions are granted`() = runTest {
        // Given
        every { mockPermissionManager.areAllPermissionsGranted(mockContext) } returns true
        permissionController.setCallback(mockCallback)

        // When
        permissionController.checkPermissions(mockContext)

        // Then
        verify { mockCallback.onPermissionCheckStarted() }
        verify { mockCallback.onAllPermissionsGranted() }
        verify(exactly = 0) { mockPermissionManager.requestPermissions(any(), any()) }
    }

    @Test
    fun `checkPermissions should request permissions when permissions are missing`() = runTest {
        // Given
        every { mockPermissionManager.areAllPermissionsGranted(mockContext) } returns false
        permissionController.setCallback(mockCallback)

        // When
        permissionController.checkPermissions(mockActivity)

        // Then
        verify { mockCallback.onPermissionCheckStarted() }
        verify { mockCallback.updateStatusText("Requesting permissions...") }
        verify { mockPermissionManager.requestPermissions(mockActivity, any()) }
    }

    @Test
    fun `checkPermissions should not request permissions for non-Activity context`() = runTest {
        // Given
        every { mockPermissionManager.areAllPermissionsGranted(mockContext) } returns false
        permissionController.setCallback(mockCallback)

        // When
        permissionController.checkPermissions(mockContext)

        // Then
        verify { mockCallback.onPermissionCheckStarted() }
        verify(exactly = 0) { mockPermissionManager.requestPermissions(any(), any()) }
    }

    // ========== Permission Manager Callback Tests ==========

    @Test
    fun `PermissionManager onAllPermissionsGranted should trigger callback`() = runTest {
        // Given
        every { mockPermissionManager.areAllPermissionsGranted(mockActivity) } returns false
        permissionController.setCallback(mockCallback)
        
        // Capture the callback passed to PermissionManager
        val callbackSlot = slot<PermissionManager.PermissionCallback>()
        every { mockPermissionManager.requestPermissions(mockActivity, capture(callbackSlot)) } just Runs

        // When
        permissionController.checkPermissions(mockActivity)
        callbackSlot.captured.onAllPermissionsGranted()

        // Then
        verify { mockCallback.onAllPermissionsGranted() }
        verify { mockCallback.onPermissionRequestCompleted() }
    }

    @Test
    fun `PermissionManager onPermissionsTemporarilyDenied should trigger callback`() = runTest {
        // Given
        val deniedPermissions = listOf("android.permission.CAMERA", "android.permission.RECORD_AUDIO")
        every { mockPermissionManager.areAllPermissionsGranted(mockActivity) } returns false
        permissionController.setCallback(mockActivity as PermissionController.PermissionCallback)
        
        // Capture the callback passed to PermissionManager
        val callbackSlot = slot<PermissionManager.PermissionCallback>()
        every { mockPermissionManager.requestPermissions(mockActivity, capture(callbackSlot)) } just Runs

        // When
        permissionController.checkPermissions(mockActivity)
        callbackSlot.captured.onPermissionsTemporarilyDenied(deniedPermissions, 3, 5)

        // Then
        verify { mockCallback.onPermissionsTemporarilyDenied(deniedPermissions, 3, 5) }
        verify { mockCallback.onPermissionRequestCompleted() }
    }

    @Test
    fun `PermissionManager onPermissionsPermanentlyDenied should trigger callback`() = runTest {
        // Given
        val deniedPermissions = listOf("android.permission.CAMERA")
        every { mockPermissionManager.areAllPermissionsGranted(mockActivity) } returns false
        permissionController.setCallback(mockActivity as PermissionController.PermissionCallback)
        
        // Capture the callback passed to PermissionManager
        val callbackSlot = slot<PermissionManager.PermissionCallback>()
        every { mockPermissionManager.requestPermissions(mockActivity, capture(callbackSlot)) } just Runs

        // When
        permissionController.checkPermissions(mockActivity)
        callbackSlot.captured.onPermissionsPermanentlyDenied(deniedPermissions)

        // Then
        verify { mockCallback.onPermissionsPermanentlyDenied(deniedPermissions) }
        verify { mockCallback.onPermissionRequestCompleted() }
    }

    // ========== Manual Permission Request Tests ==========

    @Test
    fun `requestPermissionsManually should reset state and call checkPermissions`() = runTest {
        // Given
        every { mockPermissionManager.areAllPermissionsGranted(mockContext) } returns false
        permissionController.setCallback(mockCallback)

        // When
        permissionController.requestPermissionsManually(mockContext)

        // Then
        verify { mockCallback.showPermissionButton(false) }
        verify { mockCallback.updateStatusText("Requesting permissions...") }
        verify { mockCallback.onPermissionCheckStarted() }
    }

    @Test
    fun `requestPermissionsManually should reset retry count to zero`() = runTest {
        // Given
        every { mockPermissionManager.areAllPermissionsGranted(mockContext) } returns true
        permissionController.setCallback(mockContext as PermissionController.PermissionCallback)

        // First, simulate some retry attempts
        repeat(3) {
            permissionController.checkPermissions(mockContext)
        }

        // When - manual request should reset retry count
        permissionController.requestPermissionsManually(mockContext)

        // Then - retry count should be 0
        assertEquals(0, permissionController.getPermissionRetryCount())
    }

    // ========== State Management Tests ==========

    @Test
    fun `resetState should clear internal state and persist changes`() {
        // Given
        permissionController.setCallback(mockContext as PermissionController.PermissionCallback)

        // When
        permissionController.resetState()

        // Then
        assertFalse(permissionController.hasCheckedPermissionsOnStartup())
        assertEquals(0, permissionController.getPermissionRetryCount())
        verify { mockEditor.putBoolean("has_checked_permissions_on_startup", false) }
        verify { mockEditor.putInt("permission_retry_count", 0) }
        verify { mockEditor.apply() }
    }

    @Test
    fun `clearPersistedState should clear SharedPreferences`() {
        // Given
        permissionController.setCallback(mockContext as PermissionController.PermissionCallback)

        // When
        permissionController.clearPersistedState()

        // Then
        verify { mockEditor.clear() }
        verify { mockEditor.apply() }
        assertFalse(permissionController.hasCheckedPermissionsOnStartup())
        assertEquals(0, permissionController.getPermissionRetryCount())
    }

    @Test
    fun `initializePermissionsOnStartup should check permissions on first call`() = runTest {
        // Given
        every { mockPermissionManager.areAllPermissionsGranted(mockContext) } returns true
        permissionController.setCallback(mockCallback)

        // When - first call
        permissionController.initializePermissionsOnStartup(mockContext)

        // Then
        verify { mockCallback.onPermissionCheckStarted() }
        verify { mockCallback.onAllPermissionsGranted() }
        assertTrue(permissionController.hasCheckedPermissionsOnStartup())
    }

    @Test
    fun `initializePermissionsOnStartup should skip permissions check on subsequent calls`() = runTest {
        // Given
        every { mockPermissionManager.areAllPermissionsGranted(mockContext) } returns true
        permissionController.setCallback(mockCallback)

        // When - first call
        permissionController.initializePermissionsOnStartup(mockContext)
        
        // Clear previous invocations
        clearMocks(mockCallback)

        // When - second call
        permissionController.initializePermissionsOnStartup(mockContext)

        // Then - should only update button visibility, not check permissions
        verify(exactly = 0) { mockCallback.onPermissionCheckStarted() }
        verify(exactly = 0) { mockCallback.onAllPermissionsGranted() }
    }

    // ========== Permission Button Visibility Tests ==========

    @Test
    fun `updatePermissionButtonVisibility should show button when permissions missing`() {
        // Given
        every { mockPermissionManager.areAllPermissionsGranted(mockContext) } returns false
        permissionController.setCallback(mockCallback)

        // When
        permissionController.updatePermissionButtonVisibility(mockContext)

        // Then
        verify { mockCallback.showPermissionButton(true) }
    }

    @Test
    fun `updatePermissionButtonVisibility should hide button when all permissions granted`() {
        // Given
        every { mockPermissionManager.areAllPermissionsGranted(mockContext) } returns true
        permissionController.setCallback(mockCallback)

        // When
        permissionController.updatePermissionButtonVisibility(mockContext)

        // Then
        verify { mockCallback.showPermissionButton(false) }
    }

    // ========== Permanently Denied Permissions Tests ==========

    @Test
    fun `storePermanentlyDeniedPermissions should save to SharedPreferences`() {
        // Given
        val deniedPermissions = listOf("android.permission.CAMERA", "android.permission.RECORD_AUDIO")
        every { mockPermissionManager.areAllPermissionsGranted(mockActivity) } returns false
        permissionController.setCallback(mockActivity as PermissionController.PermissionCallback)
        
        // Capture the callback passed to PermissionManager
        val callbackSlot = slot<PermissionManager.PermissionCallback>()
        every { mockPermissionManager.requestPermissions(mockActivity, capture(callbackSlot)) } just Runs

        // When
        permissionController.checkPermissions(mockActivity)
        callbackSlot.captured.onPermissionsPermanentlyDenied(deniedPermissions)

        // Then
        verify { mockEditor.putStringSet("permanently_denied_permissions", deniedPermissions.toSet()) }
        verify { mockEditor.apply() }
    }

    @Test
    fun `getPermanentlyDeniedPermissions should return stored permissions`() {
        // Given
        val deniedPermissions = setOf("android.permission.CAMERA", "android.permission.RECORD_AUDIO")
        every { mockSharedPreferences.getStringSet("permanently_denied_permissions", emptySet()) } returns deniedPermissions
        permissionController.setCallback(mockContext as PermissionController.PermissionCallback)

        // When
        val result = permissionController.getPermanentlyDeniedPermissions()

        // Then
        assertEquals(deniedPermissions, result)
    }

    @Test
    fun `getPermanentlyDeniedPermissions should return empty set when no SharedPreferences`() {
        // Given - no SharedPreferences initialized
        permissionController.setCallback(mockCallback)

        // When
        val result = permissionController.getPermanentlyDeniedPermissions()

        // Then
        assertEquals(emptySet<String>(), result)
    }

    // ========== State Persistence Tests ==========

    @Test
    fun `state should be loaded from SharedPreferences on initialization`() {
        // Given
        every { mockSharedPreferences.getBoolean("has_checked_permissions_on_startup", false) } returns true
        every { mockSharedPreferences.getInt("permission_retry_count", 0) } returns 2
        every { mockSharedPreferences.getLong("last_permission_request_time", 0) } returns System.currentTimeMillis()

        // When
        permissionController.setCallback(mockContext as PermissionController.PermissionCallback)

        // Then
        assertTrue(permissionController.hasCheckedPermissionsOnStartup())
        assertEquals(2, permissionController.getPermissionRetryCount())
    }

    @Test
    fun `state should be reset when 24 hours have passed`() {
        // Given
        val oldTime = System.currentTimeMillis() - (25 * 60 * 60 * 1000) // 25 hours ago
        every { mockSharedPreferences.getBoolean("has_checked_permissions_on_startup", false) } returns true
        every { mockSharedPreferences.getInt("permission_retry_count", 0) } returns 3
        every { mockSharedPreferences.getLong("last_permission_request_time", 0) } returns oldTime

        // When
        permissionController.setCallback(mockContext as PermissionController.PermissionCallback)

        // Then
        assertFalse(permissionController.hasCheckedPermissionsOnStartup())
        assertEquals(0, permissionController.getPermissionRetryCount())
        verify { mockEditor.putBoolean("has_checked_permissions_on_startup", false) }
        verify { mockEditor.putInt("permission_retry_count", 0) }
    }

    // ========== Permission Display Name Tests ==========

    @Test
    fun `getPermissionDisplayName should delegate to PermissionManager`() {
        // Given
        val permission = "android.permission.CAMERA"
        every { mockPermissionManager.getPermissionDisplayName(permission) } returns "Camera"

        // When
        val result = permissionController.getPermissionDisplayName(permission)

        // Then
        assertEquals("Camera", result)
        verify { mockPermissionManager.getPermissionDisplayName(permission) }
    }

    // ========== Status Reporting Tests ==========

    @Test
    fun `getPermissionStatus should return comprehensive status string`() {
        // Given
        permissionController.setCallback(mockContext as PermissionController.PermissionCallback)
        every { mockSharedPreferences.getLong("last_permission_request_time", 0) } returns 12345L

        // When
        val status = permissionController.getPermissionStatus()

        // Then
        assertTrue(status.contains("Permission Controller Status:"))
        assertTrue(status.contains("Has checked permissions on startup:"))
        assertTrue(status.contains("Permission retry count:"))
        assertTrue(status.contains("State persistence:"))
        assertTrue(status.contains("Permanently denied permissions:"))
        assertTrue(status.contains("Last request time:"))
    }

    @Test
    fun `logCurrentPermissionStates should delegate to PermissionManager`() {
        // When
        permissionController.logCurrentPermissionStates(mockContext)

        // Then
        verify { mockPermissionManager.logCurrentPermissionStates(mockContext) }
    }

    // ========== Edge Cases and Error Handling Tests ==========

    @Test
    fun `operations should not crash when callback is null`() {
        // Given - no callback set

        // When & Then - should not crash
        assertDoesNotThrow {
            permissionController.checkPermissions(mockContext)
            permissionController.updatePermissionButtonVisibility(mockContext)
            permissionController.requestPermissionsManually(mockContext)
        }
    }

    @Test
    fun `operations should handle SharedPreferences initialization failure gracefully`() {
        // Given
        every { mockContext.getSharedPreferences(any(), any()) } throws RuntimeException("Permission denied")

        // When & Then - should not crash
        assertDoesNotThrow {
            permissionController.setCallback(mockContext as PermissionController.PermissionCallback)
            permissionController.resetState()
            permissionController.clearPersistedState()
        }
    }

    @Test
    fun `multiple callbacks should work correctly`() = runTest {
        // Given
        val mockCallback2 = mockk<PermissionController.PermissionCallback>(relaxed = true)
        every { mockPermissionManager.areAllPermissionsGranted(mockContext) } returns true

        // When - set first callback
        permissionController.setCallback(mockCallback)
        permissionController.checkPermissions(mockContext)

        // Then - verify first callback was called
        verify { mockCallback.onAllPermissionsGranted() }

        // When - set second callback
        permissionController.setCallback(mockCallback2)
        permissionController.checkPermissions(mockContext)

        // Then - verify second callback was called
        verify { mockCallback2.onAllPermissionsGranted() }
    }

    // ========== Integration Test Scenarios ==========

    @Test
    fun `complete permission flow - all granted scenario`() = runTest {
        // Given
        every { mockPermissionManager.areAllPermissionsGranted(mockActivity) } returns true
        permissionController.setCallback(mockCallback)

        // When - startup permission check
        permissionController.initializePermissionsOnStartup(mockActivity)

        // Then - should grant immediately
        verify { mockCallback.onPermissionCheckStarted() }
        verify { mockCallback.onAllPermissionsGranted() }
        verify { mockCallback.showPermissionButton(false) }
        assertTrue(permissionController.hasCheckedPermissionsOnStartup())
    }

    @Test
    fun `complete permission flow - denied then granted scenario`() = runTest {
        // Given
        every { mockPermissionManager.areAllPermissionsGranted(mockActivity) } returns false andThen true
        permissionController.setCallback(mockCallback)
        
        val callbackSlot = slot<PermissionManager.PermissionCallback>()
        every { mockPermissionManager.requestPermissions(mockActivity, capture(callbackSlot)) } just Runs

        // When - initial check (denied)
        permissionController.checkPermissions(mockActivity)

        // Then - should request permissions
        verify { mockCallback.onPermissionCheckStarted() }
        verify { mockCallback.updateStatusText("Requesting permissions...") }

        // When - user grants permissions
        callbackSlot.captured.onAllPermissionsGranted()

        // Then - should complete successfully
        verify { mockCallback.onAllPermissionsGranted() }
        verify { mockCallback.onPermissionRequestCompleted() }
    }

    @Test
    fun `complete permission flow - permanently denied scenario`() = runTest {
        // Given
        val deniedPermissions = listOf("android.permission.CAMERA")
        every { mockPermissionManager.areAllPermissionsGranted(mockActivity) } returns false
        permissionController.setCallback(mockActivity as PermissionController.PermissionCallback)
        
        val callbackSlot = slot<PermissionManager.PermissionCallback>()
        every { mockPermissionManager.requestPermissions(mockActivity, capture(callbackSlot)) } just Runs

        // When - permission check and denial
        permissionController.checkPermissions(mockActivity)
        callbackSlot.captured.onPermissionsPermanentlyDenied(deniedPermissions)

        // Then - should handle permanent denial
        verify { mockCallback.onPermissionsPermanentlyDenied(deniedPermissions) }
        verify { mockCallback.onPermissionRequestCompleted() }
        verify { mockEditor.putStringSet("permanently_denied_permissions", deniedPermissions.toSet()) }
        assertEquals(deniedPermissions.toSet(), permissionController.getPermanentlyDeniedPermissions())
    }
}