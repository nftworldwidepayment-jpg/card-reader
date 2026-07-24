"""Main loop: capture the Club GG table, read cards/blinds/stacks, print status."""
from __future__ import annotations

import time

from src.capture import grab_window
from src.regions import (
    HOLE_CARD_NAMES,
    BOARD_CARD_NAMES,
    load_regions,
    crop,
)
from src.templates import load_templates, match_card
from src.ocr import read_number
from src.hand_eval import describe_hand

POLL_SECONDS = 1.0


def seat_numbers_from_regions(regions: dict) -> list[int]:
    seats = set()
    for name in regions:
        if name.startswith("seat") and name.endswith("_stack"):
            seats.add(int(name[len("seat") : -len("_stack")]))
    return sorted(seats)


def read_cards(frame, regions, names, templates) -> list[str]:
    cards = []
    for name in names:
        if name not in regions:
            continue
        c = crop(frame, regions[name])
        label = match_card(c, templates)
        if label:
            cards.append(label)
    return cards


def run_once(regions, templates, seats) -> None:
    frame = grab_window()

    hole = read_cards(frame, regions, HOLE_CARD_NAMES, templates)
    board = read_cards(frame, regions, BOARD_CARD_NAMES, templates)

    print("\033c", end="")  # clear terminal
    print(f"Hole cards : {' '.join(hole) if hole else '--'}")
    print(f"Board      : {' '.join(board) if board else '--'}")

    hand_desc = describe_hand(hole, board)
    if hand_desc:
        print(f"Mão        : {hand_desc}")

    for seat in seats:
        stack_box = regions.get(f"seat{seat}_stack")
        blind_box = regions.get(f"seat{seat}_blind")
        stack = read_number(crop(frame, stack_box)) if stack_box else None
        blind = read_number(crop(frame, blind_box)) if blind_box else None
        stack_str = f"{stack:g}" if stack is not None else "?"
        blind_str = f"{blind:g}" if blind is not None else "?"
        print(f"Seat {seat}     : stack={stack_str}  blind={blind_str}")


def main() -> None:
    regions = load_regions()
    templates = load_templates()
    seats = seat_numbers_from_regions(regions)

    if not templates:
        print(
            "Aviso: não há templates de cartas guardados ainda. "
            "Corre `python -m src.collect_templates` primeiro."
        )

    print("A correr. Ctrl+C para parar.")
    try:
        while True:
            try:
                run_once(regions, templates, seats)
            except RuntimeError as exc:
                print(f"Aviso: {exc}")
            time.sleep(POLL_SECONDS)
    except KeyboardInterrupt:
        print("\nParado.")


if __name__ == "__main__":
    main()
