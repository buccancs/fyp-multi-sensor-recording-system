from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPalette
from PyQt5.QtWidgets import (
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)
from ..utils.logging_config import get_logger
class StatusIndicator(QWidget):
    statusChanged = pyqtSignal(bool, str)
    def __init__(self, label_text="Status", parent=None):
        super().__init__(parent)
        self.is_connected = False
        self.status_text = "Disconnected"
        self.logger = get_logger(__name__)
        self.setup_ui(label_text)
        self.update_appearance()
    def setup_ui(self, label_text):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        self.label = QLabel(label_text)
        self.label.setMinimumWidth(80)
        layout.addWidget(self.label)
        self.indicator = QLabel("●")
        self.indicator.setFixedSize(16, 16)
        self.indicator.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(12)
        self.indicator.setFont(font)
        layout.addWidget(self.indicator)
        self.status_label = QLabel(self.status_text)
        self.status_label.setMinimumWidth(100)
        layout.addWidget(self.status_label)
        layout.addStretch()
    def set_status(self, is_connected, status_text=""):
        if self.is_connected != is_connected or self.status_text != status_text:
            self.is_connected = is_connected
            if status_text:
                self.status_text = status_text
            else:
                self.status_text = "Connected" if is_connected else "Disconnected"
            self.update_appearance()
            self.statusChanged.emit(is_connected, self.status_text)
            self.logger.debug(
                f"Status updated: {self.label.text()} - {self.status_text}"
            )
    def update_appearance(self):
        if self.is_connected:
            self.indicator.setStyleSheet("colour: #4CAF50;")
            self.status_label.setStyleSheet("colour: #2E7D32;")
        else:
            self.indicator.setStyleSheet("colour: #f44336;")
            self.status_label.setStyleSheet("colour: #C62828;")
        self.status_label.setText(self.status_text)
class ModernButton(QPushButton):
    def __init__(self, text, button_type="primary", parent=None):
        super().__init__(text, parent)
        self.button_type = button_type
        self.setup_styling()
    def setup_styling(self):
        base_style = """
            QPushButton {
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 500;
                min-width: 100px;
                min-height: 36px;
            }
            QPushButton:hover {
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                transform: translateY(0px);
            }
            QPushButton:disabled {
                opacity: 0.6;
            }
                QPushButton {
                    background-colour:
                    colour: white;
                }
                QPushButton:hover {
                    background-colour:
                }
                QPushButton {
                    background-colour:
                    colour: white;
                }
                QPushButton:hover {
                    background-colour:
                }
                QPushButton {
                    background-colour:
                    colour: white;
                }
                QPushButton:hover {
                    background-colour:
                }
                QPushButton {
                    background-colour:
                    colour: white;
                }
                QPushButton:hover {
                    background-colour:
                }
            QGroupBox {
                font-weight: 600;
                font-size: 14px;
                border: 2px solid
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-colour:
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                colour:
                background-colour:
            }
            QProgressBar {
                border: 2px solid
                border-radius: 5px;
                text-align: centre;
                background-colour:
            }
            QProgressBar::chunk {
                background-colour:
                border-radius: 3px;
            }
            QPlainTextEdit {
                background-colour:
                colour:
                border: 1px solid
                border-radius: 4px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                padding: 5px;
            }
