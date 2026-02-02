package com.fluencia.app.data.model

import com.google.gson.annotations.SerializedName

/**
 * Metadata about the validation status of generated content.
 *
 * @property isValidated Whether the content has been validated
 * @property confidenceScore AI confidence score for the content
 * @property primaryCheckPassed Whether the primary validation passed
 * @property secondaryCheckPassed Whether the secondary validation passed
 */
data class ValidationMetadata(
    @SerializedName("is_validated")
    val isValidated: Boolean,
    
    @SerializedName("confidence_score")
    val confidenceScore: Float? = null,
    
    @SerializedName("primary_check_passed")
    val primaryCheckPassed: Boolean? = null,
    
    @SerializedName("secondary_check_passed")
    val secondaryCheckPassed: Boolean? = null
)

/**
 * Response model for a vocabulary flashcard.
 *
 * @property word The vocabulary word to learn
 * @property definition The definition of the word
 * @property exampleSentence An example sentence using the word
 * @property options Multiple choice answer options
 * @property correctOptionIndex Index of the correct answer
 * @property imageData Base64 encoded image for the flashcard (optional)
 * @property validation Validation metadata for the generated content
 * @property isReview Whether this is a review card from SRS
 * @property reviewId The review ID if this is a review card
 */
data class FlashcardResponse(
    @SerializedName("word")
    val word: String,
    
    @SerializedName("definition")
    val definition: String,
    
    @SerializedName("example_sentence")
    val exampleSentence: String,
    
    @SerializedName("options")
    val options: List<String>? = null,
    
    @SerializedName("correct_option_index")
    val correctOptionIndex: Int? = null,
    
    @SerializedName("image_data")
    val imageData: String? = null,
    
    @SerializedName("validation")
    val validation: ValidationMetadata? = null,
    
    @SerializedName("is_review")
    val isReview: Boolean? = null,
    
    @SerializedName("review_id")
    val reviewId: Int? = null
)

/**
 * Request model for submitting a vocabulary answer.
 *
 * @property word The word that was being tested
 * @property selectedOptionIndex Index of the option selected by the user
 * @property correctOptionIndex Index of the correct answer
 * @property quality SRS quality rating (optional, for reviews)
 * @property reviewId The review ID if this is a review card
 */
data class VocabularyAnswerRequest(
    @SerializedName("word")
    val word: String,
    
    @SerializedName("selected_option_index")
    val selectedOptionIndex: Int,
    
    @SerializedName("correct_option_index")
    val correctOptionIndex: Int,
    
    @SerializedName("quality")
    val quality: Int? = null,
    
    @SerializedName("review_id")
    val reviewId: Int? = null
)

/**
 * Response model for a vocabulary answer submission.
 *
 * @property isCorrect Whether the answer was correct
 * @property correctOptionIndex Index of the correct answer
 * @property explanation Explanation of the correct answer
 */
data class VocabularyAnswerResponse(
    @SerializedName("is_correct")
    val isCorrect: Boolean,
    
    @SerializedName("correct_option_index")
    val correctOptionIndex: Int,
    
    @SerializedName("explanation")
    val explanation: String? = null
)

/**
 * Response model for SRS review statistics.
 *
 * @property due Number of cards due for review
 * @property learning Number of cards currently being learned
 * @property mastered Number of mastered cards
 * @property total Total number of cards in the system
 */
data class ReviewStatsResponse(
    @SerializedName("due")
    val due: Int,
    
    @SerializedName("learning")
    val learning: Int,
    
    @SerializedName("mastered")
    val mastered: Int,
    
    @SerializedName("total")
    val total: Int
)
