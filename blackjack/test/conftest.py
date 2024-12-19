import pytest
from blackjack.back_counter import BackCounter
from blackjack.card_counter import CardCounter
from blackjack.dealer import Dealer
from blackjack.enums import CountingStrategy
from blackjack.hand import Hand
from blackjack.house_rules import HouseRules
from blackjack.player import Player
from blackjack.playing_strategy import PlayingStrategy
from blackjack.shoe import Shoe
from blackjack.table import Table
from blackjack.simulation_stats import StatsCategory, SimulationStats


@pytest.fixture
def setup_rules():
    return HouseRules(
        min_bet=10,
        max_bet=500,
        s17=True,
        blackjack_payout=1.5,
        max_hands=4,
        double_down=True,
        double_after_split=False,
        resplit_aces=False,
        insurance=True,
        late_surrender=True,
        dealer_shows_hole_card=False
    )


@pytest.fixture
def setup_shoe():
    return Shoe(shoe_size=1)


@pytest.fixture
def setup_hand_with_ace():
    hand = Hand()
    hand.add_card(card='A')
    hand.add_card(card='6')
    return hand


@pytest.fixture
def setup_hand_without_ace():
    hand = Hand()
    hand.add_card(card='J')
    hand.add_card(card='8')
    return hand


@pytest.fixture
def setup_hand_split():
    hand = Hand()
    hand.add_card(card='7')
    hand.add_card(card='7')
    return hand


@pytest.fixture
def setup_hand_blackjack():
    hand = Hand()
    hand.add_card(card='K')
    hand.add_card(card='A')
    return hand


@pytest.fixture
def setup_dealer():
    return Dealer()


@pytest.fixture
def setup_dealer_with_hand():
    dealer = Dealer()
    dealer.hand.add_card(card='8')
    dealer.hand.add_card(card='6')
    return dealer


@pytest.fixture
def setup_player():
    return Player(
        name='Player 1',
        min_bet=10,
        bankroll=1000
    )


@pytest.fixture
def setup_player_with_hand(setup_player):
    setup_player.first_hand.add_card(card='8')
    setup_player.first_hand.add_card(card='6')
    return setup_player


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
def setup_card_counter_unbalanced():
    return CardCounter(
        name='Player 2',
        bankroll=1000,
        min_bet=10,
        counting_strategy=CountingStrategy.KO,
        bet_ramp={
            1: 15,
            2: 20,
            3: 40,
            4: 50,
            5: 70
        },
        insurance=2
    )


@pytest.fixture
def setup_back_counter():
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
    stats = SimulationStats()
    stats.add_hand(count=1, category=StatsCategory.HANDS_LOST)
    stats.add_amount(count=1, category=StatsCategory.AMOUNT_WAGERED, increment=10)
    stats.add_amount(count=1, category=StatsCategory.AMOUNT_EARNED, increment=-10)
    stats.add_hand(count=None, category=StatsCategory.HANDS_LOST)
    stats.add_amount(count=None, category=StatsCategory.AMOUNT_WAGERED, increment=20.425)
    stats.add_amount(count=None, category=StatsCategory.AMOUNT_EARNED, increment=-20.425)
    return stats


@pytest.fixture
def setup_table(setup_rules):
    return Table(rules=setup_rules)
