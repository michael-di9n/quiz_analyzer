from PyQt6.QtCore import QObject, QTimer
from hotkey.hotkey_service import HotkeyService
from gui.hotkey_menu import HotkeySettingsDialog

class HotkeyManager(QObject):
    """Manages hotkey functionality and integration with the main application"""
    
    def __init__(self, main_window):
        """
        Initialize the hotkey manager
        
        Args:
            main_window: Reference to the MainWindow for integration
        """
        super().__init__()
        self.main_window = main_window
        
        # Initialize the hotkey service
        self.hotkey_service = HotkeyService(main_window)
        
        # Flag to track if a sequence is already in progress
        self.sequence_in_progress = False
    
    def start(self):
        """Start the hotkey service"""
        self.hotkey_service.start()
    
    def stop(self):
        """Stop the hotkey service"""
        self.hotkey_service.stop()
    
    def connect_signals(self, capture_panel, question_panel, response_panel):
        """
        Connect completion signals to sequence handlers
        
        Args:
            capture_panel: The capture panel component
            question_panel: The question panel component
            response_panel: The response panel component
        """
        # Store references
        self.capture_panel = capture_panel
        self.question_panel = question_panel
        self.response_panel = response_panel
        
        # Connect signals
        self.capture_panel.capture_completed.connect(self.on_capture_completed)
        self.response_panel.claude_completed.connect(self.on_claude_completed)
        self.response_panel.email_completed.connect(self.on_email_completed)
    
    def show_settings_dialog(self):
        """Show the hotkey settings dialog"""
        dialog = HotkeySettingsDialog(self.main_window)
        dialog.exec()
    
    def trigger_action_sequence(self):
        """Trigger the sequence of actions in the main window"""
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
        success = self.capture_panel.capture_screen(emit_signal=True)
        
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
        
        # Process the captured image to extract text
        image = self.capture_panel.get_captured_image()
        text_success = self.question_panel.process_image(image)
        
        if not text_success:
            print("OCR text extraction failed")
            self.sequence_in_progress = False
            return
        
        # Move to next step - send to Claude
        # Use a small delay to allow UI to update
        QTimer.singleShot(100, self.start_claude_analysis)
    
    def start_claude_analysis(self):
        """Start the Claude analysis process"""
        print("Starting Claude analysis...")
        
        # Get question text and type
        question_text = self.question_panel.get_question_text()
        question_type = "multiple_choice" if self.question_panel.is_multiple_choice() else "short_answer"
        
        # Call send_to_claude with emit_signal=True
        success = self.response_panel.send_to_claude(question_text, question_type, emit_signal=True)
        
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
        
        # Get question text, answer text, and image
        question_text = self.question_panel.get_question_text()
        answer_text = self.response_panel.get_response_text()
        image_data = None
        
        # Get the screenshot image if available
        if self.capture_panel.get_captured_pil_image():
            # Convert the PIL image to bytes
            import io
            img_byte_arr = io.BytesIO()
            self.capture_panel.get_captured_pil_image().save(img_byte_arr, format='PNG')
            image_data = img_byte_arr.getvalue()
        
        # Call send_by_email with show_dialog=False and emit_signal=True
        success = self.response_panel.send_by_email(
            question_text=question_text,
            answer_text=answer_text,
            image_data=image_data,
            show_dialog=False, 
            emit_signal=True
        )
        
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