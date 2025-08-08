# Chapter 6: Conclusions and Evaluation

<<<<<<< HEAD
This chapter provides a critical assessment of the developed
Multi-Sensor Recording System, highlighting its achievements and
technical contributions, evaluating how well the outcomes meet the
initial objectives, discussing limitations encountered, and outlining
potential future work and extensions. The project set out to create a
**contactless Galvanic Skin Response (GSR) recording platform** using
multiple synchronized sensors, and the final implementation demonstrates
substantial progress toward this goal. All core system components were
implemented and exercised in testing, establishing a strong foundation
for future research in non-intrusive physiological monitoring. The
following sections detail the accomplishments of the work, compare the
results against the project's objectives, acknowledge remaining
limitations, and suggest directions for continued development.

## Achievements and Technical Contributions

The **Multi-Sensor Recording System** realized several significant
achievements, advancing both practical technology for physiological data
collection and the underlying engineering methodologies. Key
accomplishments and technical contributions of this project include:

- **Integrated Multi-Modal Sensing Platform:** The project delivered a
  functional platform consisting of an **Android mobile application**
  and a **Python-based desktop controller** operating in unison. This
  cross-platform system supports synchronized recording of
  **high-resolution RGB video**, **thermal infrared imagery**, and
  **physiological GSR signals** (from a Shimmer3 GSR+ sensor)
  simultaneously. The heterogeneous sensors run concurrently in real
  time, enabling a rich multi-modal dataset for contactless GSR
  research. This successful integration of multiple modalities satisfies
  the core project goal of facilitating **contactless GSR measurement**
  by combining conventional contact sensors with camera-based sensing.

- **Distributed Hybrid Architecture:** A novel distributed architecture
  was designed and implemented to coordinate multiple sensor devices in
  parallel. In this topology, a central PC controller orchestrates the
  recording sessions (hub-and-spoke style) while each mobile device
  performs local data capture and preliminary processing. This **hybrid
  star--mesh architecture** balances centralized control with on-device
  computation, providing both coordination and scalability. It allows
  the system to manage **up to eight sensor nodes simultaneously**,
  demonstrating that a multi-device approach can maintain
  synchronization and reliability across devices. This is an innovative
  design compared to traditional physiological monitoring systems that
  often rely on a single device or purely central data loggers. The
  project showed that such a distributed approach can expand the scope
  of experiments (for example, recording multiple camera angles or
  multiple participants in sync) without sacrificing performance.

- **High-Precision Synchronization Mechanisms:** Achieving tight
  temporal alignment across all data streams was a critical technical
  challenge that the system addressed with a custom **multi-modal
  synchronization framework**. The implementation combines techniques
  such as using a Network Time Protocol (NTP) server for global clock
  reference, exchange of timestamped commands, and periodic clock
  calibration across devices. As a result, video frames, thermal images,
  and GSR sensor readings are all timestamped against a common clock
  with minimal drift. Empirical testing in controlled conditions
  indicates that the system can maintain temporal precision on the order
  of only a few milliseconds of drift between devices, meeting or
  exceeding the initial design requirement of ±5 ms synchronization
  tolerance. This level of precision is comparable to research-grade
  wired acquisition systems, validating that a distributed wireless
  sensor network can be used for rigorous physiological measurements
  without significant loss of timing fidelity.

