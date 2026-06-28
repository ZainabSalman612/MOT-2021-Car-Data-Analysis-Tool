import pandas as pd
import os

def export_search(data, filepath):
    """
    Exports a list of dictionaries (search results) to a CSV file.
    
    This function is called by the GUI, receiving the already-filtered results 
    and the user-chosen file path.
    
    :param data: List of dictionaries (test records) passed from the GUI.
    :param filepath: The full path where the file should be saved (chosen by the user).
    :return: True if export was successful, False otherwise.
    """
    try:
        if not data:
            print("Export failed: No data provided for export.")
            return False

        # Convert the list of dictionaries into a Pandas DataFrame
        df = pd.DataFrame(data)

        # Write the DataFrame to a CSV file. 
        # index=False ensures the row index is not included in the file.
        df.to_csv(filepath, index=False)
        
        print(f"Successfully exported {len(data)} records to {filepath}")
        return True

    except Exception as e:
        print(f"Error during file export: {e}")
        # Return False so the GUI can show an appropriate error message
        return False