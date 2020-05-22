from house_rules import HouseRules


class SimulationStats(object):
    """
    SimulationStats is an object that stores results from simulating
    games of blackjack.

    """
    def __init__(self):
        self.stats_dict = {}

    def get_stats_dict(self):
        return self.stats_dict

    def create_player_key(self, player_key):
        if player_key not in self.stats_dict:
            self.stats_dict[player_key] = {}

    def create_count_key(self, player_key, count_key):
        if count_key not in self.stats_dict[player_key]:
            self.stats_dict[player_key][count_key] = {}

    def create_outcome_key(self, player_key, count_key):
        if ('win' or 'loss' or 'push') not in self.stats_dict[player_key][count_key]:
            self.stats_dict[player_key][count_key]['win'] = {}
            self.stats_dict[player_key][count_key]['loss'] = {}
            self.stats_dict[player_key][count_key]['push'] = {}
            self.stats_dict[player_key][count_key]['win']['natural blackjack'] = 0
            self.stats_dict[player_key][count_key]['loss']['surrender'] = 0
            for outcome_key in ['win', 'loss']:
                self.stats_dict[player_key][count_key][outcome_key]['insurance'] = 0
            for outcome_key in ['win', 'loss', 'push']:
                self.stats_dict[player_key][count_key][outcome_key]['number of hands'] = 0
                self.stats_dict[player_key][count_key][outcome_key]['double down'] = 0
                self.stats_dict[player_key][count_key][outcome_key]['double after split'] = 0
                self.stats_dict[player_key][count_key][outcome_key]['split'] = 0
                self.stats_dict[player_key][count_key][outcome_key]['other'] = 0

    def natural_blackjack(self, player_key, count_key):
        self.stats_dict[player_key][count_key]['win']['natural blackjack'] += 1
        self.stats_dict[player_key][count_key]['win']['number of hands'] += 1

    def insurance(self, player_key, count_key, outcome_key):
        self.stats_dict[player_key][count_key][outcome_key]['insurance'] += 1

    def surrender(self, player_key, count_key):
        self.stats_dict[player_key][count_key]['loss']['surrender'] += 1
        self.stats_dict[player_key][count_key]['loss']['number of hands'] += 1

    def other(self, player_key, count_key, outcome_key, hand_key=1, double_down=False):
        self.stats_dict[player_key][count_key][outcome_key]['number of hands'] += 1
        if hand_key == 1:
            if double_down:
                self.stats_dict[player_key][count_key][outcome_key]['double down'] += 1
            else:
                self.stats_dict[player_key][count_key][outcome_key]['other'] += 1
        else:
            if double_down:
                self.stats_dict[player_key][count_key][outcome_key]['double after split'] += 1
            else:
                self.stats_dict[player_key][count_key][outcome_key]['split'] += 1





