# Groqee - Voice Interactive Assistant
# Conversation manager for the Groqee virtual companion with Groq API integration

import time
import json
import os
import requests
from datetime import datetime

# Groq API configuration
GROQ_CHAT_API_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
GROQ_SPEECH_API_ENDPOINT = "https://api.groq.com/openai/v1/audio/speech"
GROQ_CHAT_MODEL = "llama3-70b-8192"  # Current supported model
GROQ_SPEECH_MODEL = "playai-tts"  # Groq's text-to-speech model
GROQ_VOICE = "Aaliyah-PlayAI"  # Updated to a valid feminine voice

class ConversationManager:
    def __init__(self, persona_name="Default"):
        # Load Groq API key
        self.api_key = self.load_api_key()
        
        # Load personas
        self.personas = self.load_personas()
        self.persona_name = persona_name if persona_name in self.personas else "Default"
        
        # Initialize memory system
        self.memory_file = os.path.join(os.path.dirname(__file__), "memory.json")
        self.memory = self.load_memory()
        
        # Conversation history for Groq API
        self.api_messages = []
        
        # Initialize system prompt based on selected persona
        self.initialize_api_conversation()
        
        # Track recent audio files for cleanup
        self.recent_audio_files = []
        self.max_recent_files = 5
    
    def load_api_key(self):
        """Load Groq API key from environment variable or file"""
        # Try to get from environment variable first
        api_key = os.environ.get("GROQ_API_KEY")
        
        # If not in environment, try to load from file
        if not api_key:
            api_key_file = os.path.join(os.path.dirname(__file__), "groq_api_key.txt")
            try:
                if os.path.exists(api_key_file):
                    with open(api_key_file, 'r') as f:
                        api_key = f.read().strip()
                else:
                    print("ERROR: No Groq API key found. Please set GROQ_API_KEY environment variable or create groq_api_key.txt file.")
            except Exception as e:
                print(f"Error loading API key: {e}")
        
        return api_key
    
    def load_personas(self):
        """Load persona definitions from personas.json"""
        personas_file = os.path.join(os.path.dirname(__file__), "personas.json")
        default_personas = {
            "Default": {
                "name": "Groqee the Storyteller",
                "prompt": "You are Groqee, the ultimate storyteller of terrifying scenarios. Your tales revolve around common household incidents and injuries, vividly describing the horrors and dangers that lurk in everyday life. Speak with a chilling tone, captivating the listener with your spine-tingling narratives."
            }
        }
        try:
            if os.path.exists(personas_file):
                with open(personas_file, 'r') as f:
                    data = json.load(f)
                    return data.get("personas", default_personas)
            else:
                print("WARNING: personas.json not found. Using default persona.")
                # Optionally create a default personas.json here
                return default_personas
        except Exception as e:
            print(f"Error loading personas.json: {e}. Using default persona.")
            return default_personas
    
    def load_memory(self):
        """Load memory from file or create a new one if it doesn't exist"""
        default_memory = {
            "user_info": {
                "name": "",
                "hobbies": [],
                "likes": [],
                "dislikes": [],
                "goals": [],
                "challenges": [],
                "job": "",
                "family": []
            },
            "conversation_history": [],
            "emotional_state": {
                "happiness": 50.0,
                "energy": 50.0
            },
            "interaction_count": 0,
            "last_interaction": "",
            "important_dates": {},
            "key_insights": []
        }
        
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            else:
                # Create the file with default memory
                with open(self.memory_file, 'w') as f:
                    json.dump(default_memory, f, indent=4)
                return default_memory
        except Exception as e:
            print(f"Error loading memory file: {e}")
            return default_memory
    
    def save_memory(self):
        """Save memory to file"""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory, f, indent=4)
        except Exception as e:
            print(f"Error saving memory: {e}")
    
    def initialize_api_conversation(self):
        """Initialize the conversation with the selected persona's system message"""
        # Format user information for context
        user_info = self.memory["user_info"]
        user_context = "User profile not yet established."
        
        if user_info["name"]:
            user_context = f"The user's name is {user_info['name']}. "
        
        if user_info["hobbies"]:
            hobbies_str = ", ".join(user_info["hobbies"])
            user_context += f"They enjoy {hobbies_str}. "
            
        if user_info["goals"]:
            goals_str = ", ".join(user_info["goals"])
            user_context += f"Their goals include: {goals_str}. "
            
        if user_info["challenges"]:
            challenges_str = ", ".join(user_info["challenges"][:2])  # Just mention a couple
            user_context += f"They've mentioned challenges with {challenges_str}. "
            
        if user_info["job"]:
            user_context += f"They work as {user_info['job']}. "
        
        # Recent conversation context
        recent_exchanges = ""
        if len(self.memory["conversation_history"]) > 0:
            recent = self.memory["conversation_history"][-5:]  # Get 5 most recent exchanges
            for exchange in recent:
                if "user" in exchange:
                    recent_exchanges += f"User: {exchange['user']}\n"
                if "assistant" in exchange:
                    recent_exchanges += f"Echo: {exchange['assistant']}\n"
        
        # --- SELECT PERSONA PROMPT ---
        selected_persona = self.personas.get(self.persona_name, self.personas["LeonardoDaVinci"])
        base_prompt = selected_persona.get("prompt", "You are a helpful AI assistant.")
        
        # Combine base prompt with dynamic context
        system_prompt = f"""{base_prompt}

ADDITIONAL CONTEXT:
USER PROFILE SUMMARY: {user_context}
RECENT CONVERSATION SNIPPET:
{recent_exchanges}
CURRENT DATE: {datetime.now().strftime('%A, %B %d, %Y')}
INTERACTION COUNT: {self.memory["interaction_count"]}
"""
        # --- END OF PERSONA PROMPT SELECTION ---

        # Reset API messages and add system prompt
        self.api_messages = [{"role": "system", "content": system_prompt}]
        
        # If we have recent conversation history, add the last few exchanges to maintain context
        if len(self.memory["conversation_history"]) > 0:
            # Add up to 6 recent message pairs (max 12 messages total)
            start_idx = max(0, len(self.memory["conversation_history"]) - 6)
            for exchange in self.memory["conversation_history"][start_idx:]:
                if "user" in exchange:
                    self.api_messages.append({"role": "user", "content": exchange["user"]})
                if "assistant" in exchange:
                    self.api_messages.append({"role": "assistant", "content": exchange["assistant"]})
    
    def process_input(self, text):
        """Process user input and generate a response using Groq API"""
        if not self.api_key:
            return "I need a Groq API key to continue our conversation. Please add one to groq_api_key.txt"
        
        # Update memory
        self.memory["interaction_count"] += 1
        self.memory["last_interaction"] = datetime.now().isoformat()
        
        # Store user message in memory
        self.memory["conversation_history"].append({
            "user": text,
            "timestamp": datetime.now().isoformat()
        })
        
        # Add user message to API conversation
        self.api_messages.append({"role": "user", "content": text})
        
        # Get response from Groq Chat API
        response = self.get_groq_chat_response()
        
        if response:
            # Add response to memory
            self.memory["conversation_history"].append({
                "assistant": response,
                "timestamp": datetime.now().isoformat()
            })
            
            # Add assistant message to API conversation
            self.api_messages.append({"role": "assistant", "content": response})
            
            # Trim API messages if they get too long (to avoid token limits)
            # Keep system message + recent exchanges
            if len(self.api_messages) > 25:
                system_msg = self.api_messages[0]
                self.api_messages = [system_msg] + self.api_messages[-14:]
            
            # Save updated memory
            self.save_memory()
            
            return response
        else:
            # If API call failed, return a simple error message
            return "I'm having trouble connecting to my voice service. Please try again in a moment."
    
    def get_groq_chat_response(self):
        """Get a response from the Groq Chat API"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # Prepare the payload
            payload = {
                "model": GROQ_CHAT_MODEL,
                "messages": self.api_messages,
                "temperature": 0.7,
                "max_tokens": 150  # Shorter responses for voice interactions
            }
            
            # Make the API call
            response = requests.post(GROQ_CHAT_API_ENDPOINT, headers=headers, json=payload)
            
            # Check if the request was successful
            if response.status_code == 200:
                response_data = response.json()
                if "choices" in response_data and len(response_data["choices"]) > 0:
                    return response_data["choices"][0]["message"]["content"].strip()
            
            # Log error
            print(f"Error from Groq Chat API: {response.status_code}, {response.text}")
            return None
            
        except Exception as e:
            print(f"Exception when calling Groq Chat API: {e}")
            return None
    
    def text_to_speech(self, text):
        """Convert text to speech using Groq's Text-to-Speech API"""
        if not self.api_key:
            print("No Groq API key available for text-to-speech")
            return None
            
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # Prepare the payload
            payload = {
                "model": GROQ_SPEECH_MODEL,
                "input": text,
                "voice": GROQ_VOICE,
                "response_format": "wav"
            }
            
            # Make the API call
            response = requests.post(GROQ_SPEECH_API_ENDPOINT, headers=headers, json=payload)
            
            # Check if the request was successful
            if response.status_code == 200:
                # Create a temporary file to store the audio
                temp_dir = os.path.join(os.path.dirname(__file__), "temp_audio")
                os.makedirs(temp_dir, exist_ok=True)
                
                # Create temporary file with .wav extension
                audio_file = os.path.join(temp_dir, f"echo_speech_{int(time.time())}.wav")
                
                # Write the audio data to the file
                with open(audio_file, "wb") as f:
                    f.write(response.content)
                
                # Keep track of recent files for cleanup
                self.recent_audio_files.append(audio_file)
                if len(self.recent_audio_files) > self.max_recent_files:
                    # Remove oldest file
                    old_file = self.recent_audio_files.pop(0)
                    if os.path.exists(old_file):
                        try:
                            os.remove(old_file)
                        except Exception as e:
                            print(f"Error removing old audio file: {e}")
                
                return audio_file
            
            # Log error
            print(f"Error from Groq Speech API: {response.status_code}, {response.text}")
            return None
            
        except Exception as e:
            print(f"Exception when calling Groq Speech API: {e}")
            return None
    
    def extract_and_update_memory(self):
        """Extract information from conversation history and update memory
           This can be called periodically to analyze conversations and update user profile"""
        if not self.api_key or len(self.memory["conversation_history"]) == 0:
            return
            
        # Get the last 10 exchanges or all if less than 10
        recent_history = self.memory["conversation_history"][-20:]
        conversation_text = ""
        
        for exchange in recent_history:
            if "user" in exchange:
                conversation_text += f"User: {exchange['user']}\n"
            if "assistant" in exchange:
                conversation_text += f"Echo: {exchange['assistant']}\n"
        
        # Prepare system prompt for analysis
        analysis_prompt = [
            {"role": "system", "content": """You are an AI assistant tasked with extracting user information from conversation history.
            Extract the following information if present:
            - User's name
            - Hobbies and interests
            - Likes and dislikes
            - Goals and aspirations
            - Challenges or problems
            - Job or profession
            - Family details
            - Important dates (birthdays, anniversaries)
            - Key insights about the user's personality
            
            Format your response as a JSON object with these fields. Only include information that is explicitly mentioned.
            Do not invent or assume information. If a field has no information, leave it as an empty list or string."""},
            {"role": "user", "content": f"Analyze this conversation and extract user information:\n\n{conversation_text}"}
        ]
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": GROQ_CHAT_MODEL,
                "messages": analysis_prompt,
                "temperature": 0.1,  # Low temperature for more factual extraction
                "response_format": {"type": "json_object"}
            }
            
            response = requests.post(GROQ_CHAT_API_ENDPOINT, headers=headers, json=payload)
            
            if response.status_code == 200:
                response_data = response.json()
                if "choices" in response_data and len(response_data["choices"]) > 0:
                    analysis = json.loads(response_data["choices"][0]["message"]["content"])
                    
                    # Update memory with extracted information
                    user_info = self.memory["user_info"]
                    
                    # Update name if found and not already set
                    if analysis.get("name") and not user_info["name"]:
                        user_info["name"] = analysis["name"]
                    
                    # Update lists by adding new items
                    for field in ["hobbies", "likes", "dislikes", "goals", "challenges"]:
                        if field in analysis and analysis[field]:
                            # Add new items that aren't already in the list
                            if isinstance(analysis[field], list):
                                for item in analysis[field]:
                                    if item not in user_info[field]:
                                        user_info[field].append(item)
                            elif isinstance(analysis[field], str) and analysis[field] not in user_info[field]:
                                user_info[field].append(analysis[field])
                    
                    # Update job if found and not already set
                    if analysis.get("job") and not user_info["job"]:
                        user_info["job"] = analysis["job"]
                    
                    # Update family information
                    if analysis.get("family") and isinstance(analysis["family"], list):
                        for member in analysis["family"]:
                            if member not in user_info["family"]:
                                user_info["family"].append(member)
                    
                    # Update important dates
                    if analysis.get("important_dates") and isinstance(analysis["important_dates"], dict):
                        for event, date in analysis["important_dates"].items():
                            self.memory["important_dates"][event] = date
                    
                    # Add key insights
                    if analysis.get("key_insights") and isinstance(analysis["key_insights"], list):
                        for insight in analysis["key_insights"]:
                            if insight not in self.memory["key_insights"]:
                                self.memory["key_insights"].append(insight)
                    
                    # Save updated memory
                    self.save_memory()
                    
                    # Reinitialize API conversation with updated memory
                    self.initialize_api_conversation()
                    
                    return True
            
            print(f"Error during memory extraction: {response.status_code}, {response.text}")
            return False
            
        except Exception as e:
            print(f"Exception during memory extraction: {e}")
            return False
    
    def update_emotional_state_over_time(self):
        """Placeholder method to avoid errors during periodic updates."""
        pass