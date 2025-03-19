# GUI module for the Quiz Analyzer application

# Import original components
from gui.email_dialog import EmailDialog
from gui.recipient_manager import RecipientManager, Recipient
from gui.hotkey_menu import HotkeySettingsDialog

# Import new refactored components
from gui.capture_panel import CapturePanel
from gui.question_panel import QuestionPanel
from gui.response_panel import ResponsePanel
from gui.system_tray_manager import SystemTrayManager
from gui.hotkey_manager import HotkeyManager
from gui.app_window import MainWindow

__all__ = [
    'MainWindow',
    'CapturePanel',
    'QuestionPanel',
    'ResponsePanel',
    'SystemTrayManager',
    'HotkeyManager',
    'EmailDialog',
    'RecipientManager',
    'Recipient',
    'HotkeySettingsDialog'
]