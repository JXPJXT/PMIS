# PowerShell Setup & Run Script for Offline PMIS
$ErrorActionPreference = "Stop"

Write-Host "Creating Python Virtual Environment..." -ForegroundColor Cyan
python -m venv venv
.\venv\Scripts\Activate.ps1

Write-Host "Installing Basic Backend Requirements..." -ForegroundColor Cyan
cd frontend/PMIS
pip install -r requirements.txt
cd ../..

Write-Host "Installing ML Runner Dependencies (pandas, scikit-learn, sentence-transformers, torch, pulp)..." -ForegroundColor Cyan
pip install pandas numpy scikit-learn pulp sentence-transformers torch torchvision torchaudio

Write-Host "Creating offline database from db/ CSV backups..." -ForegroundColor Cyan
python local_db.py

Write-Host "Building React Frontend..." -ForegroundColor Cyan
cd frontend/PMIS
npm install
npm run build
cd ../..

Write-Host "Starting Offline Flask Backend Server on port 5000..." -ForegroundColor Green
cd frontend/PMIS
python app.py
