from PyQt6.QtWidgets import (QGroupBox, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QLabel, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from capture.screen_capture import ScreenCapture

class CapturePanel(QGroupBox):
    """UI panel for screenshot capture functionality"""
    
    # Signal emitted when capture is completed
    capture_completed = pyqtSignal(bool)  # Signal with success status
    
    def __init__(self, parent=None):
        super().__init__("Step 1: Screen Capture", parent)
        
        # Initialize screen capture component
        self.screen_capture = ScreenCapture()
        
        # Set up the layout
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the UI components"""
        capture_layout = QVBoxLayout(self)
        
        # Capture controls
        capture_btn_layout = QHBoxLayout()
        self.capture_btn = QPushButton("Capture Screen")
        self.capture_btn.setMinimumHeight(40)
        self.capture_btn.clicked.connect(lambda: self.capture_screen(emit_signal=False))
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
    
    def capture_screen(self, emit_signal=False):
        """
        Capture the screen and update the UI
        
        Args:
            emit_signal (bool): Whether to emit the capture_completed signal
            
        Returns:
            bool: Success status
        """
        success = False
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
                print("Captured screen.")
                success = True
            else:
                self.preview_label.setText("Failed to capture screen")
        except Exception as e:
            print(f"Failed to capture screen: {str(e)}")
            self.preview_label.setText("Error capturing screen")

        # Emit signal only if requested (for hotkey sequence)
        if emit_signal:
            self.capture_completed.emit(success)
        return success
    
    def get_captured_image(self):
        """
        Get the captured image
        
        Returns:
            The captured image or None
        """
        return self.screen_capture.get_captured_image()
    
    def get_captured_pil_image(self):
        """
        Get the captured PIL image
        
        Returns:
            PIL.Image or None: The captured image
        """
        return self.screen_capture.get_captured_pil_image()