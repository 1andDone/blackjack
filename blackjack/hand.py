from __future__ import annotations
from blackjack.enums import HandStatus


HARD_CARD_VALUE = {
     '2': 2,
     '3': 3,
     '4': 4,
     '5': 5,
     '6': 6,
     '7': 7,
     '8': 8,
     '9': 9,
     '10': 10,
     'J': 10,
     'Q': 10,
     'K': 10,
     'A': 1
}


class Hand:
    """
    Represents a single blackjack hand.

    """
    def __init__(self, was_split: bool = False):
        """
        Parameters
        ----------
        was_split
            True if the previous hand was split, False otherwise

        """
        self._cards: list[str] = []
        self._was_split = was_split
        self._is_split = False
        self._status = HandStatus.IN_PLAY
        self._total_bet: float | int = 0
        self._side_bet: float | int = 0

        # caching attributes
        self._total_cache: int | None = None
        self._hard_total_cache: int | None = None
        self._is_soft_cache: bool | None = None
        self._is_blackjack_cache: bool | None = None

    def _invalidate_cache(self):
        self._total_cache = None
        self._hard_total_cache = None
        self._is_soft_cache = None
        self._is_blackjack_cache = None

    @property
    def cards(self) -> list[str]:
        return self._cards

    @property
    def status(self) -> HandStatus:
        return self._status

    @status.setter
    def status(self, status: HandStatus) -> None:
        self._status = status

    @property
    def total_bet(self) -> float | int:
        return self._total_bet

    def add_to_total_bet(self, amount: float | int) -> None:
        self._total_bet += amount

    @property
    def side_bet(self) -> float | int:
        return self._side_bet

    def add_to_side_bet(self, amount: float | int) -> None:
        self._side_bet += amount

    def add_card(self, card: str) -> None:
        self._cards.append(card)
        self._invalidate_cache()

    @property
    def number_of_cards(self) -> int:
        return len(self._cards)

    def _calculate_hard_total(self) -> int:
        if self._hard_total_cache is None:
            self._hard_total_cache = sum(HARD_CARD_VALUE[card] for card in self._cards)
        return self._hard_total_cache

    @property
    def total(self) -> int:
        if self._total_cache is None:
            hard_total = self._calculate_hard_total()
            self._total_cache = hard_total + 10 if 'A' in self._cards and hard_total < 12 else hard_total
        return self._total_cache

    @property
    def is_soft(self) -> bool:
        if self._is_soft_cache is None:
            hard_total = self._calculate_hard_total()
            self._is_soft_cache = 'A' in self._cards and hard_total < 12
        return self._is_soft_cache

    @property
    def is_busted(self) -> bool:
        return self.total > 21

    def split(self) -> Hand:
        self._is_split = True
        new_hand = Hand(was_split=True)
        new_hand.add_card(card=self._cards.pop())
        new_hand.add_to_total_bet(amount=self._total_bet)
        return new_hand

    @property
    def was_split(self) -> bool:
        return self._was_split

    @property
    def is_split(self) -> bool:
        return self._is_split

    @property
    def is_blackjack(self) -> bool:
        if self._is_blackjack_cache is None:
            self._is_blackjack_cache = self.number_of_cards == 2 and self.total == 21 and \
                not self._was_split and not self._is_split
        return self._is_blackjack_cache
