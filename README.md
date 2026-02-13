# Language Learning Application

A comprehensive AI-powered language learning platform built with FastAPI and Google Vertex AI, featuring interactive modules for conversation practice, writing assessment, grammar correction, phonetics training, and vocabulary flashcards with image generation.

## Table of Contents

- [Features](#features)
- [Live Demo](#live-demo)
- [System Architecture](#system-architecture)
- [Requirements](#requirements)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Configuration](#configuration)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Features

### Core Modules

1. **Conversation Practice**
   - Real-time AI-powered conversation simulation
   - Context-aware responses with difficulty adaptation
   - Conversation history tracking
   - Performance feedback and tips

2. **Writing Assessment**
   - Dual AI validation system for accuracy
   - Comprehensive feedback on grammar, vocabulary, and coherence
   - CEFR level assessment
   - Detailed improvement suggestions

3. **Grammar Correction**
   - Instant grammar analysis and correction
   - Explanations for corrections
   - Learning-focused feedback

4. **Phonetics Training**
   - Voice recording transcription
   - Pronunciation analysis
   - Feedback on articulation and tips for improvement

5. **Vocabulary Flashcards**
   - AI-generated contextual images
   - Spaced repetition learning
   - Progress tracking
   - Image preloading for smooth experience

6. **Placement Test**
   - Comprehensive language proficiency assessment
   - CEFR level determination
   - Personalized learning recommendations

### Technical Features

- RESTful API with FastAPI
- JWT-based authentication with secure password hashing
- SQLAlchemy ORM with SQLite/PostgreSQL support
- Rate limiting to prevent abuse
- Google Vertex AI integration (Gemini models)
- Image generation with Imagen 3
- Comprehensive error handling
- CORS support for web clients

## Live Demo

You can try FluencIA online at: **https://fluencia.vercel.app**

**Important Note:** The first page load may take 60-80 seconds as the server needs to wake up from sleep mode. Please be patient during the initial load. Once the server is active, the application will respond normally.

## System Architecture

```
┌─────────────────┐
│   Web Client    │
│  (Simple HTML)  │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│  FastAPI Server │
│   (Backend)     │
├─────────────────┤
│  - Auth         │
│  - Rate Limit   │
│  - Endpoints    │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌──────────────┐
│SQLite/ │ │ Vertex AI    │
│Postgres│ │ (Gemini 2.5) │
└────────┘ └──────────────┘
```

## Requirements

- Python 3.8+
- Google Cloud account with Vertex AI enabled
- SQLite (default) or PostgreSQL (production)
- Virtual environment (recommended)

## Quick Start

### 1. Automated Setup (Recommended)

Run the setup script to automatically configure everything:

```bash
cd language-app
chmod +x setup.sh
./setup.sh
```

**Windows 11 (Git Bash or WSL):**

```bash
cd language-app
chmod +x setup_windows11.sh
./setup_windows11.sh
```

**WSL note:** If you see `WSL_E_DEFAULT_DISTRO_NOT_FOUND`, you need to install a distro first.

```powershell
wsl.exe --list --online
wsl.exe --install Ubuntu
```

Alternatively, use **Git Bash** (recommended if you do not want WSL) or follow the manual PowerShell steps in this README.

This script will:
- Create and activate a Python virtual environment
- Install all dependencies
- Generate a `.env` file with placeholders
- Initialize the database
- Set up necessary directories

### 2. Configure Environment Variables

Edit `backend/.env` with your credentials:

```env
# Database Configuration
DATABASE_URL=sqlite:///./language_app.db

# LLM (Gemini / AI Studio API key)
LLM_API_KEY=your-llm-api-key

# STT (Gemini STT API key)
STT_API_KEY=your-stt-api-key

# JWT Authentication
JWT_SECRET_KEY=your-secret-key-here-generate-with-openssl-rand-hex-32
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google Cloud Vertex AI
VERTEX_AI_PROJECT_ID=your-google-cloud-project-id
VERTEX_AI_LOCATION=us-central1
VERTEX_AI_CREDENTIALS_PATH=./credentials/your-service-account-key.json
USE_VERTEX_AI=True
```

**Important:** To enable the achievements functionality, ensure you're using `language_app.db` as shown above, not a test database. The achievements system requires the main production database to function properly.

### 3. Add Google Cloud Credentials

1. Create a service account in Google Cloud Console
2. Enable Vertex AI API
3. Download the JSON key file
4. Place it in `backend/credentials/` directory
5. Update `VERTEX_AI_CREDENTIALS_PATH` in `.env`

#### Vertex AI JSON key setup (step-by-step)

**Important:** Google AI Studio API keys are *not* the same as Vertex AI JSON keys.
This project needs a **service account JSON key** from Google Cloud Console.

1. Go to Google Cloud Console: `https://console.cloud.google.com/`
2. Select or create a GCP project, then enable **Vertex AI API**.
3. Go to **IAM & Admin → Service Accounts** and create a service account.
4. Grant roles:
   - `Vertex AI User`
   - `Service Account User`
5. Open the service account → **Keys** → **Add Key** → **Create new key**.
6. Choose **JSON** and download the file.
7. Move it to: `backend/credentials/`
8. Set the path in `.env`:

```env
VERTEX_AI_PROJECT_ID=your-google-cloud-project-id
VERTEX_AI_LOCATION=us-central1
VERTEX_AI_CREDENTIALS_PATH=./credentials/your-service-account-key.json
USE_VERTEX_AI=True
```

**Security note:** never commit JSON keys. Add `backend/credentials/` to `.gitignore`.

### 4. Start the Server

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn app.main:app --reload
```

The API will be available at: `http://localhost:8000`

### 5. Launch the Web Interface

Open `simple-web-interface/index.html` in your browser or start a local server:

```bash
cd simple-web-interface
python -m http.server 8080
```

Then navigate to: `http://localhost:8080`

## Project Structure

```
language-app/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── endpoints/
│   │   │   │   │   ├── auth.py          # Authentication endpoints
│   │   │   │   │   ├── conversation.py  # Conversation module
│   │   │   │   │   ├── writing.py       # Writing assessment
│   │   │   │   │   ├── grammar.py       # Grammar correction
│   │   │   │   │   ├── phonetics.py     # Phonetics training
│   │   │   │   │   ├── vocabulary.py    # Flashcards
│   │   │   │   │   └── placement_test.py # Placement test
│   │   │   │   ├── api.py               # API router
│   │   │   │   └── deps.py              # Dependencies
│   │   ├── core/
│   │   │   ├── config.py                # Configuration
│   │   │   └── security.py              # Security utilities
│   │   ├── db/
│   │   │   ├── database.py              # Database setup
│   │   │   └── models.py                # SQLAlchemy models
│   │   ├── schemas/
│   │   │   └── *.py                     # Pydantic schemas
│   │   ├── services/
│   │   │   └── *.py                     # Business logic
│   │   └── main.py                      # FastAPI application
│   ├── credentials/                      # Google Cloud credentials
│   ├── .env                             # Environment variables
│   ├── requirements.txt                 # Python dependencies
│   └── main.py                          # Application entry point
├── simple-web-interface/
│   ├── index.html                       # Main web interface
│   ├── app.js                           # Frontend JavaScript
│   ├── styles.css                       # Styling
│   └── start.sh                         # Web server script
├── docs/                                # Documentation (to be created)
│   ├── user-guide.md
│   ├── project-management-report.md
│   ├── user-acceptance-testing.md
│   └── safety-and-reflection.md
├── setup.sh                             # Automated setup script
└── README.md                            # This file
```

## API Documentation

### Authentication

All endpoints (except `/auth/register` and `/auth/login`) require JWT authentication.

**Register:**
```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password",
  "full_name": "John Doe"
}
```

**Login:**
```bash
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=secure_password
```

**Returns:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### Endpoints Overview

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/v1/auth/register` | POST | Register new user | No |
| `/api/v1/auth/login` | POST | Login user | No |
| `/api/v1/auth/me` | GET | Get current user | Yes |
| `/api/v1/conversation/start` | POST | Start conversation | Yes |
| `/api/v1/conversation/message` | POST | Send message | Yes |
| `/api/v1/conversation/history` | GET | Get conversation history | Yes |
| `/api/v1/writing/submit` | POST | Submit writing for assessment | Yes |
| `/api/v1/writing/history` | GET | Get writing history | Yes |
| `/api/v1/grammar/correct` | POST | Get grammar corrections | Yes |
| `/api/v1/phonetics/analyze` | POST | Analyze pronunciation | Yes |
| `/api/v1/vocabulary/flashcard` | GET | Get random flashcard | Yes |
| `/api/v1/vocabulary/generate` | POST | Generate custom flashcard | Yes |
| `/api/v1/placement-test/start` | POST | Start placement test | Yes |
| `/api/v1/placement-test/submit` | POST | Submit test answers | Yes |

### Interactive API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Configuration

### Database Options

**SQLite (Default - Development):**
```env
DATABASE_URL=sqlite:///./language_app.db
```

**PostgreSQL (Production):**
```env
DATABASE_URL=postgresql://user:password@localhost:5432/language_app
```

### Security Configuration

**Generate a secure SECRET_KEY:**
```bash
openssl rand -hex 32
```

**Token Expiration:**
Adjust `ACCESS_TOKEN_EXPIRE_MINUTES` in `.env` (default: 30 minutes)

### Rate Limiting

Configure in `.env`:
```env
RATE_LIMIT_PER_MINUTE=20
```

## Development

### Setting Up Development Environment

1. Clone the repository
2. Run `./setup.sh`
3. Activate virtual environment: `source backend/venv/bin/activate`
4. Make your changes
5. Test thoroughly

### Code Style

- Follow PEP 8 for Python code
- Use type hints where applicable
- Write docstrings for functions and classes
- Keep functions focused and modular

### Database Migrations

When modifying models in `app/db/models.py`:

```bash
# For development, recreate the database
rm backend/language_app.db
python -c "from app.db.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

For production, consider using Alembic for migrations.

### Adding New Endpoints

1. Create endpoint in `app/api/v1/endpoints/`
2. Define Pydantic schemas in `app/schemas/`
3. Implement business logic in `app/services/`
4. Add router to `app/api/v1/api.py`
5. Test with the interactive docs

## Testing

### Manual Testing

Use the Swagger UI at `http://localhost:8000/docs` for interactive testing.

### API Testing Scripts

Test authentication:
```bash
cd backend
python test_rate_limit.py
```

Test Vertex AI integration:
```bash
python test_vertex_ai.py
```

### Frontend Testing

Open `simple-web-interface/test-auth.html` to test authentication flows.

## Deployment

### Production Checklist

- [ ] Set strong `SECRET_KEY` in production
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable HTTPS
- [ ] Set appropriate CORS origins in `app/main.py`
- [ ] Configure rate limiting appropriately
- [ ] Set up proper logging
- [ ] Use environment-specific `.env` files
- [ ] Secure Google Cloud credentials
- [ ] Set up database backups
- [ ] Configure reverse proxy (nginx/Apache)
- [ ] Use process manager (systemd/supervisor)

### Docker Deployment

A `Dockerfile` is provided in the backend directory:

```bash
cd backend
docker build -t language-app .
docker run -p 8000:8000 --env-file .env language-app
```

### Cloud Deployment Options

- Google Cloud Run
- AWS Elastic Beanstalk
- Heroku
- Azure App Service

## Troubleshooting

### Common Issues

**1. "ModuleNotFoundError" when starting the server**

Ensure you've activated the virtual environment:
```bash
source backend/venv/bin/activate  # macOS/Linux
backend\venv\Scripts\activate     # Windows
```

**2. "Could not load credentials" error**

- Verify `CREDENTIALS_PATH` in `.env` is correct
- Ensure the JSON key file exists in the specified location
- Check that Vertex AI API is enabled in Google Cloud

**3. "Database is locked" error**

SQLite doesn't handle concurrent writes well. Consider:
- Using PostgreSQL for production
- Reducing concurrent requests
- Implementing request queuing

**4. Rate limit errors**

Adjust `RATE_LIMIT_PER_MINUTE` in `.env` or implement user-based rate limiting.

**5. Image generation failures**

- Verify Vertex AI quota
- Check that Imagen API is enabled
- Ensure credentials have proper permissions

**6. CORS errors in web interface**

Update allowed origins in `backend/app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Add your frontend URL
    ...
)
```

### Debug Mode

Enable verbose logging by running:
```bash
uvicorn app.main:app --reload --log-level debug
```

### Getting Help

- Check the [API Documentation](http://localhost:8000/docs)
- Review error logs in the terminal
- Verify environment variables in `.env`
- Test individual components with provided test scripts

## Contributing

We welcome contributions! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit with clear messages (`git commit -m 'Add amazing feature'`)
6. Push to your branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### GenAI Usage Acknowledgment

This project was developed with assistance from generative AI tools for:
- Code generation and refactoring
- Documentation creation
- Debugging and problem-solving
- API design consultation

All AI-generated code has been reviewed, tested, and validated by human developers.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Cloud Vertex AI for AI capabilities
- FastAPI framework for the robust backend
- SQLAlchemy for database management
- The open-source community for excellent tools and libraries

---

**Version:** 1.0.0
**Last Updated:** January 2026
**Maintained By:** Language Learning App Team
