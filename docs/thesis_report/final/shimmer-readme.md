# Shimmer3 GSR+ Android SDK Integration Guide

## Overview

The **Shimmer3 GSR+** is a wearable wireless sensor used for real-time
physiological signal acquisition, particularly **galvanic skin response
(GSR)** (also known as electrodermal activity,
EDA)[\[1\]](https://www.shimmersensing.com/product/shimmer3-gsr-unit/#:~:text=The%20Shimmer3%20GSR%2B%20,clip%20or%20optical%20pulse%20probe).
It monitors the electrical conductance of the skin via two electrodes
attached to the fingers; changes in skin moisture (e.g. due to sweat
gland activity from stress or arousal) alter this conductance, allowing
measurement of emotional arousal and sympathetic nervous system
activity[\[2\]](https://www.shimmersensing.com/product/shimmer3-gsr-unit/#:~:text=The%20Galvanic%20Skin%20Response%20Sensor,increasing%20skin%20conductance)[\[3\]](https://www.neuralsense.com/tech#:~:text=Galvanic%20Skin%20Response).
The Shimmer3 GSR+ unit also supports an optical pulse sensor (PPG) via a
3.5mm jack, which can be used (with an ear-clip or finger probe) to
capture photoplethysmogram signals for heart rate
estimation[\[4\]](https://www.shimmersensing.com/product/shimmer3-gsr-unit/#:~:text=preamplification%20for%20one%20channel%20of,clip%20or%20optical%20pulse%20probe)[\[5\]](https://www.shimmersensing.com/support/wireless-sensor-networks-faqs/#:~:text=In%20addition%20to%20the%20GSR,HR%20algorithm%20is%20applied).
In addition, the Shimmer3 platform includes an on-board inertial
measurement unit (IMU), enabling up to 10 degrees-of-freedom motion data
if
needed[\[6\]](https://www.shimmersensing.com/product/shimmer3-gsr-unit/#:~:text=Shimmer%20GSR%2B%20sensor%20monitors%20skin,increasing%20skin%20conductance).
All signals can be streamed wirelessly in real time to a host device (or
logged to an SD card on the Shimmer) for
analysis[\[7\]](https://www.shimmersensing.com/product/shimmer3-gsr-unit/#:~:text=Real,Storage).
In summary, the Shimmer3 GSR+ is a compact, battery-powered sensor that
provides high-quality GSR data (skin conductance or resistance) along
with optional PPG and motion signals, making it suitable for mobile
psychophysiological research and biometric data collection.

## Project Scope

The **Shimmer3 GSR+ Android SDK/API** is a software toolkit that enables
Android applications to communicate with Shimmer3 devices and capture
their sensor data in real time. The SDK abstracts the low-level
Bluetooth communication and sensor packet parsing, providing developers
with high-level interfaces to **connect to Shimmer3 GSR+ sensors,
configure their settings, and stream GSR data live** into an
app[\[8\]](https://github.com/ShimmerEngineering/ShimmerAndroidAPI#:~:text=Introduction).
Using this API, an Android app can start and stop GSR signal acquisition
on the Shimmer, adjust parameters (such as the GSR measurement range or
sampling rate), and retrieve the sensor readings in calibrated units.
The primary purpose is to facilitate real-time data collection from the
Shimmer3 on Android devices -- for example, an app can display live GSR
waveforms, log data for later analysis, or feed the signals into
algorithms (e.g. for stress detection). The SDK supports
**bi-directional communication** with the Shimmer: the app can send
commands (to configure sensors, LED indicators, etc.) and the Shimmer
sends back sensor packets at the chosen sample rate. Under the hood, the
Shimmer3 GSR+ uses a Bluetooth 2.1 + EDR radio (RN42
module)[\[9\]](https://www.shimmersensing.com/support/wireless-sensor-networks-faqs/#:~:text=,Does%20Shimmer%20Use)
for wireless data, so the SDK manages a classic Bluetooth SPP
connection. In recent revisions (Shimmer3 R), **Bluetooth Low Energy
(BLE)** is also
supported[\[10\]](https://github.com/buccancs/fyp-gsr-windows/blob/2d41c241dfeccbb9f5dc0b582255f8b67c8e0ec6/docs/android_research.tex#L26-L34)【12†L388-L396**,
but the API abstracts these details. Overall, the scope of the SDK is to
provide a** reliable, real-time link\*\* between Shimmer3 hardware and
Android software, enabling researchers to integrate GSR/EDA signals into
mobile apps for data logging, biofeedback, or synchronized multimodal
experiments.

## Installation

To integrate the Shimmer SDK into your Android project, you can use
**Gradle dependencies** or a manual library import:

- **Gradle (GitHub Packages/JFrog):** The Shimmer Android API is
  distributed as AAR artifacts. First, add Shimmer's Maven repository to
  your Gradle settings. For example, in your module's `build.gradle`
  repositories section include:

<!-- -->

    maven { 
        url "https://shimmersensing.jfrog.io/artifactory/ShimmerAPI" 
    }

Then add the Shimmer SDK dependencies. The Shimmer API consists of
several components, including the instrument driver and a Bluetooth
manager. For instance, you can include:

    implementation(group: "com.shimmersensing", name: "ShimmerAndroidInstrumentDriver", version: "3.0.74", ext: "aar")
    implementation(group: "com.shimmersensing", name: "ShimmerBluetoothManager", version: "0.9.42beta")
    implementation(group: "com.shimmersensing", name: "ShimmerDriver", version: "0.9.138beta")

Ensure the versions match the latest release (as of writing,
3.0.73/3.0.74 are recent beta
versions[\[11\]](https://github.com/ShimmerEngineering/ShimmerAndroidAPI#:~:text=Important%20,Packages)[\[12\]](https://github.com/ShimmerEngineering/ShimmerAndroidAPI#:~:text=dependencies%3A)).
Including these in Gradle will download the SDK AARs from Shimmer's
repository. (Note: you may need to supply credentials or a GitHub token
if the packages are private; refer to Shimmer's documentation on
accessing their GitHub Packages.)

- **Manual Import:** Alternatively, you can obtain the Shimmer Android
  API library from the official website or source code. Shimmer provides
  a downloadable AAR for the Android API (e.g.,
  *ShimmerAndroidAPI-v3.0-beta.aar*). If you have this file (or built
  the SDK from source), add it to your project's `libs/` folder and
  include it in the Gradle dependencies:

<!-- -->

    implementation files("libs/ShimmerAndroidAPI-v3.0.aar")

You should also include any additional required libraries that come with
the SDK (for example, the API may depend on `ShimmerDriver` and others
as separate AARs if not bundled). After adding, sync your Gradle project
so that the SDK classes are available.

**Compatibility:** The Shimmer API is designed for Android Studio
(Gradle) projects and has been updated to support AndroidX and API level
31+. If you encounter dependency issues, check the Shimmer wiki on
migrating to
AndroidX[\[11\]](https://github.com/ShimmerEngineering/ShimmerAndroidAPI#:~:text=Important%20,Packages).
It's also recommended to use Java 8 or higher and enable multidex if
your app hits the 64K method limit (the Shimmer library is fairly
large).

Once installed, you can reference the Shimmer classes (in the package
`com.shimmerresearch.*`) in your app code. The SDK comes with example
modules (e.g., *shimmerBasicExample*) -- reviewing those can help ensure
you included everything correctly.

## Permissions

Because Shimmer3 devices communicate via Bluetooth, your Android app
needs to declare and request the appropriate permissions:

- **Bluetooth Permissions:** In the app **manifest**, include
  `<uses-permission android:name="android.permission.BLUETOOTH" />` and
  `<uses-permission android:name="android.permission.BLUETOOTH_ADMIN" />`
  (for older Android versions). For **Android 12 (API 31)** and above,
  you must instead declare the new permissions
  `<uses-permission android:name="android.permission.BLUETOOTH_SCAN" android:usesPermissionFlags="neverForLocation"/>`
  and
  `<uses-permission android:name="android.permission.BLUETOOTH_CONNECT" />`
  to scan for and connect to Bluetooth
  devices.
  (If your app will *advertise* or host a GATT server, also add
  `BLUETOOTH_ADVERTISE`.) The `neverForLocation` flag on SCAN indicates
  you are not using Bluetooth scans to derive location information.

- **Location Permission:** On Android 6.0 through Android 12, the system
  requires location access for Bluetooth device discovery. This is a
  security measure because BLE scans can be used to infer location. **If
  your Shimmer integration performs device scanning** (i.e., finding
  nearby unpaired Shimmer devices), you need to request
  `ACCESS_FINE_LOCATION` (or coarse) at
  runtime.
  In Android 12+, if you use the new Bluetooth permissions, you
  technically declare that scans are not for location (via the flag
  above), but in practice you should still prompt the user to enable
  location services during a BLE scan, as it may be needed for discovery
  mode. If your app only connects to **already-paired devices by known
  MAC address**, you may not need location permission; however, it's
  common to include a scanning feature to let users pick their Shimmer
  device.

- **Enable Bluetooth:** Your code should handle the case where the
  phone's Bluetooth is off. Before connecting, check
  `BluetoothAdapter.getDefaultAdapter().isEnabled()`. If it's off,
  prompt the user to enable it. Typically, you can use an
  `ACTION_REQUEST_ENABLE` intent to bring up the system dialog to turn
  on
  This isn't a "permission" per se, but a necessary user action.

- **Other Permissions:** Generally, no other special permissions are
  needed solely for using the Shimmer API. The GSR+ sensor streams data
  via Bluetooth; it does not require camera, storage, etc. (Unless your
  app separately needs those for other features, like saving files or
  using the phone camera, which would require their own permissions.)

**Requesting at Runtime:** Remember that for **dangerous permissions**
like `BLUETOOTH_SCAN`, `BLUETOOTH_CONNECT`, and `ACCESS_FINE_LOCATION`,
you must request them at runtime on Android 6.0+. This means you should
check `checkSelfPermission` and if not granted, call
`requestPermissions(...)` to ask the user. The Shimmer SDK's example app
demonstrates this -- for instance, it checks for `BLUETOOTH_CONNECT` and
location permission on startup and requests them if
Ensure the user grants permissions *before* you attempt to scan or
connect, or your calls will fail (and likely throw an exception or
return no results).

## Getting Started (Connecting & Streaming)

With the SDK integrated and permissions in place, you can now connect to
a Shimmer3 GSR+ and begin streaming data. The general workflow is:

**1. Initialize the Shimmer object or manager:** The SDK provides a
`Shimmer` class (representing a device connection) and a higher-level
`ShimmerBluetoothManagerAndroid` for multi-device management. For a
single device, you can directly use `Shimmer`. Typically you instantiate
it with a constructor specifying the context, a data handler, device
name, sampling rate, and sensor settings. For example:

    // Create a Handler to process incoming data (runs on UI thread in this example)
    Handler shimmerHandler = new Handler(Looper.getMainLooper()) {
        @Override
        public void handleMessage(Message msg) {
            if (msg.what == Shimmer.MESSAGE_READ) {
                // A new sensor data packet was received
                ObjectCluster cluster = (ObjectCluster) msg.obj;
                // (Data extraction shown below)
            } else if (msg.what == Shimmer.MESSAGE_STATE_CHANGE) {
                // Connection state updates (connected, disconnected, etc.)
            }
        }
    };

    // Configure which sensors to enable on the Shimmer (GSR, plus PPG in this case)
    int sensorMask = Shimmer.SENSOR_GSR | Shimmer.SENSOR_HEART;  // GSR and PPG (Pulse)

    // Choose GSR range setting (0–3 for fixed ranges, or 4 for auto-range)
    int gsrRange = 4;  // 4 = Auto Range (the device will auto-select the best range)

    // Instantiate the Shimmer device object
    Shimmer shimmerDevice = new Shimmer(
            getApplicationContext(),           // Android context
            shimmerHandler,                    // Handler for data and events
            "ShimmerGSR",                      // Device nickname (can be any string)
            128.0,                             // sampling rate in Hz (e.g. 128Hz)
            0,                                 // accel range (not used here, 0 = ±2g default)
            gsrRange,                          // GSR range setting
            sensorMask,                        // sensors to enable (bitmask)
            false                              // continuous sync (for packet syncing, false is fine)
    );

In the above code, we prepared a `Handler` to receive messages from the
Shimmer API -- the SDK will send sensor data through `MESSAGE_READ`
messages, containing an `ObjectCluster` with the sensor values. We set
the **sampling rate** to 128 Hz (common for EDA research). We enabled
the GSR sensor and the PPG ("Heart") sensor; the Shimmer's sensor bitmap
constants like `SENSOR_GSR` are ORed together to enable multiple
channels. We also set `gsrRange = 4` which tells the Shimmer to use its
**auto-ranging** feature for GSR (meaning the device will switch among
its 4 hardware resistance ranges to best capture the signal without
saturation). If needed, you could choose a fixed range (0 through 3
corresponding to 10 kΩ--56 kΩ, 56--220 kΩ, 220--680 kΩ, or
680 kΩ--4.7 MΩ
respectively[\[15\]](https://github.com/ShimmerEngineering/Shimmer-Java-Android-API/blob/563dd5b9bc88baf55d5ef479778f3dd017a7c9cb/ShimmerDriver/src/main/java/com/shimmerresearch/driver/Configuration.java#L32-L40)).
For most use cases, auto-range is convenient. The accelerometer range
parameter is not relevant unless you enable motion sensors (we left it
at default). The `Shimmer` object now encapsulates our configuration for
the device.

**2. Connect to the Shimmer device:** Each Shimmer has a Bluetooth MAC
address (e.g., printed on the device or discoverable via scanning). To
connect, call the `connect()` method with the address. For example:

    String deviceMAC = "00:07:80:4D:2B:01";  // replace with your Shimmer's MAC
    shimmerDevice.connect(deviceMAC, "default");

The second parameter `"default"` specifies which Bluetooth library to
use (the Shimmer API supports an alternative "gerdavax" library for
certain older devices; for Shimmer3, `"default"` is
appropriate)[\[16\]](https://github.com/jhallard/BioSig-for-Android/blob/f803f22e485d453516b671cd3692c79a6c898858/src/com/shimmerresearch/driver/Shimmer.java#L44-L52)[\[17\]](https://github.com/jhallard/BioSig-for-Android/blob/f803f22e485d453516b671cd3692c79a6c898858/src/com/shimmerresearch/driver/Shimmer.java#L48-L56).
This will initiate a Bluetooth SPP connection in the background. The
Shimmer's internal firmware will perform a handshake and initialization
sequence once the link is established. The `shimmerHandler` we provided
will get a `MESSAGE_STATE_CHANGE` message when the connection state
updates. Specifically, when fully connected and initialized, the state
will change to `Shimmer.MSG_STATE_FULLY_INITIALIZED` (value
3)[\[18\]](https://github.com/jhallard/BioSig-for-Android/blob/f803f22e485d453516b671cd3692c79a6c898858/src/com/shimmerresearch/driver/Shimmer.java#L18-L26)[\[19\]](https://github.com/jhallard/BioSig-for-Android/blob/f803f22e485d453516b671cd3692c79a6c898858/src/com/shimmerresearch/driver/Shimmer.java#L20-L28).
You might wait for this state before allowing the user to start
streaming.

**Note:** If your Shimmer device is not yet **paired** with the Android
device, the connection attempt may fail. It's often best to pair via
Android Settings or a scan dialog first (see *Troubleshooting* below for
pairing instructions). The Shimmer3 uses a default PIN code **1234** for
-- the SDK can initiate pairing if needed (it will prompt for the PIN).

**3. Start streaming data:** Once connected (i.e., in an initialized
state), you can instruct the Shimmer to begin streaming sensor data.
This is done by calling:

    shimmerDevice.startStreaming();

After this call, the Shimmer hardware starts sampling its sensors at the
configured rate (128 Hz) and sends packets to the phone. The
`shimmerHandler` will begin receiving `MESSAGE_READ` messages
continuously (multiple per second, depending on rate). Each
`MESSAGE_READ` contains an `ObjectCluster` object, which is essentially
a timestamped bundle of all sensor readings captured at that moment. For
example, if GSR and PPG are enabled, each packet will include a GSR
measurement and a PPG measurement (and a timestamp, plus any other
active channels). The handler's job is to extract the values and use
them (e.g., update UI or save to file).

**4. Extracting GSR data:** The Shimmer `ObjectCluster` organizes sensor
data by sensor name and data format. The SDK typically provides both raw
and calibrated values. For GSR, the key sensor name is **"GSR"** for the
calibrated skin resistance, and "GSR Raw" for the raw ADC reading. You
can retrieve data by name, for example:

    @Override 
    public void handleMessage(Message msg) {
        if (msg.what == Shimmer.MESSAGE_READ) {
            ObjectCluster cluster = (ObjectCluster) msg.obj;
            // Get calibrated GSR value (in kΩ by default)
            Collection<FormatCluster> gsrFormats = cluster.getData(Configuration.Shimmer3.ObjectClusterSensorName.GSR);
            if (gsrFormats != null && !gsrFormats.isEmpty()) {
                FormatCluster calibratedGsr = ObjectCluster.returnFormatCluster(gsrFormats, "CAL"); 
                double gsrValue = calibratedGsr.data; 
                // gsrValue is the skin resistance in kilo-ohms
            }
            // (Likewise, you could get PPG in a similar way using SensorName.HEART or PPG)
        }
    }

In the above snippet, `cluster.getData(...)` returns all formats of the
GSR measurement. We then filtered for the calibrated value ("CAL"). The
**Shimmer API auto-calibrates GSR** using an internal formula to convert
the raw ADC reading to resistance in
kΩ[\[21\]](https://github.com/jhallard/BioSig-for-Android/blob/f803f22e485d453516b671cd3692c79a6c898858/src/com/shimmerresearch/driver/Shimmer.java#L116-L123).
For example, if the raw reading is converted using the calibration
factors *p1* and *p2*, the formula is
`GSR_kOhms = (1 / (p1*raw + p2)) * 1000`[\[22\]](https://github.com/jhallard/BioSig-for-Android/blob/f803f22e485d453516b671cd3692c79a6c898858/src/com/shimmerresearch/driver/Shimmer.java#L120-L123),
yielding a result in kilo-ohms. Thus, `gsrValue` above would be, say,
"432.5" meaning 432.5 kΩ skin resistance at that moment. Higher
conductance (sweatier skin) corresponds to lower resistance. If you
prefer skin conductance in microsiemens (µS), you can convert by σ =
(1/R) \* 1e6, where R is in ohms -- e.g., 432.5 kΩ = 2.31 µS. The SDK
focuses on resistance, but you can derive conductance easily in
post-processing.

Each `ObjectCluster` also contains a timestamp. Typically, you can
retrieve the device's timestamp with
`cluster.getData(Configuration.Shimmer3.ObjectClusterSensorName.TIMESTAMP)`
(or it might be labeled "Time Stamp"). This represents the Shimmer's
internal clock for the
If synchronizing with other data (like phone sensors or multiple
Shimmers), you may use this along with system time -- see *Timestamping*
below or Shimmer's guidance on synchronization.

**5. Stopping and cleanup:** To stop streaming, call
`shimmerDevice.stopStreaming()`. You might do this when the user ends a
recording session. After stopping, you can keep the device connected
(perhaps to start again), or you can disconnect by
`shimmerDevice.disconnect()`. It's good practice to disconnect in a
`onPause()` or `onDestroy()` if your app is closing, to free the
Bluetooth channel. The Shimmer device will automatically stop sampling
when disconnected.

**Example Usage Summary:** The simplest usage pattern for one device is:

    Shimmer shimmer = new Shimmer(ctx, handler, ...config...);
    shimmer.connect(macAddress, "default");
    // wait for MSG_STATE_FULLY_INITIALIZED (in handler)
    shimmer.startStreaming();
    // ... receive data in handler ...
    shimmer.stopStreaming();
    shimmer.disconnect();

For multiple devices, the SDK provides `ShimmerBluetoothManagerAndroid`
which can manage a collection of Shimmer objects and handle connections
simultaneously. In multi-device mode, you would create a manager, add
each `Shimmer` to it, and use the manager's connect/start commands. The
principle is similar but with more bookkeeping (ensuring each device has
a unique handler or identifying the source of each message -- the
ObjectCluster contains the device MAC, so you can differentiate
The **Shimmer API does support multi-streaming** (e.g., two Shimmer GSR+
units at once) provided the Android device can handle the Bluetooth

## Data Handling (GSR Data Format and Visualization)

**Data Format:** GSR data from the Shimmer3 GSR+ can be obtained in raw
or calibrated form. The raw signal is essentially the ADC reading from a
resistor network (12-bit or 16-bit depending on firmware), and the
calibrated form is the skin resistance in kΩ as discussed. When using
the SDK's high-level methods (like `ObjectCluster.getData("GSR")`), you
are typically getting the calibrated resistance. If needed, you can also
retrieve **raw GSR** by using the key `"GSR Raw"` or by looking for the
format labeled "RAW". The Shimmer device also computes an intermediate
value called **GSR Resistance** (sometimes labeled `"GSR Res"` in older
APIs) which may be the same as the calibrated GSR in most contexts. The
**GSR range setting** affects the analog front-end gain: if you manually
choose a range (0--3), the raw values will have different scaling. In
auto-range mode, the Shimmer's firmware will dynamically switch ranges
and apply the correct calibration to always output a consistent
resistance
value[\[21\]](https://github.com/jhallard/BioSig-for-Android/blob/f803f22e485d453516b671cd3692c79a6c898858/src/com/shimmerresearch/driver/Shimmer.java#L116-L123).
This means the `ObjectCluster` "CAL" GSR values should already reflect
the true skin resistance regardless of range.

**Packet Structure:** Each data packet from Shimmer3 contains a
timestamp and the enabled sensor channels. For GSR+ with PPG, a packet
includes: timestamp, GSR raw, GSR resistance (or calibrated), and PPG
value (raw or perhaps a derived HR if using certain firmware). These are
represented in the `ObjectCluster` as entries such as *Time Stamp*,
*GSR*, *PPG* etc. The timestamp is typically in milliseconds relative to
device start, and it resets when you stop/start streaming. If precise
alignment with phone time is needed, you might record a reference (e.g.,
note SystemClock when streaming started and correlate).

**Accessing GSR Values:** We showed above how to get the GSR value in
code. Another approach the SDK allows is using the configuration
constants. For example, the SDK defines
`Configuration.Shimmer3.ObjectClusterSensorName.GSR` as the standard key
for
GSR[\[28\]](https://github.com/ShimmerEngineering/Shimmer-Java-Android-API/blob/563dd5b9bc88baf55d5ef479778f3dd017a7c9cb/ShimmerDriver/src/main/java/com/shimmerresearch/driver/Configuration.java#L80-L88).
You can use helper methods like
`ObjectCluster.returnFormatCluster(cluster, "GSR", "CAL")` to directly
get the calibrated number. If you needed the raw ADC for some reason
(e.g., for custom filtering), you could request `"GSR", "RAW"`
similarly. But generally, the calibrated GSR is what you'll use for
analysis (in kΩ).

**Data Logging:** For storage or offline analysis, you can log the GSR
data along with timestamps. A simple method is to create a CSV file. For
example, write a header: `Time(ms), GSR_kOhm, PPG`. Then on each
`MESSAGE_READ`, get the timestamp and sensor values, and append a line.
You could use the device's timestamp or the phone's
System.currentTimeMillis(); each has pros/cons (device timestamp is
monotonic from stream
while system time aligns with real-world clock). The Shimmer examples
show writing CSV lines by extracting values from the
If streaming at 128 Hz, note that that is 128 lines per second; using a
buffered writer or batching writes (e.g., write 128 lines at a time) is
wise to avoid I/O overhead. Also consider the data volume: GSR is just
one number per sample, so 128 Hz \~ 128 samples/sec is quite low (easily
under 10 KB/s). Even with PPG and accel, it remains manageable.

**Visualization:** To visualize GSR in real time, you can update a UI
element (like a graph view) each time a new sample comes in. However,
updating on every single sample at 128 Hz can be too fast for smooth UI
drawing. A common approach is to buffer a few samples or downsample for
display. For instance, update the graph at, say, 10 Hz with the latest
value or an average of the last 10 samples. This gives a responsive
display without overloading the UI thread. The Shimmer API's
`PlotManager` (if included) might assist in plotting data
streams[\[30\]](https://github.com/ShimmerEngineering/ShimmerAndroidAPI/wiki/Quick-Start-Guide#:~:text=).
Otherwise, you can use any chart library or even a simple custom Canvas
drawing. Typically, GSR signals are displayed as a slowly varying
waveform; you may plot time on the X-axis and resistance (or
conductance) on the Y-axis. The values can range widely (from \~10 kΩ
(high arousal) to \~1000 kΩ (very calm/dry), depending on the person and
electrode contact), often plotted in a scaled manner.

**Processing:** If you intend to do real-time processing (e.g.,
smoothing the GSR or detecting peaks), you can do so in the handler or,
better, offload to a background thread. For example, you might maintain
a rolling average to compute a baseline and detect phasic responses
(sudden drops in resistance indicating a skin conductance response). The
SDK doesn't provide specific algorithms for EDA analysis -- you would
implement those or use third-party libraries. But it gives you the raw
data needed for such analysis.

**Multiple Channels:** If you have enabled other channels (like PPG or
accelerometer), the ObjectCluster will carry those too. The extraction
is analogous: e.g., `cluster.getData("PPG")` for the pulse sensor
reading. PPG from the GSR+ unit comes as a raw infrared light intensity
value. You could process it to compute heart rate or use the Shimmer's
EXG module for HR if available. Ensure to label and log each channel
accordingly so data columns don't get mixed up.

Finally, if you wish to visualize data after the fact, the CSV logs can
be imported into tools like Excel, MATLAB, or Python for plotting. The
**Shimmer Consensys** software is another option for live viewing, but
since you're integrating into your own app, your app takes over that
role.

## Integration with `bucika_gsr` App Architecture

Integrating the Shimmer3 GSR+ SDK into the `bucika_gsr` **Android
application** involves fitting the streaming logic into the app's
existing architecture. In our project, the app is structured as a
multimodal data collection system (combining thermal camera, RGB camera,
and GSR sensor
inputs)[\[10\]](https://github.com/buccancs/fyp-gsr-windows/blob/2d41c241dfeccbb9f5dc0b582255f8b67c8e0ec6/docs/android_research.tex#L26-L34).
The Shimmer integration is handled by a dedicated module -- think of it
as a **GSR Sensor Service** -- that manages the Shimmer device
connection and data flow. There are two common approaches to incorporate
this:

- **Background Service Approach:** You can create an Android Service
  (either started or bound service) whose responsibility is to connect
  to the Shimmer and keep receiving data, independent of UI lifecycle.
  This is useful because GSR data collection might need to run
  continuously even if the user navigates away from the UI. In
  `bucika_gsr`, for example, one could implement a `GsrCaptureService`
  that starts when a recording session begins. This service would
  initialize the Shimmer (as shown above), handle the connection, and
  start streaming. The service could then broadcast the incoming data or
  use a callback interface to pass GSR readings to other app components
  (such as a UI fragment that displays the values, or a logger that
  writes to file). Running as a service ensures the data acquisition
  isn't interrupted by configuration changes or UI closures. In
  practice, the Shimmer API even provides a helper (`ShimmerService`
  class in the SDK) that could be adapted -- but a custom implementation
  gives more control. If using a service, consider marking it as a
  foreground service if it needs to run for long periods (to avoid being
  killed by the system; you'd show a notification during recording).

- **Dependency Injection (DI) Approach:** If your app uses a dependency
  injection framework (like Dagger/Hilt), you can set up the Shimmer
  components to be provided as singletons and injected where needed. For
  instance, you might define a `ShimmerModule` that provides a
  `ShimmerBluetoothManagerAndroid` instance. The `bucika_gsr` app could
  have a singleton manager allowing multiple parts of the app to obtain
  GSR data. You could also inject a `ShimmerRecorder` object (see below)
  into, say, a ViewModel that coordinates the data recording. DI ensures
  that there's a single, app-wide source of Shimmer data that any
  component can access (e.g., the UI layer observing LiveData for GSR,
  and a repository layer saving data).

In our architecture, we designed a `ShimmerRecorder` class to
encapsulate all Shimmer functionality (scanning, connecting, streaming,
This class can be treated as a **module** in the app's logic. For
example, the `ShimmerRecorder` might be injected into an Activity or a
higher-level controller that orchestrates the various sensors during a
recording session. When the user starts a session, the app calls methods
on `ShimmerRecorder` like `connectDevices()` and
Internally, the ShimmerRecorder uses the SDK to manage the connection(s)
and data. It might spin up threads or use coroutines to handle the
incoming data stream, and it provides callbacks or LiveData updates with
the latest GSR values. By isolating the Shimmer logic in this module,
the rest of the app can remain agnostic to Bluetooth specifics -- they
just receive GSR data updates (for instance, the Synchronization manager
in `bucika_gsr` can then timestamp these alongside camera frames).

**Placement in Architecture:** In the `bucika_gsr` app (which features
multiple modalities), the Shimmer GSR module runs in parallel with the
camera modules. All are coordinated by a central **Synchronization
Manager** that ensures data from different threads are timestamped and
aligned[\[10\]](https://github.com/buccancs/fyp-gsr-windows/blob/2d41c241dfeccbb9f5dc0b582255f8b67c8e0ec6/docs/android_research.tex#L26-L34).
Concretely, the GSR module (service) receives each Shimmer sample,
immediately tags it with a timestamp from a common clock (e.g.,
`SystemClock.elapsedRealtimeNanos()` when
received)[\[10\]](https://github.com/buccancs/fyp-gsr-windows/blob/2d41c241dfeccbb9f5dc0b582255f8b67c8e0ec6/docs/android_research.tex#L26-L34)[\[35\]](https://github.com/buccancs/fyp-gsr-windows/blob/2d41c241dfeccbb9f5dc0b582255f8b67c8e0ec6/docs/android_research.tex#L46-L49),
and then either logs it or streams it out. In our implementation,
because the Shimmer provides its own timestamp, we could use that and
then map it to the common timeline (e.g., subtract the start offset),
but a simpler method we adopted is to use the phone's time on reception
since Bluetooth latency is low and consistent (on the order of 10--20
ms)[\[35\]](https://github.com/buccancs/fyp-gsr-windows/blob/2d41c241dfeccbb9f5dc0b582255f8b67c8e0ec6/docs/android_research.tex#L46-L49).
Either way, the app's architecture treats the Shimmer data as another
asynchronous data source feeding into the overall dataset.

**Service Modules vs DI:** Note that these approaches are not mutually
exclusive -- you can use DI *and* have the actual work done in a
service. For example, you might inject the `ShimmerRecorder` into a
`RecordingService` that runs in the background. The `RecordingService`
would call `shimmerRecorder.start()` and handle the lifecycle (stop on
end, handle errors, etc.), while the DI ensures that any other component
(like an Activity or a ViewModel) can get references to the same
recorder to query status or get real-time updates. If using Hilt, the
service could be annotated with `@AndroidEntryPoint` and inject a
ViewModel-scoped recorder.

**Integration Points in bucika_gsr:** Depending on how `bucika_gsr` is
structured, the Shimmer connection might fit in as follows: - If there
is a **controller class** for sensors (like a `SessionManager`), that
class would instantiate or obtain the Shimmer SDK object at start, then
trigger connect/stream. - If using an MVVM pattern, a **ViewModel**
could initiate the Shimmer connection when the user presses "Start". The
ViewModel would then expose the live GSR value via a `LiveData<Double>`
that the UI observes to update a graph. - If using a **Service**, the UI
could bind to the service and receive data through a callback interface
or broadcasts. For example, the service could send a broadcast
`ACTION_GSR_UPDATE` with an extra for current value, or use
Messenger/aidl for a more robust interface. The advantage is the service
can continue running if the app goes to background (useful for long
recordings).

In `bucika_gsr`, we integrated the Shimmer in a way that it **starts and
stops in sync with the other modalities**. For instance, when starting a
recording, the app (through a controller or service) calls Shimmer
connect & stream at the same time as it starts the camera recordings, so
that all data aligns from the start
signal[\[36\]](https://github.com/buccancs/fyp-gsr-windows/blob/2d41c241dfeccbb9f5dc0b582255f8b67c8e0ec6/docs/android_research.tex#L30-L38)[\[37\]](https://github.com/buccancs/fyp-gsr-windows/blob/2d41c241dfeccbb9f5dc0b582255f8b67c8e0ec6/docs/android_research.tex#L40-L48).
The GSR service thread continuously buffers GSR samples with timestamps,
and the Synchronization Manager takes those along with video frame
timestamps to ensure they can be merged later. At the end of a session,
a stop signal stops the camera capture and calls
`shimmerDevice.stopStreaming()`. We also implemented fail-safes: if the
Shimmer disconnects mid-session (e.g., battery died or out of range),
the app logs an error and can attempt to reconnect or at least notify
the user.

One helpful feature of the Shimmer SDK for integration is the
**ShimmerBluetoothDialog** -- a built-in UI dialog that lists paired
Shimmer devices and can scan for new
We used this during setup: the user can press "Add GSR Device" which
launches the ShimmerBluetoothDialog, selects the Shimmer3 from the list,
and the dialog returns the MAC address to our
We then store that MAC (maybe in SharedPreferences or in the Session
config) and use it for connecting. This simplifies device selection UX.
In code, it's invoked via
`startActivityForResult(new Intent(this, ShimmerBluetoothDialog.class), REQUEST_SHIMMER)`,
and on result you get extras like `EXTRA_DEVICE_ADDRESS`. For
`bucika_gsr`, we integrated this into the device setup screen. This is
an example of how the SDK provides not just low-level API but also UI
components to ease integration.

In summary, within the `bucika_gsr` app, the Shimmer3 GSR+ integration
is handled by a dedicated component (service/module) that interfaces
with the Shimmer SDK. This component is started as part of the overall
recording workflow (likely via dependency injection or explicit service
start) and runs concurrently with the other sensor modules (thermal, RGB
cameras). It ensures GSR data is continuously captured and made
available to the rest of the app: - In code, this means using the
Shimmer API to connect and stream, as illustrated earlier. - In
architecture, it means encapsulating that logic such that other parts of
the app don't worry about Bluetooth details -- they just get GSR data
(for example, the UI gets a stream of GSR values to display, and the
data logger gets time-stamped values to write to file). - By utilizing
DI patterns, we ensure the Shimmer connection persists across
configuration changes and is easily accessible wherever needed (e.g.,
injection into both a Service and a ViewModel). By using a Service under
the hood, we ensure the GSR streaming isn't paused if the user switches
activities or the app goes background (important for uninterrupted
data).

This modular integration allows the `bucika_gsr` app to treat Shimmer
GSR data as a plug-and-play input, similarly to how it treats the camera
feeds, resulting in a cohesive synchronized data collection system.

## Troubleshooting & Tips

Working with live Bluetooth sensors can introduce some challenges. Here
are common issues and solutions when using the Shimmer3 GSR+ on Android:

- **Bluetooth Pairing Problems:** If your app cannot connect to the
  Shimmer, first verify the Shimmer is **paired** with the phone.
  Pairing is typically required for Bluetooth Classic devices. You can
  pair via Android Settings (Bluetooth menu) -- the Shimmer will appear
  as e.g. "Shimmer" or "Shimmer3". Select it, and when prompted for a
  PIN, enter **1234** (the default passcode for Shimmer3
  The device's LED will usually indicate pairing (consult Shimmer
  documentation for LED codes). If you try to connect in-app to an
  unpaired Shimmer, newer Android versions might block it or require
  pairing on the fly. The Shimmer SDK's scan dialog can handle pairing
  (it will invoke the system PIN prompt), but if you see connection
  failures, always double-check pairing status. On some phones, you may
  need to remove ("Forget") a previously paired Shimmer and re-pair if
  connections hang.

- **Permissions and Discovery:** As mentioned, not granting the
  necessary permissions will cause failures. If
  `BLUETOOTH_SCAN`/`CONNECT` (or location on older OS) is missing, your
  scan may return 0 devices or `connect()` may throw a
  SecurityException. If your scan isn't finding any devices, ensure that
  **Location Services are turned on** (for BLE discovery, the GPS toggle
  needs to be on even if you have permission, on Android \<12). Also,
  ensure Bluetooth itself is on (it sounds obvious, but apps can only
  prompt -- the user might say "Cancel" on the enable prompt, leaving BT
  off).

- **Connection Stability:** Shimmer devices stream a lot of data over
  SPP. Generally, one Shimmer streaming GSR at 128 Hz is well within
  limits. However, if you enable many sensors at high rates (e.g.,
  3-axis accel at 1 kHz + GSR), you could approach Bluetooth bandwidth
  limits. If you notice data drops (the handler reports packet loss or
  you see gaps in timestamps), you might be hitting throughput limits.
  Shimmer's documentation notes strategies like enabling the **efficient
  data array** mode for better throughput on low-end
  devices[\[40\]](https://github.com/ShimmerEngineering/ShimmerAndroidAPI/wiki/Data-Structure#:~:text=Arrays).
  For GSR+ alone, this usually isn't an issue. But if you do see
  instability: try lowering sample rate (e.g., 51.2 Hz instead of 128
  Hz) or disabling unnecessary channels. Interference in the 2.4 GHz
  band (Wi-Fi) can also occasionally cause Bluetooth packet loss -- keep
  the phone close to the Shimmer (within a few meters ideally) and away
  from heavy Wi-Fi routers if possible during recording. The Shimmer API
  can report packet loss events via a message
  (`MESSAGE_PACKET_LOSS_DETECTED`), and you can monitor
  `shimmerDevice.getPacketReceptionRate()` if needed.

- **Reconnection Strategy:** If the Shimmer goes out of range or battery
  dies during use, the connection will drop. The SDK should send a state
  change indicating disconnect. In your app logic, handle this
  gracefully: perhaps notify the user "Connection lost". To reconnect,
  you may need to call `connect()` again (after coming back in range or
  replacing battery). Sometimes the Bluetooth stack might not clean up
  immediately -- if `connect()` fails, try calling `disconnect()` first
  (even if you think it's disconnected) and then retry. In some cases,
  toggling the phone's Bluetooth off/on helps reset a stuck state.

- **Bluetooth Classic vs BLE:** The Shimmer3 uses Bluetooth Classic by
  default[\[9\]](https://www.shimmersensing.com/support/wireless-sensor-networks-faqs/#:~:text=,Does%20Shimmer%20Use).
  That means the connection process is pairing + RFCOMM. If you have a
  Shimmer3R (BLE), the SDK usage is slightly different (you'd use
  `ShimmerBluetoothManagerAndroid` with BLE mode). Ensure you know which
  one you have. The above instructions assume classic Bluetooth. One
  noticeable difference: for BLE, you definitely need location
  permission and the device won't appear in the "paired devices" list
  but rather needs scanning each time. The SDK in recent versions
  abstracts BLE Shimmers, but if something isn't connecting, verify if
  your Shimmer firmware is BLE-only. The Shimmer wiki has a section on
  Shimmer3R BLE
  support[\[41\]](https://github.com/ShimmerEngineering/ShimmerAndroidAPI/wiki/Quick-Start-Guide#:~:text=).

- **Android Version Quirks:** On Android 11 and above, scanning for
  classic Bluetooth devices (using `BluetoothAdapter.startDiscovery()`)
  also requires location permission. If you use the Shimmer's dialog or
  your own scan code and nothing shows up on Android 11, this is likely
  why. Also, Android 13 tightened some Bluetooth permissions; make sure
  your `targetSdkVersion` and permission requests are aligned with the
  latest requirements. The logcat will often tell you
  "java.lang.SecurityException: Need BLUETOOTH_CONNECT permission..." if
  you missed something. Request and grant those permissions.

- **Data Accuracy and Calibration:** The Shimmer GSR+ comes calibrated
  from the factory (the API uses stored calibration constants `p1, p2`
  for the GSR formula). If you suspect the values are off (e.g., reading
  extremely high or zero when it shouldn't), a few things to check:

- Are the electrodes properly placed with good contact? Dry or
  misattached electrodes can cause readings to peg at the max range
  (e.g., \~4.7 MΩ) or fluctuate with noise.

- Is the GSR channel definitely on? (In code, ensure `SENSOR_GSR` was
  included and that `startStreaming` was called.)

- Verify if auto-range is working: if you use a fixed range and the
  subject's resistance exceeds that range, the readings might saturate.
  Auto-range avoids that by switching -- if you used a fixed range by
  accident (gsrRange not set to 4), try enabling auto.

- There's a troubleshooting step in the Shimmer User Guide where you can
  short the GSR leads together and verify the reading goes to a known
  low value, to ensure the channel is
  functioning[\[42\]](https://shimmersensing.com/wp-content/docs/support/documentation/GSR_User_Guide_rev1.13.pdf#:~:text=3,Baseline)[\[43\]](https://shimmersensing.com/wp-content/docs/support/documentation/GSR_User_Guide_rev1.13.pdf#:~:text=7,References).
  Typically, shorting GSR leads should show near 0 kΩ (very high
  conductance).

- The Shimmer's internal battery level can sometimes be read via
  `SensorBattVoltage` channel. If the battery is very low, sensor
  performance could conceivably degrade or disconnect. Ensure the
  Shimmer is charged (or plugged in via its base) for long sessions.

- **Streaming to External Applications:** If you plan to forward the GSR
  data from the phone to a PC in real-time (for example, for monitoring
  or recording on a server), consider using Wi-Fi or USB tethering for
  the outbound link. Our setup used a custom TCP socket over Wi-Fi to
  send data lines to a
  Trying to use the phone's Bluetooth for both connecting to Shimmer and
  sending data to PC can be problematic (the phone typically can only
  maintain one SPP connection at a time, and BLE + Classic
  simultaneously could strain it). Wi-Fi or cellular is more robust for
  that. If you do use this, just ensure your network sending thread can
  handle the data rate (but as noted, GSR data is not heavy). Also
  implement reconnection or buffering in case network drops, so you
  don't lose sensor data packets.

- **Using Multiple Shimmers:** If you integrate more than one Shimmer
  (say two GSR units on different people), test with each individually
  first, then together. The Shimmer API supports multiple, but more
  devices = more bandwidth. The API's `ShimmerBluetoothManagerAndroid`
  is recommended to manage multiple connections in one
  If you see one device disconnect when the other connects, it could be
  a pairing issue or a collision -- it should not happen under normal
  conditions, but always verify each device has a unique MAC and you
  handle each connection separately in code.

- **Debugging Data:** To ensure you are getting meaningful GSR readings,
  you might output some values to logcat. For example, in the handler,
  `Log.i("ShimmerGSR", "GSR = " + gsrValue + " kΩ")`. This can help
  confirm that the values change when expected (e.g., if someone does a
  quick deep breath or mild exercise, you should see the resistance drop
  (conductance rise) and recover slowly). If you only see a flat line or
  extremely noisy values, revisit the electrode setup and make sure the
  fingers are properly prepared (clean, consistent contact). Also note
  the Shimmer GSR+ uses **dry electrodes** typically; sometimes a small
  amount of electrode gel or water can improve contact if the skin is
  very dry (though dry electrodes are designed to work without gel).

- **Further Resources:** The Shimmer SDK wiki FAQ is useful for specific
  issues. For example, if you encounter an error like "socket might be
  closed" or similar exceptions, the FAQ suggests re-pairing or ensuring
  only one instance of `Shimmer` is using that MAC at a
  The Shimmer user community (forums, etc.) also has Q&A for common
  hurdles (like the StackOverflow question on integrating Shimmer which
  reiterates the need for SPP Bluetooth
  code[\[50\]](https://stackoverflow.com/questions/8085258/integrating-shimmer-with-android-tablet#:~:text=Integrating%20Shimmer%20with%20Android%20Tablet,once%20connected%2C%20transmit%20the)).

By following these troubleshooting tips, you can usually resolve any
integration issues and achieve a stable, real-time GSR data feed in your
Android app. Once set up, the Shimmer3 GSR+ is a robust device that can
provide reliable EDA measurements for research and application
development.

## References

- **Shimmer3 GSR+ Product Page:** *Shimmer3 GSR+ Unit* -- Official
  description and specifications of the GSR+ sensor
  device[\[1\]](https://www.shimmersensing.com/product/shimmer3-gsr-unit/#:~:text=The%20Shimmer3%20GSR%2B%20,clip%20or%20optical%20pulse%20probe)[\[2\]](https://www.shimmersensing.com/product/shimmer3-gsr-unit/#:~:text=The%20Galvanic%20Skin%20Response%20Sensor,increasing%20skin%20conductance).
- **Shimmer Android API GitHub Repository:**
  *ShimmerEngineering/ShimmerAndroidAPI* -- Source code and
  documentation for the Android SDK (BETA) used to communicate with
  Shimmer3
  devices[\[8\]](https://github.com/ShimmerEngineering/ShimmerAndroidAPI#:~:text=Introduction).
  Includes a Quick Start Guide and examples.
- **Shimmer3 GSR+ User Guide (PDF):** *Shimmer GSR+ User Manual* --
  Detailed user manual covering GSR signal acquisition, best practices,
  auto-range explanation, and hardware
  setup[\[42\]](https://shimmersensing.com/wp-content/docs/support/documentation/GSR_User_Guide_rev1.13.pdf#:~:text=3,Baseline)[\[43\]](https://shimmersensing.com/wp-content/docs/support/documentation/GSR_User_Guide_rev1.13.pdf#:~:text=7,References).
- **Android Integration Design (Multimodal):** *Android-Based Multimodal
  Data Acquisition System* -- Research paper (IEEE conference)
  describing an Android app integrating Shimmer3 GSR, thermal camera,
  etc., with synchronization
  methods[\[51\]](https://github.com/buccancs/fyp-gsr-windows/blob/2d41c241dfeccbb9f5dc0b582255f8b67c8e0ec6/docs/android_research.tex#L14-L22)[\[35\]](https://github.com/buccancs/fyp-gsr-windows/blob/2d41c241dfeccbb9f5dc0b582255f8b67c8e0ec6/docs/android_research.tex#L46-L49).
  Provides context on using the Shimmer API in a complex system.
- **Shimmer FAQ -- Bluetooth Details:** *Shimmer Wireless Sensor
  Networks FAQs* -- Shimmer's FAQ page with info on Bluetooth type (RN42
  module, PIN code) and API
  Helpful for troubleshooting pairing and understanding the device's
  wireless interface.
- **Shimmer Java/Android API Documentation:** *Shimmer Java/Android API
  -- Docs & Downloads* -- Official documentation snippet stating the
  API's purpose (streaming data to Android) and listing of related
  software. (Accessible via Shimmer's Docs page and Getting Started
  guides.)
- **Example Code -- Shimmer Basic Example:** The Shimmer SDK includes an
  example app (`shimmerBasicExample`). Key sections of its
  `MainActivity.java` illustrate permission
  device
  and data handling (retrieving GSR from
  Reviewing this code is recommended for practical understanding of the
  API usage.

------------------------------------------------------------------------

[\[1\]](https://www.shimmersensing.com/product/shimmer3-gsr-unit/#:~:text=The%20Shimmer3%20GSR%2B%20,clip%20or%20optical%20pulse%20probe)
[\[2\]](https://www.shimmersensing.com/product/shimmer3-gsr-unit/#:~:text=The%20Galvanic%20Skin%20Response%20Sensor,increasing%20skin%20conductance)
[\[4\]](https://www.shimmersensing.com/product/shimmer3-gsr-unit/#:~:text=preamplification%20for%20one%20channel%20of,clip%20or%20optical%20pulse%20probe)
[\[6\]](https://www.shimmersensing.com/product/shimmer3-gsr-unit/#:~:text=Shimmer%20GSR%2B%20sensor%20monitors%20skin,increasing%20skin%20conductance)
[\[7\]](https://www.shimmersensing.com/product/shimmer3-gsr-unit/#:~:text=Real,Storage)
Shimmer3 GSR+ Unit - Shimmer Wearable Sensor Technology

<https://www.shimmersensing.com/product/shimmer3-gsr-unit/>

[\[3\]](https://www.neuralsense.com/tech#:~:text=Galvanic%20Skin%20Response)
Neuromarketing Technology \| Neural Sense

<https://www.neuralsense.com/tech>

[\[5\]](https://www.shimmersensing.com/support/wireless-sensor-networks-faqs/#:~:text=In%20addition%20to%20the%20GSR,HR%20algorithm%20is%20applied)
[\[9\]](https://www.shimmersensing.com/support/wireless-sensor-networks-faqs/#:~:text=,Does%20Shimmer%20Use)
FAQs - Shimmer Wearable Sensor Technology

<https://www.shimmersensing.com/support/wireless-sensor-networks-faqs/>

[\[8\]](https://github.com/ShimmerEngineering/ShimmerAndroidAPI#:~:text=Introduction)
[\[11\]](https://github.com/ShimmerEngineering/ShimmerAndroidAPI#:~:text=Important%20,Packages)
[\[12\]](https://github.com/ShimmerEngineering/ShimmerAndroidAPI#:~:text=dependencies%3A)
GitHub - ShimmerEngineering/ShimmerAndroidAPI

<https://github.com/ShimmerEngineering/ShimmerAndroidAPI>

[\[10\]](https://github.com/buccancs/fyp-gsr-windows/blob/2d41c241dfeccbb9f5dc0b582255f8b67c8e0ec6/docs/android_research.tex#L26-L34)
[\[35\]](https://github.com/buccancs/fyp-gsr-windows/blob/2d41c241dfeccbb9f5dc0b582255f8b67c8e0ec6/docs/android_research.tex#L46-L49)
[\[36\]](https://github.com/buccancs/fyp-gsr-windows/blob/2d41c241dfeccbb9f5dc0b582255f8b67c8e0ec6/docs/android_research.tex#L30-L38)
[\[37\]](https://github.com/buccancs/fyp-gsr-windows/blob/2d41c241dfeccbb9f5dc0b582255f8b67c8e0ec6/docs/android_research.tex#L40-L48)
[\[51\]](https://github.com/buccancs/fyp-gsr-windows/blob/2d41c241dfeccbb9f5dc0b582255f8b67c8e0ec6/docs/android_research.tex#L14-L22)
android_research.tex

<https://github.com/buccancs/fyp-gsr-windows/blob/2d41c241dfeccbb9f5dc0b582255f8b67c8e0ec6/docs/android_research.tex>

2_4_milestone.md


[\[15\]](https://github.com/ShimmerEngineering/Shimmer-Java-Android-API/blob/563dd5b9bc88baf55d5ef479778f3dd017a7c9cb/ShimmerDriver/src/main/java/com/shimmerresearch/driver/Configuration.java#L32-L40)
[\[28\]](https://github.com/ShimmerEngineering/Shimmer-Java-Android-API/blob/563dd5b9bc88baf55d5ef479778f3dd017a7c9cb/ShimmerDriver/src/main/java/com/shimmerresearch/driver/Configuration.java#L80-L88)
Configuration.java

<https://github.com/ShimmerEngineering/Shimmer-Java-Android-API/blob/563dd5b9bc88baf55d5ef479778f3dd017a7c9cb/ShimmerDriver/src/main/java/com/shimmerresearch/driver/Configuration.java>

[\[16\]](https://github.com/jhallard/BioSig-for-Android/blob/f803f22e485d453516b671cd3692c79a6c898858/src/com/shimmerresearch/driver/Shimmer.java#L44-L52)
[\[17\]](https://github.com/jhallard/BioSig-for-Android/blob/f803f22e485d453516b671cd3692c79a6c898858/src/com/shimmerresearch/driver/Shimmer.java#L48-L56)
[\[18\]](https://github.com/jhallard/BioSig-for-Android/blob/f803f22e485d453516b671cd3692c79a6c898858/src/com/shimmerresearch/driver/Shimmer.java#L18-L26)
[\[19\]](https://github.com/jhallard/BioSig-for-Android/blob/f803f22e485d453516b671cd3692c79a6c898858/src/com/shimmerresearch/driver/Shimmer.java#L20-L28)
[\[21\]](https://github.com/jhallard/BioSig-for-Android/blob/f803f22e485d453516b671cd3692c79a6c898858/src/com/shimmerresearch/driver/Shimmer.java#L116-L123)
[\[22\]](https://github.com/jhallard/BioSig-for-Android/blob/f803f22e485d453516b671cd3692c79a6c898858/src/com/shimmerresearch/driver/Shimmer.java#L120-L123)
Shimmer.java

<https://github.com/jhallard/BioSig-for-Android/blob/f803f22e485d453516b671cd3692c79a6c898858/src/com/shimmerresearch/driver/Shimmer.java>

[\[30\]](https://github.com/ShimmerEngineering/ShimmerAndroidAPI/wiki/Quick-Start-Guide#:~:text=)
[\[41\]](https://github.com/ShimmerEngineering/ShimmerAndroidAPI/wiki/Quick-Start-Guide#:~:text=)
Quick Start Guide · ShimmerEngineering/ShimmerAndroidAPI Wiki · GitHub

<https://github.com/ShimmerEngineering/ShimmerAndroidAPI/wiki/Quick-Start-Guide>

[\[40\]](https://github.com/ShimmerEngineering/ShimmerAndroidAPI/wiki/Data-Structure#:~:text=Arrays)
Data Structure · ShimmerEngineering/ShimmerAndroidAPI Wiki · GitHub

<https://github.com/ShimmerEngineering/ShimmerAndroidAPI/wiki/Data-Structure>

[\[42\]](https://shimmersensing.com/wp-content/docs/support/documentation/GSR_User_Guide_rev1.13.pdf#:~:text=3,Baseline)
[\[43\]](https://shimmersensing.com/wp-content/docs/support/documentation/GSR_User_Guide_rev1.13.pdf#:~:text=7,References)
Shimmer3 GSR+ User Guide

<https://shimmersensing.com/wp-content/docs/support/documentation/GSR_User_Guide_rev1.13.pdf>

[\[50\]](https://stackoverflow.com/questions/8085258/integrating-shimmer-with-android-tablet#:~:text=Integrating%20Shimmer%20with%20Android%20Tablet,once%20connected%2C%20transmit%20the)
Integrating Shimmer with Android Tablet - Stack Overflow

<https://stackoverflow.com/questions/8085258/integrating-shimmer-with-android-tablet>
