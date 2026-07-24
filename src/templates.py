"""Card recognition via template matching against a learned library.

Templates are stored as small PNGs in templates/<card>.png, e.g. templates/Ah.png
for the Ace of Hearts. Rank uses 2-9,T,J,Q,K,A; suit uses h,d,c,s.
"""
from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
RANKS = "23456789TJQKA"
SUITS = "hdcs"

# Empty-slot detection: a region whose content is essentially flat (no card dealt yet).
EMPTY_STD_THRESHOLD = 8.0


def all_labels() -> list[str]:
    return [f"{r}{s}" for r in RANKS for s in SUITS]


def is_valid_label(label: str) -> bool:
    return len(label) == 2 and label[0] in RANKS and label[1] in SUITS


def template_path(label: str) -> Path:
    return TEMPLATES_DIR / f"{label}.png"


def save_template(label: str, crop: np.ndarray) -> None:
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(template_path(label)), crop)


def load_templates() -> dict[str, np.ndarray]:
    templates: dict[str, np.ndarray] = {}
    if not TEMPLATES_DIR.exists():
        return templates
    for label in all_labels():
        path = template_path(label)
        if path.exists():
            img = cv2.imread(str(path))
            if img is not None:
                templates[label] = img
    return templates


def is_empty_slot(crop: np.ndarray) -> bool:
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    return float(np.std(gray)) < EMPTY_STD_THRESHOLD


def match_card(crop: np.ndarray, templates: dict[str, np.ndarray]) -> str | None:
    """Return the best-matching card label, or None if the slot looks empty
    or no template scores well enough."""
    if is_empty_slot(crop):
        return None
    if not templates:
        return None

    best_label = None
    best_score = -1.0
    for label, tmpl in templates.items():
        tmpl_resized = cv2.resize(tmpl, (crop.shape[1], crop.shape[0]))
        result = cv2.matchTemplate(crop, tmpl_resized, cv2.TM_CCOEFF_NORMED)
        score = float(result.max())
        if score > best_score:
            best_score = score
            best_label = label

    if best_score < 0.5:
        return None
    return best_label
