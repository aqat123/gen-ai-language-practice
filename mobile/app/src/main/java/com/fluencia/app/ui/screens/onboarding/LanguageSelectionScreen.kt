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
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.fluencia.app.ui.components.LoadingOverlay
import com.fluencia.app.ui.theme.FluenciaPrimary

/**
 * Data class representing a language option.
 */
data class LanguageOption(
    val code: String,
    val name: String,
    val flag: String
)

/**
 * Available languages for learning.
 */
val availableLanguages = listOf(
    LanguageOption("Spanish", "Spanish", "🇪🇸"),
    LanguageOption("French", "French", "🇫🇷"),
    LanguageOption("German", "German", "🇩🇪"),
    LanguageOption("Italian", "Italian", "🇮🇹"),
    LanguageOption("Japanese", "Japanese", "🇯🇵"),
    LanguageOption("Portuguese", "Portuguese", "🇵🇹"),
    LanguageOption("Korean", "Korean", "🇰🇷"),
    LanguageOption("Chinese", "Chinese", "🇨🇳")
)

/**
 * Language selection screen shown after registration.
 *
 * @param onLanguageSelected Callback when language is successfully selected
 * @param viewModel The onboarding ViewModel
 */
@Composable
fun LanguageSelectionScreen(
    onLanguageSelected: () -> Unit,
    viewModel: OnboardingViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    
    LaunchedEffect(uiState) {
        if (uiState is OnboardingUiState.LanguageUpdated) {
            onLanguageSelected()
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
            Spacer(modifier = Modifier.height(40.dp))
            
            Text(
                text = "🌍",
                fontSize = 64.sp
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Text(
                text = "Choose Your Language",
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold,
                color = FluenciaPrimary
            )
            
            Text(
                text = "Which language would you like to learn?",
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                textAlign = TextAlign.Center
            )
            
            Spacer(modifier = Modifier.height(32.dp))
            
            LazyVerticalGrid(
                columns = GridCells.Fixed(2),
                horizontalArrangement = Arrangement.spacedBy(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp),
                modifier = Modifier.weight(1f)
            ) {
                items(availableLanguages) { language ->
                    LanguageCard(
                        language = language,
                        onClick = { viewModel.selectLanguage(language.code) }
                    )
                }
            }
        }
        
        if (uiState is OnboardingUiState.Loading) {
            LoadingOverlay(message = "Setting language...")
        }
    }
}

/**
 * Card component for displaying a language option.
 */
@Composable
private fun LanguageCard(
    language: LanguageOption,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .aspectRatio(1f)
            .clickable { onClick() },
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Text(
                text = language.flag,
                fontSize = 48.sp
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                text = language.name,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold
            )
        }
    }
}
