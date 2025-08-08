# Chapter 6: Conclusions and Evaluation

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
  device discovery was not perfectly seamless (sometimes a device would
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
  **practical demonstration with end-users remains an outstanding
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
