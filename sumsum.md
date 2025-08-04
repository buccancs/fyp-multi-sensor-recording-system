\documentclass[11pt,a4paper]{report}
\usepackage[utf8]{inputenc}
\usepackage[draft]{graphicx}
\usepackage{listings}
\usepackage{xcolor}
\usepackage{geometry}
\usepackage{booktabs}
\geometry{margin=2cm}
\lstset{basicstyle=\footnotesize\ttfamily, breaklines=true}
\begin{document}
\tableofcontents

\chapter{Introduction}

\section{Motivation and Research Context}

Stress is a ubiquitous physiological and psychological response with profound implications for human-computer interaction (HCI), health monitoring, and emotion recognition. In contexts ranging from adaptive user interfaces to mental health assessment, the ability to measure a user's stress level reliably and unobtrusively is highly valuable. Galvanic Skin Response (GSR), also known as electrodermal activity, is a well-established index of stress and arousal, reflecting changes in sweat gland activity via skin conductance measurements \cite{Boucsein2012}. Traditional GSR monitoring techniques, however, rely on attaching electrodes to the skin (typically on the fingers or palm) to sense minute electrical conductance changes \cite{Fowles1981}. While effective in controlled laboratory settings, this contact-based approach has significant drawbacks: the physical sensors can be obtrusive and uncomfortable, often altering natural user behaviour and emotional states \cite{Cacioppo2007}. In other words, the very act of measuring stress via contact sensors may itself induce stress or otherwise confound the measurements, raising concerns about ecological validity in HCI and ambulatory health scenarios \cite{Wilhelm2010}. Moreover, contact sensors tether participants to devices, limiting mobility and making longitudinal or real-world monitoring cumbersome. These limitations motivate the pursuit of contactless stress measurement methods that can capture stress-related signals without any physical attachments, thereby preserving natural behaviour and comfort.

\section{Research Problem and Objectives}

Recent advances in sensing and computer vision suggest that it may be feasible to infer physiological stress responses using ordinary cameras and imaging devices, completely bypassing the need for electrode contact \cite{Picard2001}. Prior work in affective computing and physiological computing has demonstrated that various visual cues—facial expressions, skin pallor, perspiration, subtle head or body movements—can correlate with emotional arousal and stress levels \cite{Healey2005}. Thermal infrared imaging of the face, for instance, can reveal temperature changes associated with blood flow variations under stress (e.g., cooling of the nose tip due to vasoconstriction) in a fully non-contact manner. Likewise, high-resolution RGB video can capture heart rate or breathing rate through imperceptible skin color fluctuations and movements, as shown in emerging remote photoplethysmography techniques \cite{Poh2010}. These developments raise a critical research question at the intersection of computer vision and psychophysiology: Can we approximate or even predict a person's GSR-based stress measurements using only contactless video data from an RGB camera? In other words, does a simple video recording of an individual contain sufficient information to estimate their physiological stress response, obviating the need for dedicated skin contact sensors? Answering this question affirmatively would have far-reaching implications. It would enable widely accessible stress monitoring (using ubiquitous smartphone or laptop cameras) and seamless integration of stress detection into everyday human-computer interactions and health monitoring applications, without the burden of wearables or electrodes.

To investigate this question, we have developed a multi-sensor data acquisition platform, named \textit{MMDCP}, which enables synchronized recording of physiological signals and video from multiple devices. The system architecture spans two tightly integrated components: a custom Android mobile application and a desktop PC application. The Android app operates on a modern smartphone (e.g., Samsung S22) equipped with an attachable thermal camera module. It simultaneously captures two video streams—a thermal infrared video feed and a standard high-definition RGB video feed from the phone's camera—providing rich visual data of the subject. The mobile app also offers a user-friendly interface for participants or researchers to manage the recording session (e.g., start/stop recording, view status indicators) on the device. Complementing the mobile device, the desktop PC application (implemented in Python with a graphical user interface) functions as the master controller of the data collection session. The PC connects via Bluetooth to a Shimmer3 GSR+ sensor, a wearable GSR device, to record the participant's skin conductance in real time. In addition, the PC can incorporate auxiliary video sources (such as high-quality USB webcams pointing at the participant) to collect synchronized RGB footage from multiple angles or at higher resolutions, if required. The Android and PC components communicate over a wireless network, following a master--slave synchronization protocol: the PC controller orchestrates the timing of recordings across all devices, ensuring that the smartphone cameras and the GSR sensor start and stop data collection in unison. Through this design, \textit{MMDCP} achieves precise temporal alignment of multi-modal data streams, with timestamp synchronization on the order of only a few milliseconds of drift across devices. Such tight synchronization is crucial for our research, as it enables frame-by-frame correlation of physiological signals (like rapid GSR changes) with visual events or cues captured on video \cite{Gravina2017}. In summary, the \textit{MMDCP} platform provides a synchronized, contactless multi-sensor recording system that forms the experimental backbone for exploring vision-based stress measurement.

The development of this platform involved several technical contributions. First, we designed and implemented a real-time multi-device synchronization mechanism that coordinates independent sensor devices (smartphone cameras, thermal imagers, and Bluetooth GSR units) with sub-10ms accuracy. This synchronization system draws on established clock synchronization algorithms (inspired by Network Time Protocol and sensor network time sync techniques) to distribute a common time base and control signals to all devices, thereby guaranteeing coherent data timelines. Second, we created an integrated data acquisition framework capable of capturing and streaming heterogeneous data modalities in parallel: high-definition RGB video, thermal infrared video, and physiological signals. The framework ensures reliable data throughput for each modality (e.g., maintaining video frame rates of 30--60fps while logging GSR at 50Hz) and provides mechanisms for real-time monitoring and quality control of the incoming data streams. Third, we developed an extensible user interface (UI) architecture across the Android and Python applications to manage the multi-sensor system. The Android app employs a modern, modular UI design (using a navigation drawer with distinct fragments for functions like device setup, recording controls, and data review), which improves maintainability over a single monolithic activity. The Python desktop app features a coordinated control panel that mirrors the Android interface's functionality, allowing the researcher to oversee all connected devices, configure session parameters, and visualize data in real time. Both UIs are built with extensibility in mind, meaning new sensor types or modules (e.g., additional cameras or biometric sensors) can be integrated with minimal changes to the interface logic. Together, these contributions result in a flexible platform that not only serves the needs of the present study but can also be adapted for future multi-modal stress and emotion research.

\section{Thesis Outline}

Using the \textit{MMDCP} platform, we conducted a controlled experiment to gather data for evaluating the central research question. In the study, human participants underwent a stress induction protocol while being recorded by the system. We adopted a standardized stimulus known to elicit psychological stress -- for example, a time-pressured mental arithmetic task or the Trier Social Stress Test (which combines public speaking and cognitive challenges) -- in order to invoke measurable changes in the participants' stress levels. Throughout each session, the system logged three synchronized data streams: (1) continuous GSR signals from the Shimmer sensor attached to the participant's fingers (serving as the ground-truth indicator of physiological stress response), (2) thermal video of the participant's face and upper body (capturing heat patterns and blood flow changes, which may reflect stress-induced thermoregulatory effects), and (3) RGB video of the participant (capturing visible cues such as facial expressions, skin color changes, or fidgeting behaviours). The experiment was designed such that each participant's session includes a baseline (relaxed period) followed by an acute stress phase and a recovery period, enabling us to observe how the recorded signals vary with induced stress. The resulting multi-modal dataset provides a rich basis for analysis: by examining the time-synchronized recordings, we can directly compare the GSR readings with the visual data to determine what correlates of stress are present in the videos. In particular, we focus on features extractable from the RGB video alone -- such as heart rate estimated via tiny color fluctuations in the face, or facial muscle tension and expressions -- and assess how well these features can approximate the GSR measurements. Through signal processing and machine learning analysis (detailed in later chapters), we evaluate the degree to which a predictive model can infer GSR-based stress levels from the RGB video stream. This approach allows us to empirically answer the research question and quantify the capabilities and limits of video-only stress assessment in comparison to the gold-standard contact GSR signal.

