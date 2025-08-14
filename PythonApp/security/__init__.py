"""
Security Module
==============

Provides security features including TLS encryption, authentication tokens,
and runtime security checks for the multi-sensor recording system.
"""

import logging
import ssl
import socket
import secrets
import hashlib
import time
import json
import os
import ipaddress
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class AuthenticationToken:
    """Authentication token for device connections."""
    token_id: str
    token_hash: str
    device_id: str
    created_at: datetime
    expires_at: datetime
    permissions: List[str]
    is_active: bool = True
    
    def is_valid(self) -> bool:
        """Check if token is valid and not expired."""
        if not self.is_active:
            return False
        return datetime.now() < self.expires_at
    
    def to_dict(self) -> dict:
        return {
            'token_id': self.token_id,
            'device_id': self.device_id,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'permissions': self.permissions,
            'is_active': self.is_active
        }


class SecurityConfig:
    """Security configuration settings."""
    
    def __init__(self, config_file: str = "security_config.json"):
        self.config_file = Path(config_file)
        
        # Default security settings
        self.tls_enabled = True
        self.require_authentication = True
        self.token_expiry_hours = 24
        self.min_token_length = 32
        self.max_failed_attempts = 5
        self.lockout_duration_minutes = 30
        self.allowed_device_patterns: List[str] = []
        
        # TLS settings
        self.cert_file = "server.crt"
        self.key_file = "server.key"
        self.ca_file = None
        
        # Load config if exists
        self.load_config()
    
    def load_config(self):
        """Load security configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                
                for key, value in config_data.items():
                    if hasattr(self, key):
                        setattr(self, key, value)
                
                logger.info("Loaded security configuration")
            except Exception as e:
                logger.error(f"Error loading security config: {e}")
    
    def save_config(self):
        """Save security configuration to file."""
        try:
            config_data = {
                'tls_enabled': self.tls_enabled,
                'require_authentication': self.require_authentication,
                'token_expiry_hours': self.token_expiry_hours,
                'min_token_length': self.min_token_length,
                'max_failed_attempts': self.max_failed_attempts,
                'lockout_duration_minutes': self.lockout_duration_minutes,
                'allowed_device_patterns': self.allowed_device_patterns,
                'cert_file': self.cert_file,
                'key_file': self.key_file,
                'ca_file': self.ca_file
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            logger.info("Saved security configuration")
        except Exception as e:
            logger.error(f"Error saving security config: {e}")


class AuthenticationManager:
    """Manages authentication tokens and device access control."""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.tokens: Dict[str, AuthenticationToken] = {}
        self.failed_attempts: Dict[str, List[datetime]] = {}
        self.locked_devices: Dict[str, datetime] = {}
        
        # Load existing tokens
        self.load_tokens()
    
    def generate_token(self, device_id: str, permissions: List[str] = None) -> Tuple[str, AuthenticationToken]:
        """Generate a new authentication token for a device."""
        if permissions is None:
            permissions = ["record", "transfer", "sync"]
        
        # Generate secure token
        token_value = secrets.token_urlsafe(self.config.min_token_length)
        token_hash = hashlib.sha256(token_value.encode()).hexdigest()
        
        # Create token object
        token = AuthenticationToken(
            token_id=secrets.token_hex(16),
            token_hash=token_hash,
            device_id=device_id,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=self.config.token_expiry_hours),
            permissions=permissions
        )
        
        # Store token
        self.tokens[token.token_id] = token
        
        logger.info(f"Generated authentication token for device {device_id}")
        return token_value, token
    
    def validate_token(self, token_value: str, device_id: str, required_permission: str = None) -> bool:
        """Validate an authentication token."""
        if not self.config.require_authentication:
            return True
        
        # Check if device is locked out
        if self._is_device_locked(device_id):
            logger.warning(f"Device {device_id} is locked out")
            return False
        
        try:
            token_hash = hashlib.sha256(token_value.encode()).hexdigest()
            
            # Find matching token
            for token in self.tokens.values():
                if (token.token_hash == token_hash and 
                    token.device_id == device_id and 
                    token.is_valid()):
                    
                    # Check required permission
                    if required_permission and required_permission not in token.permissions:
                        logger.warning(f"Token for {device_id} lacks required permission: {required_permission}")
                        return False
                    
                    # Clear failed attempts on successful authentication
                    if device_id in self.failed_attempts:
                        del self.failed_attempts[device_id]
                    
                    return True
            
            # Record failed attempt
            self._record_failed_attempt(device_id)
            logger.warning(f"Invalid token for device {device_id}")
            return False
            
        except Exception as e:
            logger.error(f"Error validating token: {e}")
            self._record_failed_attempt(device_id)
            return False
    
    def revoke_token(self, token_id: str) -> bool:
        """Revoke an authentication token."""
        if token_id in self.tokens:
            self.tokens[token_id].is_active = False
            logger.info(f"Revoked token {token_id}")
            return True
        return False
    
    def revoke_device_tokens(self, device_id: str) -> int:
        """Revoke all tokens for a device."""
        revoked_count = 0
        
        for token in self.tokens.values():
            if token.device_id == device_id and token.is_active:
                token.is_active = False
                revoked_count += 1
        
        logger.info(f"Revoked {revoked_count} tokens for device {device_id}")
        return revoked_count
    
    def cleanup_expired_tokens(self):
        """Remove expired tokens from memory."""
        expired_tokens = [
            token_id for token_id, token in self.tokens.items()
            if not token.is_valid()
        ]
        
        for token_id in expired_tokens:
            del self.tokens[token_id]
        
        if expired_tokens:
            logger.info(f"Cleaned up {len(expired_tokens)} expired tokens")
    
    def _record_failed_attempt(self, device_id: str):
        """Record a failed authentication attempt."""
        if device_id not in self.failed_attempts:
            self.failed_attempts[device_id] = []
        
        self.failed_attempts[device_id].append(datetime.now())
        
        # Remove old attempts (older than lockout duration)
        cutoff_time = datetime.now() - timedelta(minutes=self.config.lockout_duration_minutes)
        self.failed_attempts[device_id] = [
            attempt for attempt in self.failed_attempts[device_id]
            if attempt > cutoff_time
        ]
        
        # Check if device should be locked
        if len(self.failed_attempts[device_id]) >= self.config.max_failed_attempts:
            self.locked_devices[device_id] = datetime.now()
            logger.warning(f"Device {device_id} locked due to too many failed attempts")
    
    def _is_device_locked(self, device_id: str) -> bool:
        """Check if a device is currently locked out."""
        if device_id not in self.locked_devices:
            return False
        
        lockout_time = self.locked_devices[device_id]
        unlock_time = lockout_time + timedelta(minutes=self.config.lockout_duration_minutes)
        
        if datetime.now() > unlock_time:
            # Unlock device
            del self.locked_devices[device_id]
            if device_id in self.failed_attempts:
                del self.failed_attempts[device_id]
            logger.info(f"Device {device_id} unlocked")
            return False
        
        return True
    
    def get_device_tokens(self, device_id: str) -> List[dict]:
        """Get all tokens for a device."""
        device_tokens = []
        
        for token in self.tokens.values():
            if token.device_id == device_id:
                device_tokens.append(token.to_dict())
        
        return device_tokens
    
    def get_all_tokens(self) -> List[dict]:
        """Get all authentication tokens."""
        return [token.to_dict() for token in self.tokens.values()]
    
    def load_tokens(self):
        """Load tokens from persistent storage."""
        # This would typically load from a secure database
        # For now, we'll skip persistent storage
        pass
    
    def save_tokens(self):
        """Save tokens to persistent storage."""
        # This would typically save to a secure database
        # For now, we'll skip persistent storage
        pass


class TLSManager:
    """Manages TLS/SSL encryption for network communications."""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.ssl_context = None
        
        if self.config.tls_enabled:
            self._setup_ssl_context()
    
    def _setup_ssl_context(self):
        """Set up SSL context for secure communications."""
        try:
            self.ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            
            # Load certificate and key
            if Path(self.config.cert_file).exists() and Path(self.config.key_file).exists():
                self.ssl_context.load_cert_chain(self.config.cert_file, self.config.key_file)
                logger.info("Loaded SSL certificate and key")
            else:
                # Generate self-signed certificate for development
                self._generate_self_signed_cert()
                self.ssl_context.load_cert_chain(self.config.cert_file, self.config.key_file)
                logger.warning("Using self-signed certificate - not suitable for production")
            
            # Configure SSL settings
            self.ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
            self.ssl_context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
            
        except Exception as e:
            logger.error(f"Error setting up SSL context: {e}")
            self.ssl_context = None
    
    def _generate_self_signed_cert(self):
        """Generate a self-signed certificate for development."""
        try:
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.primitives import serialization
            
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )
            
            # Generate certificate
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Local"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "Local"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Multi-Sensor Recording System"),
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
                datetime.utcnow() + timedelta(days=365)
            ).add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName("localhost"),
                    x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                ]),
                critical=False,
            ).sign(private_key, hashes.SHA256())
            
            # Write certificate and key files
            with open(self.config.cert_file, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            
            with open(self.config.key_file, "wb") as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            logger.info("Generated self-signed certificate")
            
        except ImportError:
            logger.error("cryptography library not available - cannot generate certificate")
            # Create dummy files
            with open(self.config.cert_file, "w") as f:
                f.write("# Dummy certificate file\n")
            with open(self.config.key_file, "w") as f:
                f.write("# Dummy key file\n")
        except Exception as e:
            logger.error(f"Error generating self-signed certificate: {e}")
    
    def wrap_socket(self, sock: socket.socket) -> socket.socket:
        """Wrap a socket with TLS encryption."""
        if self.ssl_context:
            return self.ssl_context.wrap_socket(sock, server_side=True)
        return sock
    
    def is_tls_enabled(self) -> bool:
        """Check if TLS is enabled and properly configured."""
        return self.config.tls_enabled and self.ssl_context is not None


class SecurityChecker:
    """Performs runtime security checks and validation."""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.security_warnings: List[str] = []
    
    def perform_startup_checks(self) -> Tuple[bool, List[str]]:
        """Perform security checks at application startup."""
        self.security_warnings.clear()
        
        # Check TLS configuration
        if not self.config.tls_enabled:
            self.security_warnings.append("TLS encryption is disabled - network traffic is not encrypted")
        
        # Check authentication configuration
        if not self.config.require_authentication:
            self.security_warnings.append("Authentication is disabled - any device can connect")
        
        # Check certificate files
        if self.config.tls_enabled:
            if not Path(self.config.cert_file).exists():
                self.security_warnings.append(f"TLS certificate file not found: {self.config.cert_file}")
            
            if not Path(self.config.key_file).exists():
                self.security_warnings.append(f"TLS key file not found: {self.config.key_file}")
        
        # Check file permissions
        self._check_file_permissions()
        
        # Check environment security
        self._check_environment_security()
        
        # Determine overall security status
        has_critical_issues = any(
            "disabled" in warning or "not found" in warning 
            for warning in self.security_warnings
        )
        
        return not has_critical_issues, self.security_warnings
    
    def _check_file_permissions(self):
        """Check file and directory permissions."""
        try:
            # Check if running as root (Unix-like systems)
            if hasattr(os, 'getuid') and os.getuid() == 0:
                self.security_warnings.append("Application is running as root - this is not recommended")
            
            # Check key file permissions
            if Path(self.config.key_file).exists():
                key_stat = os.stat(self.config.key_file)
                if hasattr(key_stat, 'st_mode'):
                    # Check if key file is readable by others (Unix-like systems)
                    if key_stat.st_mode & 0o044:  # Other read permissions
                        self.security_warnings.append("Private key file has overly permissive permissions")
        
        except Exception as e:
            logger.error(f"Error checking file permissions: {e}")
    
    def _check_environment_security(self):
        """Check environment security settings."""
        # Check for debug mode
        if os.environ.get('DEBUG', '').lower() in ('true', '1', 'yes'):
            self.security_warnings.append("Debug mode is enabled - may expose sensitive information")
        
        # Check for development mode
        if os.environ.get('DEVELOPMENT', '').lower() in ('true', '1', 'yes'):
            self.security_warnings.append("Development mode is enabled - security features may be reduced")
    
    def validate_device_connection(self, device_id: str, remote_address: str) -> bool:
        """Validate a device connection attempt."""
        # Check device ID pattern
        if self.config.allowed_device_patterns:
            import re
            allowed = any(
                re.match(pattern, device_id)
                for pattern in self.config.allowed_device_patterns
            )
            if not allowed:
                logger.warning(f"Device ID {device_id} does not match allowed patterns")
                return False
        
        # Additional connection validation could be added here
        # (e.g., IP address filtering, rate limiting)
        
        return True
    
    def get_security_status(self) -> dict:
        """Get current security status."""
        return {
            'tls_enabled': self.config.tls_enabled,
            'authentication_required': self.config.require_authentication,
            'security_warnings': self.security_warnings,
            'last_check': datetime.now().isoformat()
        }


class SecurityManager:
    """Main security manager that coordinates all security components."""
    
    def __init__(self, config_file: str = "security_config.json"):
        self.config = SecurityConfig(config_file)
        self.auth_manager = AuthenticationManager(self.config)
        self.tls_manager = TLSManager(self.config)
        self.security_checker = SecurityChecker(self.config)
        
        # Perform startup security checks
        is_secure, warnings = self.security_checker.perform_startup_checks()
        
        if warnings:
            logger.warning(f"Security warnings detected: {warnings}")
        
        if not is_secure:
            logger.error("Critical security issues detected - review configuration")
    
    def authenticate_device(self, device_id: str, token: str, required_permission: str = None) -> bool:
        """Authenticate a device connection."""
        return self.auth_manager.validate_token(token, device_id, required_permission)
    
    def generate_device_token(self, device_id: str, permissions: List[str] = None) -> Tuple[str, dict]:
        """Generate an authentication token for a device."""
        token_value, token_obj = self.auth_manager.generate_token(device_id, permissions)
        return token_value, token_obj.to_dict()
    
    def wrap_socket_with_tls(self, sock: socket.socket) -> socket.socket:
        """Wrap a socket with TLS encryption if enabled."""
        return self.tls_manager.wrap_socket(sock)
    
    def validate_connection(self, device_id: str, remote_address: str) -> bool:
        """Validate a device connection attempt."""
        return self.security_checker.validate_device_connection(device_id, remote_address)
    
    def get_security_status(self) -> dict:
        """Get comprehensive security status."""
        return {
            'configuration': {
                'tls_enabled': self.config.tls_enabled,
                'authentication_required': self.config.require_authentication,
                'token_expiry_hours': self.config.token_expiry_hours
            },
            'tls_status': {
                'enabled': self.tls_manager.is_tls_enabled(),
                'certificate_file': self.config.cert_file,
                'key_file': self.config.key_file
            },
            'authentication_status': {
                'total_tokens': len(self.auth_manager.tokens),
                'locked_devices': len(self.auth_manager.locked_devices)
            },
            'security_checks': self.security_checker.get_security_status()
        }
    
    def cleanup(self):
        """Perform security cleanup tasks."""
        self.auth_manager.cleanup_expired_tokens()
    
    def generate_authentication_token(self, device_id: str = "default") -> str:
        """Generate an authentication token (alias for generate_device_token)."""
        token_value, _ = self.generate_device_token(device_id)
        return token_value
    
    def validate_token(self, token: str, device_id: str = "default") -> bool:
        """Validate an authentication token."""
        try:
            return self.auth_manager.validate_token(token, device_id)
        except Exception as e:
            logger.error(f"Error validating token: {e}")
            return False
    
    def check_tls_configuration(self) -> Dict[str, Any]:
        """Check TLS configuration and return status."""
        return {
            'tls_enabled': self.config.tls_enabled,
            'certificate_exists': Path(self.config.cert_file).exists(),
            'key_exists': Path(self.config.key_file).exists(),
            'ssl_context_available': self.tls_manager.ssl_context is not None,
            'configuration_valid': self.tls_manager.is_tls_enabled()
        }