class Card:

def __init__(self, value, suit):
    self.value = value
    self.suit = suit

def __str__(self):
    return f"{self.value} {self.suit}"