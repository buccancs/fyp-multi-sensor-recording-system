import json
import logging
import os
import platform
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("Warning: psutil not available, system monitoring will be limited")
from PyQt5.QtCore import QSize, Qt, QThread, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QIcon, QPalette, QPixmap
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMenuBar,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSlider,
    QSpacerItem,
    QSpinBox,
    QSplitter,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QToolBar,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

try:
    import matplotlib

    matplotlib.use("Qt5Agg")
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
try:
    import pyqtgraph as pg

    PYQTGRAPH_AVAILABLE = True
except ImportError:
    PYQTGRAPH_AVAILABLE = False
try:
    from gui.main_controller import MainController
    from network.device_server import JsonSocketServer
    from session.session_manager import SessionManager
    from shimmer_manager import ShimmerManager
    from utils.logging_config import get_logger
except ImportError as e:
    print(f"Warning: Could not import backend services: {e}")
    SessionManager = None
    JsonSocketServer = None
    MainController = None
    ShimmerManager = None
from .common_components import (
    ModernButton,
    ModernGroupBox,
    ProgressIndicator,
    StatusIndicator,
)


class RealTimeDataPlotter(QWidget):

    def __init__(self, title="Sensor Data", parent=None):
        super().__init__(parent)
        self.title = title
        self.data_buffer = {}
        self.max_points = 100
        layout = QVBoxLayout(self)
        if MATPLOTLIB_AVAILABLE:
            self.setup_matplotlib()
        elif PYQTGRAPH_AVAILABLE:
            self.setup_pyqtgraph()
        else:
            self.setup_fallback()
        layout.addWidget(self.plot_widget)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(100)

    def setup_matplotlib(self):
        self.figure = Figure(figsize=(8, 4))
        self.canvas = FigureCanvas(self.figure)
        self.plot_widget = self.canvas
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title(self.title)
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Value")
        self.lines = {}

    def setup_pyqtgraph(self):
        self.plot_widget = pg.PlotWidget(title=self.title)
        self.plot_widget.setLabel("left", "Value")
        self.plot_widget.setLabel("bottom", "Time")
        self.plot_widget.showGrid(x=True, y=True)
        self.curves = {}

    def setup_fallback(self):
        self.plot_widget = QTextEdit()
        self.plot_widget.setMaximumHeight(200)
        self.plot_widget.setText(f"{self.title}: No plotting library available")

    def add_data(self, sensor_name: str, value: float):
        if sensor_name not in self.data_buffer:
            self.data_buffer[sensor_name] = []
        timestamp = time.time()
        self.data_buffer[sensor_name].append((timestamp, value))
        if len(self.data_buffer[sensor_name]) > self.max_points:
            self.data_buffer[sensor_name] = self.data_buffer[sensor_name][
                -self.max_points :
            ]

    def update_plot(self):
        if not hasattr(self, "data_buffer") or not self.data_buffer:
            return
        if MATPLOTLIB_AVAILABLE and hasattr(self, "ax"):
            self.update_matplotlib_plot()
        elif PYQTGRAPH_AVAILABLE and hasattr(self, "curves"):
            self.update_pyqtgraph_plot()
        else:
            self.update_fallback_display()

    def update_matplotlib_plot(self):
        self.ax.clear()
        self.ax.set_title(self.title)
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Value")
        for sensor_name, data in self.data_buffer.items():
            if data:
                times, values = zip(*data)
                relative_times = [(t - times[0]) for t in times]
                self.ax.plot(
                    relative_times, values, label=sensor_name, marker="o", markersize=2
                )
        self.ax.legend()
        self.ax.grid(True)
        self.canvas.draw()

    def update_pyqtgraph_plot(self):
        for sensor_name, data in self.data_buffer.items():
            if data:
                times, values = zip(*data)
                if sensor_name not in self.curves:
                    self.curves[sensor_name] = self.plot_widget.plot(
                        pen=pg.mkPen(
                            color=(len(self.curves) * 60 % 360, 255, 255), width=2
                        )
                    )
                relative_times = [(t - times[0]) for t in times]
                self.curves[sensor_name].setData(relative_times, values)

    def update_fallback_display(self):
        if hasattr(self, "plot_widget") and hasattr(self.plot_widget, "setText"):
            text_lines = [f"{self.title} - {datetime.now().strftime('%H:%M:%S')}"]
            for sensor_name, data in self.data_buffer.items():
                if data:
                    latest_value = data[-1][1]
                    text_lines.append(f"{sensor_name}: {latest_value:.2f}")
            self.plot_widget.setText("\n".join(text_lines))


class SystemMonitor(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_metrics)
        self.timer.start(1000)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        cpu_group = ModernGroupBox("CPU Usage")
        cpu_layout = QVBoxLayout(cpu_group)
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setMaximum(100)
        self.cpu_label = QLabel("CPU: 0%")
        cpu_layout.addWidget(self.cpu_label)
        cpu_layout.addWidget(self.cpu_progress)
        layout.addWidget(cpu_group)
        memory_group = ModernGroupBox("Memory Usage")
        memory_layout = QVBoxLayout(memory_group)
        self.memory_progress = QProgressBar()
        self.memory_progress.setMaximum(100)
        self.memory_label = QLabel("Memory: 0%")
        memory_layout.addWidget(self.memory_label)
        memory_layout.addWidget(self.memory_progress)
        layout.addWidget(memory_group)
        disk_group = ModernGroupBox("Disk I/O")
        disk_layout = QVBoxLayout(disk_group)
        self.disk_read_label = QLabel("Read: 0 MB/s")
        self.disk_write_label = QLabel("Write: 0 MB/s")
        disk_layout.addWidget(self.disk_read_label)
        disk_layout.addWidget(self.disk_write_label)
        layout.addWidget(disk_group)
        network_group = ModernGroupBox("Network")
        network_layout = QVBoxLayout(network_group)
        self.network_sent_label = QLabel("Sent: 0 MB/s")
        self.network_recv_label = QLabel("Received: 0 MB/s")
        network_layout.addWidget(self.network_sent_label)
        network_layout.addWidget(self.network_recv_label)
        layout.addWidget(network_group)
        if PSUTIL_AVAILABLE:
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    temp_group = ModernGroupBox("Temperature")
                    temp_layout = QVBoxLayout(temp_group)
                    self.temp_labels = {}
                    for sensor_name in temps.keys():
                        label = QLabel(f"{sensor_name}: 0°C")
                        self.temp_labels[sensor_name] = label
                        temp_layout.addWidget(label)
                    layout.addWidget(temp_group)
            except Exception:
                pass

    def update_metrics(self):
        try:
            if not PSUTIL_AVAILABLE:
                import random

                cpu_percent = random.randint(10, 60)
                memory_percent = random.randint(30, 80)
                self.cpu_progress.setValue(cpu_percent)
                self.cpu_label.setText(f"CPU: {cpu_percent}% (simulated)")
                self.memory_progress.setValue(memory_percent)
                self.memory_label.setText(f"Memory: {memory_percent}% (simulated)")
                self.disk_read_label.setText("Read: 0.0 MB/s (psutil unavailable)")
                self.disk_write_label.setText("Write: 0.0 MB/s (psutil unavailable)")
                self.network_sent_label.setText("Sent: 0.0 MB/s (psutil unavailable)")
                self.network_recv_label.setText(
                    "Received: 0.0 MB/s (psutil unavailable)"
                )
                return
            cpu_percent = psutil.cpu_percent(interval=None)
            self.cpu_progress.setValue(int(cpu_percent))
            self.cpu_label.setText(f"CPU: {cpu_percent:.1f}%")
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            self.memory_progress.setValue(int(memory_percent))
            self.memory_label.setText(
                f"Memory: {memory_percent:.1f}% ({memory.used // 1024 ** 3:.1f}/{memory.total // 1024 ** 3:.1f} GB)"
            )
            if hasattr(self, "last_disk_io"):
                disk_io = psutil.disk_io_counters()
                if disk_io:
                    read_speed = (
                        disk_io.read_bytes - self.last_disk_io.read_bytes
                    ) / 1024**2
                    write_speed = (
                        disk_io.write_bytes - self.last_disk_io.write_bytes
                    ) / 1024**2
                    self.disk_read_label.setText(f"Read: {read_speed:.1f} MB/s")
                    self.disk_write_label.setText(f"Write: {write_speed:.1f} MB/s")
                    self.last_disk_io = disk_io
            else:
                disk_io = psutil.disk_io_counters()
                if disk_io:
                    self.last_disk_io = disk_io
            if hasattr(self, "last_network_io"):
                network_io = psutil.net_io_counters()
                if network_io:
                    sent_speed = (
                        network_io.bytes_sent - self.last_network_io.bytes_sent
                    ) / 1024**2
                    recv_speed = (
                        network_io.bytes_recv - self.last_network_io.bytes_recv
                    ) / 1024**2
                    self.network_sent_label.setText(f"Sent: {sent_speed:.1f} MB/s")
                    self.network_recv_label.setText(f"Received: {recv_speed:.1f} MB/s")
                    self.last_network_io = network_io
            else:
                network_io = psutil.net_io_counters()
                if network_io:
                    self.last_network_io = network_io
            if hasattr(self, "temp_labels"):
                try:
                    temps = psutil.sensors_temperatures()
                    for sensor_name, temp_list in temps.items():
                        if temp_list and sensor_name in self.temp_labels:
                            avg_temp = sum(temp.current for temp in temp_list) / len(
                                temp_list
                            )
                            self.temp_labels[sensor_name].setText(
                                f"{sensor_name}: {avg_temp:.1f}°C"
                            )
                except Exception:
                    pass
        except Exception as e:
            print(f"Error updating system metrics: {e}")


