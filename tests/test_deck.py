from Projekt.models.deck import Deck, DeckEmptyError


def test_draw_until_empty():
    d = Deck()
    drawn = []
    for _ in range(52):
        drawn.append(d.draw())
    assert len(drawn) == 52

    try:
        d.draw()
        assert False, "Expected DeckEmptyError"
    except DeckEmptyError:
        assert True
