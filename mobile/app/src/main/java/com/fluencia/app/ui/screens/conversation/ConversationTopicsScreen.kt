package com.fluencia.app.ui.screens.conversation

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.fluencia.app.data.model.ConversationTopic
import com.fluencia.app.ui.components.*
import com.fluencia.app.ui.theme.ConversationColor

/**
 * Conversation topic selection screen.
 *
 * @param onTopicSelected Callback when conversation is started with session ID
 * @param onBack Navigate back
 * @param viewModel The conversation ViewModel
 */
@Composable
fun ConversationTopicsScreen(
    onTopicSelected: (String) -> Unit,
    onBack: () -> Unit,
    viewModel: ConversationViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    
    LaunchedEffect(uiState) {
        if (uiState is ConversationUiState.Started) {
            onTopicSelected((uiState as ConversationUiState.Started).sessionId)
        }
    }
    
    Scaffold(
        topBar = {
            FluenciaTopBar(
                title = "Conversation Practice",
                onBackClick = onBack
            )
        }
    ) { paddingValues ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            if (uiState is ConversationUiState.Loading) {
                LoadingOverlay(message = "Starting conversation...")
            } else {
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(16.dp)
                ) {
                    Text(
                        text = "Choose a Conversation Topic",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold
                    )
                    
                    Text(
                        text = "Select a topic to practice, or let the AI choose randomly",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    
                    Spacer(modifier = Modifier.height(24.dp))
                    
                    LazyVerticalGrid(
                        columns = GridCells.Fixed(2),
                        horizontalArrangement = Arrangement.spacedBy(12.dp),
                        verticalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        items(ConversationTopic.entries.toTypedArray()) { topic ->
                            TopicCard(
                                topic = topic,
                                onClick = {
                                    val topicValue = if (topic == ConversationTopic.RANDOM) null else topic.value
                                    viewModel.startConversation(topicValue)
                                }
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun TopicCard(
    topic: ConversationTopic,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .aspectRatio(1f)
            .clickable { onClick() },
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = ConversationColor.copy(alpha = 0.1f)
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Text(
                text = topic.emoji,
                fontSize = 40.sp
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                text = topic.displayName,
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.SemiBold,
                textAlign = TextAlign.Center
            )
        }
    }
}