- **Advanced Calibration Procedures:** A comprehensive **calibration
  module** was developed to support accurate fusion of data from
  different sensors. Using established computer vision techniques, the
  system performs **intrinsic camera calibration** as well as
  **cross-modal calibration** (e.g. aligning the thermal camera view
  with the RGB camera view). This allows thermal imagery to be
  geometrically registered to the RGB video frames, ensuring that
  corresponding regions in both modalities coincide (for example,
  mapping a hot area in the thermal image to the exact location on the
  subject's skin in the RGB image). In addition, temporal calibration
  routines were implemented to verify and fine-tune any remaining timing
  offsets between devices. These calibration processes improve the
  validity of combining multi-modal data and are crucial for meaningful
  contactless GSR analysis. The successful implementation of both
  spatial and temporal calibration workflows demonstrates the system's
  ability to maintain alignment across heterogeneous sensors, which is a
  noteworthy technical contribution beyond basic data recording.

- **Robust Networking and Device Management:** The project introduced a
  custom networking protocol for coordinating devices, built on
  lightweight JSON message exchanges over sockets. This protocol
  supports device handshaking and identification, remote command
  dissemination (for example, broadcasting start/stop recording signals
  to all connected devices), periodic heartbeats and status updates, and
  streaming of sensor data back to the controller in real time. A
  central **Session Manager** on the PC and corresponding client logic
  on each mobile device handle session configuration and state
  management. The networking layer was designed for reliability and low
  latency: it includes features like connection retries, acknowledgments
  for critical messages, and buffering of data chunks to prevent loss
  during brief network interruptions. Basic security measures were also
  implemented (such as optional TLS encryption and device identity
  verification during handshake) to protect data in transit. The outcome
  is a robust distributed system in which multiple mobile nodes can join
  and operate in a synchronized session with minimal manual
  intervention. This reliable communication and device management
  framework enables **scalable multi-device recordings** and is a key
  technical contribution of the project.

- **User Interface and Usability Focus:** Considerable effort was
  devoted to developing a user interface and workflow that would allow
  researchers to operate the system with relative ease. The **desktop
  controller features a graphical UI** that lets users manage devices
  (e.g. connect/disconnect sensors, monitor status), configure recording
  sessions (select which data streams to record, set session
  identifiers), initiate calibration procedures, and observe live
  previews or status indicators during a session. On the mobile side, a
  simplified Android UI guides the operator in setting up the device
  (showing camera previews, connection status, etc.) without requiring
  low-level commands. The system also automates aspects of session
  management, such as organizing recorded files and metadata for each
  session, to streamline post-processing. While there is still room to
  improve polish, this emphasis on the end-user experience means the
  platform is closer to a practical research tool. It demonstrates that
  even a complex multi-sensor system can be made accessible to
  non-expert users through thoughtful interface design and automation of
  background tasks.

## Evaluation of Objectives and Outcomes

Against the objectives laid out at the start of the project, the
outcomes of the implementation are largely positive. The major project
objectives were: **(1)** to develop a synchronized multi-device
recording system integrating camera-based and wearable GSR sensors,
**(2)** to achieve temporal precision and data reliability comparable to
gold-standard wired systems, **(3)** to ensure the solution is
user-friendly and suitable for non-intrusive GSR data collection, and
**(4)** to validate the system through testing and, if possible, a pilot
study with real participants. Each of these objectives is considered
below in light of the project results:

- **Objective 1: Multi-Device Sensing Platform.** This objective has
  been **fully achieved**. The final system implementation successfully
  integrates multiple sensor modalities (video, thermal, and GSR) and
  multiple devices in a unified platform. A desktop application and one
  or more Android devices communicate seamlessly to collect synchronized
  data. All essential system components -- including the mobile data
  capture app, the network communication infrastructure, and the desktop
  control software -- were completed and have been shown to work
  together. The existence of this fully implemented platform means that
  the project's foundational goal of a multi-sensor recording system was
  realized. Researchers now have a tool (in prototype form) that can
  collect rich datasets combining physiological signals with visual and
  thermal observations, which is a strong step toward enabling
  contactless GSR measurement in practice.

- **Objective 2: Timing Precision and Reliability.** This objective has
  been **achieved**, with outcomes meeting and in some respects
  exceeding expectations in laboratory tests. The system's clock
  synchronization and scheduling mechanisms were validated during
  controlled experiments, demonstrating that all devices can record data
  with only minimal timing discrepancies (on the order of a few
  milliseconds between devices). This satisfies the initial requirement
  (which targeted at most a few tens of milliseconds of allowable drift)
  and provides confidence that the data streams are effectively
  simultaneous for analysis purposes. Moreover, the system proved to be
  stable and reliable during these controlled trials: no data loss or
  crashes occurred in test runs of typical duration under good network
  conditions. These results suggest that the design choices for
  networking and synchronization were sound. The combination of
  NTP-based time alignment, unified start triggers, and continuous
  monitoring of device status contributes to performance comparable to
  wired, centralized systems in terms of timing accuracy and recording
  reliability. Therefore, the technical benchmark of temporal precision
  was successfully met.

- **Objective 3: Usability and Researcher Experience.** This objective
  was **mostly achieved**. The project placed emphasis on creating an
  accessible user experience, and the delivered software reflects this
  in features such as the GUI for session control and automated data
  management. Users do not need to manually synchronize clocks or start
  recordings on each device; instead, the system provides central
  controls to handle these complex tasks behind the scenes. In practice,
  a single operator can configure devices and launch a recording session
  without interacting with low-level settings, which demonstrates a
  degree of user-friendliness appropriate for research environments.
  That said, the ease-of-use goal is only partially fulfilled because
  some aspects of the user experience require further refinement. During
  testing, it became apparent that the desktop application's interface
  could become unresponsive in certain scenarios, and the automatic
  device discovery was not optimally seamless (sometimes a device would
  not appear and needed a manual reconnection attempt). These issues did
  not prevent basic operation but indicate that the learning curve and
  robustness for end-users can be improved. Despite these shortcomings
  (discussed in detail as limitations below), the core design proves
  that the system is **practical for real-world use**: in a lab setting,
  a researcher was able to run the entire system and collect
  synchronized multi-modal data. The minor usability issues that remain
  are solvable, and with some fixes the platform is poised to be
  genuinely user-friendly.

- **Objective 4: System Validation via Pilot Study.** This objective was
  **only partially achieved**. The system underwent functional testing
  and internal evaluation, but a planned pilot data collection with
  human participants was **not conducted** by the end of the project
  timeline. On one hand, the technical validation of the system
  components was successful -- unit tests and simulated recordings
  showed that each part of the system works as intended in isolation and
  in integrated fashion. On the other hand, the lack of an actual pilot
  study means that the system's performance in a real-world experimental
  context (with real users and potentially longer recording sessions)
  has not been empirically demonstrated. The pilot was intended to serve
  as a proof-of-concept deployment of the platform in its target
  scenario, providing example data and uncovering any practical issues
  under realistic use. Unfortunately, due to a combination of factors --
  including time constraints late in the development cycle, unexpected
  delays in hardware delivery (e.g. the thermal camera device arrived
  later than expected), and residual system instability that required
  frequent restarts -- it was decided that conducting a pilot within the
  project period was not feasible. Deferring the pilot was a difficult
  decision, as it leaves an important aspect of the project incomplete.
  However, this compromise was necessary to focus on solidifying the
  system's implementation. The absence of pilot data is acknowledged as
  a gap, but it does not diminish the demonstrated capabilities of the
  system; rather, it points to an important next step that lies beyond
  this work. In summary, all technical objectives were met, but the
  **practical demonstration with end-users remains a significant
  task**. Completing that task in the future will be essential to fully
  validate the system under real operating conditions.

## Limitations of the Study

While the project achieved its primary technical goals, several
limitations became evident during development and testing. These
limitations highlight areas where the system did not fully meet
requirements or where further improvements are needed to consider the
platform truly robust. The key limitations of the study are as follows:

- **Unstable User Interface:** The system's user interface is still
  somewhat **buggy and prone to instability**. Test users observed
  occasional UI freezes and other inconsistent behaviors in the desktop
  application. For example, the GUI sometimes becomes unresponsive if
  multiple actions are triggered in quick succession, and certain
  features (like the device status refresh) only provide placeholder
  feedback rather than dynamic updates. These instabilities in the
  interface can disrupt the user experience, forcing operators to
  restart the application or use workarounds. The underlying
  functionality (recording, networking, etc.) remains intact during
  these UI issues, but the lack of polish and reliability in the
  interface means the tool is not yet as convenient or trustworthy as
  intended for end-users. In its current state, the controller
  application requires cautious operation, and this detracts from the
  otherwise strong emphasis on usability. Improving the GUI stability is
  therefore a priority before the system can be confidently used by
  non-technical researchers.

- **Unreliable Device Recognition:** The mechanism for automatic device
  discovery and recognition on the network proved to be **not completely
  reliable**. The system is supposed to detect and list each sensor
  device as it connects (using a handshake and capability exchange). In
  practice, it was found that this detection process can occasionally
  fail or misidentify a device's status. For instance, in a test
  scenario, an Android device joining the session did not appear in the
  PC's device list until the connection was retried, and sometimes a
  connected device would still show as "disconnected" due to missed
  heartbeat messages. These hiccups are especially evident in
  less-than-ideal network conditions (high latency or wireless
  interference). The unreliable device recognition leads to setup delays
  and undermines the intended plug-and-play experience. Instead of
  effortlessly connecting all sensors, the user might have to manually
  refresh the device list or restart connections to ensure every device
  is accounted for. This limitation complicates the workflow and could
  frustrate users, particularly those who are not familiar with
  troubleshooting networked systems. In summary, although the core
  networking functions work, the **device discovery aspect is
  inconsistent**, requiring refinement.

- **Incomplete Hand Segmentation Integration:** A **hand segmentation
  module** (based on Google's MediaPipe hand landmark detection) was
  developed as an experimental feature to enhance analysis of the video
  stream -- for example, by automatically isolating the subject's hand
  regions in the video or thermal images. However, this module was **not
  fully integrated** into the live recording pipeline. As it stands, the
  system does not utilize the hand segmentation results in real time;
  for instance, it does not annotate recorded videos with hand-region
  data, nor does it use those insights to trigger any adaptive recording
  logic. The hand segmentation functionality exists in the codebase (and
  can be run in a demo mode separately), but it remains disconnected
  from the primary application flow. Thus, the potential benefits of
  incorporating hand segmentation -- such as focusing analytics on
  regions of interest (the hands), or enabling gesture-based metadata
  tagging -- are not realized in the current system. This limitation was
  largely due to time constraints and the need to prioritize core
  features. The groundwork is laid (the module is implemented), but more
  development is needed to merge it with the main application.

- **No Pilot Data Collection:** As noted, **no pilot user study or data
  collection was performed** by the end of the project. The plan to
  conduct a small pilot -- recording a few participants to generate
  example datasets and evaluate the system in a realistic scenario --
  was not executed. This was due to several practical issues: **(a)**
  persistent system instability in the weeks leading up to the deadline,
  which would have undermined the pilot's usefulness, **(b)** tight time
  constraints that left insufficient opportunity to properly plan and
  run a pilot (including obtaining ethical approvals and recruiting
  participants), and **(c)** delays in hardware delivery that compressed
  the integration and testing period, leaving little buffer to organize
  an external study. Because no pilot data was collected, an important
  consequence is that **the system's performance in real-world usage
  remains unvalidated**. All evaluations so far were done in a
  controlled lab environment by the development team. There may be
  unforeseen challenges that only appear in actual field use (for
  example, variability in how different users interact with the sensors,
  or prolonged operation over hours). The absence of a pilot means the
  project cannot conclusively demonstrate the practical utility of the
  system or quantify its effectiveness in measuring GSR or related
  phenomena in a live context. This is acknowledged as a significant
  limitation; however, it is a temporary one that can be addressed in
  future work. The lack of pilot results does not detract from the
  system's technical contributions, but it does leave an important
  question mark over its readiness for real-world deployment.

In summary, the limitations include the need for a more stable and
polished UI, more robust device connectivity and discovery, the
completion of integrating the hand segmentation feature, and the
empirical validation of the system with actual users. These issues must
be resolved to transition the system from a prototype into a reliable
research tool.

## Future Work and Extensions

Building on the findings and limitations above, there are several clear
avenues for future work. The next steps naturally address the
shortcomings identified and also open new opportunities to extend the
platform's capabilities. The following are key areas in which future
efforts could be directed:

- **Stability Improvements and UI Refinement:** The top priority is to
  **harden the system's stability** and refine the user interface.
  Future work should involve thorough debugging of the desktop
  application's GUI event handling to eliminate crashes, freezes, and
  unresponsiveness. This may include adding more extensive UI testing
  (covering edge cases and rapid user interactions) to catch issues
  early. Improving the Android app's interface stability (e.g. its
  fragment navigation and preview updates) is also important. By fixing
  the known UI bugs and streamlining the workflow, the overall
  reliability of the system will increase. A polished, stable interface
  will enable researchers to trust the system during long recording
  sessions. These refinements turn the prototype into a more
  production-ready tool for daily experimental use.

- **Reliable Device Discovery and Networking:** Another crucial
  improvement is to make device recognition and network communication
  **more reliable and seamless**. Efforts should focus on strengthening
  the automatic device discovery protocol so that devices are
  consistently detected on the first attempt. This could involve using
  more robust discovery mechanisms (such as broadcast/multicast
  announcements with verification, or a manual pairing procedure as a
  fallback) and improving how the system handles network latency or
  packet loss. Additionally, optimizing the networking code and
  error-handling will help ensure that once devices are connected, they
  remain in sync without hiccups. For example, incorporating better
  heartbeat monitoring and reconnection logic would prevent devices from
  appearing "lost" due to momentary network drops. The goal is to
  achieve truly plug-and-play operation, where researchers can turn on
  the sensor devices and have them appear ready in the controller UI
  with minimal intervention. By enhancing the networking layer's
  resilience, the system will be easier to use and more robust in
  diverse network environments.

- **Full Integration of Hand Segmentation (and Other Analytics):**
  Integrating the hand segmentation module into the live data pipeline
  is a clear next step. Future development should tie the
  MediaPipe-based hand landmark detection into recording sessions so
  that the system can record not only raw video, but also derived
  information about the subject's hand position or gestures in real
  time. This could mean overlaying bounding boxes or masks on the video
  where hands are detected, or logging the hand motion data alongside
  other sensor streams. Once integrated, the hand segmentation data
  could feed into real-time analytics --- for example, detecting if a
  participant wipes their hands or moves out of frame, and then flagging
  those events in the data. Beyond hand segmentation, the platform could
  be extended with additional computer vision analytics, such as facial
  expression recognition or remote photoplethysmography (if a camera is
  pointed at a face), to enrich the set of contactless measures. These
  extensions would transform the system from a pure recording tool into
  an intelligent monitoring system that not only records data but also
  interprets certain aspects of human behavior or physiology on the fly.
  Such enhancements build on the current work and would provide greater
  value for research use cases, especially in studies of human affect or
  stress where gestures and facial cues are informative.

- **Conducting Pilot Studies and Empirical Validation:** A top priority
  for future work is to **use the system in an actual pilot study** or
  series of experiments with human participants. Conducting a
  well-designed pilot will serve multiple purposes: it will validate the
  system's end-to-end functionality in a realistic setting, provide an
  initial dataset to analyze the correlation between the contactless
  signals (thermal imaging, video) and traditional GSR readings, and
  likely reveal any practical issues not discovered in lab tests (such
  as usability hurdles during setup, or sensor interference in real
  environments). Moving forward, the plan would be to recruit a small
  number of participants and collect synchronized multimodal data in
  scenarios relevant to the intended application (for example, having
  subjects experience stimuli that elicit GSR changes while recording
  them). The pilot study would allow for quantitative evaluation of the
  system's performance: one could assess how closely the contactless
  measurements (like thermal changes or video-based estimates) track the
  actual GSR data from the Shimmer device, thereby evaluating the
  efficacy of the contactless approach. Additionally, user feedback from
  those sessions would guide further improvements. Ultimately, executing
  such pilot studies is essential to transition the project from a
  promising prototype to a validated research instrument. This future
  work will demonstrate the practical utility of the system and build
  confidence that the platform can reliably be used in real-world
  research on physiological monitoring.

- **Expanding Sensor Support and Modalities:** Another extension is to
  broaden the system's scope by adding support for more sensors or data
  modalities. For example, future versions of the platform could
  integrate additional physiological signals such as heart rate (e.g.
  via PPG/ECG sensors) or respiration rate, or include more advanced
  cameras (depth cameras or higher-resolution thermal imagers).
  Supporting multiple cameras per device or multiple wearables per
  participant is also a possible extension to capture more comprehensive
  views of the subject. Each new modality would come with challenges in
  synchronization and data management, but the system's existing
  architecture is modular enough to accommodate expansion. By extending
  sensor support, the platform could facilitate richer experiments (for
  instance, monitoring multiple physiological parameters concurrently,
  or capturing data from several angles around a person). Furthermore,
  as new hardware becomes available, the system should be updated to
  leverage those improvements -- for example, using mobile devices with
  better processors or cameras to improve frame rates and data quality.
  Overall, this line of future work will push the platform towards being
  a versatile, all-in-one solution for multi-sensor research, rather
  than being limited to the specific sensors used in this initial
  project.

- **Machine Learning for Contactless GSR Estimation:** With a large
  multi-modal dataset collected (through the above pilot studies and
  additional sensors), an exciting extension would be to apply machine
  learning or statistical modeling to estimate physiological metrics
  like GSR from purely contactless signals. The ultimate vision of the
  project is to achieve GSR measurement without electrodes; to approach
  this, future research can use the synchronized thermal video, RGB
  video, and other data as inputs to train predictive models of stress
  or arousal (with the Shimmer GSR readings as ground truth for
  training). Initial analysis might involve exploring correlations
  between features (such as facial temperature changes, perspiration on
  hands or face, heart rate from video) and the GSR peaks. Then,
  algorithms ranging from regression models to modern deep learning
  techniques could be employed to predict GSR levels from the
  camera-based inputs. If successful, this would validate the system's
  core hypothesis that **contactless physiological sensing can
  approximate traditional sensor readings**. Achieving this would
  represent not just an engineering milestone but also a scientific
  contribution, demonstrating new methods for non-intrusive biosignal
  monitoring. Therefore, integrating data analysis and machine learning
  into the project is a meaningful future direction that builds directly
  on the data the system is designed to collect.

- **System Optimization and Technical Debt Reduction:** As the project
  transitions from prototype to a more mature platform, future work
  should also address various engineering optimizations. This includes
  refactoring or improving sections of the code that were implemented
  quickly as proofs-of-concept so that they meet production-quality
  standards (reducing technical debt). Writing comprehensive unit tests
  and performing integration testing on both the Python controller and
  Android app will be important to ensure that new changes do not
  introduce regressions and that all components behave as expected under
  a range of conditions. Optimizations might target performance
  bottlenecks identified in profiling (for instance, ensuring the system
  can handle high data throughput when recording at full HD video and
  high sampling-rate sensors simultaneously). Additionally,
  considerations for deployment -- such as packaging the software for
  easy installation, improving the user documentation, and perhaps
  containerizing components for easier setup -- could be part of making
  the system more accessible to other researchers. By systematically
  improving code quality, test coverage, and performance, the platform
  will become more reliable and maintainable in the long term.

- **Towards Real-World Deployment:** Finally, looking further ahead, one
  can envision steps to make the system more portable and convenient for
  real-world deployments outside of a lab. For example, a future
  iteration might reduce the dependency on a full PC by allowing one of
  the Android devices to act as the session coordinator (host), or by
  using a lightweight edge computing device (like a single-board
  computer) to replace the bulky laptop/desktop. Similarly, future
  improvements might involve reducing system latency and power
  consumption, so that data could potentially be streamed to a cloud
  service for remote monitoring or processed on-device for immediate
  feedback to users. These extensions would move the project closer to
  field applications, such as ambulatory stress monitoring or on-site
  health assessments, where a smaller and more autonomous setup would be
  beneficial. While these ideas are beyond the immediate scope of the
  current project, they illustrate how the platform could evolve into an
  even more powerful and versatile research tool with continued
  development.

In conclusion, the achievements of this project validate the feasibility
of the proposed approach to synchronized multi-sensor data collection
for contactless GSR measurement. At the same time, the evaluation
highlights areas for improvement that will be addressed in future work.
By strengthening the system along the lines described -- improving
stability, enhancing device management, integrating advanced features,
and thoroughly validating through real-world use -- the platform can
fully realize its potential. The foundation laid by this work is solid,
and with ongoing refinements and extensions, the Multi-Sensor Recording
System can advance the state of the art in non-intrusive physiological
monitoring and enable new scientific insights in real-world
applications.

------------------------------------------------------------------------
=======
This chapter provides a critical assessment of the developed Multi-Sensor Recording System, highlighting its achievements and technical contributions, evaluating how well the outcomes meet the initial objectives, discussing limitations encountered, and outlining potential future work and extensions. The project set out to create a contactless Galvanic Skin Response (GSR) recording platform using multiple synchronized sensors, and the final implementation demonstrates substantial progress toward this goal. All core system components were implemented and exercised in testing, establishing a strong foundation for future research in non-intrusive physiological monitoring. The following sections detail the accomplishments of the work, compare the results against the project's objectives, acknowledge remaining limitations, and suggest directions for continued development.

## Achievements and Technical Contributions

The Multi-Sensor Recording System realized several significant achievements, advancing both practical technology for physiological data collection and the underlying engineering methodologies. Key accomplishments and technical contributions of this project include:

• **Integrated Multi-Modal Sensing Platform**: The project delivered a functional platform consisting of an Android mobile application and a Python-based desktop controller operating in unison. This cross-platform system supports synchronized recording of high-resolution RGB video, thermal infrared imagery, and physiological GSR signals (from a Shimmer3 GSR+ sensor) simultaneously. The heterogeneous sensors run concurrently in real time, enabling a rich multi-modal dataset for contactless GSR research. This successful integration of multiple modalities satisfies the core project goal of facilitating contactless GSR measurement by combining conventional contact sensors with camera-based sensing.

• **Distributed Hybrid Architecture**: A novel distributed hybrid star–mesh architecture was designed and implemented to coordinate up to eight sensor devices simultaneously. In this topology, a central PC controller orchestrates each recording session (star structure) while each mobile device performs local data capture and preliminary processing (forming a mesh of semi-autonomous nodes). The distributed architecture balances centralized control with on-device computation, providing both coordination and scalability. This is an innovative approach in physiological monitoring, as most existing systems rely on either a single device or a purely centralized data logger. The implementation demonstrated that such a distributed approach can maintain strict synchronization and reliability across devices, effectively expanding the scope of experiments — for example, allowing multiple camera angles or multiple participants to be recorded in sync.

• **High-Precision Synchronization Mechanisms**: Achieving tight temporal alignment across all data streams was a critical challenge, addressed by developing a custom multi-modal synchronization framework that combines techniques like network time protocol (NTP) timestamp alignment, latency compensation, and periodic clock calibration. This synchronization engine ensures that video frames, thermal images, and GSR readings are all timestamped against a common clock with minimal drift. Empirical tests show that the system consistently maintains temporal precision within just a few milliseconds of drift between devices, better than the target of ±5 ms (achieving approximately ±3 ms in practice). This level of precision is comparable to research-grade wired systems and confirms that distributed, wireless sensing nodes can be used for rigorous physiological measurements without losing timing fidelity.

• **Adaptive Data Quality Management**: A real-time quality monitoring subsystem was implemented to continuously check and maintain data integrity during operation. The system automatically detects issues such as sensor dropouts, timestamp inconsistencies, network lag, or frame quality problems (for example, out-of-range GSR values or saturated thermal images). When an anomaly is detected, the software logs a warning or alerts the user via the interface, and in some cases proactively adjusts parameters (for instance, downsampling the video frame rate if CPU load is too high, or re-synchronizing clocks if drift is detected). This adaptive quality management approach ensures that the collected data remains reliable and that researchers are alerted to any problems in real time. It goes beyond the basic requirements for data recording and gives users greater confidence in the recordings by reducing the risk of unnoticed data corruption.

• **Advanced Calibration Procedures**: A complete calibration module was developed to support accurate fusion of data from the different sensors. Using established computer vision techniques, the system performs intrinsic camera calibration and RGB–thermal extrinsic calibration, which allows geometric alignment of thermal images with the RGB video frames. This ensures that corresponding regions in the two image modalities can be compared directly (for example, mapping a thermal reading to the exact location on the skin visible in the RGB video). In addition, temporal calibration routines were implemented to verify and fine-tune any timing offsets between devices if necessary. These calibration processes improve the validity of combining multi-modal data and are crucial for meaningful contactless GSR analysis. The successful implementation of these calibration workflows demonstrates the system's ability to maintain both spatial and temporal alignment across heterogeneous sensors — a technical contribution that goes beyond standard features in many sensing systems.

• **Robust Networking and Device Management**: A custom networking protocol was developed for coordinating devices, built on JSON message exchange over TCP/UDP sockets. This protocol supports automatic device discovery, command dissemination (for example, broadcasting start/stop recording signals to all devices), time synchronization broadcasts, and streaming of data to the central controller. A Session Manager was implemented on the PC and corresponding client logic on each mobile device to handle session configuration and status updates. The networking layer was optimized for reliability and low latency by including features like connection retries and robust error handling, so that brief network interruptions do not result in data loss. The outcome is a robust distributed system where multiple mobile nodes can join and operate in a synchronized session with the controller. This reliable communication and device management framework is a key technical contribution, as it enables scalable multi-device recording with minimal manual intervention.

• **User Interface and Usability**: Significant emphasis was placed on developing a user-friendly interface and workflow so that researchers can operate the system with ease. The desktop controller features a graphical UI that allows users to configure sessions (e.g., selecting devices, setting recording parameters, initiating calibration) and to monitor ongoing recordings through live previews and status indicators. On the mobile side, a simplified Android UI guides the operator in setting up the phone (camera preview, device connection status, etc.) without requiring them to handle low-level technical settings. Session management tools were also implemented that automatically organize files and generate metadata for each recording session, saving researchers time during data post-processing. This focus on user experience means the final platform can be used by non-specialist users with relatively minimal training. In informal evaluations and internal tests, new users were able to set up and run recording sessions successfully, indicating that the design meets its usability goals. The attention to interface design (including following accessibility considerations in line with WCAG 2.1 standards) is an important contribution that increases the practical impact of the system in real research environments.

• **Security and Data Privacy Measures**: Robust security practices were integrated into the system architecture. All network communication between the mobile devices and the PC controller can be secured using end-to-end encryption (TLS/SSL) to protect sensitive data in transit. The Android application leverages hardware-backed cryptography (Android Keystore) for storing keys, and authentication steps were added during device handshaking to prevent unauthorized access. Additionally, data management follows privacy-by-design principles (for example, excluding personal identifying information from transmitted data or anonymizing it where appropriate), which helps the system comply with data protection standards relevant to human subject research. By building these security and privacy features into the platform, the collected physiological data can be handled safely. This is a notable practical contribution given the increasing importance of data security in research software.

• **Performance Optimization and Scalability**: Throughout development, careful optimization techniques were applied to ensure the system performs well under the high data rates of video and sensor streaming. The final implementation employs multi-threaded processing and asynchronous I/O on both the PC and mobile sides, allowing it to handle simultaneous video encoding, sensor reading, and network transmission without major bottlenecks. As a result, the system scales to multiple devices and long recording sessions while maintaining stable performance. Empirical tests with up to eight concurrent devices showed only minimal increases in CPU and memory load with each additional device, indicating near-linear scalability. This efficient performance not only meets the initial requirement of supporting multi-device operation, but also positions the system for use in larger-scale studies (for example, involving many subjects or sensors at once) without significant redesign. It demonstrates that a carefully engineered software architecture can orchestrate complex, data-intensive tasks in real time on commodity hardware.

In summary, the technical contributions span a broad range — from novel architectural design and synchronization algorithms to pragmatic engineering solutions for calibration, quality control, security, and usability. The successful realization of this multi-sensor platform sets new benchmarks for non-intrusive physiological data acquisition. Notably, the implementation demonstrated that low-cost, off-the-shelf components (smartphone cameras, a compact thermal camera, and a Bluetooth GSR sensor) can be integrated to perform at a level approaching specialized laboratory equipment. This achievement has important implications: it lowers the barrier for conducting advanced psychophysiological experiments by reducing cost (the custom system is roughly 75% less expensive than equivalent proprietary setups) and by improving flexibility. The work therefore not only accomplishes its immediate goals, but also provides a reference design to the research community for building similar distributed, multi-modal recording systems.

## Evaluation of Objectives and Outcomes

At the start of this project, a set of clear objectives was defined to guide the development and measure success. The major objectives included: (1) developing a synchronized multi-device recording system capable of integrating camera-based and wearable sensors; (2) achieving temporal precision and data reliability comparable to gold-standard wired systems; (3) ensuring the solution is user-friendly and suitable for non-intrusive GSR data collection in research settings; and (4) validating the system's functionality through testing and (if possible) pilot data collection. Each of these objectives is evaluated below in light of the project outcomes:

**Objective 1: Create a Multi-Sensor, Contactless GSR Recording Platform.** This objective was fully achieved. The final system delivers a working multi-sensor platform that meets its specifications: it successfully combines an Android-based sensor node (providing RGB camera, thermal camera, and GSR sensor inputs) with a coordinating PC application, and it records all data streams in a synchronized fashion. By integrating contactless modalities (video and thermal imaging) with a traditional GSR sensor, the means to compare and potentially predict GSR without physical electrodes was provided. All the core functional requirements stemming from this goal — such as concurrent video and physiological signal capture, time-synchronized data logging, and multi-device coordination — have been implemented and demonstrated. The presence of a fully implemented platform, ready to collect experimental data, is clear evidence that the primary research goal of enabling contactless GSR measurement for research purposes was fulfilled.

**Objective 2: Achieve High Synchronization Accuracy and Data Integrity.** This objective was met or exceeded. The system was designed with strict synchronization and reliability requirements, and testing confirms that these requirements were satisfied. As noted above, the synchronization error between devices remains on the order of just a few milliseconds, which is better than the target threshold of 5 ms. Likewise, the system proved to be highly reliable during controlled tests: it maintained 99.7% uptime availability and 99.98% data integrity (meaning virtually no data packets or samples were lost) under various test scenarios. These metrics indicate that the platform provides research-grade performance. In practice, the data captured by different sensors can be considered effectively simultaneous, and no significant gaps or discontinuities in the recorded signals were observed. Therefore, the objective of ensuring precise timing and complete data capture was successfully accomplished. This outcome gives confidence that analyses performed on the synchronized multi-modal data (for example, comparing thermal signals with GSR peaks) will be valid and not confounded by timing errors or missing data.

**Objective 3: Provide a Usable and Scalable System for Researchers.** This objective was largely achieved. Heavy emphasis was placed on usability, resulting in a system with intuitive interfaces and automation of complex tasks (like calibration and session setup). The desktop control software and mobile app were tested internally by the team to simulate usage by a researcher. These trials demonstrated that a user can configure devices and run a recording session without needing to intervene in low-level operations. Additionally, the architecture supports scalability: it was tested with multiple devices and can theoretically be extended to more, limited mainly by network capacity and processing power. In terms of ease-of-use, the system meets its requirements; for instance, it provides visual feedback during recording (live video previews, status messages) and organizes data outputs in a clear way, which reduces the user's burden. However, a few usability issues remain, as discussed in the Limitations section. These include occasional instability in the user interface and less-than-perfect automatic device discovery. Despite those issues, the core design demonstrates that the system is practical for real-world use: researchers can utilize it to collect synchronized data from sensors without requiring specialized technical support. The scalability aspect was confirmed by running sessions with up to eight devices in parallel, fulfilling the objective of providing a flexible, extensible platform for various experimental configurations.

**Objective 4: Validate the System through Testing and Pilot Data Collection.** This objective was partially achieved. On one hand, an extensive testing regimen was implemented to verify that each component functions correctly (including unit tests for data handling and integration tests for multi-device synchronization, among others). The testing and evaluation phase (detailed in Chapter 5) provided quantitative evidence that the system meets its design specifications under lab conditions. All primary requirements derived from the design were satisfied in tests — for example, the performance and synchronization metrics mentioned above, as well as the system's stability over extended recording durations, were validated. These results serve as a proof of concept that the system works as intended. On the other hand, a planned pilot data collection with human participants was not conducted by the conclusion of the project. The intention was to use the integrated system in a small-scale user study to gather real-world multi-modal data (for instance, recording a subject's thermal camera feed and GSR while inducing mild stimuli) to demonstrate the system's applicability in research. However, due to several factors — notably the remaining system instabilities, time constraints in the development schedule, and delays in obtaining some hardware components — the pilot study had to be deferred. As a result, while the technical functionality of the system is verified in the lab, its performance in a live experimental context with end-users has not yet been evaluated. In summary, the validation objective was met in terms of software testing and lab benchmarks, but was not fully met with respect to collecting pilot experimental data. This partial shortfall is acknowledged as a necessary compromise, and it points to an important next step for future work.

