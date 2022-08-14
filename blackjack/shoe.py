from enum import Enum
import random


hi_lo = {
    '2': 1,
    '3': 1,
    '4': 1,
    '5': 1, 
    '6': 1, 
    '7': 0, 
    '8': 0, 
    '9': 0, 
    '10-J-Q-K': -1, 
    'A': -1,  
}

hi_opt_i = {
    '2': 0,
    '3': 1,
    '4': 1,
    '5': 1, 
    '6': 1, 
    '7': 0, 
    '8': 0, 
    '9': 0, 
    '10-J-Q-K': -1, 
    'A': 0,  
}

hi_opt_ii = {
    '2': 1,
    '3': 1,
    '4': 2,
    '5': 2, 
    '6': 1, 
    '7': 1, 
    '8': 0, 
    '9': 0, 
    '10-J-Q-K': -2, 
    'A': 0,  
}

omega_ii = {
    '2': 1,
    '3': 1,
    '4': 2,
    '5': 2, 
    '6': 2, 
    '7': 1, 
    '8': 0, 
    '9': -1, 
    '10-J-Q-K': -2, 
    'A': 0,  
}

halves = {
    '2': 0.5,
    '3': 1,
    '4': 1,
    '5': 1.5, 
    '6': 1, 
    '7': 0.5, 
    '8': 0, 
    '9': -0.5, 
    '10-J-Q-K': -1, 
    'A': -1,  
}

zen_count = {
    '2': 1,
    '3': 1,
    '4': 2,
    '5': 2, 
    '6': 2, 
    '7': 1, 
    '8': 0, 
    '9': 0, 
    '10-J-Q-K': -2, 
    'A': -1,  
}

ko_count = {
    '2': 1,
    '3': 1,
    '4': 1,
    '5': 1, 
    '6': 1, 
    '7': 1, 
    '8': 0, 
    '9': 0, 
    '10-J-Q-K': -1, 
    'A': -1,  
}


class CountingStrategy(Enum):
    HI_LO = 'Hi-Lo'
    HI_OPT_I = 'Hi-Opt I'
    HI_OPT_II = 'Hi-Opt II'
    OMEGA_II = 'Omega II'
    HALVES = 'Halves'
    ZEN_COUNT = 'Zen Count'
    KO = 'KO'


# balanced card counting systems: Hi-Lo, Hi-Opt I, Hi-Opt II, Omega II, Halves, Zen Count
# unbalanced card counting systems: KO
count_dict = {
    CountingStrategy.HI_LO: hi_lo,
    CountingStrategy.HI_OPT_I: hi_opt_i,
    CountingStrategy.HI_OPT_II: hi_opt_ii,
    CountingStrategy.OMEGA_II: omega_ii,
    CountingStrategy.HALVES: halves,
    CountingStrategy.ZEN_COUNT: zen_count,
    CountingStrategy.KO: ko_count
}


# balanced card counting systems begin at a running count equal to 0
# unbalanced card counting systems (KO) begin at a running count equal to -4 * (shoe size - 1)
# the additional (shoe size - 1) factor for KO will be added in counting_strategy.py
starting_count_dict = {
    CountingStrategy.HI_LO: 0,
    CountingStrategy.HI_OPT_I: 0,
    CountingStrategy.HI_OPT_II: 0,
    CountingStrategy.OMEGA_II: 0,
    CountingStrategy.HALVES: 0,
    CountingStrategy.ZEN_COUNT: 0,
    CountingStrategy.KO: -4
}


class Shoe:
    """
    Represents a shoe of cards.

    """
    def __init__(self, shoe_size):
        """
        Parameters
        ----------
        shoe_size: int
            Number of decks used during a blackjack game
        
        """
        if not 1 <= shoe_size <=8 :
            raise ValueError('Shoe size must be between 1 and 8 decks.')
        self._shoe_size = shoe_size
        self._cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'] * 4 * self._shoe_size
        self._total_cards = 52 * self._shoe_size
        self._seen_cards = {
            '2': 0,
            '3': 0,
            '4': 0,
            '5': 0,
            '6': 0,
            '7': 0,
            '8': 0,
            '9': 0,
            '10-J-Q-K': 0,
            'A': 0 
        }
    
    @property
    def cards(self):
        return self._cards
    
    def burn_card(self, seen=False):
        card = self._cards.pop()
        if seen:
            self.add_to_seen_cards(card=card)
    
    def shuffle(self):
        random.shuffle(self._cards)
        self.burn_card()
    
    def add_to_seen_cards(self, card):
        if card in {'10', 'J', 'Q', 'K'}:
            self._seen_cards['10-J-Q-K'] += 1
        else:
            self._seen_cards[card] += 1
    
    @property
    def seen_cards(self):
        return self._seen_cards
        
    def remaining_decks(self):
        ratio = len(self._cards)/52
        if ratio >= 0.75:
            return round(ratio, 0)
        elif 0.25 < ratio < 0.75:
            return 0.5
        return 0.25
    
    def cut_card_reached(self, penetration):
        used_cards = self._total_cards - len(self._cards)
        return used_cards/self._total_cards >= penetration
    
    def running_count(self, strategy):
        running_count = sum(count_dict[strategy][k] * self._seen_cards[k] for k in self._seen_cards)
        starting_count = starting_count_dict[strategy] * (self._shoe_size - 1)
        return running_count + starting_count

    def true_count(self, strategy):
        if strategy == CountingStrategy.KO:
            raise ValueError('"true_count" is only applicable for balanced counting systems.')
        return round(self.running_count(strategy=strategy)/self.remaining_decks(), 0)