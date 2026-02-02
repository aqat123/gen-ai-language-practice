package com.fluencia.app.ui.screens.placementtest

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.fluencia.app.ui.components.*
import com.fluencia.app.ui.theme.FluenciaPrimary

/**
 * Placement test screen for determining user's CEFR level.
 *
 * @param onTestComplete Callback when test is complete with test ID
 * @param onBack Navigate back
 * @param viewModel The placement test ViewModel
 */
@Composable
fun PlacementTestScreen(
    onTestComplete: (String) -> Unit,
    onBack: () -> Unit,
    viewModel: PlacementTestViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    
    LaunchedEffect(Unit) {
        viewModel.startTest()
    }
    
    LaunchedEffect(uiState) {
        if (uiState is PlacementTestUiState.Completed) {
            onTestComplete((uiState as PlacementTestUiState.Completed).testId)
        }
    }
    
    Scaffold(
        topBar = {
            FluenciaTopBar(
                title = "Placement Test",
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
                is PlacementTestUiState.Loading -> {
                    LoadingOverlay(message = "Loading test...")
                }
                
                is PlacementTestUiState.Error -> {
                    ErrorMessage(
                        message = state.message,
                        onRetry = { viewModel.startTest() }
                    )
                }
                
                is PlacementTestUiState.Question -> {
                    QuestionContent(
                        state = state,
                        onAnswerSelected = { index ->
                            viewModel.submitAnswer(index)
                        }
                    )
                }
                
                is PlacementTestUiState.Completed -> {
                    LoadingOverlay(message = "Loading results...")
                }
            }
        }
    }
}

@Composable
private fun QuestionContent(
    state: PlacementTestUiState.Question,
    onAnswerSelected: (Int) -> Unit
) {
    var selectedIndex by remember(state.question.questionNumber) { mutableStateOf(-1) }
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp)
    ) {
        // Progress
        ProgressBar(
            progress = state.currentQuestion.toFloat() / state.totalQuestions,
            label = "Question ${state.currentQuestion} of ${state.totalQuestions}"
        )
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Section Badge
        Card(
            shape = MaterialTheme.shapes.small,
            colors = CardDefaults.cardColors(
                containerColor = FluenciaPrimary.copy(alpha = 0.1f)
            )
        ) {
            Text(
                text = state.question.section.uppercase(),
                style = MaterialTheme.typography.labelMedium,
                color = FluenciaPrimary,
                modifier = Modifier.padding(horizontal = 12.dp, vertical = 4.dp)
            )
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Reading Passage (if any)
        if (!state.question.passage.isNullOrEmpty()) {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f)
                )
            ) {
                Text(
                    text = state.question.passage,
                    style = MaterialTheme.typography.bodyMedium,
                    modifier = Modifier.padding(16.dp)
                )
            }
            Spacer(modifier = Modifier.height(16.dp))
        }
        
        // Question Text
        Text(
            text = state.question.questionText,
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.SemiBold
        )
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Options
        state.question.options.forEachIndexed { index, option ->
            OptionButton(
                text = option,
                isSelected = selectedIndex == index,
                isCorrect = false,
                showResult = false,
                onClick = {
                    selectedIndex = index
                    onAnswerSelected(index)
                },
                enabled = selectedIndex == -1
            )
            Spacer(modifier = Modifier.height(12.dp))
        }
    }
}
