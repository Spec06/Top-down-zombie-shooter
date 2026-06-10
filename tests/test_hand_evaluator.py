from Projekt.models.card import Card
from Projekt.logic.hand_evaluator import hand_bewerten


def test_royal_flush():
    hand = [
        Card('Ass', 'Herz'),
        Card('König', 'Herz'),
        Card('Dame', 'Herz'),
        Card('Bube', 'Herz'),
        Card('10', 'Herz')
    ]
    val, name = hand_bewerten(hand)
    assert val == 9 or name == 'Royal Flush'
