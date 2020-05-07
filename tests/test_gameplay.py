import pytest

from table import Table
from house_rules import HouseRules
from player import Player
from cards import Cards
from counting_strategy import CountingStrategy
from simulation_stats import SimulationStats
from gameplay import players_place_bets, deal_hands, players_play_hands, dealer_turn, dealer_plays_hand, compare_hands


def test_players_place_bets():
    """
    Tests the players_place_bets function.

    """
    cards = Cards(shoe_size=6)
    counting_strategy = CountingStrategy(cards=cards)
    table = Table()
    rules = HouseRules(bet_limits=[10, 500])
    players = [
                Player(
                    name='Amount bet below table minimum',
                    rules=rules,
                    bankroll=20,
                    min_bet=10
                ),
                Player(
                    name='Amount bet within constraints',
                    rules=rules,
                    bankroll=20,
                    min_bet=10
                ),
                Player(
                    name='Amount bet is greater than available funds',
                    rules=rules,
                    bankroll=2000,
                    min_bet=500
                )
    ]

    for p in players:
        table.add_player(player=p)
        if p.get_name() == 'Amount bet below table minimum':
            p.set_bankroll(amount=5)
            assert p.get_bankroll() == 5
            assert p.get_bankroll() < rules.min_bet
        elif p.get_name() == 'Amount bet within constraints':
            assert rules.min_bet <= p.get_min_bet() <= rules.max_bet
        else:
            p.set_bankroll(amount=490)
            assert p.get_bankroll() == 490
            assert p.get_min_bet() > p.get_bankroll()
            assert rules.min_bet <= p.get_bankroll() <= rules.max_bet

    players_place_bets(table=table, rules=rules, counting_strategy=counting_strategy)

    for p in players:
        if p.get_name() == 'Amount bet below table minimum':
            assert p.get_bankroll() == 5  # bankroll unchanged
            assert p not in table.get_players()  # player removed from table
        elif p.get_name() == 'Amount bet within constraints':
            assert p.get_bankroll() == 10  # bankroll went down by 10
            assert p in table.get_players()  # player still at table
        else:
            assert p.get_bankroll() == 0  # player bet entire bankroll
            assert p in table.get_players()  # player still at table


def test_deal_hands():
    """
    Tests the deal_hands function.

    """
    cards = Cards(shoe_size=6)  # without shuffling, cards dealt will be 'A', 'K', 'Q', 'J', '10', etc.
    table = Table()
    rules = HouseRules(bet_limits=[10, 500])
    players = [
                Player(
                    name='First to act',
                    rules=rules,
                    bankroll=100,
                    min_bet=10
                ),
                Player(
                    name='Second to act',
                    rules=rules,
                    bankroll=100,
                    min_bet=10
                ),
                Player(
                    name='Third to act',
                    rules=rules,
                    bankroll=100,
                    min_bet=10
                )
    ]

    for p in players:
        table.add_player(player=p)
        p.create_hand(amount=10)

    dealer_hand = deal_hands(table=table, cards=cards)

    assert dealer_hand == ['J', '7']

    for p in players:
        if p.get_name() == 'First to act':
            assert p.get_hand(key=1) == ['A', '10']
        elif p.get_name() == 'Second to act':
            assert p.get_hand(key=1) == ['K', '9']
        else:
            assert p.get_hand(key=1) == ['Q', '8']


@pytest.fixture
def setup_table():
    """
    Fixture that sets up a table with a single player.

    """
    cards = Cards(shoe_size=6)
    table = Table()
    rules = HouseRules(
                bet_limits=[10, 500],
                s17=True,
                blackjack_payout=1.5,
                max_hands=4,
                double_down=True,
                split_unlike_tens=True,
                double_after_split=True,
                resplit_aces=False,
                insurance=True,
                late_surrender=True,
                dealer_shows_hole_card=False
    )
    player = Player(
                    name='Player 1',
                    rules=rules,
                    bankroll=100,
                    min_bet=10
    )

    table.add_player(player=player)
    player.initial_bet(amount=10)  # creates hand
    return cards, table, rules, player


