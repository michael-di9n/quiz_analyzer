import cv2
import numpy as np
import pytesseract
from PIL import Image

class TextExtractor:
    """Class for extracting text from images using OCR"""
    
    def __init__(self, tesseract_path=None):
        """
        Initialize the TextExtractor
        
        Args:
            tesseract_path (str, optional): Path to tesseract executable
                                           (needed on Windows)
        """
        # Set tesseract path if provided (required on Windows)
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
    
    def preprocess_image(self, image):
        """
        Preprocess the image to improve OCR accuracy
        
        Args:
            image (numpy.ndarray): The image to preprocess
            
        Returns:
            numpy.ndarray: The preprocessed image
        """
        # Convert to grayscale if it's a color image
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
            
        # Apply thresholding to get a binary image
        _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Invert the image (black text on white background is better for OCR)
        binary = 255 - binary
        
        return binary
    
    def extract_text(self, image):
        """
        Extract text from an image
        
        Args:
            image (numpy.ndarray or PIL.Image): The image to extract text from
            
        Returns:
            str: The extracted text
        """
        # Convert PIL Image to numpy array if needed
        if isinstance(image, Image.Image):
            image = np.array(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        # Preprocess the image
        preprocessed = self.preprocess_image(image)
        
        # Extract text using pytesseract
        text = pytesseract.image_to_string(preprocessed)
        
        return text
    
    def is_multiple_choice(self, text):
        """
        Determine if the extracted text is a multiple choice question
        
        Args:
            text (str): The extracted text
            
        Returns:
            bool: True if the text appears to be a multiple choice question
        """
        # Common multiple choice patterns
        mc_patterns = [
            'A)', 'B)', 'C)', 'D)',
            'a)', 'b)', 'c)', 'd)',
            'A.', 'B.', 'C.', 'D.',
            'a.', 'b.', 'c.', 'd.',
            '(A)', '(B)', '(C)', '(D)',
            '(a)', '(b)', '(c)', '(d)'
        ]
        
        # Count how many patterns are found in the text
        pattern_count = sum(1 for pattern in mc_patterns if pattern in text)
        
        # If we find at least 3 patterns, it's likely a multiple choice question
        return pattern_count >= 3
    
    def parse_question(self, text):
        """
        Parse the text to separate the question from the answer choices
        
        Args:
            text (str): The extracted text
            
        Returns:
            tuple: (question_text, list_of_choices)
        """
        # This is a simple implementation - for complex layouts,
        # more sophisticated parsing would be needed
        
        lines = text.split('\n')
        question_lines = []
        choices = []
        
        # Simple heuristic: Lines starting with A), B), etc. are choices
        choice_started = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this line starts a choice
            if any(line.startswith(pattern) for pattern in ['A)', 'B)', 'C)', 'D)', 'a)', 'b)', 'c)', 'd)',
                                                           'A.', 'B.', 'C.', 'D.', 'a.', 'b.', 'c.', 'd.',
                                                           '(A)', '(B)', '(C)', '(D)', '(a)', '(b)', '(c)', '(d)']):
                choice_started = True
                choices.append(line)
            elif choice_started:
                # If we've started seeing choices and this isn't a choice,
                # it might be a continuation of the previous choice
                if choices:
                    choices[-1] += ' ' + line
                else:
                    question_lines.append(line)
            else:
                question_lines.append(line)
        
        question_text = '\n'.join(question_lines)
        
        return question_text, choices