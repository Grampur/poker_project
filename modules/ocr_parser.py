import cv2
import numpy as np
import os
from PIL import Image

class CardTemplateDetector:
    def __init__(self):
        self.values = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
        self.suits = ['s', 'h', 'd', 'c']
        self.value_templates = {}
        self.suit_templates = {}
        self._load_templates()

    def _load_templates(self):
        print("Loading templates...")
        # Load and process value templates
        for value in self.values:
            template_path = f"card_templates/values/{value}.png"
            print(f"Checking for value template: {template_path}")
            if os.path.exists(template_path):
                # Load and convert to grayscale
                template = cv2.imread(template_path)
                if template is not None:
                    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
                    # Apply threshold to make it black and white
                    _, template = cv2.threshold(template, 127, 255, cv2.THRESH_BINARY)
                    # Resize template to be smaller (adjust size as needed)
                    target_height = 20  # Reduced from 30 to 20
                    aspect_ratio = template.shape[1] / template.shape[0]
                    target_width = int(target_height * aspect_ratio)
                    template = cv2.resize(template, (target_width, target_height))
                    self.value_templates[value] = template
                    print(f"Loaded value template: {value}")
        
        # Load and process suit templates
        for suit in self.suits:
            template_path = f"card_templates/suits/{suit}.png"
            print(f"Checking for suit template: {template_path}")
            if os.path.exists(template_path):
                # Load and convert to grayscale
                template = cv2.imread(template_path)
                if template is not None:
                    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
                    # Apply threshold to make it black and white
                    _, template = cv2.threshold(template, 127, 255, cv2.THRESH_BINARY)
                    # Resize template to be smaller
                    target_height = 20  # Reduced from 30 to 20
                    aspect_ratio = template.shape[1] / template.shape[0]
                    target_width = int(target_height * aspect_ratio)
                    template = cv2.resize(template, (target_width, target_height))
                    self.suit_templates[suit] = template
                    print(f"Loaded suit template: {suit}")
        
        print(f"Loaded {len(self.value_templates)} value templates and {len(self.suit_templates)} suit templates")
        
        # Print template sizes for debugging
        print("\nTemplate sizes:")
        for value, template in self.value_templates.items():
            print(f"Value {value} template size: {template.shape}")
        for suit, template in self.suit_templates.items():
            print(f"Suit {suit} template size: {template.shape}")

    def detect_card(self, card_img):
        print(f"Input card image size: {card_img.shape}")
        
        # Convert to grayscale if needed
        if len(card_img.shape) == 3:
            card_img = cv2.cvtColor(card_img, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold to make it black and white
        _, card_img = cv2.threshold(card_img, 127, 255, cv2.THRESH_BINARY)
        
        # Save processed card image for debugging
        cv2.imwrite('debug_images/processed_card.png', card_img)
        
        best_value_match = None
        best_value_score = -1
        best_suit_match = None
        best_suit_score = -1
        
        # Detect value
        for value, template in self.value_templates.items():
            result = cv2.matchTemplate(card_img, template, cv2.TM_CCOEFF_NORMED)
            score = np.max(result)
            print(f"Value {value} score: {score:.3f}")
            
            if score > best_value_score:
                best_value_score = score
                best_value_match = value
                
                # Debug visualization for good matches
                if score > 0.4:
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                    top_left = max_loc
                    h, w = template.shape
                    bottom_right = (top_left[0] + w, top_left[1] + h)
                    debug_img = cv2.cvtColor(card_img.copy(), cv2.COLOR_GRAY2BGR)
                    cv2.rectangle(debug_img, top_left, bottom_right, (0, 255, 0), 2)
                    cv2.putText(debug_img, f"{value}: {score:.3f}", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.imwrite(f'debug_images/match_value_{value}.png', debug_img)
        
        # Detect suit
        for suit, template in self.suit_templates.items():
            result = cv2.matchTemplate(card_img, template, cv2.TM_CCOEFF_NORMED)
            score = np.max(result)
            print(f"Suit {suit} score: {score:.3f}")
            
            if score > best_suit_score:
                best_suit_score = score
                best_suit_match = suit
                
                # Debug visualization for good matches
                if score > 0.4:
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                    top_left = max_loc
                    h, w = template.shape
                    bottom_right = (top_left[0] + w, top_left[1] + h)
                    debug_img = cv2.cvtColor(card_img.copy(), cv2.COLOR_GRAY2BGR)
                    cv2.rectangle(debug_img, top_left, bottom_right, (0, 255, 0), 2)
                    cv2.putText(debug_img, f"{suit}: {score:.3f}", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.imwrite(f'debug_images/match_suit_{suit}.png', debug_img)
        
        print(f"Best value match: {best_value_match} (score: {best_value_score:.3f})")
        print(f"Best suit match: {best_suit_match} (score: {best_suit_score:.3f})")
        
        # Lower threshold to 0.4 for testing
        if best_value_score < 0.4 or best_suit_score < 0.4:
            return None
            
        return (best_value_match, best_suit_match)

class CardOCR:
    def __init__(self):
        self.detector = CardTemplateDetector()

    def preprocess_image(self, image):
        # Convert PIL Image to numpy array if needed
        if isinstance(image, Image.Image):
            image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Save original for debugging
        cv2.imwrite('debug_images/original_capture.png', image)
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Increase contrast
        gray = cv2.convertScaleAbs(gray, alpha=1.5, beta=0)
        
        # Apply adaptive histogram equalization
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4,4))
        enhanced = clahe.apply(gray)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(enhanced)
        
        # Sharpen
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(denoised, -1, kernel)
        
        # Save intermediate results
        cv2.imwrite('debug_images/gray.png', gray)
        cv2.imwrite('debug_images/enhanced.png', enhanced)
        cv2.imwrite('debug_images/sharpened.png', sharpened)
        
        return sharpened

    def split_image(self, image):
        """Split image into left and right card regions with minimal overlap"""
        width = image.shape[1]
        height = image.shape[0]
        
        # Calculate split points
        mid_point = width // 2
        
        # Adjust the split regions to be wider
        # For left card: take from start to 65% of width
        left_end = int(width * 0.65)
        # For right card: start from 35% of width to end
        right_start = int(width * 0.35)
        
        left_card = image[:, :left_end]
        right_card = image[:, right_start:]
        
        # Add debug visualization
        left_debug = left_card.copy()
        right_debug = right_card.copy()
        cv2.rectangle(left_debug, (0,0), (left_debug.shape[1]-1, left_debug.shape[0]-1), (255,255,255), 1)
        cv2.rectangle(right_debug, (0,0), (right_debug.shape[1]-1, right_debug.shape[0]-1), (255,255,255), 1)
        
        # Save debug images
        cv2.imwrite('debug_images/left_card.png', left_debug)
        cv2.imwrite('debug_images/right_card.png', right_debug)
        
        print(f"Split regions - Left card width: {left_card.shape[1]}, Right card width: {right_card.shape[1]}")
        
        return left_card, right_card

    def parse_hand(self, image):
        """Parse an image containing two cards and return their values"""
        try:
            # Print input image details
            print(f"Original image size: {image.size}")
            print(f"Image mode: {image.mode}")
            
            # Preprocess the image
            processed_img = self.preprocess_image(image)
            print(f"Processed image shape: {processed_img.shape}")
            
            # Split into left and right cards
            left_card, right_card = self.split_image(processed_img)
            print(f"Left card shape: {left_card.shape}")
            print(f"Right card shape: {right_card.shape}")
            
            # Detect cards
            left_detection = self.detector.detect_card(left_card)
            right_detection = self.detector.detect_card(right_card)
            
            print(f"Left card detection: {left_detection}")
            print(f"Right card detection: {right_detection}")
            
            # Check if we got valid detections
            if left_detection is None or right_detection is None:
                print("Failed to detect valid cards")
                return None
            
            # Return the detected cards
            return [left_detection, right_detection]
            
        except Exception as e:
            print(f"Error parsing hand: {str(e)}")
            return None

# Create a global instance of CardOCR
_card_ocr = None

def get_card_ocr():
    """Get or create the global CardOCR instance"""
    global _card_ocr
    if _card_ocr is None:
        _card_ocr = CardOCR()
    return _card_ocr

def parse_hand(image):
    """Module-level function to parse cards from an image"""
    ocr = get_card_ocr()
    return ocr.parse_hand(image)

def convert_templates_to_grayscale():
    """Utility function to convert all templates to grayscale"""
    template_dirs = ['card_templates/values/', 'card_templates/suits/']
    for dir_path in template_dirs:
        for filename in os.listdir(dir_path):
            if filename.endswith('.png'):
                filepath = os.path.join(dir_path, filename)
                # Read image
                img = cv2.imread(filepath)
                if img is not None:
                    # Convert to grayscale
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    # Threshold to make it black and white
                    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
                    # Save back
                    cv2.imwrite(filepath, thresh)
                    print(f"Converted {filepath} to grayscale")

if __name__ == "__main__":
    convert_templates_to_grayscale()