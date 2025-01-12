import pytest
from blackjack.enums import StatsCategory
from blackjack.gameplay import get_count, get_insurance_count
from blackjack.gameplay import initialize_hands
from blackjack.gameplay import player_initial_decision, player_plays_hands
from blackjack.gameplay import dealer_turn, dealer_plays_hand, compare_hands
from blackjack.gameplay import clear_hands, play_round
from blackjack.hand import HandStatus
from blackjack.player import Player
from blackjack.playing_strategy import PlayingStrategy
from blackjack.shoe import Shoe
from blackjack.rules import Rules
from blackjack.table import Table


def test_get_count(player, table, card_counter_unbalanced, back_counter):
    """Tests the get_count function."""
    shoe = Shoe(shoe_size=6)
    # burn an entire 52 card deck and make them all visible 'K'
    # exactly 5 decks remain
    for _ in range(0, 52):
        shoe.burn_card()
        shoe.add_to_seen_cards(card='K')
    table.add_player(player=player)
    table.add_player(player=card_counter_unbalanced)
    table.add_player(player=back_counter)
    count_dict = get_count(table=table, shoe=shoe)
    assert player not in count_dict
    assert count_dict[card_counter_unbalanced] == -72
    assert count_dict[back_counter] == -10


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
    insurance_count_dict = get_insurance_count(players=table.players, shoe=shoe)
    assert player not in insurance_count_dict
    assert back_counter not in insurance_count_dict
    assert card_counter_balanced not in insurance_count_dict
    assert insurance_count_dict[card_counter_unbalanced] == -2


def test_initialize_hands(player, dealer, shoe, table):
    """Tests the initialize_hands function."""
    table.add_player(player=player)
    initialize_hands(dealer=dealer, players=table.players, shoe=shoe)
    assert player.get_first_hand().cards == ['A', 'Q']
    assert dealer.hand.cards == ['K', 'J']
    assert shoe.seen_cards['A'] == 1
    assert shoe.seen_cards['10-J-Q-K'] == 2


def test_player_initial_decision_insufficient_bankroll_insurance(card_counter_unbalanced, dealer):
    """
    Tests the player_initial_decision function when the player wants to buy
    insurance but has insufficient funds to purchase it.

    """
    rules = Rules(min_bet=10, max_bet=500)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    card_counter_unbalanced_hand = card_counter_unbalanced.get_first_hand()
    card_counter_unbalanced_hand.add_card(card='5')
    card_counter_unbalanced_hand.add_card(card='6')
    dealer.hand.add_card(card='K')
    dealer.hand.add_card(card='A')
    card_counter_unbalanced._bankroll = 10
    assert player_initial_decision(
        player=card_counter_unbalanced,
        player_stats=card_counter_unbalanced.stats.stats,
        placed_bet=10,
        count=3,
        insurance_count=4,
        dealer_hand_is_blackjack=dealer.hand.is_blackjack,
        dealer_up_card=dealer.up_card,
        rules=rules,
        playing_strategy=playing_strategy
    ) is None
    assert card_counter_unbalanced.bankroll == 0
    assert card_counter_unbalanced_hand.status == HandStatus.SETTLED
    assert card_counter_unbalanced.stats.stats[(3, StatsCategory.TOTAL_HANDS_PLAYED)] == 1
    assert card_counter_unbalanced.stats.stats[(3, StatsCategory.PLAYER_HANDS_LOST)] == 1
    assert card_counter_unbalanced.stats.stats[(3, StatsCategory.DEALER_BLACKJACKS)] == 1
    assert card_counter_unbalanced.stats.stats[(3, StatsCategory.AMOUNT_BET)] == 10
    assert card_counter_unbalanced.stats.stats[(3, StatsCategory.NET_WINNINGS)] == -10
    assert card_counter_unbalanced.stats.stats[(4, StatsCategory.INSURANCE_AMOUNT_BET)] == 0
    assert card_counter_unbalanced.stats.stats[(4, StatsCategory.INSURANCE_NET_WINNINGS)] == 0


def test_player_initial_decision_insurance_dealer_blackjack(card_counter_unbalanced, dealer):
    """
    Tests the player_initial_decision function when the player buys
    insurance and the dealer has blackjack.

    """
    rules = Rules(min_bet=10, max_bet=500)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    card_counter_unbalanced_hand = card_counter_unbalanced.get_first_hand()
    card_counter_unbalanced_hand.add_card(card='5')
    card_counter_unbalanced_hand.add_card(card='6')
    dealer.hand.add_card(card='K')
    dealer.hand.add_card(card='A')
    assert card_counter_unbalanced.bankroll == 1000
    assert player_initial_decision(
        player=card_counter_unbalanced,
        player_stats=card_counter_unbalanced.stats.stats,
        placed_bet=10,
        count=3,
        insurance_count=4,
        dealer_hand_is_blackjack=dealer.hand.is_blackjack,
        dealer_up_card=dealer.up_card,
        rules=rules,
        playing_strategy=playing_strategy
    ) is None
    assert card_counter_unbalanced.bankroll == 995
    assert card_counter_unbalanced_hand.status == HandStatus.SETTLED
    assert card_counter_unbalanced.stats.stats[(3, StatsCategory.TOTAL_HANDS_PLAYED)] == 1
    assert card_counter_unbalanced.stats.stats[(3, StatsCategory.PLAYER_HANDS_LOST)] == 1
    assert card_counter_unbalanced.stats.stats[(3, StatsCategory.DEALER_BLACKJACKS)] == 1
    assert card_counter_unbalanced.stats.stats[(3, StatsCategory.AMOUNT_BET)] == 10
    assert card_counter_unbalanced.stats.stats[(3, StatsCategory.NET_WINNINGS)] == -10
    assert card_counter_unbalanced.stats.stats[(4, StatsCategory.INSURANCE_AMOUNT_BET)] == 5
    assert card_counter_unbalanced.stats.stats[(4, StatsCategory.INSURANCE_NET_WINNINGS)] == 5


