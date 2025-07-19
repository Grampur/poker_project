"""
Loads preflop ranges and returns the optimal action.
"""
import json

def get_action(hand, position):
    with open("gto_data/preflop_ranges.json") as f:
        ranges = json.load(f)
    return ranges.get(position, {}).get(hand, "Unknown")