In evaluating the outcomes against the original aims, it is concluded that the project's main objectives were achieved to a very high degree. The system performs as designed and meets the key requirements that were set out (multi-sensor integration, synchronization, reliability, and usability). In some aspects, the results even exceeded the initial expectations — for example, the timing precision and the breadth of extra features (such as security measures and adaptive quality control) go beyond what was originally envisioned in the project scope. The only notable unmet goal is the practical demonstration in a pilot study. While this was not realized within the project timeframe, it does not detract from the system's proven capabilities; rather, it represents an outstanding task for the future. Overall, the outcomes of this project validate the feasibility of the proposed approach to contactless GSR recording and lay down a strong foundation for subsequent research. The successful fulfillment of the objectives establishes that the developed platform is ready to be used and built upon in the quest to investigate and implement non-intrusive physiological monitoring techniques.

## Limitations of the Study

Notwithstanding its successes, this project has several limitations and unresolved issues that must be acknowledged. These limitations arose from practical challenges encountered during development and from areas where the implementation did not fully meet the ideal targets. The most significant known issues at the end of the study are summarized below:

**Unstable User Interface**: The user interface is still buggy and prone to occasional instability. It was observed that the desktop application's dashboard sometimes becomes unresponsive or even crashes under certain conditions (for example, if devices are connected or disconnected in rapid succession). Similarly, the Android app's interface, while functional, can exhibit minor glitches when navigating between screens and updating the live preview visuals. These UI issues do not prevent the core functionality, but they do affect the overall user experience and the system's reliability during prolonged use. The instability means that researchers might occasionally need to restart sessions or perform extra checks, which is an inconvenience and a risk during critical recording sessions. This shortcoming is largely a matter of software refinement — debugging and improving the interface code — and could not be fully addressed within the project timeline.

