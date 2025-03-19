from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication, QMessageBox
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QBrush, QPen, QFont, QColor, QAction
from PyQt6.QtCore import Qt
import os

class SystemTrayManager:
    """Manages system tray icon and menu functionality"""
    
    def __init__(self, parent_window):
        """
        Initialize the system tray manager
        
        Args:
            parent_window: The parent window to control (show/hide/quit)
        """
        self.parent_window = parent_window
        
        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(parent_window)
        
        # Set up the icon
        self._setup_icon()
        
        # Set up the menu
        self._setup_menu()
        
        # Make the tray icon visible
        self.tray_icon.show()
        
        # Set tooltip
        self.tray_icon.setToolTip("Quiz Analyzer")
        
        # Track if close info has been shown
        self.close_info_shown = False
    
    def _setup_icon(self):
        """Set up the system tray icon"""
        try:
            # Try to load the icon from the gui folder
            current_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(current_dir, "icon.png")
            
            # Check if the file exists
            if os.path.exists(icon_path):
                app_icon = QIcon(icon_path)
                
                # Verify that the icon was loaded successfully
                if not app_icon.isNull():
                    # Icon loaded successfully
                    print(f"Using icon from: {icon_path}")
                else:
                    # Icon couldn't be loaded, use fallback
                    raise FileNotFoundError("Icon loaded but is null")
            else:
                # Icon file doesn't exist, use fallback
                raise FileNotFoundError(f"Icon not found at: {icon_path}")
                
        except Exception as e:
            # Fallback: Create a simple icon programmatically
            print(f"Using fallback icon. Error: {str(e)}")
            
            icon_pixmap = QPixmap(64, 64)
            icon_pixmap.fill(Qt.GlobalColor.transparent)
            
            # Draw a simple "Q" icon
            painter = QPainter(icon_pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setBrush(QBrush(QColor(0, 120, 215)))  # Windows blue color
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(4, 4, 56, 56)  # Draw a circle
            
            # Draw "Q" letter
            painter.setPen(QPen(Qt.GlobalColor.white, 2))
            font = QFont("Arial", 32, QFont.Weight.Bold)
            painter.setFont(font)
            painter.drawText(icon_pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "Q")
            painter.end()
            
            # Create icon from pixmap
            app_icon = QIcon(icon_pixmap)
        
        # Set the application and tray icon
        self.tray_icon.setIcon(app_icon)
        self.parent_window.setWindowIcon(app_icon)
    
    def _setup_menu(self):
        """Set up the system tray menu"""
        # Create the tray menu
        tray_menu = QMenu()
        
        # Add menu actions
        show_action = QAction("Show", self.parent_window)
        show_action.triggered.connect(self.show_app)
        
        hide_action = QAction("Hide", self.parent_window)
        hide_action.triggered.connect(self.hide_app)
        
        quit_action = QAction("Quit", self.parent_window)
        quit_action.triggered.connect(self.quit_app)
        
        # Add actions to menu
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        
        # Set the menu
        self.tray_icon.setContextMenu(tray_menu)
        
        # Double-click to show
        self.tray_icon.activated.connect(self._tray_icon_activated)
    
    def add_menu_action(self, text, slot, position=-1):
        """
        Add a custom action to the tray menu
        
        Args:
            text (str): Action text
            slot: Function to call when triggered
            position (int): Position to insert action (-1 for before quit)
            
        Returns:
            QAction: The created action
        """
        menu = self.tray_icon.contextMenu()
        action = QAction(text, self.parent_window)
        action.triggered.connect(slot)
        
        # Add at specific position or before quit
        if position >= 0:
            actions = menu.actions()
            if position < len(actions):
                menu.insertAction(actions[position], action)
                return action
        
        # Add before the separator and quit action
        actions = menu.actions()
        if len(actions) >= 2:  # Separator and quit at minimum
            menu.insertAction(actions[-2], action)  # Insert before separator
            return action
        
        # Fallback: Just add to the end
        menu.addAction(action)
        return action
    
    def _tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_app()
    
    def show_app(self):
        """Show the application window"""
        self.parent_window.show()
        self.parent_window.activateWindow()  # Bring window to front
    
    def hide_app(self):
        """Hide the application window"""
        self.parent_window.hide()
    
    def quit_app(self):
        """Quit the application"""
        # Hide the tray icon
        self.tray_icon.hide()
        
        # Tell application to quit
        QApplication.quit()
    
    def handle_close_event(self, event):
        """
        Handle window close event - hide instead of close
        
        Args:
            event: The close event
            
        Returns:
            bool: True if event was handled, False otherwise
        """
        if self.tray_icon.isVisible():
            # Show info message only the first time
            if not self.close_info_shown:
                QMessageBox.information(
                    self.parent_window,
                    "Quiz Analyzer",
                    "The application will continue running in the system tray. "
                    "To show the application again, double-click the tray icon. "
                    "To quit the application, right-click the tray icon and choose 'Quit'."
                )
                self.close_info_shown = True
            
            # Hide the window instead of closing
            self.parent_window.hide()
            event.ignore()
            return True
        
        # Not handled, proceed with normal close behavior
        return False