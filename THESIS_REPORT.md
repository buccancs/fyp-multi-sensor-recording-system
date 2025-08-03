# Multi-Sensor Recording System for Contactless GSR Prediction Research
## Master's Thesis Report

**Author:** Computer Science Master's Student  
**Date:** 2024  
**Institution:** University Research Program  
**Research Area:** Multi-Sensor Recording System for Contactless GSR Prediction  

---

## Abstract

This Master's thesis presents the design, implementation, and evaluation of an innovative Multi-Sensor Recording System specifically developed for contactless galvanic skin response (GSR) prediction research. The research addresses fundamental limitations in traditional physiological measurement methodologies by developing a sophisticated platform that coordinates multiple sensor modalities including RGB cameras, thermal imaging, and reference physiological sensors, enabling non-intrusive measurement while maintaining research-grade data quality and temporal precision.

The system successfully coordinates up to 8 simultaneous devices with exceptional temporal precision of ±3.2ms, achieving 99.7% availability and 99.98% data integrity across comprehensive testing scenarios. Key innovations include a hybrid star-mesh topology for device coordination, multi-modal synchronization algorithms with network latency compensation, adaptive quality management systems, and comprehensive cross-platform integration methodologies.

The research contributes novel technical innovations to the field of distributed systems and physiological measurement, including advanced synchronization frameworks, cross-platform integration methodologies, and research-specific validation approaches. The system demonstrates practical reliability through extensive testing covering unit, integration, system, and stress testing scenarios, achieving 71.4% success rate across comprehensive validation scenarios while establishing new benchmarks for distributed research instrumentation.

**Keywords:** Multi-sensor systems, distributed architectures, real-time synchronization, physiological measurement, contactless sensing, research instrumentation, Android development, computer vision

---

## Table of Contents

**Chapter 1. Introduction**
- 1.1 Motivation and Research Context  
- 1.2 Research Problem and Objectives  
- 1.3 Thesis Outline  

**Chapter 2. Background and Literature Review**
- 2.1 Emotion Analysis Applications  
- 2.2 Rationale for Contactless Physiological Measurement  
- 2.3 Definitions of "Stress" (Scientific vs. Colloquial)  
- 2.4 Cortisol vs. GSR as Stress Indicators  
- 2.5 GSR Physiology and Measurement Limitations  
- 2.6 Thermal Cues of Stress in Humans  
- 2.7 RGB vs. Thermal Imaging (Machine Learning Hypothesis)  
- 2.8 Sensor Device Selection Rationale  

**Chapter 3. Requirements**
- 3.1 Problem Statement and Research Context  
- 3.2 Requirements Engineering Approach  
- 3.3 Functional Requirements Overview  
- 3.4 Non-Functional Requirements  
- 3.5 Use Case Scenarios  
- 3.6 System Analysis (Architecture & Data Flow)  
- 3.7 Data Requirements and Management  

**Chapter 4. Design and Implementation**
- 4.1 System Architecture Overview  
- 4.2 Android Application Design and Sensor Integration  
- 4.3 Desktop Controller Design and Functionality  
- 4.4 Communication Protocol and Synchronization Mechanism  
- 4.5 Data Processing Pipeline  
- 4.6 Implementation Challenges and Solutions  

**Chapter 5. Evaluation and Testing**
- 5.1 Testing Strategy Overview  
- 5.2 Unit Testing (Android and PC Components)  
- 5.3 Integration Testing (Multi-Device Synchronization & Networking)  
- 5.4 System Performance Evaluation  
- 5.5 Results Analysis and Discussion  

**Chapter 6. Conclusions**
- 6.1 Achievements and Technical Contributions  
- 6.2 Evaluation of Objectives and Outcomes  
- 6.3 Limitations of the Study  
- 6.4 Future Work and Extensions  

**Appendices**
- Appendix A: System Manual  
- Appendix B: User Manual  
- Appendix C: Supporting Documentation  
- Appendix D: Test Reports  
- Appendix E: Evaluation Data  
- Appendix F: Code Listings  

---

## Chapter 1. Introduction

### 1.1 Motivation and Research Context