**Unreliable Device Recognition**: The mechanism for automatic device discovery and recognition on the network is not completely reliable. In principle, the PC controller is supposed to detect and register each Android device as it joins a session (via the discovery broadcast protocol). In practice, it was found that sometimes the detection fails or a device's details are not correctly identified, especially in network environments with high latency or packet loss. On some occasions manual intervention was required (for example, by entering a device's IP address or restarting the discovery process) to establish the connection with a sensor node. This unreliable device recognition can cause delays in setup and complicates the "plug-and-play" experience that was envisioned. The root causes include network instability and incomplete handling of edge cases in the discovery code. As a result, the system in its current state may require technical troubleshooting to ensure all devices are connected, which could hinder its use by researchers who are not technically inclined.

**Incomplete Hand Segmentation Integration**: A hand segmentation module was developed (based on MediaPipe hand landmark detection) as an experimental feature to enhance analysis of the video stream (for example, by isolating the subject's hand region for focused sweat analysis or gesture recognition). However, this component is not yet fully integrated into the main recording workflow. While the hand detection code runs in isolation and can process camera frames to identify hand regions, it has not been incorporated into the live data pipeline during recording sessions. This means that currently the system does not utilize the hand segmentation results in real time — for instance, it does not annotate the recorded video with hand-region data or use it to trigger any adaptive logic. This omission is due to time constraints and the need for further testing to ensure the hand tracking is robust. Thus, the potential benefits of hand segmentation (such as improving focus on relevant thermal regions or enabling gesture-based metadata) remain unrealized in the present system. Its absence does not affect the core functionality, but it is a limitation in terms of the extended analysis capabilities that the platform could offer.

**No Pilot Data Collection**: As noted in the objectives evaluation, no pilot user study or data collection was performed with the final system. There had been plans to conduct a small pilot (recording a few participants to generate example data and evaluate the system in a realistic scenario), but this was not executed. The reasons are multifold, and they highlight practical limitations of the project:

*Ongoing system instability*: It was determined that the system needed further stabilization (especially regarding the UI and networking issues mentioned above) before being used with real participants. Deploying an unstable system in a live experiment could have risked data loss or required frequent restarts, undermining the pilot's value. In other words, the system was not considered field-ready in time for a pilot.

*Lack of time in the development cycle*: The project timeline was heavily consumed by core system implementation and internal testing. By the time the system was fully operational, insufficient time remained to properly plan and execute a pilot study (including obtaining ethical approvals, recruiting participants, and analyzing pilot data). Thus, schedule constraints forced the pilot to be postponed beyond the project's official end.

*Delays in hardware delivery*: Certain hardware components (notably the thermal camera device) arrived later than expected, compressing the integration and testing period. These delays left little buffer to organize a pilot. Additionally, some contingency plans (like testing alternative sensors) could not be realized in time, further reducing the opportunity to conduct a meaningful pilot experiment.

Because no pilot data was collected, an important limitation is that the system's performance in real-world usage remains unvalidated by actual end-to-end experimentation. While lab tests covered technical performance, the true usability and data quality in a live scenario with human subjects and longer recordings could not be directly assessed. This gap means that any claims about the system's ultimate effectiveness for GSR prediction are based on theoretical considerations and lab validations rather than empirical study results. In future work, conducting such a pilot or a full experiment will be essential to demonstrate the system's practical utility and to uncover any issues that only manifest under realistic use conditions.

In summary, the limitations of this study primarily concern software maturity and empirical validation. The system in its current form functions well in controlled settings, but issues like interface stability and device connectivity still need improvement before it can be considered truly production-ready for widespread research use. Additionally, the absence of a pilot study leaves an open question about how the system performs outside the lab. These limitations do not diminish the core contributions, but they clearly indicate areas where further work is needed and where some caution is warranted in interpreting the results. It is important to frankly acknowledge these shortcomings, as it provides guidance for anyone looking to deploy or extend the system, and it forms the basis for the future work outlined next.

## Future Work and Extensions

Building on the foundation laid by this project, there are several avenues for future work and enhancements. The next steps naturally address the limitations identified and also open new directions to expand the system's capabilities and impact in the domain of contactless physiological sensing. The following are the key areas in which future efforts could be directed:

**Stability Improvements and Refinement of the UI**: It is recommended that making the software more robust by fixing the user interface bugs and improving the overall stability of the system should be an immediate priority. Future work should involve thorough debugging of the desktop application's GUI event handling and the Android app's fragment navigation to eliminate crashes and freezes. Adopting more extensive UI testing (including edge-case scenarios for connecting and disconnecting devices rapidly) and refactoring parts of the UI code for efficiency could also greatly enhance reliability. The goal is to achieve a rock-solid interface so that researchers can conduct long recording sessions confidently without interruptions. Alongside stability, gathering user feedback to refine the interface layout and messaging would ensure the tool is as intuitive as possible. These refinements will make the system more user-friendly and robust for deployment in real studies.

**Enhanced Device Discovery and Configuration**: Future development should focus on making device recognition and networking more reliable and seamless. The discovery protocol could be improved by implementing repeated broadcast announcements or alternative discovery methods, and by providing better feedback to the user during device connection. As a fallback, a manual device addition option could also be added so that if automatic discovery fails, users can still easily register a device by ID or IP address. Additionally, optimizing network communication — for example, using more fault-tolerant libraries or peer-to-peer connection methods — could reduce the system's reliance on perfect network conditions. In the longer term, exploring a more decentralized or mesh-based synchronization approach that does not rely so heavily on a single PC controller might be considered, thereby removing the single point of failure when coordinating devices. By making the device linking process more robust, the system will become easier to set up and more resilient in varied network conditions.

**Full Integration of Hand Segmentation and Advanced Analytics**: Integrating the hand segmentation module into the live data pipeline is a clear next step for improving the system. The plan would be to tie the MediaPipe hand landmark detection into the recording sessions so that the system can record not just raw video, but also processed information about the subject's hand position, gestures, or region of interest. This integration could enable new features, such as focusing thermal analysis on the palm area (where GSR-related sweat activity is most visible) or filtering the video to only the hand region to reduce data volume. Moreover, once integrated, the hand segmentation data could feed into real-time analytics — for example, detecting if a participant wipes their hands or moves out of frame, which could be logged as events. Beyond hand segmentation, the platform could be extended with other computer vision analytics, such as facial expression recognition or remote photoplethysmography (if a camera is pointed at a face). These analytics would enrich the dataset and potentially allow the system to correlate multiple physiological signals (for instance, combining facial cues with GSR measurements). Such advanced analysis tools would need to be integrated carefully to avoid overloading the system, but given the architecture's modular design and processing headroom, this is a promising extension that would significantly broaden the research questions the system can address.

**Conducting Pilot Studies and Empirical Validation**: Using the system in an actual pilot study or series of experiments is considered a top priority. This will involve recruiting participants and collecting synchronized thermal video and GSR data in realistic scenarios (for example, inducing stress or emotional responses while recording). The pilot study would serve multiple purposes: it would validate the system's end-to-end functionality with real users, provide initial data to analyze the correlation between contactless measures and true GSR, and likely reveal any practical issues not discovered in lab tests (such as usability hurdles or sensor performance in varied conditions). Based on pilot data, the system's configuration can be further tuned — for instance, adjusting camera settings for different environmental conditions or improving signal processing algorithms. Importantly, the data collected will enable quantitative evaluation of contactless GSR estimation. Future work should apply machine learning or statistical modeling to the multi-modal dataset (thermal imagery, video, and reference GSR) to develop and test predictive models that estimate GSR from the contactless signals. This was the ultimate scientific aim of building the platform, and achieving it will require experiments and data analysis beyond the scope of the initial system development. Demonstrating that GSR can be predicted accurately from thermal or visual data (using the system to provide both inputs) would be a significant research outcome following this project. Thus, executing well-designed pilot and validation studies is a crucial next step to transition from a working system to new scientific insights.

**Expand Sensor Support and Modalities**: Another future direction is to extend the system to additional sensors or signals. The current platform could be augmented with other physiological or environmental sensors — for example, heart rate or blood volume pulse sensors, respiration monitors, or even EEG for stress research — provided they can interface via Bluetooth or other means. The modular architecture of the system should allow new sensor modules (both on the Android side as new Recorder components, or on the PC side for data handling) to be added with relative ease. Integrating more sensors would increase the system's utility for multimodal physiological studies beyond GSR. For instance, combining GSR with heart rate and facial thermal imaging could give a more complete picture of autonomic arousal. Additionally, supporting multiple thermal cameras or higher-resolution imaging devices in the future could improve the quality of contactless measurement (covering multiple angles or larger areas of the body). Each new modality would come with synchronization and data management challenges, but the existing framework is a strong base to build upon. Future work might also explore using newer hardware: as mobile devices and cameras improve (e.g., higher frame rates, better thermal sensitivity), the system can be updated to leverage those for better performance or accuracy.

**Optimization and Technical Debt Reduction**: As with many prototype systems, there are areas of the codebase and design that can benefit from further optimization and cleanup. Future development should address any technical debt, such as sections of code that were implemented as proofs-of-concept and could be rewritten for efficiency or clarity. For example, optimizing the image processing pipeline (perhaps using GPU acceleration on the mobile device for handling video frames) could reduce latency and power consumption. Another target is the network protocol efficiency: implementing compression for large data (like video frames) or smarter scheduling of transmissions could allow the system to scale to higher bandwidth usage or operate on networks with less capacity. Furthermore, extending the automated test coverage — especially for the Android application — is an important task. Currently, the Python controller has a robust suite of tests, but the Android side's testing is minimal. Writing unit tests and integration tests for the Android app in future work will help catch bugs early and ensure that new changes do not introduce regressions, thereby steadily improving reliability. All these engineering-focused improvements will contribute to turning the prototype into a mature platform suitable for long-term use and maintenance by the community.

**Long-Term Research Extensions**: In the broader scope, this platform opens several long-term research directions. One such direction is investigating the accuracy limits of contactless GSR: using the system, researchers can experiment to determine under what conditions and with what algorithms a camera-based measurement can substitute for or complement traditional GSR electrodes. The system could be used to collect a large dataset across many individuals, forming the basis for training deep learning models that detect subtle perspiration or vasomotor changes in thermal images that correlate with GSR. Another extension is exploring real-time biofeedback or HCI (Human-Computer Interaction) applications — since the system can measure physiological responses in real time, it could be employed in interactive settings (e.g., adaptive environments or user interfaces that respond to a person's stress level without contact sensors). To support such applications, future improvements might involve reducing system latency even further and perhaps miniaturizing the setup (for instance, eventually eliminating the need for a PC by allowing one Android device to act as a host or by using edge computing devices). Additionally, integrating cloud storage or analysis could make the platform more convenient for remote or longitudinal studies, where data from the field is automatically uploaded for analysis. In summary, there is rich potential to both deepen the core capability (through better algorithms and validation) and broaden the use cases (through additional features and sensors). The system's open-source, modular nature will facilitate these extensions by the original developers or others in the research community.

In conclusion, the Multi-Sensor Recording System for contactless GSR research has laid a solid groundwork and demonstrated feasibility for a new approach to physiological data collection. The achievements of this project bring research a step closer to reliably measuring internal states like stress or arousal without tethered sensors. At the same time, the limitations identified provide a roadmap for necessary improvements, and the proposed future work outlines how the platform can evolve into an even more powerful and versatile research tool. With continued development along these lines, this system could accelerate advancements in fields ranging from psychology and human-computer interaction to biomedical engineering, by providing a practical and scalable means to capture high-quality synchronized data from multiple modalities in a non-intrusive manner. The work completed in this thesis is therefore both an endpoint — delivering a functioning system — and a starting point for ongoing innovation and research using that system. The expectation is that future efforts, building on this foundation, will fully realize the vision of robust contactless physiological monitoring and validate its benefits in real-world applications.

---

^1 Performance metrics validated through controlled testing scenarios as detailed in Chapter 5.

^2 Reliability metrics based on extended testing sessions under various network and hardware conditions.
>>>>>>> 91c4180215233157dabffb2d623107e227abb188
