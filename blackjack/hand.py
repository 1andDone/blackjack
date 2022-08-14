from enum import Enum


hard_card_value = {
     '2': 2,
     '3': 3,
     '4': 4,
     '5': 5,
     '6': 6,
     '7': 7,
     '8': 8,
     '9': 9,
     '10': 10,
     'J': 10,
     'Q': 10,
     'K': 10,
     'A': 1
}


class HandStatus(Enum):
    IN_PLAY = 'in play'
    SETTLED = 'settled'
    SHOWDOWN = 'showdown'
    

class Hand:
    """
    Represents a single blackjack hand.
    
    """
    def __init__(self, is_previous_hand_split=False):
        """
        Parameters
        ----------
        is_previous_hand_split: bool
            True if previous hand was split, false otherwise
        
        """
        self._cards = []
        self._is_previous_hand_split = is_previous_hand_split
        self._is_current_hand_split = False
        self._status = HandStatus.IN_PLAY
        self._total_bet = 0
        self._side_bet = 0
    
    @property
    def cards(self):
        return self._cards
    
    @property
    def status(self):
        return self._status
    
    @status.setter
    def status(self, status):
        self._status = status
        
    @property
    def total_bet(self):
        return self._total_bet
    
    @total_bet.setter
    def total_bet(self, amount):
        self._total_bet += amount
    
    @property
    def side_bet(self):
        return self._side_bet
    
    @side_bet.setter
    def side_bet(self, amount):
        self._side_bet += amount
    
    def add_card(self, card):
        self._cards.append(card)
    
    def number_of_cards(self):
        return len(self._cards)
    
    def _hard_total(self):
        return sum(hard_card_value[card] for card in self._cards)
    
    def total(self):
        total = self._hard_total()
        
        if 'A' in self._cards and total < 12:
            total += 10
            
        return total
    
    def is_soft(self):
        if 'A' in self._cards:
            total = self._hard_total()
            return total < 12
        return False
    
    def is_busted(self):
        return self.total() > 21
    
    def split(self):
        self._is_current_hand_split = True
        new_hand = Hand(is_previous_hand_split=True)
        new_hand.add_card(card=self._cards.pop())
        new_hand.total_bet = self._total_bet
        return new_hand
    
    @property
    def is_previous_hand_split(self):
        return self._is_previous_hand_split
    
    @property
    def is_current_hand_split(self):
        return self._is_current_hand_split

    def is_blackjack(self):
        return len(self._cards) == 2 and self.total() == 21 and \
            not self._is_previous_hand_split and not self._is_current_hand_split