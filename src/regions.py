"""Load/save the named rectangular regions calibrated for a table layout."""
from __future__ import annotations

import json
from pathlib import Path

REGIONS_PATH = Path(__file__).resolve().parent.parent / "regions.json"

HOLE_CARD_NAMES = ["hole_1", "hole_2"]
BOARD_CARD_NAMES = ["board_1", "board_2", "board_3", "board_4", "board_5"]


def seat_stack_name(seat: int) -> str:
    return f"seat{seat}_stack"


def seat_blind_name(seat: int) -> str:
    return f"seat{seat}_blind"


def default_region_names(num_seats: int = 6) -> list[str]:
    names = list(HOLE_CARD_NAMES) + list(BOARD_CARD_NAMES)
    for seat in range(1, num_seats + 1):
        names.append(seat_stack_name(seat))
        names.append(seat_blind_name(seat))
    return names


def load_regions(path: Path = REGIONS_PATH) -> dict[str, tuple[int, int, int, int]]:
    if not path.exists():
        raise FileNotFoundError(
            "Ainda não calibraste a mesa. Abre http://127.0.0.1:5000/calibrate "
            "no browser e segue os passos."
        )
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return {name: tuple(box) for name, box in raw.items()}


def save_regions(regions: dict[str, tuple[int, int, int, int]], path: Path = REGIONS_PATH) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(regions, f, indent=2, ensure_ascii=False)


def crop(frame, box: tuple[int, int, int, int]):
    x, y, w, h = box
    return frame[y : y + h, x : x + w]
