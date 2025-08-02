# Repository Component Inventory

## Complete Catalog of Features, Components, and Modules

This document provides a comprehensive inventory of every significant feature, component, and module in the **bucika_gsr** multi-sensor synchronized recording system repository.

**Last Updated**: January 2025 (Post-Documentation Consolidation)

## Related Documentation

**This inventory is part of the archive collection. For current implementation guides, see:**
- **Complete System API**: `../new_documentation/PROTOCOL_system_api_reference.md`
- **Android Application Guide**: `../new_documentation/README_Android_Mobile_Application.md`
- **Python Desktop Controller**: `../new_documentation/README_python_desktop_controller.md`
- **Complete Navigation**: `../new_documentation/INDEX.md`

---

## **System Architecture Overview**

The repository implements a **multi-platform, multi-sensor synchronized recording system** with the following primary platforms:

- **Android Mobile Application** - Smartphone-based data collection with thermal imaging
- **Python Desktop Controller** - Master orchestration and synchronization hub  
- **Cross-Platform Protocol** - Inter-device communication and synchronization
- **Development Toolchain** - Build, test, and deployment infrastructure

---

## **1. Android Application Components** 

### **Location**: `AndroidApp/src/main/java/com/multisensor/recording/`

### **Core Activities**
- `MainActivity.kt` - Primary application entry point with full feature set
- `MainNavigationActivity.kt` - Navigation-based main activity variant
- `SimplifiedMainActivity.kt` - Streamlined interface for basic recording operations
- `MultiSensorApplication.kt` - Application-level configuration and lifecycle management

### **Functional Modules**

#### **Calibration System** (`calibration/`)
- Cross-device calibration protocols
- Sensor alignment and synchronization setup
- Calibration data persistence and validation

#### **Controllers** (`controllers/`)
- Device state management
- Recording session orchestration
- Hardware sensor coordination

#### **Hand Segmentation** (`handsegmentation/`)
- Real-time hand detection and tracking
- Computer vision processing pipeline
- Gesture recognition capabilities

#### **Device Managers** (`managers/`)
- Hardware sensor management (camera, thermal, IMU)
- Bluetooth connectivity management
- Device capability discovery and configuration

#### **Monitoring** (`monitoring/`)
- System performance tracking
- Resource utilization monitoring
- Error reporting and diagnostics

#### **Network Communication** (`network/`)
- TCP/UDP socket communication with PC
- Device discovery and pairing
- Data streaming protocols

#### **Performance Optimization** (`performance/`)
- Real-time processing optimization
- Memory management
- Battery usage optimization

#### **Data Persistence** (`persistence/`)
- Local data storage and caching
- Recording session metadata
- Configuration persistence

#### **Protocol Implementation** (`protocol/`)
- Message serialization/deserialization
- Communication protocol enforcement
- Data format validation

#### **Recording Engine** (`recording/`)
- Multi-stream recording coordination
- Timestamp synchronization
- Data quality assurance

#### **Background Services** (`service/`)
- Foreground service for continuous recording
- Background task management
- System integration services

#### **Data Streaming** (`streaming/`)
- Real-time data transmission
- Stream quality management
- Adaptive bitrate control

#### **User Interface** (`ui/`)
- Recording interface components
- Settings and configuration screens
- Real-time feedback displays

#### **Utilities** (`util/`)
- Common helper functions
- Data format converters
- Validation utilities

---

## **2. Python Desktop Application Components**

### **Location**: `PythonApp/src/`

### **Application Core**
- `application.py` - Main application class with dependency injection
- `main.py` - Application entry point and initialization
- `shimmer_manager.py` - Shimmer3 GSR+ sensor integration
- `shimmer_pc_app.py` - PC-side Shimmer sensor management

### **Calibration System** (`calibration/`)
- `calibration_manager.py` - Calibration process orchestration
- `calibration_processor.py` - Calibration algorithm implementation
- `calibration_result.py` - Calibration outcome analysis and storage
- `calibration.py` - Core calibration functionality
- `calibration_quality_assessment.py` - Calibration validation and metrics

### **Session Management** (`session/`)
- `session_manager.py` - Recording session lifecycle management
- `session_logger.py` - Comprehensive session logging system
- `session_recovery.py` - Session restoration and error recovery
- `session_synchronizer.py` - Cross-device session synchronization

### **Graphical User Interface** (`gui/`)
- `main_window.py` - Standard main application window
- `simplified_main_window.py` - Streamlined interface variant
- `enhanced_main_window.py` - Feature-rich interface with advanced controls
- `enhanced_ui_main_window.py` - Enhanced UI with modern styling
- `dual_webcam_main_window.py` - Specialized dual-camera interface
- `main_controller.py` - Main window controller logic
- `stimulus_controller.py` - Stimulus presentation control
- `enhanced_stimulus_controller.py` - Advanced stimulus management
- `calibration_dialog.py` - Calibration interface components
- `session_review_dialog.py` - Session review and analysis interface
- `device_panel.py` - Device status and control panel
- `preview_panel.py` - Real-time video preview
- `stimulus_panel.py` - Stimulus configuration panel
- `common_components.py` - Reusable UI components

