from math import ceil, floor
from typing import Any
from typing_extensions import override
from blackjack.enums import CountingStrategy
from blackjack.player import Player


class CardCounter(Player):
    """
    Represents an individual player at a table that
    counts cards according to a counting strategy.

    """
    def __init__(
        self,
        counting_strategy: CountingStrategy,
        bet_ramp: dict[float | int, float | int],
        insurance: float | int | None = None,
        **kwargs: Any
    ):
        """
        Parameters
        ----------
        counting_strategy
            Card counting strategy used by the player
        bet_ramp
            Dictionary where each key value is the running or
            true count and each value indicates the amount of money
            wagered at that running or true count
        insurance
            Minimum running or true count at which a player will
            purchase insurance, if desired, and if available

        """
        super().__init__(**kwargs)

        self.max_bet_ramp = max(bet_ramp.values())
        self.min_bet_ramp = min(bet_ramp.values())

        if self.max_bet_ramp > self.bankroll:
            raise ValueError('Maximum bet in the "bet_ramp" exceeds the bankroll.')

        self.min_count = min(bet_ramp)
        self.max_count = max(bet_ramp)

        counts_to_check: list[float | int] = list(range(ceil(self.min_count), floor(self.max_count) + 1))
        if counting_strategy == CountingStrategy.HALVES:
            counts_to_check.extend([count + 0.5 for count in range(floor(self.min_count), floor(self.max_count))])

        inferred_wager = None
        for count in counts_to_check:
            if count not in bet_ramp:
                bet_ramp[count] = inferred_wager
            inferred_wager = bet_ramp[count]

        self._bet_ramp = bet_ramp
        self._counting_strategy = counting_strategy
        self._insurance = insurance

    @property
    def counting_strategy(self) -> CountingStrategy:
        return self._counting_strategy

    @override
    def initial_wager(self, **kwargs: Any) -> float | int:
        if 'count' not in kwargs:
            raise TypeError('"count" needs to be included in kwargs.')
        count = kwargs['count']
        if count < self.min_count:
            return self._min_bet
        if count >= self.max_count:
            return self.max_bet_ramp
        return self._bet_ramp[count]

    @property
    def insurance(self) -> float | int | None:
        return self._insurance
