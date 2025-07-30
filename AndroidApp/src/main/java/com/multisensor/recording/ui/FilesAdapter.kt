package com.multisensor.recording.ui

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.multisensor.recording.R
import java.text.SimpleDateFormat
import java.util.*

/**
 * RecyclerView adapter for displaying files within a recording session.
 * Refactored to use ListAdapter for better performance and automatic animations.
 */
class FilesAdapter(
    private val onFileClick: (FileItem) -> Unit,
) : ListAdapter<FileItem, FilesAdapter.FileViewHolder>(FileItemDiffCallback()) {
    private val dateFormatter = SimpleDateFormat("MMM dd, yyyy HH:mm", Locale.getDefault())

    override fun onCreateViewHolder(
        parent: ViewGroup,
        viewType: Int,
    ): FileViewHolder {
        val view =
            LayoutInflater
                .from(parent.context)
                .inflate(R.layout.item_file, parent, false)
        return FileViewHolder(view)
    }

    override fun onBindViewHolder(
        holder: FileViewHolder,
        position: Int,
    ) {
        val fileItem = getItem(position)
        holder.bind(fileItem)
    }

    inner class FileViewHolder(
        itemView: View,
    ) : RecyclerView.ViewHolder(itemView) {
        private val fileIconImageView: ImageView = itemView.findViewById(R.id.file_icon_image_view)
        private val fileNameText: TextView = itemView.findViewById(R.id.file_name_text)
        private val fileTypeText: TextView = itemView.findViewById(R.id.file_type_text)
        private val fileSizeText: TextView = itemView.findViewById(R.id.file_size_text)
        private val fileModifiedText: TextView = itemView.findViewById(R.id.file_modified_text)
        private val fileMetadataText: TextView = itemView.findViewById(R.id.file_metadata_text)

        fun bind(fileItem: FileItem) {
            // Set file name
            fileNameText.text = fileItem.file.name

            // Set file type and icon
            fileTypeText.text = fileItem.type.displayName
            fileIconImageView.setImageResource(getFileTypeIcon(fileItem.type))

            // Set file size
            fileSizeText.text = formatFileSize(fileItem.file.length())

            // Set modification date
            fileModifiedText.text = dateFormatter.format(Date(fileItem.file.lastModified()))

            // Set metadata if available
            if (fileItem.metadata.isNotEmpty()) {
                fileMetadataText.text = fileItem.metadata
                fileMetadataText.visibility = View.VISIBLE
            } else {
                fileMetadataText.visibility = View.GONE
            }

            // Set click listener
            itemView.setOnClickListener {
                onFileClick(fileItem)
            }

            // Set background based on file type
            itemView.setBackgroundResource(getFileTypeBackground(fileItem.type))
        }

        private fun getFileTypeIcon(fileType: FileType): Int =
            when (fileType) {
                FileType.VIDEO -> R.drawable.ic_video_file
                FileType.RAW_IMAGE -> R.drawable.ic_image_file
                FileType.THERMAL_DATA -> R.drawable.ic_data_file
            }

        private fun getFileTypeBackground(fileType: FileType): Int =
            when (fileType) {
                FileType.VIDEO -> R.drawable.file_item_video_background
                FileType.RAW_IMAGE -> R.drawable.file_item_image_background
                FileType.THERMAL_DATA -> R.drawable.file_item_data_background
            }

        private fun formatFileSize(bytes: Long): String =
            when {
                bytes >= 1024 * 1024 * 1024 -> String.format("%.1f GB", bytes / (1024.0 * 1024.0 * 1024.0))
                bytes >= 1024 * 1024 -> String.format("%.1f MB", bytes / (1024.0 * 1024.0))
                bytes >= 1024 -> String.format("%.1f KB", bytes / 1024.0)
                else -> "$bytes B"
            }
    }
}

/**
 * DiffUtil.ItemCallback for efficiently calculating list differences.
 */
class FileItemDiffCallback : DiffUtil.ItemCallback<FileItem>() {
    override fun areItemsTheSame(oldItem: FileItem, newItem: FileItem): Boolean {
        return oldItem.file.absolutePath == newItem.file.absolutePath
    }

    override fun areContentsTheSame(oldItem: FileItem, newItem: FileItem): Boolean {
        return oldItem == newItem
    }
}
