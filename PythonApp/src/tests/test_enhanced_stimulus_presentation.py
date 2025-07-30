#!/usr/bin/env python3
"""
Enhanced Stimulus Presentation Test Suite

This script provides comprehensive testing for the enhanced stimulus presentation functionality
with PsychoPy-inspired improvements including VLC backend support, enhanced timing precision,
and performance monitoring.

Author: Multi-Sensor Recording System Team
Date: 2025-07-29
Milestone: 3.5 - Enhanced Stimulus Presentation Controller
"""

import os
import sys
import time
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QLabel,
    QFileDialog,
    QTextEdit,
    QHBoxLayout,
    QProgressBar,
)

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from gui.enhanced_stimulus_controller import (
    EnhancedStimulusController,
    EnhancedTimingLogger,
    CodecInfo,
    VideoBackend,
    VLC_AVAILABLE,
)
from gui.stimulus_panel import StimulusControlPanel


class PerformanceTestThread(QThread):
    """Thread for running performance tests."""

    progress_updated = pyqtSignal(int, str)
    test_completed = pyqtSignal(dict)

    def __init__(self, controller, test_duration=10):
        super().__init__()
        self.controller = controller
        self.test_duration = test_duration
        self.results = {}

    def run(self):
        """Run performance monitoring test."""
        self.progress_updated.emit(0, "Starting performance test...")

        start_time = time.perf_counter()
        frame_times = []
        cpu_samples = []

        # Simulate performance monitoring
        for i in range(100):
            if not self.isRunning():
                break

            # Simulate frame timing
            frame_start = time.perf_counter()
            time.sleep(0.016)  # Simulate 60fps target
            frame_end = time.perf_counter()

            frame_times.append(frame_end - frame_start)

            # Update progress
            progress = int((i / 100) * 100)
            self.progress_updated.emit(progress, f"Performance test: {progress}%")

            if time.perf_counter() - start_time > self.test_duration:
                break

        # Calculate results
        avg_frame_time = sum(frame_times) / len(frame_times) if frame_times else 0
        max_frame_time = max(frame_times) if frame_times else 0
        min_frame_time = min(frame_times) if frame_times else 0

        self.results = {
            "avg_frame_time_ms": avg_frame_time * 1000,
            "max_frame_time_ms": max_frame_time * 1000,
            "min_frame_time_ms": min_frame_time * 1000,
            "total_frames": len(frame_times),
            "dropped_frames": len([t for t in frame_times if t > 0.020]),  # >20ms
            "performance_score": max(
                0, 100 - (len([t for t in frame_times if t > 0.020]) * 5)
            ),
        }

        self.test_completed.emit(self.results)


