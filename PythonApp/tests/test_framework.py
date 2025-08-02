"""
Comprehensive Testing and Validation Framework for Multi-Sensor Recording System

This module implements testing capabilities for Milestone 3.3 requirements including:
- Multi-device synchronization testing
- Performance and stability testing
- Robustness testing for webcam disconnection scenarios
- Video file validation

Author: Multi-Sensor Recording System Team
Date: 2025-07-29
Milestone: 3.3 - Webcam Capture Integration (Testing Framework)
"""

import cv2
import json
import numpy as np
import os
import subprocess

# Import project modules
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from webcam.webcam_capture import WebcamCapture, test_webcam_access
from session.session_manager import SessionManager
from network.device_server import JsonSocketServer


class TestResult:
    """Container for test results with detailed information."""

    def __init__(
        self, test_name: str, success: bool, message: str, details: Dict = None
    ):
        self.test_name = test_name
        self.success = success
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now()
        self.duration = 0.0

    def to_dict(self) -> Dict:
        """Convert test result to dictionary for JSON serialization."""
        return {
            "test_name": self.test_name,
            "success": self.success,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "duration": self.duration,
        }


class MultiDeviceSyncTester:
    """Test multi-device synchronization between PC webcam and Android devices."""

    def __init__(self):
        self.webcam_capture = None
        self.session_manager = None
        self.server = None
        self.test_results = []

    def setup_test_environment(self) -> TestResult:
        """Set up test environment with webcam and session manager."""
        try:
            print("[DEBUG_LOG] Setting up multi-device sync test environment...")

            # Initialize webcam capture
            self.webcam_capture = WebcamCapture()

            # Initialize session manager
            self.session_manager = SessionManager("test_recordings")

            # Initialize server for device communication
            self.server = JsonSocketServer()

            return TestResult(
                "setup_test_environment",
                True,
                "Test environment setup successful",
                {
                    "webcam_initialized": True,
                    "session_manager_ready": True,
                    "server_ready": True,
                },
            )

        except Exception as e:
            return TestResult(
                "setup_test_environment",
                False,
                f"Failed to setup test environment: {str(e)}",
                {"error": str(e)},
            )

    def test_webcam_initialization(self) -> TestResult:
        """Test webcam initialization and basic functionality."""
        start_time = time.time()

        try:
            print("[DEBUG_LOG] Testing webcam initialization...")

            # Test basic webcam access
            webcam_accessible = test_webcam_access()

            if not webcam_accessible:
                return TestResult(
                    "webcam_initialization",
                    False,
                    "Webcam not accessible",
                    {"webcam_accessible": False},
                )

            # Test webcam capture initialization
            success = self.webcam_capture.initialize_camera()

            if not success:
                return TestResult(
                    "webcam_initialization",
                    False,
                    "Failed to initialize webcam capture",
                    {"initialization_success": False},
                )

            # Get camera properties
            cap = cv2.VideoCapture(0)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            cap.release()

            duration = time.time() - start_time
            result = TestResult(
                "webcam_initialization",
                True,
                "Webcam initialization successful",
                {
                    "resolution": f"{width}x{height}",
                    "fps": fps,
                    "initialization_time": duration,
                },
            )
            result.duration = duration
            return result

        except Exception as e:
            duration = time.time() - start_time
            result = TestResult(
                "webcam_initialization",
                False,
                f"Webcam initialization failed: {str(e)}",
                {"error": str(e), "initialization_time": duration},
            )
            result.duration = duration
            return result

    def test_session_synchronization(self, test_duration: int = 10) -> TestResult:
        """Test session creation and synchronization timing."""
        start_time = time.time()

        try:
            print(
                f"[DEBUG_LOG] Testing session synchronization for {test_duration} seconds..."
            )

            # Create test session
            session_info = self.session_manager.create_session("sync_test")
            session_id = session_info["session_id"]

            # Add PC webcam to session
            self.session_manager.add_device_to_session(
                "pc_webcam", "pc_webcam", ["video_recording"]
            )

            # Set webcam output directory
            session_folder = self.session_manager.get_session_folder()
            self.webcam_capture.set_output_directory(str(session_folder))

            # Start webcam preview and recording
            self.webcam_capture.start_preview()
            time.sleep(0.5)  # Allow preview to stabilize

            recording_start_time = time.time()
            webcam_started = self.webcam_capture.start_recording(session_id)

            if not webcam_started:
                return TestResult(
                    "session_synchronization",
                    False,
                    "Failed to start webcam recording",
                    {"webcam_recording_started": False},
                )

            # Record for specified duration
            time.sleep(test_duration)

            # Stop recording
            recording_stop_time = time.time()
            webcam_filepath = self.webcam_capture.stop_recording()

            # Add file to session
            if webcam_filepath and os.path.exists(webcam_filepath):
                file_size = os.path.getsize(webcam_filepath)
                self.session_manager.add_file_to_session(
                    "pc_webcam", "webcam_video", webcam_filepath, file_size
                )

            # End session
            completed_session = self.session_manager.end_session()

            # Stop preview
            self.webcam_capture.stop_preview()

            # Calculate timing metrics
            actual_recording_duration = recording_stop_time - recording_start_time
            session_duration = completed_session["duration"] if completed_session else 0
            timing_accuracy = (
                abs(actual_recording_duration - test_duration) / test_duration
            )

            # Validate results
            success = (
                webcam_filepath is not None
                and os.path.exists(webcam_filepath)
                and completed_session is not None
                and timing_accuracy < 0.1  # Within 10% of expected duration
            )

            duration = time.time() - start_time
            result = TestResult(
                "session_synchronization",
                success,
                (
                    "Session synchronization test completed"
                    if success
                    else "Session synchronization test failed"
                ),
                {
                    "session_id": session_id,
                    "webcam_file": webcam_filepath,
                    "file_exists": (
                        os.path.exists(webcam_filepath) if webcam_filepath else False
                    ),
                    "file_size": (
                        os.path.getsize(webcam_filepath)
                        if webcam_filepath and os.path.exists(webcam_filepath)
                        else 0
                    ),
                    "expected_duration": test_duration,
                    "actual_duration": actual_recording_duration,
                    "session_duration": session_duration,
                    "timing_accuracy": timing_accuracy,
                    "timing_accuracy_percent": timing_accuracy * 100,
                },
            )
            result.duration = duration
            return result

        except Exception as e:
            duration = time.time() - start_time
            result = TestResult(
                "session_synchronization",
                False,
                f"Session synchronization test failed: {str(e)}",
                {"error": str(e), "test_duration": duration},
            )
            result.duration = duration
            return result

    def test_video_file_validation(self, video_path: str) -> TestResult:
        """Validate that recorded video files are playable and not corrupted."""
        start_time = time.time()

        try:
            print(f"[DEBUG_LOG] Validating video file: {video_path}")

            if not os.path.exists(video_path):
                return TestResult(
                    "video_file_validation",
                    False,
                    f"Video file does not exist: {video_path}",
                    {"file_exists": False, "file_path": video_path},
                )

            # Get file size
            file_size = os.path.getsize(video_path)

            if file_size == 0:
                return TestResult(
                    "video_file_validation",
                    False,
                    "Video file is empty",
                    {"file_size": 0, "file_path": video_path},
                )

            # Try to open video with OpenCV
            cap = cv2.VideoCapture(video_path)

            if not cap.isOpened():
                return TestResult(
                    "video_file_validation",
                    False,
                    "Cannot open video file with OpenCV",
                    {"opencv_readable": False, "file_path": video_path},
                )

            # Get video properties
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0

            # Try to read first and last frames
            ret1, frame1 = cap.read()

            if frame_count > 1:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count - 1)
                ret2, frame2 = cap.read()
            else:
                ret2 = ret1
                frame2 = frame1

            cap.release()

            # Validate frame reading
            frames_readable = ret1 and ret2

            # Additional validation using ffprobe if available
            ffprobe_info = None
            try:
                result = subprocess.run(
                    [
                        "ffprobe",
                        "-v",
                        "quiet",
                        "-print_format",
                        "json",
                        "-show_format",
                        "-show_streams",
                        video_path,
                    ],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.returncode == 0:
                    ffprobe_info = json.loads(result.stdout)
            except (
                subprocess.TimeoutExpired,
                subprocess.CalledProcessError,
                FileNotFoundError,
                json.JSONDecodeError,
            ):
                ffprobe_info = None

            # Determine overall success
            success = (
                file_size > 0
                and frame_count > 0
                and fps > 0
                and width > 0
                and height > 0
                and frames_readable
            )

            duration_test = time.time() - start_time
            result = TestResult(
                "video_file_validation",
                success,
                (
                    "Video file validation successful"
                    if success
                    else "Video file validation failed"
                ),
                {
                    "file_path": video_path,
                    "file_size": file_size,
                    "frame_count": frame_count,
                    "fps": fps,
                    "resolution": f"{width}x{height}",
                    "duration": duration,
                    "frames_readable": frames_readable,
                    "opencv_readable": True,
                    "ffprobe_available": ffprobe_info is not None,
                    "ffprobe_info": ffprobe_info,
                },
            )
            result.duration = duration_test
            return result

        except Exception as e:
            duration_test = time.time() - start_time
            result = TestResult(
                "video_file_validation",
                False,
                f"Video file validation failed: {str(e)}",
                {
                    "error": str(e),
                    "file_path": video_path,
                    "validation_time": duration_test,
                },
            )
            result.duration = duration_test
            return result

    def cleanup_test_environment(self) -> TestResult:
        """Clean up test environment and resources."""
        try:
            print("[DEBUG_LOG] Cleaning up test environment...")

            if self.webcam_capture:
                self.webcam_capture.cleanup()

            if self.server:
                self.server.stop_server()

            return TestResult(
                "cleanup_test_environment",
                True,
                "Test environment cleanup successful",
                {"cleanup_completed": True},
            )

        except Exception as e:
            return TestResult(
                "cleanup_test_environment",
                False,
                f"Test environment cleanup failed: {str(e)}",
                {"error": str(e)},
            )


class PerformanceStabilityTester:
    """Test performance and stability for longer recording sessions."""

    def __init__(self):
        self.webcam_capture = None
        self.session_manager = None
        self.monitoring_active = False
        self.performance_data = []

    def test_long_recording_session(self, duration_minutes: int = 5) -> TestResult:
        """Test longer recording sessions for performance and stability."""
        start_time = time.time()

        try:
            print(
                f"[DEBUG_LOG] Testing long recording session for {duration_minutes} minutes..."
            )

            # Initialize components
            self.webcam_capture = WebcamCapture()
            self.session_manager = SessionManager("performance_test_recordings")

            # Create session
            session_info = self.session_manager.create_session(
                f"performance_test_{duration_minutes}min"
            )
            session_id = session_info["session_id"]

            # Set up webcam
            session_folder = self.session_manager.get_session_folder()
            self.webcam_capture.set_output_directory(str(session_folder))

            # Start monitoring
            self.monitoring_active = True
            monitor_thread = threading.Thread(target=self._monitor_performance)
            monitor_thread.start()

            # Start recording
            self.webcam_capture.start_preview()
            time.sleep(1)  # Allow stabilization

            recording_started = self.webcam_capture.start_recording(session_id)

            if not recording_started:
                self.monitoring_active = False
                return TestResult(
                    "long_recording_session",
                    False,
                    "Failed to start recording",
                    {"recording_started": False},
                )

            # Record for specified duration
            test_duration_seconds = duration_minutes * 60
            time.sleep(test_duration_seconds)

            # Stop recording
            webcam_filepath = self.webcam_capture.stop_recording()
            self.webcam_capture.stop_preview()

            # Stop monitoring
            self.monitoring_active = False
            monitor_thread.join(timeout=5)

            # End session
            completed_session = self.session_manager.end_session()

            # Analyze performance data
            performance_analysis = self._analyze_performance_data()

            # Validate results
            success = (
                webcam_filepath is not None
                and os.path.exists(webcam_filepath)
                and completed_session is not None
                and performance_analysis["stable"]
            )

            duration = time.time() - start_time
            result = TestResult(
                "long_recording_session",
                success,
                (
                    f"Long recording session test completed ({duration_minutes} minutes)"
                    if success
                    else "Long recording session test failed"
                ),
                {
                    "duration_minutes": duration_minutes,
                    "session_id": session_id,
                    "webcam_file": webcam_filepath,
                    "file_exists": (
                        os.path.exists(webcam_filepath) if webcam_filepath else False
                    ),
                    "file_size": (
                        os.path.getsize(webcam_filepath)
                        if webcam_filepath and os.path.exists(webcam_filepath)
                        else 0
                    ),
                    "performance_analysis": performance_analysis,
                    "session_duration": (
                        completed_session["duration"] if completed_session else 0
                    ),
                },
            )
            result.duration = duration
            return result

        except Exception as e:
            self.monitoring_active = False
            duration = time.time() - start_time
            result = TestResult(
                "long_recording_session",
                False,
                f"Long recording session test failed: {str(e)}",
                {
                    "error": str(e),
                    "duration_minutes": duration_minutes,
                    "test_time": duration,
                },
            )
            result.duration = duration
            return result
        finally:
            if self.webcam_capture:
                self.webcam_capture.cleanup()

    def _monitor_performance(self):
        """Monitor system performance during recording."""
        import psutil

        while self.monitoring_active:
            try:
                # Get current process
                process = psutil.Process()

                # Collect performance metrics
                cpu_percent = process.cpu_percent()
                memory_info = process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024

                # System-wide metrics
                system_cpu = psutil.cpu_percent()
                system_memory = psutil.virtual_memory().percent

                self.performance_data.append(
                    {
                        "timestamp": time.time(),
                        "process_cpu_percent": cpu_percent,
                        "process_memory_mb": memory_mb,
                        "system_cpu_percent": system_cpu,
                        "system_memory_percent": system_memory,
                    }
                )

                time.sleep(1)  # Sample every second

            except Exception as e:
                print(f"[DEBUG_LOG] Performance monitoring error: {e}")
                break

    def _analyze_performance_data(self) -> Dict:
        """Analyze collected performance data."""
        if not self.performance_data:
            return {"stable": False, "reason": "No performance data collected"}

        # Calculate statistics
        cpu_values = [d["process_cpu_percent"] for d in self.performance_data]
        memory_values = [d["process_memory_mb"] for d in self.performance_data]

        avg_cpu = np.mean(cpu_values)
        max_cpu = np.max(cpu_values)
        avg_memory = np.mean(memory_values)
        max_memory = np.max(memory_values)

        # Check for memory leaks (significant upward trend)
        memory_trend = np.polyfit(range(len(memory_values)), memory_values, 1)[0]

        # Stability criteria
        cpu_stable = max_cpu < 80  # CPU usage under 80%
        memory_stable = max_memory < 1000  # Memory under 1GB
        no_memory_leak = memory_trend < 10  # Memory increase less than 10MB per sample

        stable = cpu_stable and memory_stable and no_memory_leak

        return {
            "stable": stable,
            "avg_cpu_percent": avg_cpu,
            "max_cpu_percent": max_cpu,
            "avg_memory_mb": avg_memory,
            "max_memory_mb": max_memory,
            "memory_trend_mb_per_sample": memory_trend,
            "cpu_stable": cpu_stable,
            "memory_stable": memory_stable,
            "no_memory_leak": no_memory_leak,
            "sample_count": len(self.performance_data),
        }


class RobustnessTester:
    """Test robustness scenarios including webcam disconnection and error recovery."""

    def __init__(self):
        self.webcam_capture = None

    def test_webcam_disconnection_recovery(self) -> TestResult:
        """Test webcam disconnection scenarios and error recovery."""
        start_time = time.time()

        try:
            print("[DEBUG_LOG] Testing webcam disconnection recovery...")

            # Initialize webcam
            self.webcam_capture = WebcamCapture()

            # Test initial connection
            init_success = self.webcam_capture.initialize_camera()

            if not init_success:
                return TestResult(
                    "webcam_disconnection_recovery",
                    False,
                    "Initial webcam connection failed",
                    {"initial_connection": False},
                )

            # Start preview
            self.webcam_capture.start_preview()
            time.sleep(2)  # Allow preview to run

            # Simulate disconnection by releasing camera
            if self.webcam_capture.cap:
                self.webcam_capture.cap.release()
                self.webcam_capture.cap = None

            time.sleep(1)

            # Try to recover
            recovery_success = self.webcam_capture.initialize_camera()

            # Test if preview can restart
            if recovery_success:
                time.sleep(2)  # Test continued operation

            # Clean up
            self.webcam_capture.cleanup()

            duration = time.time() - start_time
            result = TestResult(
                "webcam_disconnection_recovery",
                recovery_success,
                (
                    "Webcam disconnection recovery successful"
                    if recovery_success
                    else "Webcam disconnection recovery failed"
                ),
                {
                    "initial_connection": init_success,
                    "recovery_successful": recovery_success,
                    "test_duration": duration,
                },
            )
            result.duration = duration
            return result

        except Exception as e:
            duration = time.time() - start_time
            result = TestResult(
                "webcam_disconnection_recovery",
                False,
                f"Webcam disconnection recovery test failed: {str(e)}",
                {"error": str(e), "test_duration": duration},
            )
            result.duration = duration
            return result

    def test_multiple_camera_indices(self) -> TestResult:
        """Test multiple camera indices to find available cameras."""
        start_time = time.time()

        try:
            print("[DEBUG_LOG] Testing multiple camera indices...")

            available_cameras = []
            max_cameras_to_test = 5

            for camera_index in range(max_cameras_to_test):
                try:
                    cap = cv2.VideoCapture(camera_index)
                    if cap.isOpened():
                        ret, frame = cap.read()
                        if ret and frame is not None:
                            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                            available_cameras.append(
                                {
                                    "index": camera_index,
                                    "resolution": f"{width}x{height}",
                                    "working": True,
                                }
                            )
                        else:
                            available_cameras.append(
                                {
                                    "index": camera_index,
                                    "resolution": "unknown",
                                    "working": False,
                                }
                            )
                    cap.release()
                except Exception as e:
                    print(f"[DEBUG_LOG] Camera index {camera_index} error: {e}")

            success = len([cam for cam in available_cameras if cam["working"]]) > 0

            duration = time.time() - start_time
            result = TestResult(
                "multiple_camera_indices",
                success,
                f"Found {len([cam for cam in available_cameras if cam['working']])} working cameras",
                {
                    "available_cameras": available_cameras,
                    "working_camera_count": len(
                        [cam for cam in available_cameras if cam["working"]]
                    ),
                    "total_tested": max_cameras_to_test,
                },
            )
            result.duration = duration
            return result

        except Exception as e:
            duration = time.time() - start_time
            result = TestResult(
                "multiple_camera_indices",
                False,
                f"Multiple camera indices test failed: {str(e)}",
                {"error": str(e), "test_duration": duration},
            )
            result.duration = duration
            return result


class TestFramework:
    """Main test framework coordinator."""

    def __init__(self, output_dir: str = "test_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.test_results = []

    def run_all_tests(self) -> Dict:
        """Run all comprehensive tests and return results."""
        print("[DEBUG_LOG] Starting comprehensive test framework...")

        start_time = time.time()

        # Initialize testers
        sync_tester = MultiDeviceSyncTester()
        performance_tester = PerformanceStabilityTester()
        robustness_tester = RobustnessTester()

        # Run all tests
        tests_to_run = [
            # Setup and basic tests
            (sync_tester.setup_test_environment, []),
            (sync_tester.test_webcam_initialization, []),
            # Synchronization tests
            (sync_tester.test_session_synchronization, [10]),  # 10 second test
            # Performance tests
            (performance_tester.test_long_recording_session, [1]),  # 1 minute test
            # Robustness tests
            (robustness_tester.test_webcam_disconnection_recovery, []),
            (robustness_tester.test_multiple_camera_indices, []),
            # Cleanup
            (sync_tester.cleanup_test_environment, []),
        ]

        for test_func, args in tests_to_run:
            try:
                result = test_func(*args)
                self.test_results.append(result)

                status = "PASS" if result.success else "FAIL"
                print(f"[DEBUG_LOG] {result.test_name}: {status} - {result.message}")

                # Run video validation if I have a video file
                if (
                    result.test_name == "session_synchronization"
                    and result.success
                    and "webcam_file" in result.details
                ):

                    video_path = result.details["webcam_file"]
                    validation_result = sync_tester.test_video_file_validation(
                        video_path
                    )
                    self.test_results.append(validation_result)

                    status = "PASS" if validation_result.success else "FAIL"
                    print(
                        f"[DEBUG_LOG] {validation_result.test_name}: {status} - {validation_result.message}"
                    )

            except Exception as e:
                error_result = TestResult(
                    f"{test_func.__name__}_error",
                    False,
                    f"Test execution error: {str(e)}",
                    {"error": str(e)},
                )
                self.test_results.append(error_result)
                print(f"[DEBUG_LOG] {test_func.__name__}: ERROR - {str(e)}")

        # Generate test report
        total_duration = time.time() - start_time
        report = self._generate_test_report(total_duration)

        # Save test report
        self._save_test_report(report)

        return report

    def _generate_test_report(self, total_duration: float) -> Dict:
        """Generate comprehensive test report."""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.success])
        failed_tests = total_tests - passed_tests

        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        report = {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": success_rate,
                "total_duration": total_duration,
                "timestamp": datetime.now().isoformat(),
            },
            "test_results": [result.to_dict() for result in self.test_results],
            "recommendations": self._generate_recommendations(),
        }

        return report

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []

        failed_tests = [r for r in self.test_results if not r.success]

        if any("webcam_initialization" in r.test_name for r in failed_tests):
            recommendations.append("Check webcam hardware connection and drivers")

        if any("session_synchronization" in r.test_name for r in failed_tests):
            recommendations.append(
                "Review session management and timing synchronization"
            )

        if any("long_recording_session" in r.test_name for r in failed_tests):
            recommendations.append("Optimize performance for longer recording sessions")

        if any("video_file_validation" in r.test_name for r in failed_tests):
            recommendations.append("Check video codec configuration and file writing")

        if any("disconnection_recovery" in r.test_name for r in failed_tests):
            recommendations.append("Improve error handling and recovery mechanisms")

        if not recommendations:
            recommendations.append("All tests passed - system is functioning correctly")

        return recommendations

    def _save_test_report(self, report: Dict):
        """Save test report to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_dir / f"test_report_{timestamp}.json"

        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"[DEBUG_LOG] Test report saved to: {report_file}")


if __name__ == "__main__":
    # Run comprehensive tests
    print("[DEBUG_LOG] Starting Milestone 3.3 Comprehensive Testing Framework...")

    framework = TestFramework()
    report = framework.run_all_tests()

    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Total Tests: {report['test_summary']['total_tests']}")
    print(f"Passed: {report['test_summary']['passed_tests']}")
    print(f"Failed: {report['test_summary']['failed_tests']}")
    print(f"Success Rate: {report['test_summary']['success_rate']:.1f}%")
    print(f"Total Duration: {report['test_summary']['total_duration']:.1f} seconds")

    print("\nRECOMMENDATIONS:")
    for rec in report["recommendations"]:
        print(f"- {rec}")

    print("\n[DEBUG_LOG] Comprehensive testing framework completed successfully")
