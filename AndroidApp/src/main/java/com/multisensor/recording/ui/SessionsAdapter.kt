package com.multisensor.recording.ui

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.multisensor.recording.R
import com.multisensor.recording.recording.SessionInfo
import java.text.SimpleDateFormat
import java.util.*

/**
 * RecyclerView adapter for displaying recording sessions in the file browser
 */
class SessionsAdapter(
    private val sessions: List<SessionInfo>,
    private val onSessionClick: (SessionInfo) -> Unit,
) : RecyclerView.Adapter<SessionsAdapter.SessionViewHolder>() {
    private val dateFormatter = SimpleDateFormat("MMM dd, yyyy HH:mm", Locale.getDefault())

    override fun onCreateViewHolder(
        parent: ViewGroup,
        viewType: Int,
    ): SessionViewHolder {
        val view =
            LayoutInflater
                .from(parent.context)
                .inflate(R.layout.item_session, parent, false)
        return SessionViewHolder(view)
    }

    override fun onBindViewHolder(
        holder: SessionViewHolder,
        position: Int,
    ) {
        val session = sessions[position]
        holder.bind(session)
    }

    override fun getItemCount(): Int = sessions.size

    inner class SessionViewHolder(
        itemView: View,
    ) : RecyclerView.ViewHolder(itemView) {
        private val sessionIdText: TextView = itemView.findViewById(R.id.session_id_text)
        private val sessionDateText: TextView = itemView.findViewById(R.id.session_date_text)
        private val sessionDurationText: TextView = itemView.findViewById(R.id.session_duration_text)
        private val sessionStatusText: TextView = itemView.findViewById(R.id.session_status_text)
        private val sessionFilesText: TextView = itemView.findViewById(R.id.session_files_text)

        fun bind(session: SessionInfo) {
            sessionIdText.text = session.sessionId
            sessionDateText.text = dateFormatter.format(Date(session.startTime))
            sessionDurationText.text = formatDuration(session.getDurationMs())

            // Status indicator
            sessionStatusText.text =
                when {
                    session.errorOccurred -> "Error: ${session.errorMessage}"
                    session.isActive() -> "Recording..."
                    else -> "Completed"
                }

            // File count summary
            val fileCount =
                buildString {
                    var count = 0
                    if (session.videoEnabled && session.videoFilePath != null) count++
                    count += session.getRawImageCount()
                    if (session.thermalEnabled && session.thermalFilePath != null) count++

                    append("$count file")
                    if (count != 1) append("s")

                    if (session.videoEnabled) append(" • Video")
                    if (session.getRawImageCount() > 0) append(" • ${session.getRawImageCount()} RAW")
                    if (session.thermalEnabled) append(" • Thermal")
                }
            sessionFilesText.text = fileCount

            // Set click listener
            itemView.setOnClickListener {
                onSessionClick(session)
            }

            // Visual feedback for selection
            itemView.setBackgroundResource(
                if (session.errorOccurred) {
                    R.drawable.session_item_error_background
                } else {
                    R.drawable.session_item_background
                },
            )
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
    }
}
