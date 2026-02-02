package com.fluencia.app.data.model

import com.google.gson.annotations.SerializedName

/**
 * Request model for starting a conversation.
 *
 * @property topic The conversation topic (optional, null for random)
 */
data class ConversationStartRequest(
    @SerializedName("topic")
    val topic: String? = null
)

/**
 * Response model for starting a conversation.
 *
 * @property sessionId Unique identifier for the conversation session
 * @property openingMessage The AI's opening message
 */
data class ConversationStartResponse(
    @SerializedName("session_id")
    val sessionId: String,
    
    @SerializedName("opening_message")
    val openingMessage: String
)

/**
 * Request model for sending a message in a conversation.
 *
 * @property message The user's message text
 */
data class ConversationMessageRequest(
    @SerializedName("message")
    val message: String
)

/**
 * Response model for a conversation message.
 *
 * @property reply The AI's reply message
 * @property correctedUserMessage Corrected version of user's message (if applicable)
 * @property tips Learning tips based on the user's message
 * @property sessionId The conversation session identifier
 */
data class ConversationMessageResponse(
    @SerializedName("reply")
    val reply: String,
    
    @SerializedName("corrected_user_message")
    val correctedUserMessage: String? = null,
    
    @SerializedName("tips")
    val tips: String? = null,
    
    @SerializedName("session_id")
    val sessionId: String
)

/**
 * Enum representing available conversation topics.
 */
enum class ConversationTopic(val value: String, val displayName: String, val emoji: String) {
    RANDOM("random", "Random Topic", "🎲"),
    TRAVEL("travel", "Travel", "✈️"),
    FOOD("food", "Food & Dining", "🍽️"),
    HOBBIES("hobbies", "Hobbies", "🎨"),
    WORK("work", "Work & Career", "💼"),
    CULTURE("culture", "Culture", "🎭"),
    DAILY_LIFE("daily_life", "Daily Life", "🏠"),
    EDUCATION("education", "Education", "📚")
}
