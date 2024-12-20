import random
import pytest
from blackjack.enums import CountingStrategy
from blackjack.shoe import Shoe


@pytest.mark.parametrize(
    'test_shoe_size',
    [
         (-1),
         (0),
         (9)
     ]
)
def test_init_invalid_shoe_size(test_shoe_size):
    """
    Tests the __init__ method within the Shoe class
    when an invalid shoe size is provided.

    """
    with pytest.raises(ValueError) as e:
        Shoe(shoe_size=test_shoe_size)
    assert str(e.value) == 'Shoe size must be between 1 and 8 decks.'


def test_burn_card_not_seen(setup_shoe):
    """
    Tests the burn_card method within the Shoe class when the
    burn card is not seen.

    """
    assert len(setup_shoe._cards) == 52
    burn_card = setup_shoe._cards[-1]
    setup_shoe.burn_card(seen=False)
    assert len(setup_shoe._cards) == 51
    assert setup_shoe.seen_cards[burn_card] == 0


def test_burn_card_seen(setup_shoe):
    """
    Tests the burn_card method within the Shoe class
    when the burn card is seen.

    """
    assert len(setup_shoe._cards) == 52
    burn_card = setup_shoe._cards[-1]
    setup_shoe.burn_card(seen=True)
    assert len(setup_shoe._cards) == 51
    assert setup_shoe.seen_cards[burn_card] == 1


def test_shuffle(setup_shoe):
    """Tests the shuffle method within the Shoe class."""
    before_shuffle = setup_shoe._cards.copy()
    assert len(before_shuffle) == 52
    random.seed(1)
    setup_shoe.shuffle()
    after_shuffle = setup_shoe._cards
    assert len(after_shuffle) == 51
    assert before_shuffle[0] != after_shuffle[0]


def test_add_to_seen_cards(setup_shoe):
    """Tests the add_to_seen_cards method within the Shoe class."""
    assert setup_shoe.seen_cards['10-J-Q-K'] == 0
    setup_shoe.add_to_seen_cards(card='K')
    assert setup_shoe.seen_cards['10-J-Q-K'] == 1
    assert setup_shoe.seen_cards['2'] == 0
    setup_shoe.add_to_seen_cards(card='2')
    assert setup_shoe.seen_cards['2'] == 1


def test_remaining_decks(setup_shoe):
    """Tests the remaining_decks method within the Shoe class."""
    assert setup_shoe.remaining_decks == 1
    # burn half a deck
    for _ in range(0, 26):
        setup_shoe.burn_card(seen=False)
    assert setup_shoe.remaining_decks == 0.5
    # burn a quarter of a deck
    for _ in range(0, 13):
        setup_shoe.burn_card(seen=False)
    assert setup_shoe.remaining_decks == 0.25


def test_cut_card_reached(setup_shoe):
    """Tests the cut_card_reached method within the Shoe class."""
    # burn one card away from half the shoe
    for _ in range(0, 25):
        setup_shoe.burn_card(seen=False)

    assert 1 - (len(setup_shoe._cards) / 52) < 0.5
    assert not setup_shoe.cut_card_reached(penetration=0.5)
    setup_shoe.burn_card(seen=False)
    assert 1 - (len(setup_shoe._cards) / 52) >= 0.5
    assert setup_shoe.cut_card_reached(penetration=0.5)


def test_running_count():
    """Tests the running_count method within the Shoe class."""
    shoe = Shoe(shoe_size=6)
    assert shoe.running_count(strategy=CountingStrategy.HI_LO) == 0
    assert shoe.running_count(strategy=CountingStrategy.KO) == -20
    shoe.add_to_seen_cards(card='K')
    shoe.add_to_seen_cards(card='K')
    shoe.add_to_seen_cards(card='K')
    shoe.add_to_seen_cards(card='2')
    assert shoe.running_count(strategy=CountingStrategy.HI_LO) == -2
    assert shoe.running_count(strategy=CountingStrategy.KO) == -22


def test_true_count():
    """Tests the true_count method within the Shoe class."""
    shoe = Shoe(shoe_size=6)
    # burn an entire 52 card deck and make them all visible 'K'
    # exactly 5 decks remain
    for _ in range(0, 52):
        shoe.burn_card(seen=False)
        shoe.add_to_seen_cards(card='K')
    assert shoe.true_count(strategy=CountingStrategy.HI_LO) == -10
    assert shoe.true_count(strategy=CountingStrategy.HI_OPT_II) == -21


def test_true_count_unbalanced_counting_system(setup_shoe):
    """
    Tests the true_count method within the Shoe class
    when an unbalanced counting system is used.

    """
    with pytest.raises(ValueError) as e:
        setup_shoe.true_count(strategy=CountingStrategy.KO)
    assert str(e.value) == '"true_count" is only applicable for balanced counting systems.'
