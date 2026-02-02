package com.fluencia.app.data.model

import com.google.gson.annotations.SerializedName

/**
 * Model representing a writing prompt.
 *
 * @property title The title of the writing prompt
 * @property prompt The detailed prompt text
 */
data class WritingPrompt(
    @SerializedName("title")
    val title: String,
    
    @SerializedName("prompt")
    val prompt: String
)

/**
 * Request model for submitting writing for feedback.
 *
 * @property text The text written by the user
 */
data class WritingFeedbackRequest(
    @SerializedName("text")
    val text: String
)

/**
 * Response model for writing feedback.
 *
 * @property correctedText The corrected version of the user's text
 * @property overallComment General feedback about the writing
 * @property inlineExplanation Detailed inline explanations (optional)
 * @property score Score as a percentage (optional)
 */
data class WritingFeedbackResponse(
    @SerializedName("corrected_text")
    val correctedText: String,
    
    @SerializedName("overall_comment")
    val overallComment: String,
    
    @SerializedName("inline_explanation")
    val inlineExplanation: String? = null,
    
    @SerializedName("score")
    val score: Float? = null
)
