"""
File Transfer Module
===================

Handles file transfer from Android devices to PC after recording sessions.
Provides data aggregation, integrity verification, and transfer management.
"""

import json
import logging
import hashlib
import os
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
import base64

logger = logging.getLogger(__name__)


@dataclass
class FileTransferInfo:
    """Information about a file transfer."""
    file_id: str
    device_id: str
    session_id: str
    filename: str
    file_size: int
    checksum: str
    transfer_start: Optional[datetime] = None
    transfer_end: Optional[datetime] = None
    status: str = "pending"  # pending, transferring, completed, failed
    progress_bytes: int = 0
    error_message: Optional[str] = None
    
    def to_dict(self) -> dict:
        data = asdict(self)
        if self.transfer_start:
            data['transfer_start'] = self.transfer_start.isoformat()
        if self.transfer_end:
            data['transfer_end'] = self.transfer_end.isoformat()
        return data


@dataclass
class TransferStats:
    """Statistics for file transfers."""
    total_files: int = 0
    completed_files: int = 0
    failed_files: int = 0
    total_bytes: int = 0
    transferred_bytes: int = 0
    transfer_rate_mbps: float = 0.0
    estimated_time_remaining: float = 0.0
    
    def get_progress_percent(self) -> float:
        if self.total_files == 0:
            return 0.0
        return (self.completed_files / self.total_files) * 100