### **Webcam and Video Processing** (`webcam/`)
- `webcam_capture.py` - Single webcam capture implementation
- `dual_webcam_capture.py` - Synchronized dual-webcam capture
- `advanced_sync_algorithms.py` - Precision synchronization algorithms
- `cv_preprocessing_pipeline.py` - Computer vision preprocessing

### **Network Communication** (`network/`)
- `device_server.py` - PC server for Android device communication
- `enhanced_device_server.py` - Advanced server with extended capabilities
- `device_client.py` - Client-side communication handling
- `pc_server.py` - PC-to-PC communication server
- `android_device_manager.py` - Android device discovery and management

### **Hand Segmentation** (`hand_segmentation/`)
- `segmentation_engine.py` - Core hand segmentation algorithms
- `models.py` - Machine learning models for hand detection
- `post_processor.py` - Post-processing and refinement
- `utils.py` - Segmentation utility functions

### **Configuration Management** (`config/`)
- `configuration_manager.py` - System-wide configuration management
- `webcam_config.py` - Webcam-specific configuration

### **Protocol Implementation** (`protocol/`)
- Protocol buffer integration
- Message schema validation
- Cross-platform communication standards

### **Production Systems** (`production/`)
- `deployment_automation.py` - Automated deployment pipeline
- `performance_benchmark.py` - System performance benchmarking
- `phase4_validator.py` - Production readiness validation
- `security_scanner.py` - Security vulnerability scanning

### **Error Handling** (`error_handling/`)
- Centralized error management
- Exception handling and recovery
- Error reporting and logging

### **Testing Framework** (`testing/`)
- Unit test infrastructure
- Integration testing tools
- Performance testing utilities

### **Utility Functions** (`utils/`)
- Common helper functions
- Data processing utilities
- System integration tools

### **Additional Core Modules**
- `cross_device_calibration_coordinator.py` - Multi-device calibration coordination
- `master_clock_synchronizer.py` - System-wide time synchronization
- `ntp_time_server.py` - Network time protocol server
- `performance_optimizer.py` - Runtime performance optimization
- `real_time_calibration_feedback.py` - Live calibration feedback system
- `stimulus_manager.py` - Stimulus presentation management

---

## **3. Protocol and Communication System**

### **Location**: `protocol/`

### **Communication Protocols**
- `config.json` - Protocol configuration parameters
- `message_schema.json` - Message format specifications and validation schemas

### **Features**
- JSON-based message formatting
- Cross-platform compatibility
- Real-time communication protocols
- Data integrity validation
- Synchronization message handling

---

## **4. Development and Build System**

### **Build Configuration**
- `build.gradle` - Android application build configuration
- `build.gradle.kts` - Kotlin DSL build configuration
- `settings.gradle` - Multi-module build settings
- `gradle.properties` - Gradle build properties
- `gradlew` / `gradlew.bat` - Gradle wrapper executables

### **Python Environment**
- `environment.yml` - Conda environment specification
- `pyproject.toml` - Python project configuration and dependencies
- `requirements.txt` - Python package requirements
- `test-requirements.txt` - Testing framework dependencies

### **Quality Assurance**
- `.flake8` - Python code style configuration
- `detekt.yml` - Kotlin static analysis configuration
- `qodana.yaml` - JetBrains Qodana code quality configuration
- `codecov.yml` - Code coverage reporting configuration
- `pytest.ini` - Python testing framework configuration
- `.pre-commit-config.yaml` - Pre-commit hooks configuration

---

## **5. Tools and Scripts**

### **Location**: `tools/`

### **Development Tools** (`development/`)
- Development environment setup scripts
- Build validation utilities
- Dependency management tools

### **Validation Tools** (`validation/`)
- Data schema validation utilities
- System integrity checks
- Configuration validation

### **Scripts** (`scripts/`)
- `validate-build.ps1` - PowerShell build validation script

### **Root-Level Utilities**
- `validate_data_schemas.py` - Data format validation
- `test_summary.py` - Test result aggregation and reporting

---

## **6. Testing Infrastructure**

### **Python Application Tests** (`PythonApp/`)
- `test_integration_logging.py` - Integration logging validation
- `test_hardware_sensor_simulation.py` - Hardware sensor simulation testing
- `test_calibration_implementation.py` - Calibration system testing
- `test_dual_webcam_integration.py` - Dual webcam system testing
- `test_comprehensive_recording_session.py` - End-to-end session testing
- `test_data_integrity_validation.py` - Data integrity verification
- `test_enhanced_stress_testing.py` - System stress testing
- `test_network_resilience.py` - Network failure recovery testing
- `test_shimmer_implementation.py` - Shimmer sensor integration testing
- `run_complete_test_suite.py` - Comprehensive test execution
- `run_comprehensive_tests.py` - Full system validation testing

### **Android Application Tests** (`AndroidApp/`)
- `run_comprehensive_android_tests.sh` - Android test suite execution
- `validate_shimmer_integration.sh` - Shimmer integration validation

