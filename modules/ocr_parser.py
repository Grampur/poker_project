# modules/ocr_parser.py

import cv2
import numpy as np
import pytesseract
import easyocr
from PIL import Image
import os

class CardOCR:
    def __init__(self):
        self.reader = easyocr.Reader(['en'])
        self.valid_values = {'2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'}
        self.valid_suits = {'h', 'd', 'c', 's', '♥', '♦', '♣', '♠'}
        self.suit_mapping = {
            '♥': 'h', '♦': 'd', '♣': 'c', '♠': 's',
            'H': 'h', 'D': 'd', 'C': 'c', 'S': 's'
        }
        
        # Create debug directory if it doesn't exist
        os.makedirs('debug_images', exist_ok=True)

    def normalize_card(self, text):
        """Normalize card text into standard format"""
        if not text:
            return None
            
        # Remove spaces and convert to uppercase
        text = text.replace(' ', '').upper().strip()
        
        if len(text) < 2:
            return None
            
        # Handle 10 specially
        if text.startswith('10'):
            value = '10'
            suit = text[2] if len(text) > 2 else None
        else:
            value = text[0]
            suit = text[1] if len(text) > 1 else None
            
        # Validate value and suit
        if value not in self.valid_values:
            return None
            
        if suit in self.suit_mapping:
            suit = self.suit_mapping[suit]
        elif suit and suit.lower() in self.valid_suits:
            suit = suit.lower()
        else:
            return None
            
        return value + suit

    def save_debug_image(self, image, name):
        """Save image for debugging"""
        if isinstance(image, np.ndarray):
            cv2.imwrite(f'debug_images/{name}.png', image)
        elif isinstance(image, Image.Image):
            image.save(f'debug_images/{name}.png')

    def preprocess_image(self, image):
        """Enhanced image preprocessing"""
        if isinstance(image, Image.Image):
            image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Save original capture
        self.save_debug_image(image, 'original_capture')
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply multiple preprocessing techniques
        # 1. Increase contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        gray = clahe.apply(gray)
        
        # 2. Denoise
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # 3. Threshold
        _, thresh = cv2.threshold(denoised, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 4. Scale up
        scaled = cv2.resize(thresh, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        
        # Save preprocessed image
        self.save_debug_image(scaled, 'preprocessed')
        
        return scaled

    def split_image(self, image):
        """Split image into left and right card regions with overlap"""
        width = image.shape[1]
        height = image.shape[0]
        
        # Calculate split points with 10% overlap
        overlap = int(width * 0.1)
        mid_point = width // 2
        
        left_card = image[:, :mid_point+overlap]
        right_card = image[:, mid_point-overlap:]
        
        # Save split images
        self.save_debug_image(left_card, 'left_card')
        self.save_debug_image(right_card, 'right_card')
        
        return left_card, right_card

    def detect_single_card(self, image, position="unknown"):
        """Enhanced single card detection"""
        # Try multiple OCR approaches
        
        # 1. Try pytesseract with different PSM modes
        psm_modes = [6, 7, 8, 13]
        for psm in psm_modes:
            text = pytesseract.image_to_string(
                image,
                config=f'--psm {psm} --oem 3 -c tessedit_char_whitelist=0123456789AKQJTHSDC♥♦♣♠'
            ).strip()
            card = self.normalize_card(text)
            if card:
                print(f"Pytesseract detected ({position}): {text} -> {card}")
                return card

        # 2. Try EasyOCR
        try:
            results = self.reader.readtext(image)
            for _, text, conf in results:
                card = self.normalize_card(text)
                if card:
                    print(f"EasyOCR detected ({position}): {text} -> {card}")
                    return card
        except Exception as e:
            print(f"EasyOCR error: {e}")

        print(f"No card detected for {position} position")
        return None

    def parse_hand(self, image):
        """Parse hole cards from screenshot"""
        try:
            # Print image dimensions and basic info
            if isinstance(image, Image.Image):
                print(f"Original image size: {image.size}")
                print(f"Image mode: {image.mode}")
            elif isinstance(image, np.ndarray):
                print(f"Original image shape: {image.shape}")
                print(f"Image dtype: {image.dtype}")
                
            # Preprocess and get dimensions at each step
            processed_img = self.preprocess_image(image)
            print(f"Processed image shape: {processed_img.shape}")
            
            left_card_img, right_card_img = self.split_image(processed_img)
            print(f"Left card shape: {left_card_img.shape}")
            print(f"Right card shape: {right_card_img.shape}")
                        
            # Validate we have both cards
            if left_card_img and right_card_img and left_card_img != right_card_img:
                cards = (left_card_img, right_card_img)
                print(f"Successfully detected cards: {cards}")
                return cards
            else:
                print("Failed to detect valid cards or cards are identical")
                print(f"Left card: {left_card_img}, Right card: {right_card_img}")
                return None
                
        except Exception as e:
            print(f"Error parsing hand: {e}")
            import traceback
            traceback.print_exc()
            return None

# Create a singleton instance
card_ocr = CardOCR()

# Export the parse_hand function at module level
def parse_hand(image):
    return card_ocr.parse_hand(image)