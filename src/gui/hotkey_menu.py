from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                           QLabel, QDoubleSpinBox, QPushButton, 
                           QCheckBox, QGroupBox, QMessageBox)
from PyQt6.QtCore import Qt
from hotkey.hotkey_config import HotkeyConfig

class HotkeySettingsDialog(QDialog):
    """Dialog for configuring hotkey settings"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Hotkey Settings")
        self.setMinimumWidth(350)
        
        # Initialize config
        self.config = HotkeyConfig()
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Settings group
        settings_group = QGroupBox("Hotkey Configuration")
        settings_layout = QVBoxLayout(settings_group)
        
        # Enable checkbox
        self.enable_checkbox = QCheckBox("Enable Hotkey Functionality")
        self.enable_checkbox.setChecked(self.config.is_enabled())
        settings_layout.addWidget(self.enable_checkbox)
        
        # Hold duration setting
        hold_layout = QHBoxLayout()
        hold_layout.addWidget(QLabel("Hold Duration (seconds):"))
        
        self.duration_spinner = QDoubleSpinBox()
        self.duration_spinner.setMinimum(0.5)
        self.duration_spinner.setMaximum(10.0)
        self.duration_spinner.setSingleStep(0.5)
        self.duration_spinner.setValue(self.config.get_hold_duration())
        self.duration_spinner.setDecimals(1)
        hold_layout.addWidget(self.duration_spinner)
        
        settings_layout.addLayout(hold_layout)
        
        # Add information label
        info_label = QLabel(
            "The activation key is the digit that matches the current minute's ones digit.\n"
            "For example, if the time is 10:23, the activation key is 3."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666666; font-style: italic;")
        settings_layout.addWidget(info_label)
        
        layout.addWidget(settings_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_settings)
        self.save_btn.setDefault(True)
        
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
    
    def save_settings(self):
        """Save the settings and close the dialog"""
        # Get values from UI
        enabled = self.enable_checkbox.isChecked()
        hold_duration = self.duration_spinner.value()
        
        # Save to config
        success_enabled = self.config.set_enabled(enabled)
        success_duration = self.config.set_hold_duration(hold_duration)
        
        if not (success_enabled and success_duration):
            QMessageBox.warning(
                self,
                "Save Error",
                "Failed to save one or more settings. Please try again."
            )
            return
            
        # Accept (close dialog)
        self.accept()