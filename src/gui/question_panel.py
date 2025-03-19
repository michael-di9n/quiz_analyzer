from PyQt6.QtWidgets import (QGroupBox, QVBoxLayout, QHBoxLayout, 
                           QLabel, QTextEdit, QRadioButton, QButtonGroup,
                           QMessageBox)
from PyQt6.QtCore import pyqtSignal
from ocr.text_extractor import TextExtractor
import os

class QuestionPanel(QGroupBox):
    """UI panel for question extraction and editing"""
    
    def __init__(self, parent=None):
        super().__init__("Step 2: Question Extraction", parent)
        
        # Initialize OCR component
        self._init_text_extractor()
        
        # Set up the layout
        self._init_ui()
    
    def _init_text_extractor(self):
        """Initialize the text extractor (OCR) component"""
        # Try to get Tesseract path from environment or common locations
        tesseract_path = os.getenv("TESSERACT_PATH")
        
        import platform
        if platform.system() == 'Windows' and not tesseract_path:
            try:
                # Try to find Tesseract in common locations
                common_paths = [
                    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                    r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
                ]
                
                for path in common_paths:
                    if os.path.exists(path):
                        tesseract_path = path
                        break
            except Exception as e:
                print(f"Error finding Tesseract: {str(e)}")
        
        # Initialize the text extractor
        self.text_extractor = TextExtractor(tesseract_path)
    
    def _init_ui(self):
        """Initialize the UI components"""
        question_layout = QVBoxLayout(self)
        
        # Question text
        question_layout.addWidget(QLabel("Extracted Question:"))
        self.question_text = QTextEdit()
        self.question_text.setReadOnly(False)  # Allow editing for manual corrections
        question_layout.addWidget(self.question_text)
        
        # Question type selector
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Question Type:"))
        
        self.type_group = QButtonGroup(self)
        self.radio_mc = QRadioButton("Multiple Choice")
        self.radio_short = QRadioButton("Short Answer")
        self.radio_mc.setChecked(True)  # Default selection
        
        self.type_group.addButton(self.radio_mc)
        self.type_group.addButton(self.radio_short)
        
        type_layout.addWidget(self.radio_mc)
        type_layout.addWidget(self.radio_short)
        type_layout.addStretch()
        
        question_layout.addLayout(type_layout)
    
    def process_image(self, image):
        """
        Extract text from an image using OCR
        
        Args:
            image: The image to process
            
        Returns:
            bool: Success status
        """
        try:
            if image is None:
                self.question_text.setText("No image captured yet")
                return False
                
            # Extract text from the image
            extracted_text = self.text_extractor.extract_text(image)
            
            if not extracted_text:
                self.question_text.setText("No text found in the image")
                return False
                
            # Set the extracted text
            self.question_text.setText(extracted_text)
            
            # Determine if it's a multiple choice question
            is_mc = self.text_extractor.is_multiple_choice(extracted_text)
            
            # Update the radio button selection
            self.radio_mc.setChecked(is_mc)
            self.radio_short.setChecked(not is_mc)
            
            return True
            
        except Exception as e:
            error_msg = f"Failed to process image: {str(e)}"
            print(error_msg)
            self.question_text.setText(error_msg)
            return False
    
    def get_question_text(self):
        """
        Get the current question text
        
        Returns:
            str: The question text
        """
        return self.question_text.toPlainText()
    
    def is_multiple_choice(self):
        """
        Check if the current question is marked as multiple choice
        
        Returns:
            bool: True if multiple choice, False if short answer
        """
        return self.radio_mc.isChecked()