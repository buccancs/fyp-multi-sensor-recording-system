package com.multisensor.recording.ui.components

import android.content.Context
import android.graphics.Typeface
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.junit.Assert.*

/**
 * Unit tests for SectionHeaderView component
 * Ensures proper functionality and styling of section headers
 */
@RunWith(AndroidJUnit4::class)
class SectionHeaderViewTest {

    private lateinit var context: Context
    private lateinit var sectionHeaderView: SectionHeaderView

    @Before
    fun setUp() {
        context = ApplicationProvider.getApplicationContext()
        sectionHeaderView = SectionHeaderView(context)
    }

    @Test
    fun testInitialState() {
        // Test that the component initializes with default values
        assertNotNull(sectionHeaderView)
        // Default style should be SECTION_HEADER
        assertEquals(18f, sectionHeaderView.textSize / context.resources.displayMetrics.scaledDensity, 0.1f)
    }

    @Test
    fun testSetHeaderWithMainTitle() {
        // Test setting main title header
        sectionHeaderView.setHeader("Multi-Sensor Recording", SectionHeaderView.HeaderStyle.MAIN_TITLE)
        
        assertEquals("Multi-Sensor Recording", sectionHeaderView.text)
        assertEquals(24f, sectionHeaderView.textSize / context.resources.displayMetrics.scaledDensity, 0.1f)
        assertEquals(android.widget.TextView.TEXT_ALIGNMENT_CENTER, sectionHeaderView.textAlignment)
    }

    @Test
    fun testSetHeaderWithSectionHeader() {
        // Test setting section header (default style)
        sectionHeaderView.setHeader("Device Configuration", SectionHeaderView.HeaderStyle.SECTION_HEADER)
        
        assertEquals("Device Configuration", sectionHeaderView.text)
        assertEquals(18f, sectionHeaderView.textSize / context.resources.displayMetrics.scaledDensity, 0.1f)
        assertEquals(android.widget.TextView.TEXT_ALIGNMENT_TEXT_START, sectionHeaderView.textAlignment)
    }

    @Test
    fun testSetHeaderWithSubHeader() {
        // Test setting sub header
        sectionHeaderView.setHeader("Connection Settings", SectionHeaderView.HeaderStyle.SUB_HEADER)
        
        assertEquals("Connection Settings", sectionHeaderView.text)
        assertEquals(16f, sectionHeaderView.textSize / context.resources.displayMetrics.scaledDensity, 0.1f)
        assertEquals(android.widget.TextView.TEXT_ALIGNMENT_TEXT_START, sectionHeaderView.textAlignment)
    }

    @Test
    fun testSetHeaderWithDefaultStyle() {
        // Test setting header with default style parameter
        sectionHeaderView.setHeader("Default Header")
        
        assertEquals("Default Header", sectionHeaderView.text)
        assertEquals(18f, sectionHeaderView.textSize / context.resources.displayMetrics.scaledDensity, 0.1f)
    }

    @Test
    fun testTypefaceIsBold() {
        // Test that all header styles use bold typeface
        val styles = arrayOf(
            SectionHeaderView.HeaderStyle.MAIN_TITLE,
            SectionHeaderView.HeaderStyle.SECTION_HEADER,
            SectionHeaderView.HeaderStyle.SUB_HEADER
        )
        
        for (style in styles) {
            sectionHeaderView.setHeader("Test Header", style)
            assertTrue("Header should be bold for style $style", 
                sectionHeaderView.typeface.isBold || sectionHeaderView.typeface.style == Typeface.BOLD)
        }
    }

    @Test
    fun testSetHeaderTextColor() {
        // Test setting custom text color
        sectionHeaderView.setHeaderTextColor(android.R.color.holo_blue_light)
        
        // Color verification would require more complex testing setup
        // Just verify the method doesn't throw an exception
        assertNotNull(sectionHeaderView)
    }

    @Test
    fun testSetDarkTheme() {
        // Test setting dark theme
        sectionHeaderView.setDarkTheme()
        
        // Verify method executes without exception
        assertNotNull(sectionHeaderView)
    }

