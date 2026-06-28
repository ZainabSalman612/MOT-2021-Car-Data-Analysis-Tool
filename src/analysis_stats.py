import sqlite3
import os
import matplotlib.pyplot as plt
import numpy as np

# ====================================================================
# MODULE: analysis_stats.py
# PURPOSE: Statistical Analysis and Graph Generation (for GUI)
# ====================================================================

# --- Configuration ---
DB_PATH = os.path.join("data", "mot_database.db")
OUTPUT_FILE = os.path.join("output", "analysis_summary.txt")


def _get_connection():
    """Returns a new SQLite connection to the MOT database."""
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found at {DB_PATH}. Run the pipeline first.")
    return sqlite3.connect(DB_PATH)


def generate_error_figure(title, message):
    """Helper function to return a clean Matplotlib error figure for the GUI."""
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor('#1e1e2e')
    ax.set_facecolor('#1e1e2e')
    ax.set_title(title, color='#f38ba8', fontsize=16)
    ax.text(0.5, 0.5, message, ha='center', va='center', fontsize=12, color='#cdd6f4')
    ax.axis('off')
    plt.tight_layout()
    return fig


def generate_pass_rate_graph(make, model, criteria):
    """
    Generates a Matplotlib Figure showing pass rates by age or mileage for a specific make/model.
    Uses SQL queries directly on the SQLite database to avoid loading millions of rows into memory.
    """
    try:
        conn = _get_connection()
    except FileNotFoundError as e:
        return generate_error_figure("Data Load Error", str(e))

    make = make.strip().upper()
    model = model.strip().upper()

    # Validate criteria
    if criteria not in ('age', 'mileage'):
        conn.close()
        return generate_error_figure("Invalid Criteria", "Criteria must be 'age' or 'mileage'.")

    # Build SQL query based on criteria
    if criteria == 'age':
        # Calculate vehicle age = (test_date year - first_use_date year) approximately
        query = """
            SELECT 
                CAST((CAST(SUBSTR(test_date, 1, 4) AS INTEGER) - CAST(SUBSTR(first_use_date, 1, 4) AS INTEGER)) AS INTEGER) AS group_val,
                COUNT(*) AS total_tests,
                SUM(CASE WHEN test_result = 'P' THEN 1 ELSE 0 END) AS total_passes
            FROM cleaned_tests
            WHERE make = ? AND model = ? 
              AND test_result IN ('P', 'F')
              AND test_date != '' AND first_use_date != ''
              AND LENGTH(test_date) >= 4 AND LENGTH(first_use_date) >= 4
            GROUP BY group_val
            HAVING group_val >= 0 AND group_val <= 50
            ORDER BY group_val
        """
        x_label = "Vehicle Age (Years)"
        title_suffix = "by Age"
    else:  # mileage
        query = """
            SELECT 
                CAST((test_mileage / 10000) * 10 AS INTEGER) AS group_val,
                COUNT(*) AS total_tests,
                SUM(CASE WHEN test_result = 'P' THEN 1 ELSE 0 END) AS total_passes
            FROM cleaned_tests
            WHERE make = ? AND model = ? 
              AND test_result IN ('P', 'F')
              AND test_mileage > 0
            GROUP BY group_val
            ORDER BY group_val
        """
        x_label = "Test Mileage (Thousands of Miles)"
        title_suffix = "by Mileage"

    cursor = conn.cursor()
    cursor.execute(query, (make, model))
    rows = cursor.fetchall()
    conn.close()

    # Handle no data
    if not rows:
        return generate_error_figure(f"No Data Found for {make} {model}",
                                     "0 records matched the criteria (Make/Model).")

    group_vals = [r[0] for r in rows]
    total_tests = [r[1] for r in rows]
    total_passes = [r[2] for r in rows]
    pass_rates = [(p / t * 100) if t > 0 else 0 for p, t in zip(total_passes, total_tests)]

    # Generate Matplotlib Figure with dark theme
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor('#1e1e2e')
    ax.set_facecolor('#252538')

    ax.plot(group_vals, pass_rates,
            marker='o', linestyle='-', color='#89b4fa', linewidth=2, markersize=7,
            markerfacecolor='#b4befe', markeredgecolor='#89b4fa')

    ax.set_title(f"MOT Pass Rate for {make} {model} {title_suffix}", fontsize=16, color='#cdd6f4', pad=15)
    ax.set_xlabel(x_label, fontsize=12, color='#a6adc8')
    ax.set_ylabel("Pass Rate (%)", fontsize=12, color='#a6adc8')
    ax.grid(True, linestyle='--', alpha=0.3, color='#585b70')
    ax.set_ylim(0, 100)

    ax.tick_params(colors='#a6adc8')
    ax.spines['bottom'].set_color('#585b70')
    ax.spines['left'].set_color('#585b70')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Add labels to the points
    for x, y in zip(group_vals, pass_rates):
        ax.annotate(f'{y:.1f}%', (x, y), textcoords="offset points",
                     xytext=(0, 10), ha='center', fontsize=9, color='#cdd6f4')

    plt.tight_layout()
    return fig


# --- Original analysis_stats function preserved for CLI reporting ---
def analysis_stats():
    """Generates the original summary text report."""
    try:
        conn = _get_connection()
    except FileNotFoundError:
        print("Cannot run full analysis: Database not found.")
        return

    cursor = conn.cursor()

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    lines = []
    lines.append("=== OVERALL TEST RESULT DISTRIBUTION ===\n")
    cursor.execute("SELECT test_result, COUNT(*) as cnt FROM cleaned_tests GROUP BY test_result ORDER BY cnt DESC")
    for row in cursor.fetchall():
        lines.append(f"  {row[0]}: {row[1]}")
    lines.append("\n")

    cursor.execute("SELECT COUNT(*) FROM cleaned_tests WHERE test_result = 'P'")
    passes = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM cleaned_tests WHERE test_result = 'F'")
    fails = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM cleaned_tests")
    total = cursor.fetchone()[0]

    lines.append(f"Total: {total}, Passes: {passes}, Fails: {fails}")
    lines.append("\n")

    lines.append("=== TEST RESULTS BY FUEL TYPE ===\n")
    cursor.execute("""
        SELECT fuel_type, test_result, COUNT(*) as cnt 
        FROM cleaned_tests 
        GROUP BY fuel_type, test_result 
        ORDER BY fuel_type, test_result
    """)
    for row in cursor.fetchall():
        lines.append(f"  {row[0]} - {row[1]}: {row[2]}")

    conn.close()

    with open(OUTPUT_FILE, "w") as f:
        f.write("\n".join(lines))

    print("Analysis complete!")
    print("Saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    # Example usage for CLI testing:
    try:
        analysis_stats()
        fig_bmw = generate_pass_rate_graph("BMW", "3 SERIES", "age")
        plt.show()
    except Exception as e:
        print(f"CLI test failed: {e}")