def test_players_play_hands_buys_insurance(setup_table):
    """
    Tests the players_play_hands function when a player buys insurance.

    Parameters
    ----------
    setup_table
        Fixture that sets up a table with a single player

    """
    cards, table, rules, player = setup_table
    player.set_count(count=1)
    player.insurance_count = 0
    player.hit(key=1, new_card='2')
    player.hit(key=1, new_card='2')

    players_play_hands(table=table, rules=rules, cards=cards, dealer_hand=['J', 'A'], dealer_up_card='A')

    assert player.get_insurance() is True
    assert player.get_stand(key=1) is True
    assert player.get_bankroll() == 85
    assert player.get_hand(key=1) == ['2', '2']


def test_players_play_hands_does_not_buy_insurance(setup_table):
    """
    Tests the players_play_hands function when a player does not buy insurance.

    Parameters
    ----------
    setup_table
        Fixture that sets up a table with a single player

    """
    cards, table, rules, player = setup_table
    player.set_count(count=0)
    player.insurance_count = 1
    player.hit(key=1, new_card='J')
    player.hit(key=1, new_card='J')

    players_play_hands(table=table, rules=rules, cards=cards, dealer_hand=['J', 'A'], dealer_up_card='A')

    assert player.get_insurance() is False
    assert player.get_stand(key=1) is True
    assert player.get_bankroll() == 90
    assert player.get_hand(key=1) == ['J', 'J']


def test_players_play_hands_player_blackjack(setup_table):
    """
    Tests the players_play_hands function when a player has a natural blackjack.

    Parameters
    ----------
    setup_table
        Fixture that sets up a table with a single player

    """
    cards, table, rules, player = setup_table
    player.hit(key=1, new_card='K')
    player.hit(key=1, new_card='A')

    players_play_hands(table=table, rules=rules, cards=cards, dealer_hand=['J', 'J'], dealer_up_card='J')

    assert player.get_natural_blackjack() is True
    assert player.get_stand(key=1) is True
    assert player.get_hand(key=1) == ['K', 'A']


def test_players_play_hands_dealer_blackjack(setup_table):
    """
    Tests the players_play_hands function when a dealer has a natural blackjack.

    Parameters
    ----------
    setup_table
        Fixture that sets up a table with a single player

    """
    cards, table, rules, player = setup_table
    player.hit(key=1, new_card='J')
    player.hit(key=1, new_card='J')

    players_play_hands(table=table, rules=rules, cards=cards, dealer_hand=['K', 'A'], dealer_up_card='A')

    assert player.get_stand(key=1) is True
    assert player.get_hand(key=1) == ['J', 'J']


def test_players_play_hands_three_plus_card_21(setup_table):
    """
    Tests the players_play_hands function when a player has a three or more card 21.

    Parameters
    ----------
    setup_table
        Fixture that sets up a table with a single player

    """
    cards, table, rules, player = setup_table
    player.hit(key=1, new_card='6')
    player.hit(key=1, new_card='4')

    players_play_hands(table=table, rules=rules, cards=cards, dealer_hand=['J', 'J'], dealer_up_card='J')

    assert player.get_natural_blackjack() is False
    assert player.get_hand(key=1) == ['6', '4', 'A']


def test_players_play_hands_late_surrender(setup_table):
    """
    Tests the players_play_hands function when a player surrenders their hand.

    Parameters
    ----------
    setup_table
        Fixture that sets up a table with a single player

    """
    cards, table, rules, player = setup_table

    player.hit(key=1, new_card='10')
    player.hit(key=1, new_card='6')

    players_play_hands(table=table, rules=rules, cards=cards, dealer_hand=['J', 'J'], dealer_up_card='J')

    assert player.get_surrender() is True
    assert player.get_stand(key=1) is True
    assert player.get_hand(key=1) == ['10', '6']


def test_players_play_hands_split_non_aces(setup_table):
    """
    Tests the players_play_hands function when non-aces are split.

    Parameters
    ----------
    setup_table
        Fixture that sets up a table with a single player

    """
    cards, table, rules, player = setup_table

    player.hit(key=1, new_card='2')
    player.hit(key=1, new_card='2')

    players_play_hands(table=table, rules=rules, cards=cards, dealer_hand=['J', '4'], dealer_up_card='4')

    assert player.get_split(key=1) is True
    assert player.get_split(key=2) is True
    assert player.get_hand(key=1) == ['2', 'A', 'K']
    assert player.get_hand(key=2) == ['2', 'Q']


