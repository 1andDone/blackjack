import pytest
from blackjack import Player
from blackjack.hand import HandStatus
from blackjack.house_rules import HouseRules
from blackjack.shoe import Shoe
from blackjack.simulation_stats import StatsKey, StatsCategory
from blackjack.table import Table
from blackjack.helpers import get_initial_count, get_insurance_count
from blackjack.helpers import get_initial_wager, place_initial_wager
from blackjack.helpers import place_insurance_wager, initialize_hands 
from blackjack.helpers import add_back_counters, remove_back_counters
from blackjack.helpers import player_initial_decision, player_plays_hands
from blackjack.helpers import dealer_turn, all_hands_busted
from blackjack.helpers import dealer_plays_hand, compare_hands
from blackjack.helpers import clear_hands, play_round


def test_get_initial_count(setup_table, setup_player, setup_card_counter, setup_back_counter):
    """Tests the get_initial_count function."""
    shoe = Shoe(shoe_size=6)
    # burn an entire 52 card deck and make them all visible 'K'
    # exactly 5 decks remain
    for _ in range(0, 52):
        shoe.burn_card(seen=False)
        shoe.add_to_seen_cards(card='K')
    setup_table.add_player(player=setup_player)
    setup_table.add_player(player=setup_card_counter)
    setup_table.add_player(player=setup_back_counter)
    initial_count = get_initial_count(table=setup_table, shoe=shoe)
    assert initial_count[setup_player] == None
    assert initial_count[setup_card_counter] == -10
    assert initial_count[setup_back_counter] == -10


def test_get_insurance_count(setup_shoe, setup_table, setup_player, setup_card_counter, setup_card_counter_unbalanced, setup_back_counter):
    """Tests the get_insurance_count function."""
    setup_shoe.add_to_seen_cards(card='K')
    setup_shoe.add_to_seen_cards(card='K')
    setup_shoe.add_to_seen_cards(card='K')
    setup_shoe.add_to_seen_cards(card='2')
    setup_table.add_player(player=setup_player)
    setup_table.add_player(player=setup_card_counter)
    setup_table.add_player(player=setup_card_counter_unbalanced)
    setup_table.add_player(player=setup_back_counter)
    insurance_count = get_insurance_count(table=setup_table, shoe=setup_shoe)
    assert insurance_count[setup_player] == None
    assert insurance_count[setup_card_counter] == None
    assert insurance_count[setup_card_counter_unbalanced] == -2
    assert setup_back_counter not in insurance_count


def test_get_initial_wager_player_not_removed(setup_table, setup_shoe, setup_player):
    """
    Tests the get_initial_wager function when a player
    is not removed.
    """
    setup_table.add_player(player=setup_player)
    count_dict = get_initial_count(table=setup_table, shoe=setup_shoe)
    initial_wager_dict = get_initial_wager(table=setup_table, count_dict=count_dict)
    assert initial_wager_dict[setup_player] == setup_player.initial_wager()
    
    
def test_get_initial_wager_player_removed(setup_table, setup_shoe):
    """
    Tests the get_initial_wager function when a player
    is removed.
    """
    player = Player(name='Player 1', min_bet=10, bankroll=10)
    setup_table.add_player(player=player)
    player.edit_bankroll(amount=-10)
    count_dict = get_initial_count(table=setup_table, shoe=setup_shoe)
    initial_wager_dict = get_initial_wager(table=setup_table, count_dict=count_dict)
    assert player not in initial_wager_dict
    

def test_place_initial_wager(setup_player):
    """Tests the place_initial_wager function."""
    place_initial_wager(player=setup_player, initial_wager=50, count=2)
    assert setup_player.first_hand.total_bet == 50
    assert setup_player.bankroll == 950
    assert setup_player.stats.stats[StatsKey(count=2, category=StatsCategory.AMOUNT_WAGERED)] == 50


def test_place_insurance_wager(setup_card_counter_unbalanced):
    """Tests the place_insurance_wager function."""
    place_insurance_wager(player=setup_card_counter_unbalanced, insurance_wager=25, insurance_count=2)
    assert setup_card_counter_unbalanced.first_hand.side_bet == 25
    assert setup_card_counter_unbalanced.bankroll == 975
    assert setup_card_counter_unbalanced.stats.stats[StatsKey(count=2, category=StatsCategory.INSURANCE_AMOUNT_WAGERED)] == 25


def test_initialize_hands(setup_table, setup_player, setup_dealer, setup_shoe):
    """Tests the initialize_hands function."""
    setup_table.add_player(player=setup_player)
    initialize_hands(table=setup_table, dealer=setup_dealer, shoe=setup_shoe)
    assert setup_player.first_hand.cards == ['A', 'Q']
    assert setup_dealer.hand.cards == ['K', 'J']
    assert setup_shoe.seen_cards['A'] == 1
    assert setup_shoe.seen_cards['10-J-Q-K'] == 2


def test_add_back_counters_partner_not_at_table(setup_table, setup_shoe, setup_player, setup_card_counter, setup_back_counter):
    """
    Tests the add_back_counters function when the back counter's
    partner is not at the table.
    """
    setup_table.add_player(player=setup_player)
    setup_table.add_player(player=setup_card_counter)
    setup_table.add_player(player=setup_back_counter)
    setup_table.remove_player(player=setup_card_counter)
    setup_shoe.add_to_seen_cards(card='2')
    setup_shoe.add_to_seen_cards(card='2')
    add_back_counters(table=setup_table, count_dict=get_initial_count(table=setup_table, shoe=setup_shoe))
    assert len(setup_table.players) == 1
    setup_shoe.add_to_seen_cards(card='2')
    add_back_counters(table=setup_table, count_dict=get_initial_count(table=setup_table, shoe=setup_shoe))
    assert len(setup_table.players) == 1


