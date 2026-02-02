package com.fluencia.app.ui.screens.auth

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.fluencia.app.data.model.UserResponse
import com.fluencia.app.data.repository.AuthRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * UI state for authentication screens.
 */
sealed class AuthUiState {
    /** Initial idle state */
    object Idle : AuthUiState()
    
    /** Loading state during API calls */
    object Loading : AuthUiState()
    
    /** Success state with user data */
    data class Success(val user: UserResponse) : AuthUiState()
    
    /** Error state with message */
    data class Error(val message: String) : AuthUiState()
}

/**
 * ViewModel for authentication screens (login and registration).
 *
 * Handles user authentication operations including login, registration,
 * and logout functionality.
 *
 * @property authRepository Repository for authentication operations
 */
@HiltViewModel
class AuthViewModel @Inject constructor(
    private val authRepository: AuthRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<AuthUiState>(AuthUiState.Idle)
    
    /** Current UI state */
    val uiState: StateFlow<AuthUiState> = _uiState.asStateFlow()

    /**
     * Attempt to login with the provided credentials.
     *
     * @param username The user's username
     * @param password The user's password
     */
    fun login(username: String, password: String) {
        if (username.isBlank() || password.isBlank()) {
            _uiState.value = AuthUiState.Error("Please enter username and password")
            return
        }

        viewModelScope.launch {
            _uiState.value = AuthUiState.Loading
            
            val result = authRepository.login(username, password)
            
            _uiState.value = result.fold(
                onSuccess = { loginResponse ->
                    AuthUiState.Success(loginResponse.user)
                },
                onFailure = { exception ->
                    val message = parseErrorMessage(exception.message)
                    AuthUiState.Error(message)
                }
            )
        }
    }

    /**
     * Attempt to register a new user account.
     *
     * @param username The desired username
     * @param password The desired password
     * @param fullName Optional full name
     */
    fun register(username: String, password: String, fullName: String?) {
        if (username.length < 3 || username.length > 30) {
            _uiState.value = AuthUiState.Error("Username must be 3-30 characters")
            return
        }
        
        if (password.length < 8) {
            _uiState.value = AuthUiState.Error("Password must be at least 8 characters")
            return
        }

        viewModelScope.launch {
            _uiState.value = AuthUiState.Loading
            
            val result = authRepository.register(username, password, fullName)
            
            _uiState.value = result.fold(
                onSuccess = { loginResponse ->
                    AuthUiState.Success(loginResponse.user)
                },
                onFailure = { exception ->
                    val message = parseErrorMessage(exception.message)
                    AuthUiState.Error(message)
                }
            )
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
            _uiState.value = AuthUiState.Idle
            onComplete()
        }
    }

    /**
     * Reset the UI state to idle.
     */
    fun resetState() {
        _uiState.value = AuthUiState.Idle
    }

    /**
     * Parse error message from API response.
     */
    private fun parseErrorMessage(message: String?): String {
        return when {
            message == null -> "An error occurred"
            message.contains("401") -> "Invalid username or password"
            message.contains("400") -> "Username already exists"
            message.contains("detail") -> {
                // Try to extract detail from JSON
                val regex = "\"detail\"\\s*:\\s*\"([^\"]+)\"".toRegex()
                regex.find(message)?.groupValues?.get(1) ?: message
            }
            else -> message
        }
    }
}
