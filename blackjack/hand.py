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

    @property
    def number_of_cards(self) -> int:
        return len(self._cards)

    def _calculate_hard_total(self) -> int:
        return sum(HARD_CARD_VALUE[card] for card in self._cards)

    @property
    def total(self) -> int:
        total = self._calculate_hard_total()
        if 'A' in self._cards and total < 12:
            total += 10
        return total

    @property
    def is_soft(self) -> bool:
        if 'A' in self._cards:
            total = self._calculate_hard_total()
            return total < 12
        return False

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
        return self.number_of_cards == 2 and self.total == 21 and \
            not self._was_split and not self._is_split
