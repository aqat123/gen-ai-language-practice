package com.fluencia.app.ui.navigation

import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.navArgument
import com.fluencia.app.ui.screens.auth.LoginScreen
import com.fluencia.app.ui.screens.auth.RegisterScreen
import com.fluencia.app.ui.screens.conversation.ConversationScreen
import com.fluencia.app.ui.screens.conversation.ConversationTopicsScreen
import com.fluencia.app.ui.screens.grammar.GrammarScreen
import com.fluencia.app.ui.screens.home.HomeScreen
import com.fluencia.app.ui.screens.onboarding.LanguageSelectionScreen
import com.fluencia.app.ui.screens.onboarding.LevelSelectionScreen
import com.fluencia.app.ui.screens.phonetics.PhoneticsScreen
import com.fluencia.app.ui.screens.placementtest.PlacementTestResultsScreen
import com.fluencia.app.ui.screens.placementtest.PlacementTestScreen
import com.fluencia.app.ui.screens.progress.AchievementsScreen
import com.fluencia.app.ui.screens.progress.ProgressScreen
import com.fluencia.app.ui.screens.splash.SplashScreen
import com.fluencia.app.ui.screens.vocabulary.VocabularyScreen
import com.fluencia.app.ui.screens.writing.WritingScreen

/**
 * Main navigation host for the FluencIA app.
 *
 * This composable sets up all navigation destinations and handles
 * transitions between screens based on user authentication state
 * and learning progress.
 *
 * @param navController The navigation controller for managing navigation
 * @param modifier Optional modifier for the NavHost
 * @param isDarkTheme Whether the app is currently in dark theme mode
 * @param onToggleTheme Callback to toggle between light and dark themes
 */
