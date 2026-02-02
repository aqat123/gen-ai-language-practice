package com.fluencia.app.data.repository

import com.fluencia.app.data.api.FluenciaApiService
import com.fluencia.app.data.model.*
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Repository for handling progress tracking and achievements.
 *
 * This repository provides methods for getting progress summaries,
 * advancing levels, viewing history, and managing achievements.
 *
 * @property apiService The API service for network requests
 */
@Singleton
class ProgressRepository @Inject constructor(
    private val apiService: FluenciaApiService
) {

    // ==================== Progress ====================

    /**
     * Get the progress summary for the current user.
     *
     * @return Result containing the progress summary or error
     */
    suspend fun getProgressSummary(): Result<ProgressSummaryResponse> {
        return try {
            val response = apiService.getProgressSummary()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                val errorBody = response.errorBody()?.string() ?: "Failed to get progress summary"
                Result.failure(Exception(errorBody))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Attempt to advance to the next CEFR level.
     *
     * @return Result containing the advancement response or error
     */
    suspend fun advanceLevel(): Result<AdvancementResponse> {
        return try {
            val response = apiService.advanceLevel()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                val errorBody = response.errorBody()?.string() ?: "Failed to advance level"
                Result.failure(Exception(errorBody))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Get the user's level progression history.
     *
     * @return Result containing the level history or error
     */
    suspend fun getLevelHistory(): Result<List<LevelHistoryItem>> {
        return try {
            val response = apiService.getLevelHistory()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                val errorBody = response.errorBody()?.string() ?: "Failed to get level history"
                Result.failure(Exception(errorBody))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Apply a cheat code for demo purposes.
     *
     * @param code The cheat code to apply
     * @return Result containing the response or error
     */
    suspend fun applyCheatCode(code: String): Result<CheatCodeResponse> {
        return try {
            val response = apiService.applyCheatCode(CheatCodeRequest(code))
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                val errorBody = response.errorBody()?.string() ?: "Invalid code"
                Result.failure(Exception(errorBody))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Get charts data for progress visualization.
     *
     * @return Result containing the chart data or error
     */
    suspend fun getChartsData(): Result<ChartsDataResponse> {
        return try {
            val response = apiService.getChartsData()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                val errorBody = response.errorBody()?.string() ?: "Failed to get charts data"
                Result.failure(Exception(errorBody))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Get detailed data for a specific module.
     *
     * @param module The module name
     * @return Result containing the module details or error
     */
    suspend fun getModuleDetail(module: String): Result<ModuleDetailResponse> {
        return try {
            val response = apiService.getModuleDetail(module)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                val errorBody = response.errorBody()?.string() ?: "Failed to get module detail"
                Result.failure(Exception(errorBody))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    // ==================== Achievements ====================

    /**
     * Get all achievements (unlocked and locked).
     *
     * @return Result containing the achievements or error
     */
    suspend fun getAchievements(): Result<AchievementsResponse> {
        return try {
            val response = apiService.getAchievements()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                val errorBody = response.errorBody()?.string() ?: "Failed to get achievements"
                Result.failure(Exception(errorBody))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Mark all achievements as viewed.
     *
     * @return Result containing the response or error
     */
    suspend fun markAchievementsViewed(): Result<MarkViewedResponse> {
        return try {
            val response = apiService.markAchievementsViewed()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                val errorBody = response.errorBody()?.string() ?: "Failed to mark achievements viewed"
                Result.failure(Exception(errorBody))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
