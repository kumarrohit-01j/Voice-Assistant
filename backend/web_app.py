import os
import sys

from flask import Flask, jsonify, render_template, request

BASE_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.normpath(os.path.join(BASE_DIR, '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.database import get_history, init_database
from backend.engine import VoiceEngine
from backend.commands import ask_and_play_music, process_command, search_google

TEMPLATE_DIR = os.path.normpath(os.path.join(BASE_DIR, '..', 'frontend', 'templates'))
STATIC_DIR = os.path.normpath(os.path.join(BASE_DIR, '..', 'frontend', 'static'))

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
init_database()

voice = VoiceEngine(web_mode=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/history')
def history():
    data = get_history()
    return jsonify([
        {'command': command, 'timestamp': timestamp}
        for command, timestamp in data
    ])


@app.route('/api/status')
def status():
    return jsonify({'status': 'ready', 'message': 'Veda web control is running.'})


@app.route('/api/command', methods=['POST'])
def command_route():
    data = request.get_json(silent=True) or {}
    command_text = (data.get('command') or '').strip()

    if not command_text:
        return jsonify({'status': 'error', 'message': 'Please provide a command.'}), 400

    try:
        voice.last_response = ""

        if getattr(voice, "pending_action", None) == "play_youtube_music":
            voice.pending_action = None
            ask_and_play_music(voice, command_text)
        elif getattr(voice, "pending_action", None) == "google_search":
            voice.pending_action = None
            search_google(command_text, voice)
        else:
            process_command(command_text, voice)

    except Exception as exc:
        return jsonify({
            'status': 'error',
            'message': f'Command failed: {exc}',
            'command': command_text,
        }), 500

    return jsonify({
        'status': 'ok',
        'message': voice.last_response or f'Processed command: {command_text}',
        'command': command_text,
        'awaiting': getattr(voice, "pending_action", None),
    })


if __name__ == '__main__':
    app.run(debug=False, port=5000, use_reloader=False)

