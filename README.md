# GroupBuy - Production-Ready Fullstack MVP

A modern group-buying platform built with FastAPI backend, React frontend, and containerized infrastructure.

## Project Structure

```
groupbuy/
├── .github/workflows/          # CI/CD pipelines
├── backend/                    # FastAPI application with SQLAlchemy ORM
│   ├── migrations/            # Database migrations
│   ├── app/
│   │   ├── api/               # API routers and endpoints
│   │   ├── models/            # SQLAlchemy ORM models
│   │   ├── schemas/           # Pydantic request/response schemas
│   │   ├── db.py              # Database configuration
│   │   ├── settings.py        # Application settings
│   │   └── main.py            # FastAPI application entry point
│   ├── Dockerfile
│   ├── alembic.ini            # Alembic configuration
│   └── requirements.txt        # Python dependencies
├── frontend/                   # React + Vite + TypeScript
│   ├── src/
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── infra/                      # Infrastructure and orchestration
│   ├── docker-compose.yml     # Local development environment
│   └── .env.example            # Environment variables template
└── README.md                   # This file
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.10+ (for local development)
- Node.js 18+ (for frontend development)
- PostgreSQL 15 (runs in Docker)

### Development Setup with Docker Compose

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd groupbuy
   ```

2. **Create environment file**
   ```bash
   cp infra/.env.example infra/.env
   ```
   Edit `infra/.env` with your desired configuration.

3. **Start all services**
   ```bash
   docker compose -f infra/docker-compose.yml up -d
   ```

   This will start:
   - PostgreSQL database on `localhost:5432`
   - FastAPI backend on `localhost:8000`
   - React frontend on `localhost:5173`

4. **Run database migrations**
   ```bash
   docker compose -f infra/docker-compose.yml exec backend alembic upgrade head
   ```

5. **Verify the setup**
   - Backend: Visit http://localhost:8000/api/v1/health
   - Frontend: Visit http://localhost:5173
   - API Docs: Visit http://localhost:8000/docs

### Local Development (Without Docker)

#### Backend Setup

1. **Create Python virtual environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database connection details
   ```

4. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

5. **Start the backend server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

#### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server**
   ```bash
   npm run dev
   ```

   Frontend will be available at `http://localhost:5173`

## Testing

### Backend Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_health.py
```

### Frontend Tests

```bash
# Run all tests
npm run test

# Watch mode
npm run test:watch

# Coverage
npm run test:coverage
```

## Environment Variables

### Backend Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Database Configuration
DATABASE_URL=postgresql+psycopg://buytogether:password@localhost:5432/buytogether

# Application Settings
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# CORS Configuration
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]

# API Configuration
API_V1_PREFIX=/api/v1
PROJECT_NAME=GroupBuy API
PROJECT_DESCRIPTION=Group buying platform API
PROJECT_VERSION=1.0.0
```

### Infra Environment Variables

Create a `.env` file in the `infra/` directory:

```env
# PostgreSQL Configuration
POSTGRES_USER=buytogether
POSTGRES_PASSWORD=secure_password_change_me
POSTGRES_DB=buytogether

# Backend Configuration
DATABASE_URL=postgresql+psycopg://buytogether:secure_password_change_me@postgres:5432/buytogether
```

See `infra/.env.example` for a complete template.

## Database Migrations

### Creating a new migration

1. **Create migration after modifying models**
   ```bash
   cd backend
   alembic revision --autogenerate -m "describe your changes"
   ```

2. **Review the generated migration file** in `migrations/versions/`

3. **Apply the migration**
   ```bash
   alembic upgrade head
   ```

### Manual migration

```bash
alembic revision -m "migration description"
# Edit the migration file manually
alembic upgrade head
```

### Downgrade database

```bash
# Downgrade to specific revision
alembic downgrade <revision>

# Downgrade one step
alembic downgrade -1
```

## API Documentation

Once the backend is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Architecture

### Backend Technology Stack

- **Framework**: FastAPI
- **ORM**: SQLAlchemy 2.0
- **Database**: PostgreSQL with Alembic migrations
- **Validation**: Pydantic v2
- **Server**: Uvicorn ASGI server
- **Logging**: Structured logging with request IDs

### Frontend Technology Stack

- **Framework**: React 18
- **Build Tool**: Vite
- **Language**: TypeScript
- **Styling**: CSS Modules / TailwindCSS
- **HTTP Client**: Axios / Fetch API

### Infrastructure

- **Containerization**: Docker
- **Orchestration**: Docker Compose (development)
- **Database**: PostgreSQL 15
- **CI/CD**: GitHub Actions

## Key Features & Domain Models

### Deal Model
- UUID primary key with timezone-aware timestamps
- Status tracking (ACTIVE, CLOSED, FAILED)
- Price in cents to avoid float precision issues
- Configurable minimum quantity to close deal
- Automatic updated_at timestamp on changes

### Participant Model
- Tracks individual participants in a deal
- State management (JOINED, INVITED_TO_PAY, PAID, CANCELLED)
- Unique constraint on (deal_id, email) to prevent duplicates
- Cascade delete when deal is removed
- Indexed on deal_id and email for fast lookups

## Docker Commands

```bash
# View logs for all services
docker compose -f infra/docker-compose.yml logs -f

# View logs for specific service
docker compose -f infra/docker-compose.yml logs -f backend
docker compose -f infra/docker-compose.yml logs -f postgres
docker compose -f infra/docker-compose.yml logs -f frontend

# Stop all services
docker compose -f infra/docker-compose.yml down

# Remove all data (fresh start)
docker compose -f infra/docker-compose.yml down -v

# Rebuild images
docker compose -f infra/docker-compose.yml build --no-cache

# Run a command in a container
docker compose -f infra/docker-compose.yml exec backend bash
docker compose -f infra/docker-compose.yml exec postgres psql -U buytogether -d buytogether
```

## Common Issues

### Database Connection Error
If you get a database connection error:
1. Ensure PostgreSQL container is healthy: `docker compose -f infra/docker-compose.yml ps`
2. Check DATABASE_URL format in your environment file
3. Verify credentials in `.env` match `docker-compose.yml`

### Port Already in Use
If ports 5432, 8000, or 5173 are already in use:
1. Change port mappings in `docker-compose.yml`
2. Or stop conflicting services on your machine

### Module Not Found Errors (Backend)
1. Ensure you've activated the Python virtual environment
2. Run `pip install -r requirements.txt` again
3. Ensure PYTHONPATH includes the backend directory

### Frontend Build Errors
1. Delete `node_modules` and `package-lock.json`
2. Run `npm install` again
3. Check Node.js version matches requirement (18+)

## Contributing

1. Create a feature branch
2. Make your changes
3. Write tests for new functionality
4. Submit a pull request

## License

Proprietary - All rights reserved

## Support

For issues and questions, create an issue in the repository.
