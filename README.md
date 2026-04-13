# 🎯 PMIS — AI-Driven Internship Allocation System

### *Nominated for Smart India Hackathon (SIH) Nationals — Software Category*

> A full-stack AI platform that matches candidates to internships using **Sentence-BERT semantic embeddings**, **cosine similarity scoring**, and a **fairness-driven Integer Linear Programming (ILP)** optimizer — deployable both **online (Supabase)** and **fully offline (SQLite)**.

---

## 📐 System Architecture

This is a **monorepo** containing the entire stack — dashboard, backend API, AI engine, and offline database layer.

```
PMIS/
├── frontend/               # React dashboard + Flask API backend
│   ├── app.py              # Flask server — serves API & React SPA
│   ├── src/                # React + TypeScript source code
│   │   ├── components/     # UI components (shadcn/ui, custom pages)
│   │   ├── pages/          # Route-level pages (Index, NotFound)
│   │   ├── hooks/          # Custom React hooks
│   │   ├── lib/            # Utility functions
│   │   └── types/          # TypeScript type definitions
│   ├── package.json        # Frontend dependencies
│   ├── requirements.txt    # Python backend dependencies
│   ├── Dockerfile          # Container definition
│   ├── railway.toml        # Railway deployment config
│   └── railway_start.sh    # Railway build & start script
│
├── model/                  # AI / ML allocation engine
│   ├── speed_optimized_runner.py   # Cloud runner (Supabase-backed)
│   ├── local_runner.py             # Offline runner (SQLite-backed)
│   ├── api.py                      # Standalone Flask API for the model
│   ├── pipeline/
│   │   ├── model.py        # ML orchestration (Embedder → Scorer → Allocator)
│   │   ├── embedding.py    # Sentence-BERT encoding logic
│   │   ├── scoring.py      # Cosine similarity matrix computation
│   │   └── allocation.py   # ILP fairness-aware solver
│   ├── models/
│   │   └── allocation_model.pkl    # Pre-trained allocation model (~440 MB)
│   └── requirements.txt    # ML dependencies
│
├── db/                     # Offline CSV data backups
│   ├── candidates_tr.csv   # Training candidate profiles
│   ├── candidates_ts.csv   # Test/active candidate profiles
│   ├── internship.csv      # Internship listings
│   ├── results.csv         # Allocation results
│   └── login_creds.csv     # Admin credentials
│
├── local_db.py             # Builds SQLite DB from db/ CSVs
├── pmis_local.db           # Pre-built local SQLite database
├── setup_and_run_offline.ps1   # One-click offline setup (PowerShell)
└── .gitignore
```

---

## 🧠 AI Engine — How It Works

### 1. Semantic Skill-Role Mapping

Candidate profiles (skills, projects, sector interest) and internship requirements (skills, responsibilities, job descriptions) are encoded into dense vector embeddings using **Sentence-BERT** — capturing meaning far beyond simple keyword matching.

### 2. Multi-Dimensional Compatibility Scoring

A **cosine similarity matrix** is computed across multiple dimensions:

| Candidate Features     | Internship Features     |
|------------------------|------------------------|
| Technical Skills       | Skills Required        |
| Soft Skills            | Responsibilities       |
| Projects               | Job Description        |

Additional adjustments are applied for **sector/category alignment** and **location preference matching**.

### 3. Fairness-Aware Allocation (ILP)

An **Integer Linear Programming** solver maximizes total compatibility while enforcing equity constraints:

- **Social category balance** — SC, ST, OBC, EWS, GEN quotas
- **Location diversity** — Urban vs. Rural distribution
- **Capacity limits** — Respects per-internship seat caps

---

## 🖥️ Tech Stack

| Layer       | Technology                                            |
|-------------|------------------------------------------------------|
| Frontend    | React 18, TypeScript, Vite, Tailwind CSS, shadcn/ui  |
| Backend     | Python, Flask, Flask-CORS, Waitress (WSGI)           |
| AI/ML       | Sentence-BERT, scikit-learn, PuLP (ILP), PyTorch     |
| Database    | SQLite (offline) · Supabase / PostgreSQL (cloud)     |
| Deployment  | Railway, Docker                                       |

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.9+**
- **Node.js 18+**
- **pip** and **npm** available on PATH

### Option A — One-Click Offline Setup (Windows)

Run the PowerShell script from the project root:

```powershell
.\setup_and_run_offline.ps1
```

This will automatically:

