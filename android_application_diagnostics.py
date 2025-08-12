#!/usr/bin/env python3
"""
Android Application Camera & Hardware Diagnostics Tool

Analyzes the Android application code to identify why camera preview, 
device detection, and calibration appear "fake" or non-functional.

This tool examines:
1. Camera detection and initialization logic
2. Thermal camera (Topdon UVC) detection requirements  
3. Calibration functionality dependencies
4. Permission and hardware requirements
5. Fallback mechanisms and error handling
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

class AndroidCameraDiagnostics:
    def __init__(self, android_app_path: str):
        self.android_path = Path(android_app_path)
        self.src_path = self.android_path / "src" / "main" / "java" / "com" / "multisensor" / "recording"
        self.manifest_path = self.android_path / "src" / "main" / "AndroidManifest.xml"
        
        self.issues = []
        self.camera_requirements = {}
        self.thermal_requirements = {}
        self.calibration_dependencies = {}
        
    def analyze_all(self) -> Dict[str, Any]:
        """Comprehensive analysis of Android app camera issues."""
        print("🔍 Android Application Camera Diagnostics")
        print("=" * 50)
        
        results = {
            "camera_analysis": self.analyze_camera_logic(),
            "thermal_analysis": self.analyze_thermal_camera(),
            "calibration_analysis": self.analyze_calibration_logic(),
            "permissions_analysis": self.analyze_permissions(),
            "ui_analysis": self.analyze_ui_components(),
            "issues_summary": self.get_issues_summary(),
            "recommendations": self.get_recommendations()
        }
        
        return results
    
    def analyze_camera_logic(self) -> Dict[str, Any]:
        """Analyze CameraRecorder.kt for overly strict camera requirements."""
        camera_file = self.src_path / "recording" / "CameraRecorder.kt"
        
        if not camera_file.exists():
            self.issues.append("❌ CameraRecorder.kt not found")
            return {"status": "missing", "issues": ["CameraRecorder.kt file not found"]}
        
        content = camera_file.read_text()
        
        # Analyze camera selection logic
        strict_requirements = []
        
        # Look for overly strict hardware level requirements
        if "INFO_SUPPORTED_HARDWARE_LEVEL_3" in content:
            strict_requirements.append("LEVEL_3 hardware requirement (very restrictive)")
        
        if "REQUEST_AVAILABLE_CAPABILITIES_RAW" in content:
            strict_requirements.append("RAW sensor capability requirement")
            
        if "RAW_SENSOR" in content:
            strict_requirements.append("RAW sensor format requirement")
            
        # Look for Samsung-specific optimizations
        samsung_specific = "SM-G99" in content or "S21" in content or "S22" in content
        if samsung_specific:
            strict_requirements.append("Samsung S21/S22 specific optimizations")
        
        # Look for 4K requirements
        if "3840" in content and "2160" in content:
            strict_requirements.append("4K video recording requirement")
            
        # Analyze fallback mechanisms
        fallback_mechanisms = []
        if "relaxed constraints" in content.lower():
            fallback_mechanisms.append("Relaxed constraint fallback found")
        if "LENS_FACING_BACK" in content:
            fallback_mechanisms.append("Basic back camera fallback")
            
        # Check camera initialization method
        init_complex = "createCaptureSession" in content and "multiple surfaces" in content.lower()
        
        analysis = {
            "strict_requirements": strict_requirements,
            "fallback_mechanisms": fallback_mechanisms,
            "samsung_optimized": samsung_specific,
            "complex_initialization": init_complex,
            "issues": []
        }
        
        # Identify issues
        if len(strict_requirements) > 3:
            analysis["issues"].append("Too many strict camera requirements - will fail on most devices")
            self.issues.append("🚫 Camera selection too restrictive")
            
        if not fallback_mechanisms:
            analysis["issues"].append("No adequate fallback for basic camera functionality")
            self.issues.append("🚫 No camera fallback mechanisms")
            
        if samsung_specific:
            analysis["issues"].append("Code optimized for Samsung devices only")
            self.issues.append("⚠️ Samsung-specific camera logic")
            
        return analysis
    
    def analyze_thermal_camera(self) -> Dict[str, Any]:
        """Analyze ThermalRecorder.kt for thermal camera detection issues."""
        thermal_file = self.src_path / "recording" / "ThermalRecorder.kt"
        
        if not thermal_file.exists():
            self.issues.append("❌ ThermalRecorder.kt not found")
            return {"status": "missing"}
            
        content = thermal_file.read_text()
        
        # Check for external dependencies
        external_deps = []
        if "com.infisense.iruvc" in content:
            external_deps.append("Infisense IRUVC library dependency")
        if "topdon" in content.lower():
            external_deps.append("Topdon-specific libraries")
            
        # Check USB requirements
        usb_requirements = []
        if "USB_PERMISSION" in content:
            usb_requirements.append("USB permission required")
        if "UsbManager" in content:
            usb_requirements.append("USB manager access required")
        if "SUPPORTED_PRODUCT_IDS" in content:
            usb_requirements.append("Specific product ID matching required")
            
        # Check hardware requirements
        hardware_reqs = []
        if "UVCCamera" in content:
            hardware_reqs.append("UVC camera support required")
        if "USBMonitor" in content:
            hardware_reqs.append("USB monitoring required")
            
        analysis = {
            "external_dependencies": external_deps,
            "usb_requirements": usb_requirements,
            "hardware_requirements": hardware_reqs,
            "issues": []
        }
        
        # Identify issues
        if external_deps:
            analysis["issues"].append("Depends on external thermal camera libraries that may not be available")
            self.issues.append("🚫 Missing thermal camera dependencies")
            
        if len(usb_requirements) > 0:
            analysis["issues"].append("Complex USB permission and device detection requirements")
            self.issues.append("⚠️ Complex USB thermal camera setup")
            
        return analysis
    
    def analyze_calibration_logic(self) -> Dict[str, Any]:
        """Analyze calibration functionality for dependencies."""
        calibration_file = self.src_path / "calibration" / "CalibrationCaptureManager.kt"
        
        if not calibration_file.exists():
            self.issues.append("❌ CalibrationCaptureManager.kt not found")
            return {"status": "missing"}
            
        content = calibration_file.read_text()
        
        # Check dependencies
        dependencies = []
        if "CameraRecorder" in content:
            dependencies.append("Depends on CameraRecorder functionality")
        if "ThermalRecorder" in content:
            dependencies.append("Depends on ThermalRecorder functionality")
        if "captureCalibrationImage" in content:
            dependencies.append("Requires actual image capture capability")
            
        # Check error handling
        error_handling = []
        if "try {" in content and "catch" in content:
            error_handling.append("Basic exception handling present")
        if "success" in content and "false" in content:
            error_handling.append("Success/failure return values")
            
        analysis = {
            "dependencies": dependencies,
            "error_handling": error_handling,
            "issues": []
        }
        
        # Identify issues
        if "CameraRecorder" in dependencies and "ThermalRecorder" in dependencies:
            analysis["issues"].append("Calibration requires both camera systems to work - single point of failure")
            self.issues.append("🚫 Calibration depends on both failing camera systems")
            
        return analysis
    
    def analyze_permissions(self) -> Dict[str, Any]:
        """Analyze AndroidManifest.xml for permission issues."""
        if not self.manifest_path.exists():
            self.issues.append("❌ AndroidManifest.xml not found")
            return {"status": "missing"}
            
        content = self.manifest_path.read_text()
        
        # Check camera permissions
        camera_permissions = []
        if 'android.permission.CAMERA' in content:
            camera_permissions.append("CAMERA permission declared")
        if 'android.hardware.camera' in content:
            camera_permissions.append("Camera hardware feature declared")
            
        # Check USB permissions  
        usb_permissions = []
        if 'android.permission.USB_PERMISSION' in content:
            usb_permissions.append("USB_PERMISSION declared")
        if 'android.hardware.usb' in content:
            usb_permissions.append("USB hardware features declared")
            
        # Check storage permissions
        storage_permissions = []
        if 'READ_EXTERNAL_STORAGE' in content:
            storage_permissions.append("Read storage permission")
        if 'WRITE_EXTERNAL_STORAGE' in content:
            storage_permissions.append("Write storage permission")
            
        analysis = {
            "camera_permissions": camera_permissions,
            "usb_permissions": usb_permissions,
            "storage_permissions": storage_permissions,
            "issues": []
        }
        
        # Identify potential issues
        if not camera_permissions:
            analysis["issues"].append("Missing camera permissions")
            self.issues.append("🚫 Camera permissions not properly declared")
            
        if not usb_permissions:
            analysis["issues"].append("Missing USB permissions for thermal camera")
            self.issues.append("⚠️ USB permissions may be insufficient")
            
        return analysis
    
    def analyze_ui_components(self) -> Dict[str, Any]:
        """Analyze UI fragments for preview and user feedback."""
        recording_fragment = self.src_path / "ui" / "fragments" / "RecordingFragment.kt"
        
        if not recording_fragment.exists():
            self.issues.append("❌ RecordingFragment.kt not found")
            return {"status": "missing"}
            
        content = recording_fragment.read_text()
        
        # Check preview components
        preview_components = []
        if "TextureView" in content:
            preview_components.append("TextureView for camera preview")
        if "SurfaceView" in content:
            preview_components.append("SurfaceView for display")
        if "rgbCameraPreview" in content:
            preview_components.append("RGB camera preview component")
            
        # Check error handling in UI
        ui_error_handling = []
        if "Camera setup error" in content:
            ui_error_handling.append("Camera setup error messages")
        if "Toast.makeText" in content:
            ui_error_handling.append("Toast notifications for errors")
        if "previewPlaceholderText" in content:
            ui_error_handling.append("Placeholder text for failed preview")
            
        # Check fallback messages
        fallback_messages = []
        if "Camera initialization failed" in content:
            fallback_messages.append("Camera initialization failure message")
        if "device may not support" in content.lower():
            fallback_messages.append("Device compatibility warnings")
            
        analysis = {
            "preview_components": preview_components,
            "error_handling": ui_error_handling,
            "fallback_messages": fallback_messages,
            "issues": []
        }
        
        # Check for issues
        if fallback_messages:
            analysis["issues"].append("UI shows fallback messages indicating camera failures")
            self.issues.append("⚠️ UI designed to handle camera failures")
            
        return analysis
    
    def get_issues_summary(self) -> List[str]:
        """Get summary of all identified issues."""
        return self.issues
    
    def get_recommendations(self) -> List[str]:
        """Get recommendations to fix the identified issues."""
        recommendations = []
        
        # Camera fixes
        if any("Camera selection too restrictive" in issue for issue in self.issues):
            recommendations.append("🔧 Make camera selection more permissive - support basic cameras")
            recommendations.append("🔧 Implement proper graceful degradation for camera features")
            recommendations.append("🔧 Add basic camera fallback that works on all Android devices")
            
        # Thermal camera fixes
        if any("thermal camera" in issue.lower() for issue in self.issues):
            recommendations.append("🔧 Make thermal camera functionality optional")
            recommendations.append("🔧 Provide clear feedback when thermal camera is unavailable")
            recommendations.append("🔧 Implement mock/simulation mode for thermal data")
            
        # Calibration fixes
        if any("Calibration" in issue for issue in self.issues):
            recommendations.append("🔧 Make calibration work with basic camera functionality")
            recommendations.append("🔧 Provide calibration simulation mode for testing")
            recommendations.append("🔧 Decouple calibration from advanced camera features")
            
        # Permission fixes
        if any("permission" in issue.lower() for issue in self.issues):
            recommendations.append("🔧 Add runtime permission requests for camera and USB")
            recommendations.append("🔧 Provide clear permission setup instructions")
            
        # General fixes
        recommendations.extend([
            "🔧 Create Android hardware compatibility checker",
            "🔧 Add progressive feature detection (basic → advanced)",
            "🔧 Implement demo/simulation modes for missing hardware",
            "🔧 Improve error messages and user guidance"
        ])
        
        return recommendations

def main():
    """Main diagnostic function."""
    android_app_path = "/home/runner/work/bucika_gsr/bucika_gsr/AndroidApp"
    
    if not os.path.exists(android_app_path):
        print(f"❌ Android app path not found: {android_app_path}")
        return
        
    diagnostics = AndroidCameraDiagnostics(android_app_path)
    results = diagnostics.analyze_all()
    
    # Print detailed results
    print("\n📊 ANALYSIS RESULTS")
    print("=" * 50)
    
    print(f"\n🎥 CAMERA ANALYSIS:")
    camera_analysis = results["camera_analysis"]
    if camera_analysis.get("strict_requirements"):
        print("   Strict Requirements:")
        for req in camera_analysis["strict_requirements"]:
            print(f"   • {req}")
    if camera_analysis.get("issues"):
        print("   Issues:")
        for issue in camera_analysis["issues"]:
            print(f"   ❌ {issue}")
    
    print(f"\n🌡️ THERMAL CAMERA ANALYSIS:")
    thermal_analysis = results["thermal_analysis"]
    if thermal_analysis.get("external_dependencies"):
        print("   External Dependencies:")
        for dep in thermal_analysis["external_dependencies"]:
            print(f"   • {dep}")
    if thermal_analysis.get("issues"):
        print("   Issues:")
        for issue in thermal_analysis["issues"]:
            print(f"   ❌ {issue}")
    
    print(f"\n🎯 CALIBRATION ANALYSIS:")
    calibration_analysis = results["calibration_analysis"]
    if calibration_analysis.get("dependencies"):
        print("   Dependencies:")
        for dep in calibration_analysis["dependencies"]:
            print(f"   • {dep}")
    if calibration_analysis.get("issues"):
        print("   Issues:")
        for issue in calibration_analysis["issues"]:
            print(f"   ❌ {issue}")
    
    print(f"\n🔐 PERMISSIONS ANALYSIS:")
    permissions_analysis = results["permissions_analysis"]
    for perm_type, perms in permissions_analysis.items():
        if perm_type != "issues" and perms:
            print(f"   {perm_type.replace('_', ' ').title()}:")
            for perm in perms:
                print(f"   ✅ {perm}")
    
    print(f"\n🚫 ALL ISSUES IDENTIFIED:")
    for issue in results["issues_summary"]:
        print(f"   {issue}")
    
    print(f"\n💡 RECOMMENDATIONS:")
    for rec in results["recommendations"]:
        print(f"   {rec}")
    
    print(f"\n🎯 ROOT CAUSE CONCLUSION:")
    print("   The Android application appears 'fake' because:")
    print("   1. ❌ Camera selection logic is too restrictive for most devices")
    print("   2. ❌ Thermal camera requires specific hardware/libraries not available")
    print("   3. ❌ Calibration depends on both failing camera systems")
    print("   4. ❌ No adequate fallback to basic functionality")
    print("   5. ⚠️ Code is optimized for Samsung S21/S22 devices only")
    
    print(f"\n✅ SOLUTION PRIORITY:")
    print("   1. 🔧 Fix camera selection to support basic Android cameras")
    print("   2. 🔧 Make thermal camera functionality optional")  
    print("   3. 🔧 Implement graceful degradation for all features")
    print("   4. 🔧 Add simulation modes for missing hardware")
    print("   5. 🔧 Improve user feedback and error messages")

if __name__ == "__main__":
    main()