import pytest
from table import Table
from house_rules import HouseRules
from player import Player
from cards import Cards
from simulation_stats import SimulationStats
from gameplay import deal_hands, players_play_hands, dealer_turn, dealer_plays_hand, compare_hands
from helper import count_hand


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

    dealer_hand = deal_hands(table=t, cards=c)

    for player in p:
        if player.name == 'First to act':
            assert player.get_hand(key=1) == ['A', '10']
        elif player.name == 'Second to act':
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
    p.set_hand()
    s = SimulationStats()
    s.create_player_key(player_key=p.name)
    s.create_count_key(player_key=p.name, count_key=0)
    s.create_outcome_key(player_key='Player 1', count_key=0)
    return c, t, r, p, s


@pytest.mark.parametrize('insurance, count, insurance_count, expected_insurance',
                         [
                             (True, 1, 0, True),  # player buys insurance
                             (True, 0, 1, False),  # player does not buy insurance
                             (False, None, None, False),  # insurance not available
                         ])
def test_players_play_hands_insurance(
        insurance, count, insurance_count, expected_insurance
):
    """
    Tests the insurance option within the players_play_hands function.

    """
    c = Cards(shoe_size=4)
    t = Table()
    r = HouseRules(
        bet_limits=[10, 500],
        insurance=insurance
    )
    p = Player(
        name='Player 1',
        rules=r,
        bankroll=100,
        min_bet=10,
        insurance_count=insurance_count
    )
    t.add_player(player=p)
    s = SimulationStats()
    s.create_player_key(player_key=p.name)
    s.create_count_key(player_key=p.name, count_key=count)
    s.create_outcome_key(player_key='Player 1', count_key=count)

    p.count = count
    p.set_hand()
    p.hit(key=1, new_card='2')
    p.hit(key=1, new_card='2')

    players_play_hands(
        table=t,
        rules=r,
        cards=c,
        stats=s,
        dealer_hand=['J', 'A'],
        dealer_up_card='A'
    )

    assert p.get_insurance() is expected_insurance


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
        stats=s,
        dealer_hand=dealer_cards,
        dealer_up_card=dealer_cards[1]
    )

    assert p.get_natural_blackjack() is expected_natural_blackjack
    assert count_hand(p.get_hand(key=1))[0] == 21


@pytest.mark.parametrize('late_surrender, expected_surrender, expected_hand',
                         [
                             (True, True, ['10', '6']),  # player surrenders
                             (False, False, ['10', '6', 'A'])  # late surrender not available
                         ])
def test_players_play_hands_surrender(
        late_surrender, expected_surrender, expected_hand
):
    """
    Tests the late surrender option within the players_play_hands function.

    """
    c = Cards(shoe_size=4)
    t = Table()
    r = HouseRules(
        bet_limits=[10, 500],
        late_surrender=late_surrender
    )
    p = Player(
        name='Player 1',
        rules=r,
        bankroll=100,
        min_bet=10
    )
    t.add_player(player=p)
    s = SimulationStats()
    s.create_player_key(player_key=p.name)
    s.create_count_key(player_key=p.name, count_key=0)
    s.create_outcome_key(player_key='Player 1', count_key=0)

    p.set_hand()
    p.hit(key=1, new_card='10')
    p.hit(key=1, new_card='6')

    players_play_hands(
        table=t,
        rules=r,
        cards=c,
        stats=s,
        dealer_hand=['J', 'J'],
        dealer_up_card='J'
    )

    assert p.get_surrender() is expected_surrender
    assert p.get_hand(key=1) == expected_hand


@pytest.mark.parametrize('resplit_aces, max_hands, player_cards, fixed_deck, expected_split, expected_hands',
                         [
                             (False, 4, ['2', '2'], False, True, [['2', 'A', 'K'], ['2', 'Q']]),  # split non-aces
                             (False, 4, ['A', 'A'], False, True, [['A', 'A'], ['A', 'K']]),  # cannot re-split aces
                             (True, 4, ['A', 'A'], False, True, [['A', 'K'], ['A', 'Q'], ['A', 'J']]),  # re-split aces
                             (True, 3, ['A', 'A'], True, True, [['A', 'K'], ['A', 'Q'], ['A', 'A']]),  # 3 max hands
                         ])
