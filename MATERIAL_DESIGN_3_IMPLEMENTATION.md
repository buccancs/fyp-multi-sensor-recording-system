# Material Design 3 Implementation Guide

## 🎨 Color System Implementation

### Dynamic Color Palette
```xml
<!-- res/values/colors.xml - Material Design 3 Color System -->
<resources>
    <!-- Primary Color Palette -->
    <color name="md_theme_light_primary">#6750A4</color>
    <color name="md_theme_light_onPrimary">#FFFFFF</color>
    <color name="md_theme_light_primaryContainer">#EADDFF</color>
    <color name="md_theme_light_onPrimaryContainer">#21005D</color>
    
    <!-- Secondary Color Palette -->
    <color name="md_theme_light_secondary">#625B71</color>
    <color name="md_theme_light_onSecondary">#FFFFFF</color>
    <color name="md_theme_light_secondaryContainer">#E8DEF8</color>
    <color name="md_theme_light_onSecondaryContainer">#1D192B</color>
    
    <!-- Tertiary Color Palette -->
    <color name="md_theme_light_tertiary">#7D5260</color>
    <color name="md_theme_light_onTertiary">#FFFFFF</color>
    <color name="md_theme_light_tertiaryContainer">#FFD8E4</color>
    <color name="md_theme_light_onTertiaryContainer">#31111D</color>
    
    <!-- Error Color Palette -->
    <color name="md_theme_light_error">#BA1A1A</color>
    <color name="md_theme_light_errorContainer">#FFDAD6</color>
    <color name="md_theme_light_onError">#FFFFFF</color>
    <color name="md_theme_light_onErrorContainer">#410002</color>
    
    <!-- Surface Color Palette -->
    <color name="md_theme_light_background">#FFFBFE</color>
    <color name="md_theme_light_onBackground">#1C1B1F</color>
    <color name="md_theme_light_surface">#FFFBFE</color>
    <color name="md_theme_light_onSurface">#1C1B1F</color>
    <color name="md_theme_light_surfaceVariant">#E7E0EC</color>
    <color name="md_theme_light_onSurfaceVariant">#49454F</color>
    <color name="md_theme_light_outline">#79747E</color>
    <color name="md_theme_light_inverseOnSurface">#F4EFF4</color>
    <color name="md_theme_light_inverseSurface">#313033</color>
    <color name="md_theme_light_inversePrimary">#D0BCFF</color>
    <color name="md_theme_light_shadow">#000000</color>
    <color name="md_theme_light_surfaceTint">#6750A4</color>
    <color name="md_theme_light_outlineVariant">#CAC4D0</color>
    <color name="md_theme_light_scrim">#000000</color>
    
    <!-- Dark Theme Colors -->
    <color name="md_theme_dark_primary">#D0BCFF</color>
    <color name="md_theme_dark_onPrimary">#381E72</color>
    <color name="md_theme_dark_primaryContainer">#4F378B</color>
    <color name="md_theme_dark_onPrimaryContainer">#EADDFF</color>
    <!-- ... additional dark theme colors ... -->
</resources>
```