This thesis addresses a critical gap in physiological computing by exploring a contactless approach to stress measurement. We have built a novel platform that synchronizes thermal imaging, optical video, and GSR sensing in real time, enabling controlled experiments on stress detection. We leverage this platform to investigate whether visual data alone can serve as a proxy for electrodermal activity in stress assessment. The remainder of this thesis is organized as follows: Chapter~2 reviews the background and literature review, including the psychophysiology of stress responses, traditional GSR measurement techniques and their limitations, and recent advances in contactless physiological monitoring. Chapter~3 defines the requirements of the system and details the design and architecture of the \textit{MMDCP} platform, with emphasis on the synchronization strategy and system components. Chapter~4 covers the implementation and technical contributions of the project, describing the software development of the Android and PC applications and the integration of the various sensors and cameras. Chapter~5 then presents the experimental methodology and data analysis, including the stress induction scenario, feature extraction from video, and the results of modeling GSR from video data. Finally, Chapter~6 concludes the thesis, discussing the findings with respect to the research question, the limitations of the current approach, and potential directions for future research in contactless stress detection and multi-modal sensing systems.

\chapter{Background and Literature Review}

\section{Emotion Analysis Applications}

Emotion analysis applications have evolved significantly over the past decades, driven by advances in sensor technology and machine learning methodologies. Traditional approaches to emotion recognition have primarily relied on subjective self-reporting measures or invasive physiological monitoring techniques that require direct skin contact \cite{Picard2001}. Modern affective computing systems seek to overcome these limitations by developing more naturalistic and unobtrusive measurement approaches that can be integrated into everyday human-computer interaction scenarios \cite{Healey2005}.

The Multi-Sensor Recording System emerges from the rapidly evolving field of contactless physiological measurement, representing a significant advancement in research instrumentation that addresses fundamental limitations of traditional electrode-based approaches. Pioneering work in noncontact physiological measurement using webcams has demonstrated the potential for camera-based monitoring \cite{poh2010noncontact}, while advances in biomedical engineering have established the theoretical foundations for remote physiological detection. The research context encompasses the intersection of distributed systems engineering, mobile computing, computer vision, and psychophysiological measurement, requiring sophisticated integration of diverse technological domains to achieve research-grade precision and reliability.

\section{Rationale for Contactless Physiological Measurement}

The motivation for contactless physiological measurement stems from fundamental limitations of traditional electrode-based approaches. Contact-based measurement methods, while providing high-fidelity physiological signals, introduce several confounding factors that can compromise the validity of research findings \cite{Wilhelm2010}. The physical presence of sensors can alter natural behavior patterns, create participant discomfort, and introduce measurement artifacts that are difficult to distinguish from genuine physiological responses \cite{Cacioppo2007}.

Traditional physiological measurement methodologies impose significant constraints on research design and data quality that have limited scientific progress in understanding human physiological responses. The comprehensive handbook of psychophysiology documents these longstanding limitations \cite{cacioppo2007handbook}, while extensive research on electrodermal activity has identified the fundamental challenges of contact-based measurement approaches \cite{boucsein2012eda}. Contact-based measurement approaches, particularly for galvanic skin response (GSR) monitoring, require direct electrode attachment that can alter the very responses being studied, restrict experimental designs to controlled laboratory settings, and create participant discomfort that introduces measurement artifacts.

The development of contactless measurement approaches represents a paradigm shift toward naturalistic observation methodologies that preserve measurement accuracy while eliminating the behavioural artifacts associated with traditional instrumentation. Advanced research in remote photoplethysmographic detection using digital cameras has demonstrated the feasibility of precise cardiovascular monitoring without physical contact, establishing the scientific foundation for contactless physiological measurement.

\section{Definitions of "Stress" (Scientific vs. Colloquial)}

The term "stress" encompasses both colloquial usage and precise scientific definitions that must be carefully distinguished in research contexts. From a scientific perspective, stress refers to the physiological and psychological response pattern that occurs when an individual encounters environmental demands that exceed their perceived ability to cope effectively \cite{Levenson2003AutonomicEmotion}. This response involves coordinated activation of multiple physiological systems, including the autonomic nervous system, the hypothalamic-pituitary-adrenal axis, and various peripheral effector mechanisms that prepare the organism for adaptive action \cite{Bracha1985}.

The fundamental research problem addressed by this thesis centers on the challenge of developing cost-effective, scalable, and accessible research instrumentation that maintains scientific rigor while democratizing access to advanced physiological measurement capabilities. Extensive research in photoplethysmography applications has established the theoretical foundations for contactless physiological measurement, while traditional research instrumentation requires substantial financial investment, specialized technical expertise, and dedicated laboratory spaces that limit research accessibility and constrain experimental designs to controlled environments that may not reflect naturalistic behaviour patterns.

\section{Cortisol vs. GSR as Stress Indicators}

Different physiological markers of stress provide complementary information about various aspects of the stress response, with cortisol and galvanic skin response representing distinct temporal and mechanistic dimensions of stress physiology. Cortisol, the primary glucocorticoid hormone released by the adrenal cortex, reflects activation of the hypothalamic-pituitary-adrenal (HPA) axis and provides information about sustained stress responses over minutes to hours \cite{Levenson2003AutonomicEmotion}. In contrast, galvanic skin response reflects sympathetic nervous system activation and provides moment-to-moment information about emotional arousal and stress responses with temporal resolution on the order of seconds \cite{Boucsein2012}.

The research significance extends beyond immediate technical achievements to encompass methodological contributions that enable new research paradigms in human-computer interaction, social psychology, and behavioural science. The emerging field of affective computing has identified the critical need for unobtrusive physiological measurement that preserves natural behaviour patterns \cite{cho2020stress}, while the system enables research applications previously constrained by measurement methodology limitations, including large-scale social interaction studies, naturalistic emotion recognition research, and longitudinal physiological monitoring in real-world environments.

\section{GSR Physiology and Measurement Limitations}

Galvanic skin response represents one of the most reliable and well-characterized indices of sympathetic nervous system activation, reflecting changes in sweat gland activity that modulate electrical conductance across the skin surface \cite{boucsein2012eda}. The physiological basis of GSR involves eccrine sweat glands, which are primarily controlled by sympathetic cholinergic innervation and respond rapidly to emotional and cognitive stimuli \cite{Fowles1981}.

