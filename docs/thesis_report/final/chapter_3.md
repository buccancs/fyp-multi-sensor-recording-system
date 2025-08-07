# Chapter 3: Requirements and System Analysis

## 3.1 Problem Statement and Research Context

Modern physiological monitoring techniques often use Galvanic Skin Response (GSR) sensors attached to the skin to measure electrodermal activity. While GSR is a proven indicator of stress and arousal, traditional contact-based measurement is intrusive and can limit natural behavior. This project addresses the problem of predicting GSR in a contactless manner using alternative sensing modalities (such as thermal imaging and standard video cameras) without sacrificing accuracy. 

In recent years, thermal and visual cameras have improved to capture subtle physiological cues (e.g. facial temperature changes, perspiration) that correlate with stress. However, there was no integrated system to simultaneously collect synchronized thermal, visual, and reference GSR data needed to develop and validate contactless GSR prediction models. This work falls within affective computing and human-computer interaction research, where unobtrusive monitoring of stress and emotional state is highly desirable. The goal is to provide a multi-sensor recording platform that enables experiments in which participants are monitored without wires or attached electrodes, allowing more natural interactions while still capturing reliable ground-truth physiological data.

To address this, we developed a Multi-Sensor Recording System for Contactless GSR Prediction. The system can collect synchronized multi-modal data – specifically high-resolution RGB video, thermal infrared imagery, and GSR readings from a Shimmer sensor – in real time. By aligning these data streams with millisecond precision, the system produces datasets for training and evaluating machine learning models that estimate stress (or related physiological signals) from camera data alone. The system needs to be both scientifically rigorous (accurate timing, clean signals) and practical for field use (mobile devices with untethered subjects). In short, the aim is to build a distributed data acquisition system that captures synchronized physiological and imaging data for contactless GSR research. (The following sections detail the requirements derived from this problem and the system analysis that shaped the solution.)

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

