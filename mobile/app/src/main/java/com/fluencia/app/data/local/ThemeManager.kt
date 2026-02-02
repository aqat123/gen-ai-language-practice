package com.fluencia.app.data.local

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.preferencesDataStore
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Extension property for creating a DataStore instance for theme preferences.
 * 
 * Uses a separate DataStore from auth preferences to maintain separation of concerns.
 */
private val Context.themeDataStore: DataStore<Preferences> by preferencesDataStore(name = "theme_prefs")

/**
 * Manager class for handling theme preferences using DataStore.
 *
 * This class provides methods for saving and retrieving the user's dark mode preference
 * using Android's DataStore Preferences API. The preference persists across app restarts.
 *
 * @property context The application context for accessing DataStore
 */
@Singleton
class ThemeManager @Inject constructor(
    @ApplicationContext private val context: Context
) {
    companion object {
        /**
         * Key for storing the dark mode preference in DataStore.
         */
        private val DARK_MODE_KEY = booleanPreferencesKey("dark_mode_enabled")
        
        /**
         * Key for storing whether the user has explicitly set a theme preference.
         * When false, the app follows the system theme.
         */
        private val USE_SYSTEM_THEME_KEY = booleanPreferencesKey("use_system_theme")
    }

    /**
     * Retrieves the current dark mode preference.
     *
     * @return Flow emitting the dark mode preference. Returns null if the user
     *         hasn't set a preference, indicating the app should follow system theme.
     */
    fun isDarkMode(): Flow<Boolean?> {
        return context.themeDataStore.data.map { preferences ->
            if (preferences[USE_SYSTEM_THEME_KEY] != false) {
                null // Use system theme
            } else {
                preferences[DARK_MODE_KEY] ?: false
            }
        }
    }

    /**
     * Retrieves whether the app should use the system theme.
     *
     * @return Flow emitting true if following system theme, false if user has set a preference
     */
    fun useSystemTheme(): Flow<Boolean> {
        return context.themeDataStore.data.map { preferences ->
            preferences[USE_SYSTEM_THEME_KEY] ?: true
        }
    }

    /**
     * Sets the dark mode preference.
     *
     * When called, this also sets the use_system_theme flag to false,
     * indicating the user has explicitly chosen a theme.
     *
     * @param isDarkMode True for dark mode, false for light mode
     */
    suspend fun setDarkMode(isDarkMode: Boolean) {
        context.themeDataStore.edit { preferences ->
            preferences[DARK_MODE_KEY] = isDarkMode
            preferences[USE_SYSTEM_THEME_KEY] = false
        }
    }

    /**
     * Toggles between dark and light mode.
     *
     * @param currentIsDarkMode The current dark mode state
     */
    suspend fun toggleDarkMode(currentIsDarkMode: Boolean) {
        setDarkMode(!currentIsDarkMode)
    }

    /**
     * Resets the theme preference to follow the system theme.
     *
     * This clears any user-set preference and returns to using the device's theme setting.
     */
    suspend fun resetToSystemTheme() {
        context.themeDataStore.edit { preferences ->
            preferences[USE_SYSTEM_THEME_KEY] = true
        }
    }

    /**
     * Clears all theme preferences.
     *
     * This is typically used when the user logs out or wants to reset all settings.
     */
    suspend fun clearThemePreferences() {
        context.themeDataStore.edit { preferences ->
            preferences.clear()
        }
    }
}
