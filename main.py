"""
Entry point for the GTO Assistant.
- Captures screen
- Parses hand and position
- Looks up GTO action
- Displays UI
"""
import json
from modules.screen_capture import capture_hole_cards
from modules.ocr_parser import parse_hand
from modules import gto_lookup, ui_overlay
from modules.calibration import RegionCalibrator

def run():
    try:
        # Capture the screen region
        hand_image = capture_hole_cards()
        if hand_image:
            # Try to parse the cards
            cards = parse_hand(hand_image)
            if cards and len(cards) == 2:
                print(f"Detected cards: {cards}")
                position = "BTN"  # Manual toggle for MVP
                try:
                    action = gto_lookup.get_action(cards, position)
                    ui_overlay.show(action)
                except Exception as e:
                    print(f"Error looking up GTO action: {e}")
            else:
                print("Failed to detect exactly two cards. Please check the image quality.")
        else:
            print("Failed to capture hole cards. Please check configuration.")
    except Exception as e:
        print(f"Error during execution: {e}")

def setup_regions():
    print("=== GTO Assistant Region Calibration ===")
    print("We'll help you set up the regions for capturing hole cards.")
    print("Please open your ClubGG table and position it where you'll be playing.")
    
    input("Press Enter when you're ready to start calibration...")
    
    calibrator = RegionCalibrator()
    calibrator.start_calibration_window()
    
    try:
        with open("config/screen_regions.json") as f:
            config = json.load(f)
            hole_cards_config = config["tables"]["table1"]["hole_cards"]
            
            if calibrator.validate_region(hole_cards_config):
                if calibrator.test_capture(hole_cards_config):
                    print("Configuration completed successfully!")
                    return True
                else:
                    print("Error: Failed to capture screenshot of selected region.")
                    return False
            else:
                print("Error: Selected region is too small. Please try again.")
                return False
    except Exception as e:
        print(f"Error with configuration file: {e}")
        return False

if __name__ == "__main__":
    print("Starting GTO Assistant Setup...")
    if setup_regions():  # Run setup first
        print("Setup successful! Now running main program...")
        run()
    else:
        print("Setup failed. Please try running the program again.")