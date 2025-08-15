package com.multisensor.recording.stimulus

import android.content.Context
import android.net.Uri
import android.os.Bundle
import android.view.SurfaceView
import android.view.View
import android.widget.*
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import com.google.android.exoplayer2.*
import com.google.android.exoplayer2.source.MediaSource
import com.google.android.exoplayer2.source.ProgressiveMediaSource
import com.google.android.exoplayer2.upstream.DefaultDataSourceFactory
import kotlinx.coroutines.launch
import java.io.File
import com.multisensor.recording.R
import com.multisensor.recording.MainActivity
import com.multisensor.recording.util.Logger

/**
 * Video Stimulus Control Fragment
 * Provides emotion elicitation video playback capabilities for Android app
 */
class VideoStimulusFragment : Fragment() {
    
    companion object {
        private const val TAG = "VideoStimulusFragment"
        private const val REQUEST_VIDEO_PICK = 1001
    }
    
    // UI components
    private lateinit var videoPlayerView: com.google.android.exoplayer2.ui.PlayerView
    private lateinit var videoControls: LinearLayout
    private lateinit var playButton: Button
    private lateinit var pauseButton: Button
    private lateinit var stopButton: Button
    private lateinit var seekBar: SeekBar
    private lateinit var timeDisplay: TextView
    private lateinit var selectVideoButton: Button
    private lateinit var videoStatus: TextView
    
    // ExoPlayer components
    private var exoPlayer: SimpleExoPlayer? = null
    private var currentVideoUri: Uri? = null
    private var isVideoLoaded = false
    
    // Video stimulus metadata
    private var videoMetadata = mutableMapOf<String, Any>()
    
    override fun onCreateView(
        inflater: android.view.LayoutInflater,
        container: android.view.ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        // Create layout programmatically since we don't have the XML
        val rootLayout = LinearLayout(requireContext()).apply {
            orientation = LinearLayout.VERTICAL
            layoutParams = ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )
        }
        
