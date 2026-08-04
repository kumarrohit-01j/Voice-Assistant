import datetime
import json
import os
import random
import sys
import webbrowser
from urllib.parse import quote_plus

import pyautogui

try:
    from .database import save_command
    from .recipe import handle_recipe
    from .utils import lock, open_app, open_folder, open_website, system_info
except ImportError:
    from database import save_command
    from recipe import handle_recipe
    from utils import lock, open_app, open_folder, open_website, system_info


BASE_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.normpath(os.path.join(BASE_DIR, ".."))

APP_ALIASES = {
    "notepad": ("notepad",),
    "calculator": ("calculator", "calc"),
    "chrome": ("chrome",),
    "vscode": ("vscode", "vs code", "code"),
    "spotify": ("spotify",),
    "camera": ("camera",),
    "word": ("word", "winword"),
    "wordpad": ("wordpad",),
    "excel": ("excel",),
    "powerpoint": ("powerpoint", "power point", "powerpnt"),
    "paint": ("paint", "mspaint"),
    "cmd": ("cmd", "command prompt"),
    "zoom": ("zoom",),
    "teams": ("teams", "microsoft teams"),
    "discord": ("discord",),
    "telegram": ("telegram",),
    "outlook": ("outlook",),
    "control": ("control panel",),
}

WEBSITE_ALIASES = {
    "youtube": ("youtube",),
    "google": ("google",),
    "gmail": ("gmail",),
    "github": ("github",),
    "whatsapp": ("whatsapp", "whatsapp web"),
    "instagram": ("instagram",),
    "amazon": ("amazon",),
    "wikipedia": ("wikipedia",),
    "stackoverflow": ("stackoverflow", "stack overflow"),
    "reddit": ("reddit",),
    "twitter": ("twitter",),
    "x": ("x",),
    "linkedin": ("linkedin",),
    "facebook": ("facebook",),
    "netflix": ("netflix",),
    "hotstar": ("hotstar",),
    "flipkart": ("flipkart",),
    "snapchat": ("snapchat",),
    "canva": ("canva",),
    "chatgpt": ("chatgpt", "chat gpt"),
    "openai": ("openai", "open ai"),
    "gemini": ("gemini",),
}

EXIT_COMMANDS = {
    "close app",
    "goodbye",
    "bye",
    "stop",
    "quit",
    "exit",
    "shutdown tilu",
    "shutdown veda",
}


def _speak(voice, text):
    voice.speak(text)
    return True


def _clean_query(query):
    return " ".join((query or "").lower().strip().split())


def _remove_leading_words(query, words):
    cleaned = query
    for word in words:
        if cleaned.startswith(word + " "):
            cleaned = cleaned[len(word):].strip()
    return cleaned


def extract_music_search_term(query):
    if not query:
        return ""

    search_term = _clean_query(query)
    remove_phrases = [
        "play music on youtube",
        "play song on youtube",
        "play music",
        "play song",
        "on youtube",
        "youtube",
        "please",
        "play",
    ]

    for phrase in remove_phrases:
        search_term = search_term.replace(phrase, " ")

    return " ".join(search_term.split())


def ask_and_play_music(voice, query=None):
    search_term = extract_music_search_term(query)

    if not search_term:
        if getattr(voice, "web_mode", False):
            voice.pending_action = "play_youtube_music"
            return _speak(voice, "Which song would you like to play?")

        voice.speak("Which song would you like to play?")
        search_term = voice.listen_once()

    if not search_term:
        return _speak(voice, "Sorry boss, I did not catch the song name.")

    try:
        import pywhatkit as kit

        voice.speak(f"Playing {search_term} on YouTube")
        kit.playonyt(search_term.strip())
    except Exception as exc:
        print("Music error:", exc)
        webbrowser.open(
            "https://www.youtube.com/results?search_query="
            + quote_plus(search_term.strip())
        )
        voice.speak(f"Opening YouTube search for {search_term}")

    return True


def search_google(query, voice):
    term = _clean_query(query)
    for phrase in ("search google for", "google search for", "search for", "search", "google"):
        if term.startswith(phrase):
            term = term[len(phrase):].strip()
            break

    if not term:
        if getattr(voice, "web_mode", False):
            voice.pending_action = "google_search"
            return _speak(voice, "What should I search for?")

        voice.speak("What should I search for?")
        term = voice.listen_once()

    if not term:
        return _speak(voice, "Sorry boss, I did not catch the search.")

    voice.speak(f"Searching for {term}")
    webbrowser.open("https://www.google.com/search?q=" + quote_plus(term))
    return True


def _open_named_app(query, voice):
    for app_name, aliases in APP_ALIASES.items():
        if any(query == f"open {alias}" or query.endswith(f" open {alias}") for alias in aliases):
            if app_name == "camera":
                os.startfile("microsoft.windows.camera:")
                return _speak(voice, "Opening Camera")

            if open_app(app_name):
                return _speak(voice, f"Opening {aliases[0].title()}")

            return _speak(voice, f"Sorry boss, I could not open {aliases[0]}.")

    return False


def _open_named_website(query, voice):
    for site_name, aliases in WEBSITE_ALIASES.items():
        if any(query == f"open {alias}" for alias in aliases):
            if open_website(site_name):
                return _speak(voice, f"Opening {aliases[0].title()}")
            return _speak(voice, f"Sorry boss, I could not open {aliases[0]}.")

    if query.startswith("open website "):
        site = query.replace("open website ", "", 1).strip()
        if open_website(site):
            return _speak(voice, f"Opening {site}")

    return False


