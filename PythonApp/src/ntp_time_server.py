"""
NTPTimeServer - Python implementation for high-precision time synchronization

This module provides NTP-style time synchronization services for the multi-sensor
recording system, enabling Android devices to synchronize their clocks with the
PC's reference time using the same protocol expected by SyncClockManager.

Implements high-precision timestamp provision, network time validation,
and integration with the existing JSON communication protocol.

Author: Multi-Sensor Recording System
Date: 2025-07-30
"""

import time
import threading
import socket
import json
import logging
import ntplib
from datetime import datetime, timezone
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import statistics


@dataclass
class TimeServerStatus:
    """Status information for the NTP time server"""
    is_running: bool = False
    is_synchronized: bool = False
    reference_source: str = "system"
    last_ntp_sync: Optional[float] = None
    time_accuracy_ms: float = 0.0
    client_count: int = 0
    requests_served: int = 0
    average_response_time_ms: float = 0.0


@dataclass
class TimeSyncRequest:
    """Time synchronization request from client"""
    client_id: str
    request_timestamp: float
    sequence_number: int = 0


@dataclass
class TimeSyncResponse:
    """Time synchronization response to client"""
    server_timestamp: float
    request_timestamp: float
    response_timestamp: float
    server_precision_ms: float
    sequence_number: int = 0


