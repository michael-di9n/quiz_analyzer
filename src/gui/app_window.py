from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QTextEdit, QRadioButton, QButtonGroup, 
                           QLabel, QGroupBox, QFrame, QMessageBox, QInputDialog,
                           QProgressBar)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap
from capture.screen_capture import ScreenCapture
from ocr.text_extractor import TextExtractor
from ai.claude_client import ClaudeClient
import os
from dotenv import load_dotenv

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Quiz Analyzer")
        self.setMinimumSize(800, 600)
        
        # Load environment variables
        load_dotenv()
        
        # Initialize components
        self.screen_capture = ScreenCapture()
        
        # Initialize OCR - Ask for Tesseract path on Windows
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
                        
                # If not found, ask the user
                if not tesseract_path:
                    tesseract_path, ok = QInputDialog.getText(
                        self, 'Tesseract Path',
                        'Please enter the path to tesseract.exe:',
                        text=r'C:\Program Files\Tesseract-OCR\tesseract.exe'
                    )
                    if not ok or not os.path.exists(tesseract_path):
                        QMessageBox.warning(
                            self, 'Warning',
                            'Tesseract path not set or invalid. OCR functionality may not work.'
                        )
            except Exception as e:
                QMessageBox.warning(
                    self, 'Warning',
                    f'Error setting up Tesseract: {str(e)}. OCR functionality may not work.'
                )
        
        self.text_extractor = TextExtractor(tesseract_path)
        
        # Initialize Claude API client
        try:
            self.claude_client = ClaudeClient()
        except ValueError as e:
            QMessageBox.warning(
                self, 'API Key Missing',
                'Claude API key not found. Please create a .env file with your ANTHROPIC_API_KEY.'
            )
            self.claude_client = None
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # ====== Capture Section ======
        capture_group = QGroupBox("Step 1: Screen Capture")
        capture_layout = QVBoxLayout(capture_group)
        
        # Capture controls
        capture_btn_layout = QHBoxLayout()
        self.capture_btn = QPushButton("Capture Screen")
        self.capture_btn.setMinimumHeight(40)
        self.capture_btn.clicked.connect(self.capture_screen)
        capture_btn_layout.addWidget(self.capture_btn)
        capture_btn_layout.addStretch()
        capture_layout.addLayout(capture_btn_layout)
        
        # Preview area for captured screenshots
        self.preview_label = QLabel("Click 'Capture Screen' to take a screenshot")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setFrameShape(QFrame.Shape.StyledPanel)
        self.preview_label.setMinimumHeight(150)
        self.preview_label.setMinimumWidth(300)
        capture_layout.addWidget(self.preview_label)
        
        main_layout.addWidget(capture_group)
        
        # ====== Question Section ======
        question_group = QGroupBox("Step 2: Question Extraction")
        question_layout = QVBoxLayout(question_group)
        
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
        
        main_layout.addWidget(question_group)
        
        # ====== AI Response Section ======
        answer_group = QGroupBox("Step 3: AI Analysis")
        answer_layout = QVBoxLayout(answer_group)
        
        # Send to AI button
        send_layout = QHBoxLayout()
        self.send_btn = QPushButton("Send to Claude")
        self.send_btn.setMinimumHeight(40)
        self.send_btn.clicked.connect(self.send_to_claude)
        send_layout.addWidget(self.send_btn)
        
        # Add progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.setVisible(False)
        send_layout.addWidget(self.progress_bar)
        
        send_layout.addStretch()
        answer_layout.addLayout(send_layout)
        
        # AI response display
        answer_layout.addWidget(QLabel("Claude's Answer:"))
        self.response_text = QTextEdit()
        self.response_text.setReadOnly(True)
        answer_layout.addWidget(self.response_text)
        
        main_layout.addWidget(answer_group)
        
        # Make answer section take more space
        main_layout.setStretchFactor(answer_group, 2)
        main_layout.setStretchFactor(question_group, 1)
        main_layout.setStretchFactor(capture_group, 1)
    
    def capture_screen(self):
        """Capture the screen and update the UI"""
        try:
            # Capture the entire screen
            self.screen_capture.capture_screen()
            
            # Get the captured image as a QPixmap and display it
            preview_pixmap = self.screen_capture.get_qt_pixmap(
                max_width=self.preview_label.width(),
                max_height=self.preview_label.height()
            )
            
            if preview_pixmap:
                self.preview_label.setPixmap(preview_pixmap)
                self.preview_label.setScaledContents(True)
                
                # Extract text from the captured image
                self.process_captured_image()
            else:
                self.preview_label.setText("Failed to capture screen")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to capture screen: {str(e)}")
            self.preview_label.setText("Error capturing screen")
    
    def process_captured_image(self):
        """Extract text from the captured image using OCR"""
        try:
            # Get the captured image
            image = self.screen_capture.get_captured_image()
            
            if image is None:
                self.question_text.setText("No image captured yet")
                return
                
            # Extract text from the image
            extracted_text = self.text_extractor.extract_text(image)
            
            if not extracted_text:
                self.question_text.setText("No text found in the image")
                return
                
            # Set the extracted text
            self.question_text.setText(extracted_text)
            
            # Determine if it's a multiple choice question
            is_mc = self.text_extractor.is_multiple_choice(extracted_text)
            
            # Update the radio button selection
            self.radio_mc.setChecked(is_mc)
            self.radio_short.setChecked(not is_mc)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to process image: {str(e)}")
            self.question_text.setText(f"Error processing image: {str(e)}")
    
    def send_to_claude(self):
        """Send the extracted question to Claude API and display the response"""
        # Check if Claude client is initialized
        if self.claude_client is None:
            QMessageBox.critical(
                self, "Error",
                "Claude API client is not initialized. Please check your API key in the .env file."
            )
            return
            
        # Get the question text
        question_text = self.question_text.toPlainText()
        
        if not question_text:
            QMessageBox.warning(self, "Warning", "No question text to send. Please capture or enter a question.")
            return
            
        # Determine question type
        question_type = "multiple_choice" if self.radio_mc.isChecked() else "short_answer"
        
        # Show progress bar and disable send button during API call
        self.progress_bar.setVisible(True)
        self.send_btn.setEnabled(False)
        self.response_text.setText("Sending to Claude... Please wait.")
        
        # Use a timer to allow the UI to update
        QTimer.singleShot(100, lambda: self._send_to_claude_async(question_text, question_type))
    
    def _send_to_claude_async(self, question_text, question_type):
        """Async helper function to make the API call without freezing the UI"""
        try:
            # Get response from Claude
            response = self.claude_client.ask_question(
                question_text=question_text,
                question_type=question_type
            )
            
            # Display the response
            self.response_text.setText(response)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to get response from Claude: {str(e)}")
            self.response_text.setText(f"Error communicating with Claude: {str(e)}")
            
        finally:
            # Hide progress bar and re-enable send button
            self.progress_bar.setVisible(False)
            self.send_btn.setEnabled(True)