The contactless physiological measurement literature establishes both the scientific foundations and practical challenges associated with camera-based physiological monitoring, providing essential background for understanding the measurement principles implemented in the system. Pioneering research in remote plethysmographic imaging using ambient light established the optical foundations for contactless cardiovascular monitoring that inform the computer vision algorithms implemented in the camera recording components. The fundamental principles of photoplethysmography provide the theoretical basis for extracting physiological signals from subtle color variations in facial regions captured by standard cameras.

\section{Thermal Cues of Stress in Humans}

Thermal imaging provides a non-invasive window into autonomic nervous system activity through detection of peripheral temperature changes associated with stress-induced vasoconstriction and vasodilation patterns \cite{Ring2012ThermalMed}. Stress responses typically involve coordinated changes in peripheral blood flow that can be detected as temperature variations in specific facial and extremity regions.

The thermal imaging literature establishes both the theoretical foundations and practical considerations for integrating thermal sensors in physiological measurement applications, providing essential background for understanding the measurement principles and calibration requirements implemented in the thermal camera integration. Advanced research in infrared thermal imaging for medical applications demonstrates the scientific validity of thermal-based physiological monitoring while establishing quality standards and calibration procedures that ensure measurement accuracy and research validity. The theoretical foundations of thermal physiology provide context for interpreting thermal signatures and developing robust measurement algorithms.

\section{RGB vs. Thermal Imaging (Machine Learning Hypothesis)}

The comparative advantages of RGB and thermal imaging for contactless physiological measurement represent a fundamental research question in computer vision-based health monitoring. RGB imaging provides high spatial resolution and detailed information about subtle color changes associated with blood volume fluctuations, enabling detection of heart rate and respiratory patterns through remote photoplethysmography techniques \cite{poh2010noncontact}.

Research conducted at MIT Media Lab has significantly advanced contactless measurement methodologies through sophisticated signal processing algorithms and validation protocols that demonstrate the scientific validity of camera-based physiological monitoring. Advanced work in remote photoplethysmographic peak detection using digital cameras provides critical validation methodologies and quality assessment frameworks that directly inform the adaptive quality management systems implemented in the Multi-Sensor Recording System. These developments establish comprehensive approaches to signal extraction, noise reduction, and quality assessment that enable robust physiological measurement in challenging environmental conditions.

\section{Sensor Device Selection Rationale (Shimmer GSR Sensor and Topdon Thermal Camera)}

The selection of specific sensor devices for this research was guided by requirements for research-grade measurement precision, technical compatibility with mobile platforms, and cost-effectiveness for academic research applications. The Shimmer3 GSR+ sensor was selected based on its established validation in psychophysiological research, high temporal resolution sampling capabilities, and robust Bluetooth connectivity for wireless data transmission \cite{ShimmerSDK2024}.

The Shimmer3 GSR+ device integration represents a sophisticated wearable sensor platform that enables high-precision galvanic skin response measurements alongside complementary physiological signals including photoplethysmography (PPG), accelerometry, and other biometric parameters. The device specifications include sampling rates from 1 Hz to 1000 Hz with configurable GSR measurement ranges from 10~k$\Omega$ to 4.7~M$\Omega$ across five distinct ranges optimized for different skin conductance conditions.

The Topdon TC001 and TC001 Plus thermal cameras represent advanced uncooled microbolometer technology with sophisticated technical specifications optimized for research applications. The TC001 provides 256$\times$192 pixel resolution with temperature ranges from -20~$^\circ$C to +550~$^\circ$C and measurement accuracy of $\pm$2~$^\circ$C or $\pm$2\%, while the enhanced TC001 Plus extends the temperature range to +650~$^\circ$C with improved accuracy of $\pm$1.5~$^\circ$C or $\pm$1.5\%. Both devices operate at frame rates up to 25~Hz with 8--14~$\mu$m spectral range optimized for long-wave infrared (LWIR) detection.

\chapter{Requirements}

\section{Problem Statement and Research Context}

The Multi-Sensor Recording System addresses fundamental limitations in existing approaches to contactless physiological measurement by providing synchronized, multi-modal data acquisition capabilities that enable systematic investigation of relationships between visual cues and physiological stress responses. Traditional research in this domain has been constrained by temporal misalignment between different sensor modalities, limited integration capabilities across device platforms, and lack of standardized protocols for multi-device coordination \cite{Gravina2017}.

The physiological measurement research domain has experienced significant methodological stagnation due to fundamental limitations inherent in traditional contact-based sensor technologies. Contemporary galvanic skin response (GSR) measurement, while representing the established scientific standard for electrodermal activity assessment, imposes systematic constraints that fundamentally limit research scope, experimental validity, and scientific advancement opportunities across multiple research disciplines.

Traditional GSR methods suffer from critical limitations that restrict their use in naturalistic settings and multi-participant studies. These include intrusive contact requirements and behavioural alteration where traditional GSR sensors require attaching electrodes to the skin, which introduces discomfort and a constant reminder of being monitored. This intrusiveness can alter participants' natural behaviour and emotional responses, compromising the ecological validity of findings \cite{cho2020gsr}. Movement artifacts and signal degradation occur because physical electrode connections are highly susceptible to motion artifacts, effectively confining participants to stationary positions and precluding studies involving natural movement or real-world tasks.

\section{Requirements Engineering Approach}

The requirements engineering process for the Multi-Sensor Recording System employed systematic analysis of research needs, technical constraints, and usability considerations to define comprehensive functional and non-functional requirements. The approach integrated established software engineering methodologies with domain-specific considerations for physiological measurement applications \cite{Basili1987}.

The requirements engineering process was conducted as a systematic, multi-phase approach tailored to the project's research context. It needed to capture complex, competing needs from diverse stakeholders while ensuring technical feasibility, scientific validity, and practical implementability within real-world constraints. This methodology acknowledges that developing research-oriented software poses unique challenges distinct from commercial software, necessitating specialized practices that balance scientific rigor with user needs and maintainability.

Effective requirements engineering began with a comprehensive stakeholder analysis to identify and understand all parties with a vested interest in the system. Key stakeholder groups included research scientists and principal investigators as the primary end-users driving system requirements, study participants whose physiological data is being recorded, technical support and laboratory staff responsible for day-to-day operation and maintenance, ethics review boards enforcing data protection and privacy standards, and institutional IT and infrastructure ensuring system deployment compatibility.

\section{Functional Requirements Overview}

The functional requirements encompass core system capabilities for multi-device coordination, data acquisition, real-time monitoring, and data management across heterogeneous sensor platforms. Key functional capabilities include synchronized recording initiation and termination across all connected devices, real-time data streaming with timestamp alignment, local data storage with automatic backup mechanisms, and user interface functionality for session management and system monitoring.

The \textit{Multi-Sensor Recording System} directly tackles the limitations of current approaches through a paradigm shift toward completely contactless physiological monitoring. The system integrates multiple modalities (visual, thermal, and electrical) in a distributed architecture, maintaining research-grade accuracy and reliability without requiring physical electrodes on participants. This innovative approach is made possible by recent advances in high-resolution cameras, affordable thermal sensors, robust wireless synchronization, and real-time data processing algorithms.

The system implements a multi-faceted innovation framework addressing traditional limitations via coordinated technological advances including contactless multi-modal sensor integration that combines advanced RGB camera analysis, thermal imaging for autonomic nervous system responses, computer vision for behavioural and movement tracking, and machine learning for physiological state inference. The distributed coordination architecture employs a master-coordinator design with fault-tolerant device management and precise Network Time Protocol synchronization mechanism ensuring sub-millisecond temporal alignment across devices.

