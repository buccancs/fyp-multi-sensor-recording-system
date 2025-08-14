# Add project specific ProGuard rules here.
# You can control the set of applied configuration files using the
# proguardFiles setting in build.gradle.

# Keep thermal camera SDK classes
-keep class com.infisense.iruvc.** { *; }
-dontwarn com.infisense.iruvc.**

# Keep Shimmer SDK classes
-keep class com.shimmerresearch.** { *; }
-dontwarn com.shimmerresearch.**

# Keep Camera2 classes
-keep class androidx.camera.** { *; }
-dontwarn androidx.camera.**

# Keep reflection-based methods
-keepclassmembers class * {
    @android.webkit.JavascriptInterface <methods>;
}

# General Android rules
-keepattributes Signature
-keepattributes *Annotation*
-keep public class com.google.vending.licensing.ILicensingService
-keep public class com.android.vending.licensing.ILicensingService