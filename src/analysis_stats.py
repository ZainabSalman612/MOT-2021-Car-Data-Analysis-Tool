import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
import datetime

# ====================================================================
# MODULE: analysis_stats.py
# PURPOSE: Statistical Analysis and Graph Generation (for GUI)
# ====================================================================

# --- Configuration ---
DATA_DIR = os.path.join("output", "data_store")
DATA_FILE_FEATHER = os.path.join(DATA_DIR, "clean_sample_2021.feather")
DATA_FILE_PICKLE = os.path.join(DATA_DIR, "clean_sample_2021.pkl")
OUTPUT_FILE = os.path.join("output", "analysis_summary.txt")

# --- Global Data Store ---
_df_analysis = None

def _load_analysis_data():
    """Loads the main MOT data DataFrame."""
    global _df_analysis
    if _df_analysis is not None:
        return _df_analysis
        
    # REMOVED: print("Analysis tool loading dataset...") 
    
    try:
        # NOTE: Using Feather first for performance, falling back to Pickle
        if os.path.exists(DATA_FILE_FEATHER):
            df = pd.read_feather(DATA_FILE_FEATHER)
        elif os.path.exists(DATA_FILE_PICKLE):
            df = pd.read_pickle(DATA_FILE_PICKLE)
        else:
            raise FileNotFoundError("Clean data file (feather or pickle) not found.")
        
        # Essential preprocessing for analysis (CRITICAL FOR GRAPHING)
        df['first_use_date'] = pd.to_datetime(df['first_use_date'], errors='coerce')
        df['test_date'] = pd.to_datetime(df['test_date'], errors='coerce')
        
        # Calculate Vehicle Age in Years (rounded down)
        df['vehicle_age'] = ((df['test_date'] - df['first_use_date']).dt.days / 365.25).astype(int)
        
        # Normalize make/model for filtering
        df['make'] = df['make'].str.strip().str.upper()
        df['model'] = df['model'].str.strip().str.upper()

        _df_analysis = df
        # REMOVED: print("Analysis tool data loaded and preprocessed.")
        return _df_analysis
        
    except Exception as e:
        # print(f"Error loading analysis data: {e}") # Keep this commented out for GUI
        return pd.DataFrame()


def generate_error_figure(title, message):
    """Helper function to return a clean Matplotlib error figure for the GUI."""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_title(title, color='red', fontsize=16)
    ax.text(0.5, 0.5, message, ha='center', va='center', fontsize=12)
    ax.axis('off') # Hide axes for a clean message
    plt.tight_layout()
    return fig


def generate_pass_rate_graph(make, model, criteria):
    """
    Generates a Matplotlib Figure showing pass rates by age or mileage for a specific make/model.
    """
    df = _load_analysis_data()
    
    # 1. Handle Data Load Failure
    if df.empty:
        return generate_error_figure("Data Load Error", "Data failed to load. Check file paths and preprocessing steps.")

    # 2. Filter the data for the specific Make and Model
    filtered_df = df[
        (df['make'] == make.upper()) & 
        (df['model'] == model.upper()) &
        (df['test_result'].isin(['P', 'F'])) # Only consider Pass/Fail results
    ].copy()
    
    # 3. Handle No Records Found After Filtering
    if filtered_df.empty:
        return generate_error_figure(f"No Data Found for {make} {model}", 
                                     "0 records matched the criteria (Make/Model).")

    # Convert results to a numeric 1/0 for calculation
    filtered_df['is_pass'] = (filtered_df['test_result'] == 'P').astype(int)
    
    # 4. Define Grouping Logic based on criteria
    if criteria == 'age':
        group_col = 'vehicle_age'
        x_label = "Vehicle Age (Years)"
        title_suffix = "by Age"
        
    elif criteria == 'mileage':
        group_col = 'mileage_group'
        # Group mileage by 10,000 mile intervals
        filtered_df['mileage_group'] = (filtered_df['test_mileage'] // 10000) * 10
        x_label = "Test Mileage (Thousands of Miles)"
        title_suffix = "by Mileage"
    else:
        return generate_error_figure("Invalid Criteria", 
                                     "Criteria must be 'age' or 'mileage'.")


    # 5. Calculate Pass Rate for each group
    grouped = filtered_df.groupby(group_col).agg(
        total_tests=('is_pass', 'count'),
        total_passes=('is_pass', 'sum')
    ).reset_index()
    
    # Calculate Pass Rate: total_passes / total_tests
    grouped['pass_rate'] = grouped['total_passes'] / grouped['total_tests']
    
    # Ensure there's plottable data
    if grouped.empty:
        return generate_error_figure(f"No Plottable Data for {make} {model}", 
                                     "Filtering resulted in an empty dataset for plotting.")


    # 6. Generate Matplotlib Figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plotting the Pass Rate (as a percentage)
    ax.plot(grouped[group_col], grouped['pass_rate'] * 100, 
            marker='o', linestyle='-', color='#007ACC', linewidth=2, markersize=7)

    ax.set_title(f"MOT Pass Rate for {make} {model} {title_suffix}", fontsize=16)
    ax.set_xlabel(x_label, fontsize=12)
    ax.set_ylabel("Pass Rate (%)", fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Set y-axis limits to 0-100% for clarity
    ax.set_ylim(0, 100)
    
    # Add labels to the points (Pass Rate %)
    for x, y in zip(grouped[group_col], grouped['pass_rate'] * 100):
        ax.annotate(f'{y:.1f}%', (x, y), textcoords="offset points", 
                     xytext=(0, 10), ha='center', fontsize=9)
    
    plt.tight_layout() # Adjust layout to prevent labels from overlapping
    
    return fig


# --- Original analysis_stats function preserved for CLI reporting ---
def analysis_stats():
    """Generates the original summary text report."""
    df = _load_analysis_data()
    if df.empty:
        print("Cannot run full analysis: Data failed to load.")
        return
        
    lines = []
    lines.append("=== OVERALL TEST RESULT DISTRIBUTION ===\n")
    lines.append(str(df['test_result'].value_counts()))
    lines.append("\n\n")
    
    total = len(df)
    passes = (df['test_result'] == "P").sum()
    fails = (df['test_result'] == "F").sum()
    
    lines.append("\n\n")
    
    lines.append("=== TEST RESULTS BY FUEL TYPE ===\n")
    lines.append(str(pd.crosstab(df['fuel_type'], df['test_result'])))
    
    
    with open(OUTPUT_FILE, "w") as f:
        f.write("\n".join(lines))

    # You can keep these prints here, as this function is for CLI reporting.
    print("Analysis complete!")
    print("Saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    # Example usage for CLI testing:
    try:
        fig_bmw = generate_pass_rate_graph("BMW", "3 SERIES", "age")
        fig_ferrari = generate_pass_rate_graph("FERRARI", "458", "mileage")
        
        plt.show()
    except Exception as e:
        print(f"CLI test failed: {e}")