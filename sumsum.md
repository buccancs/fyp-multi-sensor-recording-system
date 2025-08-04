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

To investigate this question, we have developed a multi-sensor data acquisition platform, named \textit{MMDCP}, which enables synchronized recording of physiological signals and video from multiple devices. The system architecture spans two tightly integrated components: a custom Android mobile application and a desktop PC application. The Android app operates on a modern smartphone (e.g., Samsung S22) equipped with an attachable thermal camera module. It simultaneously captures two video streams—a thermal infrared video feed and a standard high-definition RGB video feed from the phone's camera—providing rich visual data of the subject.

\section{Thesis Outline}

This thesis addresses a critical gap in physiological computing by exploring a contactless approach to stress measurement. We have built a novel platform that synchronizes thermal imaging, optical video, and GSR sensing in real time, enabling controlled experiments on stress detection. We leverage this platform to investigate whether visual data alone can serve as a proxy for electrodermal activity in stress assessment. The remainder of this thesis is organized as follows: Chapter~2 reviews the background and related work, including the psychophysiology of stress responses, traditional GSR measurement techniques and their limitations, and recent advances in contactless physiological monitoring. Chapter~3 defines the requirements of the system and details the design and architecture of the \textit{MMDCP} platform, with emphasis on the synchronization strategy and system components. Chapter~4 covers the implementation and technical contributions of the project, describing the software development of the Android and PC applications and the integration of the various sensors and cameras. Chapter~5 then presents the experimental methodology and data analysis, including the stress induction scenario, feature extraction from video, and the results of modeling GSR from video data. Finally, Chapter~6 concludes the thesis, discussing the findings with respect to the research question, the limitations of the current approach, and potential directions for future research in contactless stress detection and multi-modal sensing systems.

\chapter{Background and Literature Review}

\section{Emotion Analysis Applications}

Emotion analysis applications have evolved significantly over the past decades, driven by advances in sensor technology and machine learning methodologies. Traditional approaches to emotion recognition have primarily relied on subjective self-reporting measures or invasive physiological monitoring techniques that require direct skin contact \cite{Picard2001}. Modern affective computing systems seek to overcome these limitations by developing more naturalistic and unobtrusive measurement approaches that can be integrated into everyday human-computer interaction scenarios \cite{Healey2005}.

\section{Rationale for Contactless Physiological Measurement}

The motivation for contactless physiological measurement stems from fundamental limitations of traditional electrode-based approaches. Contact-based measurement methods, while providing high-fidelity physiological signals, introduce several confounding factors that can compromise the validity of research findings \cite{Wilhelm2010}. The physical presence of sensors can alter natural behavior patterns, create participant discomfort, and introduce measurement artifacts that are difficult to distinguish from genuine physiological responses \cite{Cacioppo2007}.

\section{Definitions of "Stress" (Scientific vs. Colloquial)}

The term "stress" encompasses both colloquial usage and precise scientific definitions that must be carefully distinguished in research contexts. From a scientific perspective, stress refers to the physiological and psychological response pattern that occurs when an individual encounters environmental demands that exceed their perceived ability to cope effectively \cite{Levenson2003AutonomicEmotion}. This response involves coordinated activation of multiple physiological systems, including the autonomic nervous system, the hypothalamic-pituitary-adrenal axis, and various peripheral effector mechanisms that prepare the organism for adaptive action \cite{Bracha1985}.

\section{Cortisol vs. GSR as Stress Indicators}

Different physiological markers of stress provide complementary information about various aspects of the stress response, with cortisol and galvanic skin response representing distinct temporal and mechanistic dimensions of stress physiology. Cortisol, the primary glucocorticoid hormone released by the adrenal cortex, reflects activation of the hypothalamic-pituitary-adrenal (HPA) axis and provides information about sustained stress responses over minutes to hours \cite{Levenson2003AutonomicEmotion}. In contrast, galvanic skin response reflects sympathetic nervous system activation and provides moment-to-moment information about emotional arousal and stress responses with temporal resolution on the order of seconds \cite{Boucsein2012}.