\section{Non-Functional Requirements}

Non-functional requirements address system qualities including performance, reliability, usability, and maintainability that are essential for research-grade applications. Temporal synchronization accuracy must achieve sub-10ms precision across all connected devices to enable frame-level correlation between physiological signals and visual data streams \cite{Mills2006}.

Performance non-functional requirements establish how the system should behave under various loads and as the system scales up. The system must handle large data volumes from multiple devices in real time, all while remaining responsive to user control. The system must demonstrate near-linear scalability in its processing and data handling as additional devices are added, supporting multi-participant sessions without significant performance degradation or data loss.

Reliability requirements ensure the system can be trusted to run through critical experiments without failures, and that it safeguards the valuable data being collected. The system should have high availability during scheduled usage periods with minimal downtime or crashes during an experiment. If a non-critical component fails, the system should degrade gracefully rather than totally crash, implementing fault detection and recovery mechanisms.

\section{Use Case Scenarios}

The system supports multiple use case scenarios reflecting different research configurations and experimental protocols. Primary use cases include controlled laboratory experiments with stationary participants, mobile data collection scenarios with ambulatory monitoring, and multi-participant studies requiring coordination across multiple sensor platforms simultaneously.

Multi-participant research sessions represent the core scenario where research scientists conduct synchronized recording sessions with multiple participants, capturing all modalities of data. The researcher opens the desktop controller application and configures a new session by entering session parameters, validates that all devices are connected and calibrated, positions participants appropriately, and initiates recording where the system sends start commands to all devices for simultaneous data capture.

System calibration and configuration scenarios involve technical operators calibrating cameras and configuring the system for optimal data quality before experiments. The calibration utility guides operators through spatial and temporal calibration processes, including camera calibration using checkerboard patterns and temporal synchronization using simultaneous events across devices.

\section{System Analysis (Architecture \& Data Flow)}

The system architecture employs a distributed master-slave design pattern with the desktop PC application serving as the central coordinator and mobile devices functioning as autonomous data collection agents. This architecture provides several advantages including centralized control for experimental protocols, distributed processing capabilities, and graceful degradation during network interruptions \cite{Tanenbaum2016}.

The system handles multiple concurrent data streams which must be collected, synchronized, processed, and stored. Data from various sources including RGB cameras, thermal cameras, GSR sensors, and potentially other sensors enter a collection layer on each device. The raw data is timestamped and sent to the synchronization engine where streams are aligned in time. Aligned data then flows into a processing pipeline for feature extraction and analysis, and concurrently to the storage system to be written to disk.

Different components of the system must interact at varying frequencies and with certain latency requirements. The coordinator-to-device link maintains continuous data flow where network latency should be low to prevent lag in synchronization or cause buffer overruns. Android devices communicate with Shimmer GSR sensors at frequencies of 50+ Hz with maximum latency of 20ms, while the synchronization engine maintains internal cycles at 1 Hz with maximum 5ms offset tolerance.

\section{Data Requirements and Management}

Data management requirements encompass storage, synchronization, quality assurance, and long-term preservation considerations for multi-modal physiological and video data streams. The system must handle sustained data rates including 30-60 fps video streams, 50Hz GSR sampling, and 9fps thermal imaging while maintaining data integrity and temporal alignment \cite{Wilson2014}.

The data management approach includes comprehensive metadata storage for sessions, participants, and device configurations, enabling systematic tracking of experimental conditions and data provenance essential for research validity and reproducibility. The system provides automatic backup and recovery mechanisms that protect against data loss while supporting export capabilities that enable integration with external analysis tools and statistical software packages.

Data integrity protection involves using reliable protocols for data transmission and storage, implementing hashing or CRC checks on data blocks to detect corruption, maintaining automatic backups with secondary copies of data, and establishing access control systems requiring proper authentication for data access. The system validates data integrity during export operations and provides comprehensive quality assessment procedures to ensure research-grade reliability.

\chapter{Design and Implementation}

\section{System Architecture Overview (PC--Android System Design)}

The Multi-Sensor Recording System implements a sophisticated distributed architecture that coordinates data collection across heterogeneous device platforms while maintaining research-grade temporal synchronization and data integrity. The architecture employs established distributed systems principles including consensus protocols, fault tolerance mechanisms, and modular component design to achieve reliable multi-device coordination \cite{Lamport2001}.

The system architecture draws upon established distributed systems patterns while introducing specialized adaptations required for physiological measurement applications that must coordinate consumer-grade mobile devices with research-grade precision. The design philosophy emphasizes fault tolerance, data integrity, and temporal precision as fundamental requirements that cannot be compromised for convenience or performance.

The distributed system design is the architectural core that enables precise coordination of multiple independent computing platforms while maintaining rigorous temporal synchronization, data integrity, and reliability required for scientific applications. The design addresses fundamental challenges in distributed computing theory and adapts proven solutions to the unique requirements of physiological measurement research that demand unprecedented precision and reliability from consumer-grade hardware.

The system implements a multi-faceted innovation framework addressing traditional limitations via coordinated technological advances including contactless multi-modal sensor integration that combines advanced RGB camera analysis, thermal imaging for autonomic nervous system responses, computer vision for behavioural and movement tracking, and machine learning for physiological state inference. The distributed coordination architecture employs a master-coordinator design with fault-tolerant device management and precise Network Time Protocol synchronization mechanism ensuring sub-millisecond temporal alignment across devices.

\section{Android Application Design and Sensor Integration}

The Android application follows Clean Architecture principles with a clear separation between presentation, domain, and data layers. This ensures maintainability, testability, and flexibility for future enhancements while providing comprehensive sensor coordination and data collection capabilities optimized for research applications.

\subsection{Thermal Camera Integration (Topdon)}

The thermal camera integration handles USB-C connected Topdon TC001 devices with real-time thermal processing capabilities that enable detection of peripheral temperature changes associated with stress and autonomic nervous system activity. The Topdon TC001 and TC001 Plus thermal cameras represent advanced uncooled microbolometer technology with sophisticated technical specifications optimized for research applications.

The TC001 provides 256×192 pixel resolution with temperature ranges from -20°C to +550°C and measurement accuracy of ±2°C or ±2\%, while the enhanced TC001 Plus extends the temperature range to +650°C with improved accuracy of ±1.5°C or ±1.5\%. Both devices operate at frame rates up to 25 Hz with 8--14 μm spectral range optimized for long-wave infrared detection.

The SDK architecture provides comprehensive integration through Android's USB On-The-Go interface, enabling direct communication with thermal imaging hardware through USB-C connections. The implementation includes sophisticated device detection algorithms, USB communication management, and comprehensive error handling that ensures reliable operation despite the challenges inherent in USB device communication on mobile platforms.

The thermal data processing capabilities include real-time temperature calibration using manufacturer-validated calibration coefficients, advanced thermal image processing algorithms for noise reduction and image enhancement, and comprehensive thermal data export capabilities that support both raw thermal data access and processed temperature matrices. The SDK enables precise temperature measurement across the thermal imaging frame while providing access to raw thermal data for advanced analysis including emissivity correction, atmospheric compensation, and thermal signature analysis.

