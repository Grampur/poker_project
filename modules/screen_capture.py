"""
Captures and crops the screen area showing the hole cards.
"""
import pyautogui
from PIL import Image
import json

def capture_hole_cards():
    with open("config/screen_regions.json") as f:
        region = json.load(f)["hole_cards"]
    x, y, w, h = region["x"], region["y"], region["width"], region["height"]
    return pyautogui.screenshot(region=(x, y, w, h))
