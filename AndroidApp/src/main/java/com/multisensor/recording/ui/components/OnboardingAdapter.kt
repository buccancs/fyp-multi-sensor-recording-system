package com.multisensor.recording.ui.components

import androidx.fragment.app.Fragment
import androidx.fragment.app.FragmentActivity
import androidx.viewpager2.adapter.FragmentStateAdapter

class OnboardingAdapter(activity: FragmentActivity) : FragmentStateAdapter(activity) {
    
    override fun getItemCount(): Int = 3
    
    override fun createFragment(position: Int): Fragment {
        return when (position) {
            0 -> OnboardingPageFragment.newInstance(
                title = "Welcome to Multi-Sensor Recording",
                description = "This app collects synchronized data from multiple sensors including camera, thermal imaging, and physiological sensors for research purposes.",
                iconRes = com.multisensor.recording.R.drawable.ic_devices,
                showFeatures = listOf(
                    "📷 RGB Camera Recording",
                    "🌡️ Thermal Camera Integration", 
                    "📊 GSR Sensor Data",
                    "⏱️ Synchronized Timestamps"
                )
            )
            1 -> OnboardingPageFragment.newInstance(
                title = "PC Controller Setup",
                description = "Connect your PC controller for enhanced functionality and data processing. Ensure both devices are on the same Wi-Fi network.",
                iconRes = com.multisensor.recording.R.drawable.ic_network,
                showFeatures = listOf(
                    "🖥️ Connect PC controller via Wi-Fi",
                    "📡 Real-time data streaming",
                    "💾 Automatic data backup",
                    "⚙️ Remote configuration"
                )
            )
            2 -> OnboardingPageFragment.newInstance(
                title = "Permissions Required",
                description = "Grant the following permissions to ensure proper functionality. All data is processed locally and used only for research purposes.",
                iconRes = com.multisensor.recording.R.drawable.ic_settings,
                showFeatures = listOf(
                    "📷 Camera - For RGB video recording",
                    "🎙️ Microphone - For audio recording", 
                    "📍 Location - For Bluetooth device detection",
                    "📶 Bluetooth - For sensor connectivity"
                )
            )
            else -> throw IllegalArgumentException("Invalid position: $position")
        }
    }
}