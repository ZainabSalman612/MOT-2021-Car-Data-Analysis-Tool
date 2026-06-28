import os
import sys
import pandas as pd
import pickle

# input and output paths
INPUT_FILE = os.path.join("data", "clean_sample_2021.csv")
OUTPUT_DIR = os.path.join("output", "data_store")


def ensure_out_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def load_csv(path):
    print("Loading cleaned CSV...")
    df = pd.read_csv(path, low_memory=False)
    print("Loaded:", len(df), "rows")
    return df


def create_indices(df):
    print("Creating indices...")

    index_make = {}
    index_make_model = {}
    index_year = {}

    for i, row in df.iterrows():
        make = str(row.get("make", "")).strip().upper()
        model = str(row.get("model", "")).strip().upper()
        year_raw = str(row.get("first_use_date", ""))

        # extract year from first_use_date
        year = year_raw[:4] if len(year_raw) >= 4 else "UNKNOWN"

        index_make.setdefault(make, []).append(i)
        index_make_model.setdefault((make, model), []).append(i)
        index_year.setdefault(year, []).append(i)

    print("Indices created.")
    return {
        "index_make": index_make,
        "index_make_model": index_make_model,
        "index_year": index_year,
    }


def save_outputs(df, indices):
    ensure_out_dir(OUTPUT_DIR)

    print("Saving dataset...")
    try:
        df.reset_index(drop=True).to_feather(os.path.join(OUTPUT_DIR, "clean_sample_2021.feather"))
        print("Saved feather file.")
    except Exception as e:
        print("Feather failed, saving pickle instead.", e)
        df.to_pickle(os.path.join(OUTPUT_DIR, "clean_sample_2021.pkl"))

    print("Saving indices...")
    with open(os.path.join(OUTPUT_DIR, "indices.pkl"), "wb") as f:
        pickle.dump(indices, f)

    print("Data stored successfully in 'output/data_store'.")


def quick_test(indices):
    print("\n--- quick test ---")
    print("BMW count:", len(indices["index_make"].get("BMW", [])))
    print(("BMW", "3 SERIES"), "count:", len(indices["index_make_model"].get(("BMW", "3 SERIES"), [])))
    print("Year 2015 count:", len(indices["index_year"].get("2015", [])))


def main():
    if not os.path.exists(INPUT_FILE):
        print("error: CSV not found at:", INPUT_FILE)
        sys.exit()

    df = load_csv(INPUT_FILE)
    indices = create_indices(df)
    save_outputs(df, indices)
    quick_test(indices)


if __name__ == "__main__":
    main()
