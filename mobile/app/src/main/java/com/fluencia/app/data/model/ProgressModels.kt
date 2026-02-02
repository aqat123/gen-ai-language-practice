package com.fluencia.app.data.model

import com.google.gson.annotations.SerializedName

/**
 * Model representing progress in a single learning module.
 *
 * @property module Name of the learning module
 * @property score Current score percentage
 * @property totalAttempts Total number of attempts
 * @property correctAttempts Number of correct attempts
 * @property lastActivity Timestamp of last activity
 * @property meetsThreshold Whether score meets 85% threshold
 * @property meetsMinimumAttempts Whether minimum 10 attempts reached
 */
data class ModuleProgress(
    @SerializedName("module")
    val module: String,
    
    @SerializedName("score")
    val score: Float? = null,
    
    @SerializedName("total_attempts")
    val totalAttempts: Int,
    
    @SerializedName("correct_attempts")
    val correctAttempts: Int,
    
    @SerializedName("last_activity")
    val lastActivity: String? = null,
    
    @SerializedName("meets_threshold")
    val meetsThreshold: Boolean,
    
    @SerializedName("meets_minimum_attempts")
    val meetsMinimumAttempts: Boolean
)

/**
 * Model representing conversation engagement statistics.
 *
 * @property totalMessages Total number of conversation messages sent
 * @property meetsThreshold Whether minimum 20 messages reached
 */
data class ConversationEngagement(
    @SerializedName("total_messages")
    val totalMessages: Int,
    
    @SerializedName("meets_threshold")
    val meetsThreshold: Boolean
)

/**
 * Response model for the progress summary endpoint.
 *
 * @property currentLevel User's current CEFR level
 * @property nextLevel The next level to advance to
 * @property canAdvance Whether user is eligible to advance
 * @property advancementReason Reason if not eligible to advance
 * @property overallProgress Overall progress percentage (0-100)
 * @property weightedScore Weighted score across all modules
 * @property modules Progress data for each module
 * @property conversationEngagement Conversation engagement statistics
 * @property timeAtCurrentLevel Days spent at current level
 * @property totalXp Total XP earned
 */
data class ProgressSummaryResponse(
    @SerializedName("current_level")
    val currentLevel: String,
    
    @SerializedName("next_level")
    val nextLevel: String? = null,
    
    @SerializedName("can_advance")
    val canAdvance: Boolean,
    
    @SerializedName("advancement_reason")
    val advancementReason: String? = null,
    
    @SerializedName("overall_progress")
    val overallProgress: Float,
    
    @SerializedName("weighted_score")
    val weightedScore: Float,
    
    @SerializedName("modules")
    val modules: List<ModuleProgress>,
    
    @SerializedName("conversation_engagement")
    val conversationEngagement: ConversationEngagement,
    
    @SerializedName("time_at_current_level")
    val timeAtCurrentLevel: Int,
    
    @SerializedName("total_xp")
    val totalXp: Int
)

/**
 * Response model for a successful level advancement.
 *
 * @property success Whether advancement was successful
 * @property newLevel The new CEFR level
 * @property oldLevel The previous CEFR level
 * @property xpEarned XP earned from advancement
 * @property celebrationMessage Congratulatory message
 * @property moduleScores Final scores for each module
 */
data class AdvancementResponse(
    @SerializedName("success")
    val success: Boolean,
    
    @SerializedName("new_level")
    val newLevel: String,
    
    @SerializedName("old_level")
    val oldLevel: String,
    
    @SerializedName("xp_earned")
    val xpEarned: Int,
    
    @SerializedName("celebration_message")
    val celebrationMessage: String,
    
    @SerializedName("module_scores")
    val moduleScores: Map<String, Float?>
)

/**
 * Model representing a level in the user's history.
 *
 * @property level The CEFR level
 * @property startedAt Timestamp when level was started
 * @property completedAt Timestamp when level was completed
 * @property daysAtLevel Number of days spent at this level
 * @property weightedScore Weighted score when level was completed
 * @property scores Module scores when level was completed
 */
data class LevelHistoryItem(
    @SerializedName("level")
    val level: String,
    
    @SerializedName("started_at")
    val startedAt: String,
    
    @SerializedName("completed_at")
    val completedAt: String,
    
    @SerializedName("days_at_level")
    val daysAtLevel: Int,
    
    @SerializedName("weighted_score")
    val weightedScore: Float,
    
    @SerializedName("scores")
    val scores: Map<String, Float?>
)

/**
 * Request model for applying a cheat code (demo mode).
 *
 * @property code The cheat code string
 */
data class CheatCodeRequest(
    @SerializedName("code")
    val code: String
)

/**
 * Response model for cheat code application.
 *
 * @property success Whether the code was successfully applied
 * @property message Status message
 * @property modulesUpdated List of modules that were updated
 * @property conversationMessages Number of conversation messages added
 */
data class CheatCodeResponse(
    @SerializedName("success")
    val success: Boolean,
    
    @SerializedName("message")
    val message: String,
    
    @SerializedName("modules_updated")
    val modulesUpdated: List<String>,
    
    @SerializedName("conversation_messages")
    val conversationMessages: Int
)

/**
 * Model representing activity data over time for charts.
 *
 * @property dates List of date strings
 * @property vocabulary Activity count for vocabulary
 * @property grammar Activity count for grammar
 * @property writing Activity count for writing
 * @property phonetics Activity count for phonetics
 * @property conversation Activity count for conversation
 */
data class ActivityOverTime(
    @SerializedName("dates")
    val dates: List<String>,
    
    @SerializedName("vocabulary")
    val vocabulary: List<Int>,
    
    @SerializedName("grammar")
    val grammar: List<Int>,
    
    @SerializedName("writing")
    val writing: List<Int>,
    
    @SerializedName("phonetics")
    val phonetics: List<Int>,
    
    @SerializedName("conversation")
    val conversation: List<Int>
)

/**
 * Model representing module scores for charts.
 *
 * @property modules List of module names
 * @property scores List of score values
 */
data class ModuleScores(
    @SerializedName("modules")
    val modules: List<String>,
    
    @SerializedName("scores")
    val scores: List<Float>
)

/**
 * Model representing level progression for charts.
 *
 * @property levels List of level names
 * @property scores List of scores at each level
 * @property dates List of dates for each level
 */
data class LevelProgression(
    @SerializedName("levels")
    val levels: List<String>,
    
    @SerializedName("scores")
    val scores: List<Float>,
    
    @SerializedName("dates")
    val dates: List<String>
)

/**
 * Response model for progress charts data.
 *
 * @property activityOverTime Activity data over time
 * @property moduleScores Current scores per module
 * @property levelProgression Level progression history
 */
data class ChartsDataResponse(
    @SerializedName("activity_over_time")
    val activityOverTime: ActivityOverTime,
    
    @SerializedName("module_scores")
    val moduleScores: ModuleScores,
    
    @SerializedName("level_progression")
    val levelProgression: LevelProgression
)

/**
 * Response model for module detail data.
 *
 * @property module Name of the module
 * @property currentScore Current score percentage
 * @property totalAttempts Total number of attempts
 * @property correctAttempts Number of correct attempts
 * @property lastActivity Timestamp of last activity
 */
data class ModuleDetailResponse(
    @SerializedName("module")
    val module: String,
    
    @SerializedName("current_score")
    val currentScore: Float? = null,
    
    @SerializedName("total_attempts")
    val totalAttempts: Int,
    
    @SerializedName("correct_attempts")
    val correctAttempts: Int,
    
    @SerializedName("last_activity")
    val lastActivity: String? = null
)
