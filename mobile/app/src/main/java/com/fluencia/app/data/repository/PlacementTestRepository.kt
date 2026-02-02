package com.fluencia.app.data.repository

import com.fluencia.app.data.api.FluenciaApiService
import com.fluencia.app.data.model.*
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Repository for handling placement test operations.
 *
 * This repository provides methods for starting tests, getting questions,
 * submitting answers, completing tests, and viewing test history.
 *
 * @property apiService The API service for network requests
 */
@Singleton
class PlacementTestRepository @Inject constructor(
    private val apiService: FluenciaApiService
) {

    /**
     * Start a new placement test.
     *
     * @param targetLanguage The language for which to take the test
     * @return Result containing the test start response or error
     */
    suspend fun startTest(targetLanguage: String): Result<PlacementTestStartResponse> {
        return try {
            val response = apiService.startPlacementTest(
                PlacementTestStartRequest(targetLanguage)
            )
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                val errorBody = response.errorBody()?.string() ?: "Failed to start test"
                Result.failure(Exception(errorBody))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Get the next question in the placement test.
     *
     * @param testId The test session identifier
     * @return Result containing the question response or error
     */
    suspend fun getQuestion(testId: String): Result<PlacementTestQuestionResponse> {
        return try {
            val response = apiService.getPlacementTestQuestion(testId)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else if (response.code() == 404) {
                // No more questions
                Result.failure(NoMoreQuestionsException())
            } else {
                val errorBody = response.errorBody()?.string() ?: "Failed to get question"
                Result.failure(Exception(errorBody))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Submit an answer to a placement test question.
     *
     * @param testId The test session identifier
     * @param questionNumber The question number being answered
     * @param selectedOption The index of the selected answer (0-3)
     * @return Result containing the answer response or error
     */
    suspend fun submitAnswer(
        testId: String,
        questionNumber: Int,
        selectedOption: Int
    ): Result<PlacementTestAnswerResponse> {
        return try {
            val response = apiService.submitPlacementTestAnswer(
                testId,
                PlacementTestAnswerRequest(questionNumber, selectedOption)
            )
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                val errorBody = response.errorBody()?.string() ?: "Failed to submit answer"
                Result.failure(Exception(errorBody))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Complete the placement test and get results.
     *
     * @param testId The test session identifier
     * @return Result containing the test results or error
     */
    suspend fun completeTest(testId: String): Result<PlacementTestResultResponse> {
        return try {
            val response = apiService.completePlacementTest(testId)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                val errorBody = response.errorBody()?.string() ?: "Failed to complete test"
                Result.failure(Exception(errorBody))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Get the user's placement test history.
     *
     * @return Result containing the test history or error
     */
    suspend fun getTestHistory(): Result<PlacementTestHistoryResponse> {
        return try {
            val response = apiService.getPlacementTestHistory()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                val errorBody = response.errorBody()?.string() ?: "Failed to get test history"
                Result.failure(Exception(errorBody))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

/**
 * Exception thrown when there are no more questions in the placement test.
 */
class NoMoreQuestionsException : Exception("No more questions available")
