# {{project_name}} Environment Configuration
# Copy this file to .env and update the values

# ===========================================
# Application Settings
# ===========================================
PROJECT_NAME={{project_name}}
PROJECT_DESCRIPTION=A FastAPI project built with FastAPI-New
VERSION=0.1.0

# Environment: dev, staging, prod
ENVIRONMENT=dev
DEBUG=true

# ===========================================
# Server Settings
# ===========================================
HOST=0.0.0.0
PORT=8000
RELOAD=true
WORKERS=1

# ===========================================
# API Settings
# ===========================================
API_V1_PREFIX=/api/v1
OPENAPI_URL=true
DOCS_URL=true
REDOC_URL=true

# ===========================================
# Database Settings
# ===========================================
# Engine options: postgres, mysql, sqlite, mongodb
DATABASE_ENGINE=sqlite

# SQLite (default for development)
DATABASE_URL=sqlite:///./app.db

# PostgreSQL
# DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# MySQL
# DATABASE_URL=mysql://user:password@localhost:3306/dbname

# MongoDB
# DATABASE_URL=mongodb://user:password@localhost:27017/dbname

DATABASE_ECHO=false
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10

# ===========================================
# Security Settings
# ===========================================
# IMPORTANT: Change this in production!
SECRET_KEY=your-super-secret-key-change-this-in-production

# JWT Settings
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ALGORITHM=HS256

# ===========================================
# CORS Settings
# ===========================================
# Comma-separated list of allowed origins
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=["*"]
CORS_ALLOW_HEADERS=["*"]

# ===========================================
# Rate Limiting
# ===========================================
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# ===========================================
# Logging
# ===========================================
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# ===========================================
# Redis (optional)
# ===========================================
# REDIS_URL=redis://localhost:6379/0

# ===========================================
# Email (optional)
# ===========================================
# SMTP_HOST=smtp.example.com
# SMTP_PORT=587
# SMTP_USER=your-email@example.com
# SMTP_PASSWORD=your-email-password
# SMTP_FROM=noreply@example.com
# SMTP_TLS=true

# ===========================================
# AWS (optional)
# ===========================================
# AWS_ACCESS_KEY_ID=your-access-key
# AWS_SECRET_ACCESS_KEY=your-secret-key
# AWS_REGION=us-east-1
# AWS_S3_BUCKET=your-bucket-name

# ===========================================
# Sentry (optional)
# ===========================================
# SENTRY_DSN=https://your-sentry-dsn
