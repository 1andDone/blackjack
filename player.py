from helper import count_hand, splittable
from playing_strategy import PlayingStrategy
from betting_strategy import BettingStrategy


class Player(object):
    """
    Player is an object that represents an individual player at the table.

    """
    def __init__(self, name, rules, bankroll, min_bet, bet_spread=1, play_strategy='Basic',
                 bet_strategy='Flat', count_strategy=None, count_accuracy=0.5, back_counting=False,
                 back_counting_entry=0, back_counting_exit=0):
        """
        Parameters
        ----------
        name : str
            Name of the player
        rules : HouseRules
            HouseRules class instance
        bankroll : float
            Amount of money a player starts out with when sitting down at a table
        min_bet : float
            Minimum amount of money a player is willing to wager when playing a hand
        bet_spread : float, optional
            Ratio of maximum bet to minimum bet (default is 1)
        play_strategy : str, optional
            Name of the play strategy used by the player (default is "Basic", which implies
            the player plays optimally)
        bet_strategy : str, optional
            Name of the bet strategy used by the player (default is "Flat", which implies
            the player bets the same amount every hand)
        count_strategy : str, optional
            Name of the card counting strategy used by the player (default is None, which implies
            the player does not count cards)
        count_accuracy : float, optional
            Accuracy of the card counting strategy (default is 0.5)
        back_counting : bool, optional
            True if player is back counting the shoe (i.e. wonging), false otherwise (default is
            False)
        back_counting_entry : int, optional
            Count at which the back counter will start playing hands at the table (default is 0)
        back_counting_exit : int, optional
            Count at which the back counter will stop playing hands at the table (default is 0)

        """
        if bankroll <= rules.min_bet:
            raise ValueError('Initial bankroll must be greater than minimum bet.')
        if bet_strategy == 'Variable' and bet_spread < 1:
            raise ValueError('Bet spread must be greater than 1.')
        if min_bet < rules.min_bet or min_bet > rules.max_bet:
            raise ValueError('Minimum bet is not allowed according to the table rules.')
        if bet_spread > float(rules.max_bet/min_bet):
            raise ValueError('Bet spread is too large.')
        if bet_strategy == 'Variable' and count_strategy is None:
            raise ValueError('Count strategy cannot be None with a "Variable" betting strategy.')
        if play_strategy not in ['Basic']:
            raise ValueError('Playing strategy must be "Basic".')
        if bet_strategy not in ['Flat', 'Variable']:
            raise ValueError('Betting strategy must be either "Flat" or "Variable".')
        if count_strategy is not None:
            if count_strategy not in ['Hi-Lo', 'Hi-Opt I', 'Hi-Opt II', 'Omega II', 'Halves', 'Zen Count']:
                raise ValueError('Count Strategy must be "Hi-Lo", "Hi-Opt I", "Hi-Opt II", "Omega II", '
                                 '"Halves", or "Zen Count".')
        if back_counting and count_strategy is None:
            raise ValueError('Back counting requires a counting strategy.')
        if back_counting and back_counting_entry < 0:
            raise ValueError('Back counting entry point must be zero or greater.')
        if back_counting and back_counting_entry <= back_counting_exit:
            raise ValueError('Back counting exit point must be less than back counting entry point.')
        self.name = str(name)
        self.rules = rules
        self.bankroll = float(bankroll)
        self.min_bet = float(min_bet)
        self.bet_spread = float(bet_spread)
        self.play_strategy = PlayingStrategy(rules=rules, strategy=play_strategy)
        self.bet_strategy = BettingStrategy(strategy=bet_strategy)
        self.count_strategy = count_strategy
        self.count_accuracy = count_accuracy
        self.back_counting = back_counting
        self.back_counting_entry = back_counting_entry
        self.back_counting_exit = back_counting_exit
        self.count = 0
        self.hands_dict = {}

    def get_name(self):
        return self.name

    def get_back_counting(self):
        return self.back_counting

    def get_back_counting_entry(self):
        return self.back_counting_entry

    def get_back_counting_exit(self):
        return self.back_counting_exit

    def set_count(self, count):
        self.count = count

    def get_count(self):
        return self.count

    def get_bankroll(self):
        return self.bankroll

    def get_min_bet(self):
        return self.min_bet

    def get_bet_spread(self):
        return self.bet_spread

    def increment_bankroll(self, amount):
        self.bankroll = self.bankroll + amount

    def set_bankroll(self, amount):
        self.bankroll = amount

    def sufficient_funds(self, amount):
        return self.bankroll - amount >= 0

    def get_count_accuracy(self):
        return self.count_accuracy

    def get_count_strategy(self):
        return self.count_strategy

    def get_hands_dict(self):
        return self.hands_dict

    def create_hand(self, amount):
        self.hands_dict = {1: {}}
        self.hands_dict[1]['hand'] = []
        self.hands_dict[1]['initial bet'] = amount
        self.hands_dict[1]['bet'] = amount
        self.hands_dict[1]['natural blackjack'] = False
        self.hands_dict[1]['surrender'] = False
        self.hands_dict[1]['busted'] = False
        self.hands_dict[1]['split'] = False
        self.hands_dict[1]['stand'] = False

    def initial_bet(self, amount):
        if amount < self.rules.min_bet:
            raise ValueError('Initial bet must exceed table minimum.')
        if amount > self.rules.max_bet:
            raise ValueError('Initial bet must not exceed table maximum.')
        self.increment_bankroll(amount=-amount)
        self.create_hand(amount=amount)

    def natural_blackjack(self):
        self.hands_dict[1]['natural blackjack'] = True

    def surrender(self):
        self.hands_dict[1]['surrender'] = True

    def busted(self, key):
        self.hands_dict[key]['busted'] = True
        self.stand(key=key)

    def stand(self, key):
        self.hands_dict[key]['stand'] = True

    def get_hand(self, key):
        return self.hands_dict[key]['hand']

    def get_initial_bet(self, key):
        return self.hands_dict[key]['initial bet']

    def get_bet(self, key):
        return self.hands_dict[key]['bet']

    def get_natural_blackjack(self):
        return self.hands_dict[1]['natural blackjack']

    def get_surrender(self):
        return self.hands_dict[1]['surrender']

    def get_busted(self, key):
        return self.hands_dict[key]['busted']

    def get_split(self, key):
        return self.hands_dict[key]['split']

    def get_stand(self, key):
        return self.hands_dict[key]['stand']

    def hit(self, key, new_card):
        self.hands_dict[key]['hand'].append(new_card)

    def double_down(self, key, new_card):
        self.hands_dict[key]['bet'] = 2 * self.hands_dict[key]['bet']
        self.hit(key=key, new_card=new_card)
        self.stand(key=key)

    def split(self, amount, key, new_key):
        if splittable(rules=self.rules, hand=self.hands_dict[key]['hand']):
            self.hands_dict[key]['split'] = True
            self.hands_dict[new_key] = {}
            self.hands_dict[new_key]['hand'] = [self.get_hand(key=key).pop()]
            self.hands_dict[new_key]['bet'] = amount
            self.hands_dict[new_key]['busted'] = False
            self.hands_dict[new_key]['split'] = True
            self.hands_dict[new_key]['stand'] = False

    def decision(self, hand, dealer_up_card, num_hands, amount):
        if len(hand) == 1:  # if card is split, first action is always to hit
            return 'H'
        elif splittable(rules=self.rules, hand=hand) and num_hands < self.rules.max_hands \
                and self.sufficient_funds(amount=amount):
            return self.play_strategy.splits()[hand[0]][dealer_up_card]
        else:
            soft_total, hard_total = count_hand(hand=hand)
            if soft_total > hard_total and 12 <= soft_total <= 21:  # must contain an Ace
                return self.play_strategy.soft()[soft_total][dealer_up_card]
            elif 2 <= hard_total <= 21:
                return self.play_strategy.hard()[hard_total][dealer_up_card]
            else:  # player is busted
                return 'B'