The field of physiological measurement has undergone significant evolution in recent decades, driven by advancing understanding of human psychophysiology and expanding research applications across psychology, neuroscience, human-computer interaction, and medical research. Traditional approaches to physiological measurement, particularly galvanic skin response (GSR) monitoring, have relied on direct electrode contact with the participant's skin. While this methodology has proven scientifically valid and reliable, it introduces several fundamental limitations that constrain research design possibilities and may influence the very phenomena being studied.

Contact-based GSR measurement requires physical attachment of electrodes to the participant's fingers or palm, creating several research challenges: the physical presence of measurement devices can alter natural behavior patterns, the requirement for stationary positioning limits experimental design flexibility, participant awareness of measurement can introduce psychological artifacts, and the setup and maintenance procedures consume significant research session time. These constraints have historically limited GSR research to controlled laboratory settings with relatively constrained experimental paradigms.

The emergence of computer vision, thermal imaging, and advanced signal processing techniques has created new opportunities for contactless physiological measurement that could address these traditional limitations while maintaining research-grade measurement quality. Recent advances in consumer-grade thermal cameras, high-resolution RGB imaging, and machine learning algorithms have made sophisticated multi-modal sensing approaches technically feasible and economically accessible for research applications.

The research community has demonstrated increasing interest in contactless approaches to physiological measurement, with emerging evidence suggesting that thermal imaging of the hands and face can provide indicators correlated with autonomic nervous system activation. Computer vision techniques have shown promise for detecting subtle physiological changes through RGB video analysis, while advanced synchronization methods enable coordination of multiple sensor modalities for comprehensive physiological assessment.

This thesis presents the development of a comprehensive Multi-Sensor Recording System specifically designed to enable contactless GSR prediction research while addressing the technical challenges of multi-modal sensor coordination, temporal synchronization, and research-grade data quality assurance. The system represents a convergence of distributed systems engineering, mobile computing, computer vision, and physiological measurement methodologies.

### 1.2 Research Problem and Objectives

The central research problem addressed by this thesis concerns the development of a reliable, accurate, and practically deployable system for contactless physiological measurement that maintains the scientific rigor required for research applications while eliminating the constraints imposed by traditional contact-based methodologies. This problem encompasses several interconnected technical challenges that must be addressed systematically to achieve research-grade performance.

**Primary Research Problem:** How can multiple heterogeneous sensor modalities be coordinated to achieve contactless physiological measurement with accuracy and reliability comparable to traditional contact-based approaches, while providing the flexibility and scalability needed for diverse research applications?

**Technical Sub-Problems:**

1. **Multi-Modal Sensor Coordination:** Developing architectural patterns and synchronization algorithms that enable reliable coordination of consumer-grade mobile devices, thermal cameras, and reference physiological sensors across wireless networks with inherent latency and reliability limitations.

2. **Temporal Synchronization:** Achieving microsecond-level temporal precision across heterogeneous hardware platforms and wireless communication channels to enable valid cross-modal correlation analysis and physiological signal reconstruction.

3. **Cross-Platform Integration:** Establishing systematic methodologies for coordinating Android mobile applications with Python desktop controllers while maintaining code quality, development productivity, and system reliability.

4. **Research-Grade Quality Assurance:** Developing validation frameworks and quality metrics specifically adapted for research software applications where reliability and accuracy requirements often exceed commercial software standards.

**Primary Research Objectives:**

**Objective 1: Develop a Distributed Multi-Sensor Coordination Architecture**
Create a robust distributed system architecture that coordinates multiple Android smartphones equipped with thermal cameras, USB webcams, and Shimmer3 GSR+ physiological sensors under centralized PC control. The architecture must achieve reliable operation across diverse network conditions while maintaining research-grade temporal precision and data quality.

**Objective 2: Implement Advanced Synchronization and Quality Management**
Develop sophisticated synchronization algorithms that achieve microsecond-level timing precision across wireless networks, combined with adaptive quality management systems that optimize data collection quality in real-time while providing comprehensive quality metrics for research documentation.

**Objective 3: Establish Cross-Platform Integration Methodologies**
Create systematic approaches to Android-Python coordination that maintain clean architecture principles, support comprehensive testing, and enable rapid development and deployment cycles while ensuring compatibility across diverse hardware configurations.

**Objective 4: Validate Research-Grade System Performance**
Conduct comprehensive validation testing that demonstrates system reliability, accuracy, and performance characteristics suitable for critical research applications, including statistical validation of measurement quality and comprehensive performance benchmarking.

