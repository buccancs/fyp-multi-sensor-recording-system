# Webcam Configuration Guide

## Multi-Sensor Recording System - PC Webcam Integration

**Version:** 3.3  
**Date:** 2025-07-29  
**Milestone:** 3.3 - Webcam Capture Integration (PC Recording)

---

## Table of Contents

1. [Configuration Overview](#configuration-overview)
2. [Camera Selection and Detection](#camera-selection-and-detection)
3. [Recording Parameters](#recording-parameters)
4. [Preview Settings](#preview-settings)
5. [Advanced Configuration](#advanced-configuration)
6. [Performance Optimization](#performance-optimization)
7. [Use Case Configurations](#use-case-configurations)
8. [Configuration File Management](#configuration-file-management)
9. [Troubleshooting Configuration Issues](#troubleshooting-configuration-issues)
10. [Best Practices](#best-practices)

---

## Configuration Overview

The webcam configuration system provides comprehensive control over camera selection, recording parameters, preview settings, and performance optimization. The system supports both automatic configuration for ease of use and manual configuration for advanced users.

### Configuration Hierarchy

```
Webcam Configuration
├── Camera Selection
│   ├── Automatic Detection
│   ├── Manual Selection
│   └── Multiple Camera Support
├── Recording Parameters
│   ├── Resolution Settings
│   ├── Frame Rate Control
│   ├── Codec Selection
│   └── Quality Settings
├── Preview Configuration
│   ├── Display Settings
│   ├── Performance Options
│   └── Scaling Controls
└── Advanced Options
    ├── Error Recovery
    ├── Resource Management
    └── Fallback Systems
```

### Configuration Methods

1. **Automatic Configuration**: System detects optimal settings
2. **GUI Configuration**: User-friendly interface for common settings
3. **File-Based Configuration**: Direct JSON file editing for advanced users
4. **API Configuration**: Programmatic configuration for integration

---

## Camera Selection and Detection

### Automatic Camera Detection

The system automatically scans for available cameras and selects optimal settings:

#### Detection Process

1. **Hardware Scan**: Tests camera indices 0-9
2. **Capability Testing**: Checks supported resolutions and frame rates
3. **Quality Assessment**: Evaluates camera performance
4. **Optimal Selection**: Chooses best available camera

#### Configuration Parameters

```json
{
  "auto_detect_cameras": true,
  "detection_range": 10,
  "detection_timeout": 5.0,
  "prefer_higher_resolution": true
}
```

### Manual Camera Selection

For systems with multiple cameras or specific requirements:

#### Camera Index Selection

```json
{
  "camera_index": 0,
  "camera_name": "Built-in Camera (HD 1280x720)"
}
```

**Camera Index Guidelines:**
- **Index 0**: Usually built-in/primary camera
- **Index 1+**: External USB cameras
- **Virtual Cameras**: May occupy indices (OBS, ManyCam)

#### Camera Information

Each detected camera provides:

```json
{
  "index": 0,
  "name": "Built-in Camera (HD 1280x720)",
  "resolution": [1280, 720],
  "max_fps": 30.0,
  "supported_resolutions": [
    [320, 240],
    [640, 480],
    [1280, 720],
    [1920, 1080]
  ],
  "is_working": true
}
```

### Multiple Camera Support

#### Camera Switching

Switch between cameras without restarting:

1. **Runtime Detection**: Scan for new cameras
2. **Hot Swapping**: Change active camera
3. **Fallback Support**: Automatic alternative selection

#### Configuration Example

```json
{
  "primary_camera": 0,
  "fallback_cameras": [1, 2],
  "auto_fallback": true,
  "fallback_delay": 2.0
}
```

---

## Recording Parameters

### Resolution Configuration

#### Supported Resolutions

| Resolution | Aspect Ratio | Use Case |
|------------|--------------|----------|
| 320x240 (QVGA) | 4:3 | Low bandwidth/storage |
| 640x480 (VGA) | 4:3 | Standard quality |
| 854x480 (480p) | 16:9 | Widescreen SD |
| 1280x720 (720p) | 16:9 | HD recording |
| 1920x1080 (1080p) | 16:9 | Full HD |
| 3840x2160 (4K) | 16:9 | Ultra HD |

#### Resolution Selection

```json
{
  "recording": {
    "resolution": [1280, 720],
    "auto_resolution": false,
    "max_resolution": [1920, 1080],
    "prefer_16_9": true
  }
}
```

**Selection Criteria:**
- **Camera Capability**: Must be supported by hardware
- **Performance**: Higher resolution requires more resources
- **Storage**: Larger files with higher resolution
- **Bandwidth**: Network streaming considerations

### Frame Rate Configuration

#### Standard Frame Rates

| Frame Rate | Use Case | Quality |
|------------|----------|---------|
| 15 fps | Low bandwidth | Basic |
| 24 fps | Cinematic | Standard |
| 30 fps | General recording | Good |
| 60 fps | Smooth motion | High |

#### Frame Rate Settings

```json
{
  "recording": {
    "fps": 30,
    "auto_fps": false,
    "max_fps": 60,
    "adaptive_fps": true
  }
}
```

**Considerations:**
- **Camera Support**: Verify hardware capability
- **CPU Usage**: Higher FPS increases processing load
- **File Size**: More frames = larger files
- **Synchronization**: Match with other devices

### Codec Configuration

#### Supported Codecs

| Codec | Description | Pros | Cons |
|-------|-------------|------|------|
| MP4V | MPEG-4 Part 2 | Good compression, widely supported | Moderate quality |
| H264 | Advanced Video Coding | Excellent compression, high quality | CPU intensive |
| XVID | MPEG-4 variant | Good compatibility | Larger files |
| MJPG | Motion JPEG | Universal compatibility | Large files |

#### Codec Selection

```json
{
  "recording": {
    "codec": "mp4v",
    "fallback_codecs": ["mp4v", "XVID", "MJPG"],
    "auto_codec_selection": true,
    "codec_testing": true
  }
}
```

#### Codec Fallback System

The system automatically tests codecs and falls back to working alternatives:

1. **Primary Codec**: User's preferred choice
2. **Fallback Chain**: Alternative codecs in order of preference
3. **Automatic Testing**: Validates codec availability
4. **Runtime Switching**: Changes codec if encoding fails

### Quality Settings

#### Quality Parameters

```json
{
  "recording": {
    "quality": 80,
    "bitrate": "auto",
    "keyframe_interval": 30,
    "compression_level": "medium"
  }
}
```

**Quality Scale (0-100):**
- **0-30**: Low quality, small files
- **31-60**: Medium quality, balanced
- **61-85**: High quality, larger files
- **86-100**: Maximum quality, very large files

---

## Preview Settings

### Display Configuration

#### Preview Window Settings

```json
{
  "preview": {
    "max_width": 640,
    "max_height": 480,
    "enable_scaling": true,
    "maintain_aspect_ratio": true,
    "fullscreen_available": true
  }
}
```

#### Scaling Options

| Setting | Description | Performance Impact |
|---------|-------------|-------------------|
| No Scaling | Display at native resolution | Low |
| Proportional | Maintain aspect ratio | Medium |
| Stretch | Fill preview area | Medium |
| Crop | Crop to fit | Low |

### Performance Settings

#### Preview Frame Rate

```json
{
  "preview": {
    "fps": 30,
    "adaptive_fps": true,
    "min_fps": 15,
    "max_fps": 60
  }
}
```

**Performance Considerations:**
- **Lower FPS**: Reduces CPU usage
- **Adaptive FPS**: Adjusts based on system load
- **Independent Control**: Preview FPS ≠ Recording FPS

#### Resource Management

```json
{
  "preview": {
    "buffer_size": 3,
    "skip_frames": false,
    "priority": "normal",
    "thread_priority": "normal"
  }
}
```

---

## Advanced Configuration

### Error Recovery Settings

#### Camera Resource Management

```json
{
  "error_recovery": {
    "camera_conflicts": {
      "auto_recovery": true,
      "max_attempts": 3,
      "retry_delay": 1.0,
      "exponential_backoff": true
    }
  }
}
```

#### Network Recovery

```json
{
  "error_recovery": {
    "network_sync": {
      "auto_recovery": true,
      "max_failures": 5,
      "timeout": 10.0,
      "retry_interval": 2.0
    }
  }
}
```

### Resource Limits

#### System Resource Management

```json
{
  "resource_limits": {
    "max_cpu_usage": 80,
    "max_memory_mb": 1024,
    "disk_space_threshold": 1000,
    "network_bandwidth_limit": 0
  }
}
```

#### Performance Monitoring

```json
{
  "monitoring": {
    "enable_performance_tracking": true,
    "log_performance_metrics": true,
    "alert_on_resource_limits": true,
    "performance_history_size": 1000
  }
}
```

### Session Configuration

#### Session Management

```json
{
  "session": {
    "auto_create_folders": true,
    "folder_naming": "timestamp",
    "metadata_generation": true,
    "cleanup_old_sessions": false,
    "max_session_age_days": 30
  }
}
```

---

## Performance Optimization

### CPU Optimization

#### Settings for High CPU Usage

```json
{
  "performance": {
    "cpu_optimization": {
      "reduce_preview_fps": true,
      "target_preview_fps": 15,
      "disable_preview_scaling": true,
      "use_hardware_acceleration": true,
      "thread_count": "auto"
    }
  }
}
```

#### Codec Selection for Performance

| Codec | CPU Usage | Quality | File Size |
|-------|-----------|---------|-----------|
| MJPG | Low | Medium | Large |
| MP4V | Medium | Good | Medium |
| H264 | High | Excellent | Small |

### Memory Optimization

#### Memory Management Settings

```json
{
  "performance": {
    "memory_optimization": {
      "buffer_management": "conservative",
      "frame_cache_size": 5,
      "garbage_collection": "aggressive",
      "memory_limit_mb": 512
    }
  }
}
```

### Storage Optimization

#### Disk Usage Settings

```json
{
  "performance": {
    "storage_optimization": {
      "compression_level": "medium",
      "temporary_files": "memory",
      "write_buffer_size": 1024,
      "async_writing": true
    }
  }
}
```

---

## Use Case Configurations

### Research/Laboratory Use

#### High-Quality Recording Configuration

```json
{
  "research_config": {
    "camera_index": 0,
    "recording": {
      "resolution": [1920, 1080],
      "fps": 30,
      "codec": "H264",
      "quality": 90
    },
    "preview": {
      "max_width": 800,
      "max_height": 600,
      "fps": 30
    },
    "session": {
      "auto_create_folders": true,
      "metadata_generation": true
    }
  }
}
```

### Educational/Training Use

#### Balanced Quality Configuration

```json
{
  "education_config": {
    "camera_index": 0,
    "recording": {
      "resolution": [1280, 720],
      "fps": 24,
      "codec": "MP4V",
      "quality": 75
    },
    "preview": {
      "max_width": 640,
      "max_height": 480,
      "fps": 24
    }
  }
}
```

### Low-Resource Systems

#### Performance-Optimized Configuration

```json
{
  "low_resource_config": {
    "camera_index": 0,
    "recording": {
      "resolution": [640, 480],
      "fps": 15,
      "codec": "MJPG",
      "quality": 60
    },
    "preview": {
      "max_width": 320,
      "max_height": 240,
      "fps": 15,
      "enable_scaling": false
    },
    "performance": {
      "cpu_optimization": {
        "reduce_preview_fps": true,
        "disable_preview_scaling": true
      }
    }
  }
}
```

### Multi-Camera Setup

#### Multiple Camera Configuration

```json
{
  "multi_camera_config": {
    "primary_camera": 0,
    "fallback_cameras": [1, 2],
    "auto_fallback": true,
    "recording": {
      "resolution": [1280, 720],
      "fps": 30,
      "codec": "MP4V",
      "quality": 80
    },
    "camera_switching": {
      "enable_hot_swap": true,
      "detection_interval": 5.0,
      "prefer_higher_quality": true
    }
  }
}
```

---

## Configuration File Management

### Configuration File Structure

#### Complete Configuration Example

```json
{
  "version": "3.3",
  "last_updated": "2025-07-29T14:30:22",
  "camera_index": 0,
  "camera_name": "Built-in Camera (HD 1280x720)",
  "auto_detect_cameras": true,
  
  "recording": {
    "codec": "mp4v",
    "resolution": [1280, 720],
    "fps": 30,
    "quality": 80,
    "file_format": "mp4"
  },
  
  "preview": {
    "max_width": 640,
    "max_height": 480,
    "fps": 30,
    "enable_scaling": true,
    "maintain_aspect_ratio": true
  },
  
  "fallback_codecs": ["mp4v", "XVID", "MJPG"],
  
  "error_recovery": {
    "camera_conflicts": {
      "auto_recovery": true,
      "max_attempts": 3
    },
    "network_sync": {
      "auto_recovery": true,
      "max_failures": 5
    }
  },
  
  "performance": {
    "cpu_optimization": {
      "use_hardware_acceleration": true,
      "thread_count": "auto"
    },
    "memory_optimization": {
      "buffer_management": "balanced"
    }
  }
}
```

### Configuration Validation

#### Validation Rules

1. **Required Fields**: Essential configuration parameters
2. **Value Ranges**: Acceptable parameter ranges
3. **Compatibility**: Hardware capability validation
4. **Dependencies**: Inter-parameter relationships

#### Validation Example

```json
{
  "validation": {
    "camera_index": {
      "type": "integer",
      "range": [0, 9],
      "required": true
    },
    "recording.resolution": {
      "type": "array",
      "length": 2,
      "element_type": "integer",
      "min_value": 160,
      "max_value": 4096
    },
    "recording.fps": {
      "type": "integer",
      "range": [1, 120],
      "camera_dependent": true
    }
  }
}
```

### Configuration Backup and Restore

#### Backup Strategy

```json
{
  "backup": {
    "auto_backup": true,
    "backup_interval": "daily",
    "max_backups": 10,
    "backup_location": "config_backups/"
  }
}
```

#### Restore Procedures

1. **Automatic Restore**: On configuration corruption
2. **Manual Restore**: User-initiated restoration
3. **Factory Reset**: Return to default settings

---

## Troubleshooting Configuration Issues

### Common Configuration Problems

#### Invalid Camera Index

**Problem**: Camera index doesn't exist
**Solution**: Use automatic detection or try different indices

```json
{
  "camera_index": 0,
  "auto_detect_cameras": true,
  "fallback_cameras": [1, 2, 3]
}
```

#### Unsupported Resolution

**Problem**: Camera doesn't support configured resolution
**Solution**: Use supported resolution or auto-detection

```json
{
  "recording": {
    "resolution": [1280, 720],
    "auto_resolution": true,
    "fallback_resolutions": [
      [1280, 720],
      [640, 480],
      [320, 240]
    ]
  }
}
```

#### Codec Not Available

**Problem**: Selected codec not supported
**Solution**: Configure fallback codecs

```json
{
  "recording": {
    "codec": "mp4v",
    "auto_codec_selection": true,
    "fallback_codecs": ["mp4v", "XVID", "MJPG"]
  }
}
```

### Configuration Validation Errors

#### Error Types and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| Invalid JSON | Syntax error | Check JSON formatting |
| Missing required field | Incomplete config | Add required parameters |
| Value out of range | Invalid parameter | Use valid range |
| Hardware incompatible | Unsupported setting | Use compatible values |

### Recovery Procedures

#### Configuration Reset

1. **Soft Reset**: Restore from backup
2. **Hard Reset**: Return to factory defaults
3. **Selective Reset**: Reset specific sections

#### Reset Commands

```python
# Reset to defaults
config_manager.reset_to_defaults()

# Reset specific section
config_manager.reset_section("recording")

# Restore from backup
config_manager.restore_from_backup("2025-07-29_backup.json")
```

---

## Best Practices

### Configuration Management

#### Version Control

1. **Track Changes**: Document configuration modifications
2. **Backup Before Changes**: Save working configurations
3. **Test Changes**: Validate new settings before deployment
4. **Document Settings**: Maintain configuration documentation

#### Environment-Specific Configurations

1. **Development**: High logging, relaxed limits
2. **Testing**: Balanced settings, comprehensive monitoring
3. **Production**: Optimized performance, minimal logging
4. **Research**: High quality, detailed metadata

### Performance Optimization

#### General Guidelines

1. **Start Conservative**: Begin with lower settings
2. **Incremental Increases**: Gradually improve quality
3. **Monitor Resources**: Watch CPU, memory, disk usage
4. **Test Thoroughly**: Validate all changes

#### Hardware-Specific Optimization

| Hardware Type | Recommended Settings |
|---------------|---------------------|
| High-end Desktop | 1080p, 30fps, H264 |
| Standard Laptop | 720p, 24fps, MP4V |
| Low-end System | 480p, 15fps, MJPG |
| Multiple Cameras | 720p, 24fps, XVID |

### Security Considerations

#### Configuration Security

1. **File Permissions**: Restrict configuration file access
2. **Backup Security**: Secure backup storage
3. **Network Settings**: Protect network configuration
4. **Audit Trail**: Log configuration changes

#### Privacy Settings

```json
{
  "privacy": {
    "camera_access_logging": true,
    "data_retention_days": 30,
    "anonymize_metadata": false,
    "secure_storage": true
  }
}
```

### Maintenance

#### Regular Maintenance Tasks

1. **Configuration Review**: Monthly settings review
2. **Performance Monitoring**: Weekly performance checks
3. **Backup Verification**: Regular backup testing
4. **Update Management**: Keep configurations current

#### Automated Maintenance

```json
{
  "maintenance": {
    "auto_cleanup": true,
    "cleanup_interval": "weekly",
    "performance_optimization": true,
    "config_validation": "daily"
  }
}
```

---

## Appendix

### Configuration Templates

#### Basic Template

```json
{
  "camera_index": 0,
  "auto_detect_cameras": true,
  "recording": {
    "codec": "mp4v",
    "resolution": [1280, 720],
    "fps": 30,
    "quality": 80
  },
  "preview": {
    "max_width": 640,
    "max_height": 480,
    "fps": 30
  },
  "fallback_codecs": ["mp4v", "XVID", "MJPG"]
}
```

#### Advanced Template

```json
{
  "camera_index": 0,
  "auto_detect_cameras": true,
  "recording": {
    "codec": "H264",
    "resolution": [1920, 1080],
    "fps": 30,
    "quality": 85,
    "bitrate": "auto"
  },
  "preview": {
    "max_width": 800,
    "max_height": 600,
    "fps": 30,
    "enable_scaling": true
  },
  "error_recovery": {
    "camera_conflicts": {
      "auto_recovery": true,
      "max_attempts": 3
    }
  },
  "performance": {
    "cpu_optimization": {
      "use_hardware_acceleration": true
    }
  }
}
```

### Parameter Reference

#### Complete Parameter List

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| camera_index | integer | 0-9 | 0 | Camera device index |
| auto_detect_cameras | boolean | - | true | Enable automatic detection |
| recording.codec | string | See codecs | "mp4v" | Video codec |
| recording.resolution | array | [160,120]-[4096,2160] | [1280,720] | Recording resolution |
| recording.fps | integer | 1-120 | 30 | Recording frame rate |
| recording.quality | integer | 0-100 | 80 | Recording quality |
| preview.max_width | integer | 160-2048 | 640 | Preview max width |
| preview.max_height | integer | 120-1536 | 480 | Preview max height |
| preview.fps | integer | 1-60 | 30 | Preview frame rate |

### Migration Guide

#### Upgrading Configurations

When upgrading from previous versions:

1. **Backup Current Config**: Save existing settings
2. **Check Compatibility**: Verify parameter support
3. **Update Format**: Convert to new format if needed
4. **Validate Settings**: Test new configuration
5. **Document Changes**: Record modifications made

---

*This configuration guide provides comprehensive information for optimizing webcam settings. For additional support, please refer to the User Manual and Troubleshooting Guide.*
