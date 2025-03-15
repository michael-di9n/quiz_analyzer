
# Project setup
1.Settings Up the Virtual Env
`python -m venv venv_quiz`
`.\venv_quiz\Scripts\activate`

2. Install requirement
`pip install -r requirements.txt`

3. Create an .env file with the following parameters
see sample.env
Currently only works with simple questions - multiple choice and no coding questions

Project Information:
# Quiz Analyzer

## Overview
Quiz Analyzer is a Windows desktop application designed to test AI capabilities in answering quiz questions. The application captures screenshots containing quiz questions, extracts text using OCR, sends questions to the Claude API, and displays AI answers. It's primarily designed for programmers and AI hobbyists who want to evaluate AI performance on quizzes.

## Technology Stack
- **Programming Language**: Python
- **GUI Framework**: PyQt6
- **OCR Engine**: Tesseract (via pytesseract)
- **Image Processing**: OpenCV, PIL
- **AI Integration**: Claude API (via anthropic package)
- **Environment Management**: python-dotenv

## Project Structure
```
quiz_analyzer/
├── requirements.txt
├── README.md
├── .env.example
├── .env                 # Contains API keys (not in version control)
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── main.py          # Application entry point
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── app_window.py    # Main window implementation
│   │   ├── email_dialog.py  # Email configuration dialog
│   │   ├── hotkey_menu.py   # Hotkey settings dialog
│   │   └── recipient_manager.py # Email recipient management
│   ├── capture/
│   │   ├── __init__.py
│   │   └── screen_capture.py  # Screen capture functionality
│   ├── ocr/
│   │   ├── __init__.py
│   │   └── text_extractor.py  # OCR and question extraction
│   ├── ai/
│   │   ├── __init__.py
│   │   └── claude_client.py   # Claude API integration
│   └── hotkey/
│       ├── __init__.py
│       ├── hotkey_config.py   # Configuration for hotkeys
│       └── hotkey_service.py  # Hotkey detection service
└── tests/
    ├── __init__.py
    └── test_*.py         # Test files
```

## Core Components

### Main Application (main.py)
The application entry point initializes the main window and starts the PyQt application loop. It's a simple file that creates the application instance and shows the main window.

### Main Window (app_window.py)
The central UI component of the application implementing the main window with three main sections:
1. **Capture Section**: Contains controls for taking screenshots
2. **Question Section**: Displays and allows editing of extracted text
3. **AI Response Section**: Displays Claude's answer and provides email functionality

Key features:
- System tray integration for background operation
- Hotkey service integration for automated capture and analysis
- Progress indicators for API calls
- Email integration for sharing results

### Screen Capture (screen_capture.py)
Handles capturing screenshots of the entire screen or specific regions:
- Uses PIL's ImageGrab for screen capture
- Converts images between different formats (PIL, OpenCV, QPixmap)
- Scales images for preview while maintaining original resolution

Methods:
- `capture_screen()`: Captures the entire screen
- `capture_region(x, y, width, height)`: Captures a specific region
- `get_qt_pixmap(max_width, max_height)`: Converts captured image to QPixmap for display

### Text Extractor (text_extractor.py)
Handles OCR and text processing:
- Uses pytesseract (wrapper for Tesseract OCR)
- Preprocesses images to improve OCR accuracy
- Identifies question types (multiple-choice vs. short-answer)
- Parses questions to separate text from answer choices

Key methods:
- `preprocess_image(image)`: Improves image quality for OCR
- `extract_text(image)`: Extracts text from an image
- `is_multiple_choice(text)`: Determines if text is a multiple-choice question
- `parse_question(text)`: Separates question text from answer choices

### Claude Client (claude_client.py)
Integrates with Claude API to get answers:
- Uses anthropic Python package
- Handles API authentication via environment variables
- Creates appropriate system prompts based on question type
- Implements error handling and timeout management

Key methods:
- `ask_question(question_text, question_type, max_tokens, timeout)`: Sends a question to Claude and returns the answer

### Email Functionality
Two main components handle email functionality:

#### Email Dialog (email_dialog.py)
Provides UI for sending emails:
- Recipient management with validation
- Subject field configuration
- Progress indication for sending

#### Recipient Manager (recipient_manager.py)
Manages email recipients:
- Stores recipients in a text file
- Validates email addresses
- Tracks checked status for bulk sending

