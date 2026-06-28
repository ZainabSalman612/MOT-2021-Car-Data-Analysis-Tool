import pandas as pd
import os

INPUT_FILE = os.path.join("data", "sample_2021.csv")
OUTPUT_FILE = os.path.join("data", "clean_sample_2021.csv")

def clean_data():
    print("Loading sample dataset...")
    df = pd.read_csv(INPUT_FILE)

    # -------------------------
    # 1. Convert date columns
    # -------------------------

    print("Converting date columns...")
    df['test_date'] = pd.to_datetime(df['test_date'], errors='coerce')
    df['first_use_date'] = pd.to_datetime(df['first_use_date'], errors='coerce')

    # -------------------------
    # 2. Handle missing values
    # -------------------------

    print("Handling missing values...")

    # For mileage, fill missing with 0 (or use median)
    df['test_mileage'] = df['test_mileage'].fillna(0)

    # For cylinder capacity, fill missing with median
    df['cylinder_capacity'] = df['cylinder_capacity'].fillna(df['cylinder_capacity'].median())

    # -------------------------
    # 3. Standardize text columns
    # -------------------------

    text_columns = ['make', 'model', 'colour', 'fuel_type', 'test_type', 'test_result', 'postcode_area']

    print("Standardizing text fields...")
    for col in text_columns:
        df[col] = df[col].astype(str).str.strip().str.upper()

    # -------------------------
    # 4. Save cleaned dataset
    # -------------------------

    df.to_csv(OUTPUT_FILE, index=False)

    print("\nCleaning complete!")
    print("Saved cleaned file as:", OUTPUT_FILE)

if __name__ == "__main__":
    clean_data()
