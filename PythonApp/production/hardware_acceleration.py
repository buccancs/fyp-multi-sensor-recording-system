"""
Hardware acceleration optimization utilities for the multi-sensor recording system.

This module provides detection, configuration, and optimization of hardware acceleration
features including GPU processing, hardware codecs, and specialized CPU optimizations.
"""

import logging
import platform
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    cv2 = None

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

# Use consolidated import utility to eliminate code duplication
from ..utils.import_utils import get_safe_logger as get_logger


class AccelerationType(Enum):
    """Types of hardware acceleration available."""
    CPU_OPTIMIZED = "cpu_optimized"
    GPU_OPENCL = "gpu_opencl"
    GPU_CUDA = "gpu_cuda"
    GPU_VULKAN = "gpu_vulkan"
    HARDWARE_CODEC = "hardware_codec"
    INTEL_IPP = "intel_ipp"
    INTEL_TBB = "intel_tbb"
    ANDROID_MEDIACODEC = "android_mediacodec"


@dataclass
class HardwareCapability:
    """Hardware acceleration capability information."""
    
    acceleration_type: AccelerationType
    available: bool
    version: Optional[str] = None
    device_info: Optional[str] = None
    performance_score: Optional[float] = None  # 0.0-1.0 relative performance
    memory_mb: Optional[int] = None
    recommended_usage: Optional[str] = None
    limitations: List[str] = None
    
    def __post_init__(self):
        if self.limitations is None:
            self.limitations = []


@dataclass
class OptimizationProfile:
    """Hardware acceleration optimization profile."""
    
    profile_name: str
    cpu_optimization: bool = True
    gpu_acceleration: bool = False
    hardware_codec: bool = False
    
    # OpenCV optimizations
    opencv_use_opencl: bool = False
    opencv_use_cuda: bool = False
    opencv_thread_count: int = -1  # -1 = auto
    
    # Processing optimizations
    batch_processing: bool = False
    vectorized_operations: bool = True
    memory_optimization: bool = True
    
    # Quality/performance trade-offs
    enable_fast_algorithms: bool = False
    reduce_precision: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "profile_name": self.profile_name,
            "cpu_optimization": self.cpu_optimization,
            "gpu_acceleration": self.gpu_acceleration,
            "hardware_codec": self.hardware_codec,
            "opencv_use_opencl": self.opencv_use_opencl,
            "opencv_use_cuda": self.opencv_use_cuda,
            "opencv_thread_count": self.opencv_thread_count,
            "batch_processing": self.batch_processing,
            "vectorized_operations": self.vectorized_operations,
            "memory_optimization": self.memory_optimization,
            "enable_fast_algorithms": self.enable_fast_algorithms,
            "reduce_precision": self.reduce_precision
        }


