package com.multisensor.recording.ui
import android.content.Intent
import android.graphics.Color
import android.os.Bundle
import android.view.Menu
import android.view.MenuItem
import android.view.View
import android.widget.*
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import com.github.mikephil.charting.charts.LineChart
import com.github.mikephil.charting.components.XAxis
import com.github.mikephil.charting.data.Entry
import com.github.mikephil.charting.data.LineData
import com.github.mikephil.charting.data.LineDataSet
import com.google.android.material.chip.Chip
import com.google.android.material.tabs.TabLayout
import com.multisensor.recording.R
import com.multisensor.recording.util.Logger
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch
import javax.inject.Inject
@AndroidEntryPoint
class ShimmerVisualizationActivity : AppCompatActivity() {
    private val viewModel: ShimmerConfigViewModel by viewModels()
    private lateinit var deviceStatusIcon: ImageView
    private lateinit var connectionStatusChip: Chip
    private lateinit var batteryLevelText: TextView
    private lateinit var batteryProgressBar: ProgressBar
    private lateinit var signalStrengthText: TextView
    private lateinit var signalProgressBar: ProgressBar
    private lateinit var deviceInfoText: TextView
    private lateinit var dataVisualizationCard: View
    private lateinit var chartTabLayout: TabLayout
    private lateinit var gsrChart: LineChart
    private lateinit var ppgChart: LineChart
    private lateinit var accelChart: LineChart
    private lateinit var gyroChart: LineChart
    private lateinit var packetsReceivedText: TextView
    private lateinit var recordingDurationText: TextView
    private lateinit var dataRateText: TextView
    private lateinit var recordingStatusChip: Chip
    private lateinit var exportDataButton: Button
    private lateinit var startStreamingButton: Button
    private lateinit var stopStreamingButton: Button
    private lateinit var realTimeDataText: TextView
    @Inject
    lateinit var logger: Logger
    private val gsrData = mutableListOf<Entry>()
    private val ppgData = mutableListOf<Entry>()
    private val accelData = mutableListOf<Entry>()
    private val gyroData = mutableListOf<Entry>()
    private var chartEntryCount = 0
    private val maxChartEntries = 500
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_shimmer_visualization)
        setupToolbar()
        initializeViews()
        setupClickListeners()
        setupCharts()
        observeViewModelState()
        logger.info("ShimmerVisualizationActivity created")
    }
    private fun setupToolbar() {
        setSupportActionBar(findViewById(R.id.toolbar))
        supportActionBar?.apply {
            title = "Shimmer Visualization"
            setDisplayHomeAsUpEnabled(true)
        }
    }
    override fun onCreateOptionsMenu(menu: Menu?): Boolean {
        menuInflater.inflate(R.menu.menu_shimmer_visualization, menu)
        return true
    }
    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        return when (item.itemId) {
            android.R.id.home -> {
                finish()
                true
            }
            R.id.action_settings -> {
                startActivity(Intent(this, ShimmerSettingsActivity::class.java))
                true
            }
            else -> super.onOptionsItemSelected(item)
        }
    }
    private fun initializeViews() {
        deviceStatusIcon = findViewById(R.id.device_status_icon)
        connectionStatusChip = findViewById(R.id.connection_status_chip)
        batteryLevelText = findViewById(R.id.battery_level_text)
        batteryProgressBar = findViewById(R.id.battery_progress_bar)
        signalStrengthText = findViewById(R.id.signal_strength_text)
        signalProgressBar = findViewById(R.id.signal_progress_bar)
        deviceInfoText = findViewById(R.id.device_info_text)
        dataVisualizationCard = findViewById(R.id.data_visualization_card)
        chartTabLayout = findViewById(R.id.chart_tab_layout)
        gsrChart = findViewById(R.id.gsr_chart)
        ppgChart = findViewById(R.id.ppg_chart)
        accelChart = findViewById(R.id.accel_chart)
        gyroChart = findViewById(R.id.gyro_chart)
        packetsReceivedText = findViewById(R.id.packets_received_text)
        recordingDurationText = findViewById(R.id.recording_duration_text)
        dataRateText = findViewById(R.id.data_rate_text)
        recordingStatusChip = findViewById(R.id.recording_status_chip)
        exportDataButton = findViewById(R.id.export_data_button)
        startStreamingButton = findViewById(R.id.start_streaming_button)
        stopStreamingButton = findViewById(R.id.stop_streaming_button)
        realTimeDataText = findViewById(R.id.real_time_data_text)
    }
    private fun setupClickListeners() {
        startStreamingButton.setOnClickListener { 
            viewModel.startStreaming()
            dataVisualizationCard.visibility = View.VISIBLE
        }
        stopStreamingButton.setOnClickListener { 
            viewModel.stopStreaming()
        }
        exportDataButton.setOnClickListener {
            Toast.makeText(this, "Export functionality coming soon", Toast.LENGTH_SHORT).show()
        }
        chartTabLayout.addOnTabSelectedListener(object : TabLayout.OnTabSelectedListener {
            override fun onTabSelected(tab: TabLayout.Tab?) {
                when (tab?.position) {
                    0 -> showChart(gsrChart)
                    1 -> showChart(ppgChart)
                    2 -> showChart(accelChart)
                    3 -> showChart(gyroChart)
                }
            }
            override fun onTabUnselected(tab: TabLayout.Tab?) {}
            override fun onTabReselected(tab: TabLayout.Tab?) {}
        })
    }
    private fun showChart(chartToShow: LineChart) {
        gsrChart.visibility = View.GONE
        ppgChart.visibility = View.GONE
        accelChart.visibility = View.GONE
        gyroChart.visibility = View.GONE
        chartToShow.visibility = View.VISIBLE
    }
    private fun setupCharts() {
        chartTabLayout.addTab(chartTabLayout.newTab().setText("GSR"))
        chartTabLayout.addTab(chartTabLayout.newTab().setText("PPG"))
        chartTabLayout.addTab(chartTabLayout.newTab().setText("Accel"))
        chartTabLayout.addTab(chartTabLayout.newTab().setText("Gyro"))
        configureChart(gsrChart, "GSR (µS)", Color.rgb(63, 81, 181))
        configureChart(ppgChart, "PPG", Color.rgb(233, 30, 99))
        configureChart(accelChart, "Accelerometer (g)", Color.rgb(76, 175, 80))
        configureChart(gyroChart, "Gyroscope (°/s)", Color.rgb(255, 152, 0))
        showChart(gsrChart)
    }
    private fun configureChart(chart: LineChart, label: String, color: Int) {
        chart.apply {
            description.isEnabled = false
            setTouchEnabled(true)
            isDragEnabled = true
            setScaleEnabled(true)
            setPinchZoom(true)
            setDrawGridBackground(false)
            xAxis.apply {
                position = XAxis.XAxisPosition.BOTTOM
                setDrawGridLines(false)
                granularity = 1f
                isGranularityEnabled = true
            }
            axisLeft.apply {
                setDrawGridLines(true)
                gridColor = Color.LTGRAY
                gridLineWidth = 0.5f
            }
            axisRight.isEnabled = false
            legend.isEnabled = true
            val dataSet = LineDataSet(mutableListOf(), label).apply {
                this.color = color
                setCircleColor(color)
                lineWidth = 2f
                circleRadius = 3f
                setDrawCircleHole(false)
                valueTextSize = 0f
                setDrawFilled(false)
            }
            data = LineData(dataSet)
            invalidate()
        }
    }
    private fun observeViewModelState() {
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    render(state)
                }
            }
        }
    }
    private fun render(state: ShimmerConfigUiState) {
        startStreamingButton.isEnabled = state.canStartRecording
        stopStreamingButton.isEnabled = state.canStopRecording
        updateDeviceStatus(state)
        updateDataVisualization(state)
        state.errorMessage?.let { message ->
            if (state.showErrorDialog) {
                Toast.makeText(this, message, Toast.LENGTH_LONG).show()
                viewModel.onErrorMessageShown()
            }
        }
    }
    private fun updateDeviceStatus(state: ShimmerConfigUiState) {
        when {
            state.isDeviceConnected -> {
                connectionStatusChip.text = "Connected"
                connectionStatusChip.setChipBackgroundColorResource(R.color.success_color)
                deviceStatusIcon.setColorFilter(ContextCompat.getColor(this, R.color.success_color))
            }
            state.isLoadingConnection -> {
                connectionStatusChip.text = "Connecting..."
                connectionStatusChip.setChipBackgroundColorResource(R.color.warning_color)
                deviceStatusIcon.setColorFilter(ContextCompat.getColor(this, R.color.warning_color))
            }
            else -> {
                connectionStatusChip.text = "Disconnected"
                connectionStatusChip.setChipBackgroundColorResource(R.color.error_color)
                deviceStatusIcon.setColorFilter(ContextCompat.getColor(this, R.color.error_color))
            }
        }
        if (state.batteryLevel >= 0) {
            batteryLevelText.text = "${state.batteryLevel}%"
            batteryProgressBar.progress = state.batteryLevel
            batteryProgressBar.progressTintList = ContextCompat.getColorStateList(
                this,
                when {
                    state.batteryLevel > 50 -> R.color.success_color
                    state.batteryLevel > 20 -> R.color.warning_color
                    else -> R.color.error_color
                }
            )
        } else {
            batteryLevelText.text = "--"
            batteryProgressBar.progress = 0
        }
        val signalStrength = state.signalStrength
        if (signalStrength != 0) {
            signalStrengthText.text = "${signalStrength}dBm"
            val signalPercent = when {
                signalStrength > -50 -> 100
                signalStrength > -60 -> 80
                signalStrength > -70 -> 60
                signalStrength > -80 -> 40
                signalStrength > -90 -> 20
                else -> 0
            }
            signalProgressBar.progress = signalPercent
            signalProgressBar.progressTintList = ContextCompat.getColorStateList(
                this,
                when {
                    signalPercent > 60 -> R.color.success_color
                    signalPercent > 30 -> R.color.warning_color
                    else -> R.color.error_color
                }
            )
        } else {
            signalStrengthText.text = "--"
            signalProgressBar.progress = 0
        }
        if (state.isDeviceConnected) {
            deviceInfoText.text = buildString {
                append("Device Information:\n")
                append("• Firmware: ${state.firmwareVersion}\n")
                append("• Hardware: ${state.hardwareVersion}\n")
                append("• MAC: ${state.selectedDevice?.macAddress ?: "Unknown"}\n")
                append("• Battery: ${state.batteryLevel}%\n")
                append("• Signal: ${state.signalStrength}dBm")
            }
        } else {
            deviceInfoText.text = "No device connected\n\nPlease configure and connect a Shimmer device in Settings to view real-time data."
        }
    }
    private fun updateDataVisualization(state: ShimmerConfigUiState) {
        dataVisualizationCard.visibility = if (state.isRecording) View.VISIBLE else View.GONE
        recordingStatusChip.text = if (state.isRecording) "Recording" else "Stopped"
        recordingStatusChip.setChipBackgroundColorResource(
            if (state.isRecording) R.color.success_color else R.color.error_color
        )
        packetsReceivedText.text = state.dataPacketsReceived.toString()
        val duration = state.recordingDuration / 1000
        val minutes = duration / 60
        val seconds = duration % 60
        recordingDurationText.text = String.format("%02d:%02d", minutes, seconds)
        val dataRate = if (duration > 0) state.dataPacketsReceived.toDouble() / duration else 0.0
        dataRateText.text = String.format("%.1f", dataRate)
        if (state.isRecording && state.dataPacketsReceived > 0) {
            realTimeDataText.text = buildString {
                append("Active Recording Session\n")
                append("Duration: ${String.format("%02d:%02d", minutes, seconds)}\n")
                append("Packets: ${state.dataPacketsReceived}\n")
                append("Rate: ${String.format("%.1f", dataRate)} Hz\n")
                append("Signal: ${state.signalStrength} dBm\n")
                append("Battery: ${state.batteryLevel}%")
            }
        } else if (state.isDeviceConnected) {
            realTimeDataText.text = buildString {
                append("Device Ready\n")
                append("Status: Connected\n")
                append("Battery: ${if (state.batteryLevel >= 0) "${state.batteryLevel}%" else "Unknown"}\n")
                append("Signal: ${state.signalStrength} dBm\n")
                append("Firmware: ${state.firmwareVersion}")
            }
        } else {
            realTimeDataText.text = "No active session\n\nConnect a device and start recording to view real-time data."
        }
    }
}