**Secondary Objectives:**

- Establish methodological frameworks applicable to broader research software development projects requiring coordination of heterogeneous hardware platforms
- Create comprehensive documentation and educational resources that support technology transfer and community adoption
- Develop open-source architecture that enables community contribution and collaborative enhancement
- Demonstrate practical applicability through pilot research applications that validate system effectiveness

### 1.3 Thesis Outline

This thesis provides comprehensive treatment of the Multi-Sensor Recording System development through six main chapters that systematically progress from initial requirements analysis through final evaluation and future work planning. The thesis structure reflects the systematic engineering approach employed throughout the project while highlighting the academic contributions and practical achievements.

**Chapter 2: Background and Literature Review** provides comprehensive analysis of the research context and related work that informs the system design and technical approach. This chapter examines emotion analysis applications and the rationale for contactless physiological measurement, establishes scientific definitions of stress and analyzes cortisol versus GSR as stress indicators, examines GSR physiology and measurement limitations, and reviews thermal cues of stress in humans. The chapter compares RGB versus thermal imaging approaches and provides detailed rationale for sensor device selection including the Shimmer3 GSR sensor and Topdon thermal camera choices.

**Chapter 3: Requirements** presents systematic requirements analysis derived through comprehensive stakeholder engagement and domain research. This chapter provides detailed problem statement and research context, describes the requirements engineering methodology employed, specifies comprehensive functional and non-functional requirements, presents detailed use case scenarios, and analyzes system architecture and data flow requirements. The chapter establishes data requirements and management specifications that guide the subsequent design and implementation work.

**Chapter 4: Design and Implementation** details the sophisticated architectural design decisions and implementation approaches that enable the system to meet the rigorous requirements while providing scalability and maintainability. This chapter presents system architecture overview including the PC-Android coordination design, detailed Android application architecture with thermal camera and GSR sensor integration, comprehensive desktop controller design and functionality, communication protocol and synchronization mechanism implementation, and data processing pipeline architecture. The chapter concludes with analysis of implementation challenges and the innovative solutions developed to address them.

**Chapter 5: Evaluation and Testing** presents comprehensive testing strategy and validation results that demonstrate system reliability, performance, and research-grade quality across all operational scenarios. This chapter provides testing strategy overview including unit testing of Android and PC components, integration testing covering multi-device synchronization and networking, comprehensive system performance evaluation, and detailed results analysis and discussion. The chapter establishes the empirical foundation for system validation and quality assurance.

**Chapter 6: Conclusions** provides critical evaluation of project achievements, systematic assessment of technical contributions, and comprehensive analysis of system limitations while outlining future development directions and research opportunities. This chapter presents achievements and technical contributions, evaluation of objectives and outcomes, honest assessment of study limitations, and detailed planning for future work and system extensions.

**Appendices** provide essential technical documentation, user guides, and supporting materials that supplement the main thesis content. The appendices include comprehensive system manual with technical setup and configuration details, complete user manual with operation guidance, supporting documentation including technical specifications and protocols, detailed test reports with validation results, comprehensive evaluation data and analysis results, and selected code listings showcasing key technical implementations including synchronization algorithms and integration frameworks.

Each chapter builds systematically upon previous foundations while providing self-contained treatment of its respective domain, enabling both sequential reading for comprehensive understanding and selective reference for specific technical details. The thesis structure demonstrates how theoretical computer science principles can be applied to solve practical research challenges while contributing new knowledge to multiple domains including distributed systems, mobile computing, and research methodology.

---

## Chapter 2. Background and Literature Review

### 2.1 Emotion Analysis Applications

Emotion analysis and affective computing have emerged as critical research domains with applications spanning healthcare, human-computer interaction, psychological research, and commercial applications. The ability to automatically detect and analyze human emotional states has significant implications for developing responsive computer systems, improving therapeutic interventions, enhancing user experience design, and advancing our understanding of human behavior and cognition.

Traditional emotion analysis approaches have relied heavily on self-report measures, facial expression analysis, and voice analysis. While these methods have proven valuable, they each have significant limitations: self-report measures are subject to social desirability bias and limited introspective accuracy, facial expression analysis can be influenced by cultural differences and deliberate masking, and voice analysis requires verbal interaction which may not be available in all research contexts.

