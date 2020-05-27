import random
import numpy as np


class Cards(object):
    """
    Cards is an object that deals with a shoe at a table.

    """
    def __init__(self, shoe_size):
        """
        Parameters
        ----------
        shoe_size: int
            Number of decks used during a blackjack game
        """
        if shoe_size not in [4, 6, 8]:
            raise ValueError('Shoe size must be 4, 6, or 8.')
        self.shoe_size = int(shoe_size)
        self.cards = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 1] * 4 * int(shoe_size)
        self.total_cards = 52 * shoe_size
        self._seen_cards = np.array([0] * 13)

    def seen_cards(self):
        return self._seen_cards

    def add_to_seen_cards(self, card):
        self._seen_cards[card - 1] += 1

    def burn_card(self):
        return self.cards.pop()

    def shuffle(self):
        random.shuffle(self.cards)
        self.burn_card()

    def deal_card(self, seen=True):
        card = self.cards.pop()
        if seen:
            self._seen_cards[card - 1] += 1
        return card

    def remaining_decks(self):
        return round(len(self.cards)/52, 0)

    def cut_card_reached(self, penetration):
        if penetration < 0.5 or penetration > 0.9:
            raise ValueError('Penetration must be between 0.5 and 0.9.')
        used_cards = self.total_cards - len(self.cards)
        return used_cards/self.total_cards >= float(penetration)
