import pytest

from simulation_stats import SimulationStats
from house_rules import HouseRules


class TestSimulationStats(object):

    def test_init_no_rules(self):
        with pytest.raises(Exception):
            SimulationStats()

    def test_init_incorrect_rules(self):
        with pytest.raises(ValueError):
            SimulationStats(rules='Incorrect argument')

    def test_init_correct_rules(self):
        rules = HouseRules(bet_limits=[10, 500])
        stats = SimulationStats(rules=rules)
        assert stats.stats_dict == {}

    def test_create_player_key(self):
        rules = HouseRules(bet_limits=[10, 500])
        stats = SimulationStats(rules=rules)

        # new player key added
        stats.create_player_key(player_key='Player 1')
        assert stats.stats_dict == {'Player 1': {}}

        # player key already exists
        stats.create_player_key(player_key='Player 1')
        assert stats.stats_dict == {'Player 1': {}}

    def test_create_count_key(self):
        rules = HouseRules(bet_limits=[10, 500])
        stats = SimulationStats(rules=rules)
        stats.create_player_key(player_key='Player 1')

        # new count key added
        stats.create_count_key(player_key='Player 1', count_key=0)
        assert stats.stats_dict['Player 1'][0]['initial bet'] == 0

        # count key already exists
        stats.create_count_key(player_key='Player 1', count_key=0)
        assert stats.stats_dict['Player 1'][0]['initial bet'] == 0

    def test_player_bets(self):
        rules = HouseRules(bet_limits=[10, 500])
        stats = SimulationStats(rules=rules)
        stats.create_player_key(player_key='Player 1')
        stats.create_count_key(player_key='Player 1', count_key=0)

        assert stats.stats_dict['Player 1'][0]['initial bet'] == 0
        assert stats.stats_dict['Player 1'][0]['overall bet'] == 0

        stats.player_bets(player_key='Player 1', count_key=0, amount=10, initial_amount=10)

        assert stats.stats_dict['Player 1'][0]['initial bet'] == 10
        assert stats.stats_dict['Player 1'][0]['overall bet'] == 10

    def test_player_insurance_win(self):
        rules = HouseRules(bet_limits=[10, 500])
        stats = SimulationStats(rules=rules)
        stats.create_player_key(player_key='Player 1')
        stats.create_count_key(player_key='Player 1', count_key=0)

        assert stats.stats_dict['Player 1'][0]['player insurance win'] == 0
        assert stats.stats_dict['Player 1'][0]['net winnings'] == 0
        assert stats.stats_dict['Player 1'][0]['overall bet'] == 0

        stats.player_insurance_win(player_key='Player 1', count_key=0, insurance_amount=5)

        assert stats.stats_dict['Player 1'][0]['player insurance win'] == 1
        assert stats.stats_dict['Player 1'][0]['net winnings'] == 10
        assert stats.stats_dict['Player 1'][0]['overall bet'] == 5

    def test_dealer_insurance_win(self):
        rules = HouseRules(bet_limits=[10, 500])
        stats = SimulationStats(rules=rules)
        stats.create_player_key(player_key='Player 1')
        stats.create_count_key(player_key='Player 1', count_key=0)

        assert stats.stats_dict['Player 1'][0]['dealer insurance win'] == 0
        assert stats.stats_dict['Player 1'][0]['net winnings'] == 0
        assert stats.stats_dict['Player 1'][0]['overall bet'] == 0

        stats.dealer_insurance_win(player_key='Player 1', count_key=0, insurance_amount=5)

        assert stats.stats_dict['Player 1'][0]['dealer insurance win'] == 1
        assert stats.stats_dict['Player 1'][0]['net winnings'] == -5
        assert stats.stats_dict['Player 1'][0]['overall bet'] == 5

    def test_player_showdown_win(self):
        rules = HouseRules(bet_limits=[10, 500])
        stats = SimulationStats(rules=rules)
        stats.create_player_key(player_key='Player 1')
        stats.create_count_key(player_key='Player 1', count_key=0)

        assert stats.stats_dict['Player 1'][0]['player showdown win'] == 0
        assert stats.stats_dict['Player 1'][0]['number of hands'] == 0
        assert stats.stats_dict['Player 1'][0]['net winnings'] == 0
        assert stats.stats_dict['Player 1'][0]['overall bet'] == 0
        assert stats.stats_dict['Player 1'][0]['initial bet'] == 0

        stats.player_showdown_win(player_key='Player 1', count_key=0, amount=10, initial_amount=10)

        assert stats.stats_dict['Player 1'][0]['player showdown win'] == 1
        assert stats.stats_dict['Player 1'][0]['number of hands'] == 1
        assert stats.stats_dict['Player 1'][0]['net winnings'] == 10
        assert stats.stats_dict['Player 1'][0]['overall bet'] == 10
        assert stats.stats_dict['Player 1'][0]['initial bet'] == 10

    def test_dealer_showdown_win(self):
        rules = HouseRules(bet_limits=[10, 500])
        stats = SimulationStats(rules=rules)
        stats.create_player_key(player_key='Player 1')
        stats.create_count_key(player_key='Player 1', count_key=0)

        assert stats.stats_dict['Player 1'][0]['dealer showdown win'] == 0
        assert stats.stats_dict['Player 1'][0]['number of hands'] == 0
        assert stats.stats_dict['Player 1'][0]['net winnings'] == 0
        assert stats.stats_dict['Player 1'][0]['overall bet'] == 0
        assert stats.stats_dict['Player 1'][0]['initial bet'] == 0

        stats.dealer_showdown_win(player_key='Player 1', count_key=0, amount=10, initial_amount=10)

        assert stats.stats_dict['Player 1'][0]['dealer showdown win'] == 1
        assert stats.stats_dict['Player 1'][0]['number of hands'] == 1
        assert stats.stats_dict['Player 1'][0]['net winnings'] == -10
        assert stats.stats_dict['Player 1'][0]['overall bet'] == 10
        assert stats.stats_dict['Player 1'][0]['initial bet'] == 10

    def test_push(self):
        rules = HouseRules(bet_limits=[10, 500])
        stats = SimulationStats(rules=rules)
        stats.create_player_key(player_key='Player 1')
        stats.create_count_key(player_key='Player 1', count_key=0)

        assert stats.stats_dict['Player 1'][0]['push'] == 0
        assert stats.stats_dict['Player 1'][0]['number of hands'] == 0
        assert stats.stats_dict['Player 1'][0]['net winnings'] == 0
        assert stats.stats_dict['Player 1'][0]['overall bet'] == 0
        assert stats.stats_dict['Player 1'][0]['initial bet'] == 0

        stats.push(player_key='Player 1', count_key=0, amount=10, initial_amount=10)

        assert stats.stats_dict['Player 1'][0]['push'] == 1
        assert stats.stats_dict['Player 1'][0]['number of hands'] == 1
        assert stats.stats_dict['Player 1'][0]['net winnings'] == 0
        assert stats.stats_dict['Player 1'][0]['overall bet'] == 10
        assert stats.stats_dict['Player 1'][0]['initial bet'] == 10

    def test_player_surrender(self):
        rules = HouseRules(bet_limits=[10, 500])
        stats = SimulationStats(rules=rules)
        stats.create_player_key(player_key='Player 1')
        stats.create_count_key(player_key='Player 1', count_key=0)

        assert stats.stats_dict['Player 1'][0]['player surrender'] == 0
        assert stats.stats_dict['Player 1'][0]['number of hands'] == 0
        assert stats.stats_dict['Player 1'][0]['net winnings'] == 0
        assert stats.stats_dict['Player 1'][0]['overall bet'] == 0
        assert stats.stats_dict['Player 1'][0]['initial bet'] == 0

        stats.player_surrender(player_key='Player 1', count_key=0, amount=10, initial_amount=10)

        assert stats.stats_dict['Player 1'][0]['player surrender'] == 1
        assert stats.stats_dict['Player 1'][0]['number of hands'] == 1
        assert stats.stats_dict['Player 1'][0]['net winnings'] == -5
        assert stats.stats_dict['Player 1'][0]['overall bet'] == 10
        assert stats.stats_dict['Player 1'][0]['initial bet'] == 10

    def test_player_bust(self):
        rules = HouseRules(bet_limits=[10, 500])
        stats = SimulationStats(rules=rules)
        stats.create_player_key(player_key='Player 1')
        stats.create_count_key(player_key='Player 1', count_key=0)

        assert stats.stats_dict['Player 1'][0]['player bust'] == 0
        assert stats.stats_dict['Player 1'][0]['number of hands'] == 0
        assert stats.stats_dict['Player 1'][0]['net winnings'] == 0
        assert stats.stats_dict['Player 1'][0]['overall bet'] == 0
        assert stats.stats_dict['Player 1'][0]['initial bet'] == 0

        stats.player_bust(player_key='Player 1', count_key=0, amount=10, initial_amount=10)

        assert stats.stats_dict['Player 1'][0]['player bust'] == 1
        assert stats.stats_dict['Player 1'][0]['number of hands'] == 1
        assert stats.stats_dict['Player 1'][0]['net winnings'] == -10
        assert stats.stats_dict['Player 1'][0]['overall bet'] == 10
        assert stats.stats_dict['Player 1'][0]['initial bet'] == 10

    def test_dealer_bust(self):
        rules = HouseRules(bet_limits=[10, 500])
        stats = SimulationStats(rules=rules)
        stats.create_player_key(player_key='Player 1')
        stats.create_count_key(player_key='Player 1', count_key=0)

        assert stats.stats_dict['Player 1'][0]['dealer bust'] == 0
        assert stats.stats_dict['Player 1'][0]['number of hands'] == 0
        assert stats.stats_dict['Player 1'][0]['net winnings'] == 0
        assert stats.stats_dict['Player 1'][0]['overall bet'] == 0
        assert stats.stats_dict['Player 1'][0]['initial bet'] == 0

        stats.dealer_bust(player_key='Player 1', count_key=0, amount=10, initial_amount=10)

        assert stats.stats_dict['Player 1'][0]['dealer bust'] == 1
        assert stats.stats_dict['Player 1'][0]['number of hands'] == 1
        assert stats.stats_dict['Player 1'][0]['net winnings'] == 10
        assert stats.stats_dict['Player 1'][0]['overall bet'] == 10
        assert stats.stats_dict['Player 1'][0]['initial bet'] == 10

    def test_player_natural_blackjack(self):
        rules = HouseRules(bet_limits=[10, 500])
        stats = SimulationStats(rules=rules)
        stats.create_player_key(player_key='Player 1')
        stats.create_count_key(player_key='Player 1', count_key=0)

        assert stats.stats_dict['Player 1'][0]['player natural blackjack'] == 0
        assert stats.stats_dict['Player 1'][0]['number of hands'] == 0
        assert stats.stats_dict['Player 1'][0]['net winnings'] == 0
        assert stats.stats_dict['Player 1'][0]['overall bet'] == 0
        assert stats.stats_dict['Player 1'][0]['initial bet'] == 0

        stats.player_natural_blackjack(player_key='Player 1', count_key=0, amount=10, initial_amount=10)

        assert stats.stats_dict['Player 1'][0]['player natural blackjack'] == 1
        assert stats.stats_dict['Player 1'][0]['number of hands'] == 1
        assert stats.stats_dict['Player 1'][0]['net winnings'] == 10 * rules.blackjack_payout
        assert stats.stats_dict['Player 1'][0]['overall bet'] == 10
        assert stats.stats_dict['Player 1'][0]['initial bet'] == 10

    def test_dealer_natural_blackjack(self):
        rules = HouseRules(bet_limits=[10, 500])
        stats = SimulationStats(rules=rules)
        stats.create_player_key(player_key='Player 1')
        stats.create_count_key(player_key='Player 1', count_key=0)

        assert stats.stats_dict['Player 1'][0]['dealer natural blackjack'] == 0
        assert stats.stats_dict['Player 1'][0]['number of hands'] == 0
        assert stats.stats_dict['Player 1'][0]['net winnings'] == 0
        assert stats.stats_dict['Player 1'][0]['overall bet'] == 0
        assert stats.stats_dict['Player 1'][0]['initial bet'] == 0

        stats.dealer_natural_blackjack(player_key='Player 1', count_key=0, amount=10, initial_amount=10)

        assert stats.stats_dict['Player 1'][0]['dealer natural blackjack'] == 1
        assert stats.stats_dict['Player 1'][0]['number of hands'] == 1
        assert stats.stats_dict['Player 1'][0]['net winnings'] == -10
        assert stats.stats_dict['Player 1'][0]['overall bet'] == 10
        assert stats.stats_dict['Player 1'][0]['initial bet'] == 10