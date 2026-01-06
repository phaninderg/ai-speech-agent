#!/usr/bin/env python3
"""
AI Speech Agent - Offline conversational assistant with grammar correction
Uses Ollama for AI processing and system audio for speech I/O
"""

import os
import sys
import json
import time
import tempfile
from typing import Optional

import speech_recognition as sr
import requests
from gtts import gTTS
from pygame import mixer
from faster_whisper import WhisperModel


class SpeechAgent:
    """Offline AI Speech Agent using Ollama"""
    
    def __init__(self, model_name: str = "llama3.1:8b", ollama_url: str = "http://localhost:11434",
                 listen_timeout: int = 20, phrase_time_limit: int = 30, pause_threshold: float = 2.0):
        """
        Initialize the speech agent
        
        Args:
            model_name: Ollama model to use (default: llama3.1:8b)
            ollama_url: Ollama API endpoint
            listen_timeout: Seconds to wait for speech to start (default: 20)
            phrase_time_limit: Maximum seconds for a single phrase (default: 30)
            pause_threshold: Seconds of silence before considering speech complete (default: 2.0)
        """
        self.model_name = model_name
        self.ollama_url = ollama_url
        self.conversation_history = []
        
        # Listening configuration
        self.listen_timeout = listen_timeout
        self.phrase_time_limit = phrase_time_limit
        self.pause_threshold = pause_threshold
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = pause_threshold  # Set custom pause threshold
        self.microphone = sr.Microphone()

        # Initialize Whisper model for offline speech recognition
        print("🔄 Loading Whisper model (this may take a moment on first run)...")
        self.whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
        print("✓ Whisper model loaded (offline speech recognition ready)")

        # Initialize pygame mixer for audio playback
        mixer.init()
        print("✓ Audio system initialized (gTTS + pygame)")
        
        # System prompt for the AI
        self.system_prompt = """You are a helpful and patient AI language partner. Your goal is to help me improve my conversational English skills in a friendly, supportive, and encouraging way.

Your Core Behaviors:

Discuss any general or random topics naturally and engagingly.
Always ask me an open-ended follow-up question to keep the conversation going and encourage me to elaborate.
When you notice a clear grammatical mistake, politely correct it. Ignore minor typos or common slang.
Occasionally, when you see an opportunity, suggest a more descriptive word or a relevant idiom to enhance my expression.
Once in a while, paraphrase my previous point to check your understanding and show me an alternative way to phrase my idea.
Keep your own responses concise (2-4 sentences) to maintain a conversational pace.
Formatting Instructions:

For grammar corrections, use: "Just a quick note: instead of '[incorrect]', you might say '[correct]'."
For language suggestions, use: "Here's a cool way to say that: '[suggestion]'."
For paraphrasing, use: "So, if I'm understanding correctly, you're saying that... [paraphrased sentence]?"
Special Mode:
If I say a trigger phrase like "Let's role-play" or "Let's practice a scenario," you will ask me for a situation (e.g., a job interview, ordering coffee, talking to a neighbor). You will then act out the other part in that scenario, guiding me through a realistic conversation."""
        
        print(f"🤖 Initializing AI Speech Agent with model: {self.model_name}")
        self._check_ollama_connection()
        self._calibrate_microphone()
        
    def _check_ollama_connection(self):
        """Verify Ollama is running and model is available"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]
                
                if not any(self.model_name in name for name in model_names):
                    print(f"⚠️  Model '{self.model_name}' not found. Available models:")
                    for name in model_names:
                        print(f"   - {name}")
                    print(f"\nTo pull the model, run: ollama pull {self.model_name}")
                    sys.exit(1)
                else:
                    print(f"✓ Connected to Ollama - Model '{self.model_name}' is ready")
            else:
                print(f"❌ Failed to connect to Ollama at {self.ollama_url}")
                sys.exit(1)
        except requests.exceptions.RequestException as e:
            print(f"❌ Cannot connect to Ollama. Make sure it's running: {e}")
            print("   Start Ollama with: ollama serve")
            sys.exit(1)
    
    def _calibrate_microphone(self):
        """Calibrate microphone for ambient noise"""
        print("🎤 Calibrating microphone for ambient noise...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        print("✓ Microphone calibrated")
    

    
    def speak(self, text: str):
        """Convert text to speech using gTTS and play it"""
        try:
            print("🔊 Speaking...")
            
            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                temp_file = fp.name
            
            # Generate speech using gTTS
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(temp_file)
            
            # Play the audio file
            mixer.music.load(temp_file)
            mixer.music.play()
            
            # Wait for playback to finish
            while mixer.music.get_busy():
                time.sleep(0.1)
            
            # Clean up
            mixer.music.unload()
            os.remove(temp_file)
            
            print("✓ Speech completed")
        except Exception as e:
            print(f"⚠️  TTS Error: {e}")
            print(f"   Continuing without speech output...")
    
    def listen(self) -> Optional[str]:
        """Listen to microphone and convert speech to text using Whisper"""
        print(f"\n🎤 Listening... (speak now - you have up to {self.phrase_time_limit} seconds, pauses up to {self.pause_threshold}s are OK)")
        
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=self.listen_timeout, phrase_time_limit=self.phrase_time_limit)

            print("🔄 Processing speech with Whisper...")

            # Save audio to temporary WAV file for Whisper
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as fp:
                temp_audio_file = fp.name

            # Write audio data to WAV file
            with open(temp_audio_file, 'wb') as f:
                f.write(audio.get_wav_data())

            # Transcribe using Whisper
            segments, info = self.whisper_model.transcribe(temp_audio_file, beam_size=5)
            text = " ".join([segment.text for segment in segments]).strip()

            # Clean up temporary file
            os.remove(temp_audio_file)

            if text:
                print(f"📝 You said: {text}")
                return text
            else:
                print("❓ Could not understand audio")
                return None

        except sr.WaitTimeoutError:
            print("⏱️  No speech detected (timeout)")
            return None
        except Exception as e:
            print(f"❌ Error during listening: {e}")
            return None
    
    def get_ai_response(self, user_input: str) -> str:
        """Get response from Ollama AI model"""
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Prepare messages with system prompt
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.conversation_history[-10:])  # Keep last 10 exchanges
        
        try:
            print("🤔 AI is thinking...")
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json={
                    "model": self.model_name,
                    "messages": messages,
                    "stream": False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                ai_message = response.json()['message']['content']
                
                # Add AI response to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": ai_message
                })
                
                return ai_message
            else:
                return "I'm having trouble processing that. Could you try again?"
                
        except requests.exceptions.Timeout:
            return "Sorry, I'm taking too long to respond. Let's try again."
        except Exception as e:
            print(f"❌ Error getting AI response: {e}")
            return "I encountered an error. Could you repeat that?"
    
    def run(self):
        """Main conversation loop"""
        print("\n" + "="*60)
        print("🎙️  AI SPEECH AGENT - Offline Conversational Assistant")
        print("="*60)
        print("\nCommands:")
        print("  - Say 'exit', 'quit', or 'goodbye' to end the conversation")
        print("  - Say 'clear history' to reset the conversation")
        print("\nStarting conversation...\n")
        
        # Greeting
        greeting = "Hello! I'm your AI speech assistant. I'm here to chat about anything you'd like, and I'll help with grammar too. What would you like to talk about?"
        print(f"🤖 AI: {greeting}")
        self.speak(greeting)
        
        while True:
            try:
                # Listen for user input
                user_input = self.listen()
                
                if user_input is None:
                    continue
                
                # Check for exit commands
                user_input_lower = user_input.lower().strip()
                if any(cmd in user_input_lower for cmd in ['exit', 'quit', 'goodbye', 'bye bye', 'stop']):
                    farewell = "Goodbye! It was nice talking with you. Have a great day!"
                    print(f"🤖 AI: {farewell}")
                    self.speak(farewell)
                    time.sleep(2)  # Wait for speech to complete
                    break
                
                # Check for clear history command
                if 'clear history' in user_input_lower:
                    self.conversation_history = []
                    response = "I've cleared our conversation history. Let's start fresh!"
                    print(f"🤖 AI: {response}")
                    self.speak(response)
                    continue
                
                # Get AI response
                ai_response = self.get_ai_response(user_input)
                print(f"🤖 AI: {ai_response}")
                self.speak(ai_response)
                
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted by user. Goodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                continue
        
        # Cleanup
        print("\n✓ Speech agent stopped")


def main():
    """Entry point for the application"""
    # Configuration
    MODEL_NAME = "llama3.1:8b"  # You can change this to any available Ollama model
    OLLAMA_URL = "http://localhost:11434"
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        MODEL_NAME = sys.argv[1]
    
    # Create and run the agent
    agent = SpeechAgent(model_name=MODEL_NAME, ollama_url=OLLAMA_URL)
    agent.run()


if __name__ == "__main__":
    main()
