import pandas as pd
import os

SAMPLE_FILE = os.path.join("data", "sample_2021.csv")

def inspect_data():
    print("Loading sample dataset...\n")
    df = pd.read_csv(SAMPLE_FILE)

    print("First 5 rows:")
    print(df.head())
    print("\n")

    print("Column names:")
    print(df.columns.tolist())
    print("\n")

    print("Data types:")
    print(df.dtypes)
    print("\n")

    print("Basic Statistics:")
    print(df.describe(include='all'))
    print("\n")

    print("Missing Values per Column:")
    print(df.isna().sum())
    print("\n")

    print("Shape (rows, columns):")
    print(df.shape)

if __name__ == "__main__":
    inspect_data()
