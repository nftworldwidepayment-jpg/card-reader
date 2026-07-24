"""CLI loop: capture the Club GG table, read cards/blinds/stacks, print status."""
from __future__ import annotations

import time

from src.regions import load_regions
from src.templates import load_templates
from src.state import build_state, seat_numbers_from_regions

POLL_SECONDS = 1.0


def print_state(state: dict) -> None:
    print("\033c", end="")  # clear terminal
    hole = state["hole_cards"]
    board = state["board_cards"]
    print(f"Hole cards : {' '.join(hole) if hole else '--'}")
    print(f"Board      : {' '.join(board) if board else '--'}")
    if state["hand"]:
        print(f"Mão        : {state['hand']}")
    for s in state["seats"]:
        stack_str = f"{s['stack']:g}" if s["stack"] is not None else "?"
        blind_str = f"{s['blind']:g}" if s["blind"] is not None else "?"
        print(f"Seat {s['seat']}     : stack={stack_str}  blind={blind_str}")


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
                print_state(build_state(regions, templates, seats))
            except RuntimeError as exc:
                print(f"Aviso: {exc}")
            time.sleep(POLL_SECONDS)
    except KeyboardInterrupt:
        print("\nParado.")


if __name__ == "__main__":
    main()
