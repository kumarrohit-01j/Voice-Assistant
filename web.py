"""Start the Veda web dashboard.

Usage:
    python web.py
"""

from backend.web_app import app


if __name__ == "__main__":
    app.run(debug=False, port=5000, use_reloader=False)