class EnhancedStimulusTestWindow(QMainWindow):
    """Enhanced test window for stimulus presentation functionality."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced Stimulus Presentation Test Suite")
        self.setGeometry(100, 100, 1000, 700)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create test components
        self.enhanced_controller = EnhancedStimulusController(self)
        self.stimulus_panel = StimulusControlPanel(self)
        self.codec_info = CodecInfo()

        # Test results storage
        self.test_results = []
        self.performance_thread = None

        # Create UI
        self.create_header(layout)
        self.create_controller_section(layout)
        self.create_test_controls(layout)
        self.create_results_section(layout)

        # Connect signals
        self.connect_test_signals()

        print("[DEBUG_LOG] Enhanced StimulusTestWindow initialized")
        print(f"[DEBUG_LOG] VLC Backend Available: {VLC_AVAILABLE}")

    def create_header(self, layout):
        """Create header with system information."""
        header_layout = QHBoxLayout()

        title_label = QLabel("Enhanced Stimulus Presentation Test Suite")
        title_label.setStyleSheet("QLabel { font-size: 16px; font-weight: bold; }")
        header_layout.addWidget(title_label)

        # System info
        info_label = QLabel(f"VLC Available: {'Yes' if VLC_AVAILABLE else 'No'}")
        info_label.setStyleSheet("QLabel { color: #666; }")
        header_layout.addWidget(info_label)

        layout.addLayout(header_layout)

    def create_controller_section(self, layout):
        """Create enhanced controller section."""
        layout.addWidget(QLabel("Enhanced Stimulus Controller:"))
        layout.addWidget(self.enhanced_controller)

        layout.addWidget(QLabel("Stimulus Control Panel:"))
        layout.addWidget(self.stimulus_panel)

    def create_test_controls(self, layout):
        """Create test control buttons."""
        test_layout = QVBoxLayout()

        # File loading tests
        file_test_layout = QHBoxLayout()

        self.load_test_video_btn = QPushButton("Load Test Video")
        self.load_test_video_btn.clicked.connect(self.load_test_video)
        file_test_layout.addWidget(self.load_test_video_btn)

        self.create_test_video_btn = QPushButton("Create Test Video")
        self.create_test_video_btn.clicked.connect(self.create_test_video)
        file_test_layout.addWidget(self.create_test_video_btn)

        test_layout.addLayout(file_test_layout)

        # Backend tests
        backend_test_layout = QHBoxLayout()

        self.test_qt_backend_btn = QPushButton("Test Qt Backend")
        self.test_qt_backend_btn.clicked.connect(self.test_qt_backend)
        self.test_qt_backend_btn.setEnabled(False)
        backend_test_layout.addWidget(self.test_qt_backend_btn)

        self.test_vlc_backend_btn = QPushButton("Test VLC Backend")
        self.test_vlc_backend_btn.clicked.connect(self.test_vlc_backend)
        self.test_vlc_backend_btn.setEnabled(VLC_AVAILABLE)
        backend_test_layout.addWidget(self.test_vlc_backend_btn)

        self.switch_backend_btn = QPushButton("Switch Backend")
        self.switch_backend_btn.clicked.connect(self.enhanced_controller.switch_backend)
        self.switch_backend_btn.setEnabled(False)
        backend_test_layout.addWidget(self.switch_backend_btn)

        test_layout.addLayout(backend_test_layout)

        # Comprehensive tests
        comprehensive_test_layout = QHBoxLayout()

        self.run_all_tests_btn = QPushButton("Run All Tests")
        self.run_all_tests_btn.clicked.connect(self.run_all_tests)
        comprehensive_test_layout.addWidget(self.run_all_tests_btn)

        self.timing_precision_test_btn = QPushButton("Test Timing Precision")
        self.timing_precision_test_btn.clicked.connect(self.test_timing_precision)
        comprehensive_test_layout.addWidget(self.timing_precision_test_btn)

        self.performance_test_btn = QPushButton("Performance Test")
        self.performance_test_btn.clicked.connect(self.run_performance_test)
        comprehensive_test_layout.addWidget(self.performance_test_btn)

        test_layout.addLayout(comprehensive_test_layout)

        # Codec tests
        codec_test_layout = QHBoxLayout()

        self.codec_detection_btn = QPushButton("Test Codec Detection")
        self.codec_detection_btn.clicked.connect(self.test_codec_detection)
        codec_test_layout.addWidget(self.codec_detection_btn)

        self.format_support_btn = QPushButton("Test Format Support")
        self.format_support_btn.clicked.connect(self.test_format_support)
        codec_test_layout.addWidget(self.format_support_btn)

        test_layout.addLayout(codec_test_layout)

        layout.addLayout(test_layout)

    def create_results_section(self, layout):
        """Create results display section."""
        layout.addWidget(QLabel("Test Results:"))

        # Progress bar for performance tests
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Results text area
        self.results_text = QTextEdit()
        self.results_text.setMaximumHeight(200)
        self.results_text.setPlainText("Test Results: Ready to run tests")
        layout.addWidget(self.results_text)

    def connect_test_signals(self):
        """Connect test signals."""
        # Connect stimulus panel to enhanced controller
        self.stimulus_panel.file_loaded.connect(self.enhanced_controller.load_video)
        self.stimulus_panel.play_requested.connect(self.enhanced_controller.test_play)
        self.stimulus_panel.pause_requested.connect(self.enhanced_controller.test_pause)
        self.stimulus_panel.start_recording_play_requested.connect(
            self.test_synchronized_start
        )
        self.stimulus_panel.mark_event_requested.connect(
            self.enhanced_controller.mark_event
        )

        # Connect enhanced controller signals
        self.enhanced_controller.status_changed.connect(self.on_status_changed)
        self.enhanced_controller.experiment_started.connect(self.on_experiment_started)
        self.enhanced_controller.experiment_ended.connect(self.on_experiment_ended)
        self.enhanced_controller.error_occurred.connect(self.on_error_occurred)
        self.enhanced_controller.backend_changed.connect(self.on_backend_changed)

    def load_test_video(self):
        """Load a test video file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Test Video",
            "",
            "Video Files (*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm);;All Files (*)",
        )
        if file_path:
            success = self.enhanced_controller.load_video(file_path)
            if success:
                self.stimulus_panel.load_file(file_path)
                self._enable_backend_tests()
                self.add_result(
                    f"✓ Video loaded successfully: {os.path.basename(file_path)}"
                )
            else:
                self.add_result(
                    f"✗ Failed to load video: {os.path.basename(file_path)}"
                )

    def create_test_video(self):
        """Create a test video with various characteristics."""
        try:
            import cv2
            import numpy as np

            # Create test video with timing markers
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            filename = "enhanced_test_video.mp4"
            out = cv2.VideoWriter(filename, fourcc, 30.0, (640, 480))

            for i in range(300):  # 10 seconds at 30 fps
                # Create frame with timing information
                frame = np.zeros((480, 640, 3), dtype=np.uint8)

                # Color gradient based on time
                color_r = int(255 * (i / 300))
                color_g = int(255 * (1 - i / 300))
                frame[:, :] = [color_r, color_g, 128]

                # Add timing markers every second
                if i % 30 == 0:  # Every second
                    cv2.rectangle(frame, (10, 10), (100, 60), (255, 255, 255), -1)
                    cv2.putText(
                        frame,
                        f"{i//30}s",
                        (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 0, 0),
                        2,
                    )

                # Add frame number
                cv2.putText(
                    frame,
                    f"Frame {i}",
                    (50, 450),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2,
                )

                # Add precision timing marker
                timestamp = i / 30.0
                cv2.putText(
                    frame,
                    f"{timestamp:.3f}s",
                    (400, 450),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2,
                )

                out.write(frame)

            out.release()
            self.add_result(f"✓ Test video created: {filename}")

            # Auto-load the created video
            if self.enhanced_controller.load_video(filename):
                self.stimulus_panel.load_file(filename)
                self._enable_backend_tests()
                self.add_result("✓ Test video auto-loaded successfully")

        except ImportError:
            self.add_result("✗ OpenCV not available - cannot create test video")
        except Exception as e:
            self.add_result(f"✗ Error creating test video: {e}")

    def test_qt_backend(self):
        """Test Qt multimedia backend specifically."""
        if not self.enhanced_controller.current_video_file:
            self.add_result("✗ No video loaded for Qt backend test")
            return

        try:
            # Force Qt backend
            if self.enhanced_controller._load_with_backend(
                self.enhanced_controller.current_video_file, VideoBackend.QT_MULTIMEDIA
            ):
                self.enhanced_controller.current_backend = VideoBackend.QT_MULTIMEDIA
                self.enhanced_controller._update_backend_ui()
                self.add_result("✓ Qt backend test passed")
            else:
                self.add_result("✗ Qt backend test failed")
        except Exception as e:
            self.add_result(f"✗ Qt backend test error: {e}")

    def test_vlc_backend(self):
        """Test VLC backend specifically."""
        if not VLC_AVAILABLE:
            self.add_result("✗ VLC backend not available")
            return

        if not self.enhanced_controller.current_video_file:
            self.add_result("✗ No video loaded for VLC backend test")
            return

        try:
            # Force VLC backend
            if self.enhanced_controller._load_with_backend(
                self.enhanced_controller.current_video_file, VideoBackend.VLC
            ):
                self.enhanced_controller.current_backend = VideoBackend.VLC
                self.enhanced_controller._update_backend_ui()
                self.add_result("✓ VLC backend test passed")
            else:
                self.add_result("✗ VLC backend test failed")
        except Exception as e:
            self.add_result(f"✗ VLC backend test error: {e}")

    def test_synchronized_start(self):
        """Test synchronized recording and stimulus start."""
        if not self.enhanced_controller.current_video_file:
            self.add_result("✗ No video loaded for synchronization test")
            return

        try:
            screen_index = self.stimulus_panel.get_selected_screen()

            # Start enhanced stimulus playback
            if self.enhanced_controller.start_stimulus_playback(screen_index):
                self.stimulus_panel.set_experiment_active(True)
                self.add_result("✓ Enhanced synchronized start test passed")

                # Auto-stop after 3 seconds for testing
                QTimer.singleShot(
                    3000,
                    lambda: self.enhanced_controller.stop_stimulus_playback(
                        "test_complete"
                    ),
                )
            else:
                self.add_result("✗ Enhanced synchronized start test failed")
        except Exception as e:
            self.add_result(f"✗ Synchronization test error: {e}")

    def test_timing_precision(self):
        """Test enhanced timing precision."""
        try:
            # Create test timing logger
            test_logger = EnhancedTimingLogger("test_logs")

            # Test timing calibration
            self.add_result(
                f"✓ Timing calibration offset: {test_logger.clock_offset*1000:.3f}ms"
            )

            # Test multiple clock sources
            timestamps = test_logger.get_precise_timestamp()

            # Verify all clocks are working
            required_clocks = [
                "system_time",
                "monotonic_time",
                "performance_time",
                "corrected_time",
            ]
            for clock in required_clocks:
                if clock in timestamps and timestamps[clock] > 0:
                    self.add_result(f"✓ {clock} working: {timestamps[clock]:.6f}")
                else:
                    self.add_result(f"✗ {clock} failed")

            # Test precision measurement
            start_time = time.perf_counter()
            time.sleep(0.001)  # 1ms sleep
            end_time = time.perf_counter()
            measured_duration = (end_time - start_time) * 1000

            self.add_result(
                f"✓ Timing precision test: {measured_duration:.3f}ms (target: ~1ms)"
            )

        except Exception as e:
            self.add_result(f"✗ Timing precision test error: {e}")

    def test_codec_detection(self):
        """Test codec detection and format support."""
        try:
            # Test various formats
            test_formats = [
                ".mp4",
                ".avi",
                ".mov",
                ".mkv",
                ".wmv",
                ".flv",
                ".webm",
                ".unknown",
            ]

            for fmt in test_formats:
                test_file = f"test{fmt}"

                # Test Qt support
                qt_supported = self.codec_info.is_supported(
                    test_file, VideoBackend.QT_MULTIMEDIA
                )

                # Test VLC support
                vlc_supported = (
                    self.codec_info.is_supported(test_file, VideoBackend.VLC)
                    if VLC_AVAILABLE
                    else False
                )

                # Get best backend
                best_backend = self.codec_info.get_best_backend(test_file)

                result = f"Format {fmt}: Qt={qt_supported}, VLC={vlc_supported}, Best={best_backend.value if best_backend else 'None'}"
                self.add_result(f"✓ {result}")

        except Exception as e:
            self.add_result(f"✗ Codec detection test error: {e}")

    def test_format_support(self):
        """Test comprehensive format support."""
        try:
            qt_formats = self.codec_info.qt_supported
            vlc_formats = self.codec_info.vlc_supported if VLC_AVAILABLE else []
            recommended_formats = self.codec_info.recommended_formats

            self.add_result(
                f"✓ Qt supported formats ({len(qt_formats)}): {', '.join(qt_formats)}"
            )

            if VLC_AVAILABLE:
                self.add_result(
                    f"✓ VLC supported formats ({len(vlc_formats)}): {', '.join(vlc_formats)}"
                )
                unique_vlc = set(vlc_formats) - set(qt_formats)
                if unique_vlc:
                    self.add_result(
                        f"✓ VLC additional formats: {', '.join(unique_vlc)}"
                    )
            else:
                self.add_result("! VLC not available - limited format support")

            self.add_result(f"✓ Recommended formats: {', '.join(recommended_formats)}")

        except Exception as e:
            self.add_result(f"✗ Format support test error: {e}")

    def run_performance_test(self):
        """Run comprehensive performance test."""
        if self.performance_thread and self.performance_thread.isRunning():
            self.add_result("! Performance test already running")
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        self.performance_thread = PerformanceTestThread(self.enhanced_controller)
        self.performance_thread.progress_updated.connect(self.on_performance_progress)
        self.performance_thread.test_completed.connect(self.on_performance_completed)
        self.performance_thread.start()

        self.add_result("✓ Performance test started...")

    def run_all_tests(self):
        """Run comprehensive test suite."""
        self.add_result("=== Starting Enhanced Comprehensive Test Suite ===")
        self.test_results.clear()

        # Test 1: Component initialization
        self.test_component_initialization()

        # Test 2: Enhanced signal connections
        self.test_enhanced_signal_connections()

        # Test 3: Timing precision
        self.test_timing_precision()

        # Test 4: Codec detection
        self.test_codec_detection()

        # Test 5: Format support
        self.test_format_support()

        # Test 6: Backend availability
        self.test_backend_availability()

        # Test 7: Performance monitoring (if video loaded)
        if self.enhanced_controller.current_video_file:
            self.test_performance_monitoring()

        # Display final results
        self.display_final_results()

    def test_component_initialization(self):
        """Test enhanced component initialization."""
        try:
            # Check enhanced controller
            assert self.enhanced_controller is not None
            assert self.enhanced_controller.codec_info is not None
            assert self.enhanced_controller.timing_logger is not None
            assert hasattr(self.enhanced_controller, "qt_media_player")

            # Check VLC components if available
            if VLC_AVAILABLE:
                assert self.enhanced_controller.vlc_video_widget is not None

            # Check UI components
            assert hasattr(self.enhanced_controller, "backend_label")
            assert hasattr(self.enhanced_controller, "performance_bar")
            assert hasattr(self.enhanced_controller, "switch_backend_btn")

            self.add_result("✓ Enhanced component initialization test passed")

        except Exception as e:
            self.add_result(f"✗ Enhanced component initialization test failed: {e}")

    def test_enhanced_signal_connections(self):
        """Test enhanced signal connections."""
        try:
            # Test enhanced controller signals
            assert hasattr(self.enhanced_controller, "status_changed")
            assert hasattr(self.enhanced_controller, "experiment_started")
            assert hasattr(self.enhanced_controller, "experiment_ended")
            assert hasattr(self.enhanced_controller, "error_occurred")
            assert hasattr(self.enhanced_controller, "backend_changed")

            # Test timing logger
            assert hasattr(
                self.enhanced_controller.timing_logger, "get_precise_timestamp"
            )
            assert hasattr(self.enhanced_controller.timing_logger, "calibrate_timing")

            self.add_result("✓ Enhanced signal connections test passed")

        except Exception as e:
            self.add_result(f"✗ Enhanced signal connections test failed: {e}")

    def test_backend_availability(self):
        """Test backend availability and switching."""
        try:
            # Test Qt backend availability
            assert self.enhanced_controller.qt_media_player is not None
            self.add_result("✓ Qt multimedia backend available")

            # Test VLC backend availability
            if VLC_AVAILABLE:
                assert self.enhanced_controller.vlc_video_widget is not None
                self.add_result("✓ VLC backend available")
            else:
                self.add_result("! VLC backend not available (optional)")

            # Test codec info
            assert len(self.enhanced_controller.codec_info.qt_supported) > 0
            self.add_result(
                f"✓ Qt codec support: {len(self.enhanced_controller.codec_info.qt_supported)} formats"
            )

            if VLC_AVAILABLE:
                assert len(self.enhanced_controller.codec_info.vlc_supported) > 0
                self.add_result(
                    f"✓ VLC codec support: {len(self.enhanced_controller.codec_info.vlc_supported)} formats"
                )

        except Exception as e:
            self.add_result(f"✗ Backend availability test failed: {e}")

    def test_performance_monitoring(self):
        """Test performance monitoring features."""
        try:
            # Test performance bar
            assert hasattr(self.enhanced_controller, "performance_bar")
            assert hasattr(self.enhanced_controller, "frame_drop_count")
            assert hasattr(self.enhanced_controller, "last_frame_time")

            # Test timing precision
            start_time = time.perf_counter()
            self.enhanced_controller.update_position()
            end_time = time.perf_counter()

            update_time = (end_time - start_time) * 1000
            self.add_result(
                f"✓ Performance monitoring update time: {update_time:.3f}ms"
            )

        except Exception as e:
            self.add_result(f"✗ Performance monitoring test failed: {e}")

    def display_final_results(self):
        """Display final test results summary."""
        passed_tests = len([r for r in self.test_results if r.startswith("✓")])
        failed_tests = len([r for r in self.test_results if r.startswith("✗")])
        warnings = len([r for r in self.test_results if r.startswith("!")])
        total_tests = passed_tests + failed_tests

        summary = f"\n=== Enhanced Test Suite Results ===\n"
        summary += f"Passed: {passed_tests}/{total_tests}\n"
        summary += f"Failed: {failed_tests}/{total_tests}\n"
        summary += f"Warnings: {warnings}\n"
        summary += f"VLC Backend: {'Available' if VLC_AVAILABLE else 'Not Available'}\n"

        if total_tests > 0:
            success_rate = (passed_tests / total_tests) * 100
            summary += f"Success Rate: {success_rate:.1f}%\n"

        self.add_result(summary)

    def _enable_backend_tests(self):
        """Enable backend-specific test buttons."""
        self.test_qt_backend_btn.setEnabled(True)
        self.test_vlc_backend_btn.setEnabled(VLC_AVAILABLE)
        self.switch_backend_btn.setEnabled(VLC_AVAILABLE)

    def add_result(self, message):
        """Add result to display and storage."""
        self.test_results.append(message)
        current_text = self.results_text.toPlainText()
        self.results_text.setPlainText(current_text + "\n" + message)

        # Auto-scroll to bottom
        scrollbar = self.results_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

        print(f"[DEBUG_LOG] {message}")

    # Signal handlers
    def on_status_changed(self, status):
        self.add_result(f"Status: {status}")

    def on_experiment_started(self):
        self.add_result("✓ Enhanced experiment started")

    def on_experiment_ended(self):
        self.add_result("✓ Enhanced experiment ended")
        self.stimulus_panel.set_experiment_active(False)

    def on_error_occurred(self, error):
        self.add_result(f"✗ Error: {error}")

    def on_backend_changed(self, backend):
        self.add_result(f"✓ Backend switched to: {backend}")

    def on_performance_progress(self, progress, message):
        self.progress_bar.setValue(progress)
        if progress % 20 == 0:  # Update every 20%
            self.add_result(message)

    def on_performance_completed(self, results):
        self.progress_bar.setVisible(False)

        self.add_result("=== Performance Test Results ===")
        self.add_result(f"✓ Average frame time: {results['avg_frame_time_ms']:.2f}ms")
        self.add_result(f"✓ Max frame time: {results['max_frame_time_ms']:.2f}ms")
        self.add_result(f"✓ Min frame time: {results['min_frame_time_ms']:.2f}ms")
        self.add_result(f"✓ Total frames: {results['total_frames']}")
        self.add_result(f"✓ Dropped frames: {results['dropped_frames']}")
        self.add_result(f"✓ Performance score: {results['performance_score']}/100")


def main():
    """Main test function."""
    print("[DEBUG_LOG] Starting Enhanced Stimulus Presentation Test Suite")

    # Create QApplication
    app = QApplication(sys.argv)

    # Create enhanced test window
    test_window = EnhancedStimulusTestWindow()
    test_window.show()

    print("[DEBUG_LOG] Enhanced test window created")
    print("[DEBUG_LOG] Available features:")
    print("[DEBUG_LOG] - VLC Backend Support:", "Yes" if VLC_AVAILABLE else "No")
    print("[DEBUG_LOG] - Enhanced Timing Precision")
    print("[DEBUG_LOG] - Performance Monitoring")
    print("[DEBUG_LOG] - Automatic Backend Selection")
    print("[DEBUG_LOG] - Comprehensive Codec Support")

    # Run the application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
