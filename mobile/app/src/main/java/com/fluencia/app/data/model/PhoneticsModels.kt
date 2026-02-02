package com.fluencia.app.data.model

import com.google.gson.annotations.SerializedName

/**
 * Response model for a phonetics practice session.
 *
 * @property sessionId Unique identifier for the practice session
 * @property targetPhrase The phrase to practice pronouncing
 */
data class PhoneticsPracticeSession(
    @SerializedName("session_id")
    val sessionId: String,
    
    @SerializedName("target_phrase")
    val targetPhrase: String
)

/**
 * Model representing a word-level pronunciation issue.
 *
 * @property word The word with the pronunciation issue
 * @property issue Description of the pronunciation issue
 * @property tip Helpful tip for improving pronunciation
 */
data class WordIssue(
    @SerializedName("word")
    val word: String,
    
    @SerializedName("issue")
    val issue: String,
    
    @SerializedName("tip")
    val tip: String
)

/**
 * Response model for pronunciation evaluation.
 *
 * @property transcript The transcribed text from the user's speech
 * @property sttConfidence Speech-to-text confidence score
 * @property score Overall pronunciation score (0-100)
 * @property feedback General feedback about pronunciation
 * @property wordLevelFeedback Specific word-level pronunciation issues
 */
data class PhoneticsEvaluationResponse(
    @SerializedName("transcript")
    val transcript: String,
    
    @SerializedName("stt_confidence")
    val sttConfidence: Float,
    
    @SerializedName("score")
    val score: Float,
    
    @SerializedName("feedback")
    val feedback: String,
    
    @SerializedName("word_level_feedback")
    val wordLevelFeedback: List<WordIssue>? = null
)