def test_add_back_counters_partner_at_table(setup_table, setup_shoe, setup_card_counter, setup_back_counter):
    """
    Tests the add_back_counters function when the back counter's
    partner is at the table.
    """
    setup_table.add_player(player=setup_card_counter)
    setup_table.add_player(player=setup_back_counter)
    setup_shoe.add_to_seen_cards(card='2')
    setup_shoe.add_to_seen_cards(card='2')
    add_back_counters(table=setup_table, count_dict=get_initial_count(table=setup_table, shoe=setup_shoe))
    assert len(setup_table.players) == 1
    setup_shoe.add_to_seen_cards(card='2')
    add_back_counters(table=setup_table, count_dict=get_initial_count(table=setup_table, shoe=setup_shoe))
    assert len(setup_table.players) == 2


def test_remove_back_counters(setup_table, setup_shoe, setup_card_counter, setup_back_counter):
    """Tests the remove_back_counters function."""
    setup_table.add_player(player=setup_card_counter)
    setup_table.add_player(player=setup_back_counter)
    setup_shoe.add_to_seen_cards(card='2')
    setup_shoe.add_to_seen_cards(card='2')
    setup_shoe.add_to_seen_cards(card='2')
    add_back_counters(table=setup_table, count_dict=get_initial_count(table=setup_table, shoe=setup_shoe))
    assert len(setup_table.players) == 2
    remove_back_counters(table=setup_table, count_dict=get_initial_count(table=setup_table, shoe=setup_shoe))
    assert len(setup_table.players) == 2
    setup_shoe.add_to_seen_cards(card='K')
    setup_shoe.add_to_seen_cards(card='K')
    setup_shoe.add_to_seen_cards(card='K')
    remove_back_counters(table=setup_table, count_dict=get_initial_count(table=setup_table, shoe=setup_shoe))
    assert len(setup_table.players) == 1


def test_player_initial_decision_insurance_dealer_blackjack(setup_card_counter_unbalanced, setup_dealer):
    """
    Tests the player_initial_decision function when the player buys
    insurance and the dealer has blackjack.
    """
    rules = HouseRules(min_bet=10, max_bet=500, insurance=True)
    setup_card_counter_unbalanced.first_hand.add_card(card='5')
    setup_card_counter_unbalanced.first_hand.add_card(card='6')
    setup_card_counter_unbalanced.first_hand.total_bet = 10
    setup_dealer.hand.add_card(card='K')
    setup_dealer.hand.add_card(card='A')
    assert player_initial_decision(player=setup_card_counter_unbalanced, count=3, insurance_count=4, rules=rules, dealer=setup_dealer) == None
    assert setup_card_counter_unbalanced.first_hand.status == HandStatus.SETTLED
    assert setup_card_counter_unbalanced.bankroll == 1005
    assert setup_card_counter_unbalanced.stats.stats[StatsKey(count=3, category=StatsCategory.HANDS_LOST)] == 1
    assert setup_card_counter_unbalanced.stats.stats[StatsKey(count=3, category=StatsCategory.AMOUNT_EARNED)] == -10
    assert setup_card_counter_unbalanced.stats.stats[StatsKey(count=4, category=StatsCategory.INSURANCE_AMOUNT_WAGERED)] == 5
    assert setup_card_counter_unbalanced.stats.stats[StatsKey(count=4, category=StatsCategory.INSURANCE_AMOUNT_EARNED)] == 5


def test_player_initial_decision_insurance_no_dealer_blackjack(setup_card_counter_unbalanced, setup_dealer):
    """
    Tests the player_initial_decision function when the player buys
    insurance and the dealer does not have blackjack.
    """
    rules = HouseRules(min_bet=10, max_bet=500, insurance=True)
    setup_card_counter_unbalanced.first_hand.add_card(card='2')
    setup_card_counter_unbalanced.first_hand.add_card(card='2')
    setup_card_counter_unbalanced.first_hand.total_bet = 10
    setup_dealer.hand.add_card(card='6')
    setup_dealer.hand.add_card(card='A')
    assert player_initial_decision(player=setup_card_counter_unbalanced, count=3, insurance_count=4, rules=rules, dealer=setup_dealer) == 'H'
    assert setup_card_counter_unbalanced.first_hand.status == HandStatus.IN_PLAY
    assert setup_card_counter_unbalanced.bankroll == 995
    assert setup_card_counter_unbalanced.stats.stats[StatsKey(count=4, category=StatsCategory.INSURANCE_AMOUNT_WAGERED)] == 5
    assert setup_card_counter_unbalanced.stats.stats[StatsKey(count=4, category=StatsCategory.INSURANCE_AMOUNT_EARNED)] == -5
    

def test_player_initial_decision_no_insurance_dealer_blackjack(setup_player, setup_dealer):
    """
    Tests the player_initial_decision function when the player cannot
    or does not buy insurance and the dealer has a blackjack.
    """
    rules = HouseRules(min_bet=10, max_bet=500, insurance=False)
    setup_player.first_hand.add_card(card='5')
    setup_player.first_hand.add_card(card='6')
    setup_player.first_hand.total_bet = 10
    setup_dealer.hand.add_card(card='K')
    setup_dealer.hand.add_card(card='A')
    assert player_initial_decision(player=setup_player, count=0, insurance_count=None, rules=rules, dealer=setup_dealer) == None
    assert setup_player.first_hand.status == HandStatus.SETTLED
    assert setup_player.bankroll == 1000
    assert setup_player.stats.stats[StatsKey(count=0, category=StatsCategory.HANDS_LOST)] == 1
    assert setup_player.stats.stats[StatsKey(count=0, category=StatsCategory.AMOUNT_EARNED)] == -10


