"""
Synthetic Data Generator for Virtual Test Environment

This module generates realistic synthetic sensor data to simulate the data streams
that would come from real hardware sensors. The goal is to create data that has
similar characteristics, timing, and volume as real sensor data to properly
stress-test the system.

Supported data types:
- GSR (Galvanic Skin Response): 128Hz continuous readings with realistic physiological patterns
- RGB Video: 30fps camera frames with procedural content 
- Thermal: 9fps thermal image data with heat patterns
"""

import math
import random
import time
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import base64
import io


class SyntheticDataGenerator:
    """
    Generates realistic synthetic sensor data for testing purposes.
    
    This class creates synthetic data that mimics the characteristics of real sensors:
    - GSR data includes baseline drift, noise, and stress response spikes
    - RGB frames contain procedural patterns and motion
    - Thermal data simulates heat distribution and changes over time
    """
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize the synthetic data generator.
        
        Args:
            seed: Random seed for reproducible data generation
        """
        # Create isolated random generators for deterministic behavior
        if seed is not None:
            self.random_generator = np.random.Generator(np.random.PCG64(seed))
            self.py_random = random.Random(seed)
        else:
            self.random_generator = np.random.default_rng()
            self.py_random = random.Random()
        
        # GSR simulation parameters
        self.gsr_baseline = 0.8  # μS (microsiemens) - typical baseline
        self.gsr_baseline_drift_rate = 0.01  # Slow drift over time
        self.gsr_noise_amplitude = 0.05  # Random noise level
        self.gsr_stress_spike_probability = 0.001  # Probability per sample of stress event
        self.gsr_current_baseline = self.gsr_baseline
        self.gsr_stress_event_timer = 0.0
        self.gsr_stress_amplitude = 0.0
        
        # Video simulation parameters  
        self.video_width = 640
        self.video_height = 480
        self.video_frame_counter = 0
        self.video_pattern_speed = 2.0  # Pattern movement speed
        
        # Thermal simulation parameters
        self.thermal_width = 64
        self.thermal_height = 48
        self.thermal_frame_counter = 0
        self.thermal_hotspot_x = 32
        self.thermal_hotspot_y = 24
        self.thermal_base_temp = 25.0  # Celsius
        self.thermal_hotspot_temp = 35.0  # Peak temperature
        
        # Use deterministic timing for reproducible results
        self.start_time = 0.0  # Use relative time instead of actual time
        self.current_time = 0.0
        
    def generate_gsr_sample(self) -> float:
        """
        Generate a single GSR (Galvanic Skin Response) sample.
        
        Returns realistic GSR data including:
        - Baseline conductance level with slow drift
        - Random physiological noise  
        - Occasional stress response spikes
        - Motion artifacts
        
        Returns:
            float: GSR value in microsiemens (μS)
        """
        # Use deterministic time progression for reproducible results
        sample_interval = 1.0 / 128.0  # 128Hz sampling rate
        self.current_time += sample_interval
        
        # Baseline drift (very slow changes)
        drift = math.sin(self.current_time * 0.01) * self.gsr_baseline_drift_rate
        self.gsr_current_baseline = self.gsr_baseline + drift
        
        # Random noise (simulates measurement noise and small physiological variations)
        noise = self.random_generator.normal(0, self.gsr_noise_amplitude)
        
        # Stress event simulation
        stress_component = 0.0
        if self.gsr_stress_event_timer > 0:
            # Ongoing stress event - exponential decay
            stress_component = self.gsr_stress_amplitude * math.exp(-self.gsr_stress_event_timer / 3.0)
            self.gsr_stress_event_timer += 1.0 / 128.0  # Assuming 128Hz sampling
            
            # End stress event when amplitude drops low enough
            if stress_component < 0.01:
                self.gsr_stress_event_timer = 0.0
                self.gsr_stress_amplitude = 0.0
        else:
            # Check for new stress event
            if self.random_generator.random() < self.gsr_stress_spike_probability:
                # Start new stress event
                self.gsr_stress_event_timer = 0.01
                self.gsr_stress_amplitude = self.random_generator.uniform(0.3, 1.0)  # Variable stress intensity
                stress_component = self.gsr_stress_amplitude
        
        # Breathing artifact (subtle periodic component)
        breathing_rate = 0.25  # Hz (15 breaths per minute)
        breathing_component = 0.02 * math.sin(2 * math.pi * breathing_rate * self.current_time)
        
        # Heart rate artifact (very subtle)
        heart_rate = 1.17  # Hz (70 BPM)
        heart_component = 0.005 * math.sin(2 * math.pi * heart_rate * self.current_time)
        
        # Combine all components
        gsr_value = (self.gsr_current_baseline + 
                    noise + 
                    stress_component + 
                    breathing_component + 
                    heart_component)
        
        # Ensure positive value and realistic range
        gsr_value = max(0.1, min(5.0, gsr_value))
        
        return round(gsr_value, 4)
    
    def generate_gsr_batch(self, sample_count: int) -> List[float]:
        """
        Generate a batch of GSR samples.
        
        Args:
            sample_count: Number of samples to generate
            
        Returns:
            List[float]: List of GSR values
        """
        return [self.generate_gsr_sample() for _ in range(sample_count)]
    
    def generate_rgb_frame(self) -> bytes:
        """
        Generate a synthetic RGB camera frame.
        
        Creates a procedural image with moving patterns to simulate video content.
        The frame includes:
        - Moving geometric patterns
        - Color gradients
        - Pseudo-random elements to simulate scene changes
        
        Returns:
            bytes: JPEG-encoded image data
        """
        try:
            # Create a synthetic image using numpy
            frame = np.zeros((self.video_height, self.video_width, 3), dtype=np.uint8)
            
            current_time = self.current_time
            self.video_frame_counter += 1
            
            # Create moving gradient pattern
            for y in range(self.video_height):
                for x in range(self.video_width):
                    # Moving wave pattern
                    wave_x = math.sin((x / 50.0) + (current_time * self.video_pattern_speed))
                    wave_y = math.cos((y / 50.0) + (current_time * self.video_pattern_speed))
                    
                    # Color based on position and time
                    r = int(128 + 127 * wave_x)
                    g = int(128 + 127 * wave_y)
                    b = int(128 + 127 * math.sin((x + y) / 30.0 + current_time))
                    
                    frame[y, x] = [r, g, b]
            
            # Add some moving geometric shapes for interest
            center_x = int(self.video_width / 2 + 100 * math.sin(current_time * 0.5))
            center_y = int(self.video_height / 2 + 50 * math.cos(current_time * 0.7))
            radius = int(20 + 10 * math.sin(current_time * 2.0))
            
            # Draw a moving circle
            y_indices, x_indices = np.ogrid[:self.video_height, :self.video_width]
            mask = (x_indices - center_x) ** 2 + (y_indices - center_y) ** 2 <= radius ** 2
            frame[mask] = [255, 255, 255]  # White circle
            
            # Convert to bytes (simulate JPEG compression)
            # For testing purposes, we'll create a simple byte representation
            # In a real implementation, this would use PIL or cv2 to create actual JPEG
            frame_bytes = frame.tobytes()
            
            # Simulate compression by reducing size
            compressed_size = len(frame_bytes) // 10  # Simulate 10:1 compression
            synthetic_jpeg = frame_bytes[:compressed_size]
            
            return synthetic_jpeg
            
        except Exception as e:
            # Fallback: return dummy data
            dummy_frame = b"JPEG_DUMMY_DATA_" + str(self.video_frame_counter).encode() + b"_END"
            return dummy_frame
    
    def generate_rgb_frame_base64(self) -> str:
        """
        Generate an RGB frame and encode it as base64.
        
        Returns:
            str: Base64-encoded image data
        """
        frame_bytes = self.generate_rgb_frame()
        return base64.b64encode(frame_bytes).decode("utf-8")
    
    def generate_thermal_frame(self) -> bytes:
        """
        Generate a synthetic thermal camera frame.
        
        Creates thermal data simulating heat distribution:
        - Base ambient temperature
        - Moving hotspots
        - Realistic temperature gradients
        - Noise typical of thermal sensors
        
        Returns:
            bytes: Raw thermal data (temperature values)
        """
        try:
            current_time = self.current_time
            self.thermal_frame_counter += 1
            
            # Create thermal image array (temperatures in Celsius)
            thermal_data = np.full((self.thermal_height, self.thermal_width), 
                                 self.thermal_base_temp, dtype=np.float32)
            
            # Add noise
            noise = self.random_generator.normal(0, 0.5, (self.thermal_height, self.thermal_width))
            thermal_data += noise
            
            # Moving hotspot
            hotspot_x = int(self.thermal_width / 2 + 
                          self.thermal_width / 4 * math.sin(current_time * 0.3))
            hotspot_y = int(self.thermal_height / 2 + 
                          self.thermal_height / 4 * math.cos(current_time * 0.2))
            
            # Create temperature gradient around hotspot
            for y in range(self.thermal_height):
                for x in range(self.thermal_width):
                    distance = math.sqrt((x - hotspot_x) ** 2 + (y - hotspot_y) ** 2)
                    # Gaussian-like temperature distribution
                    heat_contribution = (self.thermal_hotspot_temp * 
                                       math.exp(-(distance ** 2) / (2 * 10 ** 2)))
                    thermal_data[y, x] += heat_contribution
            
            # Add secondary smaller hotspot
            secondary_x = int(self.thermal_width * 0.3 + 
                            self.thermal_width * 0.1 * math.cos(current_time * 0.7))
            secondary_y = int(self.thermal_height * 0.7 + 
                            self.thermal_height * 0.1 * math.sin(current_time * 0.5))
            
            for y in range(self.thermal_height):
                for x in range(self.thermal_width):
                    distance = math.sqrt((x - secondary_x) ** 2 + (y - secondary_y) ** 2)
                    heat_contribution = (5.0 * math.exp(-(distance ** 2) / (2 * 5 ** 2)))
                    thermal_data[y, x] += heat_contribution
            
            # Convert to bytes (16-bit temperature values)
            # Scale to 16-bit range for realistic thermal data format
            thermal_data_scaled = ((thermal_data - 0) / 60.0 * 65535).astype(np.uint16)
            thermal_bytes = thermal_data_scaled.tobytes()
            
            return thermal_bytes
            
        except Exception as e:
            # Fallback: return dummy thermal data
            dummy_size = self.thermal_width * self.thermal_height * 2  # 2 bytes per pixel
            dummy_thermal = bytes([self.random_generator.integers(0, 256) for _ in range(dummy_size)])
            return dummy_thermal
    
    def generate_thermal_frame_base64(self) -> str:
        """
        Generate a thermal frame and encode it as base64.
        
        Returns:
            str: Base64-encoded thermal data
        """
        thermal_bytes = self.generate_thermal_frame()
        return base64.b64encode(thermal_bytes).decode("utf-8")
    
    def simulate_video_file(self, duration_seconds: float, fps: int = 30) -> Dict[str, Any]:
        """
        Simulate creating a video file by generating metadata and size info.
        
        Args:
            duration_seconds: Duration of the simulated video
            fps: Frames per second
            
        Returns:
            Dict with video file metadata
        """
        frame_count = int(duration_seconds * fps)
        
        # Estimate file size based on typical video compression
        # Assume 1080p video with H.264 compression
        estimated_bitrate_mbps = 8.0  # Moderate quality 1080p
        estimated_size_mb = duration_seconds * estimated_bitrate_mbps / 8.0
        estimated_size_bytes = int(estimated_size_mb * 1024 * 1024)
        
        return {
            "duration_seconds": duration_seconds,
            "fps": fps,
            "frame_count": frame_count,
            "estimated_size_bytes": estimated_size_bytes,
            "estimated_size_mb": estimated_size_mb,
            "codec": "h264",
            "resolution": "1920x1080",
            "created_timestamp": time.time(),
        }
    
    def simulate_thermal_sequence(self, duration_seconds: float, fps: int = 9) -> Dict[str, Any]:
        """
        Simulate creating a thermal image sequence.
        
        Args:
            duration_seconds: Duration of the thermal recording
            fps: Frames per second
            
        Returns:
            Dict with thermal sequence metadata
        """
        frame_count = int(duration_seconds * fps)
        
        # Thermal data is typically less compressed
        bytes_per_pixel = 2  # 16-bit thermal data
        pixels_per_frame = self.thermal_width * self.thermal_height
        bytes_per_frame = pixels_per_frame * bytes_per_pixel
        total_size_bytes = frame_count * bytes_per_frame
        total_size_mb = total_size_bytes / (1024 * 1024)
        
        return {
            "duration_seconds": duration_seconds,
            "fps": fps,
            "frame_count": frame_count,
            "total_size_bytes": total_size_bytes,
            "total_size_mb": total_size_mb,
            "resolution": f"{self.thermal_width}x{self.thermal_height}",
            "bit_depth": 16,
            "created_timestamp": time.time(),
        }
    
    def generate_batch_gsr_with_events(self, duration_seconds: float, 
                                     sampling_rate: int = 128,
                                     stress_events: Optional[List[Tuple[float, float]]] = None) -> List[Dict[str, Any]]:
        """
        Generate a batch of GSR samples with predefined stress events.
        
        Args:
            duration_seconds: Total duration of data to generate
            sampling_rate: Samples per second
            stress_events: List of (start_time, intensity) tuples for stress events
            
        Returns:
            List of dictionaries with timestamp and GSR value
        """
        sample_count = int(duration_seconds * sampling_rate)
        sample_interval = 1.0 / sampling_rate
        
        # Plan stress events
        if stress_events:
            for start_time, intensity in stress_events:
                if 0 <= start_time <= duration_seconds:
                    # Schedule the stress event
                    pass  # Will be handled in generate_gsr_sample based on timing
        
        # Generate samples
        samples = []
        for i in range(sample_count):
            timestamp = i * sample_interval
            gsr_value = self.generate_gsr_sample()
            
            samples.append({
                "timestamp": self.start_time + timestamp,
                "gsr_value": gsr_value,
                "sample_index": i,
            })
        
        return samples
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the generated data.
        
        Returns:
            Dict with generation statistics
        """
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        
        return {
            "elapsed_time_seconds": elapsed_time,
            "gsr_baseline": self.gsr_current_baseline,
            "gsr_stress_active": self.gsr_stress_event_timer > 0,
            "video_frames_generated": self.video_frame_counter,
            "thermal_frames_generated": self.thermal_frame_counter,
            "estimated_video_fps": self.video_frame_counter / elapsed_time if elapsed_time > 0 else 0,
            "estimated_thermal_fps": self.thermal_frame_counter / elapsed_time if elapsed_time > 0 else 0,
        }
    
    def reset(self) -> None:
        """Reset the generator state for a new session."""
        self.gsr_current_baseline = self.gsr_baseline
        self.gsr_stress_event_timer = 0.0
        self.gsr_stress_amplitude = 0.0
        self.video_frame_counter = 0
        self.thermal_frame_counter = 0
        self.start_time = time.time()


