from blackjack.hand import Hand
from blackjack.playing_strategy import PlayingStrategy
from blackjack.simulation_stats import SimulationStats


class Player:
    """
    Represents an individual player at a blackjack
    table that bets a flat amount.

    """
    def __init__(self, name, bankroll, min_bet):
        """
        Parameters
        ----------
        name: str
            Name of the player
        bankroll: float
            Amount of money a player starts out with at a table
        min_bet: float
            Amount of money a player wagers when playing a hand
        
        """
        if bankroll < min_bet:
            raise ValueError("Insufficient bankroll to place the player's desired bet.")

        self._name = name
        self._bankroll = bankroll
        self._min_bet = min_bet
        self._hands = [Hand()]
        self._stats = SimulationStats()
    
    @property
    def name(self):
        return self._name
    
    @property
    def bankroll(self):
        return self._bankroll
    
    def initial_wager(self, **kwargs):
        return self._min_bet
    
    @property
    def hands(self):
        return self._hands
    
    @property
    def stats(self):
        return self._stats
    
    @property
    def first_hand(self):
        return self._hands[0]
    
    def edit_bankroll(self, amount):
        self._bankroll += amount
    
    def has_sufficient_bankroll(self, amount):
        return amount <= self._bankroll
    
    def _can_split(self, hand, rules):
        if self.has_sufficient_bankroll(amount=hand.total_bet):
            return hand.number_of_cards() == 2 and ((hand.cards[0] == hand.cards[1]) or 
                (rules.split_unlike_tens and all(card in {'10', 'J', 'Q', 'K'} for card in hand.cards))) and \
                len(self._hands) < rules.max_hands
        return False
    
    def decision(self, hand, dealer_up_card, rules):
        playing_strategy = PlayingStrategy(s17=rules.s17)
        if self._can_split(hand=hand, rules=rules):
            return playing_strategy.pair(card=hand.cards[0], dealer_up_card=dealer_up_card)
        if hand.is_soft():
            return playing_strategy.soft(total=hand.total(), dealer_up_card=dealer_up_card)
        return playing_strategy.hard(total=hand.total(), dealer_up_card=dealer_up_card)
    
    def reset_hands(self):
        self._hands = [Hand()]