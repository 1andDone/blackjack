from blackjack.hand import Hand
from blackjack.shoe import Shoe


class Dealer:
    """
    Represents the dealer at a blackjack table.

    """
    def __init__(self):
        self._hand = Hand()

    @property
    def hand(self) -> Hand:
        return self._hand

    def hole_card(self) -> str:
        return self._hand.cards[0]

    def up_card(self) -> str:
        return self._hand.cards[1]

    def deal_card(self, shoe: Shoe, seen: bool = True) -> str:
        card = shoe.cards.pop()
        if seen:
            shoe.add_to_seen_cards(card=card)
        return card

    def reset_hand(self) -> None:
        self._hand = Hand()
