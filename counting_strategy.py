from counts import count_dict, count_array, starting_count_array
from cards import Cards
from math import floor
import numpy as np


class CountingStrategy(object):
    """
    CountingStrategy is an object that represents the card counting strategy used by
    a player at the table in order to make informed betting decisions.

    """
    def __init__(self, cards):
        """
        Parameters
        ----------
        cards : Cards
            Cards class instance
        """
        if not isinstance(cards, Cards):
            raise TypeError('cards must be of type Cards.')
        self.cards = cards

    def running_count(self, strategy):
        if strategy not in ['Hi-Lo', 'Hi-Opt I', 'Hi-Opt II', 'Omega II', 'Halves', 'Zen Count', 'KO']:
            raise ValueError('Strategy must be "Hi-Lo", "Hi-Opt I", "Hi-Opt II", "Omega II", "Halves", '
                             '"Zen Count", or "KO".')
        rc_array = np.dot(self.cards.seen_cards(), count_array) + (starting_count_array * (self.cards.shoe_size - 1))
        return rc_array[count_dict[strategy]]

    def true_count(self, strategy):
        if strategy not in ['Hi-Lo', 'Hi-Opt I', 'Hi-Opt II', 'Omega II', 'Halves', 'Zen Count']:
            raise ValueError('Strategy must be "Hi-Lo", "Hi-Opt I", "Hi-Opt II", "Omega II", "Halves", or "Zen Count".')
        return floor(self.running_count(strategy=strategy)/self.cards.remaining_decks())
