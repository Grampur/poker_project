"""
Uses OCR to extract the player's hole cards.
"""
import pytesseract

def parse_hand(image):
    raw = pytesseract.image_to_string(image)
    return raw.strip().replace(" ", "").upper()
