package com.multisensor.recording.ui.adapters

import androidx.fragment.app.Fragment
import androidx.fragment.app.FragmentActivity
import androidx.viewpager2.adapter.FragmentStateAdapter
import com.multisensor.recording.ui.fragments.RecordingFragment
import com.multisensor.recording.ui.fragments.DevicesFragment
import com.multisensor.recording.ui.fragments.CalibrationFragment
import com.multisensor.recording.ui.fragments.FilesFragment

/**
 * ViewPager adapter for main navigation between different app sections.
 * Provides fragment-based navigation with consistent state management.
 */
class MainNavigationAdapter(fragmentActivity: FragmentActivity) : FragmentStateAdapter(fragmentActivity) {

    companion object {
        const val TAB_RECORDING = 0
        const val TAB_DEVICES = 1
        const val TAB_CALIBRATION = 2
        const val TAB_FILES = 3
        const val TAB_COUNT = 4
    }

    override fun getItemCount(): Int = TAB_COUNT

    override fun createFragment(position: Int): Fragment {
        return when (position) {
            TAB_RECORDING -> RecordingFragment()
            TAB_DEVICES -> DevicesFragment()
            TAB_CALIBRATION -> CalibrationFragment()
            TAB_FILES -> FilesFragment()
            else -> throw IllegalArgumentException("Invalid tab position: $position")
        }
    }

    /**
     * Get tab title for the given position
     */
    fun getTabTitle(position: Int): String {
        return when (position) {
            TAB_RECORDING -> "Recording"
            TAB_DEVICES -> "Devices"
            TAB_CALIBRATION -> "Calibration"
            TAB_FILES -> "Files"
            else -> "Unknown"
        }
    }
}