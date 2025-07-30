"""
Real-time Calibration Feedback System

Provides live quality scoring and feedback for calibration processes using
the CalibrationQualityAssessment system with camera feeds and user guidance.

Features:
- Real-time camera feed processing
- Live quality scoring display
- Interactive calibration guidance
- Multi-camera coordination
- Quality trend analysis

Author: Multi-Sensor Recording System
Date: 2025-07-30
"""

import cv2
import logging
import numpy as np
import time
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QPixmap, QImage, QFont
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QTextEdit,
    QGroupBox,
)
from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Callable, Any, Tuple

# Import calibration quality assessment
from calibration_quality_assessment import (
    CalibrationQualityAssessment,
    CalibrationQualityResult,
    PatternType,
)


@dataclass
class CalibrationFeedback:
    """Real-time calibration feedback data"""

    timestamp: float
    quality_score: float
    is_acceptable: bool
    primary_issue: str
    recommendations: List[str]
    pattern_detected: bool
    sharpness_score: float
    contrast_score: float
    alignment_score: Optional[float] = None


@dataclass
class CameraFeedConfig:
    """Configuration for camera feed processing"""

    camera_id: int
    camera_name: str
    pattern_type: PatternType
    target_fps: int = 30
    resolution: Tuple[int, int] = (640, 480)
    enable_preview: bool = True
    quality_threshold: float = 0.7


