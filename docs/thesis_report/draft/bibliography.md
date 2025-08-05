# Bibliography

## Academic References

**Apple Inc. (2019)**. *Apple Watch Series 5: Advanced Health Monitoring*. Apple Developer Documentation. Retrieved from https://developer.apple.com/health-fitness/

**Biopac Systems Inc. (2018)**. *GSR100C Galvanic Skin Response Amplifier*. Technical Specifications Manual. BIOPAC Systems, Inc.

**Boucsein, W. (2012)**. *Electrodermal Activity (2nd ed.)*. Springer Science & Business Media. DOI: 10.1007/978-1-4614-1126-0

**Brooks, F. P. (1995)**. *The Mythical Man-Month: Essays on Software Engineering*. Addison-Wesley Professional.

**Cho, Y., Bianchi-Berthouze, N., & Julier, S. J. (2017)**. DeepBreath: Deep learning of breathing patterns for automatic stress recognition using low-cost thermal imaging in natural settings. *Proceedings of the 2017 ACM International Conference on Multimodal Interaction*, 456-463.

**Coulouris, G., Dollimore, J., Kindberg, T., & Blair, G. (2011)**. *Distributed Systems: Concepts and Design (5th ed.)*. Addison-Wesley.

**Dean, J., & Ghemawat, S. (2008)**. MapReduce: Simplified data processing on large clusters. *Communications of the ACM*, 51(1), 107-113.

**Fowler, M. (2018)**. *Refactoring: Improving the Design of Existing Code (2nd ed.)*. Addison-Wesley Professional.

**Fowles, D. C., Christie, M. J., Edelberg, R., Grings, W. W., Lykken, D. T., & Venables, P. H. (1981)**. Publication recommendations for electrodermal measurements. *Psychophysiology*, 18(3), 232-239.

**Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994)**. *Design Patterns: Elements of Reusable Object-Oriented Software*. Addison-Wesley Professional.

**Goodfellow, I., Bengio, Y., & Courville, A. (2016)**. *Deep Learning*. MIT Press.

**Healey, J. A., & Picard, R. W. (2005)**. Detecting stress during real-world driving tasks using physiological sensors. *IEEE Transactions on Intelligent Transportation Systems*, 6(2), 156-166.

**Lamport, L. (1978)**. Time, clocks, and the ordering of events in a distributed system. *Communications of the ACM*, 21(7), 558-565.

**Lazarus, R. S., & Folkman, S. (1984)**. *Stress, Appraisal, and Coping*. Springer Publishing Company.

**LeCun, Y., Bengio, Y., & Hinton, G. (2015)**. Deep learning. *Nature*, 521(7553), 436-444.

**Liu, J. W. S. (2000)**. *Real-Time Systems*. Prentice Hall.

**Martin, R. C. (2008)**. *Clean Code: A Handbook of Agile Software Craftsmanship*. Prentice Hall.

**McConnell, S. (2004)**. *Code Complete: A Practical Handbook of Software Construction (2nd ed.)*. Microsoft Press.

**McDuff, D., Gontarek, S., & Picard, R. W. (2016)**. Improvements in remote cardiopulmonary measurement using a five band digital camera. *IEEE Transactions on Biomedical Engineering*, 61(10), 2593-2601.

**Picard, R. W. (1997)**. *Affective Computing*. MIT Press.

**Poh, M. Z., McDuff, D. J., & Picard, R. W. (2010)**. Non-contact, automated cardiac pulse measurements using video imaging and blind source separation. *Optics Express*, 18(10), 10762-10774.

**Samsung Electronics (2020)**. *Samsung Health: Advanced Biometric Monitoring*. Samsung Developer Documentation.

**Selye, H. (1936)**. A syndrome produced by diverse nocuous agents. *Nature*, 138(3479), 32.

**Tanenbaum, A. S., & Van Steen, M. (2016)**. *Distributed Systems: Principles and Paradigms (3rd ed.)*. Pearson.

**Wilson, G., Aruliah, D. A., Brown, C. T., Chue Hong, N. P., Davis, M., Guy, R. T., ... & Wilson, P. (2014)**. Best practices for scientific computing. *PLoS Biology*, 12(1), e1001745.

## Technical Standards and Specifications

**IEEE 802.11 (2020)**. *IEEE Standard for Information Technology - Telecommunications and Information Exchange Between Systems - Local and Metropolitan Area Networks - Specific Requirements Part 11: Wireless LAN Medium Access Control (MAC) and Physical Layer (PHY) Specifications*.

**ISO/IEC 27001 (2013)**. *Information Technology - Security Techniques - Information Security Management Systems - Requirements*.

**JSON Schema Specification (2020)**. *JSON Schema: A Media Type for Describing JSON Documents*. Internet Engineering Task Force (IETF).

## Software and Hardware Documentation

**Android Developers (2023)**. *Android Camera2 API Documentation*. Google LLC. Retrieved from https://developer.android.com/reference/android/hardware/camera2

**Kotlin Foundation (2023)**. *Kotlin Programming Language Documentation*. JetBrains. Retrieved from https://kotlinlang.org/docs/

**Python Software Foundation (2023)**. *Python 3.11 Documentation*. Retrieved from https://docs.python.org/3/

**PyQt5 Documentation (2023)**. *PyQt5 Reference Guide*. Riverbank Computing Limited.

**Shimmer Research (2023)**. *Shimmer3 GSR+ Unit Technical Specifications*. Shimmer Research Ltd.

**TopDon (2023)**. *TC001 Thermal Camera Technical Manual*. TopDon Technology Co., Ltd.

## Code Implementation References

This thesis references specific implementation files within the Multi-Sensor Recording System codebase:

### Android Application Components
- `AndroidApp/src/main/java/com/multisensor/recording/MainActivity.kt` - Main application activity
- `AndroidApp/src/main/java/com/multisensor/recording/services/CameraService.kt` - Camera recording service
- `AndroidApp/src/main/java/com/multisensor/recording/services/GSRService.kt` - GSR sensor integration
- `AndroidApp/src/main/java/com/multisensor/recording/network/SocketClient.kt` - Network communication
- `AndroidApp/src/main/java/com/multisensor/recording/ui/SessionFragment.kt` - User interface components

### Python Desktop Controller Components
- `PythonApp/src/main.py` - Main application entry point
- `PythonApp/src/application.py` - Application dependency injection container
- `PythonApp/src/network/device_server.py` - JSON socket server implementation
- `PythonApp/src/session/session_manager.py` - Session coordination and management
- `PythonApp/src/webcam/webcam_capture.py` - Desktop webcam integration
- `PythonApp/src/ui/main_window.py` - Main user interface window

### Protocol and Configuration Files
- `protocol/communication_protocol.json` - Communication protocol specification
- `config/system_config.yaml` - System configuration parameters
- `calibration_data/` - Sensor calibration data directory

### Testing and Validation
- `AndroidApp/src/test/` - Android application test suite
- `PythonApp/tests/` - Python application test suite
- `scripts/integration_tests.py` - System integration tests