def test_player_initial_decision_no_insurance_no_dealer_blackjack(setup_player, setup_dealer):
    """
    Tests the player_initial_decsion function when the player cannot
    or does not buy insurance and the dealer does not have a blackjack.
    """
    rules = HouseRules(min_bet=10, max_bet=500, insurance=False)
    setup_player.first_hand.add_card(card='2')
    setup_player.first_hand.add_card(card='3')
    setup_dealer.hand.add_card(card='K')
    setup_dealer.hand.add_card(card='J')
    assert player_initial_decision(player=setup_player, count=0, insurance_count=None, rules=rules, dealer=setup_dealer) == 'H'
    assert setup_player.first_hand.status == HandStatus.IN_PLAY
    

def test_player_initial_decision_player_blackjack(setup_player, setup_dealer, setup_rules):
    """
    Tests the player_initial_decision function when the player has a
    blackjack and the dealer does not.
    """
    setup_player.first_hand.add_card(card='A')
    setup_player.first_hand.add_card(card='K')
    setup_player.first_hand.total_bet = 20
    setup_dealer.hand.add_card(card='K')
    setup_dealer.hand.add_card(card='J')
    assert player_initial_decision(player=setup_player, count=1, insurance_count=None, rules=setup_rules, dealer=setup_dealer) == None
    assert setup_player.first_hand.status == HandStatus.SETTLED
    assert setup_player.bankroll == 1050
    assert setup_player.stats.stats[StatsKey(count=1, category=StatsCategory.HANDS_WON)] == 1
    assert setup_player.stats.stats[StatsKey(count=1, category=StatsCategory.AMOUNT_EARNED)] == 30


def test_player_initial_decision_late_surrender(setup_player, setup_dealer):
    """
    Tests the player_initial_decision function when the player has
    the option to late surrender and does.
    """
    rules = HouseRules(min_bet=10, max_bet=500, late_surrender=True)
    setup_player.first_hand.add_card(card='K')
    setup_player.first_hand.add_card(card='5')
    setup_player.first_hand.total_bet = 50
    setup_dealer.hand.add_card(card='K')
    setup_dealer.hand.add_card(card='J')
    assert player_initial_decision(player=setup_player, count=None, insurance_count=None, rules=rules, dealer=setup_dealer) == None
    assert setup_player.first_hand.status == HandStatus.SETTLED
    assert setup_player.bankroll == 1025
    assert setup_player.stats.stats[StatsKey(count=None, category=StatsCategory.HANDS_LOST)] == 1
    assert setup_player.stats.stats[StatsKey(count=None, category=StatsCategory.AMOUNT_EARNED)] == -25


def test_player_initial_decision_no_late_surrender(setup_player, setup_dealer):
    """
    Tests the player_initial_decision function when the player does
    not have the option to late surrender.
    """
    rules = HouseRules(min_bet=10, max_bet=500, late_surrender=False)
    setup_player.first_hand.add_card(card='K')
    setup_player.first_hand.add_card(card='5')
    setup_player.first_hand.total_bet = 50
    setup_dealer.hand.add_card(card='K')
    setup_dealer.hand.add_card(card='J')
    assert player_initial_decision(player=setup_player, count=None, insurance_count=None, rules=rules, dealer=setup_dealer) == 'Rh'
    assert setup_player.first_hand.status == HandStatus.IN_PLAY


def test_player_plays_hands_settled(setup_player, setup_shoe, setup_dealer):
    """
    Tests the player_plays_hands function when the hand
    is already settled.
    """
    rules = HouseRules(min_bet=10, max_bet=500, late_surrender=True)
    setup_player.first_hand.add_card(card='K')
    setup_player.first_hand.add_card(card='5')
    setup_player.first_hand.total_bet = 50
    setup_dealer.hand.add_card(card='K')
    setup_dealer.hand.add_card(card='J')
    player_plays_hands(
        player=setup_player,
        shoe=setup_shoe,
        count=None,
        insurance_count=None,
        dealer=setup_dealer,
        rules=rules
    )
    assert setup_player.first_hand.status == HandStatus.SETTLED


def test_player_plays_hands_split(setup_shoe, setup_dealer, setup_player, setup_rules):
    """
    Tests the player_plays_hands function when the player is dealt
    a pair and the hand is split.
    """
    setup_player.first_hand.add_card(card='8')
    setup_player.first_hand.add_card(card='8')
    setup_player.first_hand.total_bet = 10
    setup_dealer.hand.add_card(card='6')
    setup_dealer.hand.add_card(card='6')
    player_plays_hands(
        player=setup_player,
        shoe=setup_shoe,
        count=None,
        insurance_count=None,
        dealer=setup_dealer,
        rules=setup_rules
    )
    assert setup_player.first_hand.cards == ['8', 'A']
    assert setup_player.first_hand.status == HandStatus.SHOWDOWN
    assert setup_player.hands[1].cards == ['8', 'K']
    assert setup_player.hands[1].status == HandStatus.SHOWDOWN
    assert setup_player.bankroll == 990
    assert setup_player.stats.stats[StatsKey(count=None, category=StatsCategory.AMOUNT_WAGERED)] == 10


def test_player_plays_hands_split_insufficient_bankroll(setup_shoe, setup_dealer, setup_rules):
    """
    Tests the player_plays_hands function when the player is dealt
    a pair and the player has insufficient bankroll to split a hand.
    """
    player = Player(name='Player 1', min_bet=10, bankroll=10)
    player.first_hand.add_card(card='8')
    player.first_hand.add_card(card='8')
    player.first_hand.total_bet = 20
    setup_dealer.hand.add_card(card='6')
    setup_dealer.hand.add_card(card='6')
    player_plays_hands(
        player=player,
        shoe=setup_shoe,
        count=None,
        insurance_count=None,
        dealer=setup_dealer,
        rules=setup_rules
    )
    assert player.first_hand.cards == ['8', '8']
    assert player.first_hand.status == HandStatus.SHOWDOWN
    assert player.first_hand.total_bet > player.bankroll