def test_players_play_hands_split_aces(setup_table):
    """
    Tests the players_play_hands function when aces are split.

    Parameters
    ----------
    setup_table
        Fixture that sets up a table with a single player

    """
    cards, table, rules, player = setup_table

    player.hit(key=1, new_card='A')
    player.hit(key=1, new_card='A')

    players_play_hands(table=table, rules=rules, cards=cards, dealer_hand=['J', 'J'], dealer_up_card='J')

    assert player.get_split(key=1) is True
    assert player.get_split(key=2) is True
    assert player.get_bet(key=1) == player.get_initial_bet()
    assert player.get_bet(key=2) == player.get_initial_bet()
    assert player.get_hand(key=1) == ['A', 'A']
    assert player.get_hand(key=2) == ['A', 'K']


def test_players_play_hands_double_after_split(setup_table):
    """
    Tests the players_play_hands function when a player has the ability to
    double after splitting.

    Parameters
    ----------
    setup_table
        Fixture that sets up a table with a single player

    """
    cards, table, rules, player = setup_table

    player.hit(key=1, new_card='2')
    player.hit(key=1, new_card='2')

    players_play_hands(table=table, rules=rules, cards=cards, dealer_hand=['J', '2'], dealer_up_card='2')

    assert player.get_split(key=1) is True
    assert player.get_split(key=2) is True
    assert player.get_hand(key=1) == ['2', 'A', 'K']
    assert player.get_hand(key=2) == ['2', 'Q', 'J']


def test_players_play_hands_double_down(setup_table):
    """
    Tests the players_play_hands function when a player has the ability to
    double down.

    Parameters
    ----------
    setup_table
        Fixture that sets up a table with a single player

    """
    cards, table, rules, player = setup_table

    player.hit(key=1, new_card='6')
    player.hit(key=1, new_card='4')

    players_play_hands(table=table, rules=rules, cards=cards, dealer_hand=['J', '2'], dealer_up_card='2')

    assert player.get_bet(key=1) == player.get_initial_bet() * 2
    assert player.get_hand(key=1) == ['6', '4', 'A']


def test_players_play_hands_stand(setup_table):
    """
    Tests the players_play_hands function when a player stands.

    Parameters
    ----------
    setup_table
        Fixture that sets up a table with a single player

    """
    cards, table, rules, player = setup_table

    player.hit(key=1, new_card='K')
    player.hit(key=1, new_card='K')

    players_play_hands(table=table, rules=rules, cards=cards, dealer_hand=['J', 'J'], dealer_up_card='J')

    assert player.get_stand(key=1)
    assert player.get_hand(key=1) == ['K', 'K']


def test_players_play_hands_bust(setup_table):
    """
    Tests the players_play_hands function when a player busts.

    Parameters
    ----------
    setup_table
        Fixture that sets up a table with a single player

    """
    cards, table, rules, player = setup_table

    player.hit(key=1, new_card='6')
    player.hit(key=1, new_card='6')

    players_play_hands(table=table, rules=rules, cards=cards, dealer_hand=['J', 'J'], dealer_up_card='J')

    assert player.get_busted(key=1)
    assert player.get_hand(key=1) == ['6', '6', 'A', 'K']


def test_players_play_hands_split_insufficient_funds(setup_table):
    """
    Tests the players_play_hands function when a player has insufficient
    funds to split their hand.

    Parameters
    ----------
    setup_table
        Fixture that sets up a table with a single player

    """
    cards, table, rules, player = setup_table
    player.set_bankroll(amount=0)

    player.hit(key=1, new_card='7')
    player.hit(key=1, new_card='7')

    players_play_hands(table=table, rules=rules, cards=cards, dealer_hand=['J', '2'], dealer_up_card='2')

    assert player.get_split(key=1) is False
    assert player.get_hand(key=1) == ['7', '7']


