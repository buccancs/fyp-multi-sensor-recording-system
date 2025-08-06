package com.multisensor.recording.ui

import android.content.SharedPreferences
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class OnboardingActivityTest {

    private lateinit var sharedPreferences: SharedPreferences

    @Before
    fun setup() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        sharedPreferences = context.getSharedPreferences("app_prefs", android.content.Context.MODE_PRIVATE)

        sharedPreferences.edit().remove("onboarding_completed").apply()
    }

    @Test
    fun shouldShowOnboarding_WhenFirstLaunch_ReturnsTrue() {

        assertTrue(OnboardingActivity.shouldShowOnboarding(sharedPreferences))
    }

    @Test
    fun shouldShowOnboarding_WhenCompleted_ReturnsFalse() {

        sharedPreferences.edit().putBoolean("onboarding_completed", true).apply()

        assertFalse(OnboardingActivity.shouldShowOnboarding(sharedPreferences))
    }
}