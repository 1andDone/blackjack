import pytest
from simulation_stats import SimulationStats


class TestSimulationStats(object):

    def test_create_count_key(self):
        """
        Tests the create_count_key method.

        """
        s = SimulationStats()

        # new count key added
        s.create_count_key(count_key=0)
        assert s.results_dict == {0: {
            'net winnings': 0,
            'number of rounds': 0,
            'number of split hands': 0,
            'overall bet': 0
        }}

        # count key already exists
        s.create_count_key(count_key=0)
        assert s.results_dict == {0: {
            'net winnings': 0,
            'number of rounds': 0,
            'number of split hands': 0,
            'overall bet': 0
        }}

    @pytest.mark.parametrize('count_key, hand_key, net_winnings, overall_bet, increment, expected',
                             [
                                 (0, 1, 1.5, 1, 1,
                                  {0:
                                     {
                                         'net winnings': 1.5,
                                         'number of rounds': 1,
                                         'number of split hands': 0,
                                         'overall bet': 1,
                                     }
                                 }),
                                 (0, 2, -2, -2, 1,
                                  {0:
                                     {
                                         'net winnings': -2,
                                         'number of rounds': 0,
                                         'number of split hands': 1,
                                         'overall bet': -2,
                                     }
                                 })
                             ])
    def test_update_results(self, count_key, hand_key, net_winnings, overall_bet, increment, expected):
        """
        Tests the update_results method.

        """
        s = SimulationStats()
        s.create_count_key(count_key=0)
        s.update_results(
            count_key=count_key,
            hand_key=hand_key,
            net_winnings=net_winnings,
            overall_bet=overall_bet,
            increment=increment,
        )

        assert s.results_dict == expected
