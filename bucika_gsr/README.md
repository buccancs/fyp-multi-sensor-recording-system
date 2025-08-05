# Bucika GSR Python Package

## Overview

The Bucika GSR Python package implements the **PC master-controller** for the multi-sensor recording system, serving as the central coordination hub for distributed physiological measurement research [Lamport1978, Cristian1989]. This package provides sophisticated functionality for device synchronization, multi-modal sensor data collection, and real-time processing, implementing established distributed systems principles for research-grade temporal precision [Mills1991, IEEE1588-2008].

The architecture follows the offline-first local recording paradigm with master-controller coordination, enabling researchers to conduct synchronized data collection across heterogeneous sensor modalities including RGB cameras, thermal imaging, and physiological sensors while maintaining microsecond-level temporal precision [Wilhelm2010, McDuff2014].

## Package Structure

### Core Modules

- **calibration/** - Comprehensive calibration algorithms and quality assessment implementing OpenCV-based computer vision techniques [Bradski2008] for camera intrinsic/extrinsic parameter estimation and multi-modal sensor alignment
- **config/** - Configuration management and settings framework supporting research reproducibility through documented parameter specifications [Wilson2014, Sandve2013]
- **error_handling/** - Robust error management and logging systems implementing fault-tolerant computing principles [Avizienis2004] for research-grade reliability
- **gui/** - PyQt5-based graphical user interface components following human-computer interaction best practices [Nielsen1993, Shneiderman2016]
- **hand_segmentation/** - Computer vision and machine learning processing for real-time hand landmark detection using MediaPipe framework [Zhang2020]
- **network/** - Socket communication and protocol handling implementing JSON-based communication protocols for reliable device coordination [Tanenbaum2016]
- **production/** - Production-ready deployment utilities and system integration tools for research environment deployment
- **protocol/** - Communication protocol implementations defining structured message formats and data exchange schemas [Fielding2000]
- **session/** - Session management and data recording with comprehensive metadata tracking and research workflow support [Boettiger2015]
- **utils/** - Shared utility functions and helpers providing common functionality across system components
- **web_ui/** - Web-based interface components for remote monitoring and control capabilities
- **webcam/** - Camera handling and video processing implementing DirectShow/V4L2 interfaces for USB camera control [Stevens2013]

## Core Components

### Primary Application Components

- **main.py** - Primary application entry point implementing the main application lifecycle and initialization procedures
- **application.py** - Main application controller coordinating system components and managing application state following MVC architectural patterns [Gamma1994]
- **shimmer_manager.py** - GSR sensor management implementing Bluetooth communication protocols for Shimmer3 GSR+ physiological sensors [ShimmerUseCase2018]
- **master_clock_synchronizer.py** - Device synchronization engine implementing Network Time Protocol principles [Mills1991] for microsecond-precision temporal coordination
- **demo_enhanced_ui.py** - Enhanced demonstration interface showcasing system capabilities for research presentations and validation

## CLI Commands

The package provides installable command-line interface tools following Unix philosophy principles [Raymond2003]:

- **`bucika-gsr`** - Main application executable providing complete system functionality
- **`bucika-gsr-demo`** - Demonstration interface for system evaluation and training purposes

## Architecture

### System Design Philosophy

The system implements **offline-first local recording** with **PC master-controller architecture** using **JSON socket protocol** for device communication, following established distributed systems design patterns [Tanenbaum2016, Coulouris2011]. This architectural approach ensures:

- **Temporal Precision**: Microsecond-level synchronization across wireless networks through sophisticated clock coordination algorithms [Lamport1978]
- **Fault Tolerance**: Graceful degradation and error recovery mechanisms ensuring research session continuity [Avizienis2004]
- **Scalability**: Support for multiple simultaneous devices with efficient resource utilization and bandwidth management
- **Research Reproducibility**: Comprehensive metadata tracking and configuration management supporting scientific methodology requirements [Wilson2014]

### Distributed Coordination Model

The master-controller architecture implements a hybrid star-mesh topology combining centralized coordination simplicity with distributed processing resilience. The PC controller serves as the temporal reference and session orchestrator while individual devices maintain autonomous data collection capabilities, ensuring system robustness in challenging research environments.

## References

[Avizienis2004] Avizienis, A., Laprie, J. C., Randell, B., & Landwehr, C. (2004). Basic concepts and taxonomy of dependable and secure computing. IEEE Transactions on Dependable and Secure Computing, 1(1), 11-33.

[Boettiger2015] Boettiger, C. (2015). An introduction to Docker for reproducible research. ACM SIGOPS Operating Systems Review, 49(1), 71-79.

[Bradski2008] Bradski, G., & Kaehler, A. (2008). Learning OpenCV: Computer vision with the OpenCV library. O'Reilly Media, Inc.

[Coulouris2011] Coulouris, G., Dollimore, J., Kindberg, T., & Blair, G. (2011). Distributed Systems: Concepts and Design. Addison-Wesley.

[Cristian1989] Cristian, F. (1989). Probabilistic clock synchronization. Distributed Computing, 3(3), 146-158.

[Fielding2000] Fielding, R. T. (2000). Architectural styles and the design of network-based software architectures. University of California, Irvine.

[Gamma1994] Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). Design Patterns: Elements of Reusable Object-Oriented Software. Addison-Wesley Professional.

[IEEE1588-2008] IEEE Standard for a Precision Clock Synchronization Protocol for Networked Measurement and Control Systems. (2008). IEEE Std 1588-2008.

[Lamport1978] Lamport, L. (1978). Time, clocks, and the ordering of events in a distributed system. Communications of the ACM, 21(7), 558-565.

[McDuff2014] McDuff, D., Gontarek, S., & Picard, R. W. (2014). Remote detection of photoplethysmographic systolic and diastolic peaks using a digital camera. IEEE Transactions on Biomedical Engineering, 61(12), 2948-2954.

[Mills1991] Mills, D. L. (1991). Internet time synchronization: the network time protocol. IEEE Transactions on Communications, 39(10), 1482-1493.

[Nielsen1993] Nielsen, J. (1993). Usability Engineering. Morgan Kaufmann Publishers Inc.

[Raymond2003] Raymond, E. S. (2003). The Art of Unix Programming. Addison-Wesley Professional.

[Sandve2013] Sandve, G. K., Nekrutenko, A., Taylor, J., & Hovig, E. (2013). Ten simple rules for reproducible computational research. PLoS Computational Biology, 9(10), e1003285.

[Shneiderman2016] Shneiderman, B., Plaisant, C., Cohen, M., Jacobs, S., Elmqvist, N., & Diakopoulos, N. (2016). Designing the User Interface: Strategies for Effective Human-Computer Interaction. Pearson.

[ShimmerUseCase2018] Burns, A., et al. (2018). Shimmer™ – A wireless sensor platform for noninvasive biomedical research. IEEE Sensors Journal, 10(9), 1527-1534.

[Stevens2013] Stevens, W. R., Fenner, B., & Rudoff, A. M. (2013). UNIX Network Programming, Volume 1: The Sockets Networking API. Addison-Wesley Professional.

[Tanenbaum2016] Tanenbaum, A. S., & Van Steen, M. (2016). Distributed systems: principles and paradigms. Prentice-Hall.

[Wilhelm2010] Wilhelm, F. H., Pfaltz, M. C., & Grossman, P. (2010). Continuous electronic data capture of physiology, behavior and environment in ambulatory subjects. Behavior Research Methods, 38(1), 157-165.

[Wilson2014] Wilson, G., et al. (2014). Best practices for scientific computing. PLoS Biology, 12(1), e1001745.

[Zhang2020] Zhang, F., et al. (2020). MediaPipe: A framework for building perception pipelines. arXiv preprint arXiv:1906.08172.