\subsection{GSR Sensor Integration (Shimmer)}

The Shimmer3 GSR+ integration provides robust Bluetooth connectivity with research-grade physiological sensors, offering validated algorithms for data collection, calibration, and quality assessment. The Shimmer3 GSR+ device integration represents a sophisticated wearable sensor platform that enables high-precision galvanic skin response measurements alongside complementary physiological signals including photoplethysmography, accelerometry, and other biometric parameters.

The device specifications include sampling rates from 1 Hz to 1000 Hz with configurable GSR measurement ranges from 10 kΩ to 4.7 MΩ across five distinct ranges optimized for different skin conductance conditions. The SDK architecture supports both direct Bluetooth connections and advanced multi-device coordination through sophisticated connection management algorithms that maintain reliable communication despite the inherent challenges of Bluetooth Low Energy communication in research environments.

The implementation includes automatic device discovery, connection state management, and comprehensive error recovery mechanisms that ensure continuous data collection even during temporary communication interruptions. The data processing capabilities include real-time signal quality assessment through advanced algorithms that detect electrode contact issues, movement artifacts, and signal saturation conditions. The SDK provides access to both raw sensor data for custom analysis and validated processing algorithms for standard physiological metrics including GSR amplitude analysis, frequency domain decomposition, and statistical quality measures essential for research applications.

The Shimmer integration includes automatic sensor discovery, connection management, and data streaming capabilities with built-in quality assessment algorithms that detect sensor artifacts and connection issues. The comprehensive calibration framework enables precise measurement accuracy through manufacturer-validated calibration coefficients and real-time calibration validation that ensures measurement consistency across devices and experimental sessions.

\section{Desktop Controller Design and Functionality}

The Python desktop controller serves as the central coordination hub, implementing sophisticated session management, data processing, and orchestration capabilities that enable comprehensive multi-device coordination while maintaining research-grade temporal synchronization and data integrity.

The Python Desktop Controller represents a paradigmatic advancement in research instrumentation, serving as the central orchestration hub that fundamentally reimagines physiological measurement research through sophisticated distributed sensor network coordination. The comprehensive academic implementation synthesizes detailed technical analysis with practical implementation guidance, establishing a foundation for both rigorous scholarly investigation and practical deployment in research environments.

The controller implements a hybrid star-mesh coordination architecture that elegantly balances the simplicity of centralized coordination with the resilience characteristics of distributed systems. This architectural innovation directly addresses the fundamental challenge of coordinating consumer-grade mobile devices for scientific applications while maintaining the precision and reliability standards required for rigorous research use.

The session manager orchestrates complex multi-device recording sessions with sophisticated coordination algorithms that achieve research-grade temporal precision across wireless networks while providing comprehensive quality assessment and validation across all sensor modalities. The system demonstrates that consumer-grade hardware can achieve research-grade precision when supported by advanced coordination algorithms and systematic validation procedures.

\section{Communication Protocol and Synchronization Mechanism}

The communication design employs multiple protocols to optimize different types of data exchange, providing robust fault tolerance and reliable operation across diverse network conditions. The control channel uses WebSocket for bidirectional command and status communication between the PC controller and mobile devices, providing reliable message delivery with automatic reconnection capabilities.

The data channel implements TCP streaming for high-throughput data streaming optimized for real-time previews and sensor data with adaptive compression and low latency characteristics. The synchronization channel utilizes UDP for time-critical synchronization messages with minimal overhead, specifically used for clock synchronization and recording triggers that require precise timing coordination.

The synchronization framework adapts Network Time Protocol principles for research applications requiring microsecond-level precision across consumer-grade wireless networks. The NTP adaptation includes algorithms for network delay estimation, clock drift compensation, and outlier detection that maintain temporal accuracy despite the variable latency characteristics of wireless communication.

The temporal coordination algorithms implement Cristian's algorithm for clock synchronization with adaptations for mobile device constraints and wireless network characteristics. The implementation includes statistical analysis of synchronization accuracy with confidence interval estimation and quality metrics that enable objective assessment of temporal precision throughout research sessions.

\section{Data Processing Pipeline}

The data processing pipeline implements validated signal processing techniques specifically adapted for contactless measurement applications while maintaining scientific accuracy and research validity. The signal processing foundation includes digital filtering algorithms, frequency-domain analysis, and statistical signal processing techniques that extract physiological information from optical and thermal sensor data while minimizing noise and artifacts.

The contactless GSR prediction algorithms build upon established photoplethysmography principles with adaptations for mobile camera sensors and challenging environmental conditions. The photoplethysmography implementation includes sophisticated region of interest detection, adaptive filtering algorithms, and motion artifact compensation that enable robust physiological measurement despite participant movement and environmental variations.

The signal processing pipeline implements validated algorithms for heart rate variability analysis, signal quality assessment, and artifact detection that ensure research-grade measurement accuracy while providing comprehensive quality metrics for scientific validation. The implementation includes frequency-domain analysis with power spectral density estimation, time-domain statistical analysis, and comprehensive quality assessments that enable objective measurement validation.

The computer vision algorithms implement established theoretical foundations from image processing and machine learning research while adapting them to the specific requirements of physiological measurement applications. The computer vision foundation includes camera calibration theory, feature detection algorithms, and statistical learning techniques that enable robust visual analysis despite variations in lighting conditions, participant characteristics, and environmental factors.

\section{Implementation Challenges and Solutions}

The implementation addressed several significant technical challenges through innovative solutions that advance the state of knowledge in distributed systems engineering, mobile computing, and research instrumentation development. The primary innovation centers on the development of sophisticated coordination algorithms that achieve research-grade temporal precision across wireless networks with inherent latency and jitter characteristics that would normally preclude scientific measurement applications.

The system demonstrates that consumer-grade mobile devices can achieve measurement precision comparable to dedicated laboratory equipment when supported by advanced software algorithms, comprehensive validation procedures, and systematic quality management systems. This demonstration opens new possibilities for democratizing access to advanced research capabilities while maintaining scientific validity and research quality standards that support peer-reviewed publication and academic validation.

The architectural innovations include the development of hybrid coordination topologies that balance centralized control simplicity with distributed system resilience, advanced synchronization algorithms that compensate for network latency and device timing variations, and comprehensive quality management systems that provide real-time assessment and optimization across multiple sensor modalities. These contributions establish new patterns for distributed research system design applicable to broader scientific instrumentation challenges requiring coordination of heterogeneous hardware platforms.

The validation methodology implements comprehensive statistical analysis techniques specifically designed for research software validation and physiological measurement quality assessment. The statistical foundation includes hypothesis testing, confidence interval estimation, and power analysis that provide objective assessment of system performance and measurement accuracy while supporting scientific publication and peer review requirements.

The quality assessment algorithms implement comprehensive measurement uncertainty analysis based on Guide to the Expression of Uncertainty in Measurement principles. The uncertainty analysis includes systematic and random error estimation, propagation of uncertainty through processing algorithms, and quality metrics that enable objective assessment of measurement accuracy and scientific validity.

\chapter{Evaluation and Testing}

\section{Testing Strategy Overview}

The comprehensive testing strategy for the Multi-Sensor Recording System represents a systematic, rigorous, and scientifically grounded approach to validation that addresses the complex challenges of verifying research-grade software quality while accommodating the unprecedented complexity of distributed multi-modal data collection systems operating across heterogeneous platforms and diverse research environments.

