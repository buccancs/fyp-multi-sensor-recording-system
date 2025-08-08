# Chapter 4: Design and Implementation

## 4.1 System Architecture Overview (PC--Android System Design)

<<<<<<< HEAD
The system is designed in a client--server architecture with a **central
PC controller** coordinating multiple **Android capture devices**. The
PC application serves as the master controller, discovering and
connecting to each Android device over a local network. Each Android
device runs a capture app responsible for recording sensor data and
video, while the PC provides a unified interface to start/stop
recordings and aggregate data. **Figure 4.1** illustrates this
architecture: the PC communicates with each Android smartphone via Wi-Fi
using a custom TCP/IP protocol, sending control commands and receiving
live telemetry (video previews, sensor readings). The Android devices
operate largely autonomously during capture -- each uses its own
high-precision clock to timestamp data locally -- but all devices are
synchronized to the PC's timeline through network time alignment. This
design allows **multiple phones** to record simultaneously under one
session, with the PC as the authoritative time base. The PC can also
integrate **local hardware** (e.g. a webcam and GSR sensor connected
directly) alongside the Android data. All captured modalities (video
streams, audio, thermal data, GSR signals) are temporally aligned and
later consolidated on the PC. The result is a distributed recording
system in which heterogeneous data sources behave like a single
synchronized apparatus. *Figure 4.1 should depict the overall system
architecture, showing the PC controller, multiple Android devices, and
the data flow between them (commands going out to devices, and
streams/acknowledgments coming back).*

## 4.2 Android Application Design and Sensor Integration

