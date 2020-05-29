import random
import pytest
import numpy as np
from cards import Cards
from house_rules import HouseRules


@pytest.fixture(autouse=True)
def setup_cards():
    cards_list = []
    for shoe_size in [4, 6, 8]:
        r = HouseRules(
                shoe_size=shoe_size,
                bet_limits=[10, 500]
        )
        cards_list.append(Cards(rules=r))

    return cards_list


class TestCards(object):

    def test_add_to_seen_cards(self, setup_cards):
        """
        Tests the add_to_seen_cards method.

        """
        for c in setup_cards:
            assert c.seen_cards[0] == 0
            assert c.seen_cards[12] == 0
            c.add_to_seen_cards(card=1)
            c.add_to_seen_cards(card=13)
            assert c.seen_cards[0] == 1
            assert c.seen_cards[12] == 1

    def test_burn_card(self, setup_cards):
        """
        Tests the burn_card method.

        """
        for c in setup_cards:
            assert c.burn_card() == 1
            assert c.burn_card() == 13

    def test_shuffle(self, setup_cards):
        """
        Tests the shuffle method.

        """
        random.seed(1)
        for c in setup_cards:
            assert c.cards[-1] == 1
            assert c.cards[-2] == 13
            c.shuffle()
            assert c.cards[-1] != 1
            assert c.cards[-2] != 13

    @pytest.mark.parametrize('seen, expected',
                             [
                                 (False, 0),
                                 (True, 1)
                             ])
    def test_deal_card(self, setup_cards, seen, expected):
        """
        Tests the deal_card method.

        """
        for c in setup_cards:
            cards_before_dealing = c.cards.copy()
            c.deal_card(seen=seen)
            assert c.seen_cards[0] == expected
            assert len(c.cards) == len(cards_before_dealing) - 1

    def test_remaining_decks(self):
        """
        Tests the remaining_decks method.

        """
        for shoe_size in [4, 6, 8]:
            r = HouseRules(
                shoe_size=shoe_size,
                bet_limits=[10, 500]
            )
            c = Cards(rules=r)
            # burn within 1 card of changing remaining decks amount (rounded to the nearest integer)
            for i in range(0, 26):  # half a deck of cards
                c.burn_card()
                assert c.remaining_decks() == r.shoe_size
            c.burn_card()
            assert c.remaining_decks() == r.shoe_size - 1

    @pytest.mark.parametrize('penetration, expected',
                             [
                                 (0.25, ValueError),
                                 (0.5, True),
                                 (0.75, True),
                                 (1, ValueError)
                             ])
    def test_cut_card_reached(self, penetration, expected):
        """
        Tests the cut_card_reached method.

        """
        for shoe_size in [4, 6, 8]:
            r = HouseRules(
                shoe_size=shoe_size,
                bet_limits=[10, 500]
            )
            c = Cards(rules=r)
            if penetration < 0.5 or penetration > 0.9:
                with pytest.raises(ValueError):
                    c.cut_card_reached(penetration=penetration)
            else:
                # burn within 1 card of reaching desired penetration
                for i in range(0, int(r.shoe_size * penetration * 52) - 1):
                    c.burn_card()
                assert c.cut_card_reached(penetration=penetration) is not expected

                # burn enough cards to reach desired penetration
                c.burn_card()
                assert c.cut_card_reached(penetration=penetration) is expected
