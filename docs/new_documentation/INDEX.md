# Shimmer3 GSR+ Comprehensive Documentation Index

## Introduction

This documentation suite provides comprehensive coverage of the Shimmer3 GSR+ device integration within the Multi-Sensor Recording System. The documentation follows a component-first approach, organizing information into three primary documents that address different user needs and use cases.

The Shimmer3 GSR+ represents a professional-grade wearable sensor platform designed for physiological research applications. This integration enables precise galvanic skin response measurements alongside complementary biometric data collection, providing researchers with a robust platform for psychophysiological studies.

## Documentation Structure

### Primary Documentation Components

The documentation is organized into three interconnected components, each serving specific user needs:

#### 1. [Technical Deep-Dive](README_shimmer3_gsr_plus.md)
**Audience**: Developers and System Architects  
**Purpose**: Comprehensive technical analysis of internal design and implementation

**Key Contents**:
- Device hardware specifications and sensor capabilities  
- System architecture and integration patterns
- Class design and component relationships
- Complex algorithms for device discovery and data processing
- Threading architecture and performance optimization
- Error handling and recovery mechanisms
- SDK integration with online source references

**When to Use**: System development, architecture planning, debugging complex issues, extending functionality

#### 2. [Practical User Guide](USER_GUIDE_shimmer3_gsr_plus.md)
**Audience**: Researchers and End-Users  
**Purpose**: Step-by-step practical guide for effective device usage

**Key Contents**:
- Pre-flight checklist and hardware requirements
- Device preparation and electrode placement protocols
- Software configuration for PC and Android platforms
- Sensor configuration and range selection guidelines
- Data collection workflows and quality assessment
- Troubleshooting guide and best practices
- Integration with analysis software (R, MATLAB)

**When to Use**: Setting up experiments, configuring devices, collecting data, troubleshooting issues

#### 3. [Protocol and Data Contract](PROTOCOL_shimmer3_gsr_plus.md)
**Audience**: Developers and Data Analysts  
**Purpose**: Complete specification of data formats and communication protocols

**Key Contents**:
- Data structure definitions and specifications
- JSON message formats for network communication
- API specifications for Python and Android platforms
- CSV export format with column specifications
- Session metadata format and quality metrics
- Error codes and status message formats

**When to Use**: API integration, data analysis, protocol implementation, format validation

## Navigation Guide

### For New Users

