"""
Virtual Device Client Implementation

This module provides a VirtualDeviceClient that simulates an Android device
connecting to the PC server. It implements the same socket protocol and message
types as the real Android app, allowing for comprehensive testing without
physical devices.

The client can simulate:
- Device connection handshake (Hello message with capabilities)  
- Status updates (battery, storage, temperature, recording state)
- Sensor data streaming (GSR readings at 128Hz)
- File transfers (video and thermal image data)
- Response to commands (start/stop recording, sync signals)
"""

import asyncio
import base64
import json
import logging
import socket
import struct
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Union
import uuid

# Import the message types from the main application
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from PythonApp.network.pc_server import (
    HelloMessage,
    StatusMessage, 
    SensorDataMessage,
    AckMessage,
    FileInfoMessage,
    FileChunkMessage,
    FileEndMessage,
    JsonMessage,
)

@dataclass
class VirtualDeviceConfig:
    """Configuration for a virtual device instance"""
    device_id: str = ""
    capabilities: List[str] = field(default_factory=lambda: ["rgb_video", "thermal", "shimmer"])
    server_host: str = "127.0.0.1"
    server_port: int = 9000
    
    # Device characteristics
    battery_level: int = 85
    storage_free_gb: float = 32.5
    temperature_celsius: float = 35.2
    
    # Data generation settings
    gsr_sampling_rate_hz: int = 128
    rgb_fps: int = 30
    thermal_fps: int = 9
    
    # Behavioral settings
    heartbeat_interval_seconds: float = 10.0
    status_update_interval_seconds: float = 30.0
    response_delay_ms: int = 50  # Simulated network/processing delay
    
    def __post_init__(self):
        if not self.device_id:
            self.device_id = f"virtual_device_{uuid.uuid4().hex[:8]}"

