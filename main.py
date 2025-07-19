"""
Entry point for the GTO Assistant.
- Captures screen
- Parses hand and position
- Looks up GTO action
- Displays UI
"""
from modules import screen_capture, ocr_parser, gto_lookup, ui_overlay

def run():
    # Placeholder logic
    hand_image = screen_capture.capture_hole_cards()
    hand = ocr_parser.parse_hand(hand_image)
    position = "BTN"  # Manual toggle for MVP
    action = gto_lookup.get_action(hand, position)
    ui_overlay.show(action)

if __name__ == "__main__":
    run()
