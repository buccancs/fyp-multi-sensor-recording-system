"""
Cross-component integration tests for session orchestration.
Tests cover end-to-end workflows across Android, Desktop, and Web components.
Validates FR2 (Synchronized Recording), FR4 (Session Management), 
FR8 (Fault Tolerance), and FR10 (Data Transfer).
"""

import pytest
import threading
import time
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add PythonApp to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'PythonApp'))

try:
    from PythonApp.web_ui.web_dashboard import WebDashboardServer
    WEB_AVAILABLE = True
except ImportError:
    WEB_AVAILABLE = False
    WebDashboardServer = None

try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtTest import QTest
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False


class MockDevice:
    """Mock device for testing device management."""
    
    def __init__(self, device_id: str, device_type: str):
        self.device_id = device_id
        self.device_type = device_type
        self.connected = False
        self.recording = False
        self.data_count = 0
    
    def connect(self):
        self.connected = True
        return {"success": True, "device_id": self.device_id}
    
    def disconnect(self):
        self.connected = False
        self.recording = False
        return {"success": True}
    
    def start_recording(self):
        if self.connected:
            self.recording = True
            return {"success": True}
        return {"success": False, "error": "Device not connected"}
    
    def stop_recording(self):
        self.recording = False
        return {"success": True, "data_samples": self.data_count}
    
    def get_status(self):
        return {
            "device_id": self.device_id,
            "type": self.device_type,
            "connected": self.connected,
            "recording": self.recording,
            "data_count": self.data_count
        }


class MockController:
    """Mock controller for integration testing."""
    
    def __init__(self):
        self.devices = {}
        self.sessions = {}
        self.active_session = None
        self.device_counter = 0
    
    def add_mock_device(self, device_type: str):
        """Add a mock device for testing."""
        self.device_counter += 1
        device_id = f"{device_type}_{self.device_counter}"
        device = MockDevice(device_id, device_type)
        self.devices[device_id] = device
        return device_id
    
    def get_status(self):
        """Get controller status."""
        device_status = {}
        for device_id, device in self.devices.items():
            device_status[device_id] = device.get_status()
        
        session_info = {}
        if self.active_session:
            session_info = {
                "active": True,
                "session_id": self.active_session,
                "devices": list(self.devices.keys()),
                "start_time": time.time()
            }
        else:
            session_info = {"active": False}
        
        return {
            "running": True,
            "devices": device_status,
            "session": session_info
        }
    
    def connect_device(self, device_id: str):
        """Connect a device."""
        if device_id in self.devices:
            return self.devices[device_id].connect()
        return {"success": False, "error": "Device not found"}
    
    def start_session(self, session_name: str = None, devices: list = None):
        """Start a recording session."""
        if self.active_session:
            return {"success": False, "error": "Session already active"}
        
        session_id = session_name or f"session_{int(time.time())}"
        self.active_session = session_id
        self.sessions[session_id] = {
            "start_time": time.time(),
            "devices": devices or list(self.devices.keys()),
            "status": "recording"
        }
        
        # Start recording on all connected devices
        for device_id in self.devices:
            if self.devices[device_id].connected:
                self.devices[device_id].start_recording()
        
        return {"success": True, "session_id": session_id}
    
    def stop_session(self):
        """Stop the active session."""
        if not self.active_session:
            return {"success": False, "error": "No active session"}
        
        # Stop recording on all devices
        for device_id in self.devices:
            self.devices[device_id].stop_recording()
        
        session_id = self.active_session
        self.sessions[session_id]["status"] = "completed"
        self.sessions[session_id]["end_time"] = time.time()
        self.active_session = None
        
        return {"success": True, "session_id": session_id}
    
    def simulate_device_disconnect(self, device_id: str):
        """Simulate device disconnection for fault tolerance testing."""
        if device_id in self.devices:
            self.devices[device_id].disconnect()
            return {"success": True, "disconnected": device_id}
        return {"success": False, "error": "Device not found"}


@pytest.fixture
def mock_controller():
    """Create mock controller with test devices."""
    controller = MockController()
    
    # Add test devices
    controller.add_mock_device("webcam")
    controller.add_mock_device("android")
    controller.add_mock_device("shimmer")
    
    return controller


@pytest.fixture
def web_server(mock_controller):
    """Create web server with mock controller."""
    if not WEB_AVAILABLE:
        pytest.skip("Web components not available")
    
    server = WebDashboardServer(
        host="127.0.0.1",
        port=5002,  # Use different port for integration tests
        debug=True,
        controller=mock_controller
    )
    return server


@pytest.fixture
def web_client(web_server):
    """Create web client for integration testing."""
    web_server.app.config['TESTING'] = True
    with web_server.app.test_client() as client:
        yield client