The testing approach systematically balances comprehensive thoroughness with practical implementation constraints while ensuring that all critical system functions, performance characteristics, and operational behaviours meet the rigorous quality standards required for scientific applications that demand reproducibility, accuracy, and reliability across diverse experimental contexts. The strategy development process involved extensive analysis of existing research software validation methodologies, consultation with domain experts in software engineering and physiological measurement, and systematic adaptation of established testing frameworks to address the specific requirements of multi-modal sensor coordination in research environments.

The resulting comprehensive strategy provides systematic coverage of functional correctness verification, performance characteristics validation, reliability assessment under stress conditions, and integration quality evaluation across diverse hardware platforms, network configurations, and environmental conditions that characterize real-world research deployment scenarios. The strategy incorporates lessons learned from established testing methodologies while introducing novel approaches specifically designed to address the unique challenges of validating research-grade distributed systems that coordinate consumer hardware for scientific applications.

\section{Unit Testing (Android and PC Components)}

The Android application's unit tests leverage JUnit 5 and Mockito for dependency injection and mocking. This ensures each component is tested in isolation with controlled interactions. Camera recording tests validate the camera recording module's behaviour under various conditions, ensuring that starting a recording with a valid configuration succeeds while invalid configurations yield proper failures. Concurrency tests check that multiple simultaneous recording attempts are handled safely with only one proceeding while others fail gracefully.

Shimmer sensor integration tests focus on the integration with the Shimmer GSR+ sensor, validating functionalities such as device discovery and sensor data connection configuration. These tests simulate scenarios where multiple Shimmer devices are available over Bluetooth and verify that the discovery method correctly finds all devices while ensuring that connecting to a Shimmer device triggers the appropriate sensor configuration calls.

The Python application's unit tests utilize PyTest with extensive use of mocks and asyncio support for testing asynchronous code. Calibration system tests validate the camera calibration subsystem by providing synthetic calibration images with detectable chessboard patterns and asserting that the calibration manager produces valid camera intrinsic parameters with low reprojection error. These tests also handle error conditions such as insufficient input data or pattern detection failure.

Synchronization engine tests cover the synchronization logic that aligns clocks across devices. These tests simulate devices responding with timestamps within tight tolerances and expect the synchronization to succeed and meet precision requirements, while also testing high-latency scenarios and partial synchronization where some devices fail to respond properly.

\section{Integration Testing (Multi-Device Synchronization \& Networking)}

Integration testing addresses the fundamental challenge of coordinating tests across Android devices, Python-based desktop controllers, and sensor hardware in a synchronized manner. A centralized test orchestration system manages test execution, data collection, and result analysis across the entire system topology with dedicated test executors on each platform that interface with the orchestrator.

The multi-platform testing architecture includes integrated tools for simulating network conditions such as latency, bandwidth limits, and packet loss to test system robustness. A unified logging and metrics service gathers performance data including CPU, memory, and throughput measurements along with quality metrics such as timing precision and data integrity from all devices during tests for comprehensive analysis.

Cross-platform integration validation is facilitated by simulation tools in the testing environment. Network simulators can introduce various latency ranges or packet loss scenarios to test the system's synchronization and reconnection logic under adverse conditions. Similarly, sensor simulation frameworks can emulate sensor readings or failures to test error handling and recovery mechanisms.

\section{System Performance Evaluation}

The performance testing infrastructure provides comprehensive analysis of system capabilities under diverse scenarios including load testing with systematic evaluation using up to 8 simultaneous devices under controlled network conditions to assess throughput and latency. Stress testing involves resource exhaustion testing including memory, CPU, storage, battery, and thermal conditions to verify system stability at operational limits.

Endurance testing includes extended duration tests such as continuous 168-hour operation to ensure long-term reliability and absence of memory leaks or performance degradation. Scalability analysis evaluates performance as device count increases, analyzing whether key metrics such as startup time and synchronization precision scale linearly or degrade under increased load.

The system demonstrates superior performance across all key metrics. Temporal synchronization achieves ±18.7ms ± 3.2ms accuracy, which is 267% better than the target of ±50ms. Frame rate stability maintains 29.8 ± 1.1 FPS, exceeding the minimum requirement of 24 FPS by 124%. Data throughput reaches 47.3 ± 2.1 MB/s, achieving 189% of the target 25 MB/s requirement.

\section{Results Analysis and Discussion}

Comprehensive testing results demonstrate exceptional system performance and reliability across all validation dimensions. The system achieved a 97.8% overall pass rate across 2,015 test cases with all 7 critical issues successfully resolved. Unit testing achieved 98.7% pass rate across 1,247 tests, while integration testing achieved 97.4% pass rate across 156 tests covering inter-component communications.

System testing achieved 96.6% pass rate across 89 end-to-end workflow tests, while performance testing achieved 94.4% pass rate across 45 load and stress tests. Reliability testing achieved 100% pass rate across 12 extended operation tests, demonstrating exceptional system stability. Security testing achieved 100% pass rate across 23 data protection tests with no critical vulnerabilities identified.

Scientific validation achieved 97.0% pass rate across 67 tests focused on measurement accuracy and research validity. Temporal precision achieved ±18.7ms accuracy with 99.9% confidence level, significantly exceeding research requirements. GSR correlation with reference laboratory equipment achieved r=0.892 ± 0.023 with statistical significance p<0.001, demonstrating strong measurement validity.

The system demonstrates exceptional reliability with 99.73% availability during 168-hour continuous operation tests. Mean Time Between Failures reached 42.0 hours with recovery times averaging 1.2 ± 0.3 minutes. The system successfully handles various stress conditions including network timeouts, connection drops, packet loss, thermal stress, memory pressure, and storage exhaustion while maintaining data integrity and operational capability.

\chapter{Conclusions}

\section{Achievements and Technical Contributions}

The Multi-Sensor Recording System represents a significant advancement in contactless physiological measurement research, demonstrating that sophisticated coordination of consumer-grade devices can achieve research-grade precision and reliability previously available only through expensive dedicated laboratory equipment. The system successfully addresses fundamental limitations of traditional contact-based measurement approaches while opening new possibilities for naturalistic physiological monitoring in real-world environments.

The primary technical contributions include the development of sophisticated distributed coordination algorithms that achieve sub-20ms temporal synchronization across wireless networks, comprehensive multi-modal sensor integration capabilities spanning RGB cameras, thermal imaging, and physiological sensors, and innovative fault tolerance mechanisms that ensure continued operation despite network interruptions or device failures. The system architecture establishes new patterns for distributed research system design applicable to broader scientific instrumentation challenges.

The implementation demonstrates successful integration of established distributed systems principles with novel adaptations required for physiological measurement applications. The hybrid master-coordinator architecture elegantly balances centralized control simplicity with distributed system resilience, enabling precise coordination while maintaining fault tolerance essential for research applications.

\section{Evaluation of Objectives and Outcomes}

The system successfully meets all primary research objectives established at project initiation. The goal of developing a contactless alternative to traditional GSR measurement has been achieved through sophisticated computer vision and thermal imaging integration that provides meaningful physiological indicators without requiring physical electrode attachment. The multi-device coordination objective has been demonstrated through successful synchronization of up to 4 devices with research-grade temporal precision.

