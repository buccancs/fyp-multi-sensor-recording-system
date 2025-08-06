#!/usr/bin/env python3
"""
Vendor SDK Monitoring Script
Addresses High Priority recommendation: "Regularly update vendor SDKs"

This script monitors Shimmer and thermal camera SDK versions and provides
guidance for updating vendor-provided AARs/JARs that are not managed by Gradle.

Author: Multi-Sensor Recording System
Usage: python scripts/monitor_vendor_sdks.py [--check-updates] [--generate-report]
"""

import argparse
import json
import logging
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VendorSDKMonitor:
    """Monitor vendor SDK versions and provide update recommendations."""
    
    # Known vendor SDK information
    VENDOR_SDKS = {
        "shimmer": {
            "description": "Shimmer GSR Sensor SDK",
            "files": [
                "shimmerandroidinstrumentdriver-3.2.3_beta.aar",
                "shimmerbluetoothmanager-0.11.4_beta.jar", 
                "shimmerdriver-0.11.4_beta.jar",
                "shimmerdriverpc-0.11.4_beta.jar"
            ],
            "current_version": "0.11.4_beta",
            "vendor_url": "https://github.com/ShimmerEngineering/Shimmer-Java-Android-API",
            "update_check_url": "https://api.github.com/repos/ShimmerEngineering/Shimmer-Java-Android-API/releases/latest",
            "risk_level": "medium",
            "notes": "Beta version in use - consider moving to stable when available"
        },
        "thermal_camera": {
            "description": "Thermal Camera SDK (TopDon)",
            "files": [
                "topdon_1.3.7.aar",
                "libusbdualsdk_1.3.4_2406271906_standard.aar", 
                "opengl_1.3.2_standard.aar",
                "suplib-release.aar"
            ],
            "current_version": "1.3.7",
            "vendor_url": "https://www.topdon.com/",
            "update_check_url": None,  # Manual check required
            "risk_level": "low",
            "notes": "Proprietary SDK - manual monitoring required"
        }
    }
    
    def __init__(self, project_root: Path):
        """Initialize the SDK monitor.
        
        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root
        self.libs_dir = project_root / "AndroidApp" / "src" / "main" / "libs"
        self.reports_dir = project_root / "security_reports"
        
        # Ensure reports directory exists
        self.reports_dir.mkdir(exist_ok=True)
    
    def scan_current_sdks(self) -> Dict[str, Dict]:
        """Scan the current SDK files in the libs directory.
        
        Returns:
            Dictionary of found SDK files with metadata
        """
        if not self.libs_dir.exists():
            logger.warning(f"Libs directory not found: {self.libs_dir}")
            return {}
        
        found_sdks = {}
        
        for vendor, info in self.VENDOR_SDKS.items():
            found_files = []
            missing_files = []
            
            for filename in info["files"]:
                file_path = self.libs_dir / filename
                if file_path.exists():
                    stat = file_path.stat()
                    found_files.append({
                        "filename": filename,
                        "path": str(file_path),
                        "size_mb": round(stat.st_size / (1024 * 1024), 2),
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "exists": True
                    })
                else:
                    missing_files.append(filename)
            
            found_sdks[vendor] = {
                **info,
                "found_files": found_files,
                "missing_files": missing_files,
                "scan_timestamp": datetime.now().isoformat()
            }
        
        return found_sdks
    
    def check_for_updates(self, vendor_info: Dict) -> Dict:
        """Check for available updates for a specific vendor SDK.
        
        Args:
            vendor_info: Vendor SDK information
            
        Returns:
            Update check results
        """
        update_info = {
            "update_available": False,
            "latest_version": vendor_info["current_version"],
            "check_method": "manual",
            "check_timestamp": datetime.now().isoformat(),
            "error": None
        }
        
        # For Shimmer SDK, check GitHub API
        if vendor_info.get("update_check_url") and "shimmer" in vendor_info["description"].lower():
            try:
                import requests
                response = requests.get(vendor_info["update_check_url"], timeout=10)
                if response.status_code == 200:
                    release_data = response.json()
                    latest_version = release_data.get("tag_name", "").lstrip("v")
                    
                    if latest_version and latest_version != vendor_info["current_version"]:
                        update_info.update({
                            "update_available": True,
                            "latest_version": latest_version,
                            "check_method": "github_api",
                            "release_url": release_data.get("html_url"),
                            "release_notes": release_data.get("body", "")[:500]  # Truncate
                        })
                    
                    update_info["check_method"] = "github_api"
                    
            except Exception as e:
                update_info["error"] = str(e)
                logger.warning(f"Failed to check updates for {vendor_info['description']}: {e}")
        
        return update_info
    
    def analyze_dependency_risks(self, sdk_info: Dict) -> Dict:
        """Analyze risks associated with current SDK versions.
        
        Args:
            sdk_info: SDK information dictionary
            
        Returns:
            Risk analysis results
        """
        risks = []
        recommendations = []
        
        for vendor, info in sdk_info.items():
            # Check for beta/alpha versions
            if "beta" in info["current_version"].lower():
                risks.append({
                    "vendor": vendor,
                    "risk_type": "beta_version",
                    "severity": "medium",
                    "description": f"{info['description']} is using beta version {info['current_version']}",
                    "recommendation": "Monitor for stable release and plan migration testing"
                })
            
            if "alpha" in info["current_version"].lower():
                risks.append({
                    "vendor": vendor,
                    "risk_type": "alpha_version", 
                    "severity": "high",
                    "description": f"{info['description']} is using alpha version {info['current_version']}",
                    "recommendation": "Consider downgrading to stable version if available"
                })
            
            # Check for missing files
            if info["missing_files"]:
                risks.append({
                    "vendor": vendor,
                    "risk_type": "missing_files",
                    "severity": "high",
                    "description": f"Missing SDK files: {', '.join(info['missing_files'])}",
                    "recommendation": "Restore missing SDK files from vendor distribution"
                })
            
            # Check file age (warn if older than 6 months)
            for file_info in info["found_files"]:
                file_date = datetime.fromisoformat(file_info["modified"])
                age_days = (datetime.now() - file_date).days
                
                if age_days > 180:  # 6 months
                    risks.append({
                        "vendor": vendor,
                        "risk_type": "outdated_files",
                        "severity": "low",
                        "description": f"SDK file {file_info['filename']} is {age_days} days old",
                        "recommendation": "Check for vendor updates"
                    })
        
        return {
            "risks": risks,
            "total_risks": len(risks),
            "high_severity_count": len([r for r in risks if r["severity"] == "high"]),
            "medium_severity_count": len([r for r in risks if r["severity"] == "medium"]),
            "low_severity_count": len([r for r in risks if r["severity"] == "low"]),
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def generate_report(self, include_update_check: bool = False) -> Dict:
        """Generate a comprehensive vendor SDK report.
        
        Args:
            include_update_check: Whether to check for updates online
            
        Returns:
            Complete monitoring report
        """
        logger.info("Scanning current vendor SDKs...")
        sdk_info = self.scan_current_sdks()
        
        report = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "project_root": str(self.project_root),
                "libs_directory": str(self.libs_dir),
                "include_update_check": include_update_check
            },
            "vendor_sdks": sdk_info,
            "update_checks": {},
            "risk_analysis": {}
        }
        
        # Check for updates if requested
        if include_update_check:
            logger.info("Checking for vendor SDK updates...")
            for vendor, info in sdk_info.items():
                report["update_checks"][vendor] = self.check_for_updates(info)
        
        # Analyze risks
        logger.info("Analyzing dependency risks...")
        report["risk_analysis"] = self.analyze_dependency_risks(sdk_info)
        
        return report
    
    def save_report(self, report: Dict, filename: Optional[str] = None) -> Path:
        """Save the monitoring report to file.
        
        Args:
            report: Report dictionary to save
            filename: Optional custom filename
            
        Returns:
            Path to saved report file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"vendor_sdk_report_{timestamp}.json"
        
        report_path = self.reports_dir / filename
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Report saved to: {report_path}")
        return report_path
    
    def print_summary(self, report: Dict) -> None:
        """Print a human-readable summary of the report.
        
        Args:
            report: Report dictionary to summarize
        """
        print("\n" + "="*60)
        print("VENDOR SDK MONITORING REPORT")
        print("="*60)
        
        # SDK Status
        print(f"\n📦 VENDOR SDK STATUS:")
        for vendor, info in report["vendor_sdks"].items():
            print(f"\n  {vendor.upper()}:")
            print(f"    Description: {info['description']}")
            print(f"    Current Version: {info['current_version']}")
            print(f"    Risk Level: {info['risk_level']}")
            print(f"    Files Found: {len(info['found_files'])}")
            print(f"    Files Missing: {len(info['missing_files'])}")
            
            if info['missing_files']:
                print(f"    ⚠️  Missing: {', '.join(info['missing_files'])}")
            
            if info.get('notes'):
                print(f"    📝 Notes: {info['notes']}")
        
        # Update Check Results
        if report["update_checks"]:
            print(f"\n🔄 UPDATE CHECK RESULTS:")
            for vendor, update_info in report["update_checks"].items():
                print(f"\n  {vendor.upper()}:")
                if update_info["update_available"]:
                    print(f"    ✅ Update Available: {update_info['latest_version']}")
                    if update_info.get("release_url"):
                        print(f"    🔗 Release URL: {update_info['release_url']}")
                else:
                    print(f"    ✅ Up to date: {update_info['latest_version']}")
                
                if update_info.get("error"):
                    print(f"    ❌ Check Error: {update_info['error']}")
        
        # Risk Analysis
        risk_analysis = report["risk_analysis"]
        print(f"\n⚠️  RISK ANALYSIS:")
        print(f"    Total Risks: {risk_analysis['total_risks']}")
        print(f"    High Severity: {risk_analysis['high_severity_count']}")
        print(f"    Medium Severity: {risk_analysis['medium_severity_count']}")
        print(f"    Low Severity: {risk_analysis['low_severity_count']}")
        
        if risk_analysis["risks"]:
            print(f"\n    📋 Risk Details:")
            for risk in risk_analysis["risks"]:
                severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                icon = severity_icon.get(risk["severity"], "⚪")
                print(f"      {icon} {risk['risk_type'].upper()}: {risk['description']}")
                print(f"         💡 {risk['recommendation']}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        print(f"    1. Run this script weekly to monitor vendor SDK status")
        print(f"    2. Subscribe to vendor release notifications where possible")
        print(f"    3. Test new SDK versions in staging before production deployment")
        print(f"    4. Document any custom modifications to vendor SDKs")
        print(f"    5. Maintain backup copies of working SDK versions")
        
        print("\n" + "="*60)


def main():
    """Main entry point for the vendor SDK monitoring script."""
    parser = argparse.ArgumentParser(
        description="Monitor vendor SDK versions and health",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/monitor_vendor_sdks.py                    # Basic scan
  python scripts/monitor_vendor_sdks.py --check-updates   # Include update checks
  python scripts/monitor_vendor_sdks.py --generate-report # Save detailed report
        """
    )
    
    parser.add_argument(
        "--check-updates",
        action="store_true",
        help="Check for available updates online (requires internet)"
    )
    
    parser.add_argument(
        "--generate-report",
        action="store_true", 
        help="Generate and save detailed JSON report"
    )
    
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).parent.parent,
        help="Project root directory (default: auto-detect)"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress console output (useful for CI/CD)"
    )
    
    args = parser.parse_args()
    
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    
    try:
        # Initialize monitor
        monitor = VendorSDKMonitor(args.project_root)
        
        # Generate report
        report = monitor.generate_report(include_update_check=args.check_updates)
        
        # Save report if requested
        if args.generate_report:
            report_path = monitor.save_report(report)
            if not args.quiet:
                print(f"\n📄 Detailed report saved: {report_path}")
        
        # Print summary unless quiet
        if not args.quiet:
            monitor.print_summary(report)
        
        # Exit with error code if high severity risks found
        risk_analysis = report["risk_analysis"]
        if risk_analysis["high_severity_count"] > 0:
            logger.error(f"Found {risk_analysis['high_severity_count']} high severity risks")
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"Monitoring failed: {e}")
        if not args.quiet:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()