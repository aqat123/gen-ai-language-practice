package com.fluencia.app.data.model

import com.google.gson.annotations.SerializedName

/**
 * Request model for user registration.
 *
 * @property username The username for the new account (3-30 alphanumeric characters)
 * @property password The password for the account (minimum 8 characters)
 * @property fullName Optional full name of the user
 */
data class UserRegisterRequest(
    @SerializedName("username")
    val username: String,
    
    @SerializedName("password")
    val password: String,
    
    @SerializedName("full_name")
    val fullName: String? = null
)

/**
 * Request model for user login.
 *
 * @property username The user's username
 * @property password The user's password
 */
data class UserLoginRequest(
    @SerializedName("username")
    val username: String,
    
    @SerializedName("password")
    val password: String
)

/**
 * Response model containing user data.
 *
 * @property id The unique identifier of the user
 * @property username The user's username
 * @property fullName Optional full name of the user
 * @property targetLanguage The language the user is learning
 * @property level The user's current CEFR level (A1-C2)
 * @property placementTestCompleted Whether the user has completed the placement test
 */
data class UserResponse(
    @SerializedName("id")
    val id: String,
    
    @SerializedName("username")
    val username: String,
    
    @SerializedName("full_name")
    val fullName: String? = null,
    
    @SerializedName("target_language")
    val targetLanguage: String? = null,
    
    @SerializedName("level")
    val level: String? = null,
    
    @SerializedName("placement_test_completed")
    val placementTestCompleted: Boolean = false
)

/**
 * Response model for successful login/registration.
 *
 * @property accessToken The JWT access token for authentication
 * @property tokenType The type of token (typically "bearer")
 * @property expiresIn Token expiration time in seconds
 * @property user The authenticated user's data
 */
data class UserLoginResponse(
    @SerializedName("access_token")
    val accessToken: String,
    
    @SerializedName("token_type")
    val tokenType: String,
    
    @SerializedName("expires_in")
    val expiresIn: Int,
    
    @SerializedName("user")
    val user: UserResponse
)

/**
 * Request model for updating the user's target language.
 *
 * @property targetLanguage The language the user wants to learn (2-50 characters)
 */
data class UserUpdateLanguageRequest(
    @SerializedName("target_language")
    val targetLanguage: String
)

/**
 * Request model for updating the user's level.
 *
 * @property level The CEFR level (A1, A2, B1, B2, C1, or C2)
 */
data class UserUpdateLevelRequest(
    @SerializedName("level")
    val level: String
)

/**
 * Response model for user progress in a specific module.
 *
 * @property module The name of the learning module
 * @property score The user's score as a percentage (optional)
 * @property totalAttempts Total number of attempts made
 * @property correctAttempts Number of correct attempts
 */
data class UserProgressResponse(
    @SerializedName("module")
    val module: String,
    
    @SerializedName("score")
    val score: Float? = null,
    
    @SerializedName("total_attempts")
    val totalAttempts: Int,
    
    @SerializedName("correct_attempts")
    val correctAttempts: Int
)

/**
 * Generic API error response.
 *
 * @property detail The error message detail
 */
data class ApiError(
    @SerializedName("detail")
    val detail: String
)