def test_player_plays_hands_resplit_aces(setup_player, setup_shoe, setup_dealer):
    """
    Tests the player_plays_hands function when the player is dealt
    a pair of aces and aces can be re-split.
    """
    rules = HouseRules(min_bet=10, max_bet=500, resplit_aces=True)
    setup_player.first_hand.add_card(card='A')
    setup_player.first_hand.add_card(card='A')
    setup_player.first_hand.total_bet = 10
    setup_dealer.hand.add_card(card='6')
    setup_dealer.hand.add_card(card='6')
    player_plays_hands(
        player=setup_player,
        shoe=setup_shoe,
        count=None,
        insurance_count=None,
        dealer=setup_dealer,
        rules=rules
    )
    assert setup_player.first_hand.cards == ['A', 'K']
    assert setup_player.first_hand.status == HandStatus.SHOWDOWN
    assert setup_player.hands[1].cards == ['A', 'Q']
    assert setup_player.hands[1].status == HandStatus.SHOWDOWN
    assert setup_player.hands[2].cards == ['A', 'J']
    assert setup_player.hands[2].status == HandStatus.SHOWDOWN
    assert setup_player.bankroll == 980
    assert setup_player.stats.stats[StatsKey(count=None, category=StatsCategory.AMOUNT_WAGERED)] == 20


def test_player_plays_hands_resplit_aces_not_allowed(setup_player, setup_shoe, setup_dealer):
    """
    Tests the player_plays_hands function when the player is dealt
    a pair of aces and aces cannot be re-split.
    """
    rules = HouseRules(min_bet=10, max_bet=500, resplit_aces=False)
    setup_player.first_hand.add_card(card='A')
    setup_player.first_hand.add_card(card='A')
    setup_player.first_hand.total_bet = 10
    setup_dealer.hand.add_card(card='6')
    setup_dealer.hand.add_card(card='6')
    player_plays_hands(
        player=setup_player,
        shoe=setup_shoe,
        count=None,
        insurance_count=None,
        dealer=setup_dealer,
        rules=rules
    )
    assert setup_player.first_hand.cards == ['A', 'A']
    assert setup_player.first_hand.status == HandStatus.SHOWDOWN
    assert setup_player.hands[1].cards == ['A', 'K']
    assert setup_player.hands[1].status == HandStatus.SHOWDOWN
    assert setup_player.bankroll == 990
    assert setup_player.stats.stats[StatsKey(count=None, category=StatsCategory.AMOUNT_WAGERED)] == 10
    

def test_player_plays_hands_double_down(setup_player, setup_dealer, setup_shoe):
    """
    Tests the player_plays_hands function when the player
    can double down.
    """
    rules = HouseRules(min_bet=10, max_bet=500, double_down=True)
    setup_player.first_hand.add_card(card='5')
    setup_player.first_hand.add_card(card='6')
    setup_player.first_hand.total_bet = 10
    setup_dealer.hand.add_card(card='2')
    setup_dealer.hand.add_card(card='3')
    player_plays_hands(
        player=setup_player,
        shoe=setup_shoe,
        count=None,
        insurance_count=None,
        dealer=setup_dealer,
        rules=rules
    )
    assert setup_player.first_hand.cards == ['5', '6', 'A']
    assert setup_player.first_hand.total_bet == 20
    assert setup_player.first_hand.status == HandStatus.SHOWDOWN
    assert setup_player.bankroll == 990
    assert setup_player.stats.stats[StatsKey(count=None, category=StatsCategory.AMOUNT_WAGERED)] == 10
    

def test_player_plays_hands_double_down_not_allowed(setup_player, setup_dealer, setup_shoe):
    """
    Tests the player_plays_hands function when the player
    cannot double down.
    """
    rules = HouseRules(min_bet=10, max_bet=500, double_down=False)
    setup_player.first_hand.add_card(card='5')
    setup_player.first_hand.add_card(card='6')
    setup_player.first_hand.total_bet = 10
    setup_dealer.hand.add_card(card='2')
    setup_dealer.hand.add_card(card='3')
    player_plays_hands(
        player=setup_player,
        shoe=setup_shoe,
        count=None,
        insurance_count=None,
        dealer=setup_dealer,
        rules=rules
    )
    assert setup_player.first_hand.cards == ['5', '6', 'A', 'K']
    assert setup_player.first_hand.total_bet == 10
    assert setup_player.first_hand.status == HandStatus.SETTLED
    assert setup_player.bankroll == 1000
    assert setup_player.stats.stats[StatsKey(count=None, category=StatsCategory.AMOUNT_WAGERED)] == 0


def test_player_plays_hands_double_down_insufficient_bankroll(setup_player, setup_dealer, setup_shoe):
    """
    Tests the player_plays_hands function when the player
    has insufficient bankroll to double down.
    """
    rules = HouseRules(min_bet=10, max_bet=500, double_down=True)
    setup_player.first_hand.add_card(card='5')
    setup_player.first_hand.add_card(card='6')
    setup_player.first_hand.total_bet = 10
    setup_player.edit_bankroll(amount=-1000)
    setup_dealer.hand.add_card(card='2')
    setup_dealer.hand.add_card(card='3')
    player_plays_hands(
        player=setup_player,
        shoe=setup_shoe,
        count=None,
        insurance_count=None,
        dealer=setup_dealer,
        rules=rules
    )
    assert setup_player.first_hand.cards == ['5', '6', 'A', 'K']
    assert setup_player.first_hand.total_bet == 10
    assert setup_player.first_hand.status == HandStatus.SETTLED
    assert setup_player.bankroll == 0
    assert setup_player.stats.stats[StatsKey(count=None, category=StatsCategory.AMOUNT_WAGERED)] == 0 
    

