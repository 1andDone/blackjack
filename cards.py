import random


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
        self.deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 1] * 4 * int(shoe_size)
        self.total_cards = 52 * shoe_size
        self._visible_cards = []
        self._shoe_counter = 1

    @property
    def shoe_counter(self):
        return self._shoe_counter

    @shoe_counter.setter
    def shoe_counter(self, value):
        self._shoe_counter += value

    @property
    def visible_cards(self):
        return self._visible_cards

    @visible_cards.setter
    def visible_cards(self, value):
        self._visible_cards = value

    def burn_card(self):
        return self.deck.pop()

    def shuffle(self):
        random.shuffle(self.deck)
        self.burn_card()

    def deal_card(self, visible=True):
        card = self.deck.pop()
        if visible:
            self._visible_cards.append(card)
        return card

    def update_visible_cards(self, card):
        self._visible_cards.append(card)

    def remaining_decks(self):
        return round(len(self.deck)/52, 0)

    def cut_card_reached(self, penetration):
        if penetration < 0.5 or penetration > 0.9:
            raise ValueError('Penetration must be between 0.5 and 0.9.')
        remaining_cards = self.total_cards - len(self.deck)
        return remaining_cards/self.total_cards >= float(penetration)
