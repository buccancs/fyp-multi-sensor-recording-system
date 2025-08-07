# Topdon TC001/TC001 Plus Android SDK -- README

## Overview

**Topdon TC001 and TC001 Plus** are portable infrared thermal cameras
that attach to Android devices (via USB Type-C) to transform a
smartphone or tablet into a high-tech thermal
imager[\[1\]](https://www.topdon.us/products/tc001?srsltid=AfmBOoocBj_-_hydfJjYl-1Yj8ADMJTtQyVLOHU9jP_SnN8s51-kisBU#:~:text=%E2%80%A2%20Equipped%20with%20an%20ultra,circuit%20boards%20and%20other%20electronics).
They capture heat radiation as images, allowing non-contact temperature
measurement across a scene. The TC001 series features a 256×192 IR
sensor resolution, producing clear thermal images and detecting
temperature differences as small as
0.1 °C[\[2\]](https://www.topdon.us/products/tc001-plus?srsltid=AfmBOopq9mBNdV3ePkER8GhdlqhIks5h2xZMwObi-3oz_QF-meRQeAhV#:~:text=8%C2%A0%E2%80%93%C2%A014%CE%BCm)[\[3\]](https://www.topdon.us/products/tc001-plus?srsltid=AfmBOopq9mBNdV3ePkER8GhdlqhIks5h2xZMwObi-3oz_QF-meRQeAhV#:~:text=Sporting%20an%20ultra,analyse%20details%20of%20the%20targets).
The TC001 Plus model includes a dual-lens system (an IR sensor plus a
visible-light camera) enabling image fusion for sharper detail and
contours in the thermal
image[\[4\]](https://www.topdon.us/products/tc001-plus?srsltid=AfmBOopq9mBNdV3ePkER8GhdlqhIks5h2xZMwObi-3oz_QF-meRQeAhV#:~:text=Dual%20Lens%20to%20Unveil%20the,Unseen)[\[3\]](https://www.topdon.us/products/tc001-plus?srsltid=AfmBOopq9mBNdV3ePkER8GhdlqhIks5h2xZMwObi-3oz_QF-meRQeAhV#:~:text=Sporting%20an%20ultra,analyse%20details%20of%20the%20targets).
Both cameras support a wide temperature detection range from about
**-20 °C to 550 °C** (≈ -4 °F to
1022 °F)[\[5\]](https://www.topdon.us/products/tc001?srsltid=AfmBOoocBj_-_hydfJjYl-1Yj8ADMJTtQyVLOHU9jP_SnN8s51-kisBU#:~:text=Optimized%20Temperature%20Range%20%26%20Accuracy)[\[6\]](https://www.topdon.us/products/tc001-plus?srsltid=AfmBOopq9mBNdV3ePkER8GhdlqhIks5h2xZMwObi-3oz_QF-meRQeAhV#:~:text=%E2%80%A2%20With%20a%20temperature%20range,1%C2%B0C),
making them suitable for various applications -- from industrial
inspections to biomedical and physiological sensing.

In **physiological sensing**, infrared thermography provides a
noninvasive, contact-free way to monitor subtle temperature changes on
the
body[\[7\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=Thermal%20imaging%20is%20currently%20taking,111%5D.%20Accordingly)[\[8\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=Thermal%20imaging%20unobtrusively%20monitors%20skin,to%20discriminate%20stimuli%20with%20positive).
Many physiological signals manifest as thermal patterns: for example,
breathing rate can be measured by the cyclical temperature changes near
the nostrils, heart pulse by tiny thermal pulsations, and stress-induced
blood flow changes by temperature shifts in facial
regions[\[9\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=Thermal%20imaging%20unobtrusively%20monitors%20skin,in%20response%20to%20startling%20stimulus).
Indeed, thermal imaging has been used in psychophysiology to observe
stress responses -- e.g. a drop in nose tip temperature under acute
stress or increased forehead temperature from
vasodilation[\[10\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=variation%20of%20the%20nose%20tip,volume%20signal%20obtained%20from%20the).
With the Topdon TC001 cameras, researchers can capture such thermal
phenomena in real time, alongside other biosignals, for multimodal
analysis of human physiological states.

## Project Scope

This SDK/API provides an interface for Android developers to integrate
the Topdon TC001/TC001 Plus camera into their applications. Its primary
purpose is to facilitate **image acquisition, device configuration, and
data streaming** from the thermal camera on Android. Using the SDK, an
app can connect to the camera (via Android's USB host interface), start
the thermal video feed, and retrieve **thermal frames** (infrared images
and temperature data) in real time. The API exposes methods to configure
camera parameters -- for example, selecting colour palettes (pseudo-colour
schemes for the thermal image), adjusting image orientation, switching
between high- and low-gain modes, triggering calibrations (shutter
correction), and choosing the **data output mode** (e.g. image only,
temperature only, or both interleaved). Under the hood, the SDK handles
the low-level USB Video Class (UVC) protocol and infrared sensor
commands, so developers can work with high-level objects (like a
`UVCCamera` and frame callback) rather than raw USB transfers.

By using this SDK, developers can **stream thermal imagery** into their
apps for visualisation or analysis, obtain per-pixel temperature
readings, and synchronously capture frames at up to 25 Hz (depending on
device)[\[3\]](https://www.topdon.us/products/tc001-plus?srsltid=AfmBOopq9mBNdV3ePkER8GhdlqhIks5h2xZMwObi-3oz_QF-meRQeAhV#:~:text=Sporting%20an%20ultra,analyse%20details%20of%20the%20targets).
The SDK is designed to support **both** the TC001 and TC001 Plus models,
abstracting their dual-lens or single-lens differences. For instance,
when a TC001 Plus is connected, the SDK can fetch the simultaneous
visual and IR streams for fusion, whereas for TC001 it handles the
single thermal stream. Overall, the project enables Android applications
to utilise the TC001 series cameras for tasks such as real-time thermal
monitoring, recording thermal videos, measuring temperature at points or
regions of interest, and integrating thermal data with other sensor
modalities.

## Installation

To integrate the Topdon TC001 SDK into an Android project, begin by
obtaining the SDK package. Topdon provides an Android SDK (e.g. as a
`.zip` archive) containing the library binaries and sample
code[\[11\]](https://github.com/TopdonTechnology/Thermal#:~:text=ANDROID_SDK_USB_IR_1).
This typically includes a precompiled AAR library (or JAR with native
`.so` files) and documentation. Import the SDK library into your Android
Studio project by copying the AAR into your app module's `libs` folder
and adding it as a dependency in your Gradle build file. For example, in
`app/build.gradle`:

    dependencies {
        implementation fileTree(dir: "libs", include: ["*.aar"])
        // ... other dependencies ...
    }

Make sure to enable support for the USB host API in your app's manifest
(the Topdon camera uses Android's USB host mode). In the app
`AndroidManifest.xml`, declare the USB host feature:

    <uses-feature android:name="android.hardware.usb.host" android:required="true"/>

Also add an intent filter and metadata so that Android can recognise the
camera and grant permissions. For example, inside your launch Activity:

    <intent-filter>
        <action android:name="android.hardware.usb.action.USB_DEVICE_ATTACHED" />
    </intent-filter>
    <meta-data 
        android:name="android.hardware.usb.action.USB_DEVICE_ATTACHED"
        android:resource="@xml/device_filter" />

Here, `@xml/device_filter` is a resource file (placed in `res/xml/`)
specifying the USB Vendor ID and Product ID of the TC001 camera, so that
the system can identify and associate the device with your app. (The SDK
sample provides such a `device_filter.xml` for Topdon/Infisense
devices.)

After adding the library and manifest entries, **synchronise Gradle** to
ensure the SDK is included. The SDK may include native components, so
you should build your project to confirm that the .so libraries are
packaged correctly. No additional installation steps (like special
drivers) are needed on the Android device; the SDK leverages the
standard Android USB API. It's also recommended to use a device running
Android 7.0 or above for full compatibility with the UVC library.

**Note:** The SDK's sample code contains two utility classes,
`Usbcontorl` and `Usbjni`, which are used for low-level USB power
management on certain devices. These must retain their package name
(`android.yt.jni`) if
used[\[12\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/android/yt/jni/Usbcontorl.java#L8-L16).
In most cases, you won't need to modify these; just ensure they are
included if your project structure doesn't already include them. (They
handle loading a native library for USB hub control, used only on
specific hardware; standard Android phones typically do not require this
step.)

## Permissions

Using the TC001 camera on Android requires a few permissions and
configurations:

- **USB Permissions:** The camera communicates via USB, so your app must
  request permission to access the USB device. The Android system will
  prompt the user with a dialogue such as "Allow this app to access the
  USB device?". The SDK (via `USBMonitor`) handles this by calling
  `UsbManager.requestPermission()` when the device is attached. Ensure
  your manifest includes the USB device intent filter as shown above and
  that your app logic requests/grants permission. (There is *no*
  specific `<uses-permission>` string for USB host; it's enabled by the
  uses-feature tag and user consent dialogue.)

- **Camera Permission:** Even though the TC001 is an external camera,
  the system may treat it as a camera source. It is advisable to declare
  the camera permission in your manifest and request it on devices
  running Android 6.0+ for completeness. For example:
  `<uses-permission android:name="android.permission.CAMERA" />`[\[13\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/AndroidManifest.xml#L79-L81).

- **Storage Permissions (optional):** If your application will save
  thermal images or videos to device storage, include read/write storage
  permissions. The SDK sample app requests:

- `WRITE_EXTERNAL_STORAGE` and `READ_EXTERNAL_STORAGE` (for saving
  images/video)[\[14\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/AndroidManifest.xml#L73-L81).
  On Android 10+, you might use scoped storage or the MediaStore
  instead, but for broad access, include these permissions. (Also note
  the sample's use of `MANAGE_EXTERNAL_STORAGE` for legacy storage
  support[\[15\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/AndroidManifest.xml#L74-L82),
  though this may not be needed in a scoped storage environment.)

- `android.permission.WAKE_LOCK` to keep the CPU awake during capture
  (prevents the device from sleeping during a long
  recording)[\[16\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/AndroidManifest.xml#L79-L83)
  -- this is optional, but can be useful if your app records data with
  the screen off.

In summary, add the following to your AndroidManifest.xml under the
`<manifest>` node:

    <uses-permission android:name="android.permission.CAMERA"/>
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"/>
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE"/>

And ensure the USB host feature is declared as mentioned. The user will
need to confirm the USB permission each time the camera is connected
(unless your app is pre-installed as a system app), so be prepared to
handle the permission grant flow.

## Getting Started

Once the SDK is integrated and permissions are in place, you can
initialise and connect to the TC001 camera in your app. The basic
workflow is:

1.  **Initialise the USB monitor and listeners.** The SDK provides a
    `USBMonitor` class that monitors USB device connections. You attach
    an `OnDeviceConnectListener` to handle events: device attached,
    device permission granted, device connected, disconnected, etc.

2.  **Request permission and open the camera.** When the camera is
    attached and permission is granted, create a `UVCCamera` instance
    using the SDK's builder, open it with the USB control block, and
    initialise the infrared command interface (`IRCMD`) for thermal
    data.

3.  **Start streaming frames.** Set a frame callback to receive image
    frames, then start the camera preview. As frames come in, you can
    process the thermal image and/or temperature data.

4.  **Close the camera on disconnect.** Properly stop streaming and
    release resources if the camera is detached.

Below is a **sample code snippet** illustrating the initialisation and
frame capture process in Java:

    import android.hardware.usb.UsbDevice;
    import com.infisense.iruvc.usb.USBMonitor;
    import com.infisense.iruvc.uvc.UVCCamera;
    import com.infisense.iruvc.uvc.UVCType;
    import com.infisense.iruvc.uvc.ConnectCallback;
    import com.infisense.iruvc.ircmd.IRCMD;
    import com.infisense.iruvc.ircmd.IRCMDType;
    import com.infisense.iruvc.utils.CommonParams;
    import com.infisense.iruvc.utils.IFrameCallback;
    import com.infisense.iruvc.uvc.ConcreateUVCBuilder;
    import com.infisense.iruvc.ircmd.ConcreteIRCMDBuilder;

    // ... inside an Activity or Service:

    USBMonitor usbMonitor = new USBMonitor(getApplicationContext(), new USBMonitor.OnDeviceConnectListener() {
        @Override 
        public void onAttach(UsbDevice device) {
            // Called when a USB device (camera) is attached
            usbMonitor.requestPermission(device);  // request user permission
        }
        @Override 
        public void onGranted(UsbDevice device, boolean granted) {
            // Called after user grants/denies permission (not used here, we wait for onConnect)
        }
        @Override 
        public void onConnect(UsbDevice device, USBMonitor.UsbControlBlock ctrlBlock, boolean createNew) {
            if (!createNew) return;
            // Permission granted and new device connection:
            // 1. Initialise the UVC camera object
            ConcreateUVCBuilder uvcBuilder = new ConcreateUVCBuilder();
            UVCCamera uvcCamera = uvcBuilder
                    .setUVCType(UVCType.USB_UVC)      // using a USB UVC device
                    .build();
            int result = uvcCamera.openUVCCamera(ctrlBlock);  // open the camera
            if (result != 0) {
                // handle error (result codes defined in UVCResult)
                return;
            }
            // 2. Initialise infrared command interface (IRCMD) for thermal data
            IRCMD irCmd = new ConcreteIRCMDBuilder()
                    .setIrcmdType(IRCMDType.USB_IR_256_384)   // using 256x384 IR module (for TC001)
                    .setIdCamera(uvcCamera.getNativePtr())   // link to the opened camera
                    .build();
            // 3. Prepare a frame callback to handle incoming frames
            uvcCamera.setFrameCallback(new IFrameCallback() {
                @Override
                public void onFrame(byte[] frameData) {
                    // This method is called on every frame (on a background thread)
                    // frameData contains the thermal image data (and temperature data, if enabled)
                    // TODO: process the frame (convert to Bitmap, extract temperatures, etc.)
                }
            });
            // 4. Start the camera preview stream
            uvcCamera.onStartPreview();
            irCmd.startPreview(CommonParams.PreviewPathChannel.PREVIEW_PATH0,
                               CommonParams.StartPreviewSource.SOURCE_SENSOR,
                               15,  // desired FPS (e.g. 15)
                               CommonParams.StartPreviewMode.VOC_DVP_MODE,
                               CommonParams.DataFlowMode.IMAGE_AND_TEMP_OUTPUT);
            // Now frames will begin streaming to the IFrameCallback.
        }
        @Override 
        public void onDisconnect(UsbDevice device, USBMonitor.UsbControlBlock ctrlBlock) {
            // The device was disconnected (this is called before onDettach)
            // We can stop the preview if needed here.
        }
        @Override 
        public void onDettach(UsbDevice device) {
            // The device was physically detached from USB
            // Cleanup: release camera resources
            // (In this example, the UVCCamera object would be a member variable to close here)
        }
        @Override 
        public void onCancel(UsbDevice device) {
            // Permission dialogue canceled
        }
    });

    // Register the USBMonitor to start listening for events
    usbMonitor.register();
    // (Don’t forget to unregister in onPause/onDestroy to avoid leaks)

In the above code:

- We create a `USBMonitor` with an `OnDeviceConnectListener`. In
  `onAttach`, we immediately request permission for the device. When
  permission is granted, `onConnect` is invoked with a `UsbControlBlock`
  that we use to open the camera.
- A `UVCCamera` is built via `ConcreateUVCBuilder` (the SDK's builder
  for UVC-compliant cameras) and opened. We then build an `IRCMD` object
  via `ConcreteIRCMDBuilder` -- this represents the infrared command
  interface, which handles thermal sensor configuration and commands. We
  specify `IRCMDType.USB_IR_256_384` assuming a 256×192 sensor with
  image+temperature (256×384 output
  frame)[\[17\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/com/infisense/usbir/camera/IRUVC.java#L441-L450)[\[18\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/com/infisense/usbir/camera/IRUVC.java#L443-L451).
  (The SDK may have different `IRCMDType` enums if other sensor
  resolutions or dual-camera modes are supported.)
- We set an `IFrameCallback` on the camera. The SDK will invoke
  `onFrame(byte[] frameData)` for each incoming frame. At this point,
  the camera isn't streaming yet, so no frames come until we start
  preview.
- Finally, we call `uvcCamera.onStartPreview()` and then use
  `irCmd.startPreview(...)` to begin the infrared data
  stream[\[19\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/com/infisense/usbir/camera/IRUVC.java#L24-L32)[\[20\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/com/infisense/usbir/camera/IRUVC.java#L26-L35).
  We pass parameters specifying the source (sensor), target frame rate,
  mode (here using VOC_DVP_MODE, a default mode for infrared output),
  and the data flow mode. In this example,
  `CommonParams.DataFlowMode.IMAGE_AND_TEMP_OUTPUT` is used, which means
  each frame will contain both the thermal image and temperature data
  interleaved[\[21\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/com/infisense/usbir/camera/IRUVC.java#L22-L30).
  After this call, the camera is actively streaming, and our `onFrame`
  callback will start receiving data.

**Note:** All USBMonitor callbacks (onAttach, onConnect, etc.) run on a
background
thread[\[22\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/README.md#L13-L21).
This means the `onFrame` callback is also on a background thread, so you
should handle thread synchronisation if updating UI elements with the
thermal image. In a real app, you might use a handler or runOnUiThread
to display the image, or process frames in a dedicated worker thread (as
the SDK sample does with an `ImageThread` for image conversion).

This basic initialisation can be adapted. For example, if you only need
the temperature data without the image, you could use
`DataFlowMode.TEMP_OUTPUT` when starting preview. Or if you only need
the thermal image (for visualisation), use `IMAGE_OUTPUT`. The SDK also
provides intermediate modes (like raw sensor outputs for noise reduction
etc.), but those are advanced usage.

Once frames are streaming, you can use the SDK's image processing
utilities or Android's imaging APIs to convert and display the data --
described next.

## Data Handling

**Frame Format:** The TC001 outputs thermal frames in a YUV format
(specifically YUYV 4:2:2) by default for the infrared
image[\[23\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/README.md#L120-L128).
When using **IMAGE_AND_TEMP_OUTPUT** mode (as in the example above),
each frame delivered to `onFrame(byte[])` contains two parts: - The
first half of the byte array is the infrared image data (thermal image)
in YUV422 format. - The second half of the byte array is the per-pixel
temperature data, also in a 16-bit format (Y16).

For the TC001's 256×192 resolution: if both image and temperature are
enabled, the frame is effectively 256×384 in dimension (the two 256×192
images stacked). In memory this translates to a byte array length of
`256 * 384 * 2 = 196608` bytes, since YUV422 uses 2 bytes per pixel on
average. The **first 98,304 bytes** correspond to a 256×192 YUV image,
and the **next 98,304 bytes** correspond to a 256×192 array of
temperature
values[\[24\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/com/infisense/usbir/camera/IRUVC.java#L163-L171)[\[25\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/com/infisense/usbir/camera/IRUVC.java#L173-L181).
The SDK documentation confirms that "the frame array's front half is IR
data, the latter half is temperature data" for image+temperature
mode[\[26\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/com/infisense/usbir/camera/IRUVC.java#L165-L172)[\[25\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/com/infisense/usbir/camera/IRUVC.java#L173-L181).
If you use image-only or temp-only modes, the frame will be half that
size, containing just the single dataset.

**Converting the Image:** To display the thermal image, you need to
convert the YUYV data to a viewable format (e.g., ARGB8888). The SDK
includes a `LibIRProcess` utility with methods like
`convertYuyvMapToARGBPseudocolor(...)` and
`convertArrayYuv422ToARGB(...)`[\[23\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/README.md#L120-L128).
In the provided sample, the raw YUV is converted to an ARGB bitmap as
follows (pseudo-code):

    // Assume imageBytes is the first half of frameData containing YUV422 data
    int pixelCount = imageWidth * imageHeight;  // 256*192
    int[] argbPixels = new int[pixelCount];
    if (pseudocolorMode != null) {
        // Apply a false-colour palette to the grayscale thermal image
        LibIRProcess.convertYuyvMapToARGBPseudocolor(imageBytes, (long)pixelCount,
                                                    pseudocolorMode, argbPixels);
    } else {
        // Convert YUV422 to grayscale ARGB
        LibIRProcess.convertYuv422ToARGB(imageBytes, pixelCount, argbPixels);
    }
    // If the image is rotated (camera orientation), rotate accordingly:
    if (needRotate90) {
        LibIRProcess.ImageRes_t res = new LibIRProcess.ImageRes_t();
        res.height = (char)imageWidth;
        res.width  = (char)imageHeight;
        // Rotate right by 90 degrees
        LibIRProcess.rotateRight90(argbPixels, res, CommonParams.IRPROCSRCFMTType.IRPROC_SRC_FMT_ARGB8888, argbPixels);
    }
    // Now argbPixels contains the image in ARGB format; create a Bitmap to display:
    Bitmap thermalBitmap = Bitmap.createBitmap(argbPixels, imageWidth, imageHeight, Bitmap.Config.ARGB_8888);

This process is essentially what the SDK's sample `ImageThread` does:
YUV -\> ARGB -\> rotate -\>
Bitmap[\[23\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/README.md#L120-L128)[\[27\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/README.md#L131-L140).
You can then draw this Bitmap on an `ImageView` or a custom view
(`CameraView` in the sample) to show the live thermal image. The SDK
supports multiple **pseudo-colour palettes** (ironbow, rainbow,
grayscale, etc.), approximately 10 palettes including "white hot",
"black hot", "medical" and
others[\[28\]](https://www.topdon.us/products/tc001-plus?srsltid=AfmBOopq9mBNdV3ePkER8GhdlqhIks5h2xZMwObi-3oz_QF-meRQeAhV#:~:text=1).
By selecting a palette (e.g., `CommonParams.PseudoColorType`), you can
have the conversion routine apply that coloring to the image, enhancing
contrast for visualisation.

**Temperature Data:** The temperature values for each pixel are provided
in the second half of the frame (if using combined mode, or as the whole
frame in temp-only mode). These are 16-bit raw data values that
correspond to temperatures in either Kelvin or Celsius with a scaling
factor. According to the SDK, in **Y16 format each unit corresponds to
1/64 of a degree** (for 16-bit
data)[\[29\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/com/infisense/usbir/view/TemperatureView.java#L159-L167).
In other words, to convert a raw 16-bit value to an absolute
temperature:

- If using the default scale (for TC001 high-gain mode), **divide the
  raw value by 64** to get temperature in Kelvin, then subtract 273.15
  to convert to °C. For example, a raw value of 30000 would be 30000/64
  = 468.75 K, which is 195.6 °C.
- If the camera or mode uses 14-bit data (scale 16, e.g. low-gain mode
  or IR fusion mode), divide by 16
  instead[\[29\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/com/infisense/usbir/view/TemperatureView.java#L159-L167).
  The SDK's `LibIRTemp` class handles these conversions internally by
  setting the scale depending on mode (64 for Y16, 16 for
  Y14)[\[29\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/com/infisense/usbir/view/TemperatureView.java#L159-L167).

Typically, you won't manually convert every pixel unless needed. A
common approach is to use provided methods to find min/max or get
specific points. The `LibIRTemp` class can be used to **extract
temperature metrics** from the byte array. For instance, you can
instantiate `LibIRTemp` with the image width/height and then call
methods to sample temperatures:

    LibIRTemp irTempUtil = new LibIRTemp(imageWidth, imageHeight);
    irTempUtil.setTempData(temperatureByteArray);
    LibIRTemp.TemperatureSampleResult result = irTempUtil.getTemperatureOfRect(new Rect(0,0, imageWidth-1, imageHeight-1));
    float minC = result.minTemperature;  // minimum temperature in °C in the image
    Point minLoc = result.minTemperaturePixel;  // location of min temp
    float maxC = result.maxTemperature;

The SDK can compute statistics like max, min, and average temperature
over regions (rectangles, lines, or
points)[\[30\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/com/infisense/usbir/view/TemperatureView.java#L2-L10)[\[31\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/com/infisense/usbir/view/TemperatureView.java#L26-L34).
The sample's `TemperatureView` uses these methods to display values for
user-selected points/areas on the image (up to 3 points, lines, or
rectangles) -- for example, it draws the hottest and coldest point in a
region with their temperature
values[\[32\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/com/infisense/usbir/view/TemperatureView.java#L26-L34)[\[33\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/com/infisense/usbir/view/TemperatureView.java#L32-L40).
Using these utilities ensures the proper calibration and scale is
applied (the SDK accounts for the camera's calibration data and any
offset). The **accuracy** of the temperature readings is stated as ±2 °C
or ±2% (whichever is greater) for the TC001
series[\[34\]](https://www.topdon.us/products/tc001-plus?srsltid=AfmBOopq9mBNdV3ePkER8GhdlqhIks5h2xZMwObi-3oz_QF-meRQeAhV#:~:text=80)[\[35\]](https://www.topdon.us/products/tc001-plus?srsltid=AfmBOopq9mBNdV3ePkER8GhdlqhIks5h2xZMwObi-3oz_QF-meRQeAhV#:~:text=Extensive%20%26%20Accurate%20Temperature%20Measurement),
and the noise-equivalent temperature difference (NETD) is \<40 mK,
meaning very small temperature differences (\~0.04 °C) are
distinguishable[\[2\]](https://www.topdon.us/products/tc001-plus?srsltid=AfmBOopq9mBNdV3ePkER8GhdlqhIks5h2xZMwObi-3oz_QF-meRQeAhV#:~:text=8%C2%A0%E2%80%93%C2%A014%CE%BCm).

When visualising the temperature data, you might overlay it as numeric
values or a separate "temperature map". The TC001 Plus, with its visual
camera, allows blending the thermal data with an RGB image -- the SDK
can provide an aligned visual image so you can overlay temperature info
on actual visible
contours[\[4\]](https://www.topdon.us/products/tc001-plus?srsltid=AfmBOopq9mBNdV3ePkER8GhdlqhIks5h2xZMwObi-3oz_QF-meRQeAhV#:~:text=Dual%20Lens%20to%20Unveil%20the,Unseen).
In our context, if focusing on physiological data, one might not need
the visible-light overlay, but it can help identify anatomical features
(the SDK sample synchronizes RGB and thermal frames to locate facial
landmarks in thermal
images[\[36\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=Thermal%20imaging%20unobtrusively%20monitors%20skin,18)[\[37\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=We%20used%20thermal%20imaging%20to,e)).

**Thermal Range and Units:** As mentioned, the device can measure
roughly -20 °C to 550 °C in two gain
modes[\[5\]](https://www.topdon.us/products/tc001?srsltid=AfmBOoocBj_-_hydfJjYl-1Yj8ADMJTtQyVLOHU9jP_SnN8s51-kisBU#:~:text=Optimized%20Temperature%20Range%20%26%20Accuracy).
The camera will automatically switch between **high gain** (for lower
temperatures, finer resolution) and **low gain** (for higher
temperatures, extended range). The SDK provides callbacks
(AutoGainSwitch) if one enables them, but by default this is handled
internally. The raw values and scaling differ slightly in low-gain mode
(14-bit data); the `LibIRTemp.setScale(16)` call in the sample is doing
exactly that when IRISP (the dual-gain fusion mode) is
on[\[29\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/com/infisense/usbir/view/TemperatureView.java#L159-L167).
For most physiological use-cases (human body temperatures \~30--40 °C),
the camera will be in high-gain mode for better sensitivity.

In summary, handling data from the SDK involves splitting the frame into
image vs. temperature, converting the image for display (using provided
conversion functions and applying pseudo-colours if desired), and
converting temperature data to meaningful values (using the scale or the
`LibIRTemp` helpers). The provided sample code and SDK documentation
have detailed examples of these steps, ensuring you can both **see** the
thermal scene and **measure** temperatures at points of interest.

## Integration with `bucika_gsr`

The `bucika_gsr` Android app is a multi-modal data collection tool,
combining galvanic skin response (GSR) with other sensors. Integrating
the Topdon TC001 camera into this app allows **thermal data** to become
another channel in its physiological monitoring architecture. In
practice, the integration involves initialising and running the TC001's
thermal stream in parallel with GSR recording, and synchronising the
data streams (by timestamps or sampling rate) so that thermal features
can be correlated with electrodermal activity.

**Architecture Fit:** In a typical setup, the app might have a
background service or manager handling sensor data acquisition. The
TC001 integration would add a **Thermal Sensor Module** to this system.
For example, when a recording session starts, the app would:

- Power and connect to the TC001 camera (using the SDK as outlined in
  *Getting Started*). This could be done in the same service that reads
  GSR, or in a dedicated thread, as long as lifecycle is managed
  (start/stop with the session).

- Begin streaming thermal frames. You may choose to store the raw
  thermal video or to compute specific metrics in real-time. In a
  GSR-focused experiment, one might extract features like *facial
  temperature averages*, *nose tip temperature over time*, or *rate of
  change of temperature* to indicate stress
  responses[\[9\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=Thermal%20imaging%20unobtrusively%20monitors%20skin,in%20response%20to%20startling%20stimulus).
  These features can be computed on each frame or every few frames and
  then logged alongside GSR data.

- Ensure that each thermal sample or frame is timestamped (using the
  same clock or reference as the GSR data timestamps). Given GSR is
  often sampled at, say, 10--100 Hz and the thermal camera at up to
  25 Hz, you might down-sample or interpolate as needed. The sample
  research system described by Gioia *et al.* synchronized 5 Hz RGB
  frames with 25 Hz thermal frames for
  analysis[\[37\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=We%20used%20thermal%20imaging%20to,e),
  so a similar strategy can be applied: for instance, record thermal
  data at its native rate and later align it to GSR's timeline via
  timestamps.

- **Data Fusion:** The GSR signal primarily reflects sympathetic nervous
  system arousal (sweat gland activity), whereas the thermal camera can
  capture peripheral blood flow changes and other heat-related
  signals[\[7\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=Thermal%20imaging%20is%20currently%20taking,111%5D.%20Accordingly)[\[9\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=Thermal%20imaging%20unobtrusively%20monitors%20skin,in%20response%20to%20startling%20stimulus).
  In `bucika_gsr`, the thermal stream could be used to enrich
  interpretation of GSR events. For example, a spike in GSR (indicating
  stress or startle) might be accompanied by a drop in facial skin
  temperature (due to stress-related
  vasoconstriction)[\[10\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=variation%20of%20the%20nose%20tip,volume%20signal%20obtained%20from%20the).
  By integrating the two, the app could detect such patterns more
  reliably. The app's data model would store thermal features alongside
  GSR, allowing later analysis (e.g. plotting nose temperature and GSR
  on the same time axis to see the temporal relationship).

- **Real-Time Display:** If `bucika_gsr` has a user interface showing
  live signals (such as a graph of GSR over time), the thermal camera
  integration might also include a live thermal view or thermal metrics
  display. For instance, one could show the live thermal image in a
  window, or simply display the current temperature of a particular
  region (like forehead or hand) in real-time. The TC001 Plus's dual
  lens can assist in aiming the camera at the subject's face or skin
  area using the visible light aid. In code, once the camera is
  streaming, you can overlay markers on the thermal image (as the
  TemperatureView does) to indicate where temperature is being sampled
  for the app's purposes (e.g., the forehead region's average
  temperature).

From a software integration standpoint, adding the TC001 likely means
managing the **lifecycle** within the app: initialising the camera when
needed, handling user permissions (the app might prompt the user to
connect/allow the camera at start of a session), and gracefully stopping
the camera when the session ends or app pauses. This involves calling
`usbMonitor.register()` on start and `usbMonitor.unregister()` on stop,
and releasing the camera (`uvcCamera.close()` etc.) to free the USB
interface. The `bucika_gsr` app should also account for cases where the
camera is not available or the user denies permission, by falling back
or notifying the user.

In terms of **multimodal data architecture**, the thermal stream will
produce a high volume of data (frame bytes or extracted features), so
consider the data handling pipeline: you might not want to log every
pixel's temperature for long sessions due to storage and processing
load. Instead, the integration can focus on **key features** relevant to
the research questions. Common choices in research are: maximum facial
temperature, temperature at the tip of the nose, or at the inner canthus
of the eyes (as indicators of
stress/fear)[\[10\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=variation%20of%20the%20nose%20tip,volume%20signal%20obtained%20from%20the),
or overall average skin temperature as an indicator of thermal comfort.
The SDK makes it easy to compute these in real-time (using
`LibIRTemp.getTemperatureOfPoint()` or small regions). Those values (a
few numbers per second) can then be time-stamped and recorded alongside
GSR and perhaps other signals (heart rate, etc.) in the app's data file.

By integrating the Topdon SDK with `bucika_gsr`, the app effectively
becomes a **multisensor platform**, capturing both electrodermal
activity and thermal physiology. This enables richer analysis such as
correlating sudden GSR increases (sweat release) with subsequent changes
in peripheral skin temperature, or detecting respiration rate from the
thermal signal to see how it correlates with stress-induced GSR
fluctuations[\[36\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=Thermal%20imaging%20unobtrusively%20monitors%20skin,18)[\[9\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=Thermal%20imaging%20unobtrusively%20monitors%20skin,in%20response%20to%20startling%20stimulus).
Such integration opens the door to more robust and contactless stress or
emotion monitoring: GSR requires skin contact electrodes, whereas
thermal is contact-free -- combining them can validate findings and
provide backup measurements if one signal is lost or
noisy[\[38\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=Thermal%20imaging%20is%20currently%20taking,SNS%29%20branches%20of%20the)[\[36\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=Thermal%20imaging%20unobtrusively%20monitors%20skin,18).

In summary, within the `bucika_gsr` app, the Topdon camera's role is to
provide a **thermal imaging stream** that complements the GSR data. The
integration involves technical steps (initialising the camera via the
SDK, managing data flow) and conceptual steps (deciding which thermal
features to extract and log). Once implemented, the app can record
synchronized thermal and GSR data for each session, offering a more
complete view of the user's physiological responses than either
modality alone.

## Troubleshooting

When working with the TC001/TC001 Plus on Android, you may encounter
some common issues. Here are troubleshooting tips and solutions:

- **Device Not Detected by the App:** If plugging in the camera does
  nothing, ensure that your phone supports **USB OTG (On-The-Go)** and
  that the USB host feature is declared in the app manifest. Some phones
  require enabling OTG in settings or have power-saving modes that
  disable it after a period. Also verify your `device_filter.xml`
  includes the camera's Vendor ID and Product ID so that Android knows
  your app can handle this USB device. (If the official Topdon app
  recognizes the camera but yours doesn't, it's likely a filter or
  permission issue.) Use Android's `UsbManager.getDeviceList()` to see
  if the camera appears at all. If not, the issue may be hardware (try a
  different cable or ensure the USB-C connector is fully inserted -- the
  camera should firmly attach, and on some devices you might need to
  flip the connector if it's orientation-specific).

- **Permission Denied or No Prompt:** If you never see the "Allow
  access" dialogue, it could be because another app (or a system service)
  has claimed the USB interface. Make sure no other app (including the
  default Topdon app or other camera apps) is running and auto-opening
  the device. Also confirm your intent filter is correct. In some cases,
  you might need to manually call
  `UsbManager.requestPermission(device, pendingIntent)` if the
  USBMonitor approach is not triggering. The SDK's `USBMonitor` will
  broadcast an intent with action `USBMonitor.ACTION_USB_PERMISSION` --
  ensure your activity is registered to receive it (the SDK's sample
  takes care of this internally).

- **Frame Freezes or No Image Output:** If the camera connects but you
  only see a black screen or one static frame, it could be a **bandwidth
  or mode issue**. The SDK allows adjusting USB bandwidth:
  `uvcCamera.setDefaultBandwidth(1.0f)` is used in the sample to request
  maximum
  bandwidth[\[39\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/com/infisense/usbir/camera/IRUVC.java#L422-L430).
  Some Android devices have limited USB bandwidth for external cameras.
  Try setting a lower bandwidth factor (closer to 0) if frames aren't
  coming through, or reduce the frame rate parameter in `startPreview()`
  (e.g., try 9 or 10 fps to see if that stabilizes output). Also, ensure
  that the data flow mode you request is supported by the camera: TC001
  should support the combined mode by default, but if you accidentally
  use a mode not supported (e.g., a higher resolution or a dual-camera
  mode on a single-camera device), it may not output. Use
  `uvcCamera.getSupportedSizeList()` to log what resolutions and modes
  the camera
  provides[\[40\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/com/infisense/usbir/camera/IRUVC.java#L516-L525).

- **Heat or Calibration Issues:** The camera has an internal shutter
  that periodically calibrates the sensor (you might hear a soft *click*
  every so often). During those moments (which typically last a fraction
  of a second), the image may pause or show a uniform field. This is
  normal -- the camera is self-correcting for drift. If you find the
  calibration happening too often or at inconvenient times, you can
  manually trigger it at a known safe moment using
  `ircmd.updateOOCOrB(CommonParams.UpdateOOCOrBType.B_UPDATE)` (which
  forces a **B shutter calibration**). Conversely, if the image over
  time develops offset (e.g., appears warmer or cooler than reality), a
  manual shutter trigger can help. Also note that the **TC001 Plus** has
  a known behaviour of *self-heating*: after a minute or so, the device's
  body warms up, which can slightly raise the reported temperature in
  parts of the image (e.g., edges) due to its own
  heat[\[41\]](https://www.reddit.com/r/Thermal/comments/1gc3nwc/topdon_tc001_plus_self_heating_gradient/#:~:text=Topdon%20TC001%20Plus%20self%20heating,5F%20hotter%20after%201%20minute).
  To mitigate this, allow the camera to warm up for a minute before
  recording critical data, and keep the lens cover open to let the
  shutter calibrate. Using the camera in a stable ambient environment
  yields best results.

- **USB Connection Stability:** If the camera frequently disconnects or
  frames stop, it could be a power issue -- the camera draws power from
  the phone. Ensure the phone is sufficiently charged and not in a
  low-power mode. Some users use a Y-cable to supply external power if
  needed, but for TC001 this is rarely required as power draw is modest
  (\~0.5 W). However, avoid having multiple high-power USB devices at
  once. Additionally, use the short OTG adapter that comes with the
  camera (or a high-quality cable) -- long or poor-quality cables can
  cause voltage drop or data errors. If you detect **frame errors** or
  the SDK flags a bad frame (the sample checks the last byte of the
  frame for a bad-frame
  flag[\[42\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/com/infisense/usbir/camera/IRUVC.java#L267-L276)),
  it will attempt a sensor restart. Occasional bad frames can occur; the
  SDK handles them by restarting the stream if necessary.

- **Performance and Threading:** Processing every frame (especially at
  25 Hz) can be CPU-intensive, particularly converting to bitmaps or
  running heavy computations. If the UI is lagging or frames are being
  dropped, ensure that the frame handling is off the main thread. The
  example above posts minimal work in the callback. The SDK sample uses
  a separate `ImageThread` for converting and drawing the image so that
  the USB thread isn't backed
  up[\[23\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/README.md#L120-L128)[\[27\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/README.md#L131-L140).
  You should adopt a similar strategy: do the image conversion and any
  heavy analysis (e.g., running face detection on the thermal image) in
  a worker thread. This will prevent the frame queue from overflowing
  (which would manifest as increasing latency or stuttering).

- **App Integration Issues:** If integrating into an existing app like
  `bucika_gsr`, watch out for **Android lifecycle** mismatches. For
  example, if the USB camera is streaming and the user rotates the
  screen (causing Activity restart), you should close and reopen the
  camera properly to avoid resource leaks or crashes. A good practice is
  to handle the camera in a foreground service that isn't tied to the
  Activity lifecycle (especially if you need to continue recording with
  the screen off). Alternatively, manage it in Activity but stop
  onPause. Also be mindful of permission persistence: the user's USB
  permission is typically remembered only until the device is detached.
  If your app exits and the camera is still plugged, the next launch
  will require permission again.

- **Error Codes and Debugging:** The SDK's `ResultCode` enum provides
  codes for failures (e.g., `SUCCESS = 0`, others for various errors).
  If `uvcCamera.openUVCCamera(ctrlBlock)` or `irCmd.startPreview()`
  returns non-zero, log or inspect those. Common errors might be related
  to device busy or invalid parameters. Ensure you are using the correct
  `IRCMDType` for your device model -- for TC001/Plus it's usually
  `USB_IR_256_384` as shown (the Plus might use the same, since the IR
  sensor resolution is 256×192; "512×384 super-resolution" mentioned in
  marketing refers to upscaling/fusion, not an actual sensor pixel
  count). If you choose a wrong type, the SDK might fail to initialise
  the IR command interface.

- **Image Orientation and Alignment:** The camera's default orientation
  might not match your app's view. If you see the image rotated by 90°
  or mirrored, use the SDK's `rotate()` or mirror settings. The `IRUVC`
  helper class in the sample, for instance, has a `setRotate(true)`
  option which rotates the image 90°
  right[\[43\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/com/infisense/usbir/activity/ImageOrTempDisplayActivity.java#L272-L275).
  You can also manually rotate the Bitmap before displaying. For
  alignment (especially for TC001 Plus fusion of visual and IR), ensure
  you use the provided alignment method from the SDK so that the thermal
  and visible images overlap correctly. If the visible image is not
  needed, you can ignore it; but if you do use it (say, to locate a
  face), remember the IR and RGB frames might have slight time offsets
  -- syncing them can be done by timestamp or by using the provided
  frame callback that perhaps delivers both in one call (depending on
  SDK capabilities).

If problems persist, consult the official Topdon SDK documentation (a
PDF is provided in the SDK package) and the community forums. The
**Topdon community** site has Q&As -- for example, guidance for using
the camera in custom
apps[\[44\]](https://community.topdon.com/detail?id=352&type=1#:~:text=Developing%20a%20Flutter%20App%20with,resources%20that%20would%20help)
-- and the official FAQ addresses issues like "camera not recognized by
phone" (often solved by ensuring the phone has OTG support or using the
correct
app)[\[45\]](https://github.com/leswright1977/PyThermalCamera/issues/16#:~:text=Topdon%20TC001%20Camera%20Special%20Commands,app%20use%20just%20the).
By systematically addressing the above points, you should be able to
reliably use the TC001/TC001 Plus in your Android project and collect
high-quality thermal data for your thesis work.

## References

- Topdon TC001 Product Page -- *Thermal Imaging Camera for Android
  Devices, 256×192 Resolution, -4 °F to 1022 °F
  range*[\[1\]](https://www.topdon.us/products/tc001?srsltid=AfmBOoocBj_-_hydfJjYl-1Yj8ADMJTtQyVLOHU9jP_SnN8s51-kisBU#:~:text=%E2%80%A2%20Equipped%20with%20an%20ultra,circuit%20boards%20and%20other%20electronics)[\[5\]](https://www.topdon.us/products/tc001?srsltid=AfmBOoocBj_-_hydfJjYl-1Yj8ADMJTtQyVLOHU9jP_SnN8s51-kisBU#:~:text=Optimized%20Temperature%20Range%20%26%20Accuracy).
- Topdon TC001 Plus Specifications -- *Dual-Lens 256×192 IR Camera,
  25 Hz frame rate, image fusion, ±2 °C
  accuracy*[\[46\]](https://www.topdon.us/products/tc001-plus?srsltid=AfmBOopq9mBNdV3ePkER8GhdlqhIks5h2xZMwObi-3oz_QF-meRQeAhV#:~:text=256x192)[\[47\]](https://www.topdon.us/products/tc001-plus?srsltid=AfmBOopq9mBNdV3ePkER8GhdlqhIks5h2xZMwObi-3oz_QF-meRQeAhV#:~:text=0).
- **Topdon Technology Thermal SDK (v1.3.7) -- Android Development
  Document**, Nov 2023. (Includes API reference and sample code for
  image acquisition, pseudocolor, and temperature
  extraction).[\[23\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/README.md#L120-L128)[\[48\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/com/infisense/usbir/view/TemperatureView.java#L153-L161)
- Gioia, F. *et al.* (2022). **"Towards a Contactless Stress
  Classification Using Thermal Imaging."** *Sensors, 22*(3), 976.\*
  (Discusses the use of thermal imaging alongside ECG, GSR (EDA), and
  respiration for stress
  detection)[\[7\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=Thermal%20imaging%20is%20currently%20taking,111%5D.%20Accordingly)[\[9\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=Thermal%20imaging%20unobtrusively%20monitors%20skin,in%20response%20to%20startling%20stimulus).
- Topdon Community Forum -- **Developing Android Apps with TC001** (Q&A
  thread)[\[44\]](https://community.topdon.com/detail?id=352&type=1#:~:text=Developing%20a%20Flutter%20App%20with,resources%20that%20would%20help).
  Guidance on SDK usage, known issues, and user experiences integrating
  the camera in custom applications.

------------------------------------------------------------------------

[\[1\]](https://www.topdon.us/products/tc001?srsltid=AfmBOoocBj_-_hydfJjYl-1Yj8ADMJTtQyVLOHU9jP_SnN8s51-kisBU#:~:text=%E2%80%A2%20Equipped%20with%20an%20ultra,circuit%20boards%20and%20other%20electronics)
[\[5\]](https://www.topdon.us/products/tc001?srsltid=AfmBOoocBj_-_hydfJjYl-1Yj8ADMJTtQyVLOHU9jP_SnN8s51-kisBU#:~:text=Optimized%20Temperature%20Range%20%26%20Accuracy)
TC001 (Android Devices) -- TOPDON USA

<https://www.topdon.us/products/tc001?srsltid=AfmBOoocBj_-_hydfJjYl-1Yj8ADMJTtQyVLOHU9jP_SnN8s51-kisBU>

[\[2\]](https://www.topdon.us/products/tc001-plus?srsltid=AfmBOopq9mBNdV3ePkER8GhdlqhIks5h2xZMwObi-3oz_QF-meRQeAhV#:~:text=8%C2%A0%E2%80%93%C2%A014%CE%BCm)
[\[3\]](https://www.topdon.us/products/tc001-plus?srsltid=AfmBOopq9mBNdV3ePkER8GhdlqhIks5h2xZMwObi-3oz_QF-meRQeAhV#:~:text=Sporting%20an%20ultra,analyse%20details%20of%20the%20targets)
[\[4\]](https://www.topdon.us/products/tc001-plus?srsltid=AfmBOopq9mBNdV3ePkER8GhdlqhIks5h2xZMwObi-3oz_QF-meRQeAhV#:~:text=Dual%20Lens%20to%20Unveil%20the,Unseen)
[\[6\]](https://www.topdon.us/products/tc001-plus?srsltid=AfmBOopq9mBNdV3ePkER8GhdlqhIks5h2xZMwObi-3oz_QF-meRQeAhV#:~:text=%E2%80%A2%20With%20a%20temperature%20range,1%C2%B0C)
[\[28\]](https://www.topdon.us/products/tc001-plus?srsltid=AfmBOopq9mBNdV3ePkER8GhdlqhIks5h2xZMwObi-3oz_QF-meRQeAhV#:~:text=1)
[\[34\]](https://www.topdon.us/products/tc001-plus?srsltid=AfmBOopq9mBNdV3ePkER8GhdlqhIks5h2xZMwObi-3oz_QF-meRQeAhV#:~:text=80)
[\[35\]](https://www.topdon.us/products/tc001-plus?srsltid=AfmBOopq9mBNdV3ePkER8GhdlqhIks5h2xZMwObi-3oz_QF-meRQeAhV#:~:text=Extensive%20%26%20Accurate%20Temperature%20Measurement)
[\[46\]](https://www.topdon.us/products/tc001-plus?srsltid=AfmBOopq9mBNdV3ePkER8GhdlqhIks5h2xZMwObi-3oz_QF-meRQeAhV#:~:text=256x192)
[\[47\]](https://www.topdon.us/products/tc001-plus?srsltid=AfmBOopq9mBNdV3ePkER8GhdlqhIks5h2xZMwObi-3oz_QF-meRQeAhV#:~:text=0)
TC001 Plus (Android Devices) -- TOPDON USA

<https://www.topdon.us/products/tc001-plus?srsltid=AfmBOopq9mBNdV3ePkER8GhdlqhIks5h2xZMwObi-3oz_QF-meRQeAhV>

[\[7\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=Thermal%20imaging%20is%20currently%20taking,111%5D.%20Accordingly)
[\[8\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=Thermal%20imaging%20unobtrusively%20monitors%20skin,to%20discriminate%20stimuli%20with%20positive)
[\[9\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=Thermal%20imaging%20unobtrusively%20monitors%20skin,in%20response%20to%20startling%20stimulus)
[\[10\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=variation%20of%20the%20nose%20tip,volume%20signal%20obtained%20from%20the)
[\[36\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=Thermal%20imaging%20unobtrusively%20monitors%20skin,18)
[\[37\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=We%20used%20thermal%20imaging%20to,e)
[\[38\]](https://www.mdpi.com/1424-8220/22/3/976#:~:text=Thermal%20imaging%20is%20currently%20taking,SNS%29%20branches%20of%20the)
Towards a Contactless Stress Classification Using Thermal Imaging

<https://www.mdpi.com/1424-8220/22/3/976>

[\[11\]](https://github.com/TopdonTechnology/Thermal#:~:text=ANDROID_SDK_USB_IR_1)
GitHub - TopdonTechnology/Thermal: Thermal SDK Document

<https://github.com/TopdonTechnology/Thermal>

[\[12\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/android/yt/jni/Usbcontorl.java#L8-L16)
Usbcontorl.java

<https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/android/yt/jni/Usbcontorl.java>

[\[13\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/AndroidManifest.xml#L79-L81)
[\[14\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/AndroidManifest.xml#L73-L81)
[\[15\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/AndroidManifest.xml#L74-L82)
[\[16\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/AndroidManifest.xml#L79-L83)
AndroidManifest.xml

<https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/AndroidManifest.xml>

[\[17\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/com/infisense/usbir/camera/IRUVC.java#L441-L450)
[\[18\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/com/infisense/usbir/camera/IRUVC.java#L443-L451)
[\[19\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/com/infisense/usbir/camera/IRUVC.java#L24-L32)
[\[20\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/com/infisense/usbir/camera/IRUVC.java#L26-L35)
[\[21\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/com/infisense/usbir/camera/IRUVC.java#L22-L30)
[\[24\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/com/infisense/usbir/camera/IRUVC.java#L163-L171)
[\[25\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/com/infisense/usbir/camera/IRUVC.java#L173-L181)
[\[26\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/com/infisense/usbir/camera/IRUVC.java#L165-L172)
[\[39\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/com/infisense/usbir/camera/IRUVC.java#L422-L430)
[\[40\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/com/infisense/usbir/camera/IRUVC.java#L516-L525)
[\[42\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/com/infisense/usbir/camera/IRUVC.java#L267-L276)
IRUVC.java

<https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/com/infisense/usbir/camera/IRUVC.java>

[\[22\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/README.md#L13-L21)
[\[23\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/README.md#L120-L128)
[\[27\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/README.md#L131-L140)
README.md

<https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/README.md>

[\[29\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/com/infisense/usbir/view/TemperatureView.java#L159-L167)
[\[30\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/com/infisense/usbir/view/TemperatureView.java#L2-L10)
[\[31\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/com/infisense/usbir/view/TemperatureView.java#L26-L34)
[\[32\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/com/infisense/usbir/view/TemperatureView.java#L26-L34)
[\[33\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/com/infisense/usbir/view/TemperatureView.java#L32-L40)
[\[48\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/com/infisense/usbir/view/TemperatureView.java#L153-L161)
TemperatureView.java

<https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/com/infisense/usbir/view/TemperatureView.java>

[\[41\]](https://www.reddit.com/r/Thermal/comments/1gc3nwc/topdon_tc001_plus_self_heating_gradient/#:~:text=Topdon%20TC001%20Plus%20self%20heating,5F%20hotter%20after%201%20minute)
Topdon TC001 Plus self heating gradient : r/Thermal - Reddit

<https://www.reddit.com/r/Thermal/comments/1gc3nwc/topdon_tc001_plus_self_heating_gradient/>

[\[43\]](https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/com/infisense/usbir/activity/ImageOrTempDisplayActivity.java#L272-L275)
ImageOrTempDisplayActivity.java

<https://github.com/buccancs/topdon-sdk/blob/83329a9fe4ebc275408c872b03aac1f4e13af0b0/ANDROID_SDK_USB_IR_1.3.7/libir_sample/usbir/src/main/java/com/infisense/usbir/activity/ImageOrTempDisplayActivity.java>

[\[44\]](https://community.topdon.com/detail?id=352&type=1#:~:text=Developing%20a%20Flutter%20App%20with,resources%20that%20would%20help)
Developing a Flutter App with Topdon TC001 Thermal Camera \...

<https://community.topdon.com/detail?id=352&type=1>

[\[45\]](https://github.com/leswright1977/PyThermalCamera/issues/16#:~:text=Topdon%20TC001%20Camera%20Special%20Commands,app%20use%20just%20the)
Topdon TC001 Camera Special Commands · Issue #16 - GitHub

<https://github.com/leswright1977/PyThermalCamera/issues/16>