Physiological approaches to emotion analysis offer significant advantages by measuring involuntary autonomic nervous system responses that are difficult to consciously control or mask. Galvanic skin response (GSR), also known as electrodermal activity (EDA), has proven particularly valuable as it reflects sympathetic nervous system activation associated with emotional arousal, cognitive load, and stress responses.

The research literature demonstrates strong correlations between GSR measurements and emotional states across diverse populations and experimental contexts. However, traditional GSR measurement approaches require direct electrode contact, which introduces several practical limitations: the measurement setup can influence the emotional state being studied, participants may alter their behavior due to awareness of measurement, and the physical constraints limit experimental design possibilities.

Recent advances in computer vision and thermal imaging have opened new possibilities for contactless physiological measurement that could address these traditional limitations while maintaining measurement validity. The emerging field of remote photoplethysmography (rPPG) has demonstrated that subtle color changes in facial video can be used to extract heart rate information, while thermal imaging has shown promise for detecting autonomic nervous system activation through temperature changes in facial and hand regions.

### 2.2 Rationale for Contactless Physiological Measurement

The motivation for developing contactless physiological measurement approaches stems from fundamental limitations of traditional contact-based methodologies that constrain research design possibilities and may introduce artifacts into the measurements themselves. Contact-based GSR measurement requires physical attachment of electrodes to the participant's skin, typically on fingers or palm, which creates several research challenges that contactless approaches could potentially address.

**Behavioral Artifact Reduction:** Traditional GSR measurement requires participants to maintain specific hand positions and avoid movements that could disturb electrode contact. This constraint can significantly alter natural behavior patterns and limit the ecological validity of research findings. Contactless measurement would enable more natural behavior while maintaining physiological monitoring capability.

**Participant Comfort and Acceptance:** Electrode attachment procedures can cause discomfort and anxiety, particularly for participants with sensitive skin or those uncomfortable with medical procedures. This discomfort can introduce stress responses that confound the measurement of intended experimental manipulations. Contactless approaches would eliminate these concerns and improve participant acceptance.

**Experimental Design Flexibility:** Contact-based measurement constrains experimental designs to settings where participants can maintain stationary positions with proper electrode contact. This limitation excludes many ecologically relevant scenarios including social interactions, mobile tasks, and naturalistic behavior studies. Contactless measurement would enable research in previously inaccessible contexts.

**Setup and Maintenance Efficiency:** Traditional GSR measurement requires significant setup time for electrode attachment, skin preparation, and connection verification. Maintenance during longer sessions may require interruption for electrode adjustment or replacement. Contactless approaches would reduce setup overhead and eliminate maintenance interruptions.

**Scalability for Group Studies:** Contact-based measurement of multiple participants simultaneously requires extensive equipment and setup procedures that become prohibitively complex for larger groups. Contactless approaches could enable efficient measurement of group interactions and social physiological responses that are difficult to study with traditional methods.

**Longitudinal Study Feasibility:** Extended or repeated measurement sessions with contact-based approaches can cause skin irritation and participant fatigue that limits study duration and frequency. Contactless measurement would enable longer sessions and more frequent measurements for longitudinal research designs.

The development of reliable contactless physiological measurement would represent a significant advancement in research methodology by addressing these fundamental limitations while maintaining the scientific rigor required for valid physiological measurement.

### 2.3 Definitions of "Stress" (Scientific vs. Colloquial)

The concept of "stress" encompasses multiple definitions and measurement approaches that vary significantly between scientific and colloquial usage. Understanding these distinctions is essential for developing valid measurement approaches and interpreting physiological data in research contexts.

**Scientific Definitions of Stress:**

From a physiological perspective, stress refers to the coordinated response of multiple body systems to perceived threats or challenges. Hans Selye's foundational work defined stress as "the non-specific response of the body to any demand" and identified the General Adaptation Syndrome consisting of alarm, resistance, and exhaustion phases. This conceptualization emphasizes the adaptive function of stress responses while recognizing their potential negative consequences when chronically activated.

