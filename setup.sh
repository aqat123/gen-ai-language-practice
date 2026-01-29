#!/bin/bash

# Language Learning Application - Automated Setup Script
# This script sets up the entire development environment

set -e  # Exit on error

echo "========================================="
echo "Language Learning App - Setup Script"
echo "========================================="
echo ""

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "→ $1"
}

# Check if Python 3 is installed
print_info "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_success "Python $PYTHON_VERSION found"

# Navigate to backend directory
cd backend

# Create virtual environment
print_info "Creating Python virtual environment..."
if [ -d "venv" ]; then
    print_warning "Virtual environment already exists. Removing old environment..."
    rm -rf venv
fi

python3 -m venv venv
print_success "Virtual environment created"

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Upgrade pip
print_info "Upgrading pip..."
pip install --upgrade pip --quiet
print_success "pip upgraded"

# Install dependencies
print_info "Installing Python dependencies (this may take a few minutes)..."
pip install -r requirements.txt --quiet
print_success "All dependencies installed"

# Create credentials directory
print_info "Creating credentials directory..."
mkdir -p credentials
print_success "Credentials directory created"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_info "Creating .env file from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_success ".env file created from template"
    else
        print_error ".env.example not found, creating default .env..."
        cat > .env << 'EOF'
# Database Configuration
DATABASE_URL=sqlite:///./language_app.db

# JWT Authentication
SECRET_KEY=your-secret-key-here-PLEASE-CHANGE-THIS-IN-PRODUCTION
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google Cloud Vertex AI Configuration
PROJECT_ID=your-google-cloud-project-id
LOCATION=us-central1
CREDENTIALS_PATH=./credentials/your-service-account-key.json

# Rate Limiting
RATE_LIMIT_PER_MINUTE=20

# Server Configuration
HOST=0.0.0.0
PORT=8000
EOF
        print_success ".env file created"
    fi
    print_warning "IMPORTANT: Edit backend/.env with your actual credentials!"
else
    print_warning ".env file already exists. Skipping creation."
fi

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    print_info "Creating .gitignore file..."
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment
.env
.env.local
.env.*.local

# Database
*.db
*.sqlite
*.sqlite3

# Credentials
credentials/
*.json
!requirements.json

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Testing
.pytest_cache/
.coverage
htmlcov/
EOF
    print_success ".gitignore created"
fi

# Initialize database
print_info "Initializing database..."
python3 << 'PYEOF'
from app.db.database import Base, engine
import os

# Create all tables
Base.metadata.create_all(bind=engine)
print("Database tables created successfully!")
PYEOF
print_success "Database initialized"

# Create docs directory structure
print_info "Creating documentation directory structure..."
cd ..
mkdir -p docs
print_success "Documentation directory created"

# Return to backend
cd backend

echo ""
echo "========================================="
print_success "Setup completed successfully!"
echo "========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Configure your environment:"
print_warning "   Edit backend/.env with your Google Cloud credentials"
echo ""
echo "2. Add Google Cloud Service Account key:"
print_info "   - Download your service account JSON key"
print_info "   - Place it in: backend/credentials/"
print_info "   - Update CREDENTIALS_PATH in .env"
echo ""
echo "3. Start the development server:"
print_info "   cd backend"
print_info "   source venv/bin/activate"
print_info "   uvicorn app.main:app --reload"
echo ""
echo "4. Access the application:"
print_info "   API: http://localhost:8000"
print_info "   API Docs: http://localhost:8000/docs"
print_info "   Web Interface: Open simple-web-interface/index.html"
echo ""
echo "5. For production deployment:"
print_warning "   - Change SECRET_KEY in .env (use: openssl rand -hex 32)"
print_warning "   - Use PostgreSQL instead of SQLite"
print_warning "   - Review security settings in app/main.py"
echo ""
print_success "Happy coding!"
echo ""
