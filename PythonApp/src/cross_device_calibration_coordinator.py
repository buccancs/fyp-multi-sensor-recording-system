"""
Cross-Device Calibration Coordinator

Coordinates calibration processes across multiple devices and cameras,
ensuring synchronized calibration data collection and validation.

Features:
- Multi-device calibration synchronization
- Stereo calibration coordination
- Cross-platform calibration data sharing
- Calibration result aggregation and validation
- Network-based calibration coordination

Author: Multi-Sensor Recording System
Date: 2025-07-30
"""

import cv2
import numpy as np
import logging
import time
import threading
import json
import socket
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import queue
from pathlib import Path

# Import calibration components
from calibration_quality_assessment import (
    CalibrationQualityAssessment, CalibrationQualityResult,
    PatternType, PatternDetectionResult
)
from real_time_calibration_feedback import (
    CalibrationFeedback, CameraFeedConfig, MultiCameraCalibrationManager
)


class CalibrationPhase(Enum):
    """Calibration process phases"""
    INITIALIZATION = "initialization"
    PATTERN_DETECTION = "pattern_detection"
    DATA_COLLECTION = "data_collection"
    QUALITY_VALIDATION = "quality_validation"
    STEREO_CALIBRATION = "stereo_calibration"
    RESULT_AGGREGATION = "result_aggregation"
    COMPLETION = "completion"


@dataclass
class DeviceCalibrationInfo:
    """Information about a device participating in calibration"""
    device_id: str
    device_name: str
    device_type: str  # "android", "python", "webcam"
    ip_address: str
    port: int
    cameras: List[str]
    capabilities: List[str]
    status: str = "disconnected"
    last_seen: float = 0.0


@dataclass
class CalibrationSession:
    """Calibration session configuration and state"""
    session_id: str
    pattern_type: PatternType
    target_images_per_camera: int
    quality_threshold: float
    devices: List[DeviceCalibrationInfo]
    current_phase: CalibrationPhase = CalibrationPhase.INITIALIZATION
    start_time: float = 0.0
    collected_images: Dict[str, List[np.ndarray]] = field(default_factory=dict)
    calibration_results: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CalibrationCommand:
    """Command for coordinating calibration across devices"""
    command_type: str
    session_id: str
    target_device: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0


@dataclass
class CalibrationResponse:
    """Response from device during calibration"""
    response_type: str
    session_id: str
    device_id: str
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    timestamp: float = 0.0