class CalibrationFeedbackProcessor(QThread):
    """Background thread for processing calibration feedback"""

    # Signals for UI updates
    feedback_updated = pyqtSignal(str, CalibrationFeedback)  # camera_name, feedback
    frame_processed = pyqtSignal(str, np.ndarray)  # camera_name, frame
    error_occurred = pyqtSignal(str, str)  # camera_name, error_message

    def __init__(self, config: CameraFeedConfig, logger=None):
        super().__init__()
        self.config = config
        self.logger = logger or logging.getLogger(__name__)

        # Processing components
        self.quality_assessment = CalibrationQualityAssessment(logger=self.logger)
        self.camera = None
        self.is_running = False
        self.reference_image = None

        # Quality tracking
        self.quality_history = deque(maxlen=100)  # Last 100 measurements
        self.feedback_callbacks: List[Callable[[CalibrationFeedback], None]] = []

        # Performance tracking
        self.frame_count = 0
        self.start_time = time.time()
        self.processing_times = deque(maxlen=50)

    def set_reference_image(self, reference_image: np.ndarray):
        """Set reference image for alignment assessment"""
        self.reference_image = reference_image.copy()
        self.logger.info(f"Reference image set for {self.config.camera_name}")

    def add_feedback_callback(self, callback: Callable[[CalibrationFeedback], None]):
        """Add callback for feedback updates"""
        self.feedback_callbacks.append(callback)

    def start_processing(self):
        """Start camera processing"""
        try:
            self.logger.info(
                f"Starting calibration feedback for {self.config.camera_name}"
            )

            # Initialize camera
            self.camera = cv2.VideoCapture(self.config.camera_id)
            if not self.camera.isOpened():
                raise RuntimeError(f"Failed to open camera {self.config.camera_id}")

            # Configure camera
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.resolution[0])
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.resolution[1])
            self.camera.set(cv2.CAP_PROP_FPS, self.config.target_fps)

            self.is_running = True
            self.start_time = time.time()
            self.start()

        except Exception as e:
            error_msg = f"Error starting camera processing: {e}"
            self.logger.error(error_msg)
            self.error_occurred.emit(self.config.camera_name, error_msg)

    def stop_processing(self):
        """Stop camera processing"""
        self.is_running = False
        if self.camera:
            self.camera.release()
        self.wait()
        self.logger.info(f"Stopped calibration feedback for {self.config.camera_name}")

    def run(self):
        """Main processing loop"""
        frame_interval = 1.0 / self.config.target_fps
        last_frame_time = 0

        while self.is_running:
            try:
                current_time = time.time()

                # Control frame rate
                if current_time - last_frame_time < frame_interval:
                    time.sleep(0.001)
                    continue

                # Capture frame
                ret, frame = self.camera.read()
                if not ret:
                    continue

                last_frame_time = current_time
                self.frame_count += 1

                # Process frame for quality assessment
                processing_start = time.time()
                feedback = self._process_frame(frame)
                processing_time = (time.time() - processing_start) * 1000

                self.processing_times.append(processing_time)

                # Emit signals
                if self.config.enable_preview:
                    self.frame_processed.emit(self.config.camera_name, frame)

                self.feedback_updated.emit(self.config.camera_name, feedback)

                # Call callbacks
                for callback in self.feedback_callbacks:
                    try:
                        callback(feedback)
                    except Exception as e:
                        self.logger.error(f"Error in feedback callback: {e}")

            except Exception as e:
                error_msg = f"Error in processing loop: {e}"
                self.logger.error(error_msg)
                self.error_occurred.emit(self.config.camera_name, error_msg)
                time.sleep(0.1)

    def _process_frame(self, frame: np.ndarray) -> CalibrationFeedback:
        """Process single frame for calibration feedback"""
        try:
            # Perform quality assessment
            quality_result = self.quality_assessment.assess_calibration_quality(
                frame, self.config.pattern_type, self.reference_image
            )

            # Create feedback
            feedback = CalibrationFeedback(
                timestamp=time.time(),
                quality_score=quality_result.overall_quality_score,
                is_acceptable=quality_result.is_acceptable,
                primary_issue=self._identify_primary_issue(quality_result),
                recommendations=quality_result.recommendations,
                pattern_detected=quality_result.pattern_detection.pattern_found,
                sharpness_score=quality_result.sharpness_metrics.sharpness_score,
                contrast_score=quality_result.contrast_metrics.contrast_score,
                alignment_score=(
                    quality_result.alignment_metrics.alignment_score
                    if quality_result.alignment_metrics
                    else None
                ),
            )

            # Update quality history
            self.quality_history.append(feedback.quality_score)

            return feedback

        except Exception as e:
            self.logger.error(f"Error processing frame: {e}")
            return CalibrationFeedback(
                timestamp=time.time(),
                quality_score=0.0,
                is_acceptable=False,
                primary_issue="Processing Error",
                recommendations=["Error processing frame - check camera connection"],
                pattern_detected=False,
                sharpness_score=0.0,
                contrast_score=0.0,
            )

    def _identify_primary_issue(self, quality_result: CalibrationQualityResult) -> str:
        """Identify the primary issue affecting calibration quality"""
        if not quality_result.pattern_detection.pattern_found:
            return "Pattern Not Detected"
        elif quality_result.pattern_detection.pattern_score < 0.6:
            return "Poor Pattern Quality"
        elif quality_result.sharpness_metrics.sharpness_score < 0.3:
            return "Image Too Blurry"
        elif quality_result.contrast_metrics.contrast_score < 0.4:
            return "Low Contrast"
        elif (
            quality_result.alignment_metrics
            and quality_result.alignment_metrics.alignment_score < 0.5
        ):
            return "Poor Alignment"
        elif quality_result.overall_quality_score < 0.7:
            return "Overall Quality Low"
        else:
            return "Quality Acceptable"

    def get_performance_stats(self) -> Dict[str, float]:
        """Get processing performance statistics"""
        current_time = time.time()
        elapsed_time = current_time - self.start_time

        stats = {
            "fps": self.frame_count / elapsed_time if elapsed_time > 0 else 0,
            "avg_processing_time_ms": (
                np.mean(self.processing_times) if self.processing_times else 0
            ),
            "quality_trend": (
                np.mean(list(self.quality_history)[-10:])
                if len(self.quality_history) >= 10
                else 0
            ),
        }

        return stats


