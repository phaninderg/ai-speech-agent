# AI Speech Agent - Conversational Assistant

An AI speech agent that uses Ollama for natural language processing and voice interaction. Available in two versions: standard (with online TTS) and fully offline (macOS native). The agent can converse on any topic and provides grammar corrections in a friendly manner.

## 🎯 Features

- 🎤 **Voice Input**: Uses your system microphone to listen to your speech
- 🔊 **Voice Output**: High-quality text-to-speech using gTTS
- 🤖 **Offline AI**: AI processing via Ollama (completely offline)
- 💬 **Natural Conversations**: Discuss any random or general topics
- ✍️ **Grammar Correction**: Politely corrects grammatical mistakes
- 🔒 **Privacy**: AI processing runs locally - only TTS requires internet
- ⏱️ **Extended Listening**: 30 seconds to complete your statements
- 🌐 **Two Versions**: Online TTS (gTTS) or fully offline (macOS native)

## 📋 Prerequisites

1. **Python 3.13** installed on your system
2. **Ollama** installed and running
3. **System audio** capabilities (microphone and speakers/headphones)

### Installing Ollama

If you don't have Ollama installed:

```bash
# macOS
brew install ollama

# Start Ollama service
ollama serve

# Pull the model (in a new terminal)
ollama pull llama3.1:8b
```

For other operating systems, visit: https://ollama.ai/download

## 🎙️ TTS Options

This project includes **two versions** with different TTS approaches:

### Version 1: gTTS (Standard)
**File**: `speech_agent.py`
- Uses Google Text-to-Speech (gTTS)
- Requires internet connection for speech output
- High-quality, natural-sounding voices
- Works reliably on all platforms
- **Use this if**: You have internet and want high-quality TTS

### Version 2: macOS Native TTS (100% Offline)
**File**: `speech_agent_macos_say.py`
- Uses macOS native `say` command
- Guaranteed to work on macOS M1/M2/M3/M4
- 100% offline operation (no internet needed)
- High-quality native voices
- **Use this if**: You want fully offline operation on macOS

**Note**: pyttsx3 has compatibility issues on macOS M-series chips, so we use gTTS for the standard version.

### Quick Comparison

| Feature | speech_agent.py | speech_agent_macos_say.py |
|---------|----------------|---------------------------|
| **TTS Method** | gTTS (Google) | macOS `say` command |
| **Internet Required** | Yes (for TTS only) | No |
| **Voice Quality** | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐ Great |
| **Platform** | All platforms | macOS only |
| **AI Processing** | ✅ Offline | ✅ Offline |
| **Speech Recognition** | ✅ Offline | ✅ Offline |
| **Privacy** | AI offline, TTS online | ✅ 100% offline |
| **Works on M4** | ✅ Yes | ✅ Yes |

## 🚀 Quick Start

### 1. Installation

```bash
# Navigate to the project directory
cd ai-speech-agent

# Create virtual environment
python3.13 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Note for macOS users**: PortAudio is required for PyAudio:
```bash
brew install portaudio
```

### 2. Start the Agent

Make sure Ollama is running, then:

```bash
./start_agent.sh
```

This script will:
- Check if Ollama is running
- Verify the virtual environment exists
- Show helpful voice commands
- Start the agent

Or run manually:
```bash
source venv/bin/activate

# Option 1: Standard version with gTTS (requires internet for TTS)
python speech_agent.py

# Option 2: macOS native TTS (100% offline, macOS only)
python speech_agent_macos_say.py
```

### 3. Start Talking!

Once started, you'll see:
```
🔄 Loading Whisper model (this may take a moment on first run)...
✓ Whisper model loaded (offline speech recognition ready)
✓ Audio system initialized (gTTS + pygame)
🤖 Initializing AI Speech Agent with model: gemma3:4b
✓ Connected to Ollama
🎤 Calibrating microphone...
✓ Microphone calibrated

🤖 AI: Hello! I'm your AI speech assistant...
🔊 Speaking...
✓ Speech completed

🎤 Listening... (speak now - you have up to 30 seconds)
```

**Note**: On first run, the Whisper model (~140MB) will be automatically downloaded. This only happens once.

## 🎤 Voice Commands

- Say **"exit"**, **"quit"**, or **"goodbye"** to end the conversation
- Say **"clear history"** to reset the conversation context

## 💬 Example Conversation

```
🤖 AI: Hello! I'm your AI speech assistant. What would you like to talk about?

