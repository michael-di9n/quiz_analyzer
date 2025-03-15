from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                           QLabel, QLineEdit, QPushButton, 
                           QMessageBox, QProgressBar, QScrollArea,
                           QCheckBox, QFrame, QWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from gui.recipient_manager import RecipientManager, Recipient

class EmailDialog(QDialog):
    """Dialog for sending emails with quiz answers"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Send Quiz Answer by Email")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        # Initialize recipient manager
        self.recipient_manager = RecipientManager()
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Recipients section label
        layout.addWidget(QLabel("<b>Select Recipients:</b>"))
        
        # Create scrollable area for recipients
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMinimumHeight(200)
        
        # Create widget to hold recipient checkboxes
        self.recipients_widget = QWidget()
        self.recipients_layout = QVBoxLayout(self.recipients_widget)
        
        # Add recipients widget to scroll area
        self.scroll_area.setWidget(self.recipients_widget)
        layout.addWidget(self.scroll_area)
        
        # Add new recipient section
        layout.addWidget(QLabel("<b>Add New Recipient:</b>"))
        
        # Name field
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.name_input = QLineEdit()
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # Email field
        email_layout = QHBoxLayout()
        email_layout.addWidget(QLabel("Email:"))
        self.email_input = QLineEdit()
        email_layout.addWidget(self.email_input)
        layout.addLayout(email_layout)
        
        # Add button
        add_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add to Recipients")
        self.add_btn.clicked.connect(self.add_new_recipient)
        add_layout.addWidget(self.add_btn)
        add_layout.addStretch()
        layout.addLayout(add_layout)
        
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # Subject field
        subject_layout = QHBoxLayout()
        subject_layout.addWidget(QLabel("Subject:"))
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
        
        # Populate recipients
        self.populate_recipients()
        
        # Select first valid recipient if available
        self.select_first_valid()
    
    def populate_recipients(self):
        """Populate the recipients list"""
        # Clear existing items
        while self.recipients_layout.count():
            item = self.recipients_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Load recipients
        recipients = self.recipient_manager.get_recipients()
        
        if not recipients:
            # Add a label if no recipients
            label = QLabel("No recipients found. Add one below.")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.recipients_layout.addWidget(label)
            return
        
        # Add each recipient with a checkbox
        for recipient in recipients:
            # Create a frame for each recipient
            frame = QFrame()
            frame.setFrameShape(QFrame.Shape.Panel)
            frame.setFrameShadow(QFrame.Shadow.Raised)
            
            # Create layout for the frame
            frame_layout = QHBoxLayout(frame)
            
            # Create checkbox
            checkbox = QCheckBox()
            checkbox.setChecked(recipient.checked)
            checkbox.setEnabled(recipient.valid)  # Disable if invalid
            
            # Store the email in the checkbox for later reference
            checkbox.setProperty("email", recipient.email)
            
            # Connect to slot for updating checked status
            checkbox.stateChanged.connect(self.update_recipient_status)
            
            frame_layout.addWidget(checkbox)
            
            # Create label for recipient info
            label_text = f"{recipient.name} <{recipient.email}>"
            label = QLabel(label_text)
            
            # Apply strikethrough style if invalid
            if not recipient.valid:
                font = QFont()
                font.setStrikeOut(True)
                label.setFont(font)
                label.setStyleSheet("color: #999999;")  # Grey out invalid emails
                label.setToolTip("Invalid email address")
            
            frame_layout.addWidget(label)
            frame_layout.addStretch()
            
            # Add the frame to the main layout
            self.recipients_layout.addWidget(frame)
        
        # Add stretch to push all items to the top
        self.recipients_layout.addStretch()
    
    def select_first_valid(self):
        """Select the first valid recipient if available"""
        for i in range(self.recipients_layout.count()):
            item = self.recipients_layout.itemAt(i)
            if not item or not item.widget():
                continue
                
            frame = item.widget()
            for j in range(frame.layout().count()):
                widget = frame.layout().itemAt(j).widget()
                if isinstance(widget, QCheckBox) and widget.isEnabled():
                    widget.setChecked(True)
                    return
    
    def update_recipient_status(self, state):
        """Update the checked status of a recipient"""
        checkbox = self.sender()
        if not checkbox:
            return
            
        email = checkbox.property("email")
        checked = checkbox.isChecked()
        
        # Update in recipient manager
        self.recipient_manager.update_recipient_status(email, checked)
    
    def add_new_recipient(self):
        """Add a new recipient to the list"""
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        
        if not name or not email:
            QMessageBox.warning(
                self, "Missing Information",
                "Please enter both name and email address."
            )
            return
        
        # Add to recipient manager
        recipient = self.recipient_manager.add_recipient(name, email, True)
        
        # Show validation result
        if not recipient.valid:
            QMessageBox.warning(
                self, "Invalid Email",
                f"The email address '{email}' appears to be invalid. "
                "It will be added but cannot be selected."
            )
        
        # Clear inputs
        self.name_input.clear()
        self.email_input.clear()
        
        # Refresh the list
        self.populate_recipients()
    
    def get_checked_emails(self):
        """Get a list of checked email addresses"""
        return [r.email for r in self.recipient_manager.get_checked_recipients()]
    
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
        # Get checked recipients
        recipients = self.recipient_manager.get_checked_recipients()
        
        if not recipients:
            QMessageBox.warning(
                self, "Missing Recipients",
                "Please select at least one valid recipient."
            )
            return
            
        # Call the parent class accept method to close the dialog
        super().accept()