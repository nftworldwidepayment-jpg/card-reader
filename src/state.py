"""Build a JSON-serialisable snapshot of the table: hole cards, board, hand
strength, and per-seat stack/blind. Shared by the CLI and the web UI."""
from __future__ import annotations

from src.capture import grab_window
from src.regions import HOLE_CARD_NAMES, BOARD_CARD_NAMES, crop
from src.templates import match_card
from src.ocr import read_number
from src.hand_eval import describe_hand


def seat_numbers_from_regions(regions: dict) -> list[int]:
    seats = set()
    for name in regions:
        if name.startswith("seat") and name.endswith("_stack"):
            seats.add(int(name[len("seat") : -len("_stack")]))
    return sorted(seats)


def _read_cards(frame, regions, names, templates) -> list[str]:
    cards = []
    for name in names:
        if name not in regions:
            continue
        c = crop(frame, regions[name])
        label = match_card(c, templates)
        if label:
            cards.append(label)
    return cards


def build_state(regions: dict, templates: dict, seats: list[int]) -> dict:
    frame = grab_window()

    hole = _read_cards(frame, regions, HOLE_CARD_NAMES, templates)
    board = _read_cards(frame, regions, BOARD_CARD_NAMES, templates)
    hand_desc = describe_hand(hole, board)

    seat_data = []
    for seat in seats:
        stack_box = regions.get(f"seat{seat}_stack")
        blind_box = regions.get(f"seat{seat}_blind")
        stack = read_number(crop(frame, stack_box)) if stack_box else None
        blind = read_number(crop(frame, blind_box)) if blind_box else None
        seat_data.append({"seat": seat, "stack": stack, "blind": blind})

    return {
        "hole_cards": hole,
        "board_cards": board,
        "hand": hand_desc,
        "seats": seat_data,
    }
