# Networking and Synchronization Design

## 1. Introduction to Distributed System Networking

The contactless GSR prediction system operates as a distributed network of heterogeneous devices that must coordinate seamlessly to capture, process, and analyze physiological data with research-grade precision. The networking and synchronization architecture represents one of the most critical aspects of the system, ensuring temporal accuracy, reliable communication, and coordinated operation across multiple platforms.

This document presents a comprehensive analysis of the networking protocols, synchronization mechanisms, and distributed coordination strategies employed to achieve millisecond-precision timing across the entire system while maintaining robust communication in diverse research environments.

### 1.1 Distributed System Challenges

**Temporal Precision Requirements:**
Physiological research demands precise temporal synchronization between all data collection points, with synchronization accuracy requirements in the sub-10ms range to ensure valid correlation analysis between modalities.

**Network Heterogeneity:**
The system must operate across diverse network environments, from controlled laboratory LANs to wireless research networks, while maintaining consistent performance and reliability.

**Device Coordination:**
Multiple Android devices, desktop computers, and sensor systems must coordinate complex experimental protocols without central point-of-failure vulnerabilities.

**Real-Time Performance:**
Low-latency communication is essential for real-time feedback, immediate quality assessment, and interactive experimental control.

**Fault Tolerance:**
The distributed nature of the system requires robust fault tolerance mechanisms to ensure continued operation despite individual component failures or network disruptions.

### 1.2 Design Philosophy and Approach

**Hierarchical Architecture:**
The network design employs a hierarchical structure with the desktop application serving as the primary coordinator while maintaining peer-to-peer capabilities for direct device communication when needed.

**Protocol Layering:**
Multiple complementary protocols handle different aspects of communication, from device discovery through high-frequency data streaming, each optimized for its specific requirements.

**Temporal Priority:**
All networking decisions prioritize temporal accuracy and synchronization precision over raw throughput or traditional performance metrics.

**Graceful Degradation:**
The system maintains partial functionality even when communication channels are degraded or devices become temporarily unreachable.

**Research Flexibility:**
The architecture supports diverse experimental configurations and protocol requirements without requiring fundamental system redesign.

## 2. Network Architecture Overview

### 2.1 Overall Network Topology

The system employs a star topology with hub-and-spoke characteristics, enhanced with peer-to-peer capabilities for specific communication requirements.

```
                    ┌─────────────────────────────────────┐
                    │        DESKTOP CONTROLLER           │
                    │     (Central Coordinator)           │
                    │                                     │
                    │  ┌─────────────────────────────┐   │
                    │  │    Network Hub Services     │   │
                    │  │  - Device Discovery         │   │
                    │  │  - Time Synchronization     │   │
                    │  │  - Command Coordination     │   │
                    │  │  - Data Aggregation         │   │
                    │  └─────────────────────────────┘   │
                    └─────────────────┬───────────────────┘
                                      │
            ┌─────────────────────────┼─────────────────────────┐
            │                         │                         │
    ┌───────▼────────┐      ┌────────▼────────┐      ┌────────▼────────┐
    │   ANDROID       │      │   ANDROID       │      │   SENSOR        │
    │   DEVICE 1      │      │   DEVICE 2      │      │   SYSTEMS       │
    │                 │      │                 │      │                 │
    │  RGB Camera     │      │  RGB Camera     │      │  Shimmer GSR+   │
    │  Thermal Camera │      │  Thermal Camera │      │  Environmental  │
    │  Local Proc.    │      │  Local Proc.    │      │  Sensors        │
    └─────────────────┘      └─────────────────┘      └─────────────────┘
            │                         │                         │
            └─────────────────────────┼─────────────────────────┘
                                      │
                    ┌─────────────────▼─────────────────┐
                    │      Wi-Fi Network               │
                    │   (Research Laboratory LAN)      │
                    │                                   │
                    │  - DHCP for dynamic addressing    │
                    │  - Multicast for discovery        │
                    │  - QoS for data prioritization    │
                    └───────────────────────────────────┘
```

### 2.2 Communication Protocol Stack

The networking architecture employs a layered protocol approach, with each layer optimized for specific communication requirements:

**Application Layer Protocols:**
- Custom research protocols for experimental control
- JSON-based message exchange for structured data
- Binary protocols for high-frequency sensor data
- REST-like interfaces for configuration management

**Transport Layer Protocols:**
- WebSocket for real-time bidirectional communication
- TCP for reliable data transfer and file exchange
- UDP for time-critical discovery and synchronization
- Multicast UDP for efficient group communication

**Network Layer:**
- IPv4/IPv6 for device addressing and routing
- IGMP for multicast group management
- ICMP for network diagnostics and quality assessment

**Data Link and Physical Layers:**
- IEEE 802.11 Wi-Fi for primary wireless communication
- Bluetooth for sensor device connectivity
- USB for direct device connections when available

### 2.3 Protocol Selection Rationale

