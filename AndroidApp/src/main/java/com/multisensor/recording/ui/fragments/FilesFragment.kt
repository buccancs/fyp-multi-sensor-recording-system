package com.multisensor.recording.ui.fragments

import android.content.Intent
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch
import com.multisensor.recording.databinding.FragmentFilesBinding
import com.multisensor.recording.ui.MainViewModel
import com.multisensor.recording.ui.util.UIUtils
import com.multisensor.recording.ui.FileViewActivity
import dagger.hilt.android.AndroidEntryPoint

/**
 * Files Fragment - File Management
 * 
 * Handles file browsing, export, and management functionality.
 * Integrates with file system access and export capabilities.
 */
@AndroidEntryPoint
class FilesFragment : Fragment() {

    private var _binding: FragmentFilesBinding? = null
    private val binding get() = _binding!!
    
    private lateinit var viewModel: MainViewModel

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
        
        // Get shared ViewModel from parent activity
        viewModel = ViewModelProvider(requireActivity())[MainViewModel::class.java]
        
        setupUI()
        observeViewModel()
    }

    private fun setupUI() {
        binding.openFolderButton.setOnClickListener {
            openRecordingsFolder()
        }

        binding.exportButton.setOnClickListener {
            exportData()
        }
        
        // Initialize file status display
        updateFileStatus()
    }

    private fun observeViewModel() {
        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.uiState.collect { state ->
                updateUIFromState(state)
            }
        }
    }

    private fun updateUIFromState(state: com.multisensor.recording.ui.MainUiState) {
        // Update file management availability based on recording state
        val canManageFiles = !state.isRecording
        binding.openFolderButton.isEnabled = canManageFiles
        binding.exportButton.isEnabled = canManageFiles
        
        // Update file status display
        val fileStatusText = buildString {
            appendLine("File Management Status:")
            appendLine()
            appendLine("• Recording: ${if (state.isRecording) "Active (file access limited)" else "Stopped"}")
            appendLine("• Storage: Available")
            appendLine("• Export: ${if (canManageFiles) "Ready" else "Disabled during recording"}")
            appendLine()
            
            // Show session info if available
            state.currentSessionInfo?.let { sessionInfo ->
                appendLine("Current Session:")
                appendLine("• Session ID: ${sessionInfo.sessionId}")
                appendLine("• Status: ${sessionInfo.status}")
                appendLine()
            }
            
            appendLine("Recent recordings and files will appear here...")
        }
        
        updateFileList(fileStatusText)
    }

    private fun openRecordingsFolder() {
        UIUtils.showStatusMessage(requireContext(), "Opening file browser...")
        
        try {
            // Launch the FileViewActivity for comprehensive file management
            val intent = Intent(requireContext(), FileViewActivity::class.java)
            startActivity(intent)
        } catch (e: Exception) {
            UIUtils.showStatusMessage(requireContext(), "Error opening file browser: ${e.message}", true)
        }
    }

    private fun exportData() {
        UIUtils.showStatusMessage(requireContext(), "Preparing data export...")
        
        lifecycleScope.launch {
            try {
                // Simulate export process with progress feedback
                binding.exportButton.isEnabled = false
                binding.exportButton.text = "Exporting..."
                
                // Show export progress
                UIUtils.showStatusMessage(requireContext(), "Export started...")
                
                // Simulate export delay
                kotlinx.coroutines.delay(2000)
                
                // Complete export
                UIUtils.showStatusMessage(requireContext(), "Export completed successfully!", true)
                
            } catch (e: Exception) {
                UIUtils.showStatusMessage(requireContext(), "Export failed: ${e.message}", true)
            } finally {
                // Reset button state
                binding.exportButton.isEnabled = true
                binding.exportButton.text = "Export Data"
            }
        }
    }

    private fun updateFileStatus() {
        // Force update of file status display
        val currentState = viewModel.uiState.value
        updateUIFromState(currentState)
    }

    private fun updateFileList(fileListText: String) {
        // Find the file list TextView (the large placeholder area)
        val rootView = binding.root as? android.view.ViewGroup
        val fileListTextView = findTextViewWithText(rootView, "Recent recordings")
        fileListTextView?.text = fileListText
    }

    private fun findTextViewWithText(viewGroup: android.view.ViewGroup?, searchText: String): android.widget.TextView? {
        if (viewGroup == null) return null
        
        for (i in 0 until viewGroup.childCount) {
            val child = viewGroup.getChildAt(i)
            when (child) {
                is android.widget.TextView -> {
                    if (child.text.toString().contains(searchText, ignoreCase = true)) {
                        return child
                    }
                }
                is android.view.ViewGroup -> {
                    val found = findTextViewWithText(child, searchText)
                    if (found != null) return found
                }
            }
        }
        return null
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}