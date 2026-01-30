#!/usr/bin/env bash

# Language Learning App - Windows 11 Setup (Git Bash / WSL)
# Notes:
# - Run in Git Bash or WSL. For PowerShell, follow README manual steps.
# - Recommended Python: 3.12.x (avoid 3.13 wheels issues on Windows).

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }
print_info() { echo -e "→ $1"; }

# Verify python
print_info "Checking Python installation..."
if command -v python &> /dev/null; then
  PYTHON_CMD="python"
elif command -v py &> /dev/null; then
  PYTHON_CMD="py"
else
  print_error "Python not found. Install Python 3.12 (recommended) and retry."
  exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
print_success "Python $PYTHON_VERSION found"

# Warn on Python 3.13
if [[ "$PYTHON_VERSION" == 3.13* ]]; then
  print_warning "Python 3.13 detected. Some wheels may be missing on Windows."
  print_warning "Recommended: install Python 3.12 and rerun with: py -3.12"
fi

# Go to backend
cd backend

# Create venv
print_info "Creating Python virtual environment..."
if [ -d "venv" ]; then
  print_warning "Virtual environment already exists. Removing old environment..."
  rm -rf venv
fi

if [[ "$PYTHON_CMD" == "py" ]]; then
  $PYTHON_CMD -3.12 -m venv venv || $PYTHON_CMD -m venv venv
else
  $PYTHON_CMD -m venv venv
fi
print_success "Virtual environment created"

# Activate venv
print_info "Activating virtual environment..."
# shellcheck disable=SC1091
source venv/Scripts/activate
print_success "Virtual environment activated"

# Upgrade tooling
print_info "Upgrading pip/setuptools/wheel..."
python -m pip install --upgrade pip setuptools wheel --quiet
print_success "Tooling upgraded"

# Install dependencies
print_info "Installing Python dependencies (this may take a few minutes)..."
python -m pip install -r requirements.txt --quiet
print_success "All dependencies installed"

# Create credentials directory
print_info "Creating credentials directory..."
mkdir -p credentials
print_success "Credentials directory created"

# Create .env if missing
if [ ! -f ".env" ]; then
  print_info "Creating .env file with placeholders..."
  cat > .env << 'EOF'
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
EOF
  print_success ".env file created"
  print_warning "IMPORTANT: Edit backend/.env with your actual credentials."
else
  print_warning ".env file already exists. Skipping creation."
fi

# Initialize database
print_info "Initializing database..."
python << 'PYEOF'
from app.db.database import Base, engine
Base.metadata.create_all(bind=engine)
print("Database tables created successfully!")
PYEOF
print_success "Database initialized"

print_success "Windows 11 setup completed!"
print_info "Next: activate venv and run: uvicorn app.main:app --reload"
