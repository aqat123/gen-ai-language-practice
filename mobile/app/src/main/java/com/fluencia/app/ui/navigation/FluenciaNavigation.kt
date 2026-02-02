package com.fluencia.app.ui.navigation

/**
 * Sealed class defining all navigation routes in the FluencIA app.
 */
sealed class Screen(val route: String) {
    /** Splash screen shown during app startup */
    object Splash : Screen("splash")
    
    /** Login screen for existing users */
    object Login : Screen("login")
    
    /** Registration screen for new users */
    object Register : Screen("register")
    
    /** Language selection screen after registration */
    object LanguageSelection : Screen("language_selection")
    
    /** Level selection screen (manual or placement test) */
    object LevelSelection : Screen("level_selection")
    
    /** Placement test flow */
    object PlacementTest : Screen("placement_test")
    
    /** Placement test results screen */
    object PlacementTestResults : Screen("placement_test_results/{testId}") {
        fun createRoute(testId: String) = "placement_test_results/$testId"
    }
    
    /** Main module selection screen (home) */
    object Home : Screen("home")
    
    /** Vocabulary flashcard practice */
    object Vocabulary : Screen("vocabulary")
    
    /** Grammar practice */
    object Grammar : Screen("grammar")
    
    /** Writing practice */
    object Writing : Screen("writing")
    
    /** Phonetics/pronunciation practice */
    object Phonetics : Screen("phonetics")
    
    /** Conversation practice - topic selection */
    object ConversationTopics : Screen("conversation_topics")
    
    /** Active conversation session */
    object Conversation : Screen("conversation/{sessionId}") {
        fun createRoute(sessionId: String) = "conversation/$sessionId"
    }
    
    /** Progress dashboard */
    object Progress : Screen("progress")
    
    /** Achievements screen */
    object Achievements : Screen("achievements")
    
    /** Settings screen */
    object Settings : Screen("settings")
}

/**
 * Navigation arguments keys.
 */
object NavArgs {
    const val TEST_ID = "testId"
    const val SESSION_ID = "sessionId"
    const val TOPIC = "topic"
}
