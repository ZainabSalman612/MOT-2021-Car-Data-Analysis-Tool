# run_all.py

import os
import sys

# Ensure the project root is used as the working directory
# so that relative paths (data/, output/) resolve correctly.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))

from load_data import load_in_chunks
from clean_data import clean_data
from build_index import create_indices
from analysis_stats import analysis_stats
from summary_report import write_report


def main():
    print("=" * 50)
    print("Starting full pipeline...")
    print("=" * 50)

    print("\n[1/5] Loading raw CSV data into SQLite...")
    load_in_chunks()
    print("----------------------------")

    print("\n[2/5] Cleaning data...")
    clean_data()
    print("----------------------------")

    print("\n[3/5] Building database indexes...")
    create_indices()
    print("----------------------------")

    print("\n[4/5] Running analysis stats...")
    analysis_stats()
    print("----------------------------")

    print("\n[5/5] Generating summary report...")
    write_report()
    print("----------------------------")

    print("\n" + "=" * 50)
    print("All pipeline tasks completed successfully!")
    print("=" * 50)


if __name__ == "__main__":
    main()
