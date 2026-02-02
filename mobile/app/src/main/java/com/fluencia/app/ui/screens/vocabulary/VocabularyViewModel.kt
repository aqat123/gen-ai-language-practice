package com.fluencia.app.ui.screens.vocabulary

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.fluencia.app.data.model.FlashcardResponse
import com.fluencia.app.data.model.ReviewStatsResponse
import com.fluencia.app.data.model.VocabularyAnswerResponse
import com.fluencia.app.data.repository.LearningRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * UI state for the vocabulary screen.
 */
sealed class VocabularyUiState {
    /** Loading state */
    object Loading : VocabularyUiState()
    
    /** Flashcard display state */
    data class Flashcard(
        val flashcard: FlashcardResponse,
        val answerResult: VocabularyAnswerResponse? = null
    ) : VocabularyUiState()
    
    /** Error state */
    data class Error(val message: String) : VocabularyUiState()
}

/**
 * ViewModel for the vocabulary screen.
 *
 * Manages vocabulary flashcard practice including loading cards,
 * submitting answers, and tracking SRS statistics.
 *
 * @property learningRepository Repository for learning operations
 */
@HiltViewModel
class VocabularyViewModel @Inject constructor(
    private val learningRepository: LearningRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<VocabularyUiState>(VocabularyUiState.Loading)
    
    /** Current UI state */
    val uiState: StateFlow<VocabularyUiState> = _uiState.asStateFlow()
    
    private val _reviewStats = MutableStateFlow<ReviewStatsResponse?>(null)
    
    /** SRS review statistics */
    val reviewStats: StateFlow<ReviewStatsResponse?> = _reviewStats.asStateFlow()
    
    private var currentFlashcard: FlashcardResponse? = null

    /**
     * Load the next vocabulary flashcard.
     */
    fun loadNextFlashcard() {
        viewModelScope.launch {
            _uiState.value = VocabularyUiState.Loading
            
            val result = learningRepository.getNextFlashcard()
            
            result.fold(
                onSuccess = { flashcard ->
                    currentFlashcard = flashcard
                    _uiState.value = VocabularyUiState.Flashcard(flashcard)
                },
                onFailure = { exception ->
                    _uiState.value = VocabularyUiState.Error(
                        exception.message ?: "Failed to load flashcard"
                    )
                }
            )
        }
    }

    /**
     * Submit an answer to the current flashcard.
     *
     * @param selectedIndex Index of the selected option
     */
    fun submitAnswer(selectedIndex: Int) {
        val flashcard = currentFlashcard ?: return
        val correctIndex = flashcard.correctOptionIndex ?: return
        
        viewModelScope.launch {
            // Calculate quality for SRS
            val isCorrect = selectedIndex == correctIndex
            val quality = if (isCorrect) 5 else 2
            
            val result = learningRepository.submitVocabularyAnswer(
                word = flashcard.word,
                selectedIndex = selectedIndex,
                correctIndex = correctIndex,
                quality = if (flashcard.isReview == true) quality else null,
                reviewId = flashcard.reviewId
            )
            
            result.fold(
                onSuccess = { response ->
                    _uiState.value = VocabularyUiState.Flashcard(
                        flashcard = flashcard,
                        answerResult = response
                    )
                    // Reload stats after answer
                    loadReviewStats()
                },
                onFailure = { exception ->
                    // Show result anyway with basic feedback
                    _uiState.value = VocabularyUiState.Flashcard(
                        flashcard = flashcard,
                        answerResult = VocabularyAnswerResponse(
                            isCorrect = isCorrect,
                            correctOptionIndex = correctIndex,
                            explanation = null
                        )
                    )
                }
            )
        }
    }

    /**
     * Load SRS review statistics.
     */
    fun loadReviewStats() {
        viewModelScope.launch {
            val result = learningRepository.getReviewStats()
            result.onSuccess { stats ->
                _reviewStats.value = stats
            }
        }
    }
}
