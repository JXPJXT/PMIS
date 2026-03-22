# 🎯 AI-Driven Internship Allocation System
### *Nominated for Smart India Hackathon (SIH) Nationals — Software Category*

> An end-to-end AI platform that matches candidates to internships using **Sentence-BERT semantic embeddings**, **cosine similarity scoring**, and a **fairness-driven Integer Linear Programming (ILP)** optimizer — all managed through a scalable full-stack dashboard.

---

## 📐 System Architecture

This project is split into two repositories that work together:

```
┌─────────────────────────────────┐      ┌──────────────────────────────────┐
│   PMIS (This Repo)              │      │   AI Engine (Separate Repo)      │
│                                 │      │                                  │
│  React + TypeScript Dashboard   │      │  Sentence-BERT Embeddings        │
│  Flask REST API                 │◄────►│  Cosine Similarity Scoring       │
│  Supabase Integration           │      │  ILP Fairness Optimizer          │
└─────────────────────────────────┘      └──────────────────────────────────┘
                    │                                    │
                    └──────────────┬─────────────────────┘
                                   ▼
                          ┌─────────────────┐
                          │    Supabase     │
                          │  (PostgreSQL)   │
                          └─────────────────┘
```

---

## 🧠 AI Engine — Core Logic

The AI engine handles compatibility scoring and allocation optimization.

### How It Works

**1. Skill-Role Mapping**
Candidate profiles (skills, projects) and internship requirements are encoded into semantic vector embeddings using **Sentence-BERT**, capturing meaning beyond simple keyword matching.

**2. Compatibility Scoring**
Cosine similarity is computed between candidate and internship embeddings, producing a normalized compatibility score from **0 to 1**.

**3. Fairness-Aware Allocation**
An **Integer Linear Programming (ILP)** model maximizes total compatibility across all assignments while enforcing fairness constraints such as gender and social category balance — ensuring equitable distribution of opportunities.

### AI Engine — Project Structure

```
ai-engine/
├── speed_optimized_runner.py     # Main entry point: fetch → score → allocate → push
└── pipeline/
    ├── model.py                  # ML orchestration (Embedder, Scorer, Allocator)
    ├── embedding.py              # Sentence-BERT encoding logic
    ├── scoring.py                # Cosine similarity matrix calculation
    └── allocation.py             # ILP solver implementation
```

### AI Engine — Setup & Usage

**Install dependencies**
```bash
pip install -r requirements.txt
```

**Set environment variables**
```ini
SUPABASE_URL=https://<your-project>.supabase.co
SUPABASE_KEY=<your-service-role-key>
MODEL_PATH=models/allocation_model.pkl   # default
```

**Run the allocation pipeline**
```bash
# For a specific internship
python speed_optimized_runner.py <internship_id>

# Interactive mode (prompts for Internship ID)
python speed_optimized_runner.py
```

**What happens when you run it:**
1. Fetches all candidates and the target internship from Supabase
2. Generates Sentence-BERT embeddings and computes compatibility scores
3. Runs the ILP optimizer with fairness constraints
4. Writes final ranked results back to the `results` table in Supabase

> **Performance Note:** The `SpeedOptimizedSupabaseRunner` caches Supabase data locally, eliminating repeated API round-trips during batch processing.

---

## 🖥️ Dashboard & Backend (PMIS)

The PMIS repository provides the frontend dashboard and Flask API layer.

### Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React, TypeScript, Vite, Tailwind CSS |
| Backend | Python, Flask, Waitress (WSGI) |
| Database | Supabase (PostgreSQL) |
| Deployment | Railway, Docker |

### PMIS — Project Structure

```
pmis/
├── app.py                  # Flask backend: API endpoints + serves React SPA
├── src/                    # React frontend source
├── railway_start.sh        # Railway build script (deps → build → serve)
├── railway.toml            # Railway service configuration
└── Dockerfile              # Container definition
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+
- A [Supabase](https://supabase.com) project

### Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```ini
SUPABASE_URL=https://<your-project>.supabase.co
SUPABASE_KEY=<your-service-role-key>
CORS_ORIGINS=*
LOG_LEVEL=INFO
APP_ENV=production
```

### Local Development

**Backend (Flask) — Terminal 1**
```bash
# Create and activate virtual environment
python -m venv .venv

# Windows
./.venv/Scripts/Activate.ps1
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
python app.py
# → http://127.0.0.1:5000
```

**Frontend (React) — Terminal 2**
```bash
npm install
npm run dev
# → http://localhost:5173
```

> For local development, add `VITE_API_BASE=http://127.0.0.1:5000` to a frontend `.env` file to point the React app at your local Flask server.

---

## ☁️ Deployment

### Option A — Railway (Recommended)

1. Connect this repository to a Railway project.
2. Set the required environment variables in the Railway dashboard.
3. Railway uses `railway.toml` and `railway_start.sh` to automatically:
   - Install Python and Node.js dependencies
   - Build the React app into `dist/`
   - Start Flask, which serves `dist/index.html` as a Single Page Application

### Option B — Docker

```bash
docker build -t pmis-app .
docker run -p 8000:8000 --env-file .env pmis-app
```

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check — confirms API is live |
| `GET` | `/api/internships` | Returns all internship listings |
| `GET` | `/api/data/<table_name>` | Generic read access to any Supabase table |

---

## ✨ Key Features

- **Semantic Matching** — Goes beyond keyword matching; understands meaning using transformer-based embeddings
- **Fairness by Design** — ILP optimizer enforces demographic balance constraints, not just maximum score
- **Speed Optimized** — Local caching layer eliminates Supabase API latency during batch processing
- **Unified Deployment** — Single Railway/Docker service hosts both the API and the React SPA
- **Scalable Storage** — Supabase (PostgreSQL) handles candidates, internships, and results at scale

---

## 🏆 Recognition

This project was **nominated for Smart India Hackathon (SIH) Nationals** in the Software category — a national-level competition organized by the Government of India to encourage innovation among students.

---

## 📄 License

See [LICENSE](./LICENSE) for details.
