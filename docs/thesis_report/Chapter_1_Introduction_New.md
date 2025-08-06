# Chapter 1: Introduction

## Multi-sensor recording system for contactless GSR prediction research

---

## Table of contents

- [1.1 Motivation and research context](#11-motivation-and-research-context)
- [1.2 Research problem and objectives](#12-research-problem-and-objectives)
- [1.3 Thesis outline](#13-thesis-outline)

---

## 1.1 Motivation and research context

In recent years, there has been growing interest in physiological computing. This field uses bodily signals to infer a person's internal states for health monitoring, affective computing, and human-computer interaction. One physiological signal that has proven especially valuable is the Galvanic Skin Response (GSR), also known as electrodermal activity or skin conductance. GSR measures subtle changes in the skin's electrical conductance caused by sweat gland activity. The sympathetic nervous system directly modulates this activity [^1]. Because these changes reflect emotional arousal and stress involuntarily, researchers widely regard GSR as a reliable indicator of autonomic nervous system activity [^2].

Applications of GSR span clinical psychology (for example, biofeedback therapy and polygraph testing) and user experience research, where it can reveal unconscious stress or emotional responses. Even consumer technology has begun to leverage skin conductance. Modern wearable devices (for example, recent smartwatches by Apple and Samsung) incorporate sensors for continuous stress monitoring based on GSR or related metrics [^3] [^4]. This surge of interest underscores the motivation to harness physiological signals like GSR in everyday contexts.

Despite its value, traditional GSR measurement requires skin-contact electrodes (typically attached to fingers or palms with conductive gel) [^5]. This method causes intrusion. The wires and electrodes can restrict natural movement and comfort, and long-term use may cause discomfort or skin irritation [^6] [^7]. These practical limitations make it difficult to use GSR in natural, real-world settings outside the lab.

Consequently, contactless measurement techniques for GSR have become an appealing research direction [^8]. The idea is to infer GSR (or the underlying psychophysiological arousal) using remote sensors that do not require physical contact with the user. For example, thermal infrared cameras can detect subtle temperature changes on the skin surface due to blood flow and perspiration, offering a proxy for stress-induced responses [^9]. Facial infrared imaging has shown promise as a complementary measure in emotion research, capitalizing on the fact that stress and thermoregulation are linked (e.g. perspiration causes evaporative cooling) [^10].

Similarly, high-resolution RGB cameras with advanced computer vision algorithms can non-invasively capture other physiological signals – prior work has demonstrated heart rate and breathing can be measured from video of a person's face or body [^11] [^12]. These developments suggest that multi-modal sensing, combining traditional biosensors with imaging, could enable contactless physiological monitoring in the future.

Research in affective computing increasingly points to the benefit of fusing multiple modalities (e.g. GSR, heart rate, facial thermal signals) to more robustly capture emotional or stress states [^13] [^14]. However, realizing such a vision requires overcoming significant challenges.

A key research gap is the lack of an integrated platform to collect and synchronize these diverse data streams. Most prior studies have tackled contactless GSR estimation in isolation or under highly controlled conditions, often using separate devices that are not synchronized in real time [^15] [^16]. For instance, thermal cameras and wearable GSR sensors have typically been used independently, with any fusion of their data done post hoc. This piecemeal approach complicates the development of machine learning models, which require well-aligned datasets of inputs (e.g. video/thermal data) and ground truth outputs (measured GSR).

There is a clear need for a multi-modal data collection platform that can simultaneously record GSR signals alongside other sensor modalities in a synchronized manner. Such a platform would enable researchers to gather rich, time-aligned datasets – for example, thermal video of a participant's face recorded in lockstep with their GSR signal – thereby laying the groundwork for training and validating predictive models that infer GSR from alternative sensors.

The primary contribution of this thesis is the development of precisely such a platform: a modular, multi-sensor system for synchronized physiological data acquisition geared toward future GSR prediction research. In summary, the motivation behind this work stems from recent trends in physiological computing and multimodal sensing, and the recognized need for robust, synchronized datasets to advance contactless GSR measurement.

---

## 1.2 Research problem and objectives

Given the above context, the research problem can be stated as follows: there is currently no readily available system that enables synchronized collection of GSR signals together with complementary data streams (such as thermal and visual data) in naturalistic settings, which hinders the development of machine learning models for contactless GSR prediction.

While traditional GSR sensors provide reliable ground-truth measurements, they are intrusive for real-world use, and purely contactless approaches remain unvalidated or imprecise [^17]. To bridge this gap, researchers require a platform that can record multiple modalities simultaneously – for example, capturing a person's skin conductance with a wearable sensor while concurrently recording thermal camera footage and standard video. Crucially, all data must be time-synchronized with high precision to allow meaningful correlation and learning.

The absence of such an integrated system forms the core problem that this thesis addresses. The objective of this research, therefore, is to design and implement a multi-modal physiological data collection platform that enables the creation of a synchronized dataset for future GSR prediction models. Unlike end-user applications or final predictive systems, the focus here is on the data acquisition infrastructure – in other words, building the foundation upon which real-time GSR inference algorithms can later be developed.

It is important to clarify that real-time GSR prediction is not within the scope of this thesis. Instead, the aim is to facilitate future machine learning by providing a robust means to gather ground-truth GSR and candidate predictor signals in unison.

### Specific objectives

The following specific objectives have been defined to achieve this aim:

#### Objective 1: Multi-modal platform development

Design and develop a modular data acquisition system capable of recording synchronized physiological and imaging data. This involves integrating a wearable GSR sensor and camera-based sensors into one platform.

In practice, the system will use:
- A research-grade **Shimmer3 GSR+** device for ground-truth skin conductance measurement [^18]
- A **thermal infrared camera (Topdon TC001)** attached to a smartphone for capturing thermal video [^19]
- The smartphone's own **RGB camera** for high-resolution video

A smartphone-based sensor node will be coordinated with a desktop controller application to start/stop recordings in unison and timestamp data streams consistently. The architecture should ensure that all modalities can be recorded simultaneously with millisecond-level timestamp alignment.

#### Objective 2: Synchronized data acquisition and management

Implement methods for precise time synchronization and data handling across devices. A custom control and synchronization layer (developed in Python) will coordinate the sensor node(s) and ensure that GSR readings, thermal frames, and RGB frames are logged with synchronized timestamps.

This objective includes establishing a reliable communication protocol between the smartphone and the PC controller to transmit control commands and streaming data [^20]. It also involves data management aspects: storing the multi-modal data with appropriate formats and metadata so that they can be easily combined for analysis.

By the end, the platform should produce a well-synchronized dataset (e.g. timestamps of physiological samples aligned with video frame times) that can serve as a training corpus for machine learning.

#### Objective 3: System validation through pilot data collection

Evaluate the integrated platform's performance and data integrity in a real recording scenario. To verify that the system meets research-grade requirements, a series of test recording sessions will be conducted.

For example, pilot experiments might involve human participants performing tasks designed to elicit varying GSR responses (stress, stimuli, etc.) while the platform records all modalities. The validation will focus on:

- **Temporal synchronization accuracy** (e.g. confirming that events are correctly aligned across sensor streams)
- **Signal quality assessment** (such as signal-to-noise ratio of GSR, resolution of thermal data, etc.)

We will analyze the collected data to ensure that the GSR signals and the corresponding thermal/RGB data show the expected correlations or time-locked changes. Successful validation will demonstrate that the platform can reliably capture synchronized multi-modal data suitable for subsequent machine learning analysis.

*(Developing the predictive model itself is left for future work; here we concentrate on validating the data pipeline that would feed such a model.)*

By accomplishing these objectives, the thesis will deliver a proven multi-sensor data collection platform that fills the current technological gap. This platform will enable researchers to build multimodal datasets for GSR prediction, accelerating progress toward truly contactless and real-time stress monitoring systems.

The emphasis is on creating a flexible, extensible setup – a modular sensing system – that not only integrates the specific devices in this project (GSR sensor and thermal/RGB cameras) but can be extended to additional modalities in the future. Ultimately, this work lays the groundwork for future studies to train and test machine learning algorithms that estimate GSR from camera data, by first solving the critical challenge of acquiring synchronized ground-truth data.

---

## 1.3 Thesis outline

This thesis is organized into six chapters, following a logical progression from background concepts through system development to evaluation:

### Chapter 2: Background and research context

This chapter reviews the relevant literature and technical background underpinning the project. It discusses physiological computing and emotion recognition, the significance of GSR in stress research, and prior approaches to contactless physiological measurement. Key related works in multimodal data collection and sensor fusion are examined to highlight the state of the art and the gap that this research addresses. The chapter also introduces the rationale behind the selected sensors (Shimmer3 GSR+ and Topdon thermal camera) and the expected advantages of a multimodal approach.

### Chapter 3: Requirements analysis

In this chapter, the specific requirements for the data collection platform are defined. The research problem is analyzed in detail to derive both functional requirements (such as the ability to record multiple streams concurrently, synchronization accuracy, user interface needs for the recording system) and non-functional requirements (such as system reliability, timing precision, and data storage considerations). Use-case scenarios and user stories are presented to ground the requirements in practical research situations. By the end of this chapter, the scope of the system and the criteria for success are clearly established.

### Chapter 4: System design and architecture

This chapter describes the design of the proposed multi-modal recording system. It presents the overall architecture, detailing how hardware components and software modules interact. Key design decisions are discussed, such as the choice of a distributed setup with an Android smartphone as a sensor hub and a PC as a central controller [^21].

The chapter covers:
- **Hardware integration** (mounting and connecting the thermal camera to the phone, Bluetooth pairing with the GSR sensor, etc.)
- **Software structure** into modules for camera capture, sensor communication, network synchronization, and data logging

Diagrams are provided to illustrate the flow of data and control commands between the Android app and the Python desktop application. The design ensures modularity, so that each sensing component (thermal, RGB, GSR) can operate in sync under the coordination of the central controller.

Important considerations like timestamp synchronization protocols, latency handling, and error recovery mechanisms are also described here.

### Chapter 5: Implementation testing and validation

In this chapter, the focus is on evaluating the implemented platform and demonstrating that it meets the thesis objectives. The evaluation methodology is first outlined, including the test setup and metrics for assessing synchronization and data quality.

Results from pilot recordings are then presented: for example, timing logs verifying that the disparity between camera frame timestamps and GSR signal timestamps is within acceptable bounds (on the order of milliseconds), and qualitative examples of data (such as parallel plots of GSR peaks alongside thermal video frames during a stress event).

The chapter discusses any challenges encountered during testing – for instance, connectivity issues or drift in clocks – and how they were resolved or mitigated. We interpret the results to confirm that the system can reliably produce synchronized multi-modal datasets.

This validation demonstrates the platform's capability to serve as a data collection tool for future GSR prediction research. Any limitations observed (such as minor synchronization offsets or sensor noise issues) are also noted to inform future improvements.

### Chapter 6: Conclusion and future work

The final chapter summarizes the contributions of the thesis and reflects on the extent to which the objectives were achieved. The achievements of developing a working multi-modal physiological data collection platform are highlighted, and the significance of this platform for the research community is discussed.

The chapter also candidly addresses the limitations of the current system (for example, if real-time analysis was not implemented or if certain environments were not tested). Finally, it outlines future work and recommendations – including:

- **Next steps** of using the collected data to train machine learning models for GSR prediction
- **Improving the platform's real-time capabilities**
- **Extending the system** with additional sensors (such as heart rate or respiration sensors) to broaden its application

By charting these future directions, the thesis concludes with a roadmap for transitioning from this data collection foundation to full-fledged real-time GSR inference in forthcoming research.

---

## References

[^1]: Critchley, H. D. (2002). Electrodermal responses: what happens in the brain. *The Neuroscientist*, 8(2), 132-142.

[^2]: Boucsein, W. (2012). *Electrodermal activity*. Springer Science & Business Media.

[^3]: Apple Inc. (2021). Apple Watch Series 7 - Health features. Retrieved from developer.apple.com

[^4]: Samsung Electronics. (2021). Galaxy Watch4 - Advanced health monitoring. Retrieved from samsung.com

[^5]: Fowles, D. C., Christie, M. J., Edelberg, R., Grings, W. W., Lykken, D. T., & Venables, P. H. (1981). Publication recommendations for electrodermal measurements. *Psychophysiology*, 18(3), 232-239.

[^6]: Healey, J. A., & Picard, R. W. (2005). Detecting stress during real-world driving tasks using physiological sensors. *IEEE Transactions on Intelligent Transportation Systems*, 6(2), 156-166.

[^7]: Poh, M. Z., Swenson, N. C., & Picard, R. W. (2010). A wearable sensor for unobtrusive, long-term assessment of electrodermal activity. *IEEE Transactions on Biomedical Engineering*, 57(5), 1243-1252.

[^8]: McDuff, D., Gontarek, S., & Picard, R. W. (2014). Remote detection of photoplethysmographic systolic and diastolic peaks using a digital camera. *IEEE Transactions on Biomedical Engineering*, 61(12), 2948-2954.

[^9]: Kosonogov, V., De Zorzi, L., Honoré, J., Martínez-Velázquez, E. S., Nandrino, J. L., Martinez-Selva, J. M., & Sequeira, H. (2017). Facial thermal variations: A new marker of emotional arousal. *PLoS One*, 12(9), e0183592.

[^10]: Ioannou, S., Gallese, V., & Merla, A. (2014). Thermal infrared imaging in psychophysiology: potentialities and limits. *Psychophysiology*, 51(10), 951-963.

[^11]: Verkruysse, W., Svaasand, L. O., & Nelson, J. S. (2008). Remote plethysmographic imaging using ambient light. *Optics Express*, 16(26), 21434-21445.

[^12]: Balakrishnan, G., Durand, F., & Guttag, J. (2013). Detecting pulse from head motions in video. *Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition*, 3430-3437.

[^13]: Picard, R. W., Vyzas, E., & Healey, J. (2001). Toward machine emotional intelligence: Analysis of affective physiological state. *IEEE Transactions on Pattern Analysis and Machine Intelligence*, 23(10), 1175-1191.

[^14]: Kim, J., & André, E. (2008). Emotion recognition based on physiological changes in music listening. *IEEE Transactions on Pattern Analysis and Machine Intelligence*, 30(12), 2067-2083.

[^15]: Garg, S., Pottie, G. J., & Kaiser, W. J. (2014). Wireless sensor networks: challenges and opportunities. *In Handbook of sensor networks* (pp. 1-19). CRC Press.

[^16]: Chen, D., & Varshney, P. K. (2004). QoS support in wireless sensor networks: a survey. *In Proceedings of the 2004 international conference on wireless networks* (pp. 227-233).

[^17]: Posada-Quintero, H. F., & Chon, K. H. (2020). Innovations in electrodermal activity data collection and signal processing: A systematic review. *Sensors*, 20(2), 479.

[^18]: Shimmer Research. (2020). Shimmer3 GSR+ Development Kit User Manual. Retrieved from shimmersensing.com

[^19]: Topdon. (2021). TC001 Thermal Camera for Android Specifications. Retrieved from topdon.com

[^20]: Tanenbaum, A. S., & Van Steen, M. (2017). *Distributed systems: principles and paradigms*. Prentice-Hall.

[^21]: Coulouris, G., Dollimore, J., Kindberg, T., & Blair, G. (2011). *Distributed systems: concepts and design*. Addison-Wesley.

---

**Document Information:**
- **Title:** Chapter 1: Introduction - Multi-sensor recording system for contactless GSR prediction research
- **Student:** Computer Science Master's Student  
- **Date:** 2024
- **Institution:** University Research Program
- **Version:** 1.0
- **Keywords:** physiological computing, GSR, contactless measurement, multi-modal sensing, data synchronization