class RealTimeCalibrationWidget(QWidget):
    """Widget for displaying real-time calibration feedback"""

    def __init__(self, config: CameraFeedConfig, parent=None):
        super().__init__(parent)
        self.config = config
        self.processor = None
        self.current_feedback = None

        self.init_ui()
        self.setup_processor()

    def init_ui(self):
        """Initialize user interface"""
        layout = QVBoxLayout(self)

        # Camera info header
        header_layout = QHBoxLayout()
        self.camera_label = QLabel(f"Camera: {self.config.camera_name}")
        self.camera_label.setFont(QFont("Arial", 12, QFont.Bold))
        header_layout.addWidget(self.camera_label)

        self.status_label = QLabel("Initializing...")
        self.status_label.setAlignment(Qt.AlignRight)
        header_layout.addWidget(self.status_label)
        layout.addLayout(header_layout)

        # Preview area
        if self.config.enable_preview:
            preview_group = QGroupBox("Camera Preview")
            preview_layout = QVBoxLayout(preview_group)

            self.preview_label = QLabel()
            self.preview_label.setMinimumSize(320, 240)
            self.preview_label.setStyleSheet(
                "border: 1px solid gray; background-color: black;"
            )
            self.preview_label.setAlignment(Qt.AlignCenter)
            self.preview_label.setText("No Preview")
            preview_layout.addWidget(self.preview_label)

            layout.addWidget(preview_group)

        # Quality metrics
        metrics_group = QGroupBox("Quality Metrics")
        metrics_layout = QVBoxLayout(metrics_group)

        # Overall quality
        overall_layout = QHBoxLayout()
        overall_layout.addWidget(QLabel("Overall Quality:"))
        self.quality_progress = QProgressBar()
        self.quality_progress.setRange(0, 100)
        self.quality_progress.setValue(0)
        overall_layout.addWidget(self.quality_progress)
        self.quality_value_label = QLabel("0%")
        overall_layout.addWidget(self.quality_value_label)
        metrics_layout.addLayout(overall_layout)

        # Individual metrics
        self.sharpness_progress = self._create_metric_bar("Sharpness:", metrics_layout)
        self.contrast_progress = self._create_metric_bar("Contrast:", metrics_layout)
        self.pattern_progress = self._create_metric_bar("Pattern:", metrics_layout)

        layout.addWidget(metrics_group)

        # Status and recommendations
        status_group = QGroupBox("Status & Recommendations")
        status_layout = QVBoxLayout(status_group)

        self.primary_issue_label = QLabel("Primary Issue: Initializing")
        self.primary_issue_label.setFont(QFont("Arial", 10, QFont.Bold))
        status_layout.addWidget(self.primary_issue_label)

        self.recommendations_text = QTextEdit()
        self.recommendations_text.setMaximumHeight(100)
        self.recommendations_text.setReadOnly(True)
        status_layout.addWidget(self.recommendations_text)

        layout.addWidget(status_group)

        # Control buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_feedback)
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_feedback)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)

        self.capture_button = QPushButton("Capture Reference")
        self.capture_button.clicked.connect(self.capture_reference)
        self.capture_button.setEnabled(False)
        button_layout.addWidget(self.capture_button)

        layout.addLayout(button_layout)

    def _create_metric_bar(self, label_text: str, parent_layout) -> QProgressBar:
        """Create a metric progress bar"""
        layout = QHBoxLayout()
        layout.addWidget(QLabel(label_text))

        progress = QProgressBar()
        progress.setRange(0, 100)
        progress.setValue(0)
        layout.addWidget(progress)

        value_label = QLabel("0%")
        layout.addWidget(value_label)

        parent_layout.addLayout(layout)
        return progress

    def setup_processor(self):
        """Setup calibration feedback processor"""
        self.processor = CalibrationFeedbackProcessor(self.config)
        self.processor.feedback_updated.connect(self.update_feedback)
        self.processor.frame_processed.connect(self.update_preview)
        self.processor.error_occurred.connect(self.handle_error)

    def start_feedback(self):
        """Start real-time feedback"""
        try:
            self.processor.start_processing()
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.capture_button.setEnabled(True)
            self.status_label.setText("Running")
            self.status_label.setStyleSheet("color: green;")
        except Exception as e:
            self.handle_error(self.config.camera_name, str(e))

    def stop_feedback(self):
        """Stop real-time feedback"""
        if self.processor:
            self.processor.stop_processing()

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.capture_button.setEnabled(False)
        self.status_label.setText("Stopped")
        self.status_label.setStyleSheet("color: red;")

    def capture_reference(self):
        """Capture current frame as reference for alignment"""
        if self.processor and self.processor.camera:
            ret, frame = self.processor.camera.read()
            if ret:
                self.processor.set_reference_image(frame)
                self.status_label.setText("Reference Captured")

    def update_feedback(self, camera_name: str, feedback: CalibrationFeedback):
        """Update UI with new feedback"""
        if camera_name != self.config.camera_name:
            return

        self.current_feedback = feedback

        # Update progress bars
        quality_percent = int(feedback.quality_score * 100)
        self.quality_progress.setValue(quality_percent)
        self.quality_value_label.setText(f"{quality_percent}%")

        # Color code quality bar
        if feedback.is_acceptable:
            self.quality_progress.setStyleSheet(
                "QProgressBar::chunk { background-color: green; }"
            )
        elif feedback.quality_score > 0.5:
            self.quality_progress.setStyleSheet(
                "QProgressBar::chunk { background-color: orange; }"
            )
        else:
            self.quality_progress.setStyleSheet(
                "QProgressBar::chunk { background-color: red; }"
            )

        # Update individual metrics
        self.sharpness_progress.setValue(int(feedback.sharpness_score * 100))
        self.contrast_progress.setValue(int(feedback.contrast_score * 100))
        self.pattern_progress.setValue(100 if feedback.pattern_detected else 0)

        # Update status
        self.primary_issue_label.setText(f"Primary Issue: {feedback.primary_issue}")

        # Update recommendations
        recommendations_text = "\n".join(
            [f"• {rec}" for rec in feedback.recommendations]
        )
        self.recommendations_text.setText(recommendations_text)

    def update_preview(self, camera_name: str, frame: np.ndarray):
        """Update camera preview"""
        if camera_name != self.config.camera_name or not self.config.enable_preview:
            return

        try:
            # Convert frame to Qt format
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_image = QImage(
                frame.data, width, height, bytes_per_line, QImage.Format_RGB888
            ).rgbSwapped()

            # Scale to fit preview area
            pixmap = QPixmap.fromImage(q_image)
            scaled_pixmap = pixmap.scaled(
                self.preview_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )

            self.preview_label.setPixmap(scaled_pixmap)

        except Exception as e:
            logging.error(f"Error updating preview: {e}")

    def handle_error(self, camera_name: str, error_message: str):
        """Handle processing errors"""
        if camera_name == self.config.camera_name:
            self.status_label.setText(f"Error: {error_message}")
            self.status_label.setStyleSheet("color: red;")

            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.capture_button.setEnabled(False)

    def get_current_feedback(self) -> Optional[CalibrationFeedback]:
        """Get current calibration feedback"""
        return self.current_feedback

    def cleanup(self):
        """Clean up resources"""
        if self.processor:
            self.processor.stop_processing()


