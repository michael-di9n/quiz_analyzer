# Quiz Analyzer Application Documentation

## Project Overview

The Quiz Analyzer is a Windows desktop application designed to test AI capabilities in answering quiz questions. It allows users to capture screenshots containing quiz questions, extract the text using OCR, send the questions to Claude API, and display the AI's answers.

## Target Users
- Programmers
- AI hobbyists

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
│   │   └── app_window.py  # Main window implementation
│   ├── capture/
│   │   ├── __init__.py
│   │   └── screen_capture.py  # Screen capture functionality
│   ├── ocr/
│   │   ├── __init__.py
│   │   └── text_extractor.py  # OCR and question extraction
│   └── ai/
│       ├── __init__.py
│       └── claude_client.py   # Claude API integration
└── tests/
    ├── __init__.py
    └── test_*.py         # Test files (to be implemented)
```

## Design Decisions

### Programming Language Selection
- **Python** was chosen over JavaScript and C# for several reasons:
  - Excellent libraries for image processing (OpenCV, Tesseract OCR)
  - Strong capabilities for AI/ML tasks
  - Easy API integration with Claude
  - Supports rapid desktop application development with PyQt
  - Widely used in the AI community, making it accessible to the target audience

### Architecture
- The application follows SOLID principles and is structured with clear separation of concerns:
  - Each component (GUI, Capture, OCR, AI) is isolated in its own module
  - Each class has a single responsibility
  - Dependencies are managed through proper initialization

### GUI Layout
- Designed with a workflow-oriented approach:
  - Three main sections corresponding to the workflow steps (Capture → Extract → Analyze)
  - Each section has a clear header and relevant controls
  - Preview area for visual feedback of captured screenshots
  - Progress indicator for API calls
  - Sections can be resized with appropriate priority

### Screen Capture Implementation
- Full-screen capture using PIL's ImageGrab
- Images can be converted between different formats (PIL, OpenCV, QPixmap)
- Preview is scaled down for display while maintaining the original resolution for processing

### OCR Implementation
- Tesseract OCR with preprocessing for improved text recognition
- Automatic detection of multiple-choice vs. short-answer questions
- Text parsing to separate question text from answer choices
- Handling of Windows-specific Tesseract path requirements

### Claude API Integration
- Environment variables for secure API key storage
- Appropriate system prompts based on question type
- Error handling and timeout management
- Asynchronous processing to prevent UI freezing during API calls

## Setup Requirements

### Dependencies
- Python 3.8+ environment
- PyQt6 for the GUI
- Pillow and OpenCV for image processing
- pytesseract for OCR (requires Tesseract installation)
- anthropic Python package for Claude API access
- python-dotenv for environment variable management

### External Requirements
1. **Tesseract OCR**: Must be installed separately on the system
   - Default path on Windows: `B:\Program Files\Tesseract-OCR\tesseract.exe`
   - Path can be specified in the .env file or through a dialog prompt

2. **Claude API Key**: Required for AI integration
   - Must be added to the .env file as ANTHROPIC_API_KEY
   - Can be obtained from https://console.anthropic.com/

## Usage Workflow

1. **Setup**: 
   - Create a virtual environment on the B drive
   - Install dependencies from requirements.txt
   - Configure .env file with API key and Tesseract path

2. **Running the Application**:
   - Activate the virtual environment
   - Run `python src/main.py`

3. **Using the Application**:
   - Click "Capture Screen" to take a screenshot
   - The application extracts text using OCR and identifies question type
   - Verify and edit the extracted text if needed
   - Click "Send to Claude" to submit the question
   - View Claude's answer in the response area

## Future Enhancements (Considered but Not Implemented)

1. **OCR Improvements**:
   - Region of Interest (ROI) detection for focusing on question areas
   - Template matching for consistent quiz formats
   - Semantic segmentation to identify question components
   - Text layout analysis for better question structure recognition

2. **Additional Features**:
   - Selective screen region capture
   - History of previous questions and answers
   - Export/import of Q&A sessions
   - Multiple AI service integration (e.g., ChatGPT alongside Claude)
   - Visual highlighting of answers in multiple-choice questions

## Development Principles
- **SOLID**: Single responsibility, Open-closed, Liskov substitution, Interface segregation, Dependency inversion
- **DRY**: Don't Repeat Yourself
- **YAGNI**: You Aren't Gonna Need It
- **KISS**: Keep It Simple, Stupid
- **OOP**: Object-Oriented Programming
