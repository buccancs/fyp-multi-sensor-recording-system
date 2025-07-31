#!/usr/bin/env python3
"""
Test Suite for Enhanced Latency and Delay Measurement

This module tests the comprehensive latency measurement and network quality
assessment features of the enhanced networking implementation.

Features tested:
- Ping/pong latency measurement
- Jitter calculation
- Packet loss estimation
- Network quality assessment
- Time synchronization accuracy
- Advanced latency statistics

Author: Multi-Sensor Recording System Team
Date: 2025-01-15
"""

import asyncio
import json
import os
import socket
import sys
import threading
import time
import unittest
from unittest.mock import Mock, patch, MagicMock

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from network.enhanced_device_server import (
    EnhancedDeviceServer,
    EnhancedRemoteDevice,
    MessagePriority,
    ConnectionState,
    NetworkMessage
)


class TestLatencyMeasurement(unittest.TestCase):
    """Test latency measurement and network quality assessment."""
    
    def setUp(self):
        """Set up test environment."""
        self.server = EnhancedDeviceServer(
            host="127.0.0.1",
            port=9001,
            max_connections=5,
            heartbeat_interval=1.0
        )
        self.mock_devices = []
        
    def tearDown(self):
        """Clean up test environment."""
        for device in self.mock_devices:
            device.disconnect()
        
        if self.server.running:
            self.server.stop_server()
    
    def test_latency_calculation_basic(self):
        """Test basic latency calculation from timestamps."""
        # Create mock device
        mock_socket = Mock()
        device = EnhancedRemoteDevice(
            device_id="test_device_1",
            capabilities=["camera"],
            client_socket=mock_socket,
            address=("127.0.0.1", 12345)
        )
        
        # Test latency updates
        test_latencies = [10.0, 15.0, 20.0, 12.0, 18.0]
        for latency in test_latencies:
            device.update_latency(latency)
        
        # Verify statistics
        self.assertEqual(len(device.stats.latency_samples), 5)
        self.assertAlmostEqual(device.stats.average_latency, 15.0, places=1)
        self.assertEqual(device.stats.min_latency, 10.0)
        self.assertEqual(device.stats.max_latency, 20.0)
        self.assertGreater(device.stats.jitter, 0)  # Should have some jitter
    
    def test_ping_pong_handling(self):
        """Test ping/pong message handling for latency measurement."""
        # Create mock device
        mock_socket = Mock()
        device = EnhancedRemoteDevice(
            device_id="test_device_1",
            capabilities=["camera"],
            client_socket=mock_socket,
            address=("127.0.0.1", 12345)
        )
        
        # Test ping handling
        ping_timestamp = time.time()
        ping_data = f"ping:test_ping_1:{ping_timestamp}:1"
        
        # Simulate ping message processing
        self.server.handle_ping_message(device, ping_data, ping_timestamp)
        
        # Verify ping stats were updated
        self.assertEqual(device.stats.pong_count, 1)
        self.assertGreater(len(device.stats.latency_samples), 0)
    
    def test_jitter_calculation(self):
        """Test jitter calculation with varying latencies."""
        mock_socket = Mock()
        device = EnhancedRemoteDevice(
            device_id="test_device_1",
            capabilities=["camera"],
            client_socket=mock_socket,
            address=("127.0.0.1", 12345)
        )
        
        # Add latencies with high variation (high jitter)
        high_jitter_latencies = [10.0, 50.0, 5.0, 45.0, 15.0, 40.0]
        for latency in high_jitter_latencies:
            device.update_latency(latency)
        
        high_jitter = device.stats.jitter
        
        # Reset and add latencies with low variation (low jitter)
        device.stats.latency_samples.clear()
        low_jitter_latencies = [20.0, 21.0, 19.0, 20.5, 19.5, 20.2]
        for latency in low_jitter_latencies:
            device.update_latency(latency)
        
        low_jitter = device.stats.jitter
        
        # High variation should result in higher jitter
        self.assertGreater(high_jitter, low_jitter)
    
    def test_packet_loss_calculation(self):
        """Test packet loss rate calculation."""
        mock_socket = Mock()
        device = EnhancedRemoteDevice(
            device_id="test_device_1",
            capabilities=["camera"],
            client_socket=mock_socket,
            address=("127.0.0.1", 12345)
        )
        
        # Simulate 10 pings sent, 8 pongs received
        device.stats.ping_count = 10
        device.stats.pong_count = 8
        device.update_latency(10.0)  # Trigger packet loss calculation
        
        # Should show 20% packet loss
        self.assertAlmostEqual(device.stats.packet_loss_rate, 20.0, places=1)
    
    def test_network_quality_assessment(self):
        """Test overall network quality assessment."""
        # Start server
        self.assertTrue(self.server.start_server())
        time.sleep(0.1)  # Let server start
        
        # Create mock devices with different latency profiles
        devices_data = [
            ("excellent_device", [5.0, 6.0, 4.0, 5.5, 4.5]),  # Excellent
            ("good_device", [60.0, 70.0, 65.0, 55.0, 75.0]),   # Good
            ("poor_device", [250.0, 300.0, 280.0, 320.0, 290.0])  # Poor
        ]
        
        for device_id, latencies in devices_data:
            mock_socket = Mock()
            device = EnhancedRemoteDevice(
                device_id=device_id,
                capabilities=["camera"],
                client_socket=mock_socket,
                address=("127.0.0.1", 12345)
            )
            
            # Add to server's device list
            with self.server.devices_mutex:
                self.server.devices[device_id] = device
            
            # Update latencies
            for latency in latencies:
                device.update_latency(latency)
        
        # Test overall network statistics
        stats = self.server.get_network_statistics()
        
        self.assertEqual(stats["active_devices"], 3)
        self.assertIn("overall_stats", stats)
        self.assertIn("network_quality", stats["overall_stats"])
        
        # Test individual device statistics
        for device_id, _ in devices_data:
            device_stats = self.server.get_device_latency_statistics(device_id)
            self.assertIn("average_latency", device_stats)
            self.assertIn("jitter", device_stats)
            self.assertIn("packet_loss_rate", device_stats)
    
    def test_latency_statistics_api(self):
        """Test latency statistics API methods."""
        mock_socket = Mock()
        device = EnhancedRemoteDevice(
            device_id="test_device_1",
            capabilities=["camera"],
            client_socket=mock_socket,
            address=("127.0.0.1", 12345)
        )
        
        # Add to server
        with self.server.devices_mutex:
            self.server.devices["test_device_1"] = device
        
        # Add some latency data
        test_latencies = [10.0, 15.0, 12.0, 18.0, 14.0]
        for latency in test_latencies:
            device.update_latency(latency)
        
        # Test device-specific statistics
        stats = self.server.get_device_latency_statistics("test_device_1")
        
        self.assertEqual(stats["device_id"], "test_device_1")
        self.assertAlmostEqual(stats["average_latency"], 13.8, places=1)
        self.assertEqual(stats["min_latency"], 10.0)
        self.assertEqual(stats["max_latency"], 18.0)
        self.assertEqual(stats["sample_count"], 5)
        self.assertIsInstance(stats["recent_samples"], list)
        
        # Test non-existent device
        empty_stats = self.server.get_device_latency_statistics("non_existent")
        self.assertIn("error", empty_stats)
    
    def test_adaptive_quality_based_on_latency(self):
        """Test adaptive streaming quality based on latency measurements."""
        mock_socket = Mock()
        device = EnhancedRemoteDevice(
            device_id="test_device_1",
            capabilities=["camera"],
            client_socket=mock_socket,
            address=("127.0.0.1", 12345)
        )
        
        # Test excellent conditions (low latency, low error rate)
        device.adapt_streaming_quality(25.0, 0.01)  # 25ms latency, 1% error rate
        self.assertEqual(device.streaming_quality, 'high')
        self.assertEqual(device.max_frame_rate, 30)
        
        # Test poor conditions (high latency, high error rate)
        device.adapt_streaming_quality(250.0, 0.15)  # 250ms latency, 15% error rate
        self.assertEqual(device.streaming_quality, 'low')
        self.assertEqual(device.max_frame_rate, 5)
        
        # Test medium conditions
        device.adapt_streaming_quality(100.0, 0.07)  # 100ms latency, 7% error rate
        self.assertEqual(device.streaming_quality, 'medium')
        self.assertEqual(device.max_frame_rate, 15)
    
    def test_timestamp_accuracy(self):
        """Test timestamp accuracy for latency measurement."""
        # Test timestamp consistency
        start_time = time.time()
        
        # Simulate message with embedded timestamp
        message = {
            "type": "heartbeat",
            "timestamp": start_time
        }
        
        # Process after some delay
        time.sleep(0.01)  # 10ms delay
        process_time = time.time()
        
        # Calculate latency
        latency = (process_time - message["timestamp"]) * 1000  # Convert to ms
        
        # Latency should be approximately 10ms (within reasonable margin)
        self.assertGreater(latency, 5.0)
        self.assertLess(latency, 50.0)  # Allow some margin for processing
    
    def test_concurrent_latency_measurement(self):
        """Test latency measurement under concurrent load."""
        mock_socket = Mock()
        device = EnhancedRemoteDevice(
            device_id="test_device_1",
            capabilities=["camera"],
            client_socket=mock_socket,
            address=("127.0.0.1", 12345)
        )
        
        # Function to add latency measurements concurrently
        def add_latencies(start_latency, count):
            for i in range(count):
                device.update_latency(start_latency + i)
        
        # Create multiple threads adding latency measurements
        threads = []
        for i in range(5):
            thread = threading.Thread(target=add_latencies, args=(i * 10, 10))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all measurements were recorded
        self.assertEqual(len(device.stats.latency_samples), 50)
        self.assertGreater(device.stats.average_latency, 0)
        self.assertGreater(device.stats.max_latency, device.stats.min_latency)