**WebSocket for Real-Time Communication:**
```python
class WebSocketProtocolHandler:
    """
    WebSocket implementation optimized for low-latency research applications
    with comprehensive error recovery and connection management.
    """
    
    def __init__(self, connection_config: dict):
        self.config = connection_config
        self.websocket = None
        self.connection_state = ConnectionState.DISCONNECTED
        self.message_queue = asyncio.Queue(maxsize=1000)
        self.heartbeat_interval = 30.0  # seconds
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        
        # Performance monitoring
        self.latency_monitor = LatencyMonitor()
        self.throughput_monitor = ThroughputMonitor()
        
        # Message handlers
        self.message_handlers = {}
        self.error_handlers = []
        
    async def establish_connection(self, uri: str) -> bool:
        """Establish WebSocket connection with research-specific optimizations."""
        
        try:
            # Configure connection parameters for minimal latency
            extra_headers = {
                'X-Research-Protocol': 'GSR-Prediction-v2.0',
                'X-Timestamp-Precision': 'microseconds',
                'X-Priority': 'real-time'
            }
            
            # Establish connection with optimized parameters
            self.websocket = await websockets.connect(
                uri,
                extra_headers=extra_headers,
                ping_interval=self.heartbeat_interval,
                ping_timeout=10,
                close_timeout=5,
                max_size=10**6,  # 1MB message size limit
                read_limit=2**16,  # 64KB read buffer
                write_limit=2**16  # 64KB write buffer
            )
            
            self.connection_state = ConnectionState.CONNECTED
            self.reconnect_attempts = 0
            
            # Start background tasks
            asyncio.create_task(self.message_processor())
            asyncio.create_task(self.heartbeat_manager())
            asyncio.create_task(self.latency_monitor.start())
            
            logging.info(f"WebSocket connection established to {uri}")
            return True
            
        except Exception as e:
            logging.error(f"WebSocket connection failed: {e}")
            self.connection_state = ConnectionState.FAILED
            return False
    
    async def send_message(self, message: dict, priority: MessagePriority = MessagePriority.NORMAL) -> bool:
        """Send message with priority queuing and delivery confirmation."""
        
        if self.connection_state != ConnectionState.CONNECTED:
            logging.warning("Attempted to send message on disconnected WebSocket")
            return False
        
        try:
            # Add message metadata
            message_envelope = {
                'timestamp': time.time_ns() // 1000,  # microsecond precision
                'message_id': str(uuid.uuid4()),
                'priority': priority.value,
                'data': message
            }
            
            # Serialize with optimized encoding
            serialized_message = self.serialize_message(message_envelope)
            
            # Send with latency tracking
            send_start = time.perf_counter()
            await self.websocket.send(serialized_message)
            send_duration = time.perf_counter() - send_start
            
            # Update performance metrics
            self.latency_monitor.record_send_latency(send_duration)
            self.throughput_monitor.record_message_sent(len(serialized_message))
            
            return True
            
        except websockets.exceptions.ConnectionClosed:
            logging.warning("WebSocket connection closed during send")
            self.connection_state = ConnectionState.DISCONNECTED
            await self.attempt_reconnection()
            return False
            
        except Exception as e:
            logging.error(f"WebSocket send error: {e}")
            return False
    
    async def message_processor(self):
        """Process incoming messages with priority handling."""
        
        try:
            async for message in self.websocket:
                receive_timestamp = time.time_ns() // 1000
                
                try:
                    # Deserialize message
                    message_envelope = self.deserialize_message(message)
                    
                    # Calculate network latency
                    send_timestamp = message_envelope.get('timestamp', receive_timestamp)
                    network_latency = receive_timestamp - send_timestamp
                    self.latency_monitor.record_network_latency(network_latency)
                    
                    # Route message to appropriate handler
                    message_type = message_envelope.get('data', {}).get('type')
                    if message_type in self.message_handlers:
                        await self.message_handlers[message_type](
                            message_envelope['data']
                        )
                    else:
                        logging.warning(f"No handler for message type: {message_type}")
                        
                except Exception as e:
                    logging.error(f"Message processing error: {e}")
                    for error_handler in self.error_handlers:
                        await error_handler(e, message)
                        
        except websockets.exceptions.ConnectionClosed:
            logging.info("WebSocket connection closed")
            self.connection_state = ConnectionState.DISCONNECTED
            await self.attempt_reconnection()
            
        except Exception as e:
            logging.error(f"WebSocket message processor error: {e}")
            self.connection_state = ConnectionState.ERROR
```