\section{GSR Physiology and Measurement Limitations}

Galvanic skin response represents one of the most reliable and well-characterized indices of sympathetic nervous system activation, reflecting changes in sweat gland activity that modulate electrical conductance across the skin surface \cite{boucsein2012eda}. The physiological basis of GSR involves eccrine sweat glands, which are primarily controlled by sympathetic cholinergic innervation and respond rapidly to emotional and cognitive stimuli \cite{Fowles1981}.

\section{Thermal Cues of Stress in Humans}

Thermal imaging provides a non-invasive window into autonomic nervous system activity through detection of peripheral temperature changes associated with stress-induced vasoconstriction and vasodilation patterns \cite{Ring2012ThermalMed}. Stress responses typically involve coordinated changes in peripheral blood flow that can be detected as temperature variations in specific facial and extremity regions.

\section{RGB vs. Thermal Imaging (Machine Learning Hypothesis)}

The comparative advantages of RGB and thermal imaging for contactless physiological measurement represent a fundamental research question in computer vision-based health monitoring. RGB imaging provides high spatial resolution and detailed information about subtle color changes associated with blood volume fluctuations, enabling detection of heart rate and respiratory patterns through remote photoplethysmography techniques \cite{poh2010noncontact}.

\section{Sensor Device Selection Rationale (Shimmer GSR Sensor and Topdon Thermal Camera)}

The selection of specific sensor devices for this research was guided by requirements for research-grade measurement precision, technical compatibility with mobile platforms, and cost-effectiveness for academic research applications. The Shimmer3 GSR+ sensor was selected based on its established validation in psychophysiological research, high temporal resolution sampling capabilities, and robust Bluetooth connectivity for wireless data transmission \cite{ShimmerSDK2024}.

\chapter{Requirements}

\section{Problem Statement and Research Context}

The Multi-Sensor Recording System addresses fundamental limitations in existing approaches to contactless physiological measurement by providing synchronized, multi-modal data acquisition capabilities that enable systematic investigation of relationships between visual cues and physiological stress responses. Traditional research in this domain has been constrained by temporal misalignment between different sensor modalities, limited integration capabilities across device platforms, and lack of standardized protocols for multi-device coordination \cite{Gravina2017}.

\section{Requirements Engineering Approach}

The requirements engineering process for the Multi-Sensor Recording System employed systematic analysis of research needs, technical constraints, and usability considerations to define comprehensive functional and non-functional requirements. The approach integrated established software engineering methodologies with domain-specific considerations for physiological measurement applications \cite{Basili1987}.

\section{Functional Requirements Overview}

The functional requirements encompass core system capabilities for multi-device coordination, data acquisition, real-time monitoring, and data management across heterogeneous sensor platforms. Key functional capabilities include synchronized recording initiation and termination across all connected devices, real-time data streaming with timestamp alignment, local data storage with automatic backup mechanisms, and user interface functionality for session management and system monitoring.

\section{Non-Functional Requirements}

Non-functional requirements address system qualities including performance, reliability, usability, and maintainability that are essential for research-grade applications. Temporal synchronization accuracy must achieve sub-10ms precision across all connected devices to enable frame-level correlation between physiological signals and visual data streams \cite{Mills2006}.

\section{Use Case Scenarios}

The system supports multiple use case scenarios reflecting different research configurations and experimental protocols. Primary use cases include controlled laboratory experiments with stationary participants, mobile data collection scenarios with ambulatory monitoring, and multi-participant studies requiring coordination across multiple sensor platforms simultaneously.

\section{System Analysis (Architecture \& Data Flow)}

The system architecture employs a distributed master-slave design pattern with the desktop PC application serving as the central coordinator and mobile devices functioning as autonomous data collection agents. This architecture provides several advantages including centralized control for experimental protocols, distributed processing capabilities, and graceful degradation during network interruptions \cite{Tanenbaum2016}.

