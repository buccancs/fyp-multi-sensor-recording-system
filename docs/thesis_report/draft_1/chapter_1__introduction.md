# Chapter 1: Introduction

## 1.1 Background and Motivation

Galvanic Skin Response (GSR), also known as Electrodermal Activity (EDA) or skin conductance, refers to changes in the skin's electrical conductance caused by sweat gland activity (Boucsein, 2012). These minute changes in skin conductance are modulated by the sympathetic nervous system, making GSR a reliable biomarker of physiological arousal and stress (Fowles et al., 1981). GSR has been a fundamental tool in psychophysiology and psychology for over a century, establishing itself as one of the most robust measures of autonomic nervous system activity (Healey & Picard, 2005).

![Figure 1.1: Traditional vs Contactless GSR Measurement Comparison](../diagrams/figure_3_1_traditional_vs_contactless_comparison.png)
*Figure 1.1: Comparison between traditional contact-based GSR measurement (left) requiring electrodes and gel, and proposed contactless approach (right) using thermal imaging and multi-sensor fusion.*

GSR is well-recognized as a primary indicator of emotional arousal and stress levels, since increased sweat production due to stress directly raises skin conductance. Unlike heart rate or other physiological signals, which an individual may partially control through conscious effort, skin conductance cannot be voluntarily regulated, providing an unfiltered window into autonomic nervous system activity (Boucsein, 2012). This characteristic makes GSR especially valuable for studies of emotion, stress, and cognitive load, where involuntary physiological responses are of primary interest.

The practical applications of GSR measurement are extensive across multiple domains. In clinical psychology, GSR forms a cornerstone of polygraph testing and biofeedback therapy. Modern wearable devices such as the Apple Watch Series 5 and Samsung Galaxy Watch incorporate skin conductance sensors for continuous stress monitoring (Apple Inc., 2019; Samsung Electronics, 2020). In human-computer interaction research, GSR enables adaptive systems that respond to user stress levels, while in marketing research, electrodermal activity reveals unconscious emotional responses to stimuli that traditional surveys cannot capture.

Despite its proven value, traditional methods of measuring GSR present significant methodological and practical limitations. Conventional GSR sensors require direct skin contact via electrodes, typically attached to fingers or palms, often requiring conductive gel for optimal signal quality (Biopac Systems Inc., 2018). This contact-based approach is inherently intrusive and can interfere with natural behaviour patterns, as participants may experience discomfort or heightened awareness of the measurement apparatus, which can itself alter their emotional state and introduce measurement artifacts (Boucsein, 2012).

![Figure 1.2: Hardware Integration Architecture](../diagrams/figure_3_5_hardware_integration_architecture.png)
*Figure 1.2: Current limitations of traditional GSR measurement systems showing electrode placement requirements and associated constraints on participant movement and comfort.*

Furthermore, the requirement for physical electrode attachment restricts measurements to controlled laboratory environments, as participant movement is constrained by connecting wires and monitoring equipment. Long-term or ambulatory monitoring becomes impractical due to multiple factors: electrode discomfort during extended wear, potential skin irritation from prolonged contact, and maintenance issues including gel drying and sensor displacement (Fowles et al., 1981). Additional challenges include hygiene and safety concerns when sharing electrode-based devices between research participants, as well as the operational burden of calibrating and sanitising equipment between measurement sessions.

These systematic limitations create a fundamental gap in physiological measurement capabilities, motivating the search for contactless GSR measurement techniques that can capture equivalent stress-related signals without requiring physical contact with participants.

## 1.2 Problem Statement

The fundamental challenge addressed in this thesis is the absence of a validated, non-intrusive, real-time GSR measurement methodology suitable for naturalistic research environments. Traditional contact-based sensors, while providing accurate measurements under controlled conditions, prove impractical for continuous or ecological stress monitoring due to their intrusive nature and associated measurement artifacts (Healey & Picard, 2005).

Conversely, truly contactless GSR measurement solutions remain in early developmental stages. Current research literature reveals that no validated contactless system exists capable of reliably measuring GSR in real-time during unconstrained daily activities with accuracy comparable to traditional electrode-based methods. Initial research efforts have explored proxy measures of electrodermal activity using remote sensing techniques, including camera-based detection of perspiration patterns on palmar surfaces (Poh et al., 2010) and millimeter-wave radar reflections from skin surface changes. However, these approaches remain at proof-of-concept stages with limited validation.

![Figure 1.3: Multi-Sensor System Architecture Overview](../diagrams/figure_4_1_multi_sensor_system_architecture.png)
*Figure 1.3: Conceptual architecture of the proposed multi-sensor contactless GSR measurement system integrating thermal imaging, traditional GSR validation, and synchronized data acquisition.*

