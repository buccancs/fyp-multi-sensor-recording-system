package com.multisensor.recording.ui

import android.content.Intent
import androidx.test.core.app.ActivityScenario
import androidx.test.core.app.ApplicationProvider
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.*
import androidx.test.espresso.assertion.ViewAssertions.*
import androidx.test.espresso.matcher.ViewMatchers.*
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.filters.LargeTest
import com.multisensor.recording.R
import com.multisensor.recording.recording.SessionInfo
import com.multisensor.recording.service.SessionManager
import com.multisensor.recording.util.Logger
import dagger.hilt.android.testing.HiltAndroidRule
import dagger.hilt.android.testing.HiltAndroidTest
import org.junit.After
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import javax.inject.Inject

@LargeTest
@RunWith(AndroidJUnit4::class)
@HiltAndroidTest
class FileViewActivityUITest {
    @get:Rule
    var hiltRule = HiltAndroidRule(this)

    @Inject
    lateinit var sessionManager: SessionManager

    @Inject
    lateinit var logger: Logger

    private lateinit var activityScenario: ActivityScenario<FileViewActivity>

    @Before
    fun setUp() {
        hiltRule.inject()

        // Create test session data
        createTestSessions()

        // Launch the activity
        val intent = Intent(ApplicationProvider.getApplicationContext(), FileViewActivity::class.java)
        activityScenario = ActivityScenario.launch(intent)

        logger.info("[DEBUG_LOG] FileViewActivity UI test setup completed")
    }

    @After
    fun tearDown() {
        try {
            activityScenario.close()
            // Clean up test sessions
            kotlinx.coroutines.runBlocking {
                sessionManager.deleteAllSessions()
            }
        } catch (e: Exception) {
            logger.error("[DEBUG_LOG] Error during UI test teardown: ${e.message}")
        }
    }

    @Test
    fun testActivityLaunchesSuccessfully() {
        // Verify that the activity launches and displays the main components
        onView(withId(R.id.search_edit_text))
            .check(matches(isDisplayed()))

        onView(withId(R.id.sessions_recycler_view))
            .check(matches(isDisplayed()))

        onView(withId(R.id.files_recycler_view))
            .check(matches(isDisplayed()))

        logger.info("[DEBUG_LOG] Activity launch test completed successfully")
    }

    @Test
    fun testSearchFunctionality() {
        // Test search functionality
        onView(withId(R.id.search_edit_text))
            .check(matches(isDisplayed()))
            .perform(typeText("test"))

        // Verify search input is accepted
        onView(withId(R.id.search_edit_text))
            .check(matches(withText("test")))

        // Clear search
        onView(withId(R.id.search_edit_text))
            .perform(clearText())

        logger.info("[DEBUG_LOG] Search functionality test completed")
    }

    @Test
    fun testFilterSpinner() {
        // Test filter spinner functionality
        onView(withId(R.id.filter_spinner))
            .check(matches(isDisplayed()))
            .perform(click())

        // The spinner should open (we can't easily test the dropdown items in Espresso)
        // But we can verify the spinner is clickable and responds
        onView(withId(R.id.filter_spinner))
            .check(matches(isClickable()))

        logger.info("[DEBUG_LOG] Filter spinner test completed")
    }

    @Test
    fun testSessionInfoDisplay() {
        // Test that session info is displayed
        onView(withId(R.id.session_info_text))
            .check(matches(isDisplayed()))

        onView(withId(R.id.progress_bar))
            .check(matches(isDisplayed()))

        onView(withId(R.id.empty_state_text))
            .check(matches(isDisplayed()))

        logger.info("[DEBUG_LOG] Session info display test completed")
    }

    @Test
    fun testEmptyStateHandling() {
        // Clear all sessions first
        kotlinx.coroutines.runBlocking {
            sessionManager.deleteAllSessions()
        }

        // Restart activity to see empty state
        activityScenario.close()
        val intent = Intent(ApplicationProvider.getApplicationContext(), FileViewActivity::class.java)
        activityScenario = ActivityScenario.launch(intent)

        // Check if empty state is handled properly
        // The RecyclerViews should still be displayed even if empty
        onView(withId(R.id.sessions_recycler_view))
            .check(matches(isDisplayed()))

        onView(withId(R.id.files_recycler_view))
            .check(matches(isDisplayed()))

        logger.info("[DEBUG_LOG] Empty state handling test completed")
    }

    @Test
    fun testRefreshButton() {
        // Test that refresh button is available
        onView(withId(R.id.refresh_button))
            .check(matches(isDisplayed()))
            .perform(click())

        // Verify refresh action works (activity should still be displayed)
        onView(withId(R.id.search_edit_text))
            .check(matches(isDisplayed()))

        logger.info("[DEBUG_LOG] Refresh button test completed")
    }

    @Test
    fun testRecyclerViewInteractions() {
        // Test that RecyclerViews are scrollable and interactive
        onView(withId(R.id.sessions_recycler_view))
            .check(matches(isDisplayed()))
            .perform(swipeUp())

        onView(withId(R.id.files_recycler_view))
            .check(matches(isDisplayed()))
            .perform(swipeUp())

        logger.info("[DEBUG_LOG] RecyclerView interactions test completed")
    }

    @Test
    fun testActivityRotation() {
        // Test that activity handles rotation properly
        onView(withId(R.id.search_edit_text))
            .check(matches(isDisplayed()))

        // Simulate rotation by recreating activity
        activityScenario.recreate()

        // Verify activity is still functional after rotation
        onView(withId(R.id.search_edit_text))
            .check(matches(isDisplayed()))

        onView(withId(R.id.sessions_recycler_view))
            .check(matches(isDisplayed()))

        logger.info("[DEBUG_LOG] Activity rotation test completed")
    }

    @Test
    fun testBackNavigation() {
        // Test back navigation
        onView(withId(R.id.search_edit_text))
            .check(matches(isDisplayed()))

        // Press back button (this should close the activity)
        androidx.test.espresso.Espresso
            .pressBack()

        // Activity should be finishing
        activityScenario.onActivity { activity ->
            assert(activity.isFinishing || activity.isDestroyed)
        }

        logger.info("[DEBUG_LOG] Back navigation test completed")
    }

    private fun createTestSessions() {
        try {
            kotlinx.coroutines.runBlocking {
                // Create a few test sessions
                val session1Id = sessionManager.createNewSession()
                val session2Id = sessionManager.createNewSession()

                logger.info("[DEBUG_LOG] Created test sessions: $session1Id, $session2Id")

                // Finalize sessions to make them available for viewing
                sessionManager.finalizeCurrentSession()
            }
        } catch (e: Exception) {
            logger.error("[DEBUG_LOG] Error creating test sessions: ${e.message}")
        }
    }
}
