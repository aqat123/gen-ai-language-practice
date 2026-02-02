package com.fluencia.app.ui.screens.progress

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowUpward
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.fluencia.app.ui.components.*
import com.fluencia.app.ui.theme.*

/**
 * Progress dashboard screen.
 *
 * @param onBack Navigate back
 * @param viewModel The progress ViewModel
 */
@Composable
fun ProgressScreen(
    onBack: () -> Unit,
    viewModel: ProgressViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    var showAdvancementDialog by remember { mutableStateOf(false) }
    
    LaunchedEffect(Unit) {
        viewModel.loadProgress()
    }
    
    if (showAdvancementDialog) {
        AlertDialog(
            onDismissRequest = { showAdvancementDialog = false },
            title = { Text("Advance to Next Level") },
            text = { Text("Are you ready to advance? Your progress will be archived and reset.") },
            confirmButton = {
                TextButton(
                    onClick = {
                        showAdvancementDialog = false
                        viewModel.advanceLevel()
                    }
                ) {
                    Text("Advance")
                }
            },
            dismissButton = {
                TextButton(onClick = { showAdvancementDialog = false }) {
                    Text("Cancel")
                }
            }
        )
    }
    
    Scaffold(
        topBar = {
            FluenciaTopBar(
                title = "My Progress",
                onBackClick = onBack
            )
        }
    ) { paddingValues ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            when (val state = uiState) {
                is ProgressUiState.Loading -> {
                    LoadingOverlay(message = "Loading progress...")
                }
                
                is ProgressUiState.Error -> {
                    ErrorMessage(
                        message = state.message,
                        onRetry = { viewModel.loadProgress() }
                    )
                }
                
                is ProgressUiState.Success -> {
                    ProgressContent(
                        state = state,
                        onAdvanceClick = { showAdvancementDialog = true }
                    )
                }
                
                is ProgressUiState.AdvancementSuccess -> {
                    CelebrationContent(
                        state = state,
                        onContinue = { viewModel.loadProgress() }
                    )
                }
            }
        }
    }
}

@Composable
private fun ProgressContent(
    state: ProgressUiState.Success,
    onAdvanceClick: () -> Unit
) {
    val summary = state.summary
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp)
    ) {
        // Header Stats
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceEvenly
        ) {
            StatCard(
                value = summary.currentLevel,
                label = "Current Level",
                color = FluenciaPrimary,
                modifier = Modifier.weight(1f)
            )
            Spacer(modifier = Modifier.width(8.dp))
            StatCard(
                value = "${summary.timeAtCurrentLevel}",
                label = "Days",
                color = InfoBlue,
                modifier = Modifier.weight(1f)
            )
            Spacer(modifier = Modifier.width(8.dp))
            StatCard(
                value = "${summary.totalXp}",
                label = "XP",
                color = SuccessGreen,
                modifier = Modifier.weight(1f)
            )
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Advancement Banner
        if (summary.canAdvance && summary.nextLevel != null) {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = SuccessGreen.copy(alpha = 0.1f)
                )
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            text = "Ready to advance!",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = SuccessGreen
                        )
                        Text(
                            text = "You can advance to ${summary.nextLevel}",
                            style = MaterialTheme.typography.bodyMedium
                        )
                    }
                    Button(
                        onClick = onAdvanceClick,
                        colors = ButtonDefaults.buttonColors(
                            containerColor = SuccessGreen
                        )
                    ) {
                        Icon(Icons.Default.ArrowUpward, null)
                        Spacer(modifier = Modifier.width(4.dp))
                        Text("Advance")
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(16.dp))
        }
        
        // Overall Progress
        Card(modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "Overall Progress",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold
                )
                Spacer(modifier = Modifier.height(12.dp))
                ProgressBar(
                    progress = summary.overallProgress / 100f,
                    color = FluenciaPrimary
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = summary.advancementReason ?: "Keep practicing!",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Module Progress
        Text(
            text = "Module Progress",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold
        )
        
        Spacer(modifier = Modifier.height(12.dp))
        
        summary.modules.forEach { module ->
            ModuleProgressCard(module = module)
            Spacer(modifier = Modifier.height(8.dp))
        }
        
        // Conversation Engagement
        Spacer(modifier = Modifier.height(16.dp))
        
        Card(modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(
                            text = "💬 Conversation",
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.SemiBold
                        )
                        Text(
                            text = "${summary.conversationEngagement.totalMessages}/20 messages",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                    
                    if (summary.conversationEngagement.meetsThreshold) {
                        Text(
                            text = "✓ Ready",
                            style = MaterialTheme.typography.labelMedium,
                            color = SuccessGreen,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }
                
                Spacer(modifier = Modifier.height(8.dp))
                
                ProgressBar(
                    progress = summary.conversationEngagement.totalMessages / 20f,
                    color = ConversationColor
                )
            }
        }
    }
}

@Composable
private fun ModuleProgressCard(
    module: com.fluencia.app.data.model.ModuleProgress
) {
    val color = when (module.module) {
        "vocabulary" -> VocabularyColor
        "grammar" -> GrammarColor
        "writing" -> WritingColor
        "phonetics" -> PhoneticsColor
        else -> FluenciaPrimary
    }
    
    val icon = when (module.module) {
        "vocabulary" -> "📚"
        "grammar" -> "📖"
        "writing" -> "✍️"
        "phonetics" -> "🎤"
        else -> "📊"
    }
    
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(text = icon, style = MaterialTheme.typography.titleMedium)
                    Spacer(modifier = Modifier.width(8.dp))
                    Column {
                        Text(
                            text = module.module.replaceFirstChar { it.uppercase() },
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.SemiBold
                        )
                        Text(
                            text = "${module.totalAttempts}/10 attempts • ${module.score?.toInt() ?: 0}% accuracy",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
                
                if (module.meetsThreshold && module.meetsMinimumAttempts) {
                    Text(
                        text = "✓ Ready",
                        style = MaterialTheme.typography.labelMedium,
                        color = SuccessGreen,
                        fontWeight = FontWeight.Bold
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            ProgressBar(
                progress = minOf(module.totalAttempts / 10f, 1f),
                color = color
            )
        }
    }
}

@Composable
private fun CelebrationContent(
    state: ProgressUiState.AdvancementSuccess,
    onContinue: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = "🎉",
            style = MaterialTheme.typography.displayLarge
        )
        
        Spacer(modifier = Modifier.height(24.dp))
        
        Text(
            text = "CONGRATULATIONS!",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
            color = FluenciaPrimary
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        Row(
            verticalAlignment = Alignment.CenterVertically
        ) {
            LevelBadge(level = state.oldLevel, size = LevelBadgeSize.MEDIUM)
            Text(
                text = " → ",
                style = MaterialTheme.typography.headlineMedium
            )
            LevelBadge(level = state.newLevel, size = LevelBadgeSize.LARGE)
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        Text(
            text = "+${state.xpEarned} XP",
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.Bold,
            color = SuccessGreen
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        Text(
            text = state.celebrationMessage,
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        
        Spacer(modifier = Modifier.height(32.dp))
        
        GradientButton(
            text = "Continue Learning",
            onClick = onContinue
        )
    }
}