### Hotkey System
Enables automated operation through keyboard shortcuts:

#### Hotkey Config (hotkey_config.py)
Manages hotkey settings:
- Stores configuration in an INI file
- Manages hold duration and enabled status
- Provides dynamic activation key based on time

#### Hotkey Service (hotkey_service.py)
Detects and processes hotkey presses:
- Listens for specific key combinations
- Triggers application actions when hotkeys are detected
- Works in the background even when the app is minimized

## Workflow

### Setup
1. Create a virtual environment
2. Install dependencies from requirements.txt
3. Create .env file with:
   - ANTHROPIC_API_KEY for Claude API
   - TESSERACT_PATH for OCR (Windows)
   - Email configuration if needed

### Basic Usage
1. Launch the application (`python src/main.py`)
2. Click "Capture Screen" to take a screenshot
3. The application extracts text using OCR and identifies question type
4. Verify and edit the extracted text if needed
5. Click "Send to Claude" to submit the question
6. View Claude's answer in the response area
7. Optionally send the answer via email

### Automated Usage
The application supports automated operation through hotkeys:
1. Press and hold the digit that matches the current minute's ones digit
   (e.g., if the time is 10:23, hold "3")
2. The application automatically captures the screen, extracts text, 
   sends to Claude, and emails results

### System Tray Integration
The application runs in the system tray:
- Minimize to tray by closing the window
- Double-click tray icon to show the window
- Right-click for menu options (Show, Hide, Settings, Quit)

## Implementation Details

### OCR Implementation
- Tesseract OCR with preprocessing for improved text recognition
- Converts to grayscale and applies thresholding for better results
- Uses pattern recognition to identify multiple-choice questions
- Simple parsing to separate question text from answer choices

### Claude API Integration
- Uses Claude 3 Opus model for highest accuracy
- Tailors system prompts based on question type:
  - Multiple-choice: Instructs to identify the correct option (A, B, C, D)
  - Short-answer: Requests concise but thorough answers
- Implements timeout and error handling
- Processes responses asynchronously to prevent UI freezing

### Email Implementation
- Stores recipients in a text file for persistence
- Validates email addresses with regex
- Supports attaching screenshots with emails
- Provides both manual and automated sending modes

### Hotkey Implementation
- Global keyboard monitoring with pynput
- Dynamic key activation based on current time
- Configurable hold duration (default: 2 seconds)
- Triggers sequence of actions via QTimer to maintain UI responsiveness

## Architecture Principles

The application follows key software design principles:

### SOLID
- **Single Responsibility**: Each class has one job (capture, OCR, API, etc.)
- **Open/Closed**: Components can be extended without modification
- **Liskov Substitution**: Derived classes can substitute base classes
- **Interface Segregation**: Classes expose only necessary methods
- **Dependency Inversion**: High-level modules don't depend on low-level details

### DRY (Don't Repeat Yourself)
- Common operations are abstracted into reusable methods
- Configuration is centralized in .env and config files

### YAGNI (You Aren't Gonna Need It)
- Features are implemented only when needed
- Optional features (like email) degrade gracefully when not configured

### KISS (Keep It Simple, Stupid)
- Straightforward workflow with clear steps
- Simple UI with three main sections
- Minimal configuration required

### OOP (Object-Oriented Programming)
- Clear class hierarchies and encapsulation
- Each component is a self-contained class
- Properties and methods have appropriate access modifiers

## Troubleshooting

### Common Issues
1. **Missing Tesseract**: Ensure Tesseract OCR is installed and path is correct in .env
2. **API Key Issues**: Verify ANTHROPIC_API_KEY is correctly set in .env
3. **OCR Quality**: Adjust screen brightness/contrast for better results
4. **Email Configuration**: Check email credentials if sending fails

### Debug Tips
- Check console output for error messages
- Verify file paths in error messages
- Test components individually if full workflow fails

## Future Enhancements

1. **OCR Improvements**:
   - ROI detection for focusing on question areas
   - Template matching for consistent quiz formats
   - Semantic segmentation to identify question components

2. **Additional Features**:
   - Selective screen region capture
   - History of previous questions and answers
   - Export/import of Q&A sessions
   - Integration with other AI services