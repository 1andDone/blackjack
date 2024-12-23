import pytest
from blackjack.enums import StatsCategory
from blackjack.hand import HandStatus
from blackjack.helpers import get_count, get_insurance_count
from blackjack.helpers import get_placed_bet, place_bet
from blackjack.helpers import place_insurance_bet, initialize_hands
from blackjack.helpers import add_back_counters, remove_back_counters
from blackjack.helpers import player_initial_decision, player_plays_hands
from blackjack.helpers import dealer_turn, all_hands_busted
from blackjack.helpers import dealer_plays_hand, compare_hands
from blackjack.helpers import clear_hands, play_round
from blackjack.player import Player
from blackjack.playing_strategy import PlayingStrategy
from blackjack.shoe import Shoe
from blackjack.rules import Rules
from blackjack.stats import StatsKey
from blackjack.table import Table


def test_get_count(player, table, card_counter_unbalanced, back_counter):
    """Tests the get_count function."""
    shoe = Shoe(shoe_size=6)
    # burn an entire 52 card deck and make them all visible 'K'
    # exactly 5 decks remain
    for _ in range(0, 52):
        shoe.burn_card(seen=False)
        shoe.add_to_seen_cards(card='K')
    table.add_player(player=player)
    table.add_player(player=card_counter_unbalanced)
    table.add_player(player=back_counter)
    count = get_count(table=table, shoe=shoe)
    assert count[player] is None
    assert count[card_counter_unbalanced] == -72
    assert count[back_counter] == -10


def test_get_insurance_count(shoe, player, table, card_counter_balanced, card_counter_unbalanced, back_counter):
    """Tests the get_insurance_count function."""
    shoe.add_to_seen_cards(card='K')
    shoe.add_to_seen_cards(card='K')
    shoe.add_to_seen_cards(card='K')
    shoe.add_to_seen_cards(card='2')
    table.add_player(player=player)
    table.add_player(player=card_counter_balanced)
    table.add_player(player=card_counter_unbalanced)
    table.add_player(player=back_counter)
    insurance_count = get_insurance_count(table=table, shoe=shoe)
    assert insurance_count[player] is None
    assert insurance_count[card_counter_balanced] is None
    assert insurance_count[card_counter_unbalanced] == -2
    assert back_counter not in insurance_count


def test_get_placed_bet_player_not_removed(shoe, player, table):
    """Tests the get_placed_bet function when a player is not removed."""
    table.add_player(player=player)
    count_dict = get_count(table=table, shoe=shoe)
    placed_bet_dict = get_placed_bet(table=table, count_dict=count_dict)
    assert placed_bet_dict[player] == player.placed_bet()


def test_get_placed_bet_player_removed(shoe, table):
    """Tests the get_placed_bet function when a player is removed."""
    player = Player(name='Player 1', min_bet=10, bankroll=10)
    table.add_player(player=player)
    player.adjust_bankroll(amount=-10)
    count_dict = get_count(table=table, shoe=shoe)
    placed_bet_dict = get_placed_bet(table=table, count_dict=count_dict)
    assert player not in placed_bet_dict


def test_place_bet(player):
    """Tests the place_bet function."""
    place_bet(player=player, amount=50, count=2)
    assert player.get_first_hand().total_bet == 50
    assert player.bankroll == 950
    assert player.stats.stats[StatsKey(count=2, category=StatsCategory.AMOUNT_BET)] == 50


def test_place_insurance_bet(card_counter_unbalanced):
    """Tests the place_insurance_bet function."""
    place_insurance_bet(player=card_counter_unbalanced, amount=25, count=2)
    assert card_counter_unbalanced.get_first_hand().side_bet == 25
    assert card_counter_unbalanced.bankroll == 975
    assert card_counter_unbalanced.stats.stats[StatsKey(count=2, category=StatsCategory.INSURANCE_AMOUNT_BET)] == 25


def test_initialize_hands(player, dealer, shoe, table):
    """Tests the initialize_hands function."""
    table.add_player(player=player)
    initialize_hands(table=table, dealer=dealer, shoe=shoe)
    assert player.get_first_hand().cards == ['A', 'Q']
    assert dealer.hand.cards == ['K', 'J']
    assert shoe.seen_cards['A'] == 1
    assert shoe.seen_cards['10-J-Q-K'] == 2


def test_add_back_counters(shoe, table, card_counter_balanced, back_counter):
    """
    Tests the add_back_counters function when the back counter's partner is at
    the table.
    
    """
    table.add_player(player=card_counter_balanced)
    table.add_player(player=back_counter)
    shoe.add_to_seen_cards(card='2')
    shoe.add_to_seen_cards(card='2')
    add_back_counters(table=table, count_dict=get_count(table=table, shoe=shoe))
    assert len(table.players) == 1
    assert shoe.running_count(card_counting_system=back_counter.card_counting_system) < back_counter.entry_point
    shoe.add_to_seen_cards(card='2')
    add_back_counters(table=table, count_dict=get_count(table=table, shoe=shoe))
    assert len(table.players) == 2
    assert shoe.running_count(card_counting_system=back_counter.card_counting_system) == back_counter.entry_point


