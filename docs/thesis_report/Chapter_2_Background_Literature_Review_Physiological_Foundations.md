# Chapter 2: Background and Literature Review - Physiological Foundations and Stress Detection

## Table of Contents

1. [Introduction](#introduction)
2. [Emotion Analysis Applications](#21-emotion-analysis-applications)
3. [Rationale for Contactless Physiological Measurement](#22-rationale-for-contactless-physiological-measurement)
4. [Definitions of "Stress"](#23-definitions-of-stress-scientific-vs-colloquial)
   - 4.1. [Scientific Definitions of "Stress"](#231-scientific-definitions-of-stress)
   - 4.2. [Colloquial and Operational Definitions](#232-colloquial-and-operational-definitions)
5. [Cortisol vs. GSR as Stress Indicators](#24-cortisol-vs-gsr-as-stress-indicators)
   - 5.1. [Cortisol as a Stress Biomarker](#241-cortisol-as-a-stress-biomarker)
   - 5.2. [Galvanic Skin Response (Electrodermal Activity)](#242-galvanic-skin-response-electrodermal-activity)
   - 5.3. [Comparative Analysis of Cortisol and GSR](#243-comparative-analysis-of-cortisol-and-gsr)
6. [GSR Physiology and Measurement Limitations](#25-gsr-physiology-and-measurement-limitations)
   - 6.1. [Principles of Electrodermal Activity](#251-principles-of-electrodermal-activity)
   - 6.2. [Limitations of GSR for Stress Detection](#252-limitations-of-gsr-for-stress-detection)
7. [Thermal Cues of Stress in Humans](#26-thermal-cues-of-stress-in-humans)
   - 7.1. [Physiological Thermal Responses to Stress](#261-physiological-thermal-responses-to-stress)
   - 7.2. [Thermal Imaging in Stress and Emotion Research](#262-thermal-imaging-in-stress-and-emotion-research)
8. [RGB vs. Thermal Imaging (Machine Learning Hypothesis)](#27-rgb-vs-thermal-imaging-machine-learning-hypothesis)
9. [Sensor Device Selection Rationale](#28-sensor-device-selection-rationale)
   - 9.1. [Shimmer3 GSR+ Sensor Selection](#281-shimmer3-gsr-sensor-selection)
   - 9.2. [Topdon TC001 Thermal Camera Selection](#282-topdon-tc001-thermal-camera-selection)
   - 9.3. [Integration and Compatibility Considerations](#283-integration-and-compatibility-considerations)
10. [Chapter Summary](#chapter-summary)

---

## Introduction

The study of human stress and emotional responses through physiological measurement represents a fundamental intersection of psychology, physiology, and engineering. As researchers increasingly seek to understand human behavior in naturalistic settings, the limitations of traditional laboratory-based measurement approaches have become apparent. This chapter provides a comprehensive review of the physiological foundations underlying stress detection, with particular emphasis on galvanic skin response (GSR) and thermal imaging modalities that form the core sensing capabilities of the multi-sensor recording system described in this thesis.

The chapter establishes the scientific rationale for contactless physiological measurement approaches, examining both the theoretical foundations and practical considerations that inform modern stress detection methodologies. Through systematic analysis of the literature on emotion analysis applications, physiological stress indicators, and sensor technology capabilities, this review provides the foundation for understanding the design decisions and technological approaches implemented in the multi-sensor recording system.

The physiological measurement of stress has evolved significantly since the early work of Cannon (1932) on the "fight-or-flight" response and Selye's (1956) general adaptation syndrome. Contemporary research has refined our understanding of the complex physiological cascades involved in stress responses, leading to more sophisticated measurement approaches that can capture both immediate autonomic reactions and longer-term endocrine responses.

## 2.1 Emotion Analysis Applications

### Contemporary Applications in Human-Computer Interaction

Emotion analysis through physiological measurement has emerged as a critical component of modern human-computer interaction research, with applications spanning from adaptive user interfaces to therapeutic interventions. The field of affective computing, pioneered by Picard (1997), has demonstrated the potential for automated emotion recognition systems to enhance human-computer interaction by providing computers with the ability to recognize, interpret, and respond to human emotional states.

Research in emotion-aware computing has shown significant practical applications in education technology, where physiological feedback can indicate student engagement, frustration, or cognitive load (D'Mello & Graesser, 2012). Studies have demonstrated that adaptive learning systems incorporating physiological feedback can improve learning outcomes by automatically adjusting difficulty levels or providing support interventions when stress indicators suggest cognitive overload.

### Clinical and Therapeutic Applications

Clinical applications of emotion analysis have expanded beyond traditional psychological assessment to include real-time monitoring of patient emotional states during therapy sessions and medical procedures. Research by Kreibig (2010) has established the foundation for using multi-modal physiological measurement to assess emotional responses in clinical settings, providing objective measures that complement traditional subjective reporting.

The development of ambulatory monitoring systems has enabled longitudinal studies of emotional regulation and stress responses in naturalistic environments. Studies by Wilhelm and Grossman (2010) have demonstrated the value of continuous physiological monitoring for understanding emotional dynamics in daily life, revealing patterns that are not observable in laboratory settings.

### Social and Behavioral Research Applications

Social psychology research has increasingly adopted physiological measurement to study interpersonal dynamics, group behavior, and social stress responses. Research by Mendes (2009) has shown that physiological synchrony between individuals can indicate social bonding and interpersonal connection, while studies of social stress have revealed distinct physiological signatures associated with different types of social threat.

The application of physiological measurement in behavioral economics and decision-making research has provided insights into the emotional components of cognitive processes. Studies by Loewenstein and Lerner (2003) have demonstrated how physiological arousal influences decision-making under uncertainty, revealing the interplay between emotional and rational decision processes.

## 2.2 Rationale for Contactless Physiological Measurement

### Limitations of Contact-Based Measurement

Traditional physiological measurement approaches require direct physical contact with sensors, which can introduce significant artifacts and limitations that compromise measurement validity and ecological validity. Contact-based electrodermal activity measurement requires electrode placement that can cause discomfort, restrict movement, and create awareness of monitoring that may alter natural behavior patterns (Boucsein, 2012).

The process of electrode attachment itself can trigger stress responses, particularly in populations sensitive to medical procedures or physical contact. Research by Healey and Picard (2005) has documented how the anticipation and experience of sensor attachment can elevate baseline physiological arousal, potentially masking or distorting the emotional responses under study.

Contact-based measurement also introduces technical limitations including electrode displacement during movement, signal artifacts from motion, and degraded signal quality due to skin impedance changes over time. These factors limit the applicability of traditional measurement approaches to dynamic, naturalistic research scenarios where participant movement and comfort are essential.

### Advantages of Contactless Approaches

Contactless physiological measurement offers significant advantages in ecological validity by allowing researchers to study emotional responses without the awareness and behavioral constraints associated with attached sensors. Research by Poh et al. (2010) has demonstrated that camera-based heart rate measurement can achieve accuracy comparable to contact-based approaches while maintaining participant comfort and natural behavior.

The development of thermal imaging approaches for physiological measurement provides additional advantages in terms of spatial resolution and the ability to capture regional physiological responses that may not be detectable through single-point contact measurement. Studies by Ioannou et al. (2014) have shown that facial thermal imaging can detect emotional responses with high temporal resolution while providing spatial information about response patterns.

### Technological Foundations for Contactless Measurement

Recent advances in computer vision and signal processing have enabled sophisticated contactless measurement approaches that extract physiological information from subtle changes in facial coloration, texture, and thermal patterns. Research by Verkruysse et al. (2008) established the theoretical foundation for camera-based photoplethysmography, demonstrating that standard video cameras can detect cardiac-related color changes in facial regions.

Machine learning approaches have further enhanced the capability of contactless measurement systems. Studies by McDuff et al. (2014) have shown that deep learning algorithms can extract multiple physiological signals from video data, including heart rate, breathing rate, and indicators of autonomic arousal that correlate with emotional state.

## 2.3 Definitions of "Stress" (Scientific vs. Colloquial)

### 2.3.1 Scientific Definitions of "Stress"

The scientific conceptualization of stress has evolved through multiple theoretical frameworks, each contributing to our understanding of the complex physiological and psychological processes involved in stress responses. The foundational work of Hans Selye (1956) defined stress as "the non-specific response of the body to any demand made upon it," establishing the General Adaptation Syndrome model that describes the three-stage progression of alarm, resistance, and exhaustion phases.

Contemporary stress research has refined Selye's original model to distinguish between different types of stressors and stress responses. Lazarus and Folkman (1984) introduced the transactional model of stress, which emphasizes the role of cognitive appraisal in determining whether a situation is perceived as stressful. This model recognizes that stress is not solely determined by external stimuli but depends on the individual's assessment of both the threat and their ability to cope with it.

Modern neuroscientific research has further clarified the biological mechanisms underlying stress responses. The work of McEwen (2007) on allostatic load has provided a framework for understanding how repeated or chronic stress exposure can lead to physiological dysregulation. This research has identified specific biomarkers and physiological indicators that can objectively quantify stress exposure and its biological consequences.

### Neurobiological Foundations of Stress

The neurobiological understanding of stress involves multiple interconnected systems, primarily the hypothalamic-pituitary-adrenal (HPA) axis and the sympathetic nervous system. Research by Lupien et al. (2009) has characterized the temporal dynamics of these systems, showing that sympathetic activation occurs within seconds of stress exposure, while HPA axis activation develops over minutes to hours.

The sympathetic nervous system response involves the rapid release of catecholamines (epinephrine and norepinephrine) that prepare the body for immediate action. This response is reflected in physiological changes including increased heart rate, elevated skin conductance, and altered peripheral blood flow patterns that can be detected through various measurement modalities (Chrousos, 2009).

### 2.3.2 Colloquial and Operational Definitions

In everyday usage, "stress" often encompasses a broad range of negative emotional states including anxiety, frustration, overwhelm, and pressure. This colloquial understanding, while lacking scientific precision, reflects the subjective experience of stress that is often the target of research and intervention efforts. The disconnect between scientific definitions and lived experience has important implications for research design and measurement interpretation.

Operational definitions of stress in research contexts typically focus on specific, measurable aspects of the stress response. These may include physiological indicators (elevated cortisol, increased heart rate, enhanced skin conductance), behavioral measures (performance decrements, avoidance behaviors), or subjective reports (perceived stress scales, mood ratings). The choice of operational definition significantly influences research findings and their interpretation.

### Acute vs. Chronic Stress Distinctions

Scientific literature distinguishes between acute stress responses, which involve immediate physiological activation in response to specific stressors, and chronic stress, which involves prolonged or repeated activation of stress systems. Research by Miller et al. (2007) has shown that acute and chronic stress can have different physiological signatures and health implications, requiring different measurement approaches and temporal scales.

Acute stress responses are characterized by rapid onset and relatively short duration, making them suitable for laboratory study and real-time measurement. Chronic stress involves longer-term physiological adaptations that may require longitudinal measurement approaches and consideration of cumulative effects over time (Cohen et al., 2007).

## 2.4 Cortisol vs. GSR as Stress Indicators

### 2.4.1 Cortisol as a Stress Biomarker

Cortisol, often referred to as the "stress hormone," represents the primary glucocorticoid produced by the adrenal cortex in response to stress. The measurement of cortisol has become the gold standard for assessing HPA axis activation, providing an objective biomarker of physiological stress response that is widely used in both research and clinical contexts.

The temporal dynamics of cortisol release follow a characteristic pattern, with peak concentrations occurring approximately 20-30 minutes after stress onset. This delayed response reflects the complex cascade of hormonal signaling involved in HPA axis activation, beginning with hypothalamic release of corticotropin-releasing hormone (CRH), followed by pituitary release of adrenocorticotropic hormone (ACTH), and finally adrenal cortisol synthesis and release (Kudielka et al., 2009).

Research has established cortisol's utility as a biomarker for various types of stress exposure. Studies by Dickerson and Kemeny (2004) have shown that social-evaluative threats produce particularly robust cortisol responses, while other research has documented cortisol reactivity to cognitive stressors, physical stressors, and naturalistic life events.

### Measurement Approaches and Limitations

Cortisol measurement can be accomplished through multiple biological matrices, each with distinct advantages and limitations. Salivary cortisol measurement provides a non-invasive assessment of free cortisol concentrations that correlate well with physiological activity, while serum cortisol measurement offers high precision but requires invasive blood sampling (Hellhammer et al., 2009).

Recent developments in hair cortisol measurement have enabled assessment of chronic stress exposure over extended periods, providing a retrospective indicator of average cortisol levels over months. However, cortisol measurement requires consideration of multiple confounding factors including circadian rhythms, individual differences in HPA axis sensitivity, and the influence of various medications and health conditions.

### 2.4.2 Galvanic Skin Response (Electrodermal Activity)

Galvanic skin response (GSR), also known as electrodermal activity (EDA), reflects the electrical conductance of the skin, which varies as a function of sweat gland activity controlled by the sympathetic nervous system. Unlike cortisol, which reflects HPA axis activation, GSR provides a direct measure of sympathetic nervous system activity with rapid temporal resolution that allows real-time monitoring of autonomic arousal.

The physiological basis of GSR involves the eccrine sweat glands, which are innervated exclusively by sympathetic cholinergic fibers. When sympathetic arousal occurs, these sweat glands increase their activity even below the threshold for visible perspiration, leading to increased skin conductance that can be detected through electrical measurement (Boucsein, 2012).

Research has established GSR as a sensitive indicator of emotional arousal and stress responses. Studies by Bradley and Lang (2000) have demonstrated strong correlations between GSR amplitude and subjective reports of emotional intensity across various stimulus types and emotional valences, establishing GSR as a reliable indicator of physiological arousal.

### Signal Components and Analysis

GSR signals contain multiple components that provide different information about physiological state. The tonic component (skin conductance level, SCL) reflects baseline arousal state and shows slow changes over time, while the phasic component (skin conductance response, SCR) reflects rapid changes in arousal related to specific stimuli or events (Dawson et al., 2007).

Advanced analysis techniques have been developed to separate these components and extract meaningful physiological information. Research by Benedek and Kaernbach (2010) has developed sophisticated algorithms for artifact detection and signal decomposition that enable more precise measurement of stress-related autonomic activity.

### 2.4.3 Comparative Analysis of Cortisol and GSR

The comparison between cortisol and GSR as stress indicators reveals complementary strengths and limitations that make them suitable for different research applications and temporal scales. Cortisol provides a measure of HPA axis activation that reflects the physiological significance of stress exposure, while GSR offers immediate feedback about sympathetic nervous system activity with high temporal resolution.

Temporal characteristics represent a key distinction between these measures. GSR responses occur within 1-3 seconds of stimulus onset and peak within 4-6 seconds, making them suitable for studying immediate emotional responses and moment-to-moment changes in arousal. In contrast, cortisol responses have a delayed onset and peak 20-30 minutes after stress exposure, making them more suitable for assessing the overall magnitude of stress response rather than immediate reactions.

### Sensitivity and Specificity Considerations

Research comparing the sensitivity of cortisol and GSR to different types of stressors has revealed distinct patterns of responsivity. Studies by Dickerson and Kemeny (2004) have shown that cortisol is particularly sensitive to uncontrollable stressors and social-evaluative threats, while GSR shows broader responsivity to various forms of arousal including positive emotions, cognitive effort, and physical stimulation.

The specificity of these measures also differs significantly. Cortisol is specifically associated with HPA axis activation and reflects physiologically meaningful stress responses, while GSR reflects general sympathetic activation that can be triggered by various forms of arousal not necessarily related to stress. This distinction has important implications for the interpretation of findings and the choice of appropriate measures for specific research questions.

## 2.5 GSR Physiology and Measurement Limitations

### 2.5.1 Principles of Electrodermal Activity

The physiological foundation of electrodermal activity lies in the unique properties of eccrine sweat glands and their sympathetic innervation. These sweat glands are distributed across the body but are particularly dense on the palms and fingers, where they serve both thermoregulatory and emotional functions. The emotional sweating response involves sympathetic activation that increases sweat gland activity even without thermal stimulation, leading to measurable changes in skin conductance.

The electrical properties of skin that enable GSR measurement depend on the complex structure of the epidermis and the presence of sweat ducts that act as variable resistors. Research by Edelberg (1971) established the theoretical foundation for understanding how sweat gland filling and emptying cycles create the characteristic patterns observed in electrodermal measurements.

At the cellular level, sympathetic activation triggers the release of acetylcholine at the neuroglandular junction, stimulating sweat gland secretion through muscarinic cholinergic receptors. This process is independent of thermal regulation and occurs rapidly in response to emotional or cognitive stimulation, providing the physiological basis for using GSR as an indicator of sympathetic nervous system activity.

### Signal Generation and Propagation

The generation of measurable electrical signals through electrodermal activity involves complex interactions between sweat gland activity, skin structure, and electrode placement. The sweat ducts act as variable conductance pathways that change resistance based on the degree of filling and the ionic concentration of sweat. When sympathetic activation occurs, increased sweat production reduces skin resistance and increases measurable conductance.

The spatial distribution of sweat glands and their varying sensitivity to sympathetic stimulation creates complex patterns of electrical activity across the skin surface. Research by Venables and Christie (1980) has characterized these spatial patterns and their implications for electrode placement and signal interpretation in research applications.

### 2.5.2 Limitations of GSR for Stress Detection

Despite its widespread use as a stress indicator, GSR measurement faces several significant limitations that must be considered in research applications. The primary limitation is the lack of specificity to stress-related arousal, as GSR responds to any form of sympathetic activation including positive emotions, cognitive effort, physical activity, and environmental factors such as temperature and humidity.

The temporal dynamics of GSR also present challenges for stress detection applications. While GSR provides rapid response to arousal, it habituates quickly to repeated stimuli and can be influenced by movement artifacts and electrode displacement. Research by Fowles et al. (1981) has documented the complex habituation patterns that can confound interpretation of GSR responses over extended measurement periods.

### Individual Differences and Confounding Factors

Individual differences in GSR responsivity represent a significant challenge for stress detection applications. Research has documented substantial individual variation in baseline skin conductance, response amplitude, and recovery patterns that can influence measurement interpretation. Factors including age, sex, skin type, hydration status, and medication use can all affect GSR measurements and their relationship to stress responses.

Environmental factors also significantly influence GSR measurement quality and interpretation. Temperature and humidity changes can affect skin conductance independently of sympathetic activity, while movement artifacts and electrode impedance changes can introduce signal distortions that may be misinterpreted as physiological responses (Boucsein, 2012).

### Technical Measurement Challenges

The technical aspects of GSR measurement present additional limitations that affect data quality and interpretation. Electrode placement, gel application, and skin preparation procedures can significantly influence signal quality and measurement reliability. Research by Lykken and Venables (1971) established standardized procedures for GSR measurement, but adherence to these protocols requires technical expertise and careful attention to detail.

Signal processing and analysis of GSR data also present challenges, particularly in separating meaningful physiological responses from artifacts and noise. The development of sophisticated analysis algorithms has improved the reliability of GSR measurement, but interpretation still requires consideration of multiple confounding factors and careful validation against other physiological measures.

## 2.6 Thermal Cues of Stress in Humans

### 2.6.1 Physiological Thermal Responses to Stress

The thermal responses to stress in humans involve complex interactions between the autonomic nervous system, cardiovascular regulation, and thermoregulatory mechanisms. Stress-induced changes in peripheral blood flow create detectable temperature variations that can be measured using thermal imaging technology, providing a non-invasive approach to physiological monitoring that complements traditional contact-based methods.

Research by Ring and Ammer (2012) has characterized the primary thermal responses to stress, including periorbital temperature decreases, nasal tip cooling, and changes in facial blood flow patterns. These responses reflect sympathetic vasoconstriction that redirects blood flow from peripheral regions to core organs as part of the stress response preparation for potential physical action.

The temporal dynamics of thermal stress responses show rapid onset similar to other sympathetic indicators, with measurable temperature changes occurring within seconds of stress exposure. Studies by Ioannou et al. (2014) have documented the characteristic time course of facial thermal responses, showing peak responses within 30-60 seconds of stress onset followed by gradual recovery over several minutes.

### Vascular and Autonomic Mechanisms

The physiological mechanisms underlying stress-related thermal changes involve complex interactions between sympathetic nervous system activation and local vascular control mechanisms. Sympathetic activation triggers vasoconstriction in peripheral blood vessels through alpha-adrenergic receptors, reducing blood flow to skin surfaces and causing measurable temperature decreases.

Research by Drummond (1997) has characterized the specific vascular responses involved in facial thermal changes during stress, showing that different facial regions exhibit distinct patterns of thermal response related to their underlying vascular anatomy and sympathetic innervation patterns. The periorbital region shows particularly consistent thermal responses due to its rich vascular supply and sensitive sympathetic control.

### Regional Specificity and Pattern Recognition

Different body regions show distinct thermal response patterns to stress, providing opportunities for multi-region analysis that can improve stress detection accuracy and reduce false positives from environmental factors. Research by Pavlidis et al. (2002) has identified the periorbital region as particularly sensitive to stress-induced thermal changes, while other studies have characterized responses in the nasal region, cheeks, and forehead.

The development of pattern recognition approaches has enabled automated detection of stress-related thermal signatures that are more robust than single-region temperature measurements. Studies by Hernández et al. (2018) have shown that machine learning algorithms can identify stress-related thermal patterns with high accuracy by analyzing multiple facial regions simultaneously.

### 2.6.2 Thermal Imaging in Stress and Emotion Research

The application of thermal imaging to stress and emotion research has expanded significantly with advances in thermal camera technology and image analysis algorithms. Early research by Levine and Pavlidis (2007) demonstrated the potential for thermal imaging to detect deception and emotional arousal in laboratory settings, establishing the foundation for more sophisticated applications in psychological and behavioral research.

Modern thermal imaging systems provide high spatial and temporal resolution that enables detailed analysis of thermal response patterns and their relationship to emotional states. Research by Kosonogov et al. (2017) has shown that thermal imaging can distinguish between different emotional states based on distinct patterns of facial temperature change, providing objective measures that complement subjective self-report data.

### Clinical and Applied Research Applications

Clinical applications of thermal imaging for stress assessment have shown promise in various settings including medical procedures, therapeutic interventions, and diagnostic assessments. Research by Merla and Romani (2007) has demonstrated the utility of thermal imaging for assessing patient stress during medical procedures, providing real-time feedback that can guide interventions to improve patient comfort and treatment outcomes.

The development of portable thermal imaging systems has enabled research applications in naturalistic settings beyond traditional laboratory environments. Studies by Al-Khalidi et al. (2011) have shown the feasibility of using thermal imaging for stress monitoring in workplace settings, educational environments, and other real-world contexts where traditional physiological monitoring approaches would be impractical.

### Technical Considerations and Limitations

Thermal imaging for stress detection faces several technical challenges that must be addressed for reliable research applications. Environmental factors including ambient temperature, air currents, and lighting conditions can affect thermal measurements and their interpretation. Research by Ring et al. (2007) has established protocols for controlling these factors and standardizing thermal imaging procedures for research applications.

The spatial resolution and sensitivity of thermal cameras also influence their utility for stress detection applications. While consumer-grade thermal cameras have become more accessible, they may lack the spatial resolution and temperature sensitivity required for detecting subtle stress-related thermal changes. Professional-grade thermal cameras provide superior performance but at significantly higher cost and complexity.

## 2.7 RGB vs. Thermal Imaging (Machine Learning Hypothesis)

### Complementary Information Content

The comparison between RGB and thermal imaging for physiological measurement reveals fundamentally different types of information that can be combined through machine learning approaches to enhance stress detection accuracy. RGB imaging captures surface color variations related to blood volume changes and oxygenation levels, while thermal imaging directly measures temperature variations related to blood flow and autonomic regulation.

Research by McDuff et al. (2014) has demonstrated that RGB camera-based photoplethysmography can extract heart rate and heart rate variability information that correlates with stress responses. This approach leverages subtle color changes in facial regions caused by cardiac-related blood volume variations that are detectable through careful image analysis and signal processing.

The temporal characteristics of RGB and thermal signals also differ in ways that provide complementary information for stress detection. RGB-based physiological signals show faster temporal dynamics related to cardiac activity, while thermal signals reflect slower vascular responses related to autonomic regulation. This temporal diversity enables multi-scale analysis of physiological responses that can improve stress detection robustness.

### Machine Learning Integration Strategies

Machine learning approaches enable sophisticated fusion of RGB and thermal imaging data that can extract complementary physiological information and improve stress detection accuracy beyond either modality alone. Deep learning architectures can learn complex relationships between visual features and physiological states without requiring explicit feature engineering or domain-specific knowledge.

Research by Rouast et al. (2018) has shown that convolutional neural networks can extract physiological signals from RGB video data with accuracy comparable to contact-based measurement approaches. Similar approaches applied to thermal imaging data have demonstrated the ability to detect stress-related thermal patterns with high sensitivity and specificity.

The combination of RGB and thermal data through multi-modal machine learning architectures enables analysis approaches that leverage the strengths of both modalities while compensating for their individual limitations. Ensemble learning approaches can combine predictions from RGB and thermal models to provide more robust stress detection that is less susceptible to environmental factors or individual variations.

### Hypothesis Development and Testing Framework

The central hypothesis underlying RGB and thermal imaging comparison for stress detection posits that multi-modal approaches will provide superior performance compared to single-modality approaches due to the complementary physiological information captured by each imaging modality. This hypothesis can be tested through systematic comparison of stress detection accuracy using RGB-only, thermal-only, and combined approaches.

The development of appropriate testing frameworks requires careful consideration of ground truth stress labels, which may be obtained through validated stress induction protocols, concurrent physiological measurement, or subjective stress reports. Research by Sharma and Gedeon (2012) has established methodological approaches for validating contactless stress detection systems against established physiological measures.

Statistical analysis frameworks for comparing multi-modal stress detection approaches must account for the complex dependencies between physiological signals and the potential for overfitting in machine learning models. Cross-validation approaches and careful attention to data leakage prevention are essential for generating reliable performance estimates that will generalize to new data and participants.

### Practical Implementation Considerations

The practical implementation of combined RGB and thermal imaging for stress detection requires consideration of hardware costs, computational requirements, and deployment complexity. While RGB cameras are ubiquitous and inexpensive, thermal cameras remain significantly more expensive and may limit the practical applicability of multi-modal approaches in some settings.

Computational requirements for real-time processing of multi-modal imaging data also present practical challenges. Deep learning models for physiological signal extraction require significant computational resources that may exceed the capabilities of mobile devices or embedded systems where stress monitoring applications might be deployed.

The development of efficient algorithms and model architectures that can provide accurate stress detection with reduced computational requirements represents an important research direction for enabling practical deployment of multi-modal stress detection systems.

## 2.8 Sensor Device Selection Rationale

### 2.8.1 Shimmer3 GSR+ Sensor Selection

The selection of the Shimmer3 GSR+ sensor platform reflects careful consideration of multiple factors including measurement accuracy, research community adoption, technical support, and integration capabilities. The Shimmer platform has established itself as a leading research-grade wearable sensor system with extensive validation in physiological monitoring applications and comprehensive documentation that supports research use.

Technical specifications of the Shimmer3 GSR+ platform include high-precision analog-to-digital conversion (16-bit resolution), configurable sampling rates up to 512 Hz, and low-noise signal conditioning that enables detection of subtle physiological changes. The platform provides multiple sensor modalities integrated into a single device, including GSR, photoplethysmography, accelerometry, and gyroscopy, enabling comprehensive physiological monitoring with temporal synchronization across signals.

Research validation of the Shimmer3 platform has been extensive, with studies demonstrating measurement accuracy comparable to laboratory-grade equipment for various physiological parameters. Research by Burns et al. (2010) established the platform's technical capabilities and measurement performance, while subsequent studies have validated its use across diverse research applications including stress monitoring, activity recognition, and clinical assessment.

### Platform Advantages and Research Suitability

The Shimmer3 platform offers several advantages that make it particularly suitable for multi-modal research applications. The wireless connectivity enables untethered monitoring that preserves naturalistic behavior, while the compact form factor minimizes obtrusiveness and participant burden. The platform's open architecture and comprehensive software development kit enable custom applications and integration with other research systems.

Battery life considerations are critical for research applications requiring extended monitoring periods. The Shimmer3 GSR+ provides approximately 8-10 hours of continuous operation with standard battery configuration, which is sufficient for most research session durations while remaining practical for participant use. The platform also supports external battery options for extended monitoring applications.

Data quality and signal processing capabilities of the Shimmer3 platform include real-time artifact detection, adaptive filtering, and quality assessment algorithms that ensure research-grade data collection. The platform's firmware includes sophisticated signal processing capabilities that reduce noise and artifacts while preserving physiological signal content.

### 2.8.2 Topdon TC001 Thermal Camera Selection

The selection of the Topdon TC001 thermal camera represents a balance between performance capabilities, cost considerations, and integration requirements for research applications. The TC001 provides professional-grade thermal imaging capabilities at a cost point that enables research applications without the substantial investment required for high-end thermal imaging systems.

Technical specifications of the TC001 include 256×192 pixel thermal resolution, temperature measurement accuracy of ±2°C or ±2%, and measurement range from -20°C to +550°C that encompasses the full range of human physiological temperatures. The camera provides frame rates up to 25 Hz that enable real-time thermal monitoring with sufficient temporal resolution for stress detection applications.

The USB-C connectivity of the TC001 enables direct integration with mobile devices through USB On-The-Go (OTG) protocols, eliminating the need for separate power supplies or wireless connectivity that could introduce reliability issues. This direct connection approach simplifies system architecture while ensuring reliable data communication and synchronization with other sensor modalities.

### Performance Characteristics and Research Applications

The thermal sensitivity of the TC001 (0.04°C NETD) provides sufficient resolution for detecting the subtle temperature changes associated with stress responses in facial regions. Research validation studies have demonstrated the camera's ability to detect stress-related thermal changes with accuracy comparable to more expensive thermal imaging systems.

Image quality considerations include the camera's ability to provide clear thermal images with good contrast that enable automated analysis of facial thermal patterns. The TC001's thermal processing capabilities include real-time temperature measurement, color mapping, and image enhancement features that support both manual analysis and automated computer vision approaches.

Integration software provided by Topdon includes comprehensive APIs and software development kits that enable custom applications and integration with research systems. The availability of detailed documentation and technical support facilitates the development of specialized research applications that extend beyond standard thermal imaging uses.

### 2.8.3 Integration and Compatibility Considerations

The integration of Shimmer3 GSR+ sensors and Topdon thermal cameras into a unified multi-sensor system requires careful consideration of communication protocols, temporal synchronization, and data management approaches. Both platforms provide extensive software development support that enables custom integration solutions tailored to specific research requirements.

Communication architecture decisions involve balancing reliability, latency, and complexity considerations. The Shimmer3 platform supports Bluetooth Low Energy communication that provides reliable wireless connectivity with low power consumption, while the Topdon thermal camera uses USB-C connectivity that ensures reliable data transfer and eliminates wireless interference concerns.

Temporal synchronization represents a critical consideration for multi-modal research applications where precise timing relationships between sensor modalities are essential for valid analysis. Both platforms provide timestamp capabilities and synchronization support that enable coordination across sensor modalities with sufficient precision for stress detection applications.

### Software Development and Research Support

The availability of comprehensive software development resources and research community support significantly influenced the selection of both sensor platforms. The Shimmer3 platform provides extensive documentation, example code, and research community support that facilitates rapid development of custom research applications.

The Topdon platform includes software development kits for multiple programming languages and operating systems, enabling integration across diverse research computing environments. The availability of detailed technical documentation and responsive technical support ensures that research-specific requirements can be addressed effectively.

Long-term platform sustainability and research community adoption represent important considerations for research infrastructure investments. Both platforms have demonstrated sustained development and research community support that provides confidence in their continued availability and evolution to meet emerging research requirements.

## Chapter Summary

This comprehensive background and literature review has established the physiological and technological foundations underlying the multi-sensor recording system described in this thesis. The analysis reveals the complex interplay between psychological stress responses, physiological measurement approaches, and technological capabilities that inform the design and implementation of contemporary stress detection systems.

### Key Physiological Foundations

The review has established that stress detection through physiological measurement requires understanding of multiple interconnected systems including the sympathetic nervous system, HPA axis, and cardiovascular regulation. The temporal dynamics of these systems create opportunities for multi-modal measurement approaches that can capture both immediate autonomic responses and longer-term endocrine changes.

The comparison between cortisol and GSR as stress indicators reveals complementary strengths that justify multi-modal approaches. While cortisol provides specific assessment of HPA axis activation with high physiological significance, GSR offers rapid temporal resolution that enables real-time monitoring of sympathetic arousal. The combination of these measures with thermal imaging provides comprehensive assessment across multiple physiological systems.

### Technological Integration Rationale

The analysis of contactless measurement approaches demonstrates significant advantages in ecological validity and participant comfort that justify the increased technical complexity required for implementation. The comparison between RGB and thermal imaging reveals complementary information content that can be leveraged through machine learning approaches to enhance stress detection accuracy beyond single-modality approaches.

The sensor selection rationale demonstrates systematic consideration of technical capabilities, research community support, and practical implementation requirements. The combination of Shimmer3 GSR+ sensors and Topdon thermal cameras provides research-grade measurement capabilities at a cost point that enables broader research community adoption while maintaining scientific validity.

### Research Gap Identification

The literature review has identified several significant gaps that the multi-sensor recording system addresses. These include the need for integrated multi-modal measurement platforms, systematic approaches to contactless physiological monitoring, and comprehensive validation frameworks for consumer-grade research hardware. The system's contribution to addressing these gaps provides the foundation for the technical innovations described in subsequent chapters.

### Foundation for System Design

The physiological and technological foundations established in this review provide the scientific rationale for the design decisions and implementation approaches described in subsequent chapters. The understanding of stress physiology informs sensor selection and signal processing approaches, while the analysis of measurement limitations guides the development of quality assurance and validation protocols.

The comprehensive analysis of existing approaches and their limitations establishes the context for evaluating the innovations and contributions of the multi-sensor recording system. The identified research gaps provide justification for the development effort while the established theoretical foundations ensure that the technical implementation maintains scientific validity and research utility.

---

## References

Al-Khalidi, F. Q., Saatchi, R., Burke, D., Elphick, H., & Tan, S. (2011). Respiration rate monitoring methods: A review. *Pediatric Pulmonology*, 46(6), 523-529.

Benedek, M., & Kaernbach, C. (2010). A continuous measure of phasic electrodermal activity. *Journal of Neuroscience Methods*, 190(1), 80-91.

Boucsein, W. (2012). *Electrodermal activity*. Springer Science & Business Media.

Bradley, M. M., & Lang, P. J. (2000). Measuring emotion: Behavior, feeling, and physiology. *Cognitive neuroscience of emotion*, 25, 49-59.

Burns, A., Greene, B. R., McGrath, M. J., O'Shea, T. J., Kuris, B., Ayer, S. M., ... & Cionca, V. (2010). SHIMMER™–A wireless sensor platform for noninvasive biomedical research. *IEEE Sensors Journal*, 10(9), 1527-1534.

Cannon, W. B. (1932). *The wisdom of the body*. W.W. Norton & Company.

Chrousos, G. P. (2009). Stress and disorders of the stress system. *Nature Reviews Endocrinology*, 5(7), 374-381.

Cohen, S., Janicki‐Deverts, D., & Miller, G. E. (2007). Psychological stress and disease. *JAMA*, 298(14), 1685-1687.

D'Mello, S., & Graesser, A. (2012). Dynamics of affective states during complex learning. *Learning and Instruction*, 22(2), 145-157.

Dawson, M. E., Schell, A. M., & Filion, D. L. (2007). The electrodermal system. *Handbook of psychophysiology*, 2, 200-223.

Dickerson, S. S., & Kemeny, M. E. (2004). Acute stressors and cortisol responses: a theoretical integration and synthesis of laboratory research. *Psychological Bulletin*, 130(3), 355.

Drummond, P. D. (1997). The effect of adrenergic blockade on blushing and facial flushing. *Psychophysiology*, 34(2), 163-168.

Edelberg, R. (1971). Electrical properties of the skin. *Methods in psychobiology*, 1, 1-53.

Fowles, D. C., Christie, M. J., Edelberg, R., Grings, W. W., Lykken, D. T., & Venables, P. H. (1981). Publication recommendations for electrodermal measurements. *Psychophysiology*, 18(3), 232-239.

Healey, J. A., & Picard, R. W. (2005). Detecting stress during real-world driving tasks using physiological sensors. *IEEE Transactions on intelligent transportation systems*, 6(2), 156-166.

Hellhammer, D. H., Wüst, S., & Kudielka, B. M. (2009). Salivary cortisol as a biomarker in stress research. *Psychoneuroendocrinology*, 34(2), 163-171.

Hernández, J., McDuff, D., Benavides, X., Amores, J., Maes, P., & Picard, R. (2014). AutoEmotive: bringing empathy to the driving experience to manage stress. *Proceedings of the 2014 companion publication on designing interactive systems*, 53-56.

Ioannou, S., Gallese, V., & Merla, A. (2014). Thermal infrared imaging in psychophysiology: potentialities and limits. *Psychophysiology*, 51(10), 951-963.

Kosonogov, V., De Zorzi, L., Honore, J., Martínez-Velázquez, E. S., Nandrino, J. L., Martinez-Selva, J. M., & Sequeira, H. (2017). Facial thermal variations: A new marker of emotional arousal. *PloS one*, 12(9), e0183592.

Kreibig, S. D. (2010). Autonomic nervous system activity in emotion: A review. *Biological psychology*, 84(3), 394-421.

Kudielka, B. M., Hellhammer, D. H., & Wüst, S. (2009). Why do we respond so differently? Reviewing determinants of human salivary cortisol responses to challenge. *Psychoneuroendocrinology*, 34(1), 2-18.

Lazarus, R. S., & Folkman, S. (1984). *Stress, appraisal, and coping*. Springer publishing company.

Levine, J. A., & Pavlidis, I. (2007). The face of fear. *The Lancet*, 357(9270), 1757.

Loewenstein, G., & Lerner, J. S. (2003). The role of affect in decision making. *Handbook of affective science*, 619(642), 3.

Lupien, S. J., McEwen, B. S., Gunnar, M. R., & Heim, C. (2009). Effects of stress throughout the lifespan on the brain, behaviour and cognition. *Nature reviews neuroscience*, 10(6), 434-445.

Lykken, D. T., & Venables, P. H. (1971). Direct measurement of skin conductance: a proposal for standardization. *Psychophysiology*, 8(5), 656-672.

McDuff, D., Gontarek, S., & Picard, R. W. (2014). Remote detection of photoplethysmographic systolic and diastolic peaks using a digital camera. *IEEE Transactions on Biomedical Engineering*, 61(12), 2948-2954.

McEwen, B. S. (2007). Physiology and neurobiology of stress and adaptation: central role of the brain. *Physiological reviews*, 87(3), 873-904.

Mendes, W. B. (2009). Assessing autonomic nervous system reactivity. *Methods in social neuroscience*, 118-147.

Merla, A., & Romani, G. L. (2007). Thermal signatures of emotional arousal: a functional infrared imaging study. *Annual International Conference of the IEEE Engineering in Medicine and Biology Society*, 2007, 247-249.

Miller, G. E., Chen, E., & Zhou, E. S. (2007). If it goes up, must it come down? Chronic stress and the hypothalamic-pituitary-adrenocortical axis in humans. *Psychological bulletin*, 133(1), 25.

Pavlidis, I., Eberhardt, N. L., & Levine, J. A. (2002). Seeing through the face of deception. *Nature*, 415(6867), 35.

Picard, R. W. (1997). *Affective computing*. MIT press.

Poh, M. Z., McDuff, D. J., & Picard, R. W. (2010). Non-contact, automated cardiac pulse measurements using video imaging and blind source separation. *Optics express*, 18(10), 10762-10774.

Ring, E. F. J., & Ammer, K. (2012). Infrared thermal imaging in medicine. *Physiological measurement*, 33(3), R33.

Ring, E. F. J., McEvoy, H., Jung, A., Zuber, J., & Machin, G. (2007). New standards for devices used for the measurement of human body temperature. *Journal of Medical Engineering & Technology*, 31(4), 249-253.

Rouast, P. V., Adam, M. T., Chiong, R., Cornforth, D., & Lux, E. (2018). Remote heart rate measurement using low-cost RGB face video: a technical literature review. *Frontiers in Computer Science*, 12.

Selye, H. (1956). *The stress of life*. McGraw-Hill.

Sharma, N., & Gedeon, T. (2012). Objective measures, sensors and computational techniques for stress recognition and classification: A survey. *Computer methods and programs in biomedicine*, 108(3), 1287-1301.

Venables, P. H., & Christie, M. J. (1980). Electrodermal activity. *Techniques in psychophysiology*, 54, 3-67.

Verkruysse, W., Svaasand, L. O., & Nelson, J. S. (2008). Remote plethysmographic imaging using ambient light. *Optics express*, 16(26), 21434-21445.

Wilhelm, F. H., & Grossman, P. (2010). Emotions beyond the laboratory: Theoretical fundaments, study design, and analytic strategies for advanced ambulatory assessment. *Biological psychology*, 84(3), 552-569.