package com.fluencia.app.ui.screens.splash

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
 * UI state for the splash screen.
 */
sealed class SplashUiState {
    /** Initial loading state */
    object Loading : SplashUiState()
    
    /** User is not authenticated */
    object NotAuthenticated : SplashUiState()
    
    /** User is authenticated but needs to select language */
    object NeedsLanguage : SplashUiState()
    
    /** User is authenticated but needs to select level */
    object NeedsLevel : SplashUiState()
    
    /** User is fully authenticated and onboarded */
    object Authenticated : SplashUiState()
}

/**
 * ViewModel for the splash screen.
 *
 * Handles checking the user's authentication state and determining
 * the appropriate navigation destination.
 *
 * @property authRepository Repository for authentication operations
 */
@HiltViewModel
class SplashViewModel @Inject constructor(
    private val authRepository: AuthRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<SplashUiState>(SplashUiState.Loading)
    
    /** Current UI state */
    val uiState: StateFlow<SplashUiState> = _uiState.asStateFlow()

    /**
     * Check the current authentication state and update UI accordingly.
     */
    fun checkAuthState() {
        viewModelScope.launch {
            try {
                val isLoggedIn = authRepository.isLoggedIn().first()
                
                if (!isLoggedIn) {
                    _uiState.value = SplashUiState.NotAuthenticated
                    return@launch
                }
                
                // Try to get current user to validate token
                val result = authRepository.getCurrentUser()
                
                result.fold(
                    onSuccess = { user ->
                        _uiState.value = when {
                            user.targetLanguage.isNullOrEmpty() -> SplashUiState.NeedsLanguage
                            user.level.isNullOrEmpty() && !user.placementTestCompleted -> SplashUiState.NeedsLevel
                            else -> SplashUiState.Authenticated
                        }
                    },
                    onFailure = {
                        // Token might be invalid, clear and go to login
                        authRepository.logout()
                        _uiState.value = SplashUiState.NotAuthenticated
                    }
                )
            } catch (e: Exception) {
                // On any error, go to login
                _uiState.value = SplashUiState.NotAuthenticated
            }
        }
    }
}