**UDP for Time-Critical Operations:**
```python
class UDPSynchronizationProtocol:
    """
    UDP-based protocol for time synchronization and critical control messages
    optimized for minimal latency and maximum temporal precision.
    """
    
    def __init__(self, local_port: int, broadcast_address: str):
        self.local_port = local_port
        self.broadcast_address = broadcast_address
        self.socket = None
        self.is_running = False
        
        # Time synchronization components
        self.time_server = NetworkTimeServer()
        self.time_client = NetworkTimeClient()
        self.sync_statistics = SynchronizationStatistics()
        
        # Message processing
        self.message_processors = {
            'time_sync_request': self.handle_time_sync_request,
            'time_sync_response': self.handle_time_sync_response,
            'emergency_stop': self.handle_emergency_stop,
            'sync_pulse': self.handle_sync_pulse
        }
    
    async def start_server(self):
        """Start UDP server for synchronization operations."""
        
        try:
            # Create UDP socket with broadcast capability
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Bind to local port
            self.socket.bind(('', self.local_port))
            self.socket.setblocking(False)
            
            self.is_running = True
            
            # Start message processing loop
            asyncio.create_task(self.message_loop())
            
            logging.info(f"UDP synchronization server started on port {self.local_port}")
            
        except Exception as e:
            logging.error(f"Failed to start UDP server: {e}")
            raise
    
    async def message_loop(self):
        """Main message processing loop for UDP communications."""
        
        while self.is_running:
            try:
                # Use asyncio for non-blocking UDP operations
                loop = asyncio.get_event_loop()
                data, addr = await loop.sock_recvfrom(self.socket, 1024)
                
                # Record receive timestamp immediately
                receive_timestamp = time.time_ns()
                
                # Parse message
                try:
                    message = json.loads(data.decode('utf-8'))
                    message['receive_timestamp'] = receive_timestamp
                    
                    # Route to appropriate handler
                    message_type = message.get('type')
                    if message_type in self.message_processors:
                        await self.message_processors[message_type](message, addr)
                    else:
                        logging.warning(f"Unknown UDP message type: {message_type}")
                        
                except json.JSONDecodeError:
                    logging.warning(f"Invalid JSON in UDP message from {addr}")
                    
            except asyncio.CancelledError:
                break
                
            except Exception as e:
                logging.error(f"UDP message loop error: {e}")
                await asyncio.sleep(0.001)  # Brief pause to prevent tight error loops
    
    async def handle_time_sync_request(self, message: dict, addr: tuple):
        """Handle time synchronization request from remote device."""
        
        client_timestamp = message.get('client_timestamp')
        receive_timestamp = message.get('receive_timestamp')
        
        # Generate server timestamps
        server_timestamp = time.time_ns()
        
        # Create response message
        response = {
            'type': 'time_sync_response',
            'client_timestamp': client_timestamp,
            'server_receive_timestamp': receive_timestamp,
            'server_send_timestamp': server_timestamp,
            'server_id': self.get_server_id()
        }
        
        # Send response immediately to minimize latency
        await self.send_message(response, addr)
        
        # Update synchronization statistics
        self.sync_statistics.record_sync_request(addr[0], server_timestamp)
    
    async def broadcast_sync_pulse(self):
        """Broadcast synchronization pulse to all devices."""
        
        pulse_message = {
            'type': 'sync_pulse',
            'timestamp': time.time_ns(),
            'sequence_number': self.get_next_sequence_number(),
            'server_id': self.get_server_id()
        }
        
        # Broadcast to all devices
        broadcast_addr = (self.broadcast_address, self.local_port)
        await self.send_message(pulse_message, broadcast_addr)
        
        logging.debug(f"Sync pulse broadcast: {pulse_message['sequence_number']}")
```

## 3. Time Synchronization Architecture

### 3.1 Network Time Protocol (NTP) Enhanced Implementation

The system implements a specialized time synchronization protocol based on NTP principles but optimized for the specific requirements of physiological research applications.

**3.1.1 Precision Time Synchronization**

