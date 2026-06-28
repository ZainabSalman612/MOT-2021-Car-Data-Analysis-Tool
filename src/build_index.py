import sqlite3
import os
import sys

DB_PATH = os.path.join("data", "mot_database.db")

def create_indices(progress_callback=None):
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        sys.exit("Database not found. Run load_data.py first.")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Define indexes to create
    indexes = {
        "idx_test_id": "CREATE UNIQUE INDEX IF NOT EXISTS idx_test_id ON cleaned_tests (test_id)",
        "idx_make_model": "CREATE INDEX IF NOT EXISTS idx_make_model ON cleaned_tests (make, model)",
        "idx_make": "CREATE INDEX IF NOT EXISTS idx_make ON cleaned_tests (make)",
        "idx_first_use_year": "CREATE INDEX IF NOT EXISTS idx_first_use_year ON cleaned_tests (first_use_year)",
        "idx_test_mileage": "CREATE INDEX IF NOT EXISTS idx_test_mileage ON cleaned_tests (test_mileage)"
    }

    total_indexes = len(indexes)
    
    print("Creating database indices for high-performance querying...")
    
    for idx_num, (name, sql) in enumerate(indexes.items()):
        print(f"Creating index {name}...")
        try:
            cursor.execute(sql)
            conn.commit()
        except Exception as e:
            print(f"Error creating index {name}: {e}")
            conn.close()
            raise e

        # Calculate progress
        progress_pct = int((idx_num + 1) / total_indexes * 100)
        if progress_callback:
            progress_callback(progress_pct)
        else:
            sys.stdout.write(f"\rIndexing progress: {progress_pct}%")
            sys.stdout.flush()

    print("\nAll database indices created successfully!")
    conn.close()

def main():
    create_indices()

if __name__ == "__main__":
    main()

