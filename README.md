# Sara — Free Personal Assistant (Laptop)

Sara is a free personal assistant that runs on your own laptop.
No paid API key is needed. She always replies in clear American English.

## What Sara does
- Chats with you using Ollama running locally (llama3.2:3b)
- Remembers notes and facts about you (saved in memory.json)
- Controls your laptop: opens apps, volume, brightness, WhatsApp, shutdown
- Makes PDF and Word files from her answers, using only Python
- Optional voice mode (voice.py)

## First time setup (only once)

### 1. Install Python
Download it from https://www.python.org/downloads/
Tick "Add Python to PATH" while installing.

### 2. Install Ollama (the free AI brain)
Download it from https://ollama.com and install it.

Then run this in a terminal / Command Prompt:

```
ollama pull llama3.2:3b
```

If your laptop is slow or has little RAM, try the smaller model:

```
ollama pull qwen2.5:1.5b
```

And change `MODEL = "llama3.2:3b"` in main.py to
`MODEL = "qwen2.5:1.5b"`.

### 3. Install the one Python package Sara needs

```
pip install requests
```

### 4. Check everything (optional, but helpful)

```
python check.py
```

If everything says OK, you are ready.

## Run Sara

Double-click `run_windows.bat`, or run:

```
python main.py
```

Then just type. Try `help` to see all commands.

## Laptop tools (optional, Windows)
For opening apps, volume, brightness, and WhatsApp:

```
pip install pyautogui screen_brightness_control pyperclip pywhatkit
```

Commands that work after that: `notepad kholo`,
`google search python`, `volume zyada`, `brightness 70`,
`laptop band karo`, `whatsapp +92... : your message`,
and `explain this` (explain your copied text in simple English).

## PDF / Word files (no install needed)
Ask Sara something first. When her answer comes, type:

```
isay pdf banao
isay word banao
```

Or write your own text directly:

```
pdf banao: your text here
word banao: your text here
```

The file is saved in this same folder, for example
`assistant_20251113_123000.pdf`. Sara tells you the full path.

## Voice mode (optional)

```
pip install SpeechRecognition pyttsx3 pyaudio
python voice.py
```

Note: listening needs internet (Google speech recognition),
speaking is offline. Voice mode listens in American English (en-US).

## Commands
- `time` — the current time
- `note: ...` — save a note
- `notes` — show all notes
- `yaad rakho ...` — remember something about you
- `explain this` — explain copied text in simple English
- `exit` — close Sara

## Files in this folder
- `main.py` — Sara herself (chat + commands)
- `tools.py` — laptop tools, PDF and Word files
- `check.py` — setup check, installs nothing
- `voice.py` — optional voice mode
- `run_windows.bat` — double-click to start Sara on Windows
- `memory.json` — your notes and facts (starts empty)
- `README.md` — this file
