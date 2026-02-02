package com.fluencia.app.ui.screens.progress

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.fluencia.app.data.model.Achievement
import com.fluencia.app.data.repository.ProgressRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * UI state for the achievements screen.
 */
sealed class AchievementsUiState {
    /** Loading state */
    object Loading : AchievementsUiState()
    
    /** Success state with achievements data */
    data class Success(
        val unlocked: List<Achievement>,
        val locked: List<Achievement>,
        val newCount: Int
    ) : AchievementsUiState()
    
    /** Error state */
    data class Error(val message: String) : AchievementsUiState()
}

/**
 * ViewModel for the achievements screen.
 *
 * Manages achievements display and marking as viewed.
 *
 * @property progressRepository Repository for progress operations
 */
@HiltViewModel
class AchievementsViewModel @Inject constructor(
    private val progressRepository: ProgressRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<AchievementsUiState>(AchievementsUiState.Loading)
    
    /** Current UI state */
    val uiState: StateFlow<AchievementsUiState> = _uiState.asStateFlow()

    /**
     * Load all achievements.
     */
    fun loadAchievements() {
        viewModelScope.launch {
            _uiState.value = AchievementsUiState.Loading
            
            val result = progressRepository.getAchievements()
            
            result.fold(
                onSuccess = { response ->
                    _uiState.value = AchievementsUiState.Success(
                        unlocked = response.unlocked,
                        locked = response.locked,
                        newCount = response.newCount
                    )
                    
                    // Mark achievements as viewed
                    if (response.newCount > 0) {
                        progressRepository.markAchievementsViewed()
                    }
                },
                onFailure = { exception ->
                    _uiState.value = AchievementsUiState.Error(
                        exception.message ?: "Failed to load achievements"
                    )
                }
            )
        }
    }
}
