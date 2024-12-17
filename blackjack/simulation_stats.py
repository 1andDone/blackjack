from collections import defaultdict
from dataclasses import dataclass
from blackjack.enums import StatsCategory


@dataclass(frozen=True)
class StatsKey:
    count : float | int | None
    category : StatsCategory


class SimulationStats:
    """
    Represents a way to store blackjack
    simulation statistics.

    """
    def __init__(self):
        self._stats = defaultdict(float)

    @property
    def stats(self) -> defaultdict[str, float]:
        return self._stats

    def add_hand(self, count: float | int | None, category: StatsCategory) -> None:
        self._stats[StatsKey(count=count, category=category)] += 1
        self._stats[StatsKey(count=count, category=StatsCategory.HANDS_PLAYED)] += 1

    def add_amount(self, count: float | int | None, category: StatsCategory, increment: float | int) -> None:
        self._stats[StatsKey(count=count, category=category)] += increment

    def _compute_totals(self) -> defaultdict[str, float]:
        totals: defaultdict[str, float] = defaultdict(float)
        for key, value in self._stats.items():
            totals[key.category.value] += value
        return totals

    def _compute_total_amount_earned(self, totals: defaultdict[str, float]) -> float | int:
        total_amount_earned: float | int = 0
        if 'AMOUNT EARNED' in totals:
            total_amount_earned += totals['AMOUNT EARNED']
        if 'INSURANCE AMOUNT EARNED' in totals:
            total_amount_earned += totals['INSURANCE AMOUNT EARNED']
        return total_amount_earned

    def _compute_total_amount_wagered(self, totals: defaultdict[str, float]) -> float | int:
        total_amount_wagered: float | int = 0
        if 'AMOUNT WAGERED' in totals:
            total_amount_wagered += totals['AMOUNT WAGERED']
        if 'INSURANCE AMOUNT WAGERED' in totals:
            total_amount_wagered += totals['INSURANCE AMOUNT WAGERED']
        return total_amount_wagered

    def _format_amount(self, category: str, amount: float | int) -> str:
        if amount >= 0:
            return f'{category}: ${amount:,.2f} \n'
        return f'{category}: -${abs(amount):,.2f} \n'

    def __str__(self) -> str:
        string = ''
        totals = self._compute_totals()
        for key, value in totals.items():
            if key in {'AMOUNT EARNED', 'INSURANCE AMOUNT EARNED'}:
                string += self._format_amount(category=key, amount=value)
            elif key in {'AMOUNT WAGERED', 'INSURANCE AMOUNT WAGERED'}:
                string += self._format_amount(category=key, amount=value)
            else:
                string += f'{key}: {int(value):,} \n'

        string += self._format_amount(
                        category='TOTAL AMOUNT EARNED',
                        amount=self._compute_total_amount_earned(totals=totals)
        )

        string += self._format_amount(
                        category='TOTAL AMOUNT WAGERED',
                        amount=self._compute_total_amount_wagered(totals=totals)
        )

        if 'AMOUNT EARNED' in totals and 'AMOUNT WAGERED' in totals:
            string += f'ELEMENT OF RISK: {round((totals["AMOUNT EARNED"]/totals["AMOUNT WAGERED"]) * 100, 2)}% \n'
        return string