---

## **7. Documentation System**

### **Location**: `docs/`

### **Consolidated Documentation**
- `DOCUMENTATION_INDEX.md` - Complete navigation roadmap
- `user-guides/CONSOLIDATED_USER_GUIDE.md` - Comprehensive user manual
- `implementation/CONSOLIDATED_IMPLEMENTATION_GUIDE.md` - Technical reference
- `academic/CONSOLIDATED_RESEARCH_SUMMARY.md` - Academic contributions
- `TODO_DOCUMENTATION.md` - Structured improvement plan

### **Technical Specifications** (`technical/`)
- Detailed system specifications
- Architecture documentation
- API reference materials

### **Legacy Documentation** (`archive/`)
- Historical documentation preservation
- Migration tracking
- Reference materials

---

## **8. Data and Configuration**

### **Calibration Data** (`calibration_data/`)
- Sensor calibration parameters
- Historical calibration records
- Validation datasets

### **Example Data** (`examples/`)
- `data_management_example.py` - Data handling examples
- Sample datasets and configurations

### **Recordings Storage**
- `PythonApp/recordings/` - PC-side recording storage
- `PythonApp/test_recordings/` - Test data repository
- `AndroidApp/recordings/` - Mobile recording storage

---

## **9. Key Features and Capabilities**

### **Multi-Sensor Integration**
- **2 Android smartphones** (Samsung S22) with thermal cameras
- **2 Logitech Brio 4K USB webcams** 
- **Shimmer3 GSR+ physiological sensors**
- **Synchronized data collection** across all sensors

### **Synchronization Technology**
- Microsecond-precision timing
- NTP-based time synchronization
- Master clock coordination
- Cross-device timestamp alignment

### **Data Processing**
- Real-time hand segmentation
- Computer vision preprocessing
- Multi-modal data fusion
- Quality assessment and validation

### **User Interface Variants**
- Standard feature-complete interface
- Simplified streamlined interface
- Enhanced modern styling interface
- Dual-webcam specialized interface

### **Research Capabilities**
- Stimulus presentation system
- Multi-modal data collection
- Session management and review
- Data export and analysis tools

### **Production Features**
- Automated deployment pipeline
- Security scanning and validation
- Performance benchmarking
- System monitoring and diagnostics

---

## **10. File Statistics**

**Post-Consolidation Statistics (January 2025):**

### Code Implementation
- **Total Python Files**: 141 files
- **Total Kotlin/Java Files**: 186 files
- **Major Modules**: 10+ distinct functional areas
- **Test Files**: 25+ comprehensive test implementations

### Documentation Structure
- **New Documentation**: 43 comprehensive files in `docs/new_documentation/`
  - 15 README_*.md (Technical deep-dives)
  - 11 USER_GUIDE_*.md (Practical user guides)  
  - 14 PROTOCOL_*.md (Data contracts and specifications)
  - 3 Supporting files (INDEX.md, schemas, quick references)
- **Archive Documentation**: 6 preserved authoritative files in `docs/archive/`
- **Legacy Documentation**: Organized in `docs/technical/`, `docs/user-guides/`, `docs/api/`
- **Total Reduction**: 84% file reduction (37→6) in archive while enhancing content quality

### Documentation Impact
- **Content Volume**: 300KB+ of new consolidated documentation
- **Coverage**: Research-grade documentation suitable for academic review
- **Organization**: Component-first approach with role-based navigation
- **Maintenance**: Single source of truth for each topic area

---

## **Technical Architecture Summary**

This repository implements a sophisticated **multi-sensor synchronized recording system** designed for research applications. The architecture supports:

1. **Cross-Platform Synchronization** - Android and PC coordination
2. **Multiple Data Modalities** - Video, thermal, physiological, and gesture data
3. **Real-Time Processing** - Live data processing and feedback
4. **Research Workflow Support** - Complete experimental session management
5. **Production Deployment** - Automated build and deployment pipeline
6. **Comprehensive Testing** - Unit, integration, and stress testing
7. **Quality Assurance** - Code quality, security, and performance validation

The system serves as a complete research platform enabling synchronized multi-modal data collection with precision timing and comprehensive session management capabilities.

## References to Current Implementation

### Updated Documentation Structure
For current implementation details and comprehensive guides, refer to:

- **System Architecture**: `../new_documentation/README_system_architecture.md`
- **Implementation Guides**: `../new_documentation/README_technical_implementation.md`
- **Component APIs**: `../new_documentation/PROTOCOL_system_api_reference.md`
- **User Documentation**: `../new_documentation/USER_GUIDE_system_operation.md`

### Component-Specific Documentation
- **Android Application**: `../new_documentation/README_Android_Mobile_Application.md`
- **Python Desktop Controller**: `../new_documentation/README_python_desktop_controller.md`
- **Networking Protocol**: `../new_documentation/README_networking_protocol.md`
- **Session Management**: `../new_documentation/README_session_management.md`

**Complete Navigation**: See `../new_documentation/INDEX.md` for role-based quick-start recommendations and comprehensive document relationships.