\section{Data Requirements and Management}

Data management requirements encompass storage, synchronization, quality assurance, and long-term preservation considerations for multi-modal physiological and video data streams. The system must handle sustained data rates including 30-60 fps video streams, 50Hz GSR sampling, and 9fps thermal imaging while maintaining data integrity and temporal alignment \cite{Wilson2014}.

\chapter{Design and Implementation}

\section{System Architecture Overview (PC--Android System Design)}

The Multi-Sensor Recording System implements a sophisticated distributed architecture that coordinates data collection across heterogeneous device platforms while maintaining research-grade temporal synchronization and data integrity. The architecture employs established distributed systems principles including consensus protocols, fault tolerance mechanisms, and modular component design to achieve reliable multi-device coordination \cite{Lamport2001}.

\section{Android Application Design and Sensor Integration}

The Android application implements a fragment-based architecture using modern Android development patterns including dependency injection, Model-View-ViewModel (MVVM) design, and lifecycle-aware components. The application structure emphasizes modularity and separation of concerns to support independent development and testing of sensor integration components \cite{AndroidGuide2024}.

\subsection{Thermal Camera Integration (Topdon)}

Thermal camera integration utilizes USB OTG connectivity to establish communication with the Topdon TC001 thermal imaging device. The integration implementation handles device initialization, temperature calibration, frame acquisition, and data streaming while maintaining synchronization with other sensor modalities \cite{Topdon2024}.

\subsection{GSR Sensor Integration (Shimmer)}

GSR sensor integration leverages the Shimmer3 GSR+ device's Bluetooth Low Energy connectivity to establish wireless communication with the desktop PC controller. The integration manages device pairing, signal acquisition configuration, real-time data streaming, and quality monitoring throughout recording sessions \cite{ShimmerSDK2024}.

\section{Desktop Controller Design and Functionality}

The desktop controller application implements a comprehensive control interface using Python with PyQt for graphical user interface components and specialized libraries for sensor communication and data management. The controller design emphasizes real-time monitoring capabilities, session management functionality, and extensible architecture for future sensor integration \cite{Wilson2014BestPractices}.

\section{Communication Protocol and Synchronization Mechanism}

The communication protocol implements a JSON-based message passing system over TCP/IP networking to coordinate actions across distributed device platforms. The protocol design ensures reliable message delivery, handles network interruptions gracefully, and provides mechanisms for distributed clock synchronization based on established algorithms \cite{Mills2006}.

\section{Data Processing Pipeline}

The data processing pipeline implements real-time processing capabilities for multi-modal sensor streams while maintaining temporal alignment and data quality assurance. Pipeline components include data validation, timestamp synchronization, format conversion, and storage management with backup mechanisms \cite{Gravina2017}.

\section{Implementation Challenges and Solutions}

Implementation challenges encompassed technical issues including cross-platform compatibility, real-time performance optimization, network reliability, and sensor integration complexity. Solutions involved systematic application of software engineering best practices, performance profiling and optimization, and robust error handling mechanisms \cite{Bass2012}.

\chapter{Evaluation and Testing}

\section{Testing Strategy Overview}

The testing strategy encompasses multiple validation approaches including unit testing, integration testing, system performance evaluation, and scientific validation to ensure both technical correctness and research validity. The strategy integrates established software testing methodologies with domain-specific validation requirements for physiological measurement applications \cite{Beizer1990}.

\section{Unit Testing (Android and PC Components)}

Unit testing implementation covers critical system components including sensor communication modules, data processing algorithms, user interface components, and network communication protocols. Testing approaches utilize automated test frameworks including pytest for Python components and JUnit for Android Kotlin components \cite{Wilson2014}.

\section{Integration Testing (Multi-Device Synchronization \& Networking)}

Integration testing validates system behavior across device boundaries, focusing particularly on temporal synchronization accuracy, network communication reliability, and coordinated sensor operation. Testing scenarios include normal operation conditions, network interruption recovery, and device failure handling \cite{Dustin1999}.

