#!/usr/bin/env python3
"""
Multi-Sensor Recording System - Desktop Controller
Main entry point for the PyQt5 desktop controller application.

This application serves as the master controller for the multi-sensor recording system,
coordinating Android phones, thermal cameras, and Shimmer sensors.
"""

import sys
import logging
import socket
import threading
import base64
import json
from io import BytesIO
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QPushButton, QLabel, QTextEdit, QGroupBox,
                             QGridLayout, QStatusBar, QScrollArea)
from PyQt5.QtCore import QTimer, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QFont, QPixmap

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SocketServer(QThread):
    """Socket server to receive preview frames from Android devices."""
    
    # Signals for preview frame updates
    rgb_frame_received = pyqtSignal(bytes)
    thermal_frame_received = pyqtSignal(bytes)
    client_connected = pyqtSignal(str)
    client_disconnected = pyqtSignal(str)
    
    def __init__(self, host='0.0.0.0', port=8080):
        super().__init__()
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.clients = []
        
    def run(self):
        """Main server loop."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            logger.info(f"Socket server started on {self.host}:{self.port}")
            
            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.error as e:
                    if self.running:
                        logger.error(f"Socket accept error: {e}")
                        
        except Exception as e:
            logger.error(f"Socket server error: {e}")
        finally:
            self.cleanup()
    
    def handle_client(self, client_socket, address):
        """Handle individual client connections."""
        client_addr = f"{address[0]}:{address[1]}"
        logger.info(f"Client connected: {client_addr}")
        self.client_connected.emit(client_addr)
        self.clients.append(client_socket)
        
        try:
            buffer = ""
            while self.running:
                data = client_socket.recv(4096).decode('utf-8')
                if not data:
                    break
                    
                buffer += data
                
                # Process complete messages (assuming newline-delimited)
                while '\n' in buffer:
                    message, buffer = buffer.split('\n', 1)
                    if message.strip():
                        self.process_message(message.strip())
                        
        except Exception as e:
            logger.error(f"Client handling error for {client_addr}: {e}")
        finally:
            self.clients.remove(client_socket)
            client_socket.close()
            self.client_disconnected.emit(client_addr)
            logger.info(f"Client disconnected: {client_addr}")
    
    def process_message(self, message):
        """Process incoming messages from Android clients."""
        try:
            if message.startswith("PREVIEW_RGB:"):
                # Extract base64 image data
                base64_data = message[12:]  # Remove "PREVIEW_RGB:" prefix
                image_bytes = base64.b64decode(base64_data)
                self.rgb_frame_received.emit(image_bytes)
                
            elif message.startswith("PREVIEW_THERMAL:"):
                # Extract base64 image data
                base64_data = message[16:]  # Remove "PREVIEW_THERMAL:" prefix
                image_bytes = base64.b64decode(base64_data)
                self.thermal_frame_received.emit(image_bytes)
                
            else:
                # Handle other message types
                logger.debug(f"Received message: {message[:100]}...")
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def stop_server(self):
        """Stop the socket server."""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        
        # Close all client connections
        for client in self.clients:
            try:
                client.close()
            except:
                pass
        self.clients.clear()
    
    def cleanup(self):
        """Clean up server resources."""
        if self.server_socket:
            self.server_socket.close()
        logger.info("Socket server stopped")


class MultiSensorController(QMainWindow):
    """Main window for the Multi-Sensor Recording System controller."""
    
    # Signals for inter-component communication
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi-Sensor Recording System Controller")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize socket server
        self.socket_server = SocketServer()
        self.socket_server.rgb_frame_received.connect(self.update_rgb_preview)
        self.socket_server.thermal_frame_received.connect(self.update_thermal_preview)
        self.socket_server.client_connected.connect(self.on_client_connected)
        self.socket_server.client_disconnected.connect(self.on_client_disconnected)
        
        # Initialize UI components
        self.init_ui()
        
        # Initialize status timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)  # Update every second
        
        # Start socket server
        self.socket_server.start()
        
        logger.info("Multi-Sensor Controller initialized")
    
    def init_ui(self):
        """Initialize the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title_label = QLabel("Multi-Sensor Recording System")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        # Control panel
        control_group = self.create_control_panel()
        main_layout.addWidget(control_group)
        
        # Create horizontal layout for status and preview
        middle_layout = QHBoxLayout()
        
        # Device status panel
        status_group = self.create_status_panel()
        middle_layout.addWidget(status_group)
        
        # Preview panel
        preview_group = self.create_preview_panel()
        middle_layout.addWidget(preview_group)
        
        main_layout.addLayout(middle_layout)
        
        # Log panel
        log_group = self.create_log_panel()
        main_layout.addWidget(log_group)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def create_control_panel(self):
        """Create the main control panel."""
        group = QGroupBox("Recording Control")
        layout = QHBoxLayout(group)
        
        # Start recording button
        self.start_button = QPushButton("Start Recording")
        self.start_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        self.start_button.clicked.connect(self.start_recording)
        layout.addWidget(self.start_button)
        
        # Stop recording button
        self.stop_button = QPushButton("Stop Recording")
        self.stop_button.setStyleSheet("QPushButton { background-color: #f44336; color: white; font-weight: bold; }")
        self.stop_button.clicked.connect(self.stop_recording)
        self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)
        
        # Calibration button
        self.calibrate_button = QPushButton("Run Calibration")
        self.calibrate_button.clicked.connect(self.run_calibration)
        layout.addWidget(self.calibrate_button)
        
        return group
    
    def create_status_panel(self):
        """Create the device status panel."""
        group = QGroupBox("Device Status")
        layout = QGridLayout(group)
        
        # Android Phone 1
        layout.addWidget(QLabel("Android Phone 1:"), 0, 0)
        self.phone1_status = QLabel("Disconnected")
        self.phone1_status.setStyleSheet("color: red;")
        layout.addWidget(self.phone1_status, 0, 1)
        
        # Android Phone 2
        layout.addWidget(QLabel("Android Phone 2:"), 1, 0)
        self.phone2_status = QLabel("Disconnected")
        self.phone2_status.setStyleSheet("color: red;")
        layout.addWidget(self.phone2_status, 1, 1)
        
        # Shimmer Sensors
        layout.addWidget(QLabel("Shimmer Sensors:"), 2, 0)
        self.shimmer_status = QLabel("Disconnected")
        self.shimmer_status.setStyleSheet("color: red;")
        layout.addWidget(self.shimmer_status, 2, 1)
        
        # USB Webcams
        layout.addWidget(QLabel("USB Webcams:"), 3, 0)
        self.webcam_status = QLabel("Not detected")
        self.webcam_status.setStyleSheet("color: red;")
        layout.addWidget(self.webcam_status, 3, 1)
        
        return group
    
    def create_preview_panel(self):
        """Create the live preview panel."""
        group = QGroupBox("Live Preview")
        layout = QVBoxLayout(group)
        
        # RGB Camera Preview
        rgb_label = QLabel("RGB Camera:")
        layout.addWidget(rgb_label)
        
        self.rgb_preview = QLabel()
        self.rgb_preview.setMinimumSize(320, 240)
        self.rgb_preview.setStyleSheet("border: 1px solid gray; background-color: black;")
        self.rgb_preview.setText("No RGB preview")
        self.rgb_preview.setAlignment(0x84)  # Qt.AlignCenter
        layout.addWidget(self.rgb_preview)
        
        # Thermal Camera Preview
        thermal_label = QLabel("Thermal Camera:")
        layout.addWidget(thermal_label)
        
        self.thermal_preview = QLabel()
        self.thermal_preview.setMinimumSize(320, 240)
        self.thermal_preview.setStyleSheet("border: 1px solid gray; background-color: black;")
        self.thermal_preview.setText("No thermal preview")
        self.thermal_preview.setAlignment(0x84)  # Qt.AlignCenter
        layout.addWidget(self.thermal_preview)
        
        return group
    
    def create_log_panel(self):
        """Create the log display panel."""
        group = QGroupBox("System Log")
        layout = QVBoxLayout(group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        layout.addWidget(self.log_text)
        
        return group
    
    def start_recording(self):
        """Start the recording process."""
        logger.info("Starting recording session")
        self.log_message("Starting recording session...")
        
        # TODO: Implement actual recording start logic
        # - Send start commands to Android phones
        # - Start USB webcam recording
        # - Begin Shimmer sensor data collection
        # - Start stimulus presentation if configured
        
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_bar.showMessage("Recording in progress...")
        
        self.recording_started.emit()
        self.log_message("Recording started successfully")
    
    def stop_recording(self):
        """Stop the recording process."""
        logger.info("Stopping recording session")
        self.log_message("Stopping recording session...")
        
        # TODO: Implement actual recording stop logic
        # - Send stop commands to Android phones
        # - Stop USB webcam recording
        # - Stop Shimmer sensor data collection
        # - Save and organize recorded data
        
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_bar.showMessage("Ready")
        
        self.recording_stopped.emit()
        self.log_message("Recording stopped successfully")
    
    def run_calibration(self):
        """Run camera calibration routines."""
        logger.info("Running calibration")
        self.log_message("Starting camera calibration...")
        
        # TODO: Implement calibration logic
        # - Capture calibration images from all cameras
        # - Compute camera intrinsics and extrinsics
        # - Save calibration parameters
        
        self.log_message("Calibration completed")
    
    def update_status(self):
        """Update device status indicators."""
        # TODO: Implement actual device status checking
        # For now, this is a placeholder that could be expanded to:
        # - Check network connectivity to Android phones
        # - Verify USB webcam availability
        # - Monitor Shimmer sensor connections
        pass
    
    def log_message(self, message):
        """Add a message to the log display."""
        self.log_text.append(f"[{self.get_timestamp()}] {message}")
        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def get_timestamp(self):
        """Get current timestamp string."""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
    
    @pyqtSlot(bytes)
    def update_rgb_preview(self, image_bytes):
        """Update RGB camera preview with new frame."""
        try:
            pixmap = QPixmap()
            if pixmap.loadFromData(image_bytes):
                # Scale image to fit preview area while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(
                    self.rgb_preview.size(), 
                    1,  # Qt.KeepAspectRatio
                    1   # Qt.SmoothTransformation
                )
                self.rgb_preview.setPixmap(scaled_pixmap)
            else:
                logger.error("Failed to load RGB preview image")
        except Exception as e:
            logger.error(f"Error updating RGB preview: {e}")
    
    @pyqtSlot(bytes)
    def update_thermal_preview(self, image_bytes):
        """Update thermal camera preview with new frame."""
        try:
            pixmap = QPixmap()
            if pixmap.loadFromData(image_bytes):
                # Scale image to fit preview area while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(
                    self.thermal_preview.size(), 
                    1,  # Qt.KeepAspectRatio
                    1   # Qt.SmoothTransformation
                )
                self.thermal_preview.setPixmap(scaled_pixmap)
            else:
                logger.error("Failed to load thermal preview image")
        except Exception as e:
            logger.error(f"Error updating thermal preview: {e}")
    
    @pyqtSlot(str)
    def on_client_connected(self, client_addr):
        """Handle client connection."""
        self.log_message(f"Android device connected: {client_addr}")
        # Update device status indicators
        if "phone1" not in [client.lower() for client in self.socket_server.clients]:
            self.phone1_status.setText("Connected")
            self.phone1_status.setStyleSheet("color: green;")
        elif "phone2" not in [client.lower() for client in self.socket_server.clients]:
            self.phone2_status.setText("Connected")
            self.phone2_status.setStyleSheet("color: green;")
    
    @pyqtSlot(str)
    def on_client_disconnected(self, client_addr):
        """Handle client disconnection."""
        self.log_message(f"Android device disconnected: {client_addr}")
        # Update device status indicators
        if len(self.socket_server.clients) == 0:
            self.phone1_status.setText("Disconnected")
            self.phone1_status.setStyleSheet("color: red;")
            self.phone2_status.setText("Disconnected")
            self.phone2_status.setStyleSheet("color: red;")
    
    def closeEvent(self, event):
        """Handle application close event."""
        logger.info("Shutting down Multi-Sensor Controller")
        self.socket_server.stop_server()
        self.socket_server.wait()  # Wait for thread to finish
        event.accept()


def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Multi-Sensor Recording System")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Multi-Sensor Research")
    
    # Create and show main window
    controller = MultiSensorController()
    controller.show()
    
    logger.info("Application started")
    
    # Start event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
