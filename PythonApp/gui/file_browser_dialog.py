"""
File Browser Dialog for PyQt GUI

This module implements a comprehensive file browser dialog for the Multi-Sensor Recording System.
It provides file browsing, preview, and management capabilities similar to the web interface.

Author: Multi-Sensor Recording System Team
Date: 2025-01-01
"""

import os
import sys
from datetime import datetime
from typing import List, Optional

from PyQt5.QtCore import QDir, QFileInfo, Qt, QThread, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPixmap, QTextDocument
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTextEdit,
    QTreeView,
    QVBoxLayout,
)


class FilePreviewWidget(QFrame):
    """Widget for previewing different file types"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel)
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout(self)

        self.preview_scroll = QScrollArea()
        self.preview_scroll.setWidgetResizable(True)
        self.preview_scroll.setAlignment(Qt.AlignCenter)

        self.preview_label = QLabel("Select a file to preview")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet(
            """
            QLabel {
                color:
                font-size: 14px;
                padding: 20px;
                border: 2px dashed
                border-radius: 8px;
                background-color:
            }
        """
        )

        self.preview_scroll.setWidget(self.preview_label)
        layout.addWidget(self.preview_scroll)

        self.info_group = QGroupBox("File Information")
        info_layout = QVBoxLayout(self.info_group)

        self.info_text = QTextEdit()
        self.info_text.setMaximumHeight(120)
        self.info_text.setReadOnly(True)
        info_layout.addWidget(self.info_text)

        layout.addWidget(self.info_group)

        self.current_file_path = None

    def preview_file(self, file_path: str):
        """Preview a file based on its type"""
        self.current_file_path = file_path

        if not os.path.exists(file_path):
            self.show_error("File not found")
            return

        file_info = QFileInfo(file_path)
        file_size = file_info.size()
        file_suffix = file_info.suffix().lower()

        info_text = f"""
Name: {file_info.fileName()}
Size: {self.format_file_size(file_size)}
Type: {file_suffix.upper() if file_suffix else 'Unknown'}
Modified: {file_info.lastModified().toString(Qt.DefaultLocaleLongDate)}
Path: {file_path}
        """.strip()
        self.info_text.setPlainText(info_text)

        if file_suffix in ["jpg", "jpeg", "png", "gif", "bmp"]:
            self.preview_image(file_path)
        elif file_suffix in ["txt", "log", "json", "xml", "csv"]:
            self.preview_text(file_path)
        elif file_suffix in ["mp4", "avi", "mov", "mkv"]:
            self.preview_video(file_path)
        else:
            self.show_generic_preview(file_path, file_suffix)

    def preview_image(self, file_path: str):
        """Preview image files"""
        try:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():

                scaled_pixmap = pixmap.scaled(
                    600, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                self.preview_label.setPixmap(scaled_pixmap)
                self.preview_label.setText("")
            else:
                self.show_error("Cannot load image")
        except Exception as e:
            self.show_error(f"Error loading image: {str(e)}")

    def preview_text(self, file_path: str):
        """Preview text files"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(5000)
                if len(content) == 5000:
                    content += "\n\n... (file truncated for preview)"

            self.preview_label.setPixmap(QPixmap())
            self.preview_label.setText(content)
            self.preview_label.setFont(QFont("Courier", 9))
            self.preview_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            self.preview_label.setWordWrap(True)
        except Exception as e:
            self.show_error(f"Error reading text file: {str(e)}")

    def preview_video(self, file_path: str):
        """Preview video files (show file info only)"""
        self.preview_label.setPixmap(QPixmap())
        self.preview_label.setText(
            f"""
🎥 Video File

{os.path.basename(file_path)}

Click 'Open' to play with external application
or use the playback page for detailed analysis.
        """
        )
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setFont(QFont("Arial", 10))

    def show_generic_preview(self, file_path: str, file_type: str):
        """Show generic preview for unsupported file types"""
        self.preview_label.setPixmap(QPixmap())
        self.preview_label.setText(
            f"""
📄 {file_type.upper()} File

{os.path.basename(file_path)}

Preview not available for this file type.
Click 'Open' to open with external application.
        """
        )
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setFont(QFont("Arial", 10))

    def show_error(self, message: str):
        """Show error message in preview area"""
        self.preview_label.setPixmap(QPixmap())
        self.preview_label.setText(f"❌ {message}")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setFont(QFont("Arial", 10))
        self.preview_label.setStyleSheet("QLabel { color: #d32f2f; }")

    def clear_preview(self):
        """Clear the preview area"""
        self.preview_label.setPixmap(QPixmap())
        self.preview_label.setText("Select a file to preview")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setFont(QFont("Arial", 10))
        self.preview_label.setStyleSheet(
            """
            QLabel {
                color:
                font-size: 14px;
                padding: 20px;
                border: 2px dashed
                border-radius: 8px;
                background-color:
            }
        """
        )
        self.info_text.clear()
        self.current_file_path = None

    @staticmethod
    def format_file_size(bytes_size: int) -> str:
        """Format file size in human readable format"""
        if bytes_size < 1024:
            return f"{bytes_size} B"
        elif bytes_size < 1024 * 1024:
            return f"{bytes_size / 1024:.1f} KB"
        elif bytes_size < 1024 * 1024 * 1024:
            return f"{bytes_size / (1024 * 1024):.1f} MB"
        else:
            return f"{bytes_size / (1024 * 1024 * 1024):.1f} GB"


