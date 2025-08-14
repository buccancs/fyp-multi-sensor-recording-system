plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("kotlin-kapt")
}

android {
    namespace = "com.multisensor.recording"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.multisensor.recording"
        minSdk = 24
        targetSdk = 35
        versionCode = 1
        versionName = "1.0.0"
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildTypes {
        debug {
            isMinifyEnabled = false
            buildConfigField("String", "BUILD_TYPE", "\"debug\"")
        }
        release {
            isMinifyEnabled = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
            buildConfigField("String", "BUILD_TYPE", "\"release\"")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    buildFeatures {
        viewBinding = true
        buildConfig = true
    }

    packaging {
        resources {
            pickFirsts.add("META-INF/LICENSE.md")
            pickFirsts.add("META-INF/LICENSE-notice.md")
            excludes.add("META-INF/kotlinx-coroutines-core.kotlin_module")
        }
        jniLibs {
            useLegacyPackaging = false
            pickFirsts.addAll(listOf(
                "lib/arm64-v8a/libUSBUVCCamera.so", "lib/arm64-v8a/libencrypt.so",
                "lib/arm64-v8a/libusbcamera.so", "lib/arm64-v8a/libircmd.so",
                "lib/arm64-v8a/libirparse.so", "lib/arm64-v8a/libirprocess.so",
                "lib/arm64-v8a/libirtemp.so", "lib/arm64-v8a/libomp.so",
                "lib/arm64-v8a/libopencv_java4.so",
                "lib/armeabi-v7a/libUSBUVCCamera.so", "lib/armeabi-v7a/libencrypt.so",
                "lib/armeabi-v7a/libusbcamera.so", "lib/armeabi-v7a/libircmd.so",
                "lib/armeabi-v7a/libirparse.so", "lib/armeabi-v7a/libirprocess.so",
                "lib/armeabi-v7a/libirtemp.so", "lib/armeabi-v7a/libomp.so",
                "lib/armeabi-v7a/libopencv_java4.so",
                "lib/x86/libUSBUVCCamera.so", "lib/x86/libencrypt.so",
                "lib/x86/libusbcamera.so", "lib/x86/libircmd.so",
                "lib/x86/libirparse.so", "lib/x86/libirprocess.so",
                "lib/x86/libirtemp.so", "lib/x86/libomp.so",
                "lib/x86/libopencv_java4.so",
                "lib/x86_64/libUSBUVCCamera.so", "lib/x86_64/libencrypt.so",
                "lib/x86_64/libusbcamera.so", "lib/x86_64/libircmd.so",
                "lib/x86_64/libirparse.so", "lib/x86_64/libirprocess.so",
                "lib/x86_64/libirtemp.so", "lib/x86_64/libomp.so",
                "lib/x86_64/libopencv_java4.so"
            ))
        }
    }
}

dependencies {
    // Core Android dependencies
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.11.0")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
    implementation("androidx.activity:activity-ktx:1.8.2")
    implementation("androidx.fragment:fragment-ktx:1.6.2")
    implementation("androidx.cardview:cardview:1.0.0")

    // Camera
    implementation("androidx.camera:camera-core:1.3.1")
    implementation("androidx.camera:camera-camera2:1.3.1")
    implementation("androidx.camera:camera-lifecycle:1.3.1")
    implementation("androidx.camera:camera-video:1.3.1")
    implementation("androidx.camera:camera-view:1.3.1")
    implementation("androidx.camera:camera-extensions:1.3.1")

    // Lifecycle
    implementation("androidx.lifecycle:lifecycle-viewmodel-ktx:2.7.0")
    implementation("androidx.lifecycle:lifecycle-livedata-ktx:2.7.0")

    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")

    // Permissions - use standard Android permissions
    implementation("androidx.activity:activity-ktx:1.8.2") // For registerForActivityResult

    // IRCamera thermal camera SDKs (Topdon/InfiSense)
    implementation(files("src/main/libs/topdon_1.3.7.aar"))
    implementation(files("src/main/libs/libusbdualsdk_1.3.4_2406271906_standard.aar"))
    implementation(files("src/main/libs/opengl_1.3.2_standard.aar"))
    implementation(files("src/main/libs/suplib-release.aar"))
    
    // Shimmer GSR sensor SDKs
    implementation(files("src/main/libs/shimmerandroidinstrumentdriver-3.2.3_beta.aar"))
    implementation(files("src/main/libs/shimmerbluetoothmanager-0.11.4_beta.jar"))
    implementation(files("src/main/libs/shimmerdriver-0.11.4_beta.jar"))
    implementation(files("src/main/libs/shimmerdriverpc-0.11.4_beta.jar"))

    // Testing
    testImplementation("junit:junit:4.13.2")
    androidTestImplementation("androidx.test.ext:junit:1.1.5")
    androidTestImplementation("androidx.test.espresso:espresso-core:3.5.1")
}