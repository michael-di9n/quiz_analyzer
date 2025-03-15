import os
import configparser
from datetime import datetime

class HotkeyConfig:
    """Class for managing hotkey configuration settings"""
    
    DEFAULT_HOLD_DURATION = 2  # Default hold duration in seconds
    CONFIG_FILE = "hotkey_config.ini"
    
    def __init__(self, config_dir=None):
        """
        Initialize the HotkeyConfig with the specified config directory
        
        Args:
            config_dir (str, optional): Directory to store the config file
                                        If None, uses the same directory as this file
        """
        # Set the config directory
        if config_dir is None:
            self.config_dir = os.path.dirname(os.path.abspath(__file__))
        else:
            self.config_dir = config_dir
            
        # Set the full path to the config file
        self.config_path = os.path.join(self.config_dir, self.CONFIG_FILE)
        
        # Initialize the config parser
        self.config = configparser.ConfigParser()
        
        # Load existing config or create with defaults
        self.load_config()
    
    def load_config(self):
        """Load the configuration from the config file or create with defaults if not exists"""
        # Check if config file exists
        if os.path.exists(self.config_path):
            try:
                # Load existing config
                self.config.read(self.config_path)
                
                # Ensure the hotkeys section exists
                if not self.config.has_section('Hotkeys'):
                    self.config.add_section('Hotkeys')
                    self.set_defaults()
                    self.save_config()
            except Exception as e:
                print(f"Error loading config: {str(e)}")
                # Create a new config with defaults
                self.config = configparser.ConfigParser()
                self.config.add_section('Hotkeys')
                self.set_defaults()
                self.save_config()
        else:
            # Create a new config with defaults
            self.config.add_section('Hotkeys')
            self.set_defaults()
            self.save_config()
    
    def set_defaults(self):
        """Set default values for the configuration"""
        self.config.set('Hotkeys', 'enabled', 'true')
        self.config.set('Hotkeys', 'hold_duration', str(self.DEFAULT_HOLD_DURATION))
    
    def save_config(self):
        """Save the configuration to the config file"""
        try:
            with open(self.config_path, 'w') as f:
                self.config.write(f)
            return True
        except Exception as e:
            print(f"Error saving config: {str(e)}")
            return False
    
    def get_hold_duration(self):
        """Get the configured hold duration in seconds"""
        try:
            return float(self.config.get('Hotkeys', 'hold_duration'))
        except (configparser.NoOptionError, ValueError):
            # Return default if not set or invalid
            return self.DEFAULT_HOLD_DURATION
    
    def set_hold_duration(self, duration):
        """
        Set the hold duration in seconds
        
        Args:
            duration (float): Hold duration in seconds
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.config.set('Hotkeys', 'hold_duration', str(duration))
            return self.save_config()
        except Exception:
            return False
    
    def is_enabled(self):
        """Check if hotkeys are enabled"""
        try:
            return self.config.get('Hotkeys', 'enabled').lower() == 'true'
        except configparser.NoOptionError:
            # Return default if not set
            return True
    
    def set_enabled(self, enabled):
        """
        Enable or disable hotkeys
        
        Args:
            enabled (bool): True to enable, False to disable
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.config.set('Hotkeys', 'enabled', 'true' if enabled else 'false')
            return self.save_config()
        except Exception:
            return False
    
    def get_activation_key(self):
        """
        Get the current activation key based on the current minute's ones digit
        
        Returns:
            str: The key as a string ('0'-'9')
        """
        current_minute = datetime.now().minute
        ones_digit = current_minute % 10
        return str(ones_digit)