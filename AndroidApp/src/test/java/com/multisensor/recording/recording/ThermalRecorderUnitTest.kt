package com.multisensor.recording.recording

import android.content.Context
import com.multisensor.recording.service.SessionManager
import com.multisensor.recording.util.Logger
import com.multisensor.recording.util.ThermalCameraSettings
import io.kotest.core.spec.style.DescribeSpec
import io.kotest.matchers.shouldBe
import io.kotest.matchers.shouldNotBe
import io.mockk.*
import kotlinx.coroutines.test.runTest
import org.robolectric.annotation.Config
import java.io.File

/**
 * Comprehensive unit tests for ThermalRecorder class using modern Kotlin syntax.
 * Tests all core functionality including initialization, recording, preview,
 * error handling, thread safety, and resource management.
 * 
 * This test suite ensures the Topdon TC001/Plus integration is bulletproof.
 */
@Config(sdk = [33])
class ThermalRecorderUnitTest : DescribeSpec({

    val mockContext: Context = mockk(relaxed = true)
    val mockSessionManager: SessionManager = mockk(relaxed = true)
    val mockLogger: Logger = mockk(relaxed = true)
    val mockThermalSettings: ThermalCameraSettings = mockk(relaxed = true)
    val testSessionId = "test_thermal_session_123"
    
    lateinit var thermalRecorder: ThermalRecorder

    beforeEach {
        clearAllMocks()
        
        // Mock session manager to return valid paths
        val mockSessionPaths = mockk<SessionManager.SessionFilePaths>()
        every { mockSessionPaths.sessionFolder } returns File("/test/session/folder")
        every { mockSessionManager.getSessionFilePaths() } returns mockSessionPaths

        // Create ThermalRecorder instance
        thermalRecorder = ThermalRecorder(mockContext, mockSessionManager, mockLogger, mockThermalSettings)
    }

    describe("ThermalRecorder initialization") {
        
        it("should initialize successfully") {
            runTest {
                val result = thermalRecorder.initialize()
                
                result shouldBe true
                verify { mockLogger.debug(any<String>(), any()) }
            }
        }
        
        it("should handle initialization failure gracefully") {
            runTest {
                // Mock failure condition (e.g., no thermal camera detected)
                every { mockContext.packageManager } throws RuntimeException("No thermal camera")
                
                val result = thermalRecorder.initialize()
                
                result shouldBe false
                verify { mockLogger.error(any<String>(), any()) }
            }
        }
    }

    describe("ThermalRecorder recording operations") {
        
        it("should start recording successfully when initialized") {
            runTest {
                thermalRecorder.initialize()
                
                val result = thermalRecorder.startRecording(testSessionId)
                
                result shouldBe true
                verify { mockLogger.info(any(), "Starting thermal recording for session: $testSessionId") }
            }
        }
        
        it("should fail to start recording when not initialized") {
            runTest {
                val result = thermalRecorder.startRecording(testSessionId)
                
                result shouldBe false
                verify { mockLogger.error(any(), "Cannot start recording: ThermalRecorder not initialized") }
            }
        }
        
        it("should stop recording successfully") {
            runTest {
                thermalRecorder.initialize()
                thermalRecorder.startRecording(testSessionId)
                
                val result = thermalRecorder.stopRecording()
                
                result shouldBe true
                verify { mockLogger.info(any(), "Thermal recording stopped") }
            }
        }
        
        it("should handle stop recording when not recording") {
            runTest {
                val result = thermalRecorder.stopRecording()
                
                result shouldBe false
                verify { mockLogger.warning(any(), "Stop recording called but not currently recording") }
            }
        }
    }

    describe("ThermalRecorder preview functionality") {
        
        it("should start preview successfully when initialized") {
            runTest {
                thermalRecorder.initialize()
                
                val result = thermalRecorder.startPreview()
                
                result shouldBe true
                verify { mockLogger.debug(any(), "Thermal preview started") }
            }
        }
        
        it("should stop preview successfully") {
            runTest {
                thermalRecorder.initialize()
                thermalRecorder.startPreview()
                
                val result = thermalRecorder.stopPreview()
                
                result shouldBe true
                verify { mockLogger.debug(any(), "Thermal preview stopped") }
            }
        }
    }

    describe("ThermalRecorder status and configuration") {
        
        it("should return correct recording status") {
            runTest {
                thermalRecorder.isRecording() shouldBe false
                
                thermalRecorder.initialize()
                thermalRecorder.startRecording(testSessionId)
                
                thermalRecorder.isRecording() shouldBe true
                
                thermalRecorder.stopRecording()
                
                thermalRecorder.isRecording() shouldBe false
            }
        }
        
        it("should return correct initialization status") {
            thermalRecorder.isInitialized() shouldBe false
            
            runTest {
                thermalRecorder.initialize()
                thermalRecorder.isInitialized() shouldBe true
            }
        }
        
        it("should set temperature range correctly") {
            val minTemp = -10.0f
            val maxTemp = 150.0f
            
            thermalRecorder.setTemperatureRange(minTemp, maxTemp)
            
            verify { mockLogger.debug(any(), "Temperature range set: $minTemp to $maxTemp") }
        }
        
        it("should set color palette correctly") {
            val palette = "IRON"
            
            thermalRecorder.setColorPalette(palette)
            
            verify { mockLogger.debug(any(), "Color palette set: $palette") }
        }
    }

    describe("ThermalRecorder error handling and edge cases") {
        
        it("should handle concurrent recording attempts") {
            runTest {
                thermalRecorder.initialize()
                
                val result1 = thermalRecorder.startRecording(testSessionId)
                val result2 = thermalRecorder.startRecording("another_session")
                
                result1 shouldBe true
                result2 shouldBe false
                
                verify { mockLogger.warning(any(), "Recording already in progress") }
            }
        }
        
        it("should handle session cleanup on recording failure") {
            runTest {
                thermalRecorder.initialize()
                
                // Mock failure during recording
                every { mockSessionManager.getSessionFilePaths() } throws RuntimeException("Storage full")
                
                val result = thermalRecorder.startRecording(testSessionId)
                
                result shouldBe false
                verify { mockLogger.error(any<String>(), any()) }
            }
        }
        
        it("should handle resource cleanup properly") {
            runTest {
                thermalRecorder.initialize()
                thermalRecorder.startRecording(testSessionId)
                thermalRecorder.startPreview()
                
                thermalRecorder.cleanup()
                
                thermalRecorder.isRecording() shouldBe false
                thermalRecorder.isInitialized() shouldBe false
                verify { mockLogger.info(any(), "ThermalRecorder cleanup completed") }
            }
        }
    }

    describe("ThermalRecorder device configuration") {
        
        it("should configure device settings correctly") {
            runTest {
                thermalRecorder.initialize()
                
                thermalRecorder.configureDevice(
                    emissivity = 0.95f,
                    reflectedTemperature = 20.0f,
                    atmosphericTemperature = 22.0f,
                    humidity = 45.0f,
                    distance = 1.0f
                )
                
                verify { 
                    mockLogger.debug(any(), match { 
                        it.contains("Device configured with emissivity: 0.95") 
                    }) 
                }
            }
        }
        
        it("should validate device configuration parameters") {
            runTest {
                thermalRecorder.initialize()
                
                // Test invalid emissivity
                thermalRecorder.configureDevice(emissivity = 1.5f)
                
                verify { 
                    mockLogger.warning(any(), match { 
                        it.contains("Invalid emissivity value") 
                    }) 
                }
            }
        }
    }

    afterEach {
        runTest {
            thermalRecorder.cleanup()
        }
        clearAllMocks()
    }
})