def _save_session():
    session_path = os.path.join(ROOT_DIR, "session_data.json")
    with open(session_path, "w", encoding="utf-8") as handle:
        json.dump({"last_session": str(datetime.datetime.now())}, handle)


def _take_screenshot(voice):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(ROOT_DIR, f"screenshot_{timestamp}.png")
    try:
        pyautogui.screenshot().save(filename)
    except Exception as exc:
        print("Screenshot error:", exc)
        return _speak(voice, "Sorry boss, I could not take a screenshot.")

    return _speak(voice, f"Screenshot saved as {os.path.basename(filename)}")


def process_command(query, voice):
    query = _clean_query(query)
    if not query:
        return _speak(voice, "Please give me a command.")

    save_command(query)
    print("Processed command:", query)

    if query in {"tillu", "tilu", "hey tillu", "hey tilu", "hey veda", "hello veda", "hi veda"}:
        return _speak(voice, "Yes boss, I am here.")

    if "who are you" in query or "your name" in query:
        return _speak(voice, "I am Veda, your personal AI voice assistant.")

    if "help" in query or "what can you do" in query:
        return _speak(
            voice,
            "I can open apps and websites, play music, search Google, manage windows, take notes, and show system information.",
        )

    if any(phrase == query or phrase in query for phrase in EXIT_COMMANDS):
        _save_session()
        voice.speak("Goodbye boss. Veda is shutting down.")
        if getattr(voice, "web_mode", False):
            return True
        sys.exit()

    if query == "shutdown" or query == "shutdown computer":
        voice.speak("Shutting down your computer")
        os.system("shutdown /s /t 0")
        return True

    if query == "restart" or query == "restart computer":
        voice.speak("Restarting your computer")
        os.system("shutdown /r /t 0")
        return True

    if "lock" in query:
        lock()
        return _speak(voice, "Locking your computer")

    if _open_named_app(query, voice):
        return True

    if _open_named_website(query, voice):
        return True

    if query.startswith("open "):
        target = query.replace("open ", "", 1).strip()
        if open_website(target):
            return _speak(voice, f"Opening {target}")

    if "recipe" in query or query.startswith("make "):
        if handle_recipe(query, voice):
            return True
        return search_google(query + " recipe", voice)

    if query.startswith("play ") or "play music" in query or "play song" in query:
        return ask_and_play_music(voice, query)

    if "search" in query or query.startswith("google "):
        return search_google(query, voice)

    for folder in ("downloads", "desktop", "documents", "pictures", "music", "videos"):
        if query == f"open {folder}":
            if open_folder(folder):
                return _speak(voice, f"Opening {folder.title()}")
            return _speak(voice, f"Sorry boss, I could not open {folder}.")

    if "file explorer" in query:
        os.startfile(os.path.expanduser("~"))
        return _speak(voice, "Opening File Explorer")

    if "screenshot" in query:
        return _take_screenshot(voice)

    browser_hotkeys = {
        "new tab": (("ctrl", "t"), "Opened new tab"),
        "close tab": (("ctrl", "w"), "Closed tab"),
        "reopen tab": (("ctrl", "shift", "t"), "Reopened tab"),
    }
    for phrase, (keys, response) in browser_hotkeys.items():
        if phrase in query:
            pyautogui.hotkey(*keys)
            return _speak(voice, response)

    window_hotkeys = {
        "minimize window": (("win", "down"), "Minimized window"),
        "maximize window": (("win", "up"), "Maximized window"),
        "switch window": (("alt", "tab"), "Switched window"),
        "close window": (("alt", "f4"), "Closed window"),
        "task manager": (("ctrl", "shift", "esc"), "Opening Task Manager"),
    }
    for phrase, (keys, response) in window_hotkeys.items():
        if phrase in query:
            pyautogui.hotkey(*keys)
            return _speak(voice, response)

    volume_keys = {
        "volume up": ("volumeup", "Volume increased"),
        "volume down": ("volumedown", "Volume decreased"),
        "mute": ("volumemute", "Volume muted"),
    }
    for phrase, (key, response) in volume_keys.items():
        if phrase in query:
            pyautogui.press(key)
            return _speak(voice, response)

    if "time" in query:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        return _speak(voice, f"The time is {current_time}")

    if "date" in query:
        today = datetime.datetime.now().strftime("%d %B %Y")
        return _speak(voice, f"Today's date is {today}")

    for info_type in ("battery", "cpu", "ram", "disk", "system"):
        if info_type in query:
            value = system_info(info_type)
            if info_type == "system":
                return _speak(voice, f"System info: {value}")
            if value == "N/A":
                return _speak(voice, f"{info_type.title()} information is not available.")
            return _speak(voice, f"{info_type.title()} usage is {value} percent")

    if query.startswith("take note") or query.startswith("note "):
        note = _remove_leading_words(query, ("take note", "note")).strip()
        if not note:
            return _speak(voice, "What should I write in the note?")

        note_file = os.path.join(ROOT_DIR, "notes.txt")
        with open(note_file, "a", encoding="utf-8") as handle:
            handle.write(note + "\n")
        return _speak(voice, "Note saved")

    if "weather" in query or "vedar" in query:
        webbrowser.open("https://www.google.com/search?q=weather")
        return _speak(voice, "Opening weather")

    if "joke" in query:
        jokes = [
            "Why do programmers hate nature? It has too many bugs.",
            "Why was the computer cold? Because it forgot to close windows.",
            "Why do Java developers wear glasses? Because they cannot see sharp.",
        ]
        return _speak(voice, random.choice(jokes))

    return _speak(voice, "Sorry boss, I did not understand that command.")
