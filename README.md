# buyTogether

Monorepo scaffold for the buyTogether fullstack application.

This repository contains scaffolding only (no business logic yet).

Repository layout:

- [backend](backend) — FastAPI service (Python)
- [frontend](frontend) — React + Vite + TypeScript app
- [infra](infra) — Docker Compose and helper scripts for local development
- [.github/workflows](.github/workflows) — CI workflows for tests and lint

## Development (Docker Compose)

1. Copy the example env file to a project `.env` (compose reads repository root `.env`):

   - Copy `infra/.env.example` -> `.env` and edit values as needed

2. Start services (from repository root):

```powershell
docker compose -f infra/docker-compose.yml up --build
```

Services expose the following by default:

- Backend: http://localhost:8000
- Frontend (Vite dev server): http://localhost:5173

## Run tests

- Backend (locally):

```powershell
cd backend
python -m pip install -r requirements.txt
pytest
```

- Frontend (locally):

```powershell
cd frontend
npm install
npm run test
```

## CI

GitHub Actions workflows are in [.github/workflows/ci.yml](.github/workflows/ci.yml).

## Environment files required

- Repository root `.env` — used by `infra/docker-compose.yml` (start from `infra/.env.example`)
- Optionally, `backend/.env` or `frontend/.env` if you prefer service-local env files (examples may be added later)

If you need help running the scaffold or want me to add Dockerfiles for the frontend, tell me and I will add them.

---
Small note: this repo currently contains scaffolding only; no production business logic has been implemented yet.
