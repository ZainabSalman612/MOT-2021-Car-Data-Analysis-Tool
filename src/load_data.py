import pandas as pd
import os

# Path to your folder
DATA_FOLDER = os.path.join("data", "dft_test_result_2021", "test_results_2021")

# Files are named test_result_1 to test_result_12
FILES = [f"test_result_{i}.csv" for i in range(1, 13)]

# Output sample file
OUTPUT_SAMPLE = os.path.join("data", "sample_2021.csv")

def load_in_chunks():
    sample_frames = []

    for file in FILES:
        path = os.path.join(DATA_FOLDER, file)

        print(f"Reading {path} ...")

        # Read 1000 rows only from each file (chunk)
        df_chunk = pd.read_csv(path, nrows=1000)

        sample_frames.append(df_chunk)

    # Combine all small chunks
    combined = pd.concat(sample_frames, ignore_index=True)

    # Save sample
    combined.to_csv(OUTPUT_SAMPLE, index=False)

    print("\nSample created successfully!")
    print("Saved as:", OUTPUT_SAMPLE)

if __name__ == "__main__":
    load_in_chunks()