@Composable
fun FluenciaNavHost(
    navController: NavHostController,
    modifier: Modifier = Modifier,
    isDarkTheme: Boolean = false,
    onToggleTheme: () -> Unit = {}
) {
    NavHost(
        navController = navController,
        startDestination = Screen.Splash.route,
        modifier = modifier
    ) {
        // Splash Screen
        composable(Screen.Splash.route) {
            SplashScreen(
                onNavigateToLogin = {
                    navController.navigate(Screen.Login.route) {
                        popUpTo(Screen.Splash.route) { inclusive = true }
                    }
                },
                onNavigateToLanguageSelection = {
                    navController.navigate(Screen.LanguageSelection.route) {
                        popUpTo(Screen.Splash.route) { inclusive = true }
                    }
                },
                onNavigateToLevelSelection = {
                    navController.navigate(Screen.LevelSelection.route) {
                        popUpTo(Screen.Splash.route) { inclusive = true }
                    }
                },
                onNavigateToHome = {
                    navController.navigate(Screen.Home.route) {
                        popUpTo(Screen.Splash.route) { inclusive = true }
                    }
                }
            )
        }

        // Authentication
        composable(Screen.Login.route) {
            LoginScreen(
                onNavigateToRegister = {
                    navController.navigate(Screen.Register.route)
                },
                onLoginSuccess = { user ->
                    when {
                        user.targetLanguage == null -> {
                            navController.navigate(Screen.LanguageSelection.route) {
                                popUpTo(Screen.Login.route) { inclusive = true }
                            }
                        }
                        user.level == null && !user.placementTestCompleted -> {
                            navController.navigate(Screen.LevelSelection.route) {
                                popUpTo(Screen.Login.route) { inclusive = true }
                            }
                        }
                        else -> {
                            navController.navigate(Screen.Home.route) {
                                popUpTo(Screen.Login.route) { inclusive = true }
                            }
                        }
                    }
                }
            )
        }

        composable(Screen.Register.route) {
            RegisterScreen(
                onNavigateToLogin = {
                    navController.popBackStack()
                },
                onRegisterSuccess = {
                    navController.navigate(Screen.LanguageSelection.route) {
                        popUpTo(Screen.Register.route) { inclusive = true }
                    }
                }
            )
        }

        // Onboarding
        composable(Screen.LanguageSelection.route) {
            LanguageSelectionScreen(
                onLanguageSelected = {
                    navController.navigate(Screen.LevelSelection.route) {
                        popUpTo(Screen.LanguageSelection.route) { inclusive = true }
                    }
                }
            )
        }

        composable(Screen.LevelSelection.route) {
            LevelSelectionScreen(
                onTakePlacementTest = {
                    navController.navigate(Screen.PlacementTest.route)
                },
                onLevelSelected = {
                    navController.navigate(Screen.Home.route) {
                        popUpTo(Screen.LevelSelection.route) { inclusive = true }
                    }
                }
            )
        }

        // Placement Test
        composable(Screen.PlacementTest.route) {
            PlacementTestScreen(
                onTestComplete = { testId ->
                    navController.navigate(Screen.PlacementTestResults.createRoute(testId)) {
                        popUpTo(Screen.PlacementTest.route) { inclusive = true }
                    }
                },
                onBack = {
                    navController.popBackStack()
                }
            )
        }

        composable(
            route = Screen.PlacementTestResults.route,
            arguments = listOf(navArgument(NavArgs.TEST_ID) { type = NavType.StringType })
        ) {
            PlacementTestResultsScreen(
                onContinue = {
                    navController.navigate(Screen.Home.route) {
                        popUpTo(Screen.PlacementTestResults.route) { inclusive = true }
                    }
                },
                onRetake = {
                    navController.navigate(Screen.PlacementTest.route) {
                        popUpTo(Screen.PlacementTestResults.route) { inclusive = true }
                    }
                }
            )
        }

        // Main App
        composable(Screen.Home.route) {
            HomeScreen(
                onNavigateToVocabulary = { navController.navigate(Screen.Vocabulary.route) },
                onNavigateToGrammar = { navController.navigate(Screen.Grammar.route) },
                onNavigateToWriting = { navController.navigate(Screen.Writing.route) },
                onNavigateToPhonetics = { navController.navigate(Screen.Phonetics.route) },
                onNavigateToConversation = { navController.navigate(Screen.ConversationTopics.route) },
                onNavigateToProgress = { navController.navigate(Screen.Progress.route) },
                onNavigateToAchievements = { navController.navigate(Screen.Achievements.route) },
                onLogout = {
                    navController.navigate(Screen.Login.route) {
                        popUpTo(Screen.Home.route) { inclusive = true }
                    }
                },
                isDarkTheme = isDarkTheme,
                onToggleTheme = onToggleTheme
            )
        }

        // Learning Modules
        composable(Screen.Vocabulary.route) {
            VocabularyScreen(
                onBack = { navController.popBackStack() }
            )
        }

        composable(Screen.Grammar.route) {
            GrammarScreen(
                onBack = { navController.popBackStack() }
            )
        }

        composable(Screen.Writing.route) {
            WritingScreen(
                onBack = { navController.popBackStack() }
            )
        }

        composable(Screen.Phonetics.route) {
            PhoneticsScreen(
                onBack = { navController.popBackStack() }
            )
        }

        composable(Screen.ConversationTopics.route) {
            ConversationTopicsScreen(
                onTopicSelected = { sessionId ->
                    navController.navigate(Screen.Conversation.createRoute(sessionId)) {
                        popUpTo(Screen.ConversationTopics.route) { inclusive = true }
                    }
                },
                onBack = { navController.popBackStack() }
            )
        }

        composable(
            route = Screen.Conversation.route,
            arguments = listOf(navArgument(NavArgs.SESSION_ID) { type = NavType.StringType })
        ) {
            ConversationScreen(
                onBack = { navController.popBackStack() },
                onChangeTopic = {
                    navController.navigate(Screen.ConversationTopics.route) {
                        popUpTo(Screen.Conversation.route) { inclusive = true }
                    }
                }
            )
        }

        // Progress & Achievements
        composable(Screen.Progress.route) {
            ProgressScreen(
                onBack = { navController.popBackStack() }
            )
        }

        composable(Screen.Achievements.route) {
            AchievementsScreen(
                onBack = { navController.popBackStack() }
            )
        }
    }
}
