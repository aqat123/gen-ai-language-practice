package com.fluencia.app.ui.screens.writing

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.fluencia.app.data.model.WritingPrompt
import com.fluencia.app.data.repository.LearningRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * UI state for the writing screen.
 */
sealed class WritingUiState {
    /** Loading prompts */
    object LoadingPrompts : WritingUiState()
    
    /** Prompt selection state */
    data class PromptSelection(val prompts: List<WritingPrompt>) : WritingUiState()
    
    /** Writing state */
    data class Writing(val selectedPrompt: WritingPrompt?) : WritingUiState()
    
    /** Loading feedback */
    object Loading : WritingUiState()
    
    /** Feedback state */
    data class Feedback(
        val correctedText: String,
        val overallComment: String,
        val inlineExplanation: String?,
        val score: Float?
    ) : WritingUiState()
    
    /** Error state */
    data class Error(val message: String) : WritingUiState()
}

/**
 * ViewModel for the writing screen.
 *
 * Manages writing practice including loading prompts and getting feedback.
 *
 * @property learningRepository Repository for learning operations
 */
@HiltViewModel
class WritingViewModel @Inject constructor(
    private val learningRepository: LearningRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<WritingUiState>(WritingUiState.LoadingPrompts)
    
    /** Current UI state */
    val uiState: StateFlow<WritingUiState> = _uiState.asStateFlow()

    /**
     * Load available writing prompts.
     */
    fun loadPrompts() {
        viewModelScope.launch {
            _uiState.value = WritingUiState.LoadingPrompts
            
            val result = learningRepository.getWritingPrompts()
            
            result.fold(
                onSuccess = { prompts ->
                    _uiState.value = WritingUiState.PromptSelection(prompts)
                },
                onFailure = {
                    // Use fallback prompts
                    _uiState.value = WritingUiState.PromptSelection(fallbackPrompts)
                }
            )
        }
    }

    /**
     * Select a writing prompt.
     *
     * @param prompt The selected prompt
     */
    fun selectPrompt(prompt: WritingPrompt) {
        _uiState.value = WritingUiState.Writing(prompt)
    }

    /**
     * Start free-form writing without a prompt.
     */
    fun selectFreeForm() {
        _uiState.value = WritingUiState.Writing(null)
    }

    /**
     * Submit writing for feedback.
     *
     * @param text The user's written text
     */
    fun submitWriting(text: String) {
        if (text.isBlank()) return
        
        viewModelScope.launch {
            _uiState.value = WritingUiState.Loading
            
            val result = learningRepository.submitWritingFeedback(text)
            
            result.fold(
                onSuccess = { response ->
                    _uiState.value = WritingUiState.Feedback(
                        correctedText = response.correctedText,
                        overallComment = response.overallComment,
                        inlineExplanation = response.inlineExplanation,
                        score = response.score
                    )
                },
                onFailure = { exception ->
                    _uiState.value = WritingUiState.Error(
                        exception.message ?: "Failed to get feedback"
                    )
                }
            )
        }
    }

    companion object {
        private val fallbackPrompts = listOf(
            WritingPrompt("My Daily Routine", "Describe your typical day. What time do you wake up? What do you eat for breakfast? What do you do in the evening?"),
            WritingPrompt("My Family", "Write about your family. Who are the members of your family? What do they do? What do they look like?"),
            WritingPrompt("My Favorite Food", "What is your favorite food? Describe it. Why do you like it? When do you usually eat it?"),
            WritingPrompt("A Memorable Trip", "Write about a trip you took. Where did you go? What did you see? What was the most interesting thing you did?"),
            WritingPrompt("My Hobbies", "What do you like to do in your free time? Do you have any hobbies? How often do you do them?"),
            WritingPrompt("My Hometown", "Describe your hometown or city. What is it famous for? What do you like or dislike about it?"),
            WritingPrompt("Learning Languages", "Why are you learning this language? What do you find easy or difficult? How do you practice?"),
            WritingPrompt("My Goals", "What are your goals for the future? What do you want to achieve? How will you get there?")
        )
    }
}