        // Video player view
        videoPlayerView = com.google.android.exoplayer2.ui.PlayerView(requireContext()).apply {
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                0,
                1f
            )
        }
        rootLayout.addView(videoPlayerView)
        
        // Controls layout
        videoControls = LinearLayout(requireContext()).apply {
            orientation = LinearLayout.VERTICAL
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            )
        }
        
        // Button controls
        val buttonLayout = LinearLayout(requireContext()).apply {
            orientation = LinearLayout.HORIZONTAL
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            )
        }
        
        selectVideoButton = Button(requireContext()).apply {
            text = "Select Video"
            layoutParams = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
        }
        buttonLayout.addView(selectVideoButton)
        
        playButton = Button(requireContext()).apply {
            text = "Play"
            layoutParams = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
        }
        buttonLayout.addView(playButton)
        
        pauseButton = Button(requireContext()).apply {
            text = "Pause"
            layoutParams = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
        }
        buttonLayout.addView(pauseButton)
        
        stopButton = Button(requireContext()).apply {
            text = "Stop"
            layoutParams = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
        }
        buttonLayout.addView(stopButton)
        
        videoControls.addView(buttonLayout)
        
        // Seek bar
        seekBar = SeekBar(requireContext()).apply {
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            )
        }
        videoControls.addView(seekBar)
        
        // Time display
        timeDisplay = TextView(requireContext()).apply {
            text = "00:00 / 00:00"
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            )
            textAlignment = View.TEXT_ALIGNMENT_CENTER
        }
        videoControls.addView(timeDisplay)
        
        // Status display
        videoStatus = TextView(requireContext()).apply {
            text = "Video stimulus system ready"
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            )
            textAlignment = View.TEXT_ALIGNMENT_CENTER
        }
        videoControls.addView(videoStatus)
        
        rootLayout.addView(videoControls)
        
        return rootLayout
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        initializeViews()
        initializePlayer()
    }
    
    private fun initializeViews() {
        // Set up click listeners
        playButton.setOnClickListener { playVideo() }
        pauseButton.setOnClickListener { pauseVideo() }
        stopButton.setOnClickListener { stopVideo() }
        selectVideoButton.setOnClickListener { selectVideoFile() }
        
        // Set up seek bar
        seekBar.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                if (fromUser && exoPlayer != null) {
                    val position = (progress.toLong() * (exoPlayer?.duration ?: 0L)) / 100L
                    exoPlayer?.seekTo(position)
                }
            }
            override fun onStartTrackingTouch(seekBar: SeekBar?) {}
            override fun onStopTrackingTouch(seekBar: SeekBar?) {}
        })
        
        updateVideoStatus("Video stimulus system ready")
    }
    
    private fun initializePlayer() {
        try {
            exoPlayer = SimpleExoPlayer.Builder(requireContext()).build()
            videoPlayerView.player = exoPlayer
            
            // Set up player event listener
            exoPlayer?.addListener(object : Player.EventListener {
                override fun onPlayerStateChanged(playWhenReady: Boolean, playbackState: Int) {
                    updatePlaybackControls(playWhenReady, playbackState)
                }
                
                override fun onPlayerError(error: ExoPlaybackException) {
                    updateVideoStatus("Video playback error: ${error.message}")
                    Logger.e(TAG, "Video playback error", error)
                }
            })
            
            // Start position updates
            startPositionUpdates()
            
        } catch (e: Exception) {
            updateVideoStatus("Failed to initialize video player: ${e.message}")
            Logger.e(TAG, "Player initialization failed", e)
        }
    }
    
    private fun selectVideoFile() {
        try {
            // Launch file picker for video selection
            val intent = android.content.Intent(android.content.Intent.ACTION_GET_CONTENT)
            intent.type = "video/*"
            intent.addCategory(android.content.Intent.CATEGORY_OPENABLE)
            startActivityForResult(
                android.content.Intent.createChooser(intent, "Select Emotion Elicitation Video"),
                REQUEST_VIDEO_PICK
            )
        } catch (e: Exception) {
            updateVideoStatus("Failed to open video selector: ${e.message}")
        }
    }
    
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: android.content.Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        
        if (requestCode == REQUEST_VIDEO_PICK && resultCode == android.app.Activity.RESULT_OK) {
            data?.data?.let { uri ->
                loadVideo(uri)
            }
        }
    }
    
    private fun loadVideo(uri: Uri) {
        try {
            currentVideoUri = uri
            
            // Create media source
            val dataSourceFactory = DefaultDataSourceFactory(
                requireContext(),
                "VideoStimulusPlayer"
            )
            val mediaSource: MediaSource = ProgressiveMediaSource.Factory(dataSourceFactory)
                .createMediaSource(uri)
            
            // Prepare player
            exoPlayer?.prepare(mediaSource)
            isVideoLoaded = true
            
            // Extract video metadata
            extractVideoMetadata(uri)
            
            updateVideoStatus("Video loaded: ${getVideoName(uri)}")
            enableVideoControls(true)
            
        } catch (e: Exception) {
            updateVideoStatus("Failed to load video: ${e.message}")
            Logger.e(TAG, "Video loading failed", e)
        }
    }
    
    private fun extractVideoMetadata(uri: Uri) {
        try {
            val retriever = android.media.MediaMetadataRetriever()
            retriever.setDataSource(requireContext(), uri)
            
            videoMetadata["duration"] = retriever.extractMetadata(
                android.media.MediaMetadataRetriever.METADATA_KEY_DURATION
            )?.toLongOrNull() ?: 0L
            
            videoMetadata["width"] = retriever.extractMetadata(
                android.media.MediaMetadataRetriever.METADATA_KEY_VIDEO_WIDTH
            )?.toIntOrNull() ?: 0
            
            videoMetadata["height"] = retriever.extractMetadata(
                android.media.MediaMetadataRetriever.METADATA_KEY_VIDEO_HEIGHT
            )?.toIntOrNull() ?: 0
            
            videoMetadata["title"] = getVideoName(uri)
            videoMetadata["uri"] = uri.toString()
            
            retriever.release()
            
        } catch (e: Exception) {
            Logger.w(TAG, "Failed to extract video metadata", e)
        }
    }
    
    private fun getVideoName(uri: Uri): String {
        return try {
            val cursor = requireContext().contentResolver.query(uri, null, null, null, null)
            cursor?.use {
                if (it.moveToFirst()) {
                    val nameIndex = it.getColumnIndex(android.provider.OpenableColumns.DISPLAY_NAME)
                    if (nameIndex >= 0) it.getString(nameIndex) else "Unknown Video"
                } else "Unknown Video"
            } ?: "Unknown Video"
        } catch (e: Exception) {
            "Unknown Video"
        }
    }
    
    private fun playVideo() {
        if (isVideoLoaded && exoPlayer != null) {
            exoPlayer?.playWhenReady = true
            updateVideoStatus("Playing emotion elicitation video")
            
            // Notify main activity about video playback start
            (activity as? MainActivity)?.onVideoStimulusStarted(videoMetadata)
        }
    }
    
    private fun pauseVideo() {
        exoPlayer?.playWhenReady = false
        updateVideoStatus("Video paused")
        
        // Notify main activity
        (activity as? MainActivity)?.onVideoStimulusPaused(
            exoPlayer?.currentPosition ?: 0L
        )
    }
    
    private fun stopVideo() {
        exoPlayer?.stop()
        exoPlayer?.seekTo(0)
        updateVideoStatus("Video stopped")
        
        // Notify main activity
        (activity as? MainActivity)?.onVideoStimulusStopped(
            exoPlayer?.currentPosition ?: 0L
        )
    }
    
    private fun updatePlaybackControls(playWhenReady: Boolean, playbackState: Int) {
        when (playbackState) {
            Player.STATE_READY -> {
                playButton.isEnabled = !playWhenReady && isVideoLoaded
                pauseButton.isEnabled = playWhenReady && isVideoLoaded
                stopButton.isEnabled = isVideoLoaded
            }
            Player.STATE_BUFFERING -> {
                updateVideoStatus("Buffering video...")
            }
            Player.STATE_ENDED -> {
                updateVideoStatus("Video playback completed")
                enableVideoControls(true)
                
                // Notify main activity
                (activity as? MainActivity)?.onVideoStimulusCompleted(videoMetadata)
            }
            Player.STATE_IDLE -> {
                enableVideoControls(false)
            }
        }
    }
    
    private fun enableVideoControls(enabled: Boolean) {
        playButton.isEnabled = enabled && isVideoLoaded
        pauseButton.isEnabled = false
        stopButton.isEnabled = enabled && isVideoLoaded
        seekBar.isEnabled = enabled && isVideoLoaded
    }
    
    private fun startPositionUpdates() {
        lifecycleScope.launch {
            while (isAdded) {
                exoPlayer?.let { player ->
                    val position = player.currentPosition
                    val duration = player.duration
                    
                    if (duration > 0) {
                        val progress = ((position * 100L) / duration).toInt()
                        seekBar.progress = progress
                        
                        timeDisplay.text = formatTime(position) + " / " + formatTime(duration)
                    }
                }
                
                kotlinx.coroutines.delay(100) // Update every 100ms
            }
        }
    }
    
    private fun formatTime(milliseconds: Long): String {
        val seconds = (milliseconds / 1000) % 60
        val minutes = (milliseconds / (1000 * 60)) % 60
        return String.format("%02d:%02d", minutes, seconds)
    }
    
    private fun updateVideoStatus(message: String) {
        videoStatus.text = "[${java.text.SimpleDateFormat("HH:mm:ss", java.util.Locale.getDefault()).format(java.util.Date())}] $message"
        Logger.i(TAG, message)
    }
    
    override fun onDestroy() {
        super.onDestroy()
        exoPlayer?.release()
        exoPlayer = null
    }
    
    override fun onPause() {
        super.onPause()
        if (exoPlayer?.isPlaying == true) {
            pauseVideo()
        }
    }
    
    // Public API for external control
    fun loadVideoFromPath(videoPath: String): Boolean {
        return try {
            val uri = Uri.fromFile(File(videoPath))
            loadVideo(uri)
            true
        } catch (e: Exception) {
            updateVideoStatus("Failed to load video from path: ${e.message}")
            false
        }
    }
    
    fun getVideoStatus(): Map<String, Any> {
        return mapOf(
            "isLoaded" to isVideoLoaded,
            "isPlaying" to (exoPlayer?.isPlaying ?: false),
            "currentPosition" to (exoPlayer?.currentPosition ?: 0L),
            "duration" to (exoPlayer?.duration ?: 0L),
            "metadata" to videoMetadata
        )
    }
}