def test_players_play_hands_double_down_insufficient_funds(setup_table):
    """
    Tests the players_play_hands function when a player has insufficient
    funds to double down.

    Parameters
    ----------
    setup_table
        Fixture that sets up a table with a single player

    """
    cards, table, rules, player = setup_table
    player.set_bankroll(amount=0)

    player.hit(key=1, new_card='6')
    player.hit(key=1, new_card='4')

    players_play_hands(table=table, rules=rules, cards=cards, dealer_hand=['J', '2'], dealer_up_card='2')

    assert player.get_bet(key=1) == player.get_initial_bet()
    assert player.get_hand(key=1) == ['6', '4', 'A']


def test_players_play_hands_no_insurance(setup_table):
    """
    Tests the players_play_hands function when a player cannot
    buy insurance.

    Parameters
    ----------
    setup_table
        Fixture that sets up a table with a single player

    """
    cards, table, rules, player = setup_table
    rules.insurance = False

    player.set_count(count=1)
    player.insurance_count = 0

    player.hit(key=1, new_card='J')
    player.hit(key=1, new_card='J')

    players_play_hands(table=table, rules=rules, cards=cards, dealer_hand=['K', 'A'], dealer_up_card='A')

    assert player.get_insurance() is False
    assert player.get_stand(key=1) is True
    assert player.get_hand(key=1) == ['J', 'J']


def test_players_play_hands_no_late_surrender(setup_table):
    """
    Tests the players_play_hands function when a player cannot
    surrender late.

    Parameters
    ----------
    setup_table
        Fixture that sets up a table with a single player

    """
    cards, table, rules, player = setup_table
    rules.late_surrender = False

    player.hit(key=1, new_card='10')
    player.hit(key=1, new_card='6')

    players_play_hands(table=table, rules=rules, cards=cards, dealer_hand=['J', 'J'], dealer_up_card='J')

    assert player.get_surrender() is False
    assert player.get_stand(key=1) is True
    assert player.get_hand(key=1) == ['10', '6', 'A']


def test_players_play_hands_adjust_max_hands(setup_table):
    """
    Tests the players_play_hands function when a player has reached
    the maximum hands limit.

    Parameters
    ----------
    setup_table
        Fixture that sets up a table with a single player

    """
    cards, table, rules, player = setup_table
    rules.max_hands = 2

    player.hit(key=1, new_card='A')
    player.hit(key=1, new_card='A')

    players_play_hands(table=table, rules=rules, cards=cards, dealer_hand=['J', 'J'], dealer_up_card='J')

    assert player.get_split(key=1)
    assert player.get_split(key=2)
    assert player.get_hand(key=1) == ['A', 'A']
    assert player.get_hand(key=2) == ['A', 'K']


def test_players_play_hands_no_double_down(setup_table):
    """
    Tests the players_play_hands function when a player is unable to
    double down.

    Parameters
    ----------
    setup_table
        Fixture that sets up a table with a single player

    """
    cards, table, rules, player = setup_table
    rules.double_down = False

    player.hit(key=1, new_card='6')
    player.hit(key=1, new_card='4')

    players_play_hands(table=table, rules=rules, cards=cards, dealer_hand=['J', '2'], dealer_up_card='2')

    assert player.get_bet(key=1) == player.get_initial_bet()
    assert player.get_hand(key=1) == ['6', '4', 'A']


def test_players_play_hands_no_double_after_split(setup_table):
    """
    Tests the players_play_hands function when a player is unable to
    double after splitting.

    Parameters
    ----------
    setup_table
        Fixture that sets up a table with a single player

    """
    cards, table, rules, player = setup_table
    rules.double_after_split = False

    player.hit(key=1, new_card='2')
    player.hit(key=1, new_card='2')

    players_play_hands(table=table, rules=rules, cards=cards, dealer_hand=['J', '2'], dealer_up_card='2')

    assert player.get_split(key=1) is False
    assert player.get_hand(key=1) == ['2', '2', 'A', 'K']


