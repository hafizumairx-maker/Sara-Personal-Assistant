"""
Setup check for the free laptop assistant (Windows, Version 1).

Put this file in the SAME folder as main.py, then run:
    python check.py
If `python` does not work, try:
    py check.py

It only checks things - it installs nothing and changes nothing.
Copy the whole output and send it to your assistant if anything
says MISSING or FAIL; that output tells exactly which step is stuck.

No extra packages needed: this file uses only Python's standard library,
so it works even before `pip install requests`.
"""

import json
import os
import sys
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OLLAMA_TAGS_URL = "http://localhost:11434/api/tags"
WANTED_MODEL = "llama3.2:3b"


def line(status, text):
    print(f"[{status}] {text}")


def main():
    print("Assistant setup check")
    print("---------------------")

    # 1. Python itself
    line("OK", f"Python is running: {sys.version.split()[0]}")

    # 2. main.py in the same folder?
    main_path = os.path.join(BASE_DIR, "main.py")
    if os.path.exists(main_path):
        line("OK", "main.py is in this folder.")
    else:
        line("MISSING", "main.py is NOT in this folder. "
             "Put check.py in the same folder as main.py.")

    # 3. requests package (needed by main.py for smart answers)
    try:
        import requests  # noqa: F401
        line("OK", "requests is installed (pip install requests is done).")
    except ImportError:
        line("MISSING", "requests is NOT installed. Run: "
             "pip install requests")

    # 4. Ollama running? Which models are downloaded?
    try:
        with urllib.request.urlopen(OLLAMA_TAGS_URL, timeout=5) as resp:
            data = json.load(resp)
        models = [m.get("name", "") for m in data.get("models", [])]
        line("OK", "Ollama is running.")
        if any(WANTED_MODEL in m for m in models):
            line("OK", f"Model {WANTED_MODEL} is downloaded - you will get smart answers.")
        elif models:
            line("OK", f"A model is downloaded ({', '.join(models)}) - "
                 "you will get smart answers if MODEL in main.py is set to that name.")
        else:
            line("MISSING", f"No model is downloaded. "
                 "Run: ollama pull llama3.2:3b")
    except Exception:
        line("MISSING", "Ollama is NOT running or NOT installed. "
             "First install Ollama from ollama.com, then run "
             "ollama pull llama3.2:3b. "
             "Note: main.py still works in simple mode without Ollama - "
             "time / note / notes work, only smart answers do not.")

    print("---------------------")
    print("If everything is OK, run: python main.py")
    print("Then test it: time -- note: test -- notes")


if __name__ == "__main__":
    main()
