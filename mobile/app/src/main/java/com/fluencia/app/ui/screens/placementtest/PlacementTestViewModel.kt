package com.fluencia.app.ui.screens.placementtest

import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.fluencia.app.data.model.PlacementTestQuestion
import com.fluencia.app.data.model.PlacementTestResultResponse
import com.fluencia.app.data.repository.AuthRepository
import com.fluencia.app.data.repository.NoMoreQuestionsException
import com.fluencia.app.data.repository.PlacementTestRepository
import com.fluencia.app.ui.navigation.NavArgs
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * UI state for the placement test screen.
 */
sealed class PlacementTestUiState {
    /** Loading state */
    object Loading : PlacementTestUiState()
    
    /** Question display state */
    data class Question(
        val question: PlacementTestQuestion,
        val currentQuestion: Int,
        val totalQuestions: Int
    ) : PlacementTestUiState()
    
    /** Test completed state */
    data class Completed(val testId: String) : PlacementTestUiState()
    
    /** Error state */
    data class Error(val message: String) : PlacementTestUiState()
}

/**
 * ViewModel for the placement test screens.
 *
 * Manages the placement test flow including starting, answering questions,
 * and completing the test.
 *
 * @property placementTestRepository Repository for placement test operations
 * @property authRepository Repository for user data
 * @property savedStateHandle Handle for navigation arguments
 */
@HiltViewModel
class PlacementTestViewModel @Inject constructor(
    private val placementTestRepository: PlacementTestRepository,
    private val authRepository: AuthRepository,
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    private val _uiState = MutableStateFlow<PlacementTestUiState>(PlacementTestUiState.Loading)
    
    /** Current UI state */
    val uiState: StateFlow<PlacementTestUiState> = _uiState.asStateFlow()
    
    private val _results = MutableStateFlow<PlacementTestResultResponse?>(null)
    
    /** Test results (populated when viewing results) */
    val results: StateFlow<PlacementTestResultResponse?> = _results.asStateFlow()
    
    private var currentTestId: String? = null

    init {
        // Check if we're viewing results
        val testId = savedStateHandle.get<String>(NavArgs.TEST_ID)
        if (testId != null) {
            loadResults(testId)
        }
    }

    /**
     * Start a new placement test.
     */
    fun startTest() {
        viewModelScope.launch {
            _uiState.value = PlacementTestUiState.Loading
            
            val language = authRepository.getTargetLanguage().first()
            if (language.isNullOrEmpty()) {
                _uiState.value = PlacementTestUiState.Error("Please select a language first")
                return@launch
            }
            
            val startResult = placementTestRepository.startTest(language)
            
            startResult.fold(
                onSuccess = { response ->
                    currentTestId = response.testId
                    loadNextQuestion()
                },
                onFailure = { exception ->
                    _uiState.value = PlacementTestUiState.Error(
                        exception.message ?: "Failed to start test"
                    )
                }
            )
        }
    }

    /**
     * Load the next question.
     */
    private suspend fun loadNextQuestion() {
        val testId = currentTestId ?: return
        
        val questionResult = placementTestRepository.getQuestion(testId)
        
        questionResult.fold(
            onSuccess = { response ->
                _uiState.value = PlacementTestUiState.Question(
                    question = response.question,
                    currentQuestion = response.currentQuestionNumber,
                    totalQuestions = response.totalQuestions
                )
            },
            onFailure = { exception ->
                if (exception is NoMoreQuestionsException) {
                    completeTest()
                } else {
                    _uiState.value = PlacementTestUiState.Error(
                        exception.message ?: "Failed to load question"
                    )
                }
            }
        )
    }

    /**
     * Submit an answer to the current question.
     *
     * @param selectedOption Index of the selected answer
     */
    fun submitAnswer(selectedOption: Int) {
        val currentState = _uiState.value
        if (currentState !is PlacementTestUiState.Question) return
        
        viewModelScope.launch {
            val testId = currentTestId ?: return@launch
            
            _uiState.value = PlacementTestUiState.Loading
            
            val answerResult = placementTestRepository.submitAnswer(
                testId = testId,
                questionNumber = currentState.question.questionNumber,
                selectedOption = selectedOption
            )
            
            answerResult.fold(
                onSuccess = { response ->
                    if (response.hasNext) {
                        loadNextQuestion()
                    } else {
                        completeTest()
                    }
                },
                onFailure = { exception ->
                    _uiState.value = PlacementTestUiState.Error(
                        exception.message ?: "Failed to submit answer"
                    )
                }
            )
        }
    }

    /**
     * Complete the test and get results.
     */
    private suspend fun completeTest() {
        val testId = currentTestId ?: return
        
        val completeResult = placementTestRepository.completeTest(testId)
        
        completeResult.fold(
            onSuccess = { response ->
                _results.value = response
                _uiState.value = PlacementTestUiState.Completed(testId)
            },
            onFailure = { exception ->
                _uiState.value = PlacementTestUiState.Error(
                    exception.message ?: "Failed to complete test"
                )
            }
        )
    }

    /**
     * Load results for a completed test.
     */
    private fun loadResults(testId: String) {
        viewModelScope.launch {
            val completeResult = placementTestRepository.completeTest(testId)
            completeResult.onSuccess { response ->
                _results.value = response
            }
        }
    }
}