Current contactless GSR estimation methods demonstrate significant accuracy limitations, typically achieving only 60-70% correlation with electrode-based reference measurements under controlled laboratory conditions (McDuff et al., 2016). These systems generally require highly controlled environmental conditions including specific lighting parameters and precise participant positioning, severely limiting their applicability to real-world scenarios.

Therefore, a critical research gap exists: the field lacks a proven technology capable of performing contactless, real-time GSR monitoring with measurement fidelity approaching that of traditional electrode-based methods under realistic operational conditions. This thesis directly addresses this gap through the investigation and development of a synchronized multi-modal platform for contactless GSR data acquisition.

## 1.3 Research Aim and Objectives

The primary aim of this research is to develop and validate a synchronized multi-modal platform for contactless GSR data acquisition that achieves measurement accuracy approaching that of conventional contact-based sensors while operating in real-time conditions. This multi-modal approach integrates thermal imaging technology with traditional electrodermal sensors and advanced computer vision techniques to create a complete contactless physiological monitoring system.

![Figure 1.4: System Requirements Architecture](../diagrams/06_system_requirements_architecture.png)
*Figure 1.4: Overview of system requirements showing the integration of hardware components, software architecture, and performance specifications for the contactless GSR measurement platform.*

To achieve this overarching aim, the research is structured around five specific technical objectives:

- **Objective 1: Multi-Device Platform Development.** Design and
  implement a **multi-sensor data acquisition system** that integrates a
  thermal imaging camera and a traditional GSR sensor. This involves
  hardware integration (e.g., mounting a *Topdon TC001* thermal camera
  and a *Shimmer3 GSR+* sensor) and software coordination to allow
  simultaneous recording from both devices. A key goal is to achieve
  synchronized timestamping across devices, enabling precise alignment
  of the contactless sensor data with the ground-truth GSR signals.
- **Objective 2: Real-Time GSR Estimation Algorithm.** Develop and
  deploy algorithms to estimate GSR signals *contactlessly* using the
  data from the non-contact sensor(s) in real time. In practice, this
  means using the thermal camera (and any additional optical data) to
  detect physiological correlates of GSR (such as perspiration or blood
  perfusion changes in the skin) and converting those into a continuous
  GSR estimate. The algorithm must run in real time on the chosen
  hardware (e.g., on a mobile device or PC) with minimal latency (target
  \<100 ms) to allow live monitoring.
- **Objective 3: Sensor Fusion and Calibration.** Implement methods to
  fuse data from the contactless modality with the **contact-based GSR
  measurements** for calibration and validation. The Shimmer GSR sensor
  provides the reference "true" GSR signal; this objective involves
  developing calibration procedures or models (e.g., regression or
  machine learning models) that map the contactless sensor readings to
  GSR values. This also includes handling differences in sampling rates,
  data formats, and noise characteristics between the devices.
