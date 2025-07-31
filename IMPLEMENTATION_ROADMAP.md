# Implementation Roadmap: Multi-Sensor Recording System

Based on the comprehensive architecture assessment, here is a prioritized implementation roadmap to complete the system.

## Critical Path: Build System & Architecture Fixes

### Phase 1: Foundation Stabilization (Week 1)

#### 1.1 Build System Resolution 🚨 CRITICAL
**Status**: PARTIALLY FIXED
- ✅ Python dependencies installed (PyQt5, OpenCV, NumPy)  
- ⚠️ Android build still failing with Gradle plugin resolution
- ❌ Test execution blocked

**Immediate Actions**:
```bash
# Fix Android build by updating repositories in build.gradle
# Use conservative plugin versions for compatibility
# Test basic compilation: ./gradlew AndroidApp:assembleDebug
```

#### 1.2 MainActivity Refactoring 🚨 CRITICAL  
**Current**: 1,531 lines god class
**Target**: <300 lines with feature controllers

**Refactoring Plan**:
1. **Extract PermissionController** (~200 lines)
   - Move all permission handling logic
   - Centralize runtime permission requests
   
2. **Extract UsbController** (~250 lines)  
   - Move USB device management
   - Thermal camera connection logic
   
3. **Extract ShimmerController** (~300 lines)
   - Move Shimmer device integration
   - Bluetooth connection management
   
4. **Extract RecordingController** (~200 lines)
   - Move recording lifecycle management
   - Coordinate multiple data streams
   
5. **Extract CalibrationController** (~150 lines)
   - Move calibration workflow logic
   - Camera calibration management
   
6. **Extract NetworkController** (~100 lines)
   - Move PC communication protocol
   - Network state management

**Implementation Strategy**:
- Keep existing ShimmerManager, UsbDeviceManager (well-designed)
- Extract logic from MainActivity into controllers
- Use dependency injection for controller coordination
- Maintain backward compatibility during refactoring

### Phase 2: Core Integration (Weeks 2-4)

#### 2.1 PC-Android Communication Protocol
**Priority**: HIGH - System cannot function without this

**Current State**: Framework present, protocol incomplete
- `network/device_server.py` - JSON socket server ✅
- Android network framework - basic structure ✅
- Command protocol - partially defined ⚠️

**Implementation Tasks**:
1. **Complete Command Set**:
   ```json
   {
     "START_RECORDING": {"session_id": "...", "timestamp": "..."},
     "STOP_RECORDING": {"session_id": "..."},
     "CALIBRATION_MODE": {"enable": true/false},
     "CAPTURE_FRAME": {"camera": "rgb|thermal|both"},
     "STATUS_REQUEST": {},
     "CONFIGURATION": {"resolution": "4K", "framerate": 30}
   }
   ```

2. **Android Command Processing**:
   - Implement command parser in NetworkController
   - Add response acknowledgment system
   - Handle connection management and reconnection

3. **Testing Protocol**:
   - Create mock PC server for Android testing
   - Validate command round-trip timing
   - Test error handling and recovery

#### 2.2 End-to-End Recording Workflow
**Priority**: HIGH - Core functionality

**Integration Points**:
1. **Synchronized Start**:
   - PC sends START command to both phones
   - Phones acknowledge and begin recording
   - PC starts webcam capture simultaneously
   - All devices log precise start timestamps

2. **Data Collection**:
   - Phones record locally (4K video, thermal, Shimmer)
   - PC records webcam streams
   - Live preview streams to PC (optional)
   - Session metadata logging

3. **Synchronized Stop**:
   - PC sends STOP command
   - Devices finish recording and save files
   - Generate session summary
   - Initiate file transfer (if configured)

#### 2.3 Shimmer Data Integration
**Priority**: MEDIUM - Important for research applications

**Current State**: Android integration excellent, PC integration missing

**Tasks**:
1. **PC-Side Shimmer Support** (Alternative approach):
   - Use Python Shimmer SDK (`external/pyshimmer/`)
   - Implement direct Bluetooth connection to Shimmer from PC
   - Create ShimmerManager equivalent in Python

2. **Data Streaming**:
   - Stream live Shimmer data from phone to PC
   - Implement buffering for network reliability
   - Add real-time visualization in PC GUI

