import pytest
from table import Table
from house_rules import HouseRules
from player import Player
from cards import Cards
from counting_strategy import CountingStrategy
from simulation_stats import SimulationStats
from gameplay import players_place_bets, deal_hands, players_play_hands, dealer_turn, dealer_plays_hand, compare_hands
from helper import max_count_hand


@pytest.mark.parametrize('player_bankroll, player_min_bet, expected_bankroll, expected_table_size',
                         [
                             (5, 10, 5, 0),  # player cannot make minimum bet
                             (20, 10, 10, 1),  # player's bet is within table constraints
                             (490, 500, 0, 1)  # player cannot make maximum bet
                         ])
def test_players_place_bets(player_bankroll, player_min_bet, expected_bankroll, expected_table_size):
    """
    Tests the players_place_bets function.

    """
    c = Cards(shoe_size=4)
    cs = CountingStrategy(cards=c)
    t = Table()
    r = HouseRules(bet_limits=[10, 500])
    p = Player(
            name='Player 1',
            rules=r,
            bankroll=1000,
            min_bet=player_min_bet
    )
    t.add_player(player=p)
    p.set_bankroll(amount=player_bankroll)

    players_place_bets(table=t, rules=r, counting_strategy=cs)

    assert p.get_bankroll() == expected_bankroll
    assert len(t.get_players()) == expected_table_size


def test_deal_hands():
    """
    Tests the deal_hands function.

    """
    c = Cards(shoe_size=4)
    t = Table()
    r = HouseRules(bet_limits=[10, 500])
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
        player.create_hand(amount=10)

    dealer_hand = deal_hands(table=t, cards=c)

    for player in p:
        if player.get_name() == 'First to act':
            assert player.get_hand(key=1) == ['A', '10']
        elif player.get_name() == 'Second to act':
            assert player.get_hand(key=1) == ['K', '9']
        else:
            assert player.get_hand(key=1) == ['Q', '8']

    assert dealer_hand == ['J', '7']