def test_players_play_hands_resplit_aces(setup_table):
    """
    Tests the players_play_hands function when a player is able to
    re-split aces.

    Parameters
    ----------
    setup_table
        Fixture that sets up a table with a single player

    """
    cards, table, rules, player = setup_table
    rules.resplit_aces = True

    player.hit(key=1, new_card='A')
    player.hit(key=1, new_card='A')

    players_play_hands(table=table, rules=rules, cards=cards, dealer_hand=['J', 'J'], dealer_up_card='J')

    assert player.get_split(key=1) is True
    assert player.get_split(key=2) is True
    assert player.get_split(key=3) is True
    assert player.get_bet(key=1) == player.get_initial_bet()
    assert player.get_bet(key=2) == player.get_initial_bet()
    assert player.get_bet(key=3) == player.get_initial_bet()
    assert player.get_hand(key=1) == ['A', 'K']
    assert player.get_hand(key=2) == ['A', 'Q']
    assert player.get_hand(key=3) == ['A', 'J']


def test_dealer_turn_bust(setup_table):
    """
    Tests the dealer_turn function when all players bust.

    Parameters
    ----------
    setup_table
        Fixture that sets up a table with a single player

    """
    cards, table, rules, player = setup_table

    player.busted(key=1)
    assert player.get_busted(key=1) is True
    assert dealer_turn(table=table) is False


def test_dealer_turn_surrender(setup_table):
    """
    Tests the dealer_turn function when all players surrender.

    Parameters
    ----------
    setup_table
        Fixture that sets up a table with a single player

    """
    cards, table, rules, player = setup_table

    player.surrender()
    assert player.get_surrender() is True
    assert dealer_turn(table=table) is False


def test_dealer_turn_blackjack(setup_table):
    """
    Tests the dealer_turn function when all players have natural
    blackjack.

    Parameters
    ----------
    setup_table
        Fixture that sets up a table with a single player

    """
    cards, table, rules, player = setup_table

    player.natural_blackjack()
    assert player.get_natural_blackjack() is True
    assert dealer_turn(table=table) is False


def test_dealer_turn_player_other(setup_table):
    """
    Tests the dealer_turn function when one or more players
    do not bust, surrender, or have natural blackjack.

    Parameters
    ----------
    setup_table
        Fixture that sets up a table with a single player

    """
    cards, table, rules, player = setup_table

    player.hit(key=1, new_card='J')
    player.hit(key=1, new_card='J')
    player.stand(key=1)
    assert player.get_busted(key=1) is False
    assert player.get_surrender() is False
    assert player.get_natural_blackjack() is False
    assert player.get_stand(key=1) is True
    assert dealer_turn(table=table) is True


def test_dealer_plays_hand_s17(setup_table):
    """
    Tests the dealer_plays_hand function when a dealer stands
    on soft 17.

    Parameters
    ----------
    setup_table
        Fixture that sets up a table with a single player

    """
    cards, table, rules, player = setup_table

    assert dealer_plays_hand(rules=rules, cards=cards, dealer_hand=['8', '8'], dealer_hole_card='A') == ['8', '8', 'A']
    assert dealer_plays_hand(rules=rules, cards=cards, dealer_hand=['A', '6'], dealer_hole_card='A') == ['A', '6']
    assert dealer_plays_hand(rules=rules, cards=cards, dealer_hand=['J', 'J'], dealer_hole_card='A') == ['J', 'J']


def test_dealer_plays_hand_h17(setup_table):
    """
    Tests the dealer_plays_hand function when a dealer hits
    on soft 17.

    Parameters
    ----------
    setup_table
        Fixture that sets up a table with a single player

    """
    cards, table, rules, player = setup_table
    rules.s17 = False

    assert dealer_plays_hand(rules=rules, cards=cards, dealer_hand=['8', '8'], dealer_hole_card='A') == ['8', '8', 'A']
    assert dealer_plays_hand(rules=rules, cards=cards, dealer_hand=['A', '6'], dealer_hole_card='A') == ['A', '6', 'K']
    assert dealer_plays_hand(rules=rules, cards=cards, dealer_hand=['J', 'J'], dealer_hole_card='A') == ['J', 'J']


