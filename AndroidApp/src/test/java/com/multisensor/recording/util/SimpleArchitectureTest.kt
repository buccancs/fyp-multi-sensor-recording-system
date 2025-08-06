package com.multisensor.recording.util

import com.google.common.truth.Truth.assertThat
import com.multisensor.recording.testbase.BaseUnitTest
import org.junit.Test
import java.io.File

class SimpleArchitectureTest : BaseUnitTest() {

    @Test
    fun `should run basic test with modern architecture`() {
        val testValue = "Modern Test Architecture"

        val result = testValue.length

        assertThat(result).isEqualTo(23)
        assertThat(testValue).contains("Modern")
    }

    @Test
    fun `should work with Truth assertions`() {
        val numbers = listOf(1, 2, 3, 4, 5)

        assertThat(numbers).hasSize(5)
        assertThat(numbers).contains(3)
        assertThat(numbers).containsExactly(1, 2, 3, 4, 5).inOrder()
    }

    @Test
    fun `should demonstrate MockK integration via base class`() {

        assertThat(testDispatcher).isNotNull()
    }

    @Test
    fun `should handle coroutines testing`() {

        assertThat(testDispatcher.scheduler.currentTime).isEqualTo(0L)
    }

    @Test
    fun `should work with Kotlin collections`() {
        val map = mapOf("key1" to "value1", "key2" to "value2")

        assertThat(map).hasSize(2)
        assertThat(map).containsKey("key1")
        assertThat(map).containsEntry("key2", "value2")
    }

    // Architecture Enforcement Tests - Added to detect forbidden dependencies

    @Test
    fun `UI layer should not directly import from network or service packages`() {
        val uiFiles = getKotlinFilesInPackage("ui")
        val forbiddenImports = listOf(
            "com.multisensor.recording.network.",
            "com.multisensor.recording.service.",
            "com.multisensor.recording.recording."  // UI should go through controllers/managers
        )

        uiFiles.forEach { file ->
            val content = file.readText()
            forbiddenImports.forEach { forbiddenImport ->
                assertThat(content).doesNotContain("import $forbiddenImport")
            }
        }
    }

    @Test
    fun `Controllers should not directly import from UI packages`() {
        val controllerFiles = getKotlinFilesInPackage("controllers")
        val forbiddenImports = listOf(
            "androidx.activity.",
            "androidx.fragment.",
            "android.app.Activity",
            "android.app.Fragment"
        )

        controllerFiles.forEach { file ->
            val content = file.readText()
            forbiddenImports.forEach { forbiddenImport ->
                assertThat(content).doesNotContain("import $forbiddenImport")
            }
        }
    }

    @Test
    fun `Recording components should not directly access UI layer`() {
        val recordingFiles = getKotlinFilesInPackage("recording")
        val forbiddenImports = listOf(
            "com.multisensor.recording.ui.",
            "androidx.lifecycle.ViewModel"
        )

        recordingFiles.forEach { file ->
            val content = file.readText()
            forbiddenImports.forEach { forbiddenImport ->
                assertThat(content).doesNotContain("import $forbiddenImport")
            }
        }
    }

    @Test
    fun `Network layer should not depend on UI or business logic`() {
        val networkFiles = getKotlinFilesInPackage("network")
        val forbiddenImports = listOf(
            "com.multisensor.recording.ui.",
            "com.multisensor.recording.controllers.",
            "com.multisensor.recording.managers."
        )

        networkFiles.forEach { file ->
            val content = file.readText()
            forbiddenImports.forEach { forbiddenImport ->
                assertThat(content).doesNotContain("import $forbiddenImport")
            }
        }
    }

    @Test
    fun `Infrastructure utilities should be used consistently`() {
        val allKotlinFiles = getAllKotlinFiles()
        
        // Check that logging is done through centralized utilities
        allKotlinFiles.forEach { file ->
            val content = file.readText()
            // Should not use direct Android Log
            if (content.contains("import android.util.Log")) {
                assertThat(content).doesNotContain("Log.d(")
                assertThat(content).doesNotContain("Log.e(")
                assertThat(content).doesNotContain("Log.w(")
            }
        }
    }

    @Test
    fun `Dependency injection scope should be consistent`() {
        val allKotlinFiles = getAllKotlinFiles()
        
        allKotlinFiles.forEach { file ->
            val content = file.readText()
            
            // Check that @Singleton is used for managers and controllers
            if (content.contains("class") && 
                (content.contains("Manager") || content.contains("Controller")) &&
                content.contains("@Inject constructor")) {
                // Should have proper DI scope
                assertThat(content.contains("@Singleton") || content.contains("@ActivityScoped") || content.contains("@ServiceScoped")).isTrue()
            }
        }
    }

    // Helper methods for architecture testing

    private fun getKotlinFilesInPackage(packageName: String): List<File> {
        val srcDir = File("src/main/java/com/multisensor/recording/$packageName")
        if (!srcDir.exists()) return emptyList()
        
        return srcDir.walkTopDown()
            .filter { it.isFile && it.extension == "kt" }
            .toList()
    }

    private fun getAllKotlinFiles(): List<File> {
        val srcDir = File("src/main/java/com/multisensor/recording")
        if (!srcDir.exists()) return emptyList()
        
        return srcDir.walkTopDown()
            .filter { it.isFile && it.extension == "kt" }
            .toList()
    }
}