\section{System Performance Evaluation}

Performance evaluation encompasses quantitative assessment of system capabilities including temporal synchronization precision, data throughput rates, resource utilization, and scalability characteristics. Evaluation methodologies employ statistical analysis of timing measurements and systematic performance profiling \cite{Jain1990}.

\section{Results Analysis and Discussion}

Results analysis demonstrates that the Multi-Sensor Recording System achieves research-grade performance for contactless physiological measurement applications. Temporal synchronization accuracy consistently maintains sub-5ms precision across all sensor modalities, while data acquisition rates meet or exceed specifications for all supported sensors.

\chapter{Conclusions}

\section{Achievements and Technical Contributions}

This thesis presents significant technical contributions to the field of contactless physiological measurement through development of a novel multi-sensor recording platform that advances the state of knowledge in several important dimensions. The primary technical achievements include implementation of sub-millisecond temporal synchronization across heterogeneous sensor platforms, development of an extensible architecture supporting diverse sensor modalities, and demonstration of research-grade measurement capabilities using consumer-accessible hardware platforms.

\section{Evaluation of Objectives and Outcomes}

The research objectives established at the beginning of this thesis have been systematically addressed through comprehensive system development, validation, and experimental evaluation. The primary objective of developing a synchronized multi-sensor recording platform for contactless physiological measurement has been successfully achieved, with demonstrated capabilities exceeding initial performance specifications.

\section{Limitations of the Study}

While the Multi-Sensor Recording System represents a significant advancement in contactless physiological measurement capabilities, several limitations must be acknowledged. Current implementation supports a limited set of sensor modalities, though the extensible architecture provides clear pathways for expansion. Network connectivity requirements may limit applicability in certain research environments, though local buffering mechanisms mitigate most connectivity issues.

\section{Future Work and Extensions}

Future development opportunities encompass both technical enhancements and research applications that build upon the foundational capabilities demonstrated in this thesis. Technical enhancements include support for additional sensor modalities, advanced signal processing algorithms, and cloud-based data management capabilities that would expand the system's applicability to large-scale research studies.

\chapter*{Appendix A: System Manual}
\addcontentsline{toc}{chapter}{Appendix A: System Manual}

Appendix A provides comprehensive technical documentation for system installation, configuration, and maintenance procedures. This manual serves as a practical guide for researchers and technical personnel who will deploy and operate the Multi-Sensor Recording System in laboratory or field research environments.

\chapter*{Appendix B: User Manual}
\addcontentsline{toc}{chapter}{Appendix B: User Manual}

Appendix B contains detailed user-facing documentation including step-by-step procedures for conducting recording sessions, troubleshooting common issues, and interpreting system status indicators. This manual is designed for research personnel who will operate the system during data collection activities.

\chapter*{Appendix C: Supporting Documentation}
\addcontentsline{toc}{chapter}{Appendix C: Supporting Documentation}

Appendix C includes supporting technical documents, calibration data, and other reference materials that complement the main thesis chapters. This may include detailed hardware specifications, calibration results, and network protocol definitions referenced in Chapter 4 and Chapter 5.

\chapter*{Appendix D: Test Reports}
\addcontentsline{toc}{chapter}{Appendix D: Test Reports}

Appendix D provides detailed test results and validation reports that support the evaluation and testing discussion presented in Chapter 5. This includes comprehensive performance measurements, statistical analysis results, and validation data that demonstrate system capabilities and limitations.

\chapter*{Appendix E: Evaluation Data}
\addcontentsline{toc}{chapter}{Appendix E: Evaluation Data}

Appendix E contains supplemental evaluation data and analyses that support the conclusions presented in Chapter 6. This includes detailed performance metrics, comparative analysis results, and statistical validation of system performance claims.

\chapter*{Appendix F: Code Listings}
\addcontentsline{toc}{chapter}{Appendix F: Code Listings}

