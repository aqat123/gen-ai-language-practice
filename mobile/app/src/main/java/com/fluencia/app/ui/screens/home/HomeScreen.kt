package com.fluencia.app.ui.screens.home

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.Logout
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.fluencia.app.ui.components.LevelBadge
import com.fluencia.app.ui.components.LevelBadgeSize
import com.fluencia.app.ui.components.ModuleCard
import com.fluencia.app.ui.components.ThemeToggleButton
import com.fluencia.app.ui.theme.*

/**
 * Home screen with module selection.
 *
 * Displays the user's profile information, learning modules, and navigation
 * to progress tracking. Includes a dark mode toggle button in the app bar.
 *
 * @param onNavigateToVocabulary Navigate to vocabulary module
 * @param onNavigateToGrammar Navigate to grammar module
 * @param onNavigateToWriting Navigate to writing module
 * @param onNavigateToPhonetics Navigate to phonetics module
 * @param onNavigateToConversation Navigate to conversation module
 * @param onNavigateToProgress Navigate to progress screen
 * @param onNavigateToAchievements Navigate to achievements screen
 * @param onLogout Handle logout
 * @param isDarkTheme Whether the app is currently in dark theme mode
 * @param onToggleTheme Callback to toggle between light and dark themes
 * @param viewModel The home ViewModel
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    onNavigateToVocabulary: () -> Unit,
    onNavigateToGrammar: () -> Unit,
    onNavigateToWriting: () -> Unit,
    onNavigateToPhonetics: () -> Unit,
    onNavigateToConversation: () -> Unit,
    onNavigateToProgress: () -> Unit,
    onNavigateToAchievements: () -> Unit,
    onLogout: () -> Unit,
    isDarkTheme: Boolean = false,
    onToggleTheme: () -> Unit = {},
    viewModel: HomeViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    var showLogoutDialog by remember { mutableStateOf(false) }
    
    LaunchedEffect(Unit) {
        viewModel.loadUserData()
    }
    
    if (showLogoutDialog) {
        AlertDialog(
            onDismissRequest = { showLogoutDialog = false },
            title = { Text("Logout") },
            text = { Text("Are you sure you want to logout?") },
            confirmButton = {
                TextButton(
                    onClick = {
                        showLogoutDialog = false
                        viewModel.logout(onLogout)
                    }
                ) {
                    Text("Logout")
                }
            },
            dismissButton = {
                TextButton(onClick = { showLogoutDialog = false }) {
                    Text("Cancel")
                }
            }
        )
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(
                            text = "🎓",
                            fontSize = 28.sp
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = "FluencIA",
                            fontWeight = FontWeight.Bold
                        )
                    }
                },
                actions = {
                    // Dark mode toggle button
                    ThemeToggleButton(
                        isDarkTheme = isDarkTheme,
                        onToggleTheme = onToggleTheme
                    )
                    // Achievements button
                    IconButton(onClick = onNavigateToAchievements) {
                        Icon(
                            imageVector = Icons.Default.EmojiEvents,
                            contentDescription = "Achievements",
                            tint = FluenciaPrimary
                        )
                    }
                    // Logout button
                    IconButton(onClick = { showLogoutDialog = true }) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.Logout,
                            contentDescription = "Logout"
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.surface
                )
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .verticalScroll(rememberScrollState())
                .padding(16.dp)
        ) {
            // User Info Card
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.surface
                )
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    LevelBadge(
                        level = uiState.level ?: "?",
                        size = LevelBadgeSize.MEDIUM
                    )
                    
                    Spacer(modifier = Modifier.width(16.dp))
                    
                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            text = uiState.username ?: "User",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.SemiBold
                        )
                        Text(
                            text = "Learning ${uiState.targetLanguage ?: "..."}",
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(24.dp))
            
            Text(
                text = "Choose a Module",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Module Cards
            ModuleCard(
                title = "Vocabulary",
                description = "Learn new words with flashcards",
                icon = "📚",
                color = VocabularyColor,
                onClick = onNavigateToVocabulary
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            ModuleCard(
                title = "Grammar",
                description = "Practice grammar rules",
                icon = "📖",
                color = GrammarColor,
                onClick = onNavigateToGrammar
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            ModuleCard(
                title = "Writing",
                description = "Get feedback on your writing",
                icon = "✍️",
                color = WritingColor,
                onClick = onNavigateToWriting
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            ModuleCard(
                title = "Pronunciation",
                description = "Practice speaking with AI feedback",
                icon = "🎤",
                color = PhoneticsColor,
                onClick = onNavigateToPhonetics
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            ModuleCard(
                title = "Conversation",
                description = "Chat with AI tutor",
                icon = "💬",
                color = ConversationColor,
                onClick = onNavigateToConversation
            )
            
            Spacer(modifier = Modifier.height(24.dp))
            
            // Progress Button
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable { onNavigateToProgress() },
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(
                    containerColor = FluenciaPrimary.copy(alpha = 0.1f)
                )
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.Center
                ) {
                    Icon(
                        imageVector = Icons.Default.Analytics,
                        contentDescription = null,
                        tint = FluenciaPrimary
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "My Progress",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.SemiBold,
                        color = FluenciaPrimary
                    )
                }
            }
        }
    }
}