def test_compare_hands_insurance_dealer_and_player_blackjack(setup_table):
    """
    Tests the compare_hands function when a player buys insurance and both
    the dealer and player have natural blackjack.

    Parameters
    ----------
    setup_table
        Fixture that sets up a table with a single player

    """
    cards, table, rules, player = setup_table
    stats = SimulationStats(rules=rules)
    stats.create_player_key(player_key=player.get_name())
    stats.create_count_key(player_key=player.get_name(), count_key=0)

    player.set_count(count=0)
    player.insurance_count = 0
    player.hit(key=1, new_card='A')
    player.hit(key=1, new_card='K')
    player.insurance()
    player.natural_blackjack()
    player.increment_bankroll(amount=-0.5 * player.get_initial_bet())

    assert player.get_insurance() is True
    assert player.get_natural_blackjack() is True

    compare_hands(table=table, rules=rules, stats=stats, dealer_hand=['K', 'A'])

    assert player.get_bankroll() == 110


def test_compare_hands_insurance_dealer_blackjack_no_player_blackjack(setup_table):
    """
    Tests the compare_hands function when a player buys insurance and the dealer has
    a natural blackjack but the player does not.

    Parameters
    ----------
    setup_table
        Fixture that sets up a table with a single player

    """
    cards, table, rules, player = setup_table
    stats = SimulationStats(rules=rules)
    stats.create_player_key(player_key=player.get_name())
    stats.create_count_key(player_key=player.get_name(), count_key=0)

    player.set_count(count=0)
    player.insurance_count = 0
    player.hit(key=1, new_card='2')
    player.hit(key=1, new_card='2')
    player.insurance()
    player.increment_bankroll(amount=-0.5 * player.get_initial_bet())

    assert player.get_insurance() is True

    compare_hands(table=table, rules=rules, stats=stats, dealer_hand=['K', 'A'])

    assert player.get_bankroll() == 100


def test_compare_hands_insurance_no_dealer_blackjack_player_blackjack(setup_table):
    """
    Tests the compare_hands function when a player buys insurance and the player has
    a natural blackjack but the dealer does not.

    Parameters
    ----------
    setup_table
        Fixture that sets up a table with a single player

    """
    cards, table, rules, player = setup_table
    stats = SimulationStats(rules=rules)
    stats.create_player_key(player_key=player.get_name())
    stats.create_count_key(player_key=player.get_name(), count_key=0)

    player.set_count(count=0)
    player.insurance_count = 0
    player.hit(key=1, new_card='A')
    player.hit(key=1, new_card='K')
    player.insurance()
    player.natural_blackjack()
    player.increment_bankroll(amount=-0.5 * player.get_initial_bet())

    assert player.get_insurance() is True
    assert player.get_natural_blackjack() is True

    compare_hands(table=table, rules=rules, stats=stats, dealer_hand=['8', 'A'])

    assert player.get_bankroll() == 110


def test_compare_hands_insurance_no_dealer_blackjack_no_player_blackjack(setup_table):
    """
    Tests the compare_hands function when a player buys insurance and neither the
    dealer or player have natural blackjack.

    Parameters
    ----------
    setup_table
        Fixture that sets up a table with a single player

    """
    cards, table, rules, player = setup_table
    stats = SimulationStats(rules=rules)
    stats.create_player_key(player_key=player.get_name())
    stats.create_count_key(player_key=player.get_name(), count_key=0)

    player.set_count(count=0)
    player.insurance_count = 0
    player.hit(key=1, new_card='8')
    player.hit(key=1, new_card='A')
    player.insurance()
    player.increment_bankroll(amount=-0.5 * player.get_initial_bet())

    assert player.get_insurance() is True

    compare_hands(table=table, rules=rules, stats=stats, dealer_hand=['8', 'A'])

    assert player.get_bankroll() == 95


def test_compare_hands_surrender(setup_table):
    """
    Tests the compare_hands function when a player surrenders.

    Parameters
    ----------
    setup_table
        Fixture that sets up a table with a single player

    """
    cards, table, rules, player = setup_table
    stats = SimulationStats(rules=rules)
    stats.create_player_key(player_key=player.get_name())
    stats.create_count_key(player_key=player.get_name(), count_key=0)

    player.hit(key=1, new_card='10')
    player.hit(key=1, new_card='6')
    player.surrender()
    assert player.get_surrender() is True

    compare_hands(table=table, rules=rules, stats=stats, dealer_hand=['J', 'J'])

    assert player.get_bankroll() == 95


