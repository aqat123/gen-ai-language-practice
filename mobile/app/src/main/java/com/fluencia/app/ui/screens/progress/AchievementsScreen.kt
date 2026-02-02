package com.fluencia.app.ui.screens.progress

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.fluencia.app.data.model.Achievement
import com.fluencia.app.ui.components.*
import com.fluencia.app.ui.theme.*

/**
 * Achievements screen displaying user's earned and locked achievements.
 *
 * @param onBack Navigate back
 * @param viewModel The achievements ViewModel
 */
@Composable
fun AchievementsScreen(
    onBack: () -> Unit,
    viewModel: AchievementsViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    var selectedTab by remember { mutableStateOf(0) }
    
    LaunchedEffect(Unit) {
        viewModel.loadAchievements()
    }
    
    Scaffold(
        topBar = {
            FluenciaTopBar(
                title = "Achievements",
                onBackClick = onBack
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            when (val state = uiState) {
                is AchievementsUiState.Loading -> {
                    LoadingOverlay(message = "Loading achievements...")
                }
                
                is AchievementsUiState.Error -> {
                    ErrorMessage(
                        message = state.message,
                        onRetry = { viewModel.loadAchievements() }
                    )
                }
                
                is AchievementsUiState.Success -> {
                    // Tab Row
                    TabRow(selectedTabIndex = selectedTab) {
                        Tab(
                            selected = selectedTab == 0,
                            onClick = { selectedTab = 0 },
                            text = {
                                Text("Unlocked (${state.unlocked.size})")
                            }
                        )
                        Tab(
                            selected = selectedTab == 1,
                            onClick = { selectedTab = 1 },
                            text = {
                                Text("In Progress (${state.locked.size})")
                            }
                        )
                    }
                    
                    // Content
                    when (selectedTab) {
                        0 -> AchievementsList(
                            achievements = state.unlocked,
                            isUnlocked = true
                        )
                        1 -> AchievementsList(
                            achievements = state.locked,
                            isUnlocked = false
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun AchievementsList(
    achievements: List<Achievement>,
    isUnlocked: Boolean
) {
    if (achievements.isEmpty()) {
        Box(
            modifier = Modifier.fillMaxSize(),
            contentAlignment = Alignment.Center
        ) {
            Text(
                text = if (isUnlocked) {
                    "Complete activities to unlock achievements!"
                } else {
                    "All achievements unlocked! 🎉"
                },
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                textAlign = TextAlign.Center
            )
        }
    } else {
        LazyColumn(
            modifier = Modifier.fillMaxSize(),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            items(achievements) { achievement ->
                AchievementCard(
                    achievement = achievement,
                    isUnlocked = isUnlocked
                )
            }
        }
    }
}

@Composable
private fun AchievementCard(
    achievement: Achievement,
    isUnlocked: Boolean
) {
    val tierColor = when (achievement.tier.lowercase()) {
        "bronze" -> TierBronze
        "silver" -> TierSilver
        "gold" -> TierGold
        "platinum" -> TierPlatinum
        "diamond" -> TierDiamond
        else -> FluenciaPrimary
    }
    
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = if (isUnlocked) {
                MaterialTheme.colorScheme.surface
            } else {
                MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f)
            }
        )
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Icon
                Box(
                    modifier = Modifier
                        .size(48.dp)
                        .clip(RoundedCornerShape(12.dp))
                        .background(tierColor.copy(alpha = 0.2f)),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = achievement.icon ?: "🏆",
                        fontSize = 24.sp
                    )
                }
                
                Spacer(modifier = Modifier.width(12.dp))
                
                Column(modifier = Modifier.weight(1f)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(
                            text = achievement.name,
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.SemiBold
                        )
                        
                        if (achievement.isNew) {
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(
                                text = "NEW",
                                style = MaterialTheme.typography.labelSmall,
                                color = Color.White,
                                modifier = Modifier
                                    .clip(RoundedCornerShape(4.dp))
                                    .background(ErrorRed)
                                    .padding(horizontal = 6.dp, vertical = 2.dp)
                            )
                        }
                    }
                    
                    Text(
                        text = achievement.description,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                
                // Tier badge
                Text(
                    text = achievement.tier.uppercase(),
                    style = MaterialTheme.typography.labelSmall,
                    color = tierColor,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier
                        .clip(RoundedCornerShape(4.dp))
                        .background(tierColor.copy(alpha = 0.1f))
                        .padding(horizontal = 8.dp, vertical = 4.dp)
                )
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "+${achievement.xpReward} XP",
                    style = MaterialTheme.typography.labelLarge,
                    color = FluenciaPrimary,
                    fontWeight = FontWeight.Bold
                )
                
                if (!isUnlocked) {
                    // Progress bar for locked achievements
                    Row(
                        modifier = Modifier.width(120.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        LinearProgressIndicator(
                            progress = achievement.progress / 100f,
                            modifier = Modifier
                                .weight(1f)
                                .height(6.dp)
                                .clip(RoundedCornerShape(3.dp)),
                            color = tierColor
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = "${achievement.progress}%",
                            style = MaterialTheme.typography.labelSmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                } else if (achievement.unlockedAt != null) {
                    Text(
                        text = "Unlocked",
                        style = MaterialTheme.typography.labelSmall,
                        color = SuccessGreen
                    )
                }
            }
        }
    }
}
