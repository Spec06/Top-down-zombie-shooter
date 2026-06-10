import random
from models.card import Card


class DeckEmptyError(Exception):
    """Raised when attempting to draw from an empty deck."""

SUITS = ["Herz","Karo","Pik","Kreuz"]

VALUES = [
"2","3","4","5","6",
"7","8","9","10",
"Bube","Dame","König","Ass"
]

class Deck:

    def __init__(self):
        self.cards = [
            Card(v, s)
            for v in VALUES
            for s in SUITS
        ]

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self):
        if not self.cards:
            raise DeckEmptyError("Cannot draw from empty deck")
        return self.cards.pop()