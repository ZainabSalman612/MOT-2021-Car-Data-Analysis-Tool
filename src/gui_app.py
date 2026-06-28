import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import os
import sys
import threading
import sqlite3

# ====================================================================
# Ensure project root is correct for relative paths
# ====================================================================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))

DB_PATH = os.path.join("data", "mot_database.db")

# ====================================================================
# IMPORT BACKEND LOGIC
# ====================================================================
try:
    from search_tool import perform_search, get_vehicle_details, get_distinct_makes, get_models_for_make, get_distinct_years
    from analysis_stats import generate_pass_rate_graph
    from export_search import export_search
except ImportError as e:
    messagebox.showerror("Import Error", f"Could not import backend module(s): {e}")
    sys.exit(1)


# ====================================================================
# DARK THEME COLORS
# ====================================================================
COLORS = {
    'bg':           '#1e1e2e',
    'surface':      '#252538',
    'surface_alt':  '#2a2a3d',
    'border':       '#45475a',
    'text':         '#cdd6f4',
    'text_dim':     '#a6adc8',
    'accent':       '#89b4fa',
    'accent_hover': '#b4befe',
    'green':        '#a6e3a1',
    'red':          '#f38ba8',
    'yellow':       '#f9e2af',
    'treeview_odd': '#252538',
    'treeview_even':'#2a2a3d',
    'button':       '#45475a',
    'button_hover': '#585b70',
    'entry_bg':     '#313244',
}


def apply_dark_theme(root):
    """Configure ttk styles for a premium dark mode look."""
    style = ttk.Style(root)
    style.theme_use('clam')

    # General frames and labels
    style.configure('TFrame', background=COLORS['bg'])
    style.configure('TLabel', background=COLORS['bg'], foreground=COLORS['text'], font=('Segoe UI', 10))
    style.configure('TLabelframe', background=COLORS['bg'], foreground=COLORS['accent'], font=('Segoe UI', 11, 'bold'))
    style.configure('TLabelframe.Label', background=COLORS['bg'], foreground=COLORS['accent'], font=('Segoe UI', 11, 'bold'))

    # Buttons
    style.configure('TButton', background=COLORS['button'], foreground=COLORS['text'],
                     font=('Segoe UI', 10, 'bold'), borderwidth=0, padding=(12, 6))
    style.map('TButton',
              background=[('active', COLORS['button_hover']), ('pressed', COLORS['accent'])],
              foreground=[('active', COLORS['text']), ('pressed', COLORS['bg'])])

    # Accent buttons
    style.configure('Accent.TButton', background=COLORS['accent'], foreground=COLORS['bg'],
                     font=('Segoe UI', 10, 'bold'), borderwidth=0, padding=(14, 8))
    style.map('Accent.TButton',
              background=[('active', COLORS['accent_hover']), ('pressed', '#7287cf')],
              foreground=[('active', COLORS['bg'])])

    # Notebook tabs
    style.configure('TNotebook', background=COLORS['bg'], borderwidth=0)
    style.configure('TNotebook.Tab', background=COLORS['surface'], foreground=COLORS['text_dim'],
                     font=('Segoe UI', 11), padding=(16, 8), borderwidth=0)
    style.map('TNotebook.Tab',
              background=[('selected', COLORS['accent']), ('active', COLORS['button_hover'])],
              foreground=[('selected', COLORS['bg']), ('active', COLORS['text'])])

    # Combobox
    style.configure('TCombobox', fieldbackground=COLORS['entry_bg'], foreground=COLORS['text'],
                     background=COLORS['button'], borderwidth=1, arrowcolor=COLORS['accent'])
    style.map('TCombobox', fieldbackground=[('readonly', COLORS['entry_bg'])],
              foreground=[('readonly', COLORS['text'])])

    # Entry
    style.configure('TEntry', fieldbackground=COLORS['entry_bg'], foreground=COLORS['text'],
                     borderwidth=1, insertcolor=COLORS['text'])

    # Treeview
    style.configure('Treeview',
                     background=COLORS['surface'],
                     foreground=COLORS['text'],
                     fieldbackground=COLORS['surface'],
                     font=('Segoe UI', 10),
                     rowheight=28,
                     borderwidth=0)
    style.configure('Treeview.Heading',
                     background=COLORS['button'],
                     foreground=COLORS['accent'],
                     font=('Segoe UI', 10, 'bold'),
                     borderwidth=0)
    style.map('Treeview',
              background=[('selected', COLORS['accent'])],
              foreground=[('selected', COLORS['bg'])])

    # Scrollbar
    style.configure('Vertical.TScrollbar', background=COLORS['surface'], troughcolor=COLORS['bg'],
                     arrowcolor=COLORS['text_dim'], borderwidth=0)
    style.configure('Horizontal.TScrollbar', background=COLORS['surface'], troughcolor=COLORS['bg'],
                     arrowcolor=COLORS['text_dim'], borderwidth=0)

    # Progressbar
    style.configure('TProgressbar', troughcolor=COLORS['surface'], background=COLORS['accent'],
                     thickness=20, borderwidth=0)

    # OptionMenu
    style.configure('TMenubutton', background=COLORS['button'], foreground=COLORS['text'],
                     font=('Segoe UI', 10))


