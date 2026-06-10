from collections import Counter

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
    # dein kompletter Bewertungscode
    pass