class FileReceiver:
    """Handles receiving individual files from devices."""
    
    def __init__(self, output_directory: str):
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(exist_ok=True)
        
        self.active_transfers: Dict[str, FileTransferInfo] = {}
        self.file_handles: Dict[str, Any] = {}
        
    def start_file_transfer(self, transfer_info: FileTransferInfo) -> bool:
        """Start receiving a file from a device."""
        try:
            # Create session directory if it doesn't exist
            session_dir = self.output_directory / transfer_info.session_id
            session_dir.mkdir(exist_ok=True)
            
            # Create device subdirectory
            device_dir = session_dir / transfer_info.device_id
            device_dir.mkdir(exist_ok=True)
            
            # Open file for writing
            file_path = device_dir / transfer_info.filename
            file_handle = open(file_path, 'wb')
            
            # Store transfer info and file handle
            transfer_info.transfer_start = datetime.now()
            transfer_info.status = "transferring"
            
            self.active_transfers[transfer_info.file_id] = transfer_info
            self.file_handles[transfer_info.file_id] = file_handle
            
            logger.info(f"Started receiving file {transfer_info.filename} from {transfer_info.device_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting file transfer: {e}")
            return False
    
    def receive_file_chunk(self, file_id: str, chunk_data: bytes, chunk_index: int) -> bool:
        """Receive a chunk of file data."""
        if file_id not in self.active_transfers:
            logger.error(f"No active transfer for file ID: {file_id}")
            return False
        
        try:
            file_handle = self.file_handles[file_id]
            transfer_info = self.active_transfers[file_id]
            
            # Write chunk to file
            file_handle.write(chunk_data)
            file_handle.flush()
            
            # Update progress
            transfer_info.progress_bytes += len(chunk_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Error receiving file chunk: {e}")
            self._fail_transfer(file_id, str(e))
            return False
    
    def complete_file_transfer(self, file_id: str) -> bool:
        """Complete a file transfer and verify integrity."""
        if file_id not in self.active_transfers:
            logger.error(f"No active transfer for file ID: {file_id}")
            return False
        
        try:
            transfer_info = self.active_transfers[file_id]
            file_handle = self.file_handles[file_id]
            
            # Close file
            file_handle.close()
            del self.file_handles[file_id]
            
            # Verify file size and checksum
            file_path = self.output_directory / transfer_info.session_id / transfer_info.device_id / transfer_info.filename
            
            if not self._verify_file_integrity(file_path, transfer_info):
                self._fail_transfer(file_id, "File integrity verification failed")
                return False
            
            # Mark as completed
            transfer_info.transfer_end = datetime.now()
            transfer_info.status = "completed"
            
            logger.info(f"Completed file transfer: {transfer_info.filename} from {transfer_info.device_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error completing file transfer: {e}")
            self._fail_transfer(file_id, str(e))
            return False
    
    def _verify_file_integrity(self, file_path: Path, transfer_info: FileTransferInfo) -> bool:
        """Verify file size and checksum."""
        try:
            # Check file size
            actual_size = file_path.stat().st_size
            if actual_size != transfer_info.file_size:
                logger.error(f"File size mismatch: expected {transfer_info.file_size}, got {actual_size}")
                return False
            
            # Check checksum
            calculated_checksum = self._calculate_file_checksum(file_path)
            if calculated_checksum != transfer_info.checksum:
                logger.error(f"Checksum mismatch: expected {transfer_info.checksum}, got {calculated_checksum}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error verifying file integrity: {e}")
            return False
    
    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of a file."""
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        
        return sha256_hash.hexdigest()
    
    def _fail_transfer(self, file_id: str, error_message: str):
        """Mark a transfer as failed."""
        if file_id in self.active_transfers:
            transfer_info = self.active_transfers[file_id]
            transfer_info.status = "failed"
            transfer_info.error_message = error_message
            transfer_info.transfer_end = datetime.now()
            
            # Close file handle if open
            if file_id in self.file_handles:
                try:
                    self.file_handles[file_id].close()
                except:
                    pass
                del self.file_handles[file_id]
    
    def get_transfer_status(self, file_id: str) -> Optional[dict]:
        """Get status of a specific transfer."""
        if file_id in self.active_transfers:
            return self.active_transfers[file_id].to_dict()
        return None
    
    def cleanup_completed_transfers(self):
        """Clean up completed and failed transfers from memory."""
        completed_ids = [
            file_id for file_id, transfer_info in self.active_transfers.items()
            if transfer_info.status in ("completed", "failed")
        ]
        
        for file_id in completed_ids:
            del self.active_transfers[file_id]


class TransferManager:
    """Manages file transfers from multiple devices."""
    
    def __init__(self, output_directory: str = "transfers"):
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(exist_ok=True)
        
        self.file_receiver = FileReceiver(str(self.output_directory))
        self.network_server = None
        
        # Transfer tracking
        self.session_transfers: Dict[str, List[FileTransferInfo]] = {}
        self.transfer_history: List[FileTransferInfo] = []
        
        # Statistics
        self.transfer_stats = TransferStats()
        
        # Callbacks
        self.transfer_callbacks: List[Callable[[str, dict], None]] = []
    
    def set_network_server(self, server):
        """Set the network server for communication."""
        self.network_server = server
    
    def add_transfer_callback(self, callback: Callable[[str, dict], None]):
        """Add callback for transfer status updates."""
        self.transfer_callbacks.append(callback)
    
    def _notify_callbacks(self, event_type: str, data: dict):
        """Notify all registered callbacks."""
        for callback in self.transfer_callbacks:
            try:
                callback(event_type, data)
            except Exception as e:
                logger.error(f"Error in transfer callback: {e}")
    
    def initiate_session_transfer(self, session_id: str) -> bool:
        """Initiate file transfer for all devices in a session."""
        if not self.network_server:
            logger.error("Network server not configured")
            return False
        
        try:
            # Get connected devices
            connected_devices = self.network_server.get_connected_devices()
            if not connected_devices:
                logger.warning("No devices connected for transfer")
                return False
            
            # Request file list from each device
            transfer_data = {
                'session_id': session_id,
                'request_type': 'file_list'
            }
            
            successful_devices = self.network_server.broadcast_command(
                'transfer_request',
                transfer_data
            )
            
            logger.info(f"Initiated transfer request for session {session_id} to {len(successful_devices)} devices")
            return True
            
        except Exception as e:
            logger.error(f"Error initiating session transfer: {e}")
            return False
    
    def handle_file_list_response(self, device_id: str, session_id: str, file_list: List[dict]) -> bool:
        """Handle file list response from a device."""
        try:
            session_transfers = []
            
            for file_info in file_list:
                # Create transfer info
                transfer_info = FileTransferInfo(
                    file_id=f"{device_id}_{file_info['filename']}_{int(time.time())}",
                    device_id=device_id,
                    session_id=session_id,
                    filename=file_info['filename'],
                    file_size=file_info['file_size'],
                    checksum=file_info['checksum']
                )
                
                session_transfers.append(transfer_info)
            
            # Store session transfers
            if session_id not in self.session_transfers:
                self.session_transfers[session_id] = []
            
            self.session_transfers[session_id].extend(session_transfers)
            
            # Update statistics
            self.transfer_stats.total_files += len(session_transfers)
            self.transfer_stats.total_bytes += sum(t.file_size for t in session_transfers)
            
            # Request transfer start for each file
            self._request_file_transfers(device_id, session_transfers)
            
            logger.info(f"Queued {len(session_transfers)} files for transfer from {device_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error handling file list response: {e}")
            return False
    
    def _request_file_transfers(self, device_id: str, transfers: List[FileTransferInfo]):
        """Request file transfers from a device."""
        for transfer_info in transfers:
            # Start file receiver
            if self.file_receiver.start_file_transfer(transfer_info):
                # Request file transfer from device
                transfer_request = {
                    'file_id': transfer_info.file_id,
                    'filename': transfer_info.filename,
                    'chunk_size': 64 * 1024  # 64KB chunks
                }
                
                success = self.network_server.send_command_to_device(
                    device_id,
                    'transfer_file',
                    transfer_request
                )
                
                if success:
                    self._notify_callbacks('transfer_started', transfer_info.to_dict())
                else:
                    self.file_receiver._fail_transfer(transfer_info.file_id, "Failed to request transfer")
    
    def handle_file_chunk(self, file_id: str, chunk_data_b64: str, chunk_index: int) -> bool:
        """Handle incoming file chunk."""
        try:
            # Decode base64 chunk data
            chunk_data = base64.b64decode(chunk_data_b64)
            
            # Pass to file receiver
            success = self.file_receiver.receive_file_chunk(file_id, chunk_data, chunk_index)
            
            if success:
                # Update statistics
                self.transfer_stats.transferred_bytes += len(chunk_data)
                
                # Notify callbacks
                transfer_status = self.file_receiver.get_transfer_status(file_id)
                if transfer_status:
                    self._notify_callbacks('transfer_progress', transfer_status)
            
            return success
            
        except Exception as e:
            logger.error(f"Error handling file chunk: {e}")
            return False
    
    def handle_file_complete(self, file_id: str) -> bool:
        """Handle file transfer completion."""
        try:
            success = self.file_receiver.complete_file_transfer(file_id)
            
            if success:
                # Update statistics
                self.transfer_stats.completed_files += 1
                
                # Get transfer info and add to history
                transfer_status = self.file_receiver.get_transfer_status(file_id)
                if transfer_status:
                    transfer_info = FileTransferInfo(**transfer_status)
                    self.transfer_history.append(transfer_info)
                    
                    # Notify callbacks
                    self._notify_callbacks('transfer_completed', transfer_status)
            else:
                self.transfer_stats.failed_files += 1
                
                # Notify callbacks
                transfer_status = self.file_receiver.get_transfer_status(file_id)
                if transfer_status:
                    self._notify_callbacks('transfer_failed', transfer_status)
            
            return success
            
        except Exception as e:
            logger.error(f"Error handling file completion: {e}")
            return False
    
    def get_session_transfer_status(self, session_id: str) -> dict:
        """Get transfer status for a session."""
        if session_id not in self.session_transfers:
            return {
                'session_id': session_id,
                'total_files': 0,
                'completed_files': 0,
                'failed_files': 0,
                'progress_percent': 0.0,
                'files': []
            }
        
        transfers = self.session_transfers[session_id]
        completed = sum(1 for t in transfers if t.status == "completed")
        failed = sum(1 for t in transfers if t.status == "failed")
        
        return {
            'session_id': session_id,
            'total_files': len(transfers),
            'completed_files': completed,
            'failed_files': failed,
            'progress_percent': (completed / len(transfers)) * 100 if transfers else 0,
            'files': [t.to_dict() for t in transfers]
        }
    
    def get_overall_statistics(self) -> dict:
        """Get overall transfer statistics."""
        # Calculate transfer rate
        active_transfers = [
            t for transfers in self.session_transfers.values()
            for t in transfers if t.status == "transferring"
        ]
        
        if active_transfers:
            total_time = 0
            total_bytes = 0
            
            for transfer in active_transfers:
                if transfer.transfer_start:
                    duration = (datetime.now() - transfer.transfer_start).total_seconds()
                    if duration > 0:
                        total_time += duration
                        total_bytes += transfer.progress_bytes
            
            if total_time > 0:
                self.transfer_stats.transfer_rate_mbps = (total_bytes / total_time) / (1024 * 1024)
        
        return {
            'total_files': self.transfer_stats.total_files,
            'completed_files': self.transfer_stats.completed_files,
            'failed_files': self.transfer_stats.failed_files,
            'total_bytes': self.transfer_stats.total_bytes,
            'transferred_bytes': self.transfer_stats.transferred_bytes,
            'progress_percent': self.transfer_stats.get_progress_percent(),
            'transfer_rate_mbps': self.transfer_stats.transfer_rate_mbps,
            'active_transfers': len([
                t for transfers in self.session_transfers.values()
                for t in transfers if t.status == "transferring"
            ])
        }
    
    def cleanup_session_transfers(self, session_id: str):
        """Clean up completed transfers for a session."""
        if session_id in self.session_transfers:
            del self.session_transfers[session_id]
        
        self.file_receiver.cleanup_completed_transfers()
    
    def save_transfer_manifest(self, session_id: str) -> bool:
        """Save transfer manifest for a session."""
        try:
            session_dir = self.output_directory / session_id
            manifest_file = session_dir / "transfer_manifest.json"
            
            if session_id in self.session_transfers:
                manifest_data = {
                    'session_id': session_id,
                    'timestamp': datetime.now().isoformat(),
                    'files': [t.to_dict() for t in self.session_transfers[session_id]]
                }
                
                with open(manifest_file, 'w') as f:
                    json.dump(manifest_data, f, indent=2)
                
                logger.info(f"Saved transfer manifest for session {session_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error saving transfer manifest: {e}")
            return False
    
    def prepare_file_transfer(self, device_id: str, file_path: str, session_id: str) -> Dict[str, Any]:
        """Prepare a file transfer request."""
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Calculate file checksum
            checksum = self.calculate_file_checksum(file_path)
            file_size = file_path_obj.stat().st_size
            
            transfer_request = {
                'device_id': device_id,
                'session_id': session_id,
                'filename': file_path_obj.name,
                'file_size': file_size,
                'checksum': checksum,
                'file_path': file_path,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Prepared file transfer for {file_path_obj.name} from {device_id}")
            return transfer_request
            
        except Exception as e:
            logger.error(f"Error preparing file transfer: {e}")
            return {}
    
    def calculate_file_checksum(self, file_path: str) -> str:
        """Calculate SHA-256 checksum for a file."""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            
            checksum = hash_sha256.hexdigest()
            logger.debug(f"Calculated checksum for {file_path}: {checksum}")
            return checksum
            
        except Exception as e:
            logger.error(f"Error calculating checksum for {file_path}: {e}")
            return ""
    
    def get_transfer_status(self, device_id: str, session_id: str) -> Dict[str, Any]:
        """Get transfer status for a device and session."""
        try:
            status = {
                'device_id': device_id,
                'session_id': session_id,
                'has_transfers': False,
                'completed_transfers': 0,
                'total_transfers': 0,
                'total_bytes': 0,
                'transferred_bytes': 0,
                'status': 'unknown'
            }
            
            if session_id in self.session_transfers:
                session_transfers = [
                    t for t in self.session_transfers[session_id] 
                    if t.device_id == device_id
                ]
                
                if session_transfers:
                    status['has_transfers'] = True
                    status['total_transfers'] = len(session_transfers)
                    status['completed_transfers'] = len([
                        t for t in session_transfers 
                        if t.status == 'completed'
                    ])
                    status['total_bytes'] = sum(t.file_size for t in session_transfers)
                    status['transferred_bytes'] = sum(
                        t.progress_bytes for t in session_transfers
                    )
                    
                    if status['completed_transfers'] == status['total_transfers']:
                        status['status'] = 'completed'
                    elif any(t.status == 'transferring' for t in session_transfers):
                        status['status'] = 'transferring'
                    else:
                        status['status'] = 'pending'
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting transfer status: {e}")
            return {'error': str(e)}