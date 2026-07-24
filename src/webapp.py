"""Local web server: polls the Club GG table in the background and serves a
polished UI + JSON API on http://127.0.0.1:5000.

Also serves the web-based calibration ("/calibrate") and card-teaching
("/teach") tools, so the whole setup can be done from the browser instead
of a terminal + native OpenCV windows.
"""
from __future__ import annotations

import threading
import time
import webbrowser
from pathlib import Path

import cv2
from flask import Flask, Response, jsonify, request

from src.capture import grab_window, grab_by_hwnd, list_windows, save_selected_window, load_selected
from src.regions import load_regions, save_regions, crop
from src.templates import load_templates, save_template, is_valid_label
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


def _png_response(frame) -> Response:
    ok, buf = cv2.imencode(".png", frame)
    if not ok:
        return Response(status=500)
    return Response(buf.tobytes(), mimetype="image/png")


# --- main dashboard -----------------------------------------------------

@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.get("/api/state")
def api_state():
    with _lock:
        return jsonify(_latest_state)


# --- calibration (draw regions on a live screenshot) --------------------

@app.get("/calibrate")
def calibrate_page():
    return app.send_static_file("calibrate.html")


@app.get("/api/windows")
def api_windows():
    selected = load_selected()
    return jsonify({"windows": list_windows(), "selected": (selected or {}).get("title")})


@app.get("/api/window-preview")
def api_window_preview():
    hwnd = request.args.get("hwnd", type=int)
    if hwnd is None:
        return jsonify({"error": "hwnd em falta."}), 400
    try:
        frame = grab_by_hwnd(hwnd)
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 409
    return _png_response(frame)


@app.post("/api/select-window")
def api_select_window():
    data = request.get_json(force=True) or {}
    hwnd = data.get("hwnd")
    if not isinstance(hwnd, int):
        return jsonify({"error": "hwnd em falta ou inválido."}), 400
    try:
        save_selected_window(hwnd)
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 409
    return jsonify({"ok": True})


@app.get("/api/screenshot")
def api_screenshot():
    try:
        frame = grab_window()
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 409
    return _png_response(frame)


@app.get("/api/regions")
def api_get_regions():
    try:
        regions = load_regions()
    except FileNotFoundError:
        regions = {}
    return jsonify(regions)


@app.post("/api/regions")
def api_save_regions():
    data = request.get_json(force=True) or {}
    raw_regions = data.get("regions", {})

    clean: dict[str, list[int]] = {}
    for name, box in raw_regions.items():
        if isinstance(box, list) and len(box) == 4 and all(isinstance(v, (int, float)) for v in box):
            clean[name] = [int(v) for v in box]

    save_regions(clean)
    return jsonify({"ok": True, "count": len(clean)})


# --- teaching (label card crops from a live screenshot) ------------------

@app.get("/teach")
def teach_page():
    return app.send_static_file("teach.html")


@app.get("/api/card-crop")
def api_card_crop():
    name = request.args.get("region", "")
    try:
        regions = load_regions()
    except FileNotFoundError:
        return jsonify({"error": "Ainda não calibraste as regiões."}), 409

    if name not in regions:
        return jsonify({"error": f"Região '{name}' não existe."}), 404

    try:
        frame = grab_window()
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 409

    card_crop = crop(frame, tuple(regions[name]))
    return _png_response(card_crop)


@app.post("/api/teach")
def api_teach():
    data = request.get_json(force=True) or {}
    name = data.get("region", "")
    label = (data.get("label") or "").strip()

    if not is_valid_label(label):
        return jsonify({"error": f"Etiqueta inválida: '{label}'"}), 400

    try:
        regions = load_regions()
    except FileNotFoundError:
        return jsonify({"error": "Ainda não calibraste as regiões."}), 409

    if name not in regions:
        return jsonify({"error": f"Região '{name}' não existe."}), 404

    try:
        frame = grab_window()
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 409

    card_crop = crop(frame, tuple(regions[name]))
    save_template(label, card_crop)
    return jsonify({"ok": True, "label": label})


def main() -> None:
    thread = threading.Thread(target=_poll_loop, daemon=True)
    thread.start()

    url = f"http://{HOST}:{PORT}"
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()

    print(f"A servir em {url} (Ctrl+C para parar)")
    app.run(host=HOST, port=PORT, debug=False)


if __name__ == "__main__":
    main()
