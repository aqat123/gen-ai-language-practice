# FluencIA Mobile App

A comprehensive Android mobile application for the FluencIA AI-powered language learning platform, built with Kotlin and Jetpack Compose.

## Features

The mobile app implements all the features from the backend API:

### Core Modules

1. **Authentication**
   - User registration and login
   - JWT token management
   - Secure local storage with DataStore

2. **Placement Test**
   - 18-question adaptive test
   - Vocabulary, grammar, and reading sections
   - CEFR level determination (A1-C2)
   - Personalized recommendations

3. **Vocabulary Practice**
   - AI-generated flashcards with images
   - Spaced Repetition System (SRS)
   - Multiple choice quizzes
   - Progress tracking

4. **Grammar Practice**
   - AI-generated grammar questions
   - Topic-based exercises
   - Immediate feedback with explanations

5. **Writing Practice**
   - Curated writing prompts
   - Free-form writing option
   - AI-powered feedback and corrections
   - Score assessment

6. **Pronunciation Practice**
   - AI-generated practice phrases
   - Audio recording capability
   - Speech-to-text transcription
   - Word-level pronunciation feedback

7. **Conversation Practice**
   - Topic-based conversations
   - Real-time AI chat partner
   - Automatic grammar corrections
   - Learning tips

8. **Progress Tracking**
   - Overall progress dashboard
   - Module-specific statistics
   - Level advancement system
   - XP rewards

9. **Achievements**
   - Unlockable achievements
   - Progress tracking for locked achievements
   - Tier-based rewards (Bronze to Diamond)

## Architecture

The app follows **Clean Architecture** principles with **MVVM** pattern:

```
app/
├── data/                    # Data layer
│   ├── api/                 # API service and interceptors
│   ├── local/               # Local storage (DataStore)
│   ├── model/               # Data models
│   └── repository/          # Repositories
├── di/                      # Dependency injection modules
├── ui/                      # UI layer
│   ├── components/          # Reusable Composables
│   ├── navigation/          # Navigation setup
│   ├── screens/             # Screen-specific code
│   │   ├── auth/            # Login/Register
│   │   ├── conversation/    # Conversation module
│   │   ├── grammar/         # Grammar module
│   │   ├── home/            # Home screen
│   │   ├── onboarding/      # Language/Level selection
│   │   ├── phonetics/       # Phonetics module
│   │   ├── placementtest/   # Placement test
│   │   ├── progress/        # Progress & Achievements
│   │   ├── splash/          # Splash screen
│   │   ├── vocabulary/      # Vocabulary module
│   │   └── writing/         # Writing module
│   └── theme/               # App theme
└── FluenciaApplication.kt   # Application class
```

## Tech Stack

- **Language**: Kotlin
- **UI Framework**: Jetpack Compose with Material Design 3
- **Navigation**: Navigation Compose
- **Dependency Injection**: Hilt
- **Networking**: Retrofit + OkHttp
- **JSON Parsing**: Gson
- **Local Storage**: DataStore Preferences
- **Async Operations**: Kotlin Coroutines + Flow
- **Image Loading**: Coil
- **Permissions**: Accompanist Permissions

## Requirements

- Android Studio Hedgehog (2023.1.1) or later
- Android SDK 26+ (Android 8.0)
- Target SDK 34 (Android 14)
- JDK 17

## Setup

### 1. Open in Android Studio

Open the `mobile/` directory in Android Studio.

### 2. Configure API URL

The app is configured to connect to `http://10.0.2.2:8000/api/v1` by default, which maps to localhost when running on an Android emulator.

To change the API URL, edit `app/build.gradle.kts`:

```kotlin
buildConfigField("String", "API_BASE_URL", "\"YOUR_API_URL\"")
```

### 3. Build and Run

```bash
./gradlew assembleDebug
```

Or use the Run button in Android Studio.

### 4. Running the Backend

Make sure the FastAPI backend is running:

```bash
cd ../backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Project Structure

### Data Layer

- **Models**: Kotlin data classes matching backend schemas
- **API Service**: Retrofit interface with all endpoints
- **Repositories**: Abstract data sources for the domain layer
- **TokenManager**: Secure token storage using DataStore

### UI Layer

- **Screens**: Full-screen Composables with their ViewModels
- **Components**: Reusable UI components
- **Theme**: Material 3 color scheme and typography

## Key Components

### Navigation

The app uses Navigation Compose with a sealed class for type-safe routes:

```kotlin
sealed class Screen(val route: String) {
    object Login : Screen("login")
    object Home : Screen("home")
    // ...
}
```

### State Management

Each screen uses a ViewModel with UI state represented as sealed classes:

```kotlin
sealed class VocabularyUiState {
    object Loading : VocabularyUiState()
    data class Flashcard(...) : VocabularyUiState()
    data class Error(val message: String) : VocabularyUiState()
}
```

### API Authentication

The `AuthInterceptor` automatically adds JWT tokens to requests:

```kotlin
class AuthInterceptor @Inject constructor(
    private val tokenManager: TokenManager
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        // Add Bearer token to headers
    }
}
```

## Testing

### Unit Tests

```bash
./gradlew test
```

### Instrumented Tests

```bash
./gradlew connectedAndroidTest
```

## Building for Release

1. Generate a signing key
2. Configure signing in `app/build.gradle.kts`
3. Build the release APK:

```bash
./gradlew assembleRelease
```

## API Documentation

The app implements all endpoints from the FluencIA backend API. See the backend documentation for full API details.

## License

MIT License - see the root LICENSE file.

## Acknowledgments

- Built with Jetpack Compose
- Material Design 3
- Google Cloud Vertex AI (backend)