def test_players_play_hands_split(
        resplit_aces, max_hands, player_cards, fixed_deck, expected_split, expected_hands
):
    """
    Tests the players_play_hands function when a player has the option to
    split or re-split their hand.

    """
    c = Cards(shoe_size=4)
    if fixed_deck:
        c.deck = ['8', 'A', 'Q', 'K', 'A']  # popping off end of the list
    t = Table()
    r = HouseRules(
            bet_limits=[10, 500],
            max_hands=max_hands,
            resplit_aces=resplit_aces
    )
    p = Player(
            name='Player 1',
            rules=r,
            bankroll=100,
            min_bet=10
    )
    t.add_player(player=p)
    s = SimulationStats()
    s.create_player_key(player_key=p.name)
    s.create_count_key(player_key=p.name, count_key=0)
    s.create_outcome_key(player_key='Player 1', count_key=0)

    p.set_hand()
    p.hit(key=1, new_card=player_cards[0])
    p.hit(key=1, new_card=player_cards[1])

    players_play_hands(
        table=t,
        rules=r,
        cards=c,
        stats=s,
        dealer_hand=['J', '4'],
        dealer_up_card='4'
    )

    for key in p.hands_dict:
        assert p.get_split(key=key) is expected_split
        assert p.get_hand(key=key) == expected_hands[key - 1]


@pytest.mark.parametrize('double_after_split, expected_split, expected_hands',
                         [
                             (True, True, [['2', 'A', 'K'], ['2', 'Q', 'J']]),  # player can double after split
                             (False, False, [['2', '2', 'A', 'K']])  # player cannot double after split
                         ])
