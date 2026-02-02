package com.fluencia.app.ui.screens.conversation

import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.fluencia.app.data.repository.LearningRepository
import com.fluencia.app.ui.navigation.NavArgs
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * UI state for the conversation screen.
 */
sealed class ConversationUiState {
    /** Idle state */
    object Idle : ConversationUiState()
    
    /** Loading state (starting conversation) */
    object Loading : ConversationUiState()
    
    /** Conversation started state */
    data class Started(val sessionId: String) : ConversationUiState()
    
    /** Active conversation state */
    object Active : ConversationUiState()
    
    /** Sending message state */
    object Sending : ConversationUiState()
    
    /** Error state */
    data class Error(val message: String) : ConversationUiState()
}

/**
 * ViewModel for the conversation screens.
 *
 * Manages conversation practice including starting conversations and sending messages.
 *
 * @property learningRepository Repository for learning operations
 * @property savedStateHandle Handle for navigation arguments
 */
@HiltViewModel
class ConversationViewModel @Inject constructor(
    private val learningRepository: LearningRepository,
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    private val _uiState = MutableStateFlow<ConversationUiState>(ConversationUiState.Idle)
    
    /** Current UI state */
    val uiState: StateFlow<ConversationUiState> = _uiState.asStateFlow()
    
    private val _messages = MutableStateFlow<List<ChatMessage>>(emptyList())
    
    /** Conversation messages */
    val messages: StateFlow<List<ChatMessage>> = _messages.asStateFlow()
    
    private var currentSessionId: String? = null

    init {
        // Check if we're joining an existing conversation
        val sessionId = savedStateHandle.get<String>(NavArgs.SESSION_ID)
        if (sessionId != null) {
            currentSessionId = sessionId
            _uiState.value = ConversationUiState.Active
        }
    }

    /**
     * Start a new conversation with optional topic.
     *
     * @param topic Optional conversation topic
     */
    fun startConversation(topic: String?) {
        viewModelScope.launch {
            _uiState.value = ConversationUiState.Loading
            _messages.value = emptyList()
            
            val result = learningRepository.startConversation(topic)
            
            result.fold(
                onSuccess = { response ->
                    currentSessionId = response.sessionId
                    _messages.value = listOf(
                        ChatMessage(
                            text = response.openingMessage,
                            isUser = false
                        )
                    )
                    _uiState.value = ConversationUiState.Started(response.sessionId)
                },
                onFailure = { exception ->
                    _uiState.value = ConversationUiState.Error(
                        exception.message ?: "Failed to start conversation"
                    )
                }
            )
        }
    }

    /**
     * Send a message in the current conversation.
     *
     * @param message The message text
     */
    fun sendMessage(message: String) {
        val sessionId = currentSessionId ?: return
        if (message.isBlank()) return
        
        // Add user message immediately
        _messages.value = _messages.value + ChatMessage(
            text = message,
            isUser = true
        )
        
        viewModelScope.launch {
            _uiState.value = ConversationUiState.Sending
            
            val result = learningRepository.sendConversationMessage(sessionId, message)
            
            result.fold(
                onSuccess = { response ->
                    // Add AI reply
                    _messages.value = _messages.value + ChatMessage(
                        text = response.reply,
                        isUser = false
                    )
                    
                    // Add correction feedback if present
                    val hasCorrection = !response.correctedUserMessage.isNullOrEmpty() &&
                            response.correctedUserMessage != message &&
                            response.correctedUserMessage != "null"
                    val hasTip = !response.tips.isNullOrEmpty() && response.tips != "null"
                    
                    if (hasCorrection || hasTip) {
                        // Update the user's last message with correction
                        val updatedMessages = _messages.value.toMutableList()
                        val lastUserIndex = updatedMessages.indexOfLast { it.isUser }
                        if (lastUserIndex >= 0) {
                            updatedMessages[lastUserIndex] = updatedMessages[lastUserIndex].copy(
                                correction = if (hasCorrection) response.correctedUserMessage else null,
                                tip = if (hasTip) response.tips else null
                            )
                            _messages.value = updatedMessages
                        }
                    }
                    
                    _uiState.value = ConversationUiState.Active
                },
                onFailure = { exception ->
                    // Remove the user message on error
                    _messages.value = _messages.value.dropLast(1)
                    _uiState.value = ConversationUiState.Error(
                        exception.message ?: "Failed to send message"
                    )
                }
            )
        }
    }
}
