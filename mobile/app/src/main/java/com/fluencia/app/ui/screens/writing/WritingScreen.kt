package com.fluencia.app.ui.screens.writing

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.fluencia.app.data.model.WritingPrompt
import com.fluencia.app.ui.components.*
import com.fluencia.app.ui.theme.*

/**
 * Writing practice screen.
 *
 * @param onBack Navigate back
 * @param viewModel The writing ViewModel
 */
@Composable
fun WritingScreen(
    onBack: () -> Unit,
    viewModel: WritingViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    
    LaunchedEffect(Unit) {
        viewModel.loadPrompts()
    }
    
    Scaffold(
        topBar = {
            FluenciaTopBar(
                title = "Writing Practice",
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
                is WritingUiState.LoadingPrompts -> {
                    LoadingOverlay(message = "Loading prompts...")
                }
                
                is WritingUiState.PromptSelection -> {
                    PromptSelectionContent(
                        prompts = state.prompts,
                        onPromptSelected = { viewModel.selectPrompt(it) },
                        onWriteFreeForm = { viewModel.selectFreeForm() }
                    )
                }
                
                is WritingUiState.Writing -> {
                    WritingContent(
                        selectedPrompt = state.selectedPrompt,
                        onSubmit = { text -> viewModel.submitWriting(text) },
                        onChangePrompt = { viewModel.loadPrompts() }
                    )
                }
                
                is WritingUiState.Loading -> {
                    LoadingOverlay(message = "Getting feedback...")
                }
                
                is WritingUiState.Feedback -> {
                    FeedbackContent(
                        feedback = state,
                        onTryAnother = { viewModel.loadPrompts() }
                    )
                }
                
                is WritingUiState.Error -> {
                    ErrorMessage(
                        message = state.message,
                        onRetry = { viewModel.loadPrompts() }
                    )
                }
            }
        }
    }
}

@Composable
private fun PromptSelectionContent(
    prompts: List<WritingPrompt>,
    onPromptSelected: (WritingPrompt) -> Unit,
    onWriteFreeForm: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text(
            text = "Choose a Writing Topic",
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.Bold
        )
        
        Text(
            text = "Select a prompt that interests you",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        LazyColumn(
            modifier = Modifier.weight(1f),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            items(prompts) { prompt ->
                PromptCard(
                    prompt = prompt,
                    onClick = { onPromptSelected(prompt) }
                )
            }
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        SecondaryButton(
            text = "Write Without a Prompt",
            onClick = onWriteFreeForm
        )
    }
}

@Composable
private fun PromptCard(
    prompt: WritingPrompt,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onClick() },
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = prompt.title,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = prompt.prompt,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@Composable
private fun WritingContent(
    selectedPrompt: WritingPrompt?,
    onSubmit: (String) -> Unit,
    onChangePrompt: () -> Unit
) {
    var text by remember { mutableStateOf("") }
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        // Selected prompt display
        if (selectedPrompt != null) {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = FluenciaPrimary.copy(alpha = 0.1f)
                )
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        text = selectedPrompt.title,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.SemiBold,
                        color = FluenciaPrimary
                    )
                    Text(
                        text = selectedPrompt.prompt,
                        style = MaterialTheme.typography.bodyMedium
                    )
                    TextButton(onClick = onChangePrompt) {
                        Text("Choose Different Topic")
                    }
                }
            }
            Spacer(modifier = Modifier.height(16.dp))
        }
        
        // Writing input
        OutlinedTextField(
            value = text,
            onValueChange = { text = it },
            label = { Text("Write your text here...") },
            modifier = Modifier
                .fillMaxWidth()
                .weight(1f),
            shape = RoundedCornerShape(12.dp)
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        GradientButton(
            text = "Get Feedback",
            onClick = { onSubmit(text) },
            enabled = text.isNotBlank()
        )
    }
}

@Composable
private fun FeedbackContent(
    feedback: WritingUiState.Feedback,
    onTryAnother: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp)
    ) {
        // Corrected Text
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = SuccessGreen.copy(alpha = 0.1f)
            )
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "✅ Corrected Text",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold,
                    color = SuccessGreen
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = feedback.correctedText,
                    style = MaterialTheme.typography.bodyLarge
                )
            }
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Feedback Comment
        Card(modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "💬 Feedback",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = feedback.overallComment,
                    style = MaterialTheme.typography.bodyMedium
                )
                
                if (!feedback.inlineExplanation.isNullOrEmpty()) {
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = feedback.inlineExplanation,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        }
        
        // Score
        if (feedback.score != null) {
            Spacer(modifier = Modifier.height(16.dp))
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = FluenciaPrimary.copy(alpha = 0.1f)
                )
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    horizontalArrangement = Arrangement.Center
                ) {
                    Text(
                        text = "Score: ${feedback.score.toInt()}%",
                        style = MaterialTheme.typography.headlineSmall,
                        fontWeight = FontWeight.Bold,
                        color = FluenciaPrimary
                    )
                }
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        GradientButton(
            text = "Try Another",
            onClick = onTryAnother
        )
    }
}