def test_player_initial_decision_insurance_no_dealer_blackjack(card_counter_unbalanced, dealer):
    """
    Tests the player_initial_decision function when the player buys insurance
    and the dealer does not have blackjack.

    """
    rules = Rules(min_bet=10, max_bet=500)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    card_counter_unbalanced_hand = card_counter_unbalanced.get_first_hand()
    card_counter_unbalanced_hand.add_card(card='2')
    card_counter_unbalanced_hand.add_card(card='2')
    dealer.hand.add_card(card='6')
    dealer.hand.add_card(card='A')
    assert card_counter_unbalanced.bankroll == 1000
    assert player_initial_decision(
        player=card_counter_unbalanced,
        player_stats=card_counter_unbalanced.stats.stats,
        placed_bet=10,
        count=3,
        insurance_count=4,
        dealer_hand_is_blackjack=dealer.hand.is_blackjack,
        dealer_up_card=dealer.up_card,
        rules=rules,
        playing_strategy=playing_strategy
    ) == 'H'
    assert card_counter_unbalanced.bankroll == 985
    assert card_counter_unbalanced_hand.status == HandStatus.IN_PLAY
    assert card_counter_unbalanced.stats.stats[(3, StatsCategory.AMOUNT_BET)] == 10
    assert card_counter_unbalanced.stats.stats[(3, StatsCategory.NET_WINNINGS)] == 0
    assert card_counter_unbalanced.stats.stats[(4, StatsCategory.INSURANCE_AMOUNT_BET)] == 5
    assert card_counter_unbalanced.stats.stats[(4, StatsCategory.INSURANCE_NET_WINNINGS)] == -5


def test_player_initial_decision_no_insurance_dealer_blackjack(player, dealer):
    """
    Tests the player_initial_decision function when the player does
    not buy insurance and the dealer has a blackjack.

    """
    rules = Rules(min_bet=10, max_bet=500)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    player_hand = player.get_first_hand()
    player_hand.add_card(card='5')
    player_hand.add_card(card='6')
    dealer.hand.add_card(card='K')
    dealer.hand.add_card(card='A')
    assert player.bankroll == 1000
    assert player_initial_decision(
        player=player,
        player_stats=player.stats.stats,
        placed_bet=10,
        count=None,
        insurance_count=None,
        dealer_hand_is_blackjack=dealer.hand.is_blackjack,
        dealer_up_card=dealer.up_card,
        rules=rules,
        playing_strategy=playing_strategy
    ) is None
    assert player.bankroll == 990
    assert player_hand.status == HandStatus.SETTLED
    assert player.stats.stats[(None, StatsCategory.TOTAL_HANDS_PLAYED)] == 1
    assert player.stats.stats[(None, StatsCategory.PLAYER_HANDS_LOST)] == 1
    assert player.stats.stats[(None, StatsCategory.DEALER_BLACKJACKS)] == 1
    assert player.stats.stats[(None, StatsCategory.AMOUNT_BET)] == 10
    assert player.stats.stats[(None, StatsCategory.NET_WINNINGS)] == -10


def test_player_initial_decision_no_insurance_no_dealer_blackjack(player, dealer):
    """
    Tests the player_initial_decision function when the player does
    not buy insurance and the dealer does not have a blackjack.

    """
    rules = Rules(min_bet=10, max_bet=500)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    player_hand = player.get_first_hand()
    player_hand.add_card(card='2')
    player_hand.add_card(card='3')
    dealer.hand.add_card(card='K')
    dealer.hand.add_card(card='J')
    assert player.bankroll == 1000
    assert player_initial_decision(
        player=player,
        player_stats=player.stats.stats,
        placed_bet=10,
        count=None,
        insurance_count=None,
        dealer_hand_is_blackjack=dealer.hand.is_blackjack,
        dealer_up_card=dealer.up_card,
        rules=rules,
        playing_strategy=playing_strategy
    ) == 'H'
    assert player.bankroll == 990
    assert player_hand.status == HandStatus.IN_PLAY
    assert player.stats.stats[(None, StatsCategory.DEALER_BLACKJACKS)] == 0
    assert player.stats.stats[(None, StatsCategory.AMOUNT_BET)] == 10
    assert player.stats.stats[(None, StatsCategory.NET_WINNINGS)] == 0


def test_player_initial_decision_player_blackjack(player, dealer, rules):
    """
    Tests the player_initial_decision function when the player has a
    blackjack and the dealer does not.

    """
    playing_strategy = PlayingStrategy(s17=rules.s17)
    player_hand = player.get_first_hand()
    player_hand.add_card(card='A')
    player_hand.add_card(card='K')
    dealer.hand.add_card(card='K')
    dealer.hand.add_card(card='J')
    assert player.bankroll == 1000
    assert player_initial_decision(
        player=player,
        player_stats=player.stats.stats,
        placed_bet=10,
        count=None,
        insurance_count=None,
        dealer_hand_is_blackjack=dealer.hand.is_blackjack,
        dealer_up_card=dealer.up_card,
        rules=rules,
        playing_strategy=playing_strategy
    ) is None
    assert player.bankroll == 1015
    assert player_hand.status == HandStatus.SETTLED
    assert player.stats.stats[(None, StatsCategory.TOTAL_HANDS_PLAYED)] == 1
    assert player.stats.stats[(None, StatsCategory.PLAYER_HANDS_WON)] == 1
    assert player.stats.stats[(None, StatsCategory.PLAYER_BLACKJACKS)] == 1
    assert player.stats.stats[(None, StatsCategory.AMOUNT_BET)] == 10
    assert player.stats.stats[(None, StatsCategory.NET_WINNINGS)] == 15


def test_player_initial_decision_late_surrender(player, dealer):
    """
    Tests the player_initial_decision function when the player has
    the option to late surrender and does.

    """
    rules = Rules(min_bet=10, max_bet=500, late_surrender=True)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    player_hand = player.get_first_hand()
    player_hand.add_card(card='K')
    player_hand.add_card(card='5')
    dealer.hand.add_card(card='K')
    dealer.hand.add_card(card='J')
    assert player.bankroll == 1000
    assert player_initial_decision(
        player=player,
        player_stats=player.stats.stats,
        placed_bet=10,
        count=None,
        insurance_count=None,
        dealer_hand_is_blackjack=dealer.hand.is_blackjack,
        dealer_up_card=dealer.up_card,
        rules=rules,
        playing_strategy=playing_strategy
    ) is None
    assert player.bankroll == 995
    assert player_hand.status == HandStatus.SETTLED
    assert player.stats.stats[(None, StatsCategory.TOTAL_HANDS_PLAYED)] == 1
    assert player.stats.stats[(None, StatsCategory.PLAYER_HANDS_LOST)] == 1
    assert player.stats.stats[(None, StatsCategory.PLAYER_SURRENDERS)] == 1
    assert player.stats.stats[(None, StatsCategory.AMOUNT_BET)] == 10
    assert player.stats.stats[(None, StatsCategory.NET_WINNINGS)] == -5


