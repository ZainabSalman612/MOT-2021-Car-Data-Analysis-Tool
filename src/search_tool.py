import os
import sqlite3

# --- Configuration ---
DB_PATH = os.path.join("data", "mot_database.db")


# --- Core Search Class ---
class MOT_Search_Tool:
    def __init__(self):
        if not os.path.exists(DB_PATH):
            raise FileNotFoundError(f"Database not found at {DB_PATH}. Run the pipeline first.")
        self.db_path = DB_PATH
        print("Search tool connected to SQLite database.")

    def _get_conn(self):
        """Returns a new connection for each query (thread-safe for GUI)."""
        return sqlite3.connect(self.db_path)

    def perform_search(self, params):
        """
        Performs a combined search based on the parameters dictionary.
        Uses parameterized SQL queries on the SQLite database.

        :param params: Dictionary containing:
                       - 'make': str (e.g., 'BMW')
                       - 'model': str (e.g., '3 SERIES')
                       - 'first_use_year': str (e.g., '2014')
                       - 'mileage_min': int (in actual miles, not thousands)
                       - 'mileage_max': int (in actual miles, not thousands)
        :return: List of dictionaries (test records)
        """
        conn = self._get_conn()
        cursor = conn.cursor()

        # Build the WHERE clause dynamically
        conditions = []
        query_params = []

        make = params.get('make', '').strip().upper()
        model = params.get('model', '').strip().upper()
        first_use_year = params.get('first_use_year', '').strip()
        mileage_min = params.get('mileage_min', 0)
        mileage_max = params.get('mileage_max', 999999999)

        if make:
            conditions.append("make = ?")
            query_params.append(make)

        if model:
            conditions.append("model = ?")
            query_params.append(model)

        if first_use_year:
            conditions.append("first_use_year = ?")
            query_params.append(first_use_year)

        if mileage_min > 0:
            conditions.append("test_mileage >= ?")
            query_params.append(mileage_min)

        if mileage_max < 999999000:
            conditions.append("test_mileage <= ?")
            query_params.append(mileage_max)

        # Assemble the SQL query
        sql = "SELECT test_id, make, model, test_date, test_result, test_mileage FROM cleaned_tests"
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += " LIMIT 1000"

        cursor.execute(sql, query_params)
        columns = ['test_id', 'make', 'model', 'test_date', 'test_result', 'test_mileage']
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        conn.close()
        return results

    def get_vehicle_details(self, test_id):
        """
        Retrieves the full row data for a single test_id.
        :param test_id: The unique identifier for the test.
        :return: Dictionary of all columns for that test.
        """
        conn = self._get_conn()
        cursor = conn.cursor()

        try:
            test_id = int(test_id)
        except ValueError:
            conn.close()
            return {"Error": "Invalid Test ID format."}

        cursor.execute("SELECT * FROM cleaned_tests WHERE test_id = ?", (test_id,))
        row = cursor.fetchone()

        if row:
            # Get column names from cursor description
            columns = [desc[0] for desc in cursor.description]
            result = dict(zip(columns, row))
            conn.close()
            return result
        else:
            conn.close()
            return {"Error": f"Test ID {test_id} not found."}

    def get_distinct_makes(self):
        """Returns a sorted list of all unique vehicle makes."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT make FROM cleaned_tests ORDER BY make")
        makes = [row[0] for row in cursor.fetchall()]
        conn.close()
        return makes

    def get_models_for_make(self, make):
        """Returns a sorted list of all unique models for a given make."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT model FROM cleaned_tests WHERE make = ? ORDER BY model", (make.upper(),))
        models = [row[0] for row in cursor.fetchall()]
        conn.close()
        return models

    def get_distinct_years(self):
        """Returns a sorted list of all unique first_use_years."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT first_use_year FROM cleaned_tests WHERE first_use_year != 'UNKNOWN' ORDER BY first_use_year DESC")
        years = [row[0] for row in cursor.fetchall()]
        conn.close()
        return years


# --- Singleton Pattern for Search Tool ---
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

def get_distinct_makes():
    """GUI entry point for retrieving all unique makes."""
    return get_search_tool().get_distinct_makes()

def get_models_for_make(make):
    """GUI entry point for retrieving models for a given make."""
    return get_search_tool().get_models_for_make(make)

def get_distinct_years():
    """GUI entry point for retrieving all unique years."""
    return get_search_tool().get_distinct_years()


# --- Original main() preserved for CLI testing (optional) ---
def main():
    tool = get_search_tool()
    print("\n--- search tool ready ---")

    # Example CLI call:
    params = {'make': 'BMW', 'model': '3 SERIES', 'first_use_year': '', 'mileage_min': 0, 'mileage_max': 200000}
    results = tool.perform_search(params)
    print(f"CLI Example Search found: {len(results)} records.")


if __name__ == "__main__":
    main()