import pytest
from simulation_stats import SimulationStats
from house_rules import HouseRules


@pytest.fixture()
def setup_simulation_stats():
    s = SimulationStats()
    s.create_player_key(player_key='Player 1')
    s.create_count_key(player_key='Player 1', count_key=0)
    s.create_outcome_key(player_key='Player 1', count_key=0)
    return r, s


class TestSimulationStats(object):

    def test_create_player_key(self):
        """
        Tests the create_player_key method.

        """
        s = SimulationStats()

        # new player key added
        s.create_player_key(player_key='Player 1')
        assert s.stats_dict == {'Player 1': {}}

        # player key already exists
        s.create_player_key(player_key='Player 1')
        assert s.stats_dict == {'Player 1': {}}

    def test_create_count_key(self):
        """
        Tests the create_count_key method.

        """
        s = SimulationStats()
        s.create_player_key(player_key='Player 1')

        # new count key added
        s.create_count_key(player_key='Player 1', count_key=0)
        assert s.stats_dict['Player 1'][0] == {}

        # count key already exists
        s.create_count_key(player_key='Player 1', count_key=0)
        assert s.stats_dict['Player 1'][0] == {}

    def test_outcome_key(self):
        raise NotImplementedError()

    def test_player_bets(self, setup_simulation_stats):
        """
        Tests the player_bets method.

        """
        s = setup_simulation_stats

        s.player_bets(player_key='Player 1', count_key=0, amount=10, initial_amount=10)

        assert s.stats_dict['Player 1'][0]['initial bet'] == 10
        assert s.stats_dict['Player 1'][0]['overall bet'] == 10

    def test_player_insurance_win(self, setup_simulation_stats):
        """
        Tests the player_insurance_win method.

        """
        s = setup_simulation_stats

        s.player_insurance_win(player_key='Player 1', count_key=0, insurance_amount=5)

        assert s.stats_dict['Player 1'][0]['player insurance win'] == 1
        assert s.stats_dict['Player 1'][0]['net winnings'] == 10
        assert s.stats_dict['Player 1'][0]['overall bet'] == 5

    def test_dealer_insurance_win(self, setup_simulation_stats):
        """
        Tests the dealer_insurance_win method.

        """
        s = setup_simulation_stats

        s.dealer_insurance_win(player_key='Player 1', count_key=0, insurance_amount=5)

        assert s.stats_dict['Player 1'][0]['dealer insurance win'] == 1
        assert s.stats_dict['Player 1'][0]['net winnings'] == -5
        assert s.stats_dict['Player 1'][0]['overall bet'] == 5

    def test_player_showdown_win(self, setup_simulation_stats):
        """
        Tests the player_showdown_win method.

        """
        s = setup_simulation_stats

        s.player_showdown_win(player_key='Player 1', count_key=0, amount=10, initial_amount=10)

        assert s.stats_dict['Player 1'][0]['player showdown win'] == 1
        assert s.stats_dict['Player 1'][0]['number of hands'] == 1
        assert s.stats_dict['Player 1'][0]['net winnings'] == 10
        assert s.stats_dict['Player 1'][0]['overall bet'] == 10
        assert s.stats_dict['Player 1'][0]['initial bet'] == 10

    def test_dealer_showdown_win(self, setup_simulation_stats):
        """
        Tests the dealer_showdown_win method.

        """
        s = setup_simulation_stats

        s.dealer_showdown_win(player_key='Player 1', count_key=0, amount=10, initial_amount=10)

        assert s.stats_dict['Player 1'][0]['dealer showdown win'] == 1
        assert s.stats_dict['Player 1'][0]['number of hands'] == 1
        assert s.stats_dict['Player 1'][0]['net winnings'] == -10
        assert s.stats_dict['Player 1'][0]['overall bet'] == 10
        assert s.stats_dict['Player 1'][0]['initial bet'] == 10

    def test_push(self, setup_simulation_stats):
        """
        Tests the push method.

        """
        s = setup_simulation_stats

        s.push(player_key='Player 1', count_key=0, amount=10, initial_amount=10)

        assert s.stats_dict['Player 1'][0]['push'] == 1
        assert s.stats_dict['Player 1'][0]['number of hands'] == 1
        assert s.stats_dict['Player 1'][0]['net winnings'] == 0
        assert s.stats_dict['Player 1'][0]['overall bet'] == 10
        assert s.stats_dict['Player 1'][0]['initial bet'] == 10

    def test_player_surrender(self, setup_simulation_stats):
        """
        Tests the player_surrender method.

        """
        s = setup_simulation_stats

        s.player_surrender(player_key='Player 1', count_key=0, amount=10, initial_amount=10)

        assert s.stats_dict['Player 1'][0]['player surrender'] == 1
        assert s.stats_dict['Player 1'][0]['number of hands'] == 1
        assert s.stats_dict['Player 1'][0]['net winnings'] == -5
        assert s.stats_dict['Player 1'][0]['overall bet'] == 10
        assert s.stats_dict['Player 1'][0]['initial bet'] == 10

    def test_player_bust(self, setup_simulation_stats):
        """
        Tests the player_bust method.

        """
        s = setup_simulation_stats

        s.player_bust(player_key='Player 1', count_key=0, amount=10, initial_amount=10)

        assert s.stats_dict['Player 1'][0]['player bust'] == 1
        assert s.stats_dict['Player 1'][0]['number of hands'] == 1
        assert s.stats_dict['Player 1'][0]['net winnings'] == -10
        assert s.stats_dict['Player 1'][0]['overall bet'] == 10
        assert s.stats_dict['Player 1'][0]['initial bet'] == 10

    def test_dealer_bust(self, setup_simulation_stats):
        """
        Tests the dealer_bust method.

        """
        s = setup_simulation_stats

        s.dealer_bust(player_key='Player 1', count_key=0, amount=10, initial_amount=10)

        assert s.stats_dict['Player 1'][0]['dealer bust'] == 1
        assert s.stats_dict['Player 1'][0]['number of hands'] == 1
        assert s.stats_dict['Player 1'][0]['net winnings'] == 10
        assert s.stats_dict['Player 1'][0]['overall bet'] == 10
        assert s.stats_dict['Player 1'][0]['initial bet'] == 10

    def test_player_natural_blackjack(self, setup_simulation_stats):
        """
        Tests the player_natural_blackjack method.

        """
        s = setup_simulation_stats

        s.player_natural_blackjack(player_key='Player 1', count_key=0, amount=10, initial_amount=10)

        assert s.stats_dict['Player 1'][0]['player natural blackjack'] == 1
        assert s.stats_dict['Player 1'][0]['number of hands'] == 1
        assert s.stats_dict['Player 1'][0]['net winnings'] == 10 * r.blackjack_payout
        assert s.stats_dict['Player 1'][0]['overall bet'] == 10
        assert s.stats_dict['Player 1'][0]['initial bet'] == 10

    def test_dealer_natural_blackjack(self, setup_simulation_stats):
        """
        Tests the dealer_natural_blackjack method.

        """
        s = setup_simulation_stats

        s.dealer_natural_blackjack(player_key='Player 1', count_key=0, amount=10, initial_amount=10)

        assert s.stats_dict['Player 1'][0]['dealer natural blackjack'] == 1
        assert s.stats_dict['Player 1'][0]['number of hands'] == 1
        assert s.stats_dict['Player 1'][0]['net winnings'] == -10
        assert s.stats_dict['Player 1'][0]['overall bet'] == 10
        assert s.stats_dict['Player 1'][0]['initial bet'] == 10