def test_remove_back_counters(shoe, table, card_counter_balanced, back_counter):
    """Tests the remove_back_counters function."""
    table.add_player(player=card_counter_balanced)
    table.add_player(player=back_counter)
    shoe.add_to_seen_cards(card='2')
    shoe.add_to_seen_cards(card='2')
    shoe.add_to_seen_cards(card='2')
    add_back_counters(table=table, count_dict=get_count(table=table, shoe=shoe))
    assert len(table.players) == 2
    assert shoe.running_count(card_counting_system=back_counter.card_counting_system) > back_counter.exit_point
    remove_back_counters(table=table, count_dict=get_count(table=table, shoe=shoe))
    assert len(table.players) == 2
    assert shoe.running_count(card_counting_system=back_counter.card_counting_system) > back_counter.exit_point
    shoe.add_to_seen_cards(card='K')
    shoe.add_to_seen_cards(card='K')
    shoe.add_to_seen_cards(card='K')
    remove_back_counters(table=table, count_dict=get_count(table=table, shoe=shoe))
    assert len(table.players) == 1
    assert shoe.running_count(card_counting_system=back_counter.card_counting_system) == back_counter.exit_point


def test_player_initial_decision_insurance_dealer_blackjack(card_counter_unbalanced, dealer):
    """
    Tests the player_initial_decision function when the player buys
    insurance and the dealer has blackjack.

    """
    rules = Rules(min_bet=10, max_bet=500, insurance=True)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    card_counter_unbalanced.get_first_hand().add_card(card='5')
    card_counter_unbalanced.get_first_hand().add_card(card='6')
    card_counter_unbalanced.get_first_hand().add_to_total_bet(amount=10)
    dealer.hand.add_card(card='K')
    dealer.hand.add_card(card='A')
    assert player_initial_decision(
        player=card_counter_unbalanced,
        count=3,
        insurance_count=4,
        rules=rules,
        dealer=dealer,
        playing_strategy=playing_strategy
    ) is None
    assert card_counter_unbalanced.get_first_hand().status == HandStatus.SETTLED
    assert card_counter_unbalanced.bankroll == 1005
    assert card_counter_unbalanced.stats.stats[StatsKey(count=3, category=StatsCategory.HANDS_LOST)] == 1
    assert card_counter_unbalanced.stats.stats[StatsKey(count=3, category=StatsCategory.AMOUNT_EARNED)] == -10
    assert card_counter_unbalanced.stats.stats[StatsKey(count=4, category=StatsCategory.INSURANCE_AMOUNT_BET)] == 5
    assert card_counter_unbalanced.stats.stats[StatsKey(count=4, category=StatsCategory.INSURANCE_AMOUNT_EARNED)] == 5


def test_player_initial_decision_insurance_no_dealer_blackjack(card_counter_unbalanced, dealer):
    """
    Tests the player_initial_decision function when the player buys insurance
    and the dealer does not have blackjack.

    """
    rules = Rules(min_bet=10, max_bet=500, insurance=True)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    card_counter_unbalanced.get_first_hand().add_card(card='2')
    card_counter_unbalanced.get_first_hand().add_card(card='2')
    card_counter_unbalanced.get_first_hand().add_to_total_bet(amount=10)
    dealer.hand.add_card(card='6')
    dealer.hand.add_card(card='A')
    assert player_initial_decision(
        player=card_counter_unbalanced,
        count=3,
        insurance_count=4,
        rules=rules,
        dealer=dealer,
        playing_strategy=playing_strategy
    ) == 'H'
    assert card_counter_unbalanced.get_first_hand().status == HandStatus.IN_PLAY
    assert card_counter_unbalanced.bankroll == 995
    assert card_counter_unbalanced.stats.stats[StatsKey(count=4, category=StatsCategory.INSURANCE_AMOUNT_BET)] == 5
    assert card_counter_unbalanced.stats.stats[StatsKey(count=4, category=StatsCategory.INSURANCE_AMOUNT_EARNED)] == -5


def test_player_initial_decision_no_insurance_dealer_blackjack(player, dealer):
    """
    Tests the player_initial_decision function when the player cannot or does
    not buy insurance and the dealer has a blackjack.

    """
    rules = Rules(min_bet=10, max_bet=500, insurance=False)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    player.get_first_hand().add_card(card='5')
    player.get_first_hand().add_card(card='6')
    player.get_first_hand().add_to_total_bet(amount=10)
    dealer.hand.add_card(card='K')
    dealer.hand.add_card(card='A')
    assert player_initial_decision(
        player=player,
        count=0,
        insurance_count=None,
        rules=rules,
        dealer=dealer,
        playing_strategy=playing_strategy
    ) is None
    assert player.get_first_hand().status == HandStatus.SETTLED
    assert player.bankroll == 1000
    assert player.stats.stats[StatsKey(count=0, category=StatsCategory.HANDS_LOST)] == 1
    assert player.stats.stats[StatsKey(count=0, category=StatsCategory.AMOUNT_EARNED)] == -10


def test_player_initial_decision_no_insurance_no_dealer_blackjack(player, dealer):
    """
    Tests the player_initial_decision function when the player cannot
    or does not buy insurance and the dealer does not have a blackjack.

    """
    rules = Rules(min_bet=10, max_bet=500, insurance=False)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    player.get_first_hand().add_card(card='2')
    player.get_first_hand().add_card(card='3')
    dealer.hand.add_card(card='K')
    dealer.hand.add_card(card='J')
    assert player_initial_decision(
        player=player,
        count=0,
        insurance_count=None,
        rules=rules,
        dealer=dealer,
        playing_strategy=playing_strategy
    ) == 'H'
    assert player.get_first_hand().status == HandStatus.IN_PLAY


def test_player_initial_decision_player_blackjack(player, dealer, rules):
    """
    Tests the player_initial_decision function when the player has a
    blackjack and the dealer does not.

    """
    playing_strategy = PlayingStrategy(s17=rules.s17)
    player.get_first_hand().add_card(card='A')
    player.get_first_hand().add_card(card='K')
    player.get_first_hand().add_to_total_bet(amount=20)
    dealer.hand.add_card(card='K')
    dealer.hand.add_card(card='J')
    assert player_initial_decision(
        player=player,
        count=1,
        insurance_count=None,
        rules=rules,
        dealer=dealer,
        playing_strategy=playing_strategy
    ) is None
    assert player.get_first_hand().status == HandStatus.SETTLED
    assert player.bankroll == 1050
    assert player.stats.stats[StatsKey(count=1, category=StatsCategory.HANDS_WON)] == 1
    assert player.stats.stats[StatsKey(count=1, category=StatsCategory.AMOUNT_EARNED)] == 30