class VirtualDeviceClient:
    """
    Virtual Android device that connects to PC server and simulates device behavior.
    
    This class implements the complete device protocol, including:
    - Socket connection with length-prefixed JSON messages
    - Hello handshake with capability advertisement
    - Status message heartbeats
    - Response to recording commands
    - Sensor data streaming
    - File transfer simulation
    """
    
    def __init__(self, config: VirtualDeviceConfig, logger: Optional[logging.Logger] = None):
        self.config = config
        self.logger = logger or logging.getLogger(f"VirtualDevice-{config.device_id}")
        
        # Connection state
        self.socket: Optional[socket.socket] = None
        self.is_connected = False
        self.is_running = False
        
        # Device state
        self.is_recording = False
        self.current_session_id: Optional[str] = None
        self.connection_time = 0.0
        
        # Threading
        self.background_threads: List[threading.Thread] = []
        self.message_queue = asyncio.Queue()
        self.stop_event = threading.Event()
        
        # Callbacks for external monitoring
        self.data_callbacks: List[Callable] = []
        self.status_callbacks: List[Callable] = []
        
        # Statistics
        self.messages_sent = 0
        self.messages_received = 0
        self.data_samples_sent = 0
        self.files_transferred = 0
        
        self.logger.info(f"Virtual device initialized: {self.config.device_id}")
        
    async def connect(self) -> bool:
        """
        Connect to the PC server and perform handshake.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.logger.info(f"Connecting to {self.config.server_host}:{self.config.server_port}")
            
            # Create socket connection
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10.0)  # Connection timeout
            await asyncio.to_thread(
                self.socket.connect,
                (self.config.server_host, self.config.server_port)
            )
            
            self.is_connected = True
            self.connection_time = time.time()
            self.socket.settimeout(None)  # Remove timeout for normal operation
            
            # Send hello message
            hello_msg = HelloMessage(
                device_id=self.config.device_id,
                capabilities=self.config.capabilities.copy(),
                timestamp=time.time()
            )
            
            await self._send_message(hello_msg)
            self.logger.info(f"Hello message sent with capabilities: {self.config.capabilities}")
            
            # Start background tasks
            self.is_running = True
            self._start_background_tasks()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect: {e}")
            if self.socket:
                self.socket.close()
                self.socket = None
            self.is_connected = False
            return False
    
    async def disconnect(self) -> None:
        """Gracefully disconnect from the server"""
        try:
            self.logger.info("Disconnecting from server")
            self.is_running = False
            self.stop_event.set()
            
            # Wait for background threads
            for thread in self.background_threads:
                thread.join(timeout=5.0)
                
            if self.socket:
                self.socket.close()
                self.socket = None
                
            self.is_connected = False
            self.logger.info("Disconnected successfully")
            
        except Exception as e:
            self.logger.error(f"Error during disconnect: {e}")
    
    async def _send_message(self, message: JsonMessage) -> bool:
        """
        Send a JSON message to the server using length-prefixed protocol.
        
        Args:
            message: The message to send
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.socket or not self.is_connected:
            self.logger.warning("Cannot send message: not connected")
            return False
            
        try:
            # Simulate response delay
            if self.config.response_delay_ms > 0:
                await asyncio.sleep(self.config.response_delay_ms / 1000.0)
            
            json_data = message.to_json()
            json_bytes = json_data.encode("utf-8")
            length_header = struct.pack(">I", len(json_bytes))
            
            await asyncio.to_thread(self.socket.sendall, length_header + json_bytes)
            
            self.messages_sent += 1
            self.logger.debug(f"Sent {message.type} message")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            return False
    
    async def _receive_message(self) -> Optional[JsonMessage]:
        """
        Receive a JSON message from the server.
        
        Returns:
            JsonMessage or None if error/timeout
        """
        if not self.socket or not self.is_connected:
            return None
            
        try:
            # Read length header
            length_data = await asyncio.to_thread(self._recv_exact, 4)
            if not length_data:
                return None
                
            message_length = struct.unpack(">I", length_data)[0]
            if message_length <= 0 or message_length > 1024 * 1024:  # 1MB limit
                self.logger.error(f"Invalid message length: {message_length}")
                return None
            
            # Read message data
            message_data = await asyncio.to_thread(self._recv_exact, message_length)
            if not message_data:
                return None
                
            json_string = message_data.decode("utf-8")
            message = JsonMessage.from_json(json_string)
            
            if message:
                self.messages_received += 1
                self.logger.debug(f"Received {message.type} message")
                
            return message
            
        except Exception as e:
            self.logger.error(f"Error receiving message: {e}")
            return None
    
    def _recv_exact(self, length: int) -> Optional[bytes]:
        """Receive exactly the specified number of bytes"""
        data = b""
        while len(data) < length:
            chunk = self.socket.recv(length - len(data))
            if not chunk:
                return None
            data += chunk
        return data
    
    def _start_background_tasks(self) -> None:
        """Start background threads for device simulation"""
        
        # Message receiver thread
        receiver_thread = threading.Thread(
            target=self._message_receiver_loop,
            name=f"MessageReceiver-{self.config.device_id}",
            daemon=True
        )
        receiver_thread.start()
        self.background_threads.append(receiver_thread)
        
        # Status update thread  
        status_thread = threading.Thread(
            target=self._status_update_loop,
            name=f"StatusUpdater-{self.config.device_id}",
            daemon=True
        )
        status_thread.start()
        self.background_threads.append(status_thread)
        
        # Heartbeat thread
        heartbeat_thread = threading.Thread(
            target=self._heartbeat_loop,
            name=f"Heartbeat-{self.config.device_id}",
            daemon=True
        )
        heartbeat_thread.start()
        self.background_threads.append(heartbeat_thread)
    
    def _message_receiver_loop(self) -> None:
        """Background loop to receive and process messages from server"""
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        
        try:
            while self.is_running and not self.stop_event.is_set():
                message = loop.run_until_complete(self._receive_message())
                if message:
                    loop.run_until_complete(self._handle_received_message(message))
                elif not self.is_connected:
                    break
        except Exception as e:
            self.logger.error(f"Error in message receiver loop: {e}")
        finally:
            loop.close()
    
    async def _handle_received_message(self, message: JsonMessage) -> None:
        """Process a received message and respond appropriately"""
        try:
            if message.type == "start_record":
                await self._handle_start_record(message)
            elif message.type == "stop_record":
                await self._handle_stop_record(message)
            elif message.type == "flash_sync":
                await self._handle_flash_sync(message)
            elif message.type == "beep_sync":
                await self._handle_beep_sync(message)
            else:
                self.logger.debug(f"Received unhandled message type: {message.type}")
                
        except Exception as e:
            self.logger.error(f"Error handling message {message.type}: {e}")
    
    async def _handle_start_record(self, message: JsonMessage) -> None:
        """Handle start recording command"""
        session_id = getattr(message, 'session_id', f"session_{int(time.time())}")
        record_shimmer = getattr(message, 'record_shimmer', True)
        record_video = getattr(message, 'record_video', True)  
        record_thermal = getattr(message, 'record_thermal', True)
        
        self.logger.info(f"Starting recording for session: {session_id}")
        self.is_recording = True
        self.current_session_id = session_id
        
        # Send acknowledgment
        ack = AckMessage(cmd="start_record", status="ok", timestamp=time.time())
        await self._send_message(ack)
        
        # Start data streaming if applicable
        if record_shimmer and "shimmer" in self.config.capabilities:
            self._start_sensor_data_streaming()
            
        if record_video and "rgb_video" in self.config.capabilities:
            self._start_video_recording_simulation()
            
        if record_thermal and "thermal" in self.config.capabilities:
            self._start_thermal_recording_simulation()
    
    async def _handle_stop_record(self, message: JsonMessage) -> None:
        """Handle stop recording command"""
        self.logger.info(f"Stopping recording for session: {self.current_session_id}")
        self.is_recording = False
        
        # Send acknowledgment
        ack = AckMessage(cmd="stop_record", status="ok", timestamp=time.time())
        await self._send_message(ack)
        
        # Finalize any file transfers
        await self._finalize_file_transfers()
        
        self.current_session_id = None
    
    async def _handle_flash_sync(self, message: JsonMessage) -> None:
        """Handle flash sync command"""
        sync_id = getattr(message, 'sync_id', None)
        duration_ms = getattr(message, 'duration_ms', 200)
        
        self.logger.info(f"Flash sync received (duration: {duration_ms}ms, id: {sync_id})")
        
        # Simulate flash execution and send acknowledgment
        ack = AckMessage(
            cmd="flash_sync", 
            status="ok", 
            message=f"Flash executed: {duration_ms}ms",
            timestamp=time.time()
        )
        await self._send_message(ack)
    
    async def _handle_beep_sync(self, message: JsonMessage) -> None:
        """Handle beep sync command"""
        sync_id = getattr(message, 'sync_id', None)
        frequency_hz = getattr(message, 'frequency_hz', 1000)
        duration_ms = getattr(message, 'duration_ms', 200)
        volume = getattr(message, 'volume', 0.8)
        
        self.logger.info(f"Beep sync received ({frequency_hz}Hz, {duration_ms}ms, vol: {volume})")
        
        # Send acknowledgment
        ack = AckMessage(
            cmd="beep_sync",
            status="ok", 
            message=f"Beep executed: {frequency_hz}Hz/{duration_ms}ms",
            timestamp=time.time()
        )
        await self._send_message(ack)
    
    def _status_update_loop(self) -> None:
        """Background loop to send periodic status updates"""
        while self.is_running and not self.stop_event.is_set():
            try:
                # Create and send status message
                status = StatusMessage(
                    battery=self.config.battery_level,
                    storage=f"{self.config.storage_free_gb:.1f}GB",
                    temperature=self.config.temperature_celsius,
                    recording=self.is_recording,
                    connected=True,
                    timestamp=time.time()
                )
                
                # Send in async context
                asyncio.set_event_loop(asyncio.new_event_loop())
                loop = asyncio.get_event_loop()
                loop.run_until_complete(self._send_message(status))
                loop.close()
                
                # Wait for next update
                self.stop_event.wait(self.config.status_update_interval_seconds)
                
            except Exception as e:
                self.logger.error(f"Error in status update loop: {e}")
                time.sleep(5.0)
    
    def _heartbeat_loop(self) -> None:
        """Background loop to send periodic heartbeat messages"""
        while self.is_running and not self.stop_event.is_set():
            try:
                # Simple heartbeat via status message
                if time.time() - getattr(self, '_last_status_time', 0) > self.config.heartbeat_interval_seconds:
                    status = StatusMessage(
                        recording=self.is_recording,
                        connected=True,
                        timestamp=time.time()
                    )
                    
                    asyncio.set_event_loop(asyncio.new_event_loop())
                    loop = asyncio.get_event_loop()
                    loop.run_until_complete(self._send_message(status))
                    loop.close()
                    
                    self._last_status_time = time.time()
                
                self.stop_event.wait(self.config.heartbeat_interval_seconds / 2)
                
            except Exception as e:
                self.logger.error(f"Error in heartbeat loop: {e}")
                time.sleep(5.0)
    
    def _start_sensor_data_streaming(self) -> None:
        """Start streaming GSR sensor data"""
        if hasattr(self, '_sensor_thread') and self._sensor_thread.is_alive():
            return
            
        self._sensor_thread = threading.Thread(
            target=self._sensor_data_loop,
            name=f"SensorData-{self.config.device_id}",
            daemon=True
        )
        self._sensor_thread.start()
        self.background_threads.append(self._sensor_thread)
        self.logger.info("Started GSR sensor data streaming")
    
    def _sensor_data_loop(self) -> None:
        """Background loop to generate and send GSR sensor data"""
        from .synthetic_data_generator import SyntheticDataGenerator
        
        data_generator = SyntheticDataGenerator()
        sample_interval = 1.0 / self.config.gsr_sampling_rate_hz
        
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        
        try:
            while self.is_running and self.is_recording and not self.stop_event.is_set():
                # Generate GSR sample
                gsr_value = data_generator.generate_gsr_sample()
                
                # Create sensor data message
                sensor_msg = SensorDataMessage(
                    values={"GSR": gsr_value},
                    timestamp=time.time()
                )
                
                # Send message
                loop.run_until_complete(self._send_message(sensor_msg))
                self.data_samples_sent += 1
                
                # Wait for next sample
                self.stop_event.wait(sample_interval)
                
        except Exception as e:
            self.logger.error(f"Error in sensor data loop: {e}")
        finally:
            loop.close()
    
    def _start_video_recording_simulation(self) -> None:
        """Start simulating video recording and file transfer"""
        video_thread = threading.Thread(
            target=self._video_simulation_loop,
            name=f"VideoSim-{self.config.device_id}",
            daemon=True
        )
        video_thread.start()
        self.background_threads.append(video_thread)
        self.logger.info("Started video recording simulation")
    
    def _start_thermal_recording_simulation(self) -> None:
        """Start simulating thermal recording and file transfer"""
        thermal_thread = threading.Thread(
            target=self._thermal_simulation_loop,
            name=f"ThermalSim-{self.config.device_id}",
            daemon=True
        )
        thermal_thread.start()
        self.background_threads.append(thermal_thread)
        self.logger.info("Started thermal recording simulation")
    
    def _video_simulation_loop(self) -> None:
        """Simulate video recording by generating frame data"""
        from .synthetic_data_generator import SyntheticDataGenerator
        
        data_generator = SyntheticDataGenerator()
        frame_interval = 1.0 / self.config.rgb_fps
        frame_count = 0
        
        while self.is_running and self.is_recording and not self.stop_event.is_set():
            try:
                # Generate frame data
                frame_data = data_generator.generate_rgb_frame()
                frame_count += 1
                
                # For now, just log frames - file transfer happens at session end
                if frame_count % 100 == 0:  # Log every 100 frames
                    self.logger.debug(f"Generated RGB frame {frame_count}")
                
                self.stop_event.wait(frame_interval)
                
            except Exception as e:
                self.logger.error(f"Error in video simulation: {e}")
                break
        
        self.logger.info(f"Video simulation complete: {frame_count} frames generated")
    
    def _thermal_simulation_loop(self) -> None:
        """Simulate thermal recording by generating thermal image data"""
        from .synthetic_data_generator import SyntheticDataGenerator
        
        data_generator = SyntheticDataGenerator()
        frame_interval = 1.0 / self.config.thermal_fps
        frame_count = 0
        
        while self.is_running and self.is_recording and not self.stop_event.is_set():
            try:
                # Generate thermal frame data
                thermal_data = data_generator.generate_thermal_frame()
                frame_count += 1
                
                # Log progress periodically
                if frame_count % 50 == 0:  # Log every 50 frames
                    self.logger.debug(f"Generated thermal frame {frame_count}")
                
                self.stop_event.wait(frame_interval)
                
            except Exception as e:
                self.logger.error(f"Error in thermal simulation: {e}")
                break
        
        self.logger.info(f"Thermal simulation complete: {frame_count} frames generated")
    
    async def _finalize_file_transfers(self) -> None:
        """Simulate file transfer after recording stops"""
        if not self.is_connected:
            return
            
        try:
            # Simulate video file transfer
            if "rgb_video" in self.config.capabilities:
                await self._simulate_file_transfer(
                    filename=f"video_{self.current_session_id}_{self.config.device_id}.mp4",
                    file_size_mb=100  # Simulated 100MB video file
                )
            
            # Simulate thermal file transfer
            if "thermal" in self.config.capabilities:
                await self._simulate_file_transfer(
                    filename=f"thermal_{self.current_session_id}_{self.config.device_id}.raw",
                    file_size_mb=20  # Simulated 20MB thermal data
                )
                
        except Exception as e:
            self.logger.error(f"Error in file transfer simulation: {e}")
    
    async def _simulate_file_transfer(self, filename: str, file_size_mb: float) -> None:
        """
        Simulate transferring a file using the file transfer protocol.
        
        Args:
            filename: Name of the file being transferred
            file_size_mb: Size of the file in megabytes
        """
        try:
            file_size_bytes = int(file_size_mb * 1024 * 1024)
            chunk_size = 8192  # 8KB chunks
            total_chunks = (file_size_bytes + chunk_size - 1) // chunk_size
            
            self.logger.info(f"Starting file transfer: {filename} ({file_size_mb}MB, {total_chunks} chunks)")
            
            # Send file info
            file_info = FileInfoMessage(
                name=filename,
                size=file_size_bytes,
                timestamp=time.time()
            )
            await self._send_message(file_info)
            
            # Send chunks
            for chunk_seq in range(total_chunks):
                # Generate dummy chunk data
                actual_chunk_size = min(chunk_size, file_size_bytes - (chunk_seq * chunk_size))
                chunk_data = b"x" * actual_chunk_size  # Dummy data
                chunk_b64 = base64.b64encode(chunk_data).decode("utf-8")
                
                chunk_msg = FileChunkMessage(
                    seq=chunk_seq,
                    data=chunk_b64,
                    timestamp=time.time()
                )
                await self._send_message(chunk_msg)
                
                # Progress logging
                if chunk_seq % 100 == 0 or chunk_seq == total_chunks - 1:
                    progress = (chunk_seq + 1) / total_chunks * 100
                    self.logger.debug(f"File transfer progress: {progress:.1f}%")
                
                # Small delay to simulate realistic transfer
                await asyncio.sleep(0.001)
            
            # Send file end
            file_end = FileEndMessage(
                name=filename,
                timestamp=time.time()
            )
            await self._send_message(file_end)
            
            self.files_transferred += 1
            self.logger.info(f"File transfer completed: {filename}")
            
        except Exception as e:
            self.logger.error(f"Error in file transfer simulation for {filename}: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current device statistics"""
        current_time = time.time()
        uptime = current_time - self.connection_time if self.connection_time > 0 else 0
        
        return {
            "device_id": self.config.device_id,
            "uptime_seconds": uptime,
            "is_connected": self.is_connected,
            "is_recording": self.is_recording,
            "current_session_id": self.current_session_id,
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "data_samples_sent": self.data_samples_sent,
            "files_transferred": self.files_transferred,
            "capabilities": self.config.capabilities,
            "last_update": current_time,
        }

    def add_data_callback(self, callback: Callable) -> None:
        """Add callback for data events"""
        self.data_callbacks.append(callback)
        
    def add_status_callback(self, callback: Callable) -> None:
        """Add callback for status events"""
        self.status_callbacks.append(callback)