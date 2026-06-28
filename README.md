# 🚗 MOT 2021 Car Data Analysis Tool

A desktop data analysis tool for exploring the full UK **2021 MOT test results dataset** — over **40 million vehicle test records**. Built with Python, SQLite, Tkinter, and Matplotlib.

---

## ✨ Features

- **Automatic first-time setup** — on first launch, the app processes all raw CSV files and builds a local SQLite database automatically, with a progress bar
- **Fast search** — filter by Make, Model, First Use Year, and Mileage range using indexed SQL queries
- **Dynamic dropdowns** — Make → Model comboboxes auto-populate from the database
- **Full record details** — click any search result to view the complete test record
- **Pass rate charts** — generate dark-themed Matplotlib graphs showing MOT pass rate by vehicle age or mileage
- **CSV export** — save any search result set to a CSV file
- **Dark mode UI** — premium dark theme throughout

---

## 📂 Project Structure

```
MOT-2021-Car-Data-Analysis-Tool/
│
├── data/
│   ├── dft_test_result_2021/
│   │   └── test_results_2021/
│   │       ├── test_result_1.csv   ← raw dataset (not on GitHub)
│   │       ├── test_result_2.csv
│   │       └── ... (12 files total, ~4.4 GB)
│   └── mot_database.db             ← generated on first run (not on GitHub)
│
├── output/
│   └── reports/
│       └── summary_report.txt      ← generated on first run
│
├── src/
│   ├── gui_app.py          ← main entry point (run this)
│   ├── load_data.py        ← loads 12 CSV files into SQLite in chunks
│   ├── clean_data.py       ← cleans and standardises the raw data
│   ├── build_index.py      ← creates SQL indexes for fast querying
│   ├── analysis_stats.py   ← statistical analysis + Matplotlib charts
│   ├── summary_report.py   ← generates summary_report.txt
│   ├── search_tool.py      ← search and filter logic (SQL queries)
│   ├── export_search.py    ← exports search results to CSV
│   ├── inspect_data.py     ← CLI utility to inspect raw data
│   ├── eda_basic.py        ← basic exploratory data analysis
│   └── mpi_analysis.py     ← optional MPI parallel analysis
│
├── requirements.txt
├── verify_setup.py         ← checks imports and database state
└── README.md
```

---

## ⚙️ Requirements

**Python 3.10+** is required.

Install all dependencies:

```bash
pip install -r requirements.txt
```

`requirements.txt` includes:
```
pandas>=2.0.0
numpy>=1.25.0
matplotlib>=3.7.0
```

> `sqlite3` and `tkinter` are included with Python — no extra install needed.

---

## 🗂️ Dataset

Download the **2021 MOT test results** dataset from the UK government:  
🔗 https://www.data.gov.uk/dataset/e3939ef8-30c7-4ca8-9c7c-ad9475cc9b2f/anonymised-mot-tests-and-results

Place the 12 CSV files into:
```
data/dft_test_result_2021/test_results_2021/
```
Files should be named `test_result_1.csv` through `test_result_12.csv`.

---

## 🚀 How to Run

There is only **one command** to run:

```bash
python src/gui_app.py
```

### First Launch (no database yet)

A setup dialog will appear automatically and run the full data pipeline:

```
📂 Stage 1/5 — Loading raw CSV files into database...   (0–50%)
🧹 Stage 2/5 — Cleaning and standardising data...       (50–78%)
🔧 Stage 3/5 — Building search indexes...               (78–90%)
📊 Stage 4/5 — Running statistical analysis...          (90–97%)
📋 Stage 5/5 — Generating summary report...             (97–100%)
✅ Database ready — GUI opens
```

> ⏱️ This takes several hours on the full 40M-row dataset. You can let it run overnight.

### Subsequent Launches

The GUI opens directly — the pipeline is skipped since the database already exists.

---

## 🖥️ GUI Guide

### Search Tab
| Control | Description |
|---|---|
| **Vehicle Make** | Dropdown of all unique makes in the database |
| **Vehicle Model** | Auto-filters to models for selected make |
| **First Use Year** | Filter by registration year |
| **Min / Max Mileage** | Filter by mileage range (in thousands) |
| **Run Search** | Returns up to 1,000 matching records |
| **Export Results** | Save the current results as a CSV file |

Click any row in the results table to view the full test record details at the bottom.

### Analysis Tab
| Control | Description |
|---|---|
| **Make + Model** | Select a vehicle to analyse |
| **Group By** | `age` (years) or `mileage` |
| **Generate Report** | Plots MOT pass rate chart for the selected vehicle |

---

## 🗄️ Database

The database file (`data/mot_database.db`) is a local SQLite file created on first run. It is excluded from Git (via `.gitignore`) because of its size (~10–15 GB for 40M rows).

| Table | Description |
|---|---|
| `cleaned_tests` | All 40M cleaned and standardised MOT test records |

| Index | Column(s) | Purpose |
|---|---|---|
| `idx_make` | `make` | Fast make filtering |
| `idx_make_model` | `make, model` | Fast make+model filtering |
| `idx_first_use_year` | `first_use_year` | Fast year filtering |
| `idx_test_mileage` | `test_mileage` | Fast mileage range queries |
| `idx_test_id` | `test_id` | Fast single-record lookup |

---

## 🔍 Verify Setup

Run this to confirm everything is installed and working:

```bash
python verify_setup.py
```

---

## 📄 Output Files

| File | Location | Description |
|---|---|---|
| SQLite database | `data/mot_database.db` | All 40M cleaned records |
| Analysis summary | `output/analysis_summary.txt` | Test result distribution |
| Summary report | `output/reports/summary_report.txt` | Top makes, models, years, mileage stats |

---

## 🧬 Optional: MPI Parallel Analysis

For HPC/cluster environments, an MPI version is included:

```bash
mpiexec -n 4 python src/mpi_analysis.py
```

Divides the dataset across 4 processes to compute mileage statistics in parallel.

---

## 📝 Notes

- All file paths use relative references — the tool works on any machine
- The raw CSV files and database are excluded from version control
- The pipeline is modular — each `src/` script can also be run independently for testing
- Re-running the pipeline: delete `data/mot_database.db` and relaunch `gui_app.py`
