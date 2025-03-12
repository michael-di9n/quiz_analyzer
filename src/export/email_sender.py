import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from dotenv import load_dotenv

class EmailSender:
    """Class for sending emails with quiz answers"""
    
    def __init__(self, sender_email=None, app_password=None):
        """
        Initialize the EmailSender with Gmail credentials
        
        Args:
            sender_email (str, optional): Gmail address to send from
                                         If not provided, will look for EMAIL_ADDRESS env variable
            app_password (str, optional): Gmail app password 
                                         If not provided, will look for EMAIL_APP_PASSWORD env variable
        """
        # Load environment variables
        load_dotenv()
        
        # Get email credentials from parameters or environment variables
        self.sender_email = sender_email or os.getenv("EMAIL_ADDRESS")
        self.app_password = app_password or os.getenv("EMAIL_APP_PASSWORD")
        
        # Validate credentials
        if not self.sender_email:
            raise ValueError("Sender email is required. Please provide it or set EMAIL_ADDRESS environment variable.")
        
        if not self.app_password:
            raise ValueError("App password is required. Please provide it or set EMAIL_APP_PASSWORD environment variable.")
    
    def send_quiz_answer(self, recipient_email, question_text, answer_text, 
                        subject="Quiz Answer from Claude", image_data=None):
        """
        Send an email with quiz question and Claude's answer
        
        Args:
            recipient_email (str): Email address to send to
            question_text (str): The quiz question
            answer_text (str): Claude's answer to the question
            subject (str, optional): Email subject line
            image_data (bytes, optional): Screenshot image data to attach
            
        Returns:
            bool: True if email was sent successfully, False otherwise
            str: Success message or error description
        """
        try:
            # Create message
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = recipient_email
            message["Subject"] = subject
            
            # Create the email body with HTML formatting
            html_content = f"""
            <html>
            <body>
                <h2>Quiz Question</h2>
                <p>{question_text}</p>
                
                <h2>Claude's Answer</h2>
                <p>{answer_text}</p>
                
                <hr>
                <p><em>Sent from Quiz Analyzer Application</em></p>
            </body>
            </html>
            """
            
            # Attach the HTML content
            message.attach(MIMEText(html_content, "html"))
            
            # Attach the screenshot if provided
            if image_data:
                image = MIMEImage(image_data)
                image.add_header("Content-Disposition", "attachment", filename="screenshot.png")
                message.attach(image)
            
            # Connect to Gmail's SMTP server
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                # Login to the account
                server.login(self.sender_email, self.app_password)
                
                # Send the email
                server.send_message(message)
            
            return True, "Email sent successfully to " + recipient_email
            
        except smtplib.SMTPAuthenticationError:
            return False, "Authentication failed. Please check your email and app password."
        except smtplib.SMTPException as e:
            return False, f"SMTP error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

# Simple test function to verify the module works
def test_email_sender():
    """
    Test the EmailSender class with sample data
    This function can be called directly to test the module
    
    Example:
        # Set your test email address
        recipient = "test@example.com"
        
        # Run the test
        test_email_sender(recipient)
    """
    try:
        # Create the sender
        sender = EmailSender()
        
        # Sample data
        recipient = input("Enter recipient email for test: ")
        question = "What is the capital of France?"
        answer = "The capital of France is Paris."
        
        # Send a test email
        success, message = sender.send_quiz_answer(recipient, question, answer)
        
        # Print result
        print(f"Result: {'Success' if success else 'Failed'}")
        print(f"Message: {message}")
        
        return success
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    # If this file is run directly, perform a test
    test_email_sender()