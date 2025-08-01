package com.multisensor.recording.ui.fragments

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import com.multisensor.recording.databinding.FragmentFilesBinding

/**
 * Files Fragment - File Management
 * 
 * Handles file browsing, export, and management functionality.
 */
class FilesFragment : Fragment() {

    private var _binding: FragmentFilesBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentFilesBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        setupUI()
    }

    private fun setupUI() {
        binding.openFolderButton.setOnClickListener {
            openRecordingsFolder()
        }

        binding.exportButton.setOnClickListener {
            exportData()
        }
    }

    private fun openRecordingsFolder() {
        Toast.makeText(context, "Opening recordings folder...", Toast.LENGTH_SHORT).show()
        // TODO: Implement folder opening logic
    }

    private fun exportData() {
        Toast.makeText(context, "Exporting data...", Toast.LENGTH_SHORT).show()
        // TODO: Implement data export logic
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}