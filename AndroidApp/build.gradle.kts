import java.time.Duration
import groovy.json.JsonSlurper

plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("com.google.devtools.ksp")
    id("dagger.hilt.android.plugin")
    id("io.gitlab.arturbosch.detekt") version "1.23.6"
    id("jacoco")
}

android {
    namespace = "com.multisensor.recording"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.multisensor.recording"
        minSdk = 24
        targetSdk = 35
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "com.multisensor.recording.CustomTestRunner"

        ndk {
            abiFilters.addAll(listOf("arm64-v8a", "armeabi-v7a", "x86", "x86_64"))
        }
    }

    packaging {
        resources {
            pickFirsts.add("META-INF/LICENSE.md")
            pickFirsts.add("META-INF/LICENSE-notice.md")
            excludes.add("META-INF/kotlinx-coroutines-core.kotlin_module")
        }

        jniLibs {
            useLegacyPackaging = false
            val libsToPickFirst = listOf(
                "libUSBUVCCamera.so", "libencrypt.so", "libusbcamera.so", "libircmd.so",
                "libirparse.so", "libirprocess.so", "libirtemp.so", "libomp.so"
            )
            val abis = listOf("arm64-v8a", "armeabi-v7a", "x86", "x86_64")
            abis.forEach { abi ->
                libsToPickFirst.forEach { lib ->
                    pickFirsts.add("lib/$abi/$lib")
                }
            }
        }
    }

    buildTypes {
        debug {
            isMinifyEnabled = false
            buildConfigField("String", "BUILD_TYPE", "\"debug\"")
            enableUnitTestCoverage = true
            enableAndroidTestCoverage = true
            ndk {
                debugSymbolLevel = "SYMBOL_TABLE"
            }
        }

        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
            buildConfigField("String", "BUILD_TYPE", "\"release\"")
            ndk {
                debugSymbolLevel = "SYMBOL_TABLE"
            }
        }

        create("staging") {
            initWith(getByName("debug"))
            isDebuggable = false
            buildConfigField("String", "BUILD_TYPE", "\"staging\"")
        }
    }

    flavorDimensions.add("environment")
    productFlavors {
        create("dev") {
            dimension = "environment"
            applicationIdSuffix = ".dev"
            versionNameSuffix = "-dev"
            buildConfigField("String", "ENVIRONMENT", "\"development\"")
        }
        create("prod") {
            dimension = "environment"
            buildConfigField("String", "ENVIRONMENT", "\"production\"")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
        freeCompilerArgs += listOf(
            "-opt-in=kotlin.RequiresOptIn",
            "-opt-in=kotlinx.coroutines.ExperimentalCoroutinesApi",
            "-opt-in=kotlin.time.ExperimentalTime",
            "-opt-in=kotlin.ExperimentalStdlibApi",
            "-Xjsr305=strict"
        )
    }

    buildFeatures {
        viewBinding = true
        buildConfig = true
    }

    testOptions {
        animationsDisabled = true
        execution = "ANDROIDX_TEST_ORCHESTRATOR"
        unitTests {
            isIncludeAndroidResources = true
            isReturnDefaultValues = true
            all {
                it.jvmArgs(
                    "-XX:MaxMetaspaceSize=512m",
                    "-Djava.awt.headless=true",
                    "-Dfile.encoding=UTF-8",
                    "--add-opens=java.base/java.lang=ALL-UNNAMED"
                )
                it.maxHeapSize = "2048m"
                it.useJUnitPlatform {
                    includeEngines("junit-jupiter", "junit-vintage")
                    includeTags("unit", "integration", "performance")
                    excludeTags("manual", "stress")
                }
                it.systemProperty("robolectric.useWindowsCompatibleTempDir", "true")
                it.reports.html.required.set(true)
                it.reports.junitXml.required.set(true)
            }
        }
        managedDevices {
            devices {
                create<com.android.build.api.dsl.ManagedVirtualDevice>("pixel2api30") {
                    device = "Pixel 2"
                    apiLevel = 30
                    systemImageSource = "aosp"
                }
            }
        }
    }

    sourceSets {
        getByName("main") {
            java.srcDirs("$buildDir/generated/source/config")
        }
    }
}

//--------------- Configurations & Dependencies ---------------//

configurations {
    val ktlint by creating
}