### Theme Definition
```xml
<!-- res/values/themes.xml -->
<resources>
    <!-- Material Design 3 Light Theme -->
    <style name="Theme.BucikaGSR" parent="Theme.Material3.DayNight">
        <item name="colorPrimary">@color/md_theme_light_primary</item>
        <item name="colorOnPrimary">@color/md_theme_light_onPrimary</item>
        <item name="colorPrimaryContainer">@color/md_theme_light_primaryContainer</item>
        <item name="colorOnPrimaryContainer">@color/md_theme_light_onPrimaryContainer</item>
        <item name="colorSecondary">@color/md_theme_light_secondary</item>
        <item name="colorOnSecondary">@color/md_theme_light_onSecondary</item>
        <item name="colorSecondaryContainer">@color/md_theme_light_secondaryContainer</item>
        <item name="colorOnSecondaryContainer">@color/md_theme_light_onSecondaryContainer</item>
        <item name="colorTertiary">@color/md_theme_light_tertiary</item>
        <item name="colorOnTertiary">@color/md_theme_light_onTertiary</item>
        <item name="colorTertiaryContainer">@color/md_theme_light_tertiaryContainer</item>
        <item name="colorOnTertiaryContainer">@color/md_theme_light_onTertiaryContainer</item>
        <item name="colorError">@color/md_theme_light_error</item>
        <item name="colorErrorContainer">@color/md_theme_light_errorContainer</item>
        <item name="colorOnError">@color/md_theme_light_onError</item>
        <item name="colorOnErrorContainer">@color/md_theme_light_onErrorContainer</item>
        <item name="android:colorBackground">@color/md_theme_light_background</item>
        <item name="colorOnBackground">@color/md_theme_light_onBackground</item>
        <item name="colorSurface">@color/md_theme_light_surface</item>
        <item name="colorOnSurface">@color/md_theme_light_onSurface</item>
        <item name="colorSurfaceVariant">@color/md_theme_light_surfaceVariant</item>
        <item name="colorOnSurfaceVariant">@color/md_theme_light_onSurfaceVariant</item>
        <item name="colorOutline">@color/md_theme_light_outline</item>
        <item name="colorOnSurfaceInverse">@color/md_theme_light_inverseOnSurface</item>
        <item name="colorSurfaceInverse">@color/md_theme_light_inverseSurface</item>
        <item name="colorPrimaryInverse">@color/md_theme_light_inversePrimary</item>
    </style>
</resources>
```

## 📝 Typography System

```xml
<!-- res/values/type.xml -->
<resources>
    <!-- Display Typography -->
    <style name="TextAppearance.BucikaGSR.DisplayLarge" parent="TextAppearance.Material3.DisplayLarge">
        <item name="fontFamily">@font/roboto</item>
        <item name="android:fontWeight">400</item>
        <item name="android:textSize">57sp</item>
        <item name="android:lineHeight">64sp</item>
        <item name="android:letterSpacing">-0.25sp</item>
    </style>
    
    <!-- Headline Typography -->
    <style name="TextAppearance.BucikaGSR.HeadlineMedium" parent="TextAppearance.Material3.HeadlineMedium">
        <item name="fontFamily">@font/roboto</item>
        <item name="android:fontWeight">400</item>
        <item name="android:textSize">28sp</item>
        <item name="android:lineHeight">36sp</item>
    </style>
    
    <!-- Title Typography -->
    <style name="TextAppearance.BucikaGSR.TitleLarge" parent="TextAppearance.Material3.TitleLarge">
        <item name="fontFamily">@font/roboto</item>
        <item name="android:fontWeight">400</item>
        <item name="android:textSize">22sp</item>
        <item name="android:lineHeight">28sp</item>
    </style>
    
    <!-- Body Typography -->
    <style name="TextAppearance.BucikaGSR.BodyLarge" parent="TextAppearance.Material3.BodyLarge">
        <item name="fontFamily">@font/roboto</item>
        <item name="android:fontWeight">400</item>
        <item name="android:textSize">16sp</item>
        <item name="android:lineHeight">24sp</item>
        <item name="android:letterSpacing">0.5sp</item>
    </style>
    
    <!-- Label Typography -->
    <style name="TextAppearance.BucikaGSR.LabelMedium" parent="TextAppearance.Material3.LabelMedium">
        <item name="fontFamily">@font/roboto</item>
        <item name="android:fontWeight">500</item>
        <item name="android:textSize">12sp</item>
        <item name="android:lineHeight">16sp</item>
        <item name="android:letterSpacing">0.5sp</item>
    </style>
</resources>
```

## 🧩 Component Implementation Examples

### 1. Enhanced Recording Interface

