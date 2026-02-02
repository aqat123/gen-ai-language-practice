package com.fluencia.app.ui.screens.grammar

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

/**
 * Grammar practice screen.
 *
 * @param onBack Navigate back
 * @param viewModel The grammar ViewModel
 */
@Composable
fun GrammarScreen(
    onBack: () -> Unit,
    viewModel: GrammarViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    
    LaunchedEffect(Unit) {
        viewModel.loadNextQuestion()
    }
    
    Scaffold(
        topBar = {
            FluenciaTopBar(
                title = "Grammar Practice",
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
                is GrammarUiState.Loading -> {
                    LoadingOverlay(message = "Loading question...")
                }
                
                is GrammarUiState.Error -> {
                    ErrorMessage(
                        message = state.message,
                        onRetry = { viewModel.loadNextQuestion() }
                    )
                }
                
                is GrammarUiState.Question -> {
                    GrammarQuestionContent(
                        state = state,
                        onAnswerSelected = { index ->
                            viewModel.submitAnswer(index)
                        },
                        onNext = { viewModel.loadNextQuestion() }
                    )
                }
            }
        }
    }
}

@Composable
private fun GrammarQuestionContent(
    state: GrammarUiState.Question,
    onAnswerSelected: (Int) -> Unit,
    onNext: () -> Unit
) {
    var selectedIndex by remember(state.question.questionId) { mutableStateOf(-1) }
    val showResult = state.answerResult != null
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp)
    ) {
        // Question Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.surface
            )
        ) {
            Column(
                modifier = Modifier.padding(24.dp)
            ) {
                Text(
                    text = state.question.questionText,
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.SemiBold
                )
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Options
        state.question.options.forEachIndexed { index, option ->
            val correctIndex = state.question.correctOptionIndex
            
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
                explanation = state.answerResult.explanation,
                onNext = onNext,
                nextButtonText = "Next Question"
            )
        }
    }
}
