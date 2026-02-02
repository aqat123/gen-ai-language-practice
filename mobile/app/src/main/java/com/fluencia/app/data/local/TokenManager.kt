package com.fluencia.app.data.local

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

// Extension property for DataStore
private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "auth_prefs")

/**
 * Manager class for handling authentication token storage using DataStore.
 *
 * This class provides methods for saving, retrieving, and clearing JWT tokens
 * and user data using Android's DataStore Preferences API.
 *
 * @property context The application context for accessing DataStore
 */
@Singleton
class TokenManager @Inject constructor(
    @ApplicationContext private val context: Context
) {
    companion object {
        private val ACCESS_TOKEN_KEY = stringPreferencesKey("access_token")
        private val USER_ID_KEY = stringPreferencesKey("user_id")
        private val USERNAME_KEY = stringPreferencesKey("username")
        private val TARGET_LANGUAGE_KEY = stringPreferencesKey("target_language")
        private val LEVEL_KEY = stringPreferencesKey("level")
    }

    /**
     * Saves the authentication token to DataStore.
     *
     * @param token The JWT access token to save
     */
    suspend fun saveAccessToken(token: String) {
        context.dataStore.edit { preferences ->
            preferences[ACCESS_TOKEN_KEY] = token
        }
    }

    /**
     * Retrieves the stored authentication token.
     *
     * @return Flow emitting the stored token or null if not present
     */
    fun getAccessToken(): Flow<String?> {
        return context.dataStore.data.map { preferences ->
            preferences[ACCESS_TOKEN_KEY]
        }
    }

    /**
     * Saves user data to DataStore.
     *
     * @param userId The user's unique identifier
     * @param username The user's username
     * @param targetLanguage The user's target language (optional)
     * @param level The user's CEFR level (optional)
     */
    suspend fun saveUserData(
        userId: String,
        username: String,
        targetLanguage: String? = null,
        level: String? = null
    ) {
        context.dataStore.edit { preferences ->
            preferences[USER_ID_KEY] = userId
            preferences[USERNAME_KEY] = username
            targetLanguage?.let { preferences[TARGET_LANGUAGE_KEY] = it }
            level?.let { preferences[LEVEL_KEY] = it }
        }
    }

    /**
     * Updates the stored target language.
     *
     * @param language The new target language
     */
    suspend fun updateTargetLanguage(language: String) {
        context.dataStore.edit { preferences ->
            preferences[TARGET_LANGUAGE_KEY] = language
        }
    }

    /**
     * Updates the stored CEFR level.
     *
     * @param level The new CEFR level
     */
    suspend fun updateLevel(level: String) {
        context.dataStore.edit { preferences ->
            preferences[LEVEL_KEY] = level
        }
    }

    /**
     * Retrieves the stored user ID.
     *
     * @return Flow emitting the stored user ID or null if not present
     */
    fun getUserId(): Flow<String?> {
        return context.dataStore.data.map { preferences ->
            preferences[USER_ID_KEY]
        }
    }

    /**
     * Retrieves the stored username.
     *
     * @return Flow emitting the stored username or null if not present
     */
    fun getUsername(): Flow<String?> {
        return context.dataStore.data.map { preferences ->
            preferences[USERNAME_KEY]
        }
    }

    /**
     * Retrieves the stored target language.
     *
     * @return Flow emitting the stored target language or null if not present
     */
    fun getTargetLanguage(): Flow<String?> {
        return context.dataStore.data.map { preferences ->
            preferences[TARGET_LANGUAGE_KEY]
        }
    }

    /**
     * Retrieves the stored CEFR level.
     *
     * @return Flow emitting the stored level or null if not present
     */
    fun getLevel(): Flow<String?> {
        return context.dataStore.data.map { preferences ->
            preferences[LEVEL_KEY]
        }
    }

    /**
     * Checks if a user is currently logged in.
     *
     * @return Flow emitting true if a token is stored, false otherwise
     */
    fun isLoggedIn(): Flow<Boolean> {
        return context.dataStore.data.map { preferences ->
            !preferences[ACCESS_TOKEN_KEY].isNullOrEmpty()
        }
    }

    /**
     * Clears all stored authentication data (logout).
     */
    suspend fun clearAll() {
        context.dataStore.edit { preferences ->
            preferences.clear()
        }
    }
}