class NTPTimeServer:
    """
    High-precision NTP-style time server for device synchronization
    
    Provides accurate timestamps for Android SyncClockManager integration,
    supports multiple time sources, and maintains synchronization quality metrics.
    """
    
    def __init__(self, logger=None, port=8889):
        """Initialize NTP time server"""
        self.logger = logger or logging.getLogger(__name__)
        self.port = port
        
        # Server state
        self.is_running = False
        self.server_socket: Optional[socket.socket] = None
        self.server_thread: Optional[threading.Thread] = None
        self.thread_pool = ThreadPoolExecutor(max_workers=10)
        
        # Time synchronization
        self.ntp_client = ntplib.NTPClient()
        self.reference_time_offset = 0.0
        self.last_ntp_sync_time = 0.0
        self.time_precision_ms = 1.0  # Estimated precision in milliseconds
        
        # Statistics and monitoring
        self.status = TimeServerStatus()
        self.connected_clients: Dict[str, float] = {}
        self.response_times: List[float] = []
        self.sync_callbacks: List[Callable[[TimeSyncResponse], None]] = []
        
        # Configuration
        self.ntp_servers = [
            "pool.ntp.org",
            "time.google.com",
            "time.cloudflare.com"
        ]
        self.ntp_sync_interval = 300.0  # 5 minutes
        self.max_response_time_history = 100
        
        # Threading
        self.stop_event = threading.Event()
        self.stats_lock = threading.Lock()
        
        self.logger.info("NTPTimeServer initialized on port %d", self.port)

    def start_server(self) -> bool:
        """
        Start the NTP time server
        
        Returns:
            bool: True if server started successfully
        """
        try:
            if self.is_running:
                self.logger.warning("NTP time server already running")
                return True
            
            self.logger.info("Starting NTP time server...")
            
            # Initialize server socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', self.port))
            self.server_socket.listen(10)
            
            # Start server thread
            self.stop_event.clear()
            self.server_thread = threading.Thread(
                target=self._server_loop,
                name="NTPTimeServer"
            )
            self.server_thread.daemon = True
            self.server_thread.start()
            
            # Start NTP synchronization thread
            self._start_ntp_sync_thread()
            
            # Update status
            self.status.is_running = True
            self.is_running = True
            
            self.logger.info("NTP time server started successfully on port %d", self.port)
            return True
            
        except Exception as e:
            self.logger.error("Failed to start NTP time server: %s", e)
            return False

    def stop_server(self) -> None:
        """Stop the NTP time server"""
        try:
            if not self.is_running:
                return
            
            self.logger.info("Stopping NTP time server...")
            
            # Signal stop
            self.stop_event.set()
            self.is_running = False
            
            # Close server socket
            if self.server_socket:
                self.server_socket.close()
                self.server_socket = None
            
            # Wait for server thread
            if self.server_thread and self.server_thread.is_alive():
                self.server_thread.join(timeout=5.0)
            
            # Shutdown thread pool
            self.thread_pool.shutdown(wait=True)
            
            # Update status
            self.status.is_running = False
            self.status.client_count = 0
            self.connected_clients.clear()
            
            self.logger.info("NTP time server stopped")
            
        except Exception as e:
            self.logger.error("Error stopping NTP time server: %s", e)

    def get_precise_timestamp(self) -> float:
        """
        Get high-precision timestamp with NTP correction
        
        Returns:
            float: Precise timestamp in seconds since epoch
        """
        try:
            # Get system time with highest available precision
            current_time = time.time()
            
            # Apply NTP offset correction if available
            if self.status.is_synchronized:
                corrected_time = current_time + self.reference_time_offset
                return corrected_time
            else:
                return current_time
                
        except Exception as e:
            self.logger.error("Error getting precise timestamp: %s", e)
            return time.time()

    def get_timestamp_milliseconds(self) -> int:
        """
        Get timestamp in milliseconds (compatible with Android)
        
        Returns:
            int: Timestamp in milliseconds since epoch
        """
        return int(self.get_precise_timestamp() * 1000)

    def synchronize_with_ntp(self) -> bool:
        """
        Synchronize server time with NTP servers
        
        Returns:
            bool: True if synchronization successful
        """
        try:
            self.logger.info("Synchronizing with NTP servers...")
            
            successful_syncs = []
            
            for ntp_server in self.ntp_servers:
                try:
                    self.logger.debug("Querying NTP server: %s", ntp_server)
                    response = self.ntp_client.request(ntp_server, version=3, timeout=5)
                    
                    # Calculate offset from NTP server
                    ntp_time = response.tx_time
                    local_time = time.time()
                    offset = ntp_time - local_time
                    
                    successful_syncs.append({
                        'server': ntp_server,
                        'offset': offset,
                        'delay': response.delay,
                        'precision': response.precision
                    })
                    
                    self.logger.debug("NTP sync with %s: offset=%.3fms, delay=%.3fms", 
                                    ntp_server, offset * 1000, response.delay * 1000)
                    
                except Exception as e:
                    self.logger.warning("Failed to sync with NTP server %s: %s", ntp_server, e)
                    continue
            
            if successful_syncs:
                # Use median offset for robustness
                offsets = [sync['offset'] for sync in successful_syncs]
                self.reference_time_offset = statistics.median(offsets)
                
                # Calculate precision estimate
                delays = [sync['delay'] for sync in successful_syncs]
                self.time_precision_ms = statistics.median(delays) * 1000 / 2
                
                # Update status
                self.status.is_synchronized = True
                self.status.reference_source = "ntp"
                self.status.last_ntp_sync = time.time()
                self.status.time_accuracy_ms = self.time_precision_ms
                self.last_ntp_sync_time = time.time()
                
                self.logger.info("NTP synchronization successful: offset=%.3fms, precision=%.3fms",
                               self.reference_time_offset * 1000, self.time_precision_ms)
                return True
            else:
                self.logger.error("All NTP synchronization attempts failed")
                # Fall back to system time
                self.status.is_synchronized = False
                self.status.reference_source = "system"
                self.time_precision_ms = 10.0  # Assume 10ms precision for system time
                return False
                
        except Exception as e:
            self.logger.error("Error during NTP synchronization: %s", e)
            return False

    def handle_sync_request(self, client_socket: socket.socket, client_addr: str) -> None:
        """Handle time synchronization request from client"""
        try:
            # Receive request
            data = client_socket.recv(4096)
            if not data:
                return
            
            request_receive_time = self.get_precise_timestamp()
            
            try:
                request_data = json.loads(data.decode('utf-8'))
            except json.JSONDecodeError:
                self.logger.error("Invalid JSON in sync request from %s", client_addr)
                return
            
            # Validate request format
            if request_data.get('type') != 'time_sync_request':
                return
            
            client_id = request_data.get('client_id', client_addr)
            request_timestamp = request_data.get('timestamp', 0)
            sequence_number = request_data.get('sequence', 0)
            
            # Generate response timestamp
            response_send_time = self.get_precise_timestamp()
            
            # Create response
            response = {
                'type': 'time_sync_response',
                'server_timestamp': response_send_time,
                'request_timestamp': request_timestamp,
                'receive_timestamp': request_receive_time,
                'response_timestamp': response_send_time,
                'server_precision_ms': self.time_precision_ms,
                'sequence': sequence_number,
                'server_time_ms': self.get_timestamp_milliseconds()
            }
            
            # Send response
            response_json = json.dumps(response)
            client_socket.send(response_json.encode('utf-8'))
            
            # Update statistics
            with self.stats_lock:
                self.status.requests_served += 1
                self.connected_clients[client_id] = time.time()
                self.status.client_count = len(self.connected_clients)
                
                # Track response time
                response_time = (response_send_time - request_receive_time) * 1000
                self.response_times.append(response_time)
                if len(self.response_times) > self.max_response_time_history:
                    self.response_times.pop(0)
                
                if self.response_times:
                    self.status.average_response_time_ms = statistics.mean(self.response_times)
            
            # Call sync callbacks
            sync_response = TimeSyncResponse(
                server_timestamp=response_send_time,
                request_timestamp=request_timestamp,
                response_timestamp=response_send_time,
                server_precision_ms=self.time_precision_ms,
                sequence_number=sequence_number
            )
            
            for callback in self.sync_callbacks:
                try:
                    callback(sync_response)
                except Exception as e:
                    self.logger.error("Error in sync callback: %s", e)
            
            self.logger.debug("Served time sync request from %s (seq=%d)", client_id, sequence_number)
            
        except Exception as e:
            self.logger.error("Error handling sync request from %s: %s", client_addr, e)
        finally:
            try:
                client_socket.close()
            except:
                pass

    def get_server_status(self) -> TimeServerStatus:
        """Get current server status"""
        with self.stats_lock:
            # Clean up old clients
            current_time = time.time()
            active_clients = {
                client_id: last_seen 
                for client_id, last_seen in self.connected_clients.items()
                if current_time - last_seen < 60.0  # 1 minute timeout
            }
            self.connected_clients = active_clients
            self.status.client_count = len(active_clients)
            
            return TimeServerStatus(
                is_running=self.status.is_running,
                is_synchronized=self.status.is_synchronized,
                reference_source=self.status.reference_source,
                last_ntp_sync=self.status.last_ntp_sync,
                time_accuracy_ms=self.status.time_accuracy_ms,
                client_count=self.status.client_count,
                requests_served=self.status.requests_served,
                average_response_time_ms=self.status.average_response_time_ms
            )

    def add_sync_callback(self, callback: Callable[[TimeSyncResponse], None]) -> None:
        """Add callback for sync events"""
        self.sync_callbacks.append(callback)

    def _server_loop(self) -> None:
        """Main server loop"""
        self.logger.info("NTP time server loop started")
        
        try:
            while not self.stop_event.is_set():
                try:
                    # Set socket timeout for periodic checks
                    self.server_socket.settimeout(1.0)
                    client_socket, client_addr = self.server_socket.accept()
                    
                    # Handle request in thread pool
                    self.thread_pool.submit(
                        self.handle_sync_request,
                        client_socket,
                        f"{client_addr[0]}:{client_addr[1]}"
                    )
                    
                except socket.timeout:
                    continue
                except socket.error as e:
                    if not self.stop_event.is_set():
                        self.logger.error("Socket error in server loop: %s", e)
                    break
                except Exception as e:
                    self.logger.error("Error in server loop: %s", e)
                    break
                    
        except Exception as e:
            self.logger.error("Fatal error in server loop: %s", e)
        finally:
            self.logger.info("NTP time server loop ended")

    def _start_ntp_sync_thread(self) -> None:
        """Start background NTP synchronization thread"""
        def ntp_sync_loop():
            # Initial synchronization
            self.synchronize_with_ntp()
            
            while not self.stop_event.is_set():
                try:
                    # Wait for sync interval or stop event
                    if self.stop_event.wait(self.ntp_sync_interval):
                        break
                    
                    # Perform periodic NTP synchronization
                    self.synchronize_with_ntp()
                    
                except Exception as e:
                    self.logger.error("Error in NTP sync loop: %s", e)
                    # Wait before retrying
                    if self.stop_event.wait(60.0):
                        break
        
        sync_thread = threading.Thread(target=ntp_sync_loop, name="NTPSync")
        sync_thread.daemon = True
        sync_thread.start()


