"""
Range grid widget for displaying poker hand ranges.
Creates a 13x13 grid representing all possible starting hands.
"""

import tkinter as tk
from tkinter import ttk
from utils.poker_utils import get_hand_matrix_position, frequency_to_color

class RangeGrid:
    def __init__(self, parent):
        self.parent = parent
        self.setup_grid()
        
    def setup_grid(self):
        """Create the 13x13 range grid."""
        self.grid = ttk.Frame(self.parent)
        
        # Hand labels (A, K, Q, J, T, 9, 8, 7, 6, 5, 4, 3, 2)
        self.ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
        
        # Create grid buttons
        self.buttons = {}
        for i in range(13):
            for j in range(13):
                hand_text = self.get_hand_text(i, j)
                
                button = tk.Button(
                    self.grid,
                    text=hand_text,
                    width=5,
                    height=2,
                    font=("Arial", 8, "bold"),
                    relief="raised",
                    bd=1,
                    bg="white",
                    command=lambda r=i, c=j: self.on_hand_click(r, c)
                )
                button.grid(row=i, column=j, padx=1, pady=1)
                self.buttons[(i, j)] = button
                
        # Add rank labels
        for i, rank in enumerate(self.ranks):
            # Top labels
            label_top = tk.Label(self.grid, text=rank, font=("Arial", 10, "bold"))
            label_top.grid(row=-1, column=i, pady=(0, 5))
            
            # Left labels  
            label_left = tk.Label(self.grid, text=rank, font=("Arial", 10, "bold"))
            label_left.grid(row=i, column=-1, padx=(0, 5))
            
    def get_hand_text(self, row, col):
        """Get the text representation for a hand at given grid position."""
        rank1 = self.ranks[row]
        rank2 = self.ranks[col]
        
        if row == col:
            # Pocket pair
            return f"{rank1}{rank2}"
        elif row < col:
            # Suited
            return f"{rank1}{rank2}s"
        else:
            # Offsuit
            return f"{rank2}{rank1}o"
            
    def update_range(self, range_data):
        """Update the grid with range data."""
        # Clear current colors
        self.clear()
        
        # Update each hand
        for hand_string, frequency in range_data.items():
            if '_' in hand_string:
                hand_part = hand_string.split('_')[0]
            else:
                hand_part = hand_string
                
            # Find grid position for this hand
            position = get_hand_matrix_position(hand_part)
            if position:
                row, col = position
                if (row, col) in self.buttons:
                    color = frequency_to_color(frequency)
                    self.buttons[(row, col)].config(
                        bg=color,
                        activebackground=color,
                        text=f"{self.get_hand_text(row, col)}\n{frequency:.0%}" if frequency > 0 else self.get_hand_text(row, col)
                    )
                    
    def clear(self):
        """Clear all colors from the grid."""
        for button in self.buttons.values():
            original_text = button.cget('text').split('\n')[0]  # Remove frequency if present
            button.config(
                bg="white",
                activebackground="white",
                text=original_text
            )
            
    def on_hand_click(self, row, col):
        """Handle hand button click."""
        hand_text = self.get_hand_text(row, col)
        print(f"Clicked: {hand_text}")  # For debugging