def test_player_plays_hands_double_after_split(setup_player, setup_dealer, setup_shoe):
    """
    Tests the player_plays_hands function when the player
    doubles after splitting.
    """
    rules = HouseRules(min_bet=10, max_bet=500, double_down=True, double_after_split=True)
    setup_player.first_hand.add_card(card='2')
    setup_player.first_hand.add_card(card='2')
    setup_player.first_hand.total_bet = 10
    setup_player.edit_bankroll(amount=-970)
    setup_dealer.hand.add_card(card='2')
    setup_dealer.hand.add_card(card='3')
    setup_shoe._cards = ['K', 'A', 'J', '8', 'Q', '8']
    player_plays_hands(
        player=setup_player,
        shoe=setup_shoe,
        count=None,
        insurance_count=None,
        dealer=setup_dealer,
        rules=rules
    )
    assert setup_player.first_hand.cards == ['2', '8', 'Q']
    assert setup_player.first_hand.total_bet == 20
    assert setup_player.first_hand.status == HandStatus.SHOWDOWN
    assert setup_player.hands[1].cards == ['2', '8', 'J']
    assert setup_player.hands[1].total_bet == 20
    assert setup_player.hands[1].status == HandStatus.SHOWDOWN
    assert setup_player.stats.stats[StatsKey(count=None, category=StatsCategory.AMOUNT_WAGERED)] == 30


def test_player_plays_hands_double_after_split_not_allowed(setup_player, setup_dealer, setup_shoe):
    """
    Tests the player_plays_hands function when the player
    is not allowed to double after splitting.
    """
    rules = HouseRules(min_bet=10, max_bet=500, double_down=True, double_after_split=False)
    setup_player.first_hand.add_card(card='2')
    setup_player.first_hand.add_card(card='2')
    setup_player.first_hand.total_bet = 10
    setup_dealer.hand.add_card(card='2')
    setup_dealer.hand.add_card(card='3')
    player_plays_hands(
        player=setup_player,
        shoe=setup_shoe,
        count=None,
        insurance_count=None,
        dealer=setup_dealer,
        rules=rules
    )
    assert setup_player.first_hand.cards == ['2', '2', 'A', 'K']
    assert setup_player.first_hand.total_bet == 10
    assert setup_player.first_hand.status == HandStatus.SHOWDOWN
    assert setup_player.stats.stats[StatsKey(count=None, category=StatsCategory.AMOUNT_WAGERED)] == 0


def test_player_plays_hands_double_after_split_insufficient_bankroll(setup_player, setup_dealer, setup_shoe):
    """
    Tests the player_plays_hands function when the player
    has insufficient bankroll to double after splitting.
    """
    rules = HouseRules(min_bet=10, max_bet=500, double_down=True, double_after_split=True)
    setup_player.first_hand.add_card(card='2')
    setup_player.first_hand.add_card(card='2')
    setup_player.first_hand.total_bet = 10
    setup_player.edit_bankroll(amount=-980)
    setup_dealer.hand.add_card(card='2')
    setup_dealer.hand.add_card(card='3')
    player_plays_hands(
        player=setup_player,
        shoe=setup_shoe,
        count=None,
        insurance_count=None,
        dealer=setup_dealer,
        rules=rules
    )
    assert setup_player.first_hand.cards == ['2', '2', 'A', 'K']
    assert setup_player.first_hand.total_bet == 10
    assert setup_player.first_hand.total_bet * 3 > setup_player.bankroll
    assert setup_player.first_hand.status == HandStatus.SHOWDOWN
    assert setup_player.stats.stats[StatsKey(count=None, category=StatsCategory.AMOUNT_WAGERED)] == 0


def test_player_plays_hands_stand(setup_player, setup_dealer, setup_shoe, setup_rules):
    """Tests the player_plays_hands function when the player stands."""
    setup_player.first_hand.add_card(card='6')
    setup_player.first_hand.add_card(card='7')
    setup_player.first_hand.total_bet = 10
    setup_dealer.hand.add_card(card='6')
    setup_dealer.hand.add_card(card='6')
    player_plays_hands(
        player=setup_player,
        shoe=setup_shoe,
        count=None,
        insurance_count=None,
        dealer=setup_dealer,
        rules=setup_rules
    )
    assert setup_player.first_hand.cards == ['6', '7']
    assert setup_player.first_hand.status == HandStatus.SHOWDOWN


def test_player_plays_hands_busted(setup_player, setup_dealer, setup_shoe, setup_rules):
    """Tests the player_plays_hands function when the hand is busted."""
    setup_player.first_hand.add_card(card='6')
    setup_player.first_hand.add_card(card='7')
    setup_player.first_hand.total_bet = 10
    setup_dealer.hand.add_card(card='10')
    setup_dealer.hand.add_card(card='Q')
    player_plays_hands(
        player=setup_player,
        shoe=setup_shoe,
        count=None,
        insurance_count=None,
        dealer=setup_dealer,
        rules=setup_rules
    )
    assert setup_player.first_hand.cards == ['6', '7', 'A', 'K']
    assert setup_player.first_hand.status == HandStatus.SETTLED
    assert setup_player.first_hand.total() > 21


