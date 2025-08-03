package com.multisensor.recording.ui.fragments

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import com.multisensor.recording.databinding.FragmentFilesBinding
import com.multisensor.recording.ui.MainViewModel
import com.multisensor.recording.ui.MainUiState
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch

/**
 * Files Fragment
 * 
 * Handles file management, browsing, and export functionality
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
        binding.apply {
            // File management buttons
            browseFilesButton.setOnClickListener {
                viewModel.browseFiles()
            }
            
            exportDataButton.setOnClickListener {
                viewModel.exportData()
            }
            
            deleteSessionButton.setOnClickListener {
                viewModel.deleteCurrentSession()
            }
            
            openFolderButton.setOnClickListener {
                viewModel.openDataFolder()
            }
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
        binding.apply {
            // Update storage info
            storageUsageText.text = "Storage: ${state.storageUsagePercent}% used"
            storageProgressBar.progress = state.storageUsagePercent
            
            // Update session info
            totalSessionsText.text = "Total Sessions: ${state.totalSessions}"
            totalDataSizeText.text = "Total Data: ${state.totalDataSize}"
            
            // Update button states based on available data
            deleteSessionButton.isEnabled = state.hasCurrentSession
            exportDataButton.isEnabled = state.totalSessions > 0
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}