def test_player_initial_decision_late_surrender(player, dealer):
    """
    Tests the player_initial_decision function when the player has
    the option to late surrender and does.

    """
    rules = Rules(min_bet=10, max_bet=500, late_surrender=True)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    player.get_first_hand().add_card(card='K')
    player.get_first_hand().add_card(card='5')
    player.get_first_hand().add_to_total_bet(amount=50)
    dealer.hand.add_card(card='K')
    dealer.hand.add_card(card='J')
    assert player_initial_decision(
        player=player,
        count=None,
        insurance_count=None,
        rules=rules,
        dealer=dealer,
        playing_strategy=playing_strategy
    ) is None
    assert player.get_first_hand().status == HandStatus.SETTLED
    assert player.bankroll == 1025
    assert player.stats.stats[StatsKey(count=None, category=StatsCategory.HANDS_LOST)] == 1
    assert player.stats.stats[StatsKey(count=None, category=StatsCategory.AMOUNT_EARNED)] == -25


def test_player_initial_decision_no_late_surrender(player, dealer):
    """
    Tests the player_initial_decision function when the player does
    not have the option to late surrender.

    """
    rules = Rules(min_bet=10, max_bet=500, late_surrender=False)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    player.get_first_hand().add_card(card='K')
    player.get_first_hand().add_card(card='5')
    player.get_first_hand().add_to_total_bet(amount=50)
    dealer.hand.add_card(card='K')
    dealer.hand.add_card(card='J')
    assert player_initial_decision(
        player=player,
        count=None,
        insurance_count=None,
        rules=rules,
        dealer=dealer,
        playing_strategy=playing_strategy
    ) == 'Rh'
    assert player.get_first_hand().status == HandStatus.IN_PLAY


def test_player_plays_hands_settled(player, shoe, dealer):
    """
    Tests the player_plays_hands function when the hand
    is already settled.

    """
    rules = Rules(min_bet=10, max_bet=500, late_surrender=True)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    player.get_first_hand().add_card(card='K')
    player.get_first_hand().add_card(card='5')
    player.get_first_hand().add_to_total_bet(amount=50)
    dealer.hand.add_card(card='K')
    dealer.hand.add_card(card='J')
    player_plays_hands(
        player=player,
        shoe=shoe,
        count=None,
        insurance_count=None,
        dealer=dealer,
        rules=rules,
        playing_strategy=playing_strategy
    )
    assert player.get_first_hand().status == HandStatus.SETTLED


def test_player_plays_hands_split(shoe, dealer, player, rules):
    """
    Tests the player_plays_hands function when the player is dealt
    a pair and the hand is split.

    """
    playing_strategy = PlayingStrategy(s17=rules.s17)
    player.get_first_hand().add_card(card='8')
    player.get_first_hand().add_card(card='8')
    player.get_first_hand().add_to_total_bet(amount=10)
    dealer.hand.add_card(card='6')
    dealer.hand.add_card(card='6')
    player_plays_hands(
        player=player,
        shoe=shoe,
        count=None,
        insurance_count=None,
        dealer=dealer,
        rules=rules,
        playing_strategy=playing_strategy
    )
    assert player.get_first_hand().cards == ['8', 'A']
    assert player.get_first_hand().status == HandStatus.SHOWDOWN
    assert player.hands[1].cards == ['8', 'K']
    assert player.hands[1].status == HandStatus.SHOWDOWN
    assert player.bankroll == 990
    assert player.stats.stats[StatsKey(count=None, category=StatsCategory.AMOUNT_BET)] == 10


def test_player_plays_hands_split_insufficient_bankroll(shoe, dealer, rules):
    """
    Tests the player_plays_hands function when the player is dealt
    a pair and the player has insufficient bankroll to split a hand.

    """
    playing_strategy = PlayingStrategy(s17=rules.s17)
    player = Player(name='Player 1', min_bet=10, bankroll=10)
    player.get_first_hand().add_card(card='6')
    player.get_first_hand().add_card(card='6')
    player.get_first_hand().add_to_total_bet(amount=20)
    dealer.hand.add_card(card='7')
    dealer.hand.add_card(card='7')
    shoe._cards = ['J', 'Q', '7', '6', '5', 'A']
    player_plays_hands(
        player=player,
        shoe=shoe,
        count=None,
        insurance_count=None,
        dealer=dealer,
        rules=rules,
        playing_strategy=playing_strategy
    )
    assert player.get_first_hand().cards == ['6', '6', 'A', '5']
    assert player.get_first_hand().status == HandStatus.SHOWDOWN
    assert player.get_first_hand().total_bet > player.bankroll


def test_player_plays_hands_resplit_aces(player, shoe, dealer):
    """
    Tests the player_plays_hands function when the player is dealt
    a pair of aces and aces can be re-split.

    """
    rules = Rules(min_bet=10, max_bet=500, resplit_aces=True)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    player.get_first_hand().add_card(card='A')
    player.get_first_hand().add_card(card='A')
    player.get_first_hand().add_to_total_bet(amount=10)
    dealer.hand.add_card(card='6')
    dealer.hand.add_card(card='6')
    player_plays_hands(
        player=player,
        shoe=shoe,
        count=None,
        insurance_count=None,
        dealer=dealer,
        rules=rules,
        playing_strategy=playing_strategy
    )
    assert player.get_first_hand().cards == ['A', 'K']
    assert player.get_first_hand().status == HandStatus.SHOWDOWN
    assert player.hands[1].cards == ['A', 'Q']
    assert player.hands[1].status == HandStatus.SHOWDOWN
    assert player.hands[2].cards == ['A', 'J']
    assert player.hands[2].status == HandStatus.SHOWDOWN
    assert player.bankroll == 980
    assert player.stats.stats[StatsKey(count=None, category=StatsCategory.AMOUNT_BET)] == 20


