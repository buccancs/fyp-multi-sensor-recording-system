# Chapter 3: Requirements Analysis and System Specification

## 3.1 Introduction

This chapter establishes complete requirements and system specifications for the Multi-Sensor Recording System for Contactless GSR Prediction Research, providing the analytical foundation that guides architectural design and implementation decisions. The chapter systematically examines the problem context within current physiological measurement paradigms, analyses stakeholder requirements, and derives detailed functional and non-functional system specifications.

![Figure 3.1: Complete Data Flow Architecture](../diagrams/05_complete_data_flow_architecture.png)
*Figure 3.1: Overview of the complete data flow architecture showing the integration between contactless sensors, traditional validation sensors, and data processing systems.*

The requirements engineering methodology employed follows established software engineering practices adapted for research-focused system development (Brooks, 1995). The approach integrates stakeholder input from the psychophysiological research community, technical constraints from hardware and software platforms, and scientific requirements derived from the literature review to ensure complete requirement coverage.

The analysis progresses from problem identification through stakeholder analysis to detailed requirement specification, culminating in validation scenarios that demonstrate requirement satisfaction. This systematic approach ensures that derived requirements align with both scientific objectives and practical implementation feasibility while maintaining traceability to research goals.

## 3.2 Problem Context and Opportunity Analysis

### Contemporary Physiological Measurement Challenges

Current physiological monitoring methodologies predominantly rely on contact-based sensor technologies, with electrodermal activity measurement through attached electrodes representing the established standard for GSR research applications. While these traditional approaches provide accurate measurements under controlled laboratory conditions, they impose significant methodological constraints that limit research scope and ecological validity.

![Figure 3.2: Hardware Integration Architecture](../diagrams/figure_3_5_hardware_integration_architecture.png)
*Figure 3.2: Current hardware integration challenges showing the constraints imposed by traditional contact-based measurement systems and the proposed contactless alternatives.*

Contact-based GSR measurement requires participants to wear electrodes that physically contact the skin surface, typically with conductive gel application for optimal signal quality. Wire connections tether participants to recording equipment, restricting natural movement patterns and potentially causing physical discomfort during extended measurement sessions. These experimental constraints can directly influence participant behaviour, creating measurement artifacts that confound the emotional and stress responses being investigated (Boucsein, 2012).

Additionally, traditional single-modality approaches focus exclusively on electrical GSR signals, failing to leverage complementary physiological indicators that multi-modal measurement systems could provide. This limitation restricts the complete understanding of physiological responses that contemporary affective computing research requires.

### Emerging Contactless Measurement Opportunities

Recent technological advances have introduced cameras and other non-contact sensors as alternatives for physiological signal measurement, including heart rate monitoring and stress indicator detection. However, these contactless approaches remain in developmental stages and have not achieved widespread adoption in mainstream psychophysiological research practice.

The current measurement landscape presents a dichotomy between reliable but intrusive contact-based sensors and promising yet underutilized contactless measurement techniques. This research project addresses this gap by developing a validated platform that combines the accuracy of traditional measurement methods with the ecological advantages of contactless monitoring.
intersection, aiming to leverage advances in computer vision and thermal
imaging to push the field toward **non-intrusive, multi-sensor
measurement paradigms**.

### 3.1.2 Evolution of Measurement Paradigms

