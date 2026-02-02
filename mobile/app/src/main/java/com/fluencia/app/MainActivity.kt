package com.fluencia.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.compose.rememberNavController
import com.fluencia.app.ui.navigation.FluenciaNavHost
import com.fluencia.app.ui.theme.FluenciaTheme
import com.fluencia.app.ui.theme.ThemeViewModel
import dagger.hilt.android.AndroidEntryPoint

/**
 * Main activity for the FluencIA language learning app.
 *
 * This activity serves as the entry point for the app and sets up the
 * Compose UI with navigation. It is annotated with @AndroidEntryPoint
 * to enable Hilt dependency injection.
 *
 * The activity manages the app-wide theme state through [ThemeViewModel],
 * allowing users to toggle between light and dark modes while persisting
 * their preference.
 */
@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Enable edge-to-edge display
        enableEdgeToEdge()
        
        setContent {
            val themeViewModel: ThemeViewModel = hiltViewModel()
            val themeState by themeViewModel.themeState.collectAsState()
            
            // Determine dark mode: use user preference if set, otherwise follow system
            val systemDarkTheme = isSystemInDarkTheme()
            val isDarkTheme = if (themeState.useSystemTheme || themeState.isDarkMode == null) {
                systemDarkTheme
            } else {
                themeState.isDarkMode!!
            }
            
            FluenciaTheme(darkTheme = isDarkTheme) {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    val navController = rememberNavController()
                    FluenciaNavHost(
                        navController = navController,
                        isDarkTheme = isDarkTheme,
                        onToggleTheme = { themeViewModel.toggleDarkMode(isDarkTheme) }
                    )
                }
            }
        }
    }
}
