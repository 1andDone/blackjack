from typing import Any
from blackjack.card_counter import CardCounter


class BackCounter(CardCounter):
    """
    Represents an individual player at a table that
    counts cards according to a counting strategy and
    enters/exits the table based on a pre-defined
    running or true count.

    """

    def __init__(self, partner: CardCounter, entry_point: float | int, exit_point: float | int, **kwargs: Any):
        """
        Parameters
        ----------
        partner
            Partner that will call the back counting player to the table
        entry_point
            Running or true count at which the back counter will start
            playing hands at the table
        exit_point
            Running or true count at which the back counter will stop
            playing hands at the table

        """
        super().__init__(**kwargs)
        self._partner = partner
        # TODO: its possible that it could still be another backcounter...careful here...
        if not isinstance(partner, CardCounter):
            raise TypeError('Partner must be a card counter.')
        if self._partner.counting_strategy != self.counting_strategy:
            raise ValueError('Back counting player must have the same card counting strategy as their partner.')
        if exit_point >= entry_point:
            raise ValueError('Exit point must be less than the entry point.')
        if self.insurance and exit_point > self.insurance:
            raise ValueError('Exit point must be lower for player to take insurance bet.')
        self._entry_point = entry_point
        self._exit_point = exit_point

    @property
    def partner(self) -> CardCounter:
        return self._partner

    @property
    def entry_point(self) -> float | int:
        return self._entry_point

    def can_enter(self, count: float | int) -> bool:
        return count >= self._entry_point

    @property
    def exit_point(self) -> float | int:
        return self._exit_point

    def can_exit(self, count: float | int) -> bool:
        return self._exit_point >= count
