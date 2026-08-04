import queue
import re
import threading
import time

import pyttsx3
import speech_recognition as sr


class VoiceEngine:
    """English-only Voice Engine (Veda / TILU assistant)"""

    def __init__(self, web_mode=False):

        self.web_mode = web_mode
        self.last_response = ""
        self.pending_action = None
        self.is_speaking = False
        self.wake_active = False

        self.recognizer = sr.Recognizer()
        self.speech_lock = threading.Lock()

        self.phrase_queue = queue.Queue()
        self._listening = False
        self._background_thread = None

        self.engine = None if self.web_mode else self._init_tts()

    # ================= TTS INIT =================

    def _init_tts(self):

        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", 175)
            engine.setProperty("volume", 0.95)

            # FORCE ENGLISH VOICE ONLY
            try:
                voices = engine.getProperty("voices")

                for voice in voices:
                    name = f"{getattr(voice, 'name', '')}".lower()

                    if "english" in name or "en" in name:
                        engine.setProperty("voice", voice.id)
                        break

            except Exception:
                pass

            return engine

        except Exception as e:
            print("TTS init error:", e)
            return None

    # ================= SPEAK =================

    def speak(self, text):

        self.last_response = text

        print("Veda:", text)

        if self.web_mode:
            try:
                import pyautogui
                size = pyautogui.size()
                pyautogui.moveTo(size.width // 2, size.height // 2, duration=0.05)
                pyautogui.scroll(120)
                time.sleep(0.08)
                pyautogui.scroll(-40)
            except Exception as exc:
                print("Command feedback error:", exc)
            return

        if not self.engine:
            return

        with self.speech_lock:
            try:
                self.is_speaking = True
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print("TTS error:", e)
            finally:
                self.is_speaking = False

    # ================= WAKE WORD =================

    def is_wake_phrase(self, query):

        query = (query or "").lower()

        return "veda" in query or "tilu" in query

    def strip_wake_phrase(self, query):

        cleaned = re.sub(
            r"\b(hey\s+)?(veda|tilu)\b",
            "",
            query or "",
            flags=re.IGNORECASE
        )

        return " ".join(cleaned.split()).strip()

    # ================= LISTEN ONCE (ENGLISH ONLY) =================

    def listen_once(
        self,
        retries=2,
        timeout=6,
        phrase_time_limit=7,
        language="en-US"
    ):

        for attempt in range(retries + 1):

            while self.is_speaking:
                time.sleep(0.1)

            try:

                with sr.Microphone() as source:

                    print("Listening...")

                    self.recognizer.adjust_for_ambient_noise(
                        source,
                        duration=0.5
                    )

                    audio = self.recognizer.listen(
                        source,
                        timeout=timeout,
                        phrase_time_limit=phrase_time_limit,
                    )

                query = self.recognizer.recognize_google(
                    audio,
                    language="en-US"
                )

                query = query.lower().strip()

                print("You said:", query)

                return query

            except sr.WaitTimeoutError:
                print("No speech detected.")

            except sr.UnknownValueError:
                print("Could not understand speech.")

            except sr.RequestError as e:
                print("Speech API error:", e)
                return ""

            except Exception as e:
                print("Microphone error:", e)
                return ""

            if attempt < retries:
                self.speak("Please repeat.")

        return ""

    # ================= BACKGROUND LISTEN =================

    def listen_in_background(self, language="en-US"):

        if self._listening:
            return self._background_thread

        self._listening = True

        def run():

            while self._listening:

                query = self.listen_once(
                    retries=0,
                    timeout=5,
                    phrase_time_limit=7,
                    language="en-US"
                )

                if query:
                    self.phrase_queue.put(query)

                time.sleep(0.1)

        self._background_thread = threading.Thread(
            target=run,
            daemon=True
        )

        self._background_thread.start()

        return self._background_thread

    def stop_background_listening(self):

        self._listening = False