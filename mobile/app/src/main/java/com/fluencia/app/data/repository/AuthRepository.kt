package com.fluencia.app.data.repository

import com.fluencia.app.data.api.FluenciaApiService
import com.fluencia.app.data.local.TokenManager
import com.fluencia.app.data.model.*
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Repository for handling authentication-related operations.
 *
 * This repository provides methods for user registration, login, logout,
 * and profile management. It coordinates between the API service and
 * local token storage.
 *
 * @property apiService The API service for network requests
 * @property tokenManager The token manager for local storage
 */
@Singleton
class AuthRepository @Inject constructor(
    private val apiService: FluenciaApiService,
    private val tokenManager: TokenManager
) {

    /**
     * Register a new user account.
     *
     * @param username The username for the new account
     * @param password The password for the account
     * @param fullName Optional full name
     * @return Result containing the login response or error
     */
    suspend fun register(
        username: String,
        password: String,
        fullName: String?
    ): Result<UserLoginResponse> {
        return try {
            val response = apiService.register(
                UserRegisterRequest(username, password, fullName)
            )
            if (response.isSuccessful && response.body() != null) {
                val loginResponse = response.body()!!
                // Save token and user data
                tokenManager.saveAccessToken(loginResponse.accessToken)
                tokenManager.saveUserData(
                    userId = loginResponse.user.id,
                    username = loginResponse.user.username,
                    targetLanguage = loginResponse.user.targetLanguage,
                    level = loginResponse.user.level
                )
                Result.success(loginResponse)
            } else {
                val errorBody = response.errorBody()?.string() ?: "Registration failed"
                Result.failure(Exception(errorBody))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Login an existing user.
     *
     * @param username The user's username
     * @param password The user's password
     * @return Result containing the login response or error
     */
    suspend fun login(username: String, password: String): Result<UserLoginResponse> {
        return try {
            val response = apiService.login(UserLoginRequest(username, password))
            if (response.isSuccessful && response.body() != null) {
                val loginResponse = response.body()!!
                // Save token and user data
                tokenManager.saveAccessToken(loginResponse.accessToken)
                tokenManager.saveUserData(
                    userId = loginResponse.user.id,
                    username = loginResponse.user.username,
                    targetLanguage = loginResponse.user.targetLanguage,
                    level = loginResponse.user.level
                )
                Result.success(loginResponse)
            } else {
                val errorBody = response.errorBody()?.string() ?: "Login failed"
                Result.failure(Exception(errorBody))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Logout the current user.
     */
    suspend fun logout() {
        tokenManager.clearAll()
    }

    /**
     * Get the current authenticated user's profile.
     *
     * @return Result containing the user data or error
     */
    suspend fun getCurrentUser(): Result<UserResponse> {
        return try {
            val response = apiService.getCurrentUser()
            if (response.isSuccessful && response.body() != null) {
                val user = response.body()!!
                // Update local storage with latest user data
                tokenManager.saveUserData(
                    userId = user.id,
                    username = user.username,
                    targetLanguage = user.targetLanguage,
                    level = user.level
                )
                Result.success(user)
            } else {
                Result.failure(Exception("Failed to get user"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Update the user's target language.
     *
     * @param language The new target language
     * @return Result containing the updated user data or error
     */
    suspend fun updateLanguage(language: String): Result<UserResponse> {
        return try {
            val response = apiService.updateLanguage(UserUpdateLanguageRequest(language))
            if (response.isSuccessful && response.body() != null) {
                val user = response.body()!!
                tokenManager.updateTargetLanguage(language)
                Result.success(user)
            } else {
                Result.failure(Exception("Failed to update language"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Update the user's CEFR level manually.
     *
     * @param level The new CEFR level
     * @return Result containing the updated user data or error
     */
    suspend fun updateLevel(level: String): Result<UserResponse> {
        return try {
            val response = apiService.updateLevel(UserUpdateLevelRequest(level))
            if (response.isSuccessful && response.body() != null) {
                val user = response.body()!!
                tokenManager.updateLevel(level)
                Result.success(user)
            } else {
                Result.failure(Exception("Failed to update level"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Check if a user is currently logged in.
     *
     * @return Flow emitting the login status
     */
    fun isLoggedIn(): Flow<Boolean> = tokenManager.isLoggedIn()

    /**
     * Get the stored access token.
     *
     * @return Flow emitting the stored token
     */
    fun getAccessToken(): Flow<String?> = tokenManager.getAccessToken()

    /**
     * Get the stored username.
     *
     * @return Flow emitting the stored username
     */
    fun getUsername(): Flow<String?> = tokenManager.getUsername()

    /**
     * Get the stored target language.
     *
     * @return Flow emitting the stored target language
     */
    fun getTargetLanguage(): Flow<String?> = tokenManager.getTargetLanguage()

    /**
     * Get the stored CEFR level.
     *
     * @return Flow emitting the stored level
     */
    fun getLevel(): Flow<String?> = tokenManager.getLevel()
}
