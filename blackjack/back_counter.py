from typing import Any
from blackjack.card_counter import CardCounter


class BackCounter(CardCounter):
    """
    Represents an individual player at a table that
    counts cards according to a counting strategy and
    enters/exits the table based on a pre-defined
    running or true count.

    """

    def __init__(self, entry_point: float | int, exit_point: float | int, **kwargs: Any):
        """
        Parameters
        ----------
        entry_point
            Running or true count at which the back counter will start
            playing hands at the table
        exit_point
            Running or true count at which the back counter will stop
            playing hands at the table

        """
        super().__init__(**kwargs)

        if exit_point >= entry_point:
            raise ValueError('Exit point must be less than the entry point.')
        if self.insurance and exit_point > self.insurance:
            raise ValueError('Exit point must be lower for player to take insurance bet.')

        self._entry_point = entry_point
        self._exit_point = exit_point
        self._is_seated = False

    @property
    def entry_point(self) -> float | int:
        return self._entry_point

    def can_enter(self, count: float | int) -> bool:
        return count >= self._entry_point and self.has_sufficient_bankroll(amount=self.placed_bet(count=count))

    @property
    def exit_point(self) -> float | int:
        return self._exit_point

    def can_exit(self, count: float | int) -> bool:
        return count <= self._exit_point

    @property
    def is_seated(self) -> bool:
        return self._is_seated

    @is_seated.setter
    def is_seated(self, seated: bool) -> None:
        self._is_seated = seated
