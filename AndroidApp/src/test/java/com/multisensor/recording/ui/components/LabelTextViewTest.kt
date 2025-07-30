package com.multisensor.recording.ui.components

import android.content.Context
import android.graphics.Color
import android.text.SpannableString
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.junit.Assert.*

/**
 * Unit tests for LabelTextView component
 * Ensures proper functionality and styling of form labels and descriptive text
 */
@RunWith(AndroidJUnit4::class)
class LabelTextViewTest {

    private lateinit var context: Context
    private lateinit var labelTextView: LabelTextView

    @Before
    fun setUp() {
        context = ApplicationProvider.getApplicationContext()
        labelTextView = LabelTextView(context)
    }

    @Test
    fun testInitialState() {
        // Test that the component initializes with default values
        assertNotNull(labelTextView)
        // Default style should be FORM_LABEL (14sp)
        assertEquals(14f, labelTextView.textSize / context.resources.displayMetrics.scaledDensity, 0.1f)
    }

    @Test
    fun testSetLabelWithFormLabel() {
        // Test setting form label (default style)
        labelTextView.setLabel("Device Name:", LabelTextView.LabelStyle.FORM_LABEL)
        
        assertEquals("Device Name:", labelTextView.text)
        assertEquals(14f, labelTextView.textSize / context.resources.displayMetrics.scaledDensity, 0.1f)
    }

    @Test
    fun testSetLabelWithDescription() {
        // Test setting description style
        labelTextView.setLabel("Enter the device identifier", LabelTextView.LabelStyle.DESCRIPTION)
        
        assertEquals("Enter the device identifier", labelTextView.text)
        assertEquals(12f, labelTextView.textSize / context.resources.displayMetrics.scaledDensity, 0.1f)
    }

    @Test
    fun testSetLabelWithInstruction() {
        // Test setting instruction style
        labelTextView.setLabel("Please configure the following settings", LabelTextView.LabelStyle.INSTRUCTION)
        
        assertEquals("Please configure the following settings", labelTextView.text)
        assertEquals(14f, labelTextView.textSize / context.resources.displayMetrics.scaledDensity, 0.1f)
    }

    @Test
    fun testSetLabelWithError() {
        // Test setting error style
        labelTextView.setLabel("Invalid configuration", LabelTextView.LabelStyle.ERROR)
        
        assertEquals("Invalid configuration", labelTextView.text)
        assertEquals(14f, labelTextView.textSize / context.resources.displayMetrics.scaledDensity, 0.1f)
    }

    @Test
    fun testSetLabelWithSuccess() {
        // Test setting success style
        labelTextView.setLabel("Configuration saved successfully", LabelTextView.LabelStyle.SUCCESS)
        
        assertEquals("Configuration saved successfully", labelTextView.text)
        assertEquals(14f, labelTextView.textSize / context.resources.displayMetrics.scaledDensity, 0.1f)
    }

    @Test
    fun testSetLabelWithDefaultStyle() {
        // Test setting label with default style parameter
        labelTextView.setLabel("Default Label")
        
        assertEquals("Default Label", labelTextView.text)
        assertEquals(14f, labelTextView.textSize / context.resources.displayMetrics.scaledDensity, 0.1f)
    }

    @Test
    fun testSetLabelTextColorWithResource() {
        // Test setting custom text color with resource
        labelTextView.setLabelTextColor(android.R.color.holo_blue_light)
        
        // Color verification would require more complex testing setup
        // Just verify the method doesn't throw an exception
        assertNotNull(labelTextView)
    }

    @Test
    fun testSetLabelTextColorWithHex() {
        // Test setting custom text color with hex string
        labelTextView.setLabelTextColor("#FF0000")
        
        // Verify method executes without exception
        assertNotNull(labelTextView)
    }

    @Test
    fun testSetDarkTheme() {
        // Test setting dark theme
        labelTextView.setDarkTheme()
        
        // Verify method executes without exception
        assertNotNull(labelTextView)
    }

