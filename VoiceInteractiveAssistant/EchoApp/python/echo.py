# Groqee - Voice Interactive Assistant
# Main Python application for the Groqee virtual companion

import tkinter as tk
from tkinter import ttk
import os
import sys
import threading
import time
import queue
import json
import pygame
from conversation_flow import ConversationManager
import keyboard  # Added for global hotkeys
import argparse  # Added for command-line arguments

# Try to import speech recognition libraries
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    print("Speech recognition library not available. Voice input will be disabled.")
    SPEECH_RECOGNITION_AVAILABLE = False

# Initialize pygame for audio playback
pygame.mixer.init()

# Define speech availability - we'll use Groq's TTS API as primary and fall back to pyttsx3 if needed
SPEECH_AVAILABLE = True
USE_GROQ_TTS = True

# Try to import pyttsx3 as fallback
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    print("pyttsx3 not available. Will use only Groq TTS if available.")
    PYTTSX3_AVAILABLE = False

class GroqeeApp:
    def __init__(self, root, persona_name="Default"):  # Added persona_name argument
        self.root = root
        self.root.title("Groqee - Virtual Companion")
        self.root.geometry("500x700")  # Larger window for better readability
        
        # Modern color scheme
        self.colors = {
            'bg': '#1E1E2E',  # Dark background
            'accent': '#89B4FA',  # Soft blue accent
            'text': '#CDD6F4',  # Light text
            'secondary': '#45475A',  # Secondary background
            'highlight': '#F5C2E7',  # Highlight color
            'avatar_bg': '#313244'  # Avatar background
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        # Configure styles
        style = ttk.Style()
        style.configure('Modern.TFrame', background=self.colors['bg'])
        style.configure('Modern.TLabel', background=self.colors['bg'], foreground=self.colors['text'])
        style.configure('Modern.TLabelframe', background=self.colors['bg'], foreground=self.colors['text'])
        style.configure('Modern.TLabelframe.Label', background=self.colors['bg'], foreground=self.colors['text'])
        style.configure('Modern.TButton', background=self.colors['accent'], foreground=self.colors['text'], padding=5)
        style.configure('Modern.Horizontal.TProgressbar', background=self.colors['accent'], troughcolor=self.colors['secondary'])
        
        # Initialize components
        self.setup_gui()
        
        # Status label
        self.status_var = tk.StringVar(value="Status: Initializing...")  # Added status
        self.status_label = ttk.Label(self.main_frame, textvariable=self.status_var, style='Modern.TLabel')
        self.status_label.pack(pady=(5, 0))  # Added status label packing

        # Initialize speech components if available
        if SPEECH_AVAILABLE:
            self.setup_voice()
        
        # Initialize conversation manager with the selected persona
        self.conversation = ConversationManager(persona_name=persona_name)  # Pass persona_name
        
        # Start threads
        self.running = True
        
        self.update_thread = threading.Thread(target=self.periodic_updates)  # Renamed and repurposed thread
        self.update_thread.daemon = True
        self.update_thread.start()

        # Setup global hotkeys
        self.setup_hotkeys()
        
        # Initial greeting
        initial_greeting = "Hello there! I'm Groqee, ready to assist with my advanced cognitive abilities. What's on your mind?"
        self.add_to_conversation("Groqee", initial_greeting)
        if SPEECH_AVAILABLE:
            self.speak(initial_greeting)  # Speak the professional greeting
            
        self.status_var.set("Status: Idle")  # Set status after init

    def setup_gui(self):
        # Main frame
        self.main_frame = ttk.Frame(self.root, style='Modern.TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Groqee's face/avatar
        self.canvas = tk.Canvas(self.main_frame, width=200, height=200, bg=self.colors['avatar_bg'])
        self.canvas.pack(pady=10)
        self.draw_face("neutral")
        
        # Emotional state display
        self.emotion_frame = ttk.LabelFrame(self.main_frame, text="Emotional State", style='Modern.TLabelframe')
        self.emotion_frame.pack(fill=tk.X, pady=10)
        
        self.happiness_var = tk.DoubleVar(value=50)
        self.energy_var = tk.DoubleVar(value=50)
        
        ttk.Label(self.emotion_frame, text="Happiness:", style='Modern.TLabel').grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Progressbar(self.emotion_frame, orient=tk.HORIZONTAL, length=200, variable=self.happiness_var, style='Modern.Horizontal.TProgressbar').grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.emotion_frame, text="Energy:", style='Modern.TLabel').grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Progressbar(self.emotion_frame, orient=tk.HORIZONTAL, length=200, variable=self.energy_var, style='Modern.Horizontal.TProgressbar').grid(row=1, column=1, padx=5, pady=5)
        
        # API and TTS usage display
        self.usage_frame = ttk.LabelFrame(self.main_frame, text="API & TTS Usage", style='Modern.TLabelframe')
        self.usage_frame.pack(fill=tk.X, pady=10)

        self.api_usage_var = tk.IntVar(value=0)
        self.tts_usage_var = tk.IntVar(value=0)

        ttk.Label(self.usage_frame, text="API Calls:", style='Modern.TLabel').grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Progressbar(self.usage_frame, orient=tk.HORIZONTAL, length=200, variable=self.api_usage_var, style='Modern.Horizontal.TProgressbar').grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.usage_frame, text="TTS Usage:", style='Modern.TLabel').grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Progressbar(self.usage_frame, orient=tk.HORIZONTAL, length=200, variable=self.tts_usage_var, style='Modern.Horizontal.TProgressbar').grid(row=1, column=1, padx=5, pady=5)
        
        # Conversation display
        self.conversation_frame = ttk.LabelFrame(self.main_frame, text="Conversation", style='Modern.TLabelframe')
        self.conversation_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.conversation_text = tk.Text(self.conversation_frame, wrap=tk.WORD, height=10, bg=self.colors['secondary'], fg=self.colors['text'])
        self.conversation_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.conversation_text.config(state=tk.DISABLED)
        
        # User input
        self.input_frame = ttk.Frame(self.main_frame, style='Modern.TFrame')
        self.input_frame.pack(fill=tk.X, pady=10)
        
        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(self.input_frame, textvariable=self.input_var)
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.send_button = ttk.Button(self.input_frame, text="Send", command=self.send_message, style='Modern.TButton')
        self.send_button.pack(side=tk.LEFT)
        
        if SPEECH_AVAILABLE:
            self.voice_button = ttk.Button(self.input_frame, text="Listen", width=6, command=self.toggle_listening, style='Modern.TButton')  # Changed text from emoji to "Listen"
            self.voice_button.pack(side=tk.LEFT, padx=5)
        
        # Add a skip button to the GUI
        self.skip_button = ttk.Button(self.input_frame, text="Skip", command=self.skip_response, style='Modern.TButton')
        self.skip_button.pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key to send message
        self.input_entry.bind("<Return>", lambda event: self.send_message())

    def update_usage_display(self, api_calls, tts_usage):
        """Update the API and TTS usage meters."""
        self.api_usage_var.set(api_calls)
        self.tts_usage_var.set(tts_usage)
        
    def setup_voice(self):
        if not SPEECH_RECOGNITION_AVAILABLE:
            return
            
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        try:
            self.microphone = sr.Microphone()
            
            # Initialize fallback text-to-speech if needed
            if PYTTSX3_AVAILABLE:
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', 150)  # Speed of speech

                # Select a male voice as fallback
                for voice in self.engine.getProperty('voices'):
                    if 'male' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
            
            # Voice state
            self.listening = False
            self.listen_thread = None
            self.current_audio = None
        except Exception as e:
            print(f"Error setting up voice: {e}")
            self._speech_available = False

    def setup_hotkeys(self):
        """Sets up global hotkeys using the keyboard library."""
        try:
            # Use lambda and root.after to ensure thread safety with Tkinter
            keyboard.add_hotkey('ctrl+alt+s', lambda: self.root.after(0, self.toggle_listening), trigger_on_release=True)
            keyboard.add_hotkey('ctrl+alt+x', lambda: self.root.after(0, self.close_app), trigger_on_release=True)
            print("Global hotkeys registered: Ctrl+Alt+S (Listen), Ctrl+Alt+X (Exit)")
            self.status_var.set("Status: Idle (Hotkeys Active)")
        except Exception as e:
            error_msg = f"Hotkey registration failed: {e}. Try running as administrator."
            print(error_msg)
            self.status_var.set(f"Status: {error_msg}")

    def draw_face(self, emotion="neutral"):
        self.canvas.delete("all")
        
        # Draw face based on emotion
        if emotion == "happy":
            # Happy face
            self.canvas.create_oval(50, 50, 150, 150, fill="yellow", outline="black")
            self.canvas.create_oval(75, 80, 85, 90, fill="black")  # Left eye
            self.canvas.create_oval(115, 80, 125, 90, fill="black")  # Right eye
            self.canvas.create_arc(70, 70, 130, 130, start=0, extent=-180, style=tk.ARC, width=2)  # Smile
        elif emotion == "sad":
            # Sad face
            self.canvas.create_oval(50, 50, 150, 150, fill="yellow", outline="black")
            self.canvas.create_oval(75, 80, 85, 90, fill="black")  # Left eye
            self.canvas.create_oval(115, 80, 125, 90, fill="black")  # Right eye
            self.canvas.create_arc(70, 100, 130, 160, start=0, extent=180, style=tk.ARC, width=2)  # Frown
        else:  # neutral
            # Neutral face
            self.canvas.create_oval(50, 50, 150, 150, fill="yellow", outline="black")
            self.canvas.create_oval(75, 80, 85, 90, fill="black")  # Left eye
            self.canvas.create_oval(115, 80, 125, 90, fill="black")  # Right eye
            self.canvas.create_line(70, 110, 130, 110, width=2)  # Neutral mouth
    
    def update_emotion_display(self):
        # Update emotion values from conversation manager's memory
        if hasattr(self.conversation, 'memory') and 'emotional_state' in self.conversation.memory:
            happiness = self.conversation.memory['emotional_state'].get('happiness', 50.0)
            energy = self.conversation.memory['emotional_state'].get('energy', 50.0)
        else:
            happiness = 50.0
            energy = 50.0

        self.happiness_var.set(happiness)
        self.energy_var.set(energy)

        # Update face based on emotional state
        if happiness > 70:
            self.draw_face("happy")
        elif happiness < 30:
            self.draw_face("sad")
        else:
            self.draw_face("neutral")
    
    def add_to_conversation(self, speaker, text):
        self.conversation_text.config(state=tk.NORMAL)
        self.conversation_text.insert(tk.END, f"{speaker}: {text}\n")
        self.conversation_text.see(tk.END)
        self.conversation_text.config(state=tk.DISABLED)
    
    def send_message(self):
        user_input = self.input_var.get().strip()
        if user_input:
            self.add_to_conversation("You", user_input)
            self.input_var.set("")  # Clear input field
            self.status_var.set("Status: Thinking...")  # Update status
            self.root.update_idletasks()  # Force GUI update

            # Run API call in a separate thread to avoid blocking GUI
            threading.Thread(target=self._process_and_respond, args=(user_input,), daemon=True).start()

    def _process_and_respond(self, user_input):
        """Helper function to process input and update GUI from a thread."""
        try:
            # Get response from conversation manager
            response = self.conversation.process_input(user_input)

            # Update API usage (example: increment by 1 for each call)
            self.root.after(0, self.update_usage_display, self.api_usage_var.get() + 1, self.tts_usage_var.get())

            # Schedule GUI updates back on the main thread
            self.root.after(0, self.add_to_conversation, "Groqee", response)

            # Speak response if voice is available
            if SPEECH_AVAILABLE:
                self.speak(response)
                # Update TTS usage (example: increment by 1 for each TTS call)
                self.root.after(0, self.update_usage_display, self.api_usage_var.get(), self.tts_usage_var.get() + 1)

            # Update emotional display
            self.root.after(0, self.update_emotion_display)
            self.root.after(0, self.status_var.set, "Status: Idle")  # Reset status

        except Exception as e:
            error_message = f"Error processing message: {e}"
            print(error_message)
            self.root.after(0, self.add_to_conversation, "System", error_message)
            self.root.after(0, self.status_var.set, "Status: Error processing message")

    def toggle_listening(self):
        if not SPEECH_RECOGNITION_AVAILABLE:
            self.add_to_conversation("System", "Speech recognition is not available.")
            self.status_var.set("Status: Speech recognition unavailable.")
            return

        if self.listening:
            self.listening = False
            self.voice_button.config(text="Listen")  # Changed text back
            self.status_var.set("Status: Idle")
        else:
            # Stop any current speech playback before listening
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                print("Stopped current playback to listen.")

            self.listening = True
            self.voice_button.config(text="Stop")  # Changed text to indicate listening
            self.status_var.set("Status: Listening...")
            if self.listen_thread is None or not self.listen_thread.is_alive():
                self.listen_thread = threading.Thread(target=self.listen_for_speech)
                self.listen_thread.daemon = True
                self.listen_thread.start()

    def listen_for_speech(self):
        if not SPEECH_RECOGNITION_AVAILABLE:
            return

        with self.microphone as source:
            # Adjust for ambient noise dynamically
            try:
                print("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print(f"Adjusted ambient noise. Energy threshold: {self.recognizer.energy_threshold}")
            except Exception as e:
                print(f"Could not adjust for ambient noise: {e}")

            while self.listening:  # Loop continues as long as self.listening is True
                try:
                    print("Listening...")  # Keep console log
                    # Increased timeout, added phrase_time_limit for longer utterances
                    audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=15)

                    print("Processing speech...")
                    self.root.after(0, self.status_var.set, "Status: Processing speech...")
                    text = self.recognizer.recognize_google(audio)
                    print(f"Recognized: {text}")

                    # Process the recognized text
                    self.root.after(0, self.toggle_listening)  # Stop listening UI state
                    self.root.after(10, lambda t=text: self.input_var.set(t))  # Set input var slightly later
                    self.root.after(100, self.send_message)  # Send message after input var is set

                    break  # Exit loop after successful recognition

                except sr.WaitTimeoutError:
                    print("No speech detected within timeout.")
                    if not self.listening:
                        print("Listening stopped by user during timeout.")
                        break
                    else:
                        self.root.after(0, self.status_var.set, "Status: Listening... (Timeout)")
                except sr.UnknownValueError:
                    print("Could not understand audio")
                    self.root.after(0, self.add_to_conversation, "System", "Sorry, I couldn't understand that.")
                    self.root.after(0, self.status_var.set, "Status: Could not understand audio")
                    self.root.after(0, self.toggle_listening)
                    break
                except sr.RequestError as e:
                    error_msg = f"Speech service error; {e}"
                    print(error_msg)
                    self.root.after(0, self.add_to_conversation, "System", error_msg)
                    self.root.after(0, self.status_var.set, "Status: Speech service error")
                    self.root.after(0, self.toggle_listening)
                    break
                except Exception as e:
                    error_msg = f"Unexpected error during listening: {e}"
                    print(error_msg)
                    self.root.after(0, self.add_to_conversation, "System", error_msg)
                    self.root.after(0, self.status_var.set, "Status: Listening error")
                    self.root.after(0, self.toggle_listening)
                    break

        if self.listening:
            print("Resetting listening state after loop exit.")
            self.root.after(0, self.toggle_listening)

    def speak(self, text):
        if not SPEECH_AVAILABLE:
            return
        
        def run_speech():
            try:
                # Try to use Groq's TTS API first
                if USE_GROQ_TTS and hasattr(self.conversation, 'api_key') and self.conversation.api_key:
                    audio_file = self.conversation.text_to_speech(text)
                    if audio_file:
                        # Play the audio file using pygame
                        try:
                            # If we have a currently playing sound, stop it
                            if hasattr(self, 'current_audio') and self.current_audio:
                                pygame.mixer.stop()
                            
                            # Load and play the new audio
                            pygame.mixer.music.load(audio_file)
                            pygame.mixer.music.play()
                            
                            # Wait for audio to finish playing
                            while pygame.mixer.music.get_busy():
                                pygame.time.wait(100)
                                
                            return  # Successfully played audio, so return
                        except Exception as e:
                            print(f"Error playing Groq TTS audio: {e}")
                
                # Fallback to pyttsx3 if Groq TTS failed or is not available
                if PYTTSX3_AVAILABLE:
                    self.engine.say(text)
                    self.engine.runAndWait()
                else:
                    print("No speech synthesis available. Text: " + text)
            except Exception as e:
                print(f"Error in speech: {e}")
        
        speech_thread = threading.Thread(target=run_speech)
        speech_thread.daemon = True
        speech_thread.start()
    
    def test_audio_playback(self, file_path):
        """Test playback of a specific audio file."""
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
        except Exception as e:
            print(f"Error playing audio file {file_path}: {e}")
    
    def periodic_updates(self):
        """Handles periodic tasks like emotion updates and memory analysis."""
        memory_analysis_interval = 300  # Analyze memory every 5 minutes (300 seconds)
        emotion_update_interval = 10  # Update emotion display every 10 seconds
        last_memory_analysis = time.time() - memory_analysis_interval  # Analyze on first run

        while self.running:
            current_time = time.time()
            try:
                # Update emotional state based on time passing
                self.conversation.update_emotional_state_over_time()

                # Update the display on the main thread
                if self.root and self.root.winfo_exists():
                    self.root.after(0, self.update_emotion_display)

                # Periodically analyze memory
                if current_time - last_memory_analysis >= memory_analysis_interval:
                    print("Performing periodic memory analysis...")
                    if self.root and self.root.winfo_exists():
                        self.root.after(0, self.status_var.set, "Status: Analyzing memory...")
                    threading.Thread(target=self._run_memory_analysis, daemon=True).start()
                    last_memory_analysis = current_time

            except Exception as e:
                if isinstance(e, tk.TclError) and "application has been destroyed" in str(e):
                    print("Periodic update loop: GUI already destroyed.")
                else:
                    print(f"Error during periodic updates: {e}")

            for _ in range(emotion_update_interval):
                if not self.running:
                    break
                time.sleep(1)
            if not self.running:
                break

        print("Periodic update thread finished.")

    def _run_memory_analysis(self):
        """Helper function to run memory analysis in a thread."""
        try:
            success = self.conversation.extract_and_update_memory()
            if self.root and self.root.winfo_exists():
                if success:
                    print("Memory analysis complete and updated.")
                    self.root.after(0, self.status_var.set, "Status: Memory updated.")
                else:
                    print("Memory analysis failed or no new information found.")
                    self.root.after(0, self.status_var.set, "Status: Memory analysis check complete.")
        except Exception as e:
            print(f"Exception during memory analysis thread: {e}")
            if self.root and self.root.winfo_exists():
                self.root.after(0, self.status_var.set, "Status: Memory analysis error.")

        if self.root and self.root.winfo_exists():
            self.root.after(3000, lambda: self.status_var.set("Status: Idle") if self.status_var.get() != "Status: Listening..." else None)

    def close_app(self):
        """Gracefully closes the application."""
        if not self.running:
            return
        print("Close command received. Shutting down...")
        self.running = False
        self.status_var.set("Status: Shutting down...")

        print("Stopping audio mixer...")
        pygame.mixer.quit()

        print("Unhooking hotkeys...")
        keyboard.unhook_all()

        time.sleep(0.5)

        print("Destroying GUI window...")
        if self.root and self.root.winfo_exists():
            self.root.destroy()

        print("Exiting script.")
        os._exit(0)

    def skip_response(self):
        """Skip the current response and reset the status."""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        self.status_var.set("Status: Skipped response")