def test_player_initial_decision_no_late_surrender(player, dealer):
    """
    Tests the player_initial_decision function when the player does
    not have the option to late surrender.

    """
    rules = Rules(min_bet=10, max_bet=500, late_surrender=False)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    player_hand = player.get_first_hand()
    player_hand.add_card(card='K')
    player_hand.add_card(card='5')
    dealer.hand.add_card(card='K')
    dealer.hand.add_card(card='J')
    assert player.bankroll == 1000
    assert player_initial_decision(
        player=player,
        player_stats=player.stats.stats,
        placed_bet=10,
        count=None,
        insurance_count=None,
        dealer_hand_is_blackjack=dealer.hand.is_blackjack,
        dealer_up_card=dealer.up_card,
        rules=rules,
        playing_strategy=playing_strategy
    ) == 'Rh'
    assert player.bankroll == 990
    assert player_hand.status == HandStatus.IN_PLAY
    assert player.stats.stats[(None, StatsCategory.PLAYER_SURRENDERS)] == 0
    assert player.stats.stats[(None, StatsCategory.AMOUNT_BET)] == 10
    assert player.stats.stats[(None, StatsCategory.NET_WINNINGS)] == 0


def test_player_plays_hands_initial_decision_settled(player, shoe, dealer):
    """
    Tests the player_plays_hands function when the initial
    decision is settled.

    """
    rules = Rules(min_bet=10, max_bet=500, late_surrender=True)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    player_hand = player.get_first_hand()
    player_hand.add_card(card='K')
    player_hand.add_card(card='5')
    dealer.hand.add_card(card='K')
    dealer.hand.add_card(card='J')
    assert player.bankroll == 1000
    player_plays_hands(
        player=player,
        player_stats=player.stats.stats,
        placed_bet=10,
        shoe=shoe,
        count=None,
        insurance_count=None,
        dealer_hand_is_blackjack=dealer.hand.is_blackjack,
        dealer_up_card=dealer.up_card,
        rules=rules,
        playing_strategy=playing_strategy
    )
    assert player.bankroll == 995
    assert player_hand.status == HandStatus.SETTLED
    assert player.stats.stats[(None, StatsCategory.TOTAL_HANDS_PLAYED)] == 1
    assert player.stats.stats[(None, StatsCategory.PLAYER_HANDS_LOST)] == 1
    assert player.stats.stats[(None, StatsCategory.PLAYER_SURRENDERS)] == 1
    assert player.stats.stats[(None, StatsCategory.AMOUNT_BET)] == 10
    assert player.stats.stats[(None, StatsCategory.NET_WINNINGS)] == -5


def test_player_plays_hands_split(shoe, dealer, player, rules):
    """
    Tests the player_plays_hands function when the player is dealt
    a pair and the hand is split.

    """
    playing_strategy = PlayingStrategy(s17=rules.s17)
    player_hand = player.get_first_hand()
    player_hand.add_card(card='8')
    player_hand.add_card(card='8')
    dealer.hand.add_card(card='6')
    dealer.hand.add_card(card='6')
    assert player.bankroll == 1000
    player_plays_hands(
        player=player,
        player_stats=player.stats.stats,
        placed_bet=10,
        shoe=shoe,
        count=None,
        insurance_count=None,
        dealer_hand_is_blackjack=dealer.hand.is_blackjack,
        dealer_up_card=dealer.up_card,
        rules=rules,
        playing_strategy=playing_strategy
    )
    assert player.bankroll == 980
    assert player.number_of_hands == 2
    assert player_hand.status == HandStatus.SHOWDOWN
    assert player_hand.total_bet == 10
    assert player_hand.cards == ['8', 'A']
    assert player.hands[1].status == HandStatus.SHOWDOWN
    assert player.hands[1].total_bet == 10
    assert player.hands[1].cards == ['8', 'K']
    assert player.stats.stats[(None, StatsCategory.NET_WINNINGS)] == 0
    assert player.stats.stats[(None, StatsCategory.AMOUNT_BET)] == 20


def test_player_plays_hands_split_insufficient_bankroll(shoe, dealer, rules):
    """
    Tests the player_plays_hands function when the player is dealt
    a pair and the player has insufficient bankroll to split a hand.

    """
    playing_strategy = PlayingStrategy(s17=rules.s17)
    player = Player(name='Player 1', min_bet=10, bankroll=10)
    player_hand = player.get_first_hand()
    player_hand.add_card(card='6')
    player_hand.add_card(card='6')
    dealer.hand.add_card(card='7')
    dealer.hand.add_card(card='7')
    shoe._cards = ['J', 'Q', '7', '6', '5', 'A']
    assert player.bankroll == 10
    player_plays_hands(
        player=player,
        player_stats=player.stats.stats,
        placed_bet=10,
        shoe=shoe,
        count=None,
        insurance_count=None,
        dealer_hand_is_blackjack=dealer.hand.is_blackjack,
        dealer_up_card=dealer.up_card,
        rules=rules,
        playing_strategy=playing_strategy
    )
    assert player.bankroll == 0
    assert player.number_of_hands == 1
    assert player_hand.status == HandStatus.SHOWDOWN
    assert player_hand.cards == ['6', '6', 'A', '5']
    assert player.stats.stats[(None, StatsCategory.NET_WINNINGS)] == 0
    assert player.stats.stats[(None, StatsCategory.AMOUNT_BET)] == 10


def test_player_plays_hands_resplit_aces(player, shoe, dealer):
    """
    Tests the player_plays_hands function when the player is dealt
    a pair of aces and aces can be re-split.

    """
    rules = Rules(min_bet=10, max_bet=500, resplit_aces=True)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    player_hand = player.get_first_hand()
    player_hand.add_card(card='A')
    player_hand.add_card(card='A')
    dealer.hand.add_card(card='6')
    dealer.hand.add_card(card='6')
    assert player.bankroll == 1000
    player_plays_hands(
        player=player,
        player_stats=player.stats.stats,
        placed_bet=10,
        shoe=shoe,
        count=None,
        insurance_count=None,
        dealer_hand_is_blackjack=dealer.hand.is_blackjack,
        dealer_up_card=dealer.up_card,
        rules=rules,
        playing_strategy=playing_strategy
    )
    assert rules.resplit_aces is True
    assert player.bankroll == 970
    assert player.number_of_hands == 3
    assert player_hand.status == HandStatus.SHOWDOWN
    assert player_hand.total_bet == 10
    assert player_hand.cards == ['A', 'K']
    assert player.hands[1].status == HandStatus.SHOWDOWN
    assert player.hands[1].total_bet == 10
    assert player.hands[1].cards == ['A', 'Q']
    assert player.hands[2].status == HandStatus.SHOWDOWN
    assert player.hands[2].total_bet == 10
    assert player.hands[2].cards == ['A', 'J']
    assert player.stats.stats[(None, StatsCategory.NET_WINNINGS)] == 0
    assert player.stats.stats[(None, StatsCategory.AMOUNT_BET)] == 30


