package com.fluencia.app.ui.theme

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.fluencia.app.data.local.ThemeManager
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * Data class representing the current theme state.
 *
 * @property isDarkMode Whether dark mode is currently enabled
 * @property useSystemTheme Whether the app is following the system theme
 * @property isLoading Whether the theme preferences are still loading
 */
data class ThemeState(
    val isDarkMode: Boolean? = null,
    val useSystemTheme: Boolean = true,
    val isLoading: Boolean = true
)

/**
 * ViewModel for managing theme state across the application.
 *
 * This ViewModel provides a reactive stream of theme state that can be observed
 * by the UI layer. It handles loading persisted theme preferences and provides
 * methods for toggling between light and dark modes.
 *
 * @property themeManager The ThemeManager instance for persisting theme preferences
 */
@HiltViewModel
class ThemeViewModel @Inject constructor(
    private val themeManager: ThemeManager
) : ViewModel() {

    /**
     * StateFlow representing the current theme state.
     *
     * This flow combines the dark mode preference and system theme flag
     * into a unified theme state that the UI can observe.
     */
    val themeState: StateFlow<ThemeState> = combine(
        themeManager.isDarkMode(),
        themeManager.useSystemTheme()
    ) { isDarkMode, useSystemTheme ->
        ThemeState(
            isDarkMode = isDarkMode,
            useSystemTheme = useSystemTheme,
            isLoading = false
        )
    }.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = ThemeState()
    )

    /**
     * Toggles between dark and light mode.
     *
     * When called, this method will switch from the current theme to the opposite
     * and persist the preference. If currently using system theme, it will
     * set an explicit preference based on the provided current state.
     *
     * @param currentIsDarkMode The current dark mode state to toggle from
     */
    fun toggleDarkMode(currentIsDarkMode: Boolean) {
        viewModelScope.launch {
            themeManager.toggleDarkMode(currentIsDarkMode)
        }
    }

    /**
     * Sets the dark mode preference explicitly.
     *
     * @param isDarkMode True to enable dark mode, false for light mode
     */
    fun setDarkMode(isDarkMode: Boolean) {
        viewModelScope.launch {
            themeManager.setDarkMode(isDarkMode)
        }
    }

    /**
     * Resets the theme preference to follow the system theme.
     *
     * After calling this method, the app will use the device's system
     * theme setting to determine light or dark mode.
     */
    fun resetToSystemTheme() {
        viewModelScope.launch {
            themeManager.resetToSystemTheme()
        }
    }
}
