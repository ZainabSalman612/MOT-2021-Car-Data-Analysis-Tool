import pandas as pd
import sqlite3
import os
import sys

DB_PATH = os.path.join("data", "mot_database.db")

def clean_data(progress_callback=None):
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        sys.exit("Database not found. Run load_data.py first.")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Checking raw table size...")
    cursor.execute("SELECT COUNT(*) FROM raw_tests")
    total_rows = cursor.fetchone()[0]
    print(f"Total rows to clean: {total_rows}")

    if total_rows == 0:
        print("No raw data found to clean.")
        conn.close()
        return

    # Calculate median cylinder capacity using SQLite (efficiently)
    print("Calculating median cylinder capacity...")
    cursor.execute("""
        SELECT cylinder_capacity 
        FROM raw_tests 
        WHERE cylinder_capacity IS NOT NULL AND cylinder_capacity > 0
        ORDER BY cylinder_capacity 
        LIMIT 1 OFFSET (
            SELECT COUNT(*) 
            FROM raw_tests 
            WHERE cylinder_capacity IS NOT NULL AND cylinder_capacity > 0
        ) / 2
    """)
    median_row = cursor.fetchone()
    cc_median = median_row[0] if median_row else 1598.0  # Fallback to standard 1.6L CC
    print(f"Median cylinder capacity calculated: {cc_median} CC")

    # Drop cleaned_tests table if it exists
    cursor.execute("DROP TABLE IF EXISTS cleaned_tests")
    conn.commit()

    chunk_size = 100000
    rows_processed = 0

    print("Cleaning dataset in chunks...")
    # Fetch data in chunks from SQL
    offset = 0
    while offset < total_rows:
        # Load raw chunk
        query = f"SELECT * FROM raw_tests LIMIT {chunk_size} OFFSET {offset}"
        df = pd.read_sql_query(query, conn)
        
        if df.empty:
            break

        # 1. Convert date columns
        df['test_date_dt'] = pd.to_datetime(df['test_date'], errors='coerce')
        df['first_use_date_dt'] = pd.to_datetime(df['first_use_date'], errors='coerce')

        # Format dates as ISO string YYYY-MM-DD
        df['test_date'] = df['test_date_dt'].dt.strftime('%Y-%m-%d').fillna('')
        df['first_use_date'] = df['first_use_date_dt'].dt.strftime('%Y-%m-%d').fillna('')

        # Extract Year (for indexing and search)
        df['first_use_year'] = df['first_use_date_dt'].dt.year.fillna(0).astype(int).astype(str).replace('0', 'UNKNOWN')

        # Drop temporary datetime columns
        df = df.drop(columns=['test_date_dt', 'first_use_date_dt'])

        # 2. Handle missing values
        df['test_mileage'] = df['test_mileage'].fillna(0).astype(int)
        df['cylinder_capacity'] = df['cylinder_capacity'].fillna(cc_median).astype(float)

        # 3. Standardize text columns
        text_columns = ['make', 'model', 'colour', 'fuel_type', 'test_type', 'test_result', 'postcode_area']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().str.upper()

        # 4. Save cleaned chunk to SQLite
        df.to_sql("cleaned_tests", conn, if_exists="append", index=False)

        rows_processed += len(df)
        progress_pct = min(99, int((rows_processed / total_rows) * 100))

        if progress_callback:
            progress_callback(progress_pct)
        else:
            sys.stdout.write(f"\rCleaning Progress: {progress_pct}% ({rows_processed}/{total_rows} rows)")
            sys.stdout.flush()

        offset += chunk_size

    # Drop raw table and free up space
    print("\nDropping raw_tests table to save space...")
    cursor.execute("DROP TABLE IF EXISTS raw_tests")
    conn.commit()

    print("Optimizing SQLite database size (VACUUM)...")
    conn.execute("VACUUM")
    
    if progress_callback:
        progress_callback(100)

    conn.close()
    print("\nCleaning complete! Data stored in 'cleaned_tests' table.")

if __name__ == "__main__":
    clean_data()

