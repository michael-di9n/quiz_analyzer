import numpy as np
import cv2
from PIL import ImageGrab, Image
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt

class ScreenCapture:
    """Class for handling screen capture operations"""
    
    def __init__(self):
        self.captured_image = None
        self.captured_pil_image = None
    
    def capture_screen(self):
        """
        Capture the entire screen
        
        Returns:
            PIL.Image: The captured screenshot
        """
        # Capture the screen using PIL's ImageGrab
        self.captured_pil_image = ImageGrab.grab()
        
        # Convert to numpy array for OpenCV operations
        self.captured_image = np.array(self.captured_pil_image)
        
        # Convert from RGB to BGR (OpenCV format)
        self.captured_image = cv2.cvtColor(self.captured_image, cv2.COLOR_RGB2BGR)
        
        return self.captured_pil_image
    
    def capture_region(self, x, y, width, height):
        """
        Capture a specific region of the screen
        
        Args:
            x (int): Left coordinate
            y (int): Top coordinate
            width (int): Width of region
            height (int): Height of region
            
        Returns:
            PIL.Image: The captured region
        """
        # Capture specific region
        self.captured_pil_image = ImageGrab.grab(bbox=(x, y, x + width, y + height))
        
        # Convert to numpy array for OpenCV operations
        self.captured_image = np.array(self.captured_pil_image)
        
        # Convert from RGB to BGR (OpenCV format)
        self.captured_image = cv2.cvtColor(self.captured_image, cv2.COLOR_RGB2BGR)
        
        return self.captured_pil_image
    
    def get_captured_image(self):
        """
        Get the captured image as a numpy array
        
        Returns:
            numpy.ndarray: The captured image
        """
        return self.captured_image
    
    def get_captured_pil_image(self):
        """
        Get the captured image as a PIL Image
        
        Returns:
            PIL.Image: The captured image
        """
        return self.captured_pil_image
    
    def get_qt_pixmap(self, max_width=None, max_height=None):
        """
        Convert the captured image to a QPixmap for display in PyQt
        
        Args:
            max_width (int, optional): Maximum width for scaling
            max_height (int, optional): Maximum height for scaling
            
        Returns:
            QPixmap: The image as a QPixmap
        """
        if self.captured_pil_image is None:
            return None
        
        # Convert PIL Image to QImage
        img = self.captured_pil_image
        img_data = img.tobytes("raw", "RGB")
        q_img = QImage(img_data, img.width, img.height, img.width * 3, QImage.Format.Format_RGB888)
        
        # Convert to QPixmap
        pixmap = QPixmap.fromImage(q_img)
        
        # Scale if necessary
        if max_width and max_height and (pixmap.width() > max_width or pixmap.height() > max_height):
            pixmap = pixmap.scaled(max_width, max_height, 
                                  Qt.AspectRatioMode.KeepAspectRatio, 
                                  Qt.TransformationMode.SmoothTransformation)
        
        return pixmap