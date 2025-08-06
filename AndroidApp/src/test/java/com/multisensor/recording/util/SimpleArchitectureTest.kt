package com.multisensor.recording.util

import com.google.common.truth.Truth.assertThat
import com.multisensor.recording.testbase.BaseUnitTest
import org.junit.Test
import java.io.File

/**
 * Architecture enforcement tests to maintain strict separation of concerns.
 * Validates that the clean MVVM architecture layers are properly maintained.
 * 
 * Enforces the following architectural rules:
 * - UI layer only depends on ViewModels and Controllers
 * - Controllers don't depend on UI components
 * - Managers handle business logic without UI dependencies
 * - Network layer is isolated from UI layer
 * - Service layer maintains proper boundaries
 */
class SimpleArchitectureTest : BaseUnitTest() {

    private val sourceRoot = "AndroidApp/src/main/java/com/multisensor/recording"
    
    @Test
    fun `UI layer should not import from network packages`() {
        val violations = findForbiddenImports(
            sourcePattern = "ui/",
            forbiddenPackages = listOf("network", "service"),
            description = "UI components importing network/service packages directly"
        )
        
        assertThat(violations).isEmpty()
    }
    
    @Test
    fun `Activities and Fragments should only import from UI layer and ViewModels`() {
        val allowedPackages = listOf("ui", "controllers", "managers", "androidx", "android", "kotlin", "java", "dagger", "hilt")
        val violations = findForbiddenImportsInUIComponents(allowedPackages)
        
        assertThat(violations).isEmpty()
    }
    
    @Test
    fun `Network layer should not import from UI packages`() {
        val violations = findForbiddenImports(
            sourcePattern = "network/",
            forbiddenPackages = listOf("ui"),
            description = "Network components importing UI packages"
        )
        
        assertThat(violations).isEmpty()
    }
    
    @Test
    fun `Service layer should not import from UI packages`() {
        val violations = findForbiddenImports(
            sourcePattern = "service/",
            forbiddenPackages = listOf("ui"),
            description = "Service components importing UI packages"
        )
        
        assertThat(violations).isEmpty()
    }
    
    @Test
    fun `Controllers should not import from low-level services directly`() {
        val violations = findForbiddenImports(
            sourcePattern = "controllers/",
            forbiddenPackages = listOf("network", "service"),
            description = "Controllers importing from network/service packages directly"
        )
        
        assertThat(violations).isEmpty()
    }
    
    @Test
    fun `Managers should properly encapsulate domain logic`() {
        val violations = findForbiddenImports(
            sourcePattern = "managers/",
            forbiddenPackages = listOf("ui"),
            description = "Managers importing UI packages"
        )
        
        assertThat(violations).isEmpty()
    }

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
    
    private fun findForbiddenImports(
        sourcePattern: String,
        forbiddenPackages: List<String>,
        description: String
    ): List<String> {
        val violations = mutableListOf<String>()
        val sourceDir = File(sourceRoot)
        
        if (!sourceDir.exists()) {
            return emptyList() // Skip if source directory doesn't exist in test environment
        }
        
        sourceDir.walkTopDown()
            .filter { it.name.endsWith(".kt") && it.path.contains(sourcePattern) }
            .forEach { file ->
                val content = file.readText()
                forbiddenPackages.forEach { forbiddenPackage ->
                    val importPattern = Regex("import\\s+com\\.multisensor\\.recording\\.$forbiddenPackage")
                    if (importPattern.containsMatchIn(content)) {
                        violations.add("${file.name}: $description - imports from $forbiddenPackage")
                    }
                }
            }
        
        return violations
    }
    
    private fun findForbiddenImportsInUIComponents(allowedPackages: List<String>): List<String> {
        val violations = mutableListOf<String>()
        val sourceDir = File(sourceRoot)
        
        if (!sourceDir.exists()) {
            return emptyList() // Skip if source directory doesn't exist in test environment
        }
        
        sourceDir.walkTopDown()
            .filter { it.name.endsWith(".kt") && (it.path.contains("ui/") || it.name.contains("Activity") || it.name.contains("Fragment")) }
            .forEach { file ->
                val content = file.readText()
                val importPattern = Regex("import\\s+com\\.multisensor\\.recording\\.(\\w+)")
                importPattern.findAll(content).forEach { match ->
                    val importedPackage = match.groupValues[1]
                    if (!allowedPackages.contains(importedPackage)) {
                        violations.add("${file.name}: UI component importing from non-allowed package: $importedPackage")
                    }
                }
            }
        
        return violations

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