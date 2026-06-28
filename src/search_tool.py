import os
import pandas as pd
import pickle
import numpy as np

# --- Configuration ---
DATA_DIR = os.path.join("output", "data_store")
DATA_FILE_FEATHER = os.path.join(DATA_DIR, "clean_sample_2021.feather")
DATA_FILE_PICKLE = os.path.join(DATA_DIR, "clean_sample_2021.pkl")
INDEX_FILE = os.path.join(DATA_DIR, "indices.pkl")

# --- Core Search Class ---
class MOT_Search_Tool:
    def __init__(self):
        self.df = self._load_data()
        self.indices = self._load_indices()
        
        # Pre-process: Extract Year from first_use_date for fast filtering
        self.df['first_use_year'] = self.df['first_use_date'].str[:4]


    def _load_data(self):
        print("loading dataset...")
        try:
            if os.path.exists(DATA_FILE_FEATHER):
                df = pd.read_feather(DATA_FILE_FEATHER)
            else:
                df = pd.read_pickle(DATA_FILE_PICKLE)
            print("rows loaded:", len(df))
            return df
        except Exception as e:
            print(f"Error loading data: {e}")
            return pd.DataFrame()


    def _load_indices(self):
        print("loading indices...")
        try:
            with open(INDEX_FILE, "rb") as f:
                indices = pickle.load(f)
            print("indices loaded.")
            return indices
        except Exception as e:
            print(f"Error loading indices: {e}")
            return {}
            

    def perform_search(self, params):
        """
        Performs a combined search based on the parameters dictionary.
        This function handles the logic for the basic search tab.
        
        :param params: Dictionary containing:
                       - 'make': str (e.g., 'BMW')
                       - 'model': str (e.g., '3 SERIES')
                       - 'first_use_year': str (e.g., '2014')
                       - 'mileage_min': int (in actual miles, not thousands)
                       - 'mileage_max': int (in actual miles, not thousands)
        :return: List of dictionaries (test records)
        """
        
        if self.df.empty:
            return []

        # Start with all row indices
        combined_rows = set(self.df.index) 

        # 1. Index-based filtering (Make, Model, Year)
        
        # Filter by Make & Model (Most restrictive, use the combined index)
        make = params.get('make', '').upper()
        model = params.get('model', '').upper()
        
        if make and model:
            key = (make, model)
            if 'index_make_model' in self.indices:
                 rows = self.indices['index_make_model'].get(key, [])
                 combined_rows = combined_rows.intersection(rows)
            else:
                 # Fallback to dataframe filter if index is missing (slower)
                 combined_rows = combined_rows.intersection(self.df[
                     (self.df['make'] == make) & (self.df['model'] == model)
                 ].index)
        elif make:
            if 'index_make' in self.indices:
                rows = self.indices['index_make'].get(make, [])
                combined_rows = combined_rows.intersection(rows)
            # No fallback needed as other filters will apply to all makes if this is skipped
        
        # Filter by Year (if not already handled by combined_rows)
        year = params.get('first_use_year', '')
        if year:
            if 'index_year' in self.indices:
                 rows = self.indices['index_year'].get(year, [])
                 combined_rows = combined_rows.intersection(rows)
            else:
                # Fallback to dataframe filter
                 combined_rows = combined_rows.intersection(self.df[
                    self.df['first_use_year'] == year
                 ].index)


        # 2. Mileage filtering (Must use boolean mask on DataFrame for range)
        mileage_min = params.get('mileage_min', 0)
        mileage_max = params.get('mileage_max', float('inf'))
        
        if mileage_min > 0 or mileage_max < float('inf'):
            # Create a boolean mask for the mileage condition
            mileage_mask = (self.df['test_mileage'] >= mileage_min) & (self.df['test_mileage'] <= mileage_max)
            
            # Convert current combined_rows back to a list/array for indexing
            current_df = self.df.loc[list(combined_rows)]
            
            # Apply mileage filter to the reduced set
            filtered_df = current_df[mileage_mask.loc[current_df.index]]
            
        else:
            # If no mileage filter, just use the index filtered rows
            filtered_df = self.df.loc[list(combined_rows)]
            
        
        # Convert final results to list of dictionaries
        # Use only relevant columns for initial display in the GUI Treeview
        columns_to_return = ['test_id', 'make', 'model', 'test_date', 'test_result', 'test_mileage']
        
        # Handle cases where filtered_df might be empty
        if filtered_df.empty:
            return []
            
        # Limit results for better GUI performance (e.g., top 1000)
        return filtered_df[columns_to_return].head(1000).to_dict('records')


    def get_vehicle_details(self, test_id):
        """
        Retrieves the full row data for a single test_id.
        :param test_id: The unique identifier for the test.
        :return: Dictionary of all columns for that test.
        """
        if self.df.empty:
            return {}

        # Assuming 'test_id' is the unique identifier (though it's in the column list, not the index)
        # Find the row index where test_id matches (must convert test_id to correct type if necessary)
        # Assuming test_id in the DataFrame is stored as an integer, based on the prompt's ERD.
        try:
            test_id = int(test_id)
        except ValueError:
            return {"Error": "Invalid Test ID format."}
            
        
        # Use boolean mask to find the single row
        row_match = self.df[self.df['test_id'] == test_id]

        if not row_match.empty:
            # Return the first (and only) match as a dictionary
            return row_match.iloc[0].to_dict()
        else:
            return {"Error": f"Test ID {test_id} not found."}


# --- Singleton Pattern for Search Tool ---
# Initialize the search tool instance once when the module is imported
# This ensures data is loaded only when the GUI starts.
_tool_instance = None

def get_search_tool():
    """Returns the singleton instance of MOT_Search_Tool."""
    global _tool_instance
    if _tool_instance is None:
        _tool_instance = MOT_Search_Tool()
    return _tool_instance

# --- Wrapper functions for gui_app.py to call ---
def perform_search(params):
    """GUI entry point for searching."""
    return get_search_tool().perform_search(params)

def get_vehicle_details(test_id):
    """GUI entry point for retrieving details."""
    return get_search_tool().get_vehicle_details(test_id)


# --- Original main() preserved for CLI testing (optional) ---
def main():
    tool = get_search_tool()
    
    # ... (Your original CLI logic can be reimplemented here, calling tool methods) ...
    print("\n--- search tool ready ---")

    # Example CLI call:
    params = {'make': 'BMW', 'model': '3 SERIES', 'first_use_year': '', 'mileage_min': 0, 'mileage_max': 200000}
    results = tool.perform_search(params)
    print(f"CLI Example Search found: {len(results)} records.")


if __name__ == "__main__":
    main()