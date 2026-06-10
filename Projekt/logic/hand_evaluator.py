from collections import Counter
import random

werte = [
    "2", "3", "4", "5", "6",
    "7", "8", "9", "10",
    "Bube", "Dame", "König", "Ass"
]

werte_rang = {
    wert: i
    for i, wert in enumerate(werte, start=2)
}


def _to_pair(k):
    """Normalize a card representation to a (value, suit) pair.

    Accepts either an object with `.value` and `.suit` attributes
    (e.g. `models.card.Card`) or a 2-tuple/list like `(value, suit)`.
    """
    if hasattr(k, "value") and hasattr(k, "suit"):
        return (k.value, k.suit)
    try:
        # support tuples/lists like (value, suit)
        if len(k) >= 2:
            return (k[0], k[1])
    except Exception:
        pass
    raise TypeError(f"Unsupported card representation: {k}")


def ist_strasse(zahlen):
    zahlen = sorted(set(zahlen))

    for i in range(len(zahlen) - 4):
        if zahlen[i + 4] - zahlen[i] == 4:
            return True

    if {14, 2, 3, 4, 5}.issubset(zahlen):
        return True

    return False


# ASCII alias for non-ASCII name used elsewhere
ist_straße = ist_strasse


def hand_bewerten(hand):
    # normalize cards to (value, suit) pairs
    pairs = [_to_pair(k) for k in hand]
    zahlen = [werte_rang[p[0]] for p in pairs]
    farben_liste = [p[1] for p in pairs]
    zahlen_counter = Counter(zahlen)
    farben_counter = Counter(farben_liste)

    ist_flush = any(count >= 5 for count in farben_counter.values())
    ist_straight = ist_strasse(zahlen)

    if ist_flush and ist_straight and max(zahlen) == 14:
        return (9, "Royal Flush")
    if ist_flush and ist_straight:
        return (8, "Straight Flush")
    if 4 in zahlen_counter.values():
        return (7, "Vierling")
    if 3 in zahlen_counter.values() and 2 in zahlen_counter.values():
        return (6, "Full House")
    if ist_flush:
        return (5, "Flush")
    if ist_straight:
        return (4, "Straße")
    if 3 in zahlen_counter.values():
        return (3, "Drilling")
    if list(zahlen_counter.values()).count(2) >= 2:
        return (2, "Zwei Paare")
    if 2 in zahlen_counter.values():
        return (1, "Paar")
    return (0, "Hohe Karte")


def computer_handstaerke(hand, tisch):
    """Evaluate combined hand strength for computer play.

    Accepts `hand` and `tisch` as lists of Card objects or (value,suit) pairs.
    """
    karten = list(hand) + list(tisch)
    wert, _ = hand_bewerten(karten)
    # small randomness so AI isn't fully deterministic
    zufall = random.randint(-1, 1)
    return max(0, min(9, wert + zufall))


# keep original non-ASCII name as compatibility alias
computer_handstärke = computer_handstaerke