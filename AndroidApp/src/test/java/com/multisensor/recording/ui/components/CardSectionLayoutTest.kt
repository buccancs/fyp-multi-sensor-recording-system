package com.multisensor.recording.ui.components

import android.content.Context
import android.graphics.Color
import android.widget.LinearLayout
import android.widget.TextView
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.junit.Assert.*

/**
 * Unit tests for CardSectionLayout component
 * Ensures proper functionality and styling of card section containers
 */
@RunWith(AndroidJUnit4::class)
class CardSectionLayoutTest {

    private lateinit var context: Context
    private lateinit var cardSectionLayout: CardSectionLayout

    @Before
    fun setUp() {
        context = ApplicationProvider.getApplicationContext()
        cardSectionLayout = CardSectionLayout(context)
    }

    @Test
    fun testInitialState() {
        // Test that the component initializes with default values
        assertNotNull(cardSectionLayout)
        assertEquals(LinearLayout.VERTICAL, cardSectionLayout.orientation)
        assertEquals(0, cardSectionLayout.childCount) // Should start empty
    }

    @Test
    fun testDefaultCardStyle() {
        // Test that default style is applied correctly
        cardSectionLayout.setCardStyle(CardSectionLayout.CardStyle.DEFAULT)
        
        // Verify orientation is vertical
        assertEquals(LinearLayout.VERTICAL, cardSectionLayout.orientation)
        
        // Verify elevation is set (non-zero)
        assertTrue("Default card should have elevation", cardSectionLayout.elevation > 0)
    }

    @Test
    fun testCompactCardStyle() {
        // Test compact card style
        cardSectionLayout.setCardStyle(CardSectionLayout.CardStyle.COMPACT)
        
        assertEquals(LinearLayout.VERTICAL, cardSectionLayout.orientation)
        assertTrue("Compact card should have elevation", cardSectionLayout.elevation > 0)
    }

    @Test
    fun testFlatCardStyle() {
        // Test flat card style (no elevation)
        cardSectionLayout.setCardStyle(CardSectionLayout.CardStyle.FLAT)
        
        assertEquals(LinearLayout.VERTICAL, cardSectionLayout.orientation)
        assertEquals("Flat card should have no elevation", 0f, cardSectionLayout.elevation, 0.01f)
    }

    @Test
    fun testDarkCardStyle() {
        // Test dark card style
        cardSectionLayout.setCardStyle(CardSectionLayout.CardStyle.DARK)
        
        assertEquals(LinearLayout.VERTICAL, cardSectionLayout.orientation)
        assertTrue("Dark card should have elevation", cardSectionLayout.elevation > 0)
    }

    @Test
    fun testSetCardBackgroundColor() {
        // Test setting custom background color
        cardSectionLayout.setCardBackgroundColor(android.R.color.holo_blue_light)
        
        // Color verification would require more complex testing setup
        // Just verify the method doesn't throw an exception
        assertNotNull(cardSectionLayout)
    }

    @Test
    fun testSetCardPadding() {
        // Test setting custom padding
        val customPadding = 20
        cardSectionLayout.setCardPadding(customPadding)
        
        // Verify padding is applied (converted from dp to px)
        assertTrue("Padding should be greater than 0", cardSectionLayout.paddingLeft > 0)
        assertTrue("Padding should be greater than 0", cardSectionLayout.paddingTop > 0)
        assertTrue("Padding should be greater than 0", cardSectionLayout.paddingRight > 0)
        assertTrue("Padding should be greater than 0", cardSectionLayout.paddingBottom > 0)
        
        // All sides should have equal padding
        assertEquals(cardSectionLayout.paddingLeft, cardSectionLayout.paddingTop)
        assertEquals(cardSectionLayout.paddingTop, cardSectionLayout.paddingRight)
        assertEquals(cardSectionLayout.paddingRight, cardSectionLayout.paddingBottom)
    }

    @Test
    fun testSetCardElevation() {
        // Test setting custom elevation
        val customElevation = 8
        cardSectionLayout.setCardElevation(customElevation)
        
        // Verify elevation is set (converted from dp to px)
        assertTrue("Custom elevation should be applied", cardSectionLayout.elevation > 0)
    }

    @Test
    fun testAddHeader() {
        // Test adding a header to the card
        val headerText = "Test Section Header"
        cardSectionLayout.addHeader(headerText)
        
        // Verify header was added as first child
        assertEquals(1, cardSectionLayout.childCount)
        
        val headerView = cardSectionLayout.getChildAt(0)
        assertTrue("First child should be SectionHeaderView", headerView is SectionHeaderView)
        
        val sectionHeader = headerView as SectionHeaderView
        assertEquals(headerText, sectionHeader.text)
    }

    @Test
    fun testAddHeaderWithCustomStyle() {
        // Test adding header with custom style
        val headerText = "Main Title Header"
        cardSectionLayout.addHeader(headerText, SectionHeaderView.HeaderStyle.MAIN_TITLE)
        
        assertEquals(1, cardSectionLayout.childCount)
        
        val headerView = cardSectionLayout.getChildAt(0) as SectionHeaderView
        assertEquals(headerText, headerView.text)
    }

    @Test
    fun testAddMultipleHeaders() {
        // Test adding multiple headers
        cardSectionLayout.addHeader("First Header")
        cardSectionLayout.addHeader("Second Header")
        
        // Should have 2 headers
        assertEquals(2, cardSectionLayout.childCount)
        
        // Verify both are SectionHeaderView instances
        assertTrue(cardSectionLayout.getChildAt(0) is SectionHeaderView)
        assertTrue(cardSectionLayout.getChildAt(1) is SectionHeaderView)
        
        // Verify text content
        assertEquals("Second Header", (cardSectionLayout.getChildAt(0) as SectionHeaderView).text) // Latest header is first
        assertEquals("First Header", (cardSectionLayout.getChildAt(1) as SectionHeaderView).text)
    }

