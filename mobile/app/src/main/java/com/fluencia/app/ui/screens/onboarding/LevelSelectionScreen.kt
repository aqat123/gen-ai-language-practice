package com.fluencia.app.ui.screens.onboarding

import androidx.compose.foundation.background
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
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.fluencia.app.ui.components.GradientButton
import com.fluencia.app.ui.components.LoadingOverlay
import com.fluencia.app.ui.theme.*

/**
 * Data class representing a CEFR level option.
 */
data class LevelOption(
    val code: String,
    val name: String,
    val description: String,
    val color: Color
)

/**
 * Available CEFR levels.
 */
val availableLevels = listOf(
    LevelOption("A1", "A1", "Beginner", LevelA1Color),
    LevelOption("A2", "A2", "Elementary", LevelA2Color),
    LevelOption("B1", "B1", "Intermediate", LevelB1Color),
    LevelOption("B2", "B2", "Upper Intermediate", LevelB2Color),
    LevelOption("C1", "C1", "Advanced", LevelC1Color),
    LevelOption("C2", "C2", "Proficient", LevelC2Color)
)

/**
 * Level selection screen shown after language selection.
 *
 * @param onTakePlacementTest Navigate to placement test
 * @param onLevelSelected Callback when level is manually selected
 * @param viewModel The onboarding ViewModel
 */
@Composable
fun LevelSelectionScreen(
    onTakePlacementTest: () -> Unit,
    onLevelSelected: () -> Unit,
    viewModel: OnboardingViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    
    LaunchedEffect(uiState) {
        if (uiState is OnboardingUiState.LevelUpdated) {
            onLevelSelected()
        }
    }
    
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Spacer(modifier = Modifier.height(24.dp))
            
            Text(
                text = "📊",
                fontSize = 64.sp
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Text(
                text = "Choose Your Starting Point",
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold,
                color = FluenciaPrimary,
                textAlign = TextAlign.Center
            )
            
            Spacer(modifier = Modifier.height(24.dp))
            
            // Placement Test Button
            GradientButton(
                text = "Take Placement Test (Recommended)",
                onClick = onTakePlacementTest
            )
            
            Spacer(modifier = Modifier.height(24.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                HorizontalDivider(modifier = Modifier.weight(1f))
                Text(
                    text = "  OR  ",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                HorizontalDivider(modifier = Modifier.weight(1f))
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Text(
                text = "Select your level manually:",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            LazyVerticalGrid(
                columns = GridCells.Fixed(3),
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
                modifier = Modifier.weight(1f)
            ) {
                items(availableLevels) { level ->
                    LevelCard(
                        level = level,
                        onClick = { viewModel.selectLevel(level.code) }
                    )
                }
            }
        }
        
        if (uiState is OnboardingUiState.Loading) {
            LoadingOverlay(message = "Setting level...")
        }
    }
}

/**
 * Card component for displaying a level option.
 */
@Composable
private fun LevelCard(
    level: LevelOption,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .aspectRatio(0.9f)
            .clickable { onClick() },
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = level.color.copy(alpha = 0.15f)
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(12.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Text(
                text = level.code,
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold,
                color = level.color
            )
            
            Spacer(modifier = Modifier.height(4.dp))
            
            Text(
                text = level.description,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                textAlign = TextAlign.Center
            )
        }
    }
}
