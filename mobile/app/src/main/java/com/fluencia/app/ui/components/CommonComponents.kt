package com.fluencia.app.ui.components

import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.rotate
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.fluencia.app.ui.theme.*

/**
 * Primary gradient button used throughout the app.
 *
 * @param text Button text
 * @param onClick Click handler
 * @param modifier Optional modifier
 * @param enabled Whether the button is enabled
 * @param isLoading Whether to show loading indicator
 */
@Composable
fun GradientButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    isLoading: Boolean = false
) {
    val gradient = Brush.horizontalGradient(
        colors = listOf(FluenciaPrimary, FluenciaSecondary)
    )
    
    Box(
        modifier = modifier
            .fillMaxWidth()
            .height(56.dp)
            .clip(RoundedCornerShape(16.dp))
            .background(if (enabled) gradient else Brush.horizontalGradient(listOf(Color.Gray, Color.Gray)))
            .clickable(enabled = enabled && !isLoading) { onClick() },
        contentAlignment = Alignment.Center
    ) {
        if (isLoading) {
            CircularProgressIndicator(
                modifier = Modifier.size(24.dp),
                color = Color.White,
                strokeWidth = 2.dp
            )
        } else {
            Text(
                text = text,
                color = Color.White,
                fontWeight = FontWeight.SemiBold,
                fontSize = 16.sp
            )
        }
    }
}

/**
 * Secondary outlined button.
 *
 * @param text Button text
 * @param onClick Click handler
 * @param modifier Optional modifier
 */
@Composable
fun SecondaryButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    OutlinedButton(
        onClick = onClick,
        modifier = modifier
            .fillMaxWidth()
            .height(56.dp),
        shape = RoundedCornerShape(16.dp),
        colors = ButtonDefaults.outlinedButtonColors(
            contentColor = FluenciaPrimary
        )
    ) {
        Text(
            text = text,
            fontWeight = FontWeight.SemiBold,
            fontSize = 16.sp
        )
    }
}

/**
 * Module card for the home screen.
 *
 * @param title Module title
 * @param description Module description
 * @param icon Icon to display
 * @param color Module accent color
 * @param onClick Click handler
 * @param modifier Optional modifier
 */
@Composable
fun ModuleCard(
    title: String,
    description: String,
    icon: String,
    color: Color,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .clickable { onClick() },
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(56.dp)
                    .clip(RoundedCornerShape(12.dp))
                    .background(color.copy(alpha = 0.15f)),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = icon,
                    fontSize = 28.sp
                )
            }
            
            Spacer(modifier = Modifier.width(16.dp))
            
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold
                )
                Text(
                    text = description,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            
            Icon(
                imageVector = Icons.Default.ChevronRight,
                contentDescription = null,
                tint = color
            )
        }
    }
}

/**
 * Answer option button for quizzes.
 *
 * @param text Option text
 * @param isSelected Whether this option is selected
 * @param isCorrect Whether this is the correct answer (shown after selection)
 * @param showResult Whether to show the result (correct/incorrect)
 * @param onClick Click handler
 * @param modifier Optional modifier
 */
@Composable
fun OptionButton(
    text: String,
    isSelected: Boolean,
    isCorrect: Boolean,
    showResult: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true
) {
    val backgroundColor by animateColorAsState(
        targetValue = when {
            showResult && isCorrect -> SuccessGreen.copy(alpha = 0.15f)
            showResult && isSelected && !isCorrect -> ErrorRed.copy(alpha = 0.15f)
            isSelected -> FluenciaPrimary.copy(alpha = 0.15f)
            else -> MaterialTheme.colorScheme.surface
        },
        label = "backgroundColor"
    )
    
    val borderColor by animateColorAsState(
        targetValue = when {
            showResult && isCorrect -> SuccessGreen
            showResult && isSelected && !isCorrect -> ErrorRed
            isSelected -> FluenciaPrimary
            else -> MaterialTheme.colorScheme.outline.copy(alpha = 0.3f)
        },
        label = "borderColor"
    )
    
    Card(
        modifier = modifier
            .fillMaxWidth()
            .clickable(enabled = enabled) { onClick() }
            .border(2.dp, borderColor, RoundedCornerShape(12.dp)),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = backgroundColor)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = text,
                style = MaterialTheme.typography.bodyLarge,
                modifier = Modifier.weight(1f)
            )
            
            if (showResult) {
                Icon(
                    imageVector = if (isCorrect) Icons.Default.CheckCircle else Icons.Default.Cancel,
                    contentDescription = null,
                    tint = if (isCorrect) SuccessGreen else ErrorRed
                )
            }
        }
    }
}

/**
 * Flashcard component for vocabulary practice.
 *
 * @param word The vocabulary word
 * @param exampleSentence Example sentence using the word
 * @param modifier Optional modifier
 */
