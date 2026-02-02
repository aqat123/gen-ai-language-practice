package com.fluencia.app.data.model

import com.google.gson.annotations.SerializedName

/**
 * Request model for starting a placement test.
 *
 * @property targetLanguage The language for which to take the test (2-50 characters)
 */
data class PlacementTestStartRequest(
    @SerializedName("target_language")
    val targetLanguage: String
)

/**
 * Response model for starting a placement test.
 *
 * @property testId The unique identifier for the test session
 * @property targetLanguage The language being tested
 * @property totalQuestions Total number of questions in the test
 * @property message Informational message about the test
 */
data class PlacementTestStartResponse(
    @SerializedName("test_id")
    val testId: String,
    
    @SerializedName("target_language")
    val targetLanguage: String,
    
    @SerializedName("total_questions")
    val totalQuestions: Int,
    
    @SerializedName("message")
    val message: String
)

/**
 * Model representing a single placement test question.
 *
 * @property questionNumber The sequential number of this question
 * @property questionText The text of the question
 * @property options The available answer options (4 choices)
 * @property section The section type (vocabulary, grammar, or reading)
 * @property difficultyLevel The CEFR difficulty level of this question
 * @property passage Optional reading passage for reading comprehension questions
 */
data class PlacementTestQuestion(
    @SerializedName("question_number")
    val questionNumber: Int,
    
    @SerializedName("question_text")
    val questionText: String,
    
    @SerializedName("options")
    val options: List<String>,
    
    @SerializedName("section")
    val section: String,
    
    @SerializedName("difficulty_level")
    val difficultyLevel: String,
    
    @SerializedName("passage")
    val passage: String? = null
)

/**
 * Response model for getting the next question in a placement test.
 *
 * @property testId The test session identifier
 * @property question The current question data
 * @property currentQuestionNumber The current question number (1-based)
 * @property totalQuestions Total number of questions in the test
 * @property hasNext Whether there are more questions after this one
 */
data class PlacementTestQuestionResponse(
    @SerializedName("test_id")
    val testId: String,
    
    @SerializedName("question")
    val question: PlacementTestQuestion,
    
    @SerializedName("current_question_number")
    val currentQuestionNumber: Int,
    
    @SerializedName("total_questions")
    val totalQuestions: Int,
    
    @SerializedName("has_next")
    val hasNext: Boolean
)

/**
 * Request model for submitting an answer to a placement test question.
 *
 * @property questionNumber The number of the question being answered
 * @property selectedOption The index of the selected answer (0-3)
 */
data class PlacementTestAnswerRequest(
    @SerializedName("question_number")
    val questionNumber: Int,
    
    @SerializedName("selected_option")
    val selectedOption: Int
)

/**
 * Response model for submitting a placement test answer.
 *
 * @property message Status message
 * @property currentQuestionNumber The current question number after submission
 * @property totalQuestions Total number of questions in the test
 * @property hasNext Whether there are more questions to answer
 */
data class PlacementTestAnswerResponse(
    @SerializedName("message")
    val message: String,
    
    @SerializedName("current_question_number")
    val currentQuestionNumber: Int,
    
    @SerializedName("total_questions")
    val totalQuestions: Int,
    
    @SerializedName("has_next")
    val hasNext: Boolean
)

/**
 * Model representing a section score in the placement test results.
 *
 * @property section The section name (vocabulary, grammar, reading)
 * @property scorePercentage The percentage score for this section
 * @property correctAnswers Number of correct answers in this section
 * @property totalQuestions Total number of questions in this section
 */
data class PlacementTestSectionScore(
    @SerializedName("section")
    val section: String,
    
    @SerializedName("score_percentage")
    val scorePercentage: Float,
    
    @SerializedName("correct_answers")
    val correctAnswers: Int,
    
    @SerializedName("total_questions")
    val totalQuestions: Int
)

/**
 * Response model for completed placement test results.
 *
 * @property testId The test session identifier
 * @property overallScore The overall test score as a percentage
 * @property determinedLevel The CEFR level determined by the test
 * @property sectionScores Breakdown of scores by section
 * @property recommendations Personalized learning recommendations
 * @property completedAt Timestamp when the test was completed
 */
data class PlacementTestResultResponse(
    @SerializedName("test_id")
    val testId: String,
    
    @SerializedName("overall_score")
    val overallScore: Float,
    
    @SerializedName("determined_level")
    val determinedLevel: String,
    
    @SerializedName("section_scores")
    val sectionScores: List<PlacementTestSectionScore>,
    
    @SerializedName("recommendations")
    val recommendations: List<String>,
    
    @SerializedName("completed_at")
    val completedAt: String
)

/**
 * Model representing a placement test in the history.
 *
 * @property testId The test session identifier
 * @property targetLanguage The language that was tested
 * @property testDate The date when the test was taken
 * @property completed Whether the test was completed
 * @property determinedLevel The level determined (if completed)
 * @property overallScore The overall score (if completed)
 */
data class PlacementTestHistoryItem(
    @SerializedName("test_id")
    val testId: String,
    
    @SerializedName("target_language")
    val targetLanguage: String,
    
    @SerializedName("test_date")
    val testDate: String,
    
    @SerializedName("completed")
    val completed: Boolean,
    
    @SerializedName("determined_level")
    val determinedLevel: String? = null,
    
    @SerializedName("overall_score")
    val overallScore: Float? = null
)

/**
 * Response model for placement test history.
 *
 * @property tests List of placement tests taken by the user
 */
data class PlacementTestHistoryResponse(
    @SerializedName("tests")
    val tests: List<PlacementTestHistoryItem>
)
