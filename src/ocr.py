"""Read numeric text (stack sizes, blinds) from a cropped table region."""
from __future__ import annotations

import re

import cv2
import numpy as np
import pytesseract

# On Windows, set this if Tesseract isn't on PATH, e.g.:
# TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
TESSERACT_CMD: str | None = None

if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

_NUMERIC_CONFIG = "--psm 7 -c tessedit_char_whitelist=0123456789.,KkMm"


def _preprocess(crop: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh


def read_number(crop: np.ndarray) -> float | None:
    """OCR a stack/blind label like '1,450' or '2.5K' into a float, or None."""
    processed = _preprocess(crop)
    text = pytesseract.image_to_string(processed, config=_NUMERIC_CONFIG).strip()
    if not text:
        return None

    text = text.replace(",", "")
    match = re.match(r"^(\d+(?:\.\d+)?)\s*([KkMm]?)$", text)
    if not match:
        return None

    value = float(match.group(1))
    suffix = match.group(2).lower()
    if suffix == "k":
        value *= 1_000
    elif suffix == "m":
        value *= 1_000_000
    return value
