"""Locate and grab pixels from the Club GG desktop window."""
from __future__ import annotations

import numpy as np
import mss
import pygetwindow as gw

WINDOW_TITLE_HINTS = ("clubgg", "club gg")


def find_window():
    """Return the pygetwindow Window for Club GG, or raise if not found/running."""
    for w in gw.getAllWindows():
        title = (w.title or "").strip().lower()
        if any(hint in title for hint in WINDOW_TITLE_HINTS):
            return w
    raise RuntimeError(
        "Não encontrei a janela do Club GG. Confirma que a app está aberta "
        "e visível (não minimizada)."
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
