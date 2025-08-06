package com.multisensor.recording.recording

import android.content.Context
import com.multisensor.recording.service.SessionManager
import com.multisensor.recording.util.Logger
import com.multisensor.recording.util.ThermalCameraSettings
import io.kotest.core.spec.style.DescribeSpec
import io.kotest.matchers.shouldBe
import io.kotest.matchers.shouldNotBe
import io.mockk.clearAllMocks
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import kotlinx.coroutines.test.runTest
import org.robolectric.annotation.Config
import java.io.File

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

        val mockSessionPaths = mockk<SessionManager.SessionFilePaths>()
        every { mockSessionPaths.sessionFolder } returns File("/test/session/folder")
        every { mockSessionManager.getSessionFilePaths() } returns mockSessionPaths

        thermalRecorder = ThermalRecorder(mockContext, mockSessionManager, mockLogger, mockThermalSettings)
    }

    describe("ThermalRecorder initialization") {

        it("should initialize successfully") {
            runTest {
                val result = thermalRecorder.initialize()

                result shouldBe true
                verify { mockLogger.debug(any<String>()) }
            }
        }

        it("should handle initialization failure gracefully") {
            runTest {
                every { mockContext.packageManager } throws RuntimeException("No thermal camera")

                val result = thermalRecorder.initialize()

                result shouldBe false
                verify { mockLogger.error(any<String>()) }
            }
        }
    }

    describe("ThermalRecorder recording operations") {

        it("should start recording successfully when initialized") {
            runTest {
                thermalRecorder.initialize()

                val result = thermalRecorder.startRecording(testSessionId)

                result shouldBe true
                verify { mockLogger.info("Starting thermal recording for session: $testSessionId") }
            }
        }

        it("should fail to start recording when not initialized") {
            runTest {
                val result = thermalRecorder.startRecording(testSessionId)

                result shouldBe false
                verify { mockLogger.error("Cannot start recording: ThermalRecorder not initialized") }
            }
        }

        it("should stop recording successfully") {
            runTest {
                thermalRecorder.initialize()
                thermalRecorder.startRecording(testSessionId)

                val result = thermalRecorder.stopRecording()

                result shouldBe true
                verify { mockLogger.info("Thermal recording stopped") }
            }
        }

        it("should handle stop recording when not recording") {
            runTest {
                val result = thermalRecorder.stopRecording()

                result shouldBe false
                verify { mockLogger.warning("Stop recording called but not currently recording") }
            }
        }
    }

    describe("ThermalRecorder preview functionality") {

        it("should start preview successfully when initialized") {
            runTest {
                thermalRecorder.initialize()

                val result = thermalRecorder.startPreview()

                result shouldBe true
                verify { mockLogger.debug("Thermal preview started") }
            }
        }

        it("should stop preview successfully") {
            runTest {
                thermalRecorder.initialize()
                thermalRecorder.startPreview()

                val result = thermalRecorder.stopPreview()

                result shouldBe true
                verify { mockLogger.debug("Thermal preview stopped") }
            }
        }
    }

    describe("ThermalRecorder status and configuration") {

        it("should return correct recording status") {
            runTest {
                thermalRecorder.getThermalCameraStatus().isRecording shouldBe false

                thermalRecorder.initialize()
                thermalRecorder.startRecording(testSessionId)

                thermalRecorder.getThermalCameraStatus().isRecording shouldBe true

                thermalRecorder.stopRecording()

                thermalRecorder.getThermalCameraStatus().isRecording shouldBe false
            }
        }

        it("should return correct initialization status") {
            runTest {
                val initResult = thermalRecorder.initialize()
                initResult shouldBe true

                val previewResult = thermalRecorder.startPreview()
                previewResult shouldBe true
            }
        }

        it("should apply thermal settings correctly on initialization") {
            runTest {
                thermalRecorder.initialize()

                verify { mockLogger.info(any<String>()) }
            }
        }

        it("should get thermal camera status correctly") {
            runTest {
                val status = thermalRecorder.getThermalCameraStatus()

                status.width shouldBe 256
                status.height shouldBe 192
                status.frameRate shouldBe 25
                status.isRecording shouldBe false
            }
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

                verify { mockLogger.warning("Recording already in progress") }
            }
        }

        it("should handle session cleanup on recording failure") {
            runTest {
                thermalRecorder.initialize()

                every { mockSessionManager.getSessionFilePaths() } throws RuntimeException("Storage full")

                val result = thermalRecorder.startRecording(testSessionId)

                result shouldBe false
                verify { mockLogger.error(any<String>()) }
            }
        }

        it("should handle resource cleanup properly") {
            runTest {
                thermalRecorder.initialize()
                thermalRecorder.startRecording(testSessionId)
                thermalRecorder.startPreview()

                thermalRecorder.cleanup()

                thermalRecorder.getThermalCameraStatus().isRecording shouldBe false
                verify { mockLogger.info("ThermalRecorder cleanup completed") }
            }
        }
    }

    describe("ThermalRecorder device status and validation") {

        it("should provide correct device status information") {
            runTest {
                thermalRecorder.initialize()

                val status = thermalRecorder.getThermalCameraStatus()

                status.width shouldBe 256
                status.height shouldBe 192
                status.frameRate shouldBe 25
                status.frameCount shouldBe 0L
            }
        }

        it("should handle thermal camera validation correctly") {
            runTest {
                val initResult = thermalRecorder.initialize()
                initResult shouldBe true

                val status = thermalRecorder.getThermalCameraStatus()
                status shouldNotBe null
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
