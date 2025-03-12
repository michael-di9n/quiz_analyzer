from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                           QLabel, QLineEdit, QPushButton, 
                           QMessageBox, QProgressBar)
from PyQt6.QtCore import Qt, QTimer

class EmailDialog(QDialog):
    """Dialog for sending emails with quiz answers"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Send Quiz Answer by Email")
        self.setMinimumWidth(400)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Recipient field
        recipient_layout = QHBoxLayout()
        recipient_layout.addWidget(QLabel("Recipient Email:"))
        self.recipient_input = QLineEdit()
        recipient_layout.addWidget(self.recipient_input)
        layout.addLayout(recipient_layout)
        
        # Subject field (optional)
        subject_layout = QHBoxLayout()
        subject_layout.addWidget(QLabel("Subject (optional):"))
        self.subject_input = QLineEdit()
        self.subject_input.setText("Quiz Answer from Claude")
        subject_layout.addWidget(self.subject_input)
        layout.addLayout(subject_layout)
        
        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.accept)
        self.send_btn.setDefault(True)
        
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.send_btn)
        layout.addLayout(button_layout)
    
    def get_recipient(self):
        """Get the recipient email address entered by the user"""
        return self.recipient_input.text().strip()
    
    def get_subject(self):
        """Get the email subject entered by the user"""
        return self.subject_input.text().strip()
    
    def show_progress(self, visible=True):
        """Show or hide the progress bar"""
        self.progress_bar.setVisible(visible)
        
        # Disable/enable buttons when showing progress
        self.send_btn.setEnabled(not visible)
        self.cancel_btn.setEnabled(not visible)
    
    def accept(self):
        """Override accept to validate input before closing"""
        recipient = self.get_recipient()
        
        if not recipient:
            QMessageBox.warning(
                self, "Missing Information",
                "Please enter a recipient email address."
            )
            return
            
        # Very basic email validation
        if "@" not in recipient or "." not in recipient:
            QMessageBox.warning(
                self, "Invalid Email",
                "Please enter a valid email address."
            )
            return
            
        # Call the parent class accept method to close the dialog
        super().accept()