def is_database_ready():
    """Check if the SQLite database exists and has the cleaned_tests table with indexes."""
    if not os.path.exists(DB_PATH):
        return False
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM cleaned_tests LIMIT 1")
        count = cursor.fetchone()[0]
        # Check if an index exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_make'")
        has_index = cursor.fetchone() is not None
        conn.close()
        return count > 0 and has_index
    except Exception:
        return False


# ====================================================================
# PIPELINE INITIALIZATION DIALOG
# ====================================================================
class PipelineInitDialog:
    """A modal dialog that runs the data pipeline with a progress bar."""

    def __init__(self, parent):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Initializing Database")
        self.dialog.geometry("550x320")
        self.dialog.configure(bg=COLORS['bg'])
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - 275
        y = (self.dialog.winfo_screenheight() // 2) - 160
        self.dialog.geometry(f"+{x}+{y}")

        # Title
        title_lbl = tk.Label(self.dialog, text="⚙️  First-Time Setup", font=('Segoe UI', 18, 'bold'),
                             bg=COLORS['bg'], fg=COLORS['accent'])
        title_lbl.pack(pady=(25, 5))

        desc_lbl = tk.Label(self.dialog,
                            text="Loading and processing all 40 million MOT records.\nThis only needs to run once.",
                            font=('Segoe UI', 10), bg=COLORS['bg'], fg=COLORS['text_dim'], justify='center')
        desc_lbl.pack(pady=(0, 20))

        # Current stage label
        self.stage_label = tk.Label(self.dialog, text="Preparing...", font=('Segoe UI', 11),
                                    bg=COLORS['bg'], fg=COLORS['text'])
        self.stage_label.pack(pady=(0, 8))

        # Progress bar
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(self.dialog, variable=self.progress_var, maximum=100,
                                             length=450, style='TProgressbar')
        self.progress_bar.pack(pady=(0, 8))

        # Progress percentage label
        self.pct_label = tk.Label(self.dialog, text="0%", font=('Segoe UI', 10, 'bold'),
                                  bg=COLORS['bg'], fg=COLORS['accent'])
        self.pct_label.pack()

        # Status label
        self.status_label = tk.Label(self.dialog, text="", font=('Segoe UI', 9),
                                     bg=COLORS['bg'], fg=COLORS['text_dim'])
        self.status_label.pack(pady=(10, 0))

        self.success = False
        self.error_msg = None

    def run_pipeline(self):
        """Start the pipeline in a background thread."""
        thread = threading.Thread(target=self._run_pipeline_thread, daemon=True)
        thread.start()
        self._poll_completion(thread)

    def _update_stage(self, stage_text):
        self.dialog.after(0, lambda: self.stage_label.config(text=stage_text))

    def _update_progress(self, pct):
        self.dialog.after(0, lambda: self.progress_var.set(pct))
        self.dialog.after(0, lambda: self.pct_label.config(text=f"{int(pct)}%"))

    def _run_pipeline_thread(self):
        try:
            from load_data import load_in_chunks
            from clean_data import clean_data
            from build_index import create_indices
            from analysis_stats import analysis_stats
            from summary_report import write_report

            # Stage 1: Load data (0-50%)
            self._update_stage("📂  Stage 1/5 — Loading raw CSV files into database...")
            def load_progress(pct):
                self._update_progress(pct * 0.50)
            load_in_chunks(progress_callback=load_progress)

            # Stage 2: Clean data (50-78%)
            self._update_stage("🧹  Stage 2/5 — Cleaning and standardizing data...")
            def clean_progress(pct):
                self._update_progress(50 + pct * 0.28)
            clean_data(progress_callback=clean_progress)

            # Stage 3: Build indexes (78-90%)
            self._update_stage("🔧  Stage 3/5 — Building search indexes...")
            def index_progress(pct):
                self._update_progress(78 + pct * 0.12)
            create_indices(progress_callback=index_progress)

            # Stage 4: Analysis stats (90-97%)
            self._update_stage("📊  Stage 4/5 — Running statistical analysis...")
            analysis_stats()
            self._update_progress(97)

            # Stage 5: Summary report (97-100%)
            self._update_stage("📋  Stage 5/5 — Generating summary report...")
            def report_progress(pct):
                self._update_progress(97 + pct * 0.03)
            write_report(progress_callback=report_progress)

            self._update_progress(100)
            self._update_stage("✅  Database initialization complete!")
            self.success = True

        except Exception as e:
            self.error_msg = str(e)
            self._update_stage(f"❌  Error: {e}")

    def _poll_completion(self, thread):
        if thread.is_alive():
            self.dialog.after(200, lambda: self._poll_completion(thread))
        else:
            if self.success:
                self.dialog.after(1200, self.dialog.destroy)
            else:
                self.status_label.config(text="Pipeline failed. Close and fix the error, then restart.",
                                         fg=COLORS['red'])


# ====================================================================
# MAIN APPLICATION
# ====================================================================
class MOT_Data_Browser_App:
    def __init__(self, master):
        self.master = master
        master.title("MOT Data Analysis Tool")
        master.geometry("1280x850")
        master.configure(bg=COLORS['bg'])

        apply_dark_theme(master)

        # --- Variables ---
        self.make_var = tk.StringVar()
        self.model_var = tk.StringVar()
        self.mileage_min_var = tk.StringVar()
        self.mileage_max_var = tk.StringVar()
        self.first_use_year_var = tk.StringVar()
        self.analysis_make_var = tk.StringVar()
        self.analysis_model_var = tk.StringVar()
        self.analysis_criteria_var = tk.StringVar(value='age')
        self.current_search_results = []

        # Cache for dropdown data
        self._makes_list = []
        self._years_list = []

        # 1. Setup Tab Interface
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=True, fill='both', padx=12, pady=(12, 0))

        self.search_tab = ttk.Frame(self.notebook)
        self.analysis_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.search_tab, text='  🔍  Search & Display  ')
        self.notebook.add(self.analysis_tab, text='  📈  Analysis & Reporting  ')

        # 2. Initialize Tabs
        self.setup_search_tab()
        self.setup_analysis_tab()

        # 3. Status Bar
        self.status_label = tk.Label(master, text=" Application Ready", anchor=tk.W,
                                     bg=COLORS['surface'], fg=COLORS['text_dim'],
                                     font=('Segoe UI', 9), padx=10, pady=4)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        # 4. Load dropdown data
        self._load_dropdown_data()

    def _load_dropdown_data(self):
        """Load makes and years from the database for the comboboxes."""
        try:
            self._makes_list = get_distinct_makes()
            self._years_list = get_distinct_years()

            # Populate search tab comboboxes
            self.make_combo['values'] = [''] + self._makes_list
            self.year_combo['values'] = [''] + self._years_list

            # Populate analysis tab comboboxes
            self.analysis_make_combo['values'] = self._makes_list
            self.status_label.config(text=f" ✅ Loaded {len(self._makes_list)} makes, {len(self._years_list)} years from database")
        except Exception as e:
            self.status_label.config(text=f" ⚠️ Error loading dropdown data: {e}")

    def _on_make_selected(self, event=None):
        """When a make is selected, populate the model dropdown with matching models."""
        make = self.make_var.get().strip()
        if make:
            try:
                models = get_models_for_make(make)
                self.model_combo['values'] = [''] + models
                self.model_var.set('')
            except Exception:
                self.model_combo['values'] = []
        else:
            self.model_combo['values'] = []
            self.model_var.set('')

    def _on_analysis_make_selected(self, event=None):
        """When a make is selected on analysis tab, populate that model dropdown."""
        make = self.analysis_make_var.get().strip()
        if make:
            try:
                models = get_models_for_make(make)
                self.analysis_model_combo['values'] = models
                self.analysis_model_var.set('')
            except Exception:
                self.analysis_model_combo['values'] = []
        else:
            self.analysis_model_combo['values'] = []
            self.analysis_model_var.set('')


