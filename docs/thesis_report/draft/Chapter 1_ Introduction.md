# Chapter 1: Introduction

## Background and Motivation

Galvanic Skin Response (GSR), also known as Electrodermal Activity (EDA)
or skin conductance, refers to changes in the skin's electrical
conductance caused by sweat gland
activity[\[1\]](https://www.mdpi.com/2076-3417/14/24/11997#:~:text=The%20GSR%2C%20or%20EDA%2C%20refers,reliable%20biomarker%20for%20stress%20conditions).
These minute changes in skin conductance are modulated by the
sympathetic nervous system, making GSR a reliable biomarker of
physiological arousal and
stress[\[1\]](https://www.mdpi.com/2076-3417/14/24/11997#:~:text=The%20GSR%2C%20or%20EDA%2C%20refers,reliable%20biomarker%20for%20stress%20conditions).
In fact, GSR has been a fundamental tool in psychophysiology and
psychology for over a
century[\[2\]](https://www.mdpi.com/1424-8220/20/2/479#:~:text=The%20electrodermal%20activity%20,techniques%2C%20creating%20a%20growing%20pool).
It is well-recognized as a primary indicator of emotional arousal and
stress
levels[\[3\]](https://www.mdpi.com/2076-3417/14/24/11997#:~:text=with%20stress%20responses,stress%2C%20achieving%20an%20accuracy%20of),
since increased sweat due to stress directly raises skin conductance.
Unlike heart rate or other signals, which an individual may partially
control, skin conductance cannot be consciously regulated, providing an
**unfiltered window** into autonomic nervous system
activity[\[4\]](https://www.mdpi.com/2076-3417/14/24/11997#:~:text=Modern%20versions%20of%20these%20devices,are%20therefore%20crucial%20for%20determining).
This makes GSR especially valuable for studies of emotion, stress, and
cognitive load, where involuntary physiological responses are of
interest. *Comment: Consider expanding this paragraph with a real-world
example of GSR usage (e.g., how GSR is used in lie detector tests or
wearable stress trackers to illustrate its applications).*

Despite its value, traditional methods of measuring GSR have significant
drawbacks. **Conventional GSR sensors require direct skin contact** via
electrodes (typically attached to fingers or palms), often with
conductive gel. This contact-based approach is **intrusive** and can
interfere with natural behavior. Participants may feel discomfort or
awareness of the electrodes, which can itself alter their emotional
state and introduce artifacts into the
data[\[5\]](https://github.com/buccancs/bucika_gsr/blob/1b7d1a690e1921a2d0671c77665faa5ea994c864/docs/thesis_report/Chapter_2_Context_and_Literature_Review.md#L50-L58).
Moreover, the need to attach electrodes means measurements usually occur
in controlled environments (e.g., a lab), as movement is restricted by
wires or
devices[\[5\]](https://github.com/buccancs/bucika_gsr/blob/1b7d1a690e1921a2d0671c77665faa5ea994c864/docs/thesis_report/Chapter_2_Context_and_Literature_Review.md#L50-L58).
Long-term or ambulatory monitoring is impractical with attached
electrodes due to issues of comfort, skin irritation, and maintenance
(e.g., gel drying or sensor slippage). There are also hygiene and safety
concerns when sharing electrode-based devices between subjects, as well
as the burden of calibrating and cleaning equipment between uses. These
limitations motivate the search for **contactless GSR measurement**
techniques that can capture the same stress-related signals *without*
requiring physical contact.

## Problem Statement

Given the above constraints, the core problem addressed in this thesis
is the **lack of a non-intrusive, real-time GSR measurement method for
natural settings**. Traditional contact sensors, while accurate, are
impractical for continuous or real-world stress monitoring due to their
intrusiveness. Conversely, truly contactless GSR solutions are **not yet
mature**. To date, no validated contactless system exists that can
reliably measure GSR in real time during unconstrained, daily
activities. Initial research efforts have explored proxy measures of GSR
using remote sensing -- for example, camera-based detection of sweat
activity on the
palm[\[6\]](https://pubmed.ncbi.nlm.nih.gov/33018348/#:~:text=This%20paper%20presents%20a%20proof,used%20in%20affective%20computing%20and)
or millimeter-wave radar reflections -- but these remain at the
proof-of-concept stage. Their accuracy has been limited (often only
**60--70% correlation** with electrode-based GSR in controlled
tests[\[7\]](https://github.com/buccancs/bucika_gsr/blob/1b7d1a690e1921a2d0671c77665faa5ea994c864/docs/new_documentation/README_project_context.md#L69-L76)),
and they typically require controlled lighting or positioning. In other
words, **a clear gap exists**: we lack a proven technology that can
perform **contactless, real-time GSR monitoring with fidelity comparable
to traditional methods** under realistic conditions. This thesis
directly tackles that gap by investigating and developing a system for
contactless GSR data acquisition.

## Project Aim and Objectives

The overall aim of this project is to **develop a synchronized
multi-modal platform for contactless GSR data acquisition** that
achieves accuracy approaching that of conventional contact-based sensors
in real time. *Comment: Could clarify the term "multi-modal" here for
non-expert readers (i.e., using multiple sensor types, such as thermal
imaging and electrical sensors, together).* To fulfill this aim, the
project is broken down into several concrete objectives:

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
  system's reliability (e.g., data loss, synchronization errors) and
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

## Research Contributions

This thesis yields several novel contributions to the field of
psychophysiological sensing and data acquisition systems:

- **Contactless GSR Measurement Platform:** We present a
  first-of-its-kind **real-time contactless GSR acquisition platform**
  that combines consumer-grade devices to achieve research-grade
  physiological measurements. The system integrates a low-cost thermal
  camera (*Topdon TC001*) with a wearable GSR sensor (*Shimmer3 GSR+*)
  and standard RGB cameras, all synchronized within a unified framework.
  This platform demonstrates that it is possible to gather GSR-related
  signals without direct skin contact, by leveraging multi-sensor data
  fusion in real time.
- **Multi-Modal Sensor Fusion Approach:** A key contribution of this
  work is the development of a **multi-modal data fusion and
  synchronization technique** for physiological signals. The project
  implements robust methods to align thermal imaging data with
  electrodermal signals and fuses them to produce a continuous estimate
  of GSR. This includes novel algorithms for handling differences in
  sampling rates and network latencies between mobile devices, ensuring
  that the contactless measurements are temporally and spatially
  coordinated with traditional measurements to within scientific
  precision (on the order of
  milliseconds[\[9\]](https://github.com/buccancs/bucika_gsr/blob/1b7d1a690e1921a2d0671c77665faa5ea994c864/docs/new_documentation/README_project_context.md#L114-L122)[\[10\]](https://github.com/buccancs/bucika_gsr/blob/1b7d1a690e1921a2d0671c77665faa5ea994c864/docs/new_documentation/README_project_context.md#L129-L137)).
- **Integration of Thermal Imaging for GSR Estimation:** We demonstrate
  the *first integration of a thermal imaging sensor specifically for
  GSR estimation purposes*. Prior research in affective computing has
  used cameras for heart rate or facial expressions; here, we extend the
  paradigm by using thermal video of the skin (e.g., the palm) to detect
  sweat gland activity related to GSR. This contribution includes an
  analysis of *where* and *how* thermal changes correlate with
  electrodermal activity, providing insights into using infrared
  technology for psychophysiological monitoring.
- **Evaluation Framework and Empirical Validation:** The thesis
  contributes an **evaluation methodology** for contactless GSR systems,
  including a set of quantitative metrics and experimental protocols for
  validation. We conducted controlled experiments and provide a thorough
  analysis of the system's accuracy, comparing the contactless GSR
  readings against the gold-standard electrode measurements. The
  results, which are documented in the thesis, offer evidence of the
  system's performance (e.g., achieving a strong correlation with
  traditional GSR and identifying the conditions under which accuracy
  degrades). This is accompanied by discussions on error sources, such
  as motion artifacts or environmental influences, and how they can be
  mitigated, thereby laying a foundation for future studies to build
  upon these validation techniques.
- **Open-Source Tools and Documentation:** In the spirit of reproducible
  research, the project delivers its software as a modular, open-source
  toolset. All system components, from the Android-based thermal camera
  interface to the desktop synchronization and analysis program, are
  documented and released for the community. This lowers the barrier for
  other researchers to replicate or extend contactless GSR measurement
  in their own work, amplifying the impact of our contributions.

## Scope and Limitations

It is important to delineate the scope of this project and acknowledge
its limitations. This work focuses on establishing the feasibility of
**palm-based, contactless GSR measurement in a controlled setting**. The
emphasis is on data acquisition and signal estimation accuracy, rather
than on end-to-end application in every possible environment. Key scope
boundaries and limitations include:

- **Specific Measurement Site:** The contactless GSR estimation in this
  project is limited to the **palmar region** of the hand. The palm (and
  fingers) were chosen due to their high density of sweat glands that
  produce strong GSR signals. Other potential sites (feet, forehead,
  etc.) were not explored, and the findings are thus specific to hand
  perspiration. The algorithms and calibration are tuned to this
  region's thermal and optical characteristics.
- **Controlled Environment:** All evaluation experiments were conducted
  in a **laboratory or controlled indoor environment**. Factors like
  ambient temperature, lighting, and participant posture were managed to
  reduce variability. As a result, the system's robustness to outdoor
  conditions, varying temperatures, motion, or complex backgrounds was
  not fully tested. The performance reported is for the controlled-case;
  deploying the system in **natural everyday scenarios** (with
  uncontrolled motion, weather, or lighting) may require additional
  adaptation and was outside the immediate scope.
- **Participant Diversity:** The validation was performed on a limited
  sample of participants (e.g., a certain number of volunteers in a lab
  study). While efforts were made to include both genders and varied
  skin tones, the sample is not large enough to guarantee broad
  demographic generalizability. The **physiological variability**
  between individuals (such as differing sweating responses or skin
  properties) means results may vary beyond the tested group. This
  project did not encompass long-term studies or large population
  trials.
- **Temporal Resolution and Latency:** The system is designed for
  real-time operation with high temporal precision; however, slight
  delays (on the order of tens of milliseconds) are inherent in
  processing and data transmission. While these are negligible for many
  applications, the setup might not capture extremely rapid GSR
  transients as precisely as a benchtop system with direct electrodes.
  Additionally, synchronization between devices, while carefully
  engineered, could drift over very long sessions (many hours) --
  extended continuous operation was not extensively characterized.
- **Not a Complete Stress Intervention Tool:** The scope of this thesis
  is on data acquisition and measurement. Interpreting the GSR data in
  terms of psychological states (beyond basic stress arousal levels) or
  integrating it into a feedback loop (e.g., for biofeedback or alert
  systems) is not covered. For example, we do not develop a full
  **stress detection application** for end-users; rather, we focus on
  validating that we can capture the GSR signal itself without contact.
  Future work would be needed to apply the data for specific
  interventions or to combine it with other modalities like ECG or EEG
  for a comprehensive affective computing system.

By clarifying these limitations, we recognize that while the project
demonstrates a significant step toward contactless GSR monitoring, it is
**not** a fully universal solution. The findings and system are a
foundation that future research can build upon, for instance, by
extending to more environments, refining algorithms for robustness, or
scaling up the validation.

## Thesis Structure

The remainder of this thesis is organized as follows:

- **Chapter 2: Context and Literature Review** -- This chapter situates
  the project in the context of existing research. It reviews the
  relevant literature on GSR/EDA measurement techniques, including
  traditional electrode-based methods and prior attempts at contactless
  sensing. Key theoretical foundations (such as the physiological basis
  of EDA and principles of thermal imaging) are introduced. The chapter
  also identifies gaps in the state of the art that the project aims to
  fill, and it outlines related work in multi-sensor data fusion and
  distributed recording systems that informed our approach.
- **Chapter 3: System Requirements and Analysis** -- This chapter
  translates the research problem into specific requirements for the
  system to be developed. It presents a detailed problem analysis and
  the design requirements derived from the objectives. Functional
  requirements (like synchronization accuracy, data throughput, and user
  interface needs) and non-functional requirements (such as reliability,
  usability, and safety considerations) are documented. We also discuss
  the rationale behind key design decisions, including the choice of
  hardware (Android devices, Topdon thermal camera, Shimmer sensor) and
  software architecture, in light of these requirements.
- **Chapter 4: Design and Implementation** -- This chapter provides a
  comprehensive description of the system's design and its
  implementation details. It describes the overall system architecture,
  including how the mobile components (for camera and sensor data
  capture) communicate with the desktop controller. The chapter covers
  the hardware setup (mounting and connectivity of the thermal camera
  and GSR sensor) and the software modules for each component. We delve
  into the distributed system aspects like how multiple devices are
  synchronized over a network and how data is logged and transmitted.
  Key algorithms -- for example, the image processing steps to extract
  GSR-related features from thermal video, and the calibration algorithm
  mapping those features to GSR values -- are explained. Implementation
  challenges and the solutions or workarounds applied (such as ensuring
  time synchronization or managing thermal camera frame rates) are also
  discussed.
- **Chapter 5: Experimental Evaluation and Results** -- In this chapter,
  we describe the experimental methodology used to test the system and
  we present the results of these evaluations. The chapter starts with
  the design of the experiments (e.g., the protocol for inducing stress
  responses in participants, how data was collected and annotated) and
  the evaluation metrics used. It then reports the empirical results,
  such as the correlation between contactless and contact GSR readings,
  error analysis, and examples of GSR response waveforms captured by the
  system. We include statistical analyses to assess whether the
  contactless measurements differ significantly from the traditional
  method, and we evaluate performance criteria like real-time
  responsiveness and data loss rates. Visualizations (graphs of GSR
  signals over time, etc.) and tables summarize the findings.
- **Chapter 6: Discussion and Conclusion** -- The final chapter
  interprets the results and discusses the implications of the work. We
  assess to what extent the project objectives were met and how the
  findings support (or sometimes contradict) expectations based on the
  literature. The chapter addresses the limitations of the current
  system in more detail, reflecting on how factors like environment and
  individual differences may impact the contactless measurement. We also
  discuss potential improvements and **future work** -- for instance,
  how machine learning could enhance the GSR estimation, or how the
  system could be adapted for outdoor use or integrated into wearable
  form factors. Finally, the chapter concludes the thesis by summarizing
  the key contributions and the significance of achieving contactless
  GSR data acquisition, and it offers closing thoughts on the path
  forward for truly ubiquitous stress measurement technologies.

------------------------------------------------------------------------

[\[1\]](https://www.mdpi.com/2076-3417/14/24/11997#:~:text=The%20GSR%2C%20or%20EDA%2C%20refers,reliable%20biomarker%20for%20stress%20conditions)
[\[3\]](https://www.mdpi.com/2076-3417/14/24/11997#:~:text=with%20stress%20responses,stress%2C%20achieving%20an%20accuracy%20of)
[\[4\]](https://www.mdpi.com/2076-3417/14/24/11997#:~:text=Modern%20versions%20of%20these%20devices,are%20therefore%20crucial%20for%20determining)
Galvanic Skin Response and Photoplethysmography for Stress Recognition
Using Machine Learning and Wearable Sensors

<https://www.mdpi.com/2076-3417/14/24/11997>

[\[2\]](https://www.mdpi.com/1424-8220/20/2/479#:~:text=The%20electrodermal%20activity%20,techniques%2C%20creating%20a%20growing%20pool)
Innovations in Electrodermal Activity Data Collection and Signal
Processing: A Systematic Review

<https://www.mdpi.com/1424-8220/20/2/479>

[\[5\]](https://github.com/buccancs/bucika_gsr/blob/1b7d1a690e1921a2d0671c77665faa5ea994c864/docs/thesis_report/Chapter_2_Context_and_Literature_Review.md#L50-L58)
Chapter_2_Context_and_Literature_Review.md

<https://github.com/buccancs/bucika_gsr/blob/1b7d1a690e1921a2d0671c77665faa5ea994c864/docs/thesis_report/Chapter_2_Context_and_Literature_Review.md>

[\[6\]](https://pubmed.ncbi.nlm.nih.gov/33018348/#:~:text=This%20paper%20presents%20a%20proof,used%20in%20affective%20computing%20and)
Towards Contactless Estimation of Electrodermal Activity Correlates -
PubMed

<https://pubmed.ncbi.nlm.nih.gov/33018348/>

[\[7\]](https://github.com/buccancs/bucika_gsr/blob/1b7d1a690e1921a2d0671c77665faa5ea994c864/docs/new_documentation/README_project_context.md#L69-L76)
[\[8\]](https://github.com/buccancs/bucika_gsr/blob/1b7d1a690e1921a2d0671c77665faa5ea994c864/docs/new_documentation/README_project_context.md#L71-L76)
[\[9\]](https://github.com/buccancs/bucika_gsr/blob/1b7d1a690e1921a2d0671c77665faa5ea994c864/docs/new_documentation/README_project_context.md#L114-L122)
[\[10\]](https://github.com/buccancs/bucika_gsr/blob/1b7d1a690e1921a2d0671c77665faa5ea994c864/docs/new_documentation/README_project_context.md#L129-L137)
README_project_context.md

<https://github.com/buccancs/bucika_gsr/blob/1b7d1a690e1921a2d0671c77665faa5ea994c864/docs/new_documentation/README_project_context.md>