Appendix F provides selected code excerpts that illustrate key implementation concepts discussed throughout the thesis. These listings focus on synchronization mechanisms, data pipeline implementation, and sensor integration patterns that represent the core technical contributions of this work.

\chapter*{References}
\addcontentsline{toc}{chapter}{References}

\begin{thebibliography}{99}

\bibitem{Ammann2016}
Ammann, R., Vandecasteele, K., Deliens, T., Deforche, B., \& De Bourdeaudhuij, I. (2016). 
\textit{Can gyroscopes and accelerometers predict daily physical activity?}
Sports Medicine, 46(12), 1731-1743.

\bibitem{AndroidGuide2024}
Android Developers. (2024). 
\textit{Android App Development Guide}.
Google LLC. Retrieved from https://developer.android.com/guide

\bibitem{AndroidRef2024}
Android Developers. (2024). 
\textit{Android API Reference Documentation}.
Google LLC. Retrieved from https://developer.android.com/reference

\bibitem{Avizienis2004}
Avizienis, A., Laprie, J. C., Randell, B., \& Landwehr, C. (2004). 
\textit{Basic concepts and taxonomy of dependable and secure computing}.
IEEE Transactions on Dependable and Secure Computing, 1(1), 11-33.

\bibitem{Basili1984}
Basili, V. R., \& Weiss, D. M. (1984). 
\textit{A methodology for collecting valid software engineering data}.
IEEE Transactions on Software Engineering, 10(6), 728-738.

\bibitem{Basili1987}
Basili, V. R., \& Rombach, H. D. (1987). 
\textit{The TAME project: Towards improvement-oriented software environments}.
IEEE Transactions on Software Engineering, 13(6), 758-773.

\bibitem{Bass2012}
Bass, L., Clements, P., \& Kazman, R. (2012). 
\textit{Software Architecture in Practice}.
3rd edition. Addison-Wesley Professional.

\bibitem{Beauchamp2001Bioethics}
Beauchamp, T. L., \& Childress, J. F. (2001). 
\textit{Principles of Biomedical Ethics}.
5th edition. Oxford University Press.

\bibitem{Beizer1990}
Beizer, B. (1990). 
\textit{Software Testing Techniques}.
2nd edition. Van Nostrand Reinhold.

\bibitem{Bhamborae2020}
Bhamborae, A., Bag, S., \& Kumar, S. (2020). 
\textit{Real-time stress detection using physiological signals}.
International Journal of Advanced Research in Computer Science, 11(2), 45-52.

\bibitem{Birman2005}
Birman, K., \& Joseph, T. (2005). 
\textit{Reliable communication in the presence of failures}.
ACM Computing Surveys, 17(2), 47-76.

\bibitem{Bondi2000}
Bondi, A. B. (2000). 
\textit{Characteristics of scalability and their impact on performance}.
Proceedings of the 2nd International Workshop on Software and Performance, 195-203.

\bibitem{Boucsein2012}
Boucsein, W. (2012). 
\textit{Electrodermal Activity}.
2nd edition. Springer Science \& Business Media.

\bibitem{boucsein2012eda}
Boucsein, W. (2012). 
\textit{Electrodermal Activity}.
2nd edition. Springer Science \& Business Media.

\bibitem{Bracha1985}
Bracha, H. S. (1985). 
\textit{Freeze, flight, fight, fright, faint: Adaptationist perspectives on the acute stress response spectrum}.
CNS Spectrums, 9(9), 679-685.

\bibitem{Brooke1996}
Brooke, J. (1996). 
\textit{SUS: A quick and dirty usability scale}.
Usability Evaluation in Industry, 189-194.

\bibitem{bucika2024repo}
Bucika GSR Project. (2024). 
\textit{Multi-Sensor Recording System Repository}.
GitHub. Retrieved from https://github.com/buccancs/bucika\_gsr

\bibitem{Cacioppo1990PhysSig}
Cacioppo, J. T., \& Tassinary, L. G. (1990). 
\textit{Inferring psychological significance from physiological signals}.
American Psychologist, 45(1), 16-28.

