package com.multisensor.recording.network

import com.multisensor.recording.recording.ShimmerDevice.ConnectionState
import com.multisensor.recording.util.Logger
import dagger.hilt.android.scopes.ServiceScoped
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import java.io.BufferedInputStream
import java.io.BufferedOutputStream
import java.io.IOException
import java.net.Socket
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicInteger
import java.util.concurrent.atomic.AtomicLong
import javax.inject.Inject

@ServiceScoped
class EnhancedJsonSocketClient @Inject constructor(
    private val logger: Logger,
    private val networkConfig: NetworkConfiguration
) {

    private var socket: Socket? = null
    private var inputStream: BufferedInputStream? = null
    private var outputStream: BufferedOutputStream? = null

    private var connectionScope: CoroutineScope? = null
    private var isConnected = AtomicBoolean(false)
    private var shouldReconnect = AtomicBoolean(true)
    private var isConnecting = AtomicBoolean(false)

    private val connectionMutex = Mutex()
    private val sendMutex = Mutex()

    private val outboundMessages = Channel<PriorityMessage>(capacity = 1000)
    private val pendingAcks = ConcurrentHashMap<String, PendingMessage>()

    private val connectionStats = ConnectionStats()
    private val messageCounter = AtomicLong(0)

    private var lastHeartbeatSent = AtomicLong(0)
    private var lastHeartbeatReceived = AtomicLong(0)
    private val heartbeatInterval = 5000L
    private val heartbeatTimeout = 15000L

    private var reconnectAttempts = AtomicInteger(0)
    private var maxReconnectAttempts = 10
    private var baseReconnectDelay = 1000L
    private var maxReconnectDelay = 30000L

    private val pendingPings = ConcurrentHashMap<String, Long>()
    private var pingCounter = AtomicLong(0)
    private val pingInterval = 10000L
    private var lastPingTime = AtomicLong(0)

    private var jitter: Double = 0.0
    private var packetLoss: Double = 0.0
    private var networkQuality: NetworkQuality = NetworkQuality.UNKNOWN

    private var streamingQuality: StreamingQuality = StreamingQuality.MEDIUM
    private var lastFrameTime = AtomicLong(0)
    private var adaptiveQualityEnabled = true

    private var serverIp: String = networkConfig.getServerIp()
    private var serverPort: Int = networkConfig.getJsonPort()

    private var commandCallback: ((JsonMessage) -> Unit)? = null
    private var connectionStateCallback: ((ConnectionState) -> Unit)? = null
    private var errorCallback: ((String, Exception?) -> Unit)? = null

    companion object {
        private const val CONNECTION_TIMEOUT_MS = 10000
        private const val LENGTH_HEADER_SIZE = 4
        private const val MAX_MESSAGE_SIZE = 10 * 1024 * 1024
        private const val BUFFER_SIZE = 64 * 1024

        private const val EXCELLENT_LATENCY_THRESHOLD_MS = 30.0
        private const val GOOD_LATENCY_THRESHOLD_MS = 100.0
        private const val FAIR_LATENCY_THRESHOLD_MS = 300.0

        private const val EXCELLENT_JITTER_THRESHOLD_MS = 5.0
        private const val GOOD_JITTER_THRESHOLD_MS = 20.0
        private const val FAIR_JITTER_THRESHOLD_MS = 50.0

        private const val EXCELLENT_LOSS_THRESHOLD_PCT = 0.1
        private const val GOOD_LOSS_THRESHOLD_PCT = 1.0
        private const val FAIR_LOSS_THRESHOLD_PCT = 5.0

        private const val LATENCY_SAMPLE_WINDOW_SIZE = 100
        private const val JITTER_CALCULATION_WINDOW = 10

        private const val MILLISECONDS_TO_MICROSECONDS = 1000.0
        private const val BYTES_TO_KILOBYTES = 1024.0
        private const val PERCENT_TO_RATIO = 100.0
    }

    enum class MessagePriority(val value: Int) {
        CRITICAL(1),
        HIGH(2),
        NORMAL(3),
        LOW(4)
    }

    enum class StreamingQuality(val frameRate: Int, val compressionLevel: Int) {
        LOW(5, 80),
        MEDIUM(15, 60),
        HIGH(30, 40)
    }

    enum class NetworkQuality {
        EXCELLENT,
        GOOD,
        FAIR,
        POOR,
        UNKNOWN
    }

    private data class PingMessage(
        val pingId: String,
        val timestamp: Long,
        val sequence: Long
    )

    private data class PongMessage(
        val pingId: String,
        val originalTimestamp: Long,
        val responseTimestamp: Long,
        val sequence: Long
    )

    private data class PriorityMessage(
        val message: JsonMessage,
        val priority: MessagePriority,
        val timestamp: Long = System.currentTimeMillis(),
        val messageId: String? = null,
        val requiresAck: Boolean = false,
        val timeout: Long = 30000L
    ) : Comparable<PriorityMessage> {
        override fun compareTo(other: PriorityMessage): Int {
            return this.priority.value.compareTo(other.priority.value)
        }
    }

    private data class PendingMessage(
        val message: PriorityMessage,
        val sendTime: Long,
        val retryCount: Int = 0
    )

    private data class ConnectionStats(
        var connectedAt: Long = 0,
        var messagesSent: AtomicLong = AtomicLong(0),
        var messagesReceived: AtomicLong = AtomicLong(0),
        var bytesSent: AtomicLong = AtomicLong(0),
        var bytesReceived: AtomicLong = AtomicLong(0),
        var errorCount: AtomicLong = AtomicLong(0),
        var reconnectionCount: AtomicLong = AtomicLong(0),
        val latencySamples: ArrayDeque<Long> = ArrayDeque(),
        var averageLatency: Double = 0.0
    )

    fun configure(ip: String, port: Int = networkConfig.getJsonPort()) {
        serverIp = ip
        serverPort = port
        networkConfig.setServerIp(ip)
        networkConfig.setJsonPort(port)
        logger.info("Enhanced client configured for $ip:$port")
    }

    fun setCommandCallback(callback: (JsonMessage) -> Unit) {
        commandCallback = callback
    }

    fun setConnectionStateCallback(callback: (ConnectionState) -> Unit) {
        connectionStateCallback = callback
    }

    fun setErrorCallback(callback: (String, Exception?) -> Unit) {
        errorCallback = callback
    }

    suspend fun connect(): Boolean = connectionMutex.withLock {
        if (isConnected.get()) {
            logger.warning("Already connected")
            return true
        }

        if (isConnecting.get()) {
            logger.warning("Connection already in progress")
            return false
        }

        shouldReconnect.set(true)
        isConnecting.set(true)

        try {
            connectionScope = CoroutineScope(Dispatchers.IO + SupervisorJob())

            val success = establishConnection()
            if (success) {
                startConnectionManagement()
                connectionStateCallback?.invoke(ConnectionState.CONNECTED)
                reconnectAttempts.set(0)
                logger.info("Enhanced client connected successfully")
            } else {
                connectionStateCallback?.invoke(ConnectionState.ERROR)
            }

            return success
        } finally {
            isConnecting.set(false)
        }
    }

    suspend fun disconnect() = connectionMutex.withLock {
        logger.info("Disconnecting enhanced client...")
        shouldReconnect.set(false)

        try {
            if (isConnected.get()) {
                sendMessage(
                    createDisconnectMessage(),
                    MessagePriority.CRITICAL,
                    requiresAck = false
                )
            }

            closeConnection()

            connectionScope?.cancel()
            connectionScope = null

            connectionStateCallback?.invoke(ConnectionState.DISCONNECTED)
            logger.info("Enhanced client disconnected successfully")

        } catch (e: Exception) {
            logger.error("Error during disconnect", e)
            errorCallback?.invoke("Disconnect error", e)
        }
    }

    suspend fun sendMessage(
        message: JsonMessage,
        priority: MessagePriority = MessagePriority.NORMAL,
        requiresAck: Boolean = false,
        timeout: Long = 30000L
    ): Boolean {
        if (!isConnected.get()) {
            logger.warning("Cannot send message - not connected")
            return false
        }

        val messageId = if (requiresAck) generateMessageId() else null
        val priorityMessage = PriorityMessage(
            message = message,
            priority = priority,
            messageId = messageId,
            requiresAck = requiresAck,
            timeout = timeout
        )

        return try {
            outboundMessages.trySend(priorityMessage).isSuccess
        } catch (e: Exception) {
            logger.error("Failed to queue message", e)
            false
        }
    }

    suspend fun sendHandshake(deviceId: String, capabilities: List<String>): Boolean {
        val handshakeMessage = HelloMessage(
            device_id = deviceId,
            capabilities = capabilities + listOf("enhanced_client", "adaptive_streaming", "heartbeat")
        )

        return sendMessage(handshakeMessage, MessagePriority.CRITICAL, requiresAck = true)
    }

    suspend fun sendAck(
        commandType: String,
        success: Boolean,
        errorMessage: String? = null,
        messageId: String? = null
    ): Boolean {
        val ackMessage = AckMessage(
            cmd = commandType,
            status = if (success) "ok" else "error",
            message = errorMessage
        )

        return sendMessage(ackMessage, MessagePriority.CRITICAL)
    }

    suspend fun sendStatusUpdate(
        battery: Int?,
        storage: String?,
        temperature: Double?,
        recording: Boolean
    ): Boolean {
        val statusMessage = StatusMessage(
            battery = battery,
            storage = storage,
            temperature = temperature,
            recording = recording,
            connected = true
        )

        return sendMessage(statusMessage, MessagePriority.HIGH)
    }

    suspend fun sendPreviewFrame(
        frameType: String,
        imageData: String,
        timestamp: Long = System.currentTimeMillis()
    ): Boolean {
        val currentTime = System.currentTimeMillis()
        val frameInterval = 1000L / streamingQuality.frameRate

        if (currentTime - lastFrameTime.get() < frameInterval) {
            return false
        }

        lastFrameTime.set(currentTime)

        val previewMessage = PreviewFrameMessage(
            cam = frameType,
            timestamp = timestamp,
            image = imageData
        )

        return sendMessage(previewMessage, MessagePriority.LOW)
    }

    private suspend fun establishConnection(): Boolean = withContext(Dispatchers.IO) {
        try {
            logger.info("Attempting to connect to $serverIp:$serverPort...")

            socket = Socket().apply {
                soTimeout = CONNECTION_TIMEOUT_MS
                tcpNoDelay = true
                keepAlive = true
                receiveBufferSize = BUFFER_SIZE
                sendBufferSize = BUFFER_SIZE
                connect(java.net.InetSocketAddress(serverIp, serverPort), CONNECTION_TIMEOUT_MS)
            }

            inputStream = BufferedInputStream(socket?.getInputStream(), BUFFER_SIZE)
            outputStream = BufferedOutputStream(socket?.getOutputStream(), BUFFER_SIZE)

            isConnected.set(true)
            connectionStats.connectedAt = System.currentTimeMillis()

            logger.info("Socket connection established to $serverIp:$serverPort")
            true

        } catch (e: Exception) {
            logger.error("Connection failed", e)
            errorCallback?.invoke("Connection failed: ${e.message}", e)
            closeConnection()
            false
        }
    }

    private fun startConnectionManagement() {
        connectionScope?.launch {
            launch { messageSenderLoop() }

            launch { messageReceiverLoop() }

            launch { heartbeatSenderLoop() }

            launch { pingSenderLoop() }

            launch { connectionMonitorLoop() }

            launch { pendingMessageTimeoutLoop() }
        }
    }

    private suspend fun messageSenderLoop() {
        while (isConnected.get() && shouldReconnect.get()) {
            try {
                val priorityMessage = outboundMessages.receive()

                if (sendMessageImmediate(priorityMessage)) {
                    connectionStats.messagesSent.incrementAndGet()

                    if (priorityMessage.requiresAck && priorityMessage.messageId != null) {
                        pendingAcks[priorityMessage.messageId] = PendingMessage(
                            message = priorityMessage,
                            sendTime = System.currentTimeMillis()
                        )
                    }
                } else {
                    if (priorityMessage.priority == MessagePriority.CRITICAL) {
                        delay(1000)
                        outboundMessages.trySend(priorityMessage)
                    }
                }

            } catch (e: Exception) {
                if (shouldReconnect.get()) {
                    logger.error("Message sender error", e)
                    connectionStats.errorCount.incrementAndGet()
                    handleConnectionError(e)
                }
                break
            }
        }
    }

    private suspend fun messageReceiverLoop() {
        while (isConnected.get() && shouldReconnect.get()) {
            try {
                val message = receiveMessage()
                if (message != null) {
                    connectionStats.messagesReceived.incrementAndGet()
                    lastHeartbeatReceived.set(System.currentTimeMillis())

                    processReceivedMessage(message)
                } else {
                    delay(100)
                }

            } catch (e: Exception) {
                if (shouldReconnect.get()) {
                    logger.error("Message receiver error", e)
                    connectionStats.errorCount.incrementAndGet()
                    handleConnectionError(e)
                }
                break
            }
        }
    }

    private suspend fun heartbeatSenderLoop() {
        while (isConnected.get() && shouldReconnect.get()) {
            try {
                delay(heartbeatInterval)

                if (System.currentTimeMillis() - lastHeartbeatSent.get() >= heartbeatInterval) {
                    val heartbeat = createHeartbeatMessage()
                    sendMessage(heartbeat, MessagePriority.HIGH)
                    lastHeartbeatSent.set(System.currentTimeMillis())
                }

            } catch (e: Exception) {
                logger.error("Heartbeat sender error", e)
                break
            }
        }
    }

    private suspend fun pingSenderLoop() {
        while (isConnected.get() && shouldReconnect.get()) {
            try {
                delay(pingInterval)

                val currentTime = System.currentTimeMillis()
                if (currentTime - lastPingTime.get() >= pingInterval) {
                    sendPing()
                    lastPingTime.set(currentTime)
                }

            } catch (e: Exception) {
                logger.error("Ping sender error", e)
                break
            }
        }
    }

    private suspend fun sendPing() {
        val pingId = "ping_${pingCounter.incrementAndGet()}"
        val timestamp = System.currentTimeMillis()

        pendingPings[pingId] = timestamp

        val pingMessage = StatusMessage(
            battery = null,
            storage = null,
            temperature = null,
            recording = false,
            connected = true
        )

        val enhancedMessage = createPingAsJsonMessage(pingId, timestamp)
        sendMessage(enhancedMessage, MessagePriority.HIGH)

        val cutoffTime = timestamp - 60000
        pendingPings.entries.removeAll { it.value < cutoffTime }
    }

    private fun createPingAsJsonMessage(pingId: String, timestamp: Long): JsonMessage {
        return StatusMessage(
            battery = null,
            storage = "ping:$pingId:$timestamp:${pingCounter.get()}",
            temperature = null,
            recording = false,
            connected = true
        )
    }

    private suspend fun connectionMonitorLoop() {
        while (isConnected.get() && shouldReconnect.get()) {
            try {
                delay(5000)

                val currentTime = System.currentTimeMillis()

                if (currentTime - lastHeartbeatReceived.get() > heartbeatTimeout) {
                    logger.warning("Heartbeat timeout detected")
                    handleConnectionError(Exception("Heartbeat timeout"))
                    break
                }

                if (adaptiveQualityEnabled) {
                    adaptStreamingQuality()
                }

                updateConnectionStatistics()

            } catch (e: Exception) {
                logger.error("Connection monitor error", e)
                break
            }
        }
    }

    private suspend fun pendingMessageTimeoutLoop() {
        while (isConnected.get() && shouldReconnect.get()) {
            try {
                delay(5000)

                val currentTime = System.currentTimeMillis()
                val iterator = pendingAcks.entries.iterator()

                while (iterator.hasNext()) {
                    val entry = iterator.next()
                    val pendingMessage = entry.value

                    if (currentTime - pendingMessage.sendTime > pendingMessage.message.timeout) {
                        logger.warning("Message ACK timeout: ${entry.key}")
                        iterator.remove()

                        if (pendingMessage.message.priority == MessagePriority.CRITICAL &&
                            pendingMessage.retryCount < 3
                        ) {
                            val retryMessage = pendingMessage.message.copy(
                                timestamp = currentTime
                            )
                            outboundMessages.trySend(retryMessage)

                            pendingAcks[entry.key] = pendingMessage.copy(
                                sendTime = currentTime,
                                retryCount = pendingMessage.retryCount + 1
                            )
                        }
                    }
                }

            } catch (e: Exception) {
                logger.error("Pending message timeout handler error", e)
                break
            }
        }
    }

    private suspend fun sendMessageImmediate(priorityMessage: PriorityMessage): Boolean =
        sendMutex.withLock {
            try {
                val jsonString = JsonMessage.toJson(priorityMessage.message)
                val jsonBytes = jsonString.toByteArray(Charsets.UTF_8)

                val lengthHeader = ByteBuffer.allocate(LENGTH_HEADER_SIZE)
                    .order(ByteOrder.BIG_ENDIAN)
                    .putInt(jsonBytes.size)
                    .array()

                outputStream?.write(lengthHeader)
                outputStream?.write(jsonBytes)
                outputStream?.flush()

                connectionStats.bytesSent.addAndGet((lengthHeader.size + jsonBytes.size).toLong())

                logger.debug("Sent message: ${priorityMessage.message.type} (${jsonBytes.size} bytes)")
                true

            } catch (e: IOException) {
                logger.error("Send error", e)
                false
            }
        }

    private suspend fun receiveMessage(): JsonMessage? = withContext(Dispatchers.IO) {
        try {
            val lengthHeader = ByteArray(LENGTH_HEADER_SIZE)
            var bytesRead = 0

            while (bytesRead < LENGTH_HEADER_SIZE) {
                val read = inputStream?.read(lengthHeader, bytesRead, LENGTH_HEADER_SIZE - bytesRead) ?: -1
                if (read == -1) return@withContext null
                bytesRead += read
            }

            val messageLength = ByteBuffer.wrap(lengthHeader)
                .order(ByteOrder.BIG_ENDIAN)
                .int

            if (messageLength <= 0 || messageLength > MAX_MESSAGE_SIZE) {
                throw IOException("Invalid message length: $messageLength")
            }

            val messageBytes = ByteArray(messageLength)
            bytesRead = 0

            while (bytesRead < messageLength) {
                val read = inputStream?.read(messageBytes, bytesRead, messageLength - bytesRead) ?: -1
                if (read == -1) return@withContext null
                bytesRead += read
            }

            connectionStats.bytesReceived.addAndGet((LENGTH_HEADER_SIZE + messageLength).toLong())

            val jsonString = String(messageBytes, Charsets.UTF_8)
            JsonMessage.fromJson(jsonString)

        } catch (e: Exception) {
            logger.error("Receive error", e)
            null
        }
    }

    private suspend fun processReceivedMessage(message: JsonMessage) {
        when (message.type) {
            "heartbeat" -> handleHeartbeat(message)
            "heartbeat_response" -> handleHeartbeatResponse(message)
            "ack" -> handleAcknowledgment(message)
            "handshake_ack" -> handleHandshakeAck(message)
            "status" -> handleStatusMessage(message)
            "pong" -> handlePongMessage(message)
            else -> {
                commandCallback?.invoke(message)
            }
        }
    }

    private suspend fun handleHeartbeat(message: JsonMessage) {
        val response = createHeartbeatResponseMessage()
        sendMessage(response, MessagePriority.HIGH)
    }

    private suspend fun handleHeartbeatResponse(message: JsonMessage) {
        try {
            val currentTime = System.currentTimeMillis()

            val messageTimestamp = when (message) {
                is StatusMessage -> {
                    extractTimestampFromMessage(message)
                }

                is AckMessage -> {
                    extractTimestampFromMessage(message)
                }

                else -> {
                    extractTimestampFromMessage(message)
                }
            }

            if (messageTimestamp != null) {
                val latency = currentTime - messageTimestamp
                updateLatencyStatistics(latency)
                logger.debug("Heartbeat latency: ${latency}ms")
            }

        } catch (e: Exception) {
            logger.error("Error calculating heartbeat latency", e)
        }
    }

    private fun extractTimestampFromMessage(message: JsonMessage): Long? {
        return try {
            when (message) {
                is PreviewFrameMessage -> message.timestamp
                is SensorDataMessage -> message.timestamp
                is SetStimulusTimeCommand -> message.time
                is SyncTimeCommand -> message.pc_timestamp
                else -> {
                    logger.debug("Message type ${message.type} does not contain timestamp field")
                    null
                }
            }
        } catch (e: Exception) {
            logger.debug("Could not extract timestamp from message", e)
            null
        }
    }

    private fun updateLatencyStatistics(latency: Long) {
        connectionStats.latencySamples.addLast(latency)

        while (connectionStats.latencySamples.size > 100) {
            connectionStats.latencySamples.removeFirst()
        }

        if (connectionStats.latencySamples.isNotEmpty()) {
            connectionStats.averageLatency = connectionStats.latencySamples.average()
        }
    }

    private suspend fun handleAcknowledgment(message: JsonMessage) {
        if (message is AckMessage) {
        }
    }

    private suspend fun handleHandshakeAck(message: JsonMessage) {
        logger.info("Received handshake acknowledgment")
    }

    private suspend fun handleStatusMessage(message: JsonMessage) {
        if (message is StatusMessage) {
            message.storage?.let { storage ->
                if (storage.startsWith("pong:")) {
                    handlePongResponse(storage)
                }
            }
        }

        commandCallback?.invoke(message)
    }

    private fun handlePongResponse(pongData: String) {
        try {
            val parts = pongData.split(":")
            if (parts.size >= 5) {
                val pingId = parts[1]
                val originalTimestamp = parts[2].toLong()
                val responseTimestamp = parts[3].toLong()
                val sequence = parts[4].toLong()

                val currentTime = System.currentTimeMillis()
                val rtt = currentTime - originalTimestamp

                pendingPings.remove(pingId)

                updateLatencyStatistics(rtt)

                updateNetworkQualityMetrics(rtt)

                logger.debug("Ping $pingId RTT: ${rtt}ms")
            }
        } catch (e: Exception) {
            logger.error("Error processing pong response", e)
        }
    }

    private suspend fun handlePongMessage(message: JsonMessage) {
        logger.debug("Received pong message")
    }

    private fun updateNetworkQualityMetrics(latency: Long) {
        if (connectionStats.latencySamples.size >= 2) {
            val previousLatencies = connectionStats.latencySamples.takeLast(10)
            val latencyVariance =
                previousLatencies.map { (it - connectionStats.averageLatency).let { diff -> diff * diff } }.average()
            jitter = kotlin.math.sqrt(latencyVariance)
        }

        val totalPings = pingCounter.get()
        val lostPings = pendingPings.size
        if (totalPings > 0) {
            packetLoss = (lostPings.toDouble() / totalPings.toDouble()) * 100.0
        }

        networkQuality = assessNetworkQuality(connectionStats.averageLatency, jitter, packetLoss)

        if (adaptiveQualityEnabled) {
            adaptStreamingQualityAdvanced()
        }
    }

    private fun assessNetworkQuality(avgLatency: Double, jitter: Double, packetLoss: Double): NetworkQuality {
        return when {
            avgLatency < EXCELLENT_LATENCY_THRESHOLD_MS &&
                    jitter < EXCELLENT_JITTER_THRESHOLD_MS &&
                    packetLoss < EXCELLENT_LOSS_THRESHOLD_PCT -> NetworkQuality.EXCELLENT

            avgLatency < GOOD_LATENCY_THRESHOLD_MS &&
                    jitter < GOOD_JITTER_THRESHOLD_MS &&
                    packetLoss < GOOD_LOSS_THRESHOLD_PCT -> NetworkQuality.GOOD

            avgLatency < FAIR_LATENCY_THRESHOLD_MS &&
                    jitter < FAIR_JITTER_THRESHOLD_MS &&
                    packetLoss < FAIR_LOSS_THRESHOLD_PCT -> NetworkQuality.FAIR

            else -> NetworkQuality.POOR
        }
    }

    private fun adaptStreamingQualityAdvanced() {
        val newQuality = when (networkQuality) {
            NetworkQuality.EXCELLENT -> StreamingQuality.HIGH
            NetworkQuality.GOOD -> StreamingQuality.MEDIUM
            NetworkQuality.FAIR, NetworkQuality.POOR -> StreamingQuality.LOW
            NetworkQuality.UNKNOWN -> StreamingQuality.MEDIUM
        }

        if (newQuality != streamingQuality) {
            streamingQuality = newQuality
            logger.info("Adapted streaming quality to: ${newQuality.name} (Network: ${networkQuality.name})")
        }
    }

    private suspend fun handleConnectionError(error: Exception) {
        logger.error("Connection error occurred", error)
        errorCallback?.invoke("Connection error: ${error.message}", error)

        closeConnection()

        if (shouldReconnect.get()) {
            connectionStateCallback?.invoke(ConnectionState.RECONNECTING)
            attemptReconnection()
        }
    }

    private suspend fun attemptReconnection() {
        val attempt = reconnectAttempts.incrementAndGet()

        if (attempt > maxReconnectAttempts) {
            logger.error("Max reconnection attempts reached")
            shouldReconnect.set(false)
            connectionStateCallback?.invoke(ConnectionState.ERROR)
            return
        }

        val delay = minOf(
            baseReconnectDelay * (1L shl minOf(attempt - 1, 10)),
            maxReconnectDelay
        )

        logger.info("Reconnection attempt $attempt in ${delay}ms")

        delay(delay)

        if (shouldReconnect.get()) {
            connect()
        }
    }

    private fun closeConnection() {
        try {
            outputStream?.close()
            inputStream?.close()
            socket?.close()
        } catch (e: Exception) {
            logger.debug("Error closing connection resources", e)
        }

        isConnected.set(false)
        socket = null
        inputStream = null
        outputStream = null
    }

    private fun adaptStreamingQuality() {
        val errorRate = connectionStats.errorCount.get().toDouble() /
                maxOf(1, connectionStats.messagesReceived.get()).toDouble()

        val newQuality = when {
            errorRate > 0.1 || connectionStats.averageLatency > 200 -> StreamingQuality.LOW
            errorRate < 0.05 && connectionStats.averageLatency < 50 -> StreamingQuality.HIGH
            else -> StreamingQuality.MEDIUM
        }

        if (newQuality != streamingQuality) {
            streamingQuality = newQuality
            logger.info("Adapted streaming quality to: ${newQuality.name}")
        }
    }

    private fun updateConnectionStatistics() {
        if (connectionStats.latencySamples.isNotEmpty()) {
            connectionStats.averageLatency = connectionStats.latencySamples.average()

            while (connectionStats.latencySamples.size > 100) {
                connectionStats.latencySamples.removeFirst()
            }
        }
    }

    private fun generateMessageId(): String {
        return "${System.currentTimeMillis()}_${messageCounter.incrementAndGet()}"
    }

    private fun createHeartbeatMessage(): JsonMessage {
        return StatusMessage(
            battery = null,
            storage = null,
            temperature = null,
            recording = false,
            connected = true
        )
    }

    private fun createHeartbeatResponseMessage(): JsonMessage {
        return AckMessage(
            cmd = "heartbeat",
            status = "ok",
            message = "heartbeat_response"
        )
    }

    private fun createDisconnectMessage(): JsonMessage {
        return StatusMessage(
            battery = null,
            storage = null,
            temperature = null,
            recording = false,
            connected = false
        )
    }

    fun isConnected(): Boolean = isConnected.get()

    fun getConnectionInfo(): String = if (isConnected.get()) {
        "Connected to $serverIp:$serverPort"
    } else {
        "Disconnected"
    }

    fun getConnectionStatistics(): Map<String, Any> = mapOf(
        "connected" to isConnected.get(),
        "server" to "$serverIp:$serverPort",
        "messages_sent" to connectionStats.messagesSent.get(),
        "messages_received" to connectionStats.messagesReceived.get(),
        "bytes_sent" to connectionStats.bytesSent.get(),
        "bytes_received" to connectionStats.bytesReceived.get(),
        "error_count" to connectionStats.errorCount.get(),
        "reconnection_count" to connectionStats.reconnectionCount.get(),
        "average_latency" to connectionStats.averageLatency,
        "latency_jitter" to jitter,
        "packet_loss_percent" to packetLoss,
        "network_quality" to networkQuality.name,
        "streaming_quality" to streamingQuality.name,
        "connection_duration" to if (connectionStats.connectedAt > 0) {
            System.currentTimeMillis() - connectionStats.connectedAt
        } else 0,
        "ping_statistics" to mapOf(
            "total_pings_sent" to pingCounter.get(),
            "pending_pings" to pendingPings.size,
            "successful_pings" to (pingCounter.get() - pendingPings.size)
        )
    )

    fun setAdaptiveQualityEnabled(enabled: Boolean) {
        adaptiveQualityEnabled = enabled
        logger.info("Adaptive streaming quality ${if (enabled) "enabled" else "disabled"}")
    }

    fun setStreamingQuality(quality: StreamingQuality) {
        streamingQuality = quality
        logger.info("Streaming quality set to: ${quality.name}")
    }

    fun getCurrentLatency(): Double = connectionStats.averageLatency

    fun getNetworkJitter(): Double = jitter

    fun getPacketLoss(): Double = packetLoss

    fun getNetworkQuality(): NetworkQuality = networkQuality

    fun getLatencyStatistics(): Map<String, Any> {
        val samples = connectionStats.latencySamples
        return if (samples.isNotEmpty()) {
            mapOf(
                "average_latency_ms" to connectionStats.averageLatency,
                "min_latency_ms" to (samples.minOrNull() ?: 0.0),
                "max_latency_ms" to (samples.maxOrNull() ?: 0.0),
                "jitter_ms" to jitter,
                "sample_count" to samples.size,
                "recent_latencies" to samples.takeLast(10)
            )
        } else {
            mapOf(
                "average_latency_ms" to 0.0,
                "sample_count" to 0,
                "message" to "No latency samples available"
            )
        }
    }

    fun resetLatencyStatistics() {
        connectionStats.latencySamples.clear()
        connectionStats.averageLatency = 0.0
        jitter = 0.0
        packetLoss = 0.0
        networkQuality = NetworkQuality.UNKNOWN
        pendingPings.clear()
        pingCounter.set(0)
        logger.info("Latency statistics reset")
    }
}
