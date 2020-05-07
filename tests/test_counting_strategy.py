import pytest

from counting_strategy import CountingStrategy
from cards import Cards


class TestCountingStrategy(object):

    def test_init_no_cards(self):
        with pytest.raises(Exception):
            CountingStrategy()

    def test_init_incorrect_cards(self):
        with pytest.raises(ValueError):
            CountingStrategy(cards='Incorrect argument')

    def test_init_correct_cards(self):
        c = Cards(shoe_size=4)
        cs = CountingStrategy(cards=c)
        running_count_dict = {
            'Halves': 0,
            'Hi-Lo': 0,
            'Hi-Opt I': 0,
            'Hi-Opt II': 0,
            'Omega II': 0,
            'Zen Count': 0
        }
        assert cs.running_count_dict == running_count_dict

    def test_update_running_count(self):
        c = Cards(shoe_size=4)
        cs = CountingStrategy(cards=c)
        c.update_visible_cards(card='A')
        cs.update_running_count()
        running_count_dict = {
            'Halves': -1,
            'Hi-Lo': -1,
            'Hi-Opt I': 0,
            'Hi-Opt II': 0,
            'Omega II': 0,
            'Zen Count': -1
        }
        assert cs.running_count_dict == running_count_dict

    def test_running_count_incorrect_strategy(self):
        c = Cards(shoe_size=4)
        cs = CountingStrategy(cards=c)
        c.update_visible_cards(card='A')
        cs.update_running_count()
        with pytest.raises(ValueError):
            cs.running_count(strategy='Incorrect argument')

    def test_running_count(self):
        c = Cards(shoe_size=4)
        cs = CountingStrategy(cards=c)
        c.update_visible_cards(card='A')
        cs.update_running_count()
        assert cs.running_count(strategy='Hi-Lo') == -1
        assert cs.running_count(strategy='Omega II') == 0

    def test_true_count_incorrect_strategy(self):
        c = Cards(shoe_size=4)
        cs = CountingStrategy(cards=c)
        c.update_visible_cards(card='A')
        cs.update_running_count()
        with pytest.raises(ValueError):
            cs.true_count(strategy='Incorrect argument')

    def test_true_count_incorrect_accuracy(self):
        c = Cards(shoe_size=4)
        cs = CountingStrategy(cards=c)
        c.update_visible_cards(card='A')
        cs.update_running_count()
        with pytest.raises(ValueError):
            cs.true_count(strategy='Hi-Lo', accuracy=0.3)

    def test_true_count(self):
        c = Cards(shoe_size=4)
        cs = CountingStrategy(cards=c)

        # equivalent to adding 52 (one deck) Ace equivalent cards to visible cards
        # exactly three decks remaining
        for i in range(0, 52):
            c.burn_card()
            c.update_visible_cards(card='A')

        cs.update_running_count()
        assert cs.true_count(strategy='Hi-Lo', accuracy=0.1) == -17.3
        assert cs.true_count(strategy='Hi-Lo', accuracy=0.5) == -17.5
        assert cs.true_count(strategy='Hi-Lo', accuracy=1) == -17