class MultiCameraCalibrationManager:
    """Manager for coordinating multiple camera calibration feedback"""

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.camera_widgets: Dict[str, RealTimeCalibrationWidget] = {}
        self.feedback_history: Dict[str, List[CalibrationFeedback]] = {}

    def add_camera(self, config: CameraFeedConfig) -> RealTimeCalibrationWidget:
        """Add camera for calibration feedback"""
        widget = RealTimeCalibrationWidget(config)
        self.camera_widgets[config.camera_name] = widget
        self.feedback_history[config.camera_name] = []

        # Add callback to track feedback history
        widget.processor.add_feedback_callback(
            lambda feedback, name=config.camera_name: self._track_feedback(
                name, feedback
            )
        )

        self.logger.info(f"Added camera for calibration feedback: {config.camera_name}")
        return widget

    def _track_feedback(self, camera_name: str, feedback: CalibrationFeedback):
        """Track feedback history for analysis"""
        if camera_name in self.feedback_history:
            self.feedback_history[camera_name].append(feedback)
            # Keep only recent history
            if len(self.feedback_history[camera_name]) > 1000:
                self.feedback_history[camera_name] = self.feedback_history[camera_name][
                    -500:
                ]

    def get_overall_quality_status(self) -> Dict[str, Any]:
        """Get overall quality status across all cameras"""
        status = {"cameras": {}, "overall_acceptable": True, "average_quality": 0.0}

        total_quality = 0.0
        camera_count = 0

        for camera_name, widget in self.camera_widgets.items():
            feedback = widget.get_current_feedback()
            if feedback:
                status["cameras"][camera_name] = {
                    "quality_score": feedback.quality_score,
                    "is_acceptable": feedback.is_acceptable,
                    "primary_issue": feedback.primary_issue,
                }

                total_quality += feedback.quality_score
                camera_count += 1

                if not feedback.is_acceptable:
                    status["overall_acceptable"] = False

        if camera_count > 0:
            status["average_quality"] = total_quality / camera_count

        return status

    def cleanup(self):
        """Clean up all camera widgets"""
        for widget in self.camera_widgets.values():
            widget.cleanup()
        self.camera_widgets.clear()
        self.feedback_history.clear()


if __name__ == "__main__":
    # Test real-time calibration feedback
    import sys
    from PyQt5.QtWidgets import QApplication

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    app = QApplication(sys.argv)

    # Create test configuration
    config = CameraFeedConfig(
        camera_id=0,
        camera_name="Test Camera",
        pattern_type=PatternType.CHESSBOARD,
        target_fps=15,
        resolution=(640, 480),
        enable_preview=True,
    )

    # Create widget
    widget = RealTimeCalibrationWidget(config)
    widget.show()

    sys.exit(app.exec_())
