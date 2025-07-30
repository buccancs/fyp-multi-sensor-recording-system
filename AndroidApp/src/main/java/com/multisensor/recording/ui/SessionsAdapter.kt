package com.multisensor.recording.ui

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.multisensor.recording.R
import java.text.SimpleDateFormat
import java.util.*

/**
 * RecyclerView adapter for displaying recording sessions in the file browser.
 * Refactored to use ListAdapter for better performance and automatic animations.
 */
class SessionsAdapter(
    private val onSessionClick: (SessionItem) -> Unit,
) : ListAdapter<SessionItem, SessionsAdapter.SessionViewHolder>(SessionItemDiffCallback()) {
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
        val session = getItem(position)
        holder.bind(session)
    }

    inner class SessionViewHolder(
        itemView: View,
    ) : RecyclerView.ViewHolder(itemView) {
        private val sessionIdText: TextView = itemView.findViewById(R.id.session_id_text)
        private val sessionDateText: TextView = itemView.findViewById(R.id.session_date_text)
        private val sessionDurationText: TextView = itemView.findViewById(R.id.session_duration_text)
        private val sessionStatusText: TextView = itemView.findViewById(R.id.session_status_text)
        private val sessionFilesText: TextView = itemView.findViewById(R.id.session_files_text)

        fun bind(session: SessionItem) {
            sessionIdText.text = session.sessionId
            sessionDateText.text = dateFormatter.format(Date(session.startTime))
            sessionDurationText.text = session.formattedDuration

            // Status indicator
            sessionStatusText.text = session.status.name

            // File count and device summary
            val fileCount =
                buildString {
                    append("${session.fileCount} file")
                    if (session.fileCount != 1) append("s")

                    if (session.deviceTypes.isNotEmpty()) {
                        append(" • ${session.deviceTypes.joinToString(", ")}")
                    }
                }
            sessionFilesText.text = fileCount

            // Set click listener
            itemView.setOnClickListener {
                onSessionClick(session)
            }

            // Visual feedback for selection
            itemView.setBackgroundResource(
                if (session.status == SessionStatus.CORRUPTED) {
                    R.drawable.session_item_error_background
                } else {
                    R.drawable.session_item_background
                },
            )
        }
    }
}

/**
 * DiffUtil.ItemCallback for efficiently calculating list differences.
 */
class SessionItemDiffCallback : DiffUtil.ItemCallback<SessionItem>() {
    override fun areItemsTheSame(oldItem: SessionItem, newItem: SessionItem): Boolean {
        return oldItem.sessionId == newItem.sessionId
    }

    override fun areContentsTheSame(oldItem: SessionItem, newItem: SessionItem): Boolean {
        return oldItem == newItem
    }
}