// Extension functions for MainActivity
fun MainActivity.onVideoStimulusStarted(metadata: Map<String, Any>) {
    // Send video start event to PC server
    try {
        sharedProtocolClient.sendCommand("video_stimulus_start", metadata)
        Logger.i("MainActivity", "Video stimulus started: ${metadata["title"]}")
    } catch (e: Exception) {
        Logger.e("MainActivity", "Failed to send video start event", e)
    }
}

fun MainActivity.onVideoStimulusPaused(position: Long) {
    // Send video pause event to PC server
    try {
        sharedProtocolClient.sendCommand("video_stimulus_pause", mapOf("position" to position))
        Logger.i("MainActivity", "Video stimulus paused at position: $position")
    } catch (e: Exception) {
        Logger.e("MainActivity", "Failed to send video pause event", e)
    }
}

fun MainActivity.onVideoStimulusStopped(position: Long) {
    // Send video stop event to PC server
    try {
        sharedProtocolClient.sendCommand("video_stimulus_stop", mapOf("position" to position))
        Logger.i("MainActivity", "Video stimulus stopped at position: $position")
    } catch (e: Exception) {
        Logger.e("MainActivity", "Failed to send video stop event", e)
    }
}

fun MainActivity.onVideoStimulusCompleted(metadata: Map<String, Any>) {
    // Send video completion event to PC server
    try {
        sharedProtocolClient.sendCommand("video_stimulus_complete", metadata)
        Logger.i("MainActivity", "Video stimulus completed: ${metadata["title"]}")
    } catch (e: Exception) {
        Logger.e("MainActivity", "Failed to send video complete event", e)
    }
}