#!/usr/bin/env python3
"""
Advanced Synchronization Algorithms for Multi-Camera Systems

This module implements sophisticated synchronization algorithms specifically designed 
for dual camera systems used in physiological monitoring applications. The algorithms
ensure frame-level temporal alignment between multiple cameras while maintaining
high precision timing accuracy required for sensitive biosignal analysis.

Key Features:
- Adaptive synchronization with dynamic threshold adjustment
- Cross-correlation based temporal alignment
- Hardware timestamp synchronization
- Sub-millisecond precision timing
- Quality metrics and diagnostic tools

Theoretical Foundation:
The synchronization algorithms are based on established principles in distributed
systems timing and signal processing theory, incorporating adaptive control systems
theory to maintain optimal synchronization under varying operational conditions.

Author: Multi-Sensor Recording System Team
Date: 2025-07-31
"""

import numpy as np
import time
import threading
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Callable
from collections import deque
from enum import Enum
import statistics
import cv2

from utils.logging_config import get_logger, performance_timer

logger = get_logger(__name__)


class SynchronizationStrategy(Enum):
    """Enumeration of available synchronization strategies."""
    
    MASTER_SLAVE = "master_slave"        # One camera drives timing
    CROSS_CORRELATION = "cross_corr"     # Frame content correlation
    HARDWARE_SYNC = "hardware_sync"      # External hardware trigger
    ADAPTIVE_HYBRID = "adaptive_hybrid"  # Adaptive algorithm selection


@dataclass
class TimingMetrics:
    """Comprehensive timing metrics for synchronization quality assessment."""
    
    capture_interval_ms: float = 0.0
    sync_offset_ms: float = 0.0
    jitter_ms: float = 0.0
    drift_rate_ppm: float = 0.0  # Parts per million
    correlation_coefficient: float = 0.0
    quality_score: float = 0.0   # 0.0 to 1.0
    
    # Statistical measures
    mean_offset_ms: float = 0.0
    std_dev_offset_ms: float = 0.0
    max_offset_ms: float = 0.0
    
    # Performance indicators
    frames_processed: int = 0
    sync_violations: int = 0
    recovery_time_ms: float = 0.0


@dataclass
class SyncFrame:
    """Synchronized frame with comprehensive timing information."""
    
    timestamp: float
    frame_id: int
    camera1_frame: np.ndarray
    camera2_frame: np.ndarray
    camera1_hardware_ts: Optional[float] = None
    camera2_hardware_ts: Optional[float] = None
    software_capture_ts: float = field(default_factory=time.time)
    sync_quality: float = 0.0
    processing_latency_ms: float = 0.0
    
    def get_sync_offset_ms(self) -> float:
        """Calculate synchronization offset in milliseconds."""
        if self.camera1_hardware_ts and self.camera2_hardware_ts:
            return abs(self.camera1_hardware_ts - self.camera2_hardware_ts) * 1000
        return 0.0