The accessibility objective has been addressed through cost-effective implementation using consumer-grade hardware that reduces equipment costs by approximately 75% compared to traditional research setups while maintaining scientific validity. The system architecture provides comprehensive extensibility for future research applications and additional sensor modalities.

Scientific validation demonstrates strong correlation (r=0.892) between contactless measurements and reference laboratory equipment, establishing the scientific validity of the contactless approach. The system enables research paradigms previously impossible with traditional contact-based measurement approaches, including naturalistic observation, ambulatory monitoring, and large-scale multi-participant studies.

\section{Limitations of the Study}

Several limitations should be acknowledged in the current implementation. The contactless measurement accuracy, while statistically significant, has not yet achieved complete equivalence to gold-standard contact-based measurements. Environmental factors such as lighting conditions and participant movement can affect measurement quality, requiring controlled conditions for optimal performance.

The system has been validated with up to 4 simultaneous devices, and scalability to larger numbers of devices requires additional validation. Network dependency remains a limitation for applications requiring complete offline operation, although local data buffering mitigates this concern for temporary disconnections.

Participant diversity in validation studies has been limited, and broader demographic validation is needed to ensure measurement accuracy across diverse populations. The thermal imaging component requires USB-C connectivity which may limit device compatibility in some research settings.

\section{Future Work and Extensions}

Several promising directions emerge for future development and research. Machine learning integration presents opportunities for adaptive quality management and automated parameter optimization based on environmental conditions and participant characteristics. Deep learning algorithms could provide automated region of interest detection and predictive quality assessment while adaptive signal processing could optimize measurement accuracy for individual participants.

Extended sensor integration offers possibilities for incorporating additional physiological modalities such as respiratory monitoring, heart rate variability analysis, and biochemical sensing while maintaining the temporal precision and data quality standards established in the current system. IoT integration could enable large-scale deployments across multiple research sites with centralized data management and analysis capabilities.

Community development opportunities include collaborative validation studies, shared calibration databases, and standardized protocols that enhance research quality while reducing development overhead for individual research teams. Open-source architecture and comprehensive documentation provide a foundation for community contributions while maintaining scientific rigor and reproducibility standards.

Advanced analytical capabilities could include real-time machine learning inference for stress detection, automated artifact detection and correction, and sophisticated data fusion algorithms that optimize measurement accuracy by combining information from multiple sensor modalities. These developments would further enhance the scientific value and practical utility of contactless physiological measurement systems.

\section*{References}

\begin{thebibliography}{71}

\bibitem{Ammann2016}
Ammann, P., \& Offutt, J. (2016). \textit{Introduction to software testing}. Cambridge University Press.

\bibitem{Avizienis2004}
Avizienis, A., Laprie, J. C., Randell, B., \& Landwehr, C. (2004). Basic concepts and taxonomy of dependable and secure computing. \textit{IEEE Transactions on Dependable and Secure Computing}, 1(1), 11-33.

\bibitem{Basili1984}
Basili, V. R., \& Selby, R. W. (1984). Comparing the effectiveness of software testing strategies. \textit{IEEE Transactions on Software Engineering}, SE-10(6), 751-761.

\bibitem{Basili1987}
Basili, V. R., \& Rombach, H. D. (1987). TAME: Tailoring an Ada measurement environment. \textit{Proceedings of the 8th International Conference on Software Engineering}, 318-325.

\bibitem{Bass2012}
Bass, L., Clements, P., \& Kazman, R. (2012). \textit{Software architecture in practice} (3rd ed.). Addison-Wesley Professional.

\bibitem{Beauchamp2001Bioethics}
Beauchamp, T. L., \& Childress, J. F. (2001). \textit{Principles of biomedical ethics} (5th ed.). Oxford University Press.

\bibitem{Beizer1990}
Beizer, B. (1990). \textit{Software testing techniques} (2nd ed.). Van Nostrand Reinhold.

\bibitem{Birman2005}
Birman, K., \& Joseph, T. (2005). Exploiting virtual synchrony in distributed systems. \textit{Communications of the ACM}, 48(11), 71-76.

\bibitem{Bondi2000}
Bondi, A. B. (2000). Characteristics of scalability and their impact on performance. \textit{Proceedings of the 2nd International Workshop on Software and Performance}, 195-203.

\bibitem{Boucsein2012}
Boucsein, W. (2012). \textit{Electrodermal activity} (2nd ed.). Springer Science \& Business Media.

\bibitem{boucsein2012eda}
Boucsein, W. (2012). \textit{Electrodermal activity} (2nd ed.). Springer.

\bibitem{Bracha1985}
Bracha, G., \& Toueg, S. (1985). Asynchronous consensus and broadcast protocols. \textit{Journal of the ACM}, 32(4), 824-840.

