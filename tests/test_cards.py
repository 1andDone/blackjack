import random
import pytest
from cards import Cards


class TestCards(object):

    def test_init_no_shoe_size(self):
        with pytest.raises(Exception):
            Cards()

    def test_init_incorrect_shoe_size(self):
        with pytest.raises(ValueError):
            Cards(shoe_size=17)

    def test_init_correct_shoe_size(self):
        for shoe_size in [4, 6, 8]:
            c = Cards(shoe_size=shoe_size)
            assert c.shoe_size == shoe_size
            assert len(c.deck) == shoe_size * 52
            assert c.visible_cards == []

    def test_burn_card(self):
        c = Cards(shoe_size=4)
        assert c.burn_card() == 'A'
        assert c.burn_card() == 'K'
        assert c.burn_card() == 'Q'

    def test_shuffle(self):
        random.seed(1)
        c = Cards(shoe_size=4)
        assert c.deck[-1] == 'A'
        assert c.deck[-2] == 'K'
        deck_before_shuffle = c.deck.copy()
        c.shuffle()
        assert c.deck[-1] == '4'
        assert len(c.deck) == len(deck_before_shuffle) - 1

    def test_deal_card_visible(self):
        c = Cards(shoe_size=4)
        deck_before_dealing = c.deck.copy()
        c.deal_card(visible=True)
        assert c.visible_cards == ['A']
        assert len(c.deck) == len(deck_before_dealing) - 1

    def test_deal_card_not_visible(self):
        c = Cards(shoe_size=4)
        deck_before_dealing = c.deck.copy()
        c.deal_card(visible=False)
        assert c.visible_cards == []
        assert len(c.deck) == len(deck_before_dealing) - 1

    def test_update_visible_cards(self):
        c = Cards(shoe_size=4)
        assert c.visible_cards == []
        c.update_visible_cards(card='2')
        assert c.visible_cards == ['2']

    def test_remaining_decks(self):
        for shoe_size in [4, 6, 8]:
            c = Cards(shoe_size=shoe_size)
            assert c.remaining_decks() == shoe_size
            c.shuffle()
            assert c.remaining_decks() == ((shoe_size * 52) - 1)/52

    def test_cut_card_reached(self):
        for penetration in [0.25, 0.5, 0.75, 1]:
            c = Cards(shoe_size=4)

            if penetration < 0.5 or penetration > 0.9:
                with pytest.raises(ValueError):
                    c.cut_card_reached(penetration=penetration)
            else:
                assert c.cut_card_reached(penetration=penetration) is False

                # burn half of the deck - 1 cards
                for i in range(0, int(penetration * 4 * 52) - 1):
                    c.burn_card()
                assert c.cut_card_reached(penetration=penetration) is False

                # burn half of the deck
                c.burn_card()
                assert c.cut_card_reached(penetration=penetration) is True