@pytest.mark.parametrize(
    'test_hole_card, test_up_card, test_s17, expected',
    [
         ('2', '6', True, 19),
         ('6', 'A', True, 17),
         ('6', 'A', False, 18),
         ('7', 'J', True, 17),
         ('7', 'J', False, 17)
     ]
)
def test_dealer_plays_hand(setup_shoe, setup_dealer, test_hole_card, test_up_card, test_s17, expected):
    """Tests the dealer_plays_hand function."""
    rules = HouseRules(min_bet=10, max_bet=500, s17=test_s17)
    setup_dealer.hand.add_card(card=test_hole_card)
    setup_dealer.hand.add_card(card=test_up_card)
    dealer_plays_hand(shoe=setup_shoe, dealer=setup_dealer, rules=rules)
    assert setup_dealer.hand.total() == expected


def test_dealer_turn(setup_table, setup_player):
    """Tests the dealer_turn function."""
    setup_table.add_player(player=setup_player)
    setup_player.first_hand.status = HandStatus.SETTLED
    assert not dealer_turn(table=setup_table)
    setup_player.first_hand.status = HandStatus.SHOWDOWN
    assert dealer_turn(table=setup_table)
    

def test_all_hands_busted_true(setup_table, setup_player):
    """
    Tests the all_hands_busted function
    when all hands at the table are busted.
    """
    setup_table.add_player(player=setup_player)
    setup_player.first_hand.add_card(card='4')
    setup_player.first_hand.add_card(card='J')
    setup_player.first_hand.add_card(card='K')
    assert setup_player.first_hand.is_busted()
    assert all_hands_busted(table=setup_table)


def test_all_hands_busted_false(setup_table, setup_player):
    """
    Tests the all_hands_busted function
    when not all hands at the table are busted.
    """
    setup_table.add_player(player=setup_player)
    setup_player.first_hand.add_card(card='J')
    setup_player.first_hand.add_card(card='K')
    assert not setup_player.first_hand.is_busted()
    assert not all_hands_busted(table=setup_table)


def test_compare_hands_win_total(setup_player, setup_dealer):
    """
    Tests the compare_hands function when the player wins
    based on total.
    """
    setup_player.first_hand.status = HandStatus.SHOWDOWN
    setup_player.first_hand.add_card(card='J')
    setup_player.first_hand.add_card(card='K')
    setup_player.first_hand.total_bet = 10
    setup_dealer.hand.add_card(card='10')
    setup_dealer.hand.add_card(card='8')
    compare_hands(player=setup_player, dealer=setup_dealer, count=3)
    assert setup_player.first_hand.status == HandStatus.SETTLED
    assert setup_player.bankroll == 1020
    assert setup_player.stats.stats[StatsKey(count=3, category=StatsCategory.HANDS_WON)] == 1
    assert setup_player.stats.stats[StatsKey(count=3, category=StatsCategory.AMOUNT_EARNED)] == 10


def test_compare_hands_win_dealer_busts(setup_player, setup_dealer):
    """
    Tests the compare_hands function when the player wins
    and the dealer busts.
    """
    setup_player.first_hand.status = HandStatus.SHOWDOWN
    setup_player.first_hand.add_card(card='J')
    setup_player.first_hand.add_card(card='K')
    setup_player.first_hand.total_bet = 20
    setup_dealer.hand.add_card(card='10')
    setup_dealer.hand.add_card(card='6')
    setup_dealer.hand.add_card(card='K')
    compare_hands(player=setup_player, dealer=setup_dealer, count=1)
    assert setup_player.first_hand.status == HandStatus.SETTLED
    assert setup_player.bankroll == 1040
    assert setup_player.stats.stats[StatsKey(count=1, category=StatsCategory.HANDS_WON)] == 1
    assert setup_player.stats.stats[StatsKey(count=1, category=StatsCategory.AMOUNT_EARNED)] == 20


def test_compare_hands_push(setup_player, setup_dealer):
    """
    Tests the compare_hands function when the player and
    dealer push.
    """
    setup_player.first_hand.status = HandStatus.SHOWDOWN
    setup_player.first_hand.add_card(card='J')
    setup_player.first_hand.add_card(card='K')
    setup_player.first_hand.total_bet = 10
    setup_dealer.hand.add_card(card='10')
    setup_dealer.hand.add_card(card='Q')
    compare_hands(player=setup_player, dealer=setup_dealer, count=None)
    assert setup_player.first_hand.status == HandStatus.SETTLED
    assert setup_player.bankroll == 1010
    assert setup_player.stats.stats[StatsKey(count=None, category=StatsCategory.HANDS_PUSHED)] == 1


def test_compare_hands_loss_total(setup_player, setup_dealer):
    """
    Tests the compare_hands function when the player loses
    based on total.
    """
    setup_player.first_hand.status = HandStatus.SHOWDOWN
    setup_player.first_hand.add_card(card='6')
    setup_player.first_hand.add_card(card='K')
    setup_player.first_hand.total_bet = 20
    setup_dealer.hand.add_card(card='10')
    setup_dealer.hand.add_card(card='8')
    compare_hands(player=setup_player, dealer=setup_dealer, count=-2)
    assert setup_player.first_hand.status == HandStatus.SETTLED
    assert setup_player.bankroll == 1000
    assert setup_player.stats.stats[StatsKey(count=-2, category=StatsCategory.HANDS_LOST)] == 1
    assert setup_player.stats.stats[StatsKey(count=-2, category=StatsCategory.AMOUNT_EARNED)] == -20


def test_clear_hands(setup_dealer_with_hand, setup_table, setup_player):
    """Test the clear_hands function."""
    setup_table.add_player(player=setup_player)
    setup_player.first_hand.add_card(card='A')
    setup_player.first_hand.add_card(card='A')
    split_hand = setup_player.first_hand.split()
    setup_player.hands.append(split_hand)
    setup_player.first_hand.add_card(card='2')
    setup_player.hands[1].add_card(card='6')
    assert setup_dealer_with_hand.hand.cards == ['8', '6']
    assert setup_player.first_hand.cards == ['A', '2']
    assert setup_player.hands[1].cards == ['A', '6']
    clear_hands(dealer=setup_dealer_with_hand, table=setup_table)
    assert setup_dealer_with_hand.hand.cards == []
    assert setup_player.first_hand.cards == []
    assert len(setup_player.hands) == 1
    

