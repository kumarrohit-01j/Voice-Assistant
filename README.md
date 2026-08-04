# Veda Project

## Structure

- `backend/` - Python backend code
  - `main.py` - assistant startup file
  - `web_app.py` - Flask web interface
  - `engine.py` - voice and wake detection
  - `commands.py` - assistant command handlers
  - `database.py` - sqlite command history storage
  - `utils.py` - system utility functions

- `frontend/` - web UI files
  - `index.html` - frontend HTML page
  - `static/css/style.css` - styles
  - `static/js/app.js` - frontend logic

- `run.py` - root launcher for running the assistant from the project root
- `notes.txt` - user notes file
- `jony_data.db` - SQLite history database

## Run

- Install dependencies in a virtual environment if needed: `pip install -r requirements.txt`
- Start the hands-free voice assistant: `python run.py`
- Veda wakes up immediately. Speak your command directly.
- Say `exit` or `stop` to close the hands-free assistant.
- Start the web dashboard and command portal: `python run.py --web`
- Or start the web dashboard directly: `python web.py`
- The web app will open on the Flask port (default `http://127.0.0.1:5000`).
- Use the command box to run Veda commands from the website.
