import time
import threading
from pynput import keyboard
from datetime import datetime
from .hotkey_config import HotkeyConfig
from PyQt6.QtCore import QTimer, QObject

class HotkeyService(QObject):  # Make HotkeyService inherit from QObject for signals support
    """Service for handling global hotkeys for the Quiz Analyzer"""
    
    def __init__(self, main_window=None):
        """
        Initialize the HotkeyService
        
        Args:
            main_window: Reference to the MainWindow instance for trigger actions
        """
        super().__init__()  # Initialize QObject
        
        self.main_window = main_window
        self.config = HotkeyConfig()
        
        # Initialize key tracking variables
        self.key_press_times = {}  # Track when keys were pressed
        self.listener = None
        self.running = False
        
        # Define number keys to monitor (0-9)
        self.number_keys = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        
        # Flag to track if a sequence is already in progress
        self.sequence_in_progress = False
        
        # Connect signals if main_window is provided
        if self.main_window:
            self.connect_signals()
    
    def connect_signals(self):
        """Connect signals from the main window to sequence handlers"""
        # Connect completion signals to next steps in the sequence
        self.main_window.capture_completed.connect(self.on_capture_completed)
        self.main_window.claude_completed.connect(self.on_claude_completed)
        self.main_window.email_completed.connect(self.on_email_completed)
    
    def start(self):
        """Start the hotkey listener"""
        if self.running:
            return
            
        self.running = True
        
        # Start keyboard listener in a separate thread
        self.listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        self.listener.start()
    
    def stop(self):
        """Stop the hotkey listener"""
        self.running = False
        if self.listener:
            self.listener.stop()
            self.listener = None
    
    def on_key_press(self, key):
        """
        Handle key press events
        
        Args:
            key: The key that was pressed
        """
        if not self.config.is_enabled():
            return
            
        # Convert key to string representation
        try:
            key_str = key.char
        except AttributeError:
            # Not a character key (e.g., shift, ctrl)
            return
            
        # Check if the key is a number key
        if key_str in self.number_keys:
            # Record the time when the key was pressed
            if key_str not in self.key_press_times:
                self.key_press_times[key_str] = time.time()
    
    def on_key_release(self, key):
        """
        Handle key release events
        
        Args:
            key: The key that was released
        """
        if not self.config.is_enabled():
            return
            
        # Convert key to string representation
        try:
            key_str = key.char
        except AttributeError:
            # Not a character key
            return
            
        # Check if this was a number key that we're tracking
        if key_str in self.key_press_times:
            # Calculate how long the key was held
            press_time = self.key_press_times[key_str]
            release_time = time.time()
            hold_duration = release_time - press_time
            
            # Remove from tracking
            del self.key_press_times[key_str]
            
            # Check if the key matches the current minute's ones digit
            activation_key = self.config.get_activation_key()
            
            if key_str == activation_key:
                # Check if held long enough
                required_duration = self.config.get_hold_duration()
                if hold_duration >= required_duration:
                    # Trigger the action sequence
                    self.trigger_action_sequence()
    
    def trigger_action_sequence(self):
        """Trigger the sequence of actions in the main window"""
        if not self.main_window:
            return
            
        # Check if a sequence is already in progress
        if self.sequence_in_progress:
            print("Action sequence already in progress. Ignoring new request.")
            return
            
        # Set flag to indicate a sequence is starting
        self.sequence_in_progress = True
        
        # Start the sequence by capturing the screen
        # Use QTimer to ensure we're on the main thread
        QTimer.singleShot(0, self.start_capture)

    def start_capture(self):
        """Start the capture process"""
        print("Starting screen capture...")
        
        # Call capture_screen with emit_signal=True
        success = self.main_window.capture_screen(emit_signal=True)
        
        # If capture_screen returned False immediately (failed to start),
        # clean up the sequence
        if not success:
            print("Screen capture failed to start")
            self.sequence_in_progress = False
        
    def on_capture_completed(self, success):
        """Handle completion of screen capture"""
        print(f"Screen capture completed: {'Success' if success else 'Failed'}")
        
        if not success:
            # End sequence if capture failed
            self.sequence_in_progress = False
            return
        
        # Move to next step - send to Claude
        # Use a small delay to allow UI to update
        QTimer.singleShot(100, self.start_claude_analysis)
    
    def start_claude_analysis(self):
        """Start the Claude analysis process"""
        print("Starting Claude analysis...")
        
        # Call send_to_claude with emit_signal=True
        success = self.main_window.send_to_claude(emit_signal=True)
        
        # If send_to_claude returned False immediately (failed to start),
        # clean up the sequence
        if not success:
            print("Claude analysis failed to start")
            self.sequence_in_progress = False
    
    def on_claude_completed(self, success):
        """Handle completion of Claude analysis"""
        print(f"Claude analysis completed: {'Success' if success else 'Failed'}")
        
        if not success:
            # End sequence if Claude analysis failed
            self.sequence_in_progress = False
            return
        
        # Move to next step - send email
        # Use a small delay to allow UI to update
        QTimer.singleShot(100, self.start_email_sending)
    
    def start_email_sending(self):
        """Start the email sending process"""
        print("Starting email sending...")
        
        # Call send_by_email with show_dialog=False and emit_signal=True
        success = self.main_window.send_by_email(show_dialog=False, emit_signal=True)
        
        # If send_by_email returned False immediately (failed to start),
        # clean up the sequence
        if not success:
            print("Email sending failed to start")
            self.sequence_in_progress = False
    
    def on_email_completed(self, success):
        """Handle completion of email sending"""
        print(f"Email sending completed: {'Success' if success else 'Failed'}")
        
        # End the sequence
        self.sequence_in_progress = False