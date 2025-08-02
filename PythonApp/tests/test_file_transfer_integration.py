"""
Integration tests for File Transfer functionality - Milestone 3.6

Tests the complete file transfer system including:
- PC-side file receiving logic
- Message processing for file transfer types
- Session directory management
- Multi-device file collection
- Error handling and validation
"""

import base64
import os
import shutil
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

# Add the src directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from network.device_server import JsonSocketServer, RemoteDevice


class TestFileTransferIntegration(unittest.TestCase):
    """Test file transfer functionality integration"""

    def setUp(self):
        """Set up test environment"""
        self.server = JsonSocketServer(host="localhost", port=9001)
        self.test_dir = tempfile.mkdtemp()
        self.mock_socket = Mock()
        self.device_id = "test_device_123"
        self.session_id = "test_session_456"

        # Create test device
        self.test_device = RemoteDevice(
            device_id=self.device_id,
            capabilities=["rgb_video", "thermal", "shimmer"],
            client_socket=self.mock_socket,
        )
        self.server.devices[self.device_id] = self.test_device

        # Create test file content
        self.test_file_content = b"Test file content for transfer validation. " * 100
        self.test_file_name = "test_video.mp4"

    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        self.server.cleanup()

    def test_file_info_message_processing(self):
        """Test processing of file_info message"""
        # Arrange
        file_info_message = {
            "type": "file_info",
            "name": self.test_file_name,
            "size": len(self.test_file_content),
        }

        with patch.object(
            self.server, "get_session_directory", return_value=self.test_dir
        ):
            # Act
            self.server.process_json_message(
                self.mock_socket, "test_client", file_info_message
            )

            # Assert
            self.assertTrue(hasattr(self.test_device, "file_transfer_state"))
            self.assertIsNotNone(self.test_device.file_transfer_state)
            self.assertEqual(
                self.test_device.file_transfer_state["filename"], self.test_file_name
            )
            self.assertEqual(
                self.test_device.file_transfer_state["expected_size"],
                len(self.test_file_content),
            )
            self.assertEqual(self.test_device.file_transfer_state["received_bytes"], 0)

    def test_file_chunk_message_processing(self):
        """Test processing of file_chunk messages"""
        # Arrange - Initialize file transfer state
        self.test_device.file_transfer_state = {
            "filename": self.test_file_name,
            "expected_size": len(self.test_file_content),
            "received_bytes": 0,
            "file_handle": None,
            "chunks_received": 0,
        }

        # Create temporary file for writing
        test_file_path = os.path.join(
            self.test_dir, f"{self.device_id}_{self.test_file_name}"
        )
        self.test_device.file_transfer_state["file_handle"] = open(test_file_path, "wb")

        # Create test chunk
        chunk_data = self.test_file_content[:1000]  # First 1000 bytes
        base64_chunk = base64.b64encode(chunk_data).decode("ascii")

        file_chunk_message = {"type": "file_chunk", "seq": 1, "data": base64_chunk}

        try:
            # Act
            self.server.process_json_message(
                self.mock_socket, "test_client", file_chunk_message
            )

            # Assert
            self.assertEqual(
                self.test_device.file_transfer_state["received_bytes"], len(chunk_data)
            )
            self.assertEqual(self.test_device.file_transfer_state["chunks_received"], 1)

            # Verify file content
            self.test_device.file_transfer_state["file_handle"].close()
            with open(test_file_path, "rb") as f:
                written_content = f.read()
            self.assertEqual(written_content, chunk_data)

        finally:
            if self.test_device.file_transfer_state["file_handle"]:
                self.test_device.file_transfer_state["file_handle"].close()

    def test_file_end_message_processing(self):
        """Test processing of file_end message"""
        # Arrange - Set up completed transfer state
        test_file_path = os.path.join(
            self.test_dir, f"{self.device_id}_{self.test_file_name}"
        )

        self.test_device.file_transfer_state = {
            "filename": self.test_file_name,
            "expected_size": len(self.test_file_content),
            "received_bytes": len(self.test_file_content),  # Complete transfer
            "file_handle": open(test_file_path, "wb"),
            "chunks_received": 5,
        }

        # Write test content to file
        self.test_device.file_transfer_state["file_handle"].write(
            self.test_file_content
        )

        file_end_message = {"type": "file_end", "name": self.test_file_name}

        with patch.object(self.server, "send_command") as mock_send:
            # Act
            self.server.process_json_message(
                self.mock_socket, "test_client", file_end_message
            )

            # Assert
            self.assertIsNone(self.test_device.file_transfer_state)

            # Verify acknowledgment was sent
            mock_send.assert_called_once()
            call_args = mock_send.call_args[0]
            self.assertEqual(call_args[0], self.device_id)
            self.assertEqual(call_args[1]["type"], "file_received")
            self.assertEqual(call_args[1]["status"], "ok")

    def test_file_end_message_size_mismatch(self):
        """Test file_end message with size mismatch"""
        # Arrange - Set up transfer with size mismatch
        test_file_path = os.path.join(
            self.test_dir, f"{self.device_id}_{self.test_file_name}"
        )

        self.test_device.file_transfer_state = {
            "filename": self.test_file_name,
            "expected_size": len(self.test_file_content),
            "received_bytes": len(self.test_file_content) - 100,  # Missing bytes
            "file_handle": open(test_file_path, "wb"),
            "chunks_received": 4,
        }

        file_end_message = {"type": "file_end", "name": self.test_file_name}

        with patch.object(self.server, "send_command") as mock_send:
            # Act
            self.server.process_json_message(
                self.mock_socket, "test_client", file_end_message
            )

            # Assert
            self.assertIsNone(self.test_device.file_transfer_state)

            # Verify error acknowledgment was sent
            mock_send.assert_called_once()
            call_args = mock_send.call_args[0]
            self.assertEqual(call_args[1]["type"], "file_received")
            self.assertEqual(call_args[1]["status"], "error")

    def test_request_file_from_device(self):
        """Test requesting a file from a specific device"""
        # Arrange
        test_filepath = "/storage/test/file.mp4"

        with patch.object(self.server, "send_command", return_value=True) as mock_send:
            # Act
            result = self.server.request_file_from_device(
                self.device_id, test_filepath, "video"
            )

            # Assert
            self.assertTrue(result)
            mock_send.assert_called_once_with(
                self.device_id,
                {"type": "send_file", "filepath": test_filepath, "filetype": "video"},
            )

    def test_request_file_from_nonexistent_device(self):
        """Test requesting a file from a non-existent device"""
        # Act
        result = self.server.request_file_from_device(
            "nonexistent_device", "/test/file.mp4"
        )

        # Assert
        self.assertFalse(result)

    def test_get_expected_files_for_device(self):
        """Test getting expected files based on device capabilities"""
        # Act
        expected_files = self.server.get_expected_files_for_device(
            self.device_id, self.session_id, ["rgb_video", "thermal", "shimmer"]
        )

        # Assert
        self.assertEqual(len(expected_files), 3)

        # Check that all expected file types are present
        file_types = [os.path.basename(f) for f in expected_files]
        self.assertTrue(any("rgb.mp4" in f for f in file_types))
        self.assertTrue(any("thermal.mp4" in f for f in file_types))
        self.assertTrue(any("sensors.csv" in f for f in file_types))

        # Check that session and device IDs are in paths
        for filepath in expected_files:
            self.assertIn(self.session_id, filepath)
            self.assertIn(self.device_id, filepath)

    def test_get_expected_files_partial_capabilities(self):
        """Test getting expected files with partial capabilities"""
        # Act
        expected_files = self.server.get_expected_files_for_device(
            self.device_id, self.session_id, ["rgb_video"]  # Only RGB video
        )

        # Assert
        self.assertEqual(len(expected_files), 1)
        self.assertTrue(expected_files[0].endswith("rgb.mp4"))

    def test_request_all_session_files(self):
        """Test requesting all session files from all devices"""
        # Arrange - Add another device
        device2_id = "test_device_789"
        device2 = RemoteDevice(
            device_id=device2_id, capabilities=["thermal"], client_socket=Mock()
        )
        self.server.devices[device2_id] = device2

        with patch.object(
            self.server, "request_file_from_device", return_value=True
        ) as mock_request:
            # Act
            result = self.server.request_all_session_files(self.session_id)

            # Assert
            self.assertGreater(result, 0)  # Should have made some requests

            # Verify requests were made for both devices
            call_count = mock_request.call_count
            self.assertGreater(call_count, 0)

            # Check that requests were made for expected files
            calls = mock_request.call_args_list
            device_ids_called = set()
            for call in calls:
                device_ids_called.add(call[0][0])  # First argument is device_id

            self.assertIn(self.device_id, device_ids_called)
            self.assertIn(device2_id, device_ids_called)

    @patch("os.makedirs")
    @patch("os.getcwd")
    def test_get_session_directory(self, mock_getcwd, mock_makedirs):
        """Test session directory creation"""
        # Arrange
        mock_getcwd.return_value = "/test/working/dir"

        # Act
        session_dir = self.server.get_session_directory()

        # Assert
        self.assertIsNotNone(session_dir)
        self.assertTrue(session_dir.startswith("/test/working/dir/sessions/"))
        self.assertIn("session_", session_dir)

        # Verify directories were created
        mock_makedirs.assert_called()

    def test_complete_file_transfer_workflow(self):
        """Test complete file transfer workflow"""
        # Arrange
        with patch.object(
            self.server, "get_session_directory", return_value=self.test_dir
        ):
            # Step 1: Process file_info
            file_info_message = {
                "type": "file_info",
                "name": self.test_file_name,
                "size": len(self.test_file_content),
            }

            self.server.process_json_message(
                self.mock_socket, "test_client", file_info_message
            )

            # Step 2: Process file chunks
            chunk_size = 1000
            chunks = [
                self.test_file_content[i : i + chunk_size]
                for i in range(0, len(self.test_file_content), chunk_size)
            ]

            for seq, chunk in enumerate(chunks, 1):
                base64_chunk = base64.b64encode(chunk).decode("ascii")
                file_chunk_message = {
                    "type": "file_chunk",
                    "seq": seq,
                    "data": base64_chunk,
                }

                self.server.process_json_message(
                    self.mock_socket, "test_client", file_chunk_message
                )

            # Step 3: Process file_end
            file_end_message = {"type": "file_end", "name": self.test_file_name}

            with patch.object(self.server, "send_command") as mock_send:
                self.server.process_json_message(
                    self.mock_socket, "test_client", file_end_message
                )

                # Assert
                # Verify file was created and has correct content
                test_file_path = os.path.join(
                    self.test_dir, f"{self.device_id}_{self.test_file_name}"
                )
                self.assertTrue(os.path.exists(test_file_path))

                with open(test_file_path, "rb") as f:
                    received_content = f.read()

                self.assertEqual(received_content, self.test_file_content)

                # Verify success acknowledgment was sent
                mock_send.assert_called_once()
                call_args = mock_send.call_args[0]
                self.assertEqual(call_args[1]["status"], "ok")

    def test_multiple_concurrent_transfers(self):
        """Test handling multiple concurrent file transfers"""
        # Arrange - Create multiple devices
        devices = []
        for i in range(3):
            device_id = f"device_{i}"
            device = RemoteDevice(
                device_id=device_id, capabilities=["rgb_video"], client_socket=Mock()
            )
            self.server.devices[device_id] = device
            devices.append((device_id, device))

        with patch.object(
            self.server, "get_session_directory", return_value=self.test_dir
        ):
            # Act - Start file transfers for all devices
            for device_id, device in devices:
                file_info_message = {
                    "type": "file_info",
                    "name": f"video_{device_id}.mp4",
                    "size": 1000,
                }

                self.server.process_json_message(
                    device.client_socket, f"client_{device_id}", file_info_message
                )

            # Assert - Verify all devices have transfer state
            for device_id, device in devices:
                self.assertTrue(hasattr(device, "file_transfer_state"))
                self.assertIsNotNone(device.file_transfer_state)
                self.assertEqual(
                    device.file_transfer_state["filename"], f"video_{device_id}.mp4"
                )


if __name__ == "__main__":
    # Configure logging for tests
    import logging

    logging.basicConfig(level=logging.DEBUG)

    # Run tests
    unittest.main(verbosity=2)