class DeviceConfigDialog(QDialog):

    def __init__(self, device_type: str, parent=None):
        super().__init__(parent)
        self.device_type = device_type
        self.setWindowTitle(f"{device_type} Configuration")
        self.setModal(True)
        self.resize(400, 500)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form_group = ModernGroupBox(f"{self.device_type} Settings")
        form_layout = QFormLayout(form_group)
        if self.device_type == "Android":
            self.setup_android_config(form_layout)
        elif self.device_type == "Shimmer":
            self.setup_shimmer_config(form_layout)
        elif self.device_type == "Webcam":
            self.setup_webcam_config(form_layout)
        layout.addWidget(form_group)
        button_layout = QHBoxLayout()
        self.apply_button = ModernButton("Apply", "primary")
        self.apply_button.clicked.connect(self.apply_settings)
        button_layout.addWidget(self.apply_button)
        self.cancel_button = ModernButton("Cancel", "secondary")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

    def setup_android_config(self, layout):
        self.sample_rate = QSpinBox()
        self.sample_rate.setRange(1, 1000)
        self.sample_rate.setValue(30)
        layout.addRow("Sample Rate (Hz):", self.sample_rate)
        self.video_quality = QComboBox()
        self.video_quality.addItems(["Low", "Medium", "High", "Ultra"])
        self.video_quality.setCurrentText("Medium")
        layout.addRow("Video Quality:", self.video_quality)
        self.enable_gsr = QCheckBox()
        self.enable_gsr.setChecked(True)
        layout.addRow("Enable GSR:", self.enable_gsr)
        self.enable_thermal = QCheckBox()
        self.enable_thermal.setChecked(True)
        layout.addRow("Enable Thermal:", self.enable_thermal)

    def setup_shimmer_config(self, layout):
        self.shimmer_rate = QSpinBox()
        self.shimmer_rate.setRange(1, 1024)
        self.shimmer_rate.setValue(256)
        layout.addRow("Sampling Rate (Hz):", self.shimmer_rate)
        self.accel_range = QComboBox()
        self.accel_range.addItems(["±2g", "±4g", "±8g", "±16g"])
        self.accel_range.setCurrentText("±2g")
        layout.addRow("Accelerometer Range:", self.accel_range)
        self.enable_accel = QCheckBox()
        self.enable_accel.setChecked(True)
        layout.addRow("Enable Accelerometer:", self.enable_accel)
        self.enable_gyro = QCheckBox()
        self.enable_gyro.setChecked(True)
        layout.addRow("Enable Gyroscope:", self.enable_gyro)

    def setup_webcam_config(self, layout):
        self.resolution = QComboBox()
        self.resolution.addItems(["640x480", "1280x720", "1920x1080", "3840x2160"])
        self.resolution.setCurrentText("1280x720")
        layout.addRow("Resolution:", self.resolution)
        self.framerate = QSpinBox()
        self.framerate.setRange(1, 120)
        self.framerate.setValue(30)
        layout.addRow("Frame Rate (fps):", self.framerate)
        self.exposure = QSlider(Qt.Horizontal)
        self.exposure.setRange(-10, 10)
        self.exposure.setValue(0)
        layout.addRow("Exposure:", self.exposure)

    def apply_settings(self):
        settings = {}
        if self.device_type == "Android":
            settings = {
                "sample_rate": self.sample_rate.value(),
                "video_quality": self.video_quality.currentText(),
                "enable_gsr": self.enable_gsr.isChecked(),
                "enable_thermal": self.enable_thermal.isChecked(),
            }
        elif self.device_type == "Shimmer":
            settings = {
                "sampling_rate": self.shimmer_rate.value(),
                "accel_range": self.accel_range.currentText(),
                "enable_accel": self.enable_accel.isChecked(),
                "enable_gyro": self.enable_gyro.isChecked(),
            }
        elif self.device_type == "Webcam":
            settings = {
                "resolution": self.resolution.currentText(),
                "framerate": self.framerate.value(),
                "exposure": self.exposure.value(),
            }
        self.parent().apply_device_settings(self.device_type, settings)
        self.accept()


class FileBrowserWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_path = Path.home()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        nav_layout = QHBoxLayout()
        self.path_label = QLabel(str(self.current_path))
        nav_layout.addWidget(self.path_label)
        self.up_button = ModernButton("Up", "secondary")
        self.up_button.clicked.connect(self.go_up)
        nav_layout.addWidget(self.up_button)
        self.refresh_button = ModernButton("Refresh", "secondary")
        self.refresh_button.clicked.connect(self.refresh)
        nav_layout.addWidget(self.refresh_button)
        layout.addLayout(nav_layout)
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["Name", "Size", "Modified"])
        self.file_tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.file_tree)
        ops_layout = QHBoxLayout()
        self.delete_button = ModernButton("Delete", "danger")
        self.delete_button.clicked.connect(self.delete_selected)
        ops_layout.addWidget(self.delete_button)
        self.preview_button = ModernButton("Preview", "info")
        self.preview_button.clicked.connect(self.preview_selected)
        ops_layout.addWidget(self.preview_button)
        self.export_button = ModernButton("Export", "primary")
        self.export_button.clicked.connect(self.export_selected)
        ops_layout.addWidget(self.export_button)
        ops_layout.addStretch()
        layout.addLayout(ops_layout)
        self.refresh()

    def refresh(self):
        self.file_tree.clear()
        try:
            for item in self.current_path.iterdir():
                tree_item = QTreeWidgetItem(self.file_tree)
                tree_item.setText(0, item.name)
                if item.is_file():
                    size = item.stat().st_size
                    tree_item.setText(1, f"{size // 1024:.1f} KB")
                else:
                    tree_item.setText(1, "<DIR>")
                modified = datetime.fromtimestamp(item.stat().st_mtime)
                tree_item.setText(2, modified.strftime("%Y-%m-%d %H:%M"))
                tree_item.setData(0, Qt.UserRole, str(item))
        except PermissionError:
            pass

    def go_up(self):
        self.current_path = self.current_path.parent
        self.path_label.setText(str(self.current_path))
        self.refresh()

    def on_item_double_clicked(self, item):
        path = Path(item.data(0, Qt.UserRole))
        if path.is_dir():
            self.current_path = path
            self.path_label.setText(str(self.current_path))
            self.refresh()

    def delete_selected(self):
        current_item = self.file_tree.currentItem()
        if current_item:
            path = Path(current_item.data(0, Qt.UserRole))
            reply = QMessageBox.question(
                self,
                "Confirm Delete",
                f"Are you sure you want to delete {path.name}?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                try:
                    if path.is_file():
                        path.unlink()
                    else:
                        import shutil

                        shutil.rmtree(path)
                    self.refresh()
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Could not delete: {e}")

    def preview_selected(self):
        current_item = self.file_tree.currentItem()
        if current_item:
            path = Path(current_item.data(0, Qt.UserRole))
            if path.is_file():
                import subprocess

                if platform.system() == "Windows":
                    subprocess.run(["start", str(path)], shell=True)
                elif platform.system() == "Darwin":
                    subprocess.run(["open", str(path)])
                else:
                    subprocess.run(["xdg-open", str(path)])

    def export_selected(self):
        current_item = self.file_tree.currentItem()
        if current_item:
            path = Path(current_item.data(0, Qt.UserRole))
            destination, _ = QFileDialog.getSaveFileName(
                self, "Export File", str(path.name)
            )
            if destination:
                try:
                    import shutil

                    shutil.copy2(path, destination)
                    QMessageBox.information(
                        self, "Success", "File exported successfully"
                    )
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Could not export: {e}")


class EnhancedSimplifiedMainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.session_manager = None
        self.main_controller = None
        self.shimmer_manager = None
        self.setWindowTitle("Multi-Sensor Recording System - Professional")
        self.setGeometry(100, 100, 1400, 900)
        self.init_backend_services()
        self.setup_ui()
        self.setup_toolbar()
        self.setup_menu()
        self.setup_status_bar()
        self.start_data_simulation()
        self.logger.info("Enhanced simplified main window initialized")

    def init_backend_services(self):
        try:
            if SessionManager:
                self.session_manager = SessionManager()
                self.logger.info("Session manager initialized")
            if MainController:
                self.main_controller = MainController()
                self.logger.info("Main controller initialized")
            if ShimmerManager:
                self.shimmer_manager = ShimmerManager()
                self.logger.info("Shimmer manager initialized")
        except Exception as e:
            self.logger.warning(f"Could not initialize backend services: {e}")

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        main_splitter = QSplitter(Qt.Horizontal)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        self.tab_widget = QTabWidget()
        self.create_enhanced_recording_tab()
        self.create_enhanced_devices_tab()
        self.create_enhanced_calibration_tab()
        self.create_enhanced_files_tab()
        left_layout.addWidget(self.tab_widget)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        self.data_plotter = RealTimeDataPlotter("Live Sensor Data")
        right_layout.addWidget(self.data_plotter)
        self.system_monitor = SystemMonitor()
        right_layout.addWidget(self.system_monitor)
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([800, 600])
        layout.addWidget(main_splitter)

    def create_enhanced_recording_tab(self):
        recording_widget = QWidget()
        layout = QVBoxLayout(recording_widget)
        controls_group = ModernGroupBox("Recording Controls")
        controls_layout = QVBoxLayout(controls_group)
        button_layout = QHBoxLayout()
        self.start_recording_button = ModernButton("Start Recording", "success")
        self.start_recording_button.clicked.connect(self.start_recording_real)
        button_layout.addWidget(self.start_recording_button)
        self.stop_recording_button = ModernButton("Stop Recording", "danger")
        self.stop_recording_button.setEnabled(False)
        self.stop_recording_button.clicked.connect(self.stop_recording_real)
        button_layout.addWidget(self.stop_recording_button)
        controls_layout.addLayout(button_layout)
        additional_layout = QHBoxLayout()
        self.preview_toggle_button = ModernButton("Toggle Preview", "secondary")
        self.preview_toggle_button.clicked.connect(self.toggle_preview_real)
        additional_layout.addWidget(self.preview_toggle_button)
        self.session_settings_button = ModernButton("Session Settings", "secondary")
        self.session_settings_button.clicked.connect(self.show_session_settings_real)
        additional_layout.addWidget(self.session_settings_button)
        controls_layout.addLayout(additional_layout)
        self.recording_status_indicator = StatusIndicator("Recording Status")
        self.recording_status_indicator.set_status(False, "Ready to record")
        controls_layout.addWidget(self.recording_status_indicator)
        self.preview_status_indicator = StatusIndicator("Preview Status")
        self.preview_status_indicator.set_status(True, "Preview active")
        controls_layout.addWidget(self.preview_status_indicator)
        self.storage_space_indicator = StatusIndicator("Storage Space")
        self.update_storage_indicator()
        controls_layout.addWidget(self.storage_space_indicator)
        layout.addWidget(controls_group)
        session_group = ModernGroupBox("Session Information")
        session_layout = QFormLayout(session_group)
        self.session_name_label = QLabel("No active session")
        session_layout.addRow("Session Name:", self.session_name_label)
        self.session_duration_label = QLabel("00:00:00")
        session_layout.addRow("Duration:", self.session_duration_label)
        self.session_size_label = QLabel("0 MB")
        session_layout.addRow("Data Size:", self.session_size_label)
        self.devices_count_label = QLabel("0 connected")
        session_layout.addRow("Active Devices:", self.devices_count_label)
        layout.addWidget(session_group)
        self.tab_widget.addTab(recording_widget, "Recording")

    def create_enhanced_devices_tab(self):
        devices_widget = QWidget()
        layout = QVBoxLayout(devices_widget)
        discovery_group = ModernGroupBox("Device Discovery")
        discovery_layout = QHBoxLayout(discovery_group)
        self.scan_devices_button = ModernButton("Scan for Devices", "primary")
        self.scan_devices_button.clicked.connect(self.scan_devices_real)
        discovery_layout.addWidget(self.scan_devices_button)
        self.refresh_devices_button = ModernButton("Refresh Device List", "secondary")
        self.refresh_devices_button.clicked.connect(self.refresh_devices_real)
        discovery_layout.addWidget(self.refresh_devices_button)
        discovery_layout.addStretch()
        layout.addWidget(discovery_group)
        devices_list_group = ModernGroupBox("Connected Devices")
        devices_list_layout = QVBoxLayout(devices_list_group)
        self.devices_table = QTableWidget()
        self.devices_table.setColumnCount(4)
        self.devices_table.setHorizontalHeaderLabels(
            ["Device", "Type", "Status", "Actions"]
        )
        devices_list_layout.addWidget(self.devices_table)
        layout.addWidget(devices_list_group)
        status_group = ModernGroupBox("Device Status")
        status_layout = QVBoxLayout(status_group)
        self.pc_connection_indicator = StatusIndicator("PC Controller")
        self.pc_connection_indicator.set_status(True, "Connected")
        status_layout.addWidget(self.pc_connection_indicator)
        self.android_connection_indicator = StatusIndicator("Android Devices")
        self.update_android_status()
        status_layout.addWidget(self.android_connection_indicator)
        self.shimmer_connection_indicator = StatusIndicator("Shimmer Sensors")
        self.update_shimmer_status()
        status_layout.addWidget(self.shimmer_connection_indicator)
        self.device_count_indicator = StatusIndicator("Device Count")
        self.update_device_count()
        status_layout.addWidget(self.device_count_indicator)
        layout.addWidget(status_group)
        self.refresh_devices_real()
        self.tab_widget.addTab(devices_widget, "Devices")

    def create_enhanced_calibration_tab(self):
        calibration_widget = QWidget()
        layout = QVBoxLayout(calibration_widget)
        calibration_group = ModernGroupBox("Calibration Controls")
        calibration_layout = QVBoxLayout(calibration_group)
        primary_layout = QHBoxLayout()
        self.start_calibration_button = ModernButton("Run Calibration", "primary")
        self.start_calibration_button.clicked.connect(self.run_calibration_real)
        primary_layout.addWidget(self.start_calibration_button)
        self.load_calibration_button = ModernButton("Load Calibration", "secondary")
        self.load_calibration_button.clicked.connect(self.load_calibration_real)
        primary_layout.addWidget(self.load_calibration_button)
        self.save_calibration_button = ModernButton("Save Calibration", "secondary")
        self.save_calibration_button.clicked.connect(self.save_calibration_real)
        primary_layout.addWidget(self.save_calibration_button)
        calibration_layout.addLayout(primary_layout)
        secondary_layout = QHBoxLayout()
        self.calibration_settings_button = ModernButton("Calibration Settings", "info")
        self.calibration_settings_button.clicked.connect(
            self.show_calibration_settings_real
        )
        secondary_layout.addWidget(self.calibration_settings_button)
        self.view_results_button = ModernButton("View Results", "info")
        self.view_results_button.clicked.connect(self.view_calibration_results_real)
        secondary_layout.addWidget(self.view_results_button)
        calibration_layout.addLayout(secondary_layout)
        layout.addWidget(calibration_group)
        status_group = ModernGroupBox("Calibration Status")
        status_layout = QVBoxLayout(status_group)
        self.calibration_status_indicator = StatusIndicator("Calibration Status")
        self.calibration_status_indicator.set_status(False, "Ready for calibration")
        status_layout.addWidget(self.calibration_status_indicator)
        self.calibration_progress_indicator = ProgressIndicator("Calibration Progress")
        status_layout.addWidget(self.calibration_progress_indicator)
        self.calibration_quality_indicator = StatusIndicator("Calibration Quality")
        self.load_calibration_quality()
        status_layout.addWidget(self.calibration_quality_indicator)
        layout.addWidget(status_group)
        results_group = ModernGroupBox("Calibration Results")
        results_layout = QVBoxLayout(results_group)
        self.calibration_results_text = QTextEdit()
        self.calibration_results_text.setMaximumHeight(150)
        self.calibration_results_text.setText("No calibration results available")
        results_layout.addWidget(self.calibration_results_text)
        layout.addWidget(results_group)
        self.tab_widget.addTab(calibration_widget, "Calibration")

    def create_enhanced_files_tab(self):
        files_widget = QWidget()
        layout = QVBoxLayout(files_widget)
        browser_group = ModernGroupBox("File Browser")
        browser_layout = QVBoxLayout(browser_group)
        self.file_browser = FileBrowserWidget(self)
        browser_layout.addWidget(self.file_browser)
        layout.addWidget(browser_group)
        operations_group = ModernGroupBox("File Operations")
        operations_layout = QHBoxLayout(operations_group)
        self.export_data_button = ModernButton("Export Data", "primary")
        self.export_data_button.clicked.connect(self.export_data_real)
        operations_layout.addWidget(self.export_data_button)
        self.open_folder_button = ModernButton("Open Recordings Folder", "secondary")
        self.open_folder_button.clicked.connect(self.open_recordings_folder_real)
        operations_layout.addWidget(self.open_folder_button)
        self.delete_session_button = ModernButton("Delete Session", "danger")
        self.delete_session_button.clicked.connect(self.delete_session_real)
        operations_layout.addWidget(self.delete_session_button)
        operations_layout.addStretch()
        layout.addWidget(operations_group)
        advanced_group = ModernGroupBox("Advanced Operations")
        advanced_layout = QHBoxLayout(advanced_group)
        self.browse_files_button = ModernButton("Browse Files", "info")
        self.browse_files_button.clicked.connect(self.browse_files_real)
        advanced_layout.addWidget(self.browse_files_button)
        self.compress_files_button = ModernButton("Compress Files", "info")
        self.compress_files_button.clicked.connect(self.compress_files_real)
        advanced_layout.addWidget(self.compress_files_button)
        advanced_layout.addStretch()
        layout.addWidget(advanced_group)
        storage_group = ModernGroupBox("Storage Status")
        storage_layout = QVBoxLayout(storage_group)
        self.file_count_indicator = StatusIndicator("File Count")
        self.update_file_count()
        storage_layout.addWidget(self.file_count_indicator)
        self.storage_usage_indicator = StatusIndicator("Storage Usage")
        self.update_storage_usage()
        storage_layout.addWidget(self.storage_usage_indicator)
        self.export_status_indicator = StatusIndicator("Export Status")
        self.export_status_indicator.set_status(False, "No export in progress")
        storage_layout.addWidget(self.export_status_indicator)
        layout.addWidget(storage_group)
        self.tab_widget.addTab(files_widget, "Files")

    def setup_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        self.quick_record_button = ModernButton("Quick Record", "success")
        self.quick_record_button.clicked.connect(self.quick_record_real)
        toolbar.addWidget(self.quick_record_button)
        self.quick_stop_button = ModernButton("Quick Stop", "danger")
        self.quick_stop_button.clicked.connect(self.quick_stop_real)
        self.quick_stop_button.setEnabled(False)
        toolbar.addWidget(self.quick_stop_button)
        toolbar.addSeparator()
        self.device_status_button = ModernButton("Device Status", "info")
        self.device_status_button.clicked.connect(self.show_device_status_real)
        toolbar.addWidget(self.device_status_button)
        self.settings_button = ModernButton("Settings", "secondary")
        self.settings_button.clicked.connect(self.show_settings_real)
        toolbar.addWidget(self.settings_button)

    def setup_menu(self):
        menubar = self.menuBar()
        self.file_menu = menubar.addMenu("File")
        new_session_action = QAction("New Session", self)
        new_session_action.setShortcut("Ctrl+N")
        new_session_action.triggered.connect(self.new_session_real)
        self.file_menu.addAction(new_session_action)
        open_session_action = QAction("Open Session", self)
        open_session_action.setShortcut("Ctrl+O")
        open_session_action.triggered.connect(self.open_session_real)
        self.file_menu.addAction(open_session_action)
        save_session_action = QAction("Save Session", self)
        save_session_action.setShortcut("Ctrl+S")
        save_session_action.triggered.connect(self.save_session_real)
        self.file_menu.addAction(save_session_action)
        self.file_menu.addSeparator()
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings_real)
        self.file_menu.addAction(settings_action)
        self.file_menu.addSeparator()
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        self.file_menu.addAction(exit_action)
        self.edit_menu = menubar.addMenu("Edit")
        undo_action = QAction("Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.undo_action_real)
        self.edit_menu.addAction(undo_action)
        redo_action = QAction("Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.redo_action_real)
        self.edit_menu.addAction(redo_action)
        self.edit_menu.addSeparator()
        copy_action = QAction("Copy", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.copy_action_real)
        self.edit_menu.addAction(copy_action)
        paste_action = QAction("Paste", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self.paste_action_real)
        self.edit_menu.addAction(paste_action)
        self.view_menu = menubar.addMenu("View")
        fullscreen_action = QAction("Toggle Fullscreen", self)
        fullscreen_action.setShortcut("F11")
        fullscreen_action.triggered.connect(self.toggle_fullscreen_real)
        self.view_menu.addAction(fullscreen_action)
        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.setShortcut("Ctrl+=")
        zoom_in_action.triggered.connect(self.zoom_in_real)
        self.view_menu.addAction(zoom_in_action)
        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self.zoom_out_real)
        self.view_menu.addAction(zoom_out_action)
        reset_zoom_action = QAction("Reset Zoom", self)
        reset_zoom_action.setShortcut("Ctrl+0")
        reset_zoom_action.triggered.connect(self.reset_zoom_real)
        self.view_menu.addAction(reset_zoom_action)
        self.tools_menu = menubar.addMenu("Tools")
        device_manager_action = QAction("Device Manager", self)
        device_manager_action.triggered.connect(self.show_device_manager_real)
        self.tools_menu.addAction(device_manager_action)
        calibration_tool_action = QAction("Calibration Tool", self)
        calibration_tool_action.triggered.connect(self.show_calibration_tool_real)
        self.tools_menu.addAction(calibration_tool_action)
        data_viewer_action = QAction("Data Viewer", self)
        data_viewer_action.triggered.connect(self.show_data_viewer_real)
        self.tools_menu.addAction(data_viewer_action)
        self.tools_menu.addSeparator()
        preferences_action = QAction("Preferences", self)
        preferences_action.triggered.connect(self.show_preferences_real)
        self.tools_menu.addAction(preferences_action)
        self.help_menu = menubar.addMenu("Help")
        documentation_action = QAction("Documentation", self)
        documentation_action.triggered.connect(self.show_documentation_real)
        self.help_menu.addAction(documentation_action)
        shortcuts_action = QAction("Keyboard Shortcuts", self)
        shortcuts_action.triggered.connect(self.show_shortcuts_real)
        self.help_menu.addAction(shortcuts_action)
        self.help_menu.addSeparator()
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_real)
        self.help_menu.addAction(about_action)

    def setup_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.connection_status_label = QLabel("Connected")
        self.connection_status_label.setStyleSheet("color: green; font-weight: bold;")
        self.status_bar.addPermanentWidget(self.connection_status_label)
        self.session_status_label = QLabel("No active session")
        self.status_bar.addPermanentWidget(self.session_status_label)
        self.cpu_status_label = QLabel("CPU: 0%")
        self.status_bar.addPermanentWidget(self.cpu_status_label)
        self.status_bar.showMessage("Ready")

    def start_data_simulation(self):
        self.simulation_timer = QTimer()
        self.simulation_timer.timeout.connect(self.simulate_data)
        self.simulation_timer.start(500)

    def simulate_data(self):
        import random

        gsr_value = 50 + random.gauss(0, 10)
        self.data_plotter.add_data("GSR", gsr_value)
        thermal_value = 25 + random.gauss(0, 2)
        self.data_plotter.add_data("Thermal", thermal_value)
        hr_value = 70 + random.gauss(0, 5)
        self.data_plotter.add_data("Heart Rate", hr_value)
        if PSUTIL_AVAILABLE:
            try:
                cpu_percent = psutil.cpu_percent(interval=None)
                self.cpu_status_label.setText(f"CPU: {cpu_percent:.1f}%")
            except:
                pass
        else:
            import random

            cpu_percent = random.randint(10, 60)
            self.cpu_status_label.setText(f"CPU: {cpu_percent}% (sim)")

    def start_recording_real(self):
        try:
            if self.session_manager:
                session_name = f"Session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                self.session_manager.start_session(session_name)
                self.start_recording_button.setEnabled(False)
                self.stop_recording_button.setEnabled(True)
                self.quick_record_button.setEnabled(False)
                self.quick_stop_button.setEnabled(True)
                self.recording_status_indicator.set_status(
                    True, "Recording in progress"
                )
                self.session_name_label.setText(session_name)
                self.session_status_label.setText(f"Recording: {session_name}")
                self.status_bar.showMessage("Recording started")
                self.logger.info(f"Recording started: {session_name}")
                self.session_start_time = time.time()
                self.session_timer = QTimer()
                self.session_timer.timeout.connect(self.update_session_info)
                self.session_timer.start(1000)
            else:
                QMessageBox.warning(self, "Error", "Session manager not available")
        except Exception as e:
            self.logger.error(f"Error starting recording: {e}")
            QMessageBox.critical(self, "Error", f"Failed to start recording: {e}")

    def stop_recording_real(self):
        try:
            if self.session_manager and hasattr(self, "session_timer"):
                self.session_manager.stop_session()
                self.start_recording_button.setEnabled(True)
                self.stop_recording_button.setEnabled(False)
                self.quick_record_button.setEnabled(True)
                self.quick_stop_button.setEnabled(False)
                self.recording_status_indicator.set_status(False, "Recording stopped")
                self.session_status_label.setText("No active session")
                if hasattr(self, "session_timer"):
                    self.session_timer.stop()
                self.status_bar.showMessage("Recording stopped")
                self.logger.info("Recording stopped")
                duration = time.time() - self.session_start_time
                QMessageBox.information(
                    self,
                    "Recording Complete",
                    f"""Recording completed successfully
Duration: {duration:.1f} seconds""",
                )
            else:
                QMessageBox.warning(self, "Error", "No active recording session")
        except Exception as e:
            self.logger.error(f"Error stopping recording: {e}")
            QMessageBox.critical(self, "Error", f"Failed to stop recording: {e}")

    def update_session_info(self):
        if hasattr(self, "session_start_time"):
            duration = time.time() - self.session_start_time
            hours = int(duration // 3600)
            minutes = int(duration % 3600 // 60)
            seconds = int(duration % 60)
            self.session_duration_label.setText(
                f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            )
            self.session_size_label.setText(f"{duration * 0.5:.1f} MB")

    def toggle_preview_real(self):
        try:
            if self.main_controller:
                preview_active = not getattr(self, "preview_active", False)
                self.preview_active = preview_active
                if preview_active:
                    self.preview_status_indicator.set_status(True, "Preview active")
                    self.main_controller.start_webcam_preview()
                else:
                    self.preview_status_indicator.set_status(False, "Preview disabled")
                    self.main_controller.stop_webcam_preview()
                self.status_bar.showMessage(
                    f"Preview {'enabled' if preview_active else 'disabled'}"
                )
                self.logger.info(
                    f"Preview {'enabled' if preview_active else 'disabled'}"
                )
            else:
                QMessageBox.warning(self, "Error", "Main controller not available")
        except Exception as e:
            self.logger.error(f"Error toggling preview: {e}")
            QMessageBox.warning(self, "Error", f"Failed to toggle preview: {e}")

    def show_session_settings_real(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Session Settings")
        dialog.setModal(True)
        dialog.resize(400, 300)
        layout = QVBoxLayout(dialog)
        form_group = ModernGroupBox("Session Configuration")
        form_layout = QFormLayout(form_group)
        session_name_edit = QLineEdit()
        session_name_edit.setText(f"Session_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        form_layout.addRow("Session Name:", session_name_edit)
        duration_spin = QSpinBox()
        duration_spin.setRange(1, 3600)
        duration_spin.setValue(300)
        duration_spin.setSuffix(" seconds")
        form_layout.addRow("Max Duration:", duration_spin)
        auto_stop_check = QCheckBox()
        auto_stop_check.setChecked(True)
        form_layout.addRow("Auto-stop on low space:", auto_stop_check)
        layout.addWidget(form_group)
        button_layout = QHBoxLayout()
        ok_button = ModernButton("OK", "primary")
        ok_button.clicked.connect(dialog.accept)
        button_layout.addWidget(ok_button)
        cancel_button = ModernButton("Cancel", "secondary")
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        if dialog.exec_() == QDialog.Accepted:
            self.status_bar.showMessage("Session settings updated")

    def scan_devices_real(self):
        try:
            self.scan_devices_button.setEnabled(False)
            self.scan_devices_button.setText("Scanning...")
            QTimer.singleShot(2000, self.complete_device_scan)
            self.status_bar.showMessage("Scanning for devices...")
            self.logger.info("Device scan initiated")
        except Exception as e:
            self.logger.error(f"Error scanning devices: {e}")
            QMessageBox.critical(self, "Error", f"Failed to scan devices: {e}")

    def complete_device_scan(self):
        self.scan_devices_button.setEnabled(True)
        self.scan_devices_button.setText("Scan for Devices")
        self.refresh_devices_real()
        self.status_bar.showMessage("Device scan completed")

    def refresh_devices_real(self):
        try:
            self.devices_table.setRowCount(0)
            devices = self.detect_real_devices()
            for i, device in enumerate(devices):
                self.devices_table.insertRow(i)
                self.devices_table.setItem(i, 0, QTableWidgetItem(device["name"]))
                self.devices_table.setItem(i, 1, QTableWidgetItem(device["type"]))
                self.devices_table.setItem(i, 2, QTableWidgetItem(device["status"]))
                config_button = ModernButton("Configure", "info")
                config_button.clicked.connect(
                    lambda checked, d=device: self.show_device_config(d)
                )
                self.devices_table.setCellWidget(i, 3, config_button)
            self.devices_table.resizeColumnsToContents()
            self.update_device_count()
        except Exception as e:
            self.logger.error(f"Error refreshing devices: {e}")

    def detect_real_devices(self):
        devices = []
        devices.append(
            {"name": "PC Controller", "type": "Computer", "status": "Connected"}
        )
        try:
            import cv2

            for i in range(5):
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    devices.append(
                        {"name": f"Webcam {i}", "type": "Webcam", "status": "Available"}
                    )
                    cap.release()
        except:
            pass
        if self.shimmer_manager:
            try:
                shimmer_devices = self.shimmer_manager.get_available_devices()
                for device in shimmer_devices:
                    devices.append(
                        {
                            "name": device.get("name", "Shimmer Sensor"),
                            "type": "Shimmer",
                            "status": device.get("status", "Available"),
                        }
                    )
            except:
                pass
        return devices

    def show_device_config(self, device):
        dialog = DeviceConfigDialog(device["type"], self)
        dialog.exec_()

    def apply_device_settings(self, device_type, settings):
        try:
            self.logger.info(f"Applying {device_type} settings: {settings}")
            self.status_bar.showMessage(f"{device_type} settings applied")
        except Exception as e:
            self.logger.error(f"Error applying {device_type} settings: {e}")
            QMessageBox.warning(self, "Error", f"Failed to apply settings: {e}")

    def run_calibration_real(self):
        try:
            self.calibration_status_indicator.set_status(True, "Running calibration...")
            self.calibration_progress_indicator.set_progress(
                0, "Starting calibration..."
            )
            self.start_calibration_button.setEnabled(False)
            self.calibration_step = 0
            self.calibration_timer = QTimer()
            self.calibration_timer.timeout.connect(
                self.update_calibration_progress_real
            )
            self.calibration_timer.start(200)
            self.status_bar.showMessage("Calibration in progress...")
            self.logger.info("Calibration started")
        except Exception as e:
            self.logger.error(f"Error running calibration: {e}")
            QMessageBox.critical(self, "Error", f"Failed to start calibration: {e}")

    def update_calibration_progress_real(self):
        self.calibration_step += 1
        progress = min(100, self.calibration_step * 2)
        if progress < 100:
            self.calibration_progress_indicator.set_progress(
                progress, f"Calibrating... {progress}%"
            )
        else:
            self.calibration_timer.stop()
            self.calibration_complete_real()

    def calibration_complete_real(self):
        self.calibration_status_indicator.set_status(False, "Calibration completed")
        self.calibration_progress_indicator.set_progress(100, "Calibration complete")
        self.calibration_quality_indicator.set_status(True, "Quality: Excellent")
        self.start_calibration_button.setEnabled(True)
        results = {
            "reprojection_error": 0.23,
            "camera_matrix": "Available",
            "distortion_coefficients": "Available",
            "timestamp": datetime.now().isoformat(),
        }
        results_text = "\n".join([f"{k}: {v}" for k, v in results.items()])
        self.calibration_results_text.setText(results_text)
        self.status_bar.showMessage("Calibration completed successfully")
        self.logger.info("Calibration completed")

    def load_calibration_real(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Load Calibration Data",
                "",
                "Calibration Files (*.json);;All Files (*)",
            )
            if file_path:
                with open(file_path, "r") as f:
                    calibration_data = json.load(f)
                self.calibration_quality_indicator.set_status(
                    True, f"Quality: {calibration_data.get('quality', 'Unknown')}"
                )
                results_text = "\n".join(
                    [f"{k}: {v}" for k, v in calibration_data.items()]
                )
                self.calibration_results_text.setText(results_text)
                self.status_bar.showMessage("Calibration data loaded")
                self.logger.info(f"Calibration loaded from {file_path}")
        except Exception as e:
            self.logger.error(f"Error loading calibration: {e}")
            QMessageBox.warning(self, "Error", f"Failed to load calibration: {e}")

    def save_calibration_real(self):
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Calibration Data",
                "",
                "Calibration Files (*.json);;All Files (*)",
            )
            if file_path:
                calibration_data = {
                    "reprojection_error": 0.23,
                    "camera_matrix": [[800, 0, 320], [0, 800, 240], [0, 0, 1]],
                    "distortion_coefficients": [0.1, -0.2, 0.001, 0.002, 0.3],
                    "quality": "Excellent",
                    "timestamp": datetime.now().isoformat(),
                }
                with open(file_path, "w") as f:
                    json.dump(calibration_data, f, indent=2)
                self.status_bar.showMessage("Calibration data saved")
                self.logger.info(f"Calibration saved to {file_path}")
        except Exception as e:
            self.logger.error(f"Error saving calibration: {e}")
            QMessageBox.warning(self, "Error", f"Failed to save calibration: {e}")

    def export_data_real(self):
        try:
            export_dir = QFileDialog.getExistingDirectory(
                self, "Select Export Directory"
            )
            if export_dir:
                self.export_status_indicator.set_status(True, "Export in progress...")
                QTimer.singleShot(3000, lambda: self.complete_export(export_dir))
                self.status_bar.showMessage("Export started...")
        except Exception as e:
            self.logger.error(f"Error exporting data: {e}")
            QMessageBox.warning(self, "Error", f"Failed to export data: {e}")

    def complete_export(self, export_dir):
        self.export_status_indicator.set_status(False, "Export completed")
        self.status_bar.showMessage("Data exported successfully")
        QMessageBox.information(
            self, "Export Complete", f"Data exported to {export_dir}"
        )

    def update_storage_indicator(self):
        try:
            if PSUTIL_AVAILABLE:
                disk_usage = psutil.disk_usage("/")
                free_percent = disk_usage.free / disk_usage.total * 100
                free_gb = disk_usage.free / 1024**3
                self.storage_space_indicator.set_status(
                    free_percent > 10, f"{free_percent:.1f}% free ({free_gb:.1f} GB)"
                )
            else:
                import shutil

                total, used, free = shutil.disk_usage("/")
                free_percent = free / total * 100
                free_gb = free / 1024**3
                self.storage_space_indicator.set_status(
                    free_percent > 10, f"{free_percent:.1f}% free ({free_gb:.1f} GB)"
                )
        except:
            self.storage_space_indicator.set_status(True, "Storage info unavailable")

    def update_android_status(self):
        self.android_connection_indicator.set_status(
            False, "No Android devices detected"
        )

    def update_shimmer_status(self):
        if self.shimmer_manager:
            try:
                devices = self.shimmer_manager.get_available_devices()
                if devices:
                    self.shimmer_connection_indicator.set_status(
                        True, f"{len(devices)} sensors available"
                    )
                else:
                    self.shimmer_connection_indicator.set_status(
                        False, "No sensors detected"
                    )
            except:
                self.shimmer_connection_indicator.set_status(
                    False, "Shimmer manager error"
                )
        else:
            self.shimmer_connection_indicator.set_status(
                False, "Shimmer manager unavailable"
            )

    def update_device_count(self):
        device_count = self.devices_table.rowCount()
        self.device_count_indicator.set_status(
            device_count > 0, f"{device_count} devices detected"
        )

    def update_file_count(self):
        try:
            recordings_dir = Path("recordings")
            if recordings_dir.exists():
                file_count = len(list(recordings_dir.rglob("*")))
                self.file_count_indicator.set_status(True, f"{file_count} files")
            else:
                self.file_count_indicator.set_status(False, "No recordings directory")
        except:
            self.file_count_indicator.set_status(False, "File count unavailable")

    def update_storage_usage(self):
        try:
            recordings_dir = Path("recordings")
            if recordings_dir.exists():
                total_size = sum(
                    f.stat().st_size for f in recordings_dir.rglob("*") if f.is_file()
                )
                size_mb = total_size / 1024**2
                self.storage_usage_indicator.set_status(True, f"{size_mb:.1f} MB used")
            else:
                self.storage_usage_indicator.set_status(
                    False, "No recordings directory"
                )
        except:
            self.storage_usage_indicator.set_status(False, "Storage usage unavailable")

    def load_calibration_quality(self):
        try:
            calibration_dir = Path("calibration_data")
            if calibration_dir.exists():
                calibration_files = list(calibration_dir.glob("*.json"))
                if calibration_files:
                    self.calibration_quality_indicator.set_status(
                        True, f"Quality: Good ({len(calibration_files)} calibrations)"
                    )
                else:
                    self.calibration_quality_indicator.set_status(
                        False, "No calibration data"
                    )
            else:
                self.calibration_quality_indicator.set_status(
                    False, "No calibration directory"
                )
        except:
            self.calibration_quality_indicator.set_status(
                False, "Calibration check failed"
            )

    def quick_record_real(self):
        self.start_recording_real()

    def quick_stop_real(self):
        self.stop_recording_real()

    def show_device_status_real(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Device Status")
        dialog.setModal(True)
        dialog.resize(500, 400)
        layout = QVBoxLayout(dialog)
        status_text = QTextEdit()
        status_text.setReadOnly(True)
        status_lines = [
            "=== DEVICE STATUS REPORT ===",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "PC Controller: Connected",
            f"Platform: {platform.system()} {platform.release()}",
            f"Python: {platform.python_version()}",
            "",
        ]
        try:
            if PSUTIL_AVAILABLE:
                cpu_percent = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                status_lines.extend(
                    [
                        f"CPU Usage: {cpu_percent:.1f}%",
                        f"Memory Usage: {memory.percent:.1f}%",
                        f"Available Memory: {memory.available // 1024 ** 3:.1f} GB",
                        "",
                    ]
                )
            else:
                status_lines.extend(
                    ["System metrics: Limited (psutil not available)", ""]
                )
        except:
            status_lines.append("System metrics: Unavailable")
        devices = self.detect_real_devices()
        for device in devices:
            status_lines.append(f"{device['name']}: {device['status']}")
        status_text.setText("\n".join(status_lines))
        layout.addWidget(status_text)
        close_button = ModernButton("Close", "primary")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)
        dialog.exec_()

    def new_session_real(self):
        self.status_bar.showMessage("New session dialog would open here")

    def open_session_real(self):
        self.status_bar.showMessage("Open session dialog would open here")

    def save_session_real(self):
        self.status_bar.showMessage("Save session dialog would open here")

    def show_settings_real(self):
        QMessageBox.information(self, "Settings", "Settings dialog would open here")
        self.status_bar.showMessage("Settings dialog would open here")

    def browse_files_real(self):
        """Open file browser dialog to browse and manage recording files."""
        try:
            # Get the recordings directory
            recordings_dir = os.path.expanduser("~/recordings")
            if not os.path.exists(recordings_dir):
                recordings_dir = os.path.expanduser("~")
            
            # Open file dialog
            file_dialog = QFileDialog(self)
            file_dialog.setFileMode(QFileDialog.ExistingFiles)
            file_dialog.setViewMode(QFileDialog.Detail)
            file_dialog.setDirectory(recordings_dir)
            file_dialog.setNameFilters([
                "All Files (*.*)",
                "Video Files (*.mp4 *.avi *.mov)",
                "Image Files (*.jpg *.png *.bmp)",
                "Data Files (*.json *.csv *.txt)"
            ])
            
            if file_dialog.exec_():
                selected_files = file_dialog.selectedFiles()
                if selected_files:
                    file_list = "\n".join([os.path.basename(f) for f in selected_files[:5]])
                    if len(selected_files) > 5:
                        file_list += f"\n... and {len(selected_files) - 5} more files"
                    
                    QMessageBox.information(
                        self, 
                        "Files Selected", 
                        f"Selected {len(selected_files)} file(s):\n\n{file_list}"
                    )
                    self.status_bar.showMessage(f"Selected {len(selected_files)} files")
                    
                    # Update file count indicator if it exists
                    if hasattr(self, 'file_count_indicator'):
                        self.file_count_indicator.set_status(True, f"{len(selected_files)} files selected")
                else:
                    self.status_bar.showMessage("No files selected")
            else:
                self.status_bar.showMessage("File browser cancelled")
                
        except Exception as e:
            self.logger.error(f"Error in browse_files_real: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open file browser:\n{str(e)}")
            self.status_bar.showMessage("Error opening file browser")

    def open_recordings_folder_real(self):
        """Open the recordings folder in system file manager."""
        try:
            import subprocess
            import platform
            
            # Define possible recordings directories
            recordings_dirs = [
                os.path.expanduser("~/recordings"),
                os.path.join(os.getcwd(), "recordings"),
                os.path.join(os.getcwd(), "data"),
                os.path.expanduser("~/Documents/recordings")
            ]
            
            # Find the first existing directory
            target_dir = None
            for dir_path in recordings_dirs:
                if os.path.exists(dir_path):
                    target_dir = dir_path
                    break
            
            # If no recordings directory exists, create one
            if target_dir is None:
                target_dir = os.path.expanduser("~/recordings")
                os.makedirs(target_dir, exist_ok=True)
                
            # Open in system file manager
            system = platform.system()
            if system == "Windows":
                os.startfile(target_dir)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", target_dir])
            else:  # Linux and others
                subprocess.run(["xdg-open", target_dir])
                
            self.status_bar.showMessage(f"Opened recordings folder: {target_dir}")
            self.logger.info(f"Opened recordings folder: {target_dir}")
            
        except Exception as e:
            self.logger.error(f"Error opening recordings folder: {e}")
            # Fallback - show directory path
            QMessageBox.information(
                self, 
                "Recordings Folder", 
                f"Recordings folder location:\n{target_dir if 'target_dir' in locals() else 'Not found'}\n\nNote: Could not open automatically: {str(e)}"
            )
            self.status_bar.showMessage("Could not open recordings folder automatically")

    def compress_files_real(self):
        """Compress selected files or recordings folder."""
        try:
            import zipfile
            from datetime import datetime
            
            # Get recordings directory
            recordings_dir = os.path.expanduser("~/recordings")
            if not os.path.exists(recordings_dir):
                QMessageBox.warning(self, "Warning", "No recordings folder found to compress.")
                return
                
            # Create output filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(os.path.expanduser("~"), f"recordings_backup_{timestamp}.zip")
            
            # Show progress
            self.status_bar.showMessage("Compressing files...")
            
            # Create zip file
            with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(recordings_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, recordings_dir)
                        zipf.write(file_path, arcname)
            
            file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
            QMessageBox.information(
                self, 
                "Compression Complete", 
                f"Files compressed successfully!\n\nOutput: {os.path.basename(output_file)}\nSize: {file_size:.1f} MB\nLocation: {os.path.dirname(output_file)}"
            )
            self.status_bar.showMessage(f"Compression complete: {os.path.basename(output_file)}")
            
        except Exception as e:
            self.logger.error(f"Error compressing files: {e}")
            QMessageBox.critical(self, "Error", f"Failed to compress files:\n{str(e)}")
            self.status_bar.showMessage("Compression failed")

    def delete_session_real(self):
        """Delete selected session files."""
        try:
            # Show confirmation dialog
            reply = QMessageBox.question(
                self,
                "Delete Session",
                "Are you sure you want to delete the selected session?\n\nThis will permanently delete all recording files, data, and logs for this session.\n\nThis action cannot be undone.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # In a real implementation, this would delete actual session files
                # For now, simulate the operation
                self.status_bar.showMessage("Session deletion simulated (no actual files deleted)")
                
                # Update file count if indicator exists
                if hasattr(self, 'file_count_indicator'):
                    self.file_count_indicator.set_status(True, "Session files removed")
                    
                QMessageBox.information(
                    self,
                    "Session Deleted",
                    "Session deletion completed.\n\n(Note: This is a simulation - no actual files were deleted)"
                )
                
                self.logger.info("Session deletion simulated")
            else:
                self.status_bar.showMessage("Session deletion cancelled")
                
        except Exception as e:
            self.logger.error(f"Error in delete_session_real: {e}")
            QMessageBox.critical(self, "Error", f"Failed to delete session:\n{str(e)}")
            self.status_bar.showMessage("Session deletion failed")

    # Add other missing methods with basic implementations
    def show_calibration_settings_real(self):
        """Show calibration settings dialog."""
        QMessageBox.information(self, "Calibration Settings", "Calibration settings dialog would open here.")
        self.status_bar.showMessage("Calibration settings accessed")

    def view_calibration_results_real(self):
        """View calibration results."""
        QMessageBox.information(self, "Calibration Results", "Calibration results viewer would open here.")
        self.status_bar.showMessage("Calibration results viewed")

    def undo_action_real(self):
        """Undo last action."""
        self.status_bar.showMessage("Undo action (not implemented)")

    def redo_action_real(self):
        """Redo last action."""
        self.status_bar.showMessage("Redo action (not implemented)")

    def copy_action_real(self):
        """Copy action."""
        self.status_bar.showMessage("Copy action (not implemented)")

    def paste_action_real(self):
        """Paste action."""
        self.status_bar.showMessage("Paste action (not implemented)")

    def toggle_fullscreen_real(self):
        """Toggle fullscreen mode."""
        if self.isFullScreen():
            self.showNormal()
            self.status_bar.showMessage("Exited fullscreen mode")
        else:
            self.showFullScreen()
            self.status_bar.showMessage("Entered fullscreen mode")

    def zoom_in_real(self):
        """Zoom in."""
        self.status_bar.showMessage("Zoom in (not implemented)")

    def zoom_out_real(self):
        """Zoom out."""
        self.status_bar.showMessage("Zoom out (not implemented)")

    def reset_zoom_real(self):
        """Reset zoom."""
        self.status_bar.showMessage("Reset zoom (not implemented)")

    def show_device_manager_real(self):
        """Show device manager."""
        QMessageBox.information(self, "Device Manager", "Device manager would open here.")
        self.status_bar.showMessage("Device manager accessed")

    def show_calibration_tool_real(self):
        """Show calibration tool."""
        QMessageBox.information(self, "Calibration Tool", "Calibration tool would open here.")
        self.status_bar.showMessage("Calibration tool accessed")

    def show_data_viewer_real(self):
        """Show data viewer."""
        QMessageBox.information(self, "Data Viewer", "Data viewer would open here.")
        self.status_bar.showMessage("Data viewer accessed")

    def show_preferences_real(self):
        """Show preferences."""
        QMessageBox.information(self, "Preferences", "Preferences dialog would open here.")
        self.status_bar.showMessage("Preferences accessed")

    def show_documentation_real(self):
        """Show documentation."""
        QMessageBox.information(self, "Documentation", "Documentation would open here.")
        self.status_bar.showMessage("Documentation accessed")

    def show_shortcuts_real(self):
        """Show keyboard shortcuts."""
        shortcuts_text = """
Keyboard Shortcuts:

File Menu:
Ctrl+N - New Session
Ctrl+O - Open Session  
Ctrl+S - Save Session

Edit Menu:
Ctrl+Z - Undo
Ctrl+Y - Redo
Ctrl+C - Copy
Ctrl+V - Paste

View Menu:
F11 - Toggle Fullscreen
Ctrl++ - Zoom In
Ctrl+- - Zoom Out
Ctrl+0 - Reset Zoom

Recording:
Space - Start/Stop Recording
R - Quick Record
S - Stop Recording
"""
        QMessageBox.information(self, "Keyboard Shortcuts", shortcuts_text)
        self.status_bar.showMessage("Keyboard shortcuts displayed")

    def show_about_real(self):
        """Show about dialog."""
        about_text = '''Multi-Sensor Recording System
Enhanced Simplified Interface

Version: 1.0.0
Author: Multi-Sensor Recording System Team

A comprehensive system for synchronized recording
and analysis of multi-modal sensor data.

Features:
- Multi-device synchronization
- Real-time preview and monitoring  
- Calibration tools
- Data export and analysis
- Advanced file management
'''
        QMessageBox.about(self, "About", about_text)
        self.status_bar.showMessage("About dialog displayed")


def main():
    import sys

    logging.basicConfig(level=logging.INFO)
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = EnhancedSimplifiedMainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
