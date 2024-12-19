from collections import defaultdict
from dataclasses import dataclass
from blackjack.enums import StatsCategory


@dataclass(frozen=True)
class StatsKey:
    count : float | int | None
    category : StatsCategory


class Stats:
    """
    Represents a way to store blackjack statistics
    over the course of a simulation.

    """
    def __init__(self):
        self._stats = defaultdict(float)

    @property
    def stats(self) -> defaultdict[str, float]:
        return self._stats

    def add_hand(self, count: float | int | None, category: StatsCategory) -> None:
        self._stats[StatsKey(count=count, category=category)] += 1
        self._stats[StatsKey(count=count, category=StatsCategory.HANDS_PLAYED)] += 1

    def update_amount(self, count: float | int | None, category: StatsCategory, increment: float | int) -> None:
        self._stats[StatsKey(count=count, category=category)] += increment

    def _compute_totals(self) -> defaultdict[str, float]:
        totals: defaultdict[str, float] = defaultdict(float)
        for stats_key, value in self._stats.items():
            totals[stats_key.category.value] += value
        return totals

    def _get_total(self, totals: defaultdict[str, float], *categories: StatsCategory) -> float:
        return sum(totals.get(category.value, 0) for category in categories)

    def _format_currency(self, category: str, amount: float | int) -> str:
        formatted_amount = f'${abs(amount):,.2f}\n'
        sign = '-' if amount < 0 else ''
        return f'{category}: {sign}{formatted_amount}'

    @property
    def summary(self) -> str:
        totals = self._compute_totals()
        result = []

        for category in StatsCategory:
            value = totals.get(category.value, 0)
            if category in {
                StatsCategory.AMOUNT_EARNED,
                StatsCategory.AMOUNT_WAGERED,
                StatsCategory.INSURANCE_AMOUNT_EARNED,
                StatsCategory.INSURANCE_AMOUNT_WAGERED
            }:
                result.append(self._format_currency(category=category.value, amount=value))
            else:
                result.append(f'{category.value}: {int(value):,}\n')

        total_earned = self._get_total(totals, StatsCategory.AMOUNT_EARNED, StatsCategory.INSURANCE_AMOUNT_EARNED)
        total_wagered = self._get_total(totals, StatsCategory.AMOUNT_WAGERED, StatsCategory.INSURANCE_AMOUNT_WAGERED)

        result.append(self._format_currency(category='TOTAL AMOUNT EARNED', amount=total_earned))
        result.append(self._format_currency(category='TOTAL AMOUNT WAGERED', amount=total_wagered))

        if total_wagered > 0:
            element_of_risk = (total_earned / total_wagered) * 100
            result.append(f'ELEMENT OF RISK: {element_of_risk:.2f}%\n')
        return ''.join(result)
