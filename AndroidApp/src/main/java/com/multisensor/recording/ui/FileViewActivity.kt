package com.multisensor.recording.ui

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.view.Menu
import android.view.MenuItem
import android.view.View
import android.widget.*
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.FileProvider
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.multisensor.recording.R
import com.multisensor.recording.recording.SessionInfo
import com.multisensor.recording.service.SessionManager
import com.multisensor.recording.util.Logger
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.*
import java.io.File
import java.text.SimpleDateFormat
import java.util.*
import javax.inject.Inject

/**
 * File View Activity - Comprehensive file browser for multi-sensor recording sessions
 * 
 * Features:
 * - Browse recorded sessions and their files
 * - Display file metadata and session information
 * - File management operations (delete, share, export)
 * - Search and filter functionality
 * - Integration with SessionInfo and SessionManager
 */
@AndroidEntryPoint
class FileViewActivity : AppCompatActivity() {

    @Inject
    lateinit var sessionManager: SessionManager
    
    @Inject
    lateinit var logger: Logger

    // UI Components
    private lateinit var sessionsRecyclerView: RecyclerView
    private lateinit var filesRecyclerView: RecyclerView
    private lateinit var sessionInfoText: TextView
    private lateinit var searchEditText: EditText
    private lateinit var filterSpinner: Spinner
    private lateinit var progressBar: ProgressBar
    private lateinit var emptyStateText: TextView
    private lateinit var refreshButton: Button

    // Adapters and Data
    private lateinit var sessionsAdapter: SessionsAdapter
    private lateinit var filesAdapter: FilesAdapter
    private val sessions = mutableListOf<SessionInfo>()
    private val currentFiles = mutableListOf<FileItem>()
    private var selectedSession: SessionInfo? = null

    // Coroutine scope
    private val activityScope = CoroutineScope(Dispatchers.Main + SupervisorJob())

