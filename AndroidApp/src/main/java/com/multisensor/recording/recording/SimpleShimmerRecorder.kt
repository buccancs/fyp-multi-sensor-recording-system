package com.multisensor.recording.recording

import android.content.Context
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothManager
import com.multisensor.recording.service.SessionManager
import com.multisensor.recording.util.Logger
import com.shimmerresearch.android.Shimmer
import com.shimmerresearch.android.manager.ShimmerBluetoothManagerAndroid
import com.shimmerresearch.driver.ObjectCluster
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.*
import java.io.File
import java.io.FileWriter
import java.util.concurrent.atomic.AtomicBoolean
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class SimpleShimmerRecorder @Inject constructor(
    @ApplicationContext private val context: Context,
    private val sessionManager: SessionManager,
    private val logger: Logger,
) {
    private val isRecording = AtomicBoolean(false)
    private val isConnected = AtomicBoolean(false)
    private var currentSessionId: String? = null
    private var dataWriter: FileWriter? = null
    private var bluetoothAdapter: BluetoothAdapter? = null
    private var shimmerBluetoothManager: ShimmerBluetoothManagerAndroid? = null
    private var connectedShimmer: Shimmer? = null

    companion object {
        private const val DEFAULT_SAMPLING_RATE = 51.2
        private const val CSV_HEADER = "Timestamp_ms,GSR_Conductance_uS,PPG_A13,Accel_X_g,Accel_Y_g,Accel_Z_g"
    }

    fun initialize(): Boolean {
        return try {
            bluetoothAdapter = (context.getSystemService(Context.BLUETOOTH_SERVICE) as BluetoothManager).adapter
            shimmerBluetoothManager = ShimmerBluetoothManagerAndroid(context)
            logger.info("SimpleShimmerRecorder initialized")
            true
        } catch (e: Exception) {
            logger.error("Failed to initialize SimpleShimmerRecorder", e)
            false
        }
    }

    suspend fun connectDevice(deviceAddress: String): Boolean {
        return try {
            shimmerBluetoothManager?.let { manager ->
                connectedShimmer = manager.getShimmerBluetoothRadio(deviceAddress)
                connectedShimmer?.connect()
                isConnected.set(true)
                logger.info("Connected to Shimmer device: $deviceAddress")
                true
            } ?: false
        } catch (e: Exception) {
            logger.error("Failed to connect to Shimmer device", e)
            false
        }
    }

    suspend fun startRecording(sessionId: String): Boolean {
        if (!isConnected.get()) return false
        
        return try {
            currentSessionId = sessionId
            val outputDir = sessionManager.getSessionDirectory(sessionId)
            val dataFile = File(outputDir, "shimmer_data.csv")
            
            dataWriter = FileWriter(dataFile)
            dataWriter?.write(CSV_HEADER + "\n")
            
            connectedShimmer?.startStreaming()
            isRecording.set(true)
            logger.info("Started Shimmer recording for session: $sessionId")
            true
        } catch (e: Exception) {
            logger.error("Failed to start Shimmer recording", e)
            false
        }
    }

    suspend fun stopRecording(): Boolean {
        return try {
            connectedShimmer?.stopStreaming()
            dataWriter?.close()
            dataWriter = null
            isRecording.set(false)
            logger.info("Stopped Shimmer recording")
            true
        } catch (e: Exception) {
            logger.error("Failed to stop Shimmer recording", e)
            false
        }
    }

    suspend fun disconnect(): Boolean {
        return try {
            stopRecording()
            connectedShimmer?.stop()
            connectedShimmer = null
            isConnected.set(false)
            logger.info("Disconnected from Shimmer device")
            true
        } catch (e: Exception) {
            logger.error("Failed to disconnect Shimmer device", e)
            false
        }
    }

    private fun handleShimmerData(objectCluster: ObjectCluster) {
        if (!isRecording.get()) return
        
        try {
            val timestamp = System.currentTimeMillis()
            val gsrValue = objectCluster.getFormatClusterValue("GSR Conductance", "mS/cm")?.data ?: 0.0
            val ppgValue = objectCluster.getFormatClusterValue("PPG", "no units")?.data ?: 0.0
            val accelX = objectCluster.getFormatClusterValue("Low Noise Accelerometer X", "m/(sec^2)")?.data ?: 0.0
            val accelY = objectCluster.getFormatClusterValue("Low Noise Accelerometer Y", "m/(sec^2)")?.data ?: 0.0
            val accelZ = objectCluster.getFormatClusterValue("Low Noise Accelerometer Z", "m/(sec^2)")?.data ?: 0.0
            
            val csvLine = "$timestamp,$gsrValue,$ppgValue,$accelX,$accelY,$accelZ\n"
            dataWriter?.write(csvLine)
            dataWriter?.flush()
        } catch (e: Exception) {
            logger.error("Error processing Shimmer data", e)
        }
    }

    fun isRecording(): Boolean = isRecording.get()
    fun isConnected(): Boolean = isConnected.get()
}