# ====================================================================
# BASIC SEARCH & DISPLAY FUNCTIONALITY
# ====================================================================

    def setup_search_tab(self):
        main_frame = ttk.Frame(self.search_tab)
        main_frame.pack(fill='both', expand=True)

        # --- Left Side: Search Input Frame ---
        search_frame = ttk.LabelFrame(main_frame, text="  Search Criteria  ")
        search_frame.pack(side=tk.LEFT, fill=tk.Y, padx=12, pady=12)

        row = 0

        # Make dropdown
        ttk.Label(search_frame, text="Vehicle Make:").grid(row=row, column=0, sticky=tk.W, padx=8, pady=6)
        self.make_combo = ttk.Combobox(search_frame, textvariable=self.make_var, width=22, state='readonly')
        self.make_combo.grid(row=row, column=1, padx=8, pady=6)
        self.make_combo.bind('<<ComboboxSelected>>', self._on_make_selected)
        row += 1

        # Model dropdown
        ttk.Label(search_frame, text="Vehicle Model:").grid(row=row, column=0, sticky=tk.W, padx=8, pady=6)
        self.model_combo = ttk.Combobox(search_frame, textvariable=self.model_var, width=22, state='readonly')
        self.model_combo.grid(row=row, column=1, padx=8, pady=6)
        row += 1

        # First Use Year dropdown
        ttk.Label(search_frame, text="First Use Year:").grid(row=row, column=0, sticky=tk.W, padx=8, pady=6)
        self.year_combo = ttk.Combobox(search_frame, textvariable=self.first_use_year_var, width=22, state='readonly')
        self.year_combo.grid(row=row, column=1, padx=8, pady=6)
        row += 1

        # Mileage entries
        ttk.Label(search_frame, text="Min Mileage (k):").grid(row=row, column=0, sticky=tk.W, padx=8, pady=6)
        min_entry = ttk.Entry(search_frame, textvariable=self.mileage_min_var, width=24)
        min_entry.grid(row=row, column=1, padx=8, pady=6)
        row += 1

        ttk.Label(search_frame, text="Max Mileage (k):").grid(row=row, column=0, sticky=tk.W, padx=8, pady=6)
        max_entry = ttk.Entry(search_frame, textvariable=self.mileage_max_var, width=24)
        max_entry.grid(row=row, column=1, padx=8, pady=6)
        row += 1

        # Search Button
        search_button = ttk.Button(search_frame, text="🔍  Run Search", command=self.run_basic_search,
                                    style='Accent.TButton')
        search_button.grid(row=row, column=0, columnspan=2, pady=(18, 8), padx=8, sticky='ew')
        row += 1

        # Clear Button
        clear_button = ttk.Button(search_frame, text="Clear Filters", command=self._clear_search_filters)
        clear_button.grid(row=row, column=0, columnspan=2, pady=(4, 8), padx=8, sticky='ew')

        # --- Right Side: Results Display Frame ---
        results_frame = ttk.Frame(main_frame)
        results_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=12, pady=12)

        # A. Treeview for Search Results
        tree_cols = ("test_id", "make", "model", "test_date", "test_result", "test_mileage")
        self.results_tree = ttk.Treeview(results_frame, columns=tree_cols, show='headings')

        col_widths = {'test_id': 120, 'make': 130, 'model': 150, 'test_date': 110, 'test_result': 90, 'test_mileage': 110}
        for col in tree_cols:
            self.results_tree.heading(col, text=col.replace('_', ' ').title())
            self.results_tree.column(col, width=col_widths.get(col, 100), anchor='center')

        # Tag for alternating row colors
        self.results_tree.tag_configure('oddrow', background=COLORS['treeview_odd'])
        self.results_tree.tag_configure('evenrow', background=COLORS['treeview_even'])

        vsb = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_tree.yview)
        hsb = ttk.Scrollbar(results_frame, orient="horizontal", command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.results_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.results_tree.bind('<<TreeviewSelect>>', self.show_test_details)

        # Export Button
        export_button = ttk.Button(results_frame, text="📥  Export Results (CSV)", command=self.export_current_results)
        export_button.pack(pady=6, anchor=tk.E)

        # B. Details Display Area
        ttk.Label(results_frame, text="Full Details of Selected Test:").pack(pady=(10, 2), anchor=tk.W)
        self.details_text_widget = tk.Text(results_frame, height=8, state=tk.DISABLED, wrap=tk.WORD,
                                           bg=COLORS['surface'], fg=COLORS['text'],
                                           font=('Consolas', 10), insertbackground=COLORS['text'],
                                           relief='flat', padx=8, pady=6)
        self.details_text_widget.pack(side=tk.BOTTOM, fill=tk.X, pady=(0, 5))

    def _clear_search_filters(self):
        """Reset all search filters."""
        self.make_var.set('')
        self.model_var.set('')
        self.model_combo['values'] = []
        self.first_use_year_var.set('')
        self.mileage_min_var.set('')
        self.mileage_max_var.set('')
        self.status_label.config(text=" Filters cleared.")

    def run_basic_search(self):
        start_time = time.time()

        # Clear previous results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self.clear_details_text()
        self.current_search_results = []

        # Get search parameters
        make = self.make_var.get().strip().upper()
        model = self.model_var.get().strip().upper()
        first_use_year = self.first_use_year_var.get().strip()

        try:
            mileage_min = int(self.mileage_min_var.get().strip() or 0) * 1000
        except ValueError:
            mileage_min = 0

        try:
            mileage_max_input = self.mileage_max_var.get().strip()
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

        self.status_label.config(text=" 🔄 Searching database...")
        self.master.update_idletasks()

        try:
            search_results = perform_search(params)
            self.current_search_results = search_results

            for idx, record in enumerate(search_results):
                tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                values = (
                    record.get('test_id'), record.get('make'), record.get('model'),
                    record.get('test_date'), record.get('test_result'), record.get('test_mileage')
                )
                self.results_tree.insert('', tk.END, values=values, iid=str(record.get('test_id')), tags=(tag,))

            end_time = time.time()
            elapsed_time = end_time - start_time

            self.status_label.config(text=f" ✅ Found {len(search_results)} records in {elapsed_time:.3f}s")
            if not search_results:
                messagebox.showinfo("No Results", "No tests matched the specified criteria.")

        except Exception as e:
            messagebox.showerror("Search Error", f"An error occurred during search: {e}")
            self.status_label.config(text=" ❌ Search Failed.")


    def export_current_results(self):
        """Saves the current search results to a file using the backend export tool."""
        if not self.current_search_results:
            messagebox.showwarning("No Data", "Please run a search first to generate results for export.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save Search Results"
        )

        if filepath:
            self.status_label.config(text=f" Exporting {len(self.current_search_results)} records...")
            try:
                success = export_search(self.current_search_results, filepath)

                if success:
                    messagebox.showinfo("Export Success", f"Successfully exported {len(self.current_search_results)} records to:\n{filepath}")
                    self.status_label.config(text=f" ✅ Export complete. Saved to {os.path.basename(filepath)}")
                else:
                    messagebox.showerror("Export Failed", "The export function returned a failure status.")
                    self.status_label.config(text=" ❌ Export failed.")

            except Exception as e:
                messagebox.showerror("Export Error", f"An error occurred during export: {e}")
                self.status_label.config(text=" ❌ Export failed.")

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
        self.status_label.config(text=f" Retrieving details for Test ID: {test_id}")

        try:
            full_record = get_vehicle_details(test_id)

            details_text = "━━━ Full Test Details ━━━\n\n"
            for key in sorted(full_record.keys()):
                value = full_record[key]
                details_text += f"  {key.replace('_', ' ').title():<22}: {value}\n"

            self.details_text_widget.config(state=tk.NORMAL)
            self.details_text_widget.delete('1.0', tk.END)
            self.details_text_widget.insert(tk.END, details_text)
            self.details_text_widget.config(state=tk.DISABLED)
            self.status_label.config(text=f" ✅ Details retrieved for Test ID: {test_id}")

        except Exception as e:
            self.clear_details_text()
            self.details_text_widget.config(state=tk.NORMAL)
            self.details_text_widget.insert(tk.END, f"Error retrieving details for Test ID {test_id}: {e}")
            self.details_text_widget.config(state=tk.DISABLED)
            self.status_label.config(text=" ❌ Error in detail retrieval.")


# ====================================================================
# ANALYSIS & REPORTING FUNCTIONALITY
# ====================================================================

    def setup_analysis_tab(self):
        control_frame = ttk.LabelFrame(self.analysis_tab, text="  Analysis Parameters  ")
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=12, pady=12)

        # Make combobox
        ttk.Label(control_frame, text="Make:").grid(row=0, column=0, padx=8, pady=8, sticky=tk.W)
        self.analysis_make_combo = ttk.Combobox(control_frame, textvariable=self.analysis_make_var,
                                                 width=18, state='readonly')
        self.analysis_make_combo.grid(row=0, column=1, padx=8, pady=8)
        self.analysis_make_combo.bind('<<ComboboxSelected>>', self._on_analysis_make_selected)

        # Model combobox
        ttk.Label(control_frame, text="Model:").grid(row=0, column=2, padx=8, pady=8, sticky=tk.W)
        self.analysis_model_combo = ttk.Combobox(control_frame, textvariable=self.analysis_model_var,
                                                  width=18, state='readonly')
        self.analysis_model_combo.grid(row=0, column=3, padx=8, pady=8)

        # Criteria Selection (Age or Mileage)
        ttk.Label(control_frame, text="Group By:").grid(row=0, column=4, padx=8, pady=8, sticky=tk.W)
        criteria_options = ['age', 'mileage']
        criteria_combo = ttk.Combobox(control_frame, textvariable=self.analysis_criteria_var,
                                       values=criteria_options, width=12, state='readonly')
        criteria_combo.grid(row=0, column=5, padx=8, pady=8)

        # Generate Report Button
        report_button = ttk.Button(control_frame, text="📊  Generate Report",
                                    command=self.run_analysis_report, style='Accent.TButton')
        report_button.grid(row=0, column=6, padx=18, pady=8)

        # Graph Display Area
        self.graph_frame = ttk.Frame(self.analysis_tab)
        self.graph_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        self.canvas_widget = None


    def run_analysis_report(self):
        start_time = time.time()
        make = self.analysis_make_var.get().strip().upper()
        model = self.analysis_model_var.get().strip().upper()
        criteria = self.analysis_criteria_var.get()

        if not make or not model:
            messagebox.showwarning("Missing Input", "Please select both Vehicle Make and Model for analysis.")
            return

        self.status_label.config(text=f" 🔄 Generating pass rate report for {make} {model} by {criteria}...")
        self.master.update_idletasks()

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

            self.status_label.config(text=f" ✅ Report generated for {make} {model} in {elapsed_time:.3f}s")

        except Exception as e:
            messagebox.showerror("Analysis Error", f"Failed to generate report: {e}")
            self.status_label.config(text=" ❌ Analysis Failed.")
            fig, ax = plt.subplots(figsize=(10, 6))
            fig.patch.set_facecolor(COLORS['bg'])
            ax.set_facecolor(COLORS['bg'])
            ax.set_title("ERROR: Failed to Generate Plot", color=COLORS['red'])
            ax.text(0.5, 0.5, f"Error: {e}", ha='center', va='center', wrap=True, color=COLORS['text'])
            ax.axis('off')
            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            self.canvas_widget = canvas.get_tk_widget()
            self.canvas_widget.pack(fill=tk.BOTH, expand=True)
            canvas.draw()


# ====================================================================
# Main Execution
# ====================================================================
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide main window during potential pipeline init

    apply_dark_theme(root)

    # Check if database needs initialization
    if not is_database_ready():
        root.deiconify()  # Show root briefly so dialog has a parent
        dialog = PipelineInitDialog(root)
        dialog.run_pipeline()
        root.wait_window(dialog.dialog)

        if not dialog.success:
            messagebox.showerror("Initialization Failed",
                                 f"The data pipeline failed to complete:\n{dialog.error_msg}\n\nPlease fix the error and restart.")
            root.destroy()
            sys.exit(1)

    root.deiconify()
    app = MOT_Data_Browser_App(root)
    root.mainloop()