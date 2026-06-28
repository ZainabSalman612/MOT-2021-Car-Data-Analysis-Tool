# summary_report.py

import os
import sqlite3
import sys

# paths
DB_PATH = os.path.join("data", "mot_database.db")
REPORT_DIR = os.path.join("output", "reports")
REPORT_FILE = os.path.join(REPORT_DIR, "summary_report.txt")


def ensure_out_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def write_report(progress_callback=None):
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        sys.exit("Database not found. Run load_data.py first.")

    ensure_out_dir(REPORT_DIR)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Creating summary report from SQLite database...")

    # Total rows
    cursor.execute("SELECT COUNT(*) FROM cleaned_tests")
    total_rows = cursor.fetchone()[0]

    # Unique makes and models
    cursor.execute("SELECT COUNT(DISTINCT make) FROM cleaned_tests")
    unique_makes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT model) FROM cleaned_tests")
    unique_models = cursor.fetchone()[0]

    if progress_callback:
        progress_callback(20)

    # Top 10 Makes
    cursor.execute("SELECT make, COUNT(*) as cnt FROM cleaned_tests GROUP BY make ORDER BY cnt DESC LIMIT 10")
    top_makes = cursor.fetchall()

    if progress_callback:
        progress_callback(40)

    # Top 10 Models
    cursor.execute("SELECT model, COUNT(*) as cnt FROM cleaned_tests GROUP BY model ORDER BY cnt DESC LIMIT 10")
    top_models = cursor.fetchall()

    if progress_callback:
        progress_callback(60)

    # Year Distribution
    cursor.execute("SELECT first_use_year, COUNT(*) as cnt FROM cleaned_tests GROUP BY first_use_year ORDER BY cnt DESC")
    year_counts = cursor.fetchall()

    if progress_callback:
        progress_callback(80)

    # Mileage Statistics
    cursor.execute("""
        SELECT 
            COUNT(test_mileage),
            AVG(test_mileage),
            MIN(test_mileage),
            MAX(test_mileage)
        FROM cleaned_tests
        WHERE test_mileage > 0
    """)
    mileage_stats = cursor.fetchone()

    conn.close()

    # Write report
    with open(REPORT_FILE, "w") as f:
        f.write("MOT SUMMARY REPORT\n")
        f.write("===================\n\n")

        f.write(f"Total rows: {total_rows}\n")
        f.write(f"Unique makes: {unique_makes}\n")
        f.write(f"Unique models: {unique_models}\n\n")

        f.write("Top 10 Makes:\n")
        for make, cnt in top_makes:
            f.write(f"  {make}: {cnt}\n")
        f.write("\n")

        f.write("Top 10 Models:\n")
        for model, cnt in top_models:
            f.write(f"  {model}: {cnt}\n")
        f.write("\n")

        f.write("Year Distribution (Top 20):\n")
        for year, cnt in year_counts[:20]:
            f.write(f"  {year}: {cnt}\n")
        f.write("\n")

        f.write("Mileage Statistics:\n")
        if mileage_stats:
            f.write(f"  Count: {mileage_stats[0]}\n")
            f.write(f"  Mean:  {mileage_stats[1]:.2f}\n")
            f.write(f"  Min:   {mileage_stats[2]}\n")
            f.write(f"  Max:   {mileage_stats[3]}\n")
        f.write("\n")

    if progress_callback:
        progress_callback(100)

    print("Report saved at:", REPORT_FILE)


def main():
    write_report()


if __name__ == "__main__":
    main()
