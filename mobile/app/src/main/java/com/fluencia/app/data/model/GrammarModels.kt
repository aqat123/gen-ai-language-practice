package com.fluencia.app.data.model

import com.google.gson.annotations.SerializedName

/**
 * Response model for a grammar practice question.
 *
 * @property questionId Unique identifier for the question
 * @property questionText The text of the grammar question
 * @property options Multiple choice answer options
 * @property correctOptionIndex Index of the correct answer
 * @property explanation Explanation of the grammar rule (optional)
 * @property validation Validation metadata for the generated content
 */
data class GrammarQuestionResponse(
    @SerializedName("question_id")
    val questionId: String,
    
    @SerializedName("question_text")
    val questionText: String,
    
    @SerializedName("options")
    val options: List<String>,
    
    @SerializedName("correct_option_index")
    val correctOptionIndex: Int,
    
    @SerializedName("explanation")
    val explanation: String? = null,
    
    @SerializedName("validation")
    val validation: ValidationMetadata? = null
)

/**
 * Request model for submitting a grammar answer.
 *
 * @property questionId The ID of the question being answered
 * @property selectedOptionIndex Index of the option selected by the user
 * @property correctOptionIndex Index of the correct answer
 * @property explanation The explanation text (for tracking purposes)
 */
data class GrammarAnswerRequest(
    @SerializedName("question_id")
    val questionId: String,
    
    @SerializedName("selected_option_index")
    val selectedOptionIndex: Int,
    
    @SerializedName("correct_option_index")
    val correctOptionIndex: Int,
    
    @SerializedName("explanation")
    val explanation: String? = null
)

/**
 * Response model for a grammar answer submission.
 *
 * @property isCorrect Whether the answer was correct
 * @property correctOptionIndex Index of the correct answer
 * @property explanation Explanation of the grammar rule
 */
data class GrammarAnswerResponse(
    @SerializedName("is_correct")
    val isCorrect: Boolean,
    
    @SerializedName("correct_option_index")
    val correctOptionIndex: Int,
    
    @SerializedName("explanation")
    val explanation: String
)
