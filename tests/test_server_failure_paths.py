import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.append(str(Path(__file__).resolve().parents[1]))

from PythonApp.ntp_time_server import NTPTimeServer
from PythonApp.network.pc_server import PCServer


def test_ntp_server_start_failure(caplog):
    with patch(
        "PythonApp.ntp_time_server.socket.socket", side_effect=OSError("bind fail")
    ):
        server = NTPTimeServer(port=8891)
        with pytest.raises(OSError):
            server.start_server()
        server.thread_pool.shutdown(wait=True)
    assert any("Failed to start NTP time server" in r.message for r in caplog.records)


def test_ntp_server_stop_failure(caplog):
    server = NTPTimeServer(port=8891)
    server.is_running = True
    server.server_socket = Mock()
    server.server_socket.close.side_effect = OSError("close fail")
    with pytest.raises(OSError):
        server.stop_server()
    server.thread_pool.shutdown(wait=True)
    assert any("Error stopping NTP time server" in r.message for r in caplog.records)


def test_pc_server_start_failure(caplog):
    with patch(
        "PythonApp.network.pc_server.socket.socket", side_effect=OSError("bind fail")
    ):
        server = PCServer(port=9001)
        with pytest.raises(OSError):
            server.start()
        server.thread_pool.shutdown(wait=True)
    assert any("Failed to start PC server" in r.message for r in caplog.records)


def test_pc_server_stop_failure(caplog):
    server = PCServer(port=9001)
    server.server_socket = Mock()
    server.server_socket.close.side_effect = OSError("close fail")
    with pytest.raises(OSError):
        server.stop()
    server.thread_pool.shutdown(wait=True)
    assert any("Error stopping PC server" in r.message for r in caplog.records)