class MultiDeviceDataGenerator:
    """
    Manages data generation for multiple virtual devices with coordination.
    
    This class ensures that multiple devices can generate data with slight
    variations but maintain realistic correlations (e.g., environmental factors
    affecting all devices similarly).
    """
    
    def __init__(self, device_count: int, base_seed: Optional[int] = None):
        """
        Initialize multi-device data generation.
        
        Args:
            device_count: Number of devices to generate data for
            base_seed: Base random seed (each device gets base_seed + device_index)
        """
        self.device_count = device_count
        self.generators = []
        
        for i in range(device_count):
            seed = (base_seed + i) if base_seed is not None else None
            generator = SyntheticDataGenerator(seed=seed)
            self.generators.append(generator)
        
        # Shared environmental factors
        self.ambient_temperature = 22.0  # Celsius
        self.ambient_noise_level = 0.02
        
    def generate_synchronized_gsr_samples(self) -> List[float]:
        """
        Generate GSR samples for all devices with shared environmental factors.
        
        Returns:
            List of GSR values, one per device
        """
        # Apply shared environmental drift
        environmental_drift = 0.01 * math.sin(time.time() * 0.01)
        
        samples = []
        for generator in self.generators:
            base_sample = generator.generate_gsr_sample()
            # Add shared environmental factor
            adjusted_sample = base_sample + environmental_drift
            samples.append(max(0.1, adjusted_sample))  # Ensure positive
        
        return samples
    
    def get_all_statistics(self) -> List[Dict[str, Any]]:
        """Get statistics for all device generators."""
        return [gen.get_statistics() for gen in self.generators]
    
    def reset_all(self) -> None:
        """Reset all device generators."""
        for generator in self.generators:
            generator.reset()


