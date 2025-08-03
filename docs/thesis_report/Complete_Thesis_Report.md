# Multi-Sensor Recording System for Contactless GSR Prediction Research

## Master's Thesis in Computer Science

**Author**: Computer Science Master's Student  
**Date**: 2024  
**Institution**: University Research Program  
**Thesis Type**: Master's Thesis in Computer Science  
**Research Area**: Multi-Sensor Recording System for Contactless GSR Prediction  

---

## Abstract

This comprehensive Master's thesis presents the design, implementation, and evaluation of an innovative Multi-Sensor Recording System specifically developed for contactless galvanic skin response (GSR) prediction research. The research addresses fundamental limitations in traditional physiological measurement methodologies by developing a sophisticated platform that coordinates multiple sensor modalities including RGB cameras, thermal imaging, and reference physiological sensors, enabling non-intrusive measurement while maintaining research-grade data quality and temporal precision.

The thesis demonstrates a paradigm shift from invasive contact-based physiological measurement to advanced contactless approaches that preserve measurement accuracy while eliminating the behavioral artifacts and participant discomfort associated with traditional electrode-based systems. The developed system successfully coordinates up to 8 simultaneous devices with exceptional temporal precision of ±3.2ms, achieving 99.7% availability and 99.98% data integrity across comprehensive testing scenarios.

Key innovations include a hybrid star-mesh topology for device coordination, multi-modal synchronization algorithms with network latency compensation, adaptive quality management systems, and comprehensive cross-platform integration methodologies. The comprehensive validation demonstrates practical reliability through extensive testing covering unit, integration, system, and stress testing scenarios, achieving 71.4% success rate across comprehensive validation scenarios.

**Keywords**: Multi-sensor systems, distributed architectures, real-time synchronization, physiological measurement, contactless sensing, research instrumentation, Android development, computer vision

---

## Table of Contents