class FileBrowserDialog(QDialog):
    """Comprehensive file browser dialog for the Multi-Sensor Recording System"""

    def __init__(self, parent=None, initial_path: str = None):
        super().__init__(parent)
        self.setWindowTitle("File Browser - Multi-Sensor Recording System")
        self.setModal(True)
        self.resize(1000, 700)

        self.recordings_path = initial_path or os.path.join(os.getcwd(), "recordings")
        if not os.path.exists(self.recordings_path):
            os.makedirs(self.recordings_path, exist_ok=True)

        self.current_path = self.recordings_path
        self.selected_file = None

        self.setup_ui()
        self.load_directory(self.current_path)

    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)

        header_layout = QHBoxLayout()

        self.back_btn = QPushButton("⬅ Back")
        self.back_btn.clicked.connect(self.go_back)
        header_layout.addWidget(self.back_btn)

        self.up_btn = QPushButton("⬆ Up")
        self.up_btn.clicked.connect(self.go_up)
        header_layout.addWidget(self.up_btn)

        self.home_btn = QPushButton("🏠 Recordings")
        self.home_btn.clicked.connect(self.go_home)
        header_layout.addWidget(self.home_btn)

        self.path_label = QLabel(self.current_path)
        self.path_label.setStyleSheet(
            "QLabel { background: #f0f0f0; padding: 5px; border-radius: 3px; }"
        )
        header_layout.addWidget(self.path_label, 1)

        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh)
        header_layout.addWidget(self.refresh_btn)

        layout.addLayout(header_layout)

        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Type to filter files...")
        self.search_box.textChanged.connect(self.filter_files)
        search_layout.addWidget(self.search_box)

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(
            [
                "All Files",
                "Images",
                "Videos",
                "Text Files",
                "Session Files",
                "Recent Files",
            ]
        )
        self.filter_combo.currentTextChanged.connect(self.apply_filter)
        search_layout.addWidget(self.filter_combo)

        layout.addLayout(search_layout)

        splitter = QSplitter(Qt.Horizontal)

        self.file_list = QListWidget()
        self.file_list.setMinimumWidth(400)
        self.file_list.itemClicked.connect(self.on_file_selected)
        self.file_list.itemDoubleClicked.connect(self.on_file_double_clicked)
        splitter.addWidget(self.file_list)

        self.preview_widget = FilePreviewWidget()
        splitter.addWidget(self.preview_widget)

        splitter.setSizes([400, 600])
        layout.addWidget(splitter)

        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("QLabel { color: #666; padding: 5px; }")
        layout.addWidget(self.status_label)

        button_layout = QHBoxLayout()

        self.open_btn = QPushButton("Open")
        self.open_btn.clicked.connect(self.open_selected_file)
        self.open_btn.setEnabled(False)
        button_layout.addWidget(self.open_btn)

        self.open_external_btn = QPushButton("Open External")
        self.open_external_btn.clicked.connect(self.open_external)
        self.open_external_btn.setEnabled(False)
        button_layout.addWidget(self.open_external_btn)

        self.copy_path_btn = QPushButton("Copy Path")
        self.copy_path_btn.clicked.connect(self.copy_path)
        self.copy_path_btn.setEnabled(False)
        button_layout.addWidget(self.copy_path_btn)

        button_layout.addStretch()

        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        button_layout.addWidget(self.close_btn)

        layout.addLayout(button_layout)

    def load_directory(self, path: str):
        """Load directory contents"""
        try:
            self.current_path = path
            self.path_label.setText(path)
            self.file_list.clear()
            self.preview_widget.clear_preview()

            if not os.path.exists(path):
                self.status_label.setText(f"Directory does not exist: {path}")
                return

            items = []

            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    list_item = QListWidgetItem(f"📁 {item}")
                    list_item.setData(Qt.UserRole, item_path)
                    list_item.setData(Qt.UserRole + 1, "directory")
                    items.append(list_item)

            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isfile(item_path):
                    file_info = QFileInfo(item_path)
                    file_size = self.preview_widget.format_file_size(file_info.size())
                    modified = file_info.lastModified().toString("yyyy-MM-dd hh:mm")

                    icon = self.get_file_icon(file_info.suffix().lower())

                    list_item = QListWidgetItem(
                        f"{icon} {item} ({file_size}, {modified})"
                    )
                    list_item.setData(Qt.UserRole, item_path)
                    list_item.setData(Qt.UserRole + 1, "file")
                    items.append(list_item)

            for item in items:
                self.file_list.addItem(item)

            dir_count = sum(
                1 for item in items if item.data(Qt.UserRole + 1) == "directory"
            )
            file_count = sum(
                1 for item in items if item.data(Qt.UserRole + 1) == "file"
            )
            self.status_label.setText(f"{dir_count} folders, {file_count} files")

            self.back_btn.setEnabled(len(self.get_parent_directory(path)) > 0)
            self.up_btn.setEnabled(path != self.recordings_path)

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load directory: {str(e)}")
            self.status_label.setText(f"Error: {str(e)}")

    def get_file_icon(self, extension: str) -> str:
        """Get emoji icon for file type"""
        icons = {
            "jpg": "🖼️",
            "jpeg": "🖼️",
            "png": "🖼️",
            "gif": "🖼️",
            "bmp": "🖼️",
            "mp4": "🎥",
            "avi": "🎥",
            "mov": "🎥",
            "mkv": "🎥",
            "mp3": "🎵",
            "wav": "🎵",
            "ogg": "🎵",
            "txt": "📄",
            "log": "📄",
            "json": "📄",
            "xml": "📄",
            "csv": "📊",
            "pdf": "📕",
            "zip": "📦",
            "rar": "📦",
        }
        return icons.get(extension, "📄")

    def on_file_selected(self, item: QListWidgetItem):
        """Handle file selection"""
        file_path = item.data(Qt.UserRole)
        file_type = item.data(Qt.UserRole + 1)

        if file_type == "file":
            self.selected_file = file_path
            self.preview_widget.preview_file(file_path)
            self.open_btn.setEnabled(True)
            self.open_external_btn.setEnabled(True)
            self.copy_path_btn.setEnabled(True)
        else:
            self.selected_file = None
            self.preview_widget.clear_preview()
            self.open_btn.setEnabled(False)
            self.open_external_btn.setEnabled(False)
            self.copy_path_btn.setEnabled(False)

    def on_file_double_clicked(self, item: QListWidgetItem):
        """Handle file double-click"""
        file_path = item.data(Qt.UserRole)
        file_type = item.data(Qt.UserRole + 1)

        if file_type == "directory":
            self.load_directory(file_path)
        else:
            self.open_selected_file()

    def go_back(self):
        """Go back to previous directory"""

        parent = self.get_parent_directory(self.current_path)
        if parent:
            self.load_directory(parent)

    def go_up(self):
        """Go up one directory level"""
        parent = self.get_parent_directory(self.current_path)
        if parent:
            self.load_directory(parent)

    def go_home(self):
        """Go to recordings home directory"""
        self.load_directory(self.recordings_path)

    def refresh(self):
        """Refresh current directory"""
        self.load_directory(self.current_path)

    def get_parent_directory(self, path: str) -> str:
        """Get parent directory path"""
        parent = os.path.dirname(path)
        return parent if parent != path else ""

    def filter_files(self):
        """Filter files based on search text"""
        search_text = self.search_box.text().lower()
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            visible = search_text in item.text().lower()
            item.setHidden(not visible)

    def apply_filter(self, filter_type: str):
        """Apply file type filter"""

        self.load_directory(self.current_path)

    def open_selected_file(self):
        """Open selected file and close dialog"""
        if self.selected_file:
            self.accept()

    def open_external(self):
        """Open file with external application"""
        if self.selected_file:
            try:
                import subprocess

                if sys.platform.startswith("win"):
                    os.startfile(self.selected_file)
                elif sys.platform.startswith("darwin"):
                    subprocess.call(["open", self.selected_file])
                else:
                    subprocess.call(["xdg-open", self.selected_file])
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to open file: {str(e)}")

    def copy_path(self):
        """Copy file path to clipboard"""
        if self.selected_file:
            from PyQt5.QtWidgets import QApplication

            clipboard = QApplication.clipboard()
            clipboard.setText(self.selected_file)
            self.status_label.setText("Path copied to clipboard")

    def get_selected_file(self) -> Optional[str]:
        """Get the selected file path"""
        return self.selected_file


def show_file_browser(parent=None, initial_path: str = None) -> Optional[str]:
    """
    Show file browser dialog and return selected file path

    Args:
        parent: Parent widget
        initial_path: Initial directory to show

    Returns:
        Selected file path or None if cancelled
    """
    dialog = FileBrowserDialog(parent, initial_path)
    if dialog.exec_() == QDialog.Accepted:
        return dialog.get_selected_file()
    return None


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    selected_file = show_file_browser()
    if selected_file:
        print(f"Selected file: {selected_file}")
    else:
        print("No file selected")

    sys.exit()
