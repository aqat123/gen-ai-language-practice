package com.fluencia.app.ui.screens.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.fluencia.app.data.repository.AuthRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * UI state for the home screen.
 */
data class HomeUiState(
    val username: String? = null,
    val targetLanguage: String? = null,
    val level: String? = null,
    val isLoading: Boolean = false
)

/**
 * ViewModel for the home screen.
 *
 * Manages user data display and logout functionality.
 *
 * @property authRepository Repository for authentication operations
 */
@HiltViewModel
class HomeViewModel @Inject constructor(
    private val authRepository: AuthRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(HomeUiState())
    
    /** Current UI state */
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    /**
     * Load user data from local storage and refresh from API.
     */
    fun loadUserData() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)
            
            // First load from local storage
            val username = authRepository.getUsername().first()
            val language = authRepository.getTargetLanguage().first()
            val level = authRepository.getLevel().first()
            
            _uiState.value = HomeUiState(
                username = username,
                targetLanguage = language,
                level = level,
                isLoading = true
            )
            
            // Then refresh from API
            val result = authRepository.getCurrentUser()
            result.onSuccess { user ->
                _uiState.value = HomeUiState(
                    username = user.username,
                    targetLanguage = user.targetLanguage,
                    level = user.level,
                    isLoading = false
                )
            }
            
            _uiState.value = _uiState.value.copy(isLoading = false)
        }
    }

    /**
     * Logout the current user.
     *
     * @param onComplete Callback when logout is complete
     */
    fun logout(onComplete: () -> Unit) {
        viewModelScope.launch {
            authRepository.logout()
            onComplete()
        }
    }
}
