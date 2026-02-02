package com.fluencia.app.ui.screens.grammar

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.fluencia.app.data.model.GrammarAnswerResponse
import com.fluencia.app.data.model.GrammarQuestionResponse
import com.fluencia.app.data.repository.LearningRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * UI state for the grammar screen.
 */
sealed class GrammarUiState {
    /** Loading state */
    object Loading : GrammarUiState()
    
    /** Question display state */
    data class Question(
        val question: GrammarQuestionResponse,
        val answerResult: GrammarAnswerResponse? = null
    ) : GrammarUiState()
    
    /** Error state */
    data class Error(val message: String) : GrammarUiState()
}

/**
 * ViewModel for the grammar screen.
 *
 * Manages grammar practice including loading questions and submitting answers.
 *
 * @property learningRepository Repository for learning operations
 */
@HiltViewModel
class GrammarViewModel @Inject constructor(
    private val learningRepository: LearningRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<GrammarUiState>(GrammarUiState.Loading)
    
    /** Current UI state */
    val uiState: StateFlow<GrammarUiState> = _uiState.asStateFlow()
    
    private var currentQuestion: GrammarQuestionResponse? = null

    /**
     * Load the next grammar question.
     *
     * @param topic Optional topic filter
     */
    fun loadNextQuestion(topic: String? = "general") {
        viewModelScope.launch {
            _uiState.value = GrammarUiState.Loading
            
            val result = learningRepository.getGrammarQuestion(topic)
            
            result.fold(
                onSuccess = { question ->
                    currentQuestion = question
                    _uiState.value = GrammarUiState.Question(question)
                },
                onFailure = { exception ->
                    _uiState.value = GrammarUiState.Error(
                        exception.message ?: "Failed to load question"
                    )
                }
            )
        }
    }

    /**
     * Submit an answer to the current question.
     *
     * @param selectedIndex Index of the selected option
     */
    fun submitAnswer(selectedIndex: Int) {
        val question = currentQuestion ?: return
        
        viewModelScope.launch {
            val result = learningRepository.submitGrammarAnswer(
                questionId = question.questionId,
                selectedIndex = selectedIndex,
                correctIndex = question.correctOptionIndex,
                explanation = question.explanation
            )
            
            result.fold(
                onSuccess = { response ->
                    _uiState.value = GrammarUiState.Question(
                        question = question,
                        answerResult = response
                    )
                },
                onFailure = {
                    // Show result with pre-loaded explanation
                    _uiState.value = GrammarUiState.Question(
                        question = question,
                        answerResult = GrammarAnswerResponse(
                            isCorrect = selectedIndex == question.correctOptionIndex,
                            correctOptionIndex = question.correctOptionIndex,
                            explanation = question.explanation ?: "Check the correct answer above."
                        )
                    )
                }
            )
        }
    }
}