def test_compare_hands_player_and_dealer_blackjack(setup_table):
    """
    Tests the compare_hands function when a player and dealer both
    have natural blackjack.

    Parameters
    ----------
    setup_table
        Fixture that sets up a table with a single player

    """
    cards, table, rules, player = setup_table
    stats = SimulationStats(rules=rules)
    stats.create_player_key(player_key=player.get_name())
    stats.create_count_key(player_key=player.get_name(), count_key=0)

    player.hit(key=1, new_card='A')
    player.hit(key=1, new_card='K')
    player.natural_blackjack()
    assert player.get_natural_blackjack() is True

    compare_hands(table=table, rules=rules, stats=stats, dealer_hand=['A', 'K'])

    assert player.get_bankroll() == 100


def test_compare_hands_player_blackjack_dealer_three_plus_card_21_heads_up(setup_table):
    """
    Tests the compare_hands function when a player is playing a dealer heads
    up and has a natural blackjack but the dealer has a three or more card 21.

    Parameters
    ----------
    setup_table
        Fixture that sets up a table with a single player

    """
    cards, table, rules, player = setup_table
    stats = SimulationStats(rules=rules)
    stats.create_player_key(player_key=player.get_name())
    stats.create_count_key(player_key=player.get_name(), count_key=0)

    player.hit(key=1, new_card='A')
    player.hit(key=1, new_card='K')
    player.natural_blackjack()
    assert player.get_natural_blackjack() is True

    with pytest.raises(ValueError):
        compare_hands(table=table, rules=rules, stats=stats, dealer_hand=['7', '7', '7'])

    assert player.get_bankroll() == 90


def test_compare_hands_player_blackjack_dealer_three_plus_card_21_multi(setup_table):
    """
    Tests the compare_hands function when a player is playing at a table with multiple
    players and the player has a natural blackjack and the dealer has a three or more
    card 21.

    Parameters
    ----------
    setup_table
        Fixture that sets up a table with a single player

    """
    cards, table, rules, player = setup_table
    stats = SimulationStats(rules=rules)

    new_player = Player(
                    name='Player 2',
                    rules=rules,
                    bankroll=100,
                    min_bet=10
    )

    table.add_player(player=new_player)

    for player in table.get_players():
        stats.create_player_key(player_key=player.get_name())
        stats.create_count_key(player_key=player.get_name(), count_key=0)
        if player.get_name() == 'Player 1':
            player.hit(key=1, new_card='A')
            player.hit(key=1, new_card='K')
            player.natural_blackjack()
            assert player.get_natural_blackjack() is True
        else:
            player.initial_bet(amount=10)
            player.hit(key=1, new_card='J')
            player.hit(key=1, new_card='J')

    compare_hands(table=table, rules=rules, stats=stats, dealer_hand=['7', '7', '7'])

    for player in table.get_players():
        if player.get_name() == 'Player 1':
            assert player.get_bankroll() == 115
        else:
            assert player.get_bankroll() == 90


def test_compare_hands_player_and_dealer_three_plus_card_21(setup_table):
    """
    Tests the compare_hands function when a player and dealer both have
    three or more card 21.

    Parameters
    ----------
    setup_table
        Fixture that sets up a table with a single player

    """
    cards, table, rules, player = setup_table
    stats = SimulationStats(rules=rules)
    stats.create_player_key(player_key=player.get_name())
    stats.create_count_key(player_key=player.get_name(), count_key=0)

    player.hit(key=1, new_card='7')
    player.hit(key=1, new_card='7')
    player.hit(key=1, new_card='7')

    compare_hands(table=table, rules=rules, stats=stats, dealer_hand=['7', '7', '7'])

    assert player.get_bankroll() == 100


def test_compare_hands_player_blackjack(setup_table):
    """
    Tests the compare_hands function when a player has a natural blackjack.

    Parameters
    ----------
    setup_table
        Fixture that sets up a table with a single player

    """
    cards, table, rules, player = setup_table
    stats = SimulationStats(rules=rules)
    stats.create_player_key(player_key=player.get_name())
    stats.create_count_key(player_key=player.get_name(), count_key=0)

    player.hit(key=1, new_card='A')
    player.hit(key=1, new_card='K')
    player.natural_blackjack()
    assert player.get_natural_blackjack() is True

    compare_hands(table=table, rules=rules, stats=stats, dealer_hand=['J', 'J'])

    assert player.get_bankroll() == 115


