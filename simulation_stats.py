class SimulationStats(object):
    """
    SimulationStats is an object that stores results from simulating
    games of blackjack.

    """
    def __init__(self):
        self._stats_dict = {}

    @property
    def stats_dict(self):
        return self._stats_dict

    def create_player_key(self, player_key):
        self._stats_dict[player_key] = {}

    def create_count_key(self, player_key, count_key):
        if count_key not in self._stats_dict[player_key]:
            self._stats_dict[player_key][count_key] = {}

    def create_outcome_key(self, player_key, count_key):
        if ('win' or 'loss' or 'push') not in self._stats_dict[player_key][count_key]:
            self._stats_dict[player_key][count_key]['win'] = {}
            self._stats_dict[player_key][count_key]['loss'] = {}
            self._stats_dict[player_key][count_key]['push'] = {}
            self._stats_dict[player_key][count_key]['win']['natural blackjack'] = 0
            self._stats_dict[player_key][count_key]['loss']['surrender'] = 0
            for outcome_key in ['win', 'loss']:
                self._stats_dict[player_key][count_key][outcome_key]['insurance'] = 0
            for outcome_key in ['win', 'loss', 'push']:
                self._stats_dict[player_key][count_key][outcome_key]['number of rounds'] = 0
                self._stats_dict[player_key][count_key][outcome_key]['double down'] = 0
                self._stats_dict[player_key][count_key][outcome_key]['double after split'] = 0
                self._stats_dict[player_key][count_key][outcome_key]['split'] = 0
                self._stats_dict[player_key][count_key][outcome_key]['other'] = 0

    def natural_blackjack(self, player_key, count_key):
        self._stats_dict[player_key][count_key]['win']['natural blackjack'] += 1
        self._stats_dict[player_key][count_key]['win']['number of rounds'] += 1

    def insurance(self, player_key, count_key, outcome_key):
        self._stats_dict[player_key][count_key][outcome_key]['insurance'] += 1

    def surrender(self, player_key, count_key):
        self._stats_dict[player_key][count_key]['loss']['surrender'] += 1
        self._stats_dict[player_key][count_key]['loss']['number of rounds'] += 1

    def other(self, player_key, count_key, outcome_key, hand_key=1, double_down=False):
        self._stats_dict[player_key][count_key][outcome_key]['number of rounds'] += 1
        if hand_key == 1:
            if double_down:
                self._stats_dict[player_key][count_key][outcome_key]['double down'] += 1
            else:
                self._stats_dict[player_key][count_key][outcome_key]['other'] += 1
        else:
            if double_down:
                self._stats_dict[player_key][count_key][outcome_key]['double after split'] += 1
            else:
                self._stats_dict[player_key][count_key][outcome_key]['split'] += 1





