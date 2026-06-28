"# MOT 2021 Project" 
# MOT Data Processing Project

This project processes MOT (Vehicle Test) data through a complete pipeline including loading, cleaning, indexing, analysis, and reporting. The project is organised into modular Python scripts stored in the `src` folder.

---

## 📂 Project Structure

MOT_PROJECT/
│
├── data/ # input CSV files (raw and cleaned)
│ └── clean_sample_2021.csv
│
├── output/
│ ├── data_store/ # feather dataset + indices.pkl
│ ├── search_results/ # saved search exports
│ └── reports/ # generated summary reports
│
├── src/ # all Python scripts
│ ├── load_data.py
│ ├── inspect_data.py
│ ├── clean_data.py
│ ├── eda_basic.py
│ ├── analysis_stats.py
│ ├── build_index.py
│ ├── search_tool.py
│ ├── export_search.py
│ ├── summary_report.py
│ └── run_all.py
│
└── README.md


---

## ⚙️ Requirements

Install required packages:
pip install pandas pyarrow


---

## 🚀 Running the Full Pipeline

To execute all major scripts in order:

python src/run_all.py


This runs:

1. load_data.py
2. clean_data.py
3. analysis_stats.py
4. build_index.py
5. summary_report.py

---

## 🧩 Individual Scripts

### **1. load_data.py**
Loads the raw CSV files and prepares a combined dataset.

### **2. inspect_data.py**
Displays first rows, column names, and dataset shape.

### **3. clean_data.py**
Cleans the dataset, fixes types, removes missing values, and saves: data/clean_sample_2021.csv


### **4. eda_basic.py**
Creates EDA plots and saves them in: output/screenshots/


### **5. analysis_stats.py**
Generates basic numeric summaries and statistics.

### **6. build_index.py**
Creates:
- a fast-load dataset (`clean_sample_2021.feather`)
- indices for make, model, year
Stored in: output/data_store/


### **7. search_tool.py**
Interactive CLI search tool:
- search by make
- search by make + model
- search by year

### **8. export_search.py**
Saves filtered results into: output/search_results/


### **9. summary_report.py**
Generates: output/reports/summary_report.txt


### **10. run_all.py**
Runs the full workflow automatically.


## 🧬 MPI (Cluster Computing) — *Bonus Component*
This project includes an optional MPI version of the analysis using `mpi4py`.

### **Run using mpiexec:**
mpiexec -n 4 python src/mpi_analysis.py

This divides the cleaned dataset into 4 parts and computes:
- rows per chunk
- average mileage
- min / max mileage

Then gathers final combined results on the master node.

---

## 📄 Summary Report Output

The summary report includes:
- total number of vehicle records
- top 10 manufacturers
- top 10 models
- distribution of years
- mileage statistics
- overall dataset description
---

## ✔️ Notes

- All outputs are saved automatically in the `output/` folder.
- All paths use relative paths so the script works on any machine.
- The pipeline is modular — each script can run independently.
- `run_all.py` provides a complete automated workflow.
- `mpi_analysis.py` demonstrates parallel processing for extra marks.