```python
class ResearchTimeSynchronizer:
    """
    High-precision time synchronization system for distributed physiological
    monitoring with sub-millisecond accuracy requirements.
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.is_time_server = config.get('is_server', False)
        self.sync_interval = config.get('sync_interval', 10.0)  # seconds
        self.max_offset_threshold = config.get('max_offset', 5.0)  # milliseconds
        
        # Time offset and statistics
        self.time_offset = 0.0  # nanoseconds
        self.round_trip_time = 0.0
        self.sync_accuracy = 0.0
        self.last_sync_time = 0.0
        
        # Synchronization history for drift compensation
        self.sync_history = deque(maxlen=100)
        self.offset_filter = KalmanFilter()
        
        # Network measurement
        self.network_delay_estimator = NetworkDelayEstimator()
        
        # Callbacks for sync events
        self.sync_callbacks = []
        
    async def start_synchronization(self):
        """Start time synchronization process."""
        
        if self.is_time_server:
            await self.start_time_server()
        else:
            await self.start_time_client()
    
    async def start_time_server(self):
        """Start as time server for network synchronization."""
        
        self.time_server = TimeServer(
            port=self.config.get('time_port', 9999),
            precision_mode=True
        )
        
        await self.time_server.start()
        
        # Start periodic accuracy monitoring
        asyncio.create_task(self.monitor_server_accuracy())
        
        logging.info("Time server started in high-precision mode")
    
    async def start_time_client(self):
        """Start as time client synchronizing to server."""
        
        self.time_client = TimeClient(
            server_address=self.config.get('time_server'),
            port=self.config.get('time_port', 9999)
        )
        
        # Perform initial synchronization
        await self.perform_initial_sync()
        
        # Start periodic synchronization
        asyncio.create_task(self.periodic_sync_loop())
        
        logging.info("Time client started with periodic synchronization")
    
    async def perform_sync_exchange(self, server_address: str) -> dict:
        """Perform four-way time synchronization exchange."""
        
        # T1: Client sends request
        t1 = time.time_ns()
        
        sync_request = {
            'type': 'time_sync_request',
            'client_send_time': t1,
            'client_id': self.get_client_id()
        }
        
        # Send request and measure network characteristics
        response = await self.send_sync_request(sync_request, server_address)
        
        # T4: Client receives response
        t4 = time.time_ns()
        
        if response:
            # Extract server timestamps
            t2 = response.get('server_receive_time')  # Server received request
            t3 = response.get('server_send_time')     # Server sent response
            
            # Calculate offset and round-trip time
            offset = ((t2 - t1) + (t3 - t4)) / 2
            rtt = (t4 - t1) - (t3 - t2)
            
            # Apply Kalman filtering for noise reduction
            filtered_offset = self.offset_filter.update(offset)
            
            return {
                'offset': filtered_offset,
                'round_trip_time': rtt,
                'server_time': t3,
                'local_time': t4,
                'accuracy': abs(offset),
                'network_delay': rtt / 2
            }
        
        return None
    
    async def periodic_sync_loop(self):
        """Periodic synchronization maintenance loop."""
        
        while True:
            try:
                server_address = self.config.get('time_server')
                
                # Perform synchronization exchange
                sync_result = await self.perform_sync_exchange(server_address)
                
                if sync_result:
                    # Update time offset
                    self.time_offset = sync_result['offset']
                    self.round_trip_time = sync_result['round_trip_time']
                    self.sync_accuracy = sync_result['accuracy']
                    self.last_sync_time = time.time_ns()
                    
                    # Store in history for drift analysis
                    self.sync_history.append({
                        'timestamp': time.time_ns(),
                        'offset': self.time_offset,
                        'rtt': self.round_trip_time,
                        'accuracy': self.sync_accuracy
                    })
                    
                    # Check for large time corrections
                    if abs(self.time_offset) > self.max_offset_threshold * 1_000_000:  # Convert to ns
                        logging.warning(f"Large time offset detected: {self.time_offset / 1_000_000:.3f}ms")
                    
                    # Notify sync callbacks
                    for callback in self.sync_callbacks:
                        await callback(sync_result)
                    
                    logging.debug(f"Time sync: offset={self.time_offset/1_000_000:.3f}ms, "
                                f"rtt={self.round_trip_time/1_000_000:.3f}ms")
                else:
                    logging.warning("Time synchronization failed")
                
            except Exception as e:
                logging.error(f"Synchronization error: {e}")
            
            # Wait for next sync interval
            await asyncio.sleep(self.sync_interval)
    
    def get_synchronized_time(self) -> int:
        """Get current time synchronized with network time server."""
        
        local_time = time.time_ns()
        
        # Apply time offset correction
        synchronized_time = local_time + self.time_offset
        
        # Apply drift compensation if sufficient history
        if len(self.sync_history) > 10:
            drift_compensation = self.calculate_drift_compensation(local_time)
            synchronized_time += drift_compensation
        
        return synchronized_time
    
    def calculate_drift_compensation(self, current_time: int) -> int:
        """Calculate drift compensation based on historical sync data."""
        
        if len(self.sync_history) < 10:
            return 0
        
        # Extract timestamps and offsets
        timestamps = [entry['timestamp'] for entry in self.sync_history[-10:]]
        offsets = [entry['offset'] for entry in self.sync_history[-10:]]
        
        # Calculate drift rate using linear regression
        try:
            drift_rate = np.polyfit(timestamps, offsets, 1)[0]
            
            # Apply drift compensation
            time_since_last_sync = current_time - self.last_sync_time
            drift_compensation = drift_rate * time_since_last_sync
            
            return int(drift_compensation)
            
        except Exception as e:
            logging.warning(f"Drift calculation error: {e}")
            return 0
    
    def get_sync_quality_metrics(self) -> dict:
        """Get comprehensive synchronization quality metrics."""
        
        if not self.sync_history:
            return {'status': 'no_sync_data'}
        
        recent_syncs = list(self.sync_history)[-20:]  # Last 20 syncs
        
        accuracies = [sync['accuracy'] for sync in recent_syncs]
        rtts = [sync['rtt'] for sync in recent_syncs]
        
        return {
            'current_offset_ms': self.time_offset / 1_000_000,
            'current_accuracy_ms': self.sync_accuracy / 1_000_000,
            'mean_accuracy_ms': np.mean(accuracies) / 1_000_000,
            'std_accuracy_ms': np.std(accuracies) / 1_000_000,
            'mean_rtt_ms': np.mean(rtts) / 1_000_000,
            'sync_count': len(self.sync_history),
            'last_sync_age_s': (time.time_ns() - self.last_sync_time) / 1_000_000_000,
            'drift_rate_ns_per_s': self.calculate_current_drift_rate()
        }
```

### 3.2 Cross-Modal Temporal Alignment

**3.2.1 Multi-Device Synchronization Coordinator**