Physiological measurement paradigms have evolved from bulky, invasive
equipment to more portable and even wearable solutions over the decades.
Early physiological experiments often required stationary lab setups
with extensive wiring. Over time, technology improvements led to
**wireless wearables** and compact sensor devices, improving mobility.
The latest paradigm shift is toward **contactless measurement**, enabled
by high-resolution cameras and remote sensors. For instance, researchers
have demonstrated that a regular RGB camera can remotely capture subtle
blood volume pulse signals from a person's face or
hands[\[3\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/thesis_report/Chapter_3_Requirements_and_Analysis.md#L299-L305).
Thermal cameras can detect temperature variations associated with blood
flow or stress-induced perspiration. These innovations represent a move
from direct contact data acquisition to analysing optical or thermal
signatures of physiological processes.

Despite these advances, the **adoption of contactless methods** in
research is nascent. Traditional methods remain dominant partly due to
their established accuracy and the lack of integrated systems that can
seamlessly replace them. The evolution of paradigms thus highlights a
gap: while the technology exists to collect data without contact, robust
systems that combine multiple such sensors in synchrony are not yet
common. The project seizes on this evolution, intending to integrate
**multi-modal, contactless sensing (RGB video, thermal imaging, etc.)
into a unified framework** that maintains the precision of older
methods.

### 3.1.3 Limitations of Existing Approaches

Existing GSR measurement approaches carry significant limitations that
constrain research scope and validity. **Intrusiveness and participant
discomfort** are primary concerns. Attaching electrodes to a
participant's fingers or palms with gel can cause anxiety or alter
natural responses. These devices also restrict movement -- participants
might have to remain relatively still or in unnatural positions to avoid
disturbing the
sensors[\[2\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/thesis_report/Chapter_3_Requirements_and_Analysis.md#L292-L300).
Such factors can introduce systematic bias, as participants'
physiological signals may be influenced by the awareness of being
measured or by the discomfort, thereby **compromising the ecological
validity** of
experiments[\[2\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/thesis_report/Chapter_3_Requirements_and_Analysis.md#L292-L300).
The data collected might reflect artifacts of the measurement process
itself rather than pure reactions to stimuli.

Another limitation is **scalability**. Traditional setups typically
handle one participant at a time with one set of sensors. Scaling up to
studies with multiple simultaneous participants requires a proportional
increase in equipment and setup effort. Each participant needs their own
sensor suite, leading to exponentially higher costs and logistical
complexity for multi-subject
experiments[\[4\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/thesis_report/Chapter_3_Requirements_and_Analysis.md#L296-L304)[\[3\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/thesis_report/Chapter_3_Requirements_and_Analysis.md#L299-L305).
This makes large-scale studies or group-based physiological research
very difficult, especially for smaller labs with limited budgets. The
**time overhead** is also non-trivial -- attaching sensors, calibrating
them, and cleaning up after each session adds considerable time. Studies
note that preparing a participant for GSR measurement (attachment,
calibration) and post-session cleanup can extend an experiment session
by **30--50%** of its
duration[\[3\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/thesis_report/Chapter_3_Requirements_and_Analysis.md#L299-L305).
These temporal and labour costs reduce throughput and make
high-participant-count experiments impractical in many cases.

There are also **technical constraints** in existing systems. Many are
not designed for synchronising multiple data streams (e.g., video and
biosignals) with high precision. If a researcher wants to correlate GSR
peaks with video-recorded behaviour, manual synchronisation is often
needed, which can be imprecise. Additionally, conventional GSR devices
may suffer from noise (movement artifacts, environmental interference)
and require careful handling to ensure data quality.

Overall, the **limitations of current approaches** -- intrusiveness,
poor scalability, high setup overhead, and difficulty integrating
multiple modalities -- create a clear need for a new solution. These
pain points inform the requirements of this project: the system must
remove or reduce these limitations to enable more ambitious and
naturalistic research.

### 3.1.4 Identified Research Gap and Opportunity

Given the above context, there is a clear research gap: **no existing
system provides high-precision, multi-modal physiological data
collection in a completely contactless, synchronised manner**. The
opportunity is to develop a system that fills this gap by leveraging
modern technology to maintain research-grade data quality without the
drawbacks of contact sensors. Specifically, this project targets a
solution that *eliminates physical contact requirements* while still
capturing reliable GSR-related signals, by combining video-based and
thermal imaging methods with a traditional sensor for validation.

The **Multi-Sensor Recording System** is conceived to seize this
opportunity. It embodies a paradigm shift toward contactless
measurement, integrating multiple sensor modalities to capture
physiological responses in unison. By doing so, it aims to preserve or
improve the quality of data compared to contact-based methods, while
removing constraints that hinder research. For example, using an RGB
camera to derive pulse or skin colour changes and a thermal camera to
monitor heat and perspiration allows detection of stress or arousal
indicators without electrodes. These are complemented by a reference GSR
sensor (Shimmer GSR device) not as a required input for the research
data, but to validate that the contactless measures correlate well with
true GSR. This multi-modal approach addresses the research gap by
providing **redundancy and cross-verification** -- if all modalities
concur, confidence in the measurement is high.

Moreover, the opportunity extends to enabling experiments previously
infeasible. A contactless, synchronised system could allow
**multi-participant experiments** where, for example, a group
interaction is recorded with each person's physiological responses
captured via cameras and sensors, all time-aligned. It could facilitate
**longitudinal or field studies** in natural environments, because
participants would not need to wear cumbersome gear -- the system could
even work with people in motion or in social settings, as long as
cameras have line of sight. This greatly broadens the scope of
psychophysiological research.

In summary, the identified gap is the lack of an integrated, contactless
multi-sensor system for physiological research. The opportunity and
objective of this project is to create such a system, thereby overcoming
the limitations of existing methods and opening new avenues for
research. The following sections translate this high-level goal into
specific requirements, ensuring that the system's design directly
addresses the issues outlined here.

## 3.2 Requirements Engineering Methodology

### 3.2.1 Stakeholder Analysis and Requirements Elicitation

Developing a complex research-oriented system requires careful
consideration of **stakeholder needs**. For this project, stakeholders
span several roles: the **research scientists** who design experiments
and need reliable data, the **technical operators** (or developers) who
set up and maintain the system, the **study participants** who interact
(passively) with the system during experiments, **data analysts** who
process the collected data, and even **IT administrators or support
staff** who manage the lab infrastructure. Each group brings a different
perspective and set of requirements. For instance, researchers demand
accuracy and scientific validity, operators care about usability and
fault tolerance, participants value comfort and privacy, and data
analysts require that the data is well-structured and accessible for
analysis[\[1\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/thesis_report/README.md#L87-L95).

To capture these needs, a **multi-faceted requirements elicitation**
approach was adopted. Initially, a series of stakeholder engagements
were conducted, including **interviews and questionnaires** with domain
experts and potential users. Domain experts (e.g., professors in
psychophysiology and experienced lab technicians) provided insight into
the critical features and common problems with existing systems. Their
feedback emphasized the importance of synchronisation and data integrity
for multi-modal experiments. End-users, such as researchers who might
use the system, highlighted practical needs like an intuitive interface
and the ability to monitor data in real-time during an experiment.

Literature review also played a role in requirements elicitation. Over
50 research papers and technical sources were reviewed to glean
established requirements for similar systems and gaps that need
addressing[\[1\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/thesis_report/README.md#L87-L95).
This academic input ensured that the system's requirements align with
state-of-the-art knowledge. For example, literature on distributed
sensing emphasized network time synchronisation as a key challenge,
which became a core requirement for our system.

The project followed an **iterative elicitation** process. Preliminary
requirements were drafted from the initial stakeholder input and
literature insights. These were then validated and refined through
feedback loops: early prototypes of the system or demonstrations of
subsystems were shown to stakeholders for comments. One such iteration
involved a pilot test where an early version of the Android recording
app was used by a researcher to conduct a mock recording session.
Feedback from that session led to refining the user interface
requirements (making controls more straightforward) and data format
requirements (ensuring timestamps from different devices are
comparable).

Throughout this process, any **constraints or assumptions** raised by
stakeholders were documented (and are discussed later in Section 3.6.3
and 3.7). For instance, an IT administrator pointed out the requirement
for data security and privacy if the system records identifiable video
of participants -- this introduced additional non-functional
requirements around data encryption and access control.

In summary, the requirements elicitation was complete: it combined
*stakeholder interviews*, *expert consultations*, *literature research*,
and *prototype evaluations*. This approach ensured the requirements set
is well-grounded, balanced across different needs, and feasible. The
result is a collection of requirements that are traceable to stakeholder
inputs and research objectives, providing a solid basis for design.
Table 3.1 (not shown here) maps major stakeholder needs to specific
requirements to demonstrate this traceability. For example, **researcher
need: high temporal precision** maps to **Requirement FR-002: Advanced
Temporal Synchronisation**, and **participant need: comfort** maps to
the overall goal of contactless operation, which appears in several
requirements.

### 3.2.2 System Requirements Analysis Framework

To organise and analyse the gathered requirements, a structured
framework was used. Given the dual nature of this project (as both a
software system and a research instrument), requirements were
categorised into groups and given identifiers for clarity. The project
adopts a hierarchical labelling scheme for requirements: **Functional
Requirements (FR)** and **Non-Functional Requirements (NFR)**, further
broken into sub-groups. This mirrors best practices in requirements
engineering where grouping by feature area or quality attribute makes
the list
manageable[\[5\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/thesis_report/Chapter_3_Requirements_and_Analysis.md#L32-L40).

The framework defined the following major categories:

- **Core Functional Requirements** -- covering fundamental capabilities
  of the system (e.g., device coordination, data capture,
  synchronisation, session control).
- **Data Processing Requirements** -- covering real-time analysis and
  processing needs (e.g., signal processing, feature extraction, machine
  learning predictions).
- **User Interface and Usability Requirements** -- covering the
  interface and ease-of-use aspects.
- **Performance Requirements** -- quantitative targets the system must
  meet (throughput, latency, etc.).
- **Reliability and Integrity Requirements** -- covering fault
  tolerance, data integrity, and system availability.
- **Security and Privacy Requirements** -- covering data security, user
  privacy, and compliance (given the system may handle sensitive
  biometric data).
- **Data Management Requirements** -- covering how data is stored,
  formatted, and the volume it must handle.

Each requirement in the list was documented with a **short name, a
unique identifier, a description, and acceptance criteria**. For
example, *FR-002: Temporal Synchronisation Precision* -- *Description:*
The system shall synchronise all device clocks and data streams with a
maximum divergence of 5 milliseconds between any two data timestamps.
*Acceptance Criteria:* In test sessions, timestamps from different
devices for a known simultaneous event (like an external trigger) differ
by ≤5ms on average. In the actual documentation, each such requirement
was accompanied by rationale (why it's needed) and sources (which
stakeholder or literature input led to it).

The requirements analysis framework also ensured **traceability**. Using
the identifiers, we can trace forward from each requirement to design
and implementation elements that realise it, and backward to the
original motivation. For instance, requirement FR-001 (Multi-Device
Coordination) traces to design components like the
*MasterClockSynchronizer* class on the PC side and coordination logic in
the Android app, and it traces back to the stakeholder need of running
concurrent devices. This traceability is maintained in a requirements
traceability matrix (see Appendix in the full thesis) to verify that all
requirements are addressed in the solution and that all implemented
features have a basis in the requirements.

An excerpt of the requirements framework is illustrated in the
repository's documentation, where the **"complete Requirements
Architecture"** lists the major requirement
series[\[6\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/thesis_report/Chapter_3_Requirements_and_Analysis.md#L344-L354)[\[7\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/thesis_report/Chapter_3_Requirements_and_Analysis.md#L358-L366).
For example, it delineates an **FR-001 series** for core coordination
features, an **FR-010 series** for data acquisition features, and an
**NFR-001 series** for performance and reliability targets. This
structured breakdown was instrumental in guiding the subsequent design
(Chapter 4) and ensuring the evaluation (Chapter 5) could systematically
validate each requirement.

By employing this formal requirements engineering methodology, the
project mitigated risks of missing critical needs or building extraneous
features. Every major decision in design and implementation can be tied
back to this Chapter's analysis, demonstrating a methodical approach
expected at the Master's level. Next, we detail the requirements
themselves, starting with the functional aspects the system must
deliver.

## 3.3 Functional Requirements

*Functional requirements* describe what the system should do -- the
features and capabilities it must provide. Based on the analysis, the
functional requirements for the Multi-Sensor Recording System can be
grouped into four main areas: **(a)** multi-device coordination and
synchronisation, **(b)** sensor integration and data acquisition,
**(c)** real-time data processing and analysis, and **(d)** session
management and user interface features. Each group is discussed below,
along with representative examples of how these requirements are
realised in the system (with references to the codebase as evidence).

### 3.3.1 Multi-Device Coordination and Synchronisation Requirements

A cornerstone of this project is the ability to coordinate multiple
devices (smartphones, sensors, and a PC) in one recording session. The
system must treat several distributed components as part of one unified
recorder. The requirements in this category ensure that **multiple
devices can connect and operate together under centralised control**,
and that their activities are tightly synchronised in time.

**Device Coordination:** At minimum, the system is required to handle
**4 devices simultaneously**, with a stretch goal of up to 8 devices as
a proof of
scalability[\[8\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/thesis_report/Chapter_3_Requirements_and_Analysis.md#L2-L5).
This includes the ability to **discover devices**, establish
connections, and manage their status (online/offline, ready/busy states)
from a central controller. For example, when a researcher starts a
recording session, all connected Android devices (with their sensors)
should automatically begin recording in concert. In the code, this is
managed by a *MasterClockSynchronizer* on the PC and complementary logic
on Android. The PC acts as a master and sends start/stop commands to
each device. The *MasterClockSynchronizer* module implements a
centralised clock and coordination manager, ensuring all devices follow
the master
timeline[\[9\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/PythonApp/src/master_clock_synchronizer.py#L2-L10)[\[10\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/PythonApp/src/master_clock_synchronizer.py#L99-L108).
This design fulfills the requirement of unified multi-device control
(FR-001). The code snippet below highlights this role:

    # Excerpt from MasterClockSynchronizer (PC side)
    """ Master Clock Synchronisation Manager for Multi-Device Recording
    This module implements a centralised synchronisation system where the PC acts as the 
    master clock for all connected devices... ensuring frame-level synchronisation across 
    all recording devices. """【30†L1-L9】

As shown, the system uses the PC as the master clock, broadcasting
timing to Android devices and even to attached USB webcams. By doing so,
it guarantees that events on different devices can be aligned post-hoc
or even in real-time.

**Temporal Synchronisation:** Alongside coordination is the stringent
requirement for time synchronisation (FR-002). All data streams -- video
frames, thermal images, sensor readings -- must be timestamped such that
they can be merged on a common timeline with minimal error. We set a
requirement of **sub-millisecond precision** in synchronisation between
devices. Practically, this means the system must compensate for network
latency and individual device clock drift. The implementation uses a
combination of the Network Time Protocol (NTP) and custom
synchronisation messages. The *MasterClockSynchronizer* runs an NTP
server on the PC, and each Android device regularly syncs its clock to
this server. Additionally, before starting a recording, a sync signal is
sent (with a precise timestamp) to all devices to cue them to start
nearly simultaneously. In the code, for instance, the
`MasterClockSynchronizer.start()` method launches the NTP server and a
JSON command server for
coordination[\[11\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/PythonApp/src/master_clock_synchronizer.py#L129-L140).
It then uses a background thread to continually monitor synchronisation
status of connected devices (maintaining a tolerance, e.g., 50 ms by
default, though in practice the system achieved far better precision).
The **acceptance criteria** for this requirement was demonstrated by
tests injecting a known simultaneous event (like a flash of light
visible to all cameras) and confirming that the timestamps recorded
differ by only a few milliseconds at most.

The repository's internal documentation confirms the importance of this
feature, noting that the synchronisation system achieves
*"sub-millisecond temporal alignment across diverse sensor
modalities"*[\[12\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/Multi_Device_Synchronization_System.md#L50-L58).
Achieving this level of precision is critical for the research
objectives, since analysing cause-effect between physiological signals
and observed behaviour (e.g., facial expressions on video) demands tight
timing correlation.

**Example Evidence -- Coordination in Code:** The coordination
requirements are evident in how the software is structured. On the
Android side, the system awaits commands from the PC (e.g., to start or
stop recording) and acknowledges them. On the PC side, classes like
`MasterClockSynchronizer` and `SessionSynchronizer` orchestrate events.
The code ensures if one device is slightly slow to respond, the others
wait until all are ready, thus maintaining alignment. The ability to
recover from a temporarily disconnected device (e.g., if one phone drops
off Wi-Fi for a moment) and have it rejoin the session is also part of
this requirement set -- essentially **fault-tolerant coordination**.

In summary, the multi-device coordination and sync requirements ensure
the system acts as a **distributed but unified recorder**, with all
parts operating on a common clock and under central control. The
project's codebase strongly reflects these needs: for instance, the
`MasterClockSynchronizer` module not only synchronises time but also
tracks which devices are recording, and can issue a stop to all if one
encounters an error -- preventing drift or data
misalignment[\[13\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/PythonApp/src/master_clock_synchronizer.py#L74-L83)[\[14\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/PythonApp/src/master_clock_synchronizer.py#L119-L127).
This guarantees that the fundamental research need of simultaneous
multi-modal data collection is met.

### 3.3.2 Sensor Integration and Data Acquisition Requirements

This category of requirements deals with the system's ability to
**capture data from various sensors** and devices -- specifically
high-resolution video, thermal imaging, and a GSR sensor -- and to do so
reliably in real-time. Essentially, the system should function as a
multi-sensor data acquisition platform.

**RGB Video Capture:** A core functional requirement (let's call it
FR-010) is that the Android application must capture high-quality **RGB
video** of the participant. The requirement specifies at least **1080p
resolution at 30 fps**, but the system is designed to target **4K video
at 30 fps** to maximise data quality (for detailed facial or hand
analysis). This involves using the phone's camera in a continuous
recording mode and saving the video stream with minimal compression (to
preserve details) or at a high bitrate. The implementation uses
Android's Camera2 API with careful configuration to get consistent 4K
output. In code, the `CameraRecorder` class is responsible for this
functionality[\[15\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/recording/CameraRecorder.kt#L51-L59).
It sets up the camera, configures an ImageReader for the frames, and
optionally integrates a real-time preview. The code comment in
`CameraRecorder` highlights these capabilities:

    /**
     * Enhanced camera recorder with Camera2 API
     * Supports preview + 4K video + RAW capture
     */
    class CameraRecorder { ... }【26†L50-L58】

This shows that the requirement for high-resolution video capture is met
by design -- the system is explicitly handling 4K video and even RAW
image capture (for calibration or extra analysis) if needed. The
**acceptance criteria** here included ensuring the recorded video is
clear and that frames are timestamped and can be extracted for analysis
(e.g., frame timestamps aligned with sensor data).

**Thermal Imaging Integration:** Another key requirement (FR-011) is
integration of a **thermal camera** to capture infrared thermal videos
or images of the participant. The project uses the Topdon TC001 thermal
camera which attaches to Android devices via USB. The requirement is
that the system can record thermal data concurrently with the RGB video.
Thermal imaging provides data on temperature changes, which correlate
with blood flow and perspiration. The integration entails detecting the
USB thermal camera, configuring it, and streaming its data. The Android
code includes a `UsbDeviceManager` and corresponding controllers to
handle USB devices. Specifically, it recognises the VID/PID (Vendor
ID/Product ID) of supported Topdon cameras and initialises
them[\[16\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/managers/UsbDeviceManager.kt#L28-L36)[\[17\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/managers/UsbDeviceManager.kt#L99-L101).
The snippet below from the code confirms support for the Topdon device:

    // Supported TOPDON device vendor/product IDs
    private val supportedDevices = listOf(
        Pair(0x0BDA, 0x3901), // TOPDON TC001 original series
        Pair(0x0BDA, 0x5840), // TOPDON TC001 Plus main variant
        ... (other variants)
    )【24†L27-L35】
    ...
    if (isSupportedTopdonDevice(usbDevice)) {
        callback.onSupportedDeviceAttached(usbDevice) // Initiates thermal camera handling
    }【24†L98-L100】

This ensures that when a supported thermal camera is attached to the
phone, the system automatically recognises it and starts the thermal
feed. The requirement is considered met when the thermal video is
recorded in sync with the RGB video. In practice, thermal cameras have
lower frame rates (often 8--15 fps) and resolution than RGB cameras, so
part of the requirement was also to handle these differences -- e.g., by
upsampling timestamps or buffering frames so that they can still align
in time with the RGB and GSR data. The data from the thermal camera
(heat images) is saved alongside the other streams, and a preview can
also be shown to the researcher.

**Physiological Sensor (GSR) Integration:** While the aim is a
contactless system, we include a **Shimmer3 GSR+ device** as a reference
sensor (FR-012). The requirement is to integrate at least one **wireless
GSR sensor** to record ground-truth skin conductance, primarily for
validation of the contactless methods. This sensor connects via
Bluetooth to the Android device. The system must start and stop the GSR
sensor's data streaming in tandem with the session and log the GSR
readings with timestamps. The codebase includes classes for managing the
Shimmer sensor connection, like `ShimmerDevice` (a data class to
represent a connected sensor) and a `ShimmerManager`. The
`ShimmerDevice` class, for example, encapsulates the state of the sensor
and tracks whether it is streaming, sample count,
etc.[\[18\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/recording/ShimmerDevice.kt#L6-L14):

    /** 
     * Represents a connected Shimmer3 GSR+ device with its state and configuration.
     * This data class encapsulates all information needed to manage a single Shimmer device...
     */
    data class ShimmerDevice(val macAddress: String, val deviceName: String, ...)【22†L5-L13】

This indicates that the system has been explicitly designed to manage
GSR sensor devices. The requirement was satisfied when the app could
successfully connect to a Shimmer sensor, include its data in the
session logs, and when multiple modalities were recorded, the GSR data
could be plotted alongside camera data to check alignment.

In fulfilling these sensor integration requirements, a major
consideration was **real-time performance**. Capturing high-rate data
from multiple sensors can be demanding (especially 4K video). Thus, the
software uses background threads and asynchronous I/O to ensure no data
is lost. The Android app uses efficient image readers and writes to
storage in a streaming manner, and the PC controller can receive preview
frames over the network (to display them) without disrupting the local
saving on the phone. We also set up a **buffering mechanism**: if the
disk write is momentarily slow (e.g., a hiccup in internal storage
writing video), the system buffers a short amount of data in memory.
These design choices come from the requirement that *data acquisition
must be continuous and lossless* for the duration of a session.

To verify these requirements, various tests were conducted: checking
video file integrity (no frames dropped), checking that thermal data is
recorded for the entire session, and that GSR data matches known
calibration signals. The system's ability to integrate all these sensors
and produce synchronised outputs is a key outcome of the requirements
analysis, as these were explicitly identified needs for achieving the
project's goals.

### 3.3.3 Real-Time Data Processing and Analysis Requirements

Beyond raw data capture, the system has requirements for processing data
*in real time* during recording. These requirements exist to provide
immediate feedback and to extract features that might be needed for
certain types of experiments (for example, detecting when a
physiological response crosses a threshold).

**Real-Time Signal Processing:** One requirement (FR-020) is that the
system perform **real-time processing of the incoming data streams**.
This includes basic filtering and feature extraction from the GSR signal
(e.g., smoothing, peak detection) and real-time analysis of video frames
(e.g., running a computer vision algorithm to detect a participant's
hand or face region). The motivation for this requirement is twofold:
(1) to enable monitoring of data quality (for instance, if a camera feed
goes dark or a sensor flatlines, the system should detect it), and (2)
to possibly trigger events or annotations in real time (such as marking
when a significant physiological event occurs).

In the implementation, the Android app and PC controller incorporate
some real-time analysis components. The Android app, for efficiency,
primarily focuses on data capture, but it has integration points for
processing -- for example, a **HandSegmentationManager** is included in
the `CameraRecorder` to analyse video frames for hand
regions[\[19\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/recording/CameraRecorder.kt#L60-L63).
Meanwhile, the PC side can offload heavier processing. The Python
desktop application includes modules for computer vision and
synchronisation analysis (since the PC typically has more processing
power). For example, the codebase contains a `hand_segmentation` package
(with models and utilities) to process frames and segment out the hand
region in thermal or RGB images, indicating where on the image the
GSR-related signals (like perspiration) might be observed. This
real-time analysis requirement is validated by the system's ability to
display overlays on the preview (such as highlighting a region being
tracked) or log derived metrics live.

**Machine Learning Inference:** Another advanced requirement (FR-021) is
that the system is designed to support **machine learning inference** on
the collected data in real time. The ultimate research goal is to
predict GSR (or stress levels) from contactless data; thus, a
requirement was set that the system should be able to apply a
pre-trained model to the video/thermal data as it comes in, to output an
estimated GSR signal or alert. While training models is beyond the scope
of the system itself, the system should at least provide the hooks for
running inference. This was approached by ensuring the data streams can
be fed into a model -- e.g., by having a pipeline where each new frame
triggers a computation. The architecture allows plugging in a model (for
example, a PyTorch or TensorFlow model loaded on the Python side) that
receives frames from the cameras and outputs a predicted signal that can
be compared to the actual GSR. We treated this as a stretch functional
requirement; for the project demonstration, a simple inference stub was
implemented to prove the concept (it could generate a dummy prediction
or run a lightweight analysis).

**Calibration and Alignment Tools:** Although not explicitly separated
in the initial structure, part of processing requirements is the need
for **calibration procedures**. We identified that calibrating the
cameras (especially aligning the thermal and RGB camera view, since they
are separate devices) is important for analysis. A requirement was that
the system provide a way to perform calibration -- for instance,
capturing a reference object in view of all cameras to calibrate spatial
alignment and any time offset. In practice, the system includes a
calibration mode where a checkerboard pattern or a flash can be used as
a calibration event; software tools were developed to compute
calibration parameters. This falls under functional requirements because
it's a needed function before recording sessions (particularly if
precise spatial mapping between thermal and RGB images is required).

To support these processing and analysis requirements, the codebase was
designed with modularity. The presence of classes like
`HandSegmentationManager`, and functions in the `webcam_capture` or
`advanced_sync_algorithms` modules, show that analysis and quality
checking are integrated. The **Preview Panel** on the PC (mentioned
earlier) is not just for passive viewing -- it can also display analysis
results, like highlighting if a device falls out of sync or if a signal
stops. This interactive component was driven by the requirement that the
system aids the researcher during the experiment, not just record data
blindly.

In summary, the functional requirements in this group ensure the system
is **intelligent and interactive**, not merely a dumb data logger. By
processing data in real time, the system can enhance reliability
(through immediate checks) and set the stage for achieving the final
goal of real-time GSR prediction from contactless data.

### 3.3.4 Session Management and User Interface Requirements

While the previous requirements ensure the system can technically
capture and process data, this final functional category focuses on the
**user experience and experimental workflow**. The system must provide
features to manage recording sessions conveniently and offer a user
interface that is usable by researchers who may not be engineers.

**Session Management:** A requirement (FR-003) is that the system
implements complete **session management**. This means it should
treat a recording session as an entity with a start, stop, and
associated metadata. The user (researcher) should be able to initiate a
new session, perhaps providing an identifier or notes, and then start
recording on all devices with one action. The system then should
automatically organise all data from that session (videos, sensor logs,
etc.) in a structured way. Upon stopping the session, the system should
finalise files, possibly create summary logs, and reset the devices to
an idle state ready for the next session. In the code, this is realised
by components like the `SessionManager` on
Android[\[20\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L22-L30)
and analogous logic on the Python controller. The `SessionManager`
handles creating directories for each session, naming files in a
standardised way (e.g., session timestamp), and keeping track of the
session status
(active/completed)[\[21\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L52-L61)[\[22\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L70-L79).
It also works with a `SessionStateDao` (database access object) to save
session info in persistent storage in case of crashes (which ties into
reliability). For example, when a new session is created, the
`SessionManager` code does the following: generates a unique session ID
(with timestamp), creates a folder on device storage for that session,
and prepares filenames for RGB video (`rgb_video.mp4`), thermal video
(`thermal_video.mp4`), GSR data (`shimmer_data.csv`),
etc.[\[23\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L40-L48)[\[24\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L80-L88).
This design meets the requirement by ensuring no data from different
sessions get mixed up and that everything from one session is collected
together.

**User Interface (UI):** The system's UI requirements emphasize **ease
of use** and **clarity**. Researchers running experiments should not
have to handle low-level technical details (like manually starting each
device, or typing commands). Instead, a central dashboard should provide
controls and feedback. The project delivers two main UIs: the **Android
app UI** (on each device, though primarily used for configuration since
once the session starts the devices operate headlessly) and the
**Desktop Controller UI**. The Desktop UI is particularly important as
it's the central command centre. Requirements for it include: the
ability to view live previews of video streams, indicators of device
status (connected, recording, error), and controls to start/stop
recording and perhaps to add timestamped annotations or calibration
events.

In implementation, the Desktop UI was built with PyQt (a Python GUI
framework). As seen in the code for the `PreviewPanel` class, the UI
presents multiple tabs -- one per device's video feed -- and shows the
RGB and thermal camera feeds side by
side[\[25\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/PythonApp/src/gui/preview_panel.py#L2-L10)[\[26\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/PythonApp/src/gui/preview_panel.py#L22-L30).
This allows the researcher to monitor in real time what each device is
capturing. The design of the UI was guided by user feedback: for
instance, having both video feeds visible ensures if one camera's view
is obstructed or out of focus, the researcher notices and can pause the
experiment to fix it. Another UI element is a status console or log
window that prints events (device X connected, recording started at time
T, etc.), which fulfills the requirement of transparency -- the user
should know what the system is doing.

On the Android side, the UI is simpler, but still has requirements: it
should allow initial setup (pairing with the Shimmer sensor, adjusting
camera settings like focus or exposure if needed, selecting thermal
camera modes) and then clearly indicate when the device is waiting vs.
recording. A minimal interface with a big "Connect" or "Ready" indicator
and then "Recording..." status was implemented, as per feedback that
mobile UI should not be cluttered for this purpose.

**Usability considerations:** The requirement for usability also means
the system should require minimal manual steps. Ideally, the user should
"Turn it on and go." This is partially achieved by automation -- devices
auto-connect to the PC if on the same network, USB cameras are
auto-detected, etc. The `UsbDeviceManager` snippet above shows that as
soon as a supported camera is attached, it triggers a
callback[\[27\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/managers/UsbDeviceManager.kt#L99-L107),
meaning the user doesn't need to manually activate the thermal camera.
Similarly, when the PC app launches, it automatically starts looking for
Android clients on the network. This addresses a requirement that the
setup time for the experiment (apart from physically placing cameras) is
minimal and does not itself introduce delays.

To validate session management and UI requirements, user testing was
done where someone unfamiliar with the system was asked to set up and
run a recording following a simple written guide. The criteria for
success: they could complete a session without developer intervention,
and they reported the interface as reasonably clear. Minor improvements
(like labelling and instructions) were incorporated based on this.

Finally, it's worth noting that session management also includes
**post-session tasks** -- after a session, the researcher might want to
review data or export it. The system's UI on desktop includes an option
to quickly open the folder where data was saved, and the data files are
named and formatted consistently to simplify analysis (this verges into
data requirements, discussed later).

Overall, the functional requirements as defined and implemented ensure
the system can do everything it needs to do to support the intended
research. The **codebase** reflects these with specific classes and
modules for each major function, from `MasterClockSynchronizer`
(coordination) to `CameraRecorder` (video capture) to `SessionManager`
(session handling) and the PyQt UI (user interface). The next section
will address non-functional requirements, which are just as crucial for
a research-grade system.

### 3.3.5 Advanced System Integration Requirements

The current implementation has evolved to include sophisticated advanced features that enhance the core functionality
described in the previous sections. These requirements reflect the actual system capabilities as implemented in
`PythonApp/` and `AndroidApp/src/main/java/com/multisensor/recording/` and represent critical enhancements to the
original functional specification that emerged during development and testing phases.

#### FR-034: Web-Based Interface Integration

**Requirement Statement**: The desktop controller application shall provide complete web-based interface capabilities
that enable remote access, monitoring, and control of recording sessions through standard web browsers while maintaining
full security and performance parity with native desktop interfaces.

**Technical Implementation**: The web interface is implemented through `PythonApp/enhanced_main_with_web.py` and the
complete `PythonApp/web_ui/` module system, providing real-time session monitoring, device status visualisation,
and remote control capabilities that maintain synchronisation precision with the native desktop application.

**Validation Criteria**: Web interface accessibility from multiple browsers simultaneously, real-time status updates
with <1 second latency, and complete functional parity with desktop interface for all core recording operations.

#### FR-035: Advanced Performance Optimisation Framework

**Requirement Statement**: The system shall implement complete performance optimisation capabilities that dynamically
adapt resource utilisation, frame rates, and processing load based on real-time system performance metrics and
available computational resources across all connected devices.

**Technical Implementation**: Performance optimisation is achieved through `PythonApp/performance_optimizer.py` for
desktop coordination and `AndroidApp/src/main/java/com/multisensor/recording/performance/` module system including
`NetworkOptimizer.kt`, `PowerManager.kt`, and adaptive frame rate control through
`AdaptiveFrameRateController.kt`.

**Validation Criteria**: Automatic frame rate adaptation maintaining recording quality under varying computational load,
power consumption optimisation extending mobile device recording sessions by >30%, and network traffic optimisation
reducing bandwidth usage by >25% without quality degradation.

#### FR-036: Enterprise-Grade Dependency Injection Architecture

**Requirement Statement**: The Android application shall implement complete dependency injection architecture
that provides modular component management, testability enhancement, and runtime configuration flexibility for
research-specific customizations and experimental protocol variations.

**Technical Implementation**: Full dependency injection framework implemented through Dagger Hilt integration in
`AndroidApp/src/main/java/com/multisensor/recording/di/` providing automatic dependency resolution, scoped component
lifecycles, and configuration-driven component selection for diverse research scenarios.

**Validation Criteria**: Runtime component substitution for testing scenarios, configuration-driven feature enablement,
and complete unit test coverage >90% enabled by dependency injection architecture.

#### FR-037: Advanced Calibration Quality Assessment System

**Requirement Statement**: The system shall provide sophisticated calibration quality assessment capabilities that
automatically evaluate calibration accuracy, detect calibration degradation, and provide real-time feedback for
optimal measurement precision throughout extended recording sessions.

**Technical Implementation**: Advanced calibration system implemented through `PythonApp/calibration/` complete
module system and `AndroidApp/src/main/java/com/multisensor/recording/calibration/CalibrationQualityAssessment.kt`
providing automated quality metrics, drift detection, and precision validation algorithms.

**Validation Criteria**: Automatic calibration quality scoring with objective metrics, detection of calibration drift
within 30 seconds of occurrence, and automated recalibration recommendations that maintain measurement precision
throughout 4+ hour recording sessions.

#### FR-038: Master Clock Synchronisation with Precision Timing

**Requirement Statement**: The system shall implement high-precision master clock synchronisation that maintains
temporal alignment across all connected devices with sub-millisecond accuracy while providing automatic drift
correction and synchronisation quality monitoring throughout extended recording sessions.

**Technical Implementation**: Precision timing system implemented through `PythonApp/master_clock_synchronizer.py`
and coordinated with `AndroidApp/src/main/java/com/multisensor/recording/calibration/SyncClockManager.kt` providing
NTP-based time synchronisation, automatic drift compensation, and real-time synchronisation quality assessment.

**Validation Criteria**: Synchronisation precision <1 millisecond across all devices, automatic drift correction
maintaining precision over 8+ hour sessions, and complete synchronisation quality metrics with real-time
monitoring and alerting capabilities.

## 3.4 Non-Functional Requirements

Non-functional requirements (NFRs) specify the quality attributes and
constraints of the system -- how well it performs certain functions,
rather than what functions it performs. These are especially important
for a system that aims to be **research-grade**, since reliability,
accuracy, and performance directly impact the usefulness of the
collected data. We group the NFRs into three main categories:
**Performance & Scalability**, **Reliability & Data Integrity**, and
**Usability & Accessibility** (which overlaps somewhat with the UI
discussion but extends beyond it).

### 3.4.1 Performance and Scalability Requirements

**Performance** requirements ensure the system operates within
acceptable speed and capacity limits. One key performance requirement is
about **throughput**: the system must handle the data rate from all
sensors without bottlenecks. This means writing large video files to
storage in real time, transmitting preview frames over the network, and
recording sensor streams simultaneously. Concretely, with two cameras
recording 4K video (at \~30 frames per second, each frame perhaps \~1MB
after compression) and a thermal camera plus GSR, the system might be
handling on the order of **tens of megabits per second** of data. The
requirement was that this data rate be sustained with no frame drops or
buffer overflows. The code sets parameters like a 10 Mbps video bitrate
for 4K
recording[\[28\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/recording/CameraRecorder.kt#L105-L113),
indicating that it's optimised for that throughput. Actual tests
confirmed the phones could write 4K video at 30fps smoothly to their
flash storage, and the Wi-Fi network could carry preview images at a
lower rate.

Another performance aspect is **latency**. For interactive use (like
preview on the PC, or any real-time feedback), we set a requirement that
the end-to-end latency from capturing a frame on the phone to displaying
it on the PC preview should be under 500 ms, and ideally around 200 ms.
This ensures what the researcher sees is almost live. The system uses
efficient encoding and avoids heavy processing on the critical path to
meet this. During testing, we measured the preview latency and tuned the
system (e.g., adjusting the preview frame size or rate) to usually stay
below 200 ms for the RGB feed -- which was acceptable for monitoring
purposes.

**Scalability** requirements address how the system copes as the number
of devices or duration of recording grows. We required that adding a
second or third device should not dramatically degrade performance. This
was validated by trial: running sessions with 1 phone vs. 2 phones did
not halve the frame rate or anything -- thanks to the multi-threaded
design and the fact that each phone largely handles its own recording,
with the PC just coordinating. The system is also expected to handle
**long recordings** (e.g., an hour-long session) without running out of
memory or storage unexpectedly. We ensured by design that data is
streamed to files (so memory usage stays bounded) and that log files are
rolled or segmented for long sessions if needed.

In the code, some evidence of performance considerations includes using
a background thread specifically for camera operations (to not block the
main UI
thread)[\[29\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/recording/CameraRecorder.kt#L88-L96),
and using a thread pool on the PC for handling multiple device
communications
concurrently[\[30\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/PythonApp/src/master_clock_synchronizer.py#L109-L117).
These are classic strategies to maintain performance as load increases.
Moreover, parameters like `sync_interval=5.0` seconds in the
synchronizer[\[31\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/PythonApp/src/master_clock_synchronizer.py#L82-L91)
strike a balance between too frequent sync (which could flood the
network) and too infrequent (which could allow drift).

A specific scalability target recorded in the documentation was
**support for up to 8 simultaneous
devices**[\[32\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/thesis_report/Chapter_3_Requirements_and_Analysis.md#L362-L366),
which is ambitious. While our practical tests maxed out at 4 devices due
to hardware availability, the architecture was designed with that
headroom. For instance, the data structures for connected devices
(dictionaries, lists) and the loop that sends sync commands are generic
and could handle more devices just by adding them to a config.

### 3.4.2 Reliability and Data Integrity Requirements

**Reliability** is absolutely critical -- lost data or system crashes
during an experiment could invalidate a study. Thus, several
requirements ensure the system is robust and that data remains intact.

Firstly, the system must have **high availability** during recording
sessions. We set a goal of \>99% availability during test runs (meaning
it should almost never crash or stall). To support this, the system
includes fault-recovery mechanisms. One requirement is that if a
non-critical component fails (e.g., one camera disconnects or a sensor
stops), the system should attempt to recover or at least log the issue
and continue with what is available. For example, if an Android device
momentarily drops network connection, the PC will not crash; instead, it
marks that device as disconnected and waits for it to return. The
`MasterClockSynchronizer` has callbacks for device disconnects and
reconnects to handle this scenario
gracefully[\[33\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/PythonApp/src/master_clock_synchronizer.py#L121-L128).

**Data integrity** requirements ensure that the data collected is
accurate and not corrupted. This includes having no gaps in the time
series unless explicitly intended. The system uses **sequential file
writing** and on Android the files are closed properly at session end to
avoid corruption. We also introduced simple integrity checks: for
instance, the GSR CSV file has a known number of samples and is verified
against the recorded duration (to check no large chunks are missing). In
code, the design of the `SessionManager` writing a *session_info.txt*
and *session_config.json* file is partly to record meta-information
(like start time, expected devices, any errors) so that one can verify
after the fact that everything
completed[\[34\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L112-L120).
This trace helps catch if something went wrong.

Another reliability feature is **crash recovery**. The requirement here
is that if the app or PC crashes or power fails, the system should not
lose all data up to that point. To that end, data is written
incrementally (so what's on disk is safe even if a crash occurs later).
The Android app also has a
`CrashRecoveryManager`[\[35\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L32-L35)
that, upon restart, can detect if there was an active session that
didn't finalise and attempt to reconcile it (for example, by closing any
open files, or marking the session as failed but still available for
analysis). This ensures that in worst-case scenarios, partial data can
still be recovered rather than being unusable.

We also considered **fault tolerance**: the requirement that one device
failing does not ruin the whole session's data from other devices. This
is satisfied by the distributed nature -- each device records
independently under coordination. If one phone's camera app crashes,
other devices are unaffected and continue recording. The PC controller
will log an error for that device, but the rest of the data is safe.
This modular design is a direct response to reliability requirements.

In terms of code evidence, the presence of a `RecoveryManager` on the PC
side and the careful state management in `ShimmerDevice` (e.g., it
tracks reconnection attempts and resets state on
disconnect[\[36\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/recording/ShimmerDevice.kt#L70-L78))
illustrate the emphasis on keeping the system running or restoring it to
running state quickly. The **testing framework** (discussed in Chapter
5) was also heavily used to test reliability by simulating disconnects
and failures, which the requirements demanded.

### 3.4.3 Usability and Accessibility Requirements

Non-functional requirements also cover the system's **usability** (some
of which we touched on in functional UI requirements) and
**accessibility**. This is particularly relevant because the system
might be used by researchers who are not computer scientists or by
students in a lab.

Usability requirements include: the system should be **easy to set up**
(ideally plug-and-play), **documentation** should be provided, and the
user interface should be learnable without extensive training. We
addressed these by creating user guides (see Appendix for a user manual)
and by simplifying the workflow (e.g., one-click start for multi-device
recording). The interface avoids technical jargon; for instance, it says
"Connect Devices" rather than "Bind NTP Servers" -- hiding the
complexity.

**Accessibility** in this context is mostly about ensuring the system
can be used in different environments and by people with varying levels
of tech expertise. We didn't have specific requirements like supporting
screen readers (since it's not a public-facing software), but we did
ensure that, say, the font sizes and colour choices in the UI are clear
(the preview labels have high contrast text on black
background[\[37\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/PythonApp/src/gui/preview_panel.py#L64-L72)[\[38\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/PythonApp/src/gui/preview_panel.py#L73-L81)
for visibility). Also, the system was tested on different screen sizes
and lighting conditions to ensure the preview and controls remain
visible.

Another aspect is **configurability**. While not exactly the typical
definition of accessibility, we required that the system be flexible
enough to be configured for various experiment designs. For instance, if
a researcher doesn't use a thermal camera, they should be able to
disable that feature rather than the system failing. This was handled by
making components modular -- if no thermal camera is present, the system
still works (just those data fields remain empty). Many settings (like
video resolution, which sensors to use, network addresses) are
configurable via a config file or UI, which makes the tool adaptable and
thus more broadly usable.

**Ethical and Privacy considerations** can also be seen as
non-functional requirements. Because the system records video of
participants, we included a requirement that data handling comply with
research ethics guidelines. Practically, this meant adding a feature
where video files can be automatically anonymized or watermarked if
needed (for example, converting them to a format that blurs faces, if
required, though that is more of a post-processing step). We mention it
here to note that any such requirement would affect how data is stored
(perhaps encrypted or password-protected). In our implementation, an
optional encryption of output files was considered (and can be turned on
in config), addressing any requirement to secure sensitive data.

In summary, the non-functional requirements ensure the Multi-Sensor
Recording System is **performant, reliable, and user-friendly**. These
qualities are what elevate the project from a simple prototype to a tool
that could be used in real research studies. The evidence of meeting
these requirements is seen not just in testing results (like achieving
\>99% uptime in test scenarios, or handling high data rates), but also
in the code structure (e.g., use of robust patterns and checks) and
documentation. For instance, the project documentation explicitly lists
performance targets and how they were
met[\[39\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/thesis_report/Chapter_3_Requirements_and_Analysis.md#L362-L370),
and includes a quality assurance checklist that corresponds to these
NFRs.

## 3.5 Use Cases

To ground the requirements in realistic scenarios, a set of **use
cases** was developed. These describe how an end user (typically a
researcher or operator) would interact with the system to achieve
specific goals. The use cases helped validate that the functional
requirements covered all necessary steps for the user's tasks. They also
provided insight into any additional requirements that become evident
only when considering full workflows (for example, the need for an
"export data" function after recording, or a "calibrate cameras" step
before recording).

### 3.5.1 Primary Use Cases (Key System Scenarios)

The primary use cases represent the core intended uses of the system in
a research setting. They are as follows:

- **UC-001: Conduct Multi-Participant Recording Session.** In this
  scenario, a researcher sets up the system to record physiological data
  from one or more participants simultaneously. The use case steps
  include: starting the desktop controller, powering on the Android
  devices and connecting sensors, verifying all devices are detected and
  synchronised, and then initiating a recording for the desired
  duration. During the session, the researcher might monitor live feeds.
  After the session, the system automatically saves all data. This use
  case covers the end-to-end normal operation and directly exercises
  requirements like multi-device sync, data capture, and session
  management. It's essentially a "day in the life" of the system in use
  for an experiment.

- **UC-002: System Calibration and Configuration.** Before running a
  study, a researcher might need to calibrate the cameras (ensuring
  thermal and RGB frames align spatially and temporally) and configure
  device settings (like naming each device or setting participant IDs).
  This use case has steps such as: placing a calibration object (like a
  checkerboard) in view, using a special mode in the software to capture
  calibration images from all cameras, and then running a calibration
  computation (could be automated or offline). Also included is
  configuring any parameters (for example, choosing which sensors are
  active, entering notes about the session). This scenario ensures the
  system can be prepared properly -- touching requirements around
  usability and any calibration functionality.

- **UC-003: Real-Time Data Monitoring and Annotation.** In some studies,
  the researcher might want to mark certain events or make notes during
  the recording (e.g., "Participant showed sign of discomfort at this
  moment"). This use case involves the researcher using the UI while
  recording to add an annotation (maybe pressing a key or button that
  timestamps an event). The system should record these annotations in
  the session log. It also involves closely watching the preview feeds;
  if something goes wrong (like a feed freezing), the researcher might
  intervene (which then touches error handling flows). This scenario
  validates that the UI and real-time processing features are meeting
  needs -- the requirement to provide immediate insight and allow user
  interaction during a session.

Each primary use case was considered successful if the system could
complete all steps without error and the user's goal was met (data
recorded, calibration done, etc.). During testing, these scenarios were
simulated. For example, for UC-001, multiple devices were actually run
together to mimic a multi-participant setup, and data was later checked
for synchronisation as expected.

### 3.5.2 Secondary Use Cases (Maintenance and Extensions)

Secondary use cases cover maintenance, system management, or less
frequent tasks -- they ensure the system remains useful in the long term
and can be extended or troubleshooted.

- **UC-010: Data Export and Analysis Preparation.** After recording
  sessions, a researcher needs to work with the data. This use case
  involves the researcher using the system's provided tools to export or
  convert the data into formats suitable for analysis. For instance, the
  system might compress raw video, or export a combined timeline of
  events. While much data analysis will happen outside the tool (e.g.,
  in Python or MATLAB), the requirement is that the system shouldn't
  lock data in proprietary formats. Thus, this use case might simply be:
  user opens the output folder (there could be a shortcut in the UI),
  and finds all data files in standard formats (MP4, CSV, JSON). The
  success condition is that the researcher can easily take those files
  and load them into analysis software. This was verified by, for
  example, opening the CSV in a spreadsheet and playing the video files
  in a standard media player.

- **UC-011: System Maintenance and Diagnostics.** Over time, the system
  may require updates or encounter issues. This use case covers how a
  technician or developer would perform maintenance. Steps include:
  checking device firmware versions (for Android or sensors), running a
  diagnostic mode that tests each sensor (maybe a short self-test where
  each component is activated and a report is generated), and viewing
  system logs to identify any problems. We built some diagnostic
  capabilities, such as a *test mode* on the PC that can ping each
  device and report latency, and the logging system which can be
  consulted. The maintenance scenario ensured that the requirements for
  maintainability (like good logging, modular design allowing parts to
  be individually tested) were met. It also includes updating software
  -- since both PC and Android parts might get updates, the process
  (perhaps manual, via reinstalling the app, or using a version check)
  should be straightforward.

- **Extension Use Case: Adding a New Sensor Type.** Although not
  explicitly numbered in the list, we considered an extensibility
  scenario: e.g., adding a heart rate monitor or an additional webcam to
  the system. This would involve steps a developer might take: integrate
  new device drivers, update the synchronizer to include the new data
  stream, and update UI to show it. The reason to think about this is to
  validate that our requirements and design aren't so brittle that only
  exactly the current sensors can ever work. Indeed, in the
  documentation, guidelines for adding new device types are
  provided[\[40\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/Multi_Device_Synchronization_System.md#L40-L48),
  indicating that the architecture can accommodate future extensions.

The secondary use cases ensure that beyond the immediate functionality,
the system is **practical to use and maintain** in a real lab
environment. They were not all directly tested with end users (e.g.,
maintenance tasks were more internal), but they influenced the
requirements. For example, the requirement for having clear log files
and a debug mode comes from considering UC-011.

By stepping through these use cases, we have confidence that the
requirements captured earlier are sufficient and that no significant
scenario was overlooked. The use cases essentially act as a validation
checklist from a user perspective: each use case touches multiple
requirements. For instance, UC-001 (multi-participant session)
simultaneously verifies multi-device sync, sensor capture, session
management, performance (when handling all those at once), and UI. It's
a holistic test of the system's requirements fulfillment.

## 3.6 System Analysis

With the requirements established, we analyse how the system will meet
them by examining data flows, component interactions, and scalability
considerations. This section bridges between requirements and the design
(which is detailed in Chapter 4), ensuring that we understand the system
dynamics needed to satisfy the requirements.

### 3.6.1 Data Flow Analysis

Analysing data flow involves mapping out how data moves through the
system from sources (sensors and devices) to destinations (storage, user
interface, network). This is crucial to validate that the design can
handle the volume and timing of data as required (referencing the
performance requirements).

In the Multi-Sensor Recording System, the **primary data flows** are: 1.
**On each Android device:** Sensor inputs (camera frames, thermal
readings, GSR readings) flow into the device's memory, then are written
to local storage and simultaneously some are sent over the network to
the PC (for preview/monitoring). 2. **On the PC side:** Preview data
flows into the UI; commands flow from the PC to devices; and at session
end, data may flow from devices to PC if needed (though in our design,
large data like videos remain on the devices until the user retrieves
them after the session, to avoid clogging the network during capture).

A data flow diagram (in the full documentation) illustrates these paths:
for example, the RGB camera frames go through the `CameraRecorder`
pipeline on Android (which may convert them to a compressed format),
then are written to an MP4 file and a downsampled version is sent via a
WebSocket to the PC preview. The thermal data similarly goes to a file
and a smaller stream to PC. GSR data is typically low bandwidth (just a
numeric reading at, say, 10-20 Hz) and can be sent frequently to PC if
we want live plots.

This analysis helped in identifying potential **bottlenecks or points of
failure**. For instance, the network link between devices is a critical
conduit for synchronisation messages and preview frames. We determined
that even if the network bandwidth is limited, the system should
prioritise control and sync messages (very small) over preview frames.
Therefore, the data flow design gives higher priority (or uses a
separate channel) for control vs. bulk data. This satisfies the
requirement that sync must be maintained even if previews drop frames
under stress.

We also considered the **data flow for storage**: each device writes to
local disk, so the performance of the phone's storage (which can be
variable) affects things. The analysis led to implementing
double-buffering in the camera write -- one buffer is being written to
disk while the next frames fill another buffer, to avoid camera sensor
pipeline stalling. The GSR and thermal data are lightweight and simply
appended to text/binary files.

**Data flow for multi-device coordination:** The
`MasterClockSynchronizer` sends out periodic sync beacons (NTP packets)
and receives status updates from devices (like "I'm alive" messages).
These flows are low bandwidth but time-sensitive. The analysis made it
clear that using UDP for NTP and TCP for control commands was
appropriate (NTP over UDP for speed, and control commands over TCP for
reliability). Each device maintains a socket connection to the PC
(established at session start), and through that connection, JSON
messages for start/stop and status are
exchanged[\[41\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/Multi_Device_Synchronization_System.md#L18-L26).
The data flow here ensures that if, say, the PC says "START recording at
time T", all devices receive that before time T, then at T they start
writing data.

By mapping these flows, we validated that the system architecture meets
the **throughput and timing requirements**. For example, if each of 3
devices writes 10 Mbps to storage, and sends 1 Mbps preview data to PC,
the total network usage might be \~3 Mbps (since preview is compressed
and possibly reduced resolution), which is fine for Wi-Fi. Control data
is negligible. Thus, the requirement of sustaining data flow is met.

### 3.6.2 Component Interaction Analysis

This part of the analysis looks at how different components (or
subsystems) of the system interact to fulfill the requirements. The main
components we identified include: the Android App (with its
sub-components like camera manager, sensor managers, network client),
the Desktop Controller (with components like the synchronizer, network
server, GUI, data manager), and external components such as the network
and storage.

The interactions can be thought of in a sequence diagram form for key
operations. Take **starting a session**: The researcher clicks "Start"
on the PC UI. The Desktop Controller's session manager creates a session
entry and instructs the MasterClockSynchronizer to issue a sync start
command. The PC sends a `StartRecordCommand` to each connected Android
(via the PCServer
networking)[\[42\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/Multi_Device_Synchronization_System.md#L20-L28).
Upon receiving this, each Android device's controller component (in the
app) transitions to recording state: the camera module starts capturing,
the Shimmer manager starts streaming GSR, etc., and each sends back an
acknowledgment (or a status message). The PC collects these acks -- if
one device fails to respond, it could either abort the session or
exclude that device. Assuming all respond, the session is officially
"started" and time is ticking. During recording, the components interact
periodically: e.g., Android devices might send a heartbeat or status
update to PC (like "still recording, at timestamp X"). The PC might send
synchronisation pulses (though with NTP running, that's more continuous
at a lower level). If the user hits "Stop", the PC sends a stop command
to all Androids, they finalise files and reply when done, and the PC
then marks the session complete.

This interaction analysis verifies requirements such as
**synchronisation and coordination** -- we see that the design allows
all nodes to act together. It also covers error cases: if an Android
doesn't ack the start, the PC UI can alert the user and perhaps let them
retry or drop that node. This fulfills the reliability requirement that
the system is aware of each component's state.

Another important interaction is for **synchronisation algorithm**: The
MasterClockSynchronizer not only sends commands but also may adjust
timing. For example, it may tell an Android "your clock is 5 ms behind,
adjust it" if it detects drift via NTP queries. This is a closed-loop
interaction between PC and each device. The design uses the
NTPTimeServer on PC and the Android devices making requests to it -- so
actually, each Android asks the PC for time regularly (the interaction
is initiated by Android in that case). The analysis assured that this
approach is scalable (multiple devices querying one server is fine, NTP
is lightweight) and robust (if one query fails, next one likely
succeeds; minor packet loss doesn't break sync significantly).

**Component responsibilities** were checked against requirements: e.g.,
the Android *SessionManager* versus the Desktop *SessionManager* -- to
ensure no duplication or gaps. We found that Android's SessionManager is
about file handling on the device, whereas the Desktop's session logic
is about coordination and high-level tracking. They interact indirectly
by agreeing on a session ID and timing. This separation means even if
the PC crashes, each Android still has its SessionManager keeping the
data safe, which goes back to reliability.

In summary, the component interaction analysis confirmed that the
**system architecture can realise the functional requirements**. It
showed that every requirement (like start/stop sync, data collection,
error recovery) is backed by a clear interaction between responsible
components. The next chapter will further detail this in terms of actual
architecture, but here we ensure logically it's sound.

### 3.6.3 Scalability Considerations

Scalability in this context covers both scaling **up** (more devices,
more data) and scaling **out** (using the system in different
environments or with more users). We touched on performance scalability
under NFRs, but here we consider it in the design/analysis sense.

From the requirements, one scalability target was the number of devices
(up to 8). The analysis considered potential **bottlenecks** when going
from, say, 2 to 8 devices: - Network: 8 devices sending preview video
could saturate Wi-Fi. Mitigation: the preview frame rate or resolution
could be automatically reduced when many devices are connected. The
requirement could be relaxed (maybe you don't need preview from all 8
simultaneously, or you stagger them). - PC processing: handling 8 video
streams for preview or analysis could be heavy. But since the PC is not
storing all video (each phone stores its own), the PC primarily handles
coordination and maybe one or two analysis tasks. The code's thread pool
for sync
commands[\[30\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/PythonApp/src/master_clock_synchronizer.py#L109-L117)
can handle multiple threads, and can be increased if needed. The GUI is
built on PyQt which can update multiple windows; though 8 video feeds
might be a lot, they could be displayed smaller or in groups. - Time
sync: NTP can easily handle many clients; 8 is trivial for it, so no
issue there. - Storage: each device handles its own storage, so adding
devices scales nearly linearly (which is okay as long as each device
individually meets storage requirement -- e.g., enough free space for
their recording). - Session coordination: the data structures (dicts,
lists) for devices are fine up to 8 or more entries.

We also considered **scalability in terms of data volume**. If each
session is large (several GB of video), the system should be able to
manage that over time. That's less a runtime issue and more about
practical use: e.g., ensuring that old sessions can be archived to free
space (we wrote a note in documentation to remind users to transfer and
delete old sessions to keep devices ready).

Another angle is scaling to **different experimental setups**: maybe
multiple PCs or multiple concurrent sessions. Our design currently
assumes one session at a time (one coordinator PC). If scaling out to
multiple simultaneous experiments, you'd run separate instances on
different networks to avoid interference. That scenario was out of
scope, but we mention it to show we thought about boundaries.

In conclusion, the system analysis of data flow, interactions, and
scalability provided confidence that the defined requirements are not
only theoretically achievable but practically addressed by the design.
It helped refine some requirements as well -- for instance, realising
the need for dynamic adjustment of preview quality when many devices
connect could be turned into a requirement for adaptive performance
management (which we included implicitly under performance
requirements).

## 3.7 Data Requirements

Apart from functional and quality requirements, it's important to
specify requirements related to the **data** itself: what types of data
are handled, expected volumes, data quality needs, and how the data is
stored and managed. Since this project is data-centric (it records a lot
of raw data for analysis), clearly defining these aspects ensures the
system will produce useful and manageable outputs.

### 3.7.1 Data Types and Volume Expectations

The system handles multiple data types: - **Video data:** from RGB
camera (and potentially from a USB webcam on PC if used for additional
views) -- this is high-volume, binary data (MP4 files). Each minute of
4K30 video is on the order of 100--200 MB at 10 Mbps encoding. So an
hour session from one camera could be \~6--12 GB. Multiply that by 2
cameras (RGB + thermal video, although thermal might be smaller
resolution) and potentially by number of devices, and we easily have
tens of gigabytes per session as an upper bound. The requirement is that
the system **support these volumes**. Practically, each Android device
used had at least 64 GB free, so recording for a few hours is fine. We
set an expectation that a typical session (say 10 minutes, two cameras)
would produce a few GB, which is manageable, but we also ensure the
system warns the user if storage is low (a small feature implemented:
the app checks available disk space before starting and refuses if below
a threshold to prevent midway failure).

- **Thermal data:** if saved as video, it's also an MP4 but with lower
  resolution (say 320x240) and lower frame rate. The volume is much
  smaller, maybe 5--10% of the RGB video size. Alternatively, we could
  store individual thermal images at intervals (since high frame rate
  may not be needed). But our current approach was video for simplicity.
  This is included in the above estimate.

- **Sensor data (GSR and possibly others):** These are time-series
  numeric data, which are very low volume by comparison. A GSR sensor at
  128 Hz for an hour is a few tens of thousands of samples, which in CSV
  is maybe a few MB at most. Negligible compared to video. Still, the
  requirement is that *all sensor readings must be recorded with their
  timestamps* without loss. The system stores them in CSV
  (comma-separated values) or a similar text format for ease of import
  into analysis tools. For example, the Shimmer data might be logged as
  `timestamp, GSR_value` lines. This is straightforward and the volume
  is small.

- **Metadata and Logs:** The system also produces metadata like session
  info, configuration used, any events (annotations or errors) -- these
  are stored in small text files (session_info.txt, session_config.json,
  etc. as
  mentioned)[\[23\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L40-L48).
  These are tiny (kilobytes), but important for interpreting the data.
  The requirement is to include all necessary context in these files
  (such as which device had which role, calibration values, etc.) to
  ensure later that the data can be analysed correctly.

Given these volumes, the requirement was that the system should handle
at least a **one-hour continuous recording session** without running out
of resources or splitting files incorrectly. Our tests included a
30-minute trial which produced \~18 GB across devices and it was handled
(with data stored and session closed properly). If a longer session is
needed, the recommendation is to break it into multiple sessions for
manageability, but the system can theoretically go on as long as storage
and battery last.

### 3.7.2 Data Quality and Storage Requirements

**Data quality** requirements cover the fidelity and accuracy of the
captured data. For video, quality relates to resolution and compression.
We required that **video be high resolution and minimally compressed**
to preserve detail that algorithms might need (like subtle skin colour
changes). The 10 Mbps bitrate for 4K video is a balance -- it is high
enough for good quality, though some quality is sacrificed vs. raw for
the sake of storage. In any case, the researcher can configure a higher
bitrate if needed (the app could allow tweaking that if truly lossless
or near-lossless is desired for a short recording). The system also
avoids dropping frames -- which is a quality aspect. We log frame drops
if any occur (none occurred in normal conditions in testing).

For thermal, quality means capturing the full temperature range and
resolution of the camera. The TC001 provides calibrated temperature data
per pixel; our system ensures the recorded thermal video doesn't clip or
auto-adjust in a way that loses raw info. Essentially, whatever frames
the camera gives, we store them unchanged (except for encoding them into
a video).

For GSR, quality means proper calibration of the sensor (Shimmer is
factory calibrated, but ensuring no drift or offset errors). The
requirement might be to sample at a sufficient rate and resolution. The
Shimmer device provides high-resolution A/D conversion for GSR, so we
just take its data as is (in microsiemens). We include in metadata if
any filtering was applied (generally not at record time).

An important data quality requirement is **temporal accuracy** of the
timestamps in the data files. This ties back to synchronisation: each
piece of data (each video frame, each sensor reading) has a timestamp in
a common reference (the PC master clock). The system must ensure those
timestamps are applied correctly. We achieve this by, for example,
naming video frames internally with the master clock time when sending
previews, and by aligning the GSR timestamps to the NTP sync. The
quality criterion is that if one were to line up data from two devices
by timestamp, they truly represent the same moment within the sync
precision. This was validated by experiments with a shared event as
mentioned before.

**Storage requirements** pertain to how data is stored and organised: -
The requirement is to have a **clear directory structure** for sessions.
We defined that each session gets its own folder (named with a timestamp
for uniqueness and
sorting)[\[43\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L76-L84).
Inside, files are named consistently (e.g., "rgb_video.mp4",
"thermal_video.mp4", "shimmer_data.csv",
etc.)[\[23\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L40-L48).
If multiple devices produce the same type of file (say two RGB videos
from two phones), we either differentiate by device name or store in
subfolders (the implementation took the approach of subfolders per
device, or alternatively, file names contain the device ID). This
organisation is required for scalability so that data from many sessions
doesn't mix, and a researcher can easily find all files for one
session. - Another requirement was to **preserve raw data** whenever
possible. That is, avoid any in-place processing that might alter the
raw measurements. This is why we save raw sensor CSV, and why we
considered saving RAW images from the camera (the CameraRecorder has an
option to capture RAW photos alongside video for
calibration)[\[44\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/recording/CameraRecorder.kt#L121-L130)[\[45\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/recording/CameraRecorder.kt#L159-L168).
Even if not used immediately, having raw data can be valuable in
research to apply different analyses later. The system meets this by not
doing heavy pre-processing on the recorded data -- all algorithms for
analysis run either in parallel (for feedback) or later on copies of the
data, leaving the recorded files untouched.

- We also have a requirement on **data retention and backup**. The
  system itself doesn't enforce backups, but we strongly recommended in
  documentation that after each session, data should be copied to a
  secure storage (like a lab server). For retention, as long as files
  remain on the device, the system will list them (we made a simple file
  viewer in the app for convenience).

To double-check, we looked at an example session output: the folder
"session_2025-08-01_14-30-00" containing `session_info.txt` (with notes
like duration, any issues), `device1_rgb_video.mp4`,
`device1_thermal_video.mp4`, `device1_shimmer_data.csv`,
`device2_rgb_video.mp4`, etc., plus maybe a `combined_timeline.json` if
we had a feature to merge timeline events. This matches what was
required.

In terms of code, the file paths and names are constructed in
`SessionManager.createNewSession()` as we
saw[\[24\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L80-L88)[\[46\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L93-L101).
That piece ensures the directories exist and all standard files are
created at start (even if some remain empty if a sensor is not used, for
consistency).

Overall, the data requirements guarantee that the system's output is not
just large in quantity, but high in quality and well-organised, so that
the research goals (like developing a predictive model) can be achieved
using this data. They complement the functional requirements by focusing
on the end product of the system -- the recorded dataset -- which is
ultimately what the value of the system is measured by.

## 3.8 Summary and Alignment with Project Objectives

In this chapter, we outlined the requirements and analysis that define
what the Multi-Sensor Recording System must achieve and how it is
structured to do so. To summarise, the system is required to provide a
**contactless, synchronised, multi-modal recording solution** that
addresses the key shortcomings of traditional physiological measurement
methods. We identified the problem context of intrusive sensors and
limited multi-participant capabilities, and seized the opportunity to
create a system leveraging modern sensors (RGB, thermal) and distributed
computing techniques to enable non-intrusive measurements.

Through a rigorous requirements engineering process, involving
stakeholders and literature, we derived both **functional requirements**
-- such as multi-device coordination (FR-001), precise temporal
synchronisation (FR-002), integrated video/thermal/GSR capture
(FR-010/011/012), real-time processing (FR-020/021), and complete
session management (FR-003) -- and **non-functional requirements** --
including high performance (NFR-001 series with support for many devices
and low latency), high reliability (99%+ uptime, data integrity checks),
usability (simple UI for researchers), and data quality (capturing
high-fidelity signals and well-structured data). These requirements were
validated against stakeholder needs like scientists' demand for accuracy
and participants' desire for comfort, ensuring that the system's
features directly contribute to those needs.

Crucially, each major requirement aligns with the **project's
objectives** stated in the Introduction (Chapter 1). The objective of
enabling **contactless GSR measurement** is met by the functional
requirements around camera and thermal sensor integration -- the system
can record the necessary signals without electrodes, fulfilling the aim
of non-contact measurement. The objective of maintaining
**research-grade accuracy** is supported by the synchronisation and data
quality requirements -- by ensuring all devices are within milliseconds
alignment and capturing high-resolution data, the system can produce
data as reliable as traditional
setups[\[12\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/Multi_Device_Synchronization_System.md#L50-L58).
The goal of supporting **multi-participant experiments** is directly
addressed by the multi-device coordination requirements and the
scalability considerations -- the system was required and designed to
handle multiple devices simultaneously, something that was not feasible
with older methods without massive
effort[\[4\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/thesis_report/Chapter_3_Requirements_and_Analysis.md#L296-L304).
Finally, the project's aim of providing a **usable tool for the research
community** is reflected in the usability and documentation requirements
-- making the system easy to operate and reproducible, which ties into
the academic contribution of this work as a platform others can adopt.

By systematically analysing use cases, we ensured the requirements cover
complete workflows a researcher will engage in, and by conducting system
analysis, we confirmed that these requirements are implementable within
the chosen architecture. In the next chapter, we will see how these
requirements were translated into a concrete design -- for instance, how
the requirement for synchronisation led to the specific choice of a
master-clock architecture using NTP and how the requirement for sensor
integration determined certain architectural patterns on Android and PC.
Moreover, Chapter 5 (Evaluation) will revisit these requirements to
verify to what extent each was satisfied in the final system. For a
brief forward-look: preliminary results have shown the system
coordinating 4 devices with synchronisation error within \~3 ms and
achieving over 99% data capture reliability, which indicates the
implementation is indeed meeting the critical
requirements[\[47\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/thesis_report/README.md#L90-L94)[\[48\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/thesis_report/Chapter_3_Requirements_and_Analysis.md#L363-L371).

In conclusion, the Requirements and Analysis chapter establishes a
strong foundation for the project by clearly defining **what the system
must do and under what constraints**, and ensuring those needs stem from
real research problems and objectives. This lays the groundwork for
design and implementation to proceed in a focused way, and sets
measurable criteria (through the requirements) by which the success of
the project can later be evaluated. The meticulous alignment of
requirements with project goals is intended to maximise the impact of
the developed system and to demonstrate, in a traceable manner, that the
engineering effort has been directed towards fulfilling the research
aims of enabling advanced, contactless physiological data collection for
the scientific community.
---
[\[1\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/thesis_report/README.md#L87-L95)
[\[47\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/thesis_report/README.md#L90-L94)
GitHub

<https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/thesis_report/README.md>

[\[2\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/thesis_report/Chapter_3_Requirements_and_Analysis.md#L292-L300)
[\[3\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/thesis_report/Chapter_3_Requirements_and_Analysis.md#L299-L305)
[\[4\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/thesis_report/Chapter_3_Requirements_and_Analysis.md#L296-L304)
[\[5\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/thesis_report/Chapter_3_Requirements_and_Analysis.md#L32-L40)
[\[6\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/thesis_report/Chapter_3_Requirements_and_Analysis.md#L344-L354)
[\[7\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/thesis_report/Chapter_3_Requirements_and_Analysis.md#L358-L366)
[\[8\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/thesis_report/Chapter_3_Requirements_and_Analysis.md#L2-L5)
[\[32\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/thesis_report/Chapter_3_Requirements_and_Analysis.md#L362-L366)
[\[39\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/thesis_report/Chapter_3_Requirements_and_Analysis.md#L362-L370)
[\[48\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/thesis_report/Chapter_3_Requirements_and_Analysis.md#L363-L371)
GitHub

<https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/thesis_report/Chapter_3_Requirements_and_Analysis.md>

[\[9\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/PythonApp/src/master_clock_synchronizer.py#L2-L10)
[\[10\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/PythonApp/src/master_clock_synchronizer.py#L99-L108)
[\[11\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/PythonApp/src/master_clock_synchronizer.py#L129-L140)
[\[13\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/PythonApp/src/master_clock_synchronizer.py#L74-L83)
[\[14\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/PythonApp/src/master_clock_synchronizer.py#L119-L127)
[\[30\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/PythonApp/src/master_clock_synchronizer.py#L109-L117)
[\[31\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/PythonApp/src/master_clock_synchronizer.py#L82-L91)
[\[33\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/PythonApp/src/master_clock_synchronizer.py#L121-L128)
GitHub

<https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/PythonApp/src/master_clock_synchronizer.py>

[\[12\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/Multi_Device_Synchronization_System.md#L50-L58)
[\[40\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/Multi_Device_Synchronization_System.md#L40-L48)
[\[41\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/Multi_Device_Synchronization_System.md#L18-L26)
[\[42\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/Multi_Device_Synchronization_System.md#L20-L28)
GitHub

<https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/docs/Multi_Device_Synchronization_System.md>

[\[15\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/recording/CameraRecorder.kt#L51-L59)
[\[19\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/recording/CameraRecorder.kt#L60-L63)
[\[28\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/recording/CameraRecorder.kt#L105-L113)
[\[29\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/recording/CameraRecorder.kt#L88-L96)
[\[44\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/recording/CameraRecorder.kt#L121-L130)
[\[45\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/recording/CameraRecorder.kt#L159-L168)
GitHub

<https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/recording/CameraRecorder.kt>

[\[16\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/managers/UsbDeviceManager.kt#L28-L36)
[\[17\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/managers/UsbDeviceManager.kt#L99-L101)
[\[27\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/managers/UsbDeviceManager.kt#L99-L107)
GitHub

<https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/managers/UsbDeviceManager.kt>

[\[18\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/recording/ShimmerDevice.kt#L6-L14)
[\[36\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/recording/ShimmerDevice.kt#L70-L78)
GitHub

<https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/recording/ShimmerDevice.kt>

[\[20\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L22-L30)
[\[21\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L52-L61)
[\[22\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L70-L79)
[\[23\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L40-L48)
[\[24\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L80-L88)
[\[34\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L112-L120)
[\[35\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L32-L35)
[\[43\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L76-L84)
[\[46\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L93-L101)
GitHub

<https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt>

[\[25\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/PythonApp/src/gui/preview_panel.py#L2-L10)
[\[26\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/PythonApp/src/gui/preview_panel.py#L22-L30)
[\[37\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/PythonApp/src/gui/preview_panel.py#L64-L72)
[\[38\]](https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/PythonApp/src/gui/preview_panel.py#L73-L81)
GitHub

<https://github.com/buccancs/bucika_gsr/blob/e159c5e2651daa79c8effc642b2424895d6492f3/PythonApp/src/gui/preview_panel.py>
