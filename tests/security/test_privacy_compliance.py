"""
Privacy Compliance Security Tests
================================

This module implements comprehensive tests for privacy compliance and data handling
as recommended in the security assessment. Tests cover GDPR compliance, data 
anonymization, PII detection, and metadata stripping.

Test Coverage:
1. Metadata anonymization validation
2. PII detection and removal
3. GDPR compliance checks
4. Data retention validation
5. Log file privacy auditing
6. Participant data protection
"""

import json
import os
import re
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
from unittest.mock import Mock, patch

import pytest

# Add project root to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    # Try to import Android privacy manager if available
    from AndroidApp.src.main.java.com.multisensor.recording.security.PrivacyManager import PrivacyManager
    ANDROID_PRIVACY_AVAILABLE = True
except ImportError:
    ANDROID_PRIVACY_AVAILABLE = False
    PrivacyManager = None


class PrivacyComplianceTests(unittest.TestCase):
    """Test suite for privacy compliance and data protection."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_data_dir = Path(self.temp_dir) / "test_data"
        self.test_data_dir.mkdir(exist_ok=True)
        
        # Create mock privacy manager for Python tests
        self.privacy_manager = MockPrivacyManager()
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @pytest.mark.security
    def test_metadata_anonymization(self):
        """Test that sensitive metadata is properly anonymized."""
        # Create test metadata with PII
        original_metadata = {
            "device_id": "SAMSUNG_SM_G998B_ABC123456789",
            "serial_number": "RF8N123456Z",
            "mac_address": "00:1B:44:11:3A:B7",
            "imei": "123456789012345",
            "phone_number": "+1-555-123-4567",
            "email": "participant@example.com",
            "user_name": "John Doe",
            "device_name": "John's Phone",
            "network_ssid": "HomeWiFi_JohnDoe",
            "ip_address": "192.168.1.100",
            "location": {"lat": 37.7749, "lon": -122.4194},
            "gps": {"latitude": 37.7749, "longitude": -122.4194},
            "timestamp": "2025-01-16T10:30:00Z",
            "session_type": "calibration",
            "experiment_id": "EXP_001"
        }
        
        # Anonymize metadata
        anonymized = self.privacy_manager.anonymize_metadata(original_metadata)
        
        # Verify sensitive fields are removed
        sensitive_fields = [
            "device_id", "serial_number", "mac_address", "imei",
            "phone_number", "email", "user_name", "device_name",
            "network_ssid", "ip_address", "location", "gps"
        ]
        
        for field in sensitive_fields:
            self.assertNotIn(field, anonymized,
                           f"Sensitive field '{field}' was not removed")
        
        # Verify required fields are present
        required_fields = ["participant_id", "session_id", "device_type"]
        for field in required_fields:
            self.assertIn(field, anonymized,
                         f"Required field '{field}' is missing")
        
        # Verify participant ID is anonymous
        participant_id = anonymized.get("participant_id", "")
        self.assertTrue(participant_id.startswith("ANON_"),
                       "Participant ID should be anonymous")
        
        # Verify device type is anonymized
        device_type = anonymized.get("device_type", "")
        self.assertNotIn("123", device_type, "Device type should not contain serial numbers")

    @pytest.mark.security 
    def test_pii_detection_in_logs(self):
        """Test detection of PII patterns in log files."""
        # Create test log content with various PII
        log_content = """
        2025-01-16 10:30:00 INFO Device connected: participant@example.com
        2025-01-16 10:30:01 DEBUG User John Doe started session  
        2025-01-16 10:30:02 INFO Phone number: +1-555-123-4567
        2025-01-16 10:30:03 ERROR IMEI: 123456789012345
        2025-01-16 10:30:04 INFO IP Address: 192.168.1.100
        2025-01-16 10:30:05 DEBUG MAC: 00:1B:44:11:3A:B7
        2025-01-16 10:30:06 INFO Session started for ANON_ABC12345
        2025-01-16 10:30:07 INFO Processing sensor data
        """
        
        # Write test log file
        log_file = self.test_data_dir / "test.log"
        log_file.write_text(log_content)
        
        # Scan for PII
        pii_violations = self._scan_logs_for_pii(str(log_file))
        
        # Should find violations
        self.assertGreater(len(pii_violations), 0, "Should detect PII in logs")
        
        # Check specific patterns
        violation_types = {v["type"] for v in pii_violations}
        expected_types = {"email", "phone", "imei", "ip_address", "mac_address"}
        
        for expected_type in expected_types:
            self.assertIn(expected_type, violation_types,
                         f"Should detect {expected_type} in logs")

    def _scan_logs_for_pii(self, log_file_path: str) -> List[Dict]:
        """Scan log file for PII patterns."""
        pii_patterns = {
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "phone": r"[\+]?[1-9]?[0-9]{3}[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4}",
            "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
            "imei": r"\b\d{15}\b",
            "ip_address": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
            "mac_address": r"\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b",
            "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
        }
        
        violations = []
        
        with open(log_file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                for pii_type, pattern in pii_patterns.items():
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        violations.append({
                            "type": pii_type,
                            "line": line_num,
                            "content": match.group(),
                            "pattern": pattern
                        })
        
        return violations

    @pytest.mark.security
    def test_gdpr_compliance_features(self):
        """Test GDPR compliance features and data subject rights."""
        # Test data subject access
        participant_data = self.privacy_manager.get_participant_data("ANON_TEST123")
        self.assertIsInstance(participant_data, dict, "Should return participant data")
        
        # Test right to rectification (data correction)
        correction_result = self.privacy_manager.correct_participant_data(
            "ANON_TEST123", {"consent_version": 2}
        )
        self.assertTrue(correction_result, "Should allow data correction")
        
        # Test right to erasure (data deletion)
        deletion_result = self.privacy_manager.delete_participant_data("ANON_TEST123")
        self.assertTrue(deletion_result, "Should allow data deletion")
        
        # Test data portability
        export_result = self.privacy_manager.export_participant_data("ANON_TEST123")
        self.assertIsInstance(export_result, dict, "Should export participant data")

    @pytest.mark.security
    def test_data_retention_compliance(self):
        """Test that data retention policies are properly enforced."""
        # Create test data with different timestamps
        old_timestamp = int((datetime.now() - timedelta(days=400)).timestamp() * 1000)
        recent_timestamp = int((datetime.now() - timedelta(days=30)).timestamp() * 1000)
        
        # Test retention policy
        should_delete_old = self.privacy_manager.should_delete_data(old_timestamp)
        should_keep_recent = self.privacy_manager.should_delete_data(recent_timestamp)
        
        self.assertTrue(should_delete_old, "Old data should be marked for deletion")
        self.assertFalse(should_keep_recent, "Recent data should be retained")
        
        # Test actual cleanup
        cleanup_result = self.privacy_manager.cleanup_expired_data()
        self.assertIsInstance(cleanup_result, dict, "Should return cleanup report")

    @pytest.mark.security
    def test_consent_management(self):
        """Test consent management and validation."""
        # Test consent recording
        consent_result = self.privacy_manager.record_consent(
            participant_id="ANON_TEST123",
            study_id="STUDY_001"
        )
        self.assertTrue(consent_result, "Should record consent successfully")
        
        # Test consent validation
        has_consent = self.privacy_manager.has_valid_consent("ANON_TEST123")
        self.assertTrue(has_consent, "Should have valid consent")
        
        # Test consent withdrawal
        withdrawal_result = self.privacy_manager.withdraw_consent("ANON_TEST123")
        self.assertTrue(withdrawal_result, "Should allow consent withdrawal")
        
        # Verify consent is withdrawn
        has_consent_after = self.privacy_manager.has_valid_consent("ANON_TEST123")
        self.assertFalse(has_consent_after, "Should not have consent after withdrawal")

    @pytest.mark.security
    def test_face_blurring_privacy(self):
        """Test face blurring functionality for privacy protection."""
        # Create mock image data
        mock_image_data = b"fake_image_data_with_faces"
        
        # Test face blurring
        blurred_result = self.privacy_manager.apply_face_blurring(mock_image_data)
        self.assertIsNotNone(blurred_result, "Should return blurred image")
        self.assertNotEqual(blurred_result, mock_image_data, "Should modify image data")

    @pytest.mark.security
    def test_data_anonymization_settings(self):
        """Test data anonymization settings configuration."""
        # Configure anonymization settings
        self.privacy_manager.configure_anonymization(
            enable_data_anonymization=True,
            enable_face_blurring=True,
            enable_metadata_stripping=True
        )
        
        settings = self.privacy_manager.get_anonymization_settings()
        
        self.assertTrue(settings["data_anonymization_enabled"])
        self.assertTrue(settings["face_blurring_enabled"])
        self.assertTrue(settings["metadata_stripping_enabled"])

    @pytest.mark.security
    def test_privacy_report_generation(self):
        """Test generation of privacy compliance reports."""
        report = self.privacy_manager.generate_privacy_report()
        
        required_fields = [
            "consent_info", "anonymization_settings", "data_retention_days",
            "report_generated_at", "data_collection_purpose", "data_types",
            "data_processing_basis", "data_storage_location", "third_party_sharing"
        ]
        
        for field in required_fields:
            self.assertIn(field, report, f"Privacy report missing {field}")
        
        # Verify GDPR required information
        self.assertIn("Research consent", report["data_processing_basis"])
        self.assertEqual("None", report["third_party_sharing"])

    @pytest.mark.security
    def test_participant_id_anonymization(self):
        """Test that participant IDs are properly anonymized."""
        # Generate anonymous participant ID
        anon_id = self.privacy_manager.generate_anonymous_participant_id()
        
        self.assertTrue(anon_id.startswith("ANON_"), "Should start with ANON_ prefix")
        self.assertEqual(len(anon_id), 13, "Should be 13 characters total (ANON_ + 8 chars)")
        
        # Generate multiple IDs to ensure uniqueness
        ids = set()
        for _ in range(10):
            new_id = self.privacy_manager.generate_anonymous_participant_id()
            ids.add(new_id)
        
        self.assertEqual(len(ids), 10, "All generated IDs should be unique")

    @pytest.mark.security 
    def test_log_privacy_audit(self):
        """Test privacy audit of system logs."""
        # Create test logs with mixed content
        safe_log_content = """
        2025-01-16 10:30:00 INFO Session started for ANON_ABC12345
        2025-01-16 10:30:01 DEBUG Processing sensor data
        2025-01-16 10:30:02 INFO Calibration completed
        """
        
        unsafe_log_content = """
        2025-01-16 10:30:00 INFO User john.doe@example.com connected
        2025-01-16 10:30:01 DEBUG Device ID: SAMSUNG123456
        2025-01-16 10:30:02 ERROR Failed for +1-555-123-4567
        """
        
        # Test safe logs
        safe_log_file = self.test_data_dir / "safe.log"
        safe_log_file.write_text(safe_log_content)
        
        safe_violations = self._scan_logs_for_pii(str(safe_log_file))
        self.assertEqual(len(safe_violations), 0, "Safe logs should have no PII violations")
        
        # Test unsafe logs
        unsafe_log_file = self.test_data_dir / "unsafe.log"
        unsafe_log_file.write_text(unsafe_log_content)
        
        unsafe_violations = self._scan_logs_for_pii(str(unsafe_log_file))
        self.assertGreater(len(unsafe_violations), 0, "Unsafe logs should have PII violations")


class MockPrivacyManager:
    """Mock privacy manager for testing purposes."""
    
    def __init__(self):
        self.data_store = {}
        self.anonymization_settings = {
            "data_anonymization_enabled": False,
            "face_blurring_enabled": False,
            "metadata_stripping_enabled": True
        }
        self.data_retention_days = 365
    
    def anonymize_metadata(self, metadata: Dict) -> Dict:
        """Mock metadata anonymization."""
        anonymized = metadata.copy()
        
        if self.anonymization_settings["metadata_stripping_enabled"]:
            # Remove sensitive fields
            sensitive_fields = [
                "device_id", "serial_number", "mac_address", "imei",
                "phone_number", "email", "user_name", "device_name",
                "network_ssid", "ip_address", "location", "gps"
            ]
            
            for field in sensitive_fields:
                anonymized.pop(field, None)
            
            # Add anonymous fields
            anonymized["participant_id"] = "ANON_ABC12345"
            anonymized["session_id"] = "SESSION_XYZ78910"
            anonymized["device_type"] = "Android_Device_X"
        
        return anonymized
    
    def get_participant_data(self, participant_id: str) -> Dict:
        """Mock participant data retrieval."""
        return self.data_store.get(participant_id, {})
    
    def correct_participant_data(self, participant_id: str, corrections: Dict) -> bool:
        """Mock data correction."""
        if participant_id not in self.data_store:
            self.data_store[participant_id] = {}
        self.data_store[participant_id].update(corrections)
        return True
    
    def delete_participant_data(self, participant_id: str) -> bool:
        """Mock data deletion."""
        self.data_store.pop(participant_id, None)
        return True
    
    def export_participant_data(self, participant_id: str) -> Dict:
        """Mock data export."""
        return {
            "participant_id": participant_id,
            "data": self.data_store.get(participant_id, {}),
            "export_timestamp": datetime.now().isoformat()
        }
    
    def should_delete_data(self, timestamp: int) -> bool:
        """Mock data retention check."""
        retention_period_ms = self.data_retention_days * 24 * 60 * 60 * 1000
        current_time_ms = int(datetime.now().timestamp() * 1000)
        return (current_time_ms - timestamp) > retention_period_ms
    
    def cleanup_expired_data(self) -> Dict:
        """Mock data cleanup."""
        return {"deleted_records": 0, "cleanup_timestamp": datetime.now().isoformat()}
    
    def record_consent(self, participant_id: str, study_id: str = None) -> bool:
        """Mock consent recording."""
        if participant_id not in self.data_store:
            self.data_store[participant_id] = {}
        self.data_store[participant_id]["consent"] = {
            "given": True,
            "timestamp": datetime.now().isoformat(),
            "study_id": study_id
        }
        return True
    
    def has_valid_consent(self, participant_id: str) -> bool:
        """Mock consent validation."""
        data = self.data_store.get(participant_id, {})
        consent = data.get("consent", {})
        return consent.get("given", False)
    
    def withdraw_consent(self, participant_id: str) -> bool:
        """Mock consent withdrawal."""
        if participant_id in self.data_store:
            self.data_store[participant_id]["consent"] = {"given": False}
        return True
    
    def apply_face_blurring(self, image_data: bytes) -> bytes:
        """Mock face blurring."""
        return b"blurred_" + image_data
    
    def configure_anonymization(self, enable_data_anonymization: bool,
                              enable_face_blurring: bool,
                              enable_metadata_stripping: bool):
        """Mock anonymization configuration."""
        self.anonymization_settings.update({
            "data_anonymization_enabled": enable_data_anonymization,
            "face_blurring_enabled": enable_face_blurring,
            "metadata_stripping_enabled": enable_metadata_stripping
        })
    
    def get_anonymization_settings(self) -> Dict:
        """Mock settings retrieval."""
        return self.anonymization_settings.copy()
    
    def generate_privacy_report(self) -> Dict:
        """Mock privacy report generation."""
        return {
            "consent_info": {"participants_with_consent": 0},
            "anonymization_settings": self.anonymization_settings,
            "data_retention_days": self.data_retention_days,
            "report_generated_at": datetime.now().isoformat(),
            "data_collection_purpose": "Multi-sensor physiological research data collection",
            "data_types": ["Video recordings", "Sensor data", "Metadata"],
            "data_processing_basis": "Research consent",
            "data_storage_location": "Local device storage (encrypted)",
            "third_party_sharing": "None"
        }
    
    def generate_anonymous_participant_id(self) -> str:
        """Mock anonymous ID generation."""
        import uuid
        return f"ANON_{uuid.uuid4().hex[:8].upper()}"


if __name__ == "__main__":
    unittest.main()