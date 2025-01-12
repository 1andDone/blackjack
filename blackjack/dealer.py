from blackjack.hand import Hand


class Dealer:
    """
    Represents the dealer at a blackjack table.

    """
    def __init__(self):
        self._hand = Hand()

    @property
    def hand(self) -> Hand:
        return self._hand

    @property
    def hole_card(self) -> str:
        return self._hand.cards[0]

    @property
    def up_card(self) -> str:
        return self._hand.cards[1]

    def reset_hand(self) -> None:
        self._hand = Hand()