# Integration helper for main application
class TimeServerManager:
    """Manager class for integrating NTP time server with main application"""
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.time_server: Optional[NTPTimeServer] = None
        
    def initialize(self, port=8889) -> bool:
        """Initialize time server"""
        try:
            self.time_server = NTPTimeServer(logger=self.logger, port=port)
            return True
        except Exception as e:
            self.logger.error("Failed to initialize time server: %s", e)
            return False
    
    def start(self) -> bool:
        """Start time server"""
        if self.time_server:
            return self.time_server.start_server()
        return False
    
    def stop(self) -> None:
        """Stop time server"""
        if self.time_server:
            self.time_server.stop_server()
    
    def get_status(self) -> Optional[TimeServerStatus]:
        """Get server status"""
        if self.time_server:
            return self.time_server.get_server_status()
        return None
    
    def get_timestamp_ms(self) -> int:
        """Get current timestamp in milliseconds"""
        if self.time_server:
            return self.time_server.get_timestamp_milliseconds()
        return int(time.time() * 1000)


# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and test NTP time server
    server = NTPTimeServer()
    
    try:
        # Start server
        if server.start_server():
            print("NTP time server started successfully")
            
            # Add callback for monitoring
            def sync_callback(response):
                print(f"Sync request served: precision={response.server_precision_ms:.2f}ms")
            
            server.add_sync_callback(sync_callback)
            
            # Run for test period
            print("Server running... Press Ctrl+C to stop")
            while True:
                time.sleep(5)
                status = server.get_server_status()
                print(f"Status: clients={status.client_count}, requests={status.requests_served}, "
                      f"sync={status.is_synchronized}, accuracy={status.time_accuracy_ms:.2f}ms")
        
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        server.stop_server()
        print("Server stopped")
