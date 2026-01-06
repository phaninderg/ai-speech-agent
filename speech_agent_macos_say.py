#!/usr/bin/env python3
"""
AI Speech Agent - Alternative version using macOS native 'say' command
This version is guaranteed to work on macOS M-series chips (M1/M2/M3/M4)
Uses the native 'say' command for 100% offline, reliable TTS
"""

import os
import sys
import json
import time
import subprocess
from typing import Optional

import speech_recognition as sr
import requests
from faster_whisper import WhisperModel


class SpeechAgent:
    """Offline AI Speech Agent using Ollama and macOS native TTS"""
    
    def __init__(self, model_name: str = "gemma3:4b", ollama_url: str = "http://localhost:11434",
                 listen_timeout: int = 20, phrase_time_limit: int = 30, voice: str = "Samantha"):
        """
        Initialize the speech agent
        
        Args:
            model_name: Ollama model to use (default: gemma3:4b)
            ollama_url: Ollama API endpoint
            listen_timeout: Seconds to wait for speech to start (default: 20)
            phrase_time_limit: Maximum seconds for a single phrase (default: 30)
            voice: macOS voice to use (default: Samantha)
        """
        self.model_name = model_name
        self.ollama_url = ollama_url
        self.conversation_history = []
        self.voice = voice
        
        # Listening configuration
        self.listen_timeout = listen_timeout
        self.phrase_time_limit = phrase_time_limit
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # Initialize Whisper model for offline speech recognition
        print("🔄 Loading Whisper model (this may take a moment on first run)...")
        self.whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
        print("✓ Whisper model loaded (offline speech recognition ready)")

        # Check if 'say' command is available (macOS)
        try:
            subprocess.run(['say', '-v', '?'], capture_output=True, check=True)
            print(f"✓ Audio system initialized (macOS 'say' command - offline TTS)")
            print(f"  Using voice: {self.voice}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ macOS 'say' command not available. This script requires macOS.")
            sys.exit(1)
        
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
        """Convert text to speech using macOS native 'say' command"""
        try:
            print("🔊 Speaking (offline - macOS native)...")
            
            # Use macOS 'say' command for TTS
            # -v: voice, -r: rate (words per minute, default 175)
            subprocess.run(['say', '-v', self.voice, '-r', '175', text], check=True)
            
            print("✓ Speech completed")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  TTS Error: {e}")
            print(f"   Continuing without speech output...")
        except Exception as e:
            print(f"⚠️  Unexpected error: {e}")
            print(f"   Continuing without speech output...")
    
    def listen(self) -> Optional[str]:
        """Listen to microphone and convert speech to text using Whisper"""
        try:
            print(f"🎤 Listening... (speak now - you have up to {self.phrase_time_limit} seconds)")
            
            with self.microphone as source:
                # Listen with extended timeout
                audio = self.recognizer.listen(
                    source,
                    timeout=self.listen_timeout,
                    phrase_time_limit=self.phrase_time_limit
                )
            
            print("🔄 Processing speech (offline)...")
            
            # Convert audio to raw data for Whisper
            audio_data = audio.get_raw_data(convert_rate=16000, convert_width=2)
            
            # Use Whisper for offline transcription
            import numpy as np
            audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            
            segments, info = self.whisper_model.transcribe(audio_np, beam_size=5)
            text = " ".join([segment.text for segment in segments]).strip()
            
            if text:
                print(f"📝 You: {text}")
                return text
            else:
                print("⚠️  No speech detected. Please try again.")
                return None
                
        except sr.WaitTimeoutError:
            print(f"⚠️  No speech detected within {self.listen_timeout} seconds. Please try again.")
            return None
        except Exception as e:
            print(f"❌ Error during listening: {e}")
            return None
    
    def get_ai_response(self, user_input: str) -> str:
        """Get response from Ollama AI model"""
        # Add user input to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Prepare messages for the API
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
        print("🎙️  AI SPEECH AGENT - macOS Native TTS Version")
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
                    time.sleep(1)
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
    MODEL_NAME = "gemma3:4b"  # You can change this to any available Ollama model
    OLLAMA_URL = "http://localhost:11434"
    VOICE = "Samantha"  # macOS voice (try: say -v ? to see all voices)
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        MODEL_NAME = sys.argv[1]
    if len(sys.argv) > 2:
        VOICE = sys.argv[2]
    
    # Create and run the agent
    agent = SpeechAgent(model_name=MODEL_NAME, ollama_url=OLLAMA_URL, voice=VOICE)
    agent.run()


if __name__ == "__main__":
    main()