def test_player_plays_hands_resplit_aces_insufficient_bankroll(shoe, dealer):
    """
    Tests the player_plays_hands function when the player is dealt
    a pair of aces and aces can be re-split but the player
    has insufficient bankroll to split their hand again.

    """
    rules = Rules(min_bet=10, max_bet=500, resplit_aces=True)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    player = Player(name='Player 1', min_bet=10, bankroll=10)
    player.get_first_hand().add_card(card='A')
    player.get_first_hand().add_card(card='A')
    player.get_first_hand().add_to_total_bet(amount=10)
    dealer.hand.add_card(card='5')
    dealer.hand.add_card(card='5')
    shoe._cards = ['4', '3', '2', 'Q', 'K', 'A']
    player_plays_hands(
        player=player,
        shoe=shoe,
        count=None,
        insurance_count=None,
        dealer=dealer,
        rules=rules,
        playing_strategy=playing_strategy
    )
    assert player.get_first_hand().cards == ['A', 'A', 'K']
    assert player.get_first_hand().status == HandStatus.SHOWDOWN
    assert player.hands[1].cards == ['A', 'Q']
    assert player.hands[1].status == HandStatus.SHOWDOWN
    assert player.bankroll == 0
    assert player.stats.stats[StatsKey(count=None, category=StatsCategory.AMOUNT_BET)] == 10


def test_player_plays_hands_resplit_aces_max_hands(player, shoe, dealer):
    """
    Tests the player_plays_hands function when the player is dealt
    a pair of aces and aces can be re-split but the player reaches
    the max hands limit and is unable to split their hand again.

    """
    rules = Rules(min_bet=10, max_bet=500, resplit_aces=True, max_hands=3)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    player.get_first_hand().add_card(card='A')
    player.get_first_hand().add_card(card='A')
    player.get_first_hand().add_to_total_bet(amount=10)
    dealer.hand.add_card(card='5')
    dealer.hand.add_card(card='5')
    shoe._cards = ['4', '3', 'A', '3', '2', 'A']
    player_plays_hands(
        player=player,
        shoe=shoe,
        count=None,
        insurance_count=None,
        dealer=dealer,
        rules=rules,
        playing_strategy=playing_strategy
    )
    assert player.get_first_hand().cards == ['A', '2']
    assert player.get_first_hand().status == HandStatus.SHOWDOWN
    assert player.hands[1].cards == ['A', '3']
    assert player.hands[1].status == HandStatus.SHOWDOWN
    assert player.hands[2].cards == ['A', 'A']
    assert player.hands[2].status == HandStatus.SHOWDOWN
    assert player.bankroll == 980
    assert player.stats.stats[StatsKey(count=None, category=StatsCategory.AMOUNT_BET)] == 20


def test_player_plays_hands_resplit_aces_not_allowed(player, shoe, dealer):
    """
    Tests the player_plays_hands function when the player is dealt
    a pair of aces and aces cannot be re-split.

    """
    rules = Rules(min_bet=10, max_bet=500, resplit_aces=False)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    player.get_first_hand().add_card(card='A')
    player.get_first_hand().add_card(card='A')
    player.get_first_hand().add_to_total_bet(amount=10)
    dealer.hand.add_card(card='6')
    dealer.hand.add_card(card='6')
    player_plays_hands(
        player=player,
        shoe=shoe,
        count=None,
        insurance_count=None,
        dealer=dealer,
        rules=rules,
        playing_strategy=playing_strategy
    )
    assert player.get_first_hand().cards == ['A', 'A']
    assert player.get_first_hand().status == HandStatus.SHOWDOWN
    assert player.hands[1].cards == ['A', 'K']
    assert player.hands[1].status == HandStatus.SHOWDOWN
    assert player.bankroll == 990
    assert player.stats.stats[StatsKey(count=None, category=StatsCategory.AMOUNT_BET)] == 10


def test_player_plays_hands_double_down(player, dealer, shoe):
    """
    Tests the player_plays_hands function when the player
    can double down.

    """
    rules = Rules(min_bet=10, max_bet=500, double_down=True)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    player.get_first_hand().add_card(card='5')
    player.get_first_hand().add_card(card='6')
    player.get_first_hand().add_to_total_bet(amount=10)
    dealer.hand.add_card(card='2')
    dealer.hand.add_card(card='3')
    player_plays_hands(
        player=player,
        shoe=shoe,
        count=None,
        insurance_count=None,
        dealer=dealer,
        rules=rules,
        playing_strategy=playing_strategy
    )
    assert player.get_first_hand().cards == ['5', '6', 'A']
    assert player.get_first_hand().total_bet == 20
    assert player.get_first_hand().status == HandStatus.SHOWDOWN
    assert player.bankroll == 990
    assert player.stats.stats[StatsKey(count=None, category=StatsCategory.AMOUNT_BET)] == 10