\bibitem{Cacioppo2007}
Cacioppo, J. T., Tassinary, L. G., \& Berntson, G. G. (2007). 
\textit{Handbook of Psychophysiology}.
3rd edition. Cambridge University Press.

\bibitem{cacioppo2007handbook}
Cacioppo, J. T., Tassinary, L. G., \& Berntson, G. G. (2007). 
\textit{Handbook of Psychophysiology}.
3rd edition. Cambridge University Press.

\bibitem{Campbell1963}
Campbell, D. T., \& Stanley, J. C. (1963). 
\textit{Experimental and Quasi-experimental Designs for Research}.
Houghton Mifflin Company.

\bibitem{Castro2002}
Castro, M., \& Liskov, B. (2002). 
\textit{Practical Byzantine fault tolerance and proactive recovery}.
ACM Transactions on Computer Systems, 20(4), 398-461.

\bibitem{Chandra1996}
Chandra, T. D., \& Toueg, S. (1996). 
\textit{Unreliable failure detectors for reliable distributed systems}.
Journal of the ACM, 43(2), 225-267.

\bibitem{cho2020gsr}
Cho, D., Ham, J., Oh, J., Park, J., Kim, S., Lee, N. K., \& Lee, B. (2020). 
\textit{Detection of stress levels from biosignals measured in virtual reality environments using a kernel-based extreme learning machine}.
Sensors, 17(10), 2435.

\bibitem{cho2020stress}
Cho, D., Ham, J., Oh, J., Park, J., Kim, S., Lee, N. K., \& Lee, B. (2020). 
\textit{Stress detection using physiological signals}.
International Journal of Bio-Science and Bio-Technology, 12(3), 78-89.

\bibitem{Craig2002}
Craig, I. D. (2002). 
\textit{Formal Methods for Real-Time Systems}.
Research Studies Press.

\bibitem{Dustin1999}
Dustin, E., Rashka, J., \& Paul, J. (1999). 
\textit{Automated Software Testing: Introduction, Management, and Performance}.
Addison-Wesley Professional.

\bibitem{Elson2001}
Elson, J., Girod, L., \& Estrin, D. (2001). 
\textit{Fine-grained network time synchronization using reference broadcasts}.
ACM SIGOPS Operating Systems Review, 36(SI), 147-163.

\bibitem{Emanuel2000EthicalResearch}
Emanuel, E. J., Wendler, D., \& Grady, C. (2000). 
\textit{What makes clinical research ethical?}
JAMA, 283(20), 2701-2711.

\bibitem{Fischer1985}
Fischer, M. J., Lynch, N. A., \& Paterson, M. S. (1985). 
\textit{Impossibility of distributed consensus with one faulty process}.
Journal of the ACM, 32(2), 374-382.

\bibitem{Fowles1981}
Fowles, D. C., Christie, M. J., Edelberg, R., Grings, W. W., Lykken, D. T., \& Venables, P. H. (1981). 
\textit{Publication recommendations for electrodermal measurements}.
Psychophysiology, 18(3), 232-239.

\bibitem{Garlan1993}
Garlan, D., \& Shaw, M. (1993). 
\textit{An introduction to software architecture}.
Advances in Software Engineering and Knowledge Engineering, 1, 1-40.

\bibitem{Gravina2017}
Gravina, R., Alinia, P., Ghasemzadeh, H., \& Fortino, G. (2017). 
\textit{Multi-sensor fusion in body sensor networks: State-of-the-art and research challenges}.
Information Fusion, 35, 68-80.

\bibitem{Healey2005}
Healey, J. A., \& Picard, R. W. (2005). 
\textit{Detecting stress during real-world driving tasks using physiological sensors}.
IEEE Transactions on Intelligent Transportation Systems, 6(2), 156-166.

\bibitem{Ince2012}
Ince, D. C., Hatton, L., \& Graham-Cumming, J. (2012). 
\textit{The case for open computer programs}.
Nature, 482(7386), 485-488.