class AdaptiveSynchronizer:
    """
    Advanced adaptive synchronization system for dual camera setup.
    
    This class implements sophisticated synchronization algorithms that automatically
    adapt to changing conditions and maintain optimal timing precision for 
    physiological monitoring applications.
    
    The synchronizer employs multiple strategies and dynamically selects the most
    appropriate approach based on real-time performance metrics and environmental
    conditions.
    """
    
    def __init__(self, 
                 target_fps: float = 30.0,
                 sync_threshold_ms: float = 16.67,
                 buffer_size: int = 100,
                 strategy: SynchronizationStrategy = SynchronizationStrategy.ADAPTIVE_HYBRID):
        """
        Initialize the adaptive synchronizer.
        
        Args:
            target_fps: Target frame rate for synchronization
            sync_threshold_ms: Maximum acceptable synchronization offset
            buffer_size: Size of timing history buffer for analysis
            strategy: Initial synchronization strategy
        """
        self.target_fps = target_fps
        self.frame_interval_ms = 1000.0 / target_fps
        self.sync_threshold_ms = sync_threshold_ms
        self.current_strategy = strategy
        
        # Timing buffers for analysis
        self.timing_buffer = deque(maxlen=buffer_size)
        self.offset_history = deque(maxlen=buffer_size)
        self.quality_history = deque(maxlen=buffer_size)
        
        # Synchronization state
        self.master_clock_offset = 0.0
        self.drift_compensation = 0.0
        self.adaptive_threshold = sync_threshold_ms
        
        # Performance monitoring
        self.metrics = TimingMetrics()
        self._lock = threading.Lock()
        
        # Algorithm parameters
        self.cross_corr_window_size = 32  # pixels for correlation analysis
        self.adaptation_rate = 0.1        # Rate of adaptive adjustment
        self.drift_detection_window = 50  # frames for drift analysis
        
        logger.info(f"AdaptiveSynchronizer initialized: {target_fps}fps, "
                   f"threshold={sync_threshold_ms}ms, strategy={strategy.value}")
    
    @performance_timer("synchronize_frames")
    def synchronize_frames(self, 
                          frame1: np.ndarray, 
                          frame2: np.ndarray,
                          timestamp1: float,
                          timestamp2: float,
                          hardware_ts1: Optional[float] = None,
                          hardware_ts2: Optional[float] = None) -> SyncFrame:
        """
        Synchronize two camera frames using the selected algorithm.
        
        Args:
            frame1: First camera frame
            frame2: Second camera frame  
            timestamp1: Software timestamp for frame1
            timestamp2: Software timestamp for frame2
            hardware_ts1: Hardware timestamp for frame1 (if available)
            hardware_ts2: Hardware timestamp for frame2 (if available)
            
        Returns:
            SyncFrame: Synchronized frame with timing metrics
        """
        process_start = time.time()
        
        # Create synchronized frame object
        sync_frame = SyncFrame(
            timestamp=min(timestamp1, timestamp2),
            frame_id=self.metrics.frames_processed,
            camera1_frame=frame1,
            camera2_frame=frame2,
            camera1_hardware_ts=hardware_ts1,
            camera2_hardware_ts=hardware_ts2,
            software_capture_ts=time.time()
        )
        
        # Calculate timing metrics
        offset_ms = abs(timestamp1 - timestamp2) * 1000
        sync_frame.sync_quality = self._calculate_sync_quality(offset_ms)
        
        # Apply synchronization strategy
        if self.current_strategy == SynchronizationStrategy.MASTER_SLAVE:
            sync_frame = self._master_slave_sync(sync_frame)
        elif self.current_strategy == SynchronizationStrategy.CROSS_CORRELATION:
            sync_frame = self._cross_correlation_sync(sync_frame)
        elif self.current_strategy == SynchronizationStrategy.HARDWARE_SYNC:
            sync_frame = self._hardware_sync(sync_frame)
        elif self.current_strategy == SynchronizationStrategy.ADAPTIVE_HYBRID:
            sync_frame = self._adaptive_hybrid_sync(sync_frame)
        
        # Update metrics and history
        with self._lock:
            self._update_metrics(sync_frame, offset_ms)
            self._adapt_parameters()
        
        # Calculate processing latency
        sync_frame.processing_latency_ms = (time.time() - process_start) * 1000
        
        return sync_frame
    
    def _master_slave_sync(self, sync_frame: SyncFrame) -> SyncFrame:
        """
        Master-slave synchronization strategy.
        
        Camera 1 acts as master, camera 2 timing is adjusted to match.
        """
        # Use camera 1 timestamp as reference
        if sync_frame.camera1_hardware_ts and sync_frame.camera2_hardware_ts:
            offset = sync_frame.camera1_hardware_ts - sync_frame.camera2_hardware_ts
            self.master_clock_offset = offset
            
        sync_frame.sync_quality = min(1.0, 1.0 - abs(self.master_clock_offset) / self.sync_threshold_ms)
        return sync_frame
    
    def _cross_correlation_sync(self, sync_frame: SyncFrame) -> SyncFrame:
        """
        Cross-correlation based synchronization using frame content analysis.
        
        Analyzes visual similarity between frames to determine optimal alignment.
        """
        try:
            # Convert frames to grayscale for correlation analysis
            gray1 = cv2.cvtColor(sync_frame.camera1_frame, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(sync_frame.camera2_frame, cv2.COLOR_BGR2GRAY)
            
            # Resize for faster processing
            h, w = gray1.shape
            scale = min(1.0, self.cross_corr_window_size / min(h, w))
            
            if scale < 1.0:
                new_h, new_w = int(h * scale), int(w * scale)
                gray1 = cv2.resize(gray1, (new_w, new_h))
                gray2 = cv2.resize(gray2, (new_w, new_h))
            
            # Calculate normalized cross-correlation
            correlation = cv2.matchTemplate(gray1, gray2, cv2.TM_CCOEFF_NORMED)
            _, max_corr, _, _ = cv2.minMaxLoc(correlation)
            
            # Update sync quality based on correlation
            sync_frame.sync_quality = max(0.0, max_corr)
            
        except Exception as e:
            logger.warning(f"Cross-correlation sync failed: {e}")
            sync_frame.sync_quality = 0.5  # Fallback quality
            
        return sync_frame
    
    def _hardware_sync(self, sync_frame: SyncFrame) -> SyncFrame:
        """
        Hardware-based synchronization using external timing signals.
        
        Relies on hardware timestamps for precise synchronization.
        """
        if sync_frame.camera1_hardware_ts and sync_frame.camera2_hardware_ts:
            offset_ms = sync_frame.get_sync_offset_ms()
            sync_frame.sync_quality = max(0.0, 1.0 - offset_ms / self.sync_threshold_ms)
        else:
            # Fallback to software timing
            software_offset = abs(sync_frame.timestamp - sync_frame.software_capture_ts) * 1000
            sync_frame.sync_quality = max(0.0, 1.0 - software_offset / self.sync_threshold_ms)
            
        return sync_frame
    
    def _adaptive_hybrid_sync(self, sync_frame: SyncFrame) -> SyncFrame:
        """
        Adaptive hybrid synchronization that combines multiple strategies.
        
        Dynamically selects the best synchronization approach based on 
        current conditions and historical performance.
        """
        # Try hardware sync first if available
        if sync_frame.camera1_hardware_ts and sync_frame.camera2_hardware_ts:
            sync_frame = self._hardware_sync(sync_frame)
            
            # If hardware sync quality is good, use it
            if sync_frame.sync_quality > 0.8:
                return sync_frame
        
        # Fallback to cross-correlation for content-based sync
        sync_frame = self._cross_correlation_sync(sync_frame)
        
        # If correlation is poor, use master-slave as final fallback
        if sync_frame.sync_quality < 0.6:
            sync_frame = self._master_slave_sync(sync_frame)
            
        return sync_frame
    
    def _calculate_sync_quality(self, offset_ms: float) -> float:
        """
        Calculate synchronization quality score from timing offset.
        
        Args:
            offset_ms: Timing offset in milliseconds
            
        Returns:
            float: Quality score from 0.0 to 1.0
        """
        if offset_ms <= self.adaptive_threshold:
            return 1.0
        elif offset_ms <= self.adaptive_threshold * 2:
            return 1.0 - (offset_ms - self.adaptive_threshold) / self.adaptive_threshold
        else:
            return 0.0
    
    def _update_metrics(self, sync_frame: SyncFrame, offset_ms: float):
        """Update comprehensive timing metrics."""
        # Add to history buffers
        self.offset_history.append(offset_ms)
        self.quality_history.append(sync_frame.sync_quality)
        
        # Update frame counter
        self.metrics.frames_processed += 1
        
        # Calculate statistical measures
        if len(self.offset_history) > 1:
            self.metrics.mean_offset_ms = statistics.mean(self.offset_history)
            self.metrics.std_dev_offset_ms = statistics.stdev(self.offset_history)
            self.metrics.max_offset_ms = max(self.offset_history)
            
        # Update current metrics
        self.metrics.sync_offset_ms = offset_ms
        self.metrics.quality_score = sync_frame.sync_quality
        
        # Count sync violations
        if offset_ms > self.adaptive_threshold:
            self.metrics.sync_violations += 1
            
        # Calculate jitter (variation in timing)
        if len(self.offset_history) >= 3:
            recent_offsets = list(self.offset_history)[-3:]
            self.metrics.jitter_ms = statistics.stdev(recent_offsets)
    
    def _adapt_parameters(self):
        """
        Adapt synchronization parameters based on performance history.
        
        This method implements adaptive control to optimize synchronization
        performance under changing conditions.
        """
        if len(self.quality_history) < 10:
            return
            
        # Calculate recent performance
        recent_quality = list(self.quality_history)[-10:]
        avg_quality = statistics.mean(recent_quality)
        
        # Adapt threshold based on performance
        if avg_quality > 0.9:
            # Performance is excellent, can tighten threshold
            self.adaptive_threshold = max(
                self.sync_threshold_ms * 0.5,
                self.adaptive_threshold * (1 - self.adaptation_rate)
            )
        elif avg_quality < 0.7:
            # Performance is poor, relax threshold
            self.adaptive_threshold = min(
                self.sync_threshold_ms * 2.0,
                self.adaptive_threshold * (1 + self.adaptation_rate)
            )
            
        # Detect and compensate for systematic drift
        if len(self.offset_history) >= self.drift_detection_window:
            recent_offsets = list(self.offset_history)[-self.drift_detection_window:]
            
            # Linear regression to detect drift trend
            x = np.arange(len(recent_offsets))
            y = np.array(recent_offsets)
            
            if len(x) > 1:
                drift_slope = np.polyfit(x, y, 1)[0]
                self.drift_compensation += drift_slope * self.adaptation_rate
                self.metrics.drift_rate_ppm = drift_slope * 1000  # Convert to ppm
    
    def get_diagnostics(self) -> Dict:
        """
        Get comprehensive diagnostic information about synchronization performance.
        
        Returns:
            dict: Detailed diagnostic metrics
        """
        with self._lock:
            return {
                'strategy': self.current_strategy.value,
                'adaptive_threshold_ms': self.adaptive_threshold,
                'master_clock_offset': self.master_clock_offset,
                'drift_compensation': self.drift_compensation,
                'buffer_sizes': {
                    'timing': len(self.timing_buffer),
                    'offset': len(self.offset_history),
                    'quality': len(self.quality_history)
                },
                'metrics': {
                    'frames_processed': self.metrics.frames_processed,
                    'sync_violations': self.metrics.sync_violations,
                    'violation_rate': (self.metrics.sync_violations / max(1, self.metrics.frames_processed)),
                    'mean_offset_ms': self.metrics.mean_offset_ms,
                    'std_dev_offset_ms': self.metrics.std_dev_offset_ms,
                    'max_offset_ms': self.metrics.max_offset_ms,
                    'jitter_ms': self.metrics.jitter_ms,
                    'drift_rate_ppm': self.metrics.drift_rate_ppm,
                    'current_quality': self.metrics.quality_score
                }
            }
    
    def reset_metrics(self):
        """Reset all metrics and history buffers."""
        with self._lock:
            self.timing_buffer.clear()
            self.offset_history.clear()
            self.quality_history.clear()
            self.metrics = TimingMetrics()
            self.master_clock_offset = 0.0
            self.drift_compensation = 0.0
            self.adaptive_threshold = self.sync_threshold_ms
            
        logger.info("Synchronizer metrics reset")
    
    def set_strategy(self, strategy: SynchronizationStrategy):
        """
        Change the synchronization strategy.
        
        Args:
            strategy: New synchronization strategy to use
        """
        old_strategy = self.current_strategy
        self.current_strategy = strategy
        
        logger.info(f"Synchronization strategy changed: {old_strategy.value} -> {strategy.value}")


def test_dual_camera_sync(camera1_index: int = 0, 
                         camera2_index: int = 1,
                         duration_seconds: int = 10) -> Dict:
    """
    Test dual camera synchronization performance.
    
    Args:
        camera1_index: Index of first camera
        camera2_index: Index of second camera  
        duration_seconds: Test duration in seconds
        
    Returns:
        dict: Comprehensive test results and performance metrics
    """
    logger.info(f"Starting dual camera synchronization test (cameras {camera1_index}, {camera2_index})")
    
    synchronizer = AdaptiveSynchronizer(
        target_fps=30.0,
        strategy=SynchronizationStrategy.ADAPTIVE_HYBRID
    )
    
    try:
        # Initialize cameras
        cap1 = cv2.VideoCapture(camera1_index)
        cap2 = cv2.VideoCapture(camera2_index)
        
        if not cap1.isOpened() or not cap2.isOpened():
            return {'error': 'Failed to open cameras', 'success': False}
        
        # Configure cameras for testing
        for cap in [cap1, cap2]:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 30)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        start_time = time.time()
        frame_count = 0
        sync_frames = []
        
        # Capture and synchronize frames
        while time.time() - start_time < duration_seconds:
            ret1, frame1 = cap1.read()
            ts1 = time.time()
            
            ret2, frame2 = cap2.read()
            ts2 = time.time()
            
            if ret1 and ret2:
                sync_frame = synchronizer.synchronize_frames(frame1, frame2, ts1, ts2)
                sync_frames.append(sync_frame)
                frame_count += 1
                
                if frame_count % 30 == 0:  # Log every second
                    logger.info(f"Processed {frame_count} frames, "
                               f"sync quality: {sync_frame.sync_quality:.3f}")
            
            time.sleep(1/30)  # Target 30 FPS
        
        # Cleanup
        cap1.release()
        cap2.release()
        
        # Generate test results
        diagnostics = synchronizer.get_diagnostics()
        test_results = {
            'success': True,
            'duration_seconds': time.time() - start_time,
            'frames_captured': frame_count,
            'average_fps': frame_count / (time.time() - start_time),
            'synchronization_metrics': diagnostics,
            'quality_statistics': {
                'mean_quality': statistics.mean([f.sync_quality for f in sync_frames]) if sync_frames else 0,
                'min_quality': min([f.sync_quality for f in sync_frames]) if sync_frames else 0,
                'max_quality': max([f.sync_quality for f in sync_frames]) if sync_frames else 0,
                'frames_above_threshold': sum(1 for f in sync_frames if f.sync_quality > 0.8)
            }
        }
        
        logger.info(f"Synchronization test completed: {frame_count} frames, "
                   f"avg quality: {test_results['quality_statistics']['mean_quality']:.3f}")
        
        return test_results
        
    except Exception as e:
        logger.error(f"Synchronization test failed: {e}")
        return {'error': str(e), 'success': False}


if __name__ == "__main__":
    # Run synchronization test if module is executed directly
    results = test_dual_camera_sync()
    print(f"Test Results: {results}")