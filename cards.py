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
        self.deck = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'] * 4 * int(shoe_size)
        self.visible_cards = []

    def burn_card(self):
        return self.deck.pop()

    def shuffle(self):
        random.shuffle(self.deck)
        self.burn_card()

    def deal_card(self, visible=True):
        card = self.deck.pop()
        if visible:
            self.visible_cards.append(card)
        return card

    def set_visible_cards(self):
        self.visible_cards = []

    def get_visible_cards(self):
        return self.visible_cards

    def update_visible_cards(self, card):
        self.visible_cards.append(card)

    def remaining_decks(self):
        return len(self.deck)/52

    def cut_card_reached(self, penetration):
        if penetration < 0.5 or penetration > 0.9:
            raise ValueError('Penetration must be between 0.5 and 0.9.')
        total_cards = 52 * self.shoe_size
        remaining_cards = total_cards - len(self.deck)
        return remaining_cards/total_cards >= float(penetration)
