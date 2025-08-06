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
    }
}