import pandas as pd
import os
import matplotlib.pyplot as plt
from datetime import datetime

INPUT_FILE = os.path.join("data", "clean_sample_2021.csv")
OUTPUT_FOLDER = "screenshots"

def eda_basic():
    df = pd.read_csv(INPUT_FILE)

    # 1. Test Result Distribution
    plt.figure(figsize=(6,4))
    df['test_result'].value_counts().plot(kind='bar')
    plt.title("Test Result Distribution")
    plt.xlabel("Result")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_FOLDER, "test_result_distribution.png"))
    plt.close()

    # 2. Top 10 Car Makes
    plt.figure(figsize=(8,5))
    df['make'].value_counts().head(10).plot(kind='bar')
    plt.title("Top 10 Car Makes")
    plt.xlabel("Make")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_FOLDER, "top_10_makes.png"))
    plt.close()

    # 3. Fuel Type Distribution
    plt.figure(figsize=(6,4))
    df['fuel_type'].value_counts().plot(kind='bar')
    plt.title("Fuel Type Distribution")
    plt.xlabel("Fuel Type")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_FOLDER, "fuel_type_distribution.png"))
    plt.close()

    # 4. Mileage Distribution
    plt.figure(figsize=(7,5))
    df['test_mileage'].plot(kind='hist', bins=30)
    plt.title("Mileage Distribution")
    plt.xlabel("Mileage")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_FOLDER, "mileage_distribution.png"))
    plt.close()

    # 5. Vehicle Age Distribution
    current_year = 2021
    df['vehicle_age'] = current_year - pd.to_datetime(df['first_use_date']).dt.year

    plt.figure(figsize=(7,5))
    df['vehicle_age'].plot(kind='hist', bins=30)
    plt.title("Vehicle Age Distribution")
    plt.xlabel("Age (years)")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_FOLDER, "vehicle_age_distribution.png"))
    plt.close()

    print("\nEDA Completed!")
    print("Plots saved in:", OUTPUT_FOLDER)

if __name__ == "__main__":
    eda_basic()
