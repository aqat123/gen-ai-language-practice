package com.fluencia.app.ui.theme

import android.app.Activity
import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.SideEffect
import androidx.compose.runtime.staticCompositionLocalOf
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

/**
 * Custom extended colors for FluencIA that are not part of the standard Material3 color scheme.
 *
 * These colors provide theme-aware variants for specific UI elements that need
 * consistent styling across the app.
 *
 * @property cardBackground Background color for card components
 * @property elevatedSurface Background color for elevated surfaces like app bars
 * @property successColor Color for success states and positive feedback
 * @property warningColor Color for warning states and caution indicators
 * @property infoColor Color for informational elements
 * @property textSecondary Secondary text color for less prominent text
 * @property divider Divider and separator color
 */
data class ExtendedColors(
    val cardBackground: Color,
    val elevatedSurface: Color,
    val successColor: Color,
    val warningColor: Color,
    val infoColor: Color,
    val textSecondary: Color,
    val divider: Color
)

/**
 * Extended colors for light theme.
 */
private val LightExtendedColors = ExtendedColors(
    cardBackground = LightCardBackground,
    elevatedSurface = LightElevatedSurface,
    successColor = SuccessGreen,
    warningColor = WarningOrange,
    infoColor = InfoBlue,
    textSecondary = LightTextSecondary,
    divider = LightOutline
)

/**
 * Extended colors for dark theme.
 */
private val DarkExtendedColors = ExtendedColors(
    cardBackground = DarkCardBackground,
    elevatedSurface = DarkElevatedSurface,
    successColor = SuccessGreenDark,
    warningColor = WarningOrangeDark,
    infoColor = InfoBlueDark,
    textSecondary = DarkTextSecondary,
    divider = DarkOutline
)

/**
 * CompositionLocal for providing extended colors throughout the app.
 */
val LocalExtendedColors = staticCompositionLocalOf { LightExtendedColors }

/**
 * Dark color scheme for the FluencIA app.
 *
 * Optimized for readability and reduced eye strain in low-light environments.
 * Uses deeper, less saturated backgrounds with brighter accent colors for contrast.
 */
private val DarkColorScheme = darkColorScheme(
    primary = FluenciaPrimaryLight,
    onPrimary = Color.Black,
    primaryContainer = FluenciaPrimaryDark,
    onPrimaryContainer = Color.White,
    secondary = FluenciaSecondaryLight,
    onSecondary = Color.Black,
    secondaryContainer = FluenciaSecondary.copy(alpha = 0.3f),
    onSecondaryContainer = Color.White,
    tertiary = InfoBlueDark,
    onTertiary = Color.Black,
    tertiaryContainer = InfoBlue.copy(alpha = 0.3f),
    onTertiaryContainer = Color.White,
    background = DarkBackground,
    onBackground = DarkTextPrimary,
    surface = DarkSurface,
    onSurface = DarkTextPrimary,
    surfaceVariant = DarkSurfaceVariant,
    onSurfaceVariant = DarkOnSurfaceVariant,
    surfaceTint = FluenciaPrimaryLight,
    inverseSurface = LightSurface,
    inverseOnSurface = LightTextPrimary,
    error = ErrorRedDark,
    onError = Color.Black,
    errorContainer = ErrorRed.copy(alpha = 0.3f),
    onErrorContainer = ErrorRedLight,
    outline = DarkOutline,
    outlineVariant = DarkOutline.copy(alpha = 0.5f),
    scrim = Color.Black.copy(alpha = 0.6f)
)

/**
 * Light color scheme for the FluencIA app.
 *
 * Optimized for readability in well-lit environments with clear contrast
 * and vibrant accent colors.
 */
private val LightColorScheme = lightColorScheme(
    primary = FluenciaPrimary,
    onPrimary = Color.White,
    primaryContainer = Color(0xFFE8EDFF),
    onPrimaryContainer = FluenciaPrimaryDark,
    secondary = FluenciaSecondary,
    onSecondary = Color.White,
    secondaryContainer = Color(0xFFFAE8FF),
    onSecondaryContainer = FluenciaSecondary,
    tertiary = InfoBlue,
    onTertiary = Color.White,
    tertiaryContainer = Color(0xFFE3F2FD),
    onTertiaryContainer = Color(0xFF0D47A1),
    background = LightBackground,
    onBackground = LightTextPrimary,
    surface = LightSurface,
    onSurface = LightTextPrimary,
    surfaceVariant = LightSurfaceVariant,
    onSurfaceVariant = LightOnSurfaceVariant,
    surfaceTint = FluenciaPrimary,
    inverseSurface = DarkSurface,
    inverseOnSurface = DarkTextPrimary,
    error = ErrorRed,
    onError = Color.White,
    errorContainer = Color(0xFFFFEDED),
    onErrorContainer = ErrorRed,
    outline = LightOutline,
    outlineVariant = LightOutline.copy(alpha = 0.5f),
    scrim = Color.Black.copy(alpha = 0.4f)
)

/**
 * Main theme composable for the FluencIA app.
 *
 * Supports both light and dark themes, with optional dynamic color
 * on Android 12+ devices. The theme provides extended colors through
 * CompositionLocal for elements not covered by Material3's color scheme.
 *
 * @param darkTheme Whether to use dark theme. Defaults to system setting.
 * @param dynamicColor Whether to use dynamic colors on supported devices.
 * @param content The composable content to be themed.
 */
@Composable
fun FluenciaTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    // Dynamic color is available on Android 12+
    dynamicColor: Boolean = false,
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }
        darkTheme -> DarkColorScheme
        else -> LightColorScheme
    }
    
    val extendedColors = if (darkTheme) DarkExtendedColors else LightExtendedColors
    
    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            // Use surface color for status bar for a more integrated look
            window.statusBarColor = if (darkTheme) {
                DarkElevatedSurface.toArgb()
            } else {
                colorScheme.primary.toArgb()
            }
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = !darkTheme
        }
    }

    CompositionLocalProvider(LocalExtendedColors provides extendedColors) {
        MaterialTheme(
            colorScheme = colorScheme,
            typography = Typography,
            content = content
        )
    }
}

/**
 * Convenience accessor for extended colors within the theme.
 *
 * Usage: FluenciaTheme.extendedColors.successColor
 */
object FluenciaTheme {
    /**
     * Access extended colors from anywhere within the theme.
     */
    val extendedColors: ExtendedColors
        @Composable
        get() = LocalExtendedColors.current
}