```python
class MultiDeviceSynchronizationCoordinator:
    """
    Coordinates temporal alignment across multiple heterogeneous devices
    with different sampling rates and processing latencies.
    """
    
    def __init__(self):
        self.devices = {}
        self.sync_master = None
        self.sync_groups = {}
        
        # Synchronization parameters
        self.target_sync_accuracy = 5_000_000  # 5ms in nanoseconds
        self.sync_check_interval = 30.0  # seconds
        
        # Latency compensation
        self.device_latencies = {}
        self.processing_delays = {}
        
        # Synchronization events
        self.sync_events = asyncio.Queue()
        
    def register_device(self, device_id: str, device_info: dict):
        """Register device for synchronization coordination."""
        
        self.devices[device_id] = {
            'info': device_info,
            'last_sync': None,
            'sync_offset': 0,
            'latency_profile': LatencyProfile(),
            'status': DeviceStatus.REGISTERED
        }
        
        # Initialize latency measurement
        asyncio.create_task(self.measure_device_latency(device_id))
        
        logging.info(f"Device {device_id} registered for synchronization")
    
    async def establish_sync_master(self, preferred_master: str = None) -> str:
        """Establish synchronization master among connected devices."""
        
        if preferred_master and preferred_master in self.devices:
            master_id = preferred_master
        else:
            # Select master based on stability and capabilities
            master_id = self.select_optimal_master()
        
        self.sync_master = master_id
        
        # Configure master device
        await self.configure_sync_master(master_id)
        
        # Configure slave devices
        for device_id in self.devices:
            if device_id != master_id:
                await self.configure_sync_slave(device_id)
        
        logging.info(f"Synchronization master established: {master_id}")
        return master_id
    
    async def coordinate_synchronized_recording(self, recording_config: dict) -> bool:
        """Coordinate synchronized recording start across all devices."""
        
        if not self.sync_master:
            raise RuntimeError("No synchronization master established")
        
        try:
            # Calculate synchronized start time
            current_time = time.time_ns()
            start_delay = recording_config.get('start_delay', 5_000_000_000)  # 5 seconds default
            sync_start_time = current_time + start_delay
            
            # Send synchronization commands to all devices
            sync_command = {
                'type': 'synchronized_recording_start',
                'sync_time': sync_start_time,
                'recording_config': recording_config,
                'master_device': self.sync_master
            }
            
            # Send to master first
            master_success = await self.send_sync_command(self.sync_master, sync_command)
            
            if not master_success:
                logging.error("Failed to synchronize master device")
                return False
            
            # Send to all slave devices
            slave_results = await asyncio.gather(*[
                self.send_sync_command(device_id, sync_command)
                for device_id in self.devices
                if device_id != self.sync_master
            ], return_exceptions=True)
            
            # Check results
            failed_devices = []
            for i, result in enumerate(slave_results):
                device_id = list(self.devices.keys())[i + 1]  # Skip master
                if isinstance(result, Exception) or not result:
                    failed_devices.append(device_id)
            
            if failed_devices:
                logging.warning(f"Failed to synchronize devices: {failed_devices}")
                # Optionally continue with partial synchronization
            
            # Wait for confirmation from all devices
            confirmations = await self.wait_for_sync_confirmations(sync_start_time)
            
            success_rate = len(confirmations) / len(self.devices)
            
            if success_rate >= 0.8:  # 80% success threshold
                logging.info(f"Synchronized recording started successfully ({success_rate:.1%} devices)")
                return True
            else:
                logging.error(f"Insufficient device synchronization ({success_rate:.1%} devices)")
                return False
                
        except Exception as e:
            logging.error(f"Synchronized recording coordination failed: {e}")
            return False
    
    async def measure_device_latency(self, device_id: str):
        """Measure and profile device-specific latencies."""
        
        latency_measurements = []
        
        for i in range(10):  # Multiple measurements for accuracy
            # Send ping message
            ping_time = time.time_ns()
            ping_message = {
                'type': 'latency_ping',
                'ping_id': f"{device_id}_{i}",
                'send_time': ping_time
            }
            
            # Send and wait for response
            response = await self.send_ping_request(device_id, ping_message)
            
            if response:
                pong_time = time.time_ns()
                round_trip_latency = pong_time - ping_time
                
                # Estimate one-way latency (half of round-trip)
                one_way_latency = round_trip_latency / 2
                latency_measurements.append(one_way_latency)
            
            await asyncio.sleep(0.1)  # Brief pause between measurements
        
        if latency_measurements:
            # Calculate latency statistics
            mean_latency = np.mean(latency_measurements)
            std_latency = np.std(latency_measurements)
            min_latency = np.min(latency_measurements)
            max_latency = np.max(latency_measurements)
            
            self.device_latencies[device_id] = {
                'mean_ns': mean_latency,
                'std_ns': std_latency,
                'min_ns': min_latency,
                'max_ns': max_latency,
                'measurements': latency_measurements
            }
            
            logging.info(f"Device {device_id} latency: {mean_latency/1_000_000:.2f}ms ± {std_latency/1_000_000:.2f}ms")
        else:
            logging.warning(f"Failed to measure latency for device {device_id}")
    
    def calculate_sync_compensation(self, device_id: str, target_time: int) -> int:
        """Calculate timing compensation for device synchronization."""
        
        if device_id not in self.device_latencies:
            logging.warning(f"No latency data for device {device_id}")
            return target_time
        
        # Get device latency profile
        latency_profile = self.device_latencies[device_id]
        mean_latency = latency_profile['mean_ns']
        
        # Get processing delay if available
        processing_delay = self.processing_delays.get(device_id, 0)
        
        # Calculate compensation
        total_delay = mean_latency + processing_delay
        compensated_time = target_time - total_delay
        
        return compensated_time
    
    async def monitor_sync_quality(self):
        """Continuously monitor synchronization quality across devices."""
        
        while True:
            try:
                sync_metrics = {}
                
                for device_id in self.devices:
                    # Request sync status from device
                    status_request = {
                        'type': 'sync_status_request',
                        'request_time': time.time_ns()
                    }
                    
                    status_response = await self.send_sync_request(device_id, status_request)
                    
                    if status_response:
                        device_metrics = self.analyze_sync_status(device_id, status_response)
                        sync_metrics[device_id] = device_metrics
                
                # Evaluate overall sync quality
                overall_quality = self.evaluate_sync_quality(sync_metrics)
                
                # Take corrective action if needed
                if overall_quality < 0.8:  # Quality threshold
                    await self.perform_sync_correction(sync_metrics)
                
                logging.debug(f"Sync quality monitoring: {overall_quality:.2f}")
                
            except Exception as e:
                logging.error(f"Sync quality monitoring error: {e}")
            
            await asyncio.sleep(self.sync_check_interval)
```

