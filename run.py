"""Run entrypoint for Veda.

Usage:
    python run.py          # hands-free voice assistant
    python run.py --web    # Flask web dashboard
"""

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Veda")
    parser.add_argument("--web", action="store_true", help="start the Flask web dashboard")
    args = parser.parse_args()

    if args.web:
        from backend.web_app import app

        app.run(debug=False, port=5000, use_reloader=False)
    else:
        from backend.main import main

        main()
