"""Locate and grab pixels from the Club GG desktop window."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import mss
import pygetwindow as gw

WINDOW_TITLE_HINTS = ("clubgg", "club gg")

# Titles that must never match, even if they contain a hint above — e.g. our
# own web UI's browser tab is literally titled "Club GG Hand Reader".
WINDOW_TITLE_EXCLUDE = ("hand reader",)

WINDOW_CONFIG_PATH = Path(__file__).resolve().parent.parent / "window.json"


def list_window_titles() -> list[str]:
    """Return the distinct, non-empty titles of all currently open windows,
    for the user to pick the real Club GG window from explicitly."""
    seen: list[str] = []
    for w in gw.getAllWindows():
        title = (w.title or "").strip()
        if title and title not in seen:
            seen.append(title)
    return seen


def save_selected_title(title: str) -> None:
    with open(WINDOW_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump({"title": title}, f)


def load_selected_title() -> str | None:
    if not WINDOW_CONFIG_PATH.exists():
        return None
    with open(WINDOW_CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f).get("title")


def _table_name(title: str) -> str:
    """The stable prefix of a Club GG table title, e.g. "McJimmer's Ante"
    out of "McJimmer's Ante  - 0.25/0.50(0.10)". Club GG rewrites the part
    after the dash (blinds/pot/turn indicators) constantly, so an exact
    title match breaks within seconds of being selected."""
    return title.split(" - ")[0].strip().lower()


def find_window():
    """Return the pygetwindow Window for Club GG, or raise if not found/running.

    Prefers an explicitly user-selected title (see /calibrate's window
    picker) over guessing by substring, since title-based guessing can
    match the wrong window (e.g. our own browser tab). Matching is done by
    the stable table-name prefix rather than the full title, since Club GG
    keeps rewriting the rest of the title live."""
    selected = load_selected_title()
    if selected:
        wanted = _table_name(selected)
        for w in gw.getAllWindows():
            title = (w.title or "").strip()
            if title and _table_name(title) == wanted:
                return w
        raise RuntimeError(
            f"A janela selecionada ('{selected}') já não está aberta. "
            "Volta a Calibrar e escolhe a janela novamente."
        )

    for w in gw.getAllWindows():
        title = (w.title or "").strip().lower()
        if not title:
            continue
        if any(bad in title for bad in WINDOW_TITLE_EXCLUDE):
            continue
        if any(hint in title for hint in WINDOW_TITLE_HINTS):
            return w
    raise RuntimeError(
        "Não encontrei a janela do Club GG. Abre Calibrar e escolhe a janela "
        "certa na lista, ou confirma que a app está aberta e visível."
    )


def window_bbox(window) -> dict:
    """Return an mss-style bbox dict for the given window."""
    return {
        "left": window.left,
        "top": window.top,
        "width": window.width,
        "height": window.height,
    }


def grab(bbox: dict) -> np.ndarray:
    """Capture a region of the screen as a BGR numpy array."""
    with mss.mss() as sct:
        shot = sct.grab(bbox)
        frame = np.array(shot)  # BGRA
        return frame[:, :, :3]


def grab_window() -> np.ndarray:
    """Find the Club GG window and capture it in one call."""
    window = find_window()
    return grab(window_bbox(window))