def test_player_plays_hands_resplit_aces_insufficient_bankroll(shoe, dealer):
    """
    Tests the player_plays_hands function when the player is dealt
    a pair of aces and aces can be re-split but the player
    has insufficient bankroll to split their hand again.

    """
    rules = Rules(min_bet=10, max_bet=500, resplit_aces=True)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    player = Player(name='Player 1', min_bet=10, bankroll=20)
    player_hand = player.get_first_hand()
    player_hand.add_card(card='A')
    player_hand.add_card(card='A')
    dealer.hand.add_card(card='5')
    dealer.hand.add_card(card='5')
    shoe._cards = ['4', '3', '2', 'Q', 'K', 'A']
    assert player.bankroll == 20
    player_plays_hands(
        player=player,
        player_stats=player.stats.stats,
        placed_bet=10,
        shoe=shoe,
        count=None,
        insurance_count=None,
        dealer_hand_is_blackjack=dealer.hand.is_blackjack,
        dealer_up_card=dealer.up_card,
        rules=rules,
        playing_strategy=playing_strategy
    )
    assert rules.resplit_aces is True
    assert player.bankroll == 0
    assert player.number_of_hands == 2
    assert player_hand.status == HandStatus.SHOWDOWN
    assert player_hand.total_bet == 10
    assert player_hand.cards == ['A', 'A', 'K']
    assert player.hands[1].status == HandStatus.SHOWDOWN
    assert player.hands[1].total_bet == 10
    assert player.hands[1].cards == ['A', 'Q']
    assert player.stats.stats[(None, StatsCategory.NET_WINNINGS)] == 0
    assert player.stats.stats[(None, StatsCategory.AMOUNT_BET)] == 20


def test_player_plays_hands_resplit_aces_max_hands(player, shoe, dealer):
    """
    Tests the player_plays_hands function when the player is dealt
    a pair of aces and aces can be re-split but the player reaches
    the max hands limit and is unable to split their hand again.

    """
    rules = Rules(min_bet=10, max_bet=500, resplit_aces=True, max_hands=3)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    player_hand = player.get_first_hand()
    player_hand.add_card(card='A')
    player_hand.add_card(card='A')
    dealer.hand.add_card(card='5')
    dealer.hand.add_card(card='5')
    shoe._cards = ['4', '3', 'A', '3', '2', 'A']
    assert player.bankroll == 1000
    player_plays_hands(
        player=player,
        player_stats=player.stats.stats,
        placed_bet=10,
        shoe=shoe,
        count=None,
        insurance_count=None,
        dealer_hand_is_blackjack=dealer.hand.is_blackjack,
        dealer_up_card=dealer.up_card,
        rules=rules,
        playing_strategy=playing_strategy
    )
    assert rules.resplit_aces is True
    assert player.bankroll == 970
    assert player.number_of_hands == 3
    assert player.number_of_hands == rules.max_hands
    assert player_hand.status == HandStatus.SHOWDOWN
    assert player_hand.total_bet == 10
    assert player_hand.cards == ['A', '2']
    assert player.hands[1].status == HandStatus.SHOWDOWN
    assert player.hands[1].total_bet == 10
    assert player.hands[1].cards == ['A', '3']
    assert player.hands[2].status == HandStatus.SHOWDOWN
    assert player.hands[2].total_bet == 10
    assert player.hands[2].cards == ['A', 'A']
    assert player.stats.stats[(None, StatsCategory.NET_WINNINGS)] == 0
    assert player.stats.stats[(None, StatsCategory.AMOUNT_BET)] == 30


def test_player_plays_hands_resplit_aces_not_allowed(player, shoe, dealer):
    """
    Tests the player_plays_hands function when the player is dealt
    a pair of aces and aces cannot be re-split.

    """
    rules = Rules(min_bet=10, max_bet=500, resplit_aces=False)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    player_hand = player.get_first_hand()
    player_hand.add_card(card='A')
    player_hand.add_card(card='A')
    dealer.hand.add_card(card='6')
    dealer.hand.add_card(card='6')
    assert player.bankroll == 1000
    player_plays_hands(
        player=player,
        player_stats=player.stats.stats,
        placed_bet=10,
        shoe=shoe,
        count=None,
        insurance_count=None,
        dealer_hand_is_blackjack=dealer.hand.is_blackjack,
        dealer_up_card=dealer.up_card,
        rules=rules,
        playing_strategy=playing_strategy
    )
    assert rules.resplit_aces is False
    assert player.bankroll == 980
    assert player.number_of_hands == 2
    assert player_hand.status == HandStatus.SHOWDOWN
    assert player_hand.total_bet == 10
    assert player_hand.cards == ['A', 'A']
    assert player.hands[1].status == HandStatus.SHOWDOWN
    assert player.hands[1].total_bet == 10
    assert player.hands[1].cards == ['A', 'K']
    assert player.stats.stats[(None, StatsCategory.NET_WINNINGS)] == 0
    assert player.stats.stats[(None, StatsCategory.AMOUNT_BET)] == 20


def test_player_plays_hands_double_down(player, dealer, shoe):
    """
    Tests the player_plays_hands function when the player
    can double down.

    """
    rules = Rules(min_bet=10, max_bet=500, double_down=True)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    player_hand = player.get_first_hand()
    player_hand.add_card(card='5')
    player_hand.add_card(card='6')
    dealer.hand.add_card(card='2')
    dealer.hand.add_card(card='3')
    assert player.bankroll == 1000
    player_plays_hands(
        player=player,
        player_stats=player.stats.stats,
        placed_bet=10,
        shoe=shoe,
        count=None,
        insurance_count=None,
        dealer_hand_is_blackjack=dealer.hand.is_blackjack,
        dealer_up_card=dealer.up_card,
        rules=rules,
        playing_strategy=playing_strategy
    )
    assert rules.double_down is True
    assert player.bankroll == 980
    assert player_hand.status == HandStatus.SHOWDOWN
    assert player_hand.cards == ['5', '6', 'A']
    assert player_hand.total_bet == 20
    assert player.stats.stats[(None, StatsCategory.PLAYER_DOUBLE_DOWNS)] == 1
    assert player.stats.stats[(None, StatsCategory.NET_WINNINGS)] == 0
    assert player.stats.stats[(None, StatsCategory.AMOUNT_BET)] == 20