def test_play_round_back_counters_added(setup_table, setup_shoe, setup_dealer, setup_card_counter, setup_back_counter, setup_rules):
    """
    Tests the play_round function when back counters
    are added.
    """
    setup_table.add_player(player=setup_card_counter)
    setup_table.add_player(player=setup_back_counter)
    setup_shoe.add_to_seen_cards(card='2')
    setup_shoe.add_to_seen_cards(card='2')
    setup_shoe.add_to_seen_cards(card='2')
    play_round(table=setup_table, dealer=setup_dealer, shoe=setup_shoe, rules=setup_rules)
    assert setup_card_counter.stats.stats[StatsKey(count=3, category=StatsCategory.AMOUNT_WAGERED)] == 40
    assert setup_card_counter.stats.stats[StatsKey(count=3, category=StatsCategory.AMOUNT_EARNED)] == 60
    assert setup_card_counter.stats.stats[StatsKey(count=3, category=StatsCategory.HANDS_WON)] == 1
    assert setup_back_counter.stats.stats[StatsKey(count=3, category=StatsCategory.AMOUNT_WAGERED)] == 40
    assert setup_back_counter.stats.stats[StatsKey(count=3, category=StatsCategory.AMOUNT_EARNED)] == 40
    assert setup_back_counter.stats.stats[StatsKey(count=3, category=StatsCategory.HANDS_WON)] == 1


def test_play_round_back_counters_removed(setup_table, setup_shoe, setup_dealer, setup_card_counter, setup_back_counter, setup_rules):
    """
    Tests the play_round function when back counters
    are removed.
    """
    setup_table.add_player(player=setup_card_counter)
    setup_table.add_player(player=setup_back_counter)
    setup_shoe.add_to_seen_cards(card='2')
    setup_shoe.add_to_seen_cards(card='2')
    setup_shoe.add_to_seen_cards(card='2')
    add_back_counters(table=setup_table, count_dict=get_initial_count(table=setup_table, shoe=setup_shoe))
    assert len(setup_table.players) == 2
    setup_shoe.add_to_seen_cards(card='K')
    setup_shoe.add_to_seen_cards(card='K')
    setup_shoe.add_to_seen_cards(card='K')
    play_round(table=setup_table, dealer=setup_dealer, shoe=setup_shoe, rules=setup_rules)
    assert setup_card_counter.stats.stats[StatsKey(count=0, category=StatsCategory.AMOUNT_WAGERED)] == 10
    assert setup_card_counter.stats.stats[StatsKey(count=0, category=StatsCategory.AMOUNT_EARNED)] == 15
    assert setup_card_counter.stats.stats[StatsKey(count=0, category=StatsCategory.HANDS_WON)] == 1


def test_play_round_insufficient_funds(setup_table, setup_dealer, setup_player, setup_rules, setup_shoe):
    """
    Tests the play_round function when a player
    has insufficient funds.
    """
    setup_table.add_player(player=setup_player)
    setup_player.edit_bankroll(amount=-1000)
    assert setup_player.bankroll == 0
    play_round(table=setup_table, dealer=setup_dealer, shoe=setup_shoe, rules=setup_rules)
    assert len(setup_table.players) == 0
    assert setup_shoe.cards[-1] == 'A'
    

def test_play_round_insurance_win(setup_dealer, setup_shoe, setup_card_counter_unbalanced):
    """
    Tests the play_round function when a player
    purchases insurance and the dealer has blackjack.
    """
    rules = HouseRules(min_bet=10, max_bet=500, insurance=True)
    table = Table(rules=rules)
    table.add_player(player=setup_card_counter_unbalanced)
    setup_shoe._cards = ['A', '5', 'K', 'K']
    setup_shoe.add_to_seen_cards(card='2')
    setup_shoe.add_to_seen_cards(card='2')
    setup_shoe.add_to_seen_cards(card='2')
    play_round(table=table, dealer=setup_dealer, shoe=setup_shoe, rules=rules)
    assert setup_card_counter_unbalanced.stats.stats[StatsKey(count=3, category=StatsCategory.AMOUNT_WAGERED)] == 40
    assert setup_card_counter_unbalanced.stats.stats[StatsKey(count=3, category=StatsCategory.AMOUNT_EARNED)] == -40
    assert setup_card_counter_unbalanced.stats.stats[StatsKey(count=3, category=StatsCategory.HANDS_LOST)] == 1
    assert setup_card_counter_unbalanced.stats.stats[StatsKey(count=2, category=StatsCategory.INSURANCE_AMOUNT_WAGERED)] == 20
    assert setup_card_counter_unbalanced.stats.stats[StatsKey(count=2, category=StatsCategory.INSURANCE_AMOUNT_EARNED)] == 20