def test_players_play_hands_double_after_split(
        double_after_split, expected_split, expected_hands
):
    """
    Tests the double after splitting option within the players_play_hands function.

    """
    c = Cards(shoe_size=4)
    t = Table()
    r = HouseRules(
            bet_limits=[10, 500],
            double_after_split=double_after_split
    )
    p = Player(
            name='Player 1',
            rules=r,
            bankroll=100,
            min_bet=10
    )
    t.add_player(player=p)
    s = SimulationStats()
    s.create_player_key(player_key=p.name)
    s.create_count_key(player_key=p.name, count_key=0)
    s.create_outcome_key(player_key='Player 1', count_key=0)

    p.set_hand()
    p.hit(key=1, new_card='2')
    p.hit(key=1, new_card='2')

    players_play_hands(
        table=t,
        rules=r,
        cards=c,
        stats=s,
        dealer_hand=['J', '2'],
        dealer_up_card='2'
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
    c = Cards(shoe_size=4)
    t = Table()
    r = HouseRules(
            bet_limits=[10, 500],
            double_down=double_down
    )
    p = Player(
            name='Player 1',
            rules=r,
            bankroll=100,
            min_bet=10
    )
    t.add_player(player=p)
    s = SimulationStats()
    s.create_player_key(player_key=p.name)
    s.create_count_key(player_key=p.name, count_key=0)
    s.create_outcome_key(player_key='Player 1', count_key=0)

    p.set_hand()
    p.hit(key=1, new_card='6')
    p.hit(key=1, new_card='4')

    players_play_hands(
        table=t,
        rules=r,
        cards=c,
        stats=s,
        dealer_hand=['J', '2'],
        dealer_up_card='2'
    )

    assert p.get_double_down(key=1) == expected


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
        stats=s,
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
        stats=s,
        dealer_hand=['J', 'J'],
        dealer_up_card='J'
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
    c, t, r, p, _ = setup_table

    if player_busted:
        p.set_busted(key=1)

    elif player_surrender:
        p.set_surrender()

    elif player_or_dealer_natural_blackjack:
        p.set_settled_natural_blackjack()

    else:
        p.set_stand(key=1)

    assert dealer_turn(table=t) is expected


@pytest.mark.parametrize('s17, dealer_hand, expected_hand',
                         [
                             (True, ['A', '6'], ['A', '6']),  # dealer stands on soft 17
                             (False, ['A', '6'], ['A', '6', 'A'])  # dealer hits on soft 17
                         ])
def test_dealer_plays_hand(s17, dealer_hand, expected_hand):
    """
    Tests the dealer_plays_hand function when a dealer hits or stands
    on soft 17.

    """
    c = Cards(shoe_size=4)
    t = Table()
    r = HouseRules(
            bet_limits=[10, 500],
            s17=s17
    )
    p = Player(
            name='Player 1',
            rules=r,
            bankroll=100,
            min_bet=10
    )
    t.add_player(player=p)
    p.set_hand()

    dealer_hand = dealer_plays_hand(
                                rules=r,
                                cards=c,
                                dealer_hand=dealer_hand,
                                dealer_hole_card=dealer_hand[1]
    )

    assert dealer_hand == expected_hand


@pytest.mark.parametrize('player_hand, dealer_hand, expected_natural_blackjack, expected_outcome',
                         [
                             (['A', 'K'], ['K', 'A'], True, 'win'),  # dealer and player natural blackjack
                             (['2', '2'], ['K', 'A'], False, 'win'),  # dealer natural blackjack
                             (['A', 'K'], ['8', 'A'], True, 'loss'),  # player natural blackjack
                             (['2', '2'], ['8', 'A'], False, 'loss')   # no natural blackjack
                         ])
def test_compare_hands_insurance(
        player_hand, dealer_hand, expected_natural_blackjack, expected_outcome
):
    """
    Tests the compare_hands function when a player buys insurance.

    """
    c = Cards(shoe_size=4)
    t = Table()
    r = HouseRules(
        bet_limits=[10, 500]
    )
    p = Player(
        name='Player 1',
        rules=r,
        bankroll=100,
        min_bet=10,
        insurance_count=0
    )
    t.add_player(player=p)
    s = SimulationStats()
    s.create_player_key(player_key=p.name)
    s.create_count_key(player_key=p.name, count_key=0)
    s.create_outcome_key(player_key='Player 1', count_key=0)

    p.count = 0
    p.set_hand()
    p.hit(key=1, new_card=player_hand[0])
    p.hit(key=1, new_card=player_hand[1])

    players_play_hands(
        table=t,
        rules=r,
        cards=c,
        stats=s,
        dealer_hand=dealer_hand,
        dealer_up_card=dealer_hand[1]
    )

    assert p.get_insurance() is True
    assert p.get_natural_blackjack() is expected_natural_blackjack

    compare_hands(table=t, stats=s, dealer_hand=dealer_hand)

    assert s.stats_dict['Player 1'][0][expected_outcome]['insurance'] == 1


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
        stats=s,
        dealer_hand=['J', 'J'],
        dealer_up_card='J'
    )

    assert p.get_surrender() is True

    compare_hands(table=t, stats=s, dealer_hand=['J', 'J'])

    assert s.stats_dict['Player 1'][0]['loss']['surrender'] == 1


@pytest.mark.parametrize('player_hand, dealer_hand, expected_natural_blackjack, expected_outcome',
                         [
                             (['A', 'K'], ['K', 'A'], True, 'push'),  # dealer and player natural blackjack
                             (['2', '2'], ['K', 'A'], False, 'loss'),  # dealer natural blackjack
                             (['A', 'K'], ['2', '2'], True, 'win'),  # player natural blackjack
                         ])
def test_compare_hands_natural_blackjack(
        setup_table, player_hand, dealer_hand, expected_natural_blackjack, expected_outcome
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
        stats=s,
        dealer_hand=dealer_hand,
        dealer_up_card=dealer_hand[1]
    )

    assert p.get_natural_blackjack() is expected_natural_blackjack

    compare_hands(table=t, stats=s, dealer_hand=dealer_hand)

    if expected_outcome == 'push':
        assert s.stats_dict['Player 1'][0]['push']['number of hands'] == 1
    elif expected_outcome == 'win':
        assert s.stats_dict['Player 1'][0]['win']['natural blackjack'] == 1
    else:
        assert s.stats_dict['Player 1'][0]['loss']['other'] == 1


