package com.fluencia.app.ui.screens.placementtest

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.fluencia.app.ui.components.*
import com.fluencia.app.ui.theme.*

/**
 * Placement test results screen.
 *
 * @param onContinue Continue to main app
 * @param onRetake Retake the placement test
 * @param viewModel The placement test ViewModel
 */
@Composable
fun PlacementTestResultsScreen(
    onContinue: () -> Unit,
    onRetake: () -> Unit,
    viewModel: PlacementTestViewModel = hiltViewModel()
) {
    val results by viewModel.results.collectAsState()
    
    if (results == null) {
        LoadingOverlay(message = "Loading results...")
        return
    }
    
    val result = results!!
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Spacer(modifier = Modifier.height(24.dp))
        
        // Celebration
        Text(
            text = "🎉",
            fontSize = 64.sp
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        Text(
            text = "Test Complete!",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
            color = FluenciaPrimary
        )
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Level Badge
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(20.dp),
            colors = CardDefaults.cardColors(
                containerColor = FluenciaPrimary.copy(alpha = 0.1f)
            )
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(24.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(
                    text = "Your Level",
                    style = MaterialTheme.typography.titleMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                
                Spacer(modifier = Modifier.height(8.dp))
                
                LevelBadge(
                    level = result.determinedLevel,
                    size = LevelBadgeSize.LARGE
                )
                
                Spacer(modifier = Modifier.height(8.dp))
                
                Text(
                    text = "Overall Score: ${result.overallScore.toInt()}%",
                    style = MaterialTheme.typography.bodyLarge,
                    fontWeight = FontWeight.SemiBold
                )
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Section Scores
        Text(
            text = "Section Breakdown",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.SemiBold,
            modifier = Modifier.fillMaxWidth()
        )
        
        Spacer(modifier = Modifier.height(12.dp))
        
        result.sectionScores.forEach { section ->
            SectionScoreCard(
                section = section.section,
                score = section.scorePercentage,
                correct = section.correctAnswers,
                total = section.totalQuestions
            )
            Spacer(modifier = Modifier.height(8.dp))
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Recommendations
        if (result.recommendations.isNotEmpty()) {
            Text(
                text = "Recommendations",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold,
                modifier = Modifier.fillMaxWidth()
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f)
                )
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    result.recommendations.forEach { recommendation ->
                        Row(modifier = Modifier.padding(vertical = 4.dp)) {
                            Text(
                                text = "• ",
                                color = FluenciaPrimary,
                                fontWeight = FontWeight.Bold
                            )
                            Text(
                                text = recommendation,
                                style = MaterialTheme.typography.bodyMedium
                            )
                        }
                    }
                }
            }
        }
        
        Spacer(modifier = Modifier.height(32.dp))
        
        // Action Buttons
        GradientButton(
            text = "Start Learning",
            onClick = onContinue
        )
        
        Spacer(modifier = Modifier.height(12.dp))
        
        SecondaryButton(
            text = "Retake Test",
            onClick = onRetake
        )
    }
}

@Composable
private fun SectionScoreCard(
    section: String,
    score: Float,
    correct: Int,
    total: Int
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = section.replaceFirstChar { it.uppercase() },
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.SemiBold
                )
                Text(
                    text = "$correct / $total correct",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            
            Text(
                text = "${score.toInt()}%",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold,
                color = when {
                    score >= 80 -> SuccessGreen
                    score >= 60 -> WarningOrange
                    else -> ErrorRed
                }
            )
        }
    }
}