### Phase 3: Advanced Features (Weeks 5-8)

#### 3.1 Precision Synchronization
**Priority**: MEDIUM - Research accuracy improvement

**Implementation**:
1. **NTP Time Synchronization**:
   - Add NTP client to both Android and PC
   - Synchronize clocks before each session
   - Account for network latency in timing

2. **Hardware Timing** (Optional):
   - GPIO triggers for ultra-precise sync
   - Audio synchronization beeps
   - LED flash markers in video

#### 3.2 Camera Calibration System
**Priority**: MEDIUM - Data quality improvement

**Current State**: OpenCV framework present, needs completion

**Tasks**:
1. **Thermal Calibration Targets**:
   - Create thermal-visible calibration patterns
   - Implement thermal-specific corner detection
   - Add thermal camera intrinsics calibration

2. **Stereo Calibration**:
   - RGB-Thermal camera pair calibration
   - Generate transformation matrices
   - Validate alignment accuracy

#### 3.3 Thermal Module Consolidation
**Priority**: LOW - Code quality improvement

**Current Issue**: 6 separate thermal modules (218 total files)
- thermal-ir: 135 files
- thermal: 35 files  
- thermal-lite: 10 files
- thermal07: 10 files
- thermal-hik: 9 files
- thermal04: 9 files

**Consolidation Plan**:
1. Analyze common functionality across modules
2. Create unified ThermalModule interface
3. Migrate all implementations to single module
4. Remove duplicate code and unused modules

### Phase 4: Production Features (Weeks 9-12)

#### 4.1 Advanced GUI Features
1. **Real-Time Data Visualization**:
   - Live GSR signal plotting (PyQtGraph)
   - Device health monitoring
   - Session progress tracking

2. **Enhanced Error Handling**:
   - User-friendly error recovery
   - Automatic reconnection flows
   - Diagnostic information display

#### 4.2 File Management System
1. **Automated File Transfer**:
   - Post-session data collection from phones
   - Progress indication during transfer
   - Checksums for data integrity

2. **Session Organization**:
   - Automatic folder structure creation
   - Metadata file generation
   - Data export utilities

#### 4.3 Quality Assurance
1. **Comprehensive Testing**:
   - End-to-end hardware validation
   - Multi-device synchronization testing
   - Real research scenario validation

2. **Performance Optimization**:
   - Memory usage optimization
   - Battery life improvement
   - Network efficiency tuning

## Implementation Success Metrics

### Week 1 Success Criteria
- ✅ Android application compiles successfully
- ✅ Python GUI launches without errors
- ✅ MainActivity refactored to <300 lines
- ✅ All tests execute successfully

### Week 4 Success Criteria  
- ✅ PC can send commands to Android phones
- ✅ Synchronized recording start/stop works
- ✅ Basic file transfer operational
- ✅ End-to-end recording session completed

### Week 8 Success Criteria
- ✅ Precision timing within 50ms accuracy
- ✅ Camera calibration producing valid results
- ✅ Thermal modules consolidated
- ✅ Real-time data streaming operational

### Week 12 Success Criteria
- ✅ Complete system validated with real hardware
- ✅ Multiple simultaneous recording sessions tested
- ✅ Research-ready deployment documentation
- ✅ User training materials completed

## Risk Mitigation

### High-Risk Items
1. **Hardware Integration Complexity**
   - Mitigation: Extensive testing with actual hardware
   - Fallback: Staged rollout with simplified configurations

2. **Timing Precision Requirements**
   - Mitigation: Multiple synchronization approaches
   - Fallback: Software-based sync with timing validation

3. **Cross-Platform Compatibility**
   - Mitigation: Continuous testing on target platforms
   - Fallback: Platform-specific optimizations

## Resource Requirements

### Development Environment
- Windows PC with Android Studio
- 2 Samsung S22 phones for testing
- Topdon thermal cameras (TC001/Plus)
- Shimmer3 GSR+ sensors
- Logitech Brio 4K webcams

### Technical Expertise
- Android development (Kotlin/Camera2)
- Python desktop development (PyQt5/OpenCV)
- Computer vision and calibration
- Network protocol implementation
- Hardware integration testing

This roadmap provides a structured path to complete the Multi-Sensor Recording System based on the comprehensive architecture assessment and current implementation status.