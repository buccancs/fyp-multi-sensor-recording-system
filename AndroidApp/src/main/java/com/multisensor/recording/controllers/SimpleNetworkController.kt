package com.multisensor.recording.controllers

import android.content.Context
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import com.multisensor.recording.util.Logger
import kotlinx.coroutines.*
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class SimpleNetworkController @Inject constructor() {

    interface NetworkCallback {
        fun onNetworkStatusChanged(connected: Boolean)
        fun onStreamingError(message: String)
        fun updateStatusText(text: String)
        fun getContext(): Context
    }

    private var callback: NetworkCallback? = null
    private var isStreamingActive = false

    fun setCallback(callback: NetworkCallback) {
        this.callback = callback
    }

    fun startStreaming(): Boolean {
        return try {
            isStreamingActive = true
            callback?.updateStatusText("Streaming started")
            true
        } catch (e: Exception) {
            callback?.onStreamingError("Failed to start streaming: ${e.message}")
            false
        }
    }

    fun stopStreaming(): Boolean {
        return try {
            isStreamingActive = false
            callback?.updateStatusText("Streaming stopped")
            true
        } catch (e: Exception) {
            callback?.onStreamingError("Failed to stop streaming: ${e.message}")
            false
        }
    }

    fun isNetworkAvailable(): Boolean {
        return try {
            val context = callback?.getContext() ?: return false
            val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
            val network = connectivityManager.activeNetwork ?: return false
            val capabilities = connectivityManager.getNetworkCapabilities(network) ?: return false
            capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
        } catch (e: Exception) {
            false
        }
    }

    fun isStreaming(): Boolean = isStreamingActive
}