from collections import defaultdict
from dataclasses import dataclass
from enum import Enum


class StatsCategory(Enum):
    HANDS_LOST = 'Hands lost'
    HANDS_PUSHED = 'Hands pushed'
    HANDS_WON = 'Hands won'
    HANDS_PLAYED = 'Hands played'
    AMOUNT_EARNED = 'Amount earned'
    AMOUNT_WAGERED = 'Amount wagered'


@dataclass(frozen=True)
class StatsKey:
    count : float
    category : Enum


class SimulationStats:
    """
    Represents a way to store blackjack
    simulation statistics.
    
    """
    def __init__(self):
        self._stats = defaultdict(float)
    
    @property
    def stats(self):
        return self._stats
    
    def add_hand(self, count, category):
        self._stats[StatsKey(count=count, category=category)] += 1
        self._stats[StatsKey(count=count, category=StatsCategory.HANDS_PLAYED)] += 1
    
    def add_amount(self, count, category, increment):
        self._stats[StatsKey(count=count, category=category)] += increment
    
    def _compute_totals(self):
        totals = defaultdict(float)
        for key, value in self._stats.items():
            totals[key.category.value] += value
        return totals
    
    def _format_amount(self, category, amount):
        if amount >= 0:
            return f'{category}: ${amount:,.2f} \n'
        return f'{category}: -${abs(amount):,.2f} \n'
    
    def __repr__(self):
        string = ''
        totals = self._compute_totals()
        for key, value in totals.items():
            if key.startswith('Amount'):
                string += self._format_amount(category=key, amount=value)
            else:
                string += f'{key}: {int(value):,} \n'
                
        if 'Amount earned' in totals and 'Amount wagered' in totals:
            string += f'Element of Risk: {round((totals["Amount earned"]/totals["Amount wagered"]) * 100, 2)}% \n'
        return string