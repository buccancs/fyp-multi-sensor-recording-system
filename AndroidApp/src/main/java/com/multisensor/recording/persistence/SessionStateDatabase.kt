package com.multisensor.recording.persistence

import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import android.content.Context

/**
 * Phase 3: State Persistence System
 * Room database for session state persistence
 *
 * Extended to include Shimmer device state persistence for comprehensive
 * device configuration and connection state management across app restarts.
 * Supports multiple simultaneous Shimmer devices as required.
 */
@Database(
    entities = [
        SessionState::class,
        ShimmerDeviceState::class,
        ShimmerConnectionHistory::class
    ],
    version = 2, // Incremented version for new entities
    exportSchema = false
)
abstract class SessionStateDatabase : RoomDatabase() {
    
    abstract fun sessionStateDao(): SessionStateDao
    abstract fun shimmerDeviceStateDao(): ShimmerDeviceStateDao
    
    companion object {
        @Volatile
        private var INSTANCE: SessionStateDatabase? = null
        
        private const val DATABASE_NAME = "session_state_database"
        
        fun getDatabase(context: Context): SessionStateDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    SessionStateDatabase::class.java,
                    DATABASE_NAME
                )
                .fallbackToDestructiveMigration() // For Phase 3 initial implementation
                .build()
                INSTANCE = instance
                instance
            }
        }
    }
}