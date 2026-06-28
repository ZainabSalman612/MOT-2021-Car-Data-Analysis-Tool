import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import pandas as pd
import os

# ====================================================================
# 1. IMPORT YOUR BACKEND LOGIC HERE
# ====================================================================
try:
    # Functions for Search Tab
    from search_tool import perform_search, get_vehicle_details 
    # Functions for Analysis Tab
    from analysis_stats import generate_pass_rate_graph 
    # Function for Export
    from export_search import export_search 
    
except ImportError as e:
    # Placeholder functions if imports fail
    messagebox.showerror("Import Error", f"Could not import backend module(s). Check filenames and paths: {e}")
    
    def perform_search(params):
        return [{'test_id': 106, 'make': 'BMW', 'model': '3 SERIES', 'test_date': '2023-10-15', 'test_result': 'P', 'test_mileage': 115000}]
    def get_vehicle_details(test_id):
        return {'test_id': 106, 'vehicle_id': 12345, 'make': 'BMW', 'model': '3 SERIES', 
                'test_date': '2023-10-15', 'test_result': 'P', 'test_mileage': 115000, 'fuel_type': 'PE'}
    def generate_pass_rate_graph(make, model, criteria):
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.set_title("ERROR: Placeholder Plot (Backend Error)")
        return fig
    def export_search(data, filepath):
        print(f"Placeholder: Attempted to export {len(data)} records to {filepath}")
        return False
# ====================================================================


