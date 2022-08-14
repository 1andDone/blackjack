from blackjack.hand import Hand


class Dealer:
    """
    Represents the dealer at a blackjack table.
    
    """
    def __init__(self):
        self._hand = Hand()
    
    @property
    def hand(self):
        return self._hand
    
    def hole_card(self):
        return self._hand.cards[0]
    
    def up_card(self):
        return self._hand.cards[1]
    
    def deal_card(self, shoe, seen=True):
        card = shoe.cards.pop()
        if seen:
            shoe.add_to_seen_cards(card=card)
        return card

    def reset_hand(self):
        self._hand = Hand()