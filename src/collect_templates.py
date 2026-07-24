"""Interactive tool: teach the recognizer what each card looks like.

Run this while cards are visible on the table (hole cards and/or board).
For each configured card region it shows the crop and asks you to label it
(e.g. "Ah" for Ace of Hearts, "Td" for Ten of Diamonds), or blank to skip.
"""
from __future__ import annotations

import cv2

from src.capture import grab_window
from src.regions import HOLE_CARD_NAMES, BOARD_CARD_NAMES, load_regions, crop
from src.templates import save_template, is_empty_slot, is_valid_label

CARD_REGION_NAMES = HOLE_CARD_NAMES + BOARD_CARD_NAMES


def main() -> None:
    regions = load_regions()
    frame = grab_window()

    for name in CARD_REGION_NAMES:
        if name not in regions:
            continue
        card_crop = crop(frame, regions[name])
        if is_empty_slot(card_crop):
            print(f"[{name}] parece vazio, a saltar.")
            continue

        cv2.imshow(name, card_crop)
        cv2.waitKey(1)
        label = input(
            f"[{name}] que carta é esta? (ex: Ah, Td, 9s; ENTER para saltar): "
        ).strip()
        cv2.destroyWindow(name)

        if not label:
            continue
        if not is_valid_label(label):
            print(f"   Etiqueta inválida '{label}', a saltar.")
            continue

        save_template(label, card_crop)
        print(f"   Guardado como templates/{label}.png")

    print("\nConcluído. Corre novamente com outras mãos para completar as 52 cartas.")


if __name__ == "__main__":
    main()