class CrossDeviceCalibrationCoordinator:
    """
    Coordinates calibration processes across multiple devices
    
    Manages synchronized calibration data collection, quality validation,
    and result aggregation across Android devices, Python cameras, and webcams.
    """
    
    def __init__(self, logger=None, coordination_port=8910):
        """Initialize calibration coordinator"""
        self.logger = logger or logging.getLogger(__name__)
        self.coordination_port = coordination_port
        
        # Session management
        self.active_sessions: Dict[str, CalibrationSession] = {}
        self.connected_devices: Dict[str, DeviceCalibrationInfo] = {}
        
        # Network coordination
        self.server_socket: Optional[socket.socket] = None
        self.server_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.client_connections: Dict[str, socket.socket] = {}
        
        # Calibration components
        self.quality_assessment = CalibrationQualityAssessment(logger=self.logger)
        self.local_camera_manager = MultiCameraCalibrationManager(logger=self.logger)
        
        # Callbacks
        self.session_callbacks: List[Callable[[str, CalibrationPhase], None]] = []
        self.device_callbacks: List[Callable[[DeviceCalibrationInfo], None]] = []
        
        # Threading
        self.command_queue = queue.Queue()
        self.response_queue = queue.Queue()
        self.processing_thread: Optional[threading.Thread] = None
        
        self.logger.info("CrossDeviceCalibrationCoordinator initialized")

    def start_coordination_server(self) -> bool:
        """Start network coordination server"""
        try:
            self.logger.info(f"Starting calibration coordination server on port {self.coordination_port}")
            
            # Initialize server socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', self.coordination_port))
            self.server_socket.listen(10)
            
            # Start server thread
            self.is_running = True
            self.server_thread = threading.Thread(target=self._server_loop, name="CalibrationCoordinator")
            self.server_thread.daemon = True
            self.server_thread.start()
            
            # Start processing thread
            self.processing_thread = threading.Thread(target=self._processing_loop, name="CalibrationProcessor")
            self.processing_thread.daemon = True
            self.processing_thread.start()
            
            self.logger.info("Calibration coordination server started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start coordination server: {e}")
            return False

    def stop_coordination_server(self):
        """Stop network coordination server"""
        try:
            self.logger.info("Stopping calibration coordination server")
            
            self.is_running = False
            
            # Close client connections
            for device_id, client_socket in self.client_connections.items():
                try:
                    client_socket.close()
                except:
                    pass
            self.client_connections.clear()
            
            # Close server socket
            if self.server_socket:
                self.server_socket.close()
                self.server_socket = None
            
            # Wait for threads
            if self.server_thread and self.server_thread.is_alive():
                self.server_thread.join(timeout=5.0)
            if self.processing_thread and self.processing_thread.is_alive():
                self.processing_thread.join(timeout=5.0)
            
            self.logger.info("Calibration coordination server stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping coordination server: {e}")

    def create_calibration_session(
        self,
        session_id: str,
        pattern_type: PatternType,
        target_images_per_camera: int = 20,
        quality_threshold: float = 0.7
    ) -> bool:
        """Create new calibration session"""
        try:
            if session_id in self.active_sessions:
                self.logger.error(f"Session {session_id} already exists")
                return False
            
            session = CalibrationSession(
                session_id=session_id,
                pattern_type=pattern_type,
                target_images_per_camera=target_images_per_camera,
                quality_threshold=quality_threshold,
                devices=list(self.connected_devices.values()),
                start_time=time.time()
            )
            
            self.active_sessions[session_id] = session
            self.logger.info(f"Created calibration session: {session_id}")
            
            # Notify callbacks
            for callback in self.session_callbacks:
                try:
                    callback(session_id, CalibrationPhase.INITIALIZATION)
                except Exception as e:
                    self.logger.error(f"Error in session callback: {e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating calibration session: {e}")
            return False

    def start_calibration_session(self, session_id: str) -> bool:
        """Start calibration data collection"""
        try:
            if session_id not in self.active_sessions:
                self.logger.error(f"Session {session_id} not found")
                return False
            
            session = self.active_sessions[session_id]
            session.current_phase = CalibrationPhase.PATTERN_DETECTION
            
            # Send start command to all devices
            command = CalibrationCommand(
                command_type="start_calibration",
                session_id=session_id,
                parameters={
                    "pattern_type": session.pattern_type.value,
                    "target_images": session.target_images_per_camera,
                    "quality_threshold": session.quality_threshold
                },
                timestamp=time.time()
            )
            
            self._broadcast_command(command)
            
            self.logger.info(f"Started calibration session: {session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting calibration session: {e}")
            return False

    def add_calibration_image(
        self,
        session_id: str,
        device_id: str,
        camera_id: str,
        image: np.ndarray,
        quality_result: CalibrationQualityResult
    ) -> bool:
        """Add calibration image from device"""
        try:
            if session_id not in self.active_sessions:
                self.logger.error(f"Session {session_id} not found")
                return False
            
            session = self.active_sessions[session_id]
            camera_key = f"{device_id}_{camera_id}"
            
            # Initialize camera image list if needed
            if camera_key not in session.collected_images:
                session.collected_images[camera_key] = []
            
            # Check quality threshold
            if quality_result.overall_quality_score < session.quality_threshold:
                self.logger.warning(f"Image quality too low: {quality_result.overall_quality_score:.3f}")
                return False
            
            # Add image
            session.collected_images[camera_key].append(image.copy())
            
            self.logger.info(f"Added calibration image for {camera_key}: "
                           f"{len(session.collected_images[camera_key])}/{session.target_images_per_camera}")
            
            # Check if collection is complete
            self._check_collection_progress(session_id)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding calibration image: {e}")
            return False

    def perform_stereo_calibration(self, session_id: str, camera_pair: Tuple[str, str]) -> Optional[Dict[str, Any]]:
        """Perform stereo calibration between two cameras"""
        try:
            if session_id not in self.active_sessions:
                self.logger.error(f"Session {session_id} not found")
                return None
            
            session = self.active_sessions[session_id]
            camera1_key, camera2_key = camera_pair
            
            if camera1_key not in session.collected_images or camera2_key not in session.collected_images:
                self.logger.error(f"Missing images for stereo calibration: {camera_pair}")
                return None
            
            images1 = session.collected_images[camera1_key]
            images2 = session.collected_images[camera2_key]
            
            if len(images1) != len(images2):
                self.logger.error(f"Mismatched image counts for stereo calibration: {len(images1)} vs {len(images2)}")
                return None
            
            self.logger.info(f"Performing stereo calibration for {camera_pair}")
            
            # Detect calibration patterns in all image pairs
            object_points = []
            image_points1 = []
            image_points2 = []
            
            # Generate object points for the calibration pattern
            if session.pattern_type == PatternType.CHESSBOARD:
                pattern_size = (6, 9)  # cols, rows
                objp = np.zeros((pattern_size[0] * pattern_size[1], 3), np.float32)
                objp[:, :2] = np.mgrid[0:pattern_size[0], 0:pattern_size[1]].T.reshape(-1, 2)
            else:
                self.logger.error(f"Stereo calibration not implemented for pattern type: {session.pattern_type}")
                return None
            
            # Process image pairs
            for img1, img2 in zip(images1, images2):
                gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY) if len(img1.shape) == 3 else img1
                gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY) if len(img2.shape) == 3 else img2
                
                # Find corners in both images
                found1, corners1 = cv2.findChessboardCorners(gray1, pattern_size)
                found2, corners2 = cv2.findChessboardCorners(gray2, pattern_size)
                
                if found1 and found2:
                    # Refine corners
                    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
                    corners1 = cv2.cornerSubPix(gray1, corners1, (11, 11), (-1, -1), criteria)
                    corners2 = cv2.cornerSubPix(gray2, corners2, (11, 11), (-1, -1), criteria)
                    
                    object_points.append(objp)
                    image_points1.append(corners1)
                    image_points2.append(corners2)
            
            if len(object_points) < 10:
                self.logger.error(f"Insufficient valid image pairs for stereo calibration: {len(object_points)}")
                return None
            
            # Perform individual camera calibrations
            img_shape = images1[0].shape[:2][::-1]  # (width, height)
            
            ret1, mtx1, dist1, rvecs1, tvecs1 = cv2.calibrateCamera(
                object_points, image_points1, img_shape, None, None
            )
            ret2, mtx2, dist2, rvecs2, tvecs2 = cv2.calibrateCamera(
                object_points, image_points2, img_shape, None, None
            )
            
            # Perform stereo calibration
            flags = cv2.CALIB_FIX_INTRINSIC
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 1e-5)
            
            ret, mtx1, dist1, mtx2, dist2, R, T, E, F = cv2.stereoCalibrate(
                object_points, image_points1, image_points2,
                mtx1, dist1, mtx2, dist2, img_shape,
                criteria=criteria, flags=flags
            )
            
            # Compute rectification
            R1, R2, P1, P2, Q, validPixROI1, validPixROI2 = cv2.stereoRectify(
                mtx1, dist1, mtx2, dist2, img_shape, R, T
            )
            
            # Create result
            stereo_result = {
                'camera_pair': camera_pair,
                'reprojection_error': ret,
                'camera1_matrix': mtx1.tolist(),
                'camera1_distortion': dist1.tolist(),
                'camera2_matrix': mtx2.tolist(),
                'camera2_distortion': dist2.tolist(),
                'rotation_matrix': R.tolist(),
                'translation_vector': T.tolist(),
                'essential_matrix': E.tolist(),
                'fundamental_matrix': F.tolist(),
                'rectification_R1': R1.tolist(),
                'rectification_R2': R2.tolist(),
                'projection_P1': P1.tolist(),
                'projection_P2': P2.tolist(),
                'disparity_to_depth_Q': Q.tolist(),
                'valid_pixel_ROI1': validPixROI1,
                'valid_pixel_ROI2': validPixROI2,
                'image_pairs_used': len(object_points),
                'timestamp': time.time()
            }
            
            # Store result
            stereo_key = f"stereo_{camera1_key}_{camera2_key}"
            session.calibration_results[stereo_key] = stereo_result
            
            self.logger.info(f"Stereo calibration completed for {camera_pair}: "
                           f"error={ret:.4f}, pairs={len(object_points)}")
            
            return stereo_result
            
        except Exception as e:
            self.logger.error(f"Error performing stereo calibration: {e}")
            return None

    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get calibration session status"""
        try:
            if session_id not in self.active_sessions:
                return None
            
            session = self.active_sessions[session_id]
            
            # Calculate collection progress
            total_cameras = len(session.devices) * 2  # Assume 2 cameras per device
            collected_cameras = len(session.collected_images)
            
            progress_per_camera = {}
            for camera_key, images in session.collected_images.items():
                progress_per_camera[camera_key] = {
                    'collected': len(images),
                    'target': session.target_images_per_camera,
                    'progress': len(images) / session.target_images_per_camera
                }
            
            status = {
                'session_id': session_id,
                'current_phase': session.current_phase.value,
                'start_time': session.start_time,
                'elapsed_time': time.time() - session.start_time,
                'devices': len(session.devices),
                'total_cameras': total_cameras,
                'active_cameras': collected_cameras,
                'progress_per_camera': progress_per_camera,
                'calibration_results': list(session.calibration_results.keys()),
                'overall_progress': collected_cameras / total_cameras if total_cameras > 0 else 0
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting session status: {e}")
            return None

    def add_session_callback(self, callback: Callable[[str, CalibrationPhase], None]):
        """Add callback for session phase changes"""
        self.session_callbacks.append(callback)

    def add_device_callback(self, callback: Callable[[DeviceCalibrationInfo], None]):
        """Add callback for device status changes"""
        self.device_callbacks.append(callback)

    def _server_loop(self):
        """Main server loop for handling device connections"""
        self.logger.info("Calibration coordination server loop started")
        
        try:
            while self.is_running:
                try:
                    self.server_socket.settimeout(1.0)
                    client_socket, client_addr = self.server_socket.accept()
                    
                    # Handle client in separate thread
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, client_addr),
                        name=f"CalibrationClient-{client_addr[0]}"
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.timeout:
                    continue
                except socket.error as e:
                    if self.is_running:
                        self.logger.error(f"Socket error in server loop: {e}")
                    break
                    
        except Exception as e:
            self.logger.error(f"Fatal error in server loop: {e}")
        finally:
            self.logger.info("Calibration coordination server loop ended")

    def _handle_client(self, client_socket: socket.socket, client_addr: Tuple[str, int]):
        """Handle individual client connection"""
        device_id = None
        try:
            while self.is_running:
                # Receive data
                data = client_socket.recv(4096)
                if not data:
                    break
                
                try:
                    message = json.loads(data.decode('utf-8'))
                except json.JSONDecodeError:
                    self.logger.error(f"Invalid JSON from {client_addr}")
                    continue
                
                # Handle different message types
                if message.get('type') == 'device_registration':
                    device_id = self._handle_device_registration(message, client_socket, client_addr)
                elif message.get('type') == 'calibration_response':
                    self._handle_calibration_response(message)
                elif message.get('type') == 'image_data':
                    self._handle_image_data(message)
                
        except Exception as e:
            self.logger.error(f"Error handling client {client_addr}: {e}")
        finally:
            try:
                client_socket.close()
                if device_id and device_id in self.client_connections:
                    del self.client_connections[device_id]
                    if device_id in self.connected_devices:
                        self.connected_devices[device_id].status = "disconnected"
            except:
                pass

    def _handle_device_registration(self, message: Dict[str, Any], client_socket: socket.socket, client_addr: Tuple[str, int]) -> Optional[str]:
        """Handle device registration"""
        try:
            device_info = DeviceCalibrationInfo(
                device_id=message['device_id'],
                device_name=message['device_name'],
                device_type=message['device_type'],
                ip_address=client_addr[0],
                port=client_addr[1],
                cameras=message.get('cameras', []),
                capabilities=message.get('capabilities', []),
                status="connected",
                last_seen=time.time()
            )
            
            self.connected_devices[device_info.device_id] = device_info
            self.client_connections[device_info.device_id] = client_socket
            
            self.logger.info(f"Device registered: {device_info.device_name} ({device_info.device_id})")
            
            # Notify callbacks
            for callback in self.device_callbacks:
                try:
                    callback(device_info)
                except Exception as e:
                    self.logger.error(f"Error in device callback: {e}")
            
            return device_info.device_id
            
        except Exception as e:
            self.logger.error(f"Error handling device registration: {e}")
            return None

    def _handle_calibration_response(self, message: Dict[str, Any]):
        """Handle calibration response from device"""
        try:
            response = CalibrationResponse(
                response_type=message['response_type'],
                session_id=message['session_id'],
                device_id=message['device_id'],
                success=message['success'],
                data=message.get('data', {}),
                error_message=message.get('error_message'),
                timestamp=message.get('timestamp', time.time())
            )
            
            self.response_queue.put(response)
            
        except Exception as e:
            self.logger.error(f"Error handling calibration response: {e}")

    def _handle_image_data(self, message: Dict[str, Any]):
        """Handle calibration image data from device"""
        try:
            # Decode image data (base64 encoded)
            import base64
            image_data = base64.b64decode(message['image_data'])
            image_array = np.frombuffer(image_data, dtype=np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            
            # Extract quality result
            quality_data = message.get('quality_result', {})
            
            # Add to session
            self.add_calibration_image(
                message['session_id'],
                message['device_id'],
                message['camera_id'],
                image,
                quality_data  # Simplified for now
            )
            
        except Exception as e:
            self.logger.error(f"Error handling image data: {e}")

    def _processing_loop(self):
        """Background processing loop for handling responses"""
        while self.is_running:
            try:
                # Process responses
                try:
                    response = self.response_queue.get(timeout=1.0)
                    self._process_calibration_response(response)
                except queue.Empty:
                    continue
                    
            except Exception as e:
                self.logger.error(f"Error in processing loop: {e}")
                time.sleep(1.0)

    def _process_calibration_response(self, response: CalibrationResponse):
        """Process calibration response"""
        try:
            self.logger.info(f"Processing response: {response.response_type} from {response.device_id}")
            
            # Handle different response types
            if response.response_type == "calibration_started":
                self._handle_calibration_started(response)
            elif response.response_type == "image_captured":
                self._handle_image_captured(response)
            elif response.response_type == "calibration_completed":
                self._handle_calibration_completed(response)
                
        except Exception as e:
            self.logger.error(f"Error processing calibration response: {e}")

    def _handle_calibration_started(self, response: CalibrationResponse):
        """Handle calibration started response"""
        self.logger.info(f"Calibration started on device: {response.device_id}")

    def _handle_image_captured(self, response: CalibrationResponse):
        """Handle image captured response"""
        self.logger.info(f"Image captured on device: {response.device_id}")

    def _handle_calibration_completed(self, response: CalibrationResponse):
        """Handle calibration completed response"""
        self.logger.info(f"Calibration completed on device: {response.device_id}")

    def _broadcast_command(self, command: CalibrationCommand):
        """Broadcast command to all connected devices"""
        try:
            command_json = json.dumps(asdict(command))
            
            for device_id, client_socket in self.client_connections.items():
                try:
                    client_socket.send(command_json.encode('utf-8'))
                except Exception as e:
                    self.logger.error(f"Error sending command to {device_id}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error broadcasting command: {e}")

    def _check_collection_progress(self, session_id: str):
        """Check if calibration data collection is complete"""
        try:
            session = self.active_sessions[session_id]
            
            # Check if all cameras have enough images
            all_complete = True
            for camera_key, images in session.collected_images.items():
                if len(images) < session.target_images_per_camera:
                    all_complete = False
                    break
            
            if all_complete and session.current_phase == CalibrationPhase.DATA_COLLECTION:
                session.current_phase = CalibrationPhase.STEREO_CALIBRATION
                self.logger.info(f"Data collection complete for session {session_id}")
                
                # Notify callbacks
                for callback in self.session_callbacks:
                    try:
                        callback(session_id, CalibrationPhase.STEREO_CALIBRATION)
                    except Exception as e:
                        self.logger.error(f"Error in session callback: {e}")
                        
        except Exception as e:
            self.logger.error(f"Error checking collection progress: {e}")

    def cleanup(self):
        """Clean up coordinator resources"""
        try:
            self.logger.info("Cleaning up CrossDeviceCalibrationCoordinator")
            
            # Stop server
            self.stop_coordination_server()
            
            # Clean up local camera manager
            self.local_camera_manager.cleanup()
            
            # Clear data
            self.active_sessions.clear()
            self.connected_devices.clear()
            
            self.logger.info("CrossDeviceCalibrationCoordinator cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


if __name__ == "__main__":
    # Test cross-device calibration coordinator
    import sys
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create coordinator
    coordinator = CrossDeviceCalibrationCoordinator()
    
    try:
        # Start coordination server
        if coordinator.start_coordination_server():
            print("Calibration coordination server started")
            
            # Create test session
            session_id = "test_calibration_session"
            coordinator.create_calibration_session(
                session_id,
                PatternType.CHESSBOARD,
                target_images_per_camera=10,
                quality_threshold=0.6
            )
            
            print(f"Created calibration session: {session_id}")
            
            # Keep running
            try:
                while True:
                    time.sleep(1)
                    status = coordinator.get_session_status(session_id)
                    if status:
                        print(f"Session progress: {status['overall_progress']:.1%}")
            except KeyboardInterrupt:
                print("\nShutting down...")
        
    finally:
        coordinator.cleanup()
        print("Coordinator stopped")