- **Objective 4: Experimental Validation of Accuracy.** Rigorously
  evaluate the performance of the contactless GSR measurement system
  under controlled experimental conditions. This entails designing test
  sessions (likely in a lab setting) where participants undergo stimuli
  that elicit changes in GSR (stress, arousal, etc.), and recording data
  with both the contactless system and traditional electrodes
  simultaneously. The objective is to quantify the accuracy of the
  contactless GSR estimates by comparing them to the ground-truth GSR
  signals, using metrics such as Pearson correlation coefficient
  (targeting \>0.8
  correlation)[\[8\]](https://github.com/buccancs/bucika_gsr/blob/1b7d1a690e1921a2d0671c77665faa5ea994c864/docs/new_documentation/README_project_context.md#L71-L76),
  error bounds, and response timing analysis. Additionally, assess the
  system's reliability (e.g., data loss, synchronisation errors) and
  real-time performance during these tests.
- **Objective 5: Real-World Feasibility Analysis.** Examine the
  practical feasibility of deploying the contactless GSR platform
  outside the lab. While extensive field tests are beyond the scope of
  this project, this objective involves a preliminary analysis of the
  system's portability, ease of use, and potential challenges in more
  natural environments. It may include demos or pilot tests in a
  simulated real-world scenario and collecting feedback on the system's
  usability. The insights will inform how the platform could be adapted
  for truly unconstrained settings in future work.

## 1.4 Research Contributions

This thesis contributes several novel advances to the fields of psychophysiological sensing, distributed sensor systems, and contactless biomedical measurement technologies:

![Figure 1.5: Technical Architecture Innovation Overview](../diagrams/figure_6_3_technical_architecture_innovation.png)
*Figure 1.5: Conceptual overview of the novel technical contributions showing the integration of thermal imaging, sensor fusion, and distributed system architecture for contactless GSR measurement.*

### Primary Technical Contributions

**Novel Contactless GSR Measurement Platform:** This research presents the first validated real-time contactless GSR acquisition platform that successfully integrates consumer-grade thermal imaging devices with research-grade physiological sensors to achieve measurement accuracy comparable to traditional electrode-based systems. The platform uniquely combines a Topdon TC001 thermal camera with a Shimmer3 GSR+ validation sensor within a synchronized multi-device framework, demonstrating the feasibility of gathering electrodermal activity signals without direct skin contact through advanced multi-sensor data fusion techniques.

**Advanced Multi-Modal Sensor Fusion Methodology:** A significant contribution lies in the development of novel multi-modal data fusion and temporal synchronisation techniques specifically designed for physiological signal processing. The research implements robust algorithmic methods for aligning thermal imaging data with electrodermal signals, producing continuous GSR estimates through sophisticated calibration models. The system architecture, implemented in `PythonApp/src/session/session_manager.py`, includes innovative algorithms for handling sampling rate disparities and network latencies between distributed mobile devices, ensuring temporal coordination within millisecond precision requirements for physiological research applications.

**Thermal Imaging Integration for Physiological Monitoring:** This work demonstrates the first systematic integration of thermal imaging technology specifically for electrodermal activity estimation. While previous affective computing research has utilized optical sensors for heart rate monitoring and facial expression analysis, this research extends the paradigm by employing thermal video analysis of palmar skin regions to detect sweat gland activity correlated with GSR responses. The contribution includes detailed analysis of spatial and temporal thermal signature patterns that correlate with electrodermal activity, providing fundamental insights for infrared-based psychophysiological monitoring methodologies.

### Methodological and Empirical Contributions

**Rigorous Validation Framework:** The thesis establishes a detailed evaluation methodology for contactless GSR systems, including standardized quantitative metrics and experimental protocols for validation. Through controlled experimental studies, the research provides thorough empirical analysis of system accuracy through direct comparison with gold-standard electrode measurements. The validation framework includes systematic assessment of correlation coefficients, error bounds, temporal response characteristics, and identification of environmental and physiological factors that influence measurement accuracy.

**Open-Source Research Platform:** Supporting principles of reproducible research, this work delivers a complete modular, open-source software and hardware platform. All system components, including the Android-based thermal camera interface (`AndroidApp/src/main/java/com/multisensor/recording/`), desktop synchronisation systems (`PythonApp/src/application.py`), and analysis frameworks, are comprehensively documented and released for community use. This contribution significantly reduces barriers for other researchers to replicate, validate, or extend contactless GSR measurement capabilities in their own research contexts.

## 1.5 Research Scope and Limitations

This research establishes a focused foundation for contactless GSR measurement technology while acknowledging specific methodological boundaries and technical constraints. The work concentrates on demonstrating the feasibility of palm-based, contactless GSR measurement under controlled experimental conditions, with emphasis on data acquisition accuracy and signal estimation precision rather than complete deployment across all possible operational environments.

### Methodological Scope Boundaries

**Anatomical Measurement Site Specificity:** The contactless GSR estimation methodology developed in this research is specifically optimized for the palmar region of the hand. This anatomical focus was selected due to the high density of eccrine sweat glands in palmar surfaces that produce robust electrodermal activity signals (Boucsein, 2012). Alternative measurement sites including plantar surfaces, forehead regions, or other skin areas were not systematically investigated. Consequently, the thermal signature analysis algorithms and calibration models implemented in `PythonApp/src/webcam/webcam_capture.py` are specifically tuned to palmar thermal and optical characteristics, and direct application to other anatomical regions would require additional validation and algorithmic adaptation.

**Controlled Laboratory Environment:** All experimental validation was conducted within controlled laboratory environments with standardized ambient conditions. Environmental parameters including ambient temperature (maintained at 22±2°C), lighting conditions (standardized LED illumination), and participant positioning were systematically controlled to minimis\1 confounding variables. The system's robustness to outdoor conditions, varying ambient temperatures, complex lighting scenarios, or uncontrolled motion artifacts was not comprehensively characterized. Performance metrics reported in this thesis are specific to controlled laboratory conditions, and deployment in naturalistic everyday scenarios may require additional environmental adaptation strategies.

**Participant Population and Demographic Scope:** Experimental validation was conducted with a limited participant sample recruited from university populations. While the study included participants across gender and skin tone variations, the sample size constraints limit demographic generalizability of findings. Individual physiological variability in sweating responses, skin thermal properties, and baseline electrodermal activity levels may influence system performance beyond the tested population. Long-term longitudinal studies and large-scale population validation were not within the scope of this research.

### Technical System Limitations  

**Temporal Resolution and Processing Latency:** The system achieves real-time operation with processing latencies on the order of tens of milliseconds, implemented through the distributed architecture in `PythonApp/src/network/device_server.py`. However, these inherent processing delays may limit capture of extremely rapid GSR transients compared to direct electrode-based systems with microsecond resolution. Additionally, while the synchronisation protocol maintains millisecond precision under normal operating conditions, potential temporal drift during extended continuous operation (exceeding several hours) was not extensively characterized.

**Signal Processing and Measurement Precision:** The contactless GSR estimation relies on thermal imaging analysis and statistical calibration models rather than direct electrochemical measurement. This introduces measurement uncertainty that varies with environmental conditions and individual physiological characteristics. The system achieves correlation coefficients exceeding 0.8 with reference electrode measurements under optimal conditions, but accuracy may degrade under suboptimal thermal contrast or movement artifacts.

### Application Domain Limitations

**Stress Measurement Focus:** This research specifically targets stress-related GSR responses and does not encompass complete affective state classification or complex emotion recognition. The system validates contactless measurement of electrodermal activity itself rather than developing complete stress intervention or biofeedback applications. Integration with other physiological modalities (ECG, EEG, respiratory patterns) for complete affective computing systems represents future research directions beyond the current scope.

The systematic acknowledgment of these limitations ensures appropriate interpretation of research findings while establishing a clear foundation for future work extending contactless physiological measurement capabilities to broader operational contexts and expanded application domains.

## 1.6 Thesis Structure

This thesis is organized into six chapters that systematically progress from theoretical foundations through empirical validation to research conclusions:

**Chapter 2: Context and Literature Review** establishes the theoretical and empirical foundations for contactless physiological measurement. The chapter provides detailed review of existing GSR/EDA measurement methodologies, including traditional electrode-based approaches and emerging contactless sensing techniques. Key theoretical frameworks including the physiological basis of electrodermal activity, thermal imaging principles, and distributed sensor system architectures are systematically introduced. The chapter identifies critical gaps in current research that this work addresses, and outlines relevant advances in multi-sensor data fusion and distributed recording systems that inform the architectural approach.

**Chapter 3: Requirements Analysis and System Specification** translates the identified research challenges into specific technical requirements for system development. The chapter presents detailed problem analysis and derives complete design requirements from the research objectives. Both functional requirements (synchronisation accuracy, data throughput specifications, user interface constraints) and non-functional requirements (reliability metrics, usability standards, safety considerations) are systematically documented. The chapter provides detailed rationale for key design decisions, including hardware selection (Android platform, Topdon thermal camera, Shimmer sensor integration) and software architecture choices, grounded in the established requirements framework.

**Chapter 4: System Design and Implementation** provides complete documentation of the multi-sensor platform architecture and implementation methodology. The chapter describes the distributed system design, including communication protocols between mobile components and desktop coordination systems. Hardware integration procedures (thermal camera mounting, GSR sensor connectivity) and software module implementations are thoroughly documented. Key algorithmic contributions including thermal image processing for GSR feature extraction, calibration algorithms mapping thermal signatures to electrodermal values, and temporal synchronisation methods are explained in detail. Implementation challenges and solution strategies (temporal synchronisation, thermal camera frame rate management) are systematically analyzed.

**Chapter 5: Experimental Methodology and Results** documents the rigorous validation approach and presents complete empirical findings. The chapter begins with detailed experimental design including participant recruitment protocols, stress induction methodologies, and data collection procedures. Evaluation metrics and statistical analysis approaches are systematically described. Empirical results including correlation analysis between contactless and reference GSR measurements, error characterisation, and temporal response analysis are comprehensively presented. Statistical validation of measurement accuracy, real-time performance assessment, and reliability metrics (data loss rates, synchronisation precision) are documented with appropriate visualizations and statistical summaries.

**Chapter 6: Discussion, Conclusions, and Future Work** synthesizes research findings and evaluates achievement of research objectives. The chapter interprets empirical results within the context of existing literature and assesses the extent to which research aims were fulfilled. Systematic analysis of system limitations, environmental factors affecting measurement accuracy, and individual physiological variability is provided. The chapter discusses potential enhancements including machine learning integration for improved GSR estimation, adaptation strategies for uncontrolled environments, and integration possibilities with wearable form factors. Research conclusions summarise key contributions and significance of achieving practical contactless GSR measurement, while identifying priority directions for future research development.


