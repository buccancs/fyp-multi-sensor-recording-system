package com.multisensor.recording.persistence

import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import android.content.Context

/**
 * Phase 3: State Persistence System
 * Room database for session state persistence
 *
 * Implements the Phase 3 requirement for persistent session state management
 * to support crash recovery and session restoration capabilities.
 */
@Database(
    entities = [SessionState::class],
    version = 1,
    exportSchema = false
)
abstract class SessionStateDatabase : RoomDatabase() {
    
    abstract fun sessionStateDao(): SessionStateDao
    
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