# Vendor SDK Management Guide

This guide addresses the **High Priority** recommendation: "Regularly update vendor SDKs: Monitor the Shimmer and thermal camera SDK versions."

## Overview

The Multi-Sensor Recording System relies on vendor-provided SDKs that are not managed by standard dependency management tools like Gradle or pip. These SDKs require manual monitoring and updating procedures.

## Current Vendor SDKs

### 📟 Shimmer GSR Sensor SDK

**Current Version**: `0.11.4_beta`  
**Vendor**: Shimmer Engineering  
**Repository**: [Shimmer-Java-Android-API](https://github.com/ShimmerEngineering/Shimmer-Java-Android-API)  
**Files**:
- `shimmerandroidinstrumentdriver-3.2.3_beta.aar`
- `shimmerbluetoothmanager-0.11.4_beta.jar`
- `shimmerdriver-0.11.4_beta.jar`
- `shimmerdriverpc-0.11.4_beta.jar`

**⚠️ Risk Assessment**: Medium (Beta version in production)

### 🌡️ Thermal Camera SDK (TopDon)

**Current Version**: `1.3.7`  
**Vendor**: TopDon Technology  
**Website**: [topdon.com](https://www.topdon.com/)  
**Files**:
- `topdon_1.3.7.aar`
- `libusbdualsdk_1.3.4_2406271906_standard.aar`
- `opengl_1.3.2_standard.aar`
- `suplib-release.aar`

**⚠️ Risk Assessment**: Low (Proprietary SDK, manual monitoring required)

## Monitoring Procedures

### 🔄 Automated Monitoring

The repository includes an automated monitoring script:

```bash
# Basic SDK health check
python scripts/monitor_vendor_sdks.py

# Check for updates (requires internet)
python scripts/monitor_vendor_sdks.py --check-updates

# Generate detailed report
python scripts/monitor_vendor_sdks.py --generate-report
```

**Schedule**: The monitoring script runs automatically every Monday via GitHub Actions workflow.

### 📊 Manual Monitoring Checklist

#### Weekly Tasks
- [ ] Review automated monitoring reports in GitHub Issues
- [ ] Check vendor websites/repositories for announcements
- [ ] Monitor vendor release notes for security patches

#### Monthly Tasks  
- [ ] Download and evaluate new vendor SDK versions
- [ ] Test compatibility with current codebase in staging environment
- [ ] Document any breaking changes or new features

#### Quarterly Tasks
- [ ] Evaluate beta → stable version migration opportunities
- [ ] Review vendor support policies and EOL timelines
- [ ] Update vendor contact information and support channels

## Update Procedures

### 🚨 Security Update Process (Critical)

For security-related updates, follow this expedited process:

1. **Immediate Assessment** (< 2 hours)
   ```bash
   # Check current risk level
   python scripts/monitor_vendor_sdks.py --check-updates
   ```

2. **Emergency Testing** (< 24 hours)
   - Download security-patched SDK
   - Deploy to staging environment
   - Run minimal smoke tests
   - Verify no regressions in core functionality

3. **Production Deployment** (< 48 hours)
   - Deploy to production during maintenance window
   - Monitor system health for 24 hours
   - Rollback plan ready if issues detected

### 📋 Standard Update Process

For routine updates, follow this comprehensive process:

#### Phase 1: Preparation (Week 1)

1. **Download New SDK**
   ```bash
   # Create backup of current SDKs
   cp -r AndroidApp/src/main/libs AndroidApp/src/main/libs_backup_$(date +%Y%m%d)
   ```

2. **Initial Compatibility Check**
   - Review vendor changelog and breaking changes
   - Check Android API level compatibility
   - Verify license compliance

3. **Staging Environment Preparation**
   - Update staging with new SDK files
   - Run basic compilation tests

#### Phase 2: Testing (Week 2)

1. **Comprehensive Testing**
   ```bash
   # Run full test suite
   python run_evaluation_suite.py --category android_foundation
   python run_evaluation_suite.py --category integration_tests
   
   # Run Android specific tests
   cd AndroidApp
   ./gradlew test connectedAndroidTest
   ```

2. **Performance Validation**
   - Bluetooth connection stability (Shimmer)
   - Thermal camera frame rate and quality
   - Memory usage and battery impact
   - Multi-device synchronization accuracy

3. **User Acceptance Testing**
   - Test with actual research workflow
   - Verify data quality and integrity
   - Confirm UI/UX consistency

#### Phase 3: Deployment (Week 3)

1. **Pre-Deployment Checklist**
   - [ ] All tests passing
   - [ ] Performance benchmarks met
   - [ ] Documentation updated
   - [ ] Rollback plan documented
   - [ ] Stakeholder notification sent

2. **Production Deployment**
   ```bash
   # Update production SDK files
   cp new_sdk_files/* AndroidApp/src/main/libs/
   
   # Build and deploy
   cd AndroidApp
   ./gradlew assembleRelease
   ```

3. **Post-Deployment Monitoring**
   - Monitor error rates for 48 hours
   - Check user feedback and bug reports
   - Verify data collection continuity

#### Phase 4: Documentation (Week 4)

1. **Update Documentation**
   - Update this guide with new versions
   - Document any configuration changes
   - Update API documentation if needed

2. **Knowledge Sharing**
   - Brief team on changes and new features
   - Update troubleshooting guides
   - Share lessons learned

## Troubleshooting Common Issues

### 🔧 Shimmer SDK Issues

**Problem**: Bluetooth connection failures after update
```bash
# Check Bluetooth permissions in AndroidManifest.xml
grep -n "BLUETOOTH" AndroidApp/src/main/AndroidManifest.xml

# Verify Shimmer service configuration
grep -n "ShimmerService" AndroidApp/src/main/java/com/multisensor/recording/
```

**Solution**: 
1. Update Bluetooth permission declarations
2. Check for API changes in connection methods
3. Verify background service limitations on newer Android versions

**Problem**: Data format changes
```bash
# Compare data structures
python scripts/compare_shimmer_data_formats.py old_format.json new_format.json
```

**Solution**:
1. Update data parsing logic in `ShimmerManager.kt`
2. Add format migration for existing data
3. Update calibration algorithms if needed

### 🌡️ Thermal Camera SDK Issues

**Problem**: Camera initialization failures
```bash
# Check USB permissions and thermal camera detection
adb shell dumpsys usb
```

**Solution**:
1. Verify USB device permissions in AndroidManifest.xml
2. Check thermal camera hardware compatibility
3. Update USB device filter configurations

**Problem**: Frame rate degradation
```bash
# Monitor thermal camera performance
adb logcat | grep "ThermalCamera"
```

**Solution**:
1. Check thermal camera resolution settings
2. Verify adequate USB bandwidth
3. Update frame processing algorithms

## Vendor Communication

### 📞 Support Contacts

**Shimmer Engineering**
- Technical Support: support@shimmersensing.com
- GitHub Issues: [Shimmer-Java-Android-API/issues](https://github.com/ShimmerEngineering/Shimmer-Java-Android-API/issues)
- Documentation: [Shimmer User Manual](http://www.shimmersensing.com/support/wireless-sensor-networks-documentation)

**TopDon Technology**
- Technical Support: support@topdon.com
- SDK Documentation: Available with SDK download
- Developer Portal: Contact vendor for access

### 📧 Communication Templates

#### Update Request Email Template

```
Subject: SDK Update Request - Multi-Sensor Recording System

Dear [Vendor] Support Team,

We are using your SDK in our Multi-Sensor Recording System for academic research purposes. We would like to request information about:

1. Latest stable SDK version availability
2. Security patches and bug fixes since version [CURRENT_VERSION]
3. Breaking changes and migration guidance
4. Future release timeline and roadmap

Project Details:
- Project: Multi-Sensor Recording System for Contactless GSR Prediction Research
- Current SDK Version: [CURRENT_VERSION]
- Target Android API Level: 35
- Use Case: Academic research, physiological data collection

Please let us know the best way to stay informed about SDK updates and security notifications.

Thank you for your support.

Best regards,
[Your Name]
[Your Institution]
[Contact Information]
```

#### Issue Report Template

```
Subject: SDK Issue Report - [Brief Description]

SDK Version: [VERSION]
Android API Level: 35
Device Model: [MODEL]
Issue Severity: [Low/Medium/High/Critical]

Issue Description:
[Detailed description of the problem]

Steps to Reproduce:
1. [Step 1]
2. [Step 2]
3. [Step 3]

Expected Behavior:
[What should happen]

Actual Behavior:
[What actually happens]

Logs and Error Messages:
[Include relevant logs]

Workaround:
[Any temporary workarounds found]

Impact:
[How this affects the research system]
```

## Compliance and Legal Considerations

### 📋 License Compliance

1. **Review License Terms**
   - Check redistribution rights
   - Verify academic use permissions
   - Understand commercial use restrictions

2. **Documentation Requirements**
   - Maintain license files
   - Include attribution notices
   - Document third-party components

3. **Update Tracking**
   - Log all SDK version changes
   - Maintain change history
   - Document compliance verification

### 🔒 Security Considerations

1. **Vulnerability Assessment**
   - Monitor vendor security advisories
   - Check for CVE references
   - Assess impact on research data

2. **Supply Chain Security**
   - Verify SDK authenticity
   - Check cryptographic signatures
   - Validate download sources

3. **Data Protection**
   - Review data handling changes
   - Ensure GDPR compliance
   - Validate encryption standards

## Automation and CI/CD Integration

### 🤖 GitHub Actions Integration

The vendor SDK monitoring is integrated into the CI/CD pipeline:

```yaml
# .github/workflows/dependency-health.yml includes:
- name: Run vendor SDK monitoring
  run: python scripts/monitor_vendor_sdks.py --check-updates --generate-report
```

### 📊 Reporting and Alerts

1. **Weekly Reports**: Automated issues created with SDK status
2. **Critical Alerts**: Immediate notifications for high-risk findings
3. **Security Scans**: Integration with security monitoring workflows

### 🔄 Continuous Improvement

1. **Metrics Collection**: Track update frequency and success rates
2. **Process Refinement**: Regular review of update procedures
3. **Tool Enhancement**: Improve monitoring scripts based on experience

---

## Quick Reference Commands

```bash
# Check vendor SDK status
python scripts/monitor_vendor_sdks.py

# Generate detailed report
python scripts/monitor_vendor_sdks.py --check-updates --generate-report

# Backup current SDKs before update
cp -r AndroidApp/src/main/libs AndroidApp/src/main/libs_backup_$(date +%Y%m%d)

# Test after SDK update
python run_evaluation_suite.py --category android_foundation
cd AndroidApp && ./gradlew test

# Monitor deployment
adb logcat | grep -E "(Shimmer|ThermalCamera|ERROR)"
```

---

*This guide is maintained as part of the Multi-Sensor Recording System documentation. For questions or updates, please refer to the project's issue tracker.*