1. Create a Python virtual environment
2. Install backend + ML dependencies
3. Build the SQLite database from `db/` CSV backups
4. Build the React frontend
5. Start the Flask server at **http://localhost:5000**

### Option B — Manual Setup

**1. Create & activate virtual environment**

```bash
python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1
# macOS / Linux
source venv/bin/activate
```

**2. Initialize the offline database**

```bash
pip install pandas
python local_db.py
```

**3. Start the backend**

```bash
cd frontend
pip install -r requirements.txt
python app.py
# → http://localhost:5000
```

**4. Start the frontend (development mode)**

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

> **Tip:** For local dev, create a `.env` file in `frontend/` with `VITE_API_BASE=http://127.0.0.1:5000` to point the React app at your local Flask server.

### Running the AI Allocation Engine

```bash
# Install ML dependencies
cd model
pip install -r requirements.txt

# Run against local SQLite database
python local_runner.py <internship_id>

# Run against Supabase (requires env vars)
python speed_optimized_runner.py <internship_id>
```

---

## 📡 API Reference

### Dashboard Backend (`frontend/app.py`)

| Method | Endpoint                                     | Description                                           |
|--------|----------------------------------------------|-------------------------------------------------------|
| `GET`  | `/health`                                    | Health check — confirms API status & DB mode          |
| `POST` | `/api/login`                                 | Admin authentication                                  |
| `GET`  | `/api/internships`                           | List all internship postings                          |
| `GET`  | `/api/internships/<id>`                      | Get a specific internship by ID                       |
| `GET`  | `/api/internships/<id>/candidates`           | Get candidates for a specific internship              |
| `GET`  | `/api/candidates`                            | List all candidate profiles                           |
| `GET`  | `/api/candidate_db`                          | Candidate overview (id, name, education, skills, projects) |
| `GET`  | `/api/shortlist/<id>`                        | Trigger AI allocation & return ranked results         |
| `GET`  | `/api/data/<table_name>`                     | Generic read access to any database table             |

### Model API (`model/api.py`)

| Method | Endpoint                        | Description                              |
|--------|---------------------------------|------------------------------------------|
| `GET`  | `/health`                       | Model service health check               |
| `POST` | `/run-allocation`               | Run allocation for a given internship ID |
| `GET`  | `/get-results/<internship_id>`  | Fetch allocation results                 |
| `GET`  | `/list-internships`             | List available internships               |

---

## ☁️ Deployment

### Railway (Recommended)

1. Connect this repository to a Railway project.
2. Set environment variables in the Railway dashboard:
   ```
   SUPABASE_URL=https://<your-project>.supabase.co
   SUPABASE_KEY=<your-service-role-key>
   CORS_ORIGINS=*
   LOG_LEVEL=INFO
   APP_ENV=production
   ```
3. Railway uses `railway.toml` and `railway_start.sh` to automatically build and serve.

### Docker

```bash
cd frontend
docker build -t pmis-app .
docker run -p 8000:8000 --env-file .env pmis-app
```

---

## ✨ Key Features

- **Semantic Matching** — Transformer-based embeddings understand meaning, not just keywords
- **Fairness by Design** — ILP optimizer enforces demographic and geographic balance constraints
- **Dual-Mode Database** — Runs fully offline with SQLite or online with Supabase (PostgreSQL)
- **One-Click Offline Setup** — PowerShell script bootstraps the entire stack automatically
- **Speed Optimized** — Local caching layer eliminates repeated API calls during batch processing
- **Unified Deployment** — Single service hosts both the Flask API and the React SPA
- **AI Shortlisting from Dashboard** — Trigger allocation and view ranked results directly from the UI

---

## 📊 Dashboard Pages

| Page                  | Description                                                  |
|-----------------------|--------------------------------------------------------------|
| **Home / Index**      | Landing page with key highlights, gallery, and logo carousel |
| **Login**             | Admin authentication portal                                  |
| **Admin Dashboard**   | Overview panel for system administrators                     |
| **Internships**       | Browse and search all internship listings                     |
| **Internship Detail** | Deep-dive into a specific internship with AI shortlisting    |
| **Candidates**        | View and filter all registered candidate profiles            |
| **Candidate Listing** | Detailed candidate information and skill breakdowns          |

---

## 🏆 Recognition

This project was **nominated for Smart India Hackathon (SIH) Nationals** in the Software category — a prestigious national-level competition organized by the Government of India to encourage innovation among students.

---

## 📄 License

See [LICENSE](./LICENSE) for details.
