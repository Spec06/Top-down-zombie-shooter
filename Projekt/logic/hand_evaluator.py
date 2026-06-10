from collections import Counter
import random

werte = [
    "2","3","4","5","6",
    "7","8","9","10",
    "Bube","Dame","König","Ass"
]

werte_rang = {
    wert: i
    for i, wert in enumerate(werte, start=2)
}


def ist_straße(zahlen):
    zahlen = sorted(set(zahlen))

    for i in range(len(zahlen)-4):
        if zahlen[i+4] - zahlen[i] == 4:
            return True

    if {14,2,3,4,5}.issubset(zahlen):
        return True

    return False


def hand_bewerten(hand):
    zahlen = [werte_rang[k[0]] for k in hand]
    farben_liste = [k[1] for k in hand]
    zahlen_counter = Counter(zahlen)
    farben_counter = Counter(farben_liste)

    ist_flush = any(count >= 5 for count in farben_counter.values())
    ist_straight = ist_straße(zahlen)

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

def computer_handstärke(hand, tisch):
    # Bewertet je nach Phase (Preflop, Flop, Turn, River)
    karten = hand + tisch
    wert, _ = hand_bewerten(karten)
    # Kleine Zufallskomponente, damit er nicht komplett berechenbar ist
    zufall = random.randint(-1, 1)
    return max(0, min(9, wert + zufall))