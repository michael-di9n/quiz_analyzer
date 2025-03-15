import os
import re

class Recipient:
    """Class to represent an email recipient"""
    
    def __init__(self, name, email, checked=False):
        self.name = name
        self.email = email
        self.checked = checked
        self.valid = self._validate_email()
    
    def _validate_email(self):
        """Validate the email address using a simple regex pattern"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, self.email))
    
    def to_line(self):
        """Convert recipient to a line for the recipients.txt file"""
        checked_str = "true" if self.checked else "false"
        return f"{self.name},{self.email},{checked_str}"
    
    @classmethod
    def from_line(cls, line):
        """Create a Recipient object from a line in the recipients.txt file"""
        try:
            # Split the line by commas
            parts = line.strip().split(',', 2)
            
            # Make sure we have at least name and email
            if len(parts) < 2:
                return None
                
            name = parts[0]
            email = parts[1]
            
            # Get checked status if available, default to False
            checked = False
            if len(parts) >= 3:
                checked = parts[2].lower() == "true"
                
            return cls(name, email, checked)
            
        except Exception:
            # Return None if there's any issue parsing the line
            return None


class RecipientManager:
    """Class to manage email recipients"""
    
    def __init__(self, file_path=None):
        """
        Initialize the RecipientManager
        
        Args:
            file_path (str, optional): Path to the recipients.txt file
                                      If not provided, will use default path
        """
        # Set default path if not provided
        if file_path is None:
            # Determine the path to the gui directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.file_path = os.path.join(current_dir, "recipients.txt")
        else:
            self.file_path = file_path
            
        # List to store recipients
        self.recipients = []
        
        # Load recipients from file
        self.load_recipients()
    
    def load_recipients(self):
        """Load recipients from the recipients.txt file"""
        self.recipients = []
        
        try:
            # Check if the file exists
            if not os.path.exists(self.file_path):
                # Create an empty file if it doesn't exist
                with open(self.file_path, 'w') as f:
                    pass
                return
                
            # Read the file
            with open(self.file_path, 'r') as f:
                lines = f.readlines()
                
            # Parse each line
            for line in lines:
                recipient = Recipient.from_line(line)
                if recipient:
                    self.recipients.append(recipient)
                    
        except Exception as e:
            print(f"Error loading recipients: {str(e)}")
    
    def save_recipients(self):
        """Save recipients to the recipients.txt file"""
        try:
            with open(self.file_path, 'w') as f:
                for recipient in self.recipients:
                    f.write(recipient.to_line() + '\n')
                    
            return True
            
        except Exception as e:
            print(f"Error saving recipients: {str(e)}")
            return False
    
    def add_recipient(self, name, email, checked=False):
        """Add a new recipient"""
        # Check if the email already exists
        for r in self.recipients:
            if r.email == email:
                # Update existing recipient
                r.name = name
                r.checked = checked
                r.valid = r._validate_email()  # Revalidate
                return r
                
        # Create new recipient
        recipient = Recipient(name, email, checked)
        self.recipients.append(recipient)
        
        # Save changes
        self.save_recipients()
        
        return recipient
    
    def update_recipient_status(self, email, checked):
        """Update the checked status of a recipient"""
        for r in self.recipients:
            if r.email == email:
                r.checked = checked
                self.save_recipients()
                return True
                
        return False
    
    def get_recipients(self):
        """Get all recipients"""
        return self.recipients
    
    def get_checked_recipients(self):
        """Get only checked recipients with valid emails"""
        return [r for r in self.recipients if r.checked and r.valid]