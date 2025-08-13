package com.multisensor.recording.firebase

import com.google.firebase.firestore.FirebaseFirestore
import com.google.firebase.firestore.ktx.toObject
import kotlinx.coroutines.tasks.await
import javax.inject.Inject
import javax.inject.Singleton
import java.util.Date

/**
 * Firebase Firestore service for storing research data and metadata
 */
@Singleton
class FirebaseFirestoreService @Inject constructor(
    private val firestore: FirebaseFirestore
) {

    /**
     * Data class for recording session metadata
     */
    data class RecordingSession(
        val sessionId: String = "",
        val startTime: Date = Date(),
        val endTime: Date? = null,
        val deviceCount: Int = 0,
        val gsrSensorIds: List<String> = emptyList(),
        val thermalCameraModel: String = "",
        val rgbCameraResolution: String = "",
        val thermalResolution: String = "",
        val calibrationData: Map<String, Any> = emptyMap(),
        val dataFilePaths: Map<String, String> = emptyMap(),
        val totalDataSizeBytes: Long = 0,
        val researcherId: String = "",
        val participantId: String = "",
        val experimentType: String = "",
        val notes: String = ""
    )

    /**
     * Save recording session metadata
     */
    suspend fun saveRecordingSession(session: RecordingSession): Result<String> {
        return try {
            val docRef = firestore.collection("recording_sessions").document()
            val sessionWithId = session.copy(sessionId = docRef.id)
            docRef.set(sessionWithId).await()
            Result.success(docRef.id)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Update recording session with end time and final data
     */
    suspend fun updateRecordingSessionEnd(
        sessionId: String,
        endTime: Date,
        dataFilePaths: Map<String, String>,
        totalDataSizeBytes: Long
    ): Result<Unit> {
        return try {
            firestore.collection("recording_sessions").document(sessionId)
                .update(
                    mapOf(
                        "endTime" to endTime,
                        "dataFilePaths" to dataFilePaths,
                        "totalDataSizeBytes" to totalDataSizeBytes
                    )
                ).await()
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Get recording session by ID
     */
    suspend fun getRecordingSession(sessionId: String): Result<RecordingSession?> {
        return try {
            val doc = firestore.collection("recording_sessions").document(sessionId).get().await()
            val session = doc.toObject<RecordingSession>()
            Result.success(session)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Get recording sessions for a researcher
     */
    suspend fun getRecordingSessionsForResearcher(researcherId: String): Result<List<RecordingSession>> {
        return try {
            val snapshot = firestore.collection("recording_sessions")
                .whereEqualTo("researcherId", researcherId)
                .orderBy("startTime", com.google.firebase.firestore.Query.Direction.DESCENDING)
                .get().await()
            
            val sessions = snapshot.documents.mapNotNull { it.toObject<RecordingSession>() }
            Result.success(sessions)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Save calibration data
     */
    suspend fun saveCalibrationData(
        sessionId: String,
        calibrationType: String,
        calibrationData: Map<String, Any>
    ): Result<Unit> {
        return try {
            firestore.collection("calibration_data").document()
                .set(
                    mapOf(
                        "sessionId" to sessionId,
                        "calibrationType" to calibrationType,
                        "calibrationData" to calibrationData,
                        "timestamp" to Date()
                    )
                ).await()
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Log system error for research debugging
     */
    suspend fun logSystemError(
        sessionId: String?,
        errorType: String,
        errorMessage: String,
        stackTrace: String
    ): Result<Unit> {
        return try {
            firestore.collection("system_errors").document()
                .set(
                    mapOf(
                        "sessionId" to sessionId,
                        "errorType" to errorType,
                        "errorMessage" to errorMessage,
                        "stackTrace" to stackTrace,
                        "timestamp" to Date()
                    )
                ).await()
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}