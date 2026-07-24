"""Local web server: polls the Club GG table in the background and serves a
polished UI + JSON API on http://127.0.0.1:5000."""
from __future__ import annotations

import threading
import time
import webbrowser
from pathlib import Path

from flask import Flask, jsonify

from src.regions import load_regions
from src.templates import load_templates
from src.state import build_state, seat_numbers_from_regions

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
POLL_SECONDS = 1.0
HOST, PORT = "127.0.0.1", 5000

app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="")

_lock = threading.Lock()
_latest_state: dict = {
    "hole_cards": [],
    "board_cards": [],
    "hand": None,
    "seats": [],
    "error": "A iniciar...",
}


def _empty_state(error: str) -> dict:
    return {"hole_cards": [], "board_cards": [], "hand": None, "seats": [], "error": error}


def _publish(state: dict) -> None:
    with _lock:
        _latest_state.clear()
        _latest_state.update(state)


def _poll_loop() -> None:
    while True:
        try:
            regions = load_regions()
        except FileNotFoundError as exc:
            _publish(_empty_state(str(exc)))
            time.sleep(POLL_SECONDS)
            continue

        seats = seat_numbers_from_regions(regions)
        templates = load_templates()  # pick up newly taught cards without restarting

        try:
            state = build_state(regions, templates, seats)
            state["error"] = None
        except RuntimeError as exc:
            state = _empty_state(str(exc))

        _publish(state)
        time.sleep(POLL_SECONDS)


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.get("/api/state")
def api_state():
    with _lock:
        return jsonify(_latest_state)


def main() -> None:
    thread = threading.Thread(target=_poll_loop, daemon=True)
    thread.start()

    url = f"http://{HOST}:{PORT}"
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()

    print(f"A servir em {url} (Ctrl+C para parar)")
    app.run(host=HOST, port=PORT, debug=False)


if __name__ == "__main__":
    main()