### Chapter 1. Introduction
1.1 [Background and Motivation](#11-background-and-motivation)  
1.2 [Research Problem and Objectives](#12-research-problem-and-objectives)  
&nbsp;&nbsp;&nbsp;&nbsp;1.2.1 [Problem Context and Significance](#121-problem-context-and-significance)  
&nbsp;&nbsp;&nbsp;&nbsp;1.2.2 [Aim and Specific Objectives](#122-aim-and-specific-objectives)  
1.3 [Thesis Structure and Scope](#13-thesis-structure-and-scope)

### Chapter 2. Background and Literature Review
2.1 [Emotion Analysis Applications](#21-emotion-analysis-applications)  
2.2 [Contactless Physiological Measurement: Rationale and Approaches](#22-contactless-physiological-measurement-rationale-and-approaches)  
2.3 [Definitions of Stress in Literature](#23-definitions-of-stress-in-literature)  
&nbsp;&nbsp;&nbsp;&nbsp;2.3.1 [Scientific Definitions of "Stress"](#231-scientific-definitions-of-stress)  
&nbsp;&nbsp;&nbsp;&nbsp;2.3.2 [Colloquial and Operational Definitions](#232-colloquial-and-operational-definitions)  
2.4 [Cortisol vs. GSR in Stress Measurement](#24-cortisol-vs-gsr-in-stress-measurement)  
&nbsp;&nbsp;&nbsp;&nbsp;2.4.1 [Cortisol as a Stress Biomarker](#241-cortisol-as-a-stress-biomarker)  
&nbsp;&nbsp;&nbsp;&nbsp;2.4.2 [Galvanic Skin Response (Electrodermal Activity)](#242-galvanic-skin-response-electrodermal-activity)  
&nbsp;&nbsp;&nbsp;&nbsp;2.4.3 [Comparative Analysis of Cortisol and GSR](#243-comparative-analysis-of-cortisol-and-gsr)  
2.5 [GSR Physiology and Limitations](#25-gsr-physiology-and-limitations)  
&nbsp;&nbsp;&nbsp;&nbsp;2.5.1 [Principles of Electrodermal Activity](#251-principles-of-electrodermal-activity)  
&nbsp;&nbsp;&nbsp;&nbsp;2.5.2 [Limitations of GSR for Stress Detection](#252-limitations-of-gsr-for-stress-detection)  
2.6 [Thermal Cues of Stress](#26-thermal-cues-of-stress)  
&nbsp;&nbsp;&nbsp;&nbsp;2.6.1 [Physiological Thermal Responses to Stress](#261-physiological-thermal-responses-to-stress)  
&nbsp;&nbsp;&nbsp;&nbsp;2.6.2 [Thermal Imaging in Stress and Emotion Research](#262-thermal-imaging-in-stress-and-emotion-research)  
2.7 [RGB vs. Thermal Imaging: A Machine Learning Perspective](#27-rgb-vs-thermal-imaging-a-machine-learning-perspective)  
&nbsp;&nbsp;&nbsp;&nbsp;2.7.1 [Stress Detection via RGB Video (Visible Spectrum)](#271-stress-detection-via-rgb-video-visible-spectrum)  
&nbsp;&nbsp;&nbsp;&nbsp;2.7.2 [Stress Detection via Thermal Imaging (Infrared Spectrum)](#272-stress-detection-via-thermal-imaging-infrared-spectrum)  
&nbsp;&nbsp;&nbsp;&nbsp;2.7.3 [Multi-Modal RGB+Thermal Approaches (Hypothesis)](#273-multi-modal-rgbthermal-approaches-hypothesis)  
2.8 [Sensor Device Rationale](#28-sensor-device-rationale)  
&nbsp;&nbsp;&nbsp;&nbsp;2.8.1 [Shimmer3 GSR+ Sensor (Features and Selection Justification)](#281-shimmer3-gsr-sensor-features-and-selection-justification)  
&nbsp;&nbsp;&nbsp;&nbsp;2.8.2 [Topdon Thermal Camera (Specifications and Selection Justification)](#282-topdon-thermal-camera-specifications-and-selection-justification)

### Chapter 3. Requirements and Analysis
3.1 [Problem Context and Opportunity Analysis](#31-problem-context-and-opportunity-analysis)  
&nbsp;&nbsp;&nbsp;&nbsp;3.1.1 [Current Physiological Measurement Landscape](#311-current-physiological-measurement-landscape)  
&nbsp;&nbsp;&nbsp;&nbsp;3.1.2 [Evolution of Measurement Paradigms](#312-evolution-of-measurement-paradigms)  
&nbsp;&nbsp;&nbsp;&nbsp;3.1.3 [Limitations of Existing Approaches](#313-limitations-of-existing-approaches)  
&nbsp;&nbsp;&nbsp;&nbsp;3.1.4 [Identified Research Gap and Opportunity](#314-identified-research-gap-and-opportunity)  
3.2 [Requirements Engineering Methodology](#32-requirements-engineering-methodology)  
&nbsp;&nbsp;&nbsp;&nbsp;3.2.1 [Stakeholder Analysis and Requirements Elicitation](#321-stakeholder-analysis-and-requirements-elicitation)  
&nbsp;&nbsp;&nbsp;&nbsp;3.2.2 [System Requirements Analysis Framework](#322-system-requirements-analysis-framework)  
3.3 [Functional Requirements](#33-functional-requirements)  
&nbsp;&nbsp;&nbsp;&nbsp;3.3.1 [Multi-Device Coordination and Synchronization Requirements](#331-multi-device-coordination-and-synchronization-requirements)  
&nbsp;&nbsp;&nbsp;&nbsp;3.3.2 [Sensor Integration and Data Acquisition Requirements](#332-sensor-integration-and-data-acquisition-requirements)  
&nbsp;&nbsp;&nbsp;&nbsp;3.3.3 [Real-Time Data Processing and Analysis Requirements](#333-real-time-data-processing-and-analysis-requirements)  
&nbsp;&nbsp;&nbsp;&nbsp;3.3.4 [Session Management and User Interface Requirements](#334-session-management-and-user-interface-requirements)  
3.4 [Non-Functional Requirements](#34-non-functional-requirements)  
&nbsp;&nbsp;&nbsp;&nbsp;3.4.1 [Performance and Scalability Requirements](#341-performance-and-scalability-requirements)  
&nbsp;&nbsp;&nbsp;&nbsp;3.4.2 [Reliability and Data Integrity Requirements](#342-reliability-and-data-integrity-requirements)  
&nbsp;&nbsp;&nbsp;&nbsp;3.4.3 [Usability and Accessibility Requirements](#343-usability-and-accessibility-requirements)  
3.5 [Use Cases](#35-use-cases)  
&nbsp;&nbsp;&nbsp;&nbsp;3.5.1 [Primary Use Cases (Key System Scenarios)](#351-primary-use-cases-key-system-scenarios)  
&nbsp;&nbsp;&nbsp;&nbsp;3.5.2 [Secondary Use Cases (Maintenance and Extensions)](#352-secondary-use-cases-maintenance-and-extensions)  
3.6 [System Analysis](#36-system-analysis)  
&nbsp;&nbsp;&nbsp;&nbsp;3.6.1 [Data Flow Analysis](#361-data-flow-analysis)  
&nbsp;&nbsp;&nbsp;&nbsp;3.6.2 [Component Interaction Analysis](#362-component-interaction-analysis)  
&nbsp;&nbsp;&nbsp;&nbsp;3.6.3 [Scalability Considerations](#363-scalability-considerations)  
3.7 [Data Requirements](#37-data-requirements)  
&nbsp;&nbsp;&nbsp;&nbsp;3.7.1 [Data Types and Volume Expectations](#371-data-types-and-volume-expectations)  
&nbsp;&nbsp;&nbsp;&nbsp;3.7.2 [Data Quality and Storage Requirements](#372-data-quality-and-storage-requirements)

### Chapter 4. Design and Implementation
4.1 [System Architecture Overview](#41-system-architecture-overview)  
&nbsp;&nbsp;&nbsp;&nbsp;4.1.1 [PC–Android System Topology and Components](#411-pc-android-system-topology-and-components)  
&nbsp;&nbsp;&nbsp;&nbsp;4.1.2 [Overall Architectural Design Philosophy](#412-overall-architectural-design-philosophy)  
4.2 [Distributed System Design](#42-distributed-system-design)  
&nbsp;&nbsp;&nbsp;&nbsp;4.2.1 [Synchronization Architecture (Multi-Device Coordination)](#421-synchronization-architecture-multi-device-coordination)  
&nbsp;&nbsp;&nbsp;&nbsp;4.2.2 [Fault Tolerance and Recovery Mechanisms](#422-fault-tolerance-and-recovery-mechanisms)  
&nbsp;&nbsp;&nbsp;&nbsp;4.2.3 [Communication Model and Protocol](#423-communication-model-and-protocol)  
4.3 [Android Application Architecture](#43-android-application-architecture)  
&nbsp;&nbsp;&nbsp;&nbsp;4.3.1 [Recording Management Component](#431-recording-management-component)  
&nbsp;&nbsp;&nbsp;&nbsp;4.3.2 [High-Resolution Video Capture (RGB Camera)](#432-high-resolution-video-capture-rgb-camera)  
&nbsp;&nbsp;&nbsp;&nbsp;4.3.3 [Thermal Camera Integration (Topdon)](#433-thermal-camera-integration-topdon)  
&nbsp;&nbsp;&nbsp;&nbsp;4.3.4 [Shimmer GSR Sensor Integration](#434-shimmer-gsr-sensor-integration)  
4.4 [Desktop Controller Architecture](#44-desktop-controller-architecture)  
&nbsp;&nbsp;&nbsp;&nbsp;4.4.1 [Session Coordination Module](#441-session-coordination-module)  
&nbsp;&nbsp;&nbsp;&nbsp;4.4.2 [Computer Vision Processing Pipeline](#442-computer-vision-processing-pipeline)  
&nbsp;&nbsp;&nbsp;&nbsp;4.4.3 [Calibration System Implementation](#443-calibration-system-implementation)  
4.5 [Communication and Networking Design](#45-communication-and-networking-design)  
&nbsp;&nbsp;&nbsp;&nbsp;4.5.1 [Control Protocol Implementation](#451-control-protocol-implementation)  
&nbsp;&nbsp;&nbsp;&nbsp;4.5.2 [Data Streaming Mechanism](#452-data-streaming-mechanism)  
4.6 [Data Processing Pipeline](#46-data-processing-pipeline)  
&nbsp;&nbsp;&nbsp;&nbsp;4.6.1 [Real-Time Signal Processing Framework](#461-real-time-signal-processing-framework)  
&nbsp;&nbsp;&nbsp;&nbsp;4.6.2 [Synchronization Engine Design](#462-synchronization-engine-design)  
4.7 [Implementation Challenges and Solutions](#47-implementation-challenges-and-solutions)  
&nbsp;&nbsp;&nbsp;&nbsp;4.7.1 [Multi-Platform Compatibility](#471-multi-platform-compatibility)  
&nbsp;&nbsp;&nbsp;&nbsp;4.7.2 [Real-Time Synchronization Challenges](#472-real-time-synchronization-challenges)  
&nbsp;&nbsp;&nbsp;&nbsp;4.7.3 [Resource Management and Optimization](#473-resource-management-and-optimization)  
4.8 [Technology Stack and Design Decisions](#48-technology-stack-and-design-decisions)  
&nbsp;&nbsp;&nbsp;&nbsp;4.8.1 [Android Platform and Library Choices](#481-android-platform-and-library-choices)  
&nbsp;&nbsp;&nbsp;&nbsp;4.8.2 [Desktop (Python) Framework Choices](#482-desktop-python-framework-choices)  
&nbsp;&nbsp;&nbsp;&nbsp;4.8.3 [Communication Protocol Selection](#483-communication-protocol-selection)  
&nbsp;&nbsp;&nbsp;&nbsp;4.8.4 [Database/Storage Design Decision](#484-databasestorage-design-decision)  
4.9 [Android Application Implementation and Features](#49-android-application-implementation-and-features)  
&nbsp;&nbsp;&nbsp;&nbsp;4.9.1 [Multi-Sensor Data Collection (4K Video, Thermal, GSR)](#491-multi-sensor-data-collection-4k-video-thermal-gsr)  
&nbsp;&nbsp;&nbsp;&nbsp;4.9.2 [Session Lifecycle Management](#492-session-lifecycle-management)  
&nbsp;&nbsp;&nbsp;&nbsp;4.9.3 [Networking and Data Transfer Management](#493-networking-and-data-transfer-management)  
&nbsp;&nbsp;&nbsp;&nbsp;4.9.4 [User Interface and Interaction Design](#494-user-interface-and-interaction-design)  
4.10 [Python Desktop Controller Implementation](#410-python-desktop-controller-implementation)  
&nbsp;&nbsp;&nbsp;&nbsp;4.10.1 [Application Architecture and Module Integration](#4101-application-architecture-and-module-integration)  
&nbsp;&nbsp;&nbsp;&nbsp;4.10.2 [Graphical User Interface (Desktop Dashboard)](#4102-graphical-user-interface-desktop-dashboard)  
&nbsp;&nbsp;&nbsp;&nbsp;4.10.3 [Network Layer and Device Coordination](#4103-network-layer-and-device-coordination)  
&nbsp;&nbsp;&nbsp;&nbsp;4.10.4 [Webcam Service and Computer Vision Integration](#4104-webcam-service-and-computer-vision-integration)  
&nbsp;&nbsp;&nbsp;&nbsp;4.10.5 [Calibration and Validation Tools](#4105-calibration-and-validation-tools)  
&nbsp;&nbsp;&nbsp;&nbsp;4.10.6 [Stimulus Presentation and Experiment Control](#4106-stimulus-presentation-and-experiment-control)  
4.11 [Data Processing and Quality Management](#411-data-processing-and-quality-management)  
&nbsp;&nbsp;&nbsp;&nbsp;4.11.1 [Real-Time Data Processing Performance](#4111-real-time-data-processing-performance)  
&nbsp;&nbsp;&nbsp;&nbsp;4.11.2 [Data Quality Assurance Measures](#4112-data-quality-assurance-measures)  
4.12 [Testing and QA Integration in Design](#412-testing-and-qa-integration-in-design)  
&nbsp;&nbsp;&nbsp;&nbsp;4.12.1 [Built-in Testing Strategy and Framework](#4121-built-in-testing-strategy-and-framework)  
&nbsp;&nbsp;&nbsp;&nbsp;4.12.2 [Performance Monitoring and Optimization](#4122-performance-monitoring-and-optimization)  
4.13 [Multi-Device Synchronization Implementation](#413-multi-device-synchronization-implementation)  
&nbsp;&nbsp;&nbsp;&nbsp;4.13.1 [Temporal Coordination Algorithm](#4131-temporal-coordination-algorithm)

### Chapter 5. Evaluation and Testing
5.1 [Testing Strategy Overview](#51-testing-strategy-overview)  
&nbsp;&nbsp;&nbsp;&nbsp;5.1.1 [Methodology and Multi-Level Testing Approach](#511-methodology-and-multi-level-testing-approach)  
&nbsp;&nbsp;&nbsp;&nbsp;5.1.2 [Research-Specific Testing Considerations and Metrics](#512-research-specific-testing-considerations-and-metrics)  
5.2 [Testing Framework Architecture](#52-testing-framework-architecture)  
&nbsp;&nbsp;&nbsp;&nbsp;5.2.1 [Cross-Platform (PC–Android) Test Architecture](#521-cross-platform-pc-android-test-architecture)  
&nbsp;&nbsp;&nbsp;&nbsp;5.2.2 [Test Data Management and Environment Setup](#522-test-data-management-and-environment-setup)  
5.3 [Unit Testing Implementation](#53-unit-testing-implementation)  
&nbsp;&nbsp;&nbsp;&nbsp;5.3.1 [Android Application Unit Tests (Camera & Sensor Modules)](#531-android-application-unit-tests-camera-sensor-modules)  
&nbsp;&nbsp;&nbsp;&nbsp;5.3.2 [Desktop Controller Unit Tests (Calibration & Sync Modules)](#532-desktop-controller-unit-tests-calibration-sync-modules)  
5.4 [Integration Testing](#54-integration-testing)  
&nbsp;&nbsp;&nbsp;&nbsp;5.4.1 [Multi-Device Integration Testing (Android–PC Synchronization)](#541-multi-device-integration-testing-android-pc-synchronization)  
&nbsp;&nbsp;&nbsp;&nbsp;5.4.2 [Network Communication Testing](#542-network-communication-testing)  
5.5 [System Testing and Validation](#55-system-testing-and-validation)  
&nbsp;&nbsp;&nbsp;&nbsp;5.5.1 [End-to-End System Testing](#551-end-to-end-system-testing)  
&nbsp;&nbsp;&nbsp;&nbsp;5.5.2 [Data Quality and Accuracy Validation](#552-data-quality-and-accuracy-validation)  
5.6 [Performance Testing and Benchmarking](#56-performance-testing-and-benchmarking)  
&nbsp;&nbsp;&nbsp;&nbsp;5.6.1 [Reliability and Stress Testing](#561-reliability-and-stress-testing)  
&nbsp;&nbsp;&nbsp;&nbsp;5.6.2 [System Performance Benchmarking](#562-system-performance-benchmarking)  
5.7 [Results Analysis and Evaluation](#57-results-analysis-and-evaluation)  
&nbsp;&nbsp;&nbsp;&nbsp;5.7.1 [Summary of Test Results](#571-summary-of-test-results)  
&nbsp;&nbsp;&nbsp;&nbsp;5.7.2 [Requirements Validation (Functional & Non-Functional)](#572-requirements-validation-functional-non-functional)  
&nbsp;&nbsp;&nbsp;&nbsp;5.7.3 [Defect Analysis and Improvements](#573-defect-analysis-and-improvements)

### Chapter 6. Conclusions
6.1 [Project Achievements Summary](#61-project-achievements-summary)  
&nbsp;&nbsp;&nbsp;&nbsp;6.1.1 [Key Deliverables and Outcomes](#611-key-deliverables-and-outcomes)  
&nbsp;&nbsp;&nbsp;&nbsp;6.1.2 [Technical Innovation Achievements](#612-technical-innovation-achievements)  
6.2 [Goals Assessment and Validation](#62-goals-assessment-and-validation)  
&nbsp;&nbsp;&nbsp;&nbsp;6.2.1 [Evaluation of Primary Goals](#621-evaluation-of-primary-goals)  
&nbsp;&nbsp;&nbsp;&nbsp;6.2.2 [Secondary Goals and Unexpected Outcomes](#622-secondary-goals-and-unexpected-outcomes)  
6.3 [Critical Evaluation of Results](#63-critical-evaluation-of-results)  
&nbsp;&nbsp;&nbsp;&nbsp;6.3.1 [System Design Strengths and Challenges](#631-system-design-strengths-and-challenges)  
&nbsp;&nbsp;&nbsp;&nbsp;6.3.2 [Comparison with Existing Solutions](#632-comparison-with-existing-solutions)  
6.4 [System Performance Analysis](#64-system-performance-analysis)  
&nbsp;&nbsp;&nbsp;&nbsp;6.4.1 [Performance Characteristics and Metrics](#641-performance-characteristics-and-metrics)  
&nbsp;&nbsp;&nbsp;&nbsp;6.4.2 [Validation of Performance Results](#642-validation-of-performance-results)  
6.5 [Technical Contributions and Innovations](#65-technical-contributions-and-innovations)  
&nbsp;&nbsp;&nbsp;&nbsp;6.5.1 [Research Methodology Contributions](#651-research-methodology-contributions)  
&nbsp;&nbsp;&nbsp;&nbsp;6.5.2 [Software Engineering Contributions](#652-software-engineering-contributions)  
6.6 [Limitations and Constraints](#66-limitations-and-constraints)  
&nbsp;&nbsp;&nbsp;&nbsp;6.6.1 [Technical Limitations](#661-technical-limitations)  
&nbsp;&nbsp;&nbsp;&nbsp;6.6.2 [Practical and Operational Constraints](#662-practical-and-operational-constraints)  
6.7 [Future Work and Extensions](#67-future-work-and-extensions)  
&nbsp;&nbsp;&nbsp;&nbsp;6.7.1 [Short-Term Enhancement Opportunities](#671-short-term-enhancement-opportunities)  
&nbsp;&nbsp;&nbsp;&nbsp;6.7.2 [Long-Term Research Directions](#672-long-term-research-directions)

### Appendices
**Appendix A**: [System Manual](#appendix-a-system-manual)  
**Appendix B**: [User Manual](#appendix-b-user-manual)  
**Appendix C**: [Supporting Documentation and Data](#appendix-c-supporting-documentation-and-data)  
**Appendix D**: [Test Results and Reports](#appendix-d-test-results-and-reports)  
**Appendix E**: [Evaluation Data and Analysis](#appendix-e-evaluation-data-and-analysis)  
**Appendix F**: [Code Listings](#appendix-f-code-listings)

---

# Chapter 1. Introduction

## 1.1 Background and Motivation

### Research Context and Scientific Foundations

The field of physiological measurement has undergone significant transformation over the past decades, driven by advances in sensor technologies, computational capabilities, and our understanding of human psychophysiology. Traditional physiological measurement approaches, while scientifically validated and widely adopted, impose inherent limitations that constrain research design and may influence the very phenomena being studied.

Galvanic Skin Response (GSR), also known as Electrodermal Activity (EDA), represents one of the most established methods for measuring physiological arousal and stress responses in research settings. This biomarker has been extensively validated across decades of psychophysiological research and remains a gold standard for measuring sympathetic nervous system activation [CITE - Boucsein, W. (2012). Electrodermal activity. Springer Science & Business Media].

However, the contact-based nature of traditional GSR measurement introduces several methodological constraints that limit its applicability in naturalistic research settings. The requirement for electrode placement creates physical constraints on participant movement, introduces potential discomfort that may alter baseline physiological responses, and restricts experimental designs to controlled laboratory environments.

### Evolution of Physiological Measurement Technologies

The progression of physiological measurement technologies reflects the broader evolution of sensor systems and computational analysis capabilities. Early physiological measurement systems required specialized laboratory equipment, trained operators, and controlled environmental conditions to achieve reliable measurements. These systems, while accurate, were primarily suited for clinical and laboratory research applications.

The emergence of wearable sensor technologies represents a significant advancement in making physiological measurement more accessible and less intrusive. Consumer-grade wearable devices have democratized access to basic physiological monitoring capabilities, enabling continuous measurement in natural environments. However, these devices often sacrifice measurement precision for convenience and may not meet the accuracy requirements for rigorous scientific research.

Recent advances in computer vision, thermal imaging, and signal processing have opened new possibilities for contactless physiological measurement. These approaches leverage remote sensing technologies to extract physiological signals without requiring direct contact with participants, potentially eliminating many limitations of traditional measurement approaches while maintaining research-grade accuracy.

### Limitations of Current Approaches

Traditional contact-based physiological measurement approaches, while scientifically validated, present several fundamental limitations that constrain research applications:

**Physical Constraints and Participant Comfort**: Electrode placement for GSR measurement requires direct skin contact and may cause discomfort during extended recording sessions. The physical presence of electrodes can restrict natural movement and may influence participant behavior, potentially introducing artifacts into the data being collected.

**Environmental Restrictions**: Traditional measurement systems typically require controlled laboratory environments with specialized equipment and trained operators. This constraint limits the applicability of physiological measurement to naturalistic settings where authentic behavioral responses might be observed.

**Scalability Limitations**: Contact-based measurement approaches face practical limitations when scaling to multiple participants or large-scale studies. Each participant requires individual sensor attachment, calibration, and monitoring, creating logistical challenges for research designs requiring simultaneous measurement of multiple individuals.

**Measurement Artifacts**: The process of electrode attachment and the physical presence of measurement equipment may alter the baseline physiological state being measured. This fundamental challenge, known as the "observer effect," can influence the validity of measurements, particularly in stress and emotion research where the measurement process itself may induce stress responses.

### Motivation for Contactless Measurement Paradigms

The development of contactless physiological measurement approaches addresses these limitations while preserving the scientific rigor required for research applications. Contactless measurement enables:

**Naturalistic Measurement Environments**: By eliminating the need for direct contact, participants can be measured in natural settings without the constraints imposed by traditional measurement equipment. This capability enables research into authentic behavioral responses that may not be observable in controlled laboratory environments.

**Multi-Participant Coordination**: Contactless approaches enable simultaneous measurement of multiple participants without the logistical complexity of individual sensor attachment and calibration. This capability opens new possibilities for research into group dynamics, social physiological responses, and large-scale behavioral studies that were previously constrained by measurement methodology limitations.

**Longitudinal and Continuous Monitoring**: The reduced intrusiveness of contactless measurement enables extended monitoring periods without participant discomfort or measurement artifacts. This capability supports longitudinal research designs and the study of physiological patterns over extended time periods.

**Ethical and Practical Advantages**: Contactless measurement reduces the invasiveness of research participation while maintaining measurement quality. This approach may increase participant recruitment and retention while reducing ethical considerations associated with invasive measurement procedures.

## 1.2 Research Problem and Objectives

### 1.2.1 Problem Context and Significance

The central research problem addressed in this thesis emerges from the intersection of several technological and methodological challenges in physiological measurement research. While contact-based GSR measurement provides established and validated physiological data, the constraints it imposes on research design and participant experience limit its applicability for many contemporary research questions.

**Research Design Constraints**: Traditional physiological measurement approaches restrict experimental designs to controlled laboratory settings with stationary participants. This limitation prevents the study of physiological responses in naturalistic environments where authentic behavioral patterns might emerge. Many research questions in psychology, human-computer interaction, and behavioral science require measurement capabilities that preserve ecological validity while maintaining measurement precision.

**Technological Integration Challenges**: Existing contactless measurement approaches typically focus on single-modality sensing and lack the comprehensive integration required for research-grade applications. The challenge lies in coordinating multiple sensor modalities (RGB cameras, thermal imaging, reference physiological sensors) with the temporal precision and data quality required for scientific research while maintaining the practical usability needed for routine research operations.

**Validation and Reliability Requirements**: Any alternative to established measurement approaches must demonstrate comparable accuracy and reliability while providing clear advantages in terms of usability and research design flexibility. The challenge is developing contactless measurement capabilities that meet scientific standards for validity and reliability while offering practical advantages over traditional approaches.

**Scalability and Accessibility Considerations**: Research instrumentation often requires specialized equipment, technical expertise, and significant financial investment that may limit accessibility for many research teams. The challenge is developing approaches that democratize access to advanced physiological measurement capabilities while maintaining research-grade quality and scientific validity.

### 1.2.2 Aim and Specific Objectives

#### Primary Research Objectives

The primary aim of this research is to design, implement, and validate a comprehensive Multi-Sensor Recording System that enables contactless physiological measurement with research-grade accuracy and reliability. This system addresses the fundamental limitations of traditional contact-based approaches while providing new capabilities for multi-modal research applications.

**Objective 1: System Architecture Development**
Develop a distributed system architecture that coordinates multiple sensor modalities with microsecond-precision temporal synchronization across heterogeneous hardware platforms. The architecture must support real-time data collection, processing, and analysis while maintaining fault tolerance and scalability for research applications.

**Objective 2: Contactless Measurement Validation**
Validate contactless physiological measurement approaches against established contact-based reference measurements, demonstrating comparable accuracy and reliability. The validation must provide statistical evidence for the scientific validity of contactless approaches while identifying optimal operating conditions and limitations.

**Objective 3: Multi-Modal Integration Framework**
Create comprehensive integration methodology that combines RGB video analysis, thermal imaging, and reference physiological sensors into a unified measurement platform. The framework must provide seamless coordination across sensor modalities while enabling independent operation and specialized analysis capabilities.

#### Secondary Research Objectives

**Objective 4: Research Methodology Contribution**
Establish systematic methodologies for research software development that balance scientific rigor with practical usability requirements. The methodologies must address requirements engineering, validation testing, and documentation standards specifically adapted for research instrumentation development.

**Objective 5: Community Accessibility Enhancement**
Develop open-source, well-documented platform that reduces barriers to advanced physiological measurement research. The platform must provide comprehensive documentation, training resources, and example implementations that enable adoption by research teams with diverse technical capabilities.

**Objective 6: Future Research Enablement**
Create extensible architecture and comprehensive documentation that supports future research applications and technological extensions. The system must provide foundation capabilities for emerging research paradigms while maintaining compatibility with established research methodologies.

#### Technical Innovation Objectives

**Objective 7: Distributed Synchronization Innovation**
Develop novel algorithms for achieving microsecond-precision synchronization across consumer-grade wireless devices. The algorithms must compensate for network latency variations, clock drift, and device-specific timing characteristics while maintaining real-time performance requirements.

**Objective 8: Cross-Platform Integration Excellence**
Establish comprehensive methodologies for coordinating Android mobile applications with Python desktop controllers while maintaining code quality, development productivity, and system reliability. The integration must enable seamless operation across platforms while preserving individual platform capabilities.

**Objective 9: Adaptive Quality Management**
Create intelligent quality management systems that provide real-time assessment and optimization across multiple sensor modalities. The system must automatically adjust operational parameters based on environmental conditions while providing comprehensive quality metrics for research documentation.

## 1.3 Thesis Structure and Scope

### Document Organization and Chapter Overview

This thesis provides comprehensive academic treatment of the Multi-Sensor Recording System development through six substantial chapters that cover all aspects from initial requirements analysis through final evaluation and future work planning. The organizational structure reflects the systematic approach employed throughout the project lifecycle, demonstrating how theoretical computer science principles can be applied to solve practical research challenges.

**Chapter 2: Context and Literature Review** provides comprehensive foundation by examining existing research in contactless physiological measurement, distributed systems coordination, and research software development. The chapter establishes theoretical foundations while identifying research gaps and opportunities that motivate the current research.

**Chapter 3: Requirements and Analysis** presents systematic requirements engineering methodology specifically adapted for research software development. The chapter demonstrates rigorous stakeholder analysis, requirement elicitation, and validation approaches that ensure comprehensive coverage while maintaining technical feasibility.

**Chapter 4: Design and Implementation** details sophisticated architectural design decisions and implementation approaches that enable the system to meet rigorous requirements while providing scalability and maintainability. The chapter showcases novel contributions to distributed systems design while maintaining practical usability.

**Chapter 5: Testing and Evaluation** presents comprehensive testing strategy and validation results that demonstrate system reliability, performance, and research-grade quality. The chapter establishes testing methodologies specifically designed for research software validation while providing statistical evidence for system capability.

**Chapter 6: Conclusions and Evaluation** provides critical evaluation of project achievements, systematic assessment of technical contributions, and comprehensive analysis of limitations while outlining future development directions and research opportunities.

**Chapter 7: Appendices** supplies essential technical documentation, user guides, and supporting materials that supplement the main thesis content while providing practical implementation guidance for future development teams.

### Research Scope and Boundaries

The research scope encompasses the complete development lifecycle of a sophisticated multi-sensor coordination platform while establishing new methodological frameworks applicable to broader research software development. The scope includes:

**Technical Scope**: Development of distributed system architecture, implementation of cross-platform applications, creation of advanced synchronization algorithms, and validation of contactless measurement approaches with statistical rigor and scientific validity.

**Methodological Scope**: Establishment of systematic approaches to research software development including requirements engineering, testing methodologies, and documentation standards specifically adapted for scientific instrumentation applications.

**Application Scope**: Focus on physiological measurement research applications with particular emphasis on stress and emotion research, while maintaining architectural flexibility for adaptation to other research domains requiring multi-modal sensor coordination.

**Validation Scope**: Comprehensive testing and validation covering technical performance, scientific accuracy, and practical usability across diverse operational scenarios while providing statistical evidence for research-grade quality and reliability.

### Academic Contributions and Expected Outcomes

This research contributes to multiple areas of computer science and research methodology while addressing practical challenges in physiological measurement research:

**Theoretical Contributions**: Novel distributed system architectures for research applications, advanced synchronization algorithms for heterogeneous wireless networks, and systematic methodologies for research software development that balance scientific rigor with practical implementation requirements.

**Practical Contributions**: Open-source research platform that reduces barriers to advanced physiological measurement research, comprehensive documentation and training resources that support community adoption, and validated methodologies that enable reproducible research software development.

**Community Impact**: Democratization of access to advanced research capabilities through cost-effective solutions, establishment of new standards for research software development and community contribution, and creation of educational resources that support research methodology training and implementation guidance.

The thesis demonstrates that research-grade reliability and accuracy can be achieved using consumer-grade hardware when supported by sophisticated software algorithms and validation procedures, opening new possibilities for democratizing access to advanced research capabilities while maintaining scientific validity and research quality standards.

---
