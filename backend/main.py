import queue
import time

try:
    from .commands import process_command
    from .database import init_database
    from .engine import VoiceEngine
except ImportError:
    from commands import process_command
    from database import init_database
    from engine import VoiceEngine


EXIT_COMMANDS = {"exit", "stop", "quit", "goodbye", "bye"}


def is_exit_command(query):
    words = set((query or "").lower().split())
    return bool(words.intersection(EXIT_COMMANDS))


class HandsFreeAssistant:
    def __init__(self):
        init_database()
        self.voice = VoiceEngine()
        self.running = True

    def start(self):
        self.voice.speak("Veda AI is awake. Give me a command.")
        print("=" * 50)
        print("VEDA COMMAND MODE")
        print("Veda is awake. Speak any command directly.")
        print("Say 'exit' or 'stop' to close the assistant.")
        print("=" * 50)

        self.voice.listen_in_background()
        while self.running:
            try:
                phrase = self.voice.phrase_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            self.handle_phrase(phrase)

    def handle_phrase(self, phrase):
        phrase = (phrase or "").strip().lower()
        if not phrase:
            return

        if is_exit_command(phrase):
            self.shutdown()
            return

        self.voice.stop_background_listening()
        self.clear_pending_phrases()
        command = self.voice.strip_wake_phrase(phrase)

        if not command:
            command = self.voice.listen_once(retries=2, timeout=7, phrase_time_limit=8)

        if not command:
            self.voice.speak("I did not hear a command.")
            self.voice.listen_in_background()
            return

        if is_exit_command(command):
            self.shutdown()
            return

        self.run_command(command)
        if self.running:
            self.voice.listen_in_background()

    def run_command(self, command):
        try:
            process_command(command, self.voice)
        except SystemExit:
            self.running = False
        except Exception as exc:
            print(f"Command error: {exc}")
            self.voice.speak("Sorry boss, that command failed.")

    def clear_pending_phrases(self):
        while True:
            try:
                self.voice.phrase_queue.get_nowait()
            except queue.Empty:
                return

    def shutdown(self):
        self.running = False
        self.voice.stop_background_listening()
        self.voice.speak("Stopping Veda. Goodbye boss.")


def main():
    assistant = HandsFreeAssistant()
    try:
        assistant.start()
    except KeyboardInterrupt:
        assistant.shutdown()
    finally:
        time.sleep(0.2)


if __name__ == "__main__":
    main()