Given the experimental nature of the project, the **requirements
engineering approach was iterative and incremental**. The team followed
an agile-like process: initial core requirements were established from
the research objectives (e.g. *"record thermal and video data
synchronised with GSR"*), and a **prototype system** was quickly built
to validate feasibility. As the prototype was tested with actual
sensors, new requirements and refinements were discovered (for instance,
the need for automated device re-connection on failure, or a method to
log stimulus events during recording). The repository's commit history
reflects these iterations -- each commit often corresponded to
implementing or refining a specific requirement (e.g. adding the Shimmer
sensor integration or improving time synchronisation). This evolutionary
process ensured continuous alignment between requirements and
implementation.

The project also adhered to established **software requirements
specification practices** (in line with IEEE guidelines) to
systematically document each requirement with an identifier,
description, and priority. Requirements were classified into functional
and non-functional categories for clarity. Throughout development, a
strong emphasis was placed on **validation and testing** to ensure
requirements were met: a thorough test suite (with \>95% coverage)
was developed to automatically verify that each functional requirement
(device communication, data recording, etc.) behaved as expected in real
scenarios. In summary, the requirements engineering combined up-front
analysis of research needs with continuous feedback from implementation,
resulting in a robust set of requirements that guided the system design
and implementation.

## 3.3 Functional Requirements Overview

Table 3.1 lists the **Functional Requirements (FR)** identified for the
multi-sensor recording system. Each requirement is labelled with a unique
ID and a priority (H = High, M = Medium) indicating its importance.
These functional requirements capture the intended capabilities and
behaviours of the system. They were derived to ensure the system meets
the needs of coordinating multiple devices, acquiring various sensor
data streams, synchronising and storing data, and supporting the
research workflow.

**Table 3.1 -- Functional Requirements**
---
  ID                      Functional Requirement Description                                                                                                                                                                                                                                                                                                                                                 Priority
---
  FR-01                   **Centralised Multi-Device Coordination:** The system shall provide a PC-based master controller application that can connect to and manage multiple remote recording devices (Android smartphones). This enables one operator to initiate and control recording sessions across all devices from a single interface.                                                              H

  FR-02                   **User Interface for Session Control:** The PC master controller shall offer an intuitive graphical user interface (GUI) for configuring sessions, displaying device status, and controlling recordings (start/stop). The GUI should show connected device indicators and allow the user to easily monitor the recording process in real time.                                     H

  FR-03                   **High-Precision Synchronisation:** The system shall synchronise all data streams (video frames, thermal frames, GSR samples) with a unified timeline. Recording on all devices must start nearly simultaneously, achieving time alignment with an accuracy on the order of 1 millisecond or better. Each data sample/frame will be timestamped to enable precise cross-modal      H
                          correlation [\[1\]](PythonApp/shimmer_manager.py#L144-L151).

  FR-04                   **Visual Video Capture:** Each Android recording device shall capture high-resolution **RGB video** of the participant during the session. The system should support at least 30 frames per second at HD (720p) resolution or higher (up to the device's capabilities, e.g. 1080p or 4K) for detailed visual data. The video recording is to be continuous for the session         H
                          duration, saved in a standard format (e.g. MP4).

  FR-05                   **Thermal Imaging Capture:** If a recording device is equipped with a thermal camera, the system shall capture **thermal infrared video** in parallel with the RGB video. Thermal frames must be recorded at the highest available resolution and frame rate (device-dependent) and time-synchronised with other streams. This provides contactless skin temperature data          H
                          corresponding to the participant's physiological state.

  FR-06                   **GSR Sensor Integration:** The system shall integrate **Shimmer GSR sensor** devices to collect ground-truth physiological signals (electrodermal activity and related sensors). The PC controller must handle Shimmer data either via direct Bluetooth connection or via an Android device acting as a relay (proxy) for the                                                     H
                          sensor[\[2\]](PythonApp/shimmer_manager.py#L138-L145). All connected GSR sensors should be managed concurrently, and their data samples (GSR conductivity, plus other channels like PPG or accelerometer) timestamped and synchronised with the session timeline.

  FR-07                   **Session Management and Metadata:** The system shall allow the user to create a new *recording session* and automatically assign it a unique Session ID. During a session, the controller will maintain metadata including session start time, configured duration (if applicable), and the list of active devices/sensors. Upon session start, each device and sensor is         H
                          registered in the session metadata, and upon stop, the session is finalised with end time and duration
                          recorded[\[3\]](PythonApp/session/session_manager.py#L74-L81)[\[4\]](AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L334-L342). A session metadata file (e.g. JSON or
                          text) shall be saved, summarising the session details for future reference.

  FR-08                   **Local Data Storage (Offline-First):** All recording devices shall store their captured data **locally on-device** during the session to avoid reliance on continuous network streaming. Video streams are saved as files on the smartphones (and any PC-local video source) and GSR data is logged (e.g. to CSV) on the PC or device collecting it. Each data file is            H
                          timestamped or contains timestamps internally. This *offline-first* design ensures no data loss in case of network disruption and maximises reliability of recording.

  FR-09                   **Data Aggregation and Transfer:** After a recording session is stopped, the system shall support automatic aggregation of the distributed data. The PC controller will instruct each Android device to **transfer the recorded files** (video and any other data) to the PC over the network. The files are transmitted in chunks with verification -- the PC confirms the file   M
                          sizes and integrity on receipt[\[5\]](PythonApp/network/device_server.py#L355-L364). All files from the session are collected into the PC's session folder for centralised storage. (In the event automatic transfer fails or is unavailable, the system permits manual retrieval as a
                          fallback.)

  FR-10                   **Real-Time Status Monitoring:** The PC interface shall display real-time status updates from each connected device, including indicators such as recording state (recording/idle), battery level, storage space, and connectivity health[\[6\]](PythonApp/network/device_server.py#L26-L34). M
                          During an active session, the operator can observe that all devices are recording and see any warnings (e.g. low battery) in real time. Optionally, the system may also show a low-frame-rate preview of the video streams for verification purposes (e.g. a thumbnail
                          update)[\[7\]](PythonApp/network/device_server.py#L244-L252). These status and preview updates help the operator ensure data quality throughout the session.

  FR-11                   **Event Annotation:** The system shall allow the researcher to **annotate events** or markers during a recording session. For example, if a stimulus is presented to the participant at a specific time, the researcher can log an event (through the PC app UI or a hardware trigger). The event is recorded with a timestamp (relative to session start) and a short description M
                          or type[\[8\]](AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L124-L133). All such events are saved (e.g. in a `stimulus_events.csv` in the session folder) to facilitate aligning external events with physiological responses during data analysis.

  FR-12                   **Sensor Calibration Mode:** The system shall provide a mode or tools for calibration and configuration of sensors before a session. This includes the ability to capture calibration data for the cameras (e.g. a one-time procedure to spatially align the thermal and RGB cameras using a reference pattern) and to configure sensor settings (focus, exposure, thermal range,  M
                          etc.) as needed. Calibration data (such as images of a checkerboard or known thermal target) are stored in a dedicated calibration folder for each session or
                          device[\[9\]](AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L300-L308)[\[10\]](AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L311-L319).
                          This requirement ensures that the multi-modal data can be properly registered and any sensor biases corrected in post-processing.

FR-13                   **Post-Session Data Processing:** The system shall support optional **post-processing steps** on the recorded data to enrich the dataset. For example, after a session, a *hand segmentation* algorithm can be run on the recorded video frames to identify and crop the participant's hand region (since GSR is often measured on the hand). If enabled, the PC controller will   M
                          automatically invoke the hand segmentation module on the session's video files and save the results (segmented images or masks) in the session folder[\[11\]](PythonApp/session/session_manager.py#L216-L224). This automates part of the data analysis preparation (e.g. extracting relevant
                          features) and is configurable by the user.
---
**Discussion:** The above functional requirements cover the core
capabilities of the system. Together, they ensure that the
**multi-sensor recording system can capture synchronised data from
multiple devices and sensors** and manage that data effectively for
research use. The design addresses multi-device coordination (FR-01,
FR-02) and tight time synchronisation (FR-03) as top priorities, since
these are critical for aligning different data modalities. Requirements
FR-04 through FR-06 enumerate the data acquisition needs for each sensor
modality -- visual video, thermal imaging, and GSR -- reflecting the
system's multi-modal nature. Session handling and data management
(FR-07, FR-08, FR-09) form the backbone that guarantees recordings are
organised and preserved reliably (e.g., creating session metadata and
using offline local storage to avoid data loss). Real-time feedback and
control (FR-10 and FR-11) improve the usability of the system during
experiments, allowing the operator to monitor progress and mark
important moments. Finally, FR-12 and FR-13 address advanced
functionality: calibration support and post-processing, which enhance
the quality and utility of the collected data (these are considered
"Medium" priority since the system can run without them, but they are
valuable for achieving research-grade results). Many of these
requirements are explicitly supported by the implementation -- for
instance, the **ShimmerManager** class in the code confirms the
multi-sensor integration and error-handling for GSR
sensors[\[2\]](PythonApp/shimmer_manager.py#L138-L145)[\[1\]](PythonApp/shimmer_manager.py#L144-L151),
and the session management logic creates metadata files and directory
structures as
specified[\[3\]](PythonApp/session/session_manager.py#L74-L81)[\[4\]](AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L334-L342).
The next section will consider constraints and quality attributes
(non-functional requirements) that also had to be satisfied to meet
these functional goals.

## 3.4 Non-Functional Requirements

In addition to the explicit features and behaviours, the system must
fulfill several **Non-Functional Requirements (NFR)** that define
qualities such as performance, reliability, and usability. Table 3.2
summarises the key non-functional requirements for the multi-sensor
recording system, again with unique IDs and priority levels. These
requirements ensure the system not only *works*, but works effectively
and robustly in the contexts it will be used (research labs, possibly
mobile or field environments, with human participants involved).

**Table 3.2 -- Non-Functional Requirements**
---
  ID                      Non-Functional Requirement Description                                                                                                                                                                                                                                                                Priority
---
  NFR-01                  **Real-Time Performance:** The system shall operate in real time, handling data streams without undue delay. All components must be efficient enough to **capture video at full frame rate and sensor data at full sampling rate** without buffering issues or frame drops. For example, the Android  High
                          app should sustain 30 FPS video recording and \~50 Hz GSR sampling simultaneously. The end-to-end latency from capturing a sensor sample/frame to logging it with a timestamp should be minimal (well below 100 ms), ensuring a responsive system.

  NFR-02                  **Synchronisation Accuracy:** The system's clock synchronisation and triggering mechanisms shall be precise, as reflected in FR-03. The design should ensure that any timestamp discrepancies between devices are below acceptable thresholds (on the order of milliseconds). In practice, this may   High
                          involve time synchronisation protocols or timestamp calibration. Each data sample is tagged with both device-local time and a unified time reference to permit alignment during
                          analysis[\[12\]](PythonApp/shimmer_manager.py#L91-L99). This requirement guarantees the **temporal integrity** of the multi-modal dataset.

  NFR-03                  **Reliability and Fault Tolerance:** The system must be reliable during long recording sessions. It shall handle errors gracefully -- for instance, if a device temporarily disconnects (due to network drop or power issues), the system will attempt to reconnect automatically and continue the    High
                          session without crashing[\[13\]](PythonApp/shimmer_manager.py#L146-L150). Data already recorded should remain safe in such events (thanks to local storage on devices). The system should not lose data or
                          corrupt files even if an interruption occurs; any partial data is cleanly saved up to the point of failure. Robust **error handling and recovery** mechanisms are implemented (e.g., retry logic for device connections and file transfers).

  NFR-04                  **Data Integrity and Accuracy:** The system shall ensure the integrity and accuracy of recorded data. All data files (videos, sensor CSV) are verified for correctness after recording -- for example, the file transfer process includes confirming file sizes and sending                           High
                          acknowledgments[\[5\]](PythonApp/network/device_server.py#L355-L364). Time stamps must be consistent and accurate (no clock drift over typical session durations). The GSR sensor data should be sampled with
                          stable timing and recorded with the correct units (e.g., microSiemens for conductance) without clipping or quantization errors. This requirement is crucial for the scientific validity of the collected dataset.

  NFR-05                  **Scalability (Multi-Device Support):** The architecture should scale to **multiple recording devices** operating concurrently. Adding more Android devices (or additional Shimmer sensors) to a session should have a linear or manageable impact on performance. The network and PC controller must Medium
                          handle the bandwidth of multiple video streams and sensor feeds. At minimum, the system is expected to support a scenario of *at least two Android devices* plus one or two Shimmer sensors recording together. The design (threaded server, asynchronous I/O, etc.) allows scaling up the number of  
                          devices with minimal
                          modification[\[14\]](PythonApp/network/device_server.py#L424-L432)[\[15\]](PythonApp/network/device_server.py#L484-L492).

  NFR-06                  **Usability and Accessibility:** The system's user interface and workflow shall be designed for **ease of use** by researchers who may not be software experts. This means the PC application should be straightforward to install and run, and the process to start a session is simple (e.g.,       High
                          devices auto-discover the PC, one-click to start recording). Visual feedback (FR-10) is provided to reduce user uncertainty. The Android app should require minimal user interaction -- ideally launching and automatically connecting to the PC. Clear notifications or dialogues guide the user if
                          any issues occur (e.g. permission requests, errors). The system should also be documented well enough that new users can learn to operate it quickly.

  NFR-07                  **Maintainability and Extensibility:** The software shall be designed following clean code and modular architecture principles to facilitate maintenance and future extension. For example, the Android app follows an MVVM (Model-View-ViewModel) architecture with dependency injection (Hilt) to   Medium
                          separate concerns, making it easier to modify or upgrade components (such as replacing the camera subsystem or adding a new sensor) without affecting others. The PC code similarly separates the GUI, networking, and data management logic into distinct modules. Code quality metrics were
                          enforced (e.g., complexity limits) to keep the implementation understandable and
                          testable[\[16\]](changelog.md#L34-L41)[\[17\]](changelog.md#L60-L64). Additionally, a high level of automated test coverage
                          was achieved, so developers can confidently refactor the system and add features while catching regressions early. This requirement ensures the longevity of the system as a research platform.

  NFR-08                  **Portability:** The system should be portable and not dependent on specialised or expensive hardware beyond the sensors themselves. The PC controller is a cross-platform Python application that can run on standard laptops or desktops (the only requirement being moderate processing power, \~4 Medium
                          GB RAM, and Python 3.8+ environment). The Android app runs on common Android devices (Android 8.0 or above) and supports a range of phone models, provided they have the needed sensors (camera, etc.) and Bluetooth for Shimmer. This allows the system to be deployed in different laboratories or  
                          even off-site (using a router or local hotspot for networking). Portability also implies that the system's components (PC and mobile) communicate over standard interfaces (TCP/IP network, JSON messages) without requiring wired connections, increasing the flexibility of where and how it can be
                          used.

NFR-09                  **Security and Data Privacy:** While the system is typically used in controlled research settings, basic security measures are required. The network communication (JSON command channel and file transfers) should occur only over a secure local network. Only authorized devices (which send a     Medium
                          correct handshake/hello message with expected format) are allowed to connect to the PC controller, reducing the risk of unauthorized interception. Additionally, participant data (video and physiological signals) are sensitive, so the system should provide options to encrypt stored data or
                          otherwise protect data at rest, according to institutional data handling guidelines. (For example, the recorded files can be stored on encrypted drives or be anonymized by not embedding personal identifiers.) Although full encryption of live streams is not implemented in the current version,  
                          this requirement is noted for completeness to ensure ethical research data management.
---
**Discussion:** These non-functional requirements underline the system's
quality attributes that make it suitable for research use. Performance
(NFR-01) and synchronisation accuracy (NFR-02) ensure that the **data
quality** meets scientific standards -- the system can capture
high-resolution, high-frequency data in sync, which is essential for
meaningful analysis. Reliability and data integrity (NFR-03, NFR-04) are
critical given that experimental sessions are often unrepeatable -- the
system must not crash or lose data during a trial. Scalability (NFR-05)
acknowledges that the research may expand to more devices or
participants; the system's **distributed architecture** (with a
multi-threaded server and modular device handling) was designed to
accommodate this growth with minimal rework. Usability (NFR-06) was a
high priority because complex setups can impede researchers -- features
like auto device discovery and real-time feedback were included to make
the system as user-friendly as possible. Maintainability and
extensibility (NFR-07) have been addressed by following rigorous
software engineering practices (the commit history shows extensive
refactoring and documentation efforts to keep code complexity in
check[\[16\]](changelog.md#L34-L41)).
This means the system can be updated (for example, to integrate a new
type of physiological sensor or to improve algorithms) by future
developers with relative ease. Portability (NFR-08) ensures the system
can be used in various environments -- whether in a lab or a field study
-- without heavy infrastructure. Finally, security (NFR-09) and data
privacy considerations reflect the ethical dimension: while not the
primary focus during development, the design allows operation on closed
networks and the addition of security layers so that sensitive
participant data is safeguarded. In sum, the NFRs complement the
functional requirements by guaranteeing that the system operates
**efficiently, robustly, and responsibly** in a real-world research
context.

## 3.5 Use Case Scenarios

To illustrate how the system is intended to be used, this section
describes several primary **use case scenarios**. These scenarios
represent typical workflows for the multi-sensor recording system,
demonstrating how the functional requirements come together to support
research activities. *(Figure 3.1 provides a use case diagram
summarising the actors and interactions in these scenarios
\[Placeholder\].)* The main actor in these use cases is the
**Researcher** operating the system via the PC Master Controller, with
secondary actors being the **Recording Devices** (Android phones with
cameras, sensors) and the **Participant(s)** being recorded. The
scenarios assume all devices have been set up and the software is
running on the PC and smartphones.

***Figure 3.1: Use case diagram illustrating the system's primary
scenarios -- conducting a multi-participant recording session,
performing system calibration, and real-time monitoring with event
annotation (Placeholder).***

**Use Case 1: Multi-Participant Recording Session** -- *"Conduct a
synchronised multi-sensor recording for one or more participants."* In
this primary use case, a researcher records an experimental session
involving physiological monitoring. The steps are as follows:

1. **Setup:** The researcher ensures all Android devices (e.g., two
    smartphones, each focusing on a participant) are powered on and
    running the recording app. Each participant is equipped with a
    Shimmer GSR sensor (e.g., worn on the fingers) which is either
    paired to the PC or to one of the phones. All devices are connected
    to the same Wi-Fi network. The researcher launches the PC Controller
    application and sees indications that the devices have
    auto-discovered and connected (each device sends a "hello"
    registration to the
    PC[\[18\]](PythonApp/network/device_server.py#L216-L224),
    and appears in the PC UI list of available devices). The PC UI shows
    each device's ID and capabilities (for example, "Device A: camera +
    thermal, Device B: camera + GSR").

1. **Initiate Recording:** The researcher configures session parameters
    on the PC (optionally setting a session name or notes) and clicks
    "Start Session". The PC controller then broadcasts a **start
    recording command** to all connected
    devices[\[14\]](PythonApp/network/device_server.py#L424-L432)[\[19\]](PythonApp/network/device_server.py#L486-L494).
    Each Android device receives the command and begins recording its
    sensors: the cameras start capturing video frames and writing to
    local MP4 files, and if a device has a paired Shimmer, it starts
    streaming GSR data to a local file. The PC concurrently might start
    its own recording (e.g., if a webcam on the PC is used as another
    video source). All these actions are synchronised -- devices either
    start immediately upon command or according to a coordinated start
    timestamp so that their internal clocks align (the system accounts
    for network latency by using very short command messages and
    preparing devices in advance). The PC UI updates to indicate
    "Recording in progress" for each device, and the session timer
    begins.

1. **Data Collection:** During the session (which could last e.g. 5
    minutes, 30 minutes, or longer), the system continuously collects
    data. Each smartphone writes video frames to its storage and
    periodically sends status updates to the PC (battery level, elapsed
    recording time, file size, etc. as per FR-10). The Shimmer sensors
    stream GSR (and possibly additional signals like PPG, accelerometer)
    -- if a Shimmer is connected directly to the PC, the PC logs that
    data in real time; if connected via a phone, the phone relays the
    sensor data packets to the PC over the network or stores them to
    include in its file. The system ensures that all data streams are
    timestamped consistently (each device uses a monotonic clock or
    synchronised timestamp). If any device encounters an error (for
    example, a camera error or a Bluetooth disconnection), it
    automatically tries to resolve it (restart the camera, reconnect the
    sensor) without user intervention, as long as the session is active.
    The researcher observes the PC dashboard occasionally -- for
    example, they might see a small preview frame updating for each
    device, confirming that video is being captured, and status text
    like "Device A: Recording 120s, Battery 85%".

1. **Concurrent Participants:** This use case can involve **multiple
    participants**. For instance, if two participants are in an
    interaction, each is being recorded by a separate phone and wearing
    a separate GSR sensor. The PC coordinates both streams. This scaled
    scenario simply repeats the above for each device -- because of the
    system's scalability, it handles two sets of data as easily as one.
    The PC's session metadata will log both devices under the same
    Session ID, and all data will share the timeline. The researcher can
    thus capture social or group scenarios with synchronised
    physiological measurements for each person.

1. **Stop Session:** Once the desired recording duration or
    experimental task is completed, the researcher clicks "Stop Session"
    on the PC. The controller sends a **stop command** to all devices.
    Each Android device stops recording: it finalises the video file
    (closing the file safely) and similarly finalises any sensor data
    file. The devices then each report back a final status (e.g., "Saved
    300s of video, file size 500 MB"). At this point, the PC invokes the
    data aggregation process (FR-09): it requests each device to
    transmit its files. One by one, the phones send their recorded files
    to the PC: for example, Device A sends
    `session_20250806_101530_rgb.mp4` and `thermal.mp4`, Device B sends
    its `session_20250806_101530_rgb.mp4` and `sensors.csv`. The PC
    receives these via the JSON socket connection in
    chunks[\[20\]](PythonApp/network/device_server.py#L313-L322)[\[5\]](PythonApp/network/device_server.py#L355-L364),
    writing them into the PC's own storage
    (`recordings/session_20250806_101530/DeviceA_rgb.mp4`, etc.). The PC
    verifies the file sizes match what the device reported. When all
    files are received, the PC marks the session as completed, updates
    the session metadata (end time and
    duration)[\[21\]](PythonApp/session/session_manager.py#L82-L91),
    and presents a summary to the researcher (e.g., "Session completed:
    2 devices, 2 video files, 1 sensor file, duration 5:00"). The
    researcher can then proceed to analyse the data offline.

1. **Post-conditions:** The outcome of this use case is that **all
    relevant multi-modal data has been recorded and centralised**. The
    session folder on the PC now contains subfolders or files for each
    device: e.g., video files from each camera, thermal data, GSR CSV,
    plus a session log and metadata. The researcher has a complete,
    time-synchronised dataset from the multi-participant session, which
    can be used for model training or other analysis.

**Use Case 2: System Calibration and Configuration** -- *"Calibrate
sensors and configure system settings prior to recording."* This
secondary use case is often performed before an actual data collection
session (it can be considered a preparatory or maintenance scenario).
Its goal is to ensure that all sensors are correctly configured and
aligned to collect high-quality data.

1. **Camera Calibration:** The researcher wants to calibrate the
    alignment between the RGB camera and the thermal camera on a device
    (if the device has both, or between two devices if one provides
    thermal and another RGB). Using a **calibration module** in the
    system (invoked via the PC UI or directly on the device app), the
    researcher places a known reference object (such as a checkerboard
    pattern or a thermal reference pad) in view. They then trigger a
    **calibration capture** -- the system might capture a set of images
    from the RGB and thermal cameras simultaneously. These images are
    saved in the session's calibration folder (e.g., `calibration/`
    directory for that
    session)[\[9\]](AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L300-L308)[\[10\]](AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L311-L319).
    Later, the researcher can use these image pairs to compute a spatial
    transformation that maps thermal images to the RGB frame (this
    computation might be done by an external script or a provided
    calibration tool). The resulting calibration parameters (e.g., a
    matrix or alignment file) can be stored and used in analysing the
    recorded data (so that features in the thermal and visual data can
    be compared pixel-to-pixel after alignment).

1. **Sensor Configuration:** The system allows adjusting certain sensor
    settings to suit the experimental needs. For example, the researcher
    can configure the Shimmer GSR device's **sampling rate** (e.g.
    51.2 Hz by default, but maybe set to 128 Hz for higher resolution)
    and which channels are enabled (GSR, photoplethysmograph, 3-axis
    accelerometer,
    etc.)[\[22\]](PythonApp/shimmer_manager.py#L72-L80)[\[23\]](PythonApp/shimmer_manager.py#L96-L104).
    This is done through a configuration interface (the PC or Android
    app exposes options if the sensor is connected). The chosen
    configuration is saved so that the device will use those settings in
    the upcoming session -- the ShimmerManager, for instance, stores a
    profile for the device with its MAC address and the enabled channels
    and sampling
    rate[\[24\]](PythonApp/shimmer_manager.py#L184-L191).
    Similarly, the researcher can set the resolution or frame rate for
    the smartphone cameras if needed (though by default, the system
    auto-selects the highest supported resolution and a standard frame
    rate).

1. **System Checks:** Before recording, the researcher performs a quick
    system diagnostic. They may use a **"Preview" mode** in the PC UI
    where each device streams a preview frame or short segment to the
    PC. The PC displays these to confirm the cameras have the
    participant in frame and the thermal camera is properly focused,
    etc. The researcher also checks that all devices show good battery
    levels or are connected to power (to satisfy reliability needs for a
    long session). The PC's status panel might show available storage on
    each device; if a device has low space, the researcher knows to free
    up space (this is part of configuration -- ensuring enough memory
    for the session).

1. **Result:** After this use case, the system is calibrated and
    configured. All devices are aligned and set with optimal parameters.
    This increases the quality of the data in the main recording use
    case. Calibration images and configuration files are stored for
    reference. For instance, the `session_config.json` might record the
    settings used (thermal camera frame rate, emissivity setting,
    etc.)[\[25\]](AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L354-L362)[\[26\]](AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L370-L378),
    and the `calibration/` directory holds raw frames used for
    calibration. The system is now ready to begin an actual recording
    session with confidence that data from different sensors will be
    comparable and that sensors are operating within desired ranges.

**Use Case 3: Real-Time Monitoring and Annotation** -- *"Monitor live
data and annotate events during a session."* This use case occurs
concurrently with an active recording (as in Use Case 1) but focuses on
the researcher's interaction with the system while it is running. Its
purpose is to allow the researcher to mark important moments and observe
the data quality in real time.

1. **Live Monitoring:** As the session proceeds, the researcher watches
    the PC application's live dashboard. The PC receives periodic
    **preview frames** from the devices (for example, a downsampled
    image every few
    seconds)[\[7\]](PythonApp/network/device_server.py#L244-L252).
    The UI might show a small video window for each device updating with
    these frames, so the researcher can ensure the participant remains
    properly framed and that lighting/thermal conditions are good. The
    PC also could display running plots for sensor streams (e.g., a
    real-time chart of GSR values) -- in this system, since GSR is
    recorded either on PC or relayed, the PC can plot the incoming GSR
    signal live. This real-time feedback helps detect any issues (e.g.,
    a sensor detached or a camera view obstructed) so they can be fixed
    immediately rather than only discovered after the session.

1. **Stimulus/Event Annotation:** During the recording, certain events
    might occur that the researcher wants to log. For instance, in a
    stress experiment, at time 2:00 a loud sound might be played to
    startle the participant. The researcher clicks an **"Add Event"**
    button in the PC UI at that moment (and perhaps types "Startle
    sound" or selects an event type from a list). The PC then records an
    event with a timestamp (relative to session start) and a label
    "Startle sound". In the implementation, this triggers a call to the
    Session Manager's `addStimulusEvent()` method on the Android device
    or PC, which appends the event to the `stimulus_events.csv` file
    along with the exact
    timestamp[\[8\]](AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L124-L133).
    Multiple events can be logged: e.g., "Questionnaire start",
    "Questionnaire end", "Unexpected noise", etc., each at specific
    times. These annotations are invaluable later when analysing the
    physiological data, as they mark when external stimuli or notable
    participant actions occurred.

1. **Adaptive Control (if applicable):** In some scenarios, the
    researcher might make adjustments during the session. For example,
    if they notice the thermal camera's auto-calibration has triggered a
    re-adjustment (which might briefly pause the feed), they could note
    that or disable auto-calibration next time. Or if one participant
    leaves the frame, the researcher might physically adjust the camera
    and use the preview to recentre. The system design allows for such
    mid-session interventions without stopping the recording -- the data
    continues to be captured uninterrupted.

1. **Observation of Limits:** Real-time monitoring also lets the
    researcher see if any **system limits** are being approached -- for
    instance, the PC might show that one phone's storage is 90% filled
    or that its battery is at 15%. The researcher can then decide to
    stop the session a bit early or ensure data just up to that point is
    used. Because of NFRs like reliability, these warnings are part of
    the UI to prevent data loss (e.g., a low storage warning at runtime
    might prompt the researcher to stop recording before the file system
    is full).

1. **Session End and Event Log:** After the session, the
    `session_metadata.json` or `session_log.txt` on each device/PC
    includes a summary of any events annotated (with their timestamps
    and
    labels)[\[27\]](AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L126-L134)[\[28\]](AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L140-L148).
    The researcher, when reviewing the data, can easily line up the
    event times with spikes in GSR or changes in thermal imagery. The
    result of this use case is an **enhanced dataset**: not only the raw
    sensor data, but also contextual markers that help interpret that
    data. The live monitoring aspect ensured that the data captured is
    of high quality (since the operator could catch problems in real
    time), and the annotation aspect enriched the dataset for analysis.

These use case scenarios demonstrate the end-to-end flow of how the
system is used in practice. In a typical experiment day, the researcher
would first calibrate and configure the system (Use Case 2), then run
one or multiple recording sessions (Use Case 1) while monitoring and
annotating (Use Case 3), and finally end up with well-organised data
ready for analysis. The scenarios involve multiple system components
interacting seamlessly: for example, the **network communication** plays
a crucial role in all cases (device discovery, start/stop commands, live
data relay, file transfer) and must function reliably under the hood.
The next section will delve into the system's architecture and data
flow, explaining how these use cases are supported by the design of the
software and the distribution of responsibilities between the PC
controller and the Android devices.

## 3.6 System Analysis (Architecture & Data Flow)

This section analyses the overall architecture of the multi-sensor
recording system and describes the flow of data through the system's
components. The design follows a **distributed client-server
architecture** with the PC as the central server (or coordinator) and
the Android devices as clients. It also employs modular subsystems to
handle the various concerns: user interface, device communication,
sensor data handling, and data storage. The analysis here shows how the
chosen architecture meets the requirements (both functional and
non-functional) and how data moves from capture to storage in a
synchronised way. Key architectural elements and their interactions are
summarised in *Figure 3.2* and the data flow is illustrated in *Figure
3.3*.

***Figure 3.2: High-level system architecture, showing the PC Master
Controller communicating over a Wi-Fi network with multiple Android
Recording Devices and directly or indirectly with Shimmer GSR sensors
(Placeholder).***

**Architecture Overview:** The system architecture can be viewed in two
layers -- **hardware nodes** and **software components**. On the
hardware side, we have: (1) the **PC Master Controller** (a
laptop/desktop running the Python application) and (2) one or more
**Android Recording Devices** (smartphones). Optionally, (3) **Shimmer
GSR sensor devices** are also present; they can interface either with
the PC (via Bluetooth) or with an Android phone (via the phone's
Bluetooth). The PC and phones are connected via a **Wireless LAN**
(e.g., a dedicated Wi-Fi router or hotspot), forming a private network
for the system. This network enables low-latency communication required
for synchronisation and data transfer.

On the software side, the PC runs a **Master Controller Application**
which includes several components working together: a **GUI Module**
(for the user interface), a **Session Manager** (for session metadata
and file management), and a **Network Communication Server** (to handle
connections with devices). The network server on PC is implemented as a
custom JSON socket server listening on a known port (e.g.,
9000)[\[29\]](PythonApp/network/device_server.py#L129-L137)[\[30\]](PythonApp/network/device_server.py#L120-L128).
It accepts incoming connections from the Android clients and uses a
length-prefixed JSON message protocol to exchange commands and data.
Each connected Android device is represented in the PC software as a
**RemoteDevice** object which tracks its capabilities (camera, thermal,
GSR, etc.) and
status[\[31\]](PythonApp/network/device_server.py#L18-L26)[\[32\]](PythonApp/network/device_server.py#L40-L48).
The PC's Session Manager on the other hand handles higher-level logic:
creating session folders, writing metadata, and coordinating the
start/stop across devices.

Each **Android Recording Device** runs an **Android app** (written in
Kotlin) that has its own internal architecture. The app is built with a
**Model-View-ViewModel (MVVM)** pattern. The core components include: a
**Recording Controller/Service** (which manages the camera and sensor
hardware on that phone), a **Session Manager** (on Android, which
parallels the PC's session logic, creating local folders on the phone's
storage for each session), and a **Network Client** that maintains a
socket connection back to the PC. The Android app's UI (if the user
opens it) provides local status, but in typical operation it runs mostly
headlessly after startup, responding to PC commands. The Android's
Recording Controller uses Android's Camera2 API for video and the
Shimmer SDK for sensor data if a Shimmer is connected to the phone.
Crucially, the Android app does not make autonomous decisions -- it acts
on commands from the PC or on a local user action (which is rare in this
use case). This separation ensures that **control logic is centralised**
on the PC, fulfilling the requirement of FR-01 (centralised multi-device
coordination).

The **Shimmer GSR Sensors** integration is architected flexibly. The
system supports three modes (as mentioned in FR-06): **Direct PC
Connection**, **Android-Mediated Connection**, or **Simulation Mode**
(for testing). In direct mode, the PC runs a Shimmer Bluetooth driver
(via the PyShimmer library) in the Python app -- the `ShimmerManager` on
PC opens a Bluetooth COM port to the Shimmer and reads data packets in a
background
thread[\[33\]](PythonApp/shimmer_manager.py#L19-L28)[\[34\]](PythonApp/shimmer_manager.py#L51-L59).
In Android-mediated mode, an Android phone pairs with the Shimmer (using
the Shimmer Android API) and that phone's app becomes responsible for
reading the GSR data; the phone then sends those sensor readings to the
PC over the network (using JSON messages of type
"sensor_data")[\[35\]](PythonApp/network/device_server.py#L256-L265).
The PC doesn't directly talk to the Shimmer in that case; it receives
the data already parsed from the phone. The architecture allows both
modes to operate simultaneously if needed (for example, two Shimmers
could be connected, one via PC, one via a phone). In all cases, the
Shimmer data is funneled into the same session structure: the PC will
eventually store it as part of the session data (either logging directly
or saving the file sent from the phone).

Several design patterns and strategies were used to satisfy
maintainability and extensibility (NFR-07) in the architecture. For
instance, the Android app relies heavily on **dependency injection**
(using Dagger/Hilt): components like the Camera Recorder, Thermal
Recorder, and Shimmer Recorder are provided to the Main ViewModel, so
they can be easily replaced or mocked for
testing[\[36\]](AndroidApp/src/main/java/com/multisensor/recording/ui/MainViewModel.kt#L32-L40)[\[37\]](AndroidApp/src/main/java/com/multisensor/recording/ui/MainViewModel.kt#L34-L42).
This makes it possible to extend support to new sensor types by adding
new modules without altering the core logic. On the PC side, the
networking is abstracted behind a `JsonSocketServer` class with
well-defined events (device_connected, status_received, etc.), and the
GUI is kept separate in a Qt-based `MainWindow`. This separation
enforces a **modular architecture** -- for example, one could develop an
alternative web-based UI (and indeed, the code contains a `web_ui`
module as an experimental interface) without needing to rewrite how
sessions or networking work. The architecture also emphasizes thread
separation for performance: the PC networking runs in a background
thread (so that heavy file transfers don't freeze the GUI), and the
Android uses background threads or coroutines for camera and file
operations (preventing UI jank on the phone). Overall, the chosen
architecture ensures that the system can reliably coordinate multiple
devices and handle data streams, while also being organised for future
modifications.

**Data Flow Analysis:** The flow of data through the system can be
described step-by-step for a typical session, highlighting how
information moves and transforms from capture to storage. *Figure 3.3
depicts this flow, from the moment the user initiates a session to the
final data aggregation \[Placeholder\].* Here is the sequence:

1. **Session Initiation (Command Flow):** The user action of starting a
    session on the PC triggers command messages over the network. The
    PC's JsonSocketServer sends a
    `{"type": "command", "command": "start_recording", ...}` (for
    example) to each connected Android
    device[\[38\]](PythonApp/network/device_server.py#L410-L419)[\[14\]](PythonApp/network/device_server.py#L424-L432).
    These messages are small JSON payloads, prefixed with a length
    header (to ensure the receiver knows how many bytes to
    read)[\[39\]](PythonApp/network/device_server.py#L156-L165).
    When an Android device receives the start command, it immediately
    responds (if needed) with an acknowledgment
    (`{"type": "ack", "cmd": "start_recording", "status": "ok"}`)[\[40\]](PythonApp/network/device_server.py#L276-L284)
    and then begins its recording process. This command flow is
    one-to-many (one PC to multiple clients) and happens almost
    simultaneously to all devices (the PC either sends commands in a
    quick loop or uses a broadcast helper function to send to
    all[\[14\]](PythonApp/network/device_server.py#L424-L432)).

1. **Sensor Data Capture (Local Flow on Devices):** Once recording,
    each device is capturing data from sensors:

1. The **camera data** (visual and thermal) flows from the camera
    hardware through Android's Camera2 API into either a file or a
    buffer. On Android, the CameraRecorder sets up a MediaRecorder that
    encodes video frames directly to an MP4 file on the device's file
    system[\[41\]](PythonApp/webcam/webcam_capture.py#L98-L106)[\[42\]](PythonApp/webcam/webcam_capture.py#L159-L168).
    Simultaneously, for thermal, if a separate stream exists, it might
    use a similar approach or raw frames saved as images (depending on
    implementation). The key is that frames are timestamped by the
    system -- the MediaRecorder frames are implicitly timed, and if raw
    frames are grabbed (for thermal or for preview), the code attaches
    the current timestamp to them (for preview frames, they even convert
    to Base64 strings to send to PC).

1. The **GSR sensor data** flow varies by mode: in direct PC mode, the
    PC's ShimmerManager receives Bluetooth packets, decodes them to
    numeric values (like GSR microSiemens) and immediately writes them
    to a CSV file or stores them in memory
    queues[\[43\]](PythonApp/shimmer_manager.py#L9-L17)[\[12\]](PythonApp/shimmer_manager.py#L91-L99).
    In Android-mediated mode, the Shimmer Android API delivers sensor
    samples to the phone app, which then either writes to a local CSV on
    the phone or streams the values as JSON messages to the PC (the code
    supports a streaming socket for live
    data[\[44\]](AndroidApp/src/main/java/com/multisensor/recording/recording/ShimmerRecorder.kt#L74-L82)[\[45\]](AndroidApp/src/main/java/com/multisensor/recording/recording/ShimmerRecorder.kt#L76-L84)).
    In both cases, each sensor sample is augmented with timing info:
    e.g., the code records the sample's device timestamp and the system
    time it arrived on the
    PC[\[12\]](PythonApp/shimmer_manager.py#L91-L99),
    ensuring later that alignment can be done.

1. **Real-Time Data Communication (Status/Preview Flow):** Throughout
    recording, a parallel flow of **status and preview data** occurs
    from the Android devices back to the PC. Each device periodically
    sends a `status` message with its current recording status (every
    few
    seconds)[\[46\]](PythonApp/network/device_server.py#L228-L237)[\[47\]](PythonApp/network/device_server.py#L240-L248).
    This includes data like battery % and free storage, as well as a
    `timestamp` (which can be used by PC to gauge device clock vs PC
    clock). These status packets help update the UI and also carry
    implicit sync info. Additionally, if preview is enabled, the device
    captures a frame (say every 1 second), compresses it (e.g., JPEG),
    Base64-encodes it, and sends a `preview_frame` message containing a
    small image
    string[\[7\]](PythonApp/network/device_server.py#L244-L252).
    The PC receives this and emits a signal that the GUI uses to display
    the new frame. This data flow is one-way from each device to PC and
    is designed to be low-bandwidth (e.g., a thumbnail image rather than
    full-frame, to avoid bogging down the network). Meanwhile, if the
    Shimmer is streaming live via Android, those readings might also be
    sent continuously in `sensor_data`
    messages[\[35\]](PythonApp/network/device_server.py#L256-L265);
    however, in practice the PC may choose not to plot every point to
    avoid overload -- it could sample or aggregate before display.

1. **Command and Control Feedback:** The PC can also send other
    commands during the session -- for example, if the user triggers an
    event annotation, the PC might send a `notification` message to
    devices (or directly log it on PC). In many cases, the annotation is
    handled on PC side (since PC knows the session time and can just
    write to the events file immediately). If devices needed to do
    something (like flash a light when an event is marked), a message
    would be sent. In our design, most *mid-session* control is minimal;
    the heavy command flows are start and stop.

1. **Session Termination and Data Gathering:** When stop command is
    issued, the data flow reverses for file transfer. Each device, after
    closing its files, initiates a **file transfer protocol** to send
    the recorded files to PC. The flow is:

1. Device sends a `file_info` message indicating it is about to send a
    file, including file name and
    size[\[48\]](PythonApp/network/device_server.py#L284-L293)[\[49\]](PythonApp/network/device_server.py#L298-L306).
    For example, `"name": "rgb_video.mp4", "size": 50012345`.

1. PC prepares to receive by creating a new file in the session folder
    (`DeviceID_rgb_video.mp4`) and responds (implicitly via ack or
    readiness).

1. Device then sends a series of `file_chunk` messages, each containing
    a segment of the file encoded (typically in
    Base64)[\[50\]](PythonApp/network/device_server.py#L320-L328).
    The PC decodes each chunk and writes to the file
    handle[\[51\]](PythonApp/network/device_server.py#L323-L331).
    This continues until the whole file is sent (chunks are often a few
    KB each). The PC's networking layer tracks how many bytes have been
    received and can log
    progress[\[52\]](PythonApp/network/device_server.py#L330-L338).

1. When the device finishes sending, it sends `file_end` message with
    the file
    name[\[53\]](PythonApp/network/device_server.py#L347-L355).
    PC then closes the file and compares the received byte count to the
    expected
    size[\[54\]](PythonApp/network/device_server.py#L356-L364).
    If they match, PC logs success and sends back a confirmation
    (`file_received` message with status
    ok)[\[55\]](PythonApp/network/device_server.py#L364-L372).
    If there's a mismatch, PC logs an error and could request a retry
    (in our code, it at least reports the error; a full retry mechanism
    could be initiated if needed).

1. This process repeats for each file (each device might have multiple
    files: e.g., one for video, one for thermal, one for sensor data).
    The PC can pipeline requests or handle one device at a time. In the
    current implementation, it likely sequentially requests each
    expected file from each
    device[\[56\]](PythonApp/network/device_server.py#L509-L518)
    to avoid network congestion (with a short delay between as
    indicated[\[57\]](PythonApp/network/device_server.py#L516-L524)).

1. Throughout this, the Session Manager on PC is aware of incoming
    files and uses
    `add_file_to_session(device_id, file_type, path, size)` to update
    the session
    metadata[\[58\]](PythonApp/session/session_manager.py#L120-L129)[\[59\]](PythonApp/session/session_manager.py#L130-L139).
    This means the session's JSON metadata will list, for each device,
    the files that were collected (with file paths and sizes),
    confirming that they are now on the PC.

1. **Post-Processing Flow:** If post-processing (FR-13) is enabled,
    once all raw data is gathered, the PC may invoke additional
    processing. For instance, the PC might load the recorded video file
    and run the hand segmentation algorithm. This would generate output
    files (images or mask videos) which the Session Manager then places
    into the session folder (e.g., under a `processed/` subdirectory or
    by appending results next to original files). The data flow here is
    local on the PC -- using OpenCV or other libraries on the saved
    files. The results are logged (the `post_processing` field in
    session metadata is updated to true with a
    timestamp[\[60\]](PythonApp/session/session_manager.py#L218-L226)[\[61\]](PythonApp/session/session_manager.py#L232-L240)).

1. **Data Storage and Access:** At the end of the data flow, all data
    resides in an organised manner on the PC. The **session folder**
    (typically under a `recordings/` directory) contains the following:
    video files (named by device and type), sensor data CSV, events log,
    session metadata JSON, and any calibration or processed data
    subfolders. For example, one might see:

- recordings/session_20250806_101530/
        session_metadata.json
        DeviceA_rgb_video.mp4
        DeviceA_thermal_video.mp4
        DeviceB_rgb_video.mp4
        DeviceB_sensors.csv
        stimulus_events.csv
        calibration/ (folder with calibration images)
        processed/ (folder with segmented hand images)

  This structure was defined by the requirements and is implemented in
  code (the Android app creates similar filenames on its
  side[\[62\]](AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L374-L382),
  and the PC adds the device prefix upon receipt). Because each data
  file is timestamped or accompanied by timestamps internally, a
  researcher can load, for instance, the `DeviceB_sensors.csv` and the
  videos and align them using the timestamps. The data integrity checks
  ensure these files are complete and not corrupted.

1. **Scalability and Data Flow Considerations:** The architecture's
    data flow is largely **parallel** -- each device operates
    independently for data capture, which is crucial for scalability.
    The PC coordinates and eventually brings data together. As more
    devices are added, the network traffic and PC disk I/O grow, but the
    modular handling (each device in its thread) means the system can
    scale up to the point where either network bandwidth or PC write
    speed becomes the bottleneck. Because video files can be large, the
    file transfer part is the heaviest data flow; the system mitigates
    issues by writing chunks to disk as they arrive and using a binary
    encoding to avoid JSON overhead for large
    data[\[50\]](PythonApp/network/device_server.py#L320-L328).
    Also, to maintain performance, intensive tasks like video encoding
    are done on the devices (leveraging phone hardware encoders), and
    the PC mainly handles control and file aggregation -- this
    distribution balances load across the system.

In summary, the system's architecture is a **star topology** with
intelligent clients, and the data flow is designed to minimis\1 latency
and maintain synchronisation. The PC orchestrates the process (command
flows out, data flows back), which aligns well with the requirement of
central control and monitoring. The use of standard formats (MP4, CSV,
JSON) in the data flow ensures that once data reaches the PC, it's
immediately usable with analysis tools. The combination of real-time
communication and local storage means the system is robust: even if the
network has a hiccup, each phone still has its data, and it can be
transferred later. The thorough session metadata and logging implemented
(on both PC and Android) provide traceability -- one can trace each step
in the data flow from the logs (e.g., see in the PC log that Device A
started recording at time X, or that file transfer for file Y completed,
etc.). Thus, the architecture and data flow together fulfill the system
requirements by enabling **coordinated, synchronous data capture and
reliable data unification**.

***Figure 3.3: Data flow diagram for a typical session, illustrating
command dissemination, local data capture on devices, status/preview
feedback, and post-session data collection into the PC's storage
\[Placeholder\].***

## 3.7 Data Requirements and Management

The multi-sensor system produces and handles a variety of data types.
This section outlines the specific **data requirements**, including data
formats, volumes, and how data is managed and stored to ensure integrity
and accessibility for analysis.

**Data Types and Formats:** The primary data generated by the system
are: - **Video data:** This includes regular RGB video and thermal
video. The video is encoded in a standard compressed format
(MPEG-4/H.264 in an MP4 container) on the recording devices to manage
file size. Each video file is accompanied by an internal timestamp track
(every video frame has a timestamp in the file), and frame rate
information is stored. Thermal video, if captured, is also stored as an
MP4 (if using a sensor that outputs a stream) or potentially as a
sequence of images if the device captures frame-by-frame -- in this
implementation it was designed to be an MP4 for consistency (FR-05).
Typical video resolution for RGB might be 1920×1080 at 30 fps (if the
phone supports it, possibly even 4K as configured in
code[\[63\]](AndroidApp/src/main/java/com/multisensor/recording/recording/CameraRecorder.kt#L74-L82)[\[64\]](AndroidApp/src/main/java/com/multisensor/recording/recording/CameraRecorder.kt#L75-L83)),
whereas thermal cameras usually have lower resolution (for example
320×240 or 160×120 at a lower frame rate like 8--30 fps). Regardless,
the system handles these as just "video files" -- the exact resolution
and frame rate used in a session are recorded in the session
configuration
file[\[65\]](AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L356-L364)[\[26\]](AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L370-L378)
for reference. - **Sensor data:** The Shimmer GSR (and associated
sensors) produce time-series data. This data is recorded in **CSV
(Comma-Separated Values)** format for human readability and easy import
into analysis tools. Each row in the CSV represents a sensor sample. For
example, a row might contain: *Timestamp, SystemTime, GSR_Conductance,
PPG, Accel_X, Accel_Y, Accel_Z,
BatteryLevel*[\[66\]](AndroidApp/src/main/java/com/multisensor/recording/recording/ShimmerRecorder.kt#L113-L119).
The `Timestamp` is the device's relative time or sample count, and
`SystemTime` could be an absolute UNIX timestamp (to tie it to PC
clock). Using CSV ensures that researchers can open the file in Python,
MATLAB, Excel, etc. easily. If multiple Shimmer sensors are used, either
multiple CSV files are created (one per device) or all data is merged
into one file with device identifiers -- in our design we create
separate files per device to keep things simple (the file naming will
include the device ID or name). - **Metadata and logs:** The system
generates JSON and text files for metadata. The **session metadata**
(JSON) contains structured information about the session: session ID,
start/end times, list of devices, files names, and possibly environment
info (like app versions). For instance, `session_metadata.json` might
have an entry listing each device by ID and the files it
produced[\[67\]](PythonApp/session/session_manager.py#L104-L112)[\[68\]](PythonApp/session/session_manager.py#L130-L138).
Additionally, a human-readable **session_info.txt** is generated on the
Android side listing the folder contents and
status[\[69\]](AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L322-L330)[\[4\]](AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L334-L342).
This redundancy is intentional for clarity -- researchers can quickly
read the text summary or use the JSON for programmatic processing. The
PC and devices also maintain **log files** (e.g., `session_log.txt`)
that record events and any errors with timestamps -- these are useful
for debugging and audit trails. - **Event annotations:** As discussed,
event markers are stored in a simple CSV file (e.g.,
`stimulus_events.csv`). Each line has an event timestamp (in
milliseconds or a readable time format) and a label. This file is
managed by the Session Manager (either on PC or device) whenever an
event is
added[\[27\]](AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L126-L134).
The format is straightforward, ensuring that during analysis one can
load this file and overlay events onto signal timelines.

**Data Volume and Storage Considerations:** The system is expected to
handle significant data volumes, especially for video. For example, one
minute of 1080p RGB video at 30 fps can be on the order of 60--120 MB
when encoded (depending on the scene and compression bit rate). Thermal
video tends to be smaller (both in resolution and often lower frame
rate, plus uniform scenes compress well), perhaps a few MB per minute.
GSR CSV files are relatively tiny in comparison (on the order of
kilobytes per minute; e.g., 60 samples per second for 60 seconds is 3600
lines -- a few hundred KB at most). Even so, a multi-hour recording
could generate multiple gigabytes of data (mostly video), so the
system's data requirement is that devices have **sufficient storage**
available. The Android app checks available free space on the device
storage before and during
recording[\[70\]](AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L424-L428)
and can warn the PC if space is low. The data management plan recommends
using high-capacity SD cards or internal memory on phones, and the PC of
course typically has ample disk space.

To manage this, each recording session's data is isolated in its own
directory (both on the device during capture and on the PC after
aggregation). This not only organises the data but makes it easier to
move or archive entire sessions. If a user needs to free space, they can
archive older session folders to an external drive. The naming
convention with session timestamps (e.g., `session_YYYYMMDD_HHMMSS`)
ensures uniqueness and chronological order. The inclusion of the session
name (if the researcher provided one) in the folder or file names helps
in identifying the context of the data (for example,
`session_20250806_101530_stressTest` if "stressTest" was given as a
name).

**Data Integrity and Verification:** As outlined in NFR-04, the system
has built-in measures to verify data integrity. During file transfer,
checksums or at least byte counts are
compared[\[54\]](PythonApp/network/device_server.py#L356-L364).
After a session, the Session Manager on PC logs a **session summary**
that includes whether each expected file is present and its
size[\[71\]](AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L410-L418).
For example, the PC log might say "RGB Video: ✓ (50012345 bytes),
Thermal Video: ✓ (12345678 bytes), Shimmer Data: ✓ (N bytes)" confirming
successful captures. In case a file is missing or incomplete, that is
flagged in the log (and the PC UI would alert the user). The system
avoids modifying the raw data once recorded -- all data files are
write-once (append or create-only). If post-processing outputs are
generated, they are written as new files rather than altering the
originals. This way, the raw recordings remain pristine for analysis or
for rerunning analysis with different parameters.

**Data Accessibility and Use:** The data formats chosen (MP4, CSV, JSON)
make the dataset **portable** across analysis environments. Researchers
can copy the entire session folder and load it into analysis software.
For example, MP4 videos can be played or imported into computer vision
pipelines (OpenCV, etc.), and CSV sensor data can be read by pandas or
MATLAB. The system's documentation includes a **Technical Glossary**
(not reproduced here) which describes each data field and any
calibration that has been applied, so analysts understand how to
interpret values (e.g., that GSR is in microSiemens, temperature might
be in Celsius if thermal camera yields absolute temperature after
calibration, etc.). In some cases, calibration results (from Use Case 2)
might also produce data (like a camera intrinsic matrix or a mapping
file); these are stored in the calibration folder or appended to the
metadata JSON so that analysis code can automatically correct the data
if needed.

**Data Security and Privacy Management:** As noted in NFR-09, while the
system doesn't inherently encrypt data, it assumes data will be handled
on secure storage. If required, the entire `recordings/` directory on
the PC can reside on an encrypted drive. Personal identifiers are
generally not embedded in file names (device IDs are generic like
"phone1" or a device serial, and session IDs are timestamps or
user-defined codes, not participant names). This is a conscious decision
to keep the data pseudonymized at the file system level. The mapping
from session ID to a specific participant or experiment trial would be
maintained separately by the researcher (not in the recorded data
itself), to protect participant identity if files are shared with others
for analysis.

In conclusion, the system's data management strategy creates a
**self-contained record** of each session that is easy to navigate and
analyse. By structuring the files logically and including metadata and
logs, the system meets all requirements for data completeness,
integrity, and usability. Even if months later a researcher or a
different team examines the files, they should be able to understand the
content and trust that it accurately represents what occurred during the
session. This careful attention to data requirements and management
ensures that the valuable multi-modal data collected by the system can
lead to reliable research findings in contactless GSR prediction.
---
[\[1\]](PythonApp/shimmer_manager.py#L144-L151)
[\[2\]](PythonApp/shimmer_manager.py#L138-L145)
[\[12\]](PythonApp/shimmer_manager.py#L91-L99)
[\[13\]](PythonApp/shimmer_manager.py#L146-L150)
[\[22\]](PythonApp/shimmer_manager.py#L72-L80)
[\[23\]](PythonApp/shimmer_manager.py#L96-L104)
[\[24\]](PythonApp/shimmer_manager.py#L184-L191)
[\[33\]](PythonApp/shimmer_manager.py#L19-L28)
[\[34\]](PythonApp/shimmer_manager.py#L51-L59)
[\[43\]](PythonApp/shimmer_manager.py#L9-L17)
shimmer_manager.py

<PythonApp/shimmer_manager.py>

[\[3\]](PythonApp/session/session_manager.py#L74-L81)
[\[11\]](PythonApp/session/session_manager.py#L216-L224)
[\[21\]](PythonApp/session/session_manager.py#L82-L91)
[\[58\]](PythonApp/session/session_manager.py#L120-L129)
[\[59\]](PythonApp/session/session_manager.py#L130-L139)
[\[60\]](PythonApp/session/session_manager.py#L218-L226)
[\[61\]](PythonApp/session/session_manager.py#L232-L240)
[\[67\]](PythonApp/session/session_manager.py#L104-L112)
[\[68\]](PythonApp/session/session_manager.py#L130-L138)
session_manager.py

<PythonApp/session/session_manager.py>

[\[4\]](AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L334-L342)
[\[8\]](AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L124-L133)
[\[9\]](AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L300-L308)
[\[10\]](AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L311-L319)
[\[25\]](AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L354-L362)
[\[26\]](AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L370-L378)
[\[27\]](AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L126-L134)
[\[28\]](AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L140-L148)
[\[62\]](AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L374-L382)
[\[65\]](AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L356-L364)
[\[69\]](AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L322-L330)
[\[70\]](AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L424-L428)
[\[71\]](AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt#L410-L418)
SessionManager.kt

<AndroidApp/src/main/java/com/multisensor/recording/service/SessionManager.kt>

[\[5\]](PythonApp/network/device_server.py#L355-L364)
[\[6\]](PythonApp/network/device_server.py#L26-L34)
[\[7\]](PythonApp/network/device_server.py#L244-L252)
[\[14\]](PythonApp/network/device_server.py#L424-L432)
[\[15\]](PythonApp/network/device_server.py#L484-L492)
[\[18\]](PythonApp/network/device_server.py#L216-L224)
[\[19\]](PythonApp/network/device_server.py#L486-L494)
[\[20\]](PythonApp/network/device_server.py#L313-L322)
[\[29\]](PythonApp/network/device_server.py#L129-L137)
[\[30\]](PythonApp/network/device_server.py#L120-L128)
[\[31\]](PythonApp/network/device_server.py#L18-L26)
[\[32\]](PythonApp/network/device_server.py#L40-L48)
[\[35\]](PythonApp/network/device_server.py#L256-L265)
[\[38\]](PythonApp/network/device_server.py#L410-L419)
[\[39\]](PythonApp/network/device_server.py#L156-L165)
[\[40\]](PythonApp/network/device_server.py#L276-L284)
[\[46\]](PythonApp/network/device_server.py#L228-L237)
[\[47\]](PythonApp/network/device_server.py#L240-L248)
[\[48\]](PythonApp/network/device_server.py#L284-L293)
[\[49\]](PythonApp/network/device_server.py#L298-L306)
[\[50\]](PythonApp/network/device_server.py#L320-L328)
[\[51\]](PythonApp/network/device_server.py#L323-L331)
[\[52\]](PythonApp/network/device_server.py#L330-L338)
[\[53\]](PythonApp/network/device_server.py#L347-L355)
[\[54\]](PythonApp/network/device_server.py#L356-L364)
[\[55\]](PythonApp/network/device_server.py#L364-L372)
[\[56\]](PythonApp/network/device_server.py#L509-L518)
[\[57\]](PythonApp/network/device_server.py#L516-L524)
device_server.py

<PythonApp/network/device_server.py>

[\[16\]](changelog.md#L34-L41)
[\[17\]](changelog.md#L60-L64)
changelog.md

<changelog.md>

[\[36\]](AndroidApp/src/main/java/com/multisensor/recording/ui/MainViewModel.kt#L32-L40)
[\[37\]](AndroidApp/src/main/java/com/multisensor/recording/ui/MainViewModel.kt#L34-L42)
MainViewModel.kt

<AndroidApp/src/main/java/com/multisensor/recording/ui/MainViewModel.kt>

[\[41\]](PythonApp/webcam/webcam_capture.py#L98-L106)
[\[42\]](PythonApp/webcam/webcam_capture.py#L159-L168)
webcam_capture.py

<PythonApp/webcam/webcam_capture.py>

[\[44\]](AndroidApp/src/main/java/com/multisensor/recording/recording/ShimmerRecorder.kt#L74-L82)
[\[45\]](AndroidApp/src/main/java/com/multisensor/recording/recording/ShimmerRecorder.kt#L76-L84)
[\[66\]](AndroidApp/src/main/java/com/multisensor/recording/recording/ShimmerRecorder.kt#L113-L119)
ShimmerRecorder.kt

<AndroidApp/src/main/java/com/multisensor/recording/recording/ShimmerRecorder.kt>

[\[63\]](AndroidApp/src/main/java/com/multisensor/recording/recording/CameraRecorder.kt#L74-L82)
[\[64\]](AndroidApp/src/main/java/com/multisensor/recording/recording/CameraRecorder.kt#L75-L83)
CameraRecorder.kt

<AndroidApp/src/main/java/com/multisensor/recording/recording/CameraRecorder.kt>