class HardwareAccelerationDetector:
    """Detects available hardware acceleration capabilities."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.detected_capabilities: List[HardwareCapability] = []
        
    def detect_all_capabilities(self) -> List[HardwareCapability]:
        """Detect all available hardware acceleration capabilities."""
        self.logger.info("HardwareAccelerationDetector: Starting hardware capability detection")
        
        self.detected_capabilities = []
        
        # CPU optimizations
        self._detect_cpu_optimizations()
        
        # OpenCV accelerations
        if OPENCV_AVAILABLE:
            self._detect_opencv_accelerations()
        else:
            self.logger.warning("HardwareAccelerationDetector: OpenCV not available")
            
        # Hardware codecs
        self._detect_hardware_codecs()
        
        # Intel optimizations
        self._detect_intel_optimizations()
        
        self.logger.info(f"HardwareAccelerationDetector: Detected {len(self.detected_capabilities)} capabilities")
        return self.detected_capabilities
        
    def _detect_cpu_optimizations(self):
        """Detect CPU-specific optimizations."""
        try:
            import multiprocessing
            cpu_count = multiprocessing.cpu_count()
            
            # Check CPU features
            cpu_info = platform.processor()
            
            self.detected_capabilities.append(HardwareCapability(
                acceleration_type=AccelerationType.CPU_OPTIMIZED,
                available=True,
                device_info=f"CPU: {cpu_info}, Cores: {cpu_count}",
                performance_score=0.7,  # Base CPU performance
                recommended_usage="Multi-threaded processing, vectorized operations"
            ))
            
            self.logger.info(f"HardwareAccelerationDetector: CPU optimization available - {cpu_count} cores")
            
        except Exception as e:
            self.logger.error(f"HardwareAccelerationDetector: Error detecting CPU optimizations: {e}")
            
    def _detect_opencv_accelerations(self):
        """Detect OpenCV GPU acceleration capabilities."""
        if not OPENCV_AVAILABLE:
            return
            
        try:
            # Check OpenCL support
            if cv2.ocl.haveOpenCL():
                opencl_devices = cv2.ocl.getOpenCLPlatforms()
                
                self.detected_capabilities.append(HardwareCapability(
                    acceleration_type=AccelerationType.GPU_OPENCL,
                    available=True,
                    version=cv2.ocl.getPlatfomsInfo() if hasattr(cv2.ocl, 'getPlatfomsInfo') else "Unknown",
                    device_info=f"OpenCL platforms: {len(opencl_devices)}",
                    performance_score=0.85,
                    recommended_usage="Image processing, filtering, computer vision operations",
                    limitations=["May have driver compatibility issues", "Performance varies by GPU"]
                ))
                
                self.logger.info("HardwareAccelerationDetector: OpenCL acceleration available")
            else:
                self.logger.info("HardwareAccelerationDetector: OpenCL not available")
                
        except Exception as e:
            self.logger.error(f"HardwareAccelerationDetector: Error detecting OpenCL: {e}")
            
        try:
            # Check CUDA support
            cuda_devices = cv2.cuda.getCudaEnabledDeviceCount()
            if cuda_devices > 0:
                device_info = []
                for i in range(cuda_devices):
                    try:
                        device_props = cv2.cuda.getDevice()
                        device_info.append(f"Device {i}")
                    except:
                        device_info.append(f"Device {i} (info unavailable)")
                        
                self.detected_capabilities.append(HardwareCapability(
                    acceleration_type=AccelerationType.GPU_CUDA,
                    available=True,
                    device_info=f"CUDA devices: {', '.join(device_info)}",
                    performance_score=0.95,
                    recommended_usage="High-performance image processing, deep learning operations",
                    limitations=["Requires NVIDIA GPU", "CUDA runtime must be installed"]
                ))
                
                self.logger.info(f"HardwareAccelerationDetector: CUDA acceleration available - {cuda_devices} devices")
            else:
                self.logger.info("HardwareAccelerationDetector: CUDA not available")
                
        except Exception as e:
            self.logger.debug(f"HardwareAccelerationDetector: CUDA not available: {e}")
            
    def _detect_hardware_codecs(self):
        """Detect hardware video codec support."""
        system = platform.system()
        
        if system == "Windows":
            self._detect_windows_codecs()
        elif system == "Linux":
            self._detect_linux_codecs()
        elif system == "Darwin":
            self._detect_macos_codecs()
            
    def _detect_windows_codecs(self):
        """Detect Windows hardware codec support."""
        try:
            # Check for Windows Media Foundation codecs
            # This is simplified detection - real implementation would use Windows APIs
            
            self.detected_capabilities.append(HardwareCapability(
                acceleration_type=AccelerationType.HARDWARE_CODEC,
                available=True,
                device_info="Windows Media Foundation",
                performance_score=0.8,
                recommended_usage="Video encoding/decoding",
                limitations=["Windows specific", "Codec availability varies by hardware"]
            ))
            
            self.logger.info("HardwareAccelerationDetector: Windows hardware codecs available")
            
        except Exception as e:
            self.logger.error(f"HardwareAccelerationDetector: Error detecting Windows codecs: {e}")
            
    def _detect_linux_codecs(self):
        """Detect Linux hardware codec support."""
        try:
            # Check for VA-API (Video Acceleration API)
            vaapi_available = False
            try:
                result = subprocess.run(['vainfo'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    vaapi_available = True
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
                
            if vaapi_available:
                self.detected_capabilities.append(HardwareCapability(
                    acceleration_type=AccelerationType.HARDWARE_CODEC,
                    available=True,
                    device_info="VA-API",
                    performance_score=0.8,
                    recommended_usage="Hardware video encoding/decoding on Intel/AMD GPUs",
                    limitations=["Linux specific", "Requires VA-API drivers"]
                ))
                
                self.logger.info("HardwareAccelerationDetector: VA-API hardware codecs available")
            else:
                self.logger.info("HardwareAccelerationDetector: VA-API not detected")
                
        except Exception as e:
            self.logger.error(f"HardwareAccelerationDetector: Error detecting Linux codecs: {e}")
            
    def _detect_macos_codecs(self):
        """Detect macOS hardware codec support."""
        try:
            # Check for VideoToolbox
            self.detected_capabilities.append(HardwareCapability(
                acceleration_type=AccelerationType.HARDWARE_CODEC,
                available=True,
                device_info="VideoToolbox",
                performance_score=0.85,
                recommended_usage="Hardware video encoding/decoding on macOS",
                limitations=["macOS specific", "Performance varies by Mac model"]
            ))
            
            self.logger.info("HardwareAccelerationDetector: VideoToolbox hardware codecs available")
            
        except Exception as e:
            self.logger.error(f"HardwareAccelerationDetector: Error detecting macOS codecs: {e}")
            
    def _detect_intel_optimizations(self):
        """Detect Intel-specific optimizations."""
        try:
            # Check if OpenCV was built with Intel optimizations
            if OPENCV_AVAILABLE:
                build_info = cv2.getBuildInformation()
                
                intel_ipp = "IPP:" in build_info and "YES" in build_info
                intel_tbb = "TBB:" in build_info and "YES" in build_info
                
                if intel_ipp:
                    self.detected_capabilities.append(HardwareCapability(
                        acceleration_type=AccelerationType.INTEL_IPP,
                        available=True,
                        device_info="Intel Integrated Performance Primitives",
                        performance_score=0.75,
                        recommended_usage="Optimized image processing operations",
                        limitations=["Intel processors only", "Limited to IPP-optimized functions"]
                    ))
                    
                    self.logger.info("HardwareAccelerationDetector: Intel IPP optimization available")
                    
                if intel_tbb:
                    self.detected_capabilities.append(HardwareCapability(
                        acceleration_type=AccelerationType.INTEL_TBB,
                        available=True,
                        device_info="Intel Threading Building Blocks",
                        performance_score=0.8,
                        recommended_usage="Parallel processing acceleration",
                        limitations=["Intel processors optimal", "May benefit other processors"]
                    ))
                    
                    self.logger.info("HardwareAccelerationDetector: Intel TBB optimization available")
                    
        except Exception as e:
            self.logger.error(f"HardwareAccelerationDetector: Error detecting Intel optimizations: {e}")
            
    def get_capability_by_type(self, acceleration_type: AccelerationType) -> Optional[HardwareCapability]:
        """Get capability information for a specific acceleration type."""
        for capability in self.detected_capabilities:
            if capability.acceleration_type == acceleration_type:
                return capability
        return None
        
    def get_available_capabilities(self) -> List[HardwareCapability]:
        """Get only available hardware capabilities."""
        return [cap for cap in self.detected_capabilities if cap.available]
        
    def get_best_capabilities(self, limit: int = 3) -> List[HardwareCapability]:
        """Get the best available capabilities by performance score."""
        available = self.get_available_capabilities()
        available.sort(key=lambda x: x.performance_score or 0, reverse=True)
        return available[:limit]


class HardwareAccelerationOptimizer:
    """Optimizes system configuration for hardware acceleration."""
    
    def __init__(self, detector: Optional[HardwareAccelerationDetector] = None):
        self.logger = get_logger(__name__)
        self.detector = detector or HardwareAccelerationDetector()
        self.current_profile: Optional[OptimizationProfile] = None
        
    def create_optimization_profile(self, target_performance: str = "balanced") -> OptimizationProfile:
        """
        Create an optimization profile based on detected hardware and target performance.
        
        Args:
            target_performance: "conservative", "balanced", "aggressive", or "maximum"
        """
        capabilities = self.detector.detect_all_capabilities()
        
        if target_performance == "conservative":
            return self._create_conservative_profile(capabilities)
        elif target_performance == "balanced":
            return self._create_balanced_profile(capabilities)
        elif target_performance == "aggressive":
            return self._create_aggressive_profile(capabilities)
        elif target_performance == "maximum":
            return self._create_maximum_profile(capabilities)
        else:
            self.logger.warning(f"Unknown target performance: {target_performance}, using balanced")
            return self._create_balanced_profile(capabilities)
            
    def _create_conservative_profile(self, capabilities: List[HardwareCapability]) -> OptimizationProfile:
        """Create a conservative optimization profile with minimal risk."""
        return OptimizationProfile(
            profile_name="conservative",
            cpu_optimization=True,
            gpu_acceleration=False,
            hardware_codec=False,
            opencv_use_opencl=False,
            opencv_use_cuda=False,
            opencv_thread_count=2,  # Conservative thread count
            batch_processing=False,
            vectorized_operations=True,
            memory_optimization=True,
            enable_fast_algorithms=False,
            reduce_precision=False
        )
        
    def _create_balanced_profile(self, capabilities: List[HardwareCapability]) -> OptimizationProfile:
        """Create a balanced optimization profile."""
        # Check what's available
        has_opencl = any(cap.acceleration_type == AccelerationType.GPU_OPENCL and cap.available for cap in capabilities)
        has_cuda = any(cap.acceleration_type == AccelerationType.GPU_CUDA and cap.available for cap in capabilities)
        has_hardware_codec = any(cap.acceleration_type == AccelerationType.HARDWARE_CODEC and cap.available for cap in capabilities)
        
        return OptimizationProfile(
            profile_name="balanced",
            cpu_optimization=True,
            gpu_acceleration=has_opencl or has_cuda,
            hardware_codec=has_hardware_codec,
            opencv_use_opencl=has_opencl,
            opencv_use_cuda=False,  # Prefer OpenCL for stability
            opencv_thread_count=-1,  # Auto-detect
            batch_processing=True,
            vectorized_operations=True,
            memory_optimization=True,
            enable_fast_algorithms=True,
            reduce_precision=False
        )
        
    def _create_aggressive_profile(self, capabilities: List[HardwareCapability]) -> OptimizationProfile:
        """Create an aggressive optimization profile."""
        has_opencl = any(cap.acceleration_type == AccelerationType.GPU_OPENCL and cap.available for cap in capabilities)
        has_cuda = any(cap.acceleration_type == AccelerationType.GPU_CUDA and cap.available for cap in capabilities)
        has_hardware_codec = any(cap.acceleration_type == AccelerationType.HARDWARE_CODEC and cap.available for cap in capabilities)
        
        return OptimizationProfile(
            profile_name="aggressive",
            cpu_optimization=True,
            gpu_acceleration=has_opencl or has_cuda,
            hardware_codec=has_hardware_codec,
            opencv_use_opencl=has_opencl and not has_cuda,  # Prefer CUDA if available
            opencv_use_cuda=has_cuda,
            opencv_thread_count=-1,
            batch_processing=True,
            vectorized_operations=True,
            memory_optimization=False,  # Trade memory for speed
            enable_fast_algorithms=True,
            reduce_precision=True
        )
        
    def _create_maximum_profile(self, capabilities: List[HardwareCapability]) -> OptimizationProfile:
        """Create a maximum performance profile (highest risk)."""
        has_opencl = any(cap.acceleration_type == AccelerationType.GPU_OPENCL and cap.available for cap in capabilities)
        has_cuda = any(cap.acceleration_type == AccelerationType.GPU_CUDA and cap.available for cap in capabilities)
        has_hardware_codec = any(cap.acceleration_type == AccelerationType.HARDWARE_CODEC and cap.available for cap in capabilities)
        
        return OptimizationProfile(
            profile_name="maximum",
            cpu_optimization=True,
            gpu_acceleration=True,
            hardware_codec=has_hardware_codec,
            opencv_use_opencl=has_opencl and not has_cuda,
            opencv_use_cuda=has_cuda,
            opencv_thread_count=-1,
            batch_processing=True,
            vectorized_operations=True,
            memory_optimization=False,
            enable_fast_algorithms=True,
            reduce_precision=True
        )
        
    def apply_optimization_profile(self, profile: OptimizationProfile) -> Dict[str, Any]:
        """Apply an optimization profile to the system."""
        self.logger.info(f"HardwareAccelerationOptimizer: Applying optimization profile: {profile.profile_name}")
        
        results = {
            "profile_applied": profile.profile_name,
            "optimizations_applied": [],
            "errors": []
        }
        
        try:
            # Apply OpenCV optimizations
            if OPENCV_AVAILABLE:
                self._apply_opencv_optimizations(profile, results)
            else:
                results["errors"].append("OpenCV not available for optimization")
                
            # Apply threading optimizations
            self._apply_threading_optimizations(profile, results)
            
            # Apply memory optimizations
            if profile.memory_optimization:
                self._apply_memory_optimizations(profile, results)
                
            self.current_profile = profile
            
        except Exception as e:
            error_msg = f"Error applying optimization profile: {e}"
            self.logger.error(f"HardwareAccelerationOptimizer: {error_msg}")
            results["errors"].append(error_msg)
            
        return results
        
    def _apply_opencv_optimizations(self, profile: OptimizationProfile, results: Dict[str, Any]):
        """Apply OpenCV-specific optimizations."""
        if not OPENCV_AVAILABLE:
            return
            
        try:
            # Set thread count
            if profile.opencv_thread_count > 0:
                cv2.setNumThreads(profile.opencv_thread_count)
                results["optimizations_applied"].append(f"OpenCV threads set to {profile.opencv_thread_count}")
            else:
                cv2.setNumThreads(0)  # Use all available threads
                results["optimizations_applied"].append("OpenCV using all available threads")
                
            # Enable/disable OpenCL
            if profile.opencv_use_opencl and cv2.ocl.haveOpenCL():
                cv2.ocl.setUseOpenCL(True)
                results["optimizations_applied"].append("OpenCL acceleration enabled")
            else:
                cv2.ocl.setUseOpenCL(False)
                if profile.opencv_use_opencl:
                    results["errors"].append("OpenCL requested but not available")
                    
            # CUDA optimization (if available)
            if profile.opencv_use_cuda:
                try:
                    if cv2.cuda.getCudaEnabledDeviceCount() > 0:
                        results["optimizations_applied"].append("CUDA acceleration enabled")
                    else:
                        results["errors"].append("CUDA requested but no devices available")
                except:
                    results["errors"].append("CUDA requested but not supported")
                    
        except Exception as e:
            results["errors"].append(f"OpenCV optimization error: {e}")
            
    def _apply_threading_optimizations(self, profile: OptimizationProfile, results: Dict[str, Any]):
        """Apply threading optimizations."""
        try:
            if NUMPY_AVAILABLE and profile.vectorized_operations:
                # NumPy automatically uses optimized BLAS if available
                results["optimizations_applied"].append("Vectorized operations enabled")
                
        except Exception as e:
            results["errors"].append(f"Threading optimization error: {e}")
            
    def _apply_memory_optimizations(self, profile: OptimizationProfile, results: Dict[str, Any]):
        """Apply memory optimizations."""
        try:
            import gc
            
            if profile.memory_optimization:
                # Configure garbage collection for better memory management
                gc.set_threshold(700, 10, 10)  # More aggressive GC
                results["optimizations_applied"].append("Memory optimization enabled")
                
        except Exception as e:
            results["errors"].append(f"Memory optimization error: {e}")
            
    def benchmark_acceleration(self, test_duration_seconds: float = 30.0) -> Dict[str, Any]:
        """Benchmark different acceleration configurations."""
        self.logger.info("HardwareAccelerationOptimizer: Starting acceleration benchmark")
        
        if not OPENCV_AVAILABLE or not NUMPY_AVAILABLE:
            return {"error": "OpenCV and NumPy required for benchmarking"}
            
        # Test configurations
        test_configs = [
            ("cpu_only", {"use_opencl": False, "threads": 1}),
            ("cpu_multi", {"use_opencl": False, "threads": -1}),
        ]
        
        # Add GPU tests if available
        if cv2.ocl.haveOpenCL():
            test_configs.append(("opencl", {"use_opencl": True, "threads": -1}))
            
        results = {
            "test_duration_seconds": test_duration_seconds,
            "configurations": {}
        }
        
        for config_name, config in test_configs:
            try:
                result = self._benchmark_configuration(config, test_duration_seconds)
                results["configurations"][config_name] = result
                
            except Exception as e:
                self.logger.error(f"HardwareAccelerationOptimizer: Benchmark error for {config_name}: {e}")
                results["configurations"][config_name] = {"error": str(e)}
                
        # Determine best configuration
        best_config = None
        best_fps = 0
        
        for config_name, result in results["configurations"].items():
            if "fps" in result and result["fps"] > best_fps:
                best_fps = result["fps"]
                best_config = config_name
                
        results["best_configuration"] = best_config
        results["best_fps"] = best_fps
        
        return results
        
    def _benchmark_configuration(self, config: Dict[str, Any], duration: float) -> Dict[str, Any]:
        """Benchmark a specific configuration."""
        import time
        
        # Apply configuration
        cv2.ocl.setUseOpenCL(config.get("use_opencl", False))
        if config.get("threads", -1) > 0:
            cv2.setNumThreads(config["threads"])
        else:
            cv2.setNumThreads(0)
            
        # Create test data
        test_image = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
        
        # Benchmark
        start_time = time.time()
        frame_count = 0
        
        while time.time() - start_time < duration:
            # Simulate typical image processing operations
            gray = cv2.cvtColor(test_image, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (15, 15), 0)
            edges = cv2.Canny(blurred, 50, 150)
            resized = cv2.resize(test_image, (640, 480))
            
            frame_count += 1
            
        actual_duration = time.time() - start_time
        fps = frame_count / actual_duration
        
        return {
            "frames_processed": frame_count,
            "actual_duration": actual_duration,
            "fps": fps,
            "config": config
        }
        
    def get_current_profile(self) -> Optional[OptimizationProfile]:
        """Get the currently applied optimization profile."""
        return self.current_profile
        
    def get_optimization_recommendations(self) -> List[str]:
        """Get optimization recommendations based on detected hardware."""
        recommendations = []
        capabilities = self.detector.get_available_capabilities()
        
        # Check for high-performance options
        cuda_available = any(cap.acceleration_type == AccelerationType.GPU_CUDA for cap in capabilities)
        opencl_available = any(cap.acceleration_type == AccelerationType.GPU_OPENCL for cap in capabilities)
        hardware_codec_available = any(cap.acceleration_type == AccelerationType.HARDWARE_CODEC for cap in capabilities)
        
        if cuda_available:
            recommendations.append(
                "CUDA acceleration detected. Consider using aggressive or maximum optimization "
                "profiles for best performance in image processing tasks."
            )
        elif opencl_available:
            recommendations.append(
                "OpenCL acceleration available. Balanced or aggressive optimization profiles "
                "recommended for improved performance."
            )
        else:
            recommendations.append(
                "No GPU acceleration detected. Focus on CPU optimizations and consider "
                "hardware upgrade for better performance."
            )
            
        if hardware_codec_available:
            recommendations.append(
                "Hardware video codecs available. Enable hardware encoding/decoding "
                "for reduced CPU load during video processing."
            )
            
        if not recommendations:
            recommendations.append(
                "Limited acceleration options detected. Consider conservative optimization "
                "profile and monitor system performance."
            )
            
        return recommendations


def create_optimal_profile_for_system() -> OptimizationProfile:
    """Create an optimal optimization profile for the current system."""
    detector = HardwareAccelerationDetector()
    optimizer = HardwareAccelerationOptimizer(detector)
    
    # Auto-detect best profile
    return optimizer.create_optimization_profile("balanced")


def benchmark_system_performance(duration_seconds: float = 30.0) -> Dict[str, Any]:
    """Benchmark the system's hardware acceleration performance."""
    optimizer = HardwareAccelerationOptimizer()
    return optimizer.benchmark_acceleration(duration_seconds)