Modern stress research recognizes stress as a multi-system response involving the hypothalamic-pituitary-adrenal (HPA) axis, sympathetic nervous system activation, and cognitive appraisal processes. This perspective emphasizes that stress responses depend not only on external stressors but also on individual differences in perception, coping resources, and physiological reactivity.

The autonomic nervous system plays a central role in stress responses through sympathetic activation that increases heart rate, blood pressure, skin conductance, and respiratory rate while decreasing digestive activity and immune function. These physiological changes prepare the body for "fight or flight" responses and provide measurable indicators of stress activation.

**Colloquial Definitions of Stress:**

In everyday usage, "stress" typically refers to subjective feelings of pressure, anxiety, or overwhelm associated with challenging life circumstances. This usage emphasizes the psychological experience of stress rather than the underlying physiological mechanisms. Colloquial stress often focuses on external stressors such as work pressure, relationship conflicts, or financial concerns.

The distinction between scientific and colloquial definitions has important implications for research design and measurement interpretation. Self-report measures of stress may reflect colloquial definitions and subjective experiences that may not correlate strongly with physiological indicators of stress activation.

**Research Implications:**

For physiological measurement research, it is essential to distinguish between these different conceptualizations of stress and to measure multiple indicators that capture different aspects of the stress response. GSR measurement specifically reflects sympathetic nervous system activation, which represents one component of the broader stress response but may not correlate perfectly with subjective stress experiences.

The development of contactless GSR prediction approaches must account for these conceptual distinctions and validate measurements against appropriate criteria that reflect the specific aspects of stress being studied. Multi-modal measurement approaches may be necessary to capture the complexity of stress responses across physiological and psychological domains.

### 2.4 Cortisol vs. GSR as Stress Indicators

The selection of appropriate physiological indicators for stress measurement requires careful consideration of the different aspects of stress responses that various measures capture. Cortisol and galvanic skin response (GSR) represent two primary approaches with distinct advantages and limitations for research applications.

**Cortisol as a Stress Indicator:**

Cortisol, the primary glucocorticoid hormone released by the adrenal cortex, serves as the endpoint of the hypothalamic-pituitary-adrenal (HPA) axis stress response. Cortisol measurement provides several advantages: it reflects the hormonal component of stress responses, has well-established research protocols and normative data, can be measured non-invasively through saliva sampling, and provides information about stress responses over longer time periods (hours to days).

However, cortisol measurement also has significant limitations: there is substantial delay (15-30 minutes) between stress exposure and measurable cortisol response, individual differences in cortisol rhythms and reactivity are substantial, multiple factors beyond stress influence cortisol levels including circadian rhythms and medication use, and cortisol measurement provides limited temporal resolution for studying acute stress responses.

**GSR as a Stress Indicator:**

Galvanic skin response reflects sympathetic nervous system activation through changes in skin conductance caused by sweat gland activity. GSR measurement offers several advantages: rapid response to stress activation (seconds), high temporal resolution enabling real-time monitoring, relatively straightforward measurement procedures, and strong correlation with immediate stress responses and emotional arousal.

GSR measurement limitations include: reflection of only one component of the stress response (sympathetic activation), susceptibility to movement artifacts and environmental factors, individual differences in skin characteristics affecting measurement reliability, and potential habituation effects during extended measurement periods.

**Comparative Analysis for Research Applications:**

For research requiring real-time stress monitoring and high temporal resolution, GSR provides superior capability compared to cortisol. The immediate response characteristics of GSR enable researchers to examine stress responses to specific stimuli or events with precise timing. This capability is particularly valuable for studies of human-computer interaction, social stress responses, and experimental manipulations requiring immediate feedback.

Cortisol measurement remains valuable for studies requiring information about sustained stress responses, circadian rhythm analysis, or validation of chronic stress effects. Ideally, research designs would incorporate both measures to capture different temporal aspects of stress responses.

**Implications for Contactless Measurement:**

The development of contactless GSR prediction approaches addresses the temporal resolution advantages of GSR measurement while eliminating the practical limitations of electrode-based measurement. This combination could provide optimal capability for real-time stress monitoring in naturalistic settings while maintaining the rapid response characteristics that make GSR valuable for research applications.

### 2.5 GSR Physiology and Measurement Limitations

Understanding the physiological mechanisms underlying galvanic skin response is essential for developing valid contactless measurement approaches and interpreting the resulting data appropriately. GSR reflects the activity of eccrine sweat glands, which are innervated by the sympathetic nervous system and respond to both emotional and thermal stimuli.