🎤 Listening...
📝 You: "I wants to learn about space exploration"

🤖 AI: Just a quick note: instead of "I wants", you might say "I want". 
       Space exploration is fascinating! Are you interested in recent 
       missions like the James Webb telescope, or Mars rovers?

🎤 Listening...
📝 You: "Tell me about Mars rovers"

🤖 AI: Mars rovers are incredible robots exploring the red planet! NASA's 
       Perseverance is currently searching for signs of ancient life and 
       collecting samples. What aspect interests you most?
```

## ⚙️ Configuration

### Adjusting Listening Time

The default settings give you:
- **20 seconds** to start speaking
- **30 seconds** to complete your statement

To customize, edit the `main()` function in `speech_agent.py`:

```python
def main():
    MODEL_NAME = "llama3.1:8b"
    OLLAMA_URL = "http://localhost:11434"
    
    # Customize listening times
    LISTEN_TIMEOUT = 30        # Time to start speaking
    PHRASE_TIME_LIMIT = 60     # Time to complete statement
    
    agent = SpeechAgent(
        model_name=MODEL_NAME,
        ollama_url=OLLAMA_URL,
        listen_timeout=LISTEN_TIMEOUT,
        phrase_time_limit=PHRASE_TIME_LIMIT
    )
    agent.run()
```

### Using Different Models

You can use any Ollama model:

```bash
# List available models
ollama list

# Use a different model
python speech_agent.py mistral:7b

# Or with the launcher
./start_agent.sh gemma3:27b-it-qat
```

### Customizing AI Behavior

Edit the `system_prompt` in `speech_agent.py` to change how the AI responds:

```python
self.system_prompt = """You are a helpful AI assistant engaged in a casual conversation. 
Your role is to:
1. Discuss any general or random topics naturally and engagingly
2. When you notice grammatical mistakes in the user's speech, politely correct them
3. Keep responses concise and conversational (2-3 sentences typically)
4. Be friendly, supportive, and encouraging
"""
```

## 🛠️ Technical Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| AI Model | Ollama (llama3.1:8b) | Natural language processing |
| Speech-to-Text | Whisper (faster-whisper) | Offline voice to text conversion |
| Text-to-Speech | gTTS + pygame | Convert text to voice |
| Audio I/O | PyAudio + SpeechRecognition | Microphone access |
| HTTP Client | requests | Ollama API communication |
| Python | 3.13 | Runtime environment |

## 🔧 Troubleshooting

### Ollama Connection Issues

If you see "Cannot connect to Ollama":
1. Make sure Ollama is running: `ollama serve`
2. Verify the service: `curl http://localhost:11434/api/tags`
3. Check if the model is available: `ollama list`

### Microphone Issues

If the microphone isn't working:
1. Check system permissions (System Settings → Privacy & Security → Microphone)
2. Grant permission to Terminal or your Python application
3. Test your microphone with another application
4. Try adjusting the calibration duration in the code

### Audio Output Issues

If you can't hear the AI's responses:
1. Check your system volume is not muted
2. Ensure headphones/speakers are properly connected
3. Verify audio output device in System Settings → Sound
4. Ensure you have an internet connection (gTTS requires internet)
5. **Want offline TTS?** Use `speech_agent_macos_say.py` for 100% offline operation on macOS

### Speech Recognition Issues

The app uses OpenAI's Whisper model for offline speech recognition via the faster-whisper library. If you experience issues:
- The first run will download the Whisper model (base model ~140MB)
- For better accuracy, you can switch to larger models in the code (small, medium, or large)
- For faster processing, the base model offers good balance between speed and accuracy
- Ensure you speak clearly and minimize background noise

## 📁 Project Structure

```
ai-speech-agent/
├── speech_agent.py              # Standard version (gTTS - online TTS)
├── speech_agent_macos_say.py    # Offline version (macOS native TTS)
├── requirements.txt             # Python dependencies
├── start_agent.sh               # Launcher script
├── .gitignore                   # Git ignore rules
├── README.md                    # This file
```

## 🔒 Privacy & Security

- ✅ All AI processing happens locally via Ollama
- ✅ Speech recognition runs completely offline via Whisper
- ⚠️ Speech output uses gTTS (requires internet) in standard version
- ✅ Use `speech_agent_macos_say.py` for 100% offline operation (macOS)
- ✅ Conversation history stored only in memory (not persisted)
- ✅ No AI data sent to external servers