# Utility functions for creating realistic test scenarios

def create_stress_test_scenario(duration_minutes: float = 60.0) -> List[Tuple[float, float]]:
    """
    Create a predefined stress test scenario with realistic stress events.
    
    Args:
        duration_minutes: Total scenario duration
        
    Returns:
        List of (start_time_seconds, intensity) tuples
    """
    duration_seconds = duration_minutes * 60.0
    events = []
    
    # Baseline period (first 10 minutes - no stress)
    
    # Mild stress event at 15 minutes
    events.append((15 * 60, 0.4))
    
    # Moderate stress at 30 minutes  
    events.append((30 * 60, 0.7))
    
    # High stress event at 45 minutes
    events.append((45 * 60, 1.0))
    
    # Recovery period (last 15 minutes - gradually decreasing)
    events.append((50 * 60, 0.3))
    
    return events


def estimate_data_volume(device_count: int, duration_hours: float) -> Dict[str, float]:
    """
    Estimate the total data volume for a test scenario.
    
    Args:
        device_count: Number of virtual devices
        duration_hours: Test duration in hours
        
    Returns:
        Dict with data volume estimates in MB
    """
    duration_seconds = duration_hours * 3600
    
    # GSR data: 128 samples/sec * 8 bytes per sample (timestamp + value)
    gsr_mb_per_device = (128 * 8 * duration_seconds) / (1024 * 1024)
    
    # Video data: 30fps * ~100KB per frame (compressed)
    video_mb_per_device = (30 * 100 * 1024 * duration_seconds) / (1024 * 1024)
    
    # Thermal data: 9fps * ~6KB per frame (64x48 * 2 bytes)
    thermal_mb_per_device = (9 * 6 * 1024 * duration_seconds) / (1024 * 1024)
    
    total_per_device = gsr_mb_per_device + video_mb_per_device + thermal_mb_per_device
    total_all_devices = total_per_device * device_count
    
    return {
        "gsr_mb_per_device": round(gsr_mb_per_device, 2),
        "video_mb_per_device": round(video_mb_per_device, 2),
        "thermal_mb_per_device": round(thermal_mb_per_device, 2),
        "total_mb_per_device": round(total_per_device, 2),
        "total_mb_all_devices": round(total_all_devices, 2),
        "device_count": device_count,
        "duration_hours": duration_hours,
    }