**First-Time Setup**: Start with the [User Guide Prerequisites](USER_GUIDE_shimmer3_gsr_plus.md#pre-flight-checklist) to ensure all hardware and software requirements are met.

**Device Configuration**: Follow the [Step-by-Step Setup Guide](USER_GUIDE_shimmer3_gsr_plus.md#step-by-step-setup-guide) for initial device configuration and connection establishment.

**Data Collection**: Use the [Data Collection Workflow](USER_GUIDE_shimmer3_gsr_plus.md#data-collection-workflow) for structured recording sessions.

### For Developers

**Architecture Understanding**: Begin with the [System Integration Architecture](README_shimmer3_gsr_plus.md#architecture-overview) to understand the overall design.

**API Integration**: Reference the [API Specifications](PROTOCOL_shimmer3_gsr_plus.md#api-specifications) for programmatic access and control.

**Data Processing**: Examine the [Complex Algorithms and Logic](README_shimmer3_gsr_plus.md#complex-algorithms-and-logic) section for implementation details.

### For Data Analysts

**Data Format Understanding**: Start with [CSV Export Format](PROTOCOL_shimmer3_gsr_plus.md#csv-export-format) to understand data structure.

**Quality Assessment**: Review [Data Quality Assessment](USER_GUIDE_shimmer3_gsr_plus.md#data-quality-assessment) for quality metrics and validation procedures.

**Metadata Interpretation**: Use [JSON Session Metadata Format](PROTOCOL_shimmer3_gsr_plus.md#json-session-metadata-format) to understand session context.

## Quick Reference

### Device Specifications Summary

| Specification | Value | Notes |
|---------------|-------|-------|
| **Primary Sensor** | GSR (Galvanic Skin Response) | High-precision electrodermal activity |
| **Sampling Rate** | 1 Hz to 1000 Hz | Configurable, 51.2 Hz recommended |
| **GSR Ranges** | 5 ranges + auto-range | 10kΩ to 4.7MΩ coverage |
| **Additional Sensors** | PPG, Accelerometer, Gyroscope, Magnetometer | Multi-modal physiological monitoring |
| **Connectivity** | Bluetooth Classic + BLE | Dual-mode connection support |
| **Battery Life** | 24+ hours | Typical continuous operation |
| **Data Storage** | MicroSD + Network Transfer | Hybrid storage approach |

### Connection Methods

| Method | Use Case | Advantages | Limitations |
|--------|----------|-------------|-------------|
| **Direct PC** | Laboratory research | Low latency, full control | PC Bluetooth required |
| **Android-Mediated** | Mobile research | Portable, Android integration | Android device dependency |
| **Simulation** | Development/Testing | No hardware required | Synthetic data only |

### GSR Range Selection Guide

| Range | Resistance | Conductance | Typical Use Case |
|-------|------------|-------------|------------------|
| **0** | 10kΩ - 56kΩ | 18-100 μS | High arousal, stress research |
| **1** | 56kΩ - 220kΩ | 4.5-18 μS | Normal conditions, general studies |
| **2** | 220kΩ - 680kΩ | 1.5-4.5 μS | Dry skin, low humidity |
| **3** | 680kΩ - 4.7MΩ | 0.2-1.5 μS | Very dry skin, special populations |
| **4** | Auto-Range | Dynamic | Long-term monitoring, unknown conditions |

## External Resources and References

### Official Shimmer Research Resources

**Shimmer Research Official Website**: [www.shimmersensing.com](https://www.shimmersensing.com)
- Official hardware documentation
- Firmware updates and changelogs
- Technical support and user forums
- Product specifications and datasheets

**Shimmer Java Android API**: [github.com/ShimmerEngineering/Shimmer-Java-Android-API](https://github.com/ShimmerEngineering/Shimmer-Java-Android-API)
- Official Android SDK from Shimmer Research
- API documentation and examples
- Latest SDK updates and bug fixes
- Community contributions and extensions

### Community and Extended Resources

**pyshimmer Library**: [github.com/seemoo-lab/pyshimmer](https://github.com/seemoo-lab/pyshimmer)
- Python library for direct PC communication
- Cross-platform Bluetooth support
- Research-focused implementation
- Academic community contributions

**Shimmer SDK Fork**: [github.com/buccancs/shimmer-sdk](https://github.com/buccancs/shimmer-sdk)
- Enhanced SDK with additional features
- Integration examples and utilities
- Extended device support
- Research application focus

**Shimmer Android API Fork**: [github.com/buccancs/ShimmerAndroidAPI](https://github.com/buccancs/ShimmerAndroidAPI)
- Extended Android integration
- Multi-device coordination features
- Enhanced data processing capabilities
- Production-ready implementations

### Academic and Research References

**GSR Measurement Principles**:
- Boucsein, W. (2012). *Electrodermal Activity*. Springer Science+Business Media
- Critchley, H. D. (2002). Electrodermal responses: What happens in the brain. *The Neuroscientist*, 8(2), 132-142

**Physiological Signal Processing**:
- Benedek, M., & Kaernbach, C. (2010). A continuous measure of phasic electrodermal activity. *Journal of Neuroscience Methods*, 190(1), 80-91
- Greco, A., et al. (2016). cvxEDA: A convex optimization approach to electrodermal activity processing. *IEEE Transactions on Biomedical Engineering*, 63(4), 797-804

**Wearable Sensor Applications**:
- Picard, R. W., et al. (2001). Affective wearables. *Personal Technologies*, 1(4), 231-240
- Schmidt, P., et al. (2018). Introducing WESAD, a multimodal dataset for wearable stress and affect detection. *ICMI '18: Proceedings of the 2018 on International Conference on Multimodal Interaction*

## Integration Examples

### Basic Python Integration

```python
# Quick start example
from shimmer_manager import ShimmerManager

# Initialize manager
manager = ShimmerManager(enable_android_integration=True)
manager.initialize()

# Discover and connect devices
devices = manager.scan_and_pair_devices()
if devices['direct'] or devices['android']:
    manager.connect_devices(devices)
    
    # Configure sensors
    channels = {"GSR", "PPG_A13", "ACCEL_X", "ACCEL_Y", "ACCEL_Z"}
    for device_id in manager.device_status:
        manager.set_enabled_channels(device_id, channels)
    
    # Start recording
    session_id = f"test_session_{int(time.time())}"
    manager.start_recording(session_id)
    
    # Monitor for 60 seconds
    time.sleep(60)
    
    # Stop and cleanup
    manager.stop_recording()
    manager.cleanup()
```

### Android Integration Example

```kotlin
// Android integration example
class ShimmerActivity : AppCompatActivity() {
    private lateinit var shimmerManager: ShimmerAndroidManager
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        shimmerManager = ShimmerAndroidManager(this)
        shimmerManager.initialize()
        
        // Set data callback
        shimmerManager.setDataCallback { objectCluster ->
            val sample = objectCluster.toShimmerSample("device_001")
            processShimmerData(sample)
        }
        
        // Scan and connect
        lifecycleScope.launch {
            val devices = shimmerManager.scanForDevices()
            if (devices.isNotEmpty()) {
                val result = shimmerManager.connectDevice(
                    devices.first().macAddress,
                    BluetoothConnectionType.CLASSIC
                )
                if (result.success) {
                    startDataCollection()
                }
            }
        }
    }
}
```

## Version Information

- **Documentation Version**: 1.0.0
- **Last Updated**: December 2024
- **Compatible SDK Versions**: 
  - Shimmer Java Android API: 3.2.3_beta+
  - pyshimmer: 1.0.0+
- **Minimum Android API**: 24 (Android 7.0)
- **Python Requirements**: 3.8+

## Support and Contributing

### Getting Help

1. **Documentation Issues**: Check the [troubleshooting sections](USER_GUIDE_shimmer3_gsr_plus.md#troubleshooting-guide) in each document
2. **Technical Support**: Refer to the [Shimmer Support Forum](https://www.shimmersensing.com/support/)
3. **API Issues**: Review [GitHub Issues](https://github.com/ShimmerEngineering/Shimmer-Java-Android-API/issues) for known problems

### Contributing

Contributions to improve this documentation are welcome:

1. **Error Corrections**: Submit corrections for technical accuracy
2. **Usage Examples**: Add practical examples and use cases
3. **Integration Guides**: Contribute guides for specific research applications
4. **Performance Optimizations**: Share optimization techniques and best practices

### Feedback

Documentation feedback helps improve usability and accuracy:

- **Clarity Issues**: Identify sections needing clarification
- **Missing Information**: Suggest additional topics to cover
- **Use Case Examples**: Propose specific application examples
- **Integration Challenges**: Report difficulties in implementation

This comprehensive documentation provides the foundation for successful integration and utilization of Shimmer3 GSR+ devices within research and application environments. The modular structure ensures that users can quickly find relevant information while providing complete technical details for advanced implementation scenarios.