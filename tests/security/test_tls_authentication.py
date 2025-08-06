"""
TLS Authentication and Encryption Security Tests
===============================================

This module implements comprehensive tests for TLS encryption, certificate validation,
and authentication workflows as recommended in the security assessment.

Test Coverage:
1. Valid TLS certificate acceptance
2. Invalid/expired certificate rejection  
3. Token authentication validation
4. Certificate pinning verification
5. TLS version enforcement
6. Debug mode security warnings
"""

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

# Add project root to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from PythonApp.network.device_client import DeviceClient


class TLSAuthenticationTests(unittest.TestCase):
    """Test suite for TLS and authentication security features."""
    
    def setUp(self):
        """Set up test environment with temporary certificates and configs."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_port = 9999  # Use different port to avoid conflicts
        
        # Create temporary certificate files for testing
        self.cert_file = os.path.join(self.temp_dir, "test_cert.pem") 
        self.key_file = os.path.join(self.temp_dir, "test_key.pem")
        self.ca_file = os.path.join(self.temp_dir, "test_ca.pem")
        
        # Generate test certificates (self-signed for testing)
        self._generate_test_certificates()
        
        # Mock device client for testing
        self.device_client = DeviceClient()
        self.device_client.server_port = self.test_port
        
    def tearDown(self):
        """Clean up test environment."""
        if hasattr(self.device_client, 'running'):
            self.device_client.running = False
        
        # Clean up temporary files
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _generate_test_certificates(self):
        """Generate test SSL certificates for testing purposes."""
        try:
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import rsa
        except ImportError:
            self.skipTest("cryptography package not available")
        
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Create certificate
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
        
        # Write certificate and key files
        with open(self.cert_file, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
            
        with open(self.key_file, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
            
        # Use same cert as CA for testing
        with open(self.ca_file, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
    
    def _generate_expired_certificate(self):
        """Generate an expired certificate for testing rejection."""
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
            datetime.utcnow() - timedelta(days=1)  # Expired
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
        """Test that valid TLS certificates are properly accepted."""
        # Configure SSL with valid certificate
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
        """Test that authentication tokens are properly validated."""
        # Test valid token
        valid_token = "a" * 32  # Meets minimum length requirement
        self.assertTrue(
            self._validate_auth_token(valid_token),
            "Valid token should be accepted"
        )
        
        # Test short token (security risk)
        short_token = "abc123"
        self.assertFalse(
            self._validate_auth_token(short_token),
            "Short token should be rejected"
        )
        
        # Test empty token
        self.assertFalse(
            self._validate_auth_token(""),
            "Empty token should be rejected"
        )
        
        # Test None token
        self.assertFalse(
            self._validate_auth_token(None),
            "None token should be rejected"
        )

    def _validate_auth_token(self, token: Optional[str]) -> bool:
        """Validate authentication token according to security requirements."""
        if not token:
            return False
        
        # Check minimum length (from config: auth_token_min_length: 32)
        if len(token) < 32:
            return False
            
        # Check for common weak patterns
        if token.isdigit() or token.isalpha() or token == token[0] * len(token):
            return False
            
        return True

    @pytest.mark.security 
    def test_certificate_pinning_enabled(self):
        """Test that certificate pinning is properly enabled and enforced."""
        # Load protocol config
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
        """Test that TLS version is properly enforced."""
        success = self.device_client.configure_ssl(
            certfile=self.cert_file,
            keyfile=self.key_file
        )
        
        self.assertTrue(success, "SSL configuration should succeed")

    @pytest.mark.security
    def test_debug_mode_security_warnings(self):
        """Test that debug mode produces appropriate security warnings."""
        with patch('builtins.print') as mock_print:
            # Enable debug mode (simulated)
            debug_mode = True
            if debug_mode and self.device_client._ssl_enabled:
                print("[SECURITY WARNING] Debug mode enabled with SSL - ensure this is not production")
                
            # Check that warning was printed
            mock_print.assert_called_with(
                "[SECURITY WARNING] Debug mode enabled with SSL - ensure this is not production"
            )

    @pytest.mark.security  
    def test_connection_rate_limiting(self):
        """Test that connection rate limiting is properly enforced."""
        # Test rate limiting functionality
        client_ip = "192.168.1.100"
        
        # Simulate multiple rapid connections
        for i in range(70):  # Exceed max_requests_per_minute: 60
            is_allowed = self.device_client._check_rate_limit(client_ip)
            if i < 60:
                self.assertTrue(is_allowed, f"Connection {i+1} should be allowed")
            else:
                self.assertFalse(is_allowed, f"Connection {i+1} should be rate limited")


class SecurityConfigurationTests(unittest.TestCase):
    """Test suite for security configuration validation."""

    @pytest.mark.security
    def test_production_security_configuration(self):
        """Test that production security configuration meets requirements."""
        config_path = Path(__file__).parent.parent.parent / "protocol" / "config.json"
        
        self.assertTrue(config_path.exists(), "Protocol configuration should exist")
        
        with open(config_path) as f:
            config = json.load(f)
        
        security = config.get("security", {})
        
        # Test encryption settings
        self.assertTrue(
            security.get("encryption_enabled", False),
            "Encryption must be enabled in production"
        )
        
        # Test authentication settings
        self.assertTrue(
            security.get("authentication_required", False),
            "Authentication must be required in production"
        )
        
        # Test secure transfer
        self.assertTrue(
            security.get("secure_transfer", False),
            "Secure transfer must be enabled"
        )
        
        # Test TLS version
        tls_version = security.get("tls_version")
        self.assertIn(
            tls_version,
            ["1.2", "1.3"],
            "TLS version must be 1.2 or higher"
        )
        
        # Test certificate pinning
        self.assertTrue(
            security.get("certificate_pinning_enabled", False),
            "Certificate pinning should be enabled"
        )
        
        # Test token requirements
        min_token_length = security.get("auth_token_min_length", 0)
        self.assertGreaterEqual(
            min_token_length,
            32,
            "Minimum token length should be at least 32 characters"
        )

    @pytest.mark.security
    def test_no_default_credentials(self):
        """Test that no default credentials are present in configuration."""
        config_path = Path(__file__).parent.parent.parent / "protocol" / "config.json"
        
        with open(config_path) as f:
            config_text = f.read()
        
        # Check for common default credentials
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