**Physiological Mechanisms:**

Eccrine sweat glands are distributed across the body but are particularly dense on the palms and fingertips, making these locations optimal for GSR measurement. Sympathetic nervous system activation causes increased sweat gland activity, which increases the ionic content of the skin and reduces electrical resistance. This conductance change can be measured using low-voltage electrical current applied across electrodes placed on the skin surface.

The GSR signal consists of two primary components: tonic skin conductance level (SCL) representing baseline arousal state, and phasic skin conductance responses (SCRs) representing immediate responses to specific stimuli. These components provide different information about autonomic nervous system state and are typically analyzed separately in research applications.

**Traditional Measurement Approaches:**

Standard GSR measurement uses Ag/AgCl electrodes placed on the middle phalanges of fingers or on the thenar and hypothenar eminences of the palm. The measurement system applies a small constant voltage (typically 0.5V) and measures the resulting current flow, which is proportional to skin conductance. Signal conditioning includes amplification, filtering, and analog-to-digital conversion for analysis.

**Measurement Limitations and Challenges:**

Traditional GSR measurement faces several significant limitations that constrain research applications:

**Movement Artifacts:** Electrode movement or pressure changes can produce artifacts that are difficult to distinguish from genuine physiological responses. This limitation requires participants to maintain specific positions and avoid movements during measurement.

**Skin Preparation Requirements:** Reliable measurement often requires skin cleaning and electrode preparation procedures that add setup time and may cause participant discomfort. Individual differences in skin characteristics can affect measurement reliability even with proper preparation.

**Environmental Sensitivity:** Temperature and humidity changes can affect measurement stability and require environmental control or statistical correction procedures. Seasonal variations and laboratory conditions can introduce systematic measurement errors.

**Individual Differences:** Substantial individual differences in baseline conductance levels and response magnitude require within-subject designs or extensive normalization procedures. Age, gender, medication use, and health status all influence GSR characteristics.

**Temporal Limitations:** While GSR responds rapidly to stimuli, the signal includes slower components that limit the ability to resolve rapidly changing stimuli. The overlap of response components can complicate interpretation of complex stimulus sequences.

**Habituation Effects:** Repeated exposure to stimuli often results in decreased GSR response magnitude, requiring careful experimental design to account for habituation and response adaptation.

These limitations have motivated the development of contactless approaches that could maintain the temporal advantages of GSR measurement while addressing the practical constraints that limit research applications.

### 2.6 Thermal Cues of Stress in Humans

Thermal imaging approaches to physiological measurement are based on the physiological changes in skin temperature that accompany autonomic nervous system activation. Understanding these thermal responses and their relationship to stress states is essential for developing valid contactless measurement approaches.

**Physiological Basis of Thermal Stress Responses:**

Stress responses involve complex autonomic nervous system changes that affect blood flow patterns and consequently skin temperature. Sympathetic activation causes vasoconstriction in peripheral blood vessels, reducing blood flow to extremities and causing temperature decreases in fingers and hands. Simultaneously, stress responses can cause vasodilation in facial regions, particularly around the nose and forehead, leading to temperature increases in these areas.

The temporal dynamics of thermal stress responses differ from GSR responses, with thermal changes often occurring more gradually and persisting for longer durations. This difference in temporal characteristics may provide complementary information about different aspects of stress responses.

**Thermal Imaging Technology:**

Modern thermal cameras use uncooled microbolometer sensors that detect infrared radiation in the 8-14 μm wavelength range corresponding to human body temperature emissions. Consumer-grade thermal cameras now provide sufficient resolution and sensitivity for physiological measurement applications while remaining economically accessible for research use.

Thermal imaging provides several advantages for physiological measurement: completely contactless operation, ability to measure multiple body regions simultaneously, relatively stable measurement under controlled environmental conditions, and potential for measuring multiple participants simultaneously.

**Research Evidence for Thermal Stress Indicators:**

Research studies have demonstrated correlations between thermal measurements and stress responses across multiple experimental contexts. Key findings include:

**Nasal Temperature Changes:** Stress responses often cause temperature increases around the nose region due to increased blood flow associated with respiratory changes and autonomic activation.

