package com.multisensor.recording.managers

import android.content.Context
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothManager
import com.shimmerresearch.android.manager.ShimmerBluetoothManagerAndroid
import com.multisensor.recording.util.Logger
import dagger.hilt.android.qualifiers.ApplicationContext
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class SimpleShimmerManager @Inject constructor(
    @ApplicationContext private val context: Context,
    private val logger: Logger
) {

    private var shimmerBluetoothManager: ShimmerBluetoothManagerAndroid? = null
    private var bluetoothAdapter: BluetoothAdapter? = null

    fun initialize(): Boolean {
        return try {
            val bluetoothManager = context.getSystemService(Context.BLUETOOTH_SERVICE) as BluetoothManager
            bluetoothAdapter = bluetoothManager.adapter
            shimmerBluetoothManager = ShimmerBluetoothManagerAndroid(context)
            logger.info("SimpleShimmerManager initialized")
            true
        } catch (e: Exception) {
            logger.error("Failed to initialize SimpleShimmerManager", e)
            false
        }
    }

    fun isBluetoothEnabled(): Boolean {
        return bluetoothAdapter?.isEnabled ?: false
    }

    fun getShimmerBluetoothManager(): ShimmerBluetoothManagerAndroid? {
        return shimmerBluetoothManager
    }

    fun scanForDevices(): List<String> {
        return try {
            bluetoothAdapter?.bondedDevices?.filter { device ->
                device.name?.contains("Shimmer", ignoreCase = true) == true
            }?.map { it.address } ?: emptyList()
        } catch (e: Exception) {
            logger.error("Error scanning for Shimmer devices", e)
            emptyList()
        }
    }
}