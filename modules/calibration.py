# modules/calibration.py

import json
import tkinter as tk
import pyautogui

class RegionCalibrator:
    def __init__(self):
        self.config_path = "config/screen_regions.json"
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.current_rectangle = None
        self.dimension_label = None
        
    def start_calibration_window(self):
        """Creates a transparent overlay window for region selection"""
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True, '-alpha', 0.3)
        self.root.title("GTO Assistant - Region Calibration")
        
        # Create canvas for drawing selection rectangle
        self.canvas = tk.Canvas(self.root, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Create label for showing dimensions
        self.dimension_label = tk.Label(
            self.root, 
            text="", 
            bg='white',
            font=('Arial', 12)
        )
        self.dimension_label.place(relx=0.5, rely=0.05, anchor='center')
        
        # Instructions label
        instructions = """
        Click and drag to select the hole cards region.
        Selection must be at least 50x20 pixels.
        Current size will be shown while dragging.
        Press ESC to cancel.
        Press ENTER when selection is correct (green).
        """
        label = tk.Label(self.root, text=instructions, bg='white')
        label.place(relx=0.5, rely=0.1, anchor='center')
        
        # Bind mouse events
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        
        self.root.bind('<Escape>', lambda e: self.root.destroy())
        self.root.bind('<Return>', self.save_region)
        
        self.root.mainloop()

    def on_mouse_down(self, event):
        """Handle mouse button press"""
        self.start_x = event.x
        self.start_y = event.y
        
    def on_mouse_drag(self, event):
        """Handle mouse drag to draw selection rectangle"""
        if self.current_rectangle:
            self.canvas.delete(self.current_rectangle)
            
        width = abs(event.x - self.start_x)
        height = abs(event.y - self.start_y)
        
        # Update dimension label
        self.dimension_label.config(
            text=f"Selection size: {width}x{height} pixels"
            + (" (Valid)" if width >= 50 and height >= 20 else " (Too small)")
        )
        
        # Color the rectangle based on validity
        color = 'green' if width >= 50 and height >= 20 else 'red'
        
        self.current_rectangle = self.canvas.create_rectangle(
            self.start_x, self.start_y,
            event.x, event.y,
            outline=color,
            width=2
        )

    def on_mouse_up(self, event):
        """Handle mouse button release"""
        self.end_x = event.x
        self.end_y = event.y

    def save_region(self, event=None):
        """Save the selected region to config file"""
        if not all([self.start_x, self.start_y, self.end_x, self.end_y]):
            return
            
        # Calculate region dimensions
        x = min(self.start_x, self.end_x)
        y = min(self.start_y, self.end_y)
        width = abs(self.end_x - self.start_x)
        height = abs(self.end_y - self.start_y)
        
        # Save to config with correct structure
        config = {
            "tables": {
                "table1": {
                    "hole_cards": {
                        "x": x,
                        "y": y,
                        "width": width,
                        "height": height
                    },
                    "active": True
                }
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
            
        self.root.destroy()

    def validate_region(self, region):
        """Validate the selected region dimensions"""
        try:
            min_width = 50  # minimum width for hole cards
            min_height = 20
            return (region["width"] >= min_width and 
                    region["height"] >= min_height)
        except KeyError:
            return False

    def test_capture(self, region):
        """Test screenshot of selected region"""
        try:
            screenshot = pyautogui.screenshot(region=(
                region["x"],
                region["y"],
                region["width"],
                region["height"]
            ))
            return True
        except Exception as e:
            print(f"Error capturing region: {e}")
            return False