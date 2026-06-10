from models.deck import Deck
from models.player import Player

class GameManager:

def __init__(self):

    self.player = Player(
        "Spieler",
        1000
    )

    self.ai = Player(
        "Computer",
        1000
    )

    self.table_cards = []
    self.pot = 0

def new_round(self):

    self.deck = Deck()
    self.deck.shuffle()

    self.player.clear_hand()
    self.ai.clear_hand()

    self.table_cards.clear()

    for _ in range(2):
        self.player.hand.append(
            self.deck.draw()
        )

        self.ai.hand.append(
            self.deck.draw()
        )

    self.pot = 0