def test_player_plays_hands_double_down_not_allowed(player, dealer, shoe):
    """
    Tests the player_plays_hands function when the player
    cannot double down.

    """
    rules = Rules(min_bet=10, max_bet=500, double_down=False)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    player_hand = player.get_first_hand()
    player_hand.add_card(card='5')
    player_hand.add_card(card='6')
    dealer.hand.add_card(card='2')
    dealer.hand.add_card(card='3')
    assert player.bankroll == 1000
    player_plays_hands(
        player=player,
        player_stats=player.stats.stats,
        placed_bet=10,
        shoe=shoe,
        count=None,
        insurance_count=None,
        dealer_hand_is_blackjack=dealer.hand.is_blackjack,
        dealer_up_card=dealer.up_card,
        rules=rules,
        playing_strategy=playing_strategy
    )
    assert rules.double_down is False
    assert player.bankroll == 990
    assert player_hand.status == HandStatus.SETTLED
    assert player_hand.cards == ['5', '6', 'A', 'K']
    assert player_hand.total_bet == 10
    assert player.stats.stats[(None, StatsCategory.TOTAL_HANDS_PLAYED)] == 1
    assert player.stats.stats[(None, StatsCategory.PLAYER_HANDS_LOST)] == 1
    assert player.stats.stats[(None, StatsCategory.PLAYER_DOUBLE_DOWNS)] == 0
    assert player.stats.stats[(None, StatsCategory.NET_WINNINGS)] == -10
    assert player.stats.stats[(None, StatsCategory.AMOUNT_BET)] == 10


def test_player_plays_hands_double_down_insufficient_bankroll(player, dealer, shoe):
    """
    Tests the player_plays_hands function when the player
    has insufficient bankroll to double down.

    """
    rules = Rules(min_bet=10, max_bet=500, double_down=True)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    player_hand = player.get_first_hand()
    player_hand.add_card(card='5')
    player_hand.add_card(card='6')
    dealer.hand.add_card(card='2')
    dealer.hand.add_card(card='3')
    player._bankroll = 10
    assert player.bankroll == 10
    player_plays_hands(
        player=player,
        player_stats=player.stats.stats,
        placed_bet=10,
        shoe=shoe,
        count=None,
        insurance_count=None,
        dealer_hand_is_blackjack=dealer.hand.is_blackjack,
        dealer_up_card=dealer.up_card,
        rules=rules,
        playing_strategy=playing_strategy
    )
    assert rules.double_down is True
    assert player.bankroll == 0
    assert player_hand.status == HandStatus.SETTLED
    assert player_hand.total_bet == 10
    assert player_hand.cards == ['5', '6', 'A', 'K']
    assert player.stats.stats[(None, StatsCategory.TOTAL_HANDS_PLAYED)] == 1
    assert player.stats.stats[(None, StatsCategory.PLAYER_HANDS_LOST)] == 1
    assert player.stats.stats[(None, StatsCategory.PLAYER_DOUBLE_DOWNS)] == 0
    assert player.stats.stats[(None, StatsCategory.NET_WINNINGS)] == -10
    assert player.stats.stats[(None, StatsCategory.AMOUNT_BET)] == 10


def test_player_plays_hands_double_after_split(player, dealer, shoe):
    """
    Tests the player_plays_hands function when the player
    doubles after splitting.

    """
    rules = Rules(min_bet=10, max_bet=500, double_down=True, double_after_split=True)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    player_hand = player.get_first_hand()
    player_hand.add_card(card='2')
    player_hand.add_card(card='2')
    dealer.hand.add_card(card='2')
    dealer.hand.add_card(card='3')
    shoe._cards = ['K', 'A', 'J', '8', 'Q', '8']
    assert player.bankroll == 1000
    player_plays_hands(
        player=player,
        player_stats=player.stats.stats,
        placed_bet=10,
        shoe=shoe,
        count=None,
        insurance_count=None,
        dealer_hand_is_blackjack=dealer.hand.is_blackjack,
        dealer_up_card=dealer.up_card,
        rules=rules,
        playing_strategy=playing_strategy
    )
    assert rules.double_after_split is True
    assert player.bankroll == 960
    assert player.number_of_hands == 2
    assert player_hand.status == HandStatus.SHOWDOWN
    assert player_hand.total_bet == 20
    assert player_hand.cards == ['2', '8', 'Q']
    assert player.hands[1].status == HandStatus.SHOWDOWN
    assert player.hands[1].total_bet == 20
    assert player.hands[1].cards == ['2', '8', 'J']
    assert player.stats.stats[(None, StatsCategory.PLAYER_DOUBLE_DOWNS)] == 2
    assert player.stats.stats[(None, StatsCategory.NET_WINNINGS)] == 0
    assert player.stats.stats[(None, StatsCategory.AMOUNT_BET)] == 40


def test_player_plays_hands_double_after_split_not_allowed(player, dealer, shoe):
    """
    Tests the player_plays_hands function when the player
    is not allowed to double after splitting.

    """
    rules = Rules(min_bet=10, max_bet=500, double_down=True, double_after_split=False)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    player_hand = player.get_first_hand()
    player_hand.add_card(card='2')
    player_hand.add_card(card='2')
    dealer.hand.add_card(card='2')
    dealer.hand.add_card(card='3')
    assert player.bankroll == 1000
    player_plays_hands(
        player=player,
        player_stats=player.stats.stats,
        placed_bet=10,
        shoe=shoe,
        count=None,
        insurance_count=None,
        dealer_hand_is_blackjack=dealer.hand.is_blackjack,
        dealer_up_card=dealer.up_card,
        rules=rules,
        playing_strategy=playing_strategy
    )
    assert rules.double_after_split is False
    assert player.bankroll == 990
    assert player_hand.status == HandStatus.SHOWDOWN
    assert player_hand.total_bet == 10
    assert player_hand.cards == ['2', '2', 'A', 'K']
    assert player.stats.stats[(None, StatsCategory.PLAYER_DOUBLE_DOWNS)] == 0
    assert player.stats.stats[(None, StatsCategory.NET_WINNINGS)] == 0
    assert player.stats.stats[(None, StatsCategory.AMOUNT_BET)] == 10


def test_player_plays_hands_double_after_split_insufficient_bankroll(player, dealer, shoe):
    """
    Tests the player_plays_hands function when the player
    has insufficient bankroll to double after splitting.

    """
    rules = Rules(min_bet=10, max_bet=500, double_down=True, double_after_split=True)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    player_hand = player.get_first_hand()
    player_hand.add_card(card='2')
    player_hand.add_card(card='2')
    dealer.hand.add_card(card='2')
    dealer.hand.add_card(card='3')
    player._bankroll = 30
    assert player.bankroll == 30
    player_plays_hands(
        player=player,
        player_stats=player.stats.stats,
        placed_bet=10,
        shoe=shoe,
        count=None,
        insurance_count=None,
        dealer_hand_is_blackjack=dealer.hand.is_blackjack,
        dealer_up_card=dealer.up_card,
        rules=rules,
        playing_strategy=playing_strategy
    )
    assert rules.double_after_split is True
    assert player.bankroll == 20
    assert player_hand.status == HandStatus.SHOWDOWN
    assert player_hand.total_bet == 10
    assert player_hand.cards == ['2', '2', 'A', 'K']
    assert player.stats.stats[(None, StatsCategory.PLAYER_DOUBLE_DOWNS)] == 0
    assert player.stats.stats[(None, StatsCategory.NET_WINNINGS)] == 0
    assert player.stats.stats[(None, StatsCategory.AMOUNT_BET)] == 10


