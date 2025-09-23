#!/usr/bin/env python3
"""
Preflop Range Solver GUI
A desktop application for looking up preflop ranges from poker solutions.
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow

def main():
    """Main entry point for the application."""
    try:
        # Create the main window
        root = tk.Tk()
        app = MainWindow(root)
        
        # Start the application
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()