@pytest.fixture
def setup_table():
    """
    Fixture that sets up a table with a single player.

    """
    c = Cards(shoe_size=4)
    t = Table()
    r = HouseRules(
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
    p = Player(
            name='Player 1',
            rules=r,
            bankroll=100,
            min_bet=10
    )

    t.add_player(player=p)
    p.initial_bet(amount=10)  # creates hand

    s = SimulationStats(rules=r)
    s.create_player_key(player_key=p.get_name())
    s.create_count_key(player_key=p.get_name(), count_key=0)

    return c, t, r, p, s


@pytest.mark.parametrize('insurance, count, insurance_count, player_bankroll, expected_insurance, expected_bankroll',
                         [
                             (True, 1, 0, 90, True, 85),  # player buys insurance
                             (True, 0, 1, 90, False, 90),  # player does not buy insurance
                             (True, 1, 0, 0, False, 0),  # player has insufficient funds to buy insurance
                             (False, None, None, 90, False, 90),  # insurance not available
                         ])
def test_players_play_hands_insurance(
        setup_table, insurance, count, insurance_count, player_bankroll, expected_insurance, expected_bankroll
):
    """
    Tests the insurance option within the players_play_hands function.

    """
    c, t, r, p, s = setup_table
    r.insurance = insurance

    p.set_count(count=count)
    p.insurance_count = insurance_count
    p.set_bankroll(amount=player_bankroll)
    p.hit(key=1, new_card='2')
    p.hit(key=1, new_card='2')

    players_play_hands(
        table=t,
        rules=r,
        cards=c,
        dealer_hand=['J', 'A'],
        dealer_up_card='A'
    )

    assert p.get_insurance() is expected_insurance
    assert p.get_bankroll() == expected_bankroll


@pytest.mark.parametrize('player_cards, dealer_cards, expected_natural_blackjack',
                         [
                             (['K', 'A'], ['J', 'J'], True),  # player natural blackjack
                             (['K', 'A'], ['K', 'A'], True),  # player and dealer natural blackjack
                             (['6', '4'], ['J', 'J'], False)  # player has 3+ card 21
                         ])
def test_players_play_hands_21(
        setup_table, player_cards, dealer_cards, expected_natural_blackjack
):
    """
    Tests the players_play_hands function when a player has 21.

    """
    c, t, r, p, s = setup_table

    p.hit(key=1, new_card=player_cards[0])
    p.hit(key=1, new_card=player_cards[1])

    players_play_hands(
        table=t,
        rules=r,
        cards=c,
        dealer_hand=dealer_cards,
        dealer_up_card=dealer_cards[1]
    )

    assert p.get_natural_blackjack() is expected_natural_blackjack
    assert max_count_hand(p.get_hand(key=1)) == 21


@pytest.mark.parametrize('late_surrender, expected_surrender, expected_hand',
                         [
                             (True, True, ['10', '6']),  # player surrenders
                             (False, False, ['10', '6', 'A'])  # late surrender not available
                         ])
def test_players_play_hands_surrender(
        setup_table, late_surrender, expected_surrender, expected_hand
):
    """
    Tests the late surrender option within the players_play_hands function.

    """
    c, t, r, p, s = setup_table
    r.late_surrender = late_surrender

    p.hit(key=1, new_card='10')
    p.hit(key=1, new_card='6')

    players_play_hands(
        table=t,
        rules=r,
        cards=c,
        dealer_hand=['J', 'J'],
        dealer_up_card='J'
    )

    assert p.get_surrender() is expected_surrender
    assert p.get_hand(key=1) == expected_hand


@pytest.mark.parametrize('resplit_aces, max_hands, player_cards, player_bankroll, expected_split, expected_hands',
                         [
                             (False, 4, ['2', '2'], 90, True, [['2', 'A', 'K'], ['2', 'Q']]),  # split non-aces
                             (False, 4, ['A', 'A'], 90, True, [['A', 'A'], ['A', 'K']]),  # split aces, cannot re-split
                             (True, 4, ['A', 'A'], 90, True, [['A', 'K'], ['A', 'Q'], ['A', 'J']]),  # re-split aces
                             (True, 2, ['A', 'A'], 90, True, [['A', 'A', 'K'], ['A', 'Q']]),  # 2 max hands
                             (False, 4, ['7', '7'], 0, False, [['7', '7']])  # insufficient funds to split
                         ])
def test_players_play_hands_split(
        setup_table, resplit_aces, max_hands, player_cards, player_bankroll, expected_split, expected_hands
):
    """
    Tests the players_play_hands function when a player has the option to
    split or re-split their hand.

    """
    c, t, r, p, s = setup_table
    r.resplit_aces = resplit_aces
    r.max_hands = max_hands

    p.set_bankroll(amount=player_bankroll)
    p.hit(key=1, new_card=player_cards[0])
    p.hit(key=1, new_card=player_cards[1])

    players_play_hands(
        table=t,
        rules=r,
        cards=c,
        dealer_hand=['J', '4'],
        dealer_up_card='4'
    )

    for key in p.get_hands_dict().keys():
        assert p.get_split(key=key) is expected_split
        assert p.get_hand(key=key) == expected_hands[key - 1]
        assert p.get_bet(key=key) == 10


@pytest.mark.parametrize('double_after_split, expected_split, expected_hands',
                         [
                             (True, True, [['2', 'A', 'K'], ['2', 'Q', 'J']]),  # player can double after split
                             (False, False, [['2', '2', 'A', 'K']])  # player cannot double after split
                         ])
def test_players_play_hands_double_after_split(
        setup_table, double_after_split, expected_split, expected_hands
):
    """
    Tests the double after splitting option within the players_play_hands function.

    """
    c, t, r, p, s = setup_table
    r.double_after_split = double_after_split

    p.hit(key=1, new_card='2')
    p.hit(key=1, new_card='2')

    players_play_hands(
        table=t,
        rules=r,
        cards=c,
        dealer_hand=['J', '2'],
        dealer_up_card='2'
    )

    for key in p.get_hands_dict().keys():
        assert p.get_split(key=key) is expected_split
        assert p.get_hand(key=key) == expected_hands[key - 1]


@pytest.mark.parametrize('double_down, player_bankroll, expected_bet',
                         [
                             (True, 90, 20),  # player doubles down
                             (True, 0, 10),  # player has insufficient funds to double down
                             (False, 90, 10),  # player cannot double down
                         ])
def test_players_play_hands_double_down(
        setup_table, double_down, player_bankroll, expected_bet
):
    """
    Tests the double down option within the players_play_hands function.

    """
    c, t, r, p, s = setup_table
    r.double_down = double_down

    p.set_bankroll(amount=player_bankroll)
    p.hit(key=1, new_card='6')
    p.hit(key=1, new_card='4')

    players_play_hands(
        table=t,
        rules=r,
        cards=c,
        dealer_hand=['J', '2'],
        dealer_up_card='2'
    )

    assert p.get_bet(key=1) == expected_bet


def test_players_play_hands_stand(setup_table):
    """
    Tests the players_play_hands function when a player stands.

    """
    c, t, r, p, s = setup_table

    p.hit(key=1, new_card='K')
    p.hit(key=1, new_card='K')

    players_play_hands(
        table=t,
        rules=r,
        cards=c,
        dealer_hand=['J', 'J'],
        dealer_up_card='J'
    )

    assert p.get_stand(key=1) is True
    assert p.get_hand(key=1) == ['K', 'K']


def test_players_play_hands_bust(setup_table):
    """
    Tests the players_play_hands function when a player busts.

    """
    c, t, r, p, s = setup_table

    p.hit(key=1, new_card='6')
    p.hit(key=1, new_card='6')

    players_play_hands(
        table=t,
        rules=r,
        cards=c,
        dealer_hand=['J', 'J'],
        dealer_up_card='J'
    )

    assert p.get_busted(key=1) is True
    assert max_count_hand(p.get_hand(key=1)) > 21


@pytest.mark.parametrize('player_busted, player_surrender, player_natural_blackjack, expected',
                         [
                             (True, False, False, False),  # player busts
                             (False, True, False, False),  # player surrenders
                             (False, False, True, False),  # player has natural blackjack
                             (False, False, False, True)  # player does not bust, surrender, or have a natural blackjack
                         ])
def test_dealer_turn_bust(
        setup_table, player_busted, player_surrender, player_natural_blackjack, expected
):
    """
    Tests the dealer_turn function.

    """
    c, t, r, p, s = setup_table

    if player_busted:
        p.busted(key=1)

    elif player_surrender:
        p.surrender()

    elif player_natural_blackjack:
        p.natural_blackjack()

    else:
        p.stand(key=1)

    assert dealer_turn(table=t) is expected


@pytest.mark.parametrize('s17, dealer_hand, expected_hand',
                         [
                             (True, ['A', '6'], ['A', '6']),  # dealer stands on soft 17
                             (False, ['A', '6'], ['A', '6', 'A'])  # dealer hits on soft 17
                         ])
def test_dealer_plays_hand(setup_table, s17, dealer_hand, expected_hand):
    """
    Tests the dealer_plays_hand function when a dealer hits or stands
    on soft 17.

    """
    c, t, r, p, s = setup_table
    r.s17 = s17

    dealer_hand = dealer_plays_hand(
                                rules=r,
                                cards=c,
                                dealer_hand=dealer_hand,
                                dealer_hole_card=dealer_hand[1]
    )

    assert dealer_hand == expected_hand


@pytest.mark.parametrize('player_hand, dealer_hand, expected_natural_blackjack, expected_bankroll',
                         [
                             (['A', 'K'], ['K', 'A'], True, 110),  # dealer and player natural blackjack
                             (['2', '2'], ['K', 'A'], False, 100),  # dealer natural blackjack
                             (['A', 'K'], ['8', 'A'], True, 110),  # player natural blackjack
                             (['2', '2'], ['8', 'A'], False, 85)   # no natural blackjack
                         ])
def test_compare_hands_insurance(
        setup_table, player_hand, dealer_hand, expected_natural_blackjack, expected_bankroll
):
    """
    Tests the compare_hands function when a player buys insurance.

    """
    c, t, r, p, s = setup_table

    p.set_count(count=0)
    p.insurance_count = 0
    p.hit(key=1, new_card=player_hand[0])
    p.hit(key=1, new_card=player_hand[1])

    players_play_hands(
        table=t,
        rules=r,
        cards=c,
        dealer_hand=dealer_hand,
        dealer_up_card=dealer_hand[1]
    )

    assert p.get_insurance() is True
    assert p.get_natural_blackjack() is expected_natural_blackjack
    assert p.get_bankroll() == 85

    compare_hands(table=t, rules=r, stats=s, dealer_hand=dealer_hand)

    assert p.get_bankroll() == expected_bankroll


def test_compare_hands_surrender(setup_table):
    """
    Tests the compare_hands function when a player surrenders.

    """
    c, t, r, p, s = setup_table

    p.hit(key=1, new_card='10')
    p.hit(key=1, new_card='6')

    players_play_hands(
        table=t,
        rules=r,
        cards=c,
        dealer_hand=['J', 'J'],
        dealer_up_card='J'
    )

    assert p.get_surrender() is True
    assert p.get_bankroll() == 90

    compare_hands(table=t, rules=r, stats=s, dealer_hand=['J', 'J'])

    assert p.get_bankroll() == 95


@pytest.mark.parametrize('player_hand, dealer_hand, expected_natural_blackjack, expected_bankroll',
                         [
                             (['A', 'K'], ['K', 'A'], True, 100),  # dealer and player natural blackjack
                             (['2', '2'], ['K', 'A'], False, 90),  # dealer natural blackjack
                             (['A', 'K'], ['2', '2'], True, 115),  # player natural blackjack
                         ])
def test_compare_hands_natural_blackjack(
        setup_table, player_hand, dealer_hand, expected_natural_blackjack, expected_bankroll
):
    """
    Tests the compare_hands function when either a player and/or dealer
    have natural blackjack.

    """
    c, t, r, p, s = setup_table

    p.hit(key=1, new_card=player_hand[0])
    p.hit(key=1, new_card=player_hand[1])

    players_play_hands(
        table=t,
        rules=r,
        cards=c,
        dealer_hand=dealer_hand,
        dealer_up_card=dealer_hand[1]
    )

    assert p.get_natural_blackjack() is expected_natural_blackjack
    assert p.get_bankroll() == 90

    compare_hands(table=t, rules=r, stats=s, dealer_hand=dealer_hand)

    assert p.get_bankroll() == expected_bankroll


@pytest.mark.parametrize('player_hand, new_player_hand, expected_natural_blackjack, expected_bankroll',
                         [
                             (['A', 'K'], None, True, ValueError),  # impossible heads up
                             (['A', 'K'], ['6', '4'], True, 115),  # possible with 2+ players at the table
                             (['6', '4'], None, False, 100)  # both player and dealer have 3+ card 21, push
                         ])
def test_compare_hands_player_three_plus_card_21(
        setup_table, player_hand, new_player_hand, expected_natural_blackjack, expected_bankroll
):
    """
    Tests the compare_hands function when either a player and/or dealer have
    a three or more card 21.

    """
    c, t, r, p, s = setup_table
    r.double_down = False  # necessary so that player doesn't double down on ['6', '4']

    p.hit(key=1, new_card=player_hand[0])
    p.hit(key=1, new_card=player_hand[1])

    if new_player_hand is not None:
        new_p = Player(
                 name='Player 2',
                 rules=r,
                 bankroll=100,
                 min_bet=10
        )
        t.add_player(player=new_p)
        s.create_player_key(player_key=new_p.get_name())
        s.create_count_key(player_key=new_p.get_name(), count_key=0)
        new_p.initial_bet(amount=10)
        new_p.hit(key=1, new_card=new_player_hand[0])
        new_p.hit(key=1, new_card=new_player_hand[1])

    players_play_hands(
        table=t,
        rules=r,
        cards=c,
        dealer_hand=['7', '7'],
        dealer_up_card='7'
    )

    assert p.get_natural_blackjack() is expected_natural_blackjack
    assert max_count_hand(p.get_hand(key=1)) == 21
    assert p.get_bankroll() == 90

    if type(expected_bankroll) == type and issubclass(expected_bankroll, Exception):
        with pytest.raises(ValueError):
            compare_hands(table=t, rules=r, stats=s, dealer_hand=['7', '7', '7'])

    else:
        compare_hands(table=t, rules=r, stats=s, dealer_hand=['7', '7', '7'])
        assert p.get_bankroll() == expected_bankroll


@pytest.mark.parametrize('player_hand, dealer_hand, expected_bankroll',
                         [
                             (['7', '5'], ['J', 'J'], 90),  # player busts
                             (['7', '5'], ['A', 'A', 'K'], 90),  # both player and dealer bust
                             (['J', 'J'], ['A', 'A', 'K'], 110)  # dealer busts
                         ]
                         )
def test_compare_hands_bust(setup_table, player_hand, dealer_hand, expected_bankroll):
    """
    Tests the compare_hands function when either a player and/or dealer bust.

    """
    c, t, r, p, s = setup_table

    p.hit(key=1, new_card=player_hand[0])
    p.hit(key=1, new_card=player_hand[1])

    players_play_hands(
        table=t,
        rules=r,
        cards=c,
        dealer_hand=dealer_hand,
        dealer_up_card=dealer_hand[1]
    )

    assert p.get_bankroll() == 90

    compare_hands(table=t, rules=r, stats=s, dealer_hand=dealer_hand)

    assert p.get_bankroll() == expected_bankroll


def test_compare_hands_push(setup_table):
    """
    Tests the compare_hands function when a player and dealer tie.

    """
    c, t, r, p, s = setup_table

    p.hit(key=1, new_card='J')
    p.hit(key=1, new_card='J')

    compare_hands(table=t, rules=r, stats=s, dealer_hand=['J', 'J'])

    assert p.get_bankroll() == 100


@pytest.mark.parametrize('player_hand, dealer_hand, expected_bankroll',
                          [
                              (['J', 'J'], ['J', '9'], 110),  # player showdown win
                              (['J', '9'], ['J', 'J'], 90)  # dealer showdown win
                          ])
def test_compare_hands_showdown(setup_table, player_hand, dealer_hand, expected_bankroll):
    """
    Tests the compare_hands function when a player and dealer both
    have hand totals less than 21.

    """
    c, t, r, p, s = setup_table

    p.hit(key=1, new_card=player_hand[0])
    p.hit(key=1, new_card=player_hand[1])

    compare_hands(table=t, rules=r, stats=s, dealer_hand=dealer_hand)

    assert p.get_bankroll() == expected_bankroll

