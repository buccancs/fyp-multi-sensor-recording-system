package com.multisensor.recording.persistence

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update
import kotlinx.coroutines.flow.Flow

/**
 * Phase 3: State Persistence System
 * DAO for SessionState database operations
 *
 * Provides the database access operations for session state persistence
 * supporting crash recovery and session restoration.
 */
@Dao
interface SessionStateDao {
    
    /**
     * Insert or replace session state
     */
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertSessionState(sessionState: SessionState)
    
    /**
     * Update existing session state
     */
    @Update
    suspend fun updateSessionState(sessionState: SessionState)
    
    /**
     * Get session state by ID
     */
    @Query("SELECT * FROM session_state WHERE sessionId = :sessionId")
    suspend fun getSessionState(sessionId: String): SessionState?
    
    /**
     * Get all session states
     */
    @Query("SELECT * FROM session_state ORDER BY timestamp DESC")
    suspend fun getAllSessionStates(): List<SessionState>
    
    /**
     * Get active sessions (not completed or failed)
     */
    @Query("SELECT * FROM session_state WHERE recordingState IN ('STARTING', 'RECORDING') ORDER BY timestamp DESC")
    suspend fun getActiveSessions(): List<SessionState>
    
    /**
     * Get the most recent session state
     */
    @Query("SELECT * FROM session_state ORDER BY timestamp DESC LIMIT 1")
    suspend fun getLatestSession(): SessionState?
    
    /**
     * Delete session state by ID
     */
    @Query("DELETE FROM session_state WHERE sessionId = :sessionId")
    suspend fun deleteSessionState(sessionId: String)
    
    /**
     * Delete old completed sessions (older than specified timestamp)
     */
    @Query("DELETE FROM session_state WHERE recordingState IN ('COMPLETED', 'FAILED') AND timestamp < :cutoffTime")
    suspend fun deleteOldSessions(cutoffTime: Long)
    
    /**
     * Get sessions with errors
     */
    @Query("SELECT * FROM session_state WHERE errorOccurred = 1 ORDER BY timestamp DESC")
    suspend fun getFailedSessions(): List<SessionState>
    
    /**
     * Observe active sessions for real-time updates
     */
    @Query("SELECT * FROM session_state WHERE recordingState IN ('STARTING', 'RECORDING') ORDER BY timestamp DESC")
    fun observeActiveSessions(): Flow<List<SessionState>>
}