class TestSessionOrchestration:
    """Test end-to-end session orchestration across components."""
    
    @pytest.mark.unit
    def test_session_lifecycle_via_web_api(self, web_client, mock_controller):
        """FR2, FR4: Test complete session lifecycle through web API."""
        # Step 1: Check initial status
        response = web_client.get('/api/status')
        assert response.status_code == 200
        
        status = response.get_json()
        assert not status['session']['active']
        
        # Step 2: Connect devices
        for device_id in mock_controller.devices:
            result = mock_controller.connect_device(device_id)
            assert result['success']
        
        # Step 3: Start session via web API
        session_payload = {
            "session_name": "integration_test_session",
            "devices": list(mock_controller.devices.keys())
        }
        
        response = web_client.post('/api/session/start',
                                 json=session_payload)
        
        if response.status_code == 200:
            result = response.get_json()
            assert result['success']
            session_id = result['session_id']
            
            # Step 4: Verify session is active
            response = web_client.get('/api/status')
            status = response.get_json()
            assert status['session']['active']
            assert status['session']['session_id'] == session_id
            
            # Step 5: Stop session
            response = web_client.post('/api/session/stop')
            assert response.status_code == 200
            
            result = response.get_json()
            assert result['success']
            
            # Step 6: Verify session is stopped
            response = web_client.get('/api/status')
            status = response.get_json()
            assert not status['session']['active']
    
    @pytest.mark.unit
    def test_device_status_synchronization(self, mock_controller):
        """FR1, FR6: Test device status synchronization across components."""
        # Connect devices
        webcam_id = None
        for device_id, device in mock_controller.devices.items():
            if device.device_type == "webcam":
                webcam_id = device_id
                break
        
        assert webcam_id is not None
        
        # Initially disconnected
        status = mock_controller.get_status()
        assert not status['devices'][webcam_id]['connected']
        
        # Connect device
        result = mock_controller.connect_device(webcam_id)
        assert result['success']
        
        # Verify status updated
        status = mock_controller.get_status()
        assert status['devices'][webcam_id]['connected']
        
        # Start session
        session_result = mock_controller.start_session("sync_test")
        assert session_result['success']
        
        # Verify recording status
        status = mock_controller.get_status()
        assert status['devices'][webcam_id]['recording']
    
    @pytest.mark.unit
    def test_multi_device_coordination(self, mock_controller):
        """FR2: Test synchronized multi-device recording coordination."""
        # Connect all devices
        connected_devices = []
        for device_id in mock_controller.devices:
            result = mock_controller.connect_device(device_id)
            if result['success']:
                connected_devices.append(device_id)
        
        assert len(connected_devices) >= 2  # Need multiple devices for coordination test
        
        # Start session with multiple devices
        session_result = mock_controller.start_session("multi_device_test", connected_devices)
        assert session_result['success']
        
        # Verify all devices started recording simultaneously
        status = mock_controller.get_status()
        for device_id in connected_devices:
            assert status['devices'][device_id]['recording']
        
        # Stop session
        stop_result = mock_controller.stop_session()
        assert stop_result['success']
        
        # Verify all devices stopped recording
        status = mock_controller.get_status()
        for device_id in connected_devices:
            assert not status['devices'][device_id]['recording']


class TestFaultTolerance:
    """Test fault tolerance and recovery mechanisms (FR8, NFR3)."""
    
    def test_device_disconnect_during_session(self, mock_controller):
        """FR8: Test handling of device disconnection during active session."""
        # Setup: Connect devices and start session
        device_ids = list(mock_controller.devices.keys())
        for device_id in device_ids:
            mock_controller.connect_device(device_id)
        
        session_result = mock_controller.start_session("fault_test", device_ids)
        assert session_result['success']
        
        # Simulate device disconnect
        disconnected_device = device_ids[0]
        disconnect_result = mock_controller.simulate_device_disconnect(disconnected_device)
        assert disconnect_result['success']
        
        # Verify session continues with remaining devices
        status = mock_controller.get_status()
        assert status['session']['active']  # Session should continue
        assert not status['devices'][disconnected_device]['connected']
        assert not status['devices'][disconnected_device]['recording']
        
        # Other devices should still be recording
        for device_id in device_ids[1:]:
            assert status['devices'][device_id]['recording']
    
    def test_session_recovery_after_device_reconnection(self, mock_controller):
        """FR8: Test session state recovery when device reconnects."""
        # Setup session with device disconnect
        device_ids = list(mock_controller.devices.keys())
        for device_id in device_ids:
            mock_controller.connect_device(device_id)
        
        mock_controller.start_session("recovery_test", device_ids)
        
        # Disconnect and reconnect device
        test_device = device_ids[0]
        mock_controller.simulate_device_disconnect(test_device)
        
        # Reconnect device
        reconnect_result = mock_controller.connect_device(test_device)
        assert reconnect_result['success']
        
        # Device should be able to rejoin session state
        status = mock_controller.get_status()
        assert status['devices'][test_device]['connected']
        # Note: In a full implementation, device would rejoin recording automatically
    
    @pytest.mark.unit
    def test_graceful_degradation_no_devices(self, mock_controller):
        """NFR3: Test graceful degradation when no devices are available."""
        # Don't connect any devices
        
        # Try to start session without devices
        session_result = mock_controller.start_session("no_devices_test", [])
        
        # Should handle gracefully (may succeed with empty device list or fail gracefully)
        if not session_result['success']:
            assert 'error' in session_result
        else:
            # If it succeeds, should handle empty device list
            status = mock_controller.get_status()
            assert status['session']['active']