def test_player_plays_hands_double_down_not_allowed(player, dealer, shoe):
    """
    Tests the player_plays_hands function when the player
    cannot double down.

    """
    rules = Rules(min_bet=10, max_bet=500, double_down=False)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    player.get_first_hand().add_card(card='5')
    player.get_first_hand().add_card(card='6')
    player.get_first_hand().add_to_total_bet(amount=10)
    dealer.hand.add_card(card='2')
    dealer.hand.add_card(card='3')
    player_plays_hands(
        player=player,
        shoe=shoe,
        count=None,
        insurance_count=None,
        dealer=dealer,
        rules=rules,
        playing_strategy=playing_strategy
    )
    assert player.get_first_hand().cards == ['5', '6', 'A', 'K']
    assert player.get_first_hand().total_bet == 10
    assert player.get_first_hand().status == HandStatus.SETTLED
    assert player.bankroll == 1000
    assert player.stats.stats[StatsKey(count=None, category=StatsCategory.AMOUNT_BET)] == 0


def test_player_plays_hands_double_down_insufficient_bankroll(player, dealer, shoe):
    """
    Tests the player_plays_hands function when the player
    has insufficient bankroll to double down.

    """
    rules = Rules(min_bet=10, max_bet=500, double_down=True)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    player.get_first_hand().add_card(card='5')
    player.get_first_hand().add_card(card='6')
    player.get_first_hand().add_to_total_bet(amount=10)
    player.adjust_bankroll(amount=-1000)
    dealer.hand.add_card(card='2')
    dealer.hand.add_card(card='3')
    player_plays_hands(
        player=player,
        shoe=shoe,
        count=None,
        insurance_count=None,
        dealer=dealer,
        rules=rules,
        playing_strategy=playing_strategy
    )
    assert player.get_first_hand().cards == ['5', '6', 'A', 'K']
    assert player.get_first_hand().total_bet == 10
    assert player.get_first_hand().status == HandStatus.SETTLED
    assert player.bankroll == 0
    assert player.stats.stats[StatsKey(count=None, category=StatsCategory.AMOUNT_BET)] == 0


def test_player_plays_hands_double_after_split(player, dealer, shoe):
    """
    Tests the player_plays_hands function when the player
    doubles after splitting.

    """
    rules = Rules(min_bet=10, max_bet=500, double_down=True, double_after_split=True)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    player.get_first_hand().add_card(card='2')
    player.get_first_hand().add_card(card='2')
    player.get_first_hand().add_to_total_bet(amount=10)
    player.adjust_bankroll(amount=-970)
    dealer.hand.add_card(card='2')
    dealer.hand.add_card(card='3')
    shoe._cards = ['K', 'A', 'J', '8', 'Q', '8']
    player_plays_hands(
        player=player,
        shoe=shoe,
        count=None,
        insurance_count=None,
        dealer=dealer,
        rules=rules,
        playing_strategy=playing_strategy
    )
    assert player.get_first_hand().cards == ['2', '8', 'Q']
    assert player.get_first_hand().total_bet == 20
    assert player.get_first_hand().status == HandStatus.SHOWDOWN
    assert player.hands[1].cards == ['2', '8', 'J']
    assert player.hands[1].total_bet == 20
    assert player.hands[1].status == HandStatus.SHOWDOWN
    assert player.stats.stats[StatsKey(count=None, category=StatsCategory.AMOUNT_BET)] == 30


def test_player_plays_hands_double_after_split_not_allowed(player, dealer, shoe):
    """
    Tests the player_plays_hands function when the player
    is not allowed to double after splitting.

    """
    rules = Rules(min_bet=10, max_bet=500, double_down=True, double_after_split=False)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    player.get_first_hand().add_card(card='2')
    player.get_first_hand().add_card(card='2')
    player.get_first_hand().add_to_total_bet(amount=10)
    dealer.hand.add_card(card='2')
    dealer.hand.add_card(card='3')
    player_plays_hands(
        player=player,
        shoe=shoe,
        count=None,
        insurance_count=None,
        dealer=dealer,
        rules=rules,
        playing_strategy=playing_strategy
    )
    assert player.get_first_hand().cards == ['2', '2', 'A', 'K']
    assert player.get_first_hand().total_bet == 10
    assert player.get_first_hand().status == HandStatus.SHOWDOWN
    assert player.stats.stats[StatsKey(count=None, category=StatsCategory.AMOUNT_BET)] == 0


def test_player_plays_hands_double_after_split_insufficient_bankroll(player, dealer, shoe):
    """
    Tests the player_plays_hands function when the player
    has insufficient bankroll to double after splitting.

    """
    rules = Rules(min_bet=10, max_bet=500, double_down=True, double_after_split=True)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    player.get_first_hand().add_card(card='2')
    player.get_first_hand().add_card(card='2')
    player.get_first_hand().add_to_total_bet(amount=10)
    player.adjust_bankroll(amount=-980)
    dealer.hand.add_card(card='2')
    dealer.hand.add_card(card='3')
    player_plays_hands(
        player=player,
        shoe=shoe,
        count=None,
        insurance_count=None,
        dealer=dealer,
        rules=rules,
        playing_strategy=playing_strategy
    )
    assert player.get_first_hand().cards == ['2', '2', 'A', 'K']
    assert player.get_first_hand().total_bet == 10
    assert player.get_first_hand().total_bet * 3 > player.bankroll
    assert player.get_first_hand().status == HandStatus.SHOWDOWN
    assert player.stats.stats[StatsKey(count=None, category=StatsCategory.AMOUNT_BET)] == 0


def test_player_plays_hands_stand(player, dealer, shoe, rules):
    """Tests the player_plays_hands function when the player stands."""
    playing_strategy = PlayingStrategy(s17=rules.s17)
    player.get_first_hand().add_card(card='6')
    player.get_first_hand().add_card(card='7')
    player.get_first_hand().add_to_total_bet(amount=10)
    dealer.hand.add_card(card='6')
    dealer.hand.add_card(card='6')
    player_plays_hands(
        player=player,
        shoe=shoe,
        count=None,
        insurance_count=None,
        dealer=dealer,
        rules=rules,
        playing_strategy=playing_strategy
    )
    assert player.get_first_hand().cards == ['6', '7']
    assert player.get_first_hand().status == HandStatus.SHOWDOWN


