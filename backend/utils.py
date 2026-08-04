import glob
import os
import shutil
import webbrowser
import ctypes
import pyautogui
from requests import get
import psutil
from datetime import datetime
from urllib.parse import quote_plus, urlparse


def _existing_paths(*paths):
    return [path for path in paths if path and os.path.exists(path)]


def _matching_paths(*patterns):
    matches = []
    for pattern in patterns:
        matches.extend(glob.glob(pattern))
    return [path for path in matches if os.path.exists(path)]


def open_app(app):
    user_home = os.path.expanduser("~")
    local_app_data = os.environ.get("LOCALAPPDATA", os.path.join(user_home, "AppData", "Local"))
    roaming_app_data = os.environ.get("APPDATA", os.path.join(user_home, "AppData", "Roaming"))
    program_files = os.environ.get("PROGRAMFILES", r"C:\Program Files")
    program_files_x86 = os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)")

    apps = {
        "notepad": ["notepad.exe"],
        "wordpad": ["write.exe", "wordpad.exe"],
        "calculator": ["calc.exe", "calculator:"],
        "cmd": ["cmd.exe"],
        "paint": ["mspaint.exe"],
        "chrome": _existing_paths(
            os.path.join(program_files, "Google", "Chrome", "Application", "chrome.exe"),
            os.path.join(program_files_x86, "Google", "Chrome", "Application", "chrome.exe"),
            os.path.join(local_app_data, "Google", "Chrome", "Application", "chrome.exe"),
        ) + ["chrome.exe"],
        "code": _existing_paths(
            os.path.join(local_app_data, "Programs", "Microsoft VS Code", "Code.exe"),
            os.path.join(program_files, "Microsoft VS Code", "Code.exe"),
        ) + ["code.exe", "Code.exe"],
        "vscode": _existing_paths(
            os.path.join(local_app_data, "Programs", "Microsoft VS Code", "Code.exe"),
            os.path.join(program_files, "Microsoft VS Code", "Code.exe"),
        ) + ["code.exe", "Code.exe"],
        "spotify": _existing_paths(
            os.path.join(local_app_data, "Microsoft", "WindowsApps", "Spotify.exe"),
            os.path.join(local_app_data, "Spotify", "Spotify.exe"),
            os.path.join(roaming_app_data, "Spotify", "Spotify.exe"),
        ) + ["spotify.exe"],
        "zoom": _existing_paths(
            os.path.join(local_app_data, "Programs", "Zoom", "bin", "Zoom.exe"),
            os.path.join(roaming_app_data, "Zoom", "bin", "Zoom.exe"),
            os.path.join(program_files, "Zoom", "bin", "Zoom.exe"),
        ) + ["Zoom.exe"],
        "teams": _existing_paths(
            os.path.join(local_app_data, "Microsoft", "WindowsApps", "ms-teams.exe"),
            os.path.join(local_app_data, "Microsoft", "Teams", "current", "Teams.exe"),
        ) + ["ms-teams:", "Teams.exe"],
        "discord": _matching_paths(
            os.path.join(local_app_data, "Discord", "app-*", "Discord.exe"),
        ) + _existing_paths(
            os.path.join(local_app_data, "Discord", "Update.exe"),
            os.path.join(local_app_data, "Microsoft", "WindowsApps", "Discord.exe"),
        ) + ["Discord.exe"],
        "telegram": _matching_paths(
            os.path.join(program_files, "WindowsApps", "TelegramMessengerLLP.TelegramDesktop_*", "Telegram.exe"),
        ) + _existing_paths(
            os.path.join(program_files, "WindowsApps", "TelegramMessengerLLP.TelegramDesktop_t4vj0pshhgkwm", "Telegram.exe"),
            os.path.join(local_app_data, "Telegram Desktop", "Telegram.exe"),
            os.path.join(roaming_app_data, "Telegram Desktop", "Telegram.exe"),
        ) + ["Telegram.exe"],
        "winword": ["winword.exe"],
        "word": ["winword.exe"],
        "excel": ["excel.exe"],
        "powerpnt": ["powerpnt.exe"],
        "powerpoint": ["powerpnt.exe"],
        "outlook": ["outlook.exe"],
        "control": ["control.exe"],
    }

    candidates = apps.get(app.lower())
    if not candidates:
        return False

    for command in candidates:
        executable = command if os.path.exists(command) else shutil.which(command) or command
        try:
            os.startfile(executable)
            return True
        except Exception as e:
            print(f"Unable to open {app} with {command}: {e}")

    return False


