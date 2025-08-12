"""
Load and Stress Testing Package
==============================

Provides comprehensive load and stress testing capabilities for the
Multi-Sensor Recording System, focusing on Socket.IO connections,
concurrent device management, and high-frequency data streaming.

Modules:
- test_socketio_load: Socket.IO load generation and stress testing
- test_concurrent_devices: Multi-device connection stress tests
- test_data_streaming_load: High-frequency data streaming load tests
- load_generators: Utility classes for generating test loads

Requirements Coverage:
- NFR1: Performance under load and stress conditions
- NFR3: Fault tolerance with concurrent connections
- FR2: Synchronized recording under heavy load
- FR8: System stability with multiple device failures
"""