```xml
<!-- activity_main_md3.xml -->
<androidx.coordinatorlayout.widget.CoordinatorLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:fitsSystemWindows="true">

    <!-- Top App Bar -->
    <com.google.android.material.appbar.AppBarLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:fitsSystemWindows="true">

        <com.google.android.material.appbar.MaterialToolbar
            android:id="@+id/topAppBar"
            android:layout_width="match_parent"
            android:layout_height="?attr/actionBarSize"
            app:title="Bucika GSR"
            app:titleTextAppearance="@style/TextAppearance.BucikaGSR.TitleLarge"
            app:menu="@menu/top_app_bar" />

    </com.google.android.material.appbar.AppBarLayout>

    <!-- Main Content with Bottom Navigation -->
    <androidx.fragment.app.FragmentContainerView
        android:id="@+id/nav_host_fragment"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        app:layout_behavior="@string/appbar_scrolling_view_behavior" />

    <!-- Recording FAB -->
    <com.google.android.material.floatingactionbutton.FloatingActionButton
        android:id="@+id/recordingFab"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_gravity="bottom|end"
        android:layout_marginEnd="16dp"
        android:layout_marginBottom="80dp"
        android:contentDescription="@string/start_recording"
        app:srcCompat="@drawable/ic_record_24"
        app:fabSize="large"
        app:backgroundTint="?attr/colorPrimary"
        app:tint="?attr/colorOnPrimary" />

    <!-- Bottom Navigation -->
    <com.google.android.material.bottomnavigation.BottomNavigationView
        android:id="@+id/bottom_navigation"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_gravity="bottom"
        app:menu="@menu/bottom_navigation_menu"
        app:backgroundTint="?attr/colorSurface"
        app:itemIconTint="?attr/colorOnSurface"
        app:itemTextColor="?attr/colorOnSurface" />

</androidx.coordinatorlayout.widget.CoordinatorLayout>
```

### 2. Status Cards with Material Design 3

```xml
<!-- fragment_recording.xml -->
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:padding="16dp">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical">

        <!-- Device Status Card -->
        <com.google.android.material.card.MaterialCardView
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginBottom="16dp"
            app:cardCornerRadius="12dp"
            app:cardElevation="2dp"
            app:strokeWidth="0dp">

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical"
                android:padding="16dp">

                <TextView
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:text="Device Status"
                    android:textAppearance="@style/TextAppearance.BucikaGSR.TitleLarge"
                    android:layout_marginBottom="12dp" />

                <!-- Status Chips -->
                <com.google.android.material.chip.ChipGroup
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    app:chipSpacing="8dp"
                    app:lineSpacing="4dp">

                    <com.google.android.material.chip.Chip
                        android:id="@+id/shimmerStatusChip"
                        style="@style/Widget.Material3.Chip.Filter"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:text="Shimmer GSR"
                        app:chipIcon="@drawable/ic_sensors_24"
                        app:chipIconTint="?attr/colorOnSecondaryContainer"
                        app:chipBackgroundColor="?attr/colorSecondaryContainer"
                        android:textColor="?attr/colorOnSecondaryContainer" />

                    <com.google.android.material.chip.Chip
                        android:id="@+id/thermalStatusChip"
                        style="@style/Widget.Material3.Chip.Filter"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:text="Thermal Camera"
                        app:chipIcon="@drawable/ic_camera_24"
                        app:chipIconTint="?attr/colorOnTertiaryContainer"
                        app:chipBackgroundColor="?attr/colorTertiaryContainer"
                        android:textColor="?attr/colorOnTertiaryContainer" />

                    <com.google.android.material.chip.Chip
                        android:id="@+id/pcStatusChip"
                        style="@style/Widget.Material3.Chip.Filter"
                        android:layout_width="wrap_content"
                        android:layout_height="wrap_content"
                        android:text="PC Connection"
                        app:chipIcon="@drawable/ic_computer_24"
                        app:chipIconTint="?attr/colorOnPrimaryContainer"
                        app:chipBackgroundColor="?attr/colorPrimaryContainer"
                        android:textColor="?attr/colorOnPrimaryContainer" />

                </com.google.android.material.chip.ChipGroup>

            </LinearLayout>

        </com.google.android.material.card.MaterialCardView>

        <!-- Recording Controls Card -->
        <com.google.android.material.card.MaterialCardView
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginBottom="16dp"
            app:cardCornerRadius="12dp"
            app:cardElevation="2dp">

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical"
                android:padding="16dp">

                <TextView
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:text="Recording Controls"
                    android:textAppearance="@style/TextAppearance.BucikaGSR.TitleLarge"
                    android:layout_marginBottom="16dp" />

                <LinearLayout
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:orientation="horizontal">

                    <com.google.android.material.button.MaterialButton
                        android:id="@+id/calibrationButton"
                        style="@style/Widget.Material3.Button.TonalButton"
                        android:layout_width="0dp"
                        android:layout_height="wrap_content"
                        android:layout_weight="1"
                        android:layout_marginEnd="8dp"
                        android:text="Calibration"
                        app:icon="@drawable/ic_calibrate_24"
                        app:cornerRadius="20dp" />

                    <com.google.android.material.button.MaterialButton
                        android:id="@+id/handSegmentationButton"
                        style="@style/Widget.Material3.Button.OutlinedButton"
                        android:layout_width="0dp"
                        android:layout_height="wrap_content"
                        android:layout_weight="1"
                        android:layout_marginStart="8dp"
                        android:text="Hand Detect"
                        app:icon="@drawable/ic_hand_24"
                        app:cornerRadius="20dp" />

                </LinearLayout>

            </LinearLayout>

        </com.google.android.material.card.MaterialCardView>

        <!-- Real-time Data Preview Card -->
        <com.google.android.material.card.MaterialCardView
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            app:cardCornerRadius="12dp"
            app:cardElevation="2dp">

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical"
                android:padding="16dp">

                <TextView
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:text="Live Data Preview"
                    android:textAppearance="@style/TextAppearance.BucikaGSR.TitleLarge"
                    android:layout_marginBottom="16dp" />

                <!-- Data visualization would go here -->
                <TextView
                    android:layout_width="match_parent"
                    android:layout_height="100dp"
                    android:text="📊 GSR Signal Chart\n🌡️ Thermal Display\n📹 Video Preview"
                    android:textAppearance="@style/TextAppearance.BucikaGSR.BodyLarge"
                    android:gravity="center"
                    android:background="?attr/colorSurfaceVariant"
                    android:textColor="?attr/colorOnSurfaceVariant" />

            </LinearLayout>

        </com.google.android.material.card.MaterialCardView>

    </LinearLayout>

</ScrollView>
```

