package com.fluencia.app.data.repository

import com.fluencia.app.data.api.FluenciaApiService
import com.fluencia.app.data.model.*
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.File
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Repository for handling learning module operations.
 *
 * This repository provides methods for vocabulary, grammar, writing,
 * phonetics, and conversation practice modules.
 *
 * @property apiService The API service for network requests
 */
@Singleton
class LearningRepository @Inject constructor(
    private val apiService: FluenciaApiService
) {

    // ==================== Vocabulary ====================

    /**
     * Get the next vocabulary flashcard.
     *
     * @return Result containing the flashcard or error
     */
    suspend fun getNextFlashcard(): Result<FlashcardResponse> {
        return try {
            val response = apiService.getNextFlashcard()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                val errorBody = response.errorBody()?.string() ?: "Failed to get flashcard"
                Result.failure(Exception(errorBody))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Submit a vocabulary answer.
     *
     * @param word The word being tested
     * @param selectedIndex Index of the selected option
     * @param correctIndex Index of the correct answer
     * @param quality Optional SRS quality rating
     * @param reviewId Optional review ID for SRS cards
     * @return Result containing the answer response or error
     */
    suspend fun submitVocabularyAnswer(
        word: String,
        selectedIndex: Int,
        correctIndex: Int,
        quality: Int? = null,
        reviewId: Int? = null
    ): Result<VocabularyAnswerResponse> {
        return try {
            val response = apiService.submitVocabularyAnswer(
                VocabularyAnswerRequest(word, selectedIndex, correctIndex, quality, reviewId)
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
     * Get SRS review statistics.
     *
     * @return Result containing review stats or error
     */
    suspend fun getReviewStats(): Result<ReviewStatsResponse> {
        return try {
            val response = apiService.getReviewStats()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                val errorBody = response.errorBody()?.string() ?: "Failed to get review stats"
                Result.failure(Exception(errorBody))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    // ==================== Grammar ====================

    /**
     * Get a grammar practice question.
     *
     * @param topic Optional topic filter
     * @return Result containing the grammar question or error
     */
    suspend fun getGrammarQuestion(topic: String? = null): Result<GrammarQuestionResponse> {
        return try {
            val response = apiService.getGrammarQuestion(topic)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                val errorBody = response.errorBody()?.string() ?: "Failed to get grammar question"
                Result.failure(Exception(errorBody))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Submit a grammar answer.
     *
     * @param questionId The question ID
     * @param selectedIndex Index of the selected option
     * @param correctIndex Index of the correct answer
     * @param explanation Optional explanation text
     * @return Result containing the answer response or error
     */
    suspend fun submitGrammarAnswer(
        questionId: String,
        selectedIndex: Int,
        correctIndex: Int,
        explanation: String? = null
    ): Result<GrammarAnswerResponse> {
        return try {
            val response = apiService.submitGrammarAnswer(
                GrammarAnswerRequest(questionId, selectedIndex, correctIndex, explanation)
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

    // ==================== Writing ====================

    /**
     * Get available writing prompts.
     *
     * @return Result containing list of prompts or error
     */
    suspend fun getWritingPrompts(): Result<List<WritingPrompt>> {
        return try {
            val response = apiService.getWritingPrompts()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                val errorBody = response.errorBody()?.string() ?: "Failed to get writing prompts"
                Result.failure(Exception(errorBody))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Submit writing for feedback.
     *
     * @param text The user's written text
     * @return Result containing feedback or error
     */
    suspend fun submitWritingFeedback(text: String): Result<WritingFeedbackResponse> {
        return try {
            val response = apiService.submitWritingFeedback(WritingFeedbackRequest(text))
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                val errorBody = response.errorBody()?.string() ?: "Failed to get feedback"
                Result.failure(Exception(errorBody))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    // ==================== Phonetics ====================

    /**
     * Get a practice phrase for pronunciation.
     *
     * @return Result containing the practice session or error
     */
    suspend fun getPhoneticsPracticePhrase(): Result<PhoneticsPracticeSession> {
        return try {
            val response = apiService.getPhoneticsPracticePhrase()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                val errorBody = response.errorBody()?.string() ?: "Failed to get practice phrase"
                Result.failure(Exception(errorBody))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Evaluate pronunciation by uploading audio.
     *
     * @param targetPhrase The phrase that was supposed to be pronounced
     * @param audioFile The audio recording file
     * @return Result containing evaluation or error
     */
    suspend fun evaluatePronunciation(
        targetPhrase: String,
        audioFile: File
    ): Result<PhoneticsEvaluationResponse> {
        return try {
            val phraseRequestBody = targetPhrase.toRequestBody("text/plain".toMediaTypeOrNull())
            val audioRequestBody = audioFile.asRequestBody("audio/webm".toMediaTypeOrNull())
            val audioPart = MultipartBody.Part.createFormData(
                "audio_file",
                audioFile.name,
                audioRequestBody
            )

            val response = apiService.evaluatePronunciation(phraseRequestBody, audioPart)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                val errorBody = response.errorBody()?.string() ?: "Failed to evaluate pronunciation"
                Result.failure(Exception(errorBody))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    // ==================== Conversation ====================

    /**
     * Start a new conversation session.
     *
     * @param topic Optional conversation topic
     * @return Result containing the start response or error
     */
    suspend fun startConversation(topic: String? = null): Result<ConversationStartResponse> {
        return try {
            val response = apiService.startConversation(ConversationStartRequest(topic))
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                val errorBody = response.errorBody()?.string() ?: "Failed to start conversation"
                Result.failure(Exception(errorBody))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Send a message in an existing conversation.
     *
     * @param sessionId The conversation session ID
     * @param message The user's message
     * @return Result containing the message response or error
     */
    suspend fun sendConversationMessage(
        sessionId: String,
        message: String
    ): Result<ConversationMessageResponse> {
        return try {
            val response = apiService.sendConversationMessage(
                sessionId,
                ConversationMessageRequest(message)
            )
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                val errorBody = response.errorBody()?.string() ?: "Failed to send message"
                Result.failure(Exception(errorBody))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
