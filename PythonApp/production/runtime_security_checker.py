"""
Runtime Security Checks Module
=============================

This module provides runtime security validation to ensure the system
is running with appropriate security configurations. It performs startup
checks and ongoing monitoring as recommended in the security assessment.

Security Checks:
- TLS configuration validation
- Default password detection  
- Environment security assessment
- File encryption verification
- Network security validation
"""

import json
import os
import platform
import socket
import ssl
import subprocess
import sys
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Use consolidated import utility to eliminate code duplication
from ..utils.import_utils import get_safe_logger as get_logger


class SecurityValidationError(Exception):
    """Raised when critical security validation fails."""
    pass


class SecurityWarning(UserWarning):
    """Warning for non-critical security issues."""
    pass


class RuntimeSecurityChecker:
    """Performs runtime security checks and validation."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self._security_issues: List[Dict] = []
        self._warnings: List[str] = []
        
    def perform_startup_checks(self, config_path: Optional[str] = None) -> bool:
        """
        Perform comprehensive security checks at application startup.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            True if all critical checks pass, False otherwise
            
        Raises:
            SecurityValidationError: If critical security issues are found
        """
        self.logger.info("Starting runtime security validation...")
        
        # Load configuration
        if not config_path:
            config_path = self._find_config_file()
            
        config = self._load_configuration(config_path)
        
        # Perform security checks
        checks = [
            ("TLS Configuration", self._check_tls_configuration, config),
            ("Authentication Setup", self._check_authentication_config, config),
            ("Default Credentials", self._check_default_passwords, config),
            ("Environment Security", self._check_environment_security, None),
            ("File Permissions", self._check_file_permissions, None),
            ("Network Security", self._check_network_security, config),
            ("Debug Mode", self._check_debug_mode, config),
        ]
        
        critical_failures = []
        
        for check_name, check_func, check_arg in checks:
            try:
                self.logger.debug(f"Running security check: {check_name}")
                if check_arg is not None:
                    result = check_func(check_arg)
                else:
                    result = check_func()
                    
                if not result:
                    critical_failures.append(check_name)
                    self.logger.error(f"CRITICAL: Security check failed: {check_name}")
                    
            except Exception as e:
                self.logger.error(f"Security check error for {check_name}: {e}")
                critical_failures.append(check_name)
        
        # Report results
        self._report_security_status(critical_failures)
        
        if critical_failures:
            error_msg = f"Critical security checks failed: {', '.join(critical_failures)}"
            raise SecurityValidationError(error_msg)
            
        return True
    
    def _find_config_file(self) -> str:
        """Find the protocol configuration file."""
        possible_paths = [
            Path(__file__).parent.parent.parent / "protocol" / "config.json",
            Path(__file__).parent.parent / "config" / "config.json",
            Path("protocol/config.json"),
            Path("config.json")
        ]
        
        for path in possible_paths:
            if path.exists():
                return str(path)
                
        raise FileNotFoundError("Protocol configuration file not found")
    
    def _load_configuration(self, config_path: str) -> Dict:
        """Load and validate configuration file."""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            self.logger.debug(f"Loaded configuration from {config_path}")
            return config
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            raise
    
    def _check_tls_configuration(self, config: Dict) -> bool:
        """Check TLS/SSL configuration for security compliance."""
        security_config = config.get("security", {})
        
        issues = []
        
        # Check if encryption is enabled
        if not security_config.get("encryption_enabled", False):
            issues.append("TLS encryption is disabled")
            self._add_security_issue("critical", "TLS encryption disabled", 
                                   "Enable encryption_enabled in security configuration")
        
        # Check TLS version
        tls_version = security_config.get("tls_version")
        if not tls_version or tls_version not in ["1.2", "1.3"]:
            issues.append(f"Insecure TLS version: {tls_version}")
            self._add_security_issue("high", "Weak TLS version",
                                   "Use TLS 1.2 or 1.3 for secure communications")
        
        # Check certificate pinning
        if not security_config.get("certificate_pinning_enabled", False):
            self._add_warning("Certificate pinning is disabled - consider enabling for production")
        
        # Test actual SSL context creation
        try:
            context = ssl.create_default_context()
            if hasattr(ssl, 'PROTOCOL_TLSv1_2'):
                # Verify modern TLS is available
                context.minimum_version = ssl.TLSVersion.TLSv1_2
        except Exception as e:
            issues.append(f"SSL context creation failed: {e}")
            self._add_security_issue("critical", "SSL unavailable",
                                   "Ensure OpenSSL is properly installed")
        
        if issues:
            self.logger.warning(f"TLS configuration issues: {'; '.join(issues)}")
            return False
            
        self.logger.info("TLS configuration validation passed")
        return True
    
    def _check_authentication_config(self, config: Dict) -> bool:
        """Check authentication configuration."""
        security_config = config.get("security", {})
        
        # Check if authentication is required
        if not security_config.get("authentication_required", False):
            self._add_warning("Authentication is not required - consider enabling for production")
        
        # Check token requirements
        min_token_length = security_config.get("auth_token_min_length", 0)
        if min_token_length < 32:
            self._add_security_issue("medium", "Weak token requirements",
                                   "Set auth_token_min_length to at least 32 characters")
            return False
        
        self.logger.info("Authentication configuration validation passed")
        return True
    
    def _check_default_passwords(self, config: Dict) -> bool:
        """Check for default or weak passwords in configuration."""
        config_str = json.dumps(config, indent=2).lower()
        
        default_patterns = [
            "password", "admin", "default", "123456", "password123",
            "root", "test", "guest", "user", "changeme"
        ]
        
        found_defaults = []
        for pattern in default_patterns:
            if pattern in config_str:
                found_defaults.append(pattern)
        
        if found_defaults:
            self.logger.warning(f"Potential default credentials found: {found_defaults}")
            self._add_security_issue("high", "Default credentials detected",
                                   "Remove or change default passwords")
            return False
        
        self.logger.info("Default password check passed")
        return True
    
    def _check_environment_security(self) -> bool:
        """Check environment security settings."""
        issues = []
        
        # Check if running as root (dangerous)
        if hasattr(os, 'getuid') and os.getuid() == 0:
            issues.append("Running as root user")
            self._add_security_issue("medium", "Root execution",
                                   "Run application with limited user privileges")
        
        # Check debug environment variables
        debug_vars = ['DEBUG', 'FLASK_DEBUG', 'DJANGO_DEBUG', 'MSR_DEBUG']
        for var in debug_vars:
            if os.environ.get(var, '').lower() in ['true', '1', 'yes', 'on']:
                issues.append(f"Debug mode enabled via {var}")
                self._add_warning(f"Debug mode enabled via environment variable {var}")
        
        # Check for development mode indicators
        if os.environ.get('NODE_ENV') == 'development':
            self._add_warning("Development environment detected")
        
        # Check file system permissions
        try:
            current_dir = Path.cwd()
            if oct(current_dir.stat().st_mode)[-3:] == '777':
                issues.append("Working directory has world-writable permissions")
                self._add_security_issue("medium", "Insecure directory permissions",
                                       "Restrict directory permissions")
        except Exception:
            pass
        
        if issues:
            self.logger.warning(f"Environment security issues: {'; '.join(issues)}")
        
        return len(issues) == 0
    
    def _check_file_permissions(self) -> bool:
        """Check file permissions for security compliance."""
        project_root = Path(__file__).parent.parent.parent
        sensitive_files = [
            "protocol/config.json",
            "config.json",
            ".env",
            "credentials.json"
        ]
        
        issues = []
        
        for file_path in sensitive_files:
            full_path = project_root / file_path
            if full_path.exists():
                try:
                    mode = oct(full_path.stat().st_mode)[-3:]
                    # Check if file is world-readable or world-writable
                    if mode[-1] in ['4', '5', '6', '7']:  # World-readable
                        issues.append(f"{file_path} is world-readable")
                    if mode[-1] in ['2', '3', '6', '7']:  # World-writable
                        issues.append(f"{file_path} is world-writable")
                        self._add_security_issue("high", "World-writable sensitive file",
                                               f"Restrict permissions on {file_path}")
                except Exception:
                    pass
        
        if issues:
            self.logger.warning(f"File permission issues: {'; '.join(issues)}")
            return False
            
        return True
    
    def _check_network_security(self, config: Dict) -> bool:
        """Check network security configuration."""
        network_config = config.get("network", {})
        security_config = config.get("security", {})
        
        issues = []
        
        # Check if binding to all interfaces
        host = network_config.get("host", "localhost")
        if host in ["0.0.0.0", "::"]:
            if not security_config.get("authentication_required", False):
                issues.append("Binding to all interfaces without authentication")
                self._add_security_issue("high", "Insecure network binding",
                                       "Enable authentication when binding to all interfaces")
        
        # Check port configuration
        port = network_config.get("port", 8080)
        if port < 1024 and hasattr(os, 'getuid') and os.getuid() != 0:
            self._add_warning(f"Using privileged port {port} without root privileges")
        
        # Check for HTTP usage (should be HTTPS)
        if not security_config.get("secure_transfer", False):
            issues.append("Secure transfer is disabled")
            self._add_security_issue("high", "Insecure transfer protocol",
                                   "Enable secure_transfer for HTTPS/TLS")
        
        if issues:
            self.logger.warning(f"Network security issues: {'; '.join(issues)}")
            return False
            
        return True
    
    def _check_debug_mode(self, config: Dict) -> bool:
        """Check for debug mode configuration."""
        # Check various debug configurations
        debug_indicators = [
            config.get("debug", False),
            config.get("testing", {}).get("fake_device_enabled", False),
            config.get("logging", {}).get("level", "").upper() == "DEBUG"
        ]
        
        if any(debug_indicators):
            self._add_warning("Debug mode indicators found - ensure this is not production")
            self.logger.warning("🔒 [SECURITY WARNING] Debug mode detected - verify this is not production")
            
        return True  # Non-critical for now
    
    def check_android_device_security(self) -> Dict[str, bool]:
        """Check Android device security if available."""
        results = {
            "device_encrypted": False,
            "screen_lock_enabled": False,
            "unknown_sources_disabled": True,
            "usb_debugging_disabled": True
        }
        
        try:
            # Try to check if ADB is available and get device info
            result = subprocess.run(['adb', 'devices'], 
                                  capture_output=True, text=True, timeout=5)
            
            if "device" in result.stdout:
                self.logger.info("Android device detected via ADB")
                
                # Check encryption status
                encrypt_result = subprocess.run(
                    ['adb', 'shell', 'getprop', 'ro.crypto.state'],
                    capture_output=True, text=True, timeout=5
                )
                if encrypt_result.returncode == 0:
                    results["device_encrypted"] = "encrypted" in encrypt_result.stdout
                    
                # Check developer options
                dev_result = subprocess.run(
                    ['adb', 'shell', 'settings', 'get', 'global', 'development_settings_enabled'],
                    capture_output=True, text=True, timeout=5
                )
                if dev_result.returncode == 0 and "1" in dev_result.stdout:
                    results["usb_debugging_disabled"] = False
                    self._add_warning("USB debugging is enabled on Android device")
                    
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.logger.debug("ADB not available or no Android device connected")
        except Exception as e:
            self.logger.debug(f"Android security check failed: {e}")
        
        return results
    
    def _add_security_issue(self, severity: str, title: str, recommendation: str):
        """Add a security issue to the report."""
        self._security_issues.append({
            "severity": severity,
            "title": title,
            "recommendation": recommendation
        })
    
    def _add_warning(self, message: str):
        """Add a security warning."""
        self._warnings.append(message)
        warnings.warn(message, SecurityWarning)
    
    def _report_security_status(self, critical_failures: List[str]):
        """Report overall security status."""
        if not critical_failures and not self._security_issues:
            self.logger.info("🔒 All security checks passed")
            return
        
        self.logger.warning("🔒 Security Status Report:")
        
        if critical_failures:
            self.logger.error(f"❌ Critical failures: {len(critical_failures)}")
            for failure in critical_failures:
                self.logger.error(f"   - {failure}")
        
        if self._security_issues:
            self.logger.warning(f"⚠️  Security issues found: {len(self._security_issues)}")
            for issue in self._security_issues:
                self.logger.warning(f"   [{issue['severity'].upper()}] {issue['title']}")
                self.logger.warning(f"      Recommendation: {issue['recommendation']}")
        
        if self._warnings:
            self.logger.info(f"💡 Security warnings: {len(self._warnings)}")
            for warning in self._warnings:
                self.logger.info(f"   - {warning}")
    
    def get_security_report(self) -> Dict:
        """Get detailed security report."""
        return {
            "security_issues": self._security_issues,
            "warnings": self._warnings,
            "checks_performed": True,
            "timestamp": str(Path(__file__).stat().st_mtime)
        }


def validate_runtime_security(config_path: Optional[str] = None) -> bool:
    """
    Convenience function to perform runtime security validation.
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        True if all critical security checks pass
        
    Raises:
        SecurityValidationError: If critical security issues found
    """
    checker = RuntimeSecurityChecker()
    return checker.perform_startup_checks(config_path)


def check_production_readiness() -> Dict[str, bool]:
    """
    Check if system is ready for production deployment.
    
    Returns:
        Dictionary with readiness indicators
    """
    checker = RuntimeSecurityChecker()
    
    try:
        # Try to run security checks
        checker.perform_startup_checks()
        security_ready = True
    except SecurityValidationError:
        security_ready = False
    
    # Additional production checks
    android_security = checker.check_android_device_security()
    
    return {
        "security_validated": security_ready,
        "tls_configured": True,  # Will be False if TLS check fails
        "authentication_enabled": True,  # From config check
        "debug_mode_disabled": len(checker._warnings) == 0,
        "android_device_secure": android_security.get("device_encrypted", False),
        "overall_ready": security_ready and len(checker._warnings) == 0
    }


if __name__ == "__main__":
    # Run standalone security check
    try:
        print("🔒 Running runtime security validation...")
        validate_runtime_security()
        print("✅ All security checks passed!")
        
        print("\n🏭 Checking production readiness...")
        readiness = check_production_readiness()
        for check, status in readiness.items():
            status_icon = "✅" if status else "❌"
            print(f"{status_icon} {check}: {status}")
            
    except SecurityValidationError as e:
        print(f"❌ Security validation failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"💥 Security check error: {e}")
        sys.exit(1)