@Composable
fun Flashcard(
    word: String,
    exampleSentence: String,
    modifier: Modifier = Modifier,
    onSpeakClick: () -> Unit = {}
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.End
            ) {
                IconButton(onClick = onSpeakClick) {
                    Icon(
                        imageVector = Icons.Default.VolumeUp,
                        contentDescription = "Listen",
                        tint = FluenciaPrimary
                    )
                }
            }
            
            Text(
                text = word,
                style = MaterialTheme.typography.headlineLarge,
                fontWeight = FontWeight.Bold,
                textAlign = TextAlign.Center,
                color = FluenciaPrimary
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Text(
                text = "\"$exampleSentence\"",
                style = MaterialTheme.typography.bodyLarge,
                textAlign = TextAlign.Center,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Text(
                text = "What does this mean?",
                style = MaterialTheme.typography.labelLarge,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

/**
 * Progress bar with percentage display.
 *
 * @param progress Progress value (0-1)
 * @param label Optional label text
 * @param modifier Optional modifier
 */
@Composable
fun ProgressBar(
    progress: Float,
    label: String? = null,
    modifier: Modifier = Modifier,
    color: Color = FluenciaPrimary
) {
    Column(modifier = modifier.fillMaxWidth()) {
        if (label != null) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = label,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Text(
                    text = "${(progress * 100).toInt()}%",
                    style = MaterialTheme.typography.bodySmall,
                    fontWeight = FontWeight.SemiBold,
                    color = color
                )
            }
            Spacer(modifier = Modifier.height(4.dp))
        }
        
        LinearProgressIndicator(
            progress = progress.coerceIn(0f, 1f),
            modifier = Modifier
                .fillMaxWidth()
                .height(8.dp)
                .clip(RoundedCornerShape(4.dp)),
            color = color,
            trackColor = color.copy(alpha = 0.2f)
        )
    }
}

/**
 * Stats card for displaying numerical statistics.
 *
 * @param value The statistic value
 * @param label The label for the statistic
 * @param color Accent color
 * @param modifier Optional modifier
 */
@Composable
fun StatCard(
    value: String,
    label: String,
    color: Color,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier,
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = color.copy(alpha = 0.1f)
        )
    ) {
        Column(
            modifier = Modifier
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = value,
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold,
                color = color
            )
            Text(
                text = label,
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

/**
 * Level badge component.
 *
 * @param level CEFR level string (e.g., "A1", "B2")
 * @param modifier Optional modifier
 */
@Composable
fun LevelBadge(
    level: String,
    modifier: Modifier = Modifier,
    size: LevelBadgeSize = LevelBadgeSize.MEDIUM
) {
    val color = when (level) {
        "A1" -> LevelA1Color
        "A2" -> LevelA2Color
        "B1" -> LevelB1Color
        "B2" -> LevelB2Color
        "C1" -> LevelC1Color
        "C2" -> LevelC2Color
        else -> FluenciaPrimary
    }
    
    val (badgeSize, fontSize) = when (size) {
        LevelBadgeSize.SMALL -> 32.dp to 12.sp
        LevelBadgeSize.MEDIUM -> 48.dp to 16.sp
        LevelBadgeSize.LARGE -> 64.dp to 20.sp
    }
    
    Box(
        modifier = modifier
            .size(badgeSize)
            .clip(CircleShape)
            .background(color),
        contentAlignment = Alignment.Center
    ) {
        Text(
            text = level,
            color = Color.White,
            fontWeight = FontWeight.Bold,
            fontSize = fontSize
        )
    }
}

enum class LevelBadgeSize {
    SMALL, MEDIUM, LARGE
}

/**
 * Top app bar with back navigation.
 *
 * @param title Screen title
 * @param onBackClick Back button click handler
 * @param actions Optional action buttons
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun FluenciaTopBar(
    title: String,
    onBackClick: () -> Unit,
    actions: @Composable RowScope.() -> Unit = {}
) {
    TopAppBar(
        title = {
            Text(
                text = title,
                fontWeight = FontWeight.SemiBold
            )
        },
        navigationIcon = {
            IconButton(onClick = onBackClick) {
                Icon(
                    imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                    contentDescription = "Back"
                )
            }
        },
        actions = actions,
        colors = TopAppBarDefaults.topAppBarColors(
            containerColor = MaterialTheme.colorScheme.surface
        )
    )
}

/**
 * Loading indicator overlay.
 *
 * @param message Optional loading message
 */
@Composable
fun LoadingOverlay(
    message: String = "Loading..."
) {
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            CircularProgressIndicator(
                color = FluenciaPrimary
            )
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = message,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

/**
 * Error message component.
 *
 * @param message Error message text
 * @param onRetry Optional retry callback
 */
@Composable
fun ErrorMessage(
    message: String,
    onRetry: (() -> Unit)? = null
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Icon(
            imageVector = Icons.Default.Error,
            contentDescription = null,
            tint = ErrorRed,
            modifier = Modifier.size(48.dp)
        )
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            text = message,
            style = MaterialTheme.typography.bodyMedium,
            textAlign = TextAlign.Center,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        if (onRetry != null) {
            Spacer(modifier = Modifier.height(16.dp))
            TextButton(onClick = onRetry) {
                Text("Retry")
            }
        }
    }
}

/**
 * Feedback card for showing results (correct/incorrect).
 *
 * @param isCorrect Whether the answer was correct
 * @param explanation Explanation text
 * @param onNext Callback for next action
 * @param nextButtonText Text for the next button
 */
@Composable
fun FeedbackCard(
    isCorrect: Boolean,
    explanation: String,
    onNext: () -> Unit,
    nextButtonText: String = "Next"
) {
    val backgroundColor = if (isCorrect) SuccessGreen.copy(alpha = 0.1f) else ErrorRed.copy(alpha = 0.1f)
    val borderColor = if (isCorrect) SuccessGreen else ErrorRed
    
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .border(2.dp, borderColor, RoundedCornerShape(16.dp)),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = backgroundColor)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    imageVector = if (isCorrect) Icons.Default.CheckCircle else Icons.Default.Cancel,
                    contentDescription = null,
                    tint = borderColor,
                    modifier = Modifier.size(24.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = if (isCorrect) "Correct!" else "Incorrect",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = borderColor
                )
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            Text(
                text = explanation,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurface
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            GradientButton(
                text = nextButtonText,
                onClick = onNext
            )
        }
    }
}

