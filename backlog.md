# Project Backlog

This file tracks pending items and TODOs identified in the thesis documentation and system development.

## Documentation TODOs

### High Priority
- [ ] **Maintenance Documentation** (Appendices): Provide detailed maintenance schedule document covering daily checks, weekly maintenance, monthly calibration, and annual system updates
- [ ] **Figure Implementation - Session Data**: Complete figures A2, A3, A4, A5, A10, A11 requiring implementation with collected session data
- [ ] **Figure Implementation - Sensor Data**: Complete figure A9 requiring implementation with sensor characterisation data  
- [ ] **Figure Implementation - Usage Data**: Complete figure A11 requiring implementation with usage analysis data

### Medium Priority
- [ ] **Cross-reference Validation**: Validate and fix internal links pointing to `docs/thesis_report/Chapter_7_Appendices.md` to ensure they point to correct paths
- [ ] **ADR References**: Add cross-references to Architecture Decision Records (ADR-001, ADR-002, ADR-003) in Chapter 4 design decision sections
- [ ] **Risk Management Section**: Add brief risk management section to Chapter 3 outlining key technical risks and mitigation strategies

### Low Priority
- [ ] **Extended Performance Testing**: Implement peak load scenario tests (>8 devices, additional video streams)
- [ ] **Advanced Synchronisation Metrics**: Develop additional synchronisation quality metrics and visualisations

## Code/System TODOs

### Future Enhancements
- [ ] **Cloud Integration**: Investigate cloud storage and remote monitoring capabilities
- [ ] **Mobile Controller**: Explore Android device as session coordinator option
- [ ] **Edge Computing**: Research single-board computer alternatives to replace PC controller
- [ ] **Production Deployment**: Address technical debt, improve test coverage, and containerisation for easier setup

### Security Implementation
- [ ] **BL-SEC-001**: Implement TLS encryption for PC-Android communication protocol
  - Add RSA/AES encryption layer for command and data transmission
  - Implement certificate-based authentication
  - Add encrypted file transfer mechanism

### User Interface Enhancements
- [ ] **BL-UI-003**: Implement Playback & Annotation tab for post-session analysis
  - Add PyAV integration for video file handling
  - Implement timeline scrubbing with synchronized sensor data display
  - Add annotation functionality with sidecar file storage
- [ ] **BL-UI-004**: Implement Camera Calibration utility
  - Add OpenCV integration for calibration pattern detection
  - Implement intrinsic/extrinsic parameter calculation
  - Add calibration results export for research use
- [ ] **BL-UI-005**: Implement Data Export functionality
  - Add MATLAB .mat file export capability
  - Implement HDF5 export with structured datasets
  - Add batch processing for multiple sessions
- [ ] **BL-UI-006**: Add comprehensive benchmarking dashboard
  - Implement synchronization accuracy metrics visualization
  - Add performance monitoring for multi-device coordination
  - Create network latency and jitter analysis tools

### Data Processing
- [ ] **BL-ANNO-001**: Implement user annotation system
  - Add marker placement during recording
  - Implement event timestamp logging
  - Add annotation export to session metadata

## Notes
- Items marked as TODO in thesis documentation should be addressed before final submission
- Session data collection needed for completing several appendix figures
- Consider ethics approval requirements for any future human participant studies