    @Test
    fun testSetLightTheme() {
        // Test setting light theme
        labelTextView.setLightTheme()
        
        // Verify method executes without exception
        assertNotNull(labelTextView)
    }

    @Test
    fun testSetRequired() {
        // Test setting required field indicator
        labelTextView.setLabel("Username")
        labelTextView.setRequired(true)
        
        // Should add asterisk to the text
        assertTrue("Required field should have asterisk", labelTextView.text.toString().endsWith("*"))
        assertEquals("Username*", labelTextView.text.toString())
    }

    @Test
    fun testSetRequiredMultipleTimes() {
        // Test setting required multiple times (should not add multiple asterisks)
        labelTextView.setLabel("Password")
        labelTextView.setRequired(true)
        labelTextView.setRequired(true)
        
        // Should only have one asterisk
        assertEquals("Password*", labelTextView.text.toString())
        assertEquals(1, labelTextView.text.toString().count { it == '*' })
    }

    @Test
    fun testSetRequiredFalse() {
        // Test setting required to false (should not add asterisk)
        labelTextView.setLabel("Optional Field")
        labelTextView.setRequired(false)
        
        assertEquals("Optional Field", labelTextView.text.toString())
        assertFalse("Non-required field should not have asterisk", labelTextView.text.toString().contains("*"))
    }

    @Test
    fun testSetClickableHelp() {
        // Test setting clickable help text
        var clicked = false
        val clickListener = android.view.View.OnClickListener { clicked = true }
        
        labelTextView.setClickableHelp(clickListener)
        
        // Verify clickable properties
        assertTrue("Help text should be clickable", labelTextView.isClickable)
        
        // Simulate click
        labelTextView.performClick()
        assertTrue("Click listener should be triggered", clicked)
    }

    @Test
    fun testSetClickableHelpWithNull() {
        // Test setting clickable help with null listener
        labelTextView.setClickableHelp(null)
        
        assertTrue("Should still be clickable even with null listener", labelTextView.isClickable)
        
        // Should not throw exception when clicked
        labelTextView.performClick()
    }

    @Test
    fun testAllLabelStyles() {
        // Test all label styles to ensure they don't throw exceptions
        val styles = arrayOf(
            LabelTextView.LabelStyle.FORM_LABEL,
            LabelTextView.LabelStyle.DESCRIPTION,
            LabelTextView.LabelStyle.INSTRUCTION,
            LabelTextView.LabelStyle.ERROR,
            LabelTextView.LabelStyle.SUCCESS
        )
        
        for (style in styles) {
            labelTextView.setLabel("Test Label", style)
            assertEquals("Text should be set for style $style", "Test Label", labelTextView.text)
        }
    }

    @Test
    fun testTextSizesForAllStyles() {
        // Test that each style has the correct text size
        labelTextView.setLabel("Test", LabelTextView.LabelStyle.FORM_LABEL)
        assertEquals(14f, labelTextView.textSize / context.resources.displayMetrics.scaledDensity, 0.1f)
        
        labelTextView.setLabel("Test", LabelTextView.LabelStyle.DESCRIPTION)
        assertEquals(12f, labelTextView.textSize / context.resources.displayMetrics.scaledDensity, 0.1f)
        
        labelTextView.setLabel("Test", LabelTextView.LabelStyle.INSTRUCTION)
        assertEquals(14f, labelTextView.textSize / context.resources.displayMetrics.scaledDensity, 0.1f)
        
        labelTextView.setLabel("Test", LabelTextView.LabelStyle.ERROR)
        assertEquals(14f, labelTextView.textSize / context.resources.displayMetrics.scaledDensity, 0.1f)
        
        labelTextView.setLabel("Test", LabelTextView.LabelStyle.SUCCESS)
        assertEquals(14f, labelTextView.textSize / context.resources.displayMetrics.scaledDensity, 0.1f)
    }

