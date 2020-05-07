from house_rules import HouseRules


class SimulationStats(object):
    """
    SimulationStats is an object that stores results from simulating
    games of blackjack.

    """
    def __init__(self, rules):
        """
        Parameters
        ----------
        rules : HouseRules
            HouseRules class instance
        """
        if not isinstance(rules, HouseRules):
            raise ValueError('Rules must be of type HouseRules.')
        self.rules = rules
        self.stats_dict = {}

    def get_stats_dict(self):
        return self.stats_dict

    def create_player_key(self, player_key):
        if player_key not in self.stats_dict.keys():
            self.stats_dict[player_key] = {}

    def create_count_key(self, player_key, count_key):
        if count_key not in self.stats_dict[player_key].keys():
            self.stats_dict[player_key][count_key] = {}
            self.stats_dict[player_key][count_key]['initial bet'] = 0
            self.stats_dict[player_key][count_key]['overall bet'] = 0
            self.stats_dict[player_key][count_key]['net winnings'] = 0
            self.stats_dict[player_key][count_key]['player insurance win'] = 0
            self.stats_dict[player_key][count_key]['dealer insurance win'] = 0
            self.stats_dict[player_key][count_key]['player showdown win'] = 0
            self.stats_dict[player_key][count_key]['dealer showdown win'] = 0
            self.stats_dict[player_key][count_key]['push'] = 0
            self.stats_dict[player_key][count_key]['player surrender'] = 0
            self.stats_dict[player_key][count_key]['player bust'] = 0
            self.stats_dict[player_key][count_key]['dealer bust'] = 0
            self.stats_dict[player_key][count_key]['player natural blackjack'] = 0
            self.stats_dict[player_key][count_key]['dealer natural blackjack'] = 0
            self.stats_dict[player_key][count_key]['number of hands'] = 0

    def player_bets(self, player_key, count_key, amount, initial_amount):
        self.stats_dict[player_key][count_key]['initial bet'] += initial_amount
        self.stats_dict[player_key][count_key]['overall bet'] += amount

    def player_insurance_win(self, player_key, count_key, insurance_amount):
        self.stats_dict[player_key][count_key]['player insurance win'] += 1
        self.stats_dict[player_key][count_key]['net winnings'] += 2 * insurance_amount
        self.stats_dict[player_key][count_key]['overall bet'] += insurance_amount

    def dealer_insurance_win(self, player_key, count_key, insurance_amount):
        self.stats_dict[player_key][count_key]['dealer insurance win'] += 1
        self.stats_dict[player_key][count_key]['net winnings'] += -insurance_amount
        self.stats_dict[player_key][count_key]['overall bet'] += insurance_amount

    def player_showdown_win(self, player_key, count_key, amount, initial_amount):
        self.stats_dict[player_key][count_key]['player showdown win'] += 1
        self.stats_dict[player_key][count_key]['number of hands'] += 1
        self.stats_dict[player_key][count_key]['net winnings'] += amount
        self.player_bets(player_key=player_key, count_key=count_key, amount=amount, initial_amount=initial_amount)

    def dealer_showdown_win(self, player_key, count_key, amount, initial_amount):
        self.stats_dict[player_key][count_key]['dealer showdown win'] += 1
        self.stats_dict[player_key][count_key]['number of hands'] += 1
        self.stats_dict[player_key][count_key]['net winnings'] += -amount
        self.player_bets(player_key=player_key, count_key=count_key, amount=amount, initial_amount=initial_amount)

    def push(self, player_key, count_key, amount, initial_amount):
        self.stats_dict[player_key][count_key]['push'] += 1
        self.stats_dict[player_key][count_key]['number of hands'] += 1
        self.player_bets(player_key=player_key, count_key=count_key, amount=amount, initial_amount=initial_amount)

    def player_surrender(self, player_key, count_key, amount, initial_amount):
        self.stats_dict[player_key][count_key]['player surrender'] += 1
        self.stats_dict[player_key][count_key]['number of hands'] += 1
        self.stats_dict[player_key][count_key]['net winnings'] += -0.5 * amount
        self.player_bets(player_key=player_key, count_key=count_key, amount=amount, initial_amount=initial_amount)

    def player_bust(self, player_key, count_key, amount, initial_amount):
        self.stats_dict[player_key][count_key]['player bust'] += 1
        self.stats_dict[player_key][count_key]['number of hands'] += 1
        self.stats_dict[player_key][count_key]['net winnings'] += -amount
        self.player_bets(player_key=player_key, count_key=count_key, amount=amount, initial_amount=initial_amount)

    def dealer_bust(self, player_key, count_key, amount, initial_amount):
        self.stats_dict[player_key][count_key]['dealer bust'] += 1
        self.stats_dict[player_key][count_key]['number of hands'] += 1
        self.stats_dict[player_key][count_key]['net winnings'] += amount
        self.player_bets(player_key=player_key, count_key=count_key, amount=amount, initial_amount=initial_amount)

    def player_natural_blackjack(self, player_key, count_key, amount, initial_amount):
        self.stats_dict[player_key][count_key]['player natural blackjack'] += 1
        self.stats_dict[player_key][count_key]['number of hands'] += 1
        self.stats_dict[player_key][count_key]['net winnings'] += self.rules.blackjack_payout * amount
        self.player_bets(player_key=player_key, count_key=count_key, amount=amount, initial_amount=initial_amount)

    def dealer_natural_blackjack(self, player_key, count_key, amount, initial_amount):
        self.stats_dict[player_key][count_key]['dealer natural blackjack'] += 1
        self.stats_dict[player_key][count_key]['number of hands'] += 1
        self.stats_dict[player_key][count_key]['net winnings'] += -amount
        self.player_bets(player_key=player_key, count_key=count_key, amount=amount, initial_amount=initial_amount)



