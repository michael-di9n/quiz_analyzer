from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QMessageBox, QInputDialog, QApplication
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction
from dotenv import load_dotenv
import os
import sys

from gui.capture_panel import CapturePanel
from gui.question_panel import QuestionPanel
from gui.response_panel import ResponsePanel
from gui.system_tray_manager import SystemTrayManager
from gui.hotkey_manager import HotkeyManager

class MainWindow(QMainWindow):
    """Main window for the Quiz Analyzer application"""
    
    # Signals for communication between components
    capture_completed = pyqtSignal(bool)  # Signal with success status
    claude_completed = pyqtSignal(bool)   # Signal with success status
    email_completed = pyqtSignal(bool)    # Signal with success status
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Quiz Analyzer")
        self.setMinimumSize(800, 600)
        
        # Load environment variables
        load_dotenv()
        
        # Set up to prevent closing when x is clicked
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
        
        # Initialize UI components
        self._init_ui()
        
        # Initialize system tray
        self.system_tray = SystemTrayManager(self)
        
        # Add hotkey settings to system tray menu
        self.system_tray.add_menu_action("Hotkey Settings", self.show_hotkey_settings, 0)
        
        # Initialize hotkey service
        self.hotkey_manager = HotkeyManager(self)
        self.hotkey_manager.start()
        
        # Connect component signals to main window signals for forwarding
        self._connect_signals()
    
    def _init_ui(self):
        """Initialize the UI components"""
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create UI panels
        self.capture_panel = CapturePanel()
        self.question_panel = QuestionPanel()
        self.response_panel = ResponsePanel()
        
        # Add panels to main layout
        main_layout.addWidget(self.capture_panel)
        main_layout.addWidget(self.question_panel)
        main_layout.addWidget(self.response_panel)
        
        # Make answer section take more space
        main_layout.setStretchFactor(self.response_panel, 2)
        main_layout.setStretchFactor(self.question_panel, 1)
        main_layout.setStretchFactor(self.capture_panel, 1)
    
    def _connect_signals(self):
        """Connect signals between components"""
        # Forward signals from components to main window signals
        self.capture_panel.capture_completed.connect(self.capture_completed)
        self.response_panel.claude_completed.connect(self.claude_completed)
        self.response_panel.email_completed.connect(self.email_completed)
        
        # Connect capture button to process captured images
        self.capture_panel.capture_completed.connect(self.on_capture_completed)
        
        # CHANGE: Connect the new analyze button in question panel
        self.question_panel.analyze_btn.clicked.connect(self.on_analyze_button_clicked)
        
        # Connect hotkey manager to components
        self.hotkey_manager.connect_signals(
            self.capture_panel,
            self.question_panel,
            self.response_panel
        )
        
        # Connect send button in response panel
        self.response_panel.send_btn.clicked.connect(self.on_send_to_claude_clicked)
    
    def on_capture_completed(self, success):
        """Handle completion of capture to process the image"""
        if success:
            # Get the captured image and process it with OCR
            image = self.capture_panel.get_captured_image()
            self.question_panel.process_image(image)
            
    # CHANGE: Added new method to handle the analyze button click
    def on_analyze_button_clicked(self):
        """Handle manual analysis button click in question panel"""
        # Get the captured image
        image = self.capture_panel.get_captured_image()
        if image is None:
            QMessageBox.warning(
                self, "No Image", 
                "No image has been captured. Please capture an image first."
            )
            return
            
        # Process the image with OCR
        success = self.question_panel.process_image(image)
        
        # Show appropriate message
        if success:
            QMessageBox.information(
                self, "Analysis Complete", 
                "The image has been analyzed and text has been extracted."
            )
        else:
            QMessageBox.warning(
                self, "Analysis Failed", 
                "Failed to extract text from the image. The image may not contain readable text."
            )
    
    def on_send_to_claude_clicked(self):
        """Handle send to Claude button click"""
        question_text = self.question_panel.get_question_text()
        question_type = "multiple_choice" if self.question_panel.is_multiple_choice() else "short_answer"
        
        # Send to Claude
        self.response_panel.send_to_claude(question_text, question_type)
    
    def show_hotkey_settings(self):
        """Show the hotkey settings dialog"""
        self.hotkey_manager.show_settings_dialog()
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Delegate to system tray manager
        if self.system_tray.handle_close_event(event):
            return
        
        # If not handled by system tray, proceed with normal close
        event.accept()
    
    def quit_app(self):
        """Quit the application"""
        # Stop the hotkey service
        if hasattr(self, 'hotkey_manager'):
            self.hotkey_manager.stop()
            
        # Close the application
        QApplication.quit()
    
    # These methods provide backward compatibility with the hotkey service
    def capture_screen(self, emit_signal=False):
        """Forward to capture panel"""
        return self.capture_panel.capture_screen(emit_signal)
    
    def send_to_claude(self, emit_signal=False):
        """Forward to response panel"""
        question_text = self.question_panel.get_question_text()
        question_type = "multiple_choice" if self.question_panel.is_multiple_choice() else "short_answer"
        return self.response_panel.send_to_claude(question_text, question_type, emit_signal)
    
    def send_by_email(self, show_dialog=True, emit_signal=False):
        """Forward to response panel"""
        question_text = self.question_panel.get_question_text()
        answer_text = self.response_panel.get_response_text()
        
        # Get the screenshot image if available
        image_data = None
        if self.capture_panel.get_captured_pil_image():
            import io
            img_byte_arr = io.BytesIO()
            self.capture_panel.get_captured_pil_image().save(img_byte_arr, format='PNG')
            image_data = img_byte_arr.getvalue()
        
        return self.response_panel.send_by_email(
            question_text, 
            answer_text,
            image_data, 
            show_dialog, 
            emit_signal
        )