def test_player_plays_hands_busted(player, dealer, shoe, rules):
    """Tests the player_plays_hands function when the hand is busted."""
    playing_strategy = PlayingStrategy(s17=rules.s17)
    player.get_first_hand().add_card(card='6')
    player.get_first_hand().add_card(card='7')
    player.get_first_hand().add_to_total_bet(amount=10)
    dealer.hand.add_card(card='10')
    dealer.hand.add_card(card='Q')
    player_plays_hands(
        player=player,
        shoe=shoe,
        count=None,
        insurance_count=None,
        dealer=dealer,
        rules=rules,
        playing_strategy=playing_strategy
    )
    assert player.get_first_hand().cards == ['6', '7', 'A', 'K']
    assert player.get_first_hand().status == HandStatus.SETTLED
    assert player.get_first_hand().total > 21


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
def test_dealer_plays_hand(shoe, dealer, test_hole_card, test_up_card, test_s17, expected):
    """Tests the dealer_plays_hand function."""
    rules = Rules(min_bet=10, max_bet=500, s17=test_s17)
    dealer.hand.add_card(card=test_hole_card)
    dealer.hand.add_card(card=test_up_card)
    dealer_plays_hand(shoe=shoe, dealer=dealer, rules=rules)
    assert dealer.hand.total == expected


def test_dealer_turn(player, table):
    """Tests the dealer_turn function."""
    table.add_player(player=player)
    player.get_first_hand().status = HandStatus.SETTLED
    assert not dealer_turn(table=table)
    player.get_first_hand().status = HandStatus.SHOWDOWN
    assert dealer_turn(table=table)


def test_all_hands_busted_true(player, table):
    """
    Tests the all_hands_busted function
    when all hands at the table are busted.

    """
    table.add_player(player=player)
    player.get_first_hand().add_card(card='4')
    player.get_first_hand().add_card(card='J')
    player.get_first_hand().add_card(card='K')
    assert player.get_first_hand().is_busted
    assert all_hands_busted(table=table)


def test_all_hands_busted_false(player, table):
    """
    Tests the all_hands_busted function
    when not all hands at the table are busted.

    """
    table.add_player(player=player)
    player.get_first_hand().add_card(card='J')
    player.get_first_hand().add_card(card='K')
    assert not player.get_first_hand().is_busted
    assert not all_hands_busted(table=table)


def test_compare_hands_win_total(player, dealer):
    """
    Tests the compare_hands function when the player wins
    based on total.

    """
    player.get_first_hand().status = HandStatus.SHOWDOWN
    player.get_first_hand().add_card(card='J')
    player.get_first_hand().add_card(card='K')
    player.get_first_hand().add_to_total_bet(amount=10)
    dealer.hand.add_card(card='10')
    dealer.hand.add_card(card='8')
    compare_hands(player=player, dealer=dealer, count=3)
    assert player.get_first_hand().status == HandStatus.SETTLED
    assert player.bankroll == 1020
    assert player.stats.stats[StatsKey(count=3, category=StatsCategory.HANDS_WON)] == 1
    assert player.stats.stats[StatsKey(count=3, category=StatsCategory.AMOUNT_EARNED)] == 10


def test_compare_hands_win_dealer_busts(player, dealer):
    """
    Tests the compare_hands function when the player wins
    and the dealer busts.

    """
    player.get_first_hand().status = HandStatus.SHOWDOWN
    player.get_first_hand().add_card(card='J')
    player.get_first_hand().add_card(card='K')
    player.get_first_hand().add_to_total_bet(amount=20)
    dealer.hand.add_card(card='10')
    dealer.hand.add_card(card='6')
    dealer.hand.add_card(card='K')
    compare_hands(player=player, dealer=dealer, count=1)
    assert player.get_first_hand().status == HandStatus.SETTLED
    assert player.bankroll == 1040
    assert player.stats.stats[StatsKey(count=1, category=StatsCategory.HANDS_WON)] == 1
    assert player.stats.stats[StatsKey(count=1, category=StatsCategory.AMOUNT_EARNED)] == 20


def test_compare_hands_push(player, dealer):
    """
    Tests the compare_hands function when the player and
    dealer push.

    """
    player.get_first_hand().status = HandStatus.SHOWDOWN
    player.get_first_hand().add_card(card='J')
    player.get_first_hand().add_card(card='K')
    player.get_first_hand().add_to_total_bet(amount=10)
    dealer.hand.add_card(card='10')
    dealer.hand.add_card(card='Q')
    compare_hands(player=player, dealer=dealer, count=None)
    assert player.get_first_hand().status == HandStatus.SETTLED
    assert player.bankroll == 1010
    assert player.stats.stats[StatsKey(count=None, category=StatsCategory.HANDS_PUSHED)] == 1


def test_compare_hands_loss_total(player, dealer):
    """
    Tests the compare_hands function when the player loses
    based on total.

    """
    player.get_first_hand().status = HandStatus.SHOWDOWN
    player.get_first_hand().add_card(card='6')
    player.get_first_hand().add_card(card='K')
    player.get_first_hand().add_to_total_bet(amount=20)
    dealer.hand.add_card(card='10')
    dealer.hand.add_card(card='8')
    compare_hands(player=player, dealer=dealer, count=-2)
    assert player.get_first_hand().status == HandStatus.SETTLED
    assert player.bankroll == 1000
    assert player.stats.stats[StatsKey(count=-2, category=StatsCategory.HANDS_LOST)] == 1
    assert player.stats.stats[StatsKey(count=-2, category=StatsCategory.AMOUNT_EARNED)] == -20