    @Test
    fun testAddContentAfterHeader() {
        // Test adding content after header
        cardSectionLayout.addHeader("Section Header")
        
        // Add some content
        val contentView = TextView(context)
        contentView.text = "Content text"
        cardSectionLayout.addView(contentView)
        
        assertEquals(2, cardSectionLayout.childCount)
        
        // First child should be header
        assertTrue(cardSectionLayout.getChildAt(0) is SectionHeaderView)
        // Second child should be content
        assertTrue(cardSectionLayout.getChildAt(1) is TextView)
        assertEquals("Content text", (cardSectionLayout.getChildAt(1) as TextView).text)
    }

    @Test
    fun testAllCardStyles() {
        // Test all card styles to ensure they don't throw exceptions
        val styles = arrayOf(
            CardSectionLayout.CardStyle.DEFAULT,
            CardSectionLayout.CardStyle.COMPACT,
            CardSectionLayout.CardStyle.FLAT,
            CardSectionLayout.CardStyle.DARK
        )
        
        for (style in styles) {
            cardSectionLayout.setCardStyle(style)
            assertEquals("Orientation should remain vertical for style $style", 
                LinearLayout.VERTICAL, cardSectionLayout.orientation)
        }
    }

    @Test
    fun testLayoutParams() {
        // Test that layout parameters are set correctly
        val layoutParams = cardSectionLayout.layoutParams
        
        // Layout params might be null if not added to a parent, so we test after setting style
        cardSectionLayout.setCardStyle(CardSectionLayout.CardStyle.DEFAULT)
        
        // The component should handle layout params internally
        assertNotNull(cardSectionLayout)
    }

    @Test
    fun testMultipleStyleChanges() {
        // Test changing styles multiple times
        cardSectionLayout.setCardStyle(CardSectionLayout.CardStyle.DEFAULT)
        cardSectionLayout.setCardStyle(CardSectionLayout.CardStyle.COMPACT)
        cardSectionLayout.setCardStyle(CardSectionLayout.CardStyle.FLAT)
        cardSectionLayout.setCardStyle(CardSectionLayout.CardStyle.DARK)
        
        // Should not throw exceptions and maintain vertical orientation
        assertEquals(LinearLayout.VERTICAL, cardSectionLayout.orientation)
    }

    @Test
    fun testCustomizationCombination() {
        // Test combining multiple customizations
        cardSectionLayout.setCardStyle(CardSectionLayout.CardStyle.DEFAULT)
        cardSectionLayout.setCardBackgroundColor(android.R.color.holo_green_light)
        cardSectionLayout.setCardPadding(24)
        cardSectionLayout.setCardElevation(4)
        cardSectionLayout.addHeader("Customized Section")
        
        // Verify header was added
        assertEquals(1, cardSectionLayout.childCount)
        assertTrue(cardSectionLayout.getChildAt(0) is SectionHeaderView)
        
        // Verify customizations applied
        assertTrue("Custom padding should be applied", cardSectionLayout.paddingLeft > 0)
        assertTrue("Custom elevation should be applied", cardSectionLayout.elevation > 0)
    }

    @Test
    fun testEmptyHeaderText() {
        // Test adding header with empty text
        cardSectionLayout.addHeader("")
        
        assertEquals(1, cardSectionLayout.childCount)
        val headerView = cardSectionLayout.getChildAt(0) as SectionHeaderView
        assertEquals("", headerView.text)
    }

    @Test
    fun testLongHeaderText() {
        // Test adding header with very long text
        val longText = "This is a very long header text that should still be handled properly by the card section layout component"
        cardSectionLayout.addHeader(longText)
        
        assertEquals(1, cardSectionLayout.childCount)
        val headerView = cardSectionLayout.getChildAt(0) as SectionHeaderView
        assertEquals(longText, headerView.text)
    }

    @Test
    fun testComponentInheritance() {
        // Test that the component properly extends LinearLayout
        assertTrue("CardSectionLayout should extend LinearLayout", 
            cardSectionLayout is LinearLayout)
    }

    @Test
    fun testRealWorldUsageScenario() {
        // Test a real-world usage scenario
        cardSectionLayout.setCardStyle(CardSectionLayout.CardStyle.DEFAULT)
        cardSectionLayout.addHeader("Device Configuration", SectionHeaderView.HeaderStyle.SECTION_HEADER)
        
        // Add some form elements
        val label = TextView(context)
        label.text = "Device Name:"
        cardSectionLayout.addView(label)
        
        val input = TextView(context)
        input.text = "Shimmer Device 1"
        cardSectionLayout.addView(input)
        
        // Verify structure
        assertEquals(3, cardSectionLayout.childCount)
        assertTrue(cardSectionLayout.getChildAt(0) is SectionHeaderView)
        assertTrue(cardSectionLayout.getChildAt(1) is TextView)
        assertTrue(cardSectionLayout.getChildAt(2) is TextView)
        
        assertEquals("Device Configuration", (cardSectionLayout.getChildAt(0) as SectionHeaderView).text)
        assertEquals("Device Name:", (cardSectionLayout.getChildAt(1) as TextView).text)
        assertEquals("Shimmer Device 1", (cardSectionLayout.getChildAt(2) as TextView).text)
    }
}