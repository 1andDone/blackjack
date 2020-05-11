import random
import pytest
from cards import Cards


@pytest.fixture(autouse=True)
def setup_cards():
    return [Cards(shoe_size=4), Cards(shoe_size=6), Cards(shoe_size=8)]


class TestCards(object):

    @pytest.mark.parametrize('shoe_size, expected',
                             [
                                 (4, 4),
                                 (6, 6),
                                 (8, 8),
                                 (10, ValueError)
                             ])
    def test_shoe_size(self, shoe_size, expected):
        """
        Tests the shoe_size parameter of the __init__ method.

        """
        if type(expected) == type and issubclass(expected, Exception):
            with pytest.raises(ValueError):
                Cards(shoe_size=shoe_size)

        else:
            c = Cards(shoe_size=shoe_size)
            assert c.shoe_size == expected

    def test_burn_card(self, setup_cards):
        """
        Tests the burn_card method.

        """
        for c in setup_cards:
            assert c.burn_card() == 'A'
            assert c.burn_card() == 'K'

    def test_shuffle(self, setup_cards):
        """
        Tests the shuffle method.

        """
        random.seed(1)
        for c in setup_cards:
            assert c.deck[-1] == 'A'
            assert c.deck[-2] == 'K'
            c.shuffle()
            assert c.deck[-1] != 'A'
            assert c.deck[-2] != 'K'

    @pytest.mark.parametrize('visible, expected',
                             [
                                 (False, []),
                                 (True, ['A'])
                             ])
    def test_deal_card(self, setup_cards, visible, expected):
        """
        Tests the deal_card method.

        """
        for c in setup_cards:
            deck_before_dealing = c.deck.copy()
            c.deal_card(visible=visible)
            assert c.visible_cards == expected
            assert len(c.deck) == len(deck_before_dealing) - 1

    def test_update_visible_cards(self, setup_cards):
        """
        Tests the update_visible_cards method.

        """
        for c in setup_cards:
            assert c.visible_cards == []
            c.update_visible_cards(card='2')
            assert c.visible_cards == ['2']

    def test_remaining_decks(self, setup_cards):
        """
        Tests the remaining_decks method.

        """
        for c in setup_cards:
            c.burn_card()
            assert c.remaining_decks() == ((c.shoe_size * 52) - 1) / 52

    @pytest.mark.parametrize('penetration, expected',
                             [
                                 (0.25, ValueError),
                                 (0.5, True),
                                 (0.75, True),
                                 (1, ValueError)
                             ])
    def test_cut_card_reached(self, setup_cards, penetration, expected):
        """
        Tests the cut_card_reached method.

        """
        for c in setup_cards:
            if penetration < 0.5 or penetration > 0.9:
                with pytest.raises(ValueError):
                    c.cut_card_reached(penetration=penetration)
            else:
                # burn within 1 card of reaching desired penetration
                for i in range(0, int(c.shoe_size * penetration * 52) - 1):
                    c.burn_card()
                assert c.cut_card_reached(penetration=penetration) is not expected

                # burn enough cards to reach desired penetration
                c.burn_card()
                assert c.cut_card_reached(penetration=penetration) is expected
