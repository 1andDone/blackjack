import pytest
from blackjack import CardCounter, BackCounter, CountingStrategy
from blackjack import HouseRules, Player, Table
from blackjack.dealer import Dealer
from blackjack.hand import Hand
from blackjack.shoe import Shoe
from blackjack.playing_strategy import PlayingStrategy
from blackjack.simulation_stats import StatsCategory, SimulationStats


@pytest.fixture
def setup_rules():
    return HouseRules(
        shoe_size=6,
        min_bet=10,
        max_bet=500,
        s17=True,
        max_hands=2,
        split_unlike_tens=True
    )
    

@pytest.fixture
def setup_rules_no_insurance():
    return HouseRules(
        shoe_size=6,
        min_bet=10,
        max_bet=500,
        insurance=False
    )


@pytest.fixture
def setup_shoe():
    return Shoe(size=6)


@pytest.fixture
def setup_hand():
    return Hand()


@pytest.fixture
def setup_hand_with_ace(setup_hand):
    setup_hand.add_card(card='A')
    setup_hand.add_card(card='6')
    return setup_hand


@pytest.fixture
def setup_hand_without_ace(setup_hand):
    setup_hand.add_card(card='J')
    setup_hand.add_card(card='8')
    return setup_hand


@pytest.fixture
def setup_hand_split(setup_hand):
    setup_hand.add_card(card='7')
    setup_hand.add_card(card='7')
    return setup_hand


@pytest.fixture
def setup_hand_blackjack(setup_hand):
    setup_hand.add_card(card='K')
    setup_hand.add_card(card='A')
    return setup_hand


@pytest.fixture
def setup_dealer_with_hand():
    d = Dealer()
    d.hand.add_card(card='8')
    d.hand.add_card(card='6')
    return d


@pytest.fixture
def setup_player_without_split_hand(setup_player):
    setup_player.first_hand.add_card(card='8')
    setup_player.first_hand.add_card(card='6')
    return setup_player


@pytest.fixture
def setup_player_with_split_hand(setup_player):
    setup_player.first_hand.add_card(card='7')
    setup_player.first_hand.add_card(card='7')
    return setup_player


@pytest.fixture
def setup_player():
    return Player(
        name='Player 1',
        bankroll=1000,
        min_bet=10
    )


@pytest.fixture
def setup_card_counter():
    return CardCounter(
        name='Player 2',
        bankroll=1000,
        min_bet=10,
        counting_strategy=CountingStrategy.HI_LO,
        bet_ramp={
            1: 15,
            2: 20,
            3: 40,
            4: 50,
            5: 70
        },
        insurance=None
    )


@pytest.fixture
def setup_back_counter(setup_card_counter):
    return BackCounter(
        name='Player 3',
        bankroll=1000,
        min_bet=10,
        counting_strategy=CountingStrategy.HI_LO,
        bet_ramp={
            1: 15,
            2: 20,
            3: 40,
            4: 50,
            5: 70
        },
        insurance=None,
        partner=setup_card_counter,
        entry_point=3,
        exit_point=0
    )


@pytest.fixture
def setup_playing_strategy_h17():
    return PlayingStrategy(s17=False)


@pytest.fixture
def setup_playing_strategy_s17():
    return PlayingStrategy(s17=True)


@pytest.fixture
def setup_simulation_stats():
    s = SimulationStats()
    s.add_hand(count=1, category=StatsCategory.HANDS_LOST)
    s.add_amount(count=1, category=StatsCategory.AMOUNT_EARNED, increment=-10)
    s.add_hand(count=None, category=StatsCategory.HANDS_LOST)
    s.add_amount(count=None, category=StatsCategory.AMOUNT_EARNED, increment=-20.425)
    return s


@pytest.fixture
def setup_table(setup_rules):
    return Table(rules=setup_rules)


@pytest.fixture
def setup_table_no_insurance(setup_rules_no_insurance):
    return Table(rules=setup_rules_no_insurance)