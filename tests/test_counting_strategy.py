import pytest
from counting_strategy import CountingStrategy
from cards import Cards
from house_rules import HouseRules


@pytest.fixture()
def setup_counting_strategy():
    r = HouseRules(
            shoe_size=4,
            bet_limits=[10, 500]
    )
    c = Cards(rules=r)
    c.burn_card()
    c.add_to_seen_cards(card=1)
    cs = CountingStrategy(rules=r, cards=c)
    return c, cs


class TestCountingStrategy(object):

    @pytest.mark.parametrize('strategy, expected',
                             [
                                 ('No Strategy', ValueError),
                                 ('Hi-Lo', -1),
                                 ('KO', -13)
                             ])
    def test_running_count(self, setup_counting_strategy, strategy, expected):
        """
        Tests the running_count method.

        """
        c, cs = setup_counting_strategy

        if type(expected) == type and issubclass(expected, Exception):
            with pytest.raises(ValueError):
                cs.running_count(strategy=strategy)

        else:
            assert cs.running_count(strategy=strategy) == expected

    @pytest.mark.parametrize('strategy, expected',
                             [
                                 ('Hi-Lo', -18),
                                 ('KO', ValueError),
                                 ('No Strategy', ValueError)
                             ])
    def test_true_count(self, setup_counting_strategy, strategy, expected):
        """
        Tests the true_count method.

        """
        c, cs = setup_counting_strategy

        if type(expected) == type and issubclass(expected, Exception):
            with pytest.raises(ValueError):
                cs.true_count(strategy=strategy)

        else:
            # one Ace was already taken out in the setup
            # 51 additional Ace equivalent cards are added to seen cards
            # exactly three decks remain
            for i in range(0, 51):
                c.burn_card()
                c.add_to_seen_cards(card=1)
            assert cs.true_count(strategy=strategy) == expected

