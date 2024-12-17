def test_hard_h17(setup_playing_strategy_h17):
    """
    Tests the hard method within the PlayingStrategy class
    when the dealer hits on a soft 17.
    """
    assert setup_playing_strategy_h17.hard(total=11, dealer_up_card='A') == 'Dh'


def test_soft_h17(setup_playing_strategy_h17):
    """
    Tests the soft method within the PlayingStrategy class
    when the dealer hits on a soft 17.
    """
    assert setup_playing_strategy_h17.soft(total=19, dealer_up_card='6') == 'Ds'


def test_pair_h17(setup_playing_strategy_h17):
    """
    Tests the pair method within the PlayingStrategy class
    when the dealer hits on a soft 17.
    """
    assert setup_playing_strategy_h17.pair(card='8', dealer_up_card='A') == 'Rp'


def test_hard_s17(setup_playing_strategy_s17):
    """
    Tests the hard method within the PlayingStrategy class
    when the dealer stands on a soft 17.
    """
    assert setup_playing_strategy_s17.hard(total=11, dealer_up_card='A') == 'H'


def test_soft_s17(setup_playing_strategy_s17):
    """
    Tests the soft method within the PlayingStrategy class
    when the dealer stands on a soft 17.
    """
    assert setup_playing_strategy_s17.soft(total=19, dealer_up_card='6') == 'S'


def test_pair_s17(setup_playing_strategy_s17):
    """
    Tests the pair method within the PlayingStrategy class
    when the dealer stands on a soft 17.
    """
    assert setup_playing_strategy_s17.pair(card='8', dealer_up_card='A') == 'P'