    @Test
    fun testMultipleLabelChanges() {
        // Test changing label text and style multiple times
        labelTextView.setLabel("First Label", LabelTextView.LabelStyle.FORM_LABEL)
        assertEquals("First Label", labelTextView.text)
        
        labelTextView.setLabel("Second Label", LabelTextView.LabelStyle.DESCRIPTION)
        assertEquals("Second Label", labelTextView.text)
        
        labelTextView.setLabel("Third Label", LabelTextView.LabelStyle.ERROR)
        assertEquals("Third Label", labelTextView.text)
    }

    @Test
    fun testEmptyLabelText() {
        // Test setting empty label text
        labelTextView.setLabel("")
        assertEquals("", labelTextView.text)
    }

    @Test
    fun testLongLabelText() {
        // Test setting very long label text
        val longText = "This is a very long label text that should still be handled properly by the component and wrap appropriately"
        labelTextView.setLabel(longText)
        assertEquals(longText, labelTextView.text)
    }

    @Test
    fun testSpecialCharactersInLabel() {
        // Test label with special characters
        val specialText = "Label with émojis 📝 and symbols ★ ♦ ♠"
        labelTextView.setLabel(specialText)
        assertEquals(specialText, labelTextView.text)
    }

    @Test
    fun testLabelWithNumbers() {
        // Test label with numbers
        val numberText = "Field 1.2.3:"
        labelTextView.setLabel(numberText)
        assertEquals(numberText, labelTextView.text)
    }

    @Test
    fun testRequiredWithSpecialCharacters() {
        // Test required field with special characters
        val specialText = "Spéciál Fïeld"
        labelTextView.setLabel(specialText)
        labelTextView.setRequired(true)
        assertEquals("Spéciál Fïeld*", labelTextView.text.toString())
    }

    @Test
    fun testThemeChangesAfterLabelSet() {
        // Test changing theme after setting label
        labelTextView.setLabel("Test Label", LabelTextView.LabelStyle.FORM_LABEL)
        labelTextView.setDarkTheme()
        assertEquals("Test Label", labelTextView.text)
        
        labelTextView.setLightTheme()
        assertEquals("Test Label", labelTextView.text)
    }

    @Test
    fun testComponentInheritance() {
        // Test that the component properly extends AppCompatTextView
        assertTrue("LabelTextView should extend AppCompatTextView", 
            labelTextView is androidx.appcompat.widget.AppCompatTextView)
    }

    @Test
    fun testFormFieldScenario() {
        // Test typical form field scenario
        labelTextView.setLabel("Email Address:", LabelTextView.LabelStyle.FORM_LABEL)
        labelTextView.setRequired(true)
        
        assertEquals("Email Address:*", labelTextView.text.toString())
        assertEquals(14f, labelTextView.textSize / context.resources.displayMetrics.scaledDensity, 0.1f)
    }

    @Test
    fun testErrorMessageScenario() {
        // Test error message scenario
        labelTextView.setLabel("Invalid email format", LabelTextView.LabelStyle.ERROR)
        
        assertEquals("Invalid email format", labelTextView.text)
        assertEquals(14f, labelTextView.textSize / context.resources.displayMetrics.scaledDensity, 0.1f)
    }

    @Test
    fun testHelpTextScenario() {
        // Test help text scenario
        var helpClicked = false
        labelTextView.setLabel("Need help?", LabelTextView.LabelStyle.DESCRIPTION)
        labelTextView.setClickableHelp { helpClicked = true }
        
        assertTrue(labelTextView.isClickable)
        labelTextView.performClick()
        assertTrue(helpClicked)
    }

    @Test
    fun testCombinedFeatures() {
        // Test combining multiple features
        labelTextView.setLabel("Required Field", LabelTextView.LabelStyle.FORM_LABEL)
        labelTextView.setRequired(true)
        labelTextView.setLabelTextColor("#0000FF")
        
        assertEquals("Required Field*", labelTextView.text.toString())
        assertTrue(labelTextView.text.toString().endsWith("*"))
    }
}