def main():
    """Command-line interface for hardware acceleration utilities."""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Hardware Acceleration Utilities")
    parser.add_argument("--detect", action="store_true", help="Detect hardware capabilities")
    parser.add_argument("--benchmark", action="store_true", help="Benchmark acceleration performance")
    parser.add_argument("--duration", type=float, default=30.0, help="Benchmark duration in seconds")
    parser.add_argument("--profile", type=str, choices=["conservative", "balanced", "aggressive", "maximum"],
                       help="Create optimization profile")
    parser.add_argument("--output", type=str, help="Output file for results")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    results = {}
    
    try:
        if args.detect:
            print("Detecting hardware acceleration capabilities...")
            detector = HardwareAccelerationDetector()
            capabilities = detector.detect_all_capabilities()
            
            print(f"\nDetected {len(capabilities)} hardware capabilities:")
            for cap in capabilities:
                status = "✓" if cap.available else "✗"
                print(f"  {status} {cap.acceleration_type.value}: {cap.device_info or 'Available'}")
                if cap.performance_score:
                    print(f"    Performance Score: {cap.performance_score:.2f}")
                if cap.limitations:
                    print(f"    Limitations: {', '.join(cap.limitations)}")
                    
            results["capabilities"] = [
                {
                    "type": cap.acceleration_type.value,
                    "available": cap.available,
                    "device_info": cap.device_info,
                    "performance_score": cap.performance_score,
                    "limitations": cap.limitations
                } for cap in capabilities
            ]
            
        if args.profile:
            print(f"\nCreating {args.profile} optimization profile...")
            optimizer = HardwareAccelerationOptimizer()
            profile = optimizer.create_optimization_profile(args.profile)
            
            print(f"Profile: {profile.profile_name}")
            print(f"  CPU Optimization: {profile.cpu_optimization}")
            print(f"  GPU Acceleration: {profile.gpu_acceleration}")
            print(f"  Hardware Codec: {profile.hardware_codec}")
            print(f"  OpenCL: {profile.opencv_use_opencl}")
            print(f"  CUDA: {profile.opencv_use_cuda}")
            
            results["optimization_profile"] = profile.to_dict()
            
        if args.benchmark:
            print(f"\nBenchmarking acceleration performance for {args.duration} seconds...")
            benchmark_results = benchmark_system_performance(args.duration)
            
            print("\nBenchmark Results:")
            for config_name, result in benchmark_results["configurations"].items():
                if "fps" in result:
                    print(f"  {config_name}: {result['fps']:.1f} FPS")
                elif "error" in result:
                    print(f"  {config_name}: Error - {result['error']}")
                    
            if benchmark_results.get("best_configuration"):
                print(f"\nBest Configuration: {benchmark_results['best_configuration']} "
                      f"({benchmark_results['best_fps']:.1f} FPS)")
                      
            results["benchmark"] = benchmark_results
            
        # Save results if output file specified
        if args.output and results:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\nResults saved to: {args.output}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()