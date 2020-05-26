from counts import count_dict
from cards import Cards
from math import floor


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
        running_count_dict = {}
        for strategy in ['Hi-Lo', 'Hi-Opt I', 'Hi-Opt II', 'Omega II', 'Halves', 'Zen Count']:  # balanced system
            running_count_dict[strategy] = 0  # starting count equal to 0
        for strategy in ['KO']:  # unbalanced system
            running_count_dict[strategy] = -4 * (cards.shoe_size - 1)  # starting count not equal to 0
        self.running_count_dict = running_count_dict

    def update_running_count(self):
        for strategy in ['Hi-Lo', 'Hi-Opt I', 'Hi-Opt II', 'Omega II', 'Halves', 'Zen Count', 'KO']:
            for card in self.cards.visible_cards:
                self.running_count_dict[strategy] += count_dict[strategy].get(card)

    def running_count(self, strategy):
        if strategy not in ['Hi-Lo', 'Hi-Opt I', 'Hi-Opt II', 'Omega II', 'Halves', 'Zen Count', 'KO']:
            raise ValueError('Strategy must be "Hi-Lo", "Hi-Opt I", "Hi-Opt II", "Omega II", "Halves", '
                             '"Zen Count", or "KO".')
        return self.running_count_dict[strategy]

    def true_count(self, strategy):
        if strategy not in ['Hi-Lo', 'Hi-Opt I', 'Hi-Opt II', 'Omega II', 'Halves', 'Zen Count']:
            raise ValueError('Strategy must be "Hi-Lo", "Hi-Opt I", "Hi-Opt II", "Omega II", "Halves", or "Zen Count".')
        return floor(self.running_count(strategy=strategy)/self.cards.remaining_decks())