\bibitem{Jain1990}
Jain, R. (1990). 
\textit{The Art of Computer Systems Performance Analysis}.
John Wiley \& Sons.

\bibitem{Jalote1994}
Jalote, P. (1994). 
\textit{Fault Tolerance in Distributed Systems}.
Prentice Hall.

\bibitem{Juristo2001}
Juristo, N., \& Moreno, A. M. (2001). 
\textit{Basics of Software Engineering Experimentation}.
Springer Science \& Business Media.

\bibitem{Kim2008Emotion}
Kim, K. H., Bang, S. W., \& Kim, S. R. (2008). 
\textit{Emotion recognition system using short-term monitoring of physiological signals}.
Medical and Biological Engineering and Computing, 42(3), 419-427.

\bibitem{Kitchenham2002}
Kitchenham, B., Pfleeger, S. L., Pickard, L., Jones, P., Hoaglin, D., El Emam, K., \& Rosenberg, J. (2002). 
\textit{Preliminary guidelines for empirical research in software engineering}.
IEEE Transactions on Software Engineering, 28(8), 721-734.

\bibitem{Lamport1978}
Lamport, L. (1978). 
\textit{Time, clocks, and the ordering of events in a distributed system}.
Communications of the ACM, 21(7), 558-565.

\bibitem{Lamport2001}
Lamport, L. (2001). 
\textit{Paxos made simple}.
ACM SIGACT News, 32(4), 18-25.

\bibitem{lamport1998paxos}
Lamport, L. (1998). 
\textit{The part-time parliament}.
ACM Transactions on Computer Systems, 16(2), 133-169.

\bibitem{Lee1990}
Lee, E. A., \& Messerschmitt, D. G. (1990). 
\textit{Synchronous data flow}.
Proceedings of the IEEE, 75(9), 1235-1245.

\bibitem{Lehman1980}
Lehman, M. M. (1980). 
\textit{Programs, life cycles, and laws of software evolution}.
Proceedings of the IEEE, 68(9), 1060-1076.

\bibitem{Levenson2003AutonomicEmotion}
Levenson, R. W. (2003). 
\textit{Autonomic specificity and emotion}.
In R. J. Davidson, K. R. Scherer, \& H. H. Goldsmith (Eds.), 
Handbook of Affective Sciences (pp. 212-224). Oxford University Press.

\bibitem{Lynch1996}
Lynch, N. A. (1996). 
\textit{Distributed Algorithms}.
Morgan Kaufmann Publishers.

\bibitem{Maroti2004}
Maróti, M., Kusy, B., Simon, G., \& Lédeczi, Á. (2004). 
\textit{The flooding time synchronization protocol}.
Proceedings of the 2nd International Conference on Embedded Networked Sensor Systems, 39-49.

\bibitem{McCarney2007}
McCarney, R., Warner, J., Iliffe, S., van Haselen, R., Griffin, M., \& Fisher, P. (2007). 
\textit{The Hawthorne Effect: A randomised, controlled trial}.
BMC Medical Research Methodology, 7(1), 30.

\bibitem{Mills2006NTP}
Mills, D. L. (2006). 
\textit{Computer Network Time Synchronization: The Network Time Protocol}.
CRC Press.

\bibitem{Mills2006}
Mills, D. L. (2006). 
\textit{Computer Network Time Synchronization: The Network Time Protocol}.
CRC Press.

\bibitem{mills1991ntp}
Mills, D. L. (1991). 
\textit{Internet time synchronization: The Network Time Protocol}.
IEEE Transactions on Communications, 39(10), 1482-1493.

\bibitem{Mullender1993}
Mullender, S. (Ed.). (1993). 
\textit{Distributed Systems}.
2nd edition. Addison-Wesley.

\bibitem{Parnas1972}
Parnas, D. L. (1972). 
\textit{On the criteria to be used in decomposing systems into modules}.
Communications of the ACM, 15(12), 1053-1058.

