"""
Range grid widget for displaying poker hand ranges.
Creates a 13x13 grid representing all possible starting hands.
"""

import tkinter as tk
from tkinter import ttk
from data.range_parser import RangeParser

class RangeGrid:
    def __init__(self, parent):
        self.parent = parent
        self.range_parser = RangeParser()  # Use RangeParser for utility methods
        self.setup_grid()
        
    def setup_grid(self):
        """Create the 13x13 range grid."""
        # Create a container frame for the entire grid including labels
        self.grid_container = ttk.Frame(self.parent)
        self.grid = ttk.Frame(self.grid_container)
        
        # Hand labels (A, K, Q, J, T, 9, 8, 7, 6, 5, 4, 3, 2)
        self.ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
        
        # Add top rank labels (column headers)
        for i, rank in enumerate(self.ranks):
            label_top = tk.Label(self.grid_container, text=rank, font=("Arial", 10, "bold"))
            label_top.grid(row=0, column=i+1, pady=(0, 5))
            
        # Add left rank labels (row headers) and create grid buttons
        self.buttons = {}
        for i in range(13):
            # Left label for this row
            label_left = tk.Label(self.grid_container, text=self.ranks[i], font=("Arial", 10, "bold"))
            label_left.grid(row=i+1, column=0, padx=(0, 5))
            
            # Create buttons for this row
            for j in range(13):
                hand_text = self.get_hand_text(i, j)
                
                button = tk.Button(
                    self.grid_container,
                    text=hand_text,
                    width=5,
                    height=2,
                    font=("Arial", 8, "bold"),
                    relief="raised",
                    bd=1,
                    bg="white",
                    command=lambda r=i, c=j: self.on_hand_click(r, c)
                )
                button.grid(row=i+1, column=j+1, padx=1, pady=1)
                self.buttons[(i, j)] = button
        
        # Set the grid container as the main grid attribute for external access
        self.grid = self.grid_container
            
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
        
        # Store current range data for reference
        self.current_range_data = range_data
        
        # Update each hand
        for hand_string, frequency in range_data.items():
            if '_' in hand_string:
                hand_part = hand_string.split('_')[0]
            else:
                hand_part = hand_string
                
            # Convert specific hand to generic format if needed
            if len(hand_part) == 4:
                generic_hand = self.range_parser.convert_to_generic_hand(hand_part)
            else:
                generic_hand = hand_part
                
            # Find grid position for this hand using RangeParser method
            position = self.range_parser.get_hand_matrix_position(generic_hand)
            if position:
                row, col = position
                if (row, col) in self.buttons:
                    color = self.range_parser.frequency_to_color(frequency)
                    display_text = self.get_hand_text(row, col)
                    
                    # Add frequency percentage if > 0
                    if frequency > 0:
                        display_text += f"\n{frequency:.0%}"
                    
                    self.buttons[(row, col)].config(
                        bg=color,
                        activebackground=color,
                        text=display_text
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
        
        # Optional: Show hand details in a tooltip or status update
        if hasattr(self, 'current_range_data') and self.current_range_data:
            # Try to find this hand in current range data
            for hand_string, frequency in self.current_range_data.items():
                generic_hand = hand_string.split('_')[0] if '_' in hand_string else hand_string
                if len(generic_hand) == 4:
                    generic_hand = self.range_parser.convert_to_generic_hand(generic_hand)
                
                if generic_hand == hand_text:
                    print(f"Hand {hand_text}: {frequency:.1%} frequency")
                    break
            else:
                print(f"Hand {hand_text}: Not in current range (0% frequency)")