    // Date formatter
    private val dateFormatter = SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault())

    companion object {
        private const val AUTHORITY = "com.multisensor.recording.fileprovider"
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_file_view)
        
        setupActionBar()
        initializeViews()
        setupRecyclerViews()
        setupClickListeners()
        setupSearch()
        loadSessions()
        
        logger.info("FileViewActivity created")
    }

    override fun onDestroy() {
        super.onDestroy()
        activityScope.cancel()
        logger.info("FileViewActivity destroyed")
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        menuInflater.inflate(R.menu.file_view_menu, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        return when (item.itemId) {
            R.id.action_refresh -> {
                refreshSessions()
                true
            }
            R.id.action_delete_all -> {
                showDeleteAllDialog()
                true
            }
            R.id.action_export_all -> {
                exportAllSessions()
                true
            }
            android.R.id.home -> {
                onBackPressed()
                true
            }
            else -> super.onOptionsItemSelected(item)
        }
    }

    private fun setupActionBar() {
        supportActionBar?.apply {
            setDisplayHomeAsUpEnabled(true)
            setDisplayShowHomeEnabled(true)
            title = "File Browser"
        }
    }

    private fun initializeViews() {
        sessionsRecyclerView = findViewById(R.id.sessions_recycler_view)
        filesRecyclerView = findViewById(R.id.files_recycler_view)
        sessionInfoText = findViewById(R.id.session_info_text)
        searchEditText = findViewById(R.id.search_edit_text)
        filterSpinner = findViewById(R.id.filter_spinner)
        progressBar = findViewById(R.id.progress_bar)
        emptyStateText = findViewById(R.id.empty_state_text)
        refreshButton = findViewById(R.id.refresh_button)
    }

    private fun setupRecyclerViews() {
        // Sessions RecyclerView
        sessionsAdapter = SessionsAdapter(sessions) { session ->
            selectSession(session)
        }
        sessionsRecyclerView.apply {
            layoutManager = LinearLayoutManager(this@FileViewActivity)
            adapter = sessionsAdapter
        }

        // Files RecyclerView
        filesAdapter = FilesAdapter(currentFiles) { fileItem ->
            handleFileClick(fileItem)
        }
        filesRecyclerView.apply {
            layoutManager = LinearLayoutManager(this@FileViewActivity)
            adapter = filesAdapter
        }
    }

    private fun setupClickListeners() {
        refreshButton.setOnClickListener {
            refreshSessions()
        }
    }

    private fun setupSearch() {
        // Search functionality using TextWatcher for EditText
        searchEditText.addTextChangedListener(object : android.text.TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {
                filterSessions(s?.toString())
            }
            
            override fun afterTextChanged(s: android.text.Editable?) {}
        })

        // Filter spinner
        val filterOptions = arrayOf("All Files", "Video Files", "RAW Images", "Thermal Data", "Recent Sessions")
        val filterAdapter = ArrayAdapter(this, android.R.layout.simple_spinner_item, filterOptions)
        filterAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        filterSpinner.adapter = filterAdapter
        
        filterSpinner.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
                applyFilter(position)
            }
            override fun onNothingSelected(parent: AdapterView<*>?) {}
        }
    }

    private fun loadSessions() {
        activityScope.launch {
            try {
                progressBar.visibility = View.VISIBLE
                emptyStateText.visibility = View.GONE
                
                // Load sessions from SessionManager
                val loadedSessions = withContext(Dispatchers.IO) {
                    sessionManager.getAllSessions()
                }
                
                sessions.clear()
                sessions.addAll(loadedSessions)
                sessionsAdapter.notifyDataSetChanged()
                
                updateEmptyState()
                
                logger.info("Loaded ${sessions.size} sessions")
                
            } catch (e: Exception) {
                logger.error("Failed to load sessions", e)
                showError("Failed to load sessions: ${e.message}")
            } finally {
                progressBar.visibility = View.GONE
            }
        }
    }

    private fun refreshSessions() {
        logger.info("Refreshing sessions...")
        loadSessions()
    }

    private fun selectSession(session: SessionInfo) {
        selectedSession = session
        updateSessionInfo(session)
        loadSessionFiles(session)
        
        logger.info("Selected session: ${session.sessionId}")
    }

    private fun updateSessionInfo(session: SessionInfo) {
        val info = buildString {
            append("Session: ${session.sessionId}\n")
            append("Duration: ${formatDuration(session.getDurationMs())}\n")
            append("Started: ${dateFormatter.format(Date(session.startTime))}\n")
            if (session.endTime > 0) {
                append("Ended: ${dateFormatter.format(Date(session.endTime))}\n")
            }
            append("Video: ${if (session.videoEnabled) "Enabled" else "Disabled"}\n")
            append("RAW Images: ${session.getRawImageCount()} files\n")
            append("Thermal: ${if (session.thermalEnabled) "Enabled (${session.thermalFrameCount} frames)" else "Disabled"}\n")
            if (session.errorOccurred) {
                append("Error: ${session.errorMessage}\n")
            }
        }
        
        sessionInfoText.text = info
    }

    private fun loadSessionFiles(session: SessionInfo) {
        activityScope.launch {
            try {
                val files = withContext(Dispatchers.IO) {
                    buildList {
                        // Add video file
                        session.videoFilePath?.let { path ->
                            val file = File(path)
                            if (file.exists()) {
                                add(FileItem(
                                    file = file,
                                    type = FileType.VIDEO,
                                    sessionId = session.sessionId,
                                    metadata = "Video recording"
                                ))
                            }
                        }
                        
                        // Add RAW files
                        session.rawFilePaths.forEach { path ->
                            val file = File(path)
                            if (file.exists()) {
                                add(FileItem(
                                    file = file,
                                    type = FileType.RAW_IMAGE,
                                    sessionId = session.sessionId,
                                    metadata = "RAW image"
                                ))
                            }
                        }
                        
                        // Add thermal file
                        session.thermalFilePath?.let { path ->
                            val file = File(path)
                            if (file.exists()) {
                                add(FileItem(
                                    file = file,
                                    type = FileType.THERMAL_DATA,
                                    sessionId = session.sessionId,
                                    metadata = "Thermal data (${session.thermalFrameCount} frames)"
                                ))
                            }
                        }
                    }
                }
                
                currentFiles.clear()
                currentFiles.addAll(files)
                filesAdapter.notifyDataSetChanged()
                
                logger.info("Loaded ${files.size} files for session ${session.sessionId}")
                
            } catch (e: Exception) {
                logger.error("Failed to load session files", e)
                showError("Failed to load files: ${e.message}")
            }
        }
    }

    private fun handleFileClick(fileItem: FileItem) {
        AlertDialog.Builder(this)
            .setTitle(fileItem.file.name)
            .setMessage(buildString {
                append("Type: ${fileItem.type.displayName}\n")
                append("Size: ${formatFileSize(fileItem.file.length())}\n")
                append("Modified: ${dateFormatter.format(Date(fileItem.file.lastModified()))}\n")
                append("Path: ${fileItem.file.absolutePath}\n")
                if (fileItem.metadata.isNotEmpty()) {
                    append("Info: ${fileItem.metadata}")
                }
            })
            .setPositiveButton("Open") { _, _ ->
                openFile(fileItem)
            }
            .setNeutralButton("Share") { _, _ ->
                shareFile(fileItem)
            }
            .setNegativeButton("Delete") { _, _ ->
                deleteFile(fileItem)
            }
            .show()
    }

    private fun openFile(fileItem: FileItem) {
        try {
            val uri = FileProvider.getUriForFile(this, AUTHORITY, fileItem.file)
            val intent = Intent(Intent.ACTION_VIEW).apply {
                setDataAndType(uri, getMimeType(fileItem.type))
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }
            
            if (intent.resolveActivity(packageManager) != null) {
                startActivity(intent)
            } else {
                showError("No app available to open this file type")
            }
            
        } catch (e: Exception) {
            logger.error("Failed to open file", e)
            showError("Failed to open file: ${e.message}")
        }
    }

    private fun shareFile(fileItem: FileItem) {
        try {
            val uri = FileProvider.getUriForFile(this, AUTHORITY, fileItem.file)
            val intent = Intent(Intent.ACTION_SEND).apply {
                type = getMimeType(fileItem.type)
                putExtra(Intent.EXTRA_STREAM, uri)
                putExtra(Intent.EXTRA_TEXT, "Shared from Multi-Sensor Recording")
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }
            
            startActivity(Intent.createChooser(intent, "Share file"))
            
        } catch (e: Exception) {
            logger.error("Failed to share file", e)
            showError("Failed to share file: ${e.message}")
        }
    }

    private fun deleteFile(fileItem: FileItem) {
        AlertDialog.Builder(this)
            .setTitle("Delete File")
            .setMessage("Are you sure you want to delete ${fileItem.file.name}?")
            .setPositiveButton("Delete") { _, _ ->
                performDeleteFile(fileItem)
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    private fun performDeleteFile(fileItem: FileItem) {
        activityScope.launch {
            try {
                val deleted = withContext(Dispatchers.IO) {
                    fileItem.file.delete()
                }
                
                if (deleted) {
                    currentFiles.remove(fileItem)
                    filesAdapter.notifyDataSetChanged()
                    showMessage("File deleted successfully")
                    logger.info("Deleted file: ${fileItem.file.name}")
                } else {
                    showError("Failed to delete file")
                }
                
            } catch (e: Exception) {
                logger.error("Failed to delete file", e)
                showError("Failed to delete file: ${e.message}")
            }
        }
    }

    private fun filterSessions(query: String?) {
        // TODO: Implement session filtering based on search query
        logger.debug("Filtering sessions with query: $query")
    }

    private fun applyFilter(filterIndex: Int) {
        // TODO: Implement file filtering based on selected filter
        logger.debug("Applying filter: $filterIndex")
    }

    private fun showDeleteAllDialog() {
        AlertDialog.Builder(this)
            .setTitle("Delete All Sessions")
            .setMessage("Are you sure you want to delete all recorded sessions? This action cannot be undone.")
            .setPositiveButton("Delete All") { _, _ ->
                deleteAllSessions()
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    private fun deleteAllSessions() {
        activityScope.launch {
            try {
                progressBar.visibility = View.VISIBLE
                
                withContext(Dispatchers.IO) {
                    sessionManager.deleteAllSessions()
                }
                
                sessions.clear()
                currentFiles.clear()
                sessionsAdapter.notifyDataSetChanged()
                filesAdapter.notifyDataSetChanged()
                
                selectedSession = null
                sessionInfoText.text = "No session selected"
                updateEmptyState()
                
                showMessage("All sessions deleted successfully")
                logger.info("Deleted all sessions")
                
            } catch (e: Exception) {
                logger.error("Failed to delete all sessions", e)
                showError("Failed to delete sessions: ${e.message}")
            } finally {
                progressBar.visibility = View.GONE
            }
        }
    }

    private fun exportAllSessions() {
        // TODO: Implement export functionality
        showMessage("Export functionality coming soon")
        logger.info("Export all sessions requested")
    }

    private fun updateEmptyState() {
        if (sessions.isEmpty()) {
            emptyStateText.visibility = View.VISIBLE
            emptyStateText.text = "No recorded sessions found.\nStart recording to see files here."
        } else {
            emptyStateText.visibility = View.GONE
        }
    }

    private fun formatDuration(durationMs: Long): String {
        val seconds = durationMs / 1000
        val minutes = seconds / 60
        val hours = minutes / 60
        
        return when {
            hours > 0 -> String.format("%d:%02d:%02d", hours, minutes % 60, seconds % 60)
            minutes > 0 -> String.format("%d:%02d", minutes, seconds % 60)
            else -> "${seconds}s"
        }
    }

    private fun formatFileSize(bytes: Long): String {
        return when {
            bytes >= 1024 * 1024 * 1024 -> String.format("%.1f GB", bytes / (1024.0 * 1024.0 * 1024.0))
            bytes >= 1024 * 1024 -> String.format("%.1f MB", bytes / (1024.0 * 1024.0))
            bytes >= 1024 -> String.format("%.1f KB", bytes / 1024.0)
            else -> "$bytes B"
        }
    }

    private fun getMimeType(fileType: FileType): String {
        return when (fileType) {
            FileType.VIDEO -> "video/mp4"
            FileType.RAW_IMAGE -> "image/*"
            FileType.THERMAL_DATA -> "application/octet-stream"
        }
    }

    private fun showMessage(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
    }

    private fun showError(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_LONG).show()
    }
}

/**
 * Data class representing a file item in the browser
 */
data class FileItem(
    val file: File,
    val type: FileType,
    val sessionId: String,
    val metadata: String = ""
)

/**
 * Enum representing different file types
 */
enum class FileType(val displayName: String) {
    VIDEO("Video"),
    RAW_IMAGE("RAW Image"),
    THERMAL_DATA("Thermal Data")
}