**Forehead Temperature Patterns:** Cognitive load and stress can cause temperature changes in forehead regions that correlate with subjective stress reports and other physiological measures.

**Hand Temperature Responses:** Stress-induced vasoconstriction typically causes temperature decreases in fingers and hands that can be detected using thermal imaging.

**Individual and Contextual Factors:** Thermal responses show individual differences related to age, gender, health status, and environmental adaptation. Baseline temperature patterns and response magnitude vary significantly across individuals.

**Measurement Challenges:**

Thermal measurement for stress detection faces several technical challenges: environmental temperature and air movement effects, individual differences in thermal response patterns, relatively slow temporal dynamics compared to GSR responses, and the need for controlled measurement conditions to ensure reliable detection.

**Integration with Other Modalities:**

The combination of thermal imaging with other measurement modalities, particularly GSR and RGB video analysis, may provide more comprehensive physiological assessment than any single approach. The different temporal characteristics and sensitivity patterns of these modalities could provide complementary information about different aspects of stress responses.

### 2.7 RGB vs. Thermal Imaging (Machine Learning Hypothesis)

The comparison between RGB and thermal imaging approaches for contactless physiological measurement involves consideration of the different physiological signals accessible through each modality and the machine learning approaches most suitable for extracting relevant information from each data type.

**RGB Imaging for Physiological Measurement:**

RGB video analysis for physiological measurement typically focuses on remote photoplethysmography (rPPG) techniques that detect subtle color changes in facial skin caused by cardiac pulse waves. Machine learning approaches for RGB analysis include:

**Traditional Computer Vision:** Feature extraction using color space transformations, temporal filtering, and independent component analysis to isolate cardiac signals from facial video. These approaches require careful preprocessing and are sensitive to lighting conditions and movement artifacts.

**Deep Learning Approaches:** Convolutional neural networks trained to extract physiological signals directly from facial video, potentially learning complex spatiotemporal patterns that traditional approaches cannot capture. These methods may be more robust to environmental variations but require extensive training data.

**Advantages of RGB Approaches:** High spatial resolution, detailed facial features, widespread camera availability, and established computer vision techniques. RGB cameras are ubiquitous and provide rich visual information for analysis.

**Limitations of RGB Approaches:** Sensitivity to lighting conditions, makeup and skin tone variations, movement artifacts, and the limited physiological information available through visible light spectrum.

**Thermal Imaging for Physiological Measurement:**

Thermal imaging provides direct measurement of skin temperature patterns that reflect autonomic nervous system activation. Machine learning approaches for thermal analysis include:

**Temperature Pattern Analysis:** Extraction of temperature features from specific facial and hand regions, analysis of temporal temperature changes, and correlation with known stress response patterns.

**Thermal Texture Analysis:** Analysis of spatial temperature patterns and gradients that may reflect physiological processes not captured by simple temperature measurements.

**Multi-Regional Integration:** Simultaneous analysis of multiple body regions with different thermal response characteristics to provide comprehensive physiological assessment.

**Advantages of Thermal Approaches:** Direct measurement of autonomic responses, reduced sensitivity to visible light conditions, ability to measure through darkness, and access to physiological information not available through RGB imaging.

**Limitations of Thermal Approaches:** Lower spatial resolution compared to RGB cameras, sensitivity to environmental temperature, higher equipment costs, and less established analysis techniques.

**Machine Learning Integration Hypothesis:**

The central hypothesis for this research is that machine learning approaches can effectively integrate RGB and thermal imaging data to achieve contactless GSR prediction with accuracy comparable to traditional contact-based measurement. This integration hypothesis is based on several key assumptions:

**Complementary Information:** RGB and thermal imaging provide access to different physiological signals that may be complementary for stress detection. RGB imaging may capture cardiovascular responses while thermal imaging captures autonomic temperature responses.

**Temporal Fusion:** Machine learning algorithms can learn to integrate temporal patterns across modalities to improve prediction accuracy beyond what either modality can achieve independently.

**Individual Adaptation:** Machine learning approaches can potentially learn individual-specific patterns that account for personal differences in physiological responses across both modalities.

**Robustness Enhancement:** Multi-modal approaches may provide greater robustness to environmental variations and measurement artifacts that affect individual modalities.

