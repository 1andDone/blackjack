class SimulationStats(object):
    """
    SimulationStats is an object that stores results from simulating
    games of blackjack.

    """
    def __init__(self):
        self._results_dict = {}

    @property
    def results_dict(self):
        return self._results_dict

    def create_count_key(self, count_key):
        if count_key not in self._results_dict:
            self._results_dict[count_key] = {}
            self._results_dict[count_key]['net winnings'] = 0
            self._results_dict[count_key]['overall bet'] = 0
            self._results_dict[count_key]['number of rounds'] = 0
            self._results_dict[count_key]['number of split hands'] = 0

    def update_results(self, count_key, hand_key=1, net_winnings=0, overall_bet=0, increment=1):
        self._results_dict[count_key]['net winnings'] += net_winnings
        self._results_dict[count_key]['overall bet'] += overall_bet
        if hand_key == 1:
            self._results_dict[count_key]['number of rounds'] += increment
        else:
            self._results_dict[count_key]['number of split hands'] += increment