def test_player_plays_hands_stand(player, dealer, shoe, rules):
    """Tests the player_plays_hands function when the player stands."""
    playing_strategy = PlayingStrategy(s17=rules.s17)
    player_hand = player.get_first_hand()
    player_hand.add_card(card='6')
    player_hand.add_card(card='7')
    dealer.hand.add_card(card='6')
    dealer.hand.add_card(card='6')
    assert player.bankroll == 1000
    player_plays_hands(
        player=player,
        player_stats=player.stats.stats,
        placed_bet=10,
        shoe=shoe,
        count=None,
        insurance_count=None,
        dealer_hand_is_blackjack=dealer.hand.is_blackjack,
        dealer_up_card=dealer.up_card,
        rules=rules,
        playing_strategy=playing_strategy
    )
    assert player.bankroll == 990
    assert player_hand.status == HandStatus.SHOWDOWN
    assert player_hand.cards == ['6', '7']
    assert player.stats.stats[(None, StatsCategory.NET_WINNINGS)] == 0
    assert player.stats.stats[(None, StatsCategory.AMOUNT_BET)] == 10


def test_player_plays_hands_busted(player, dealer, shoe, rules):
    """Tests the player_plays_hands function when the hand is busted."""
    playing_strategy = PlayingStrategy(s17=rules.s17)
    player_hand = player.get_first_hand()
    player_hand.add_card(card='6')
    player_hand.add_card(card='7')
    dealer.hand.add_card(card='10')
    dealer.hand.add_card(card='Q')
    assert player.bankroll == 1000
    player_plays_hands(
        player=player,
        player_stats=player.stats.stats,
        placed_bet=10,
        shoe=shoe,
        count=None,
        insurance_count=None,
        dealer_hand_is_blackjack=dealer.hand.is_blackjack,
        dealer_up_card=dealer.up_card,
        rules=rules,
        playing_strategy=playing_strategy
    )
    assert player.bankroll == 990
    assert player_hand.status == HandStatus.SETTLED
    assert player_hand.total > 21
    assert player_hand.cards == ['6', '7', 'A', 'K']
    assert player.stats.stats[(None, StatsCategory.TOTAL_HANDS_PLAYED)] == 1
    assert player.stats.stats[(None, StatsCategory.PLAYER_HANDS_LOST)] == 1
    assert player.stats.stats[(None, StatsCategory.NET_WINNINGS)] == -10
    assert player.stats.stats[(None, StatsCategory.AMOUNT_BET)] == 10


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
    dealer.hand.add_card(card=test_hole_card)
    dealer.hand.add_card(card=test_up_card)
    dealer_plays_hand(shoe=shoe, dealer=dealer, s17=test_s17)
    assert dealer.hand.total == expected


def test_dealer_turn(player, table):
    """Tests the dealer_turn function."""
    table.add_player(player=player)
    player_hand = player.get_first_hand()
    player_hand.status = HandStatus.IN_PLAY
    assert dealer_turn(players=table.players) is False
    player_hand.status = HandStatus.SETTLED
    assert dealer_turn(players=table.players) is False
    player_hand.status = HandStatus.SHOWDOWN
    assert dealer_turn(players=table.players) is True


def test_compare_hands_win_total(player, dealer):
    """
    Tests the compare_hands function when the player wins
    based on total.

    """
    player_hand = player.get_first_hand()
    player_hand.add_to_total_bet(amount=10)
    player_hand.add_card(card='J')
    player_hand.add_card(card='K')
    player_hand.status = HandStatus.SHOWDOWN
    dealer.hand.add_card(card='10')
    dealer.hand.add_card(card='8')
    assert player.bankroll == 1000
    compare_hands(
        player=player,
        player_stats=player.stats.stats,
        dealer_hand_is_busted=dealer.hand.is_busted,
        dealer_hand_total=dealer.hand.total,
        count=None
    )
    assert player.bankroll == 1020
    assert player_hand.status == HandStatus.SETTLED
    assert player.stats.stats[(None, StatsCategory.TOTAL_HANDS_PLAYED)] == 1
    assert player.stats.stats[(None, StatsCategory.PLAYER_HANDS_WON)] == 1
    assert player.stats.stats[(None, StatsCategory.NET_WINNINGS)] == 10


def test_compare_hands_win_dealer_busts(player, dealer):
    """
    Tests the compare_hands function when the player wins
    and the dealer busts.

    """
    player_hand = player.get_first_hand()
    player_hand.add_to_total_bet(amount=10)
    player_hand.add_card(card='J')
    player_hand.add_card(card='K')
    player_hand.status = HandStatus.SHOWDOWN
    dealer.hand.add_card(card='10')
    dealer.hand.add_card(card='6')
    dealer.hand.add_card(card='K')
    assert player.bankroll == 1000
    compare_hands(
        player=player,
        player_stats=player.stats.stats,
        dealer_hand_is_busted=dealer.hand.is_busted,
        dealer_hand_total=dealer.hand.total,
        count=None
    )
    assert player.bankroll == 1020
    assert player_hand.status == HandStatus.SETTLED
    assert player.stats.stats[(None, StatsCategory.TOTAL_HANDS_PLAYED)] == 1
    assert player.stats.stats[(None, StatsCategory.PLAYER_HANDS_WON)] == 1
    assert player.stats.stats[(None, StatsCategory.NET_WINNINGS)] == 10


def test_compare_hands_push(player, dealer):
    """
    Tests the compare_hands function when the player and
    dealer push.

    """
    player_hand = player.get_first_hand()
    player_hand.add_to_total_bet(amount=10)
    player_hand.add_card(card='J')
    player_hand.add_card(card='K')
    player_hand.status = HandStatus.SHOWDOWN
    dealer.hand.add_card(card='10')
    dealer.hand.add_card(card='Q')
    assert player.bankroll == 1000
    compare_hands(
        player=player,
        player_stats=player.stats.stats,
        dealer_hand_is_busted=dealer.hand.is_busted,
        dealer_hand_total=dealer.hand.total,
        count=None
    )
    assert player.bankroll == 1010
    assert player_hand.status == HandStatus.SETTLED
    assert player.stats.stats[(None, StatsCategory.TOTAL_HANDS_PLAYED)] == 1
    assert player.stats.stats[(None, StatsCategory.PLAYER_HANDS_PUSHED)] == 1
    assert player.stats.stats[(None, StatsCategory.NET_WINNINGS)] == 0


