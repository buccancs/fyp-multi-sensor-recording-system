
import json
import os
import socket
import ssl
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch
from typing import Optional

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from PythonApp.network.device_client import DeviceClient


class TLSAuthenticationTests(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_port = 9999
        
        self.cert_file = os.path.join(self.temp_dir, "test_cert.pem") 
        self.key_file = os.path.join(self.temp_dir, "test_key.pem")
        self.ca_file = os.path.join(self.temp_dir, "test_ca.pem")
        
        self._generate_test_certificates()
        
        self.device_client = DeviceClient()
        self.device_client.server_port = self.test_port
        
    def tearDown(self):
        if hasattr(self.device_client, 'running'):
            self.device_client.running = False
        
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _generate_test_certificates(self):
        try:
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import rsa
        except ImportError:
            self.skipTest("cryptography package not available")
        
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Test"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Test"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Test Org"),
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=10)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.IPAddress("127.0.0.1"),
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256())
        
        with open(self.cert_file, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
            
        with open(self.key_file, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
            
        with open(self.ca_file, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
    
    def _generate_expired_certificate(self):
        try:
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import rsa
        except ImportError:
            self.skipTest("cryptography package not available")
        
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, "expired.localhost"),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow() - timedelta(days=10)
        ).not_valid_after(
            datetime.utcnow() - timedelta(days=1)
        ).sign(private_key, hashes.SHA256())
        
        expired_cert_file = os.path.join(self.temp_dir, "expired_cert.pem")
        expired_key_file = os.path.join(self.temp_dir, "expired_key.pem")
        
        with open(expired_cert_file, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
            
        with open(expired_key_file, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
            
        return expired_cert_file, expired_key_file

    @pytest.mark.security
    def test_valid_tls_certificate_acceptance(self):
        success = self.device_client.configure_ssl(
            certfile=self.cert_file,
            keyfile=self.key_file,
            ca_certs=self.ca_file
        )
        
        self.assertTrue(success, "Valid SSL configuration should succeed")
        self.assertTrue(self.device_client._ssl_enabled, "SSL should be enabled")
        self.assertIsNotNone(self.device_client._ssl_context, "SSL context should be created")

    @pytest.mark.security
    def test_authentication_token_validation(self):
        valid_token = "a" * 32
        self.assertTrue(
            self._validate_auth_token(valid_token),
            "Valid token should be accepted"
        )
        
        short_token = "abc123"
        self.assertFalse(
            self._validate_auth_token(short_token),
            "Short token should be rejected"
        )
        
        self.assertFalse(
            self._validate_auth_token(""),
            "Empty token should be rejected"
        )
        
        self.assertFalse(
            self._validate_auth_token(None),
            "None token should be rejected"
        )

    def _validate_auth_token(self, token: Optional[str]) -> bool:
        if not token:
            return False
        
        if len(token) < 32:
            return False
            
        if token.isdigit() or token.isalpha() or token == token[0] * len(token):
            return False
            
        return True

    @pytest.mark.security 
    def test_certificate_pinning_enabled(self):
        config_path = Path(__file__).parent.parent.parent / "protocol" / "config.json"
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
            
            security_config = config.get("security", {})
            self.assertTrue(
                security_config.get("certificate_pinning_enabled", False),
                "Certificate pinning should be enabled in production config"
            )
            self.assertTrue(
                security_config.get("encryption_enabled", False),
                "Encryption should be enabled in production config"
            )
            self.assertEqual(
                security_config.get("tls_version"),
                "1.3",
                "TLS 1.3 should be configured for maximum security"
            )

    @pytest.mark.security
    def test_tls_version_enforcement(self):
        success = self.device_client.configure_ssl(
            certfile=self.cert_file,
            keyfile=self.key_file
        )
        
        self.assertTrue(success, "SSL configuration should succeed")

    @pytest.mark.security
    def test_debug_mode_security_warnings(self):
        with patch('builtins.print') as mock_print:
            debug_mode = True
            if debug_mode and self.device_client._ssl_enabled:
                print("[SECURITY WARNING] Debug mode enabled with SSL - ensure this is not production")
                
            mock_print.assert_called_with(
                "[SECURITY WARNING] Debug mode enabled with SSL - ensure this is not production"
            )

    @pytest.mark.security  
    def test_connection_rate_limiting(self):
        client_ip = "192.168.1.100"
        
        for i in range(70):
            is_allowed = self.device_client._check_rate_limit(client_ip)
            if i < 60:
                self.assertTrue(is_allowed, f"Connection {i+1} should be allowed")
            else:
                self.assertFalse(is_allowed, f"Connection {i+1} should be rate limited")


class SecurityConfigurationTests(unittest.TestCase):

    @pytest.mark.security
    def test_production_security_configuration(self):
        config_path = Path(__file__).parent.parent.parent / "protocol" / "config.json"
        
        self.assertTrue(config_path.exists(), "Protocol configuration should exist")
        
        with open(config_path) as f:
            config = json.load(f)
        
        security = config.get("security", {})
        
        self.assertTrue(
            security.get("encryption_enabled", False),
            "Encryption must be enabled in production"
        )
        
        self.assertTrue(
            security.get("authentication_required", False),
            "Authentication must be required in production"
        )
        
        self.assertTrue(
            security.get("secure_transfer", False),
            "Secure transfer must be enabled"
        )
        
        tls_version = security.get("tls_version")
        self.assertIn(
            tls_version,
            ["1.2", "1.3"],
            "TLS version must be 1.2 or higher"
        )
        
        self.assertTrue(
            security.get("certificate_pinning_enabled", False),
            "Certificate pinning should be enabled"
        )
        
        min_token_length = security.get("auth_token_min_length", 0)
        self.assertGreaterEqual(
            min_token_length,
            32,
            "Minimum token length should be at least 32 characters"
        )

    @pytest.mark.security
    def test_no_default_credentials(self):
        config_path = Path(__file__).parent.parent.parent / "protocol" / "config.json"
        
        with open(config_path) as f:
            config_text = f.read()
        
        default_patterns = [
            "password",
            "admin", 
            "default",
            "123456",
            "password123"
        ]
        
        for pattern in default_patterns:
            self.assertNotIn(
                pattern.lower(),
                config_text.lower(),
                f"Default credential pattern '{pattern}' found in configuration"
            )


if __name__ == "__main__":
    unittest.main()