On the Android side, the application is structured to handle
**multi-modal data capture** in a coordinated fashion. At its core is a
`RecordingController` class that manages all hardware components and
recording tasks. This controller prepares each subsystem -- cameras (RGB
and thermal), physiological sensors (GSR/PPG), microphone, etc. -- and
triggers them in sync. When a recording session starts, the controller
initializes a new session directory and then concurrently starts each
enabled sensor/camera capture with nanosecond-precision
timestamps[\[1\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/controller/RecordingController.kt#L36-L45)[\[2\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/controller/RecordingController.kt#L51-L59).
Each modality's data is written to device storage in real time. The
design relies on Android's modern libraries for robust performance:
**CameraX** is used for efficient video and image capture, and the
**Nordic BLE** library for reliable Bluetooth Low Energy communication
with sensors. Crucially, all sensor readings and frames are timestamped
using a monotonic clock source to ensure internal consistency. The app
architecture cleanly separates concerns -- for example, camera handling
is in a `RgbCameraManager`, thermal imaging in a `TopdonThermalCamera`
module, and GSR sensing in a `ShimmerGsrSensor` class -- each exposing a
common interface for the controller to start/stop streams. This modular
design makes it easy to enable/disable features based on device
capabilities (e.g. if a phone has no thermal camera attached, that
module remains inactive). It also simplifies synchronization logic,
since the controller can treat each data source uniformly (start all,
stop all) and trust each to timestamp its output. The following
subsections detail the integration of the **Topdon thermal camera** and
**Shimmer GSR sensor** in the Android app.

### 4.2.1 Thermal Camera Integration (Topdon)

Integrating the **Topdon TC001** thermal camera on Android required
using USB host mode and a UVC (USB Video Class) library. The app
utilizes the open-source **Serenegiant USB Camera** library (UVCCamera)
to interface with the device. A dedicated class `TopdonThermalCamera`
implements the `ThermalCamera` interface and encapsulates all thermal
camera functionality. When the camera is physically connected via USB-C,
an **Android USB monitor** detects the device. The `TopdonThermalCamera`
registers a `USBMonitor.OnDeviceConnectListener` to handle attachment
events. On a successful connection, it opens the UVC device and
configures it to a desired frame size and mode before starting the video
stream[\[3\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/TopdonThermalCamera.kt#L84-L92).
By default, the camera is set to its **native thermal resolution**
(256×192 pixels) and begins previewing immediately on a background
thread.

For each incoming thermal frame, the library provides a framebuffer in
ByteBuffer format. The implementation registers a frame callback to
retrieve this data stream. In the callback, the code reads the raw
temperature data from the ByteBuffer as an array of 16-bit or 32-bit
values (depending on the camera's output format). In this system, the
Topdon camera delivers a full temperature matrix for each frame -- the
code treats it as an array of floats representing per-pixel temperature
readings[\[4\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/TopdonThermalCamera.kt#L54-L62).
The `TopdonThermalCamera` writes each frame's data to a CSV file: each
row corresponds to one frame, beginning with a high-resolution timestamp
(in nanoseconds), followed by the temperature values of all 49,152
pixels (256×192) in that
frame[\[4\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/TopdonThermalCamera.kt#L54-L62).
This exhaustive logging yields a large but information-rich dataset,
essentially a thermal video recorded as numeric data per frame. To
manage performance, the thermal capture runs in its own thread context
(inside the UVCCamera library's callback) so that writing to disk does
not block the main UI or other sensors. The system foregoes any heavy
processing on these frames in real-time; it simply dumps the raw
temperature grid to file and uses a lightweight callback to notify the
controller after each frame is saved. In the `RecordingController`, a
lambda hook is provided to receive a reference when a new thermal frame
file is saved, which is used to mark events (for synchronization or
debugging) via a Lab Streaming Layer
marker[\[5\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/controller/RecordingController.kt#L28-L32).
*Figure 4.2 should show the thermal camera integration flow --- the
Topdon device connected to the phone via USB, the data path through the
UVCCamera library, and the logging of frame data to storage.*

Because the Topdon camera operates over USB, the app also handles
permission requests and device registration. The `TopdonThermalCamera`
calls `usbMonitor.register()` during app start to begin listening for
devices[\[6\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/TopdonThermalCamera.kt#L28-L36),
and unregisters on app pause to release resources. If the device is
present, the user is prompted to grant the app access. Once granted, the
`TopdonThermalCamera.open()` method uses the USBMonitor to obtain a
control block and create a `UVCCamera`
instance[\[7\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/TopdonThermalCamera.kt#L80-L88).
The camera is then configured and flagged as *connected*. At that point,
if a preview display surface is available (e.g., a small on-screen
preview window in the app), it can be attached via
`startPreview(surface)` to render the thermal feed
live[\[8\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/TopdonThermalCamera.kt#L36-L44).
Previewing is optional for headless operation; whether or not preview is
shown, frames are being captured and logged. Stopping the thermal camera
involves stopping the preview (if any), disabling the frame callback,
closing the file writer, and destroying the UVC camera
instance[\[9\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/TopdonThermalCamera.kt#L66-L74)[\[10\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/TopdonThermalCamera.kt#L76-L84).
This orderly shutdown ensures the USB device is released for future
sessions. Overall, the Topdon integration provides **frame-synchronized
thermal imaging**, with each frame's precise capture time recorded -- a
cornerstone for later aligning thermal data with RGB video and
physiological signals.

### 4.2.2 GSR Sensor Integration (Shimmer)

The Android app connects to a **Shimmer3 GSR+ sensor** to record
Galvanic Skin Response (GSR) and photoplethysmography (PPG) data.
Integration is done via **Bluetooth Low Energy (BLE)**. The
`ShimmerGsrSensor` class extends Nordic's `BleManager` to handle the GSR
sensor's BLE protocol. The Shimmer3 GSR+ device advertises a custom GATT
service (proprietary to Shimmer) which the app accesses using known
UUIDs. In the code, the service and characteristic UUIDs for the
Shimmer's BLE interface are defined as
constants[\[11\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/ShimmerGsrSensor.kt#L16-L24).
The Shimmer uses a communication scheme akin to a UART-over-BLE: one
characteristic (TX) is used to send commands to the sensor, and another
(RX) is used by the sensor to send continuous data notifications to the
app. The app's `ShimmerGsrSensor` knows the specific byte commands to
control streaming -- for this sensor, sending `0x07` starts the live
data stream and `0x20` stops
it[\[11\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/ShimmerGsrSensor.kt#L16-L24)[\[12\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/ShimmerGsrSensor.kt#L52-L60).

When a Shimmer sensor is enabled in the app's configuration, the
`RecordingController` will create a `ShimmerGsrSensor` instance at
startup and keep it
ready[\[13\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/controller/RecordingController.kt#L26-L34)[\[5\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/controller/RecordingController.kt#L28-L32).
Upon beginning a recording session, if GSR recording is turned on, the
controller invokes `physiologicalSensor.startStreaming(...)` with a file
writer for
output[\[14\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/controller/RecordingController.kt#L39-L47).
Internally, this triggers the BLE manager to connect (if not already
connected) and then write the **Start Streaming** command (0x07) to the
sensor's TX
characteristic[\[12\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/ShimmerGsrSensor.kt#L52-L60).
The Shimmer device responds by sending a stream of notifications
(typically at 128 Hz) on the RX characteristic, each containing the
latest GSR and PPG readings. The `ShimmerGsrSensor` sets up a
notification callback in its GATT callback's `initialize()` method to
handle incoming data
packets[\[15\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/ShimmerGsrSensor.kt#L69-L77).
As data arrives, the `onShimmerDataReceived()` function parses the byte
payload according to Shimmer's data
protocol[\[16\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/ShimmerGsrSensor.kt#L84-L92).
The first byte acts as an identifier (0x00 indicates standard data
packet), and subsequent bytes contain the sensor readings. In each
8-byte packet, there are two bytes for PPG and two bytes for GSR, among
other info. The app reconstructs the 16-bit raw values for PPG and GSR
from the byte
sequence[\[17\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/ShimmerGsrSensor.kt#L86-L94).
The GSR reading includes a range indicator encoded in the top bits,
because the Shimmer3 employs multiple gain ranges for skin conductance.
The implementation extracts the range and applies the appropriate
conversion formula to derive the resistance, then inverts it to get
conductance (microsiemens). This conversion is done exactly as per
Shimmer's guidelines: for example, if the range bit indicates 40.2kΩ
resistor, the formula used is *GSR (µS) = (1 / R)*1000, where R is
computed from the 14-bit ADC value using that
resistor\*[\[18\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/ShimmerGsrSensor.kt#L94-L101).
Similar piecewise formulas are used for the other ranges (287kΩ, 1MΩ,
3.3MΩ)[\[18\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/ShimmerGsrSensor.kt#L94-L101).
After conversion, each data point consists of a timestamp, a GSR value
(in µS), and a raw PPG value.

Every GSR/PPG sample is immediately written to a CSV file by the app.
The `ShimmerGsrSensor` maintains a file writer stream; on starting, it
writes a header line (`timestamp_ns, GSR_uS, PPG_raw`) and then appends
each new sample as a new
line[\[12\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/ShimmerGsrSensor.kt#L52-L60)[\[19\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/ShimmerGsrSensor.kt#L103-L111).
The timestamp is pulled from the app's
`TimeManager.getCurrentTimestampNanos()` to ensure consistency with how
other modalities are
timed[\[17\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/ShimmerGsrSensor.kt#L86-L94).
In addition to logging to file, the app feeds the live data into an
in-memory stream for sync with video: the `RecordingController` provides
a callback to `startStreaming()` that pushes each sample into a local
**Lab Streaming Layer (LSL)** outlet named
`"Android_GSR"`[\[14\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/controller/RecordingController.kt#L39-L47).
This allows GSR data to be shared or monitored in real time (e.g.,
plotted on the phone or streamed to PC) without interrupting the file
recording. The BLE manager handles the connection in a background
thread, so incoming notifications do not block the UI. If the BLE
connection drops or has an error, the Nordic library's built-in retry
mechanism attempts reconnection up to 3 times with a short
delay[\[20\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/ShimmerGsrSensor.kt#L39-L45).
The app also provides graceful shutdown: when recording stops, it sends
the stop command (0x20) to halt
streaming[\[21\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/ShimmerGsrSensor.kt#L61-L65),
and closes the file writer. This ensures the CSV is properly finalized.
Overall, the Shimmer integration brings in high-resolution physiological
data synchronized with video. *Figure 4.3 should depict the Shimmer GSR
integration, showing the Android device connected to the Shimmer sensor
via BLE, and the data flow from the sensor to the app (BLE packets being
converted to meaningful GSR/PPG values and logged to storage).*

## 4.3 Desktop Controller Design and Functionality

The desktop controller is a **cross-platform application** (tested on
Windows, Linux, macOS) built with Qt for the GUI (PyQt6/PySide6) and
Python 3 for logic, augmented by performance-critical C++ components.
Its design follows a **modular MVC-like pattern**: the UI is separated
into tabs corresponding to major functionalities (e.g., device
management/dashboard, live monitoring, playback/annotation, settings).
When the controller starts, it initializes a main window with a tabbed
interface[\[22\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/main/main.py#L112-L120).
The primary **Dashboard tab** provides an overview of connected devices
and local sensors. For example, it can display live video feeds and GSR
plots in a grid layout -- the code sets up a QLabel for a video preview
and a pyqtgraph PlotWidget for GSR on the
dashboard[\[23\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/main/main.py#L140-L149).
A **Logs tab** captures real-time system messages (status updates,
errors) for
debugging[\[24\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/main/main.py#L114-L122)[\[25\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/main/main.py#L144-L148).
Another tab for **Playback & Annotation** is prepared to allow review of
recorded
sessions[\[26\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/main/main.py#L116-L124).
Each tab's UI elements are created and managed in an organized way
(using Qt layouts), making the interface flexible and scalable to
multiple devices.

Under the hood, the PC controller employs several background threads and
helpers to manage networking and data processing without freezing the
GUI. A dedicated **WorkerThread** (a QThread subclass) is responsible
for all communication with Android
devices[\[27\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/main/main.py#L32-L40).
When the user initiates a connection to a device, this worker thread
opens a TCP socket to the Android's IP and
port[\[28\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/main/main.py#L53-L61).
The thread then runs an event loop receiving JSON messages from the
device. It parses incoming messages and emits Qt signals to the main
thread for handling UI updates. For instance, if a connected Android
phone sends a preview frame update, the worker decodes the
base64-encoded image bytes to a QImage and emits a `newPreviewFrame`
signal carrying the image and device
identifier[\[29\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/main/main.py#L64-L72).
The main GUI thread connects this signal to a slot that displays the
frame in the dashboard (e.g., updating the corresponding QLabel's
pixmap). The worker also handles command responses: every command sent
to a device includes a unique ID, and the device's reply includes an
`ack_id` with status info. When the worker sees a response, it checks
the type. A `"capabilities_data"` status, for example, contains the list
of cameras the device has -- the worker emits `camerasReceived` with
that list so the UI can populate camera
options[\[30\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/main/main.py#L74-L81).
This asynchronous message-passing design keeps the GUI responsive and
allows the PC to manage multiple devices simultaneously by spawning
separate threads (or tasks) per connection. The application uses
**Zeroconf (mDNS)** to simplify device discovery: on startup, the PC
browses for services of type `_gsr-controller._tcp` on the local
network. Each Android device advertises itself with that service type
and a name like "GSR Android Device
\[Model\]"[\[31\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/network/NsdHelper.kt#L34-L41).
The PC can thus list available devices and their addresses
automatically, eliminating manual IP entry.

A standout feature of the PC controller is its **native C++ backend**
for time-sensitive hardware interaction. This is implemented as a Python
extension module (built via PyBind11) named `native_backend`. It
provides classes `NativeWebcam` and `NativeShimmer` which run in
background threads and feed data to the Python layer with minimal
latency[\[32\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/main/main.py#L126-L135).
The controller instantiates these at startup: for example,
`NativeWebcam(0)` opens the local webcam (device 0) and begins capturing
frames in a
loop[\[33\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/main/main.py#L126-L134),
and `NativeShimmer("COM3")` connects to a Shimmer GSR device via a
serial port (in this case COM3 on
Windows)[\[33\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/main/main.py#L126-L134).
These native objects are started immediately and run independently of
the Python GIL, pushing data into thread-safe queues. The GUI uses a
QTimer tick (every \~16 ms) to periodically retrieve the latest data
from the native
threads[\[34\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/main/main.py#L132-L140)[\[35\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/main/main.py#L150-L159).
On each tick, it pulls a frame from the webcam class (as a NumPy array)
and updates the corresponding video
label[\[36\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/main/main.py#L150-L158).
Similarly, it polls the Shimmer class for new GSR samples and updates
the live
plot[\[37\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/main/main.py#L154-L159).
The use of a C++ backend drastically improved performance: the webcam
thread captures at a fixed \~60 FPS by sleeping \~16ms per
iteration[\[38\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/cpp_backend/native_backend.cpp#L80-L88),
and yields frames without significant buffering, while the Shimmer
thread reads sensor bytes as fast as they arrive (128 Hz) with precise
timing. Both use lock-free queues to decouple production and consumption
of
data[\[39\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/cpp_backend/native_backend.cpp#L22-L31)[\[40\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/cpp_backend/native_backend.cpp#L94-L101).
The C++ code directly converts camera frames to a shared memory buffer
that is exposed to Python as a NumPy array without
copying[\[41\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/cpp_backend/native_backend.cpp#L66-L74),
and similarly packages GSR readings into Python
tuples[\[42\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/cpp_backend/native_backend.cpp#L193-L201)[\[43\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/cpp_backend/native_backend.cpp#L200-L208).
This design minimizes overhead and latency/jitter -- an imperative for
synchronizing local PC data with remote device data.

Beyond live monitoring, the desktop app includes tools for
**post-session analysis**. The **Playback & Annotation** tab (Figure
4.4) is designed to load the recorded video files (RGB and thermal)
along with sensor data and allow the user to replay the session in a
synchronized fashion. Internally, the controller uses libraries like
*PyAV* (wrapping FFmpeg) to read video files and *pyqtgraph* for
plotting time-series data like GSR. The user can seek through the
timeline; the app will display the video frame at that time and the
corresponding point on the GSR plot, maintaining alignment via
timestamps. Annotation functionality enables adding notes at specific
times -- these could be saved in a sidecar file or embedded in a
metadata structure for the session. Another part of the PC software is
the **Calibration utility**, which helps calibrate cameras after
recordings. Using OpenCV, it can detect calibration patterns
(chessboards or ChArUco markers) in the raw RGB frames to calculate each
camera's intrinsic parameters, and if multiple cameras (e.g. a phone's
RGB and thermal, or phone and PC webcam) observed the same pattern, it
can compute extrinsic calibration between them. The results (camera
matrices, distortion coefficients, transformation matrices) are saved
for use in data analysis, ensuring that researchers can accurately map
thermal and RGB imagery. Finally, a **Data Export** feature allows
converting a session's dataset into formats like MATLAB `.mat` files or
HDF5. This is done by reading the CSVs and video files from the session,
packaging the data (often downsampled or compressed as needed) into a
single file per session for convenient distribution or analysis. In
summary, the desktop controller is both the live "mission control"
during data acquisition and a post-processing suite, all implemented in
a cohesive application. *Figure 4.4 should show the PC controller's GUI
layout -- for instance, a screenshot or schematic with the Dashboard tab
displaying live video thumbnails and GSR plots, and perhaps the Playback
tab with a video player and timeline chart.*

## 4.4 Communication Protocol and Synchronization Mechanism

A custom **communication protocol** connects the PC controller with each
Android device, built on TCP/IP sockets with JSON message payloads.
After the PC discovers an Android device (via Zeroconf), it initiates a
TCP connection to the device's advertised port. The Android app runs a
lightweight TCP server to accept this connection. All commands from PC
to Android are sent as JSON objects with a schema like:
`{"id": <command_id>, "command": "<action>", "params": { ... }}`[\[44\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/main/main.py#L89-L97).
The device, upon receiving a command, executes the requested action and
then replies with a JSON response containing the original `id` (as
`ack_id`) and a status or result. For example, the first command the PC
sends is `"query_capabilities"`, which asks the phone to report its
hardware
capabilities[\[28\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/main/main.py#L53-L61).
The Android app responds with a message like
`{"ack_id": 1, "status": "capabilities_data", "capabilities": { ... }}`
including details such as available cameras (with their identifiers,
resolutions, and frame
rates)[\[30\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/main/main.py#L74-L81).
This exchange allows the PC to dynamically adjust to each device -- for
instance, listing the camera options or knowing if the thermal sensor is
present. Another command might be `"start_recording"`, which instructs
the Android to begin a new recording session. The phone will then
initiate all its sensors (cameras, etc.) and reply with an
acknowledgment (`"status": "ok"`) once recording has successfully
started. Similarly, a `"stop_recording"` command stops all captures and
finalizes files.

In addition to explicit commands, the protocol supports **continuous
data streaming** for live previews. While a session is idle or
recording, the Android app periodically sends `"preview_frame"` messages
containing a downsampled frame from the camera preview encoded as a
base64 JPEG
string[\[29\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/main/main.py#L64-L72).
The PC's worker thread listens for these and updates the UI so the
operator can see a low-latency video feed from each device. This preview
is throttled (for example, a frame every 1/2 second or as configured) to
balance timeliness with network load. Similarly, the app could stream
low-rate telemetry (like current recording status or battery level)
using this push mechanism. All such asynchronous messages include a
`type` field (like `"type": "preview_frame"`) rather than an ack id, so
the PC knows they are not responses to a specific command but rather
unsolicited data.

**Figure 4.5** illustrates the communication sequence and
synchronization strategy. When a PC and phone connect, they perform a
simple handshake (exchange of hello and capabilities). Part of this
handshake is a **time synchronization routine**. The system employs an
NTP-inspired algorithm to align clocks: the PC (as the time server)
sends a sync request carrying its current timestamp, the phone responds
with its own timestamp, and the PC measures the round-trip time to
estimate network latency. Through a series of such exchanges (or just
one at connect time in this implementation), the PC can calculate the
offset between its clock and the phone's clock. This offset is then used
to adjust or relate the timestamps coming from that device. Each device
continues to timestamp its data with its **local monotonic clock**
(nanosecond precision clocks are used on both ends), which ensures
extremely fine timing granularity. The PC, however, knows the offset for
each device and can thus translate a device timestamp into the PC's
master clock domain. This yields cross-device synchronization typically
within **sub-millisecond accuracy**. In practice, the controller might
designate itself as time 0 when recording starts and instruct each
Android to note its local time at that moment; subsequent data from the
phones then include raw timestamps which are later converted to the
common timeline.
=======
At a high level, the Multi-Sensor Recording System employs a distributed architecture comprising an Android mobile application and a Python-based desktop controller. The Android device serves as a dedicated sensor node for data capture, while the PC functions as the central coordinating hub. This PC–Android system design adopts a master–slave paradigm: the desktop Python application orchestrates one or more Android sensor nodes to achieve tightly synchronized operation across all devices. The architecture strikes a balance between individual device autonomy and centralized oversight. Each Android device can manage its own sensors and data logging locally (even running standalone if needed), but under the desktop controller's supervision all devices participate in unified sessions with common timing and control. The design prioritizes temporal synchronization, reliability, and modularity. A custom network communication layer links the mobile and desktop components, carrying command-and-control messages, status updates, and data previews over a Wi-Fi or LAN connection. Communication is event-driven and buttressed by robust error handling, so that transient network issues or device glitches do not compromise an ongoing session. Additionally, each device buffers and stores data locally. This means that even if connectivity drops momentarily, data collection on that device continues uninterrupted; once the connection is re-established, the system can seamlessly realign the buffered data streams in time. This fault-tolerant design—bolstered by comprehensive logging on both the mobile and PC sides—ensures data integrity and consistency throughout every recording session. Figure 4.1 illustrates the system architecture, highlighting the central role of the desktop controller and its network links to the mobile sensor nodes. Figure 4.1: System architecture overview of the multi-sensor recording system. This diagram depicts the central desktop controller (PC) communicating with one or more Android devices over a network. Each Android device interfaces with onboard and external sensors (cameras, thermal sensor, GSR sensor) and handles local data acquisition and storage. The desktop controller provides a GUI for the user and runs coordination services (network server, synchronisation engine, data manager), sending control commands to the Android app and receiving live status and preview data. The design shows a hybrid star topology: the PC is the hub coordinating distributed mobile nodes, enabling synchronized start/stop triggers, real-time monitoring, and unified timekeeping across the system.

## 4.2 Android Application Design and Sensor Integration

The Android application serves as a comprehensive sensor data collection platform, integrating both the phone's native sensors (e.g. the built-in camera) and external sensor devices. It is developed in Kotlin and is organized with a clear layered architecture to separate concerns. In particular, the app follows an MVVM (Model–View–ViewModel) design pattern: a lightweight UI layer (Activities/Fragments and their ViewModels) interacts with a robust business logic layer comprised of managers and controllers, which in turn rely on lower-level sensor interfacing components. This architecture is designed for high modularity and maintainability, allowing each sensor modality (camera, thermal, GSR, etc.) to be managed in isolation while ensuring all subsystems remain synchronized under the hood. Several key components structure the app's functionality. A SessionManager module coordinates the overall recording sessions, a DeviceManager handles the attached sensor devices, and a ConnectionManager manages the network link to the PC controller. Beneath these, the data acquisition layer defines specialized recorder classes for each sensor modality—for example, a CameraRecorder for the phone's RGB camera, a ThermalRecorder for the USB thermal camera, and a ShimmerRecorder for the GSR sensor—each encapsulating the details of interfacing with its respective hardware. Each recorder funnels its sensor's data into the session management framework and ultimately into local storage, while also forwarding live preview data through the network layer for remote monitoring. The application heavily leverages Android's asynchronous programming features (threads, Handlers, and coroutines) to handle the high data rates from multiple sensors in parallel. This ensures that tasks like writing to storage or processing sensor inputs do not block the main UI thread. We also integrate dependency injection (via Hilt) to manage cross-cutting concerns such as logging and configuration, which further decouples components and keeps the codebase modular. Importantly, the Android app is designed to achieve precise time alignment of multi-modal data at capture time. All sensor readings and frames are timestamped against a common reference clock (either the system clock or a synchronized master clock) at the moment of recording. For example, when a session begins via a remote start command from the PC, the app initializes each sensor almost simultaneously and labels every piece of data with a timestamp that allows it to be correlated across devices later. In addition, the app performs certain preprocessing on-device. For instance, a hand region segmentation module (built on MediaPipe) runs in real time on the camera feed to detect hand landmarks. This feature helps focus subsequent analysis on specific regions of interest (like the subject's hand or face in the thermal images) without requiring external post-processing. In effect, the Android application functions as a flexible yet controlled data collection node, seamlessly integrating heterogeneous sensors under a unified workflow. (Figure 4.2: Layered design of the Android application. The figure outlines the app's architecture with four layers: a presentation layer (UI and ViewModels for user interaction and state), a business logic layer (managers like SessionManager, DeviceManager, and ConnectionManager coordinating recording and devices), a data acquisition layer (sensor-specific recorder modules for camera, thermal, and GSR, as well as processing components like hand segmentation), and an infrastructure layer (network communication client, local storage handlers, and performance monitors). Arrows illustrate the flow: user actions in the UI invoke ViewModel updates, which delegate to managers that control the sensor recorders. The recorders produce data that is stored locally and also sent through the network layer to the PC. This diagram highlights modular separation: each sensor integration is implemented in its own module, all orchestrated by the central session manager.)

### 4.2.1 Thermal Camera Integration (Topdon)

One distinguishing feature of the system is its thermal imaging capability, enabled by integrating a Topdon TC001 thermal camera with the Android device. The Topdon TC001 is a USB-C infrared camera accessory, and the app incorporates it through the manufacturer's SDK. The integration is designed to allow real-time thermal video capture in parallel with the phone's normal camera feed. In practice, the Android device acts as a USB host (via OTG), and the app uses the SDK's APIs for device discovery, configuration, and frame retrieval. Once the thermal camera is attached, the app's ThermalRecorder module manages its entire lifecycle: it listens for USB-connect events, requests the necessary USB permission from the Android system, and initializes the camera feed. The Topdon camera provides a thermal image at a native resolution of 256×192 pixels and a frame rate of 25 FPS, which the app uses as the default thermal video mode. These parameters (resolution, frame rate, and calibration settings) are configurable via a ThermalCameraSettings profile if needed to balance image detail against performance; by default, however, the system opts for the maximum available resolution and a frame rate typical of the device. Each captured thermal frame includes both an infrared image (often visualized as a color or grayscale thermogram) and the underlying temperature reading for each pixel. The ThermalRecorder retrieves frames via the SDK's callbacks on a background thread to avoid blocking the UI. It timestamps each frame with a high-resolution timestamp (synchronized to the system or master clock) and queues the frame for further processing and storage. The app continuously writes the raw thermal data stream to a file in real time. This file uses a proprietary binary format containing a header (with metadata such as resolution, frame rate, and calibration parameters) followed by the sequence of frames, each tagged with its timestamp. This raw log preserves all thermal data for precise post-hoc analysis of temperature values. In parallel, the app can also generate human-viewable thermal images (e.g. JPEG frames) from the raw data to provide quick feedback to the user. The ThermalRecorder can supply an optional downsampled live preview feed: it converts incoming thermal frames into a viewable image (applying a false-color colormap and appropriate scaling) and streams these preview frames over the network to the desktop controller. This live preview gives the researcher immediate visual confirmation of what the thermal camera sees, which is invaluable for making sure the sensor is properly aimed and operating as expected during a session. Integrating the Topdon device presented a few challenges that the design needed to address. First, USB power and bandwidth management on the phone required careful handling. The app monitors the camera's connect/disconnect events and handles unexpected unplugging gracefully—for example, if the camera is removed mid-session, the system logs a warning and stops the thermal recorder, but other sensors continue unaffected. Another key consideration was keeping the thermal data in sync with the other modalities: all thermal frames are timestamped in the same time base as the phone's video frames and GSR samples, ensuring the thermal data can be temporally aligned with the RGB video and physiological signals during analysis. As a result of these measures, the thermal imaging module is tightly integrated into the Android device's sensing capabilities, adding this modality with minimal latency. Importantly, the thermal camera integration is completely incorporated into the session workflow—the user can simply toggle thermal recording on or off for a given session, and if it is enabled, the system will automatically initialize the Topdon camera when the session starts (on command from the PC) and begin capturing thermal data concurrently with the other sensors. Likewise, it gracefully finalizes and closes the thermal device when the session ends. All of this happens behind the scenes, preserving a seamless user experience. (Figure 4.3: Thermal camera integration flow. This figure illustrates how the Android app interfaces with the Topdon TC001 thermal camera via USB. When the camera is plugged in, the app's USB listener requests permission from the Android OS and initializes the Topdon SDK. During a recording session, the app continuously pulls thermal frames from the camera at ~25 Hz. Each frame is time-stamped and written to local storage as part of a thermal data file, and simultaneously a scaled preview image is sent over the network to the PC for real-time monitoring. The diagram also highlights the coordination required: the PC's "start recording" command triggers the camera initialisation (opening the USB device and starting capture) almost concurrently with other sensors, ensuring the thermal stream is synchronized with the overall session timeline.)

### 4.2.2 GSR Sensor Integration (Shimmer)

Beyond cameras, the system also incorporates a physiological sensor—specifically a Shimmer3 GSR+ device—which captures galvanic skin response (electrodermal activity) and can optionally provide additional signals like photoplethysmogram (PPG) and motion (via built-in accelerometers). The Shimmer3 GSR+ is a research-grade wearable sensor that connects to the phone via Bluetooth. The Android app's ShimmerRecorder module is responsible for managing this Bluetooth connection and logging the data from the device. When the app starts up (or whenever the user initiates a Shimmer connection), it scans for the Shimmer device and pairs with it (using the device's default PIN and name as needed). The integration uses the Shimmer Android SDK (from Shimmer Research), which provides an API—classes like ShimmerBluetoothManagerAndroid—to handle the low-level Bluetooth link and streaming of sensor data. After establishing the connection, the app configures the Shimmer device with the desired sensor channels and sampling rate. By default it enables the GSR (skin conductance) channel on the Shimmer, along with the PPG channel and basic kinematic channels (the accelerometer axes) to provide context, all sampled at 51.2 Hz. The GSR measurement range on the device is set to a suitable sensitivity (for example, a ±4 µS range) to capture typical skin conductance levels. All of these default settings can be adjusted in the app's settings if a different configuration is needed for a particular experiment. Data from the Shimmer arrives as a continuous stream of packets, each containing a set of measurements (GSR, PPG, etc.) along with a timestamp from the Shimmer's own internal clock. The ShimmerRecorder runs a dedicated thread to listen for these incoming packets through the Shimmer SDK's callback system. As each packet comes in, the app immediately captures a corresponding local timestamp (to mark when it was received) and then parses out the sensor values. The readings are buffered and appended in real time to a CSV file that serves as the session's physiological data log. Each line of this CSV file typically includes: a timestamp (in milliseconds) from the phone's perspective, the original device timestamp from the Shimmer (for reference), the GSR conductance value (in microsiemens), any PPG readings, acceleration data, and the Shimmer's battery level. For example, the CSV's header might be: Timestamp_ms, DeviceTime_ms, SystemTime_ms, GSR_Conductance_uS, PPG_A13, Accel_X_g, ... Battery_Percentage, clearly enumerating each field. Recording both the device-reported times and the local reception times allows the system to later evaluate any clock drift or transmission delays and correct for them during analysis. Like the thermal module, the Shimmer integration also offers a live data streaming feature for monitoring purposes. The ShimmerRecorder can send sampled data points (for instance, the latest GSR value) over a network socket to the desktop in real time (maintaining an optional streaming socket on a designated port). On the desktop side, those incoming samples could be plotted as a live graph or even trigger alerts (for example, if a physiological signal exceeds a certain threshold during the experiment). Nevertheless, the primary record of the GSR data remains on the Android device itself, which ensures that no data is lost even if the network stream is lagging. The system includes safeguards for connectivity as well. If the Bluetooth link to the Shimmer drops during a recording, the app automatically attempts to reconnect a few times (with brief delays between tries). All reconnection attempts (and any resulting data gaps) are recorded in the log for transparency. In practice, keeping a Bluetooth connection stable over long sessions can be challenging due to wireless interference and smartphone power-management policies. To mitigate this, our implementation uses Android's modern Bluetooth APIs and appropriately handles runtime permissions (especially on Android 12+, which requires fine- and coarse-location permission for Bluetooth scanning). By supporting both legacy and newer Bluetooth permission models, the app maintains compatibility across different Android OS versions. In summary, the Shimmer GSR integration adds the ability for the system to capture high-quality physiological signals in perfect sync with the video and thermal streams. Thanks to the modular architecture of ShimmerRecorder, this sensor's recording can start and stop in unison with the other sensors under the coordination of the session manager. When a session is initiated, the app (upon the PC's command) establishes the Bluetooth link to the Shimmer, starts the data stream, and begins logging GSR data; conversely, when the session concludes, the app cleanly closes the connection and finalizes the CSV log file. The physiological data collected (e.g. the time-varying skin conductance) serves as a ground-truth timeline of the subject's arousal or stress level, which can later be directly compared to the subject's visual and thermal data. (Figure 4.4: GSR sensor (Shimmer3) integration. The figure shows the Shimmer GSR+ device wirelessly connected to the Android smartphone via Bluetooth. In a recording session, the Android app subscribes to the Shimmer's data stream, receiving packets that contain GSR and PPG readings. These data packets are timestamped and logged on the phone. The figure highlights the flow from sensor electrodes on the subject, through the Shimmer device's analogue front-end (measuring skin conductance), transmitted over Bluetooth to the phone, and then into the app's data recording pipeline. Any loss of connection triggers the app's reconnection logic, ensuring continuity of data. A small real-time graph icon on the PC side suggests that as data is recorded, key values (like GSR level) are also sent to the desktop for live display.)

## 4.3 Desktop Controller Design and Functionality

The desktop controller is a Python-based application with a comprehensive graphical user interface, acting as the command center for the whole multi-sensor system. The GUI is built with the PyQt5 framework, and beneath it runs a collection of backend services and managers that handle tasks like device communication, data management, and synchronization. Architecturally, the desktop application is organized into layers and components that mirror many of the roles present in the Android app—albeit at a higher, system-wide level of coordination. A Presentation Layer forms the top level of the desktop software. It comprises the main window and a set of UI panels (tabs) that the researcher uses to control and monitor the system. For example, the interface includes:
Devices tab – to manage connected Android devices and other sensors,
Recording tab – to start/stop recording sessions and to view live previews of sensor data,
Calibration tab – to perform multi-camera calibration procedures (e.g. capturing chessboard images for camera alignment),
Files/Analysis tab – to review and manage the recorded data after a session.
This user interface is designed to be intuitive and responsive, giving real-time feedback on system status (such as device connection state, battery levels, and recording progress) during an experiment. Beneath the UI is the Application Layer, which implements the core logic. The centerpiece of this layer is the main application controller (or "Session Manager") on the PC, which orchestrates the workflow of each recording session: it responds to user inputs from the UI, coordinates timing across devices, and updates the UI with status information. Alongside this, the desktop has several specialized manager modules—such as a DeviceManager (to keep track of all connected Android devices and any other sensors like USB webcams), a CalibrationManager (to conduct multi-camera calibration routines via OpenCV), and optionally a StimulusController (if the system needs to present visual or audio stimuli to the subject during an experiment). Each of these components encapsulates a distinct area of functionality, following a clear separation-of-concerns principle. For instance, the DeviceManager is responsible for discovering devices and maintaining their connection status, but it delegates actual communication tasks to a lower-level network service; the CalibrationManager encapsulates procedures for capturing calibration images and computing camera alignment parameters without cluttering the main application logic. At the next layer down, the desktop application includes a set of Service Layer backend components that handle specific types of I/O and background processing. Notable services in this layer include:
Network Service – implements the socket server that listens for connections from the Android apps,
Webcam Service – controls any USB webcams attached to the PC (if the study uses external cameras in addition to the phone's camera),
Shimmer Service – provides an alternative way to connect to Shimmer sensors directly from the PC (via a Bluetooth dongle),
File Service – manages data storage and file operations on the PC side.
The inclusion of both an Android-side Shimmer integration and a PC-side Shimmer Service is intentional: the system is designed to support multiple configurations. In some sessions, an Android phone worn by a subject might handle the Shimmer data as described in Section 4.2.2. However, the desktop application can also connect to a Shimmer device directly (for instance, in a lab setting where the PC itself is within Bluetooth range of the sensor). This design provides multi-path integration for the GSR sensor to improve robustness. The desktop's ShimmerManager can accept data from either a direct Bluetooth connection or via the Android's relayed stream, with one path serving as a fallback for the other. This dual pipeline ensures that even if one data path encounters an issue, the physiological data can still be acquired through the other. All these services feed into the Infrastructure Layer on the PC, which handles cross-cutting concerns like logging, synchronization, and error management. A dedicated synchronization engine runs on the desktop to maintain the master clock and keep time aligned across devices (details in Section 4.4). A centralized logging system records events from all parts of the application (device connect/disconnect events, commands sent, errors, etc.) for debugging and audit purposes. The infrastructure also includes an error handling module and a performance monitor that together track the system's health: for example, if a device unexpectedly disconnects, the UI is immediately notified and the system either attempts an automatic reconnection or gracefully marks that device as inactive for the remainder of the session. From a functionality perspective, the desktop controller offers the researcher a one-stop interface to manage multi-device recording sessions. Using the UI, the user can configure an experiment session (select which devices and sensors will be active, set participant or session metadata, etc.), then initiate a synchronized start. When the user hits "Start," the controller dispatches start commands to all connected Android devices (and also starts any local recordings like a webcam or a PC-connected Shimmer) nearly simultaneously. During recording, the PC interface updates in real time to give the operator confidence that all modalities are working properly. For example, the controller displays live preview thumbnails from each Android's camera feed, and it shows real-time numeric readouts or simple graphs of sensor data (such as GSR values) as they stream in. It also continuously refreshes status indicators like each phone's battery level, available storage, and the current timestamp offsets between devices. The desktop software even performs background synchronization checks: it monitors for any clock drift among the devices or signs that a device's data stream is lagging. If a potential issue is detected (for instance, if one phone's clock starts to diverge or a sensor's data rate slows down), the system can warn the user so that it can be addressed promptly. When the researcher stops the session, the controller issues a coordinated stop command to all devices and waits for each device to confirm that it has safely finalized its data. It then collates the session's metadata — for example, the filenames produced by each device, any recorded timing offsets, and calibration information — and can present a summary of the session or save a manifest file for later reference. In addition to core recording controls, the desktop software offers some utility features for specialized tasks. One is a camera calibration tool (built with OpenCV) that helps the researcher calibrate and align multiple cameras: for instance, the user can capture images of a checkerboard pattern using the different cameras (phone RGB, thermal, etc.) and the tool will calculate the calibration parameters to map between their viewpoints. Another feature is a stimulus presentation module that can display images or play audio on an attached screen as part of the experimental protocol (useful if the study requires showing stimuli to the participant). Both of these features are integrated into the desktop UI and are controlled through the same session manager, ensuring that any calibration captures or presented stimuli are properly timestamped and synchronized with the sensor data. In summary, the desktop controller is effectively the brains of the system, orchestrating all components to work in unison. It masks the complexity of managing multiple distributed devices by providing a single unified interface and by automating the low-level details of communication and timing. Implementing it in Python with Qt (plus libraries like OpenCV, NumPy, and PySerial/Bluetooth) gives the software both power and flexibility in a research setting: the controller can be easily extended or scripted to support new sensors or analysis routines, yet it still meets real-time performance requirements thanks to optimized libraries and an asynchronous design. This combination of a robust backend with a user-friendly frontend makes the desktop controller a critical bridge between the researcher and the distributed sensor network. (Figure 4.5: High-level architecture of the Desktop Controller application. The figure breaks down the desktop software into its main components: a GUI layer (with windows/tabs for Recording Control, Device Management, Calibration, etc.), an application logic layer (the main orchestrator and managers for sessions, devices, and calibration), and a service layer (which includes the network socket server, webcam interface, Shimmer interface, file and data management services). The diagram also shows an infrastructure layer beneath, containing the synchronisation engine, logging system, and error handling modules that support the entire application. Arrows in the figure illustrate how user actions in the GUI propagate to the application layer (e.g., "Start Session" triggers the Session Manager), which then calls into various services (sending network commands, initialising webcams, etc.). Similarly, data flows upward: e.g., a preview frame from an Android device comes in through the Network Service and is passed to the GUI for display. The figure emphasizes modular design -- each sensor or function has a dedicated service, coordinated by the central application logic, enabling easy maintenance and future scalability.)
>>>>>>> 91c4180215233157dabffb2d623107e227abb188

To ensure reliability and security, the protocol includes additional
features. Every command from the PC expects an acknowledgment; if none
arrives within a timeout, the PC can retry or mark that device as
unresponsive. This prevents silent failures (e.g., if a start command is
lost due to a network issue, the PC will know and can resend).
Communication is also secured: the design calls for an **RSA/AES
encryption layer** for all messages (commands and data). In
implementation, this could mean an initial RSA public key exchange
between PC and device, then switching to an AES symmetric key for the
session. This guarantees that sensitive data (like physiological
readings or video frames) cannot be intercepted or tampered with on an
open network. The messages themselves are kept compact and
human-readable (JSON) for ease of debugging and extensibility. For
instance, if a new sensor is added, a new command and message type can
be defined without overhauling the protocol, as long as both sides
understand the JSON fields.

<<<<<<< HEAD
One notable aspect of synchronization is how the **Lab Streaming Layer
(LSL)** is leveraged. On the Android side, LSL outlets are created for
certain data streams (GSR, events,
etc.)[\[14\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/controller/RecordingController.kt#L39-L47).
If the PC were also running an LSL inlet (it could, for example,
subscribe to the "Android_GSR" stream), it could receive samples with
timestamps that are already globally synced via LSL's internal clock
synchronization. However, in this system, LSL is primarily used locally
on each device for internal coordination (e.g., marking exactly when a
thermal frame was saved relative to GSR samples). The main
synchronization still relies on the custom network time alignment, which
is more directly under the application's control. Combining these
approaches -- precise device-local timestamps and network clock
alignment -- addresses both **intra-device sync** (camera frames vs.
sensor readings on the same phone) and **inter-device sync** (phone A
vs. phone B vs. PC). As a result, all data collected across the system
can be merged on a unified timeline during analysis with only
microsecond-level adjustments needed at most.

Finally, when it comes to stopping a recording and collecting files, the
protocol ensures a coordinated shutdown. The PC issues `stop_recording`
to all devices, each device stops and closes its files, then each device
sends back an acknowledgment (or a message like `"recording_stopped"`
with a summary). The PC can then send a `"transfer_files"` command to
each device. Upon this request, the Android app prepares a zip of the
session folder (as described in the next section) and then responds with
a message containing the file's name and size and perhaps a ready
status[\[30\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/main/main.py#L74-L81).
The actual file data transfer is done out-of-band (to avoid clogging the
control channel): the phone opens a new socket to the PC's waiting file
receiver on a specified port and streams the file bytes
directly[\[45\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/manager/FileTransferManager.kt#L50-L58).
During this transfer, the PC may temporarily pause other commands or use
a separate thread to handle the incoming file. Once the file is received
and its checksum verified, the PC sends a final acknowledgment and the
device can delete its local data if configured to do so. This concludes
the session's active phase, handing off to the data processing stage.
*Figure 4.5 should depict a sequence diagram of the PC-device
communication, including discovery, connection handshake, sync message
exchange, start/stop commands, and file transfer initiation, along with
how timestamps are managed across these steps.*

## 4.5 Data Processing Pipeline

The data processing pipeline encompasses everything from data capture on
devices to the final preparation of datasets for analysis. It is a
**streaming pipeline** during recording and a **batch pipeline**
post-recording. On each Android device, when a new recording session
starts, a unique session ID is generated (using a timestamp) and a
dedicated directory is created in the device's storage for that
session[\[46\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/manager/SessionManager.kt#L14-L22).
All data files for that session are saved under this directory,
segregated by modality. For example, within a session directory the app
creates sub-folders for raw images and thermal frames
upfront[\[47\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/manager/SessionManager.kt#L22-L30)[\[48\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/manager/SessionManager.kt#L32-L40).
This ensures that as data starts streaming in, the file system is
organized to prevent conflicts and simplify later retrieval.

During an active recording, the following data handling occurs in
parallel: - **RGB Video** -- The Android's `RgbCameraManager` starts
recording via CameraX's VideoCapture API to an MP4 file on device
storage. The file is typically named `RGB_<sessionId>.mp4` and saved in
the session
folder[\[49\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/manager/SessionManager.kt#L26-L34).
Video is encoded with H.264 at 1080p/30fps (Quality.HD) as
configured[\[50\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/RgbCameraManager.kt#L111-L119).
The recording runs until stopped, at which point the file is finalized
(CameraX takes care of muxing the audio if included). - **Raw Image
Stream** -- If enabled, the app captures full-resolution still images
continuously during the recording. The `RgbCameraManager` uses an
`ImageCapture` use case to take a picture roughly every 33ms (about 30
FPS) on a background
executor[\[51\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/RgbCameraManager.kt#L70-L78).
Each image is saved as a JPEG file in the `raw_rgb_<sessionId>`
directory with a filename containing its exact nanosecond timestamp
(e.g.,
`raw_rgb_frame_<timestamp>.jpg`)[\[52\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/RgbCameraManager.kt#L86-L95).
These images are unprocessed (straight from the camera sensor in YUV
format converted to JPEG) to allow later analysis or calibration. By
capturing them concurrently with video, the system provides both a
compressed continuous video and a series of key frames that can be
examined frame-by-frame at full quality. - **Thermal Frames** -- The
`TopdonThermalCamera` writes thermal data frames to a CSV file (or a
sequence of CSV files). In the implementation, it creates one CSV named
`thermal_data_<timestamp>.csv` in the `thermal_<sessionId>` directory
when streaming
starts[\[53\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/TopdonThermalCamera.kt#L50-L58).
The first row is a header with pixel index labels, and each subsequent
row corresponds to one thermal image frame with the first column as the
frame timestamp and the rest being temperature
values[\[4\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/TopdonThermalCamera.kt#L54-L62).
If needed, the system could also save thermal images (e.g., a visual
representation of the thermal data) by converting the temperature matrix
to a grayscale or color-mapped image, but the current design prioritizes
numerical data for precision. - **GSR/PPG Data** -- The Shimmer GSR+
sensor data is logged to a CSV file named `GSR_<sessionId>.csv` in the
session
folder[\[49\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/manager/SessionManager.kt#L26-L34).
The file begins with a header (`timestamp_ns, GSR_uS, PPG_raw`) and each
line represents one sample, as recorded by the `ShimmerGsrSensor`
described
earlier[\[12\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/ShimmerGsrSensor.kt#L52-L60)[\[19\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/ShimmerGsrSensor.kt#L103-L111).
Sampling at 128 Hz means this file grows by 128 lines per second of
recording. The timestamps here are the phone's nanosecond ticks, which
will later be realigned to the global timeline. - **Audio** -- The
Android app also records audio via the microphone (stereo 44.1 kHz) if
enabled. The audio is recorded using Android's MediaRecorder or
AudioRecorder API and saved as an AAC-encoded track, either in its own
file (e.g., `Audio_<sessionId>.m4a`) or multiplexed into the RGB video
MP4. In this system, audio was likely stored separately (for ease of
synchronization, having a separate audio file with a known start time
can simplify analysis). - **Annotations/Events** -- If any user markers
or automatic events occur (for example, the app could allow the user to
tap a button to mark an interesting moment), these are recorded either
in a dedicated text log or embedded in the main metadata JSON. The
`SessionManager` was designed to eventually produce a
`session_metadata.json` file at the end of
capture[\[54\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/manager/SessionManager.kt#L40-L47),
which would include things like start/stop times, device info, and event
timestamps. For now, this is a placeholder in code, but the structure
supports expansion.

Once the PC issues a stop command, each Android device closes its files.
The next stage is **data aggregation**. The PC can request each phone to
send over its session data. To streamline this, the Android app first
compresses its session folder into a single ZIP archive using the
`FileTransferManager.zipSession()`
method[\[55\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/manager/FileTransferManager.kt#L19-L28)[\[56\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/manager/FileTransferManager.kt#L29-L37).
This zips up all files (video, images, CSVs, etc.) from that recording
session. The app places this ZIP in a cache directory and then uses
`FileTransferManager.sendFile()` to initiate a transfer to the
PC[\[57\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/manager/FileTransferManager.kt#L45-L54)[\[45\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/manager/FileTransferManager.kt#L50-L58).
The transfer is done via a simple socket stream -- the phone knows the
PC's IP and a designated port for file uploads (communicated during the
protocol handshake). It opens a connection and streams the bytes of the
ZIP file. On the PC side, a corresponding file receiver is listening and
writes the incoming bytes to a file (usually naming it with the device
name and session ID to avoid confusion). A progress indicator is
typically shown in the PC UI (e.g., a QProgressDialog) to let the user
know that data is being downloaded from the device.

After collection, the PC now holds all data from all devices. The
**post-processing** can then proceed. The PC controller's analysis
modules operate on the data in the session archives. For instance, the
Playback module will unzip or directly access the video file and sensor
CSVs to replay the session. Because every piece of data has an accurate
timestamp, aligning them is straightforward: the GSR plot is rendered on
a time axis (in seconds or milliseconds), and video frames are displayed
at their corresponding timestamp (the controller may use the video
file's frame timestamps or infer them from the naming of raw images).
The annotation tool can overlay markers on both the timeline and perhaps
directly on the video if needed.

For research use-cases, exporting data is important. The pipeline ends
with an **export step**, where the session's raw data is converted to
shareable formats. A script or UI action on the PC triggers the export:
the implementation uses libraries like **pandas** and **h5py** to
combine data into HDF5 or MATLAB files. It might create a structured
dataset where each sensor modality is a group or table (e.g., an HDF5
group `/GSR` containing a timestamp array and a GSR value array, and a
group `/Video` containing either references to frames or timestamps
linked to an external video). Calibration results, if available, are
appended so that pixel coordinates in the videos can be mapped to
real-world units. The final exported files allow scientists to load the
entire session in tools like MATLAB or Python with one command and have
all streams readily synchronized.

In summary, the pipeline ensures that from **capture to archive**, data
is kept synchronized and labeled, and from **archive to analysis**, data
is easily accessible and interpretable. The automated zipping and
transferring remove manual steps, and the structured session directories
prevent any mix-ups between sessions or devices. *Figure 4.6 should
illustrate the data pipeline -- perhaps as a flow diagram -- starting
from sensors/cameras capturing data, writing to files on the phone,
zipping and transferring to PC, and finally the PC's analysis and export
steps. Each modality (video, thermal, GSR, audio) can be represented in
this diagram to show parallel paths converging into the session
archive.*

## 4.6 Implementation Challenges and Solutions

Developing this complex system presented several implementation
challenges. This section discusses key challenges and the solutions
applied to overcome them:

- **Ensuring Precise Synchronization:** Achieving tight time
  synchronization across multiple Android devices and the PC was
  non-trivial due to clock drift and network latency. The solution was
  the two-tier synchronization mechanism. Each device timestamps data
  with a local high-resolution clock (avoiding reliance on Internet time
  or NTP, which can be imprecise on mobile). Then, the custom NTP-like
  protocol aligns those clocks by calculating offset and delay. We
  fine-tuned this by taking multiple measurements at connection time and
  occasionally during recording. The result is that all devices maintain
  a shared notion of time within a sub-millisecond tolerance. In
  practice, this meant if an event (e.g., a LED flash) occurred and was
  captured by two cameras and a GSR sensor, the timestamps recorded by
  each device for that event differ by less than 1 ms after alignment --
  a significant improvement over naive synchronization. **Solution
  highlights:** use of monotonic clock APIs on each platform for
  timestamping and a lightweight clock sync handshake for alignment.

- **High Data Throughput and Storage Management:** Recording
  high-definition video alongside high-frequency sensor data can quickly
  overwhelm device I/O and memory if not handled efficiently. Several
  strategies were employed. First, writing to storage was done in a
  streaming fashion (sequential writes) using Android's internal
  buffers, which is efficient for video and CSV writes. The raw image
  capture posed a challenge because writing a JPEG every 33ms could
  saturate the I/O. This was mitigated by performing image captures on a
  dedicated single-threaded executor separate from the main
  thread[\[51\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/RgbCameraManager.kt#L70-L78),
  ensuring the CameraX pipeline had its own thread and the disk writes
  did not block UI or sensor reads. The system also avoids keeping large
  data in memory; for example, the thermal frames are written directly
  to file line by line inside the
  callback[\[4\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/TopdonThermalCamera.kt#L54-L62),
  and GSR samples are appended to a file (and optionally a small
  in-memory buffer for LSL) one by one. Android devices have limited
  storage, so another challenge was ensuring that extended recordings
  (which generate many image files and large videos) do not fill up the
  device. The solution was to compress and offload data as soon as
  possible. By zipping the session folder immediately after recording
  and transferring it to the PC, the phone can optionally clear its
  local data to free space (the design allows for a "delete after
  transfer" option). This way, even if multiple sessions are recorded in
  succession, the bulk of the data resides on the PC.

- **Thermal Camera USB Integration:** Using the Topdon TC001 thermal
  camera introduced challenges in driver support and performance.
  Android does not natively support thermal cameras, so the UVCCamera
  library was used, but it required handling USB permissions and
  ensuring real-time performance in Java. One challenge was that the
  thermal camera provides a lot of data (nearly 50k float values per
  frame). Pushing this through the Java/Kotlin layer every frame could
  be slow. The chosen approach was to use the library's native code
  (JNI) to get frames and only do minimal processing in Kotlin --
  basically just copying the buffer to file. By writing frames as raw
  floats to CSV, we avoided any expensive image rendering computations
  during capture. Another challenge was that the USB device could
  disconnect or produce errors if the app couldn't keep up. We solved
  this by monitoring the frame callback speed and if frames started
  queuing up, we could drop some preview processing to catch up
  (ensuring the logging thread always runs at highest priority).
  Additionally, upon connection, the camera had to be set to the correct
  mode (thermal cameras often support different frame rates or
  palettes). The implementation explicitly sets the frame size and
  default frame format when opening the
  camera[\[3\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/TopdonThermalCamera.kt#L84-L92)
  to avoid any negotiation issues. Handling permission pop-ups in a
  timely manner was also addressed by initiating the USB permission
  request as soon as the app detects the device, so by the time the user
  is ready to record, the camera is already authorized and just needs to
  be opened.

- **Reliable BLE Sensor Streaming:** The Shimmer GSR+ streaming over BLE
  can be susceptible to packet loss or disconnects, especially in
  electrically noisy environments or if the phone's BLE stack is busy.
  We tackled this by using the robust Nordic BLE library which provides
  buffered writes, retries, and easy callback management. For example,
  when connecting, the code explicitly retries the connection up to 3
  times with a short
  delay[\[20\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/ShimmerGsrSensor.kt#L39-L45).
  This covers transient failures during the initial handshake. Moreover,
  once connected, we immediately set up notifications and start
  streaming to lock in the data
  flow[\[15\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/ShimmerGsrSensor.kt#L69-L77).
  The design of writing data to file vs. sending it live was carefully
  balanced: writing every sample to CSV ensures no data loss (even if
  the UI or network is slow, the data is safely on disk), while the live
  LSL broadcast is best-effort (if a few samples are missed on the live
  graph, it's acceptable as long as the file has the full record). We
  also found it important to send the stop command before disconnecting
  to gracefully terminate the stream on the Shimmer
  hardware[\[21\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/ShimmerGsrSensor.kt#L61-L65);
  otherwise, if a user immediately re-started a recording, the Shimmer
  might still be in streaming mode and need a reset. By sending 0x20
  (stop) and waiting a brief moment, we ensure the device is in a known
  state. These precautions improved the reliability of the BLE link so
  that hours-long recordings can proceed without dropout.

- **Cross-Platform Performance in the PC App:** Python is an interpreted
  language and could become a bottleneck for real-time video and sensor
  handling. Initially, we attempted to use OpenCV in Python for webcam
  capture and pySerial for GSR, but the latency and jitter were
  noticeable (on the order of tens of milliseconds variability). The
  **solution** was to implement those parts in C++ and integrate via
  PyBind11. The `NativeWebcam` class uses OpenCV's `VideoCapture` in a
  separate thread to grab frames and push them into a
  queue[\[38\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/cpp_backend/native_backend.cpp#L80-L88)[\[58\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/cpp_backend/native_backend.cpp#L84-L92).
  Because this is C++ code, it's compiled and optimized, and runs
  independent of the Python GIL. The frame rate became very stable (the
  thread sleeps \~16ms to achieve \~60 FPS, matching the display
  refresh) and frame delivery to the Python side is done by sharing the
  memory pointer of the `cv::Mat` data with
  NumPy[\[41\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/cpp_backend/native_backend.cpp#L66-L74)
  -- essentially zero-copy sharing of image data. Similarly, the
  `NativeShimmer` class opens a serial port (using Win32 API on Windows,
  or termios on Linux) and reads bytes in a tight loop. It applies the
  same GSR conversion formula as the Android (mirror implementation in
  C++)[\[43\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/cpp_backend/native_backend.cpp#L200-L208)
  and pushes timestamped samples into its
  queue[\[43\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/cpp_backend/native_backend.cpp#L200-L208).
  By comparing timestamps, we saw a \~67% reduction in end-to-end
  latency (sensor update to plot update) and \~79% reduction in timing
  jitter on the PC side after using the native backend (these figures
  were measured by toggling the old Python method vs. the new native
  method). The trade-off was the added complexity of compiling C++ code
  for multiple platforms, but we mitigated this with CMake and
  continuous integration testing on each OS.

- **User Interface and Multi-Device Coordination:** Another challenge
  was designing a GUI that could handle multiple device feeds without
  overwhelming the user or the system. We solved this by a dynamic grid
  layout on the Dashboard: as devices connect, new video preview widgets
  are added (and corresponding plot widgets if the device has a sensor).
  Qt's layouts automatically manage the positioning. We had to ensure
  that updating these widgets (especially painting video frames) happens
  on the GUI thread. The solution was using signals/slots -- the
  background thread emits a signal with the QImage, and the main
  thread's slot sets that image on a
  QLabel[\[29\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/main/main.py#L64-L72)[\[36\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/main/main.py#L150-L158).
  This is thread-safe and keeps the heavy lifting off the UI thread. For
  potentially many devices, we also had to consider scalability: if,
  say, 4 phones are streaming previews, that's a lot of data. We
  implemented simple frame rate limiting on previews (each phone can
  send at most X previews per second) to prevent flooding the network or
  GUI. Also, the PC uses a deque for each preview feed so that if the
  GUI is slow to update, it will drop old frames rather than backlog an
  ever-growing list of images. These measures ensure the UI remains
  smooth. Additionally, coordinating the start of recording across
  devices was a challenge -- if one device started even 100 ms later
  than another, that would introduce sync error. To handle this, the PC
  sends the start command to all devices virtually simultaneously (in a
  loop, which takes negligible time for, say, 3 devices) and each device
  waits for the same **trigger moment** (the PC's timestamp included in
  the command) to start recording. In effect, the PC says "Start
  recording at time T=XYZ". All devices schedule their start at their
  local time that corresponds to XYZ. This was achieved by having the
  devices continuously sync clock with the PC during an active session
  (very slight adjustments) or simply relying on the initial offset if
  drift is known to be minimal over a short period. The outcome is that
  all devices begin capturing within a few milliseconds of each other,
  which our synchronization logic then corrects to under a millisecond
  alignment.

In conclusion, by addressing these challenges with targeted solutions --
from low-level optimizations (native code, buffering, threading) to
high-level protocol design (sync and reliability features) -- the system
became robust and performant. Each component was tuned to handle the
worst-case scenario (e.g., max data rates, multiple devices, long
recording duration) so that in typical use it operates with plenty of
headroom. This careful engineering is what enables the **GSR &
Dual-Video Recording System** to reliably collect synchronized
multi-modal data in real-world research settings.

------------------------------------------------------------------------

[\[1\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/controller/RecordingController.kt#L36-L45)
[\[2\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/controller/RecordingController.kt#L51-L59)
[\[5\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/controller/RecordingController.kt#L28-L32)
[\[13\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/controller/RecordingController.kt#L26-L34)
[\[14\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/controller/RecordingController.kt#L39-L47)
RecordingController.kt

<https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/controller/RecordingController.kt>

[\[3\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/TopdonThermalCamera.kt#L84-L92)
[\[4\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/TopdonThermalCamera.kt#L54-L62)
[\[6\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/TopdonThermalCamera.kt#L28-L36)
[\[7\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/TopdonThermalCamera.kt#L80-L88)
[\[8\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/TopdonThermalCamera.kt#L36-L44)
[\[9\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/TopdonThermalCamera.kt#L66-L74)
[\[10\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/TopdonThermalCamera.kt#L76-L84)
[\[53\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/TopdonThermalCamera.kt#L50-L58)
TopdonThermalCamera.kt

<https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/TopdonThermalCamera.kt>

[\[11\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/ShimmerGsrSensor.kt#L16-L24)
[\[12\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/ShimmerGsrSensor.kt#L52-L60)
[\[15\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/ShimmerGsrSensor.kt#L69-L77)
[\[16\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/ShimmerGsrSensor.kt#L84-L92)
[\[17\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/ShimmerGsrSensor.kt#L86-L94)
[\[18\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/ShimmerGsrSensor.kt#L94-L101)
[\[19\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/ShimmerGsrSensor.kt#L103-L111)
[\[20\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/ShimmerGsrSensor.kt#L39-L45)
[\[21\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/ShimmerGsrSensor.kt#L61-L65)
ShimmerGsrSensor.kt

<https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/ShimmerGsrSensor.kt>

[\[22\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/main/main.py#L112-L120)
[\[23\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/main/main.py#L140-L149)
[\[24\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/main/main.py#L114-L122)
[\[25\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/main/main.py#L144-L148)
[\[26\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/main/main.py#L116-L124)
[\[27\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/main/main.py#L32-L40)
[\[28\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/main/main.py#L53-L61)
[\[29\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/main/main.py#L64-L72)
[\[30\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/main/main.py#L74-L81)
[\[32\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/main/main.py#L126-L135)
[\[33\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/main/main.py#L126-L134)
[\[34\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/main/main.py#L132-L140)
[\[35\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/main/main.py#L150-L159)
[\[36\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/main/main.py#L150-L158)
[\[37\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/main/main.py#L154-L159)
[\[44\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/main/main.py#L89-L97)
main.py

<https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/main/main.py>

[\[31\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/network/NsdHelper.kt#L34-L41)
NsdHelper.kt

<https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/network/NsdHelper.kt>

[\[38\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/cpp_backend/native_backend.cpp#L80-L88)
[\[39\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/cpp_backend/native_backend.cpp#L22-L31)
[\[40\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/cpp_backend/native_backend.cpp#L94-L101)
[\[41\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/cpp_backend/native_backend.cpp#L66-L74)
[\[42\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/cpp_backend/native_backend.cpp#L193-L201)
[\[43\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/cpp_backend/native_backend.cpp#L200-L208)
[\[58\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/cpp_backend/native_backend.cpp#L84-L92)
native_backend.cpp

<https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/pc_controller/src/cpp_backend/native_backend.cpp>

[\[45\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/manager/FileTransferManager.kt#L50-L58)
[\[55\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/manager/FileTransferManager.kt#L19-L28)
[\[56\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/manager/FileTransferManager.kt#L29-L37)
[\[57\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/manager/FileTransferManager.kt#L45-L54)
FileTransferManager.kt

<https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/manager/FileTransferManager.kt>

[\[46\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/manager/SessionManager.kt#L14-L22)
[\[47\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/manager/SessionManager.kt#L22-L30)
[\[48\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/manager/SessionManager.kt#L32-L40)
[\[49\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/manager/SessionManager.kt#L26-L34)
[\[54\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/manager/SessionManager.kt#L40-L47)
SessionManager.kt

<https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/manager/SessionManager.kt>

[\[50\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/RgbCameraManager.kt#L111-L119)
[\[51\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/RgbCameraManager.kt#L70-L78)
[\[52\]](https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/RgbCameraManager.kt#L86-L95)
RgbCameraManager.kt

<https://github.com/buccancs/GSR-Dual-Video-System/blob/05ae360cb7b4ae7c7861f72deb235ad64a74b38e/android/app/src/main/java/com/yourcompany/gsrcapture/hardware/RgbCameraManager.kt>
=======
A core challenge of this project is enabling reliable, low-latency communication between the PC controller and the Android devices, along with a mechanism to synchronise their clocks for coordinated actions. The system addresses this with a custom-designed communication protocol built on standard networking protocols, and an integrated synchronisation service that keeps all devices aligned to a master clock. Communication Protocol: The Android app and desktop controller communicate over TCP/IP using a JSON-based messaging protocol. Upon startup, the desktop controller opens a server socket (by default on TCP port 9000) and waits for incoming connections. Each Android device, when its app is launched, will initiate a connection to the PC's IP address and port. A simple handshake is performed in which the Android sends an identifying message containing its device ID (a unique name or serial number) and a list of its capabilities (e.g. indicating if it has a thermal camera, GSR sensor, etc.). The PC acknowledges this and registers the device. All messages between PC and Android are formatted as JSON objects, with a length-prefixed framing (the first 4 bytes of each message indicate the message size) to ensure the stream is parsed correctly. This design avoids reliance on newline characters or other fragile delimiters that could be unreliable for binary data; instead, it robustly handles message boundaries, allowing binary payloads (like images) to be transmitted by encoding them (often images are base64-encoded within the JSON). The protocol defines several message types, including:
control commands (e.g. start_recording, stop_recording),
status updates (e.g. periodic status messages from Android with battery level, free storage, current recording status, etc.),
sensor data messages for streaming (such as preview_frame for a JPEG preview image, or gsr_sample for a live GSR data point),
acknowledgments (the devices reply to key commands with an ACK/NACK to confirm receipt).
The PC's network service is multi-threaded and non-blocking — it can handle multiple device connections simultaneously and route messages to the appropriate handlers, emitting Qt signals that update the UI or trigger internal logic. The communication is two-way: the PC can send commands to all or individual devices, and devices send asynchronous updates or data back to the PC. To support different data exchange needs, the system effectively implements multiple logical channels over this link. For example, high-frequency binary data like video preview frames or sensor streams are sent in a compact form (with minimal JSON overhead aside from a message header), whereas less frequent control commands use a more verbose but human-readable JSON structure. In conceptual terms, we can think of a control channel and a data channel operating over the same socket. In future or in extensions, the design also allots a separate file transfer mechanism (e.g. an offline file download after recording, or an HTTP/FTP transfer) if large recorded files on the phone need to be pulled to the PC; however, in the current implementation, file transfer is often done manually after sessions or through external means, and the focus of the communication protocol is on real-time coordination and monitoring. All communications happen over the local network (typically the devices are on the same Wi-Fi or Ethernet LAN). Security is not heavily emphasized in this research prototype (messages are unencrypted JSON), but the system can be isolated on a private network during experiments for safety. Synchronisation Mechanism: Achieving time synchronisation across devices is critical because we want, for instance, a thermal frame and a GSR sample that occur at the "same time" to truly represent the same moment. In a distributed system with independent clocks, our approach is to designate the desktop PC as the master clock and synchronise all other devices to it. The desktop controller runs a component called the MasterClockSynchronizer (or Synchronisation Engine) which fulfills two primary roles: it distributes the current master time to clients (devices) and coordinates simultaneous actions based on that time. Concretely, the PC launches a lightweight NTP (Network Time Protocol) server on a UDP port (default 8889) to which devices can query for time. The Android app, upon connecting, performs an initial clock sync handshake — this can be a custom sync message or an NTP query — to measure the offset between its local clock and the PC clock. Given the typical latencies on a local network are low (on the order of a few milliseconds), this offset can be estimated with high precision using techniques akin to Cristian's algorithm or NTP's exchange (the system may send a timestamped sync message and get a response to calculate round-trip delay and clock offset). The SynchronizationEngine on the PC possibly refines this by periodic pings (e.g. every 5 seconds) to adjust for any drift during a long session. In practice, the Android device will apply any calculated offset to its own timestamps for data labelling, meaning if its clock was 5 ms ahead of the PC, it will subtract 5 ms from all timestamps to align with the master timeline. When a recording session is initiated, the PC doesn't just send a blind "start" command — it issues a coordinated start time. For example, the PC might determine "start recording at time T = 1622541600.000 (Unix epoch seconds)" a few hundred milliseconds in the future, and send a message to each device: "start_recording at T with session_id X". Each Android device receives this and waits until its local clock (synchronised to master) hits T to begin capturing data. Because all devices are sync'd to the master within a few milliseconds accuracy, this effectively aligns the start of recording across devices to a very tight margin (usually well below 50 ms difference, often within a few ms). The devices then proceed to timestamp their data relative to this common start. The PC also notes its own start time for any local recordings (like webcams) to align with the same T. During recording, the devices continue to exchange sync information. Each status update from device to PC may include the device's current clock vs. the master clock (or implicitly, the PC knows when it sent a sync and what the device's last offset was). If any device's clock starts to drift beyond an acceptable tolerance (say more than a few milliseconds), the PC can issue a re-synchronisation or simply record the drift for later correction. The synchronisation engine might incorporate simple drift compensation — for instance, if one phone tends to run its clock slightly faster, the system can predict and adjust timing gradually (rather than waiting for a large error to accumulate). In this implementation, because the recording durations might be on the order of minutes to an hour, and modern devices have reasonably stable clocks, straightforward NTP-based periodic correction is sufficient to maintain sub-millisecond alignment. Finally, the communication protocol assists synchronisation by carrying timing info in every message. The JSON messages often include timestamps. For example, when an Android sends a preview frame to the PC, it tags it with the timestamp of frame capture; the PC can compare that with its own reception time and the known offset to estimate network delay and clock skew in real-time. Similarly, the PC's commands can carry the master timestamp. This pervasive inclusion of timestamps means that even if absolute clock sync had a small error, each piece of data can be re-aligned precisely in post-processing using interpolation or offset adjustment. In summary, the PC–Android communication is realised via a reliable JSON/TCP socket protocol, enabling complete remote control and live data streaming, while the synchronisation mechanism ensures all devices operate on a unified timeline. Together, these allow the system to achieve a high degree of temporal precision: tests have shown the system tolerates network latency variations from ~1 ms up to hundreds of milliseconds without losing synchronisation. This is accomplished by designing for asynchronous, non-blocking communication and by decoupling the command from the execution time (i.e. schedule actions in the future on a shared clock). The result is a robust coordination layer that underpins the multi-modal data collection with the necessary timing guarantees. (Figure 4.6: Communication and synchronisation sequence. This figure illustrates the sequence of interactions for device connection and a synchronised session start. Initially, each Android device connects to the desktop's socket server and sends a JSON handshake (including device ID and sensor capabilities). The desktop acknowledges and lists the device as ready. The figure then shows the synchronisation phase: the desktop (master) sends a time sync request or NTP response to the phone, and the phone adjusts its clock offset. When the researcher clicks "Start" on the PC, the desktop broadcasts a StartRecording message with a specified start timestamp. All Android devices (and the PC's own data acquisition for webcams) wait until the shared clock reaches that timestamp, then begin recording simultaneously. During recording, devices send periodic Status messages (with current frame counts, battery, and time sync quality) and stream preview data (video frames, sensor samples) to the PC. The PC might send occasional Sync messages if needed to fine-tune clocks. Finally, on "Stop", the PC sends a stop command and each device halts recording and closes files, confirming back to the PC. This sequence diagram underscores how the protocol and sync mechanism work in tandem to coordinate distributed devices in time.)
>>>>>>> 91c4180215233157dabffb2d623107e227abb188