def test_clear_hands(dealer_with_hand, player, rules):
    """Test the clear_hands function."""
    table = Table(rules=rules)
    table.add_player(player=player)
    player.get_first_hand().add_card(card='A')
    player.get_first_hand().add_card(card='A')
    split_hand = player.get_first_hand().split()
    player.hands.append(split_hand)
    player.get_first_hand().add_card(card='2')
    player.hands[1].add_card(card='6')
    assert dealer_with_hand.hand.cards == ['8', '6']
    assert player.get_first_hand().cards == ['A', '2']
    assert player.hands[1].cards == ['A', '6']
    clear_hands(dealer=dealer_with_hand, table=table)
    assert not dealer_with_hand.hand.cards
    assert not player.get_first_hand().cards
    assert len(player.hands) == 1


def test_play_round_back_counters_added(shoe, dealer, rules, card_counter_balanced, back_counter):
    """Tests the play_round function when back counters are added."""
    table = Table(rules=rules)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    table.add_player(player=card_counter_balanced)
    table.add_player(player=back_counter)
    shoe.add_to_seen_cards(card='2')
    shoe.add_to_seen_cards(card='2')
    shoe.add_to_seen_cards(card='2')
    play_round(table=table, dealer=dealer, shoe=shoe, rules=rules, playing_strategy=playing_strategy)
    assert card_counter_balanced.stats.stats[StatsKey(count=3, category=StatsCategory.AMOUNT_BET)] == 40
    assert card_counter_balanced.stats.stats[StatsKey(count=3, category=StatsCategory.AMOUNT_EARNED)] == 60
    assert card_counter_balanced.stats.stats[StatsKey(count=3, category=StatsCategory.HANDS_WON)] == 1
    assert back_counter.stats.stats[StatsKey(count=3, category=StatsCategory.AMOUNT_BET)] == 40
    assert back_counter.stats.stats[StatsKey(count=3, category=StatsCategory.AMOUNT_EARNED)] == 40
    assert back_counter.stats.stats[StatsKey(count=3, category=StatsCategory.HANDS_WON)] == 1


def test_play_round_back_counters_removed(shoe, dealer, rules, card_counter_balanced, back_counter):
    """Tests the play_round function when back counters are removed."""
    table = Table(rules=rules)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    table.add_player(player=card_counter_balanced)
    table.add_player(player=back_counter)
    shoe.add_to_seen_cards(card='2')
    shoe.add_to_seen_cards(card='2')
    shoe.add_to_seen_cards(card='2')
    add_back_counters(table=table, count_dict=get_count(table=table, shoe=shoe))
    assert len(table.players) == 2
    shoe.add_to_seen_cards(card='K')
    shoe.add_to_seen_cards(card='K')
    shoe.add_to_seen_cards(card='K')
    play_round(table=table, dealer=dealer, shoe=shoe, rules=rules, playing_strategy=playing_strategy)
    assert card_counter_balanced.stats.stats[StatsKey(count=0, category=StatsCategory.AMOUNT_BET)] == 10
    assert card_counter_balanced.stats.stats[StatsKey(count=0, category=StatsCategory.AMOUNT_EARNED)] == 15
    assert card_counter_balanced.stats.stats[StatsKey(count=0, category=StatsCategory.HANDS_WON)] == 1


def test_play_round_insufficient_funds(dealer, player, shoe, rules):
    """Tests the play_round function when a player has insufficient funds."""
    table = Table(rules=rules)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    table.add_player(player=player)
    player.adjust_bankroll(amount=-1000)
    assert player.bankroll == 0
    play_round(table=table, dealer=dealer, shoe=shoe, rules=rules, playing_strategy=playing_strategy)
    assert len(table.players) == 0
    assert shoe.cards[-1] == 'A'


def test_play_round_insurance_win(dealer, shoe, card_counter_unbalanced):
    """
    Tests the play_round function when a player
    purchases insurance and the dealer has blackjack.

    """
    rules = Rules(min_bet=10, max_bet=500, insurance=True)
    table = Table(rules=rules)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    table.add_player(player=card_counter_unbalanced)
    shoe._cards = ['A', '5', 'K', 'K']
    shoe.add_to_seen_cards(card='2')
    shoe.add_to_seen_cards(card='2')
    shoe.add_to_seen_cards(card='2')
    play_round(table=table, dealer=dealer, shoe=shoe, rules=rules, playing_strategy=playing_strategy)
    assert card_counter_unbalanced.stats.stats[StatsKey(count=3, category=StatsCategory.AMOUNT_BET)] == 40
    assert card_counter_unbalanced.stats.stats[StatsKey(count=3, category=StatsCategory.AMOUNT_EARNED)] == -40
    assert card_counter_unbalanced.stats.stats[StatsKey(count=3, category=StatsCategory.HANDS_LOST)] == 1
    assert card_counter_unbalanced.stats.stats[StatsKey(count=2, category=StatsCategory.INSURANCE_AMOUNT_BET)] == 20
    assert card_counter_unbalanced.stats.stats[StatsKey(count=2, category=StatsCategory.INSURANCE_AMOUNT_EARNED)] == 20