class MOT_Data_Browser_App:
    def __init__(self, master):
        self.master = master
        master.title("MOT Data Analysis Tool (Cluster-Optimized)")
        master.geometry("1200x800") 

        # --- Variables ---
        self.make_var = tk.StringVar()
        self.model_var = tk.StringVar()
        self.mileage_min_var = tk.StringVar()
        self.mileage_max_var = tk.StringVar()
        self.first_use_year_var = tk.StringVar()
        self.analysis_make_var = tk.StringVar()
        self.analysis_model_var = tk.StringVar()
        self.analysis_criteria_var = tk.StringVar(value='age')
        self.current_search_results = [] # Store search results for export

        # 1. Setup Tab Interface
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        self.search_tab = ttk.Frame(self.notebook)
        self.analysis_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.search_tab, text='🔍 Basic Search & Display')
        self.notebook.add(self.analysis_tab, text='📈 Analysis & Reporting')

        # 2. Initialize Tabs
        self.setup_search_tab()
        self.setup_analysis_tab() 

        # 3. Status Bar
        self.status_label = ttk.Label(master, text="Application Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

# ====================================================================
# BASIC SEARCH & DISPLAY FUNCTIONALITY
# ====================================================================

    def setup_search_tab(self):
        main_frame = ttk.Frame(self.search_tab)
        main_frame.pack(fill='both', expand=True)

        # --- Left Side: Search Input Frame ---
        search_frame = ttk.LabelFrame(main_frame, text="Search Criteria")
        search_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        widgets = [
            ("Vehicle Make:", self.make_var),
            ("Vehicle Model:", self.model_var),
            ("First Use Year:", self.first_use_year_var),
            ("Min Mileage (k):", self.mileage_min_var),
            ("Max Mileage (k):", self.mileage_max_var),
        ]

        for i, (label_text, var) in enumerate(widgets):
            ttk.Label(search_frame, text=label_text).grid(row=i, column=0, sticky=tk.W, padx=5, pady=5)
            ttk.Entry(search_frame, textvariable=var, width=20).grid(row=i, column=1, padx=5, pady=5)

        # Search Button and MPI Status (Bonus Points Feature)
        search_button = ttk.Button(search_frame, text="Run Search (Cluster/MPI)", command=self.run_basic_search)
        search_button.grid(row=len(widgets), column=0, columnspan=2, pady=(10, 5))
        
        ttk.Label(search_frame, text="Backend Status: MPI Ready", foreground="green").grid(row=len(widgets) + 1, column=0, columnspan=2, pady=2)
        
        # --- Right Side: Results Display Frame ---
        results_frame = ttk.Frame(main_frame)
        results_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # A. Treeview for Search Results
        tree_cols = ("test_id", "make", "model", "test_date", "test_result", "test_mileage")
        self.results_tree = ttk.Treeview(results_frame, columns=tree_cols, show='headings')

        for col in tree_cols:
            self.results_tree.heading(col, text=col.replace('_', ' ').title())
            self.results_tree.column(col, width=100, anchor='center')

        vsb = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_tree.yview)
        hsb = ttk.Scrollbar(results_frame, orient="horizontal", command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.results_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.results_tree.bind('<<TreeviewSelect>>', self.show_test_details)

        # Export Button (New Feature)
        export_button = ttk.Button(results_frame, text="Export Current Results (CSV)", command=self.export_current_results)
        export_button.pack(pady=5, anchor=tk.E)

        # B. Details Display Area
        ttk.Label(results_frame, text="Full Details of Selected Test:").pack(pady=(10, 2), anchor=tk.W)
        self.details_text_widget = tk.Text(results_frame, height=10, state=tk.DISABLED, wrap=tk.WORD)
        self.details_text_widget.pack(side=tk.BOTTOM, fill=tk.X, pady=(0, 5))


    def run_basic_search(self):
        start_time = time.time() # Start timer
        
        # Clear previous results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self.clear_details_text()
        self.current_search_results = [] # Clear stored results

        # Get search parameters and clean/validate
        make = self.make_var.get().strip().upper()
        model = self.model_var.get().strip().upper()
        first_use_year = self.first_use_year_var.get().strip()
        
        try:
            # The GUI expects mileage in 'k' (thousands), so multiply by 1000
            mileage_min = int(self.mileage_min_var.get().strip() or 0) * 1000
        except ValueError:
            mileage_min = 0
            
        try:
            mileage_max_input = self.mileage_max_var.get().strip()
            # Set a very high default if max is blank, and multiply by 1000
            mileage_max = int(mileage_max_input or 999999) * 1000
        except ValueError:
            mileage_max = 999999 * 1000

        params = {
            'make': make, 
            'model': model, 
            'first_use_year': first_use_year, 
            'mileage_min': mileage_min, 
            'mileage_max': mileage_max
        }
        
        self.status_label.config(text="Searching database... (Distributed Search using MPI/Cluster)")
        try:
            search_results = perform_search(params) 
            self.current_search_results = search_results # Store results for export
            
            for record in search_results:
                values = (
                    record.get('test_id'), record.get('make'), record.get('model'), 
                    record.get('test_date'), record.get('test_result'), record.get('test_mileage')
                )
                self.results_tree.insert('', tk.END, values=values, iid=record.get('test_id')) 
            
            end_time = time.time()
            elapsed_time = end_time - start_time
                                         
            self.status_label.config(text=f"Search Complete. Found {len(search_results)} records in {elapsed_time:.3f} seconds.")
            if not search_results:
                 messagebox.showinfo("No Results", "No tests matched the specified criteria.")

        except Exception as e:
            messagebox.showerror("Search Error", f"An error occurred during search: {e}")
            self.status_label.config(text="Search Failed.")


    def export_current_results(self):
        """Saves the current search results to a file using the backend export tool."""
        if not self.current_search_results:
            messagebox.showwarning("No Data", "Please run a search first to generate results for export.")
            return

        # Use a standard file dialog to get the save location
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save Search Results"
        )
        
        if filepath:
            self.status_label.config(text=f"Exporting {len(self.current_search_results)} records...")
            try:
                # Call the backend export function
                success = export_search(self.current_search_results, filepath)
                
                if success:
                    messagebox.showinfo("Export Success", f"Successfully exported {len(self.current_search_results)} records to:\n{filepath}")
                    self.status_label.config(text=f"Export complete. Saved to {os.path.basename(filepath)}")
                else:
                    messagebox.showerror("Export Failed", "The export function returned a failure status.")
                    self.status_label.config(text="Export failed.")
                    
            except Exception as e:
                messagebox.showerror("Export Error", f"An error occurred during export: {e}")
                self.status_label.config(text="Export failed.")

    def clear_details_text(self):
        self.details_text_widget.config(state=tk.NORMAL)
        self.details_text_widget.delete('1.0', tk.END)
        self.details_text_widget.insert(tk.END, "Select a test above for full details.")
        self.details_text_widget.config(state=tk.DISABLED)


    def show_test_details(self, event):
        selected_item = self.results_tree.selection()
        if not selected_item:
            return

        test_id = self.results_tree.item(selected_item, 'iid') 
        self.status_label.config(text=f"Retrieving full details for Test ID: {test_id}")
        
        try:
            full_record = get_vehicle_details(test_id) 
            
            details_text = "--- Full Test Details ---\n"
            for key in sorted(full_record.keys()):
                value = full_record[key]
                details_text += f"{key.replace('_', ' ').title():<20}: {value}\n"
            
            self.details_text_widget.config(state=tk.NORMAL)
            self.details_text_widget.delete('1.0', tk.END)
            self.details_text_widget.insert(tk.END, details_text)
            self.details_text_widget.config(state=tk.DISABLED)
            self.status_label.config(text=f"Details retrieved for Test ID: {test_id}")
            
        except Exception as e:
            self.clear_details_text()
            self.details_text_widget.config(state=tk.NORMAL)
            self.details_text_widget.insert(tk.END, f"Error retrieving full details for Test ID {test_id}: {e}")
            self.details_text_widget.config(state=tk.DISABLED)
            self.status_label.config(text="Error in detail retrieval.")


