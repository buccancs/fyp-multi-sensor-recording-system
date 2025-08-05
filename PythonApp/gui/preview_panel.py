from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QLabel

from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class PreviewPanel(QTabWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.device1_widget = self.create_device_tab('Device 1')
        self.addTab(self.device1_widget, 'Device 1')
        self.device2_widget = self.create_device_tab('Device 2')
        self.addTab(self.device2_widget, 'Device 2')
        self.webcam_widget = self.create_webcam_tab('PC Webcam')
        self.addTab(self.webcam_widget, 'PC Webcam')
        self.rgb_labels = [self.device1_widget.rgb_label, self.
            device2_widget.rgb_label]
        self.thermal_labels = [self.device1_widget.thermal_label, self.
            device2_widget.thermal_label]
        self.webcam_label = self.webcam_widget.webcam_label

    def create_device_tab(self, device_name):
        device_widget = QWidget()
        device_layout = QVBoxLayout(device_widget)
        rgb_label = QLabel('RGB Camera Feed')
        rgb_label.setMinimumSize(320, 240)
        rgb_label.setStyleSheet(
            'background-color: black; color: white; border: 1px solid gray;')
        rgb_label.setAlignment(Qt.AlignCenter)
        device_layout.addWidget(rgb_label)
        thermal_label = QLabel('Thermal Camera Feed')
        thermal_label.setMinimumSize(320, 240)
        thermal_label.setStyleSheet(
            'background-color: black; color: white; border: 1px solid gray;')
        thermal_label.setAlignment(Qt.AlignCenter)
        device_layout.addWidget(thermal_label)
        device_layout.addStretch(1)
        device_widget.rgb_label = rgb_label
        device_widget.thermal_label = thermal_label
        return device_widget

    def create_webcam_tab(self, device_name):
        webcam_widget = QWidget()
        webcam_layout = QVBoxLayout(webcam_widget)
        webcam_label = QLabel('PC Webcam Feed')
        webcam_label.setMinimumSize(640, 480)
        webcam_label.setStyleSheet(
            'background-color: black; color: white; border: 1px solid gray;')
        webcam_label.setAlignment(Qt.AlignCenter)
        webcam_layout.addWidget(webcam_label)
        webcam_layout.addStretch(1)
        webcam_widget.webcam_label = webcam_label
        return webcam_widget

    def update_rgb_feed(self, device_index, pixmap):
        if 0 <= device_index < len(self.rgb_labels):
            self.rgb_labels[device_index].setPixmap(pixmap)

    def update_thermal_feed(self, device_index, pixmap):
        if 0 <= device_index < len(self.thermal_labels):
            self.thermal_labels[device_index].setPixmap(pixmap)

    def update_webcam_feed(self, pixmap):
        if hasattr(self, 'webcam_label') and self.webcam_label:
            self.webcam_label.setPixmap(pixmap)

    def clear_webcam_feed(self):
        if hasattr(self, 'webcam_label') and self.webcam_label:
            self.webcam_label.clear()
            self.webcam_label.setText('PC Webcam Feed')

    def clear_feed(self, device_index, feed_type='both'):
        if 0 <= device_index < len(self.rgb_labels):
            if feed_type in ['rgb', 'both']:
                self.rgb_labels[device_index].clear()
                self.rgb_labels[device_index].setText('RGB Camera Feed')
            if feed_type in ['thermal', 'both']:
                self.thermal_labels[device_index].clear()
                self.thermal_labels[device_index].setText('Thermal Camera Feed'
                    )

    def clear_all_feeds(self):
        for i in range(len(self.rgb_labels)):
            self.clear_feed(i, 'both')
        self.clear_webcam_feed()

    def set_device_tab_active(self, device_index):
        if 0 <= device_index < self.count():
            self.setCurrentIndex(device_index)

    def get_active_device_index(self):
        return self.currentIndex()

    def get_rgb_label(self, device_index):
        if 0 <= device_index < len(self.rgb_labels):
            return self.rgb_labels[device_index]
        return None

    def get_thermal_label(self, device_index):
        if 0 <= device_index < len(self.thermal_labels):
            return self.thermal_labels[device_index]
        return None
