import random
import pytest
from table import Table
from house_rules import HouseRules
from player import Player
from cards import Cards
from gameplay import deal_hands, players_play_hands, dealer_turn, dealer_plays_hand, compare_hands
from helper import count_hand


def test_deal_hands():
    """
    Tests the deal_hands function.

    """
    r = HouseRules(
        shoe_size=4,
        bet_limits=[10, 500]
    )
    c = Cards(rules=r)
    t = Table()
    p = [
        Player(
            name='First to act',
            rules=r,
            bankroll=100,
            min_bet=10
        ),
        Player(
            name='Second to act',
            rules=r,
            bankroll=100,
            min_bet=10
        ),
        Player(
            name='Third to act',
            rules=r,
            bankroll=100,
            min_bet=10
        )
    ]

    for player in p:
        t.add_player(player=player)

    dealer_hand = deal_hands(table=t, cards=c)

    for player in p:
        if player.name == 'First to act':
            assert player.get_hand(key=1) == [1, 10]
        elif player.name == 'Second to act':
            assert player.get_hand(key=1) == [13, 9]
        else:
            assert player.get_hand(key=1) == [12, 8]

    assert dealer_hand == [11, 7]


@pytest.fixture
def setup_table():
    """
    Fixture that sets up a table with a single player.

    """
    r = HouseRules(
        shoe_size=4,
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
        dealer_shows_hole_card=True
    )
    c = Cards(rules=r)
    t = Table()
    p = Player(
        name='Player 1',
        rules=r,
        bankroll=100,
        min_bet=10
    )
    t.add_player(player=p)
    p.set_hand()
    p.stats.create_count_key(count_key=0)
    return c, t, r, p


@pytest.mark.parametrize('insurance, player_count, pre_insurance_count, expected',
                         [
                             (True, 0, 1, True),  # player buys insurance
                             (True, 1, 0, False),  # player does not buy insurance
                             (False, None, None, False),  # insurance not available
                         ])
def test_players_play_hands_insurance(
        insurance, player_count, pre_insurance_count, expected
):
    """
    Tests the insurance option within the players_play_hands function.

    """
    r = HouseRules(
        shoe_size=4,
        bet_limits=[10, 500],
        insurance=insurance
    )
    c = Cards(rules=r)
    t = Table()
    p = Player(
        name='Player 1',
        rules=r,
        bankroll=100,
        min_bet=10,
        insurance=player_count
    )
    t.add_player(player=p)
    p.pre_insurance_count = pre_insurance_count
    p.stats.create_count_key(count_key=0)  # count before betting
    p.stats.create_count_key(count_key=pre_insurance_count)  # count before insurance bet

    p.set_hand()
    p.hit(key=1, new_card=2)
    p.hit(key=1, new_card=2)

    players_play_hands(
        table=t,
        rules=r,
        cards=c,
        dealer_hand=[11, 1],
        dealer_up_card=1
    )

    assert p.get_insurance() is expected


@pytest.mark.parametrize('player_cards, dealer_cards, expected',
                         [
                             ([13, 1], [11, 11], True),  # player natural blackjack
                             ([13, 1], [13, 1], True),  # player and dealer natural blackjack
                             ([6, 4], [11, 11], False)  # player has 3+ card 21
                         ])
def test_players_play_hands_21(
        setup_table, player_cards, dealer_cards, expected
):
    """
    Tests the players_play_hands function when a player has 21.

    """
    c, t, r, p = setup_table

    p.hit(key=1, new_card=player_cards[0])
    p.hit(key=1, new_card=player_cards[1])

    players_play_hands(
        table=t,
        rules=r,
        cards=c,
        dealer_hand=dealer_cards,
        dealer_up_card=dealer_cards[1]
    )

    assert p.get_natural_blackjack() is expected
    assert count_hand(p.get_hand(key=1))[0] == 21


@pytest.mark.parametrize('late_surrender, expected_surrender, expected_hand',
                         [
                             (True, True, [10, 6]),  # player surrenders
                             (False, False, [10, 6, 1])  # late surrender not available
                         ])
def test_players_play_hands_surrender(
        late_surrender, expected_surrender, expected_hand
):
    """
    Tests the late surrender option within the players_play_hands function.

    """
    r = HouseRules(
        shoe_size=4,
        bet_limits=[10, 500],
        late_surrender=late_surrender
    )
    c = Cards(rules=r)
    t = Table()
    p = Player(
        name='Player 1',
        rules=r,
        bankroll=100,
        min_bet=10
    )
    t.add_player(player=p)
    p.stats.create_count_key(count_key=0)

    p.set_hand()
    p.hit(key=1, new_card=10)
    p.hit(key=1, new_card=6)

    players_play_hands(
        table=t,
        rules=r,
        cards=c,
        dealer_hand=[11, 11],
        dealer_up_card=11
    )

    assert p.get_surrender() is expected_surrender
    assert p.get_hand(key=1) == expected_hand


