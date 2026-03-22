# AI-Driven Internship Allocation System - Dashboard & Backend (PMIS)

> **Nominated for Smart India Hackathon (SIH) Nationals in Software Category**

This repository contains the **Frontend Dashboard** and **Backend Service** for an AI-driven internship allocation system. It is designed to visualize and manage optimum matches between candidates and internships using advanced skill-role mapping.

## Project Context
The system uses **Sentence-BERT** and **cosine similarity** for precise skill-role mapping and integrates a fairness-driven **Integer Linear Programming (ILP)** model (hosted in a separate repository) to promote balanced and transparent allocations.

This project specifically provides:
-   A **Scalable Full-Stack Dashboard** (React + TypeScript) for administrators to view candidates, internships, and allocation results.
-   A **Flask Backend** that acts as the API layer, interfacing with Supabase and serving the frontend.
-   **Supabase Integration** for secure and scalable data storage.

## Tech Stack
-   **Frontend**: React, TypeScript, Vite, Tailwind CSS
-   **Backend**: Python, Flask, Waitress (Production WSGI)
-   **Database**: Supabase (PostgreSQL)
-   **Deployment**: Railway, Docker

## Repository Structure
-   `app.py`: Flask backend, exposes API endpoints and serves the React frontend.
-   `src/`: React frontend source code.
-   `railway_start.sh`: Build script for Railway deployment (installs Python/Node deps, builds frontend, starts server).
-   `Dockerfile`: Container definition for reliable deployment.

---

## Developer Guide

### Environment Variables
Copy `.env.example` to `.env` and configure:
```ini
SUPABASE_URL=https://<your-project>.supabase.co
SUPABASE_KEY=<your-service-role-key>
CORS_ORIGINS=*
LOG_LEVEL=INFO
APP_ENV=production
```

### Local Development

#### 1. Backend (Flask)
```bash
# Windows PowerShell
python -m venv .venv
./.venv/Scripts/Activate.ps1
pip install -r requirements.txt

# Run Server
python app.py
# Server runs at http://127.0.0.1:5000
```

#### 2. Frontend (React)
```bash
# In a new terminal
npm install
npm run dev
# Frontend runs at http://localhost:5173
```
*Note: For local dev, configure `VITE_API_BASE=http://127.0.0.1:5000` in a frontend `.env` file if needed.*

### Deployment (Railway / Docker)
This project is optimized for **Railway**. It can be deployed as a single service comprising both the Python backend and the React frontend.

**Option A: Railway (Auto-Build)**
1.  Connect repository to Railway.
2.  Set environment variables.
3.  The `railway.toml` and `railway_start.sh` handle the build process:
    -   Installs Python & Node dependencies.
    -   Builds React app to `dist/`.
    -   Starts Flask, which serves `dist/index.html` as a SPA.

**Option B: Docker**
```bash
docker build -t pmis-app .
docker run -p 8000:8000 --env-file .env pmis-app
```

## API Endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | API Health Check |
| GET | `/api/internships` | List all internships |
| GET | `/api/data/<table_name>` | Generic Supabase table access |
