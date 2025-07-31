#!/usr/bin/env python3
"""
Simplified Rock-Solid Networking Test

This test validates the core networking concepts without requiring PyQt5 or other dependencies.
It tests the basic socket communication, message framing, and reliability features.

Author: Multi-Sensor Recording System Team
Date: 2025-01-15
"""

import json
import random
import socket
import struct
import threading
import time
import unittest
from typing import Dict, List, Optional


class SimpleNetworkMessage:
    """Simple network message class without dependencies."""
    
    def __init__(self, msg_type: str, payload: Dict, priority: int = 3):
        self.type = msg_type
        self.payload = payload
        self.priority = priority
        self.timestamp = time.time()
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        data = {
            "type": self.type,
            "timestamp": self.timestamp,
            **self.payload
        }
        return json.dumps(data)
    
    @classmethod
    def from_json(cls, json_str: str) -> Optional['SimpleNetworkMessage']:
        """Create from JSON string."""
        try:
            data = json.loads(json_str)
            msg_type = data.pop("type")
            timestamp = data.pop("timestamp", time.time())
            
            msg = cls(msg_type, data)
            msg.timestamp = timestamp
            return msg
        except Exception:
            return None


class SimpleServer:
    """Simple server for testing networking concepts."""
    
    def __init__(self, host: str = "127.0.0.1", port: int = None):
        self.host = host
        self.port = port or (9000 + random.randint(1, 999))
        self.server_socket = None
        self.running = False
        self.clients = {}
        self.message_count = 0
        
    def start(self):
        """Start the server."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            print(f"Simple server started on {self.host}:{self.port}")
            
            # Start in separate thread
            threading.Thread(target=self._accept_loop, daemon=True).start()
            return True
            
        except Exception as e:
            print(f"Server start failed: {e}")
            return False
    
    def stop(self):
        """Stop the server."""
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        print("Simple server stopped")
    
    def _accept_loop(self):
        """Accept client connections."""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                client_id = f"{address[0]}:{address[1]}"
                self.clients[client_id] = client_socket
                
                print(f"Client connected: {client_id}")
                
                # Handle client in separate thread
                threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, client_id),
                    daemon=True
                ).start()
                
            except Exception as e:
                if self.running:
                    print(f"Accept error: {e}")
    
    def _handle_client(self, client_socket: socket.socket, client_id: str):
        """Handle individual client."""
        try:
            while self.running:
                # Receive message with length prefix
                message = self._receive_message(client_socket)
                if not message:
                    break
                
                self.message_count += 1
                print(f"Received from {client_id}: {message.type}")
                
                # Echo back with response
                if message.type == "handshake":
                    response = SimpleNetworkMessage("handshake_ack", {
                        "server_name": "Simple Test Server",
                        "compatible": True
                    })
                    self._send_message(client_socket, response)
                
                elif message.type == "command":
                    command = message.payload.get("command", "unknown")
                    response = SimpleNetworkMessage("ack", {
                        "cmd": command,
                        "status": "ok"
                    })
                    self._send_message(client_socket, response)
                
                elif message.type == "heartbeat":
                    response = SimpleNetworkMessage("heartbeat_response", {})
                    self._send_message(client_socket, response)
                
        except Exception as e:
            print(f"Client {client_id} error: {e}")
        finally:
            try:
                client_socket.close()
            except:
                pass
            if client_id in self.clients:
                del self.clients[client_id]
            print(f"Client {client_id} disconnected")
    
    def _receive_message(self, sock: socket.socket) -> Optional[SimpleNetworkMessage]:
        """Receive message with length prefix."""
        try:
            # Read length header
            length_data = self._recv_exact(sock, 4)
            if not length_data:
                return None
            
            message_length = struct.unpack('>I', length_data)[0]
            
            if message_length <= 0 or message_length > 1024 * 1024:
                return None
            
            # Read message data
            message_data = self._recv_exact(sock, message_length)
            if not message_data:
                return None
            
            json_str = message_data.decode('utf-8')
            return SimpleNetworkMessage.from_json(json_str)
            
        except Exception:
            return None
    
    def _send_message(self, sock: socket.socket, message: SimpleNetworkMessage) -> bool:
        """Send message with length prefix."""
        try:
            json_data = message.to_json().encode('utf-8')
            length_header = struct.pack('>I', len(json_data))
            
            sock.sendall(length_header + json_data)
            return True
            
        except Exception as e:
            print(f"Send error: {e}")
            return False
    
    def _recv_exact(self, sock: socket.socket, length: int) -> Optional[bytes]:
        """Receive exactly 'length' bytes."""
        data = b""
        while len(data) < length:
            chunk = sock.recv(length - len(data))
            if not chunk:
                return None
            data += chunk
        return data
    
    def send_command_to_all(self, command: str) -> int:
        """Send command to all connected clients."""
        message = SimpleNetworkMessage("command", {"command": command})
        count = 0
        
        for client_id, client_socket in list(self.clients.items()):
            if self._send_message(client_socket, message):
                count += 1
        
        return count
    
    def get_stats(self) -> Dict:
        """Get server statistics."""
        return {
            "running": self.running,
            "connected_clients": len(self.clients),
            "messages_processed": self.message_count
        }


class SimpleClient:
    """Simple client for testing networking concepts."""
    
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.socket = None
        self.connected = False
        self.running = False
        self.messages_received = 0
        
    def connect(self, host: str = "127.0.0.1", port: int = None) -> bool:
        """Connect to server."""
        if port is None:
            port = 9004  # Default port for backward compatibility
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.connected = True
            self.running = True
            
            print(f"Client {self.client_id} connected to {host}:{port}")
            
            # Start receiver thread
            threading.Thread(target=self._receive_loop, daemon=True).start()
            
            return True
            
        except Exception as e:
            print(f"Client {self.client_id} connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from server."""
        self.running = False
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        print(f"Client {self.client_id} disconnected")
    
    def send_handshake(self) -> bool:
        """Send handshake message."""
        message = SimpleNetworkMessage("handshake", {
            "device_id": self.client_id,
            "capabilities": ["test_capability"]
        })
        return self._send_message(message)
    
    def send_heartbeat(self) -> bool:
        """Send heartbeat message."""
        message = SimpleNetworkMessage("heartbeat", {})
        return self._send_message(message)
    
    def send_status(self, **kwargs) -> bool:
        """Send status update."""
        message = SimpleNetworkMessage("status", kwargs)
        return self._send_message(message)
    
    def _send_message(self, message: SimpleNetworkMessage) -> bool:
        """Send message to server."""
        if not self.connected or not self.socket:
            return False
        
        try:
            json_data = message.to_json().encode('utf-8')
            length_header = struct.pack('>I', len(json_data))
            
            self.socket.sendall(length_header + json_data)
            return True
            
        except Exception as e:
            print(f"Client {self.client_id} send error: {e}")
            return False
    
    def _receive_loop(self):
        """Receive messages from server."""
        while self.running and self.connected:
            try:
                message = self._receive_message()
                if message:
                    self.messages_received += 1
                    print(f"Client {self.client_id} received: {message.type}")
                else:
                    time.sleep(0.1)
                    
            except Exception as e:
                if self.running:
                    print(f"Client {self.client_id} receive error: {e}")
                break
    
    def _receive_message(self) -> Optional[SimpleNetworkMessage]:
        """Receive message from server."""
        try:
            # Read length header
            length_data = self._recv_exact(4)
            if not length_data:
                return None
            
            message_length = struct.unpack('>I', length_data)[0]
            
            if message_length <= 0 or message_length > 1024 * 1024:
                return None
            
            # Read message data
            message_data = self._recv_exact(message_length)
            if not message_data:
                return None
            
            json_str = message_data.decode('utf-8')
            return SimpleNetworkMessage.from_json(json_str)
            
        except Exception:
            return None
    
    def _recv_exact(self, length: int) -> Optional[bytes]:
        """Receive exactly 'length' bytes."""
        data = b""
        while len(data) < length:
            chunk = self.socket.recv(length - len(data))
            if not chunk:
                return None
            data += chunk
        return data
    
    def get_stats(self) -> Dict:
        """Get client statistics."""
        return {
            "client_id": self.client_id,
            "connected": self.connected,
            "messages_received": self.messages_received
        }


