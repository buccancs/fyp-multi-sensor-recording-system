"""
Main Controller for the Multi-Sensor Recording System.

This module implements the MainController class that follows the Controller/Presenter pattern
to separate UI concerns from business logic. It orchestrates all backend services and provides
a clean interface for the MainWindow to interact with.

Created: 2025-07-30
Author: Junie (Architectural Refactoring)
"""

from typing import Optional, Dict, Any, List
from PyQt5.QtCore import QObject, pyqtSignal

# Import modern logging system
from utils.logging_config import get_logger

# Import backend services
from network.device_server import JsonSocketServer
from session.session_manager import SessionManager
from session.session_logger import get_session_logger
from webcam.webcam_capture import WebcamCapture
from gui.stimulus_controller import StimulusController


class MainController(QObject):
    """
    Main Controller that orchestrates all backend services.
    
    This class implements the Controller/Presenter pattern to separate UI concerns
    from business logic. It manages the lifecycle of all backend services and
    provides a clean interface for the UI to interact with.
    
    Signals are used to communicate with the UI layer, ensuring thread-safe
    communication and loose coupling between the controller and view.
    """
    
    # UI State Signals
    server_status_changed = pyqtSignal(bool)  # server_running
    webcam_status_changed = pyqtSignal(str)   # status_message
    session_status_changed = pyqtSignal(str, bool)  # session_id, is_active
    
    # Device Management Signals
    device_connected = pyqtSignal(str, list)  # device_id, capabilities
    device_disconnected = pyqtSignal(str)     # device_id
    device_status_received = pyqtSignal(str, dict)  # device_id, status_data
    
    # Data Signals
    preview_frame_received = pyqtSignal(str, str, str)  # device_id, frame_type, base64_data
    webcam_frame_ready = pyqtSignal(object)  # QPixmap
    sensor_data_received = pyqtSignal(str, dict)  # device_id, sensor_data
    
    # Event Signals
    recording_started = pyqtSignal(str)  # session_id
    recording_stopped = pyqtSignal(str, float)  # session_id, duration
    calibration_completed = pyqtSignal(str, dict)  # device_id, result
    
    # Error Signals
    error_occurred = pyqtSignal(str, str)  # component, error_message
    
    def __init__(self, parent=None):
        """
        Initialize the MainController with dependency injection.
        
        Args:
            parent: Parent QObject (optional)
        """
        super().__init__(parent)
        
        # Initialize logger
        self.logger = get_logger(__name__)
        
        # Backend services (injected dependencies)
        self._session_manager: Optional[SessionManager] = None
        self._json_server: Optional[JsonSocketServer] = None
        self._webcam_capture: Optional[WebcamCapture] = None
        self._stimulus_controller: Optional[StimulusController] = None
        self._session_logger = None
        
        # Controller state
        self._server_running = False
        self._webcam_previewing = False
        self._webcam_recording = False
        self._current_session_id: Optional[str] = None
        
        self.logger.info("MainController initialized")
    
    def inject_dependencies(self, 
                          session_manager: SessionManager,
                          json_server: JsonSocketServer,
                          webcam_capture: WebcamCapture,
                          stimulus_controller: StimulusController):
        """
        Inject backend service dependencies.
        
        This method implements dependency injection to provide the controller
        with all required backend services. This allows for better testability
        and loose coupling.
        
        Args:
            session_manager: Session management service
            json_server: Network communication service
            webcam_capture: Webcam capture service
            stimulus_controller: Stimulus presentation service
        """
        self._session_manager = session_manager
        self._json_server = json_server
        self._webcam_capture = webcam_capture
        self._stimulus_controller = stimulus_controller
        self._session_logger = get_session_logger()
        
        # Connect service signals to controller handlers
        self._connect_service_signals()
        
        self.logger.info("Dependencies injected successfully")
    
    def _connect_service_signals(self):
        """Connect all backend service signals to controller handlers."""
        if not all([self._json_server, self._webcam_capture, self._stimulus_controller]):
            raise RuntimeError("Dependencies must be injected before connecting signals")
        
        # JSON Server signals
        self._json_server.device_connected.connect(self._on_device_connected)
        self._json_server.device_disconnected.connect(self._on_device_disconnected)
        self._json_server.status_received.connect(self._on_status_received)
        self._json_server.ack_received.connect(self._on_ack_received)
        self._json_server.preview_frame_received.connect(self._on_preview_frame_received)
        self._json_server.sensor_data_received.connect(self._on_sensor_data_received)
        self._json_server.notification_received.connect(self._on_notification_received)
        self._json_server.error_occurred.connect(self._on_server_error)
        
        # Webcam signals
        self._webcam_capture.frame_ready.connect(self._on_webcam_frame_ready)
        self._webcam_capture.recording_started.connect(self._on_webcam_recording_started)
        self._webcam_capture.recording_stopped.connect(self._on_webcam_recording_stopped)
        self._webcam_capture.error_occurred.connect(self._on_webcam_error)
        self._webcam_capture.status_changed.connect(self._on_webcam_status_changed)
        
        # Stimulus controller signals
        self._stimulus_controller.seek_requested.connect(self._on_stimulus_seek_requested)
        self._stimulus_controller.screen_changed.connect(self._on_stimulus_screen_changed)
        self._stimulus_controller.start_recording_play_requested.connect(self._on_start_recording_play_requested)
        self._stimulus_controller.mark_event_requested.connect(self._on_mark_event_requested)
        self._stimulus_controller.status_changed.connect(self._on_stimulus_status_changed)
        self._stimulus_controller.experiment_started.connect(self._on_stimulus_experiment_started)
        self._stimulus_controller.experiment_ended.connect(self._on_stimulus_experiment_ended)
        self._stimulus_controller.error_occurred.connect(self._on_stimulus_error)
        
        # Session logger signals
        if self._session_logger:
            self._session_logger.session_started.connect(self._on_session_logger_session_started)
            self._session_logger.session_ended.connect(self._on_session_logger_session_ended)
            self._session_logger.error_occurred.connect(self._on_session_logger_error)
    
    # Public API Methods (called by UI)
    
    def start_server(self) -> bool:
        """
        Start the JSON socket server.
        
        Returns:
            bool: True if server started successfully
        """
        try:
            if not self._json_server:
                raise RuntimeError("JSON server not injected")
            
            if not self._server_running:
                self._json_server.start()
                self._server_running = True
                self.server_status_changed.emit(True)
                self.logger.info("Server started successfully")
                return True
            return True
        except Exception as e:
            self.logger.error(f"Failed to start server: {e}")
            self.error_occurred.emit("server", str(e))
            return False
    
    def stop_server(self) -> bool:
        """
        Stop the JSON socket server.
        
        Returns:
            bool: True if server stopped successfully
        """
        try:
            if self._json_server and self._server_running:
                self._json_server.stop_server()
                self._server_running = False
                self.server_status_changed.emit(False)
                self.logger.info("Server stopped successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to stop server: {e}")
            self.error_occurred.emit("server", str(e))
            return False
    
    def start_session(self) -> Optional[str]:
        """
        Start a new recording session.
        
        Returns:
            Optional[str]: Session ID if successful, None otherwise
        """
        try:
            if not self._session_manager:
                raise RuntimeError("Session manager not injected")
            
            session_id = self._session_manager.start_session()
            if session_id:
                self._current_session_id = session_id
                self.session_status_changed.emit(session_id, True)
                self.recording_started.emit(session_id)
                self.logger.info(f"Session started: {session_id}")
            return session_id
        except Exception as e:
            self.logger.error(f"Failed to start session: {e}")
            self.error_occurred.emit("session", str(e))
            return None
    
    def stop_session(self) -> bool:
        """
        Stop the current recording session.
        
        Returns:
            bool: True if session stopped successfully
        """
        try:
            if not self._session_manager or not self._current_session_id:
                return False
            
            duration = self._session_manager.end_session(self._current_session_id)
            self.session_status_changed.emit(self._current_session_id, False)
            self.recording_stopped.emit(self._current_session_id, duration)
            self.logger.info(f"Session stopped: {self._current_session_id}")
            self._current_session_id = None
            return True
        except Exception as e:
            self.logger.error(f"Failed to stop session: {e}")
            self.error_occurred.emit("session", str(e))
            return False
    
    def start_webcam_preview(self) -> bool:
        """
        Start webcam preview.
        
        Returns:
            bool: True if preview started successfully
        """
        try:
            if not self._webcam_capture:
                raise RuntimeError("Webcam capture not injected")
            
            if not self._webcam_previewing:
                self._webcam_capture.start_preview()
                self._webcam_previewing = True
                self.logger.info("Webcam preview started")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start webcam preview: {e}")
            self.error_occurred.emit("webcam", str(e))
            return False
    
    def stop_webcam_preview(self) -> bool:
        """
        Stop webcam preview.
        
        Returns:
            bool: True if preview stopped successfully
        """
        try:
            if self._webcam_capture and self._webcam_previewing:
                self._webcam_capture.stop_preview()
                self._webcam_previewing = False
                self.logger.info("Webcam preview stopped")
            return True
        except Exception as e:
            self.logger.error(f"Failed to stop webcam preview: {e}")
            self.error_occurred.emit("webcam", str(e))
            return False
    
    def start_webcam_recording(self, session_id: str) -> bool:
        """
        Start webcam recording for a session.
        
        Args:
            session_id: Session ID for the recording
            
        Returns:
            bool: True if recording started successfully
        """
        try:
            if not self._webcam_capture:
                raise RuntimeError("Webcam capture not injected")
            
            if not self._webcam_recording:
                self._webcam_capture.start_recording(session_id)
                self._webcam_recording = True
                self.logger.info(f"Webcam recording started for session: {session_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start webcam recording: {e}")
            self.error_occurred.emit("webcam", str(e))
            return False
    
    def stop_webcam_recording(self) -> bool:
        """
        Stop webcam recording.
        
        Returns:
            bool: True if recording stopped successfully
        """
        try:
            if self._webcam_capture and self._webcam_recording:
                self._webcam_capture.stop_recording()
                self._webcam_recording = False
                self.logger.info("Webcam recording stopped")
            return True
        except Exception as e:
            self.logger.error(f"Failed to stop webcam recording: {e}")
            self.error_occurred.emit("webcam", str(e))
            return False
    
    def send_command_to_device(self, device_id: str, command: str, params: Dict[str, Any] = None) -> bool:
        """
        Send a command to a specific device.
        
        Args:
            device_id: Target device ID
            command: Command to send
            params: Command parameters
            
        Returns:
            bool: True if command sent successfully
        """
        try:
            if not self._json_server:
                raise RuntimeError("JSON server not injected")
            
            from network.device_server import create_command_message
            command_dict = create_command_message(command, **(params or {}))
            self._json_server.send_command(device_id, command_dict)
            self.logger.debug(f"Command sent to {device_id}: {command}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to send command to {device_id}: {e}")
            self.error_occurred.emit("network", str(e))
            return False
    
    def broadcast_command(self, command: str, params: Dict[str, Any] = None) -> bool:
        """
        Broadcast a command to all connected devices.
        
        Args:
            command: Command to broadcast
            params: Command parameters
            
        Returns:
            bool: True if command broadcast successfully
        """
        try:
            if not self._json_server:
                raise RuntimeError("JSON server not injected")
            
            from network.device_server import create_command_message
            command_dict = create_command_message(command, **(params or {}))
            self._json_server.broadcast_command(command_dict)
            self.logger.debug(f"Command broadcast: {command}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to broadcast command: {e}")
            self.error_occurred.emit("network", str(e))
            return False
    
    def get_connected_devices(self) -> List[str]:
        """
        Get list of connected device IDs.
        
        Returns:
            List[str]: List of connected device IDs
        """
        if self._json_server:
            return list(self._json_server.get_connected_devices().keys())
        return []
    
    def is_server_running(self) -> bool:
        """Check if server is running."""
        return self._server_running
    
    def is_webcam_previewing(self) -> bool:
        """Check if webcam is previewing."""
        return self._webcam_previewing
    
    def is_webcam_recording(self) -> bool:
        """Check if webcam is recording."""
        return self._webcam_recording
    
    def get_current_session_id(self) -> Optional[str]:
        """Get current session ID."""
        return self._current_session_id
    
    # Signal Handlers (private methods)
    
    def _on_device_connected(self, device_id: str, capabilities: list):
        """Handle device connection."""
        self.device_connected.emit(device_id, capabilities)
        self.logger.info(f"Device connected: {device_id}")
    
    def _on_device_disconnected(self, device_id: str):
        """Handle device disconnection."""
        self.device_disconnected.emit(device_id)
        self.logger.info(f"Device disconnected: {device_id}")
    
    def _on_status_received(self, device_id: str, status_data: dict):
        """Handle device status updates."""
        self.device_status_received.emit(device_id, status_data)
    
    def _on_ack_received(self, device_id: str, cmd: str, success: bool, message: str):
        """Handle command acknowledgments."""
        if not success:
            self.error_occurred.emit(device_id, f"Command {cmd} failed: {message}")
    
    def _on_preview_frame_received(self, device_id: str, frame_type: str, base64_data: str):
        """Handle preview frame data."""
        self.preview_frame_received.emit(device_id, frame_type, base64_data)
    
    def _on_sensor_data_received(self, device_id: str, sensor_data: dict):
        """Handle sensor data."""
        self.sensor_data_received.emit(device_id, sensor_data)
    
    def _on_notification_received(self, device_id: str, event_type: str, event_data: dict):
        """Handle device notifications."""
        self.logger.debug(f"Notification from {device_id}: {event_type}")
    
    def _on_server_error(self, device_id: str, error_message: str):
        """Handle server errors."""
        self.error_occurred.emit(device_id, error_message)
    
    def _on_webcam_frame_ready(self, pixmap):
        """Handle webcam frame updates."""
        self.webcam_frame_ready.emit(pixmap)
    
    def _on_webcam_recording_started(self, filepath: str):
        """Handle webcam recording start."""
        self.logger.info(f"Webcam recording started: {filepath}")
    
    def _on_webcam_recording_stopped(self, filepath: str, duration: float):
        """Handle webcam recording stop."""
        self.logger.info(f"Webcam recording stopped: {filepath} (duration: {duration}s)")
    
    def _on_webcam_error(self, error_message: str):
        """Handle webcam errors."""
        self.error_occurred.emit("webcam", error_message)
    
    def _on_webcam_status_changed(self, status_message: str):
        """Handle webcam status changes."""
        self.webcam_status_changed.emit(status_message)
    
    def _on_stimulus_seek_requested(self, position: float):
        """Handle stimulus seek requests."""
        # Implement stimulus seek handling
        try:
            if hasattr(self, 'stimulus_controller') and self.stimulus_controller:
                # Convert position percentage to actual seek position
                duration = self.stimulus_controller.get_duration()
                if duration > 0:
                    seek_time = int((position / 100.0) * duration)
                    self.stimulus_controller.seek_to_position(seek_time)
                    
                    # Emit signal for UI updates
                    self.stimulus_status_changed.emit(f"Stimulus seek to {position:.1f}% ({seek_time}ms)")
                else:
                    self.stimulus_status_changed.emit("Cannot seek: no media loaded")
            else:
                self.stimulus_status_changed.emit("Stimulus controller not available")
                
        except Exception as e:
            error_msg = f"Error seeking stimulus: {str(e)}"
            self.stimulus_status_changed.emit(error_msg)
            self.error_occurred.emit(error_msg)
    
    def _on_stimulus_screen_changed(self, screen_index: int):
        """Handle stimulus screen changes."""
        # Implement stimulus screen change handling
        try:
            if hasattr(self, 'stimulus_controller') and self.stimulus_controller:
                # Set the target screen for stimulus display
                if hasattr(self.stimulus_controller, 'set_display_screen'):
                    self.stimulus_controller.set_display_screen(screen_index)
                    self.stimulus_status_changed.emit(f"Stimulus display screen set to {screen_index}")
                else:
                    # Store screen index for future use
                    self.stimulus_controller.target_screen = screen_index
                    self.stimulus_status_changed.emit(f"Stimulus target screen set to {screen_index}")
                
                # Update any UI components that need to know about screen change
                self.stimulus_screen_changed.emit(screen_index)
                
            else:
                self.stimulus_status_changed.emit("Stimulus controller not available")
                
        except Exception as e:
            error_msg = f"Error changing stimulus screen: {str(e)}"
            self.stimulus_status_changed.emit(error_msg)
            self.error_occurred.emit(error_msg)
    
    def _on_start_recording_play_requested(self):
        """Handle start recording/play requests."""
        # This should trigger session start
        self.start_session()
    
    def _on_mark_event_requested(self):
        """Handle event marking requests."""
        if self._session_logger and self._current_session_id:
            self._session_logger.log_event(self._current_session_id, "user_marked_event", {})
    
    def _on_stimulus_status_changed(self, status_message: str):
        """Handle stimulus status changes."""
        self.logger.debug(f"Stimulus status: {status_message}")
    
    def _on_stimulus_experiment_started(self):
        """Handle stimulus experiment start."""
        self.logger.info("Stimulus experiment started")
    
    def _on_stimulus_experiment_ended(self):
        """Handle stimulus experiment end."""
        self.logger.info("Stimulus experiment ended")
    
    def _on_stimulus_error(self, error_message: str):
        """Handle stimulus errors."""
        self.error_occurred.emit("stimulus", error_message)
    
    def _on_session_logger_session_started(self, session_id: str):
        """Handle session logger session start."""
        self.logger.info(f"Session logger started for: {session_id}")
    
    def _on_session_logger_session_ended(self, session_id: str, duration: float):
        """Handle session logger session end."""
        self.logger.info(f"Session logger ended for: {session_id} (duration: {duration}s)")
    
    def _on_session_logger_error(self, error_type: str, error_message: str):
        """Handle session logger errors."""
        self.error_occurred.emit("session_logger", f"{error_type}: {error_message}")
    
    def cleanup(self):
        """Clean up resources when shutting down."""
        try:
            self.stop_server()
            self.stop_webcam_preview()
            self.stop_webcam_recording()
            if self._current_session_id:
                self.stop_session()
            self.logger.info("MainController cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")