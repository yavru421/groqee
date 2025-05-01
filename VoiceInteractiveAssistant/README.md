# Groqee - Voice Interactive Assistant

A voice-first AutoHotkey v2 application that integrates Python for speech recognition and emotional intelligence.

## Features

- **Voice Interactions**: Responds to voice commands and speaks responses
- **Emotional Intelligence**: Groqee has emotional states that change based on interactions
- **GUI Interface**: Visual representation of Groqee with emotional indicators
- **AutoHotkey v2 Integration**: Hotkeys to control the application with modern AHK syntax

## Requirements

- Windows OS
- Python 3.6+
- AutoHotkey v2
- Python packages:
  - tkinter (usually comes with Python)
  - speech_recognition
  - pyttsx3

## Installation

1. Install Python packages:
```
pip install SpeechRecognition pyttsx3
```

2. Make sure AutoHotkey v2 is installed on your system
   - Download from: https://www.autohotkey.com/v2/

## Usage

1. Run the AutoHotkey v2 script `Groqee_v2.ahk` in the `ahk` folder
2. The application will automatically start and show the Groqee interface
3. Use the following hotkeys:
   - Ctrl+Alt+E: Toggle Groqee's visibility
   - Ctrl+Alt+S: Start voice recognition
   - Ctrl+Alt+X: Exit the application

## Conversation Features

Groqee can:
- Respond to greetings and farewells
- Tell jokes, provide the time/date
- Express different emotional states based on interactions
- Remember conversation history

## Project Structure

```
VoiceInteractiveAssistant/
    GroqeeApp/
        ahk/
            Groqee_v2.ahk        # AutoHotkey v2 script for controlling Groqee
            Groqee.ahk           # Legacy AutoHotkey v1 script (for compatibility)
        python/
            groqee.py            # Main Python application with GUI
            conversation_flow.py  # Conversation and emotional intelligence
            responses.json        # Created automatically with default responses
```

## How It Works

1. The AutoHotkey v2 script serves as the launcher and controller
2. The Python application provides the GUI and handles voice interactions
3. The conversation manager keeps track of Groqee's emotional state and responses
4. Communication between AutoHotkey and Python uses a robust file-based protocol with response verification

## Communication Protocol

The system uses a simple but robust file-based communication protocol:
1. AutoHotkey writes commands to `command.txt`
2. Python reads the command and processes it
3. Python writes acknowledgment to `response.txt`
4. AutoHotkey checks for a response and handles success/failure

## Extending Groqee

You can extend Groqee's capabilities by:
- Adding more responses in the `responses.json` file
- Implementing more advanced NLP for better conversation flow
- Adding more complex emotional states and needs
- Integrating with other systems and services

## License

This project is provided as-is with no warranties.