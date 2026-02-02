package com.fluencia.app.ui.screens.onboarding

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.fluencia.app.data.repository.AuthRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * UI state for onboarding screens.
 */
sealed class OnboardingUiState {
    /** Initial idle state */
    object Idle : OnboardingUiState()
    
    /** Loading state during API calls */
    object Loading : OnboardingUiState()
    
    /** Language has been successfully updated */
    object LanguageUpdated : OnboardingUiState()
    
    /** Level has been successfully updated */
    object LevelUpdated : OnboardingUiState()
    
    /** Error state with message */
    data class Error(val message: String) : OnboardingUiState()
}

/**
 * ViewModel for onboarding screens (language and level selection).
 *
 * Handles updating user preferences during the onboarding flow.
 *
 * @property authRepository Repository for user operations
 */
@HiltViewModel
class OnboardingViewModel @Inject constructor(
    private val authRepository: AuthRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<OnboardingUiState>(OnboardingUiState.Idle)
    
    /** Current UI state */
    val uiState: StateFlow<OnboardingUiState> = _uiState.asStateFlow()

    /**
     * Update the user's target language.
     *
     * @param language The selected language code
     */
    fun selectLanguage(language: String) {
        viewModelScope.launch {
            _uiState.value = OnboardingUiState.Loading
            
            val result = authRepository.updateLanguage(language)
            
            _uiState.value = result.fold(
                onSuccess = { OnboardingUiState.LanguageUpdated },
                onFailure = { OnboardingUiState.Error(it.message ?: "Failed to update language") }
            )
        }
    }

    /**
     * Update the user's CEFR level manually.
     *
     * @param level The selected level code (A1-C2)
     */
    fun selectLevel(level: String) {
        viewModelScope.launch {
            _uiState.value = OnboardingUiState.Loading
            
            val result = authRepository.updateLevel(level)
            
            _uiState.value = result.fold(
                onSuccess = { OnboardingUiState.LevelUpdated },
                onFailure = { OnboardingUiState.Error(it.message ?: "Failed to update level") }
            )
        }
    }

    /**
     * Reset the UI state to idle.
     */
    fun resetState() {
        _uiState.value = OnboardingUiState.Idle
    }
}
