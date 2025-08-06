package com.multisensor.recording.ui

import android.annotation.SuppressLint
import android.content.Intent
import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.net.Uri
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.text.Editable
import android.text.TextWatcher
import android.view.Menu
import android.view.MenuItem
import android.view.View
import android.widget.*
import androidx.activity.viewModels
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.FileProvider
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.multisensor.recording.*
import com.google.android.material.snackbar.Snackbar
import dagger.hilt.android.AndroidEntryPoint
import com.multisensor.recording.R
import com.multisensor.recording.recording.SessionInfo
import com.multisensor.recording.util.Logger
import kotlinx.coroutines.launch
import java.io.File
import java.text.SimpleDateFormat
import java.util.*
import javax.inject.Inject
import kotlin.math.*
import kotlin.random.Random

@AndroidEntryPoint
class FileViewActivity : AppCompatActivity() {

    private val viewModel: FileViewViewModel by viewModels()

    @Inject
    lateinit var logger: Logger

    private lateinit var sessionsRecyclerView: RecyclerView
    private lateinit var filesRecyclerView: RecyclerView
    private lateinit var sessionInfoText: TextView
    private lateinit var searchEditText: EditText
    private lateinit var filterSpinner: Spinner
    private lateinit var progressBar: ProgressBar
    private lateinit var emptyStateText: TextView
    private lateinit var refreshButton: Button

    private lateinit var rgbPreviewBtn: Button
    private lateinit var irPreviewBtn: Button
    private lateinit var rgbPreviewImage: ImageView
    private lateinit var irPreviewImage: ImageView
    private lateinit var rgbPreviewPlaceholder: TextView
    private lateinit var irPreviewPlaceholder: TextView

    private lateinit var sessionsAdapter: SessionsAdapter
    private lateinit var filesAdapter: FilesAdapter

    private var isRgbPreviewActive = false
    private var isIrPreviewActive = false
    private val cameraPreviewHandler = Handler(Looper.getMainLooper())
    private val rgbPreviewRunnable = object : Runnable {
        override fun run() {
            if (isRgbPreviewActive) {
                updateRgbPreview()
                cameraPreviewHandler.postDelayed(this, 100)
            }
        }
    }
    private val irPreviewRunnable = object : Runnable {
        override fun run() {
            if (isIrPreviewActive) {
                updateIrPreview()
                cameraPreviewHandler.postDelayed(this, 200)
            }
        }
    }

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
        setupEventListeners()
        observeUiState()

        logger.info("FileViewActivity created with MVVM architecture")
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        menuInflater.inflate(R.menu.file_view_menu, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean =
        when (item.itemId) {
            R.id.action_refresh -> {
                viewModel.refreshSessions()
                true
            }

            R.id.action_delete_all -> {
                showDeleteAllDialog()
                true
            }

            R.id.action_export_all -> {
                showMessage("Export functionality coming soon")
                true
            }

            android.R.id.home -> {
                onBackPressedDispatcher.onBackPressed()
                true
            }

            else -> super.onOptionsItemSelected(item)
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

        rgbPreviewBtn = findViewById(R.id.rgb_preview_btn)
        irPreviewBtn = findViewById(R.id.ir_preview_btn)
        rgbPreviewImage = findViewById(R.id.rgb_preview_image)
        irPreviewImage = findViewById(R.id.ir_preview_image)
        rgbPreviewPlaceholder = findViewById(R.id.rgb_preview_placeholder)
        irPreviewPlaceholder = findViewById(R.id.ir_preview_placeholder)

        rgbPreviewBtn.setOnClickListener { toggleRgbPreview() }
        irPreviewBtn.setOnClickListener { toggleIrPreview() }
    }

    private fun setupRecyclerViews() {
        sessionsAdapter = SessionsAdapter { session ->
            viewModel.selectSession(session)
        }
        sessionsRecyclerView.apply {
            layoutManager = LinearLayoutManager(this@FileViewActivity)
            adapter = sessionsAdapter
        }

        filesAdapter = FilesAdapter { fileItem ->
            handleFileClick(fileItem)
        }
        filesRecyclerView.apply {
            layoutManager = LinearLayoutManager(this@FileViewActivity)
            adapter = filesAdapter
        }
    }

    private fun setupEventListeners() {
        searchEditText.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {
                viewModel.onSearchQueryChanged(s.toString())
            }

            override fun afterTextChanged(s: Editable?) {}
        })

        val filterOptions = arrayOf("All Files", "Video Files", "RAW Images", "Thermal Data", "Recent Sessions")
        val filterAdapter = ArrayAdapter(this, android.R.layout.simple_spinner_item, filterOptions)
        filterAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        filterSpinner.adapter = filterAdapter

