# Test script for Windows
# Activate venv
& backend\.venv\Scripts\Activate.ps1

# Start the test DB
docker-compose -f infra/docker-compose.yml up -d db_test

# Wait for DB to be ready
Start-Sleep -Seconds 10

# Set env vars
$env:DATABASE_URL = "postgresql+psycopg://buytogether:password@localhost:5432/buytogether"
$env:TEST_DATABASE_URL = "postgresql+psycopg://buytogether:password@localhost:5433/buytogether_test"
$env:PYTHONPATH = "backend"

# Run pytest
pytest backend/tests -v