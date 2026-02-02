package com.fluencia.app.ui.screens.progress

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.fluencia.app.data.model.ProgressSummaryResponse
import com.fluencia.app.data.repository.ProgressRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * UI state for the progress screen.
 */
sealed class ProgressUiState {
    /** Loading state */
    object Loading : ProgressUiState()
    
    /** Success state with progress data */
    data class Success(val summary: ProgressSummaryResponse) : ProgressUiState()
    
    /** Advancement success state */
    data class AdvancementSuccess(
        val oldLevel: String,
        val newLevel: String,
        val xpEarned: Int,
        val celebrationMessage: String
    ) : ProgressUiState()
    
    /** Error state */
    data class Error(val message: String) : ProgressUiState()
}

/**
 * ViewModel for the progress screen.
 *
 * Manages progress display and level advancement.
 *
 * @property progressRepository Repository for progress operations
 */
@HiltViewModel
class ProgressViewModel @Inject constructor(
    private val progressRepository: ProgressRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<ProgressUiState>(ProgressUiState.Loading)
    
    /** Current UI state */
    val uiState: StateFlow<ProgressUiState> = _uiState.asStateFlow()

    /**
     * Load the user's progress summary.
     */
    fun loadProgress() {
        viewModelScope.launch {
            _uiState.value = ProgressUiState.Loading
            
            val result = progressRepository.getProgressSummary()
            
            result.fold(
                onSuccess = { summary ->
                    _uiState.value = ProgressUiState.Success(summary)
                },
                onFailure = { exception ->
                    _uiState.value = ProgressUiState.Error(
                        exception.message ?: "Failed to load progress"
                    )
                }
            )
        }
    }

    /**
     * Attempt to advance to the next level.
     */
    fun advanceLevel() {
        viewModelScope.launch {
            _uiState.value = ProgressUiState.Loading
            
            val result = progressRepository.advanceLevel()
            
            result.fold(
                onSuccess = { response ->
                    _uiState.value = ProgressUiState.AdvancementSuccess(
                        oldLevel = response.oldLevel,
                        newLevel = response.newLevel,
                        xpEarned = response.xpEarned,
                        celebrationMessage = response.celebrationMessage
                    )
                },
                onFailure = { exception ->
                    _uiState.value = ProgressUiState.Error(
                        exception.message ?: "Failed to advance level"
                    )
                }
            )
        }
    }
}