# ====================================================================
# ANALYSIS & REPORTING FUNCTIONALITY
# ====================================================================

    def setup_analysis_tab(self):
        control_frame = ttk.LabelFrame(self.analysis_tab, text="Analysis Parameters")
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # 1. Input Fields
        ttk.Label(control_frame, text="Make:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(control_frame, textvariable=self.analysis_make_var, width=15).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(control_frame, text="Model:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(control_frame, textvariable=self.analysis_model_var, width=15).grid(row=0, column=3, padx=5, pady=5)
        
        # 2. Criteria Selection (Age or Mileage)
        ttk.Label(control_frame, text="Group By:").grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        criteria_options = ['age', 'mileage']
        ttk.OptionMenu(control_frame, self.analysis_criteria_var, self.analysis_criteria_var.get(), *criteria_options).grid(row=0, column=5, padx=5, pady=5)

        # 3. Generate Report Button
        report_button = ttk.Button(control_frame, text="Generate Pass Rate Report (Cluster/MPI)", command=self.run_analysis_report)
        report_button.grid(row=0, column=6, padx=15, pady=5)
        
        # 4. Graph Display Area
        self.graph_frame = ttk.Frame(self.analysis_tab)
        self.graph_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Placeholder for the Matplotlib canvas
        self.canvas_widget = None


    def run_analysis_report(self):
        start_time = time.time()
        make = self.analysis_make_var.get().strip().upper()
        model = self.analysis_model_var.get().strip().upper()
        criteria = self.analysis_criteria_var.get()
        
        if not make or not model:
            messagebox.showwarning("Missing Input", "Please enter both Vehicle Make and Model for analysis.")
            return
        
        self.status_label.config(text=f"Generating pass rate report for {make} {model} by {criteria}...")
        
        # Clear previous graph
        if self.canvas_widget:
            self.canvas_widget.destroy()
            
        try:
            fig = generate_pass_rate_graph(make, model, criteria) 
            
            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            self.canvas_widget = canvas.get_tk_widget()
            self.canvas_widget.pack(fill=tk.BOTH, expand=True)
            canvas.draw()
            
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            self.status_label.config(text=f"Report generated successfully for {make} {model} in {elapsed_time:.3f} seconds.")
            
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Failed to generate report: {e}")
            self.status_label.config(text="Analysis Failed.")
            # Create a blank plot to indicate failure
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.set_title("ERROR: Failed to Generate Plot")
            ax.text(0.5, 0.5, f"Error: {e}", ha='center', va='center', wrap=True)
            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            self.canvas_widget = canvas.get_tk_widget()
            self.canvas_widget.pack(fill=tk.BOTH, expand=True)
            canvas.draw()


# ====================================================================
# Main Execution
# ====================================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = MOT_Data_Browser_App(root)
    root.mainloop()