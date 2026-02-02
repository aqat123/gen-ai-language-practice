package com.fluencia.app.ui.screens.splash

import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.fluencia.app.ui.theme.FluenciaPrimary
import com.fluencia.app.ui.theme.FluenciaSecondary
import kotlinx.coroutines.delay

/**
 * Splash screen shown during app startup.
 *
 * This screen checks the authentication state and navigates to the
 * appropriate destination based on the user's status.
 *
 * @param onNavigateToLogin Navigate to login when not authenticated
 * @param onNavigateToLanguageSelection Navigate when language not set
 * @param onNavigateToLevelSelection Navigate when level not set
 * @param onNavigateToHome Navigate to home when fully onboarded
 * @param viewModel The splash screen ViewModel
 */
@Composable
fun SplashScreen(
    onNavigateToLogin: () -> Unit,
    onNavigateToLanguageSelection: () -> Unit,
    onNavigateToLevelSelection: () -> Unit,
    onNavigateToHome: () -> Unit,
    viewModel: SplashViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    var startAnimation by remember { mutableStateOf(false) }
    
    val alphaAnim by animateFloatAsState(
        targetValue = if (startAnimation) 1f else 0f,
        animationSpec = tween(durationMillis = 1000),
        label = "alpha"
    )
    
    LaunchedEffect(Unit) {
        startAnimation = true
        delay(1500)
        viewModel.checkAuthState()
    }
    
    LaunchedEffect(uiState) {
        when (uiState) {
            is SplashUiState.NotAuthenticated -> onNavigateToLogin()
            is SplashUiState.NeedsLanguage -> onNavigateToLanguageSelection()
            is SplashUiState.NeedsLevel -> onNavigateToLevelSelection()
            is SplashUiState.Authenticated -> onNavigateToHome()
            else -> { /* Still loading */ }
        }
    }
    
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                Brush.verticalGradient(
                    colors = listOf(FluenciaPrimary, FluenciaSecondary)
                )
            ),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            modifier = Modifier.alpha(alphaAnim)
        ) {
            Text(
                text = "🎓",
                fontSize = 80.sp
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Text(
                text = "FluencIA",
                style = MaterialTheme.typography.displaySmall,
                fontWeight = FontWeight.Bold,
                color = Color.White
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                text = "Master Languages with AI",
                style = MaterialTheme.typography.bodyLarge,
                color = Color.White.copy(alpha = 0.9f)
            )
            
            Spacer(modifier = Modifier.height(48.dp))
            
            CircularProgressIndicator(
                color = Color.White,
                modifier = Modifier.size(32.dp),
                strokeWidth = 3.dp
            )
        }
    }
}
