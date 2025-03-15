import time
import threading
from pynput import keyboard
from datetime import datetime
from .hotkey_config import HotkeyConfig

class HotkeyService:
    """Service for handling global hotkeys for the Quiz Analyzer"""
    
    def __init__(self, main_window=None):
        """
        Initialize the HotkeyService
        
        Args:
            main_window: Reference to the MainWindow instance for trigger actions
        """
        self.main_window = main_window
        self.config = HotkeyConfig()
        
        # Initialize key tracking variables
        self.key_press_times = {}  # Track when keys were pressed
        self.listener = None
        self.running = False
        
        # Define number keys to monitor (0-9)
        self.number_keys = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    
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
            
        # Use a thread to avoid blocking the hotkey listener
        threading.Thread(target=self._execute_action_sequence).start()
    
    def _execute_action_sequence(self):
        """Execute the sequence of actions in the main window"""
        try:
            # 1. Capture the screen
            self.main_window.capture_screen()
            
            # Wait a moment for processing
            time.sleep(0.5)
            
            # 2. Send to Claude
            self.main_window.send_to_claude()
            
            # Wait for Claude to respond (this is approximate)
            # In a real implementation, we would need a callback or event
            time.sleep(5)
            
            # 3. Send by email
            self.main_window.send_by_email()
            
        except Exception as e:
            # Silently fail as per requirements
            print(f"Error in action sequence: {str(e)}")