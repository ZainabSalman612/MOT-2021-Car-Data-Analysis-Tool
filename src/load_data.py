import pandas as pd
import sqlite3
import os
import sys

# Path to your folder
DATA_FOLDER = os.path.join("data", "dft_test_result_2021", "test_results_2021")

# Files are named test_result_1 to test_result_12
FILES = [f"test_result_{i}.csv" for i in range(1, 13)]

# Output SQLite database file
DB_PATH = os.path.join("data", "mot_database.db")

def load_in_chunks(progress_callback=None):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Dropping raw_tests table if it already exists...")
    cursor.execute("DROP TABLE IF EXISTS raw_tests")
    conn.commit()
    
    total_files = len(FILES)
    chunk_size = 100000
    approx_chunks_per_file = 34  # ~3.4 million rows per file
    total_approx_chunks = total_files * approx_chunks_per_file
    
    global_chunk_count = 0

    for file_idx, file in enumerate(FILES):
        path = os.path.join(DATA_FOLDER, file)
        if not os.path.exists(path):
            print(f"Error: File not found at: {path}")
            conn.close()
            sys.exit(f"File not found: {path}")

        print(f"Reading {path} into SQLite raw_tests...")

        # Read the large CSV file in chunks
        try:
            reader = pd.read_csv(path, chunksize=chunk_size, low_memory=False)
            for chunk_idx, df_chunk in enumerate(reader):
                df_chunk.to_sql("raw_tests", conn, if_exists="append", index=False)
                
                global_chunk_count += 1
                progress_pct = min(99, int((global_chunk_count / total_approx_chunks) * 100))
                
                if progress_callback:
                    progress_callback(progress_pct)
                else:
                    if chunk_idx % 5 == 0:
                        sys.stdout.write(f"\rFile {file_idx+1}/{total_files} - Progress: {progress_pct}%")
                        sys.stdout.flush()
        except Exception as e:
            conn.close()
            print(f"\nError processing file {file}: {e}")
            raise e

        print(f"\nDone: {file}")
        print("----------------------------")

    if progress_callback:
        progress_callback(100)
        
    conn.close()
    print("\nAll raw files loaded successfully into SQLite raw_tests!")

if __name__ == "__main__":
    load_in_chunks()

