from PyQt6.QtWidgets import (QGroupBox, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QLabel, QTextEdit, QProgressBar,
                           QMessageBox, QDialog)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from ai.claude_client import ClaudeClient
from export.email_sender import EmailSender
from gui.email_dialog import EmailDialog
import os
from dotenv import load_dotenv

class ResponsePanel(QGroupBox):
    """UI panel for Claude AI responses and email functionality"""
    
    # Signals
    claude_completed = pyqtSignal(bool)  # Signal with success status
    email_completed = pyqtSignal(bool)   # Signal with success status
    
    def __init__(self, parent=None):
        super().__init__("Step 3: AI Analysis", parent)
        
        # Initialize components
        self._init_components()
        
        # Set up the layout
        self._init_ui()
    
    def _init_components(self):
        """Initialize the Claude API client and Email sender"""
        # Load environment variables
        load_dotenv()
        
        # Initialize Claude API client
        try:
            self.claude_client = ClaudeClient()
        except ValueError as e:
            print(f"API Key Missing: {str(e)}")
            self.claude_client = None
            
        # Initialize Email sender
        try:
            self.email_sender = EmailSender()
        except ValueError as e:
            print(f"Email Configuration Missing: {str(e)}")
            self.email_sender = None
    
    def _init_ui(self):
        """Initialize the UI components"""
        answer_layout = QVBoxLayout(self)
        
        # Send to AI button
        send_layout = QHBoxLayout()
        self.send_btn = QPushButton("Send to Claude")
        self.send_btn.setMinimumHeight(40)
        self.send_btn.clicked.connect(lambda: self.send_to_claude(emit_signal=False))
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
        self.email_btn.clicked.connect(lambda: self.send_by_email(show_dialog=True, emit_signal=False))
        email_layout.addWidget(self.email_btn)
        email_layout.addStretch()
        answer_layout.addLayout(email_layout)
    
    def send_to_claude(self, question_text, question_type="multiple_choice", emit_signal=False):
        """
        Send the question to Claude API and display the response
        
        Args:
            question_text (str): The question text to send
            question_type (str): Either "multiple_choice" or "short_answer"
            emit_signal (bool): Whether to emit the claude_completed signal
            
        Returns:
            bool: True if the process started successfully, False otherwise
        """
        # Check if Claude client is initialized
        if self.claude_client is None:
            QMessageBox.critical(
                self, "Error",
                "Claude API client is not initialized. Please check your API key in the .env file."
            )
            if emit_signal:
                self.claude_completed.emit(False)
            return False
            
        if not question_text:
            QMessageBox.warning(self, "Warning", "No question text to send. Please capture or enter a question.")
            if emit_signal:
                self.claude_completed.emit(False)
            return False
            
        # Show progress bar and disable send button during API call
        self.progress_bar.setVisible(True)
        self.send_btn.setEnabled(False)
        self.response_text.setText("Sending to Claude... Please wait.")
        
        # Use a timer to allow the UI to update
        QTimer.singleShot(100, lambda: self._send_to_claude_async(question_text, question_type, emit_signal))
        return True  # Return success for starting the process
    
    def _send_to_claude_async(self, question_text, question_type, emit_signal=False):
        """Async helper function to make the API call without freezing the UI"""
        success = False
        try:
            # Get response from Claude
            response = self.claude_client.ask_question(
                question_text=question_text,
                question_type=question_type
            )
            
            # Display the response
            self.response_text.setText(response)
            success = True
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to get response from Claude: {str(e)}")
            self.response_text.setText(f"Error communicating with Claude: {str(e)}")
            
        finally:
            # Hide progress bar and re-enable send button
            self.progress_bar.setVisible(False)
            self.send_btn.setEnabled(True)
            
            # Emit signal only if requested (for hotkey sequence)
            if emit_signal:
                self.claude_completed.emit(success)
    
    def send_by_email(self, question_text, answer_text, image_data=None, show_dialog=True, emit_signal=False):
        """
        Send the question and answer by email
        
        Args:
            question_text (str): The question text
            answer_text (str): The answer text
            image_data (bytes, optional): Screenshot image data to attach
            show_dialog (bool): Whether to show the email dialog or send automatically
            emit_signal (bool): Whether to emit the email_completed signal
            
        Returns:
            bool: True if email sending process started successfully, False otherwise
        """
        print(f"Sending by email. Show dialog: {show_dialog}")
        success = False
        
        # Check if email sender is initialized
        if self.email_sender is None:
            if show_dialog:
                QMessageBox.critical(
                    self, "Error",
                    "Email sender is not initialized. Please check your email configuration in the .env file."
                )
            print("Email sender is not initialized")
            self.email_completed.emit(False)
            return False
        
        # Check if we have content to send
        if not question_text or not answer_text:
            if show_dialog:
                QMessageBox.warning(
                    self, "Warning",
                    "Missing content. Please make sure you have captured a question and received an answer."
                )
            print("Missing content for email")
            self.email_completed.emit(False)
            return False
        
        if show_dialog:
            # Show the email dialog
            dialog = EmailDialog(self)
            result = dialog.exec()
            
            if result == QDialog.DialogCode.Accepted:
                # Get recipients
                recipients = dialog.get_checked_emails()
                subject = dialog.get_subject() or "Quiz Answer from Claude"
                
                # Send to each recipient
                for recipient in recipients:
                    # Use a timer to allow the UI to update
                    QTimer.singleShot(100, lambda r=recipient: self._send_email_async(
                        r, question_text, answer_text, subject, image_data, show_dialog))
                success = True
            else:
                success = False
        else:
            # Automatic mode - get recipients from recipient manager
            from gui.recipient_manager import RecipientManager
            recipient_manager = RecipientManager()
            recipients = recipient_manager.get_checked_recipients()
            
            if not recipients:
                print("No recipients selected for automatic email")
                self.email_completed.emit(False)
                return False
                
            subject = "Quiz Answer from Claude (Auto-Sent)"
            
            # Send to each recipient
            for recipient in recipients:
                try:
                    # Send directly without timer
                    self._send_email_async(
                        recipient.email, 
                        question_text, 
                        answer_text, 
                        subject, 
                        image_data,
                        show_dialog,
                        emit_signal
                    )
                    success = True
                except Exception as e:
                    print(f"Error sending automatic email: {str(e)}")
                    success = False
        
        # If no actual sending occurs, emit completion now
        if emit_signal and not success:
            self.email_completed.emit(False)
        
        return success
    
    def _send_email_async(self, recipient, question_text, answer_text, subject, image_data=None, show_dialog=True, emit_signal=False):
        """Async helper function to send email without freezing the UI"""
        success = False
        try:
            # Send the email
            success, message = self.email_sender.send_quiz_answer(
                recipient_email=recipient,
                question_text=question_text,
                answer_text=answer_text,
                subject=subject,
                image_data=image_data
            )
            
            # Show result only if show_dialog is True
            if show_dialog:
                if success:
                    QMessageBox.information(self, "Success", message)
                else:
                    QMessageBox.critical(self, "Error", message)
            else:
                # Just log the result in automatic mode
                print(f"Email to {recipient}: {'Success' if success else 'Failed - ' + message}")
                
        except Exception as e:
            if show_dialog:
                QMessageBox.critical(self, "Error", f"Failed to send email: {str(e)}")
            else:
                print(f"Error sending email: {str(e)}")
            success = False
        
        if emit_signal:
            # Emit signal with success status
            self.email_completed.emit(success)
    
    def get_response_text(self):
        """
        Get the current response text
        
        Returns:
            str: The response text
        """
        return self.response_text.toPlainText()