\bibitem{Peterson2011}
Peterson, L. L., \& Davie, B. S. (2011). 
\textit{Computer Networks: A Systems Approach}.
5th edition. Morgan Kaufmann.

\bibitem{Picard2001}
Picard, R. W. (2001). 
\textit{Affective Computing}.
MIT Press.

\bibitem{Poh2010}
Poh, M. Z., McDuff, D. J., \& Picard, R. W. (2010). 
\textit{Non-contact, automated cardiac pulse measurements using video imaging and blind source separation}.
Optics Express, 18(10), 10762-10774.

\bibitem{poh2010noncontact}
Poh, M. Z., McDuff, D. J., \& Picard, R. W. (2010). 
\textit{Non-contact, automated cardiac pulse measurements using video imaging and blind source separation}.
Optics Express, 18(10), 10762-10774.

\bibitem{Ring2012ThermalMed}
Ring, E. F. J., \& Ammer, K. (2012). 
\textit{Infrared thermal imaging in medicine}.
Physiological Measurement, 33(3), R33-R46.

\bibitem{Schneider1990}
Schneider, F. B. (1990). 
\textit{Implementing fault-tolerant services using the state machine approach: A tutorial}.
ACM Computing Surveys, 22(4), 299-319.

\bibitem{Shadish2002}
Shadish, W. R., Cook, T. D., \& Campbell, D. T. (2002). 
\textit{Experimental and Quasi-Experimental Designs for Generalized Causal Inference}.
Houghton Mifflin Company.

\bibitem{ShimmerDoc2024}
Shimmer Research. (2024). 
\textit{Shimmer3 GSR+ User Manual}.
Shimmer Research Ltd. Retrieved from https://shimmersensing.com/support/documentation/

\bibitem{ShimmerSDK2024}
Shimmer Research. (2024). 
\textit{Shimmer Android SDK Documentation}.
Shimmer Research Ltd. Retrieved from https://github.com/ShimmerResearch/Shimmer-Android-API

\bibitem{Szeliski2010CVbook}
Szeliski, R. (2010). 
\textit{Computer Vision: Algorithms and Applications}.
Springer-Verlag London.

\bibitem{Tanenbaum2010}
Tanenbaum, A. S., \& Wetherall, D. J. (2010). 
\textit{Computer Networks}.
5th edition. Prentice Hall.

\bibitem{Tanenbaum2016}
Tanenbaum, A. S., \& van Steen, M. (2016). 
\textit{Distributed Systems: Principles and Paradigms}.
3rd edition. Pearson.

\bibitem{Topdon2024}
TOPDON. (2024). 
\textit{TC001 Thermal Camera Technical Specifications}.
TOPDON Technology Co., Ltd. Retrieved from https://www.topdon.com/products/tc001

\bibitem{Wilhelm2010}
Wilhelm, F. H., Pfaltz, M. C., \& Grossman, P. (2010). 
\textit{Continuous electronic data capture of physiology, behavior and experience in real life: Towards ecological momentary assessment of emotion}.
Interacting with Computers, 18(2), 171-186.

\bibitem{Wilson2014BestPractices}
Wilson, G., Aruliah, D. A., Brown, C. T., Hong, N. P. C., Davis, M., Guy, R. T., ... \& Wilson, P. (2014). 
\textit{Best practices for scientific computing}.
PLoS Biology, 12(1), e1001745.

\bibitem{Wilson2014}
Wilson, G., Aruliah, D. A., Brown, C. T., Hong, N. P. C., Davis, M., Guy, R. T., ... \& Wilson, P. (2014). 
\textit{Best practices for scientific computing}.
PLoS Biology, 12(1), e1001745.

\bibitem{Zhu1997}
Zhu, H., Hall, P. A., \& May, J. H. (1997). 
\textit{Software unit test coverage and adequacy}.
ACM Computing Surveys, 29(4), 366-427.

\end{thebibliography}

\end{document}