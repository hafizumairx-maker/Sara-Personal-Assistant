"""
Optional voice mode - 100% free.
Note: sunne ke liye internet chahiye (Google speech recognition),
bolna (pyttsx3) offline hai.
Install once:  pip install SpeechRecognition pyttsx3 pyaudio
  - Windows: pyaudio install mein dikkat ho to: pip install pipwin && pipwin install pyaudio
  - Is file ko chalane se pehle main.py wala Ollama setup kar lo,
    warna ye sirf simple commands (time / note) bol kar jawab dega.

Run:  python voice.py
Bolna shuru karo, "exit" bolne par band ho jayega.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import speech_recognition as sr
    import pyttsx3
except ImportError as e:
    print("First install this: pip install SpeechRecognition pyttsx3 pyaudio")
    print("Error:", e)
    raise SystemExit(1)

from main import ASSISTANT_NAME, ask_assistant, load_memory, simple_reply

engine = pyttsx3.init()
engine.setProperty("rate", 175)


def speak(text):
    print(f"{ASSISTANT_NAME}: {text}")
    engine.say(text)
    engine.runAndWait()


def listen(recognizer, mic):
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print("Listening... speak now:")
        audio = recognizer.listen(source, timeout=10, phrase_time_limit=20)
    return recognizer.recognize_google(audio, language="en-US")


def main():
    memory = load_memory()
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    speak("Hello! I am listening. Say something, or say exit to stop.")

    while True:
        try:
            user_text = listen(recognizer, mic)
        except Exception:
            speak("Sorry, I did not understand that. Please say it again.")
            continue

        print("You said:", user_text)
        if user_text.strip().lower() in ("exit", "quit", "bye", "allah hafiz"):
            speak("Goodbye! See you soon.")
            break

        reply = simple_reply(user_text, memory)
        if reply is None:
            reply = ask_assistant(user_text, memory)
        if reply is None:
            reply = "Ollama is not running. Start Ollama first, then try again."
        speak(reply)


if __name__ == "__main__":
    main()
