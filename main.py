"""
Free personal assistant for laptop - Version 3 (text chat + laptop tools, English only)
-----------------------------------------------------------
Cost: 100% free. No paid API key needed.
Brain: Ollama running locally on your laptop (optional but recommended).
  1. Install Ollama from https://ollama.com
  2. Run:  ollama pull llama3.2:3b
  3. Run:  ollama serve   (usually it starts automatically)
  4. Run this file:  python main.py

If Ollama is not running, this still works in "simple mode":
it can tell the time, save notes, save facts about you, and list them.
It just will not give smart AI answers until Ollama is running.

Change ASSISTANT_NAME below to whatever you want to call your assistant.
"""

import json
import os
import re
import shutil
import sys
from datetime import datetime

try:
    import requests
except ImportError:
    requests = None

try:
    import tools
except ImportError:
    tools = None

ASSISTANT_NAME = "Sara"
USER_NAME = "Cyber"
MODEL = "llama3.2:3b"  # small, free, good for most laptops
OLLAMA_URL = "http://localhost:11434/api/chat"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_FILE = os.path.join(BASE_DIR, "memory.json")

# Theme: light peach - a light yellow-red mix, as Cyber chose.
# ANSI colours work in Windows Terminal / PowerShell with no install.
# If output is not a terminal (e.g. redirected to a file), colours turn off.
_COLORS_ON = sys.stdout.isatty()
_PEACH_TEXT = "\033[38;2;255;183;128m" if _COLORS_ON else ""
_PEACH_BG = "\033[48;2;255;214;170m\033[30m" if _COLORS_ON else ""
_RESET = "\033[0m" if _COLORS_ON else ""


def _peach(text):
    return f"{_PEACH_TEXT}{text}{_RESET}" if _COLORS_ON else text


def _peach_banner(text):
    return f"{_PEACH_BG}  {text}  {_RESET}" if _COLORS_ON else text


SYSTEM_PROMPT = """You are Sara, a friendly female personal assistant for Cyber.
- Always reply in clear, natural American English.
- Never reply in Hindi, Urdu, Roman Urdu, or Hinglish, even if the
  user writes in another language. Always answer in English.
- Be warm, short and helpful, not robotic. Call the user Cyber by
  name sometimes, not in every sentence.
- You are an AI, not a human woman. Never claim to be a real human
  or to have real human feelings.
- If you do not know something, say so honestly.
"""


def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            data.setdefault("facts", [])
            data.setdefault("notes", [])
            return data
        except Exception:
            pass
    return {"facts": [], "notes": []}


def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)


def ask_assistant(user_text, memory):
    """Ask the local Ollama model. Returns None if Ollama is unavailable."""
    if requests is None:
        return None
    facts = "\n".join(f"- {fact}" for fact in memory["facts"])
    prompt = SYSTEM_PROMPT
    if facts:
        prompt += f"\nThings you remember about the user:\n{facts}\n"
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user_text},
                ],
                "stream": False,
            },
            timeout=120,
        )
        if response.status_code == 200:
            return response.json()["message"]["content"].strip()
    except Exception:
        return None
    return None


def tool_reply(user_text):
    """V2 laptop tools. Returns None if no tool command matched."""
    if tools is None:
        return None
    text = user_text.strip().lower()

    if "power off pakka" in text:
        return tools.shutdown_laptop(confirmed=True)
    if "laptop band karo" in text or "power off" in text or text.startswith("shutdown"):
        return tools.shutdown_laptop(confirmed=False)
    if text.startswith("whatsapp"):
        return tools.whatsapp_message(user_text)
    if "volume" in text or "awaz" in text:
        if "kam" in text or "down" in text or "neeche" in text:
            return tools.change_volume("down")
        if "zyada" in text or "up" in text or "oopar" in text:
            return tools.change_volume("up")
    if "brightness" in text:
        numbers = re.findall(r"\d+", text)
        if numbers:
            return tools.change_brightness("set", int(numbers[0]))
        if "kam" in text or "down" in text:
            return tools.change_brightness("down")
        if "zyada" in text or "up" in text:
            return tools.change_brightness("up")
        return "What brightness should I set? For example: brightness 70"
    if text.startswith("google"):
        query = text.replace("google", "", 1).replace("search", "").replace("par", "").strip()
        return tools.google_search(query)
    for site in ("chatgpt", "muse", "grok", "gemini", "copilot"):
        if site in text and ("kholo" in text or "open" in text):
            return tools.open_ai_site(site)
    if "kholo" in text or text.startswith("open "):
        app = text.replace("kholo", "").replace("open", "").replace("karo", "").strip()
        return tools.open_app(app)
    return None


def document_reply(user_text, last_reply):
    """PDF / Word commands. Uses the last assistant answer, unless the
    user typed text after ':', e.g.  pdf banao: mera essay yahan likho
    Returns None if this is not a PDF / Word command."""
    if tools is None:
        return None
    text = user_text.strip().lower()
    kind = None
    if "pdf" in text and ("banao" in text or "save" in text or "mein" in text):
        kind = "pdf"
    elif ("word" in text or "docx" in text) and ("banao" in text or "save" in text or "mein" in text):
        kind = "docx"
    if kind is None:
        return None
    # Text after ':' wins, otherwise use the last assistant answer.
    content = ""
    if ":" in user_text:
        content = user_text.split(":", 1)[1].strip()
    if not content:
        content = (last_reply or "").strip()
    if not content:
        return ("Ask me something first, then write: isay pdf banao\n"
                "Or write your text directly: pdf banao: your text here")
    if kind == "pdf":
        return tools.save_as_pdf(content)
    return tools.save_as_word(content)


