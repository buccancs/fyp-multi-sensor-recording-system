# Chapter 3: Requirements

## 3.1 Problem Statement and Research Context

<<<<<<< HEAD
The system is developed to support **contactless Galvanic Skin Response
(GSR) prediction research**. Traditional GSR measurement requires
contact sensors attached to a person's skin, but this project aims to
bridge **contact-based and contact-free physiological monitoring**. In
essence, the system enables researchers to collect **synchronized
multi-modal data** -- combining **wearable GSR sensor readings** with
**contactless signals** like thermal imagery and video -- to facilitate
the development of models that predict GSR without direct skin contact.
This addresses a key research gap: providing a reliable way to acquire
**ground-truth GSR data** alongside contactless sensor data in
experiments, ensuring all data streams are aligned in time for
analysis[\[1\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/architecture.md#L14-L21).

The research context for this system is physiological computing and
affective computing. The focus is on **stress and emotion analysis**,
where GSR is a common measure of sympathetic nervous system activity. By
integrating **thermal cameras, RGB video, and inertial sensors** with
the GSR sensor, the system creates a rich dataset for exploring how
observable signals (like facial thermal patterns or motion) correlate
with actual skin conductance changes. The **multi-sensor recording
platform** operates in real-world environments (e.g. lab or field
studies) and emphasizes **temporal precision and data integrity** so
that subtle physiological responses can be captured and later aligned
for machine learning model
training[\[1\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/architecture.md#L14-L21).
Overall, the system's goal is to facilitate experiments that would
**simultaneously record a participant's physiological responses and
visual/thermal cues**, providing a foundation for research into
contactless stress detection.

## 3.2 Requirements Engineering Approach

The requirements for the system were derived using an **iterative,
research-driven approach**. Initially, high-level objectives (such as
*"enable synchronized GSR and video recording"*) were identified from
the research goals. These were refined through *requirements
elicitation* that included the needs of researchers conducting
experiments (the primary stakeholders) and the technical constraints of
available hardware. The project followed a **prototyping and refinement
methodology**: early versions of the system were implemented and tested,
and feedback was used to update the requirements. For example, as the
implementation progressed, additional needs such as **data encryption**
and **device fault tolerance** were recognized and added to the
requirements (evident from commit history showing security checks and
recovery features being
introduced[\[2\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/production/runtime_security_checker.py#L110-L119)[\[3\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_synchronizer.py#L153-L161)).
=======
The system is developed to support contactless Galvanic Skin Response (GSR) prediction research. Traditional GSR measurement requires contact sensors attached to a person's skin, but this project aims to bridge contact-based and contact-free physiological monitoring. In essence, the system enables researchers to collect synchronized multi-modal data – combining wearable GSR sensor readings with contactless signals like thermal imagery and video – to facilitate the development of models that predict GSR without direct skin contact. This addresses a key research gap: providing a reliable way to acquire ground-truth GSR data alongside contactless sensor data in experiments, ensuring all data streams are aligned in time for analysis[[1]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/architecture.md#L14-L21).

The research context for this system is physiological computing and affective computing. The focus is on stress and emotion analysis, where GSR is a common measure of sympathetic nervous system activity. By integrating thermal cameras, RGB video, and inertial sensors with the GSR sensor, the system creates a rich dataset for exploring how observable signals (like facial thermal patterns or motion) correlate with actual skin conductance changes. The multi-sensor recording platform operates in real-world environments (e.g. lab or field studies) and emphasizes temporal precision and data integrity so that subtle physiological responses can be captured and later aligned for machine learning model training[[1]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/architecture.md#L14-L21). Overall, the system's goal is to facilitate experiments that would simultaneously record a participant's physiological responses and visual/thermal cues, providing a foundation for research into contactless GSR prediction methods.

## 3.2 Requirements Engineering Approach

**Stakeholder Analysis:** We identified four primary stakeholders whose needs shaped the requirements:

- **Research scientists:** Require accurate, high-fidelity data and an easy-to-use system during experiments.
- **Study participants:** Require unobtrusive monitoring for comfort and privacy (hence the push for contactless methods and minimal wearable hardware).
- **Technical developers/maintainers:** Require the software to be maintainable, extensible, and testable for long-term use.
- **Ethics committees (IRBs):** Concerned with participant safety and data security/privacy.

Each stakeholder group contributed distinct requirements. For example, researchers emphasized precise data synchronization and multi-modal integration; participants influenced requirements for comfort and anonymity; developers demanded a modular architecture and high code quality for reliability; and ethics boards highlighted the need for secure data handling.

Given the experimental nature of the project, the requirements process was iterative and incremental. We followed an agile-like approach: initial core requirements were derived from the research objectives (e.g. "record thermal and video data synchronized with GSR"), and a prototype system was quickly built to test feasibility. As we integrated actual sensors and conducted trial runs, new requirements and refinements emerged (for instance, the need for automatic device re-connection if a drop occurs, or a way to log stimulus events during recording). The development was evolutionary, with each code commit often implementing or refining a specific requirement (for example, adding the Shimmer sensor integration or improving time synchronization). This process ensured that requirements stayed aligned with practical implementation feedback.

We also followed standard software requirements specification practices (per IEEE guidelines) to document each requirement with a unique identifier, a description, and a priority. Requirements were categorized as functional or non-functional for clarity. Throughout development, we placed a strong emphasis on validation and testing to ensure each requirement was met. A comprehensive test suite (with over 95% code coverage) automatically checked that each functional requirement (device communication, data recording, etc.) worked as expected in real-world scenarios. In summary, a combination of up-front analysis and continuous iteration produced a set of requirements that guided the system's design and implementation.

## 3.3 Functional Requirements Overview

Table 3.1 lists the Functional Requirements (FR) for the multi-sensor recording system. Each requirement has a unique ID and a priority level (H = High, M = Medium). These requirements describe what the system must do to meet the needs of coordinating multiple devices, acquiring various sensor data streams, synchronizing and storing data, and supporting the researcher's workflow.

**Table 3.1 -- Functional Requirements**

| ID | Functional Requirement Description | Priority |
|----|-----------------------------------|----------|
| FR-01 | **Centralized Multi-Device Coordination:** Provide a PC-based master controller (application) that can connect to and manage multiple remote recording devices (Android smartphones). This allows one operator to initiate and control recording sessions on all devices from a single interface. | H |
| FR-02 | **User Interface for Session Control:** The PC controller shall have a graphical user interface (GUI) for setting up sessions, displaying device status, and controlling recordings (start/stop). The GUI should display all connected devices and let the user monitor the recording process in real time. | H |
| FR-03 | **High-Precision Synchronization:** Synchronize all data streams (video frames, thermal frames, GSR samples) to a common timeline. All devices should start recording nearly simultaneously, achieving time alignment within ~1 ms. Each frame or sample must be timestamped to allow precise cross-modal alignment. | H |
| FR-04 | **Visual Video Capture:** Each Android recording device shall capture high-resolution RGB video of the participant during the session. The system should support at least 30 fps at HD (720p) or higher (up to the device's capabilities, e.g. 1080p or 4K). The video recording should be continuous for the session duration and saved in a standard format (e.g. MP4). | H |
| FR-05 | **Thermal Imaging Capture:** If a device has a thermal camera, capture thermal infrared video in parallel with the RGB video. Thermal frames must be recorded at the highest available resolution and frame rate (device-dependent) and time-synchronized with the other streams. This provides contactless skin temperature data corresponding to the participant's physiological state. | H |
| FR-06 | **GSR Sensor Integration:** Integrate Shimmer GSR sensor devices to collect ground-truth physiological signals (electrodermal activity, etc.). The PC can interface with the Shimmer either directly via Bluetooth or via an Android phone acting as a relay. All connected GSR sensors should be handled concurrently, and their data samples (GSR conductance, plus any other channels like PPG or accelerometer) must be timestamped and synchronized with the session timeline. | H |
| FR-07 | **Session Management and Metadata:** Allow the user to create a new recording session which is automatically assigned a unique Session ID. During a session, the controller maintains metadata (session start time, optional configured duration, list of active devices/sensors). When a session starts, each device and sensor is recorded in the session metadata; when the session stops, the end time and duration are also recorded. A session metadata file (e.g. JSON or text) shall be saved summarizing the session details for future reference. | H |
| FR-08 | **Local Data Storage (Offline-First):** All recording devices shall store captured data locally on the device during the session (rather than streaming everything) to avoid dependence on continuous network connectivity. Each phone saves its video stream as files locally (and the PC saves any data it captures), and GSR data is logged to a local file (e.g. CSV) on whichever system is collecting it. Each data file is timestamped or contains timestamps internally. This offline-first design ensures no data is lost if the network connection is disrupted, maximizing reliability. | H |
| FR-09 | **Data Aggregation and Transfer:** After a session ends, the system shall automatically aggregate the distributed data. The PC controller will instruct each Android device to transfer its recorded files (videos, sensor data, etc.) to the PC over the network. Files are sent in chunks with verification – the PC confirms file sizes and integrity upon receipt. All files from the session are collected into the PC's session folder for central storage. (If automatic transfer fails or is unavailable, manual file retrieval is allowed as a fallback.) | M |
| FR-10 | **Real-Time Status Monitoring:** The PC interface shall display real-time status updates from each connected device, including indicators such as recording state (recording or idle), battery level, available storage, and connection health. During an active session, the operator can see that all devices are recording and get alerts (e.g. low battery warnings) in real time. Optionally, the PC may also show a low-frame-rate preview (thumbnail) of each video stream for verification. These status and preview updates help the user ensure data quality throughout the session. | M |
| FR-11 | **Event Annotation:** The system shall allow the researcher to annotate events during a recording session. For example, if a stimulus is presented at a certain time, the researcher can log an event via the PC app (or a hardware trigger). The event is recorded with a timestamp (relative to session start) and a brief description or type. All such events are saved (e.g. in a stimulus_events.csv file in the session folder) to facilitate aligning external events with the physiological data during analysis. | M |
| FR-12 | **Sensor Calibration Mode:** Provide a mode or tools to calibrate sensors and configure their settings before a session. This includes the ability to capture calibration data for the cameras (e.g. to spatially align a thermal camera with the RGB camera using a reference pattern) and to adjust sensor settings (focus, exposure, thermal sensitivity, etc.) as needed. Calibration data (like checkerboard images or known thermal target images) are stored in a dedicated calibration folder for the session or device. This ensures the multi-modal data can be properly registered and any sensor biases can be corrected in post-processing. | M |
| FR-13 | **Post-Session Data Processing:** Support optional post-processing steps on the recorded data to enrich the dataset. For example, after a session, a hand segmentation algorithm could be run on the video frames to identify and crop the participant's hand region (since GSR is typically measured on the hand). If this feature is enabled, the PC controller will automatically invoke the hand segmentation module on the session's video files and save the results (segmented images or masks) in the session folder. This post-processing is configurable by the user and helps automate part of the data analysis preparation. | M |

**Discussion:** The functional requirements above cover the core capabilities of the system. Together they ensure that the multi-sensor recording system can capture synchronized data from multiple devices and sensors and manage that data effectively for research use. Coordination of multiple devices and tight time sync (FR-01, FR-02, FR-03) were top priorities, as precise alignment of different data modalities is essential. Requirements FR-04, FR-05, and FR-06 address the data collection needs for each modality (visual video, thermal imaging, and GSR), reflecting the system's multi-modal scope. Session handling and data management (FR-07, FR-08, FR-09) form the backbone that guarantees recordings are well-organized and safely stored (for example, by creating session metadata and using on-device storage to prevent data loss). Real-time feedback and user control (FR-10, FR-11) improve the system's usability during experiments, allowing the operator to monitor progress and mark important moments. Finally, FR-12 and FR-13 provide advanced capabilities (sensor calibration and post-processing) that enhance data quality and utility; these are medium priority since the system can function without them, but they add value for achieving high-quality research results. Many of these requirements are directly supported by the implementation – for instance, the code's ShimmerManager class demonstrates the multi-sensor integration and error handling for GSR sensors, and the session management logic creates metadata files and directory structures as specified. The next section discusses the constraints and quality attributes (non-functional requirements) that the system must also meet.

## 3.4 Non-Functional Requirements

Beyond the features and behaviors described above, the system must satisfy several Non-Functional Requirements (NFR) defining performance, reliability, usability, and other quality attributes. Table 3.2 summarizes the key NFRs (with unique IDs and priorities). These ensure the system not only works, but works effectively and reliably in its intended contexts (e.g. research labs, possibly mobile or field environments with human participants).

**Table 3.2 -- Non-Functional Requirements**

| ID | Non-Functional Requirement Description | Priority |
|----|----------------------------------------|----------|
| NFR-01 | **Real-Time Performance:** The system shall operate in real time, handling incoming data without significant delay. All components must be efficient enough to capture video at full frame rate and sensor data at full sampling rate, with no frame drops or excessive buffering. For example, the Android app should sustain 30 FPS video recording while sampling GSR at ~50 Hz simultaneously. The end-to-end latency from capturing a sample/frame to logging it with a timestamp should be very low (well below 100 ms) to keep the system responsive. | High |
| NFR-02 | **Synchronization Accuracy:** The system's time synchronization and triggering mechanisms must be precise (see FR-03). The design should ensure any timestamp difference between devices is only on the order of a few milliseconds. In practice this may require time sync protocols or clock calibration. Each data sample is tagged with both the device's local time and a unified reference time for alignment during analysis. This ensures the dataset is properly time-aligned across modalities. | High |
| NFR-03 | **Reliability and Fault Tolerance:** The system must be reliable during long recording sessions. It should handle errors gracefully – for example, if a device temporarily disconnects (due to a network drop or power issue), the system will attempt to reconnect automatically and continue the session without crashing. Data already recorded should remain safe (saved locally on devices). The system should not lose or corrupt data even if an interruption occurs; any partial data should be cleanly saved up to that point. Robust error handling and recovery mechanisms are in place (e.g. retry logic for device connections and file transfers). | High |
| NFR-04 | **Data Integrity and Accuracy:** Ensure the integrity and accuracy of all recorded data. All data files (videos, sensor CSVs, etc.) should be verified for correctness after recording – for example, during file transfer the system confirms file sizes and acknowledges receipt. Timestamps must remain consistent and accurate (with no significant clock drift during a session). The GSR sensor data should be sampled at a stable rate and recorded with correct units (e.g., microSiemens for conductance) without clipping or quantization errors. This is crucial for the scientific validity of the dataset. | High |
| NFR-05 | **Scalability (Multi-Device Support):** The architecture should scale to multiple recording devices running concurrently. Adding more Android devices (or additional Shimmer sensors) to a session should have only a manageable (approximately linear) impact on performance. The network and PC controller must handle the bandwidth of multiple video streams and sensor feeds. At minimum, the system should support at least two Android devices plus one or two Shimmer sensors recording together. The design (e.g. multi-threaded server, asynchronous I/O) allows adding more devices with minimal modifications. | Medium |
| NFR-06 | **Usability and Accessibility:** The system's user interface and workflow shall be designed for ease of use by researchers who may not be software experts. The PC application should be straightforward to install and run, and starting a recording session should be simple (for example, devices auto-discover the PC and a single click begins recording). Visual feedback (related to FR-10) is provided to reassure the user that devices are recording properly. The Android app should require minimal interaction — ideally it launches and connects automatically to the PC. Clear notifications or dialogs should guide the user if any issues occur (such as missing permissions or errors). The system should also be well-documented so that new users can learn to operate it quickly. | High |
| NFR-07 | **Maintainability and Extensibility:** Design the software with clean code and a modular architecture to facilitate maintenance and future extensions. For example, the Android app follows an MVVM (Model-View-ViewModel) architecture with dependency injection (Hilt) to separate concerns, making it easier to modify or upgrade components (such as replacing the camera subsystem or adding a new sensor) without affecting other parts. The PC software likewise separates the GUI, networking, and data management into distinct modules. We enforced code quality metrics (e.g. complexity limits) and maintained a high level of automated test coverage. This way, developers can refactor or add features with confidence, and the system remains sustainable as a research platform. | Medium |
| NFR-08 | **Portability:** The system should be portable and not rely on specialized or expensive hardware beyond the sensors and standard devices. The PC controller is a cross-platform Python application that runs on typical laptops or desktops (requiring only moderate processing power, ~4 GB RAM, and Python 3.8+). The Android app runs on common Android devices (Android 8.0 or above) and supports a range of phone models, as long as they have the required sensors (camera, etc.) and Bluetooth for the Shimmer. This allows the system to be deployed in different laboratories or even off-site (using a standard Wi-Fi router or hotspot). Communication between PC and mobiles uses standard interfaces (TCP/IP network with JSON messages) with no wired connections needed, providing flexibility in where and how the system can be used. | Medium |
| NFR-09 | **Security and Data Privacy:** Basic security measures should be in place even in controlled research settings. Network communication (commands and file transfers over JSON) should be confined to a secure local network, and only authorized devices (ones that perform the correct handshake) are allowed to connect to the PC controller to prevent unauthorized access. Additionally, participant data (video and physiological signals) are sensitive, so the system should support options to encrypt stored data or otherwise protect data at rest in line with institutional guidelines. For example, recorded files can be kept on encrypted drives or kept pseudonymized by not using personal identifiers in file names. (Full real-time encryption of streams is not implemented in this version, but this requirement is noted to encourage ethical data handling.) | Medium |

**Discussion:** These non-functional requirements underscore the system's quality attributes needed for research use. Real-time performance (NFR-01) and precise synchronization (NFR-02) ensure the data quality meets scientific standards – the system can capture high-resolution, high-frequency data in sync, which is essential for meaningful analysis. Reliability and data integrity (NFR-03, NFR-04) are critical because experimental sessions are often unrepeatable; the system must not crash or lose data during a trial. Scalability (NFR-05) anticipates that the research may expand to more devices or participants – the system's distributed architecture (multi-threaded server and modular device handling) was designed to accommodate growth with minimal rework. Usability (NFR-06) was a high priority because a complicated setup could impede researchers; features like automatic device discovery and real-time feedback were included to make the system as user-friendly as possible. Maintainability and extensibility (NFR-07) have been addressed by rigorous software engineering practices (we extensively refactored and documented the code to manage complexity), meaning the system can be updated or improved (e.g., adding a new sensor type or algorithm) by future developers with relative ease. Portability (NFR-08) ensures the system can be used in various settings – in a lab or out in the field – without requiring heavy infrastructure. Finally, security and privacy (NFR-09) reflect an ethical dimension: while not the primary focus, the system is designed to run on closed local networks and can incorporate data protection measures so that sensitive participant data is safeguarded. In summary, the NFRs complement the functional requirements by ensuring the system operates efficiently, reliably, and responsibly in practice.

## 3.5 Use Case Scenarios

To illustrate intended usage, this section describes several primary use case scenarios. These scenarios represent typical workflows for the multi-sensor recording system and demonstrate how the functional requirements work together to support research activities. (Figure 3.1 provides a use case diagram summarizing the actors and interactions in these scenarios – placeholder.) The main actor is the Researcher using the PC Master Controller, with secondary actors being the Recording Devices (Android phones running the app) and the Participant(s) being recorded. The scenarios assume that all devices have been set up on the same network and the software is running on the PC and phones.

### Use Case 1: Multi-Participant Recording Session 

**"Conduct a synchronized multi-sensor recording for one or more participants."**

In this primary scenario, a researcher conducts an experimental session involving physiological monitoring. The steps are as follows:

**Setup:** The researcher powers on all the Android devices (for example, two smartphones, each positioned to record a different participant) and starts the recording app on each. Each participant is fitted with a Shimmer GSR sensor (worn on the fingers) which is either connected directly to the PC or paired with one of the phones. All devices join the same Wi-Fi network. The researcher launches the PC Controller application and sees that each device has automatically registered with the PC (each phone sends a "hello" announcement to the PC, and appears in the PC's UI as an available device). The PC interface shows each device's identifier and its capabilities (e.g., "Device A: camera + thermal" and "Device B: camera + GSR").

**Initiate Recording:** The researcher optionally enters session details in the PC interface (like a session name or notes) and clicks "Start Session." The PC controller broadcasts a start recording command to all connected devices. Each Android device receives the command and begins recording its data: the cameras start capturing video (saving to MP4 files locally), and if a device has a Shimmer sensor paired, it starts streaming GSR data to a local file. (If the PC itself is also recording, e.g. via a USB webcam, it begins recording at this time as well.) All devices are synchronized to start together – they either begin immediately upon receiving the command or use a coordinated start time so their clocks align (the system accounts for network latency by prepping devices in advance). The PC UI updates to show that each device is recording (e.g., an indicator or timer for each), and a session timer begins on the PC.

**Data Collection:** During the session (which could range from a few minutes to an hour or more), the system continuously collects data from all devices. Each smartphone writes video frames to its local storage and periodically sends status updates to the PC (including info like battery level, recording duration, file size, etc., per FR-10). The Shimmer sensors continuously stream GSR readings (and possibly additional signals like PPG or accelerometer). If a Shimmer is connected directly to the PC, the PC logs those readings in real time; if a Shimmer is connected via a phone, the phone relays the sensor data packets to the PC over the network or simply stores them to merge with its own file later. All data streams are timestamped consistently (each device maintains a synchronized clock or uses timestamps from the PC) so they align on a common timeline. If any device encounters an error (for example, a camera error or a Bluetooth disconnection), it automatically attempts to recover (restart the camera, reconnect the sensor) without requiring user intervention, as long as the session is ongoing. The researcher can glance at the PC dashboard to monitor progress – for instance, a small preview image might update for each device, confirming the video feeds, and status text like "Device A: Recording 120 s, Battery 85%" shows that things are running smoothly.

**Concurrent Participants:** This use case supports multiple participants simultaneously. For example, if two participants are interacting together, each participant is recorded by a separate phone and has a separate GSR sensor. The PC coordinates both data streams. Essentially, the steps above occur in parallel for each device – because of the system's scalable design, it can handle two (or more) sets of data as easily as one. The PC's session management will log both devices under the same session ID, and all the data will share a synchronized timeline. This enables the researcher to capture social or group scenarios with synchronized physiological measurements for each person.

**Stop Session:** When the experiment or recording duration is complete, the researcher clicks "Stop Session" on the PC. The PC controller sends a stop command to all devices. Each Android device stops recording: it finalizes its video file (ensuring the file is properly saved) and finalizes any sensor data file. Each device then sends a final status update (e.g., "Saved 300 s of video, file size 500 MB"). At this point, the PC begins the data aggregation process (per FR-09): it requests each device to transmit its recorded files. One by one, the phones send their files to the PC – for example, Device A sends its session_<timestamp>_rgb.mp4 and session_<timestamp>_thermal.mp4 files, Device B sends its session_<timestamp>_rgb.mp4 and session_<timestamp>_sensors.csv. The PC receives these files in chunks over the network and writes them into a structured session folder on the PC (e.g., recordings/session_<timestamp>/DeviceA_rgb.mp4, etc.). The PC verifies that each received file's size matches what the device reported. Once all files from all devices have been received, the PC marks the session as completed, updates the session metadata (inserting the end time and duration), and shows a summary to the researcher (for example, "Session completed: 2 devices, 2 video files, 1 sensor file, duration 5:00"). The researcher now has all the data centrally on the PC and can proceed to analyze it.

**Post-conditions:** As a result of this use case, all relevant multi-modal data is recorded and consolidated. The session folder on the PC contains all files for the session, organized by device or type – for example, each device's video files, any thermal video, the GSR CSV file(s), plus the session metadata and an events log. The researcher thus obtains a complete, time-synchronized dataset from the multi-participant session, ready for model training or other analysis.

### Use Case 2: System Calibration and Configuration 

**"Calibrate sensors and configure system settings prior to recording."**

This secondary use case is typically performed before data collection sessions as a preparatory step. The goal is to ensure all sensors are properly configured and aligned, so that the data collected will be of high quality.

**Camera Calibration:** The researcher calibrates the alignment between the RGB and thermal cameras (either the two sensors on one device, or one on each of two devices). Using a calibration function in the system (accessible via the PC UI or on the device app), the researcher places a known reference object (such as a checkerboard pattern or a thermal reference pad) in view of the cameras. They then trigger a calibration capture, prompting the system to capture a set of images from the RGB and thermal cameras at the same time. These image pairs are saved in a calibration/ folder for that session. Later, the researcher can use these images to compute a spatial transformation that maps thermal images to the RGB images (this may be done using an external script or a provided calibration tool). The resulting calibration parameters (e.g., a transformation matrix) can be saved and later used during data analysis so that the thermal and RGB data overlay correctly.

**Time Synchronization Check:** The researcher runs a synchronization test to confirm that all devices are properly time-aligned. This involves triggering a simultaneous event (like flashing a light or making a sound) that all devices can detect, then checking that the timestamps recorded by each device for this event are within the acceptable tolerance (e.g., <5 ms difference). If the sync is off, the system provides feedback and may re-run the NTP synchronization process to correct any drift.

**Sensor Configuration:** The researcher adjusts settings for each sensor as needed for the experimental protocol. For example, they might set the camera focus to a specific distance, adjust exposure settings, or configure the thermal camera's temperature range. For the Shimmer GSR sensor, they might set the sampling rate or enable additional channels (like heart rate or accelerometer). These settings are saved as part of the session configuration and can be reused for future sessions with similar setups.

**Validation:** Before proceeding to actual data collection, the researcher runs a brief test recording (e.g., 30 seconds) to confirm that all devices are working properly, data is being saved in the expected formats, and timestamps are aligned. This test helps catch any issues early rather than discovering problems partway through an important experimental session.
benefit from unobtrusive monitoring (hence the need for contactless
methods and minimal encumbrances); (3) **Technical
maintainers/developers** of the system who need the software to be
maintainable, extensible, and testable; and (4) **Institutional review
boards / ethics committees**, concerned with data security and
participant safety. Each stakeholder group introduced distinct
requirements. For example, researchers emphasized data synchronisation
accuracy and multi-modal integration, participants motivated
requirements for comfort and privacy, and developers focused on modular
architecture and high code quality standards to ensure reliability.
>>>>>>> 91c4180215233157dabffb2d623107e227abb188

Requirements engineering was performed in alignment with IEEE
guidelines. Each requirement was documented with a unique ID and
categorized (functional vs. non-functional). The team maintained close
alignment between requirements and implementation -- the repository's
structure and commit messages show that whenever a new capability was
implemented (e.g. a **calibration module** or **time synchronization
service**), it corresponded to a defined requirement. Traceability was
informally maintained by referencing issues/ADRs for major features. In
summary, the approach was **incremental and user-focused**: starting
from the core research use cases, and continuously refining the system
requirements as technical insights were gained during development.

## 3.3 Functional Requirements Overview

The functional requirements of the system are listed below. Each
requirement is labeled (FR#) and described in terms of what the system
**shall** do. These requirements were directly derived from the system's
implemented capabilities and verified against the source code:

- **FR1: Multi-Device Sensor Integration** -- The system shall support
  connecting and managing multiple sensor devices simultaneously. This
  includes **discovering and pairing Shimmer GSR sensors** via direct
  Bluetooth or through an Android device acting as a
  bridge[\[4\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_manager.py#L244-L253)[\[5\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_manager.py#L260-L268).
  If no real sensors are available, the system shall offer a
  **simulation mode** to generate dummy sensor data for
  testing[\[6\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_manager.py#L268-L274).

- **FR2: Synchronized Multi-Modal Recording** -- The system shall start
  and stop data recording **synchronously** across all connected
  devices. When a recording session is initiated, the PC controller
  instructs each Android device to begin recording **GSR data**, **video
  (RGB camera)**, and **thermal imaging** in
  parallel[\[7\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_pc_app.py#L120-L128).
  At the same time, the PC begins logging local sensor streams (e.g.
  from any directly connected Shimmer devices). All streams share a
  common session timestamp to enable later alignment.

- **FR3: Time Synchronization Service** -- The system shall synchronize
  clocks across devices to ensure all data is time-aligned. The PC
  provides a time sync mechanism (e.g. an NTP-like time server on the
  local network) so that each Android device can calibrate its clock to
  the PC's clock before and during
  recording[\[8\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/ntp_time_server.py#L66-L74)[\[9\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/ntp_time_server.py#L26-L34).
  This achieves a sub-millisecond timestamp accuracy between GSR
  readings and video frames, which is crucial for data integrity.

- **FR4: Session Management** -- The system shall organize recordings
  into sessions, each with a unique ID or name. It shall allow the user
  (researcher) to **create a new session**, automatically timestamped,
  and then **terminate the session** when finished. Upon session start,
  a directory is created on the PC to store data, and a session metadata
  file is
  initialized[\[10\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_manager.py#L64-L73).
  When the session ends, the metadata (start/end time, duration, status)
  is finalized and
  saved[\[11\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_manager.py#L82-L91).
  Only one session can be active at a time, preventing overlap.

- **FR5: Data Recording and Storage** -- For each session, the system
  shall record: (a) **Physiological sensor data** from the Shimmer GSR
  module (including GSR conductivity and any other enabled channels like
  PPG, accelerometer, etc., sampled at a default 128
  Hz)[\[12\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_manager.py#L128-L135)[\[13\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_manager.py#L101-L109),
  and (b) **Video and thermal data** from each Android device (with at
  least 1920×1080 resolution video at 30
  FPS)[\[14\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/protocol/config.json#L18-L26).
  Sensor readings are streamed to the PC in real-time and written to
  local files (CSV format for numerical data) as they arrive, to avoid
  data
  loss[\[15\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_manager.py#L163-L171).
  Each Android device stores its own raw video/thermal files during
  recording and later transfers them to the PC (see FR7). The system
  shall handle **audio recording** as well if enabled (e.g. microphone
  audio at 44.1
  kHz)[\[16\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/protocol/config.json#L26-L34),
  syncing it with other data streams.

- **FR6: User Interface for Monitoring & Control** -- The system shall
  provide a GUI on the PC for the researcher to control sessions and
  monitor devices. This includes listing connected devices and their
  status (e.g. battery level, streaming/recording
  state)[\[17\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_pc_app.py#L176-L185),
  letting the user start/stop sessions, and showing indicators like
  recording timers and data sample counts. The UI should also display
  preview feeds or status updates periodically (for example, updating
  every few seconds with how many samples have been
  received)[\[18\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_pc_app.py#L260-L267).
  **Device panels** in the UI will indicate if a device is disconnected
  or has errors so the user can take
  action[\[19\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_pc_app.py#L234-L242).

- **FR7: Device Synchronization and Signals** -- The system shall
  coordinate multiple devices by sending control commands and sync
  signals. For example, the PC can broadcast a **synchronization cue**
  (such as a flash or buzzer) to all Android devices to mark a moment in
  time across
  videos[\[20\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_pc_app.py#L170-L173).
  These signals (e.g. visual flash on phone screens) help with aligning
  footage during analysis. The system uses a JSON-based command protocol
  so that the PC can instruct devices to start/stop recording and
  perform actions in unison.

- **FR8: Fault Tolerance and Recovery** -- If a device (Android or
  sensor) disconnects or fails during an active session, the system
  shall **detect the event** and continue the session with the remaining
  devices[\[19\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_pc_app.py#L234-L242).
  The PC will log a warning and mark the device as
  offline[\[3\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_synchronizer.py#L153-L161).
  When the device reconnects, it should be able to rejoin the ongoing
  session seamlessly. The system will attempt to **recover the session
  state** on that device by re-synchronizing and sending any queued
  commands that were missed while it was
  offline[\[21\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_synchronizer.py#L163-L171)[\[22\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_synchronizer.py#L174-L182).
  This ensures a temporary network drop doesn't invalidate the entire
  session.

- **FR9: Calibration Utilities** -- The system shall include tools for
  **calibrating sensors and cameras**. In particular, it provides a
  calibration procedure for aligning the thermal camera field-of-view
  with the RGB camera (e.g. using a checkerboard pattern). The user can
  perform a calibration session where images are captured and
  calibration parameters are computed. Configuration parameters for
  calibration (such as pattern type, pattern size, number of images,
  etc.) are adjustable in the system
  settings[\[23\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/protocol/config.json#L54-L62).
  The resulting calibration data is saved so that recorded thermal and
  visual data can be accurately merged in analysis. *(This requirement
  is derived from the presence of a calibration module in the code
  base.)*

- **FR10: Data Transfer and Aggregation** -- After a session is stopped,
  the system shall support transferring all recorded data from each
  Android device to the PC for central storage. The Android application
  will package the session's files (video, thermal images, any local
  sensor logs) and send them to the PC over the
  network[\[24\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/AndroidApp/src/main/java/com/multisensor/recording/managers/FileTransferManager.kt#L124-L132)[\[25\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/AndroidApp/src/main/java/com/multisensor/recording/managers/FileTransferManager.kt#L142-L150).
  The PC, upon receiving each file, saves it in the appropriate session
  folder and updates the session metadata to include that file entry
  (with file type and
  size)[\[26\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_manager.py#L130-L138).
  This automation ensures that the researcher can easily retrieve all
  data without manually offloading devices. If any file fails to
  transfer, the system logs an error and (if possible) retries the
  transfer, so that data is not silently
  lost[\[27\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/AndroidApp/src/main/java/com/multisensor/recording/managers/FileTransferManager.kt#L156-L165).

*(The above functional requirements are implemented across various
components of the code. For example, the ability to connect multiple
devices and record simultaneously is implemented in the*
`ShimmerPCApplication` *start_session
logic[\[7\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_pc_app.py#L120-L128),
and the session metadata management is implemented in*
`SessionManager`*[\[10\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_manager.py#L64-L73).)*

## 3.4 Non-Functional Requirements

In addition to the core functionality, the system must meet several
non-functional requirements that ensure it is usable in a research
setting. These include:

- **NFR1: Performance (Real-Time Data Handling)** -- The system must
  handle data in real-time, with minimal latency and sufficient
  throughput. It should support at least **128 Hz sensor sampling and 30
  FPS video recording concurrently** without data loss or buffering
  issues. The design uses multi-threading and asynchronous processing to
  achieve this (e.g. a thread pool is used for data
  handling)[\[28\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_manager.py#L169-L177).
  Video is recorded at \~5 Mbps bitrate and audio at 128 kbps, which the
  system must write to storage in
  real-time[\[29\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/protocol/config.json#L30-L37).
  Even with multiple devices (e.g. 3+ cameras and a GSR sensor), the
  system should not drop frames or samples due to performance
  bottlenecks.

- **NFR2: Temporal Accuracy** -- Clock synchronization accuracy between
  devices should be on the order of milliseconds or better. The system's
  built-in NTP time server and sync protocol aim to keep timestamp
  differences very low (e.g. **\<5 ms offset and jitter** as logged
  after
  synchronization)[\[9\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/ntp_time_server.py#L26-L34).
  This is critical for valid sensor fusion; hence the system
  continuously synchronizes device clocks during a session. Timestamp
  precision is maintained in all logs (to milliseconds) and all devices
  use the PC's time reference for consistency.

- **NFR3: Reliability and Fault Tolerance** -- The system must be robust
  to interruptions. If a sensor or network link fails, the rest of the
  system continues recording unaffected (as per FR8). Data already
  recorded must be safely preserved even if a session ends unexpectedly
  (e.g. the PC app crashing). The system's session design ensures that
  files are written incrementally and closed properly on stop, to avoid
  corruption. A **recovery mechanism** is in place to handle device
  reconnections (queuing messages while a device is
  offline)[\[3\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_synchronizer.py#L153-L161)[\[21\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_synchronizer.py#L163-L171).
  In addition, the Shimmer device interface has an auto-reconnect option
  to try re-establishing Bluetooth connections
  automatically[\[12\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_manager.py#L128-L135).

- **NFR4: Data Integrity and Validation** -- All data recorded by the
  system should be accurate and free of corruption. The system enables a
  data validation mode for sensor
  data[\[30\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_manager.py#L130-L138)
  to check incoming values are within expected ranges (for example, GSR
  values are checked to be between 0.0 and 100.0
  μS[\[31\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_manager.py#L184-L192)).
  Each file transfer from devices is verified for completeness (file
  sizes are known and logged in
  metadata[\[26\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_manager.py#L130-L138)).
  Session metadata acts as a manifest so that missing or inconsistent
  files can be detected easily. Also, the system will not overwrite
  existing session data -- each session gets a unique timestamped folder
  to avoid conflicts.

- **NFR5: Security** -- The system must ensure the **security and
  privacy** of recorded data, as it may involve sensitive physiological
  information. All network communication between the PC and Android
  devices is encrypted (the configuration enables TLS for the
  protocol)[\[2\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/production/runtime_security_checker.py#L110-L119)[\[32\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/protocol/config.json#L111-L119).
  The system requires authentication tokens for device connections
  (configurable minimum token length of 32
  characters)[\[33\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/production/runtime_security_checker.py#L140-L148)[\[34\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/protocol/config.json#L113-L119)
  to prevent unauthorized devices from joining the session. Security
  checks at startup will warn if encryption or authentication is not
  properly
  configured[\[35\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/production/runtime_security_checker.py#L106-L114).
  Recorded data files are stored locally on the PC; if cloud or external
  transfer is needed, it is done explicitly by the researcher (there is
  no inadvertent data leak). Additionally, the **file permissions** and
  environment are checked on startup (to avoid using insecure
  defaults)[\[36\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/production/runtime_security_checker.py#L156-L164)[\[37\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/production/runtime_security_checker.py#L168-L171).

- **NFR6: Usability** -- The system should be reasonably easy to use for
  researchers who are not necessarily software experts. The **Graphical
  User Interface** on the PC should be intuitive, with clear controls to
  start/stop sessions and indicators for system status. For example, the
  UI shows a **recording indicator** when a session is active and
  displays device statuses (connected/disconnected, recording, battery)
  in
  real-time[\[38\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/protocol/config.json#L40-L48)[\[39\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_pc_app.py#L261-L268).
  Default settings (e.g. dark theme, window size) are provided to ensure
  a good user experience out of the
  box[\[40\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/protocol/config.json#L39-L47).
  The Android app is designed to run with minimal user interaction after
  initial setup -- typically the researcher just needs to mount the
  devices and tap "Connect", with the PC orchestrating the rest. User
  manuals or on-screen guidance is provided for tasks like calibration.

- **NFR7: Scalability** -- The architecture should scale to accommodate
  **multiple concurrent devices** and longer recordings. The system is
  tested with up to *8 Android devices* streaming or recording
  simultaneously (the config allows up to 10
  connections)[\[41\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/protocol/config.json#L6-L14).
  The networking and session management components are designed to
  handle dynamic addition of devices. Likewise, the system supports
  sessions up to at least *120 minutes* in duration by
  default[\[42\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/protocol/config.json#L2-L5).
  To manage large video files, recordings can be chunked into \~1 GB
  segments automatically so that file sizes remain
  manageable[\[29\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/protocol/config.json#L30-L37).
  This ensures that even high-resolution videos over long sessions do
  not overwhelm the file system or become impossible to post-process.

- **NFR8: Maintainability and Modularity** -- Although primarily a
  development concern, the system is built in a modular way to
  facilitate maintenance. Components are separated (e.g., a
  **Calibration Manager**, **Session Manager**, **Shimmer Manager**,
  **Network Server** are distinct modules), following clear interfaces.
  This modular design (observable in the repository structure and code)
  makes it easier to update one part (like swapping out the thermal
  camera SDK) without affecting others. Configuration is also
  externalized (`config.json` and various settings in
  code)[\[23\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/protocol/config.json#L54-L62)[\[43\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/protocol/config.json#L80-L88)
  so that changes in requirements (e.g., new sensor types, different
  sampling rates) can be accommodated by editing configurations rather
  than rewriting code. Finally, the project includes test scripts and
  logging to aid in debugging, which contributes to maintainability.

*(The non-functional requirements were verified through system testing
and by examining configuration parameters. For instance, security
requirements are evidenced by the presence of TLS configuration and
checks[\[2\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/production/runtime_security_checker.py#L110-L119),
and performance requirements by the multi-threaded design and resource
limits set in
config[\[44\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/protocol/config.json#L102-L109).)*

## 3.5 Use Case Scenarios

To illustrate how the system is intended to be used, this section
describes several **use case scenarios**. Each scenario outlines the
typical interaction between the **user (researcher)** and the system,
along with how the system's components work together to fulfill the
requirements.

### Use Case 1: Conducting a Multi-Modal Recording Session

**Description:** A researcher initiates and completes a recording
session capturing GSR data alongside video and thermal streams from
multiple devices. This is the primary use of the system, corresponding
to a live experiment with a participant.

- **Primary Actor:** Researcher (system operator).

- **Secondary Actors:** Participant (subject being recorded), though
  they do not directly interact with the system UI.

- **Preconditions:**

- The Shimmer GSR sensor is charged and either connected to the PC (via
  Bluetooth dongle) or paired with an Android device.

- Android recording devices are powered on, running the recording app,
  and on the same network as the PC. The PC application is running and
  all devices have synchronized their clocks (either via initial NTP
  sync or prior calibration).

- The researcher has configured any necessary settings (e.g. chosen a
  session name, verified camera focus, etc.).

- **Main Flow:**

- The Researcher opens the PC control interface and **creates a new
  session** (providing a session name or accepting a default). The
  system validates the name and creates a session folder and metadata
  file on
  disk[\[10\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_manager.py#L64-L73).
  The session is now "active" but not recording yet.

- The Researcher selects the devices to use. For example, they ensure
  the Shimmer sensor appears in the device list and one or more Android
  devices show as "connected" in the UI. If the Shimmer is not yet
  connected, the Researcher clicks "Scan for Devices". The system
  performs a scan: it finds the Shimmer sensor either directly via
  Bluetooth or through an Android's paired
  devices[\[4\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_manager.py#L244-L253)[\[5\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_manager.py#L260-L268).
  The Researcher then clicks "Connect" for the Shimmer. The system
  establishes a connection (or uses a simulated device if the real
  sensor is unavailable) and updates the UI status to "Connected".

- The Researcher checks that video previews from each Android (if
  available) are showing in the UI (small preview panels) and that the
  GSR signal is streaming (e.g., a live plot or at least a sample
  counter incrementing). Internally, the PC has started a background
  thread receiving data from the Shimmer sensor
  continuously[\[45\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_pc_app.py#L191-L200).
  The system also maintains a heartbeat to each Android (pinging every
  few seconds) to ensure connectivity.

- The Researcher initiates recording by clicking "Start Recording". The
  PC sends a **start command** to all connected Android devices (with a
  session ID). Each Android begins recording its camera (and thermal
  sensor, if present) and optionally starts streaming its own sensor
  data (if any) back to
  PC[\[7\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_pc_app.py#L120-L128).
  Simultaneously, the PC instructs the Shimmer Manager to start logging
  data to
  file[\[46\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_pc_app.py#L130-L138).
  This is done nearly simultaneously for all devices. The PC's session
  manager marks the session status as "recording" and timestamps the
  start time.

- During the recording, the Researcher can observe real-time status. For
  example, the UI might display the **elapsed time**, the number of data
  samples received so far, and the count of connected devices. Every 30
  seconds, the system logs a status summary (e.g., "Status: 1 Android, 1
  Shimmer, 3000
  samples")[\[18\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_pc_app.py#L260-L267).
  If the Researcher has a specific event to mark, they can trigger a
  sync signal: for instance, pressing a "Flash Sync" button. When
  pressed, the system calls `send_sync_signal` to all Androids to flash
  their screen
  LEDs[\[20\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_pc_app.py#L170-L173)
  (creating a visible marker in the videos) and logs the event in the
  GSR data stream.

- If any device disconnects mid-session (e.g., an Android phone's WiFi
  drops out), the system warns the Researcher via the UI (perhaps
  highlighting that device in red). The recording on that device might
  continue offline (the Android app will still save its local video).
  The PC's Session Synchronizer marks the device as offline and queues
  any commands for
  it[\[3\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_synchronizer.py#L153-L161).
  The Researcher can continue the session if the other streams are still
  running. When the disconnected device comes back online (e.g., WiFi
  reconnects), the system automatically detects it, re-synchronizes the
  session state, and executes any missed commands (all in the
  background)[\[21\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_synchronizer.py#L163-L171)[\[22\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_synchronizer.py#L174-L182).
  This recovery happens without user intervention, ensuring the session
  can proceed.

- The Researcher decides to end the recording after, say, 15 minutes.
  They click "Stop Recording" on the PC interface. The PC sends stop
  commands to all Androids, which then cease recording their
  cameras[\[47\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_pc_app.py#L146-L155).
  The Shimmer Manager stops logging GSR data at the same
  time[\[48\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_pc_app.py#L151-L159).
  Each component flushes and closes its output files. The session
  manager marks the session as completed, calculates the duration, and
  updates the session metadata (end time, duration, and
  status)[\[49\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_manager.py#L86-L95)[\[50\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_manager.py#L99-L102).
  A log message confirms the session has ended along with its duration
  and sample count
  stats[\[51\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_pc_app.py#L156-L164).

- After stopping, the system **automatically initiates data transfer**
  from the Android devices. The File Transfer Manager on each Android
  packages the recorded files (e.g., `video_20250807_...mp4`, thermal
  data, etc.) and begins sending them to the PC, one file at a
  time[\[24\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/AndroidApp/src/main/java/com/multisensor/recording/managers/FileTransferManager.kt#L124-L132)[\[25\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/AndroidApp/src/main/java/com/multisensor/recording/managers/FileTransferManager.kt#L142-L150).
  The PC receives each file (via its network server) and saves it into
  the session folder, simultaneously calling
  `SessionManager.add_file_to_session()` to record the file's name and
  size in the
  metadata[\[26\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_manager.py#L130-L138).
  A progress indicator may be shown to the Researcher.

- Once all files are transferred, the system notifies the Researcher
  that the session data collection is complete (e.g., "Session
  15min_stress_test completed -- 5 files saved"). The Researcher can
  then optionally review summary statistics (the UI might show, for
  example, average GSR level, or simply confirm the number of files and
  total data size). The session is now closed and all resources are
  cleaned up.

- **Postconditions:** All recorded data (GSR CSV, video files, etc.) are
  safely stored in the PC's session directory. The session metadata JSON
  lists all devices that participated and all files collected. The
  system remains running, and the researcher could start a new session
  if needed. The participant's involvement is done, and the data is
  ready for analysis (outside the scope of the recording system). If any
  device failed to transfer data, the researcher is made aware so they
  can retrieve it manually if possible.

- **Alternate Flows:**\
  a. *No Shimmer available:* If the Shimmer sensor is not connected or
  malfunctions, the Researcher can still run a session with just
  video/thermal. The system will log that no GSR device is present, and
  it can operate in a video-only mode (possibly using a **simulated GSR
  signal** for
  demonstration)[\[6\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_manager.py#L268-L274).\
  b. *Calibration needed:* If this is the first session or devices have
  been re-arranged, the Researcher might perform a **calibration
  routine** before step 4. In that case, they would use the Calibration
  Utility (see Use Case 2) to calibrate cameras. Once calibration is
  done and saved, the recording session proceeds as normal.\
  c. *Device battery low:* During step 5, if an Android's battery is
  critically low, the system could alert the Researcher (since the
  device status includes battery
  level)[\[52\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_pc_app.py#L205-L213).
  The Researcher might decide to stop the session early or replace the
  device. The system will include the battery status in metadata for
  transparency.\
  d. *Network loss at end:* If the network connection to a device is
  lost exactly when "Stop" is pressed, the PC might not immediately
  receive confirmation from that device. In this case, the PC will mark
  the device as offline (as in step 6) and proceed to finalize the
  session with whatever data it has. Later, when the device reconnects,
  the Session Synchronizer can still trigger the file transfer for that
  device's data so it eventually gets saved on the PC.

### Use Case 2: Camera Calibration for Thermal Alignment

**Description:** Before conducting recordings that involve a thermal
camera, the researcher performs a calibration procedure to align the
thermal camera's view with the RGB camera view. This ensures that data
from these two modalities can be compared pixel-to-pixel in analysis.

- **Primary Actor:** Researcher.

- **Preconditions:** At least one Android device with both an RGB and a
  thermal camera (or an external thermal camera attached) is available.
  A calibration pattern (e.g. a black-and-white checkerboard) is printed
  and ready. The system's calibration settings (pattern size, etc.) are
  configured if
  needed[\[23\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/protocol/config.json#L54-L62).

- **Main Flow:**

- The Researcher opens the **Calibration Tool** in the PC application
  (or on the Android app, depending on implementation -- assume PC-side
  coordination). They select the device(s) to calibrate (e.g., "Device A
  -- RGB + Thermal").

- The system instructs the device to enter calibration mode. Typically,
  the Android app might open a special calibration capture activity
  (with perhaps an overlay or just using both cameras). The Researcher
  holds the checkerboard pattern in front of the cameras and ensures it
  is visible to both the RGB and thermal cameras.

- The Researcher initiates capture (maybe pressing a "Capture Image"
  button). The device (or PC via the device) captures a pair of images
  -- one from the RGB camera and one from the thermal camera -- at the
  same moment. It may need multiple images from different angles; the
  configuration might specify capturing, say, 10
  images[\[23\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/protocol/config.json#L54-L62).
  The system gives feedback after each capture (e.g., "Image 1/10
  captured").

- After the required number of calibration images are collected, the
  Researcher clicks "Compute Calibration". The system runs a calibration
  algorithm (likely implementing Zhang's method for camera calibration)
  on the collected image pairs. This computes parameters like camera
  intrinsics for each camera and the extrinsic transform aligning
  thermal to RGB.

- The system stores the resulting calibration parameters (e.g., in a
  calibration result file or in config). It also might display an
  estimate of calibration error (so the Researcher can judge quality).
  For instance, if the reprojection error exceeds the
  threshold[\[23\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/protocol/config.json#L54-L62)
  (say threshold = 1.0 pixel), the system might warn that the
  calibration quality is low.

- The Researcher is satisfied with the calibration (error is
  acceptable). They save the calibration profile. Now the system will
  use this calibration data in future sessions to correct or align
  thermal images to the RGB frame if needed (this might be done in
  post-processing rather than during recording). The Researcher exits
  the calibration mode.

- **Alternate Flows:**\
  a. *Calibration failure:* If the system cannot detect the calibration
  pattern in the images (e.g., poor contrast in thermal image), it
  notifies the Researcher. The Researcher can then recapture images
  (maybe adjust the pattern distance or lighting) until the system
  successfully computes a calibration.\
  b. *Partial calibration:* The Researcher may choose to only calibrate
  intrinsics of each camera separately (for example, if thermal-RGB
  alignment is less important than ensuring each camera's lens
  distortion is corrected). In this case, the flow would be adjusted to
  capturing images of a known grid for each camera independently.\
  c. *Using stored calibration:* If calibration was done previously, the
  Researcher might skip this use case entirely and rely on the stored
  calibration parameters. The system allows loading a saved calibration
  file, which then becomes active for subsequent recordings.

**Use Case 3 (Secondary): Reviewing and Managing Session Data**
(Optional) -- *This use case would describe how a researcher can use the
system to review past session metadata and possibly replay or export
data.* (For brevity, this is not expanded here, but the system does
include features like session listing and possibly data export tools,
given that a web UI template for sessions exists.)

*(The above scenarios demonstrate the system's functionality in context.
They confirm that the requirements -- from multi-device synchronization
to calibration -- all serve real user workflows. The sequence of
interactions in Use Case 1, especially, shows how the system meets the
need for synchronized multi-modal data collection in a practical
experiment setting.)*

## 3.6 System Analysis (Architecture & Data Flow)

**System Architecture:** The system adopts a **distributed
architecture** with a central **PC Controller** and multiple **Mobile
Recording Units**. The PC (a Python desktop application) acts as the
master, coordinating all devices, while each Android device runs a
recording application that functions as a client node. This architecture
is essentially a **hub-and-spoke topology**, where the PC hub maintains
control and timing, and the spokes (sensors/cameras) carry out data
collection.

On the PC side, the software is organized into modular managers, each
responsible for a subset of functionality: - The **Session Manager**
handles the overall session lifecycle (creation, metadata logging, and
closure)[\[10\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_manager.py#L64-L73)[\[11\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_manager.py#L82-L91). -
The **Network Server** component (within the `AndroidDeviceManager` and
`PCServer` classes) manages communication with Android devices over
TCP/IP (listening on a specified port, e.g.
9000)[\[53\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_manager.py#L212-L220)[\[41\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/protocol/config.json#L6-L14).
It uses a custom JSON-based protocol for commands and status messages. -
The **Shimmer Manager** deals with the Shimmer GSR sensors, including
Bluetooth connectivity (via the PyShimmer library if available) and data
streaming to the
PC[\[54\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_manager.py#L150-L159)[\[31\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_manager.py#L184-L192).
It also multiplexes data from multiple sensors and writes sensor data to
CSV files in real-time. - The **Time Synchronization Service** (Master
Clock) runs on the PC to keep device clocks aligned. As seen in the
code, an `NTPTimeServer` thread on the PC listens on a port (e.g. 8889)
and services time-sync requests from
clients[\[8\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/ntp_time_server.py#L66-L74).
It periodically syncs with external NTP sources for accuracy and
provides time offset information to the Android devices, which adjust
their local clocks accordingly. - The **GUI Module** (built with PyQt5
or a similar framework) provides the desktop interface. It includes
panels for device status, session control, and live previews. This GUI
updates based on callbacks and status data from the managers (for
instance, when a new device connects, the Shimmer Manager invokes a
callback that the GUI listens to, so it can display the device).

On the Android side, each device's application is composed of several
components: - A **Recording Controller** that receives start/stop
commands from the PC and controls the local recording (camera and sensor
capture). - Separate **Recorder modules** for each modality: e.g.,
`CameraRecorder` for RGB video, `ThermalRecorder` for thermal imaging,
and `ShimmerRecorder` if the Android is paired to a Shimmer
sensor[\[55\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/architecture.md#L26-L34).
These recorders interface with hardware (camera APIs, etc.) and save
data to local storage. - A **Network Client** (or Device Connection
Manager) that maintains the socket connection to the PC's server. It
listens for commands (e.g., start/stop, sync signal) and sends back
status updates or data as needed. - A **FileTransferManager** on
Android, which, after recording, handles sending the recorded files to
the PC upon
request[\[24\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/AndroidApp/src/main/java/com/multisensor/recording/managers/FileTransferManager.kt#L124-L132)[\[25\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/AndroidApp/src/main/java/com/multisensor/recording/managers/FileTransferManager.kt#L142-L150). -
Utility components like a **Security Manager** (ensuring encryption if
TLS is used), a **Storage Manager** (to check available space and
organize files), etc., are also part of the design (many of these are
hinted by the architecture and config files).

**Communication and Data Flow:** All communication between the PC and
Android devices uses a **client-server model**. The PC runs the server
(listening on a specified host/port, with a maximum number of
connections
defined)[\[41\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/protocol/config.json#L6-L14),
and each Android client connects to it when ready. Messages are likely
encoded in JSON and could be sent over a persistent TCP socket (the
config specifies
`protocol: "TCP"`[\[41\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/protocol/config.json#L6-L14)).
Important message types include: device registration/hello, start
session command, stop session command, sync signal command, status
update from device, file transfer requests, etc.

During a session, the **data flow** is as follows: - **Shimmer GSR
Data:** If a Shimmer sensor is directly connected to the PC, it streams
data via Bluetooth to the PC's Shimmer Manager, which then immediately
enqueues the data for writing to a CSV and also triggers any real-time
displays. If the Shimmer is connected to an Android (i.e.,
Android-mediated), the sensor data first goes to the Android (via
Bluetooth), and the Android then forwards each GSR sample (or batch of
samples) over the network to the
PC[\[56\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_manager.py#L260-L269)[\[57\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_manager.py#L261-L268).
This is handled by the `AndroidDeviceManager._on_android_shimmer_data`
callback on the PC side, which receives `ShimmerDataSample` objects from
the device and processes them similarly. In both cases, each GSR sample
is timestamped (using the synchronized clock) and logged. The PC might
accumulate these in memory (e.g., in `data_queues`) briefly for
processing but ultimately writes them out via a background file-writing
thread[\[15\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_manager.py#L163-L171). -
**Video and Thermal Data:** The Android devices record video and thermal
streams locally to their flash storage (to avoid saturating the network
by streaming raw video). The PC may receive low-frequency updates or
thumbnails for monitoring, but the bulk video data stays on the device
until session end. The **temporal synchronization** of video with GSR is
ensured by all devices starting recording upon the same start command
and using synchronized clocks. Additionally, the PC's sync signal
(flash) provides a reference point that can be seen in the video and is
logged in the GSR timeline, tying the streams together. After the
recording, when the PC issues the file transfer, the video files are
sent to the PC. This transfer uses the network (possibly chunking files
if large). The FileTransferHandler on PC receives each chunk or file and
saves it. Because the PC knows the session start time and each video
frame's device timestamp (the Android might embed timestamp metadata in
video or provide a separate timestamp log), alignment can be done in
post-processing. There is also a possibility that the Android app sends
periodic timestamps during recording to the PC (as part of
SessionSynchronizer updates) so the PC is aware of recording
progress[\[58\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_synchronizer.py#L113-L122)[\[59\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_synchronizer.py#L130-L138). -
**Time Sync and Heartbeats:** Throughout a session, the PC might send
periodic time sync packets to the Androids (or the Androids request
them). The `SessionSynchronizer` on PC also keeps a heartbeat: it tracks
if it hasn't heard from a device's state in a while, marking it offline
after a
threshold[\[60\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_synchronizer.py#L154-L161).
Android devices likely send a small status message every few seconds
("I'm alive, recording, file X size = ..."). This data flow ensures the
PC has up-to-date knowledge of each device (e.g., how many frames
recorded, or storage used). - **Data Aggregation:** Once all data
reaches the PC, the system has a **session aggregation step** (which can
be considered post-session). For instance, the Session Manager might
invoke a function to perform any post-processing -- the code even shows
a hook for *post-session hand segmentation processing* on the recorded
video[\[61\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_manager.py#L172-L180)[\[62\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_manager.py#L214-L222).
In practice, after all files are in place, the PC could combine or index
them (for example, generating an index of timestamps). This ensures that
all data from the distributed sources is now centralized in one place
(the PC's file system) and organized.

**System Architecture Diagram:** *Figure 3.1 (Placeholder)* would
illustrate the above in a block diagram: a PC node on one side with
blocks for Session Manager, Shimmer Manager, Network Server, etc., and
multiple Android nodes on the other, each containing Camera, Thermal,
Shimmer (if any) and a network client. Lines would show Bluetooth links
(PC to Shimmer, or Android to Shimmer), and WiFi/LAN links between PC
and each Android. Data flows (like GSR data flowing to PC, video files
flowing after stop) would be indicated with arrows. Time sync flows (PC
broadcasting time) would also be shown. The diagram would emphasize the
star topology (PC in center).

**Key Design Considerations:** The architecture ensures **scalability**
by decoupling data producers (devices) from the central coordinator.
Each Android operates largely independently during recording (writing to
local disk), which avoids overloading the network. The PC focuses on
low-bandwidth critical data (GSR streams, commands, and occasional
thumbnails or status). By using local storage on devices and
transferring after, the system mitigates the risk of network bandwidth
issues affecting the recording quality. The use of threads and
asynchronous I/O on the PC side (for writing files and handling multiple
sockets) ensures that adding more devices will linearly increase
resource usage but not deadlock the
system[\[28\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_manager.py#L169-L177).

The architecture also provides **fault isolation**: if one device
crashes, it does not bring down the whole system -- the PC will continue
managing others. The SessionSynchronizer component acts like a watchdog
and queue, so even if connectivity returns after a lapse, the overall
session can still be
coherent[\[63\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_synchronizer.py#L169-L178)[\[64\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_synchronizer.py#L179-L187).

Finally, the data flow design was made with **data integrity** in mind.
Every piece of data is tagged with device ID and timestamp, and funneled
into the session structure. The system uses consistent file naming
conventions (e.g., `<device>_<datatype>_<timestamp>.ext` for
files)[\[65\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_manager.py#L20-L28)
to aid in identifying and parsing data later. This systematic approach
to data flow and storage helps maintain the quality of the dataset
produced for research.

## 3.7 Data Requirements and Management

The system handles multiple types of data, each with specific
requirements for quality and management:

- **Data Types and Formats:** The primary data types include:

- *GSR (Galvanic Skin Response) data:* continuous time-series of skin
  conductance values (in microsiemens) recorded at **128 Hz** by
  default[\[12\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_manager.py#L128-L135).
  Each sample may also include related signals (e.g., PPG, accelerometer
  axes) if those Shimmer channels are
  enabled[\[13\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_manager.py#L101-L109).
  GSR and other sensor readings are saved in **CSV format** with
  timestamps.

- *Video footage:* high-resolution RGB video, typically **1080p at 30
  FPS**
  (configurable)[\[14\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/protocol/config.json#L18-L26),
  encoded in a standard format (e.g. H.264 MP4). If multiple cameras
  (e.g., front and rear or multiple angles) are used, each video is
  stored separately.

- *Thermal imaging data:* either recorded as thermal video (if the
  thermal camera supports video) or as a sequence of image frames.
  Thermal data has lower resolution (depending on camera, e.g., 320×240)
  and frame rate (\~8-15 FPS is common for thermal). The system treats
  it similarly to video (MP4 or a series of JPEG/PNG images).

- *Audio:* if recorded, stereo audio sampled at 44.1 kHz, stored within
  the video file (as AAC audio track) or as separate WAV
  files[\[16\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/protocol/config.json#L26-L34).

- *Metadata:* JSON files (such as `session_metadata.json`) which contain
  structured information about the session (session ID, device list,
  start/end times, and lists of data
  files)[\[10\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_manager.py#L64-L73).
  These are crucial for data management but are small in size.

- **Quality Requirements:** For research validity, the data must be high
  quality:

- GSR data should have appropriate resolution (the Shimmer GSR+ device
  provides 16-bit resolution) and be free from gaps. The system's 128 Hz
  sampling satisfies typical GSR analysis needs, and it can be increased
  if needed (config allows setting a higher rate, up to the hardware
  max)[\[12\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_manager.py#L128-L135).
  Signal noise should be minimized (the system does basic validation and
  could be extended with filtering if required).

- Video quality is set to high (1080p) so that fine details (e.g.,
  subtle facial perspiration or color changes) are visible. The bitrate
  \~5
  Mbps[\[29\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/protocol/config.json#L30-L37)
  is chosen to avoid excessive compression artifacts. The system ensures
  that lighting conditions are sufficient (not a direct software
  requirement, but an experimental protocol matter). Thermal images must
  have good contrast; the system cannot control thermal camera
  resolution (that's hardware-defined) but ensures that all frames are
  timestamped and in focus (if the thermal camera has focus
  adjustments).

- Synchronization quality is part of data quality: as noted, all data
  streams carry timestamps from a common reference. The system's time
  management ensures that when data is analyzed, a sample from the GSR
  CSV can be aligned to the exact video frame using timestamps (within a
  few milliseconds tolerance).

- **Volume and Storage Management:** The system is expected to generate
  **large volumes of data** per session, especially video. For example,
  a 10-minute session with one 1080p camera (\~5 Mbps) will produce
  around 375 MB of video data, plus a few MB of sensor data. With
  multiple cameras or longer sessions, this scales up. To manage this:

- The Android app monitors available storage before and during
  recording. If free space is below a threshold (configurable, e.g.,
  warn at 500 MB
  remaining)[\[66\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/protocol/config.json#L32-L38),
  it alerts the user to avoid data loss.

- The system is configured to **chunk large files**: video files are
  capped at \~1000 MB
  each[\[66\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/protocol/config.json#L32-L38),
  so a long recording will result in sequential files (e.g., video1.mp4,
  video2.mp4) rather than one enormous file. This makes transfers and
  post-processing more reliable.

- **Session Directory Structure:** On the PC, all data for a session is
  contained in one folder (e.g., `recordings/session_20250808_123000/`).
  Within it, subfolders or naming conventions separate data by device or
  type. For instance, GSR CSV might be named
  `Shimmer01_gsr_20250808_123000.csv`[\[67\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_manager.py#L8-L16)[\[65\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_manager.py#L20-L28)
  and an Android's video `AndroidDeviceA_video_20250808_123000.mp4`.
  This systematic naming is created by the `generate_device_filename`
  utility[\[68\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_manager.py#L2-L9).
  The session metadata JSON lists each file with its device and type for
  easy
  reference[\[26\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_manager.py#L130-L138).

- **Backup and Redundancy:** The system can be configured to keep a
  backup of data. In the config, `backup_enabled` is
  true[\[42\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/protocol/config.json#L2-L5),
  meaning the system will duplicate session data to a secondary location
  (this could be an external drive or cloud, depending on setup). This
  is important for research robustness -- no single copy of valuable
  data. The backup operation might happen after the session or at the
  end of the day, ensuring at least two copies of each file exist.

- **Data Retention:** Sessions are stored with unique IDs, and the
  system does not automatically delete anything (unless a retention
  policy is specified). It's up to the user to clear old sessions if
  needed. The session listing in the UI helps track what is stored.

- **Post-Processing and Data Export:** While not the primary focus of
  requirements, the system does facilitate post-session processing. For
  example, as noted in the SessionManager code, after a session the
  researcher can trigger a **hand segmentation** process on the recorded
  video[\[61\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_manager.py#L172-L180)[\[62\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_manager.py#L214-L222)
  -- this would produce additional data (segmentation masks) stored
  alongside the session. Also, the design allows exporting data in
  standard formats for analysis (the raw data is already in CSV/MP4
  which are standard). If needed, an export utility could package a
  session's data (e.g., compress the folder or convert it to a specific
  data format required by analysis software).

In summary, the system meets stringent data requirements by capturing
**high-resolution, high-frequency data**, keeping it well-organized per
session, and implementing measures for integrity (synchronization,
validation) and safety (storage management, backups). This ensures that
researchers using the system will obtain a comprehensive and reliable
dataset for each experiment, without worrying about data loss or
misalignment. All these measures together make the data management
**compliant with research best practices** -- for instance, it aligns
with FAIR data principles by clearly documenting metadata and
maintaining data
quality[\[69\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/architecture.md#L6-L14).

------------------------------------------------------------------------

[\[1\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/architecture.md#L14-L21)
[\[55\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/architecture.md#L26-L34)
[\[69\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/architecture.md#L6-L14)
architecture.md

<https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/architecture.md>

[\[2\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/production/runtime_security_checker.py#L110-L119)
[\[33\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/production/runtime_security_checker.py#L140-L148)
[\[35\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/production/runtime_security_checker.py#L106-L114)
[\[36\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/production/runtime_security_checker.py#L156-L164)
[\[37\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/production/runtime_security_checker.py#L168-L171)
runtime_security_checker.py

<https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/production/runtime_security_checker.py>

[\[3\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_synchronizer.py#L153-L161)
[\[21\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_synchronizer.py#L163-L171)
[\[22\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_synchronizer.py#L174-L182)
[\[58\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_synchronizer.py#L113-L122)
[\[59\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_synchronizer.py#L130-L138)
[\[60\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_synchronizer.py#L154-L161)
[\[63\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_synchronizer.py#L169-L178)
[\[64\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_synchronizer.py#L179-L187)
session_synchronizer.py

<https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_synchronizer.py>

[\[4\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_manager.py#L244-L253)
[\[5\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_manager.py#L260-L268)
[\[6\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_manager.py#L268-L274)
[\[12\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_manager.py#L128-L135)
[\[13\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_manager.py#L101-L109)
[\[15\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_manager.py#L163-L171)
[\[28\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_manager.py#L169-L177)
[\[30\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_manager.py#L130-L138)
[\[31\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_manager.py#L184-L192)
[\[53\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_manager.py#L212-L220)
[\[54\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_manager.py#L150-L159)
[\[56\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_manager.py#L260-L269)
[\[57\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_manager.py#L261-L268)
shimmer_manager.py

<https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_manager.py>

[\[7\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_pc_app.py#L120-L128)
[\[17\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_pc_app.py#L176-L185)
[\[18\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_pc_app.py#L260-L267)
[\[19\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_pc_app.py#L234-L242)
[\[20\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_pc_app.py#L170-L173)
[\[39\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_pc_app.py#L261-L268)
[\[45\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_pc_app.py#L191-L200)
[\[46\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_pc_app.py#L130-L138)
[\[47\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_pc_app.py#L146-L155)
[\[48\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_pc_app.py#L151-L159)
[\[51\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_pc_app.py#L156-L164)
[\[52\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_pc_app.py#L205-L213)
shimmer_pc_app.py

<https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/shimmer_pc_app.py>

[\[8\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/ntp_time_server.py#L66-L74)
[\[9\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/ntp_time_server.py#L26-L34)
ntp_time_server.py

<https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/ntp_time_server.py>

[\[10\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_manager.py#L64-L73)
[\[11\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_manager.py#L82-L91)
[\[26\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_manager.py#L130-L138)
[\[49\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_manager.py#L86-L95)
[\[50\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_manager.py#L99-L102)
[\[61\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_manager.py#L172-L180)
[\[62\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_manager.py#L214-L222)
[\[65\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_manager.py#L20-L28)
[\[67\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_manager.py#L8-L16)
[\[68\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_manager.py#L2-L9)
session_manager.py

<https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/PythonApp/session/session_manager.py>

[\[14\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/protocol/config.json#L18-L26)
[\[16\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/protocol/config.json#L26-L34)
[\[23\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/protocol/config.json#L54-L62)
[\[29\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/protocol/config.json#L30-L37)
[\[32\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/protocol/config.json#L111-L119)
[\[34\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/protocol/config.json#L113-L119)
[\[38\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/protocol/config.json#L40-L48)
[\[40\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/protocol/config.json#L39-L47)
[\[41\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/protocol/config.json#L6-L14)
[\[42\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/protocol/config.json#L2-L5)
[\[43\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/protocol/config.json#L80-L88)
[\[44\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/protocol/config.json#L102-L109)
[\[66\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/protocol/config.json#L32-L38)
config.json

<https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/protocol/config.json>

[\[24\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/AndroidApp/src/main/java/com/multisensor/recording/managers/FileTransferManager.kt#L124-L132)
[\[25\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/AndroidApp/src/main/java/com/multisensor/recording/managers/FileTransferManager.kt#L142-L150)
[\[27\]](https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/AndroidApp/src/main/java/com/multisensor/recording/managers/FileTransferManager.kt#L156-L165)
FileTransferManager.kt

<https://github.com/buccancs/bucika_gsr/blob/7048f7f6a7536f5cd577ed2184800d3dad97fd08/AndroidApp/src/main/java/com/multisensor/recording/managers/FileTransferManager.kt>