    @Test
    fun testSetLightTheme() {
        // Test setting light theme
        sectionHeaderView.setLightTheme()
        
        // Verify method executes without exception
        assertNotNull(sectionHeaderView)
    }

    @Test
    fun testTextSizesForAllStyles() {
        // Test that each style has the correct text size
        sectionHeaderView.setHeader("Test", SectionHeaderView.HeaderStyle.MAIN_TITLE)
        assertEquals(24f, sectionHeaderView.textSize / context.resources.displayMetrics.scaledDensity, 0.1f)
        
        sectionHeaderView.setHeader("Test", SectionHeaderView.HeaderStyle.SECTION_HEADER)
        assertEquals(18f, sectionHeaderView.textSize / context.resources.displayMetrics.scaledDensity, 0.1f)
        
        sectionHeaderView.setHeader("Test", SectionHeaderView.HeaderStyle.SUB_HEADER)
        assertEquals(16f, sectionHeaderView.textSize / context.resources.displayMetrics.scaledDensity, 0.1f)
    }

    @Test
    fun testTextAlignmentForAllStyles() {
        // Test text alignment for each style
        sectionHeaderView.setHeader("Test", SectionHeaderView.HeaderStyle.MAIN_TITLE)
        assertEquals(android.widget.TextView.TEXT_ALIGNMENT_CENTER, sectionHeaderView.textAlignment)
        
        sectionHeaderView.setHeader("Test", SectionHeaderView.HeaderStyle.SECTION_HEADER)
        assertEquals(android.widget.TextView.TEXT_ALIGNMENT_TEXT_START, sectionHeaderView.textAlignment)
        
        sectionHeaderView.setHeader("Test", SectionHeaderView.HeaderStyle.SUB_HEADER)
        assertEquals(android.widget.TextView.TEXT_ALIGNMENT_TEXT_START, sectionHeaderView.textAlignment)
    }

    @Test
    fun testMultipleHeaderChanges() {
        // Test changing header text and style multiple times
        sectionHeaderView.setHeader("First Header", SectionHeaderView.HeaderStyle.MAIN_TITLE)
        assertEquals("First Header", sectionHeaderView.text)
        
        sectionHeaderView.setHeader("Second Header", SectionHeaderView.HeaderStyle.SECTION_HEADER)
        assertEquals("Second Header", sectionHeaderView.text)
        
        sectionHeaderView.setHeader("Third Header", SectionHeaderView.HeaderStyle.SUB_HEADER)
        assertEquals("Third Header", sectionHeaderView.text)
    }

    @Test
    fun testEmptyHeaderText() {
        // Test setting empty header text
        sectionHeaderView.setHeader("")
        assertEquals("", sectionHeaderView.text)
    }

    @Test
    fun testLongHeaderText() {
        // Test setting very long header text
        val longText = "This is a very long header text that should still be handled properly by the component"
        sectionHeaderView.setHeader(longText)
        assertEquals(longText, sectionHeaderView.text)
    }

    @Test
    fun testSpecialCharactersInHeader() {
        // Test header with special characters
        val specialText = "Header with émojis 📱 and symbols ★ ♦ ♠"
        sectionHeaderView.setHeader(specialText)
        assertEquals(specialText, sectionHeaderView.text)
    }

    @Test
    fun testHeaderWithNumbers() {
        // Test header with numbers
        val numberText = "Section 1.2.3 - Configuration"
        sectionHeaderView.setHeader(numberText)
        assertEquals(numberText, sectionHeaderView.text)
    }

    @Test
    fun testThemeChangesAfterHeaderSet() {
        // Test changing theme after setting header
        sectionHeaderView.setHeader("Test Header", SectionHeaderView.HeaderStyle.MAIN_TITLE)
        sectionHeaderView.setDarkTheme()
        assertEquals("Test Header", sectionHeaderView.text)
        
        sectionHeaderView.setLightTheme()
        assertEquals("Test Header", sectionHeaderView.text)
    }

    @Test
    fun testComponentInheritance() {
        // Test that the component properly extends AppCompatTextView
        assertTrue("SectionHeaderView should extend AppCompatTextView", 
            sectionHeaderView is androidx.appcompat.widget.AppCompatTextView)
    }
}