def open_website(site):
    sites = {
        "youtube": "https://youtube.com",
        "google": "https://google.com",
        "gmail": "https://gmail.com",
        "github": "https://github.com",
        "whatsapp": "https://web.whatsapp.com",
        "amazon": "https://amazon.com",
        "wikipedia": "https://wikipedia.org",
        "stackoverflow": "https://stackoverflow.com",
        "reddit": "https://reddit.com",
        "twitter": "https://twitter.com",
        "x": "https://x.com",
        "linkedin": "https://linkedin.com",
        "facebook": "https://facebook.com",
        "instagram": "https://instagram.com",
        "netflix": "https://netflix.com",
        "hotstar": "https://hotstar.com",
        "flipkart": "https://flipkart.com",
        "snapchat": "https://web.snapchat.com",
        "canva": "https://canva.com",
        "chatgpt": "https://chatgpt.com",
        "openai": "https://openai.com",
        "gemini": "https://gemini.google.com",
    }

    site = (site or "").strip().lower()
    url = sites.get(site)
    if not url:
        url = website_url_from_text(site)
        if not url:
            return False

    return webbrowser.open(url)


def website_url_from_text(text):
    """Turn spoken website text into a browser URL."""
    text = (text or "").strip().lower()
    if not text:
        return ""

    text = " ".join(text.split())
    for prefix in ("the ", "website ", "site "):
        if text.startswith(prefix):
            text = text[len(prefix):].strip()

    spoken_domains = {
        "dot com": ".com",
        "dot in": ".in",
        "dot org": ".org",
        "dot net": ".net",
        "dot ai": ".ai",
        "dot io": ".io",
        " dot ": ".",
    }
    for spoken, symbol in spoken_domains.items():
        text = text.replace(spoken, symbol)

    text = text.replace(" ", "")
    if not text:
        return ""

    parsed = urlparse(text if "://" in text else f"https://{text}")
    host = parsed.netloc or parsed.path

    if "." not in host:
        host = f"{host}.com"

    if not host.replace(".", "").replace("-", "").isalnum():
        return f"https://www.google.com/search?q={quote_plus(text)}"

    return f"https://{host}"


def system_info(type_):
    if type_ == "ram":
        return psutil.virtual_memory().percent
    elif type_ == "cpu":
        return psutil.cpu_percent()
    elif type_ == "battery":
        try:
            return psutil.sensors_battery().percent
        except:
            return "N/A"
    elif type_ == "disk":
        # Windows-safe disk usage: use system drive (fallback to C:\)
        drive = os.getenv("SystemDrive", "C:\\")
        return psutil.disk_usage(drive).percent

    elif type_ == "system":
        return f"{os.name}, CPU {psutil.cpu_percent()}%, RAM {psutil.virtual_memory().percent}%"
    return "N/A"


def shutdown():
    os.system("shutdown /s /t 10")

def restart():
    os.system("shutdown /r /t 10")

def lock():
    ctypes.windll.user32.LockWorkStation()


def screenshot():
    filename = f"screenshot_{datetime.now().strftime('%H%M%S')}.png"
    try:
        pyautogui.screenshot().save(filename)
        return filename
    except Exception as e:
        print(f"Unable to take screenshot: {e}")
        return ""


def ip_address():
    try:
        return get('https://api.ipify.org').text
    except Exception as e:
        print(f"Unable to fetch IP address: {e}")
        return "Unable to fetch IP address"


def play_youtube(song):
    try:
        import pywhatkit as kit
    except Exception as e:
        print(f"pywhatkit unavailable: {e}")
        return False

    try:
        kit.playonyt(song)
        return True
    except Exception as e:
        print(f"Failed to play YouTube: {e}")
        return webbrowser.open(f"https://www.youtube.com/results?search_query={song.replace(' ', '+')}")


def open_folder(folder_name):
    """Open system folders"""
    folder_paths = {
        "downloads": os.path.join(os.path.expanduser("~"), "Downloads"),
        "documents": os.path.join(os.path.expanduser("~"), "Documents"),
        "desktop": os.path.join(os.path.expanduser("~"), "Desktop"),
        "pictures": os.path.join(os.path.expanduser("~"), "Pictures"),
        "music": os.path.join(os.path.expanduser("~"), "Music"),
        "videos": os.path.join(os.path.expanduser("~"), "Videos")
    }
    
    folder = folder_paths.get(folder_name.lower())
    if folder and os.path.exists(folder):
        os.startfile(folder)
        return True
    return False
