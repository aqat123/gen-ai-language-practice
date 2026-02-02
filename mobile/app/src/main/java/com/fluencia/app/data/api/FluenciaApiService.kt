package com.fluencia.app.data.api

import com.fluencia.app.data.model.*
import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.Response
import retrofit2.http.*

/**
 * Retrofit API service interface for the FluencIA backend.
 *
 * This interface defines all API endpoints for the language learning application,
 * including authentication, placement tests, vocabulary, grammar, writing,
 * phonetics, conversation, progress tracking, and achievements.
 */
interface FluenciaApiService {

    // ==================== Authentication ====================

    /**
     * Register a new user account.
     *
     * @param request The registration request containing username, password, and optional full name
     * @return Response containing authentication token and user data
     */
    @POST("auth/register")
    suspend fun register(
        @Body request: UserRegisterRequest
    ): Response<UserLoginResponse>

    /**
     * Login an existing user.
     *
     * @param request The login request containing username and password
     * @return Response containing authentication token and user data
     */
    @POST("auth/login")
    suspend fun login(
        @Body request: UserLoginRequest
    ): Response<UserLoginResponse>

    /**
     * Get the current authenticated user's profile.
     *
     * @return Response containing user data
     */
    @GET("auth/me")
    suspend fun getCurrentUser(): Response<UserResponse>

    /**
     * Update the user's target language.
     *
     * @param request The language update request
     * @return Response containing updated user data
     */
    @PUT("auth/me/language")
    suspend fun updateLanguage(
        @Body request: UserUpdateLanguageRequest
    ): Response<UserResponse>

    /**
     * Update the user's CEFR level manually.
     *
     * @param request The level update request
     * @return Response containing updated user data
     */
    @PUT("auth/me/level")
    suspend fun updateLevel(
        @Body request: UserUpdateLevelRequest
    ): Response<UserResponse>

    /**
     * Get the current user's progress across all modules.
     *
     * @return Response containing list of progress for each module
     */
    @GET("auth/me/progress")
    suspend fun getUserProgress(): Response<List<UserProgressResponse>>

    // ==================== Placement Test ====================

    /**
     * Start a new placement test.
     *
     * @param request The test start request containing target language
     * @return Response containing test session information
     */
    @POST("placement-test/start")
    suspend fun startPlacementTest(
        @Body request: PlacementTestStartRequest
    ): Response<PlacementTestStartResponse>

    /**
     * Get the next question in the placement test.
     *
     * @param testId The test session identifier
     * @return Response containing the next question
     */
    @GET("placement-test/{testId}/question")
    suspend fun getPlacementTestQuestion(
        @Path("testId") testId: String
    ): Response<PlacementTestQuestionResponse>

    /**
     * Submit an answer to a placement test question.
     *
     * @param testId The test session identifier
     * @param request The answer request containing question number and selected option
     * @return Response containing submission result
     */
    @POST("placement-test/{testId}/answer")
    suspend fun submitPlacementTestAnswer(
        @Path("testId") testId: String,
        @Body request: PlacementTestAnswerRequest
    ): Response<PlacementTestAnswerResponse>

    /**
     * Complete the placement test and get results.
     *
     * @param testId The test session identifier
     * @return Response containing test results and determined level
     */
    @POST("placement-test/{testId}/complete")
    suspend fun completePlacementTest(
        @Path("testId") testId: String
    ): Response<PlacementTestResultResponse>

    /**
     * Get the user's placement test history.
     *
     * @return Response containing list of past placement tests
     */
    @GET("placement-test/history")
    suspend fun getPlacementTestHistory(): Response<PlacementTestHistoryResponse>

    // ==================== Vocabulary ====================

    /**
     * Get the next vocabulary flashcard.
     *
     * @return Response containing flashcard data
     */
    @GET("vocabulary/next")
    suspend fun getNextFlashcard(): Response<FlashcardResponse>

    /**
     * Submit an answer to a vocabulary question.
     *
     * @param request The answer request
     * @return Response containing correctness and explanation
     */
    @POST("vocabulary/answer")
    suspend fun submitVocabularyAnswer(
        @Body request: VocabularyAnswerRequest
    ): Response<VocabularyAnswerResponse>

    /**
     * Get SRS review statistics.
     *
     * @return Response containing review stats (due, learning, mastered)
     */
    @GET("vocabulary/review-stats")
    suspend fun getReviewStats(): Response<ReviewStatsResponse>

    // ==================== Grammar ====================