@pytest.mark.parametrize('resplit_aces, max_hands, player_cards, fixed_deck, expected_split, expected_hands',
                         [
                             (False, 4, [2, 2], False, True, [[2, 1, 13], [2, 12]]),  # split non-aces
                             (False, 4, [1, 1], False, True, [[1, 1], [1, 13]]),  # cannot re-split aces
                             (True, 4, [1, 1], False, True, [[1, 13], [1, 12], [1, 11]]),  # re-split aces
                             (True, 3, [1, 1], True, True, [[1, 1], [1, 1], [1, 1]]),  # 3 max hands
                         ])
def test_players_play_hands_split(
        resplit_aces, max_hands, player_cards, fixed_deck, expected_split, expected_hands
):
    """
    Tests the players_play_hands function when a player has the option to
    split or re-split their hand.

    """
    r = HouseRules(
        shoe_size=4,
        bet_limits=[10, 500],
        max_hands=max_hands,
        resplit_aces=resplit_aces
    )
    c = Cards(rules=r)
    t = Table()
    p = Player(
        name='Player 1',
        rules=r,
        bankroll=100,
        min_bet=10
    )
    t.add_player(player=p)
    p.stats.create_count_key(count_key=0)

    if fixed_deck:
        random.seed(27418)  # 4 aces dealt in a row, would be 6 hands if no max hands limit
        c.shuffle()

    p.set_hand()
    p.hit(key=1, new_card=player_cards[0])
    p.hit(key=1, new_card=player_cards[1])

    players_play_hands(
        table=t,
        rules=r,
        cards=c,
        dealer_hand=[11, 4],
        dealer_up_card=4
    )

    for key in p.hands_dict:
        assert p.get_split(key=key) is expected_split
        assert p.get_hand(key=key) == expected_hands[key - 1]


@pytest.mark.parametrize('double_after_split, expected_split, expected_hands',
                         [
                             (True, True, [[2, 1, 13], [2, 12, 11]]),  # player can double after split
                             (False, False, [[2, 2, 1, 13]])  # player cannot double after split
                         ])
def test_players_play_hands_double_after_split(
        double_after_split, expected_split, expected_hands
):
    """
    Tests the double after splitting option within the players_play_hands function.

    """
    r = HouseRules(
        shoe_size=4,
        bet_limits=[10, 500],
        double_after_split=double_after_split
    )
    c = Cards(rules=r)
    t = Table()
    p = Player(
        name='Player 1',
        rules=r,
        bankroll=100,
        min_bet=10
    )
    t.add_player(player=p)
    p.stats.create_count_key(count_key=0)

    p.set_hand()
    p.hit(key=1, new_card=2)
    p.hit(key=1, new_card=2)

    players_play_hands(
        table=t,
        rules=r,
        cards=c,
        dealer_hand=[11, 2],
        dealer_up_card=2
    )

    for key in p.hands_dict:
        assert p.get_split(key=key) is expected_split
        assert p.get_hand(key=key) == expected_hands[key - 1]


@pytest.mark.parametrize('double_down, expected',
                         [
                             (True, True),  # player doubles down
                             (False, False),  # player cannot double down
                         ])
def test_players_play_hands_double_down(double_down, expected):
    """
    Tests the double down option within the players_play_hands function.

    """
    r = HouseRules(
        shoe_size=4,
        bet_limits=[10, 500],
        double_down=double_down
    )
    c = Cards(rules=r)
    t = Table()
    p = Player(
        name='Player 1',
        rules=r,
        bankroll=100,
        min_bet=10
    )
    t.add_player(player=p)
    p.stats.create_count_key(count_key=0)

    p.set_hand()
    p.hit(key=1, new_card=6)
    p.hit(key=1, new_card=4)

    players_play_hands(
        table=t,
        rules=r,
        cards=c,
        dealer_hand=[11, 2],
        dealer_up_card=2
    )

    assert p.get_double_down(key=1) == expected


def test_players_play_hands_stand(setup_table):
    """
    Tests the players_play_hands function when a player stands.

    """
    c, t, r, p = setup_table

    p.hit(key=1, new_card=13)
    p.hit(key=1, new_card=13)

    players_play_hands(
        table=t,
        rules=r,
        cards=c,
        dealer_hand=[11, 11],
        dealer_up_card=11
    )

    assert p.get_stand(key=1) is True
    assert p.get_hand(key=1) == [13, 13]


def test_players_play_hands_bust(setup_table):
    """
    Tests the players_play_hands function when a player busts.

    """
    c, t, r, p = setup_table

    p.hit(key=1, new_card=6)
    p.hit(key=1, new_card=6)

    players_play_hands(
        table=t,
        rules=r,
        cards=c,
        dealer_hand=[11, 11],
        dealer_up_card=11
    )

    assert p.get_busted(key=1) is True
    assert count_hand(p.get_hand(key=1))[0] > 21


