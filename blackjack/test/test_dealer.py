def test_hole_card(setup_dealer_with_hand):
    """Tests the hole_card method within the Dealer class."""
    assert setup_dealer_with_hand.hole_card() == '8'


def test_up_card(setup_dealer_with_hand):
    """Tests the up_card method within the Dealer class."""
    assert setup_dealer_with_hand.up_card() == '6'


def test_deal_card(setup_dealer_with_hand, setup_shoe):
    """Tests the deal_card method within the Dealer class."""
    assert setup_dealer_with_hand.deal_card(shoe=setup_shoe, seen=True) == 'A'
    assert setup_shoe.seen_cards['A'] == 1
    assert setup_dealer_with_hand.deal_card(shoe=setup_shoe, seen=False) == 'K'
    assert setup_shoe.seen_cards['10-J-Q-K'] == 0


def test_reset_hand(setup_dealer_with_hand):
    """Tests the reset_hand method within the Dealer class."""
    assert setup_dealer_with_hand.hand.cards == ['8', '6']
    setup_dealer_with_hand.reset_hand()
    assert setup_dealer_with_hand.hand.cards == []