@pytest.mark.parametrize('player_hand, new_player_hand, expected_natural_blackjack, expected_outcome',
                         [
                             (['A', 'K'], ['6', '4'], True, 'win'),  # possible with 2+ players at the table
                             (['6', '4'], None, False, 'push')  # both player and dealer have 3+ card 21, push
                         ])
def test_compare_hands_player_three_plus_card_21(
        player_hand, new_player_hand, expected_natural_blackjack, expected_outcome
):
    """
    Tests the compare_hands function when either a player and/or dealer have
    a three or more card 21.

    """
    c = Cards(shoe_size=4)
    t = Table()
    r = HouseRules(
        bet_limits=[10, 500],
        double_down=False  # necessary so that player doesn't double down on ['6', '4']
    )
    p = Player(
        name='Player 1',
        rules=r,
        bankroll=100,
        min_bet=10
    )
    t.add_player(player=p)
    s = SimulationStats()
    s.create_player_key(player_key=p.name)
    s.create_count_key(player_key=p.name, count_key=0)
    s.create_outcome_key(player_key='Player 1', count_key=0)

    p.set_hand()
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
        s.create_player_key(player_key=new_p.name)
        s.create_count_key(player_key=new_p.name, count_key=0)
        s.create_outcome_key(player_key=new_p.name, count_key=0)
        new_p.set_hand()
        new_p.hit(key=1, new_card=new_player_hand[0])
        new_p.hit(key=1, new_card=new_player_hand[1])

    players_play_hands(
        table=t,
        rules=r,
        cards=c,
        stats=s,
        dealer_hand=['7', '7'],
        dealer_up_card='7'
    )

    assert p.get_natural_blackjack() is expected_natural_blackjack
    assert count_hand(p.get_hand(key=1))[0] == 21

    compare_hands(table=t, stats=s, dealer_hand=['7', '7', '7'])

    if expected_outcome == 'push':
        assert s.stats_dict['Player 1'][0]['push']['number of hands'] == 1
    else:
        assert s.stats_dict['Player 1'][0]['win']['natural blackjack'] == 1


@pytest.mark.parametrize('player_hand, dealer_hand, expected_outcome',
                         [
                             (['7', '5'], ['J', 'J'], 'loss'),  # player busts
                             (['7', '5'], ['A', 'A', 'K'], 'loss'),  # both player and dealer bust
                             (['J', 'J'], ['A', 'A', 'K'], 'win')  # dealer busts
                         ]
                         )
def test_compare_hands_bust(setup_table, player_hand, dealer_hand, expected_outcome):
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
        stats=s,
        dealer_hand=dealer_hand,
        dealer_up_card=dealer_hand[1]
    )

    compare_hands(table=t, stats=s, dealer_hand=dealer_hand)

    assert s.stats_dict['Player 1'][0][expected_outcome]['other'] == 1


def test_compare_hands_push(setup_table):
    """
    Tests the compare_hands function when a player and dealer tie.

    """
    c, t, r, p, s = setup_table

    p.hit(key=1, new_card='J')
    p.hit(key=1, new_card='J')

    compare_hands(table=t, stats=s, dealer_hand=['J', 'J'])

    assert s.stats_dict['Player 1'][0]['push']['number of hands'] == 1


@pytest.mark.parametrize('player_hand, dealer_hand, expected_outcome',
                          [
                              (['J', 'J'], ['J', '9'], 'win'),  # player showdown win
                              (['J', '9'], ['J', 'J'], 'loss')  # dealer showdown win
                          ])
def test_compare_hands_showdown(setup_table, player_hand, dealer_hand, expected_outcome):
    """
    Tests the compare_hands function when a player and dealer both
    have hand totals less than 21.

    """
    c, t, r, p, s = setup_table

    p.hit(key=1, new_card=player_hand[0])
    p.hit(key=1, new_card=player_hand[1])

    compare_hands(table=t, stats=s, dealer_hand=dealer_hand)

    assert s.stats_dict['Player 1'][0][expected_outcome]['other'] == 1

