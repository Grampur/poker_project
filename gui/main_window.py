"""
Main window for the Preflop Range Solver GUI.
Simplified version focused on position-based preflop decisions.
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
        
        # Predefined positions and actions for preflop scenarios
        self.positions = ['UTG', 'MP', 'CO', 'BU', 'SB', 'BB']
        self.actions = ['Open Raise', 'Call', '3-Bet', '4-Bet', 'Fold']
        self.stack_sizes = ['9', '11', '14', '20', '25', '30', '50', '100']
        
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
        main_frame.rowconfigure(0, weight=1)
        
        # Control panel (left side)
        self.create_control_panel(main_frame)
        
        # Range display (right side)
        self.create_range_display(main_frame)
        
        # Status bar
        self.create_status_bar()
        
    def create_control_panel(self, parent):
        """Create the control panel with position and action selection."""
        control_frame = ttk.LabelFrame(parent, text="Preflop Range Lookup", padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), padx=(0, 10))
        control_frame.columnconfigure(0, weight=1)
        
        # Solutions folder selection
        ttk.Label(control_frame, text="Solutions Folder:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        folder_frame = ttk.Frame(control_frame)
        folder_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        folder_frame.columnconfigure(0, weight=1)
        
        self.folder_var = tk.StringVar(value="Settings/Solutions/3-max Tournament")
        folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_var, state="readonly")
        folder_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(folder_frame, text="Browse", command=self.browse_folder).grid(row=0, column=1)
        
        # Stack size selection
        ttk.Label(control_frame, text="Stack Size (BB):").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.stack_var = tk.StringVar()
        self.stack_combo = ttk.Combobox(control_frame, textvariable=self.stack_var, 
                                       values=self.stack_sizes, state="readonly", width=25)
        self.stack_combo.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        self.stack_combo.bind('<<ComboboxSelected>>', self.on_stack_change)
        
        # Position selection
        ttk.Label(control_frame, text="Your Position:").grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        self.position_var = tk.StringVar()
        self.position_combo = ttk.Combobox(control_frame, textvariable=self.position_var, 
                                          values=self.positions, state="readonly", width=25)
        self.position_combo.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        self.position_combo.bind('<<ComboboxSelected>>', self.on_position_change)
        
        # Facing action selection
        ttk.Label(control_frame, text="Facing Action:").grid(row=6, column=0, sticky=tk.W, pady=(0, 5))
        self.facing_var = tk.StringVar()
        self.facing_combo = ttk.Combobox(control_frame, textvariable=self.facing_var, 
                                        state="readonly", width=25)
        self.facing_combo.grid(row=7, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        self.facing_combo.bind('<<ComboboxSelected>>', self.on_facing_change)
        
        # Range type selection (what action you should take)
        ttk.Label(control_frame, text="Show Hands You Should:").grid(row=8, column=0, sticky=tk.W, pady=(0, 5))
        self.action_var = tk.StringVar(value="All")
        action_frame = ttk.Frame(control_frame)
        action_frame.grid(row=9, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Radiobutton(action_frame, text="All Actions", 
                       variable=self.action_var, value="All", 
                       command=self.update_range_display).grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(action_frame, text="Raise/3-Bet", 
                       variable=self.action_var, value="Raise", 
                       command=self.update_range_display).grid(row=1, column=0, sticky=tk.W)
        ttk.Radiobutton(action_frame, text="Call", 
                       variable=self.action_var, value="Call", 
                       command=self.update_range_display).grid(row=2, column=0, sticky=tk.W)
        ttk.Radiobutton(action_frame, text="Fold", 
                       variable=self.action_var, value="Fold", 
                       command=self.update_range_display).grid(row=3, column=0, sticky=tk.W)
        
        # Action buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=10, column=0, sticky=(tk.W, tk.E), pady=(15, 0))
        button_frame.columnconfigure(0, weight=1)
        
        ttk.Button(button_frame, text="Load Range", 
                  command=self.load_selected_range).grid(row=0, column=0, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(button_frame, text="Clear Display", 
                  command=self.clear_display).grid(row=1, column=0, pady=5, sticky=(tk.W, tk.E))
        
        # Range statistics
        stats_frame = ttk.LabelFrame(control_frame, text="Range Statistics", padding="10")
        stats_frame.grid(row=11, column=0, sticky=(tk.W, tk.E), pady=(15, 0))
        
        self.stats_text = tk.Text(stats_frame, height=8, width=30, state='disabled', 
                                 font=("Consolas", 9))
        self.stats_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Scrollbar for stats
        stats_scroll = ttk.Scrollbar(stats_frame, orient="vertical", command=self.stats_text.yview)
        stats_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.stats_text.configure(yscrollcommand=stats_scroll.set)
        
    def create_range_display(self, parent):
        """Create the range grid display."""
        display_frame = ttk.LabelFrame(parent, text="Preflop Range", padding="15")
        display_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        display_frame.columnconfigure(0, weight=1)
        display_frame.rowconfigure(0, weight=1)
        
        # Range grid container
        grid_container = ttk.Frame(display_frame)
        grid_container.grid(row=0, column=0, sticky=(tk.N))
        
        # Range grid
        self.range_grid = RangeGrid(grid_container)
        self.range_grid.grid.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Legend
        legend_frame = ttk.Frame(display_frame)
        legend_frame.grid(row=1, column=0, pady=(20, 0))
        
        ttk.Label(legend_frame, text="Legend:", font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=10, pady=(0, 5))
        
        # Color legend items
        colors = [
            ("Always (100%)", "#006400"),
            ("Often (75%+)", "#228B22"),
            ("Sometimes (50%+)", "#FFD700"),
            ("Rarely (25%+)", "#FFA500"),
            ("Very Rarely (<25%)", "#FFB6C1"),
            ("Never (0%)", "#FFFFFF")
        ]
        
        for i, (label, color) in enumerate(colors):
            legend_item = tk.Frame(legend_frame, bg=color, width=20, height=15, relief="solid", bd=1)
            legend_item.grid(row=1, column=i*2, padx=2, pady=2)
            legend_item.grid_propagate(False)
            ttk.Label(legend_frame, text=label, font=("Arial", 8)).grid(row=1, column=i*2+1, padx=(2, 10), pady=2)
        
    def create_status_bar(self):
        """Create status bar at bottom."""
        self.status_var = tk.StringVar(value="Ready - Select position and facing action to view ranges")
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
                
            # Load available data
            self.available_data = self.solution_loader.scan_solutions_folder(folder_path)
            
            # Update stack sizes dropdown with available stacks
            available_stacks = sorted(self.available_data.get('stacks', []))
            if available_stacks:
                self.stack_combo['values'] = available_stacks
                self.stack_combo.set(available_stacks[0])
                self.on_stack_change()
                
            self.status_var.set(f"Loaded solutions from {folder_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load solutions: {str(e)}")
            
    def on_stack_change(self, event=None):
        """Handle stack size selection change."""
        stack = self.stack_var.get()
        if stack and hasattr(self, 'available_data'):
            # Update available scenarios based on stack
            scenarios = self.available_data.get('stack_scenarios', {}).get(stack, [])
            # These should be position-based scenarios like "MP vs BB", "BU vs SB", etc.
            if scenarios:
                # Auto-select first position and update facing options
                if self.position_combo.get() == "":
                    self.position_combo.set(self.positions[0])
                self.update_facing_options()
                
    def on_position_change(self, event=None):
        """Handle position selection change."""
        self.update_facing_options()
        
    def update_facing_options(self):
        """Update facing action options based on position."""
        position = self.position_var.get()
        if not position:
            return
            