## 4. Protocol Implementation and Message Formats

### 4.1 Research Protocol Specification

**4.1.1 Message Format Standards**

```python
class ResearchProtocolV2:
    """
    Standardized protocol for research communication with comprehensive
    message validation and temporal metadata.
    """
    
    PROTOCOL_VERSION = "2.0"
    
    class MessageType(Enum):
        # Discovery and connection
        DEVICE_ANNOUNCEMENT = "device_announcement"
        CONNECTION_REQUEST = "connection_request"
        CONNECTION_RESPONSE = "connection_response"
        HANDSHAKE = "handshake"
        
        # Time synchronization
        TIME_SYNC_REQUEST = "time_sync_request"
        TIME_SYNC_RESPONSE = "time_sync_response"
        SYNC_PULSE = "sync_pulse"
        
        # Recording control
        RECORDING_START = "recording_start"
        RECORDING_STOP = "recording_stop"
        RECORDING_PAUSE = "recording_pause"
        RECORDING_STATUS = "recording_status"
        
        # Data transmission
        SENSOR_DATA = "sensor_data"
        VIDEO_FRAME = "video_frame"
        PROCESSED_DATA = "processed_data"
        
        # Quality and monitoring
        QUALITY_REPORT = "quality_report"
        STATUS_UPDATE = "status_update"
        ERROR_REPORT = "error_report"
        
        # Configuration
        CONFIG_UPDATE = "config_update"
        CALIBRATION_DATA = "calibration_data"
    
    @staticmethod
    def create_message(message_type: MessageType, data: dict, 
                      device_id: str, priority: int = 5) -> dict:
        """Create standardized protocol message."""
        
        timestamp = time.time_ns()
        
        message = {
            'protocol_version': ResearchProtocolV2.PROTOCOL_VERSION,
            'message_id': str(uuid.uuid4()),
            'timestamp': timestamp,
            'device_id': device_id,
            'message_type': message_type.value,
            'priority': priority,
            'data': data,
            'checksum': None  # Will be calculated
        }
        
        # Calculate and add checksum
        message['checksum'] = ResearchProtocolV2.calculate_checksum(message)
        
        return message
    
    @staticmethod
    def validate_message(message: dict) -> tuple[bool, str]:
        """Validate protocol message format and integrity."""
        
        required_fields = [
            'protocol_version', 'message_id', 'timestamp',
            'device_id', 'message_type', 'data', 'checksum'
        ]
        
        # Check required fields
        for field in required_fields:
            if field not in message:
                return False, f"Missing required field: {field}"
        
        # Validate protocol version
        if message['protocol_version'] != ResearchProtocolV2.PROTOCOL_VERSION:
            return False, f"Unsupported protocol version: {message['protocol_version']}"
        
        # Validate message type
        try:
            MessageType(message['message_type'])
        except ValueError:
            return False, f"Unknown message type: {message['message_type']}"
        
        # Validate timestamp (not too old or future)
        current_time = time.time_ns()
        message_time = message['timestamp']
        
        if abs(current_time - message_time) > 60_000_000_000:  # 60 seconds
            return False, "Message timestamp out of acceptable range"
        
        # Validate checksum
        expected_checksum = message['checksum']
        message_copy = message.copy()
        message_copy['checksum'] = None
        calculated_checksum = ResearchProtocolV2.calculate_checksum(message_copy)
        
        if expected_checksum != calculated_checksum:
            return False, "Message checksum validation failed"
        
        return True, "Message valid"
    
    @staticmethod
    def calculate_checksum(message: dict) -> str:
        """Calculate message checksum for integrity validation."""
        
        # Create deterministic string representation
        message_copy = message.copy()
        message_copy.pop('checksum', None)  # Remove checksum field
        
        # Sort keys for consistent ordering
        sorted_message = json.dumps(message_copy, sort_keys=True, separators=(',', ':'))
        
        # Calculate SHA-256 hash
        hash_object = hashlib.sha256(sorted_message.encode())
        return hash_object.hexdigest()[:16]  # First 16 characters


class DeviceAnnouncementMessage:
    """Device announcement message for network discovery."""
    
    @staticmethod
    def create(device_info: dict) -> dict:
        """Create device announcement message."""
        
        announcement_data = {
            'device_type': device_info.get('type', 'unknown'),
            'device_name': device_info.get('name', 'Unknown Device'),
            'capabilities': device_info.get('capabilities', []),
            'network_info': {
                'ip_address': device_info.get('ip_address'),
                'websocket_port': device_info.get('websocket_port'),
                'udp_port': device_info.get('udp_port')
            },
            'hardware_info': {
                'manufacturer': device_info.get('manufacturer'),
                'model': device_info.get('model'),
                'serial_number': device_info.get('serial_number')
            },
            'software_info': {
                'app_version': device_info.get('app_version'),
                'protocol_version': ResearchProtocolV2.PROTOCOL_VERSION,
                'supported_features': device_info.get('features', [])
            },
            'status': {
                'battery_level': device_info.get('battery_level'),
                'available_storage': device_info.get('storage_available'),
                'temperature': device_info.get('device_temperature')
            }
        }
        
        return ResearchProtocolV2.create_message(
            ResearchProtocolV2.MessageType.DEVICE_ANNOUNCEMENT,
            announcement_data,
            device_info.get('device_id', 'unknown')
        )


class SensorDataMessage:
    """Sensor data transmission message with temporal metadata."""
    
    @staticmethod
    def create(sensor_data: dict, device_id: str) -> dict:
        """Create sensor data message with temporal information."""
        
        # Standardize sensor data format
        standardized_data = {
            'sensor_type': sensor_data.get('type'),
            'timestamp': sensor_data.get('timestamp', time.time_ns()),
            'sequence_number': sensor_data.get('sequence'),
            'sampling_rate': sensor_data.get('sampling_rate'),
            'data_format': sensor_data.get('format', 'json'),
            'quality_indicators': {
                'signal_quality': sensor_data.get('quality', 1.0),
                'noise_level': sensor_data.get('noise_level', 0.0),
                'saturation_flag': sensor_data.get('saturated', False)
            },
            'sensor_readings': sensor_data.get('readings', []),
            'metadata': sensor_data.get('metadata', {})
        }
        
        return ResearchProtocolV2.create_message(
            ResearchProtocolV2.MessageType.SENSOR_DATA,
            standardized_data,
            device_id,
            priority=8  # High priority for sensor data
        )


class RecordingControlMessage:
    """Recording control messages for coordinated data collection."""
    
    @staticmethod
    def create_start_command(recording_config: dict, coordinator_id: str) -> dict:
        """Create recording start command."""
        
        start_data = {
            'command': 'start',
            'session_id': recording_config.get('session_id'),
            'sync_timestamp': recording_config.get('sync_start_time'),
            'recording_parameters': {
                'duration': recording_config.get('duration'),
                'quality_settings': recording_config.get('quality'),
                'sensor_configuration': recording_config.get('sensors'),
                'storage_location': recording_config.get('storage_path')
            },
            'synchronization_config': {
                'master_device': recording_config.get('sync_master'),
                'sync_accuracy_requirement': recording_config.get('sync_accuracy'),
                'backup_sync_method': recording_config.get('backup_sync')
            }
        }
        
        return ResearchProtocolV2.create_message(
            ResearchProtocolV2.MessageType.RECORDING_START,
            start_data,
            coordinator_id,
            priority=9  # Highest priority for control commands
        )
```

