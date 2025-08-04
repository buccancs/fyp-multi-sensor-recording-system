from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QProgressBar, QFrame, QGroupBox, QSizePolicy
from PyQt5.QtGui import QFont, QPalette
from bucika_gsr.utils.logging_config import get_logger


class StatusIndicator(QWidget):
    statusChanged = pyqtSignal(bool, str)

    def __init__(self, label_text='Status', parent=None):
        super().__init__(parent)
        self.is_connected = False
        self.status_text = 'Disconnected'
        self.logger = get_logger(__name__)
        self.setup_ui(label_text)
        self.update_appearance()

    def setup_ui(self, label_text):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        self.label = QLabel(label_text)
        self.label.setMinimumWidth(80)
        layout.addWidget(self.label)
        self.indicator = QLabel('●')
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

    def set_status(self, is_connected, status_text=''):
        if (self.is_connected != is_connected or self.status_text !=
            status_text):
            self.is_connected = is_connected
            if status_text:
                self.status_text = status_text
            else:
                self.status_text = ('Connected' if is_connected else
                    'Disconnected')
            self.update_appearance()
            self.statusChanged.emit(is_connected, self.status_text)
            self.logger.debug(
                f'Status updated: {self.label.text()} - {self.status_text}')

    def update_appearance(self):
        if self.is_connected:
            self.indicator.setStyleSheet('color: #4CAF50;')
            self.status_label.setStyleSheet('color: #2E7D32;')
        else:
            self.indicator.setStyleSheet('color: #f44336;')
            self.status_label.setStyleSheet('color: #C62828;')
        self.status_label.setText(self.status_text)


class ModernButton(QPushButton):

    def __init__(self, text, button_type='primary', parent=None):
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
        """
        color_styles = {'primary':
            """
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """
            , 'success':
            """
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #388E3C;
                }
            """
            , 'danger':
            """
                QPushButton {
                    background-color: #f44336;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #D32F2F;
                }
            """
            , 'secondary':
            """
                QPushButton {
                    background-color: #757575;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #616161;
                }
            """
            }
        style = base_style + color_styles.get(self.button_type,
            color_styles['primary'])
        self.setStyleSheet(style)


class ModernGroupBox(QGroupBox):

    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setup_styling()

    def setup_styling(self):
        self.setStyleSheet(
            """
            QGroupBox {
                font-weight: 600;
                font-size: 14px;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #FAFAFA;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #424242;
                background-color: #FAFAFA;
            }
        """
            )


class ProgressIndicator(QWidget):

    def __init__(self, label_text='Progress', parent=None):
        super().__init__(parent)
        self.setup_ui(label_text)

    def setup_ui(self, label_text):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(label_text)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 2px solid #E0E0E0;
                border-radius: 5px;
                text-align: center;
                background-color: #F5F5F5;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
                border-radius: 3px;
            }
        """
            )
        layout.addWidget(self.progress_bar)

    def set_progress(self, value, text=''):
        self.progress_bar.setValue(max(0, min(100, value)))
        if text:
            self.label.setText(text)

    def set_indeterminate(self, active=True):
        if active:
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(0)
        else:
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(100)


class LogViewer(QWidget):

    def __init__(self, title='System Log', parent=None):
        super().__init__(parent)
        self.max_lines = 1000
        self.setup_ui(title)

    def setup_ui(self, title):
        layout = QVBoxLayout(self)
        title_label = QLabel(title)
        title_label.setStyleSheet(
            'font-weight: 600; font-size: 14px; margin-bottom: 5px;')
        layout.addWidget(title_label)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumBlockCount(self.max_lines)
        self.log_text.setStyleSheet(
            """
            QTextEdit {
                background-color: #263238;
                color: #ECEFF1;
                border: 1px solid #455A64;
                border-radius: 4px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                padding: 5px;
            }
        """
            )
        layout.addWidget(self.log_text)
        button_layout = QHBoxLayout()
        self.clear_button = ModernButton('Clear', 'secondary')
        self.clear_button.clicked.connect(self.clear_log)
        button_layout.addWidget(self.clear_button)
        button_layout.addStretch()
        self.save_button = ModernButton('Save Log', 'primary')
        self.save_button.clicked.connect(self.save_log)
        button_layout.addWidget(self.save_button)
        layout.addLayout(button_layout)

    def add_log_entry(self, message, level='INFO'):
        from datetime import datetime
        timestamp = datetime.now().strftime('%H:%M:%S')
        level_colors = {'DEBUG': '#90A4AE', 'INFO': '#81C784', 'WARNING':
            '#FFB74D', 'ERROR': '#E57373', 'CRITICAL': '#F44336'}
        color = level_colors.get(level, '#ECEFF1')
        formatted_message = (
            f'<span style="color: {color};">[{timestamp}] {level}: {message}</span>'
            )
        self.log_text.append(formatted_message)
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_log(self):
        self.log_text.clear()
        self.add_log_entry('Log cleared', 'INFO')

    def save_log(self):
        from PyQt5.QtWidgets import QFileDialog
        filename, _ = QFileDialog.getSaveFileName(self, 'Save Log',
            'system_log.txt', 'Text Files (*.txt)')
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.log_text.toPlainText())
                self.add_log_entry(f'Log saved to {filename}', 'INFO')
            except Exception as e:
                self.add_log_entry(f'Failed to save log: {e}', 'ERROR')


class ConnectionManager(QWidget):
    connectionRequested = pyqtSignal(str)
    disconnectionRequested = pyqtSignal(str)

    def __init__(self, device_type='Generic Device', parent=None):
        super().__init__(parent)
        self.device_type = device_type
        self.is_connected = False
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        device_label = QLabel(self.device_type)
        device_label.setStyleSheet('font-weight: 600; font-size: 14px;')
        layout.addWidget(device_label)
        self.status_indicator = StatusIndicator('Status')
        layout.addWidget(self.status_indicator)
        button_layout = QHBoxLayout()
        self.connect_button = ModernButton('Connect', 'success')
        self.connect_button.clicked.connect(self.request_connection)
        button_layout.addWidget(self.connect_button)
        self.disconnect_button = ModernButton('Disconnect', 'danger')
        self.disconnect_button.clicked.connect(self.request_disconnection)
        self.disconnect_button.setEnabled(False)
        button_layout.addWidget(self.disconnect_button)
        layout.addLayout(button_layout)

    def request_connection(self):
        self.connectionRequested.emit(self.device_type)

    def request_disconnection(self):
        self.disconnectionRequested.emit(self.device_type)

    def set_connection_status(self, connected, status_text=''):
        self.is_connected = connected
        self.status_indicator.set_status(connected, status_text)
        self.connect_button.setEnabled(not connected)
        self.disconnect_button.setEnabled(connected)


def apply_dark_theme(widget):
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, Qt.darkGray)
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, Qt.black)
    dark_palette.setColor(QPalette.AlternateBase, Qt.darkCyan)
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, Qt.darkGray)
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, Qt.blue)
    dark_palette.setColor(QPalette.Highlight, Qt.blue)
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)
    widget.setPalette(dark_palette)


def create_separator(orientation=Qt.Horizontal):
    separator = QFrame()
    if orientation == Qt.Horizontal:
        separator.setFrameShape(QFrame.HLine)
    else:
        separator.setFrameShape(QFrame.VLine)
    separator.setFrameShadow(QFrame.Sunken)
    separator.setStyleSheet('color: #E0E0E0;')
    return separator
