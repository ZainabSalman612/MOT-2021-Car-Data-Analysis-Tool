import sys, os, sqlite3
sys.path.insert(0, 'src')
os.chdir(r'c:\Users\Hp\Documents\MOT-2021-Car-Data-Analysis-Tool')

DB_PATH = os.path.join('data', 'mot_database.db')

print('=== Database State Check ===')
print(f'Database file exists: {os.path.exists(DB_PATH)}')

if os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    indexes = conn.execute("SELECT name FROM sqlite_master WHERE type='index'").fetchall()
    print(f'Tables: {[t[0] for t in tables]}')
    print(f'Indexes: {[i[0] for i in indexes]}')
    conn.close()
    print('\nDB EXISTS: GUI will open directly without running pipeline.')
else:
    print('\nNO DB: GUI will trigger the pipeline initialization dialog.')

print()
print('=== Import Test ===')
from load_data import load_in_chunks; print('  [OK] load_data')
from clean_data import clean_data; print('  [OK] clean_data')
from build_index import create_indices; print('  [OK] build_index')
from analysis_stats import generate_pass_rate_graph; print('  [OK] analysis_stats')
from summary_report import write_report; print('  [OK] summary_report')
from search_tool import perform_search, get_distinct_makes, get_models_for_make, get_distinct_years; print('  [OK] search_tool')
from export_search import export_search; print('  [OK] export_search')
print()
print('All checks passed! Ready to launch: python src/gui_app.py')