        filterSpinner.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
                viewModel.applyFilter(position)
            }

            override fun onNothingSelected(parent: AdapterView<*>?) {}
        }

        refreshButton.setOnClickListener {
            viewModel.refreshSessions()
        }
    }

    private fun observeUiState() {
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    render(state)
                }
            }
        }
    }

    private fun render(state: FileViewUiState) {
        progressBar.visibility = if (state.isLoadingSessions || state.isLoadingFiles) View.VISIBLE else View.GONE

        emptyStateText.visibility = if (state.showEmptyState) View.VISIBLE else View.GONE

        sessionsAdapter.submitList(state.sessions)

        filesAdapter.submitList(state.sessionFiles)

        state.selectedSession?.let { session ->
            updateSessionInfo(session)
        } ?: run {
            sessionInfoText.text = "No session selected"
        }

        state.errorMessage?.let { error ->
            showError(error)
            viewModel.clearError()
        }
    }

    private fun updateSessionInfo(session: SessionItem) {
        val info = buildString {
            append("Session: ${session.sessionId}\n")
            append("Name: ${session.name}\n")
            append("Start: ${dateFormatter.format(Date(session.startTime))}\n")
            if (session.endTime > 0) {
                append("End: ${dateFormatter.format(Date(session.endTime))}\n")
                append("Duration: ${session.formattedDuration}\n")
            } else {
                append("Status: ${session.status}\n")
            }
            append("Files: ${session.fileCount}\n")
            append("Size: ${formatFileSize(session.totalSize)}\n")
            append("Devices: ${session.deviceTypes.joinToString(", ")}")
        }
        sessionInfoText.text = info
    }

    private fun handleFileClick(fileItem: FileItem) {
        AlertDialog.Builder(this)
            .setTitle(fileItem.file.name)
            .setMessage(
                "File size: ${formatFileSize(fileItem.file.length())}\nLast modified: ${
                    dateFormatter.format(
                        Date(fileItem.file.lastModified())
                    )
                }"
            )
            .setPositiveButton("Open") { _, _ ->
                openFile(fileItem)
            }
            .setNeutralButton("Share") { _, _ ->
                shareFile(fileItem)
            }
            .setNegativeButton("Delete") { _, _ ->
                confirmDeleteFile(fileItem)
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
            startActivity(Intent.createChooser(intent, "Open with"))
        } catch (e: Exception) {
            showError("Failed to open file: ${e.message}")
        }
    }

    private fun shareFile(fileItem: FileItem) {
        try {
            val uri = FileProvider.getUriForFile(this, AUTHORITY, fileItem.file)
            val intent = Intent(Intent.ACTION_SEND).apply {
                type = getMimeType(fileItem.type)
                putExtra(Intent.EXTRA_STREAM, uri)
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }
            startActivity(Intent.createChooser(intent, "Share file"))
        } catch (e: Exception) {
            showError("Failed to share file: ${e.message}")
        }
    }

    private fun confirmDeleteFile(fileItem: FileItem) {
        AlertDialog.Builder(this)
            .setTitle("Delete File")
            .setMessage("Are you sure you want to delete ${fileItem.file.name}?")
            .setPositiveButton("Delete") { _, _ ->
                viewModel.deleteFile(fileItem)
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    private fun showDeleteAllDialog() {
        AlertDialog.Builder(this)
            .setTitle("Delete All Sessions")
            .setMessage("Are you sure you want to delete all recording sessions? This action cannot be undone.")
            .setPositiveButton("Delete All") { _, _ ->
                viewModel.deleteAllSessions()
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    @SuppressLint("DefaultLocale")
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

    @SuppressLint("DefaultLocale")
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
            FileType.VIDEO -> "video/*"
            FileType.THERMAL -> "application/octet-stream"
            FileType.GSR -> "text/csv"
            FileType.METADATA -> "application/json"
            FileType.LOG -> "text/plain"
            else -> "application/octet-stream"
        }
    }

    private fun showMessage(message: String) {
        findViewById<View>(android.R.id.content)?.let { view ->
            Snackbar.make(view, message, Snackbar.LENGTH_SHORT).show()
        }
    }

    private fun showError(message: String) {
        findViewById<View>(android.R.id.content)?.let { view ->
            Snackbar.make(view, message, Snackbar.LENGTH_LONG)
                .setBackgroundTint(getColor(android.R.color.holo_red_dark))
                .show()
        }
    }

    private fun toggleRgbPreview() {
        if (!isRgbPreviewActive) {
            startRgbPreview()
        } else {
            stopRgbPreview()
        }
    }

    private fun toggleIrPreview() {
        if (!isIrPreviewActive) {
            startIrPreview()
        } else {
            stopIrPreview()
        }
    }

    private fun startRgbPreview() {
        isRgbPreviewActive = true
        rgbPreviewBtn.text = "Stop"
        rgbPreviewBtn.backgroundTintList = getColorStateList(android.R.color.holo_red_dark)

        rgbPreviewPlaceholder.visibility = View.GONE
        rgbPreviewImage.visibility = View.VISIBLE

        cameraPreviewHandler.post(rgbPreviewRunnable)

        logger.info("RGB camera preview started")
        showMessage("RGB camera preview started")
    }

    private fun stopRgbPreview() {
        isRgbPreviewActive = false
        rgbPreviewBtn.text = "Start"
        rgbPreviewBtn.backgroundTintList = getColorStateList(android.R.color.holo_green_dark)

        rgbPreviewImage.visibility = View.GONE
        rgbPreviewPlaceholder.visibility = View.VISIBLE

        cameraPreviewHandler.removeCallbacks(rgbPreviewRunnable)

        logger.info("RGB camera preview stopped")
        showMessage("RGB camera preview stopped")
    }

    private fun startIrPreview() {
        isIrPreviewActive = true
        irPreviewBtn.text = "Stop"
        irPreviewBtn.backgroundTintList = getColorStateList(android.R.color.holo_red_dark)

        irPreviewPlaceholder.visibility = View.GONE
        irPreviewImage.visibility = View.VISIBLE

        cameraPreviewHandler.post(irPreviewRunnable)

        logger.info("IR camera preview started")
        showMessage("IR camera preview started")
    }

    private fun stopIrPreview() {
        isIrPreviewActive = false
        irPreviewBtn.text = "Start"
        irPreviewBtn.backgroundTintList = getColorStateList(android.R.color.holo_orange_dark)

        irPreviewImage.visibility = View.GONE
        irPreviewPlaceholder.visibility = View.VISIBLE

        cameraPreviewHandler.removeCallbacks(irPreviewRunnable)

        logger.info("IR camera preview stopped")
        showMessage("IR camera preview stopped")
    }

    private fun updateRgbPreview() {
        try {

            val bitmap = generateRgbPreviewBitmap()
            rgbPreviewImage.setImageBitmap(bitmap)
        } catch (e: Exception) {
            logger.error("Error updating RGB preview: ${e.message}")
        }
    }

    private fun updateIrPreview() {
        try {

            val bitmap = generateThermalPreviewBitmap()
            irPreviewImage.setImageBitmap(bitmap)
        } catch (e: Exception) {
            logger.error("Error updating IR preview: ${e.message}")
        }
    }

    private fun generateRgbPreviewBitmap(): Bitmap {
        val width = 320
        val height = 240
        val bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
        val canvas = Canvas(bitmap)
        val paint = Paint()

        val time = System.currentTimeMillis() / 100

        paint.color = Color.rgb(50, 50, 80)
        canvas.drawRect(0f, 0f, width.toFloat(), height.toFloat(), paint)

        for (i in 0..10) {
            val x = ((time + i * 30) % (width + 100)).toFloat() - 50
            val y = (height * 0.2f + i * height * 0.05f).toFloat()

            paint.color = Color.rgb(
                (100 + i * 15) % 255,
                (150 + i * 10) % 255,
                (200 + i * 5) % 255
            )
            canvas.drawCircle(x, y, 15f, paint)
        }

        paint.color = Color.RED
        paint.textSize = 24f
        canvas.drawText("● LIVE", 10f, 30f, paint)

        paint.color = Color.WHITE
        paint.textSize = 16f
        val timeStr = SimpleDateFormat("HH:mm:ss", Locale.getDefault()).format(Date())
        canvas.drawText(timeStr, 10f, height - 10f, paint)

        return bitmap
    }

    private fun generateThermalPreviewBitmap(): Bitmap {
        val width = 320
        val height = 240
        val bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
        val canvas = Canvas(bitmap)
        val paint = Paint()

        val time = System.currentTimeMillis() / 200.0

        for (y in 0 until height) {
            for (x in 0 until width) {

                val centerX = width / 2.0
                val centerY = height / 2.0
                val distance = sqrt((x - centerX).pow(2) + (y - centerY).pow(2))

                val intensity = (127 + 127 * sin(distance * 0.1 + time)).toInt().coerceIn(0, 255)

                val color = when {
                    intensity < 85 -> Color.rgb(0, 0, intensity * 3)
                    intensity < 170 -> Color.rgb((intensity - 85) * 3, 0, 255 - (intensity - 85) * 2)
                    else -> Color.rgb(255, (intensity - 170) * 3, 0)
                }

                paint.color = color
                canvas.drawPoint(x.toFloat(), y.toFloat(), paint)
            }
        }

        paint.color = Color.YELLOW
        for (i in 0..3) {
            val hotX = Random.nextInt(50, width - 50).toFloat()
            val hotY = Random.nextInt(50, height - 50).toFloat()
            canvas.drawCircle(hotX, hotY, 20f, paint)
        }

        paint.color = Color.WHITE
        paint.textSize = 18f
        canvas.drawText("🌡️ THERMAL", 10f, 30f, paint)

        val temp = (20 + Random.nextFloat() * 15).toInt()
        paint.textSize = 14f
        canvas.drawText("${temp}°C", width - 60f, height - 10f, paint)

        return bitmap
    }

    override fun onDestroy() {
        super.onDestroy()

        stopRgbPreview()
        stopIrPreview()

        logger.info("FileViewActivity destroyed")
    }
}