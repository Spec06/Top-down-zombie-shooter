import random
from models.card import Card

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
        return self.cards.pop()