Your conversations are 100% private and never leave your computer.

## 🎨 Advanced Customization

### Whisper Model Selection

Change the Whisper model size for different accuracy/speed trade-offs in `speech_agent.py`:

```python
# In __init__ method (line 49):
self.whisper_model = WhisperModel("base", device="cpu", compute_type="int8")

# Available models (larger = more accurate but slower):
# "tiny"   - ~39MB   - Fastest, least accurate
# "base"   - ~74MB   - Good balance (default)
# "small"  - ~244MB  - Better accuracy
# "medium" - ~769MB  - Very accurate
# "large"  - ~2.9GB  - Best accuracy
```

### Microphone Sensitivity

Adjust in the `_calibrate_microphone()` method:

```python
def _calibrate_microphone(self):
    with self.microphone as source:
        self.recognizer.adjust_for_ambient_noise(source, duration=2)  # Increase from 1
```

### Conversation History Length

Change how many exchanges the AI remembers:

```python
messages.extend(self.conversation_history[-10:])  # Keep last 10 exchanges
```

### Speech Speed and Voice

#### For speech_agent.py (gTTS)

Modify the `speak()` method to adjust speed:

```python
# In speak() method:
tts = gTTS(text=text, lang='en', slow=True)   # Slower speech
tts = gTTS(text=text, lang='en', slow=False)  # Normal speed (default)
```

#### For speech_agent_macos_say.py (macOS Native)

Modify voice and rate in the `speak()` method:

```python
# In speak() method, adjust rate (words per minute):
subprocess.run(['say', '-v', self.voice, '-r', '200', text])  # Faster
subprocess.run(['say', '-v', self.voice, '-r', '150', text])  # Slower
subprocess.run(['say', '-v', self.voice, '-r', '175', text])  # Default

# Change voice in __init__() method:
self.voice = "Samantha"  # Default
self.voice = "Alex"      # Male voice
self.voice = "Victoria"  # Female voice
```

To see all available macOS voices:
```bash
say -v ?
```

## 📊 System Requirements

### Common Requirements (Both Versions)
- ✅ macOS (tested on M4, should work on M1/M2/M3)
- ✅ Python 3.13
- ✅ Ollama installed and running
- ✅ Microphone access
- ✅ Speaker/headphone output
- ✅ ~5.2GB disk space (for Ollama model + Whisper model)

### Version-Specific Requirements

**speech_agent.py (Standard)**
- ⚠️ Internet connection required (for gTTS only)
- ✅ AI processing: Offline (Ollama)
- ✅ Speech recognition: Offline (Whisper)
- ⚠️ Speech output: Online (gTTS)

**speech_agent_macos_say.py (Offline)**
- ✅ 100% offline operation (no internet needed)
- ✅ AI processing: Offline (Ollama)
- ✅ Speech recognition: Offline (Whisper)
- ✅ Speech output: Offline (macOS `say` command)
- ✅ macOS only

## 🆘 Getting Help

If you encounter issues:

1. **Check Ollama is running**: `ollama serve`
2. **Verify model is available**: `ollama list`
3. **Test microphone**: Check System Settings
4. **Test audio output**: Play any audio/video
5. **Check Python version**: `python --version` (should be 3.13)

## 📝 Tips for Best Experience

1. **Speak clearly** - Enunciate your words
2. **Minimize background noise** - For better recognition
3. **Natural pace** - Don't rush, but don't pause too long
4. **Use headphones** - For best audio quality
5. **Keep pauses short** - Under 1 second between words

## 🎉 Enjoy!

Your AI speech agent is ready to have conversations with you! Start it up and enjoy chatting with your offline AI assistant.

---

## License

MIT License - Feel free to modify and use as needed.

## Acknowledgments

- [Ollama](https://ollama.ai/) - Local AI model runtime
- [faster-whisper](https://github.com/guillaumekln/faster-whisper) - Offline speech recognition
- [gTTS](https://github.com/pndurette/gTTS) - Google Text-to-Speech (standard version)
- [pygame](https://www.pygame.org/) - Audio playback
- [SpeechRecognition](https://github.com/Uberi/speech_recognition) - Audio handling
- Apple macOS - Native TTS engine (offline version)