    /**
     * Get a grammar practice question.
     *
     * @param topic Optional topic filter for the question
     * @return Response containing the grammar question
     */
    @GET("grammar/question")
    suspend fun getGrammarQuestion(
        @Query("topic") topic: String? = null
    ): Response<GrammarQuestionResponse>

    /**
     * Submit an answer to a grammar question.
     *
     * @param request The answer request
     * @return Response containing correctness and explanation
     */
    @POST("grammar/answer")
    suspend fun submitGrammarAnswer(
        @Body request: GrammarAnswerRequest
    ): Response<GrammarAnswerResponse>

    // ==================== Writing ====================

    /**
     * Get available writing prompts.
     *
     * @return Response containing list of writing prompts
     */
    @GET("writing/prompts")
    suspend fun getWritingPrompts(): Response<List<WritingPrompt>>

    /**
     * Submit writing for feedback.
     *
     * @param request The feedback request containing the user's text
     * @return Response containing corrections and feedback
     */
    @POST("writing/feedback")
    suspend fun submitWritingFeedback(
        @Body request: WritingFeedbackRequest
    ): Response<WritingFeedbackResponse>

    // ==================== Phonetics ====================

    /**
     * Get a practice phrase for pronunciation practice.
     *
     * @return Response containing the target phrase
     */
    @GET("phonetics/phrase")
    suspend fun getPhoneticsPracticePhrase(): Response<PhoneticsPracticeSession>

    /**
     * Evaluate pronunciation by uploading audio.
     *
     * @param targetPhrase The phrase that was supposed to be pronounced
     * @param audioFile The audio recording file
     * @return Response containing pronunciation evaluation
     */
    @Multipart
    @POST("phonetics/evaluate")
    suspend fun evaluatePronunciation(
        @Part("target_phrase") targetPhrase: RequestBody,
        @Part audioFile: MultipartBody.Part
    ): Response<PhoneticsEvaluationResponse>

    // ==================== Conversation ====================

    /**
     * Start a new conversation session.
     *
     * @param request The start request containing optional topic
     * @return Response containing session ID and opening message
     */
    @POST("conversation/start")
    suspend fun startConversation(
        @Body request: ConversationStartRequest
    ): Response<ConversationStartResponse>

    /**
     * Send a message in an existing conversation.
     *
     * @param sessionId The conversation session identifier
     * @param request The message request containing the user's message
     * @return Response containing AI reply and feedback
     */
    @POST("conversation/{sessionId}/message")
    suspend fun sendConversationMessage(
        @Path("sessionId") sessionId: String,
        @Body request: ConversationMessageRequest
    ): Response<ConversationMessageResponse>

    // ==================== Progress ====================

    /**
     * Get the progress summary for the current user.
     *
     * @return Response containing comprehensive progress data
     */
    @GET("progress/summary")
    suspend fun getProgressSummary(): Response<ProgressSummaryResponse>

    /**
     * Attempt to advance to the next CEFR level.
     *
     * @return Response containing advancement result
     */
    @POST("progress/advance")
    suspend fun advanceLevel(): Response<AdvancementResponse>

    /**
     * Get the user's level progression history.
     *
     * @return Response containing list of completed levels
     */
    @GET("progress/history")
    suspend fun getLevelHistory(): Response<List<LevelHistoryItem>>

    /**
     * Apply a cheat code for demo purposes.
     *
     * @param request The cheat code request
     * @return Response containing application result
     */
    @POST("progress/cheat-code")
    suspend fun applyCheatCode(
        @Body request: CheatCodeRequest
    ): Response<CheatCodeResponse>

    /**
     * Get charts data for progress visualization.
     *
     * @return Response containing chart data
     */
    @GET("progress/charts")
    suspend fun getChartsData(): Response<ChartsDataResponse>

    /**
     * Get detailed data for a specific module.
     *
     * @param module The module name (vocabulary, grammar, writing, phonetics, conversation)
     * @return Response containing module details
     */
    @GET("progress/modules/{module}")
    suspend fun getModuleDetail(
        @Path("module") module: String
    ): Response<ModuleDetailResponse>

    // ==================== Achievements ====================

    /**
     * Get all achievements (unlocked and locked).
     *
     * @return Response containing achievements lists
     */
    @GET("achievements/")
    suspend fun getAchievements(): Response<AchievementsResponse>

    /**
     * Mark all achievements as viewed.
     *
     * @return Response containing success status
     */
    @POST("achievements/mark-viewed")
    suspend fun markAchievementsViewed(): Response<MarkViewedResponse>

    // ==================== Health Check ====================

    /**
     * Check API health status.
     *
     * @return Response containing health status
     */
    @GET("health")
    suspend fun healthCheck(): Response<Map<String, String>>
}
