"""
Captures and crops the screen area showing the hole cards.
"""
# modules/screen_capture.py

import json
import pyautogui
from PIL import Image

class ScreenCapture:
    def __init__(self):
        self.config_path = "config/screen_regions.json"
        self.config = self.load_config()

    def load_config(self):
        """Load screen region configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Return default config if file doesn't exist
            return {
                "tables": {
                    "table1": {
                        "hole_cards": {
                            "x": 0,
                            "y": 0,
                            "width": 0,
                            "height": 0
                        },
                        "active": True
                    }
                }
            }

    def capture_hole_cards(self, table_id="table1"):
        """Capture screenshot of hole cards region"""
        try:
            table_config = self.config["tables"].get(table_id)
            if not table_config:
                raise ValueError(f"Table {table_id} not configured")

            region = table_config["hole_cards"]
            
            # Get screen dimensions
            screen_width, screen_height = pyautogui.size()
            
            # Validate coordinates are within screen bounds
            if (region["x"] < 0 or region["y"] < 0 or
                region["x"] + region["width"] > screen_width or
                region["y"] + region["height"] > screen_height):
                raise ValueError(
                    f"Capture region ({region['x']}, {region['y']}, "
                    f"{region['width']}, {region['height']}) "
                    f"is outside screen bounds ({screen_width}x{screen_height})"
                )
                
            screenshot = pyautogui.screenshot(region=(
                region["x"],
                region["y"],
                region["width"],
                region["height"]
            ))
            return screenshot
        except Exception as e:
            print(f"Error capturing hole cards: {e}")
            return None

# Create a singleton instance
screen_capture = ScreenCapture()

# Export the capture_hole_cards function at module level
def capture_hole_cards(table_id="table1"):
    return screen_capture.capture_hole_cards(table_id)
            
    def get_active_tables(self):
        """Return list of active table configurations"""
        return [table for table in self.config["tables"].items() 
                if table[1].get("active")]
                
    def capture_hole_cards(self, table_id="table1"):
        """Capture hole cards for specific table"""
        if table_id not in self.config["tables"]:
            raise ValueError(f"Table {table_id} not configured")
            
        region = self.config["tables"][table_id]["hole_cards"]
        return pyautogui.screenshot(region=(
            region["x"], 
            region["y"], 
            region["width"], 
            region["height"]
        ))
