#!/usr/bin/env python3

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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VendorSDKMonitor:
    
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
            "update_check_url": None,
            "risk_level": "low",
            "notes": "Proprietary SDK - manual monitoring required"
        }
    }
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.libs_dir = project_root / "AndroidApp" / "src" / "main" / "libs"
        self.reports_dir = project_root / "security_reports"
        
        self.reports_dir.mkdir(exist_ok=True)
    
    def scan_current_sdks(self) -> Dict[str, Dict]:
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
        update_info = {
            "update_available": False,
            "latest_version": vendor_info["current_version"],
            "check_method": "manual",
            "check_timestamp": datetime.now().isoformat(),
            "error": None
        }
        
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
                            "release_notes": release_data.get("body", "")[:500]
                        })
                    
                    update_info["check_method"] = "github_api"
                    
            except Exception as e:
                update_info["error"] = str(e)
                logger.warning(f"Failed to check updates for {vendor_info['description']}: {e}")
        
        return update_info
    
    def analyze_dependency_risks(self, sdk_info: Dict) -> Dict:
        risks = []
        recommendations = []
        
        for vendor, info in sdk_info.items():
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
            
            if info["missing_files"]:
                risks.append({
                    "vendor": vendor,
                    "risk_type": "missing_files",
                    "severity": "high",
                    "description": f"Missing SDK files: {', '.join(info['missing_files'])}",
                    "recommendation": "Restore missing SDK files from vendor distribution"
                })
            
            for file_info in info["found_files"]:
                file_date = datetime.fromisoformat(file_info["modified"])
                age_days = (datetime.now() - file_date).days
                
                if age_days > 180:
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
        
        if include_update_check:
            logger.info("Checking for vendor SDK updates...")
            for vendor, info in sdk_info.items():
                report["update_checks"][vendor] = self.check_for_updates(info)
        
        logger.info("Analyzing dependency risks...")
        report["risk_analysis"] = self.analyze_dependency_risks(sdk_info)
        
        return report
    
    def save_report(self, report: Dict, filename: Optional[str] = None) -> Path:
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"vendor_sdk_report_{timestamp}.json"
        
        report_path = self.reports_dir / filename
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Report saved to: {report_path}")
        return report_path
    
    def print_summary(self, report: Dict) -> None:
        print("\n" + "="*60)
        print("VENDOR SDK MONITORING REPORT")
        print("="*60)
        
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
        
        print(f"\n💡 RECOMMENDATIONS:")
        print(f"    1. Run this script weekly to monitor vendor SDK status")
        print(f"    2. Subscribe to vendor release notifications where possible")
        print(f"    3. Test new SDK versions in staging before production deployment")
        print(f"    4. Document any custom modifications to vendor SDKs")
        print(f"    5. Maintain backup copies of working SDK versions")
        
        print("\n" + "="*60)


def main():
    parser = argparse.ArgumentParser(
        description="Monitor vendor SDK versions and health",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/monitor_vendor_sdks.py
  python scripts/monitor_vendor_sdks.py --check-updates
  python scripts/monitor_vendor_sdks.py --generate-report
"""
    )
    
    parser.add_argument('--check-updates', action='store_true',
                        help='Check for SDK updates online')
    parser.add_argument('--generate-report', action='store_true',
                        help='Generate detailed health report')
    
    args = parser.parse_args()
    
    try:
        monitor = VendorSDKMonitor()
        
        if args.check_updates:
            monitor.check_for_updates()
        
        if args.generate_report:
            monitor.generate_health_report()
        
        # Always run basic monitoring
        monitor.monitor_all_sdks()
        
        logger.info("Vendor SDK monitoring completed successfully")
        
    except Exception as e:
        logger.error(f"Vendor SDK monitoring failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
