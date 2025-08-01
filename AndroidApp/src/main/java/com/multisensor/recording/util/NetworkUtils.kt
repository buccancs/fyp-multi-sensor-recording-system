@file:Suppress("DEPRECATION")
package com.multisensor.recording.util

import android.content.Context
import android.net.ConnectivityManager
import android.net.Network
import android.net.NetworkCapabilities
import android.net.NetworkInfo
import android.os.Build
import android.telephony.TelephonyManager
import android.util.Log

/**
 * Utility class for network connectivity operations using modern Android APIs
 * while maintaining backward compatibility.
 */
object NetworkUtils {

    private const val TAG = "NetworkUtils"

    /**
     * Check if network is connected using modern APIs where available.
     * Falls back to deprecated APIs for older Android versions.
     */
    fun isNetworkConnected(context: Context): Boolean {
        return try {
            val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
            
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                val activeNetwork = connectivityManager.activeNetwork
                val networkCapabilities = connectivityManager.getNetworkCapabilities(activeNetwork)
                networkCapabilities?.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET) == true &&
                networkCapabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_VALIDATED)
            } else {
                @Suppress("DEPRECATION")
                val networkInfo = connectivityManager.activeNetworkInfo
                @Suppress("DEPRECATION")
                networkInfo?.isConnected == true
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error checking network connectivity: ${e.message}")
            false
        }
    }

    /**
     * Get network type information using modern APIs where available.
     * Falls back to deprecated APIs for older Android versions.
     */
    fun getNetworkType(context: Context): String {
        return try {
            val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
            
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                val activeNetwork = connectivityManager.activeNetwork
                if (activeNetwork == null) return "Disconnected"
                
                val networkCapabilities = connectivityManager.getNetworkCapabilities(activeNetwork)
                if (networkCapabilities == null) return "Not Connected"
                
                when {
                    !networkCapabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET) -> "Not Connected"
                    networkCapabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) -> "WiFi"
                    networkCapabilities.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) -> {
                        getCellularNetworkType(context)
                    }
                    networkCapabilities.hasTransport(NetworkCapabilities.TRANSPORT_ETHERNET) -> "Ethernet"
                    else -> "Other"
                }
            } else {
                @Suppress("DEPRECATION")
                val networkInfo = connectivityManager.activeNetworkInfo
                
                when {
                    networkInfo == null -> "Disconnected"
                    @Suppress("DEPRECATION")
                    !networkInfo.isConnected -> "Not Connected"
                    @Suppress("DEPRECATION")
                    networkInfo.type == ConnectivityManager.TYPE_WIFI -> "WiFi"
                    @Suppress("DEPRECATION")
                    networkInfo.type == ConnectivityManager.TYPE_MOBILE -> {
                        @Suppress("DEPRECATION")
                        val subtype = networkInfo.subtype
                        when (subtype) {
                            TelephonyManager.NETWORK_TYPE_LTE -> "4G LTE"
                            TelephonyManager.NETWORK_TYPE_HSDPA,
                            TelephonyManager.NETWORK_TYPE_HSUPA,
                            TelephonyManager.NETWORK_TYPE_HSPA -> "3G"
                            TelephonyManager.NETWORK_TYPE_EDGE,
                            TelephonyManager.NETWORK_TYPE_GPRS -> "2G"
                            else -> "Mobile"
                        }
                    }
                    @Suppress("DEPRECATION")
                    networkInfo.type == ConnectivityManager.TYPE_ETHERNET -> "Ethernet"
                    else -> "Other"
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error detecting network type: ${e.message}")
            "Unknown"
        }
    }

    /**
     * Get cellular network type for modern API versions
     */
    private fun getCellularNetworkType(context: Context): String {
        return try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
                val telephonyManager = context.getSystemService(Context.TELEPHONY_SERVICE) as TelephonyManager
                when (telephonyManager.dataNetworkType) {
                    TelephonyManager.NETWORK_TYPE_LTE -> "4G LTE"
                    TelephonyManager.NETWORK_TYPE_HSDPA,
                    TelephonyManager.NETWORK_TYPE_HSUPA,
                    TelephonyManager.NETWORK_TYPE_HSPA -> "3G"
                    TelephonyManager.NETWORK_TYPE_EDGE,
                    TelephonyManager.NETWORK_TYPE_GPRS -> "2G"
                    else -> "Mobile"
                }
            } else {
                "Mobile"
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error getting cellular network type: ${e.message}")
            "Mobile"
        }
    }
}