### 3. Bottom Navigation Menu

```xml
<!-- res/menu/bottom_navigation_menu.xml -->
<menu xmlns:android="http://schemas.android.com/apk/res/android">
    <item
        android:id="@+id/nav_recording"
        android:enabled="true"
        android:icon="@drawable/ic_record_24"
        android:title="Recording" />
    <item
        android:id="@+id/nav_monitoring"
        android:enabled="true"
        android:icon="@drawable/ic_monitor_24"
        android:title="Monitoring" />
    <item
        android:id="@+id/nav_files"
        android:enabled="true"
        android:icon="@drawable/ic_folder_24"
        android:title="Files" />
    <item
        android:id="@+id/nav_settings"
        android:enabled="true"
        android:icon="@drawable/ic_settings_24"
        android:title="Settings" />
    <item
        android:id="@+id/nav_advanced"
        android:enabled="true"
        android:icon="@drawable/ic_build_24"
        android:title="Advanced" />
</menu>
```

## 🎯 Accessibility Implementation

### Content Descriptions
```xml
<!-- Accessibility-enhanced components -->
<com.google.android.material.chip.Chip
    android:id="@+id/shimmerStatusChip"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:text="Shimmer GSR"
    android:contentDescription="Shimmer GSR sensor status: connected"
    android:hint="Tap to view sensor details"
    app:chipIcon="@drawable/ic_sensors_24" />

<com.google.android.material.floatingactionbutton.FloatingActionButton
    android:id="@+id/recordingFab"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:contentDescription="Start recording session"
    android:hint="Press to begin multi-sensor data recording"
    app:srcCompat="@drawable/ic_record_24" />
```

