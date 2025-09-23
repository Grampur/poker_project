"""
Main window for the Preflop Range Solver GUI.
Contains the control panel and range display.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from .range_grid import RangeGrid
from data.solution_loader import SolutionLoader
from data.range_parser import RangeParser

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Preflop Range Solver")
        self.root.geometry("1200x800")
        
        # Initialize data components
        self.solution_loader = SolutionLoader()
        self.range_parser = RangeParser()
        
        # Current solution data
        self.current_solution = None
        
        self.setup_ui()
        self.load_available_solutions()
        
    def setup_ui(self):
        """Set up the user interface."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Control panel (left side)
        self.create_control_panel(main_frame)
        
        # Range display (right side)
        self.create_range_display(main_frame)
        
        # Status bar
        self.create_status_bar()
        
    def create_control_panel(self, parent):
        """Create the control panel with dropdowns and options."""
        control_frame = ttk.LabelFrame(parent, text="Range Lookup", padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), padx=(0, 10))
        
        # Solutions folder selection
        ttk.Label(control_frame, text="Solutions Folder:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        folder_frame = ttk.Frame(control_frame)
        folder_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        folder_frame.columnconfigure(0, weight=1)
        
        self.folder_var = tk.StringVar(value="Settings/Solutions/3-max Tournament")
        folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_var, state="readonly")
        folder_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(folder_frame, text="Browse", command=self.browse_folder).grid(row=0, column=1)
        
        # Stack size selection
        ttk.Label(control_frame, text="Stack Size (BB):").grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        self.stack_var = tk.StringVar()
        self.stack_combo = ttk.Combobox(control_frame, textvariable=self.stack_var, state="readonly", width=20)
        self.stack_combo.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.stack_combo.bind('<<ComboboxSelected>>', self.on_stack_change)
        
        # Scenario selection
        ttk.Label(control_frame, text="Preflop Scenario:").grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        self.scenario_var = tk.StringVar()
        self.scenario_combo = ttk.Combobox(control_frame, textvariable=self.scenario_var, state="readonly", width=30)
        self.scenario_combo.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.scenario_combo.bind('<<ComboboxSelected>>', self.on_scenario_change)
        
        # Board selection
        ttk.Label(control_frame, text="Board:").grid(row=6, column=0, sticky=tk.W, pady=(0, 5))
        self.board_var = tk.StringVar()
        self.board_combo = ttk.Combobox(control_frame, textvariable=self.board_var, state="readonly", width=20)
        self.board_combo.grid(row=7, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.board_combo.bind('<<ComboboxSelected>>', self.on_board_change)
        
        # Position selection
        ttk.Label(control_frame, text="View Range For:").grid(row=8, column=0, sticky=tk.W, pady=(0, 5))
        self.position_var = tk.StringVar(value="OOP")
        position_frame = ttk.Frame(control_frame)
        position_frame.grid(row=9, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Radiobutton(position_frame, text="OOP (Out of Position)", 
                       variable=self.position_var, value="OOP", 
                       command=self.update_range_display).grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(position_frame, text="IP (In Position)", 
                       variable=self.position_var, value="IP", 
                       command=self.update_range_display).grid(row=1, column=0, sticky=tk.W)
        
        # Action buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=10, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(button_frame, text="Load Range", 
                  command=self.load_selected_range).grid(row=0, column=0, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(button_frame, text="Clear Display", 
                  command=self.clear_display).grid(row=1, column=0, pady=5, sticky=(tk.W, tk.E))
        
        # Range statistics
        stats_frame = ttk.LabelFrame(control_frame, text="Range Statistics", padding="10")
        stats_frame.grid(row=11, column=0, sticky=(tk.W, tk.E), pady=(15, 0))
        
        self.stats_text = tk.Text(stats_frame, height=6, width=30, state='disabled')
        self.stats_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Scrollbar for stats
        stats_scroll = ttk.Scrollbar(stats_frame, orient="vertical", command=self.stats_text.yview)
        stats_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.stats_text.configure(yscrollcommand=stats_scroll.set)
        
    def create_range_display(self, parent):
        """Create the range grid display."""
        display_frame = ttk.LabelFrame(parent, text="Preflop Range", padding="10")
        display_frame.grid(row=0, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Range grid
        self.range_grid = RangeGrid(display_frame)
        self.range_grid.grid.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Legend
        legend_frame = ttk.Frame(display_frame)
        legend_frame.grid(row=1, column=0, pady=(10, 0))
        
        ttk.Label(legend_frame, text="Legend:").grid(row=0, column=0, padx=(0, 10))
        
        # Color legend items
        colors = [
            ("Always (100%)", "#006400"),
            ("Often (75%+)", "#228B22"),
            ("Sometimes (50%+)", "#FFD700"),
            ("Rarely (25%+)", "#FFA500"),
            ("Never (0%)", "#FFFFFF")
        ]
        
        for i, (label, color) in enumerate(colors):
            legend_item = tk.Frame(legend_frame, bg=color, width=20, height=15, relief="solid", bd=1)
            legend_item.grid(row=0, column=i*2+1, padx=2)
            legend_item.grid_propagate(False)
            ttk.Label(legend_frame, text=label, font=("Arial", 8)).grid(row=0, column=i*2+2, padx=(0, 10))
        
    def create_status_bar(self):
        """Create status bar at bottom."""
        self.status_var = tk.StringVar(value="Ready - Select a solution to view preflop ranges")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w")
        status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
    def browse_folder(self):
        """Browse for solutions folder."""
        folder = filedialog.askdirectory(title="Select Solutions Folder")
        if folder:
            self.folder_var.set(folder)
            self.load_available_solutions()
            
    def load_available_solutions(self):
        """Load available solutions from the selected folder."""
        try:
            folder_path = self.folder_var.get()
            if not os.path.exists(folder_path):
                self.status_var.set("Error: Solutions folder not found")
                return
                
            # Load available stack sizes, scenarios, and boards
            self.available_data = self.solution_loader.scan_solutions_folder(folder_path)
            
            # Update dropdowns
            self.stack_combo['values'] = sorted(self.available_data.get('stacks', []))
            self.scenario_combo['values'] = list(self.available_data.get('scenarios', []))
            
            if self.stack_combo['values']:
                self.stack_combo.set(self.stack_combo['values'][0])
                self.on_stack_change()
                
            self.status_var.set(f"Loaded solutions from {folder_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load solutions: {str(e)}")
            
    def on_stack_change(self, event=None):
        """Handle stack size selection change."""
        stack = self.stack_var.get()
        if stack and hasattr(self, 'available_data'):
            scenarios = self.available_data.get('stack_scenarios', {}).get(stack, [])
            self.scenario_combo['values'] = scenarios
            if scenarios:
                self.scenario_combo.set(scenarios[0])
                self.on_scenario_change()
                
    def on_scenario_change(self, event=None):
        """Handle scenario selection change."""
        stack = self.stack_var.get()
        scenario = self.scenario_var.get()
        
        if stack and scenario and hasattr(self, 'available_data'):
            key = f"{stack}_{scenario}"
            boards = self.available_data.get('scenario_boards', {}).get(key, [])
            self.board_combo['values'] = boards
            if boards:
                self.board_combo.set(boards[0])
                self.on_board_change()
                
    def on_board_change(self, event=None):
        """Handle board selection change."""
        # Auto-load when board changes
        self.load_selected_range()
        
    def load_selected_range(self):
        """Load and display the selected range."""
        try:
            folder_path = self.folder_var.get()
            stack = self.stack_var.get()
            scenario = self.scenario_var.get()
            board = self.board_var.get()
            
            if not all([folder_path, stack, scenario, board]):
                messagebox.showwarning("Warning", "Please select all options first")
                return
                
            # Construct file path
            solution_file = os.path.join(folder_path, stack, scenario, f"{board}.txt")
            
            if not os.path.exists(solution_file):
                messagebox.showerror("Error", f"Solution file not found: {solution_file}")
                return
                
            # Load solution
            self.current_solution = self.solution_loader.load_solution(solution_file)
            
            # Update display
            self.update_range_display()
            self.update_statistics()
            
            self.status_var.set(f"Loaded: {stack}bb {scenario} on {board}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load range: {str(e)}")
            
    def update_range_display(self):
        """Update the range grid display."""
        if not self.current_solution:
            return
            
        position = self.position_var.get()
        range_data = self.current_solution.get(f'{position.lower()}_range', {})
        
        if range_data:
            self.range_grid.update_range(range_data)
        else:
            self.range_grid.clear()
            
    def update_statistics(self):
        """Update range statistics display."""
        if not self.current_solution:
            return
            
        position = self.position_var.get()
        range_data = self.current_solution.get(f'{position.lower()}_range', {})
        
        stats = self.range_parser.calculate_range_statistics(range_data)
        
        self.stats_text.config(state='normal')
        self.stats_text.delete(1.0, tk.END)
        
        stats_text = f"""Total Combos: {stats['total_combos']}
Played Combos: {stats['played_combos']}
VPIP: {stats['vpip']:.1f}%

Hand Categories:
Pairs: {stats['pairs']:.1f}%
Suited: {stats['suited']:.1f}%
Offsuit: {stats['offsuit']:.1f}%

Strength Distribution:
Premium: {stats['premium']:.1f}%
Strong: {stats['strong']:.1f}%
Marginal: {stats['marginal']:.1f}%"""
        
        self.stats_text.insert(1.0, stats_text)
        self.stats_text.config(state='disabled')
        
    def clear_display(self):
        """Clear the range display."""
        self.range_grid.clear()
        self.current_solution = None
        
        self.stats_text.config(state='normal')
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.config(state='disabled')
        
        self.status_var.set("Display cleared")