@pytest.mark.parametrize('player_busted, player_surrender, player_or_dealer_natural_blackjack, expected',
                         [
                             (True, False, False, False),  # player busts
                             (False, True, False, False),  # player surrenders
                             (False, False, True, False),  # player or dealer has natural blackjack
                             (False, False, False, True)  # none of the above
                         ])
def test_dealer_turn_bust(
        setup_table, player_busted, player_surrender, player_or_dealer_natural_blackjack, expected
):
    """
    Tests the dealer_turn function.

    """
    c, t, r, p = setup_table

    if player_busted:
        p.set_busted(key=1)

    elif player_surrender:
        p.set_surrender()

    elif player_or_dealer_natural_blackjack:
        p.set_settled_natural_blackjack()

    else:
        p.set_stand(key=1)

    assert dealer_turn(table=t) is expected


@pytest.mark.parametrize('s17, dealer_hand, expected',
                         [
                             (True, [1, 6], 17),  # dealer stands on soft 17
                             (False, [1, 6], 18)  # dealer hits on soft 17
                         ])
def test_dealer_plays_hand(s17, dealer_hand, expected):
    """
    Tests the dealer_plays_hand function when a dealer hits or stands
    on soft 17.

    """
    r = HouseRules(
        shoe_size=4,
        bet_limits=[10, 500],
        s17=s17
    )
    c = Cards(rules=r)
    t = Table()
    p = Player(
        name='Player 1',
        rules=r,
        bankroll=100,
        min_bet=10
    )
    t.add_player(player=p)
    p.stats.create_count_key(count_key=0)

    dealer_hand = dealer_plays_hand(
        rules=r,
        cards=c,
        dealer_hole_card=dealer_hand[1],
        dealer_hand=dealer_hand
    )

    assert dealer_hand == expected


@pytest.mark.parametrize('player_hand, dealer_hand, dealer_total, expected_net_winnings, expected_overall_bet, '
                         'expected_rounds, expected_split_hands',
                         [
                             ([7, 5], [11, 11], 20, -1, 1, 1, 0),  # player busts
                             ([7, 5], [1, 13, 1], 22, -1, 1, 1, 0),  # both player and dealer bust
                             ([11, 11], [1, 13, 1], 22, 1, 1, 1, 0)  # dealer busts
                         ]
                         )
def test_compare_hands_bust(
        setup_table, player_hand, dealer_hand, dealer_total, expected_net_winnings, expected_overall_bet,
        expected_rounds, expected_split_hands
):
    """
    Tests the compare_hands function when either a player and/or dealer bust.

    """
    c, t, r, p = setup_table

    p.hit(key=1, new_card=player_hand[0])
    p.hit(key=1, new_card=player_hand[1])

    players_play_hands(
        table=t,
        rules=r,
        cards=c,
        dealer_hand=dealer_hand,
        dealer_up_card=dealer_hand[1]
    )

    compare_hands(table=t, dealer_total=dealer_total)

    assert p.stats.results_dict[0]['net winnings'] == expected_net_winnings
    assert p.stats.results_dict[0]['overall bet'] == expected_overall_bet
    assert p.stats.results_dict[0]['number of rounds'] == expected_rounds
    assert p.stats.results_dict[0]['number of split hands'] == expected_split_hands


def test_compare_hands_push(setup_table):
    """
    Tests the compare_hands function when a player and dealer tie.

    """
    c, t, r, p = setup_table

    p.hit(key=1, new_card=11)
    p.hit(key=1, new_card=11)

    compare_hands(table=t, dealer_total=20)

    assert p.stats.results_dict[0]['net winnings'] == 0
    assert p.stats.results_dict[0]['overall bet'] == 1
    assert p.stats.results_dict[0]['number of rounds'] == 1
    assert p.stats.results_dict[0]['number of split hands'] == 0


@pytest.mark.parametrize('player_hand, dealer_hand, dealer_total, expected_net_winnings, expected_overall_bet, '
                         'expected_rounds, expected_split_hands',
                         [
                             ([11, 11], [11, 9], 19, 1, 1, 1, 0),  # player showdown win
                             ([11, 9], [11, 11], 20, -1, 1, 1, 0)  # dealer showdown win
                         ])
def test_compare_hands_showdown(
        setup_table, player_hand, dealer_hand, dealer_total, expected_net_winnings,
        expected_overall_bet, expected_rounds, expected_split_hands
):
    """
    Tests the compare_hands function when a player and dealer both
    have hand totals less than 21.

    """
    c, t, r, p = setup_table

    p.hit(key=1, new_card=player_hand[0])
    p.hit(key=1, new_card=player_hand[1])

    compare_hands(table=t, dealer_total=dealer_total)

    assert p.stats.results_dict[0]['net winnings'] == expected_net_winnings
    assert p.stats.results_dict[0]['overall bet'] == expected_overall_bet
    assert p.stats.results_dict[0]['number of rounds'] == expected_rounds
    assert p.stats.results_dict[0]['number of split hands'] == expected_split_hands