### Focus Management
```xml
<!-- Sequential focus order -->
<LinearLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:focusable="true"
    android:nextFocusDown="@+id/recordingControls">
    
    <com.google.android.material.chip.Chip
        android:id="@+id/firstChip"
        android:nextFocusRight="@+id/secondChip"
        android:nextFocusDown="@+id/calibrationButton" />
        
    <com.google.android.material.chip.Chip
        android:id="@+id/secondChip"
        android:nextFocusLeft="@+id/firstChip"
        android:nextFocusDown="@+id/handSegmentationButton" />
        
</LinearLayout>
```

### Live Regions for Dynamic Content
```xml
<TextView
    android:id="@+id/statusText"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:accessibilityLiveRegion="polite"
    android:accessibilityHeading="true"
    android:textAppearance="@style/TextAppearance.BucikaGSR.BodyLarge" />
```

## 🚀 Animation and Motion

### Enter/Exit Transitions
```xml
<!-- res/anim/slide_in_bottom.xml -->
<set xmlns:android="http://schemas.android.com/apk/res/android">
    <translate
        android:duration="300"
        android:fromYDelta="100%"
        android:toYDelta="0"
        android:interpolator="@android:interpolator/decelerate_quart" />
    <alpha
        android:duration="300"
        android:fromAlpha="0.0"
        android:toAlpha="1.0" />
</set>

<!-- res/anim/slide_out_bottom.xml -->
<set xmlns:android="http://schemas.android.com/apk/res/android">
    <translate
        android:duration="200"
        android:fromYDelta="0"
        android:toYDelta="100%"
        android:interpolator="@android:interpolator/accelerate_quad" />
    <alpha
        android:duration="200"
        android:fromAlpha="1.0"
        android:toAlpha="0.0" />
</set>
```

### Fragment Transitions
```kotlin
// In Activity
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    
    // Configure fragment transitions
    supportFragmentManager.setFragmentResultListener("navigation") { _, bundle ->
        val targetFragment = bundle.getString("target")
        navigateToFragment(targetFragment)
    }
}

private fun navigateToFragment(fragmentName: String) {
    val fragment = when (fragmentName) {
        "recording" -> RecordingFragment()
        "monitoring" -> MonitoringFragment()
        "files" -> FilesFragment()
        "settings" -> SettingsFragment()
        "advanced" -> AdvancedFragment()
        else -> RecordingFragment()
    }
    
    supportFragmentManager.beginTransaction()
        .setCustomAnimations(
            R.anim.slide_in_right,
            R.anim.slide_out_left,
            R.anim.slide_in_left,
            R.anim.slide_out_right
        )
        .replace(R.id.nav_host_fragment, fragment)
        .addToBackStack(null)
        .commit()
}
```

## 📊 Implementation Checklist

### Phase 1: Core Material Design 3 Setup
- [ ] Update `build.gradle` dependencies to Material Design 3
- [ ] Migrate color system to MD3 tokens
- [ ] Update typography to MD3 type scale
- [ ] Replace theme with Material3 base theme

### Phase 2: Component Migration
- [ ] Convert buttons to MaterialButton variants
- [ ] Replace LinearLayouts with CardView where appropriate
- [ ] Implement status chips instead of colored rectangles
- [ ] Add FloatingActionButton for primary recording action

### Phase 3: Navigation Update
- [ ] Implement BottomNavigationView
- [ ] Create fragment-based architecture
- [ ] Add proper navigation animations
- [ ] Implement navigation drawer for secondary features

### Phase 4: Accessibility Enhancement
- [ ] Add content descriptions to all interactive elements
- [ ] Implement proper focus management
- [ ] Add live regions for dynamic content
- [ ] Test with TalkBack and Switch Access

### Phase 5: Polish and Testing
- [ ] Add motion and animation
- [ ] Implement dark theme support
- [ ] Performance testing and optimization
- [ ] User acceptance testing

This implementation guide provides a comprehensive roadmap for modernizing the Bucika GSR app with Material Design 3 principles while maintaining accessibility and usability standards.