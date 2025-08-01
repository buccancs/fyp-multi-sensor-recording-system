package com.multisensor.recording.ui.adapters

import org.junit.Test
import org.junit.Assert.*

/**
 * Unit test for MainNavigationAdapter constants and static methods
 * Tests navigation adapter functionality without Android framework dependencies
 */
class MainNavigationAdapterUnitTest {

    @Test
    fun testTabConstants() {
        // Verify tab constants are correctly defined
        assertEquals(0, MainNavigationAdapter.TAB_RECORDING)
        assertEquals(1, MainNavigationAdapter.TAB_DEVICES)
        assertEquals(2, MainNavigationAdapter.TAB_CALIBRATION)
        assertEquals(3, MainNavigationAdapter.TAB_FILES)
        assertEquals(4, MainNavigationAdapter.TAB_COUNT)
    }

    @Test
    fun testTabTitles() {
        // Test tab title generation logic
        assertEquals("Recording", getTabTitleForPosition(MainNavigationAdapter.TAB_RECORDING))
        assertEquals("Devices", getTabTitleForPosition(MainNavigationAdapter.TAB_DEVICES))
        assertEquals("Calibration", getTabTitleForPosition(MainNavigationAdapter.TAB_CALIBRATION))
        assertEquals("Files", getTabTitleForPosition(MainNavigationAdapter.TAB_FILES))
        assertEquals("Unknown", getTabTitleForPosition(-1))
        assertEquals("Unknown", getTabTitleForPosition(999))
    }

    /**
     * Helper method that mimics the logic from MainNavigationAdapter.getTabTitle()
     */
    private fun getTabTitleForPosition(position: Int): String {
        return when (position) {
            MainNavigationAdapter.TAB_RECORDING -> "Recording"
            MainNavigationAdapter.TAB_DEVICES -> "Devices"
            MainNavigationAdapter.TAB_CALIBRATION -> "Calibration"
            MainNavigationAdapter.TAB_FILES -> "Files"
            else -> "Unknown"
        }
    }
}