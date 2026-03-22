# AI Internship Allocation Model

This repository houses the **AI Engine** for the internship allocation system. It is responsible for calculating compatibility scores between candidates and internships and performing fairness-aware allocation.

## Core Logic
-   **Skill-Role Mapping**: Uses **Sentence-BERT** to generate semantic embeddings for candidate skills/projects and internship requirements.
-   **Scoring**: Computes cosine similarity between embeddings to determine a compatibility score (0-1).
-   **Optimization**: Uses **Integer Linear Programming (ILP)** to assign internships, maximizing overall compatibility while adhering to fairness constraints (e.g., gender, social category balance).

## Features
-   **Speed Optimized Runner**: Includes a custom `SpeedOptimizedSupabaseRunner` that caches Supabase data locally to eliminate API latency during batch processing.
-   **Fairness Driven**: Ensures equitable distribution of opportunities.
-   **Automated Pipeline**: End-to-end pipeline from fetching data -> processing -> storing results.

## Project Structure
-   `speed_optimized_runner.py`: The main entry point. Fetches data, runs the model, and efficiently pushes results back to Supabase.
-   `pipeline/`:
    -   `model.py`: Wraps the ML logic (Embedder, Scorer, Allocator).
    -   `embedding.py`: Handles Sentence-BERT encoding.
    -   `scoring.py`: Logic for similarity matrix calculation.
    -   `allocation.py`: ILP solver implementation.
-   `models/`: Directory for storing the trained/pickled model artifacts.

## Setup & Usage

### 1. Requirements
```bash
pip install -r requirements.txt
```

### 2. Environment Variables
Ensure the following variables are set (can be passed via command line or environment):
-   `SUPABASE_URL`: Your Supabase Project URL.
-   `SUPABASE_KEY`: Your Supabase Service Role Key.
-   `MODEL_PATH`: Path to the `.pkl` model file (default: `models/allocation_model.pkl`).

### 3. Running the Allocation
To run the allocation for a specific internship:

```bash
python speed_optimized_runner.py <internship_id>
```

Or run interactively:
```bash
python speed_optimized_runner.py
# Prompts for Internship ID
```

This will:
1.  Fetch all candidates and the specific internship from Supabase.
2.  Compute compatibility scores using the trained AI model.
3.  Optimize allocation using ILP.
4.  Store the final ranked results back into the `results` table in Supabase.