class TestSimpleNetworking(unittest.TestCase):
    """Test simple networking implementation."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_port = 9000 + random.randint(100, 999)
        self.server = SimpleServer(port=self.test_port)
        self.clients = []
    
    def tearDown(self):
        """Clean up test environment."""
        for client in self.clients:
            client.disconnect()
        
        if self.server:
            self.server.stop()
        
        time.sleep(0.5)  # Allow cleanup
    
    def test_server_startup(self):
        """Test server startup and shutdown."""
        success = self.server.start()
        self.assertTrue(success, "Server should start successfully")
        
        time.sleep(0.2)
        stats = self.server.get_stats()
        self.assertTrue(stats["running"], "Server should be running")
        self.assertEqual(stats["connected_clients"], 0, "No clients initially")
        
        self.server.stop()
        time.sleep(0.2)
        stats = self.server.get_stats()
        self.assertFalse(stats["running"], "Server should be stopped")
    
    def test_client_connection(self):
        """Test client connection and handshake."""
        self.assertTrue(self.server.start(), "Server should start")
        time.sleep(0.2)
        
        # Connect client
        client = SimpleClient("test_client_1")
        self.clients.append(client)
        
        success = client.connect(port=self.test_port)
        self.assertTrue(success, "Client should connect")
        
        # Send handshake
        success = client.send_handshake()
        self.assertTrue(success, "Handshake should be sent")
        
        time.sleep(0.5)  # Allow server processing
        
        # Check server stats
        stats = self.server.get_stats()
        self.assertEqual(stats["connected_clients"], 1, "One client should be connected")
    
    def test_message_exchange(self):
        """Test message exchange between client and server."""
        self.assertTrue(self.server.start(), "Server should start")
        time.sleep(0.2)
        
        # Connect client
        client = SimpleClient("test_client_2")
        self.clients.append(client)
        self.assertTrue(client.connect(port=self.test_port), "Client should connect")
        
        # Send various messages
        self.assertTrue(client.send_handshake(), "Should send handshake")
        time.sleep(0.2)
        
        self.assertTrue(client.send_heartbeat(), "Should send heartbeat")
        time.sleep(0.2)
        
        self.assertTrue(client.send_status(battery=85, recording=True), "Should send status")
        time.sleep(0.2)
        
        # Check message processing
        server_stats = self.server.get_stats()
        self.assertGreaterEqual(server_stats["messages_processed"], 3, "Server should process messages")
        
        client_stats = client.get_stats()
        self.assertGreaterEqual(client_stats["messages_received"], 2, "Client should receive responses")
    
    def test_multiple_clients(self):
        """Test multiple client connections."""
        self.assertTrue(self.server.start(), "Server should start")
        time.sleep(0.2)
        
        # Connect multiple clients
        num_clients = 3
        for i in range(num_clients):
            client = SimpleClient(f"test_client_{i}")
            self.clients.append(client)
            
            self.assertTrue(client.connect(port=self.test_port), f"Client {i} should connect")
            self.assertTrue(client.send_handshake(), f"Client {i} should send handshake")
            time.sleep(0.1)
        
        time.sleep(0.5)  # Allow all connections to process
        
        # Check server has all clients
        stats = self.server.get_stats()
        self.assertEqual(stats["connected_clients"], num_clients, f"Should have {num_clients} clients")
    
    def test_broadcast_command(self):
        """Test broadcasting commands to all clients."""
        self.assertTrue(self.server.start(), "Server should start")
        time.sleep(0.2)
        
        # Connect multiple clients
        num_clients = 2
        for i in range(num_clients):
            client = SimpleClient(f"broadcast_client_{i}")
            self.clients.append(client)
            
            self.assertTrue(client.connect(port=self.test_port), f"Client {i} should connect")
            self.assertTrue(client.send_handshake(), f"Client {i} should send handshake")
            time.sleep(0.1)
        
        time.sleep(0.5)
        
        # Send broadcast command
        count = self.server.send_command_to_all("start_recording")
        self.assertEqual(count, num_clients, "Command should be sent to all clients")
        
        time.sleep(0.5)  # Allow message processing
        
        # Verify clients received command
        for client in self.clients:
            stats = client.get_stats()
            self.assertGreaterEqual(stats["messages_received"], 1, "Client should receive broadcast")
    
    def test_connection_resilience(self):
        """Test connection handling when client disconnects."""
        self.assertTrue(self.server.start(), "Server should start")
        time.sleep(0.2)
        
        # Connect client
        client = SimpleClient("resilience_client")
        self.clients.append(client)
        self.assertTrue(client.connect(port=self.test_port), "Client should connect")
        self.assertTrue(client.send_handshake(), "Should send handshake")
        
        time.sleep(0.5)
        stats = self.server.get_stats()
        self.assertEqual(stats["connected_clients"], 1, "Should have one client")
        
        # Disconnect client abruptly
        client.socket.close()
        client.connected = False
        
        time.sleep(1.0)  # Allow server to detect disconnection
        
        # Server should handle disconnection gracefully
        stats = self.server.get_stats()
        self.assertEqual(stats["connected_clients"], 0, "Client should be removed from server")
    
    def test_message_framing(self):
        """Test length-prefixed message framing."""
        # Test message serialization
        message = SimpleNetworkMessage("test", {"data": "hello", "number": 42})
        json_str = message.to_json()
        
        # Verify JSON contains expected data
        data = json.loads(json_str)
        self.assertEqual(data["type"], "test")
        self.assertEqual(data["data"], "hello")
        self.assertEqual(data["number"], 42)
        self.assertIn("timestamp", data)
        
        # Test deserialization
        reconstructed = SimpleNetworkMessage.from_json(json_str)
        self.assertIsNotNone(reconstructed)
        self.assertEqual(reconstructed.type, "test")
        self.assertEqual(reconstructed.payload["data"], "hello")
        self.assertEqual(reconstructed.payload["number"], 42)
    
    def test_performance_basic(self):
        """Test basic performance characteristics."""
        self.assertTrue(self.server.start(), "Server should start")
        time.sleep(0.2)
        
        # Connect client
        client = SimpleClient("perf_client")
        self.clients.append(client)
        self.assertTrue(client.connect(port=self.test_port), "Client should connect")
        self.assertTrue(client.send_handshake(), "Should send handshake")
        
        # Send messages rapidly
        start_time = time.time()
        message_count = 50
        successful = 0
        
        for i in range(message_count):
            if client.send_status(counter=i, battery=90):
                successful += 1
            time.sleep(0.01)  # Small delay to avoid overwhelming
        
        duration = time.time() - start_time
        rate = successful / duration
        
        print(f"Performance: {successful}/{message_count} messages in {duration:.2f}s ({rate:.1f} msg/sec)")
        
        # Verify reasonable performance
        self.assertGreater(rate, 20, "Should handle at least 20 messages per second")
        self.assertGreater(successful, message_count * 0.8, "At least 80% messages should succeed")


def run_simple_tests():
    """Run simple networking tests."""
    print("Running Simple Rock-Solid Networking Tests")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestSimpleNetworking))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print("Simple Networking Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("✅ All simple networking tests passed!")
        print("✅ Basic rock-solid networking concepts validated")
    else:
        print("❌ Some tests failed")
        
        if result.failures:
            print("\nFailures:")
            for test, trace in result.failures:
                print(f"- {test}")
        
        if result.errors:
            print("\nErrors:")
            for test, trace in result.errors:
                print(f"- {test}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_simple_tests()
    exit(0 if success else 1)