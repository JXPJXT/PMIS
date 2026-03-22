import sqlite3
import pandas as pd
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "pmis_local.db")
DB_DIR = os.path.join(os.path.dirname(__file__), "db")

def init_db_from_csv():
    conn = sqlite3.connect(DB_PATH)
    
    # login_creds
    try:
        df_login = pd.read_csv(os.path.join(DB_DIR, "login_creds.csv"))
        df_login.columns = df_login.columns.str.replace('"', '').str.replace("'", "")
        df_login.to_sql("login_creds", conn, if_exists="replace", index=False)
        print("Loaded login_creds")
    except Exception as e:
        print(f"Error loading login_creds: {e}")

    # internship
    try:
        df_internship = pd.read_csv(os.path.join(DB_DIR, "internship.csv"))
        df_internship.columns = df_internship.columns.str.replace('"', '').str.replace("'", "")
        df_internship.to_sql("internship", conn, if_exists="replace", index=False)
        print("Loaded internship")
    except Exception as e:
        print(f"Error loading internship: {e}")

    # candidates_ts
    try:
        df_candidates_ts = pd.read_csv(os.path.join(DB_DIR, "candidates_ts.csv"))
        df_candidates_ts.columns = df_candidates_ts.columns.str.replace('"', '').str.replace("'", "")
        df_candidates_ts.to_sql("candidates_ts", conn, if_exists="replace", index=False)
        print("Loaded candidates_ts")
    except Exception as e:
        print(f"Error loading candidates_ts: {e}")
        
    # candidates_tr
    try:
        df_candidates_tr = pd.read_csv(os.path.join(DB_DIR, "candidates_tr.csv"))
        df_candidates_tr.columns = df_candidates_tr.columns.str.replace('"', '').str.replace("'", "")
        df_candidates_tr.to_sql("candidates_tr", conn, if_exists="replace", index=False)
        print("Loaded candidates_tr")
    except Exception as e:
        print(f"Error loading candidates_tr: {e}")

    # results
    try:
        df_results = pd.read_csv(os.path.join(DB_DIR, "results.csv"))
        df_results.columns = df_results.columns.str.replace('"', '').str.replace("'", "")
        df_results.to_sql("results", conn, if_exists="replace", index=False)
        print("Loaded results")
    except Exception as e:
        print(f"Error loading results: {e}")

    conn.close()
    print("Database initialized successfully from CSVs.")

if __name__ == '__main__':
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("Removed existing database.")
    init_db_from_csv()
