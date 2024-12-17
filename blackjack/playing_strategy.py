from blackjack.source.basic_strategy import H17_HARD_DICT, H17_SOFT_DICT, H17_PAIR_DICT
from blackjack.source.basic_strategy import S17_HARD_DICT, S17_SOFT_DICT, S17_PAIR_DICT


class PlayingStrategy:
    """
    Represents the decisions a player will make when faced with a
    pair split situation or a certain soft or hard count. Assumes the
    use of basic strategy.

    """
    def __init__(self, s17: bool):
        """
        Parameters
        ----------
        s17
            True if dealer stands on a soft 17, false otherwise

        """
        self._s17 = s17

    def hard(self, total: int, dealer_up_card: str) -> str:
        if self._s17:
            return S17_HARD_DICT[total][dealer_up_card]
        return H17_HARD_DICT[total][dealer_up_card]

    def soft(self, total: int, dealer_up_card: str) -> str:
        if self._s17:
            return S17_SOFT_DICT[total][dealer_up_card]
        return H17_SOFT_DICT[total][dealer_up_card]

    def pair(self, card: str, dealer_up_card: str) -> str:
        if self._s17:
            return S17_PAIR_DICT[card][dealer_up_card]
        return H17_PAIR_DICT[card][dealer_up_card]
