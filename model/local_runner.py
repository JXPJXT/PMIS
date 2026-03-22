import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
import json
import logging
import sqlite3

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load model class
try:
    from pipeline.model import AllocationModel
except ImportError as e:
    logger.error(f"Missing model: {e}")
    sys.exit(1)

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(current_dir)), "pmis_local.db")
MODEL_PATH = os.path.join(current_dir, 'models', 'allocation_model.pkl')

class LocalSQLiteRunner:
    """Speed optimized runner using local SQLite DB"""

    def __init__(self, model_path: str = MODEL_PATH):
        # PRE-CACHE ALL DATA
        self.candidates_cache = {}
        self.internship_cache = {}

        # Test connection
        try:
            self.conn = sqlite3.connect(DB_PATH)
            self.conn.row_factory = sqlite3.Row
            logger.info(f"✅ Connected to local DB: {DB_PATH}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to DB: {e}")
            raise

        # Load trained model
        try:
            self.model = AllocationModel.load(model_path)
            if not self.model.fitted:
                raise ValueError("Model is not fitted")
            logger.info(f"✅ Loaded trained model from {model_path}")
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            raise

    def fetch_candidates_from_db(self) -> pd.DataFrame:
        """Fetch all candidates from local sqlite database"""
        try:
            logger.info("📊 Fetching candidates from database...")
            c = self.conn.cursor()
            rows = c.execute('SELECT * FROM candidates_ts').fetchall()
            data = [dict(ix) for ix in rows]

            if not data:
                logger.warning("No candidates found in database")
                return pd.DataFrame()

            for candidate in data:
                candidate_id = candidate.get('candidate_id')
                if not candidate_id and 'id' in candidate:
                    candidate_id = str(candidate['id'])
                self.candidates_cache[candidate_id] = candidate

            logger.info(f"✅ CACHED {len(self.candidates_cache)} candidates")

            candidates_df = pd.DataFrame(data)

            # Map columns to model expected columns
            column_mapping = {
                'candidate_id': 'Candidate ID',
                'name': 'Name',
                'candidate_degree': 'Degree',
                'technical_skills': 'Technical Skills',
                'soft_skills': 'Soft Skills', 
                'projects': 'Projects',
                'location_preference_1': 'Location Preference 1',
                'location_preference_2': 'Location Preference 2', 
                'location_preference_3': 'Location Preference 3',
                'sector_interest': 'Sector Interest',
                'past_participation': 'Past Participation',
                'location_category': 'location_category',
                'social_category_ews': 'Social_Category_EWS',
                'social_category_gen': 'Social_Category_GEN',
                'social_category_obc': 'Social_Category_OBC', 
                'social_category_sc': 'Social_Category_SC',
                'social_category_st': 'Social_Category_ST'
            }

            for db_col, model_col in column_mapping.items():
                if db_col in candidates_df.columns:
                    candidates_df = candidates_df.rename(columns={db_col: model_col})

            candidates_df = candidates_df.fillna("")
            return candidates_df

        except Exception as e:
            logger.error(f"❌ Failed to fetch candidates: {e}")
            raise

    def fetch_internship_by_id(self, internship_id: str) -> pd.DataFrame:
        """Fetch specific internship by ID"""
        try:
            logger.info(f"📊 Fetching internship ID: {internship_id}")
            c = self.conn.cursor()
            row = c.execute('SELECT * FROM internship WHERE internship_id = ?', (internship_id,)).fetchone()
            
            if not row:
                logger.error(f"No internship found with ID: {internship_id}")
                return pd.DataFrame()

            data = [dict(row)]
            self.internship_cache[internship_id] = data[0]

            internship_df = pd.DataFrame(data)

            column_mapping = {
                'internship_id': 'Internship ID',
                'internship_title': 'Title',
                'skills_required': 'Skills Required',
                'job_description': 'Job Description', 
                'responsibilities': 'Responsibilities',
                'duration_months': 'Duration',
                'stipend_inr_month': 'Stipend',
                'company_name': 'Company',
                'location': 'Location',
                'capacity': 'capacity',
                'category': 'Category',
                'status': 'Status'
            }

            for db_col, model_col in column_mapping.items():
                if db_col in internship_df.columns:
                    internship_df = internship_df.rename(columns={db_col: model_col})

            internship_df = internship_df.fillna("")
            return internship_df
        except Exception as e:
            logger.error(f"❌ Failed to fetch internship: {e}")
            raise

    def process_data_for_internship(self, candidates_df: pd.DataFrame, internship_df: pd.DataFrame) -> pd.DataFrame:
        try:
            logger.info("⚙️ Processing data through trained model...")
            candidates_df["Tech_Skills"] = candidates_df["Technical Skills"].apply(
                lambda x: self.model.embedder.clean_and_limit(str(x), 5)
            )
            candidates_df["Soft_Skills"] = candidates_df["Soft Skills"].apply(
                lambda x: self.model.embedder.clean_and_limit(str(x), 3) 
            )
            candidates_df["Projects"] = candidates_df["Projects"].fillna("")

            internship_df["Req_Skills"] = internship_df["Skills Required"].apply(
                lambda x: self.model.embedder.clean_and_limit(str(x), 10)
            )
            internship_df["Responsibilities"] = internship_df["Responsibilities"].fillna("")
            internship_df["Job Description"] = internship_df["Job Description"].fillna("")

            logger.info("🧠 Generating embeddings...")
            cand_tech_emb = self.model.embedder.encode_batch(candidates_df["Tech_Skills"].tolist())
            cand_soft_emb = self.model.embedder.encode_batch(candidates_df["Soft_Skills"].tolist())
            cand_proj_emb = self.model.embedder.encode_batch(candidates_df["Projects"].tolist())

            intern_req_emb = self.model.embedder.encode_batch(internship_df["Req_Skills"].tolist())
            intern_resp_emb = self.model.embedder.encode_batch(internship_df["Responsibilities"].tolist())
            intern_desc_emb = self.model.embedder.encode_batch(internship_df["Job Description"].tolist())

            logger.info("📊 Computing similarity scores...")
            skill_matrix = self.model.scorer.compute_skill_matrix(
                cand_tech_emb, cand_soft_emb, cand_proj_emb,
                intern_req_emb, intern_resp_emb, intern_desc_emb
            )

            skill_matrix = self.model.scorer.apply_category_adjustment(
                skill_matrix, candidates_df["Sector Interest"], internship_df["Category"]
            )

            cand_locs = candidates_df[["Location Preference 1", "Location Preference 2", "Location Preference 3"]]
            skill_matrix = self.model.scorer.apply_location_adjustment(
                skill_matrix, cand_locs, internship_df["Location"]
            )

            scores_df = pd.DataFrame(
                skill_matrix,
                index=candidates_df["Candidate ID"],
                columns=internship_df["Internship ID"]
            )

            logger.info("🎯 Running allocation optimization...")
            allocations = self.model.allocator.allocate(candidates_df, internship_df, scores_df)
            return allocations
        except Exception as e:
            logger.error(f"❌ Failed to process data: {e}")
            raise

    def store_results_to_db(self, results_df: pd.DataFrame, internship_id: str) -> bool:
        try:
            logger.info(f"💾 Storing {len(results_df)} results for {internship_id}...")
            c = self.conn.cursor()
            c.execute('DELETE FROM results WHERE InternshipID = ?', (internship_id,))
            
            internship_data = self.internship_cache.get(internship_id, {})
            results_data = []
            
            for _, row in results_df.iterrows():
                candidate_id = str(row['CandidateID'])
                candidate_data = self.candidates_cache.get(candidate_id, {})

                social_category = 'GEN'
                if candidate_data.get('social_category_sc'): social_category = 'SC'
                elif candidate_data.get('social_category_st'): social_category = 'ST' 
                elif candidate_data.get('social_category_obc'): social_category = 'OBC'
                elif candidate_data.get('social_category_ews'): social_category = 'EWS'

                loc_cat = candidate_data.get('location_category', 0)
                location_category = 'Urban' if loc_cat == 1 else 'Rural'

                past_participation = bool(candidate_data.get('past_participation', 0))

                results_data.append((
                    str(row['InternshipID']), candidate_id, int(row['Rank']), float(row['Score']),
                    social_category, location_category,
                    str(candidate_data.get('technical_skills', '')),
                    past_participation,
                    str(candidate_data.get('soft_skills', '')),
                    str(candidate_data.get('projects', '')),
                    str(internship_data.get('skills_required', '')),
                    str(internship_data.get('responsibilities', '')),
                    str(internship_data.get('job_description', '')),
                    str(internship_data.get('location', '')),
                    str(internship_data.get('category', '')),
                    datetime.now().isoformat()
                ))

            c.executemany('''INSERT INTO results 
                (InternshipID, CandidateID, Rank, Score, Social_Category, Location_Category,
                 Technical_Skills, Past_Participation, Soft_Skills, Projects, Skills_Required,
                 Responsibilities, Job_Description, Location, Category, created_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', results_data)
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"❌ Failed to store results: {e}")
            self.conn.rollback()
            return False

    def run_allocation_for_internship(self, internship_id: str) -> bool:
        try:
            candidates_df = self.fetch_candidates_from_db()
            internship_df = self.fetch_internship_by_id(internship_id)
            if candidates_df.empty or internship_df.empty:
                return False

            results_df = self.process_data_for_internship(candidates_df, internship_df)
            if results_df.empty: return False

            return self.store_results_to_db(results_df, internship_id)
        except Exception as e:
            logger.error(f"❌ Failed to run allocation: {e}")
            return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        internship_id = sys.argv[1]
        runner = LocalSQLiteRunner()
        success = runner.run_allocation_for_internship(internship_id)
        sys.exit(0 if success else 1)
    else:
        print("Usage: python local_runner.py <internship_id>")