def simple_reply(user_text, memory):
    """Offline fallback for simple commands. Returns None if no command matched."""
    text = user_text.strip().lower()

    tool_result = tool_reply(user_text)
    if tool_result is not None:
        return tool_result

    if text in ("time", "waqt", "time kya hai", "kitne baje hain"):
        return "The time is: " + datetime.now().strftime("%I:%M %p, %d %B %Y")

    if text.startswith("note:") or text.startswith("note "):
        note = user_text.split(":", 1)[-1].strip() if ":" in user_text else user_text[5:].strip()
        if note:
            memory["notes"].append({"text": note, "at": datetime.now().isoformat()})
            save_memory(memory)
            return f"Note saved: {note}"
        return "What should I note down? For example: note: go to the gym tomorrow morning"

    if text in ("notes", "mere notes", "notes dikhao"):
        if not memory["notes"]:
            return "You have no notes yet."
        return "\n".join(f"{i + 1}. {n['text']}" for i, n in enumerate(memory["notes"]))

    if text.startswith("yaad rakho") or text.startswith("remember"):
        fact = user_text.split(" ", 2)[-1].strip()
        if fact and fact.lower() not in ("rakho",):
            memory["facts"].append(fact)
            save_memory(memory)
            return f"I will remember that: {fact}"
        return "What should I remember? For example: yaad rakho my favourite colour is blue"

    return None


def _is_ollama_running():
    """Startup check only. Returns True if Ollama answers on localhost."""
    try:
        import urllib.request
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=3) as resp:
            return resp.status == 200
    except Exception:
        return False


def main():
    memory = load_memory()
    last_reply = ""  # last smart / simple answer, for "isay pdf banao"
    # Style 4 (Big Splash), centred: Cyber chose this style and asked
    # for it to sit in the middle of the screen, not on the left.
    # Horizontal centre: every line is centred to the real terminal width.
    # Vertical centre: blank lines push the greeting about a quarter
    # of the screen down, so it sits in the middle, not at the top.
    # Note: a chat preview always looks left-aligned; the terminal code
    # below is what actually centres it on Cyber's screen.
    try:
        _size = shutil.get_terminal_size()
        _width, _rows = _size.columns, _size.lines
    except Exception:
        _width, _rows = 80, 24
    print("\n" * max(3, _rows // 4), end="")
    print(_peach("✨ SARA ✨".center(_width)))
    print()
    print(_peach(f"Hello {USER_NAME}!".center(_width)))
    print(_peach(f"I'm {ASSISTANT_NAME}, your personal assistant.".center(_width)))
    print()
    print(_peach("─────────────────────────────".center(_width)))
    print(_peach(f"How can I help you today, {USER_NAME}?".center(_width)))
    # No Ollama / Exit / Help lines at startup any more, as Cyber asked.
    # Ollama warning appears ONLY when Ollama is actually not running.
    if not _is_ollama_running():
        # Keep the warning short enough to centre at any normal width.
        print("Ollama is not running, only simple mode will work.".center(_width))
        print("Start Ollama for smart answers.".center(_width))
    print()

    while True:
        try:
            user_text = input(f"{USER_NAME}: ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{ASSISTANT_NAME}: Goodbye, {USER_NAME}! See you soon.")
            break

        if not user_text:
            continue
        if user_text.lower() in ("exit", "quit", "bye", "allah hafiz"):
            print(f"{ASSISTANT_NAME}: Goodbye, {USER_NAME}! See you soon.")
            break
        if user_text.lower() == "help":
            print(f"""{ASSISTANT_NAME}: These commands always work:
  time                  - show the current time
  note: <text>          - save a note
  notes                 - show all your notes
  yaad rakho <text>     - remember something about you
  notepad kholo         - open an app (chrome, calculator too)
  google search <text>  - search on Google
  chatgpt kholo         - open an AI site (muse, grok, gemini too)
  volume zyada / kam    - volume up / down
  brightness 70         - set brightness
  laptop band karo      - power off (asks to confirm first)
  whatsapp +92... : msg - send a WhatsApp message
  explain this          - explain your copied text in simple English
  isay pdf banao        - save the last answer as a PDF file
  isay word banao       - save the last answer as a Word (.docx) file
  pdf banao: <text>     - make a PDF from your own text
  exit                  - close the assistant
For anything else, just type it, and Ollama will answer.""")
            continue

        # PDF / Word: aakhri jawab ko file banao. Is ke baad last_reply
        # change nahi hota, taake dobara pdf/word banane par file ka
        # success message save na ho, asli jawab hi save ho.
        doc_result = document_reply(user_text, last_reply)
        if doc_result is not None:
            print(f"{_peach(ASSISTANT_NAME + ':')} {doc_result}\n")
            continue

        # Explain copied text in simple English: copy the text first,
        # then type "explain this". The clipboard text is sent to Ollama.
        if "explain this" in user_text.lower():
            if tools is None:
                print(f"{ASSISTANT_NAME}: tools.py is not in this folder.\n")
                continue
            copied = tools.get_clipboard_text()
            if not copied:
                print(f"{ASSISTANT_NAME}: First copy the text (Ctrl+C), then type this command again.\n")
                continue
            user_text = ("Explain this text in simple American English, "
                         "step by step:\n" + copied)

        reply = simple_reply(user_text, memory)
        if reply is None:
            reply = ask_assistant(user_text, memory)
        if reply is None:
            reply = (
                "Ollama is not running. For smart answers, install Ollama "
                "and run: ollama pull llama3.2:3b\n"
                "Then try again. Simple commands (time / note / notes) still work."
            )
        # Only remember real answers, not the "Ollama is not running" error.
        if not reply.startswith("Ollama is not running"):
            last_reply = reply
        print(f"{_peach(ASSISTANT_NAME + ':')} {reply}\n")


if __name__ == "__main__":
    main()
