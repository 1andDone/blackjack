import pytest
from counting_strategy import CountingStrategy
from cards import Cards


@pytest.fixture()
def setup_counting_strategy():
    c = Cards(shoe_size=4)
    c.burn_card()
    c.update_visible_cards(card='A')
    cs = CountingStrategy(cards=c)
    return c, cs


class TestCountingStrategy(object):

    def test_update_running_count(self, setup_counting_strategy):
        """
        Tests the update_running_count method.

        """
        c, cs = setup_counting_strategy
        cs.update_running_count()
        assert cs.running_count_dict == {
                'Halves': -1,
                'Hi-Lo': -1,
                'Hi-Opt I': 0,
                'Hi-Opt II': 0,
                'Omega II': 0,
                'Zen Count': -1
            }

    @pytest.mark.parametrize('strategy, expected',
                             [
                                 ('No Strategy', ValueError),
                                 ('Hi-Lo', -1)
                             ])
    def test_running_count(self, setup_counting_strategy, strategy, expected):
        """
        Tests the running_count method.

        """
        c, cs = setup_counting_strategy
        cs.update_running_count()

        if type(expected) == type and issubclass(expected, Exception):
            with pytest.raises(ValueError):
                cs.running_count(strategy=strategy)

        else:
            assert cs.running_count(strategy=strategy) == expected

    @pytest.mark.parametrize('strategy, accuracy, expected',
                             [
                                 ('Hi-Lo', 0.1, -17.3),
                                 ('Hi-Lo', 0.5, -17.5),
                                 ('Hi-Lo', 1, -17),
                                 ('Hi-Lo', 0.3, ValueError),
                                 ('No Strategy', 1, ValueError)
                             ])
    def test_true_count(self, setup_counting_strategy, strategy, accuracy, expected):
        """
        Tests the true_count method.

        """
        c, cs = setup_counting_strategy
        cs.update_running_count()
        c.set_visible_cards()

        if type(expected) == type and issubclass(expected, Exception):
            with pytest.raises(ValueError):
                cs.true_count(strategy=strategy, accuracy=accuracy)

        else:
            # one Ace was already taken out in the setup
            # 51 additional Ace equivalent cards are added to visible cards
            # exactly three decks remain
            for i in range(0, 51):
                c.burn_card()
                c.update_visible_cards(card='A')

            cs.update_running_count()
            assert cs.true_count(strategy=strategy, accuracy=accuracy) == expected