def test_play_round_insurance_loss(setup_dealer, setup_shoe, setup_card_counter_unbalanced):
    """
    Tests the play_round function when a player
    purchases insurance and the dealer does not have blackjack.
    """
    rules = HouseRules(min_bet=10, max_bet=500, insurance=True)
    table = Table(rules=rules)
    table.add_player(player=setup_card_counter_unbalanced)
    setup_shoe._cards = ['5', 'A', '5', '7', 'K']
    setup_shoe.add_to_seen_cards(card='2')
    setup_shoe.add_to_seen_cards(card='2')
    setup_shoe.add_to_seen_cards(card='2')
    play_round(table=table, dealer=setup_dealer, shoe=setup_shoe, rules=rules)
    assert setup_card_counter_unbalanced.stats.stats[StatsKey(count=3, category=StatsCategory.AMOUNT_WAGERED)] == 40
    assert setup_card_counter_unbalanced.stats.stats[StatsKey(count=3, category=StatsCategory.AMOUNT_EARNED)] == 40
    assert setup_card_counter_unbalanced.stats.stats[StatsKey(count=3, category=StatsCategory.HANDS_WON)] == 1
    assert setup_card_counter_unbalanced.stats.stats[StatsKey(count=2, category=StatsCategory.INSURANCE_AMOUNT_WAGERED)] == 20
    assert setup_card_counter_unbalanced.stats.stats[StatsKey(count=2, category=StatsCategory.INSURANCE_AMOUNT_EARNED)] == -20
    

def test_play_round_player_blackjack(setup_table, setup_player, setup_dealer, setup_shoe, setup_rules):
    """
    Tests the play_round function when a player
    has a blackjack.
    """
    setup_table.add_player(player=setup_player)
    setup_shoe._cards = ['K', 'K', '9', 'A']
    play_round(table=setup_table, dealer=setup_dealer, shoe=setup_shoe, rules=setup_rules)
    assert setup_player.stats.stats[StatsKey(count=None, category=StatsCategory.AMOUNT_WAGERED)] == 10
    assert setup_player.stats.stats[StatsKey(count=None, category=StatsCategory.AMOUNT_EARNED)] == 15
    assert setup_player.stats.stats[StatsKey(count=None, category=StatsCategory.HANDS_WON)] == 1
    

def test_play_round_dealer_blackjack(setup_table, setup_player, setup_dealer, setup_shoe, setup_rules):
    """
    Tests the play_round function when the dealer
    has a blackjack.
    """
    setup_table.add_player(player=setup_player)
    setup_shoe._cards = ['K', '9', 'A', 'A']
    play_round(table=setup_table, dealer=setup_dealer, shoe=setup_shoe, rules=setup_rules)
    assert setup_player.stats.stats[StatsKey(count=None, category=StatsCategory.AMOUNT_WAGERED)] == 10
    assert setup_player.stats.stats[StatsKey(count=None, category=StatsCategory.AMOUNT_EARNED)] == -10
    assert setup_player.stats.stats[StatsKey(count=None, category=StatsCategory.HANDS_LOST)] == 1


def test_play_round_player_dealer_blackjack(setup_table, setup_player, setup_dealer, setup_shoe, setup_rules):
    """
    Tests the play_round function when a player
    and the dealer have a blackjack.
    """
    setup_table.add_player(player=setup_player)
    setup_shoe._cards = ['K', 'K', 'A', 'A']
    play_round(table=setup_table, dealer=setup_dealer, shoe=setup_shoe, rules=setup_rules)
    assert setup_player.stats.stats[StatsKey(count=None, category=StatsCategory.AMOUNT_WAGERED)] == 10
    assert setup_player.stats.stats[StatsKey(count=None, category=StatsCategory.AMOUNT_EARNED)] == 0
    assert setup_player.stats.stats[StatsKey(count=None, category=StatsCategory.HANDS_PUSHED)] == 1


def test_play_round_all_hands_busted_dealer_shows_hole_card(setup_player, setup_dealer, setup_shoe):
    """
    Tests the play_round function when all hands
    are busted and the dealer shows their hole card.
    """
    rules = HouseRules(min_bet=10, max_bet=500, dealer_shows_hole_card=True)
    table = Table(rules=rules)
    table.add_player(player=setup_player)
    setup_shoe._cards = ['10', 'J', 'Q', 'K', '4']
    play_round(table=table, dealer=setup_dealer, shoe=setup_shoe, rules=rules)
    assert setup_shoe.seen_cards['4'] == 1
    assert setup_shoe.seen_cards['10-J-Q-K'] == 4


def test_play_round_all_hands_busted_dealer_does_not_show_hole_card(setup_player, setup_dealer, setup_shoe):
    """
    Tests the play_round function when all hands
    are busted and the dealer does not show their hole card.
    """
    rules = HouseRules(min_bet=10, max_bet=500, dealer_shows_hole_card=False)
    table = Table(rules=rules)
    table.add_player(player=setup_player)
    setup_shoe._cards = ['10', 'J', 'Q', 'K', '4']
    play_round(table=table, dealer=setup_dealer, shoe=setup_shoe, rules=rules)
    assert setup_shoe.seen_cards['4'] == 1
    assert setup_shoe.seen_cards['10-J-Q-K'] == 3


@pytest.mark.parametrize(
    'test_dealer_shows_hole_card',
    [
         (True),
         (False)
     ]
)
def test_play_round_all_hands_do_not_bust(setup_player, setup_dealer, setup_shoe, test_dealer_shows_hole_card):
    """
    Tests the play_round function when there are
    hands that are not busted.
    """
    rules = HouseRules(min_bet=10, max_bet=500, dealer_shows_hole_card=test_dealer_shows_hole_card)
    table = Table(rules=rules)
    table.add_player(player=setup_player)
    setup_shoe._cards = ['10', 'J', 'Q', 'K']
    play_round(table=table, dealer=setup_dealer, shoe=setup_shoe, rules=rules)
    assert setup_shoe.seen_cards['10-J-Q-K'] == 4


def test_play_round_clear_hands(setup_table, setup_player, setup_dealer, setup_shoe, setup_rules):
    """
    Tests the play_round function to check
    that the hands are properly cleared after
    each round.
    """
    setup_table.add_player(player=setup_player)
    play_round(table=setup_table, dealer=setup_dealer, shoe=setup_shoe, rules=setup_rules)
    assert setup_dealer.hand.cards == []
    assert setup_player.first_hand.cards == []