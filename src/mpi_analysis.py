from mpi4py import MPI
import pandas as pd
import os
import numpy as np

# relative path
CSV_PATH = os.path.join("data", "clean_sample_2021.csv")

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

def load_data():
    df = pd.read_csv(CSV_PATH)
    return df

def analyze_chunk(df_chunk):
    return {
        "rows": len(df_chunk),
        "avg_mileage": df_chunk["test_mileage"].mean(),
        "max_mileage": df_chunk["test_mileage"].max(),
        "min_mileage": df_chunk["test_mileage"].min(),
    }

def main():
    if rank == 0:
        print(f"Master starting with {size} total processes...")
        df = load_data()
        chunks = np.array_split(df, size)
    else:
        chunks = None

    my_chunk = comm.scatter(chunks, root=0)

    local_result = analyze_chunk(my_chunk)

    results = comm.gather(local_result, root=0)

    if rank == 0:
        print("\n--- Combined MPI Results ---")
        
        total_rows = sum(r["rows"] for r in results)
        avg_mileage = sum(r["avg_mileage"] for r in results) / size
        max_mileage = max(r["max_mileage"] for r in results)
        min_mileage = min(r["min_mileage"] for r in results)

        print("Total rows:", total_rows)
        print("Average Mileage:", avg_mileage)
        print("Max Mileage:", max_mileage)
        print("Min Mileage:", min_mileage)

if __name__ == "__main__":
    main()