if __name__ == "__main__":
    # --- Add Argument Parsing ---
    parser = argparse.ArgumentParser(description="Groqee - Voice Interactive Assistant")
    parser.add_argument(
        "--persona",
        type=str,
        default="Default",
        help="Specify the persona to use (e.g., Default, Realtor, Tamagotchi, Pikachu, NamingSession)"
    )
    args = parser.parse_args()
    selected_persona = args.persona
    print(f"Attempting to load persona: {selected_persona}")
    # --- End Argument Parsing ---

    is_admin = False
    if os.name == 'nt':
        try:
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            if not is_admin:
                print("\nWARNING: Script not run as administrator.")
                print("Global hotkeys (Ctrl+Alt+S, Ctrl+Alt+X) might not work unless the application window is focused.")
                print("Run the script as administrator for global hotkey functionality.\n")
        except Exception as e:
            print(f"Could not check admin status: {e}")

    app = None
    try:
        root = tk.Tk()
        # --- Pass selected persona to GroqeeApp ---
        app = GroqeeApp(root, persona_name=selected_persona)
        # --- End persona passing ---
        root.protocol("WM_DELETE_WINDOW", app.close_app)
        root.mainloop()
    except Exception as e:
        print(f"Fatal Error in main application: {e}")
        if app:
            app.close_app()
        else:
            print("Unhooking hotkeys (fallback)...")
            keyboard.unhook_all()
            os._exit(1)
    finally:
        print("Application main loop finished or crashed.")
        keyboard.unhook_all()
