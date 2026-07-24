"""Interactive tool: draw a rectangle for each named region on a Club GG screenshot."""
from __future__ import annotations

import cv2

from src.capture import grab_window
from src.regions import default_region_names, save_regions

WINDOW = "Calibração Club GG"


def ask_num_seats() -> int:
    raw = input("Quantos lugares (seats) tem a mesa? [padrão 6]: ").strip()
    return int(raw) if raw else 6


def draw_box(frame, prompt: str) -> tuple[int, int, int, int]:
    print(f"-> Desenha um retângulo à volta de: {prompt}  (ENTER/SPACE para confirmar, 'c' para cancelar)")
    box = cv2.selectROI(WINDOW, frame, showCrosshair=True, fromCenter=False)
    x, y, w, h = (int(v) for v in box)
    return x, y, w, h


def main() -> None:
    print("A capturar a janela do Club GG...")
    frame = grab_window()

    num_seats = ask_num_seats()
    names = default_region_names(num_seats)

    regions: dict[str, tuple[int, int, int, int]] = {}
    cv2.namedWindow(WINDOW, cv2.WINDOW_NORMAL)
    for name in names:
        box = draw_box(frame, name)
        if box[2] == 0 or box[3] == 0:
            print(f"   (saltado: {name})")
            continue
        regions[name] = box

    cv2.destroyAllWindows()
    save_regions(regions)
    print(f"\nGuardado em regions.json ({len(regions)} regiões).")


if __name__ == "__main__":
    main()
