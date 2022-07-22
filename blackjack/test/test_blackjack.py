#import pytest
#from blackjack.card_counter import CardCounter
#from blackjack.blackjack import Blackjack
#from blackjack.simulation_stats import StatsKey, StatsCategory
#from blackjack.shoe import Shoe, CountingStrategy
#from blackjack.house_rules import HouseRules
#from blackjack.table import Table
#from blackjack.player import Player
#from blackjack.dealer import Dealer
#from blackjack.hand import HandStatus
#
#
#@pytest.fixture
#def setup_shoe():
#    return Shoe(size=6)
#
#
#@pytest.fixture
#def setup_player():
#    return Player(
#        name='Player 1',
#        bankroll=1000,
#        min_bet=10
#    )
#
#
#@pytest.fixture
#def setup_card_counter_balanced():
#    return CardCounter(
#        name='Player 1',
#        bankroll=1000,
#        min_bet=10,
#        counting_strategy=CountingStrategy.HI_LO,
#        bet_ramp={
#            1: 15,
#            2: 20,
#            3: 40,
#            4: 50,
#            5: 70
#        },
#        insurance=None
#    )
#
#
#@pytest.fixture
#def setup_card_counter_unbalanced():
#    return CardCounter(
#        name='Player 1',
#        bankroll=1000,
#        min_bet=10,
#        counting_strategy=CountingStrategy.KO,
#        bet_ramp={
#            1: 15,
#            2: 20,
#            3: 40,
#            4: 50,
#            5: 70
#        },
#        insurance=None
#    )
#
#
#@pytest.fixture
#def setup_card_counter():
#    return CardCounter(
#        name='Player 2',
#        bankroll=1000,
#        min_bet=10,
#        counting_strategy=CountingStrategy.HI_LO,
#        bet_ramp={
#            1: 15,
#            2: 20,
#            3: 40,
#            4: 50,
#            5: 70
#        },
#        insurance=2
#    )
#
#
#@pytest.fixture
#def setup_rules():
#    return HouseRules(
#        shoe_size=6,
#        min_bet=10,
#        max_bet=500
#    )
#
#
#@pytest.fixture
#def setup_table(setup_rules, setup_player, setup_card_counter):
#    t = Table(rules=setup_rules)
#    t.add_player(player=setup_player)
#    t.add_player(player=setup_card_counter)
#    return t
#
#
#@pytest.fixture
#def setup_dealer():
#    return Dealer()
#
#
#@pytest.fixture
#def setup_blackjack(setup_table, setup_rules, setup_dealer):
#    return Blackjack(table=setup_table, rules=setup_rules, dealer=setup_dealer)
#
#
#def test_dealer_turn(setup_blackjack, setup_player):
#    """Tests the _dealer_turn method within the Blackjack class."""
#    setup_player.first_hand.status == HandStatus.SETTLED
#    assert not setup_blackjack._dealer_turn()
#    setup_player.first_hand.status == HandStatus.SHOWDOWN
#    assert not setup_blackjack._dealer_turn()
#
#
#
#
#@pytest.mark.parametrize(
#    'test_count, expected',
#    [
#         (-5, 10), # total < 17
#         (1, 15), # total == 17, soft
#         (6, 70) 
#     ]
#)
#def test_dealer_plays_hand(setup_dealer, setup_shoe, setup_blackjack):
#    """Tests the _dealer_plays_hand method within the Blackjack class."""
#    setup_blackjack._dealer_plays_hand()
#
#
#
##def test_get_count_balanced(setup_card_counter_balanced, setup_shoe):
##    """Tests the get_count function with a balanced card counting system."""
##    # burn an entire 52 card deck and make them all visible 'K'
##    # exactly 5 decks remain
##    for _ in range(0, 52):
##        setup_shoe.burn_card(seen=False)
##        setup_shoe.add_to_seen_cards(card='K')
##    assert get_count(player=setup_card_counter_balanced, shoe=setup_shoe) == -10
##
##
##def test_get_count_unbalanced(setup_card_counter_unbalanced, setup_shoe):
##    """Tests the get_count function with an unbalanced card counting system."""
##    assert get_count(player=setup_card_counter_unbalanced, shoe=setup_shoe) == -20
##    setup_shoe.add_to_seen_cards(card='K')
##    setup_shoe.add_to_seen_cards(card='K')
##    setup_shoe.add_to_seen_cards(card='K')
##    setup_shoe.add_to_seen_cards(card='2')
##    assert get_count(player=setup_card_counter_unbalanced, shoe=setup_shoe) == -22
##    
##
##def test_can_place_wager(setup_player):
##    """Tests the can_place_initial_wager function."""
##    assert not can_place_wager(player=setup_player, wager=1001)
##    assert can_place_wager(player=setup_player, wager=1000)
##    
##
##def test_place_initial_wager(setup_player):
##    """Tests the place_initial_wager function."""
##    place_initial_wager(player=setup_player, initial_wager=50, count=2)
##    assert setup_player.hands[0].total_bet == 50
##    assert setup_player.bankroll == 950
##    assert setup_player.stats.stats[StatsKey(count=2, category=StatsCategory.AMOUNT_WAGERED)] == 50
##
##
##def test_initialize_hands(setup_rules, setup_player, setup_dealer, setup_shoe):
##    """Tests the initialize_hands function."""
##    t = Table(rules=setup_rules)
##    t.add_player(player=setup_player)
##    initialize_hands(table=t, dealer=setup_dealer, shoe=setup_shoe)
##    assert setup_player.hands[0].cards == ['A', 'Q']
##    assert setup_dealer.hand.cards == ['K', 'J']
##    assert setup_shoe.seen_cards['A'] == 1
##    assert setup_shoe.seen_cards['10-J-Q-K'] == 2
##
##
##def test_place_insurance_wager(setup_card_counter_insurance):
##    """Tests the place_insurance_wager function."""
##    place_insurance_wager(player=setup_card_counter_insurance, insurance_wager=25, insurance_count=2)
##    assert setup_card_counter_insurance.hands[0].side_bet == 25
##    assert setup_card_counter_insurance.bankroll == 975
##    assert setup_card_counter_insurance.stats.stats[StatsKey(count=2, category=StatsCategory.AMOUNT_WAGERED)] == 25
##
##
##def test_update_insurance_stats_dealer_blackjack(setup_dealer, setup_card_counter_insurance):
##    """
##    Tests the update_insurance_stats function when the dealer
##    has a blackjack.
##    """
##    setup_dealer.hand.add_card('K')
##    setup_dealer.hand.add_card('A')
##    update_insurance_stats(dealer=setup_dealer, player=setup_card_counter_insurance, insurance_wager=25, insurance_count=2)
##    assert setup_card_counter_insurance.bankroll == 1050
##    assert setup_card_counter_insurance.stats.stats[StatsKey(count=2, category=StatsCategory.AMOUNT_EARNED)] == 25
##
##
##def test_update_insurance_stats_no_dealer_blackjack(setup_dealer, setup_card_counter_insurance):
##    """
##    Tests the update_insurance_stats function when the dealer
##    does not have a blackjack.
##    """
##    setup_dealer.hand.add_card('7')
##    setup_dealer.hand.add_card('A')
##    update_insurance_stats(dealer=setup_dealer, player=setup_card_counter_insurance, insurance_wager=25, insurance_count=2)
##    assert setup_card_counter_insurance.bankroll == 1000
##    assert setup_card_counter_insurance.stats.stats[StatsKey(count=2, category=StatsCategory.AMOUNT_EARNED)] == -25
##
##
##def test_update_blackjack_stats_player_blackjack(setup_dealer, setup_player):
##    """
##    Tests the update_blackjack_stats function
##    when the player has blackjack.
##    """
##    setup_player.hands[0].add_card('A')
##    setup_player.hands[0].add_card('K')
##    update_blackjack_stats(dealer=setup_dealer, player=setup_player, initial_wager=20, blackjack_payout=1.5, count=2)
##    assert setup_player.bankroll == 1050
##    assert setup_player.stats.stats[StatsKey(count=2, category=StatsCategory.HANDS_WON)] == 1
##    assert setup_player.stats.stats[StatsKey(count=2, category=StatsCategory.AMOUNT_EARNED)] == 30
##
##    
##def test_update_blackjack_stats_dealer_blackjack(setup_dealer, setup_player):
##    """
##    Tests the update_blackjack_stats function when the
##    dealer has blackjack.
##    """
##    setup_dealer.hand.add_card('A')
##    setup_dealer.hand.add_card('K')
##    update_blackjack_stats(dealer=setup_dealer, player=setup_player, initial_wager=20, blackjack_payout=1.5, count=2)
##    assert setup_player.bankroll == 1000
##    assert setup_player.stats.stats[StatsKey(count=2, category=StatsCategory.HANDS_LOST)] == 1
##    assert setup_player.stats.stats[StatsKey(count=2, category=StatsCategory.AMOUNT_EARNED)] == -20
##
##
##def test_update_blackjack_stats_player_dealer_blackjack(setup_dealer, setup_player):
##    """
##    Tests the update_blackjack_stats function when
##    both the player and dealer have blackjack.
##    """
##    setup_dealer.hand.add_card('A')
##    setup_dealer.hand.add_card('K')
##    setup_player.hands[0].add_card('A')
##    setup_player.hands[0].add_card('K')
##    update_blackjack_stats(dealer=setup_dealer, player=setup_player, initial_wager=20, blackjack_payout=1.5, count=2)
##    assert setup_player.bankroll == 1020
##    assert setup_player.stats.stats[StatsKey(count=2, category=StatsCategory.HANDS_PUSHED)] == 1
##
##
##def test_update_late_surrender_stats(setup_player):
##    """Tests the update_late_surrender_stats function."""
##    update_late_surrender_stats(player=setup_player, initial_wager=50, count=2)
##    assert setup_player.bankroll == 1025
##    assert setup_player.stats.stats[StatsKey(count=2, category=StatsCategory.HANDS_LOST)] == 1
##    assert setup_player.stats.stats[StatsKey(count=2, category=StatsCategory.AMOUNT_EARNED)] == -25
##
##
##def test_update_increase_wager_stats(setup_player):
##    """Tests the update_increase_wager_stats function."""
##    update_increase_wager_stats(player=setup_player, hand_wager=10, count=2)
##    assert setup_player.bankroll == 990
##    assert setup_player.stats.stats[StatsKey(count=2, category=StatsCategory.AMOUNT_WAGERED)] == 10
##
##
##def test_update_win_stats(setup_player):
##    """Tests the update_win_stats function."""
##    update_win_stats(player=setup_player, hand_wager=10, count=2)
##    assert setup_player.bankroll == 1020
##    assert setup_player.stats.stats[StatsKey(count=2, category=StatsCategory.HANDS_WON)] == 1
##    assert setup_player.stats.stats[StatsKey(count=2, category=StatsCategory.AMOUNT_EARNED)] == 10
##    
##
##def test_update_push_stats(setup_player):
##    """Tests the update_push_stats function."""
##    update_push_stats(player=setup_player, hand_wager=10, count=2)
##    assert setup_player.bankroll == 1010
##    assert setup_player.stats.stats[StatsKey(count=2, category=StatsCategory.HANDS_PUSHED)] == 1
##
##
##def test_update_loss_stats(setup_player):
##    """Tests the update_loss_stats function."""
##    update_loss_stats(player=setup_player, hand_wager=10, count=2)
##    assert setup_player.bankroll == 1000
##    assert setup_player.stats.stats[StatsKey(count=2, category=StatsCategory.HANDS_LOST)] == 1
##    assert setup_player.stats.stats[StatsKey(count=2, category=StatsCategory.AMOUNT_EARNED)] == -10
#    
#    
#
#    