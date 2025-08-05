# Bucika GSR Python Package

## Overview

The Bucika GSR Python package implements the **PC master-controller** for the multi-sensor recording system, serving as the central coordination hub for distributed physiological measurement research. This package provides functionality for device synchronization, multi-modal sensor data collection, and real-time processing with research-grade temporal precision.

The architecture follows the offline-first local recording paradigm with master-controller coordination, enabling researchers to conduct synchronized data collection across heterogeneous sensor modalities including RGB cameras, thermal imaging, and physiological sensors.

## Package Structure

### Core Modules

- **calibration/** - Calibration algorithms and quality assessment for camera intrinsic/extrinsic parameter estimation and multi-modal sensor alignment
- **config/** - Configuration management and settings framework supporting research reproducibility
- **error_handling/** - Robust error management and logging systems for research-grade reliability
- **gui/** - PyQt5-based graphical user interface components following HCI best practices
- **hand_segmentation/** - Computer vision and machine learning processing for real-time hand landmark detection using MediaPipe
- **network/** - Socket communication and protocol handling for reliable device coordination
- **production/** - Production-ready deployment utilities and system integration tools
- **protocol/** - Communication protocol implementations defining structured message formats and data exchange schemas
- **session/** - Session management and data recording with comprehensive metadata tracking
- **utils/** - Shared utility functions and helpers providing common functionality across system components
- **web_ui/** - Web-based interface components for remote monitoring and control capabilities
- **webcam/** - Camera handling and video processing for USB camera control

## Core Components

### Primary Application Components

- **main.py** - Primary application entry point implementing the main application lifecycle
- **application.py** - Main application controller coordinating system components and managing application state
- **shimmer_manager.py** - GSR sensor management implementing Bluetooth communication protocols for Shimmer3 GSR+ physiological sensors
- **master_clock_synchronizer.py** - Device synchronization engine for microsecond-precision temporal coordination
- **demo_enhanced_ui.py** - Enhanced demonstration interface showcasing system capabilities

## CLI Commands

The package provides installable command-line interface tools:

- **`bucika-gsr`** - Main application executable providing complete system functionality
- **`bucika-gsr-demo`** - Demonstration interface for system evaluation and training purposes

## Architecture

### System Design Philosophy

The system implements **offline-first local recording** with **PC master-controller architecture** using **JSON socket protocol** for device communication. This architectural approach ensures:

- **Temporal Precision**: Microsecond-level synchronization across wireless networks through sophisticated clock coordination algorithms
- **Fault Tolerance**: Graceful degradation and error recovery mechanisms ensuring research session continuity
- **Scalability**: Support for multiple simultaneous devices with efficient resource utilization and bandwidth management
- **Research Reproducibility**: Comprehensive metadata tracking and configuration management supporting scientific methodology requirements [Wilson2014]

### Distributed Coordination Model

The master-controller architecture implements a hybrid star-mesh topology combining centralized coordination simplicity with distributed processing resilience. The PC controller serves as the temporal reference and session orchestrator while individual devices maintain autonomous data collection capabilities, ensuring system robustness in challenging research environments.

## References

[IEEE1588-2008] IEEE Standard for a Precision Clock Synchronization Protocol for Networked Measurement and Control Systems. (2008). IEEE Std 1588-2008.

[Wilhelm2010] Wilhelm, F. H., Pfaltz, M. C., & Grossman, P. (2010). Continuous electronic data capture of physiology, behavior and environment in ambulatory subjects. Behavior Research Methods, 38(1), 157-165.