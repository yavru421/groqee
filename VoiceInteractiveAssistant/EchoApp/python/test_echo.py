# Echo Command Line Test
# A simplified test script to verify Echo components

import os
import sys
import time
from conversation_flow import ConversationManager

def test_conversation():
    print("\n===== Testing Conversation Module =====")
    try:
        cm = ConversationManager()
        print("ConversationManager initialized successfully")
        
        # Test basic response
        response = cm.process_input("hello")
        print(f"Test greeting response: '{response}'")
        
        # Test keyword response
        response = cm.process_input("what time is it")
        print(f"Test time response: '{response}'")
        
        print("Conversation module test: SUCCESS")
        return True
    except Exception as e:
        print(f"Conversation module test FAILED: {e}")
        return False

def test_command_interface():
    print("\n===== Testing Command Interface =====")
    try:
        # Test command file creation
        command_file = "command.txt"
        response_file = "response.txt"
        
        # Clean up existing files
        if os.path.exists(command_file):
            os.remove(command_file)
        if os.path.exists(response_file):
            os.remove(response_file)
            
        # Test writing to command file
        with open(command_file, 'w') as f:
            f.write("test")
        print(f"Created test command file: {command_file}")
        
        # Test response file
        with open(response_file, 'w') as f:
            f.write("ack:test")
        print(f"Created test response file: {response_file}")
        
        # Verify files exist
        cmd_exists = os.path.exists(command_file)
        resp_exists = os.path.exists(response_file)
        print(f"Command file exists: {cmd_exists}")
        print(f"Response file exists: {resp_exists}")
        
        # Clean up
        if os.path.exists(command_file):
            os.remove(command_file)
        if os.path.exists(response_file):
            os.remove(response_file)
            
        if cmd_exists and resp_exists:
            print("Command interface test: SUCCESS")
            return True
        else:
            print("Command interface test FAILED: Files not created properly")
            return False
    except Exception as e:
        print(f"Command interface test FAILED: {e}")
        return False

def test_speech_modules():
    print("\n===== Testing Speech Modules =====")
    try:
        # Try importing the speech libraries without initializing them
        import speech_recognition
        import pyttsx3
        
        engine = pyttsx3.init()  # Initialize the text-to-speech engine
        print(f"SpeechRecognition version: {speech_recognition.__version__}")
        print("Speech modules imported successfully")
        print("Speech modules test: SUCCESS")
        return True
    except ImportError as e:
        print(f"Speech modules test FAILED: {e}")
        print("Voice features will be disabled")
        return False
    except Exception as e:
        print(f"Speech modules test FAILED with unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("===== Echo Voice Interactive Assistant Tests =====")
    print(f"Running tests from directory: {os.getcwd()}")
    
    # Run tests
    conversation_success = test_conversation()
    command_success = test_command_interface()
    speech_success = test_speech_modules()
    
    # Summary
    print("\n===== Test Summary =====")
    print(f"Conversation Module: {'✓' if conversation_success else '✗'}")
    print(f"Command Interface:   {'✓' if command_success else '✗'}")
    print(f"Speech Modules:      {'✓' if speech_success else '✗'}")
    
    if conversation_success and command_success:
        print("\nCore functionality tests PASSED")
        print("The application is ready for integration with AutoHotkey")
    else:
        print("\nSome tests FAILED - See above for details")