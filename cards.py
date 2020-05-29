import random
import numpy as np
from house_rules import HouseRules


class Cards(object):
    """
    Cards is an object that deals with a shoe at a table.

    """
    def __init__(self, rules):
        """
        Parameters
        ----------
        rules : HouseRules
            HouseRules class instance
        """
        self._cards = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 1] * 4 * rules.shoe_size
        self._total_cards = 52 * rules.shoe_size
        self._seen_cards = np.array([0] * 13)

    @property
    def cards(self):
        return self._cards

    @property
    def total_cards(self):
        return self._total_cards

    @property
    def seen_cards(self):
        return self._seen_cards

    @seen_cards.setter
    def seen_cards(self, value):
        self._seen_cards = value

    def add_to_seen_cards(self, card):
        self._seen_cards[card - 1] += 1

    def burn_card(self):
        return self._cards.pop()

    def shuffle(self):
        random.shuffle(self._cards)
        self.burn_card()

    def deal_card(self, seen=True):
        card = self._cards.pop()
        if seen:
            self.add_to_seen_cards(card=card)
        return card

    def remaining_decks(self):
        return round(len(self._cards)/52, 0)

    def cut_card_reached(self, penetration):
        if penetration < 0.5 or penetration > 0.9:
            raise ValueError('Penetration must be between 0.5 and 0.9.')
        used_cards = self._total_cards - len(self._cards)
        return used_cards/self._total_cards >= penetration
