package com.fluencia.app.data.model

import com.google.gson.annotations.SerializedName

/**
 * Model representing an achievement.
 *
 * @property id Unique identifier for the achievement
 * @property name Name of the achievement
 * @property description Description of how to unlock the achievement
 * @property icon Emoji icon for the achievement
 * @property tier Achievement tier (bronze, silver, gold, etc.)
 * @property xpReward XP reward for unlocking the achievement
 * @property unlockedAt Timestamp when the achievement was unlocked (null if locked)
 * @property isNew Whether this achievement was recently unlocked and unviewed
 * @property progress Progress percentage towards unlocking (0-100, for locked achievements)
 */
data class Achievement(
    @SerializedName("id")
    val id: String,
    
    @SerializedName("name")
    val name: String,
    
    @SerializedName("description")
    val description: String,
    
    @SerializedName("icon")
    val icon: String? = null,
    
    @SerializedName("tier")
    val tier: String,
    
    @SerializedName("xp_reward")
    val xpReward: Int,
    
    @SerializedName("unlocked_at")
    val unlockedAt: String? = null,
    
    @SerializedName("is_new")
    val isNew: Boolean = false,
    
    @SerializedName("progress")
    val progress: Int = 0
)

/**
 * Response model for achievements list endpoint.
 *
 * @property unlocked List of unlocked achievements
 * @property locked List of locked achievements with progress
 * @property newCount Number of unviewed newly unlocked achievements
 */
data class AchievementsResponse(
    @SerializedName("unlocked")
    val unlocked: List<Achievement>,
    
    @SerializedName("locked")
    val locked: List<Achievement>,
    
    @SerializedName("new_count")
    val newCount: Int
)

/**
 * Response model for marking achievements as viewed.
 *
 * @property success Whether the operation was successful
 * @property message Status message
 */
data class MarkViewedResponse(
    @SerializedName("success")
    val success: Boolean,
    
    @SerializedName("message")
    val message: String
)