dependencies {
    // Core & UI Components
    implementation(libs.bundles.core.ui)

    // Settings and Preferences
    implementation("androidx.preference:preference-ktx:1.2.1")

    // Material Design Components
    implementation("com.google.android.material:material:1.12.0")
    implementation("androidx.cardview:cardview:1.0.0")

    // Jetpack Navigation
    implementation("androidx.navigation:navigation-fragment-ktx:2.7.7")
    implementation("androidx.navigation:navigation-ui-ktx:2.7.7")
    testImplementation("androidx.navigation:navigation-testing:2.7.7") // For testing navigation graphs

    // Architecture
    implementation(libs.bundles.lifecycle)
    implementation(libs.kotlinx.coroutines.android)
    implementation(libs.bundles.activity.fragment)
    testImplementation("androidx.arch.core:core-testing:2.2.0") // For testing Architecture Components
    testImplementation("androidx.fragment:fragment-testing:1.7.1") // For testing Fragments
    testImplementation(libs.kotlinx.coroutines.test) // For testing coroutines (assuming alias exists)

    // Permissions
    implementation(libs.xxpermissions)

    // CameraX
    implementation(libs.bundles.camera)
    testImplementation(libs.bundles.camera.testing) // For testing CameraX (assuming alias exists)

    // Dependency Injection
    implementation(libs.hilt.android)
    ksp(libs.hilt.compiler)

    // Room Database
    implementation(libs.bundles.room)
    ksp(libs.room.compiler)
    testImplementation(libs.bundles.room.testing) // For testing Room (assuming alias exists)

    // Networking
    implementation(libs.bundles.networking)
    testImplementation("com.squareup.okhttp3:mockwebserver:4.12.0") // For mocking server responses

    // Unit Testing
    testImplementation(libs.bundles.enhanced.unit.testing)
    testImplementation(libs.hilt.android.testing)
    kspTest(libs.hilt.compiler)

    // Integration Testing
    androidTestImplementation(libs.bundles.enhanced.integration.testing)
    androidTestUtil("androidx.test:orchestrator:1.5.0")
    androidTestImplementation(libs.hilt.android.testing)
    kspAndroidTest(libs.hilt.compiler)

    // Code Quality
    ktlint("com.pinterest:ktlint:0.51.0")
    detektPlugins("io.gitlab.arturbosch.detekt:detekt-formatting:1.23.6")

    // Local SDKs
    implementation(files("src/main/libs/shimmerandroidinstrumentdriver-3.2.3_beta.aar"))
    testImplementation(files("src/main/libs/shimmerandroidinstrumentdriver-3.2.3_beta.aar"))
    implementation(files("src/main/libs/shimmerbluetoothmanager-0.11.4_beta.jar"))
    testImplementation(files("src/main/libs/shimmerbluetoothmanager-0.11.4_beta.jar"))
    implementation(files("src/main/libs/shimmerdriver-0.11.4_beta.jar"))
    testImplementation(files("src/main/libs/shimmerdriver-0.11.4_beta.jar"))
    implementation(files("src/main/libs/shimmerdriverpc-0.11.4_beta.jar"))
    testImplementation(files("src/main/libs/shimmerdriverpc-0.11.4_beta.jar"))
    implementation(files("src/main/libs/topdon_1.3.7.aar"))
    testImplementation(files("src/main/libs/topdon_1.3.7.aar"))
    implementation(files("src/main/libs/libusbdualsdk_1.3.4_2406271906_standard.aar"))
    testImplementation(files("src/main/libs/libusbdualsdk_1.3.4_2406271906_standard.aar"))
    implementation(files("src/main/libs/opengl_1.3.2_standard.aar"))
    testImplementation(files("src/main/libs/opengl_1.3.2_standard.aar"))
    implementation(files("src/main/libs/suplib-release.aar"))
    testImplementation(files("src/main/libs/suplib-release.aar"))
}

//--------------- Custom Tasks & Build Logic ---------------//

val outputDir = file("$buildDir/generated/source/config")
tasks.register("generateConstants") {
    group = "build"
    description = "Generates Kotlin constants from config.json."
    val configFile = file("src/main/assets/config.json")
    val outputFile = file("$outputDir/com/multisensor/recording/config/CommonConstants.kt")

    inputs.file(configFile)
    outputs.file(outputFile)

    doLast {
        val json = JsonSlurper().parse(configFile) as Map<*, *>
        outputDir.mkdirs()
        outputFile.writeText("""
        // Auto-generated from config.json. Do not edit manually.
        package com.multisensor.recording.config
        object CommonConstants {
            const val PROTOCOL_VERSION: Int = ${json["protocol_version"]}
            const val APP_VERSION: String = "${json["version"]}"
        }
        """.trimIndent())
        println("Generated CommonConstants.kt from config.json")
    }
}

tasks.named("preBuild") {
    dependsOn("generateConstants")
}

detekt {
    buildUponDefaultConfig = true
    allRules = false
    config.setFrom(files("$projectDir/../detekt.yml"))
    baseline.set(file("$projectDir/detekt-baseline.xml"))
    reports {
        html.required.set(true)
        xml.required.set(true)
        sarif.required.set(true)
    }
}

jacoco {
    toolVersion = "0.8.12"
}

tasks.register<JacocoReport>("jacocoTestReport") {
    group = "Reporting"
    description = "Generates Jacoco coverage reports for all variants."

    dependsOn(tasks.matching { it.name.startsWith("test") && it.name.endsWith("UnitTest") })

    reports {
        xml.required.set(true)
        html.required.set(true)
    }

    val fileFilter = listOf(
        "**/R.class", "**/R$*.class", "**/BuildConfig.*",
        "**/*_Factory.*", "**/*_MembersInjector.*", "**/*Module*.*",
        "**/databinding/*", "**/generated/**/*.*"
    )
    val javaClasses = fileTree("$buildDir/intermediates/javac/debug/classes") { exclude(fileFilter) }
    val kotlinClasses = fileTree("$buildDir/tmp/kotlin-classes/debug") { exclude(fileFilter) }

    classDirectories.setFrom(files(javaClasses, kotlinClasses))
    sourceDirectories.setFrom(files("$projectDir/src/main/java", "$projectDir/src/main/kotlin"))
    executionData.setFrom(fileTree(buildDir) { include("jacoco/**/*.exec", "outputs/code_coverage/**/*.ec") })

    doFirst {
        executionData.setFrom(files(executionData.files.filter { it.exists() }))
    }
}

tasks.register<JavaExec>("formatKotlin") {
    group = "formatting"
    description = "Format Kotlin code with ktlint."
    classpath = configurations.ktlint.get()
    mainClass.set("com.pinterest.ktlint.Main")
    args("-F", "src/**/*.kt")
}

tasks.register<JavaExec>("lintKotlin") {
    group = "verification"
    description = "Check Kotlin code style with ktlint."
    classpath = configurations.ktlint.get()
    mainClass.set("com.pinterest.ktlint.Main")
    args("src/**/*.kt")
}

tasks.named("check") {
    dependsOn("detekt", "lintKotlin")
}

tasks.named("build") {
    finalizedBy("jacocoTestReport")
}
