package com.fluencia.app.ui.screens.phonetics

import android.Manifest
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.filled.Stop
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.google.accompanist.permissions.ExperimentalPermissionsApi
import com.google.accompanist.permissions.isGranted
import com.google.accompanist.permissions.rememberPermissionState
import com.fluencia.app.ui.components.*
import com.fluencia.app.ui.theme.*

/**
 * Phonetics/pronunciation practice screen.
 *
 * @param onBack Navigate back
 * @param viewModel The phonetics ViewModel
 */
@OptIn(ExperimentalPermissionsApi::class)
@Composable
fun PhoneticsScreen(
    onBack: () -> Unit,
    viewModel: PhoneticsViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val micPermissionState = rememberPermissionState(Manifest.permission.RECORD_AUDIO)
    
    LaunchedEffect(Unit) {
        viewModel.loadPhrase()
    }
    
    Scaffold(
        topBar = {
            FluenciaTopBar(
                title = "Pronunciation Practice",
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
                is PhoneticsUiState.Loading -> {
                    LoadingOverlay(message = "Loading phrase...")
                }
                
                is PhoneticsUiState.Error -> {
                    ErrorMessage(
                        message = state.message,
                        onRetry = { viewModel.loadPhrase() }
                    )
                }
                
                is PhoneticsUiState.Practice -> {
                    PracticeContent(
                        state = state,
                        hasPermission = micPermissionState.status.isGranted,
                        onRequestPermission = { micPermissionState.launchPermissionRequest() },
                        onStartRecording = { viewModel.startRecording() },
                        onStopRecording = { viewModel.stopRecording() },
                        onValidate = { viewModel.validatePronunciation() },
                        onNextPhrase = { viewModel.loadPhrase() }
                    )
                }
                
                is PhoneticsUiState.Evaluating -> {
                    LoadingOverlay(message = "Analyzing pronunciation...")
                }
            }
        }
    }
}

@Composable
private fun PracticeContent(
    state: PhoneticsUiState.Practice,
    hasPermission: Boolean,
    onRequestPermission: () -> Unit,
    onStartRecording: () -> Unit,
    onStopRecording: () -> Unit,
    onValidate: () -> Unit,
    onNextPhrase: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // Target Phrase
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.surface
            )
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(24.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(
                    text = "Read this phrase aloud:",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                
                Spacer(modifier = Modifier.height(16.dp))
                
                Text(
                    text = state.targetPhrase,
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold,
                    textAlign = TextAlign.Center
                )
            }
        }
        
        Spacer(modifier = Modifier.height(32.dp))
        
        // Recording Controls
        if (!hasPermission) {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = WarningOrange.copy(alpha = 0.1f)
                )
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = "Microphone permission required",
                        style = MaterialTheme.typography.bodyMedium,
                        fontWeight = FontWeight.SemiBold
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Button(onClick = onRequestPermission) {
                        Text("Grant Permission")
                    }
                }
            }
        } else {
            // Record Button
            FloatingActionButton(
                onClick = {
                    if (state.isRecording) {
                        onStopRecording()
                    } else {
                        onStartRecording()
                    }
                },
                modifier = Modifier.size(80.dp),
                containerColor = if (state.isRecording) WarningOrange else ErrorRed,
                shape = CircleShape
            ) {
                Icon(
                    imageVector = if (state.isRecording) Icons.Default.Stop else Icons.Default.Mic,
                    contentDescription = if (state.isRecording) "Stop" else "Record",
                    tint = Color.White,
                    modifier = Modifier.size(40.dp)
                )
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                text = if (state.isRecording) "Recording... Tap to stop" else "Tap to record",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            
            if (state.hasRecording) {
                Spacer(modifier = Modifier.height(24.dp))
                
                GradientButton(
                    text = "Validate Pronunciation",
                    onClick = onValidate
                )
            }
        }
        
        // Evaluation Result
        if (state.evaluation != null) {
            Spacer(modifier = Modifier.height(32.dp))
            
            // Score Card
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = if (state.evaluation.score > 70) {
                        SuccessGreen.copy(alpha = 0.1f)
                    } else {
                        ErrorRed.copy(alpha = 0.1f)
                    }
                )
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = "Score: ${state.evaluation.score.toInt()}/100",
                        style = MaterialTheme.typography.headlineMedium,
                        fontWeight = FontWeight.Bold,
                        color = if (state.evaluation.score > 70) SuccessGreen else ErrorRed
                    )
                    
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    Text(
                        text = "Heard: \"${state.evaluation.transcript}\"",
                        style = MaterialTheme.typography.bodyMedium
                    )
                    
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    Text(
                        text = state.evaluation.feedback,
                        style = MaterialTheme.typography.bodyMedium,
                        textAlign = TextAlign.Center
                    )
                }
            }
            
            // Word-level feedback
            if (!state.evaluation.wordLevelFeedback.isNullOrEmpty()) {
                Spacer(modifier = Modifier.height(16.dp))
                
                Text(
                    text = "Specific Issues:",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold,
                    modifier = Modifier.fillMaxWidth()
                )
                
                Spacer(modifier = Modifier.height(8.dp))
                
                state.evaluation.wordLevelFeedback.forEach { issue ->
                    Card(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 4.dp),
                        colors = CardDefaults.cardColors(
                            containerColor = WarningOrange.copy(alpha = 0.1f)
                        )
                    ) {
                        Column(modifier = Modifier.padding(12.dp)) {
                            Text(
                                text = "Word: \"${issue.word}\"",
                                style = MaterialTheme.typography.bodyMedium,
                                fontWeight = FontWeight.SemiBold
                            )
                            Text(
                                text = "Issue: ${issue.issue}",
                                style = MaterialTheme.typography.bodySmall
                            )
                            Text(
                                text = "💡 Tip: ${issue.tip}",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(24.dp))
            
            GradientButton(
                text = "Next Practice",
                onClick = onNextPhrase
            )
        }
    }
}