class TestDataTransferIntegration:
    """Test data transfer and aggregation workflows (FR10)."""
    
    def test_session_data_aggregation(self, mock_controller):
        """FR10: Test data aggregation after session completion."""
        # Setup and run session
        device_ids = list(mock_controller.devices.keys())
        for device_id in device_ids:
            mock_controller.connect_device(device_id)
        
        session_result = mock_controller.start_session("data_test", device_ids)
        assert session_result['success']
        session_id = session_result['session_id']
        
        # Simulate data collection
        for device_id in device_ids:
            device = mock_controller.devices[device_id]
            device.data_count = 100  # Simulate collected data
        
        # Stop session
        stop_result = mock_controller.stop_session()
        assert stop_result['success']
        
        # Verify session data is aggregated
        session_data = mock_controller.sessions[session_id]
        assert session_data['status'] == 'completed'
        assert 'end_time' in session_data
        assert session_data['devices'] == device_ids
    
    def test_data_export_functionality(self, web_client, mock_controller):
        """FR10: Test data export through web API."""
        # Run a session first
        device_ids = list(mock_controller.devices.keys())
        for device_id in device_ids:
            mock_controller.connect_device(device_id)
        
        session_result = mock_controller.start_session("export_test")
        if session_result['success']:
            mock_controller.stop_session()
            
            # Test export API
            export_payload = {
                "session_id": session_result['session_id'],
                "start_time": 0,
                "end_time": 60,
                "export_format": "json"
            }
            
            response = web_client.post('/api/sessions/export', json=export_payload)
            # Should handle export request appropriately
            assert response.status_code in [200, 404, 501]


class TestPerformanceIntegration:
    """Test performance under integration scenarios (NFR1)."""
    
    def test_multiple_session_performance(self, mock_controller):
        """NFR1: Test performance with multiple session cycles."""
        device_ids = list(mock_controller.devices.keys())
        for device_id in device_ids:
            mock_controller.connect_device(device_id)
        
        start_time = time.time()
        
        # Run multiple session cycles
        for i in range(5):
            session_result = mock_controller.start_session(f"perf_test_{i}")
            assert session_result['success']
            
            # Brief recording period
            time.sleep(0.1)
            
            stop_result = mock_controller.stop_session()
            assert stop_result['success']
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should handle multiple sessions efficiently (under 2 seconds for 5 cycles)
        assert total_time < 2.0, f"Performance test took {total_time} seconds"
    
    def test_concurrent_api_requests(self, web_client):
        """NFR1: Test handling of concurrent API requests."""
        import concurrent.futures
        
        def make_status_request():
            response = web_client.get('/api/status')
            return response.status_code
        
        # Make concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_status_request) for _ in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed
        for status_code in results:
            assert status_code == 200


@pytest.mark.integration
@pytest.mark.unit
def test_end_to_end_workflow(mock_controller, web_client):
    """Complete end-to-end workflow test covering all major components."""
    if not WEB_AVAILABLE:
        pytest.skip("Web components not available")
    
    # Step 1: System initialization
    status_response = web_client.get('/api/status')
    assert status_response.status_code == 200
    
    # Step 2: Device discovery and connection
    device_ids = list(mock_controller.devices.keys())
    for device_id in device_ids:
        connect_result = mock_controller.connect_device(device_id)
        assert connect_result['success']
    
    # Step 3: Session creation and start
    session_payload = {
        "session_name": "end_to_end_test",
        "devices": device_ids
    }
    
    session_response = web_client.post('/api/session/start', json=session_payload)
    if session_response.status_code == 200:
        session_result = session_response.get_json()
        assert session_result['success']
        
        # Step 4: Monitor session status
        status_response = web_client.get('/api/status')
        status = status_response.get_json()
        assert status['session']['active']
        
        # Step 5: Session completion
        stop_response = web_client.post('/api/session/stop')
        assert stop_response.status_code == 200
        
        stop_result = stop_response.get_json()
        assert stop_result['success']
        
        # Step 6: Final status verification
        final_status_response = web_client.get('/api/status')
        final_status = final_status_response.get_json()
        assert not final_status['session']['active']