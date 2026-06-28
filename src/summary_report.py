# summary_report.py

import os
import pandas as pd

# paths
INPUT_FEATHER = os.path.join("output", "data_store", "clean_sample_2021.feather")
INPUT_PICKLE = os.path.join("output", "data_store", "clean_sample_2021.pkl")
REPORT_DIR = os.path.join("output", "reports")
REPORT_FILE = os.path.join(REPORT_DIR, "summary_report.txt")


def ensure_out_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def load_data():
    print("loading dataset...")

    if os.path.exists(INPUT_FEATHER):
        df = pd.read_feather(INPUT_FEATHER)
    else:
        df = pd.read_pickle(INPUT_PICKLE)

    print("rows loaded:", len(df))
    return df


def write_report(df):
    ensure_out_dir(REPORT_DIR)

    print("creating summary report...")

    total_rows = len(df)
    unique_makes = df["make"].nunique()
    unique_models = df["model"].nunique()

    top_makes = df["make"].value_counts().head(10)
    top_models = df["model"].value_counts().head(10)

    df["year"] = df["first_use_date"].astype(str).str[:4]
    year_counts = df["year"].value_counts()

    mileage_stats = df["test_mileage"].describe()

    with open(REPORT_FILE, "w") as f:
        f.write("MOT SUMMARY REPORT\n")
        f.write("===================\n\n")

        f.write(f"Total rows: {total_rows}\n")
        f.write(f"Unique makes: {unique_makes}\n")
        f.write(f"Unique models: {unique_models}\n\n")

        f.write("Top 10 Makes:\n")
        f.write(str(top_makes))
        f.write("\n\n")

        f.write("Top 10 Models:\n")
        f.write(str(top_models))
        f.write("\n\n")

        f.write("Year Distribution:\n")
        f.write(str(year_counts))
        f.write("\n\n")

        f.write("Mileage Statistics:\n")
        f.write(str(mileage_stats))
        f.write("\n")

    print("report saved at:", REPORT_FILE)


def main():
    df = load_data()
    write_report(df)


if __name__ == "__main__":
    main()
