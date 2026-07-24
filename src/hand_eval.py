"""Rank the current hand (hole cards + board) using treys."""
from __future__ import annotations

from treys import Card, Evaluator

_evaluator = Evaluator()


def describe_hand(hole_cards: list[str], board_cards: list[str]) -> str | None:
    """hole_cards/board_cards use labels like 'Ah', 'Td' (see src/templates.py).
    Returns a human description, or None if there aren't enough cards yet."""
    if len(hole_cards) < 2:
        return None

    hole = [Card.new(c) for c in hole_cards]
    board = [Card.new(c) for c in board_cards]

    if len(board) < 3:
        return "Pré-flop"

    score = _evaluator.evaluate(board, hole)
    rank_class = _evaluator.get_rank_class(score)
    return _evaluator.class_to_string(rank_class)