def test_compare_hands_dealer_blackjack(setup_table):
    """
    Tests the compare_hands function when a dealer has a natural blackjack.

    Parameters
    ----------
    setup_table
        Fixture that sets up a table with a single player

    """
    cards, table, rules, player = setup_table
    stats = SimulationStats(rules=rules)
    stats.create_player_key(player_key=player.get_name())
    stats.create_count_key(player_key=player.get_name(), count_key=0)

    player.hit(key=1, new_card='J')
    player.hit(key=1, new_card='J')

    compare_hands(table=table, rules=rules, stats=stats, dealer_hand=['A', 'K'])

    assert player.get_bankroll() == 90


def test_compare_hands_player_bust(setup_table):
    """
    Tests the compare_hands function when a player busts.

    Parameters
    ----------
    setup_table
        Fixture that sets up a table with a single player

    """
    cards, table, rules, player = setup_table
    stats = SimulationStats(rules=rules)
    stats.create_player_key(player_key=player.get_name())
    stats.create_count_key(player_key=player.get_name(), count_key=0)

    player.hit(key=1, new_card='8')
    player.hit(key=1, new_card='7')
    player.hit(key=1, new_card='K')

    compare_hands(table=table, rules=rules, stats=stats, dealer_hand=['J', 'J'])

    assert player.get_bankroll() == 90


def test_compare_hands_dealer_bust(setup_table):
    """
    Tests the compare_hands function when a dealer busts.

    Parameters
    ----------
    setup_table
        Fixture that sets up a table with a single player

    """
    cards, table, rules, player = setup_table
    stats = SimulationStats(rules=rules)
    stats.create_player_key(player_key=player.get_name())
    stats.create_count_key(player_key=player.get_name(), count_key=0)

    player.hit(key=1, new_card='J')
    player.hit(key=1, new_card='J')

    compare_hands(table=table, rules=rules, stats=stats, dealer_hand=['K', '5', 'J'])

    assert player.get_bankroll() == 110


def test_compare_hands_push(setup_table):
    """
    Tests the compare_hands function when a player and dealer tie.

    Parameters
    ----------
    setup_table
        Fixture that sets up a table with a single player

    """
    cards, table, rules, player = setup_table
    stats = SimulationStats(rules=rules)
    stats.create_player_key(player_key=player.get_name())
    stats.create_count_key(player_key=player.get_name(), count_key=0)

    player.hit(key=1, new_card='J')
    player.hit(key=1, new_card='J')

    compare_hands(table=table, rules=rules, stats=stats, dealer_hand=['J', 'J'])

    assert player.get_bankroll() == 100


def test_compare_hands_player_showdown_win(setup_table):
    """
    Tests the compare_hands function when a player and dealer both
    have hand totals below 21 but the player's hand total beats the
    dealer's hand total.

    Parameters
    ----------
    setup_table
        Fixture that sets up a table with a single player

    """
    cards, table, rules, player = setup_table
    stats = SimulationStats(rules=rules)
    stats.create_player_key(player_key=player.get_name())
    stats.create_count_key(player_key=player.get_name(), count_key=0)

    player.hit(key=1, new_card='J')
    player.hit(key=1, new_card='J')

    compare_hands(table=table, rules=rules, stats=stats, dealer_hand=['J', '9'])

    assert player.get_bankroll() == 110


def test_compare_hands_dealer_showdown_win(setup_table):
    """
    Tests the compare_hands function when a player and dealer both
    have hand totals below 21 but the dealer's hand total beats the
    player's hand total.

    Parameters
    ----------
    setup_table
        Fixture that sets up a table with a single player

    """
    cards, table, rules, player = setup_table
    stats = SimulationStats(rules=rules)
    stats.create_player_key(player_key=player.get_name())
    stats.create_count_key(player_key=player.get_name(), count_key=0)

    player.hit(key=1, new_card='J')
    player.hit(key=1, new_card='9')

    compare_hands(table=table, rules=rules, stats=stats, dealer_hand=['J', 'J'])

    assert player.get_bankroll() == 90
