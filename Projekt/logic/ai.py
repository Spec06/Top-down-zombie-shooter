import random

class PokerAI:

    def handstaerke(self, hand, tisch):
        return random.randint(0, 9)

    def aktion(
        self,
        comp_chips,
        player_bet,
        comp_bet,
        pot,
        tisch,
        hand,
        phase
    ):
    
    def computer_aktion(comp_chips, player_bet, comp_bet, pot, sicht_tisch, computer_hand, phase):
        to_call = player_bet - comp_bet
        strength = computer_handstärke(computer_hand, sicht_tisch)

        # Aggressivität je nach Phase
        if phase == "preflop":
            base_aggr = 0.8
        elif phase == "flop":
            base_aggr = 1.0
        elif phase == "turn":
            base_aggr = 1.1
        else:  # river
            base_aggr = 1.2

        # Effektive Bereitschaft zu investieren
        max_call = int((strength + random.randint(3, 10)) * 200 * base_aggr)
        max_raise = int((strength - 1) * 60 * base_aggr) if strength >= 2 else 0

        # Wenn nichts zu callen ist
        if to_call <= 0:
            # Bluff-Chance bei schwacher Hand
            if strength <= 1 and random.random() < 0.1 and comp_chips > 0:
                bet_amt = min(40, comp_chips)
                comp_chips -= bet_amt
                comp_bet += bet_amt
                pot += bet_amt
                print(f"\nComputer blufft und setzt {bet_amt}.")
                return comp_chips, comp_bet, pot, "raise"

            # Starke Hand → Value Bet
            if strength >= 3 and comp_chips > 0:
                bet_amt = min(max(40, max_raise), comp_chips)
                if bet_amt > 0:
                    comp_chips -= bet_amt
                    comp_bet += bet_amt
                    pot += bet_amt
                    print(f"\nComputer setzt {bet_amt}.")
                    return comp_chips, comp_bet, pot, "raise"

            print("\nComputer checkt.")
            return comp_chips, comp_bet, pot, "check"

        # Es gibt etwas zu callen
        if to_call > 0:
            # Zu teuer im Verhältnis zur Handstärke
            if to_call > max_call:
                # Schwache Hände folden
                if strength <= 1:
                    print("\nComputer foldet. Du gewinnst den Pot.")
                    return comp_chips, comp_bet, pot, "fold"

                # Mittlere Hände entscheiden sich zufällig
                if strength <= 3:
                    if random.random() < 0.5 and comp_chips > 0:
                        call_amt = min(to_call, comp_chips)
                        comp_chips -= call_amt
                        comp_bet += call_amt
                        pot += call_amt
                        print(f"\nComputer zögert, callt aber {call_amt}.")
                        return comp_chips, comp_bet, pot, "call"
                    else:
                        print("\nComputer foldet. Du gewinnst den Pot.")
                        return comp_chips, comp_bet, pot, "fold"

                # Starke Hände callen (oder gehen ggf. selbst all-in)
                call_amt = min(to_call, comp_chips)
                # Wenn Computer nichts mehr hat, kann er nicht callen
                if call_amt == 0 and to_call > 0:
                    print("\nComputer kann nicht callen (kein Geld).")
                    return comp_chips, comp_bet, pot, "call_zero"
                comp_chips -= call_amt
                comp_bet += call_amt
                pot += call_amt
                if strength >= 6 and comp_chips > 0 and random.random() < 0.5:
                    raise_amt = comp_chips
                    comp_chips -= raise_amt
                    comp_bet += raise_amt
                    pot += raise_amt
                    print(f"\nComputer geht mit starkem Blatt All-in ({comp_bet}).")
                    return comp_chips, comp_bet, pot, "raise"
                print(f"\nComputer callt {call_amt}.")
                return comp_chips, comp_bet, pot, "call"

            # Call (normalfall)
            call_amt = min(to_call, comp_chips)
            # Wenn Computer nichts mehr hat, kann er nicht callen
            if call_amt == 0 and to_call > 0:
                print("\nComputer kann nicht callen (kein Geld).")
                return comp_chips, comp_bet, pot, "call_zero"
            comp_chips -= call_amt
            comp_bet += call_amt
            pot += call_amt

            # Eventuell zusätzlich raisen
            if strength >= 5 and max_raise > 0 and comp_chips > 0 and random.random() < 0.5:
                raise_amt = min(max_raise, comp_chips)
                comp_chips -= raise_amt
                comp_bet += raise_amt
                pot += raise_amt
                print(f"\nComputer callt {call_amt} und erhöht um {raise_amt}.")
                return comp_chips, comp_bet, pot, "raise"

            print(f"\nComputer callt {call_amt}.")
            return comp_chips, comp_bet, pot, "call"
        pass