/**
 * Theme toggle button for switching between light and dark modes.
 *
 * Displays a sun icon when in dark mode (click to switch to light),
 * and a moon icon when in light mode (click to switch to dark).
 * Includes a smooth rotation animation when toggling.
 *
 * @param isDarkTheme Whether the app is currently in dark theme mode
 * @param onToggleTheme Callback invoked when the button is clicked to toggle theme
 * @param modifier Optional modifier for the IconButton
 */
@Composable
fun ThemeToggleButton(
    isDarkTheme: Boolean,
    onToggleTheme: () -> Unit,
    modifier: Modifier = Modifier
) {
    // Animate rotation when theme changes
    val rotationAngle by animateFloatAsState(
        targetValue = if (isDarkTheme) 180f else 0f,
        animationSpec = tween(durationMillis = 300),
        label = "themeToggleRotation"
    )
    
    // Animate icon color for smooth transition
    val iconTint by animateColorAsState(
        targetValue = if (isDarkTheme) {
            WarningOrangeDark // Sun color for dark mode
        } else {
            FluenciaPrimary // Moon color for light mode
        },
        animationSpec = tween(durationMillis = 300),
        label = "themeToggleColor"
    )
    
    IconButton(
        onClick = onToggleTheme,
        modifier = modifier
    ) {
        Icon(
            imageVector = if (isDarkTheme) {
                Icons.Default.LightMode // Sun icon to switch to light mode
            } else {
                Icons.Default.DarkMode // Moon icon to switch to dark mode
            },
            contentDescription = if (isDarkTheme) {
                "Switch to light mode"
            } else {
                "Switch to dark mode"
            },
            tint = iconTint,
            modifier = Modifier.rotate(rotationAngle)
        )
    }
}

/**
 * Compact theme toggle button variant with smaller size.
 *
 * Suitable for use in tight spaces or alongside other compact UI elements.
 *
 * @param isDarkTheme Whether the app is currently in dark theme mode
 * @param onToggleTheme Callback invoked when the button is clicked to toggle theme
 * @param modifier Optional modifier for the container
 */
@Composable
fun CompactThemeToggleButton(
    isDarkTheme: Boolean,
    onToggleTheme: () -> Unit,
    modifier: Modifier = Modifier
) {
    val iconTint by animateColorAsState(
        targetValue = if (isDarkTheme) {
            WarningOrangeDark
        } else {
            FluenciaPrimary
        },
        animationSpec = tween(durationMillis = 300),
        label = "compactThemeToggleColor"
    )
    
    IconButton(
        onClick = onToggleTheme,
        modifier = modifier.size(40.dp)
    ) {
        Icon(
            imageVector = if (isDarkTheme) {
                Icons.Default.LightMode
            } else {
                Icons.Default.DarkMode
            },
            contentDescription = if (isDarkTheme) {
                "Switch to light mode"
            } else {
                "Switch to dark mode"
            },
            tint = iconTint,
            modifier = Modifier.size(20.dp)
        )
    }
}
