# Master Clock Synchronizer - Troubleshooting and Diagnostics Guide

## Table of Contents

- [Overview](#overview)
- [Quick Diagnostic Checklist](#quick-diagnostic-checklist)
  - [Emergency 5-Minute Diagnosis](#emergency-5-minute-diagnosis)
- [Common Issues and Solutions](#common-issues-and-solutions)
  - [Synchronization Problems](#synchronization-problems)
  - [Network Connectivity Issues](#network-connectivity-issues)
  - [Performance Degradation](#performance-degradation)
  - [Device Connection Problems](#device-connection-problems)
- [Advanced Diagnostics](#advanced-diagnostics)
  - [Network Analysis](#network-analysis)
  - [Timing Analysis](#timing-analysis)
  - [System Resource Analysis](#system-resource-analysis)
- [Diagnostic Tools](#diagnostic-tools)
  - [Built-in Diagnostic Commands](#built-in-diagnostic-commands)
  - [External Tools](#external-tools)
  - [Log Analysis](#log-analysis)
- [Recovery Procedures](#recovery-procedures)
  - [Automatic Recovery](#automatic-recovery)
    - [Self-Healing System Implementation](#self-healing-system-implementation)
  - [Manual Recovery Steps](#manual-recovery-steps)
  - [Emergency Procedures](#emergency-procedures)
    - [Complete System Recovery](#complete-system-recovery)
- [Preventive Maintenance](#preventive-maintenance)
  - [Regular Health Checks](#regular-health-checks)
  - [System Optimization](#system-optimization)
  - [Monitoring Setup](#monitoring-setup)

## Overview

This guide provides comprehensive troubleshooting procedures, diagnostic tools, and recovery strategies for the Master Clock Synchronizer. It is designed to help researchers, technicians, and system administrators quickly identify and resolve synchronization issues in research environments.

## Quick Diagnostic Checklist

**Emergency 5-Minute Diagnosis:**

```python
class QuickDiagnostic:
    """Quick diagnostic checklist for immediate problem identification."""
    
    def __init__(self, synchronizer: MasterClockSynchronizer):
        self.sync = synchronizer
        self.issues_found = []
        self.severity_levels = []
    
    def run_quick_check(self) -> dict:
        """Run rapid diagnostic check."""
        logger.info("Running quick diagnostic check...")
        
        # 1. Check if synchronizer is running
        if not self._check_synchronizer_running():
            return self._create_critical_report("Synchronizer not running")
        
        # 2. Check device connectivity
        connectivity_score = self._check_device_connectivity()
        
        # 3. Check sync quality
        quality_score = self._check_sync_quality()
        
        # 4. Check network health
        network_score = self._check_network_health()
        
        # 5. Check system resources
        resource_score = self._check_system_resources()
        
        # Generate quick report
        overall_score = (connectivity_score + quality_score + network_score + resource_score) / 4
        
        return {
            "overall_health": self._grade_health(overall_score),
            "overall_score": overall_score,
            "connectivity_score": connectivity_score,
            "quality_score": quality_score,
            "network_score": network_score,
            "resource_score": resource_score,
            "issues_found": self.issues_found,
            "immediate_actions": self._get_immediate_actions(),
            "diagnosis_timestamp": time.time()
        }
    
    def _check_synchronizer_running(self) -> bool:
        """Check if synchronizer is running properly."""
        try:
            return self.sync.is_running and self.sync.ntp_server.is_running
        except Exception as e:
            self.issues_found.append({
                "type": "synchronizer_not_running",
                "severity": "critical",
                "message": f"Synchronizer not running: {e}"
            })
            return False
    
    def _check_device_connectivity(self) -> float:
        """Check device connectivity health (0.0-1.0)."""
        try:
            devices = self.sync.get_connected_devices()
            
            if not devices:
                self.issues_found.append({
                    "type": "no_devices_connected",
                    "severity": "high",
                    "message": "No devices connected to synchronizer"
                })
                return 0.0
            
            # Check how many devices are responsive
            responsive_count = 0
            total_count = len(devices)
            current_time = time.time()
            
            for device_id, status in devices.items():
                time_since_last_sync = current_time - status.last_sync_time
                
                if time_since_last_sync < 30.0:  # Responsive within 30 seconds
                    responsive_count += 1
                else:
                    self.issues_found.append({
                        "type": "device_unresponsive",
                        "severity": "medium",
                        "message": f"Device {device_id} unresponsive for {time_since_last_sync:.1f}s"
                    })
            
            return responsive_count / total_count
            
        except Exception as e:
            self.issues_found.append({
                "type": "connectivity_check_failed",
                "severity": "medium",
                "message": f"Failed to check connectivity: {e}"
            })
            return 0.5
    
    def _check_sync_quality(self) -> float:
        """Check synchronization quality (0.0-1.0)."""
        try:
            devices = self.sync.get_connected_devices()
            
            if not devices:
                return 0.0
            
            quality_scores = []
            poor_quality_devices = []
            
            for device_id, status in devices.items():
                quality_scores.append(status.sync_quality)
                
                if status.sync_quality < 0.7:
                    poor_quality_devices.append(device_id)
            
            if poor_quality_devices:
                self.issues_found.append({
                    "type": "poor_sync_quality",
                    "severity": "medium",
                    "message": f"Poor sync quality on devices: {poor_quality_devices}"
                })
            
            return np.mean(quality_scores) if quality_scores else 0.0
            
        except Exception as e:
            self.issues_found.append({
                "type": "quality_check_failed",
                "severity": "medium",
                "message": f"Failed to check sync quality: {e}"
            })
            return 0.5
    
    def _check_network_health(self) -> float:
        """Check network health (0.0-1.0)."""
        try:
            # Test NTP server responsiveness
            ntp_responsive = self._test_ntp_response()
            
            # Test PC server responsiveness
            pc_server_responsive = self._test_pc_server_response()
            
            # Estimate network latency
            network_latency = self._estimate_network_latency()
            
            network_score = 0.0
            
            if ntp_responsive:
                network_score += 0.4
            else:
                self.issues_found.append({
                    "type": "ntp_server_unresponsive",
                    "severity": "high",
                    "message": "NTP server not responding"
                })
            
            if pc_server_responsive:
                network_score += 0.4
            else:
                self.issues_found.append({
                    "type": "pc_server_unresponsive", 
                    "severity": "high",
                    "message": "PC server not responding"
                })
            
            # Latency scoring
            if network_latency < 10.0:
                network_score += 0.2
            elif network_latency < 50.0:
                network_score += 0.1
            else:
                self.issues_found.append({
                    "type": "high_network_latency",
                    "severity": "medium",
                    "message": f"High network latency: {network_latency:.1f}ms"
                })
            
            return network_score
            
        except Exception as e:
            self.issues_found.append({
                "type": "network_check_failed",
                "severity": "medium",
                "message": f"Failed to check network health: {e}"
            })
            return 0.5
    
    def _get_immediate_actions(self) -> list:
        """Get immediate action recommendations based on issues found."""
        actions = []
        
        for issue in self.issues_found:
            if issue["type"] == "synchronizer_not_running":
                actions.append("Restart the Master Clock Synchronizer service")
            elif issue["type"] == "no_devices_connected":
                actions.append("Check device connections and restart Android apps")
            elif issue["type"] == "ntp_server_unresponsive":
                actions.append("Restart NTP server component")
            elif issue["type"] == "poor_sync_quality":
                actions.append("Check network stability and device battery levels")
            elif issue["type"] == "high_network_latency":
                actions.append("Check network configuration and reduce network load")
        
        # Add general actions if no specific issues found
        if not actions:
            actions.append("System appears healthy - monitor for emerging issues")
        
        return actions
```

## Common Issues and Solutions

### Synchronization Problems

**Issue: Poor Synchronization Quality**

*Symptoms:*
- Sync quality scores below 0.8
- High time offset values (>50ms)
- Frequent re-synchronization attempts

*Diagnostic Steps:*
```python
def diagnose_sync_quality_issues(synchronizer):
    """Comprehensive sync quality diagnosis."""
    
    # Check device-specific quality
    devices = synchronizer.get_connected_devices()
    problem_devices = []
    
    for device_id, status in devices.items():
        if status.sync_quality < 0.8:
            problem_devices.append({
                'device_id': device_id,
                'quality': status.sync_quality,
                'time_offset_ms': status.time_offset_ms,
                'last_sync_time': status.last_sync_time
            })
    
    # Analyze patterns
    analysis = {
        'total_devices': len(devices),
        'problem_devices': len(problem_devices),
        'problem_percentage': len(problem_devices) / len(devices) * 100 if devices else 0,
        'avg_quality': np.mean([d.sync_quality for d in devices.values()]) if devices else 0,
        'max_time_offset': max([abs(d.time_offset_ms) for d in devices.values()]) if devices else 0
    }
    
    # Generate recommendations
    recommendations = []
    
    if analysis['problem_percentage'] > 50:
        recommendations.append("Network-wide issue detected - check network infrastructure")
    elif analysis['max_time_offset'] > 100:
        recommendations.append("High time offsets - check NTP server synchronization")
    elif len(problem_devices) <= 2:
        recommendations.append("Device-specific issues - restart problematic devices")
    
    return {
        'analysis': analysis,
        'problem_devices': problem_devices,
        'recommendations': recommendations
    }
```

*Solutions:*
1. **Network Optimization:**
   ```bash
   # Reduce network latency
   sudo sysctl -w net.ipv4.tcp_low_latency=1
   
   # Increase buffer sizes
   sudo sysctl -w net.core.rmem_max=16777216
   sudo sysctl -w net.core.wmem_max=16777216
   ```

2. **Adjust Synchronization Parameters:**
   ```python
   # Relax tolerance for unstable networks
   synchronizer.sync_tolerance_ms = 75.0
   
   # Increase sync interval for power saving
   synchronizer.sync_interval = 4.0
   
   # Lower quality threshold temporarily
   synchronizer.quality_threshold = 0.75
   ```

3. **Device-Specific Fixes:**
   ```python
   def fix_device_sync_issues(synchronizer, device_id):
       """Fix sync issues for specific device."""
       
       # Force re-synchronization
       synchronizer._initiate_device_sync(device_id)
       
       # Reset device statistics
       if device_id in synchronizer.connected_devices:
           status = synchronizer.connected_devices[device_id]
           status.sync_quality = 0.0
           status.frame_count = 0
       
       # Send wake-up message
       wake_msg = JsonMessage(type="wake_up")
       wake_msg.timestamp = synchronizer.get_master_timestamp()
       synchronizer.pc_server.send_message(device_id, wake_msg)
   ```

### Network Connectivity Issues

**Issue: Intermittent Device Disconnections**

*Symptoms:*
- Devices appearing and disappearing from connection list
- "Device timeout" messages in logs
- Recording sessions interrupted

*Diagnostic Procedure:*
```python
class NetworkConnectivityDiagnostic:
    """Diagnose network connectivity issues."""
    
    def __init__(self, synchronizer):
        self.sync = synchronizer
        self.connection_history = {}
    
    def monitor_connections(self, duration_minutes=10):
        """Monitor connection stability over time."""
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        while time.time() < end_time:
            current_devices = set(self.sync.connected_devices.keys())
            timestamp = time.time()
            
            # Record current state
            for device_id in current_devices:
                if device_id not in self.connection_history:
                    self.connection_history[device_id] = []
                
                self.connection_history[device_id].append({
                    'timestamp': timestamp,
                    'connected': True,
                    'quality': self.sync.connected_devices[device_id].sync_quality
                })
            
            # Check for missing devices
            all_known_devices = set(self.connection_history.keys())
            missing_devices = all_known_devices - current_devices
            
            for device_id in missing_devices:
                self.connection_history[device_id].append({
                    'timestamp': timestamp,
                    'connected': False,
                    'quality': 0.0
                })
            
            time.sleep(5.0)  # Check every 5 seconds
        
        return self._analyze_connection_stability()
    
    def _analyze_connection_stability(self):
        """Analyze connection stability patterns."""
        stability_report = {}
        
        for device_id, history in self.connection_history.items():
            # Calculate connection uptime
            connected_time = sum(1 for h in history if h['connected'])
            total_time = len(history)
            uptime_percentage = (connected_time / total_time) * 100 if total_time > 0 else 0
            
            # Count disconnection events
            disconnections = 0
            for i in range(1, len(history)):
                if history[i-1]['connected'] and not history[i]['connected']:
                    disconnections += 1
            
            # Average quality when connected
            connected_qualities = [h['quality'] for h in history if h['connected']]
            avg_quality = np.mean(connected_qualities) if connected_qualities else 0
            
            stability_report[device_id] = {
                'uptime_percentage': uptime_percentage,
                'disconnection_count': disconnections,
                'avg_quality_when_connected': avg_quality,
                'stability_grade': self._grade_stability(uptime_percentage, disconnections)
            }
        
        return stability_report
    
    def _grade_stability(self, uptime_percentage, disconnections):
        """Grade connection stability."""
        if uptime_percentage >= 95 and disconnections <= 1:
            return "Excellent"
        elif uptime_percentage >= 85 and disconnections <= 3:
            return "Good"
        elif uptime_percentage >= 70 and disconnections <= 5:
            return "Fair"
        else:
            return "Poor"
```

*Solutions:*

1. **Network Infrastructure Improvements:**
   ```bash
   # Check WiFi signal strength
   iwconfig wlan0
   
   # Optimize WiFi power management
   sudo iwconfig wlan0 power off
   
   # Check for interference
   sudo iwlist scan | grep -E "(ESSID|Frequency|Quality)"
   ```

2. **Connection Resilience Settings:**
   ```python
   # Increase connection timeout
   synchronizer.connection_timeout = 20.0
   
   # Enable automatic reconnection
   synchronizer.auto_reconnect_enabled = True
   synchronizer.reconnect_interval = 5.0
   
   # Increase retry attempts
   synchronizer.max_retry_attempts = 5
   ```

### Performance Degradation

**Issue: Increasing CPU/Memory Usage Over Time**

*Symptoms:*
- Gradually increasing CPU usage
- Memory usage growing over time
- Slower response times
- System becoming unresponsive

*Diagnostic Tools:*
```python
class PerformanceDegradationAnalyzer:
    """Analyze performance degradation patterns."""
    
    def __init__(self):
        self.performance_history = []
        self.monitoring_active = False
    
    def start_monitoring(self):
        """Start long-term performance monitoring."""
        self.monitoring_active = True
        threading.Thread(target=self._monitoring_loop, daemon=True).start()
    
    def _monitoring_loop(self):
        """Monitor performance metrics over time."""
        while self.monitoring_active:
            try:
                import psutil
                
                # Collect system metrics
                metrics = {
                    'timestamp': time.time(),
                    'cpu_percent': psutil.cpu_percent(interval=1),
                    'memory_mb': psutil.virtual_memory().used / 1024 / 1024,
                    'disk_io': psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else {},
                    'network_io': psutil.net_io_counters()._asdict() if psutil.net_io_counters() else {}
                }
                
                # Process-specific metrics
                try:
                    process = psutil.Process()
                    metrics.update({
                        'process_cpu': process.cpu_percent(),
                        'process_memory_mb': process.memory_info().rss / 1024 / 1024,
                        'thread_count': process.num_threads(),
                        'open_files': len(process.open_files())
                    })
                except psutil.NoSuchProcess:
                    pass
                
                self.performance_history.append(metrics)
                
                # Keep only last 24 hours of data (assuming 60s intervals)
                if len(self.performance_history) > 1440:
                    self.performance_history = self.performance_history[-1440:]
                
                time.sleep(60)  # Sample every minute
                
            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
                time.sleep(60)
    
    def detect_degradation(self) -> dict:
        """Detect performance degradation trends."""
        if len(self.performance_history) < 10:
            return {"error": "Insufficient data for trend analysis"}
        
        # Analyze trends over different time windows
        recent_data = self.performance_history[-60:]  # Last hour
        older_data = self.performance_history[-120:-60]  # Hour before that
        
        if len(older_data) < 10:
            return {"error": "Insufficient historical data"}
        
        degradation_analysis = {}
        
        # CPU trend analysis
        recent_cpu = np.mean([d['process_cpu'] for d in recent_data])
        older_cpu = np.mean([d['process_cpu'] for d in older_data])
        cpu_change = recent_cpu - older_cpu
        
        degradation_analysis['cpu'] = {
            'recent_avg': recent_cpu,
            'older_avg': older_cpu,
            'change_percent': cpu_change,
            'degradation_detected': cpu_change > 10.0  # >10% increase
        }
        
        # Memory trend analysis
        recent_memory = np.mean([d['process_memory_mb'] for d in recent_data])
        older_memory = np.mean([d['process_memory_mb'] for d in older_data])
        memory_change = recent_memory - older_memory
        
        degradation_analysis['memory'] = {
            'recent_avg_mb': recent_memory,
            'older_avg_mb': older_memory,
            'change_mb': memory_change,
            'degradation_detected': memory_change > 50.0  # >50MB increase
        }
        
        # Thread count analysis
        recent_threads = np.mean([d['thread_count'] for d in recent_data])
        older_threads = np.mean([d['thread_count'] for d in older_data])
        thread_change = recent_threads - older_threads
        
        degradation_analysis['threads'] = {
            'recent_avg': recent_threads,
            'older_avg': older_threads,
            'change': thread_change,
            'degradation_detected': thread_change > 5  # >5 additional threads
        }
        
        # Overall degradation assessment
        degradation_detected = any([
            degradation_analysis['cpu']['degradation_detected'],
            degradation_analysis['memory']['degradation_detected'],
            degradation_analysis['threads']['degradation_detected']
        ])
        
        degradation_analysis['overall'] = {
            'degradation_detected': degradation_detected,
            'severity': self._assess_degradation_severity(degradation_analysis),
            'recommendations': self._get_degradation_recommendations(degradation_analysis)
        }
        
        return degradation_analysis
    
    def _assess_degradation_severity(self, analysis) -> str:
        """Assess the severity of performance degradation."""
        cpu_degraded = analysis['cpu']['degradation_detected']
        memory_degraded = analysis['memory']['degradation_detected']
        threads_degraded = analysis['threads']['degradation_detected']
        
        degradation_count = sum([cpu_degraded, memory_degraded, threads_degraded])
        
        if degradation_count >= 3:
            return "Critical"
        elif degradation_count == 2:
            return "High"
        elif degradation_count == 1:
            return "Medium"
        else:
            return "Low"
    
    def _get_degradation_recommendations(self, analysis) -> list:
        """Get recommendations for addressing performance degradation."""
        recommendations = []
        
        if analysis['cpu']['degradation_detected']:
            recommendations.append("High CPU usage detected - check for background processes")
            recommendations.append("Consider reducing sync frequency or device count")
        
        if analysis['memory']['degradation_detected']:
            recommendations.append("Memory usage increasing - possible memory leak")
            recommendations.append("Restart synchronizer service to free memory")
        
        if analysis['threads']['degradation_detected']:
            recommendations.append("Thread count increasing - check for thread leaks")
            recommendations.append("Review thread pool configuration")
        
        if not recommendations:
            recommendations.append("Performance is stable - continue monitoring")
        
        return recommendations
```

*Solutions:*

1. **Memory Leak Prevention:**
   ```python
   def prevent_memory_leaks(synchronizer):
       """Implement memory leak prevention measures."""
       
       # Periodic cleanup of old data
       def cleanup_old_data():
           current_time = time.time()
           
           # Clean up old session data
           for session_id, session in list(synchronizer.active_sessions.items()):
               if not session.is_active and (current_time - session.start_timestamp) > 3600:
                   del synchronizer.active_sessions[session_id]
           
           # Clean up old device status entries
           for device_id, status in list(synchronizer.connected_devices.items()):
               if (current_time - status.last_sync_time) > 300:  # 5 minutes
                   del synchronizer.connected_devices[device_id]
       
       # Schedule cleanup every 10 minutes
       cleanup_timer = threading.Timer(600.0, cleanup_old_data)
       cleanup_timer.daemon = True
       cleanup_timer.start()
   ```

2. **Resource Optimization:**
   ```python
   # Optimize thread pool size
   synchronizer.thread_pool = ThreadPoolExecutor(max_workers=8)
   
   # Reduce callback frequency
   synchronizer.sync_interval = 5.0
   
   # Enable garbage collection optimization
   import gc
   gc.set_threshold(700, 10, 10)
   ```

## Recovery Procedures

### Automatic Recovery

**Self-Healing System Implementation:**
```python
class AutoRecoverySystem:
    """Automatic recovery system for common issues."""
    
    def __init__(self, synchronizer):
        self.sync = synchronizer
        self.recovery_active = False
        self.recovery_history = []
        
        # Recovery thresholds
        self.thresholds = {
            'min_sync_quality': 0.6,
            'max_device_timeout': 30.0,
            'max_consecutive_failures': 5,
            'min_device_response_rate': 0.7
        }
    
    def start_auto_recovery(self):
        """Start automatic recovery monitoring."""
        self.recovery_active = True
        threading.Thread(target=self._recovery_loop, daemon=True).start()
    
    def _recovery_loop(self):
        """Main automatic recovery loop."""
        while self.recovery_active:
            try:
                # Check for issues requiring recovery
                issues = self._detect_recovery_triggers()
                
                for issue in issues:
                    recovery_success = self._execute_recovery(issue)
                    
                    # Log recovery attempt
                    self.recovery_history.append({
                        'timestamp': time.time(),
                        'issue_type': issue['type'],
                        'issue_details': issue['details'],
                        'recovery_action': issue['recovery_action'],
                        'success': recovery_success
                    })
                
                time.sleep(10.0)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Auto recovery loop error: {e}")
                time.sleep(5.0)
    
    def _detect_recovery_triggers(self) -> list:
        """Detect conditions that trigger automatic recovery."""
        triggers = []
        
        # Check device sync quality
        devices = self.sync.get_connected_devices()
        for device_id, status in devices.items():
            if status.sync_quality < self.thresholds['min_sync_quality']:
                triggers.append({
                    'type': 'poor_sync_quality',
                    'device_id': device_id,
                    'details': f"Quality: {status.sync_quality}",
                    'recovery_action': 'resync_device'
                })
            
            # Check device timeout
            time_since_sync = time.time() - status.last_sync_time
            if time_since_sync > self.thresholds['max_device_timeout']:
                triggers.append({
                    'type': 'device_timeout',
                    'device_id': device_id,
                    'details': f"Timeout: {time_since_sync:.1f}s",
                    'recovery_action': 'reconnect_device'
                })
        
        # Check NTP server health
        if not self._check_ntp_health():
            triggers.append({
                'type': 'ntp_server_failure',
                'details': "NTP server not responding",
                'recovery_action': 'restart_ntp_server'
            })
        
        return triggers
    
    def _execute_recovery(self, issue) -> bool:
        """Execute recovery action for detected issue."""
        try:
            action = issue['recovery_action']
            
            if action == 'resync_device':
                return self._recover_device_sync(issue['device_id'])
            elif action == 'reconnect_device':
                return self._recover_device_connection(issue['device_id'])
            elif action == 'restart_ntp_server':
                return self._recover_ntp_server()
            else:
                logger.warning(f"Unknown recovery action: {action}")
                return False
                
        except Exception as e:
            logger.error(f"Recovery execution failed for {issue}: {e}")
            return False
    
    def _recover_device_sync(self, device_id: str) -> bool:
        """Recover synchronization for a specific device."""
        try:
            # Force re-synchronization
            self.sync._initiate_device_sync(device_id)
            
            # Wait for sync to improve
            time.sleep(3.0)
            
            # Check if recovery was successful
            if device_id in self.sync.connected_devices:
                new_quality = self.sync.connected_devices[device_id].sync_quality
                return new_quality > self.thresholds['min_sync_quality']
            
            return False
            
        except Exception as e:
            logger.error(f"Device sync recovery failed for {device_id}: {e}")
            return False
    
    def _recover_device_connection(self, device_id: str) -> bool:
        """Recover connection for a specific device."""
        try:
            # Send wake-up message
            wake_msg = JsonMessage(type="connection_recovery")
            wake_msg.timestamp = self.sync.get_master_timestamp()
            
            success = self.sync.pc_server.send_message(device_id, wake_msg)
            
            if not success:
                # Remove device and wait for reconnection
                if device_id in self.sync.connected_devices:
                    del self.sync.connected_devices[device_id]
            
            return success
            
        except Exception as e:
            logger.error(f"Device connection recovery failed for {device_id}: {e}")
            return False
    
    def _recover_ntp_server(self) -> bool:
        """Recover NTP server functionality."""
        try:
            # Stop and restart NTP server
            self.sync.ntp_server.stop()
            time.sleep(2.0)
            
            return self.sync.ntp_server.start()
            
        except Exception as e:
            logger.error(f"NTP server recovery failed: {e}")
            return False
```

### Emergency Procedures

**Complete System Recovery:**
```python
def emergency_system_recovery(synchronizer):
    """Emergency recovery procedure for critical failures."""
    
    logger.critical("Initiating emergency system recovery...")
    
    recovery_steps = [
        ("Stop all active sessions", lambda: stop_all_sessions(synchronizer)),
        ("Disconnect all devices", lambda: disconnect_all_devices(synchronizer)),
        ("Restart NTP server", lambda: restart_ntp_server(synchronizer)),
        ("Restart PC server", lambda: restart_pc_server(synchronizer)),
        ("Clear device cache", lambda: clear_device_cache(synchronizer)),
        ("Reinitialize synchronizer", lambda: reinitialize_synchronizer(synchronizer)),
        ("Verify system health", lambda: verify_system_health(synchronizer))
    ]
    
    recovery_results = []
    
    for step_name, step_function in recovery_steps:
        logger.info(f"Emergency recovery step: {step_name}")
        
        try:
            result = step_function()
            recovery_results.append({
                'step': step_name,
                'success': result,
                'timestamp': time.time()
            })
            
            if not result:
                logger.error(f"Emergency recovery step failed: {step_name}")
                break
                
        except Exception as e:
            logger.error(f"Emergency recovery step exception in {step_name}: {e}")
            recovery_results.append({
                'step': step_name,
                'success': False,
                'error': str(e),
                'timestamp': time.time()
            })
            break
    
    # Generate recovery report
    successful_steps = sum(1 for r in recovery_results if r['success'])
    total_steps = len(recovery_results)
    
    recovery_report = {
        'recovery_completed': successful_steps == len(recovery_steps),
        'successful_steps': successful_steps,
        'total_steps': total_steps,
        'step_results': recovery_results,
        'system_status': 'recovered' if successful_steps == len(recovery_steps) else 'partial_recovery'
    }
    
    logger.info(f"Emergency recovery completed: {recovery_report['system_status']}")
    
    return recovery_report

def stop_all_sessions(synchronizer):
    """Stop all active recording sessions."""
    try:
        active_sessions = list(synchronizer.active_sessions.keys())
        for session_id in active_sessions:
            synchronizer.stop_synchronized_recording(session_id)
        return True
    except Exception as e:
        logger.error(f"Failed to stop sessions: {e}")
        return False

def disconnect_all_devices(synchronizer):
    """Disconnect all connected devices."""
    try:
        connected_devices = list(synchronizer.connected_devices.keys())
        for device_id in connected_devices:
            synchronizer._on_device_disconnected(device_id)
        return True
    except Exception as e:
        logger.error(f"Failed to disconnect devices: {e}")
        return False
```

This comprehensive troubleshooting guide provides systematic approaches to diagnosing and resolving issues with the Master Clock Synchronizer, ensuring researchers can maintain reliable synchronization even in challenging conditions.