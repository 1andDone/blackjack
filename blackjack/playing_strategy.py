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
            True if dealer stands on a soft 17, False otherwise

        """
        if s17:
            self._hard_dict = S17_HARD_DICT
            self._soft_dict = S17_SOFT_DICT
            self._pair_dict = S17_PAIR_DICT
        else:
            self._hard_dict = H17_HARD_DICT
            self._soft_dict = H17_SOFT_DICT
            self._pair_dict = H17_PAIR_DICT

    def hard(self, total: int, dealer_up_card: str) -> str:
        return self._hard_dict[total][dealer_up_card]

    def soft(self, total: int, dealer_up_card: str) -> str:
        return self._soft_dict[total][dealer_up_card]

    def pair(self, card: str, dealer_up_card: str) -> str:
        return self._pair_dict[card][dealer_up_card]
