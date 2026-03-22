from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import os
import sqlite3
from dotenv import load_dotenv
import logging
from typing import Optional
import requests

load_dotenv()

BUILD_DIR = os.getenv("FRONTEND_BUILD_DIR", "dist")
app = Flask(__name__, static_folder=BUILD_DIR, static_url_path="/")

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

CORS(app, resources={r"/api/*": {"origins": os.getenv("CORS_ORIGINS", "*").split(",")}})

MODEL_URL = os.getenv("MODEL_URL")

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "pmis_local.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Routes
@app.route('/health')
def health():
    return jsonify({
        "status": "ok",
        "supabase": False,
        "sqlite": True,
        "environment": os.getenv("APP_ENV", "production")
    })

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    try:
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM login_creds WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()
        
        if user:
            return jsonify({"success": True, "message": "Login successful", "username": username})
        else:
            return jsonify({"success": False, "message": "Invalid credentials"}), 401
    except Exception as e:
        logger.exception("Error during login")
        return jsonify({"error": str(e)}), 500

@app.route('/')
def root():
    index_path = os.path.join(app.static_folder, 'index.html')
    if os.path.exists(index_path):
        return send_from_directory(app.static_folder, 'index.html')
    return "Backend service is running. See /health and /api endpoints."

@app.errorhandler(404)
def spa_fallback(e):  # noqa: D401, ANN001
    """If a built SPA exists, serve index.html for unmatched routes (excluding API)."""
    if request.path.startswith('/api') or request.path.startswith('/health'):
        return jsonify({"error": "Not Found"}), 404
    index_path = os.path.join(app.static_folder, 'index.html')
    if os.path.exists(index_path):
        return send_from_directory(app.static_folder, 'index.html')
    return jsonify({"error": "Not Found"}), 404

@app.route('/api/data/<table_name>')
def get_table_data(table_name):
    try:
        conn = get_db_connection()
        rows = conn.execute(f'SELECT * FROM {table_name}').fetchall()
        conn.close()
        return jsonify([dict(ix) for ix in rows]), 200
    except Exception as e:  # noqa: BLE001
        logger.exception("Error fetching table data")
        return jsonify({"error": str(e)}), 500

@app.route('/api/internships')
def get_internships():
    try:
        conn = get_db_connection()
        rows = conn.execute('SELECT * FROM internship').fetchall()
        conn.close()
        return jsonify([dict(ix) for ix in rows])
    except Exception as e:  # noqa: BLE001
        logger.exception("Error fetching internships")
        return jsonify({"error": str(e)}), 500

@app.route('/api/internships/<internship_id>')
def get_internship(internship_id):
    try:
        conn = get_db_connection()
        internship = conn.execute('SELECT * FROM internship WHERE internship_id = ?', (internship_id,)).fetchone()
        conn.close()
        
        if not internship:
            return jsonify({"error": "Not found"}), 404
        return jsonify(dict(internship))
    except Exception as e:
        logger.exception("Error fetching internship detail")
        return jsonify({"error": str(e)}), 500

@app.route('/api/candidates')
def get_candidates():
    try:
        conn = get_db_connection()
        rows = conn.execute('SELECT * FROM candidates_ts').fetchall()
        conn.close()
        return jsonify([dict(ix) for ix in rows])
    except Exception as e:  # noqa: BLE001
        logger.exception("Error fetching candidates from db")
        return jsonify({"error": str(e)}), 500

@app.route('/api/candidate_db')
def get_candidates_database():
    try:
        conn = get_db_connection()
        rows = conn.execute('SELECT id, name, education, skills, projects FROM candidates_ts').fetchall()
        conn.close()
        return jsonify([dict(ix) for ix in rows])
    except Exception as e:  # noqa: BLE001
        logger.exception("Error fetching candidates from db")
        return jsonify({"error": str(e)}), 500

@app.route('/api/internships/<internship_id>/candidates')
def get_candidates_for_internship(internship_id):
    try:
        conn = get_db_connection()
        rows = conn.execute('SELECT * FROM candidates_ts WHERE internship_id = ?', (internship_id,)).fetchall()
        conn.close()
        return jsonify([dict(ix) for ix in rows])
    except Exception as e:
        logger.exception(f"Error fetching candidates for internship {internship_id}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/shortlist/<internship_id>')
def shortlist_candidates(internship_id):
    logger.info(f"Triggering AI shortlist for internship {internship_id}")
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        local_runner_path = os.path.join(os.path.dirname(os.path.dirname(current_dir)), 'model', 'allocation_model', 'local_runner.py')
        
        import subprocess
        import sys
        
        # Run the local python model using the current python executable
        result = subprocess.run(
            [sys.executable, local_runner_path, internship_id],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            logger.error(f"Error running model: {result.stderr}")
            return jsonify({"error": "Failed to run AI Model"}), 500
            
    except Exception as e:
        logger.exception("Error executing local model script.")
        return jsonify({"error": str(e)}), 500

    logger.info(f"Fetching shortlist for internship {internship_id} from 'results' table.")
    try:
        conn = get_db_connection()
        # The .order() method will sort the results by the 'Rank' column
        rows = conn.execute('SELECT * FROM results WHERE InternshipID = ? ORDER BY Rank', (internship_id,)).fetchall()
        conn.close()
        
        results = [dict(ix) for ix in rows]

        if not results:
            return jsonify({"data": [[]]}), 200

        final_response = {"data": [results]}
        return jsonify(final_response)

    except Exception as e:
        logger.exception(f"An error occurred while fetching shortlist for internship {internship_id}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    logger.info(f"Starting development server on port {port}")
    app.run(host='0.0.0.0', port=port)