def test_compare_hands_loss_total(player, dealer):
    """
    Tests the compare_hands function when the player loses
    based on total.

    """
    player_hand = player.get_first_hand()
    player_hand.add_to_total_bet(amount=10)
    player_hand.add_card(card='7')
    player_hand.add_card(card='K')
    player_hand.status = HandStatus.SHOWDOWN
    dealer.hand.add_card(card='10')
    dealer.hand.add_card(card='8')
    assert player.bankroll == 1000
    compare_hands(
        player=player,
        player_stats=player.stats.stats,
        dealer_hand_is_busted=dealer.hand.is_busted,
        dealer_hand_total=dealer.hand.total,
        count=None
    )
    assert player.bankroll == 1000
    assert player_hand.status == HandStatus.SETTLED
    assert player.stats.stats[(None, StatsCategory.TOTAL_HANDS_PLAYED)] == 1
    assert player.stats.stats[(None, StatsCategory.PLAYER_HANDS_LOST)] == 1
    assert player.stats.stats[(None, StatsCategory.NET_WINNINGS)] == -10


def test_clear_hands(table, dealer_with_hand, player, rules):
    """Test the clear_hands function."""
    table.add_player(player=player)
    player_hand = player.get_first_hand()
    player_hand.add_card(card='A')
    player_hand.add_card(card='A')
    split_hand = player_hand.split()
    player.hands.append(split_hand)
    player_hand.add_card(card='2')
    player.hands[1].add_card(card='6')
    assert dealer_with_hand.hand.cards == ['8', '6']
    assert player_hand.cards == ['A', '2']
    assert player.hands[1].cards == ['A', '6']
    clear_hands(dealer=dealer_with_hand, players=table.players)
    assert player.number_of_hands == 1
    assert player.get_first_hand().cards == []
    assert dealer_with_hand.hand.cards == []


def test_play_round_back_counters_added(table, shoe, dealer, rules, card_counter_balanced, back_counter):
    """Tests the play_round function when back counters are added."""
    playing_strategy = PlayingStrategy(s17=rules.s17)
    table.add_player(player=card_counter_balanced)
    table.add_player(player=back_counter)
    shoe.add_to_seen_cards(card='2')
    shoe.add_to_seen_cards(card='2')
    shoe.add_to_seen_cards(card='2')
    play_round(table=table, dealer=dealer, shoe=shoe, rules=rules, playing_strategy=playing_strategy)
    assert card_counter_balanced.stats.stats[(3, StatsCategory.TOTAL_ROUNDS_PLAYED)] == 1
    assert card_counter_balanced.stats.stats[(3, StatsCategory.TOTAL_HANDS_PLAYED)] == 1
    assert card_counter_balanced.stats.stats[(3, StatsCategory.PLAYER_HANDS_WON)] == 1
    assert card_counter_balanced.stats.stats[(3, StatsCategory.PLAYER_BLACKJACKS)] == 1
    assert card_counter_balanced.stats.stats[(3, StatsCategory.AMOUNT_BET)] == 40
    assert card_counter_balanced.stats.stats[(3, StatsCategory.NET_WINNINGS)] == 60
    assert back_counter.stats.stats[(3, StatsCategory.TOTAL_ROUNDS_PLAYED)] == 1
    assert back_counter.stats.stats[(3, StatsCategory.TOTAL_HANDS_PLAYED)] == 1
    assert back_counter.stats.stats[(3, StatsCategory.PLAYER_HANDS_WON)] == 1
    assert back_counter.stats.stats[(3, StatsCategory.AMOUNT_BET)] == 40
    assert back_counter.stats.stats[(3, StatsCategory.NET_WINNINGS)] == 40


def test_play_round_insufficient_funds(table, dealer, player, shoe, rules):
    """Tests the play_round function when a player has insufficient funds."""
    playing_strategy = PlayingStrategy(s17=rules.s17)
    table.add_player(player=player)
    player._bankroll = 0
    assert player.bankroll == 0
    assert len(table.players) == 1
    play_round(table=table, dealer=dealer, shoe=shoe, rules=rules, playing_strategy=playing_strategy)
    assert len(table.players) == 0


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
    assert card_counter_unbalanced.stats.stats[(3, StatsCategory.TOTAL_ROUNDS_PLAYED)] == 1
    assert card_counter_unbalanced.stats.stats[(3, StatsCategory.TOTAL_HANDS_PLAYED)] == 1
    assert card_counter_unbalanced.stats.stats[(3, StatsCategory.PLAYER_HANDS_LOST)] == 1
    assert card_counter_unbalanced.stats.stats[(3, StatsCategory.AMOUNT_BET)] == 40
    assert card_counter_unbalanced.stats.stats[(3, StatsCategory.NET_WINNINGS)] == -40
    assert card_counter_unbalanced.stats.stats[(2, StatsCategory.INSURANCE_AMOUNT_BET)] == 20
    assert card_counter_unbalanced.stats.stats[(2, StatsCategory.INSURANCE_NET_WINNINGS)] == 20


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
    assert card_counter_unbalanced.stats.stats[(3, StatsCategory.TOTAL_ROUNDS_PLAYED)] == 1
    assert card_counter_unbalanced.stats.stats[(3, StatsCategory.TOTAL_HANDS_PLAYED)] == 1
    assert card_counter_unbalanced.stats.stats[(3, StatsCategory.PLAYER_HANDS_WON)] == 1
    assert card_counter_unbalanced.stats.stats[(3, StatsCategory.AMOUNT_BET)] == 40
    assert card_counter_unbalanced.stats.stats[(3, StatsCategory.NET_WINNINGS)] == 40
    assert card_counter_unbalanced.stats.stats[(2, StatsCategory.INSURANCE_AMOUNT_BET)] == 20
    assert card_counter_unbalanced.stats.stats[(2, StatsCategory.INSURANCE_NET_WINNINGS)] == -20


def test_play_round_player_blackjack(table, player, dealer, shoe, rules):
    """Tests the play_round function when a player has a blackjack."""
    playing_strategy = PlayingStrategy(s17=rules.s17)
    table.add_player(player=player)
    shoe._cards = ['K', 'K', '9', 'A']
    play_round(table=table, dealer=dealer, shoe=shoe, rules=rules, playing_strategy=playing_strategy)
    assert shoe.seen_cards['A'] == 1
    assert shoe.seen_cards['10-J-Q-K'] == 2
    assert shoe.seen_cards['9'] == 0
    assert player.stats.stats[(None, StatsCategory.TOTAL_ROUNDS_PLAYED)] == 1
    assert player.stats.stats[(None, StatsCategory.TOTAL_HANDS_PLAYED)] == 1
    assert player.stats.stats[(None, StatsCategory.PLAYER_HANDS_WON)] == 1
    assert player.stats.stats[(None, StatsCategory.PLAYER_BLACKJACKS)] == 1
    assert player.stats.stats[(None, StatsCategory.AMOUNT_BET)] == 10
    assert player.stats.stats[(None, StatsCategory.NET_WINNINGS)] == 15


