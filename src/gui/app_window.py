from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QTextEdit, QRadioButton, QButtonGroup, 
                           QLabel, QGroupBox, QFrame, QMessageBox, QInputDialog,
                           QProgressBar, QSystemTrayIcon, QMenu, QDialog, QApplication)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QIcon, QAction
from capture.screen_capture import ScreenCapture
from ocr.text_extractor import TextExtractor
from ai.claude_client import ClaudeClient
from export.email_sender import EmailSender
from gui.email_dialog import EmailDialog
import os
from dotenv import load_dotenv
import io
import sys

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
            
        # Initialize Email sender
        try:
            self.email_sender = EmailSender()
        except ValueError as e:
            QMessageBox.warning(
                self, 'Email Configuration Missing',
                'Email configuration not found. Please create a .env file with your EMAIL_ADDRESS and EMAIL_APP_PASSWORD.'
            )
            self.email_sender = None
        
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
        
        # Email button
        email_layout = QHBoxLayout()
        self.email_btn = QPushButton("Send Answer by Email")
        self.email_btn.setMinimumHeight(30)
        self.email_btn.clicked.connect(self.send_by_email)
        email_layout.addWidget(self.email_btn)
        email_layout.addStretch()
        answer_layout.addLayout(email_layout)
        
        main_layout.addWidget(answer_group)
        
        # Make answer section take more space
        main_layout.setStretchFactor(answer_group, 2)
        main_layout.setStretchFactor(question_group, 1)
        main_layout.setStretchFactor(capture_group, 1)
        
        # Initialize system tray
        self.setup_system_tray()
        
        # Set up to prevent closing when x is clicked
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
    
    def setup_system_tray(self):
        """Set up the system tray icon and menu"""
        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(self)
        
        # Use a standard icon - replace later with your app icon
        self.tray_icon.setIcon(QIcon.fromTheme("application-x-executable"))
        
        # Create the tray menu
        tray_menu = QMenu()
        
        # Add menu actions
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show_app)
        
        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(self.hide_app)
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_app)
        
        # Add actions to menu
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        
        # Set the menu
        self.tray_icon.setContextMenu(tray_menu)
        
        # Make the tray icon visible
        self.tray_icon.show()
        
        # Double-click to show
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
        # Set tooltip
        self.tray_icon.setToolTip("Quiz Analyzer")
    
    def tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_app()
    
    def show_app(self):
        """Show the application window"""
        self.show()
        self.activateWindow()  # Bring window to front
    
    def hide_app(self):
        """Hide the application window"""
        self.hide()
    
    def quit_app(self):
        """Quit the application"""
        # Hide the tray icon
        self.tray_icon.hide()
        
        # Actually quit the application
        QApplication.quit()
    
    def closeEvent(self, event):
        """Handle window close event - hide instead of close"""
        if self.tray_icon.isVisible():
            # Show info message only the first time
            if not hasattr(self, 'close_info_shown'):
                QMessageBox.information(
                    self,
                    "Quiz Analyzer",
                    "The application will continue running in the system tray. "
                    "To show the application again, double-click the tray icon. "
                    "To quit the application, right-click the tray icon and choose 'Quit'."
                )
                self.close_info_shown = True
            
            # Hide the window instead of closing
            self.hide()
            event.ignore()
        else:
            # If tray icon is not visible for some reason, allow normal close
            event.accept()
    
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
    
    def send_by_email(self):
        """Send the question and answer by email"""
        # Check if email sender is initialized
        if self.email_sender is None:
            QMessageBox.critical(
                self, "Error",
                "Email sender is not initialized. Please check your email configuration in the .env file."
            )
            return
        
        # Check if we have content to send
        question_text = self.question_text.toPlainText()
        answer_text = self.response_text.toPlainText()
        
        if not question_text or not answer_text:
            QMessageBox.warning(
                self, "Warning",
                "Missing content. Please make sure you have captured a question and received an answer."
            )
            return
        
        # Show the email dialog
        dialog = EmailDialog(self)
        result = dialog.exec()
        
        if result == QDialog.DialogCode.Accepted:
            # Get recipients
            recipients = dialog.get_checked_emails()
            subject = dialog.get_subject() or "Quiz Answer from Claude"
            
            # Get the screenshot image if available
            image_data = None
            if self.screen_capture.get_captured_pil_image():
                # Convert the PIL image to bytes
                img_byte_arr = io.BytesIO()
                self.screen_capture.get_captured_pil_image().save(img_byte_arr, format='PNG')
                image_data = img_byte_arr.getvalue()
            
            # Send to each recipient
            for recipient in recipients:
                # Use a timer to allow the UI to update
                QTimer.singleShot(100, lambda r=recipient: self._send_email_async(
                    r, question_text, answer_text, subject, image_data))
    
    def _send_email_async(self, recipient, question_text, answer_text, subject, image_data=None):
        """Async helper function to send email without freezing the UI"""
        try:
            # Send the email
            success, message = self.email_sender.send_quiz_answer(
                recipient_email=recipient,
                question_text=question_text,
                answer_text=answer_text,
                subject=subject,
                image_data=image_data
            )
            
            # Show result
            if success:
                QMessageBox.information(self, "Success", message)
            else:
                QMessageBox.critical(self, "Error", message)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to send email: {str(e)}")