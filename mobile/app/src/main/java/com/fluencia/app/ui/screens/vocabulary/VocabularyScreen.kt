package com.fluencia.app.ui.screens.vocabulary

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.fluencia.app.ui.components.*
import com.fluencia.app.ui.theme.*

/**
 * Vocabulary flashcard practice screen.
 *
 * @param onBack Navigate back
 * @param viewModel The vocabulary ViewModel
 */
@Composable
fun VocabularyScreen(
    onBack: () -> Unit,
    viewModel: VocabularyViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val stats by viewModel.reviewStats.collectAsState()
    
    LaunchedEffect(Unit) {
        viewModel.loadNextFlashcard()
        viewModel.loadReviewStats()
    }
    
    Scaffold(
        topBar = {
            FluenciaTopBar(
                title = "Vocabulary",
                onBackClick = onBack
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
            // SRS Stats
            stats?.let { reviewStats ->
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceEvenly
                ) {
                    StatCard(
                        value = reviewStats.due.toString(),
                        label = "Due Now",
                        color = WarningOrange,
                        modifier = Modifier.weight(1f)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    StatCard(
                        value = reviewStats.learning.toString(),
                        label = "Learning",
                        color = InfoBlue,
                        modifier = Modifier.weight(1f)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    StatCard(
                        value = reviewStats.mastered.toString(),
                        label = "Mastered",
                        color = SuccessGreen,
                        modifier = Modifier.weight(1f)
                    )
                }
                
                Spacer(modifier = Modifier.height(24.dp))
            }
            
            when (val state = uiState) {
                is VocabularyUiState.Loading -> {
                    LoadingOverlay(message = "Loading flashcard...")
                }
                
                is VocabularyUiState.Error -> {
                    ErrorMessage(
                        message = state.message,
                        onRetry = { viewModel.loadNextFlashcard() }
                    )
                }
                
                is VocabularyUiState.Flashcard -> {
                    FlashcardContent(
                        state = state,
                        onAnswerSelected = { index ->
                            viewModel.submitAnswer(index)
                        },
                        onNext = { viewModel.loadNextFlashcard() }
                    )
                }
            }
        }
    }
}

@Composable
private fun FlashcardContent(
    state: VocabularyUiState.Flashcard,
    onAnswerSelected: (Int) -> Unit,
    onNext: () -> Unit
) {
    var selectedIndex by remember(state.flashcard.word) { mutableStateOf(-1) }
    val showResult = state.answerResult != null
    
    // Flashcard
    Flashcard(
        word = state.flashcard.word,
        exampleSentence = state.flashcard.exampleSentence,
        onSpeakClick = { /* TTS would be handled here */ }
    )
    
    // Review indicator
    if (state.flashcard.isReview == true) {
        Spacer(modifier = Modifier.height(8.dp))
        Card(
            colors = CardDefaults.cardColors(
                containerColor = FluenciaPrimary.copy(alpha = 0.1f)
            )
        ) {
            Text(
                text = "📖 Review Card",
                style = MaterialTheme.typography.labelMedium,
                color = FluenciaPrimary,
                fontWeight = FontWeight.SemiBold,
                modifier = Modifier.padding(horizontal = 12.dp, vertical = 4.dp)
            )
        }
    }
    
    Spacer(modifier = Modifier.height(24.dp))
    
    // Options
    state.flashcard.options?.forEachIndexed { index, option ->
        val correctIndex = state.flashcard.correctOptionIndex ?: -1
        
        OptionButton(
            text = option,
            isSelected = selectedIndex == index,
            isCorrect = index == correctIndex,
            showResult = showResult,
            onClick = {
                if (!showResult) {
                    selectedIndex = index
                    onAnswerSelected(index)
                }
            },
            enabled = !showResult
        )
        Spacer(modifier = Modifier.height(12.dp))
    }
    
    // Feedback
    if (showResult && state.answerResult != null) {
        Spacer(modifier = Modifier.height(16.dp))
        FeedbackCard(
            isCorrect = state.answerResult.isCorrect,
            explanation = state.answerResult.explanation ?: "The correct answer is highlighted above.",
            onNext = onNext,
            nextButtonText = "Next Word"
        )
    }
}
