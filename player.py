import card_values as cv
from helper import count_hand, splittable
from playing_strategy import PlayingStrategy
from betting_strategy import BettingStrategy
from house_rules import HouseRules


class Player(object):
    """
    Player is an object that represents an individual player at the table.

    """
    def __init__(
            self, name, rules, bankroll, min_bet, bet_spread=None, bet_count_amount=None, play_strategy='Basic',
            bet_strategy='Flat', count_strategy=None, true_count_accuracy=None, insurance_count=None,
            back_counting=False, back_counting_entry_exit=None
    ):
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
            Ratio of maximum bet to minimum bet (default is None)
        bet_count_amount : list of tuples, optional
            List of tuples in ascending order, where the first value of the tuple indicates
            the running or true count and the second value indicates the amount of money wagered
            at that running or true count. These values are used to create a bet scale that
            increments by a custom amount (default is None)
        play_strategy : str, optional
            Name of the play strategy used by the player (default is "Basic", which implies
            the player plays optimally)
        bet_strategy : str, optional
            Name of the bet strategy used by the player (default is "Flat", which implies
            the player bets the same amount every hand)
        count_strategy : str, optional
            Name of the balanced or unbalanced card counting strategy used by the player (default is
            None, which implies the player does not count cards)
        true_count_accuracy : float, optional
            Accuracy of the balanced card counting strategy (default is None)
        insurance_count : float, optional
            Minimum running or true count at which a player will purchase insurance, if
            available (default is None)
        back_counting : bool, optional
            True if player is back counting the shoe (i.e. wonging), false otherwise (default is
            False)
        back_counting_entry_exit : list, optional
            Running or true count at which the back counter will start and stop playing hands at the
            table (default is None)
        """
        if not isinstance(name, str):
            raise TypeError('Name must be of type string.')
        if not isinstance(rules, HouseRules):
            raise TypeError('Rules must be of type HouseRules.')
        if bankroll < rules.min_bet or bankroll < min_bet:
            raise ValueError('Initial bankroll must be greater than or equal to both player and table minimum bet.')
        if min_bet < rules.min_bet or min_bet > rules.max_bet:
            raise ValueError('Minimum bet is not allowed according to the table rules.')
        if bet_strategy == 'Spread' and bet_spread is None:
            raise ValueError('Bet spread cannot be None with a "Spread" betting strategy.')
        if bet_strategy == 'Spread' and bet_spread is not None and bet_spread < 1:
            raise ValueError('Bet spread must be greater than 1.')
        if bet_spread is not None and bet_spread > float(rules.max_bet/min_bet):
            raise ValueError('Bet spread is too large.')
        if bet_strategy == 'Spread' and count_strategy is None:
            raise ValueError('Count strategy cannot be None with a "Spread" betting strategy.')
        if bet_strategy == 'Spread' and bet_count_amount is None:
            raise ValueError('Bet count amount cannot be None with a "Spread" betting strategy.')
        if bet_count_amount is not None and not all(isinstance(x, tuple) for x in bet_count_amount):
            raise TypeError('Bet count amount must be made up of a list of tuples.')
        if bet_count_amount is not None and not all(isinstance(x[0], (int, float)) for x in bet_count_amount):
            raise TypeError('Count for bet count amount must be either an integer or floating point.')
        if bet_count_amount is not None and not all(isinstance(x[1], (int, float)) for x in bet_count_amount):
            raise TypeError('Amount for bet count amount must be either an integer or floating point.')
        if bet_count_amount is not None and sorted(bet_count_amount, key=lambda x: x[0]) != bet_count_amount:
            raise ValueError('Bet count amount must be sorted from least to greatest counts.')
        if bet_count_amount is not None and sorted(bet_count_amount, key=lambda x: x[1]) != bet_count_amount:
            raise ValueError('Bet count amount must be sorted from least to greatest amounts.')
        if bet_count_amount is not None and bet_count_amount[0][1] != min_bet:
            raise ValueError('First amount in bet count amount must be the minimum player bet.')
        if bet_count_amount is not None and bet_spread is not None and \
                bet_count_amount[len(bet_count_amount) - 1][1] > min_bet * bet_spread:
            raise ValueError('Last amount in bet count amount must be less than the maximum player bet.')
        if play_strategy not in ['Basic']:
            raise ValueError('Playing strategy must be "Basic".')
        if bet_strategy not in ['Flat', 'Spread']:
            raise ValueError('Betting strategy must be either "Flat" or "Spread".')
        if count_strategy is not None:
            if count_strategy not in ['Hi-Lo', 'Hi-Opt I', 'Hi-Opt II', 'Omega II', 'Halves', 'Zen Count', 'KO']:
                raise ValueError('Count Strategy must be "Hi-Lo", "Hi-Opt I", "Hi-Opt II", "Omega II", '
                                 '"Halves", "Zen Count", or "KO".')
        if true_count_accuracy is None and count_strategy in ['Hi-Lo', 'Hi-Opt I', 'Hi-Opt II', 'Omega II', 'Halves',
                                                              'Zen Count']:
            raise ValueError('True count accuracy cannot be None while using a balanced card counting system.')
        if true_count_accuracy is not None and count_strategy == 'KO':
            raise ValueError('True count accuracy must be None while using an unbalanced card counting system.')
        if true_count_accuracy is not None and count_strategy is None:
            raise ValueError('True count accuracy must be None if the player is not counting cards.')
        if back_counting and count_strategy is None:
            raise ValueError('Back counting requires a counting strategy.')
        if not back_counting and back_counting_entry_exit is not None:
            raise ValueError('Back counting entry/exit point should be None.')
        if back_counting and back_counting_entry_exit is None:
            raise ValueError('Back counting entry/exit point cannot be None.')
        if back_counting and not all(isinstance(x, (int, float)) for x in back_counting_entry_exit):
            raise ValueError('Back counting entry/exit points must be either integers or floating points.')
        if back_counting and len(back_counting_entry_exit) != 2:
            raise ValueError('Back counting entry/exit point must be a list of two values.')
        self.name = str(name)
        self.rules = rules
        self.bankroll = float(bankroll)
        self.min_bet = float(min_bet)
        self.bet_spread = bet_spread
        if bet_strategy == 'Flat':
            self.bet_scale = None
        if bet_strategy == 'Spread' and bet_count_amount is not None:
            bet_scale = {}
            for count, amount in bet_count_amount:
                bet_scale[count] = round(amount, 2)
            self.bet_scale = bet_scale
        self.play_strategy = PlayingStrategy(rules=rules, strategy=play_strategy)
        self.bet_strategy = BettingStrategy(strategy=bet_strategy)
        self.count_strategy = count_strategy
        self.true_count_accuracy = true_count_accuracy
        self.insurance_count = insurance_count
        self.back_counting = back_counting
        self.back_counting_entry_exit = back_counting_entry_exit
        self.count = 0
        self.hands_dict = {}

    def get_name(self):
        return self.name

    def get_bankroll(self):
        return self.bankroll

    def get_min_bet(self):
        return self.min_bet

    def get_bet_spread(self):
        return self.bet_spread

    def get_bet_scale(self):
        return self.bet_scale

    def get_count_strategy(self):
        return self.count_strategy

    def get_true_count_accuracy(self):
        return self.true_count_accuracy

    def get_insurance_count(self):
        return self.insurance_count

    def get_back_counting(self):
        return self.back_counting

    def get_back_counting_entry_exit(self):
        return self.back_counting_entry_exit

    def get_count(self):
        return self.count

    def get_hands_dict(self):
        return self.hands_dict

    def set_bankroll(self, amount):
        self.bankroll = amount

    def set_count(self, count):
        self.count = count

    def increment_bankroll(self, amount):
        self.bankroll = self.bankroll + amount

    def sufficient_funds(self, amount):
        if amount < 0:
            raise ValueError('Amount needs to be a positive value.')
        return self.bankroll - amount >= 0

    def create_hand(self, amount):
        self.hands_dict = {1: {}}
        self.hands_dict[1]['hand'] = []
        self.hands_dict[1]['initial bet'] = amount
        self.hands_dict[1]['insurance bet'] = 0
        self.hands_dict[1]['bet'] = amount
        self.hands_dict[1]['insurance'] = False
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

    def get_hand(self, key):
        return self.hands_dict[key]['hand']

    def get_initial_bet(self):
        return self.hands_dict[1]['initial bet']

    def get_insurance_bet(self):
        return self.hands_dict[1]['insurance bet']

    def get_bet(self, key):
        return self.hands_dict[key]['bet']

    def get_insurance(self):
        return self.hands_dict[1]['insurance']

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

    def insurance(self):
        self.hands_dict[1]['insurance'] = True
        self.hands_dict[1]['insurance bet'] = 0.5 * self.get_initial_bet()

    def natural_blackjack(self):
        self.hands_dict[1]['natural blackjack'] = True

    def surrender(self):
        self.hands_dict[1]['surrender'] = True

    def stand(self, key):
        self.hands_dict[key]['stand'] = True

    def busted(self, key):
        self.hands_dict[key]['busted'] = True
        self.stand(key=key)

    def hit(self, key, new_card):
        self.hands_dict[key]['hand'].append(new_card)

    def split(self, amount, key, new_key):
        if splittable(rules=self.rules, hand=self.hands_dict[key]['hand']):
            self.hands_dict[key]['split'] = True
            self.hands_dict[new_key] = {}
            self.hands_dict[new_key]['hand'] = [self.get_hand(key=key).pop()]
            self.hands_dict[new_key]['bet'] = amount
            self.hands_dict[new_key]['busted'] = False
            self.hands_dict[new_key]['split'] = True
            self.hands_dict[new_key]['stand'] = False

    def double_down(self, key, new_card):
        self.hands_dict[key]['bet'] = 2 * self.hands_dict[key]['bet']
        self.hit(key=key, new_card=new_card)
        self.stand(key=key)

    def decision(self, hand, dealer_up_card, num_hands, amount):
        if len(hand) == 1:  # if card is split, first action is always to hit
            return 'H'
        elif splittable(rules=self.rules, hand=hand) and num_hands < self.rules.max_hands \
                and self.sufficient_funds(amount=amount):
            if hand[0] == 'A':
                return self.play_strategy.splits()[hand[0]][dealer_up_card]
            elif cv.card_values[hand[0]] == 10:
                return self.play_strategy.splits()['10'][dealer_up_card]
            return self.play_strategy.splits()[hand[0]][dealer_up_card]
        else:
            soft_total, hard_total = count_hand(hand=hand)
            if soft_total > hard_total and 12 <= soft_total <= 21:  # must contain an Ace
                return self.play_strategy.soft()[soft_total][dealer_up_card]
            elif 2 <= hard_total <= 21:
                return self.play_strategy.hard()[hard_total][dealer_up_card]
            else:  # player is busted
                return 'B'
