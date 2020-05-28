from playing_strategy import PlayingStrategy
from house_rules import HouseRules
from simulation_stats import SimulationStats


class Player(object):
    """
    Player is an object that represents an individual player at the table.

    """
    def __init__(
            self, name, rules, bankroll, min_bet, bet_spread=None, bet_count_amount=None,
            play_strategy='Basic', bet_strategy='Flat', count_strategy=None, insurance=None,
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
            at that running or true count. These values are used to create a bet ramp that
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
        insurance : float, optional
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
        if bet_count_amount is not None and bet_spread is not None:
            if bet_count_amount[len(bet_count_amount) - 1][1] > min_bet * bet_spread:
                raise ValueError('Last amount in bet count amount must be less than the maximum player bet.')
        if play_strategy not in ['Basic']:
            raise ValueError('Playing strategy must be "Basic".')
        if bet_strategy not in ['Flat', 'Spread']:
            raise ValueError('Betting strategy must be either "Flat" or "Spread".')
        if count_strategy is not None:
            if count_strategy not in ['Hi-Lo', 'Hi-Opt I', 'Hi-Opt II', 'Omega II', 'Halves', 'Zen Count', 'KO']:
                raise ValueError('Count Strategy must be "Hi-Lo", "Hi-Opt I", "Hi-Opt II", "Omega II", '
                                 '"Halves", "Zen Count", or "KO".')
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
        self._name = str(name)
        self.rules = rules
        self._bankroll = float(bankroll)
        self._min_bet = float(min_bet)
        self._bet_spread = bet_spread
        if bet_strategy == 'Spread' and bet_count_amount is not None:
            bet_ramp = {}
            for count, amount in bet_count_amount:
                bet_ramp[count] = round(amount, 2)
            self._bet_ramp = bet_ramp
        else:
            self._bet_ramp = None
        self.play_strategy = PlayingStrategy(rules=rules, strategy=play_strategy)
        self._bet_strategy = bet_strategy
        self._count_strategy = count_strategy
        self._insurance = insurance
        self._back_counting = back_counting
        self._back_counting_entry_exit = back_counting_entry_exit
        self._bet_count = 0
        self._pre_insurance_count = None
        self._hands_dict = None
        self._stats = SimulationStats()

    @property
    def name(self):
        return self._name

    @property
    def bankroll(self):
        return self._bankroll

    @property
    def min_bet(self):
        return self._min_bet

    @property
    def bet_spread(self):
        return self._bet_spread

    @property
    def bet_ramp(self):
        return self._bet_ramp

    @property
    def bet_strategy(self):
        return self._bet_strategy

    @property
    def count_strategy(self):
        return self._count_strategy

    @property
    def insurance(self):
        return self._insurance

    @property
    def back_counting(self):
        return self._back_counting

    @property
    def back_counting_entry(self):
        return self._back_counting_entry_exit[0]

    @property
    def back_counting_exit(self):
        return self._back_counting_entry_exit[1]

    @property
    def bet_count(self):
        return self._bet_count

    @bet_count.setter
    def bet_count(self, value):
        self._bet_count = value

    @property
    def pre_insurance_count(self):
        return self._pre_insurance_count

    @pre_insurance_count.setter
    def pre_insurance_count(self, value):
        self._pre_insurance_count = value

    @property
    def hands_dict(self):
        return self._hands_dict

    @property
    def stats(self):
        return self._stats

    def get_hand(self, key):
        return self._hands_dict[key]['hand']

    def set_hand(self):
        self._hands_dict = {1: {}}
        self._hands_dict[1]['hand'] = []
        self._hands_dict[1]['insurance'] = False
        self._hands_dict[1]['stand'] = False
        self._hands_dict[1]['surrender'] = False
        self._hands_dict[1]['natural blackjack'] = False
        self._hands_dict[1]['double down'] = False
        self._hands_dict[1]['split'] = False
        self._hands_dict[1]['busted'] = False
        self._hands_dict[1]['settled natural blackjack'] = False

    def get_insurance(self):
        return self._hands_dict[1]['insurance']

    def set_insurance(self):
        self._hands_dict[1]['insurance'] = True

    def get_stand(self, key):
        return self._hands_dict[key]['stand']

    def set_stand(self, key):
        self._hands_dict[key]['stand'] = True

    def get_settled_natural_blackjack(self):
        return self._hands_dict[1]['settled natural blackjack']

    def set_settled_natural_blackjack(self):
        self._hands_dict[1]['settled natural blackjack'] = True
        self.set_stand(key=1)

    def get_surrender(self):
        return self._hands_dict[1]['surrender']

    def set_surrender(self):
        self._hands_dict[1]['surrender'] = True
        self.set_stand(key=1)

    def get_natural_blackjack(self):
        return self._hands_dict[1]['natural blackjack']

    def set_natural_blackjack(self):
        self._hands_dict[1]['natural blackjack'] = True

    def get_double_down(self, key):
        return self._hands_dict[key]['double down']

    def set_double_down(self, key, new_card):
        self._hands_dict[key]['double down'] = True
        self.hit(key=key, new_card=new_card)
        self.set_stand(key=key)

    def get_split(self, key):
        return self._hands_dict[key]['split']

    def set_split(self, key, new_key):
        self._hands_dict[key]['split'] = True
        self._hands_dict[new_key] = {}
        self._hands_dict[new_key]['hand'] = [self.get_hand(key=key).pop()]
        self._hands_dict[new_key]['stand'] = False
        self._hands_dict[new_key]['double down'] = False
        self._hands_dict[new_key]['split'] = True
        self._hands_dict[new_key]['busted'] = False

    def get_busted(self, key):
        return self._hands_dict[key]['busted']

    def set_busted(self, key):
        self._hands_dict[key]['busted'] = True
        self.set_stand(key=key)

    def hit(self, key, new_card):
        self._hands_dict[key]['hand'].append(new_card)

    def decision(self, total, hand, pair, soft_hand, dealer_up_card):
        if pair:
            if hand[0] >= 10:
                return self.play_strategy.pair()[10][dealer_up_card]
            else:
                return self.play_strategy.pair()[hand[0]][dealer_up_card]
        elif soft_hand:
            return self.play_strategy.soft()[total][dealer_up_card]
        else:
            return self.play_strategy.hard()[total][dealer_up_card]