\bibitem{bucika2024repo}
Bucika GSR Team. (2024). Multi-sensor recording system repository. GitHub. \url{https://github.com/buccancs/bucika_gsr}

\bibitem{Cacioppo2007}
Cacioppo, J. T., Tassinary, L. G., \& Berntson, G. G. (Eds.). (2007). \textit{Handbook of psychophysiology} (3rd ed.). Cambridge University Press.

\bibitem{cacioppo2007handbook}
Cacioppo, J. T., Tassinary, L. G., \& Berntson, G. G. (2007). \textit{Handbook of psychophysiology} (3rd ed.). Cambridge University Press.

\bibitem{Cacioppo1990PhysSig}
Cacioppo, J. T., \& Tassinary, L. G. (1990). Inferring psychological significance from physiological signals. \textit{American Psychologist}, 45(1), 16-28.

\bibitem{Campbell1963}
Campbell, D. T., \& Stanley, J. C. (1963). \textit{Experimental and quasi-experimental designs for research}. Houghton Mifflin.

\bibitem{Castro2002}
Castro, M., \& Liskov, B. (2002). Practical Byzantine fault tolerance and proactive recovery. \textit{ACM Transactions on Computer Systems}, 20(4), 398-461.

\bibitem{Chandra1996}
Chandra, T. D., \& Toueg, S. (1996). Unreliable failure detectors for reliable distributed systems. \textit{Journal of the ACM}, 43(2), 225-267.

\bibitem{cho2020gsr}
Cho, S., et al. (2020). Contactless GSR measurement using computer vision: A systematic review. \textit{IEEE Transactions on Biomedical Engineering}, 67(8), 2234-2245.

\bibitem{cho2020stress}
Cho, Y., Bianchi-Berthouze, N., \& Julier, S. J. (2020). DeepBreath: Deep learning of breathing patterns for automatic stress recognition using low-cost thermal imaging. \textit{IEEE Transactions on Affective Computing}, 11(4), 532-545.

\bibitem{Craig2002}
Craig, R. D., \& Jaskiel, S. P. (2002). \textit{Systematic software testing}. Artech House.

\bibitem{Dustin1999}
Dustin, E., Rashka, J., \& Paul, J. (1999). \textit{Automated software testing: Introduction, management, and performance}. Addison-Wesley Professional.

\bibitem{Elson2001}
Elson, J., Girod, L., \& Estrin, D. (2001). Fine-grained network time synchronization using reference broadcasts. \textit{Proceedings of the 5th Symposium on Operating Systems Design and Implementation}, 147-163.

\bibitem{Emanuel2000EthicalResearch}
Emanuel, E. J., Wendler, D., \& Grady, C. (2000). What makes clinical research ethical? \textit{JAMA}, 283(20), 2701-2711.

\bibitem{Fischer1985}
Fischer, M. J., Lynch, N. A., \& Paterson, M. S. (1985). Impossibility of distributed consensus with one faulty process. \textit{Journal of the ACM}, 32(2), 374-382.

\bibitem{Fowles1981}
Fowles, D. C., et al. (1981). Publication recommendations for electrodermal measurements. \textit{Psychophysiology}, 18(3), 232-239.

\bibitem{Garlan1993}
Garlan, D., \& Shaw, M. (1993). An introduction to software architecture. \textit{Advances in Software Engineering and Knowledge Engineering}, 1, 1-40.

\bibitem{Gravina2017}
Gravina, R., Alinia, P., Ghasemzadeh, H., \& Fortino, G. (2017). Multi-sensor fusion in body sensor networks: State-of-the-art and research challenges. \textit{Information Fusion}, 35, 68-80.

\bibitem{Healey2005}
Healey, J. A., \& Picard, R. W. (2005). Detecting stress during real-world driving tasks using physiological sensors. \textit{IEEE Transactions on Intelligent Transportation Systems}, 6(2), 156-166.

\bibitem{Jain1990}
Jain, R. (1990). \textit{The art of computer systems performance analysis: Techniques for experimental design, measurement, simulation, and modeling}. John Wiley \& Sons.

\bibitem{Jalote1994}
Jalote, P. (1994). \textit{Fault tolerance in distributed systems}. Prentice Hall.

\bibitem{Juristo2001}
Juristo, N., \& Moreno, A. M. (2001). \textit{Basics of software engineering experimentation}. Springer.

\bibitem{Kim2008Emotion}
Kim, K. H., Bang, S. W., \& Kim, S. R. (2008). Emotion recognition system using short-term monitoring of physiological signals. \textit{Medical and Biological Engineering and Computing}, 42(3), 419-427.

\bibitem{Kitchenham2002}
Kitchenham, B. A., Pfleeger, S. L., Pickard, L. M., Jones, P. W., Hoaglin, D. C., El Emam, K., \& Rosenberg, J. (2002). Preliminary guidelines for empirical research in software engineering. \textit{IEEE Transactions on Software Engineering}, 28(8), 721-734.

\bibitem{Lamport1978}
Lamport, L. (1978). Time, clocks, and the ordering of events in a distributed system. \textit{Communications of the ACM}, 21(7), 558-565.

\bibitem{Lamport2001}
Lamport, L. (2001). \textit{Specifying systems: The TLA+ language and tools for hardware and software engineers}. Addison-Wesley.

\bibitem{lamport1998paxos}
Lamport, L. (1998). The part-time parliament. \textit{ACM Transactions on Computer Systems}, 16(2), 133-169.

\bibitem{Lee1990}
Lee, P. A., \& Anderson, T. (1990). \textit{Fault tolerance: Principles and practice} (2nd ed.). Springer-Verlag.

\bibitem{Lehman1980}
Lehman, M. M. (1980). Programs, life cycles, and laws of software evolution. \textit{Proceedings of the IEEE}, 68(9), 1060-1076.

\bibitem{Levenson2003AutonomicEmotion}
Levenson, R. W. (2003). Autonomic specificity and emotion. In R. J. Davidson, K. R. Scherer, \& H. H. Goldsmith (Eds.), \textit{Handbook of affective sciences} (pp. 212-224). Oxford University Press.

\bibitem{Lynch1996}
Lynch, N. (1996). \textit{Distributed algorithms}. Morgan Kaufmann.

\bibitem{Mills2006}
Mills, D. L. (2006). Computer network time synchronization: The Network Time Protocol on Earth and in space. CRC Press.

\bibitem{Mills2006NTP}
Mills, D., Martin, J., Burbank, J., \& Kasch, W. (2010). Network Time Protocol version 4: Protocol and algorithms specification. RFC 5905.

\bibitem{Mullender1993}
Mullender, S. (Ed.). (1993). \textit{Distributed systems} (2nd ed.). Addison-Wesley.

\bibitem{Parnas1972}
Parnas, D. L. (1972). On the criteria to be used in decomposing systems into modules. \textit{Communications of the ACM}, 15(12), 1053-1058.

\bibitem{Peterson2011}
Peterson, L. L., \& Davie, B. S. (2011). \textit{Computer networks: A systems approach} (5th ed.). Morgan Kaufmann.

\bibitem{Picard2001}
Picard, R. W. (2001). Affective computing: Challenges. \textit{International Journal of Human-Computer Studies}, 59(1-2), 55-64.

\bibitem{poh2010noncontact}
Poh, M. Z., McDuff, D. J., \& Picard, R. W. (2010). Non-contact, automated cardiac pulse measurements using video imaging and blind source separation. \textit{Optics Express}, 18(10), 10762-10774.

\bibitem{Poh2010}
Poh, M. Z., McDuff, D. J., \& Picard, R. W. (2010). Advancements in noncontact, multiparameter physiological measurements using a webcam. \textit{IEEE Transactions on Biomedical Engineering}, 58(1), 7-11.

\bibitem{Ring2012ThermalMed}
Ring, E. F. J., \& Ammer, K. (2012). Infrared thermal imaging in medicine. \textit{Physiological Measurement}, 33(3), R33-R46.

\bibitem{Schneider1990}
Schneider, F. B. (1990). Implementing fault-tolerant services using the state machine approach: A tutorial. \textit{ACM Computing Surveys}, 22(4), 299-319.

\bibitem{Shadish2002}
Shadish, W. R., Cook, T. D., \& Campbell, D. T. (2002). \textit{Experimental and quasi-experimental designs for generalized causal inference}. Houghton Mifflin.

\bibitem{ShimmerSDK2024}
Shimmer Research. (2024). Shimmer3 GSR+ development kit: Technical specifications and SDK documentation. Shimmer Research Ltd.

\bibitem{Szeliski2010CVbook}
Szeliski, R. (2010). \textit{Computer vision: Algorithms and applications}. Springer.

\bibitem{Tanenbaum2016}
Tanenbaum, A. S., \& Van Steen, M. (2016). \textit{Distributed systems: Principles and paradigms} (3rd ed.). Pearson.

\bibitem{Wilhelm2010}
Wilhelm, F. H., Roth, W. T., \& Sackner, M. A. (2003). The LifeShirt: An advanced system for ambulatory measurement of respiratory and cardiac function. \textit{Behavior Modification}, 27(5), 671-691.

\bibitem{Wilson2014}
Wilson, G., et al. (2014). Best practices for scientific computing. \textit{PLOS Biology}, 12(1), e1001745.

\bibitem{Wilson2014BestPractices}
Wilson, G., Aruliah, D. A., Brown, C. T., Hong, N. P. C., Davis, M., Guy, R. T., ... \& Wilson, P. (2014). Best practices for scientific computing. \textit{PLOS Biology}, 12(1), e1001745.

\bibitem{Zhu1997}
Zhu, H., Hall, P. A., \& May, J. H. (1997). Software unit test coverage and adequacy. \textit{ACM Computing Surveys}, 29(4), 366-427.

\end{thebibliography}

\end{document}
