package com.multisensor.recording.ui.fragments

import android.content.Intent
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import kotlinx.coroutines.launch
import com.multisensor.recording.databinding.FragmentFilesBinding
import com.multisensor.recording.ui.MainViewModel
import com.multisensor.recording.ui.MainUiState
import com.multisensor.recording.ui.FileViewActivity
import dagger.hilt.android.AndroidEntryPoint

/**
 * Files Fragment
 * 
 * File management and data export interface.
 * Features:
 * - View recorded sessions
 * - File management (delete, export)
 * - Storage status monitoring
 * - Data transfer to PC
 */
@AndroidEntryPoint
class FilesFragment : Fragment() {
    
    private var _binding: FragmentFilesBinding? = null
    private val binding get() = _binding!!
    
    private val viewModel: MainViewModel by activityViewModels()
    
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
        observeViewModel()
    }
    
    private fun setupUI() {
        // File actions
        binding.viewFilesButton.setOnClickListener {
            startActivity(Intent(requireContext(), FileViewActivity::class.java))
        }
        
        binding.exportAllButton.setOnClickListener {
            viewModel.exportAllFiles()
        }
        
        binding.deleteAllButton.setOnClickListener {
            viewModel.deleteAllFiles()
        }
        
        binding.transferToPcButton.setOnClickListener {
            viewModel.transferFilesToPC()
        }
        
        binding.refreshStorageButton.setOnClickListener {
            viewModel.refreshStorageInfo()
        }
        
        binding.clearCacheButton.setOnClickListener {
            viewModel.clearCache()
        }
    }
    
    private fun observeViewModel() {
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    updateUI(state)
                }
            }
        }
    }
    
    private fun updateUI(state: MainUiState) {
        // Update storage info
        binding.storageUsedText.text = "Used: ${formatBytes(state.storageUsed)}"
        binding.storageAvailableText.text = "Available: ${formatBytes(state.storageAvailable)}"
        binding.storageTotalText.text = "Total: ${formatBytes(state.storageTotal)}"
        
        // Update progress bar
        val usagePercent = if (state.storageTotal > 0) {
            ((state.storageUsed.toFloat() / state.storageTotal.toFloat()) * 100).toInt()
        } else 0
        binding.storageProgressBar.progress = usagePercent
        binding.storagePercentText.text = "$usagePercent%"
        
        // Update file counts
        binding.sessionCountText.text = "Sessions: ${state.sessionCount}"
        binding.fileCountText.text = "Files: ${state.fileCount}"
        
        // Update button states
        binding.exportAllButton.isEnabled = state.fileCount > 0
        binding.deleteAllButton.isEnabled = state.fileCount > 0
        binding.transferToPcButton.isEnabled = state.fileCount > 0 && state.isPcConnected
        
        // Update transfer status
        binding.transferStatusText.text = when {
            state.isTransferring -> "Transferring files..."
            !state.isPcConnected -> "PC not connected"
            state.fileCount == 0 -> "No files to transfer"
            else -> "Ready to transfer"
        }
        
        binding.transferProgressBar.visibility = if (state.isTransferring) View.VISIBLE else View.GONE
        
        // Update recent sessions (mock data for now)
        updateRecentSessions(state)
    }
    
    private fun updateRecentSessions(state: MainUiState) {
        // Show/hide recent sessions
        if (state.sessionCount > 0) {
            binding.recentSessionsCard.visibility = View.VISIBLE
            binding.noFilesCard.visibility = View.GONE
        } else {
            binding.recentSessionsCard.visibility = View.GONE
            binding.noFilesCard.visibility = View.VISIBLE
        }
    }
    
    private fun formatBytes(bytes: Long): String {
        return when {
            bytes >= 1024 * 1024 * 1024 -> String.format("%.1f GB", bytes / (1024.0 * 1024.0 * 1024.0))
            bytes >= 1024 * 1024 -> String.format("%.1f MB", bytes / (1024.0 * 1024.0))
            bytes >= 1024 -> String.format("%.1f KB", bytes / 1024.0)
            else -> "$bytes B"
        }
    }
    
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}