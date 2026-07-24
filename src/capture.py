"""Locate and grab pixels from the Club GG desktop window.

Club GG's window title changes constantly (blinds, pot size, and even the
table name itself when you switch tables), so identifying "the Club GG
window" by title text is unreliable. Instead we identify it by the
underlying process (e.g. "ClubGG.exe") once, and always grab whatever
window that process currently owns.
"""
from __future__ import annotations

import ctypes
import json
from ctypes import wintypes
from pathlib import Path

import numpy as np
import mss
import psutil
import pygetwindow as gw

# Titles that must never match — our own web UI's browser tab can be
# literally titled "Club GG Hand Reader", so it must never be picked.
WINDOW_TITLE_EXCLUDE = ("hand reader",)

WINDOW_CONFIG_PATH = Path(__file__).resolve().parent.parent / "window.json"


def _hwnd_of(w) -> int | None:
    return getattr(w, "_hWnd", None)


def _process_name_for_window(w) -> str | None:
    """Best-effort executable name (e.g. 'ClubGG.exe') owning this window."""
    hwnd = _hwnd_of(w)
    if hwnd is None:
        return None
    pid = wintypes.DWORD()
    ctypes.windll.user32.GetWindowThreadProcessId(wintypes.HWND(hwnd), ctypes.byref(pid))
    if not pid.value:
        return None
    try:
        return psutil.Process(pid.value).name()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None


def _visible_windows():
    for w in gw.getAllWindows():
        title = (w.title or "").strip()
        if not title:
            continue
        if any(bad in title.lower() for bad in WINDOW_TITLE_EXCLUDE):
            continue
        if _hwnd_of(w) is None:
            continue
        yield w


def list_windows() -> list[dict]:
    """Currently open windows as {hwnd, title}, for the user to pick the real
    Club GG window from explicitly. `hwnd` (not the title, which Club GG
    rewrites many times per second) is what identifies the window."""
    return [{"hwnd": _hwnd_of(w), "title": w.title} for w in _visible_windows()]


def save_selected_window(hwnd: int) -> None:
    """Resolve the window with this exact handle to its owning process, and
    remember that process — matching by title (even done immediately) is
    unreliable because Club GG's title can already have changed by the time
    the lookup runs."""
    match = next((w for w in _visible_windows() if _hwnd_of(w) == hwnd), None)
    if match is None:
        raise RuntimeError("Essa janela já não está aberta. Atualiza a lista e escolhe outra vez.")

    process = _process_name_for_window(match)
    with open(WINDOW_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump({"title": match.title, "process": process}, f)


def load_selected() -> dict | None:
    if not WINDOW_CONFIG_PATH.exists():
        return None
    with open(WINDOW_CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def find_window():
    """Return the pygetwindow Window for Club GG, or raise if not found/running."""
    selected = load_selected()
    if not selected:
        raise RuntimeError(
            "Ainda não escolheste a janela do Club GG. Abre Calibrar e "
            "seleciona-a na lista."
        )

    process = selected.get("process")
    if process:
        for w in _visible_windows():
            if _process_name_for_window(w) == process:
                return w
        raise RuntimeError(
            f"Não encontrei nenhuma janela do programa '{process}' aberta. "
            "Confirma que o Club GG está aberto, ou volta a Calibrar e "
            "escolhe a janela novamente."
        )

    # Fallback for an older window.json saved before process-based matching.
    title = selected.get("title", "")
    for w in _visible_windows():
        if w.title == title:
            return w
    raise RuntimeError(
        f"A janela selecionada ('{title}') já não está aberta. "
        "Volta a Calibrar e escolhe a janela novamente."
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
