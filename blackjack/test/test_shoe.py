import random
import pytest
from blackjack import CountingStrategy


def test_burn_card_not_seen(setup_shoe):
    """
    Tests the burn_card method within the Shoe class when the
    burn card is not seen.
    """
    assert len(setup_shoe._cards) == 312
    burn_card = setup_shoe._cards[-1]
    setup_shoe.burn_card(seen=False)
    assert len(setup_shoe._cards) == 311
    assert setup_shoe.seen_cards[burn_card] == 0


def test_burn_card_seen(setup_shoe):
    """
    Tests the burn_card method within the Shoe class
    when the burn card is seen.
    """
    assert len(setup_shoe._cards) == 312
    burn_card = setup_shoe._cards[-1]
    setup_shoe.burn_card(seen=True)
    assert len(setup_shoe._cards) == 311
    assert setup_shoe.seen_cards[burn_card] == 1
    

def test_shuffle(setup_shoe):
    """Tests the shuffle method within the Shoe class."""
    before_shuffle = setup_shoe._cards.copy()
    assert len(before_shuffle) == 312
    random.seed(1)
    setup_shoe.shuffle()
    after_shuffle = setup_shoe._cards
    assert len(after_shuffle) == 311
    assert before_shuffle[0] != after_shuffle[0]
    

def test_add_to_seen_cards(setup_shoe):
    """Tests the add_to_seen_cards method within the Shoe class."""
    assert setup_shoe.seen_cards['10-J-Q-K'] == 0
    assert setup_shoe.seen_cards['2'] == 0
    setup_shoe.add_to_seen_cards(card='K')
    setup_shoe.add_to_seen_cards(card='2')
    assert setup_shoe.seen_cards['10-J-Q-K'] == 1
    assert setup_shoe.seen_cards['2'] == 1


def test_remaining_decks(setup_shoe):
    """Tests the remaining_decks method within the Shoe class."""
    assert setup_shoe.remaining_decks() == 6
    # burn half a deck
    for i in range(0, 26):
        setup_shoe.burn_card(seen=False)
    
    assert setup_shoe.remaining_decks() == 6
    setup_shoe.burn_card(seen=False)
    assert setup_shoe.remaining_decks() == 5


def test_cut_card_reached(setup_shoe):
    """Tests the cut_card_reached method within the Shoe class."""
    # burn one card away from half the shoe
    for i in range(0, 155):
        setup_shoe.burn_card(seen=False)
        
    assert 1 - (len(setup_shoe._cards)/312) < 0.5
    assert not setup_shoe.cut_card_reached(penetration=0.5)
    setup_shoe.burn_card(seen=False)
    assert 1 - (len(setup_shoe._cards)/312) >= 0.5
    assert setup_shoe.cut_card_reached(penetration=0.5)


def test_running_count(setup_shoe):
    """Tests the running_count method within the Shoe class."""
    assert setup_shoe.running_count(strategy=CountingStrategy.HI_LO) == 0
    assert setup_shoe.running_count(strategy=CountingStrategy.KO) == -20
    setup_shoe.add_to_seen_cards(card='K')
    setup_shoe.add_to_seen_cards(card='K')
    setup_shoe.add_to_seen_cards(card='K')
    setup_shoe.add_to_seen_cards(card='2')
    assert setup_shoe.running_count(strategy=CountingStrategy.HI_LO) == -2
    assert setup_shoe.running_count(strategy=CountingStrategy.KO) == -22


def test_true_count(setup_shoe):
    """Tests the true_count method within the Shoe class."""
    # burn an entire 52 card deck and make them all visible 'K'
    # exactly 5 decks remain
    for _ in range(0, 52):
        setup_shoe.burn_card(seen=False)
        setup_shoe.add_to_seen_cards(card='K')
    assert setup_shoe.true_count(strategy=CountingStrategy.HI_LO) == -10
    assert setup_shoe.true_count(strategy=CountingStrategy.HI_OPT_II) == -21
    

def test_true_count_unbalanced_counting_system(setup_shoe):
    """
    Tests the true_count method within the Shoe class
    when an unbalanced counting system is used.
    """
    with pytest.raises(ValueError):
        setup_shoe.true_count(strategy=CountingStrategy.KO)