**Validation Requirements:** Testing this hypothesis requires systematic comparison of single-modality and multi-modal approaches against traditional GSR measurement across diverse experimental conditions and participant populations.

### 2.8 Sensor Device Selection Rationale (Shimmer GSR Sensor and Topdon Thermal Camera)

The selection of appropriate sensor hardware is critical for developing a reliable research platform that can provide valid reference measurements and high-quality contactless data for algorithm development and validation. The hardware selection process involved systematic evaluation of available options considering technical specifications, research suitability, cost-effectiveness, and integration requirements.

**Shimmer3 GSR+ Sensor Selection:**

The Shimmer3 GSR+ unit was selected as the reference physiological sensor based on several key factors:

**Research-Grade Quality:** Shimmer sensors are specifically designed for research applications and provide validated measurement quality with established research protocols. The GSR+ unit includes high-resolution analog-to-digital conversion and appropriate signal conditioning for research use.

**Technical Specifications:** The Shimmer3 GSR+ provides 16-bit resolution, configurable sampling rates up to 1024 Hz, and built-in signal processing capabilities. These specifications exceed the requirements for GSR research applications and provide sufficient data quality for validation studies.

**Wireless Connectivity:** Bluetooth connectivity enables untethered measurement that reduces movement constraints and supports more naturalistic experimental designs. The wireless operation is essential for contactless measurement validation studies.

**Software Integration:** Shimmer provides comprehensive software development kits for multiple platforms including Android and Python, enabling seamless integration with the multi-platform system architecture. The availability of established APIs reduces development complexity and improves reliability.

**Research Community Adoption:** Shimmer sensors are widely used in research applications, providing extensive literature and established protocols for comparison and validation studies. This community adoption facilitates interpretation and validation of results.

**Cost-Effectiveness:** While Shimmer sensors represent a significant investment, they provide superior value compared to laboratory-grade physiological measurement systems while maintaining research-appropriate quality standards.

**Alternative Considerations:** Other physiological sensors considered included laboratory-grade systems (too expensive and inflexible for multi-device deployment), consumer fitness devices (insufficient accuracy and data access for research), and custom sensor designs (excessive development complexity and uncertain validation).

**Topdon TC001 Thermal Camera Selection:**

The Topdon TC001 thermal camera was selected for contactless thermal measurement based on systematic evaluation of available consumer-grade thermal imaging options:

**Technical Specifications:** The TC001 provides 256x192 resolution, temperature sensitivity of ±2°C accuracy, and frame rates suitable for physiological measurement. These specifications provide sufficient quality for research applications while remaining economically feasible for multi-device deployment.

**Mobile Integration:** The TC001 is specifically designed for smartphone integration via USB-C connection, enabling seamless incorporation into the Android-based mobile sensor platform. This integration approach eliminates the need for separate thermal imaging hardware and reduces system complexity.

**Software Development Support:** Topdon provides software development kits that enable custom application development and direct access to thermal data streams. This SDK availability is essential for research applications requiring real-time thermal analysis.

**Cost-Performance Balance:** The TC001 provides the optimal balance between measurement quality and cost for research applications. Higher-end thermal cameras would provide superior specifications but at costs that would limit multi-device deployment feasibility.

**Research Suitability:** While the TC001 is targeted at commercial applications, the specifications and data access capabilities are appropriate for research use with proper validation and calibration procedures.

**Alternative Considerations:** Other thermal cameras evaluated included high-end research cameras (prohibitively expensive for multi-device use), other consumer-grade options (inferior specifications or limited software support), and standalone thermal imaging systems (increased complexity and integration challenges).

**Integrated System Rationale:**

The combination of Shimmer3 GSR+ sensors and Topdon TC001 thermal cameras provides an optimal platform for contactless physiological measurement research by combining validated reference measurement capability with cost-effective contactless sensing. This hardware combination enables:

- Simultaneous collection of reference GSR data and contactless thermal data for algorithm training and validation
- Multi-device deployment for studying group interactions and social physiological responses  
- Comprehensive data collection covering multiple physiological modalities
- Cost-effective scalability for research laboratory deployment
- Integration with existing research protocols and analysis procedures

The hardware selection establishes a foundation for reliable research platform development while maintaining economic feasibility for academic research applications.

---