def test_play_round_insurance_loss(dealer, shoe, card_counter_unbalanced):
    """
    Tests the play_round function when a player
    purchases insurance and the dealer does not have blackjack.

    """
    rules = Rules(min_bet=10, max_bet=500, insurance=True)
    table = Table(rules=rules)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    table.add_player(player=card_counter_unbalanced)
    shoe._cards = ['5', 'A', '5', '7', 'K']
    shoe.add_to_seen_cards(card='2')
    shoe.add_to_seen_cards(card='2')
    shoe.add_to_seen_cards(card='2')
    play_round(table=table, dealer=dealer, shoe=shoe, rules=rules, playing_strategy=playing_strategy)
    assert card_counter_unbalanced.stats.stats[StatsKey(count=3, category=StatsCategory.AMOUNT_BET)] == 40
    assert card_counter_unbalanced.stats.stats[StatsKey(count=3, category=StatsCategory.AMOUNT_EARNED)] == 40
    assert card_counter_unbalanced.stats.stats[StatsKey(count=3, category=StatsCategory.HANDS_WON)] == 1
    assert card_counter_unbalanced.stats.stats[StatsKey(count=2, category=StatsCategory.INSURANCE_AMOUNT_BET)] == 20
    assert card_counter_unbalanced.stats.stats[StatsKey(count=2, category=StatsCategory.INSURANCE_AMOUNT_EARNED)] == -20


def test_play_round_player_blackjack(player, dealer, shoe, rules):
    """Tests the play_round function when a player has a blackjack."""
    table = Table(rules=rules)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    table.add_player(player=player)
    shoe._cards = ['K', 'K', '9', 'A']
    play_round(table=table, dealer=dealer, shoe=shoe, rules=rules, playing_strategy=playing_strategy)
    assert player.stats.stats[StatsKey(count=None, category=StatsCategory.AMOUNT_BET)] == 10
    assert player.stats.stats[StatsKey(count=None, category=StatsCategory.AMOUNT_EARNED)] == 15
    assert player.stats.stats[StatsKey(count=None, category=StatsCategory.HANDS_WON)] == 1


def test_play_round_dealer_blackjack(player, dealer, shoe, rules):
    """Tests the play_round function when the dealer has a blackjack."""
    table = Table(rules=rules)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    table.add_player(player=player)
    shoe._cards = ['K', '9', 'A', 'A']
    play_round(table=table, dealer=dealer, shoe=shoe, rules=rules, playing_strategy=playing_strategy)
    assert player.stats.stats[StatsKey(count=None, category=StatsCategory.AMOUNT_BET)] == 10
    assert player.stats.stats[StatsKey(count=None, category=StatsCategory.AMOUNT_EARNED)] == -10
    assert player.stats.stats[StatsKey(count=None, category=StatsCategory.HANDS_LOST)] == 1


def test_play_round_player_dealer_blackjack(player, dealer, shoe, rules):
    """
    Tests the play_round function when a player
    and the dealer have a blackjack.

    """
    table = Table(rules=rules)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    table.add_player(player=player)
    shoe._cards = ['K', 'K', 'A', 'A']
    play_round(table=table, dealer=dealer, shoe=shoe, rules=rules, playing_strategy=playing_strategy)
    assert player.stats.stats[StatsKey(count=None, category=StatsCategory.AMOUNT_BET)] == 10
    assert player.stats.stats[StatsKey(count=None, category=StatsCategory.AMOUNT_EARNED)] == 0
    assert player.stats.stats[StatsKey(count=None, category=StatsCategory.HANDS_PUSHED)] == 1


def test_play_round_all_hands_busted_dealer_shows_hole_card(player, dealer, shoe):
    """
    Tests the play_round function when all hands
    are busted and the dealer shows their hole card.

    """
    rules = Rules(min_bet=10, max_bet=500, dealer_shows_hole_card=True)
    table = Table(rules=rules)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    table.add_player(player=player)
    shoe._cards = ['10', 'J', 'Q', 'K', '4']
    play_round(table=table, dealer=dealer, shoe=shoe, rules=rules, playing_strategy=playing_strategy)
    assert shoe.seen_cards['4'] == 1
    assert shoe.seen_cards['10-J-Q-K'] == 4


def test_play_round_all_hands_busted_dealer_does_not_show_hole_card(player, dealer, shoe):
    """
    Tests the play_round function when all hands
    are busted and the dealer does not show their hole card.

    """
    rules = Rules(min_bet=10, max_bet=500, dealer_shows_hole_card=False)
    table = Table(rules=rules)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    table.add_player(player=player)
    shoe._cards = ['10', 'J', 'Q', 'K', '4']
    play_round(table=table, dealer=dealer, shoe=shoe, rules=rules, playing_strategy=playing_strategy)
    assert shoe.seen_cards['4'] == 1
    assert shoe.seen_cards['10-J-Q-K'] == 3


@pytest.mark.parametrize(
    'test_dealer_shows_hole_card',
    [
        (True),
        (False)
     ]
)
def test_play_round_all_hands_do_not_bust(player, dealer, shoe, test_dealer_shows_hole_card):
    """
    Tests the play_round function when there are
    hands that are not busted.

    """
    rules = Rules(min_bet=10, max_bet=500, dealer_shows_hole_card=test_dealer_shows_hole_card)
    table = Table(rules=rules)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    table.add_player(player=player)
    shoe._cards = ['10', 'J', 'Q', 'K']
    play_round(table=table, dealer=dealer, shoe=shoe, rules=rules, playing_strategy=playing_strategy)
    assert shoe.seen_cards['10-J-Q-K'] == 4


def test_play_round_clear_hands(player, dealer, shoe, rules):
    """
    Tests the play_round function to check
    that the hands are properly cleared after
    each round.

    """
    table = Table(rules=rules)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    table.add_player(player=player)
    play_round(table=table, dealer=dealer, shoe=shoe, rules=rules, playing_strategy=playing_strategy)
    assert not dealer.hand.cards
    assert not player.get_first_hand().cards