def test_play_round_dealer_blackjack(table, player, dealer, shoe, rules):
    """Tests the play_round function when the dealer has a blackjack."""
    playing_strategy = PlayingStrategy(s17=rules.s17)
    table.add_player(player=player)
    shoe._cards = ['K', '9', 'A', 'A']
    play_round(table=table, dealer=dealer, shoe=shoe, rules=rules, playing_strategy=playing_strategy)
    assert shoe.seen_cards['A'] == 2
    assert shoe.seen_cards['10-J-Q-K'] == 1
    assert shoe.seen_cards['9'] == 1
    assert player.stats.stats[(None, StatsCategory.TOTAL_ROUNDS_PLAYED)] == 1
    assert player.stats.stats[(None, StatsCategory.TOTAL_HANDS_PLAYED)] == 1
    assert player.stats.stats[(None, StatsCategory.PLAYER_HANDS_LOST)] == 1
    assert player.stats.stats[(None, StatsCategory.AMOUNT_BET)] == 10
    assert player.stats.stats[(None, StatsCategory.NET_WINNINGS)] == -10


def test_play_round_player_dealer_blackjack(table, player, dealer, shoe, rules):
    """
    Tests the play_round function when a player
    and the dealer have a blackjack.

    """
    playing_strategy = PlayingStrategy(s17=rules.s17)
    table.add_player(player=player)
    shoe._cards = ['K', 'K', 'A', 'A']
    play_round(table=table, dealer=dealer, shoe=shoe, rules=rules, playing_strategy=playing_strategy)
    assert shoe.seen_cards['A'] == 2
    assert shoe.seen_cards['10-J-Q-K'] == 2
    assert player.stats.stats[(None, StatsCategory.TOTAL_ROUNDS_PLAYED)] == 1
    assert player.stats.stats[(None, StatsCategory.TOTAL_HANDS_PLAYED)] == 1
    assert player.stats.stats[(None, StatsCategory.PLAYER_HANDS_PUSHED)] == 1
    assert player.stats.stats[(None, StatsCategory.PLAYER_BLACKJACKS)] == 1
    assert player.stats.stats[(None, StatsCategory.AMOUNT_BET)] == 10
    assert player.stats.stats[(None, StatsCategory.NET_WINNINGS)] == 0


@pytest.mark.parametrize(
    'test_dealer_shows_hole_card, test_seen_cards',
    [
        (True, 5),
        (False, 4)
     ]
)
def test_play_round_all_hands_settled_dealer_shows_hole_card(
    player,
    card_counter_balanced,
    dealer,
    shoe,
    test_dealer_shows_hole_card,
    test_seen_cards
):
    """
    Tests the play_round function when all hands
    are settled and the dealer does or does not
    show the hole card.

    """
    rules = Rules(min_bet=10, max_bet=500, dealer_shows_hole_card=test_dealer_shows_hole_card)
    table = Table(rules=rules)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    table.add_player(player=player)
    table.add_player(player=card_counter_balanced)
    shoe._cards = ['10', 'J', 'J', 'Q', 'K', 'A', '4']
    play_round(table=table, dealer=dealer, shoe=shoe, rules=rules, playing_strategy=playing_strategy)
    assert shoe.seen_cards['A'] == 1
    assert shoe.seen_cards['4'] == 1
    assert shoe.seen_cards['10-J-Q-K'] == test_seen_cards


@pytest.mark.parametrize(
    'test_dealer_shows_hole_card',
    [
        (True),
        (False)
     ]
)
def test_play_round_showdown_hands_dealer_shows_hole_card(player, dealer, shoe, test_dealer_shows_hole_card):
    """
    Tests the play_round function when there are
    showdown hands and the dealer does or does not
    show the hole card.

    """
    rules = Rules(min_bet=10, max_bet=500, dealer_shows_hole_card=test_dealer_shows_hole_card)
    table = Table(rules=rules)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    table.add_player(player=player)
    shoe._cards = ['10', 'J', 'Q', 'K']
    play_round(table=table, dealer=dealer, shoe=shoe, rules=rules, playing_strategy=playing_strategy)
    assert shoe.seen_cards['10-J-Q-K'] == 4


def test_play_round_clear_hands(table, player, dealer, shoe, rules):
    """
    Tests the play_round function to check
    that the hands are properly cleared after
    each round.

    """
    playing_strategy = PlayingStrategy(s17=rules.s17)
    table.add_player(player=player)
    play_round(table=table, dealer=dealer, shoe=shoe, rules=rules, playing_strategy=playing_strategy)
    assert dealer.hand.cards == []
    assert player.get_first_hand().cards == []


def test_play_round_player_removed(table, player, dealer, shoe, rules):
    """Tests the play_round function when a player is removed."""
    player = Player(name='Player 1', bankroll=10, min_bet=10)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    table.add_player(player=player)
    player._bankroll = 0
    assert player.bankroll == 0
    assert len(table.players) == 1
    play_round(table=table, dealer=dealer, shoe=shoe, rules=rules, playing_strategy=playing_strategy)
    assert len(table.players) == 0
    assert player.stats.stats[(None, StatsCategory.TOTAL_HANDS_PLAYED)] == 0
    assert player.stats.stats[(None, StatsCategory.TOTAL_ROUNDS_PLAYED)] == 0


def test_play_round_add_and_remove_back_counters(table, dealer, player, rules, back_counter):
    """
    Tests the play_round function when a back counter
    is added and removed from the table.

    """
    shoe = Shoe(shoe_size=1, penetration=0.75)
    playing_strategy = PlayingStrategy(s17=rules.s17)
    table.add_player(player=player)
    table.add_player(player=back_counter)
    for _ in range(0, 3):
        shoe.add_to_seen_cards(card='2')
    shoe._cards = ['A', 'K', 'Q', 'J'] * 13
    assert len(table.players) == 1
    count_round_1 = shoe.true_count(card_counting_system=back_counter.card_counting_system)
    assert count_round_1 >= back_counter.entry_point
    play_round(table=table, dealer=dealer, shoe=shoe, rules=rules, playing_strategy=playing_strategy)
    assert len(table.players) == 2
    assert back_counter.stats.stats[(count_round_1, StatsCategory.TOTAL_ROUNDS_PLAYED)] == 1
    play_round(table=table, dealer=dealer, shoe=shoe, rules=rules, playing_strategy=playing_strategy)
    assert len(table.players) == 1
    count_round_2 = shoe.true_count(card_counting_system=back_counter.card_counting_system)
    assert count_round_2 <= back_counter.exit_point
    assert back_counter.stats.stats[(count_round_2, StatsCategory.TOTAL_ROUNDS_PLAYED)] == 0