### 4.2 Network Quality of Service (QoS)

**4.2.1 Traffic Prioritization and Bandwidth Management**

```python
class NetworkQoSManager:
    """
    Quality of Service manager for research network traffic prioritization
    and bandwidth optimization.
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.traffic_classifiers = {}
        self.bandwidth_monitors = {}
        self.congestion_controllers = {}
        
        # QoS policies
        self.priority_classes = {
            'critical_control': {'priority': 10, 'max_latency_ms': 10},
            'time_sync': {'priority': 9, 'max_latency_ms': 5},
            'sensor_data': {'priority': 8, 'max_latency_ms': 50},
            'video_stream': {'priority': 6, 'max_latency_ms': 100},
            'file_transfer': {'priority': 3, 'max_latency_ms': 1000},
            'status_updates': {'priority': 2, 'max_latency_ms': 5000}
        }
        
        # Traffic shaping
        self.rate_limiters = {}
        self.packet_schedulers = {}
        
        self.setup_qos_infrastructure()
    
    def setup_qos_infrastructure(self):
        """Initialize QoS infrastructure and policies."""
        
        # Create traffic classifiers
        for traffic_class, policy in self.priority_classes.items():
            self.traffic_classifiers[traffic_class] = TrafficClassifier(
                class_name=traffic_class,
                priority=policy['priority'],
                max_latency=policy['max_latency_ms']
            )
        
        # Initialize bandwidth monitoring
        self.bandwidth_monitor = BandwidthMonitor(
            measurement_interval=1.0,
            history_size=300  # 5 minutes of history
        )
        
        # Setup congestion control
        self.congestion_controller = AdaptiveCongestionController(
            target_utilization=0.8,
            adaptation_rate=0.1
        )
    
    def classify_message(self, message: dict) -> str:
        """Classify message for QoS handling."""
        
        message_type = message.get('message_type', '')
        priority = message.get('priority', 5)
        
        # Classification rules
        if message_type in ['time_sync_request', 'time_sync_response', 'sync_pulse']:
            return 'time_sync'
        elif message_type in ['recording_start', 'recording_stop', 'emergency_stop']:
            return 'critical_control'
        elif message_type == 'sensor_data':
            return 'sensor_data'
        elif message_type == 'video_frame':
            return 'video_stream'
        elif message_type in ['status_update', 'quality_report']:
            return 'status_updates'
        elif priority >= 8:
            return 'critical_control'
        elif priority >= 6:
            return 'sensor_data'
        else:
            return 'status_updates'
    
    async def send_with_qos(self, message: dict, destination: str, 
                           transport: str = 'websocket') -> bool:
        """Send message with QoS prioritization."""
        
        # Classify message
        traffic_class = self.classify_message(message)
        
        # Get QoS policy
        qos_policy = self.priority_classes.get(traffic_class, {})
        
        # Check bandwidth availability
        available_bandwidth = self.bandwidth_monitor.get_available_bandwidth()
        
        if available_bandwidth < 0.1:  # Less than 10% available
            # Apply congestion control
            await self.handle_congestion(message, traffic_class)
        
        # Apply rate limiting
        if traffic_class in self.rate_limiters:
            await self.rate_limiters[traffic_class].wait_for_capacity()
        
        # Send with appropriate transport
        if transport == 'websocket':
            success = await self.send_websocket_with_priority(message, destination, qos_policy)
        elif transport == 'udp':
            success = await self.send_udp_with_priority(message, destination, qos_policy)
        else:
            raise ValueError(f"Unsupported transport: {transport}")
        
        # Update bandwidth monitoring
        message_size = len(json.dumps(message).encode())
        self.bandwidth_monitor.record_transmission(message_size, success)
        
        return success
    
    async def handle_congestion(self, message: dict, traffic_class: str):
        """Handle network congestion based on traffic class."""
        
        if traffic_class in ['critical_control', 'time_sync']:
            # Critical traffic - try to send anyway
            return
        elif traffic_class == 'sensor_data':
            # Reduce sensor data rate
            await self.request_sensor_rate_reduction()
        elif traffic_class == 'video_stream':
            # Reduce video quality or frame rate
            await self.request_video_quality_reduction()
        else:
            # Delay non-critical traffic
            await asyncio.sleep(0.1)
    
    def get_network_statistics(self) -> dict:
        """Get comprehensive network performance statistics."""
        
        return {
            'bandwidth_utilization': self.bandwidth_monitor.get_utilization(),
            'average_latency_ms': self.bandwidth_monitor.get_average_latency(),
            'packet_loss_rate': self.bandwidth_monitor.get_packet_loss_rate(),
            'congestion_events': self.congestion_controller.get_congestion_count(),
            'traffic_distribution': self.get_traffic_distribution(),
            'qos_violations': self.get_qos_violations()
        }
    
    def get_traffic_distribution(self) -> dict:
        """Get traffic distribution across priority classes."""
        
        distribution = {}
        total_traffic = 0
        
        for traffic_class, classifier in self.traffic_classifiers.items():
            class_traffic = classifier.get_total_traffic()
            distribution[traffic_class] = class_traffic
            total_traffic += class_traffic
        
        # Convert to percentages
        if total_traffic > 0:
            for traffic_class in distribution:
                distribution[traffic_class] = (distribution[traffic_class] / total_traffic) * 100
        
        return distribution


class AdaptiveCongestionController:
    """
    Adaptive congestion control for research network traffic with
    specialized handling for time-critical physiological data.
    """
    
    def __init__(self, target_utilization: float = 0.8, adaptation_rate: float = 0.1):
        self.target_utilization = target_utilization
        self.adaptation_rate = adaptation_rate
        
        # Congestion state
        self.current_utilization = 0.0
        self.congestion_count = 0
        self.last_congestion_time = 0
        
        # Adaptive parameters
        self.video_quality_factor = 1.0
        self.sensor_sampling_factor = 1.0
        self.update_rate_factor = 1.0
        
        # Control algorithm
        self.pid_controller = PIDController(
            kp=0.5, ki=0.1, kd=0.2,
            setpoint=target_utilization
        )
    
    async def update_congestion_state(self, utilization: float):
        """Update congestion control based on current network utilization."""
        
        self.current_utilization = utilization
        
        # Detect congestion
        if utilization > self.target_utilization:
            self.congestion_count += 1
            self.last_congestion_time = time.time()
            
            # Calculate control output
            control_output = self.pid_controller.update(utilization)
            
            # Apply adaptive rate control
            await self.apply_rate_adaptation(control_output)
        
        # Recovery detection
        elif utilization < self.target_utilization * 0.9:
            # Gradually restore rates
            await self.restore_rates()
    
    async def apply_rate_adaptation(self, control_output: float):
        """Apply adaptive rate control based on congestion level."""
        
        # Adjust video quality
        video_reduction = max(0.1, 1.0 - (control_output * 0.5))
        self.video_quality_factor = min(self.video_quality_factor, video_reduction)
        
        # Adjust sensor sampling rates (more conservative)
        sensor_reduction = max(0.5, 1.0 - (control_output * 0.2))
        self.sensor_sampling_factor = min(self.sensor_sampling_factor, sensor_reduction)
        
        # Adjust status update rates
        update_reduction = max(0.1, 1.0 - (control_output * 0.8))
        self.update_rate_factor = min(self.update_rate_factor, update_reduction)
        
        # Apply the adaptations
        await self.notify_rate_changes()
    
    async def restore_rates(self):
        """Gradually restore rates after congestion clears."""
        
        recovery_rate = 0.05  # 5% increase per update
        
        self.video_quality_factor = min(1.0, self.video_quality_factor + recovery_rate)
        self.sensor_sampling_factor = min(1.0, self.sensor_sampling_factor + recovery_rate)
        self.update_rate_factor = min(1.0, self.update_rate_factor + recovery_rate)
        
        await self.notify_rate_changes()
```

This completes the Networking and Synchronization design document. The document provides comprehensive coverage of the distributed system networking architecture, time synchronization mechanisms, protocol implementations, and quality of service management required for precise physiological research applications.

Would you like me to continue with the remaining Chapter 4 documents (Sensor Integration, UI/UX Design, Database Design) or move on to Chapter 5 (Testing and Evaluation)? Let me know how you'd like to proceed!