class TestLatencyIntegration(unittest.TestCase):
    """Integration tests for latency measurement in realistic scenarios."""
    
    def setUp(self):
        """Set up integration test environment."""
        self.server = EnhancedDeviceServer(
            host="127.0.0.1",
            port=9002,
            max_connections=5,
            heartbeat_interval=0.5  # Faster for testing
        )
    
    def tearDown(self):
        """Clean up integration test environment."""
        if self.server.running:
            self.server.stop_server()
    
    def test_end_to_end_latency_measurement(self):
        """Test end-to-end latency measurement in realistic scenario."""
        # Start server
        self.assertTrue(self.server.start_server())
        time.sleep(0.1)
        
        # Create and connect mock client
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect(("127.0.0.1", 9002))
            
            # Send handshake
            handshake = {
                "type": "handshake",
                "device_id": "integration_test_device",
                "capabilities": ["camera", "enhanced_latency"],
                "timestamp": time.time()
            }
            
            json_data = json.dumps(handshake).encode('utf-8')
            length_header = len(json_data).to_bytes(4, 'big')
            client_socket.sendall(length_header + json_data)
            
            # Wait for handshake response
            time.sleep(0.1)
            
            # Send ping message
            ping_timestamp = time.time()
            ping_message = {
                "type": "status",
                "storage": f"ping:test_ping:{ping_timestamp}:1",
                "timestamp": ping_timestamp,
                "battery": 80,
                "connected": True
            }
            
            json_data = json.dumps(ping_message).encode('utf-8')
            length_header = len(json_data).to_bytes(4, 'big')
            client_socket.sendall(length_header + json_data)
            
            # Wait for processing
            time.sleep(0.1)
            
            # Check server statistics
            stats = self.server.get_network_statistics()
            self.assertGreater(stats["active_devices"], 0)
            
            # Verify latency measurement was recorded
            if "integration_test_device" in stats["devices"]:
                device_stats = stats["devices"]["integration_test_device"]["stats"]
                self.assertGreaterEqual(device_stats["pong_count"], 1)
                
        finally:
            client_socket.close()


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)