import pytest
from blackjack.back_counter import BackCounter
from blackjack.card_counter import CardCounter
from blackjack.dealer import Dealer
from blackjack.enums import CardCountingSystem
from blackjack.enums import StatsCategory
from blackjack.hand import Hand
from blackjack.player import Player
from blackjack.playing_strategy import PlayingStrategy
from blackjack.rules import Rules
from blackjack.shoe import Shoe
from blackjack.stats import Stats
from blackjack.table import Table


@pytest.fixture
def rules():
    return Rules(min_bet=10, max_bet=500)


@pytest.fixture
def shoe():
    return Shoe(shoe_size=1, penetration=0.75)


@pytest.fixture
def hand_with_ace():
    hand = Hand()
    hand.add_card(card='A')
    hand.add_card(card='6')
    return hand


@pytest.fixture
def hand_without_ace():
    hand = Hand()
    hand.add_card(card='J')
    hand.add_card(card='8')
    return hand


@pytest.fixture
def hand_pair():
    hand = Hand()
    hand.add_card(card='7')
    hand.add_card(card='7')
    return hand


@pytest.fixture
def hand_blackjack():
    hand = Hand()
    hand.add_card(card='K')
    hand.add_card(card='A')
    return hand


@pytest.fixture
def dealer():
    return Dealer()


@pytest.fixture
def dealer_with_hand(dealer):
    dealer.hand.add_card(card='8')
    dealer.hand.add_card(card='6')
    return dealer


@pytest.fixture
def player():
    return Player(name='Player 1', min_bet=10, bankroll=1000)


@pytest.fixture
def card_counter_balanced():
    return CardCounter(
        name='Player 2',
        bankroll=1000,
        min_bet=10,
        card_counting_system=CardCountingSystem.HI_LO,
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
def card_counter_unbalanced():
    return CardCounter(
        name='Player 2',
        bankroll=1000,
        min_bet=10,
        card_counting_system=CardCountingSystem.KO,
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
def back_counter():
    return BackCounter(
        name='Player 3',
        bankroll=1000,
        min_bet=10,
        card_counting_system=CardCountingSystem.HI_LO,
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
def playing_strategy_h17():
    return PlayingStrategy(s17=False)


@pytest.fixture
def playing_strategy_s17():
    return PlayingStrategy(s17=True)


@pytest.fixture
def stats():
    stats = Stats()
    stats.stats[(1, StatsCategory.TOTAL_ROUNDS_PLAYED)] += 1
    stats.stats[(1, StatsCategory.TOTAL_HANDS_PLAYED)] += 1
    stats.stats[(1, StatsCategory.PLAYER_HANDS_LOST)] += 1
    stats.stats[(1, StatsCategory.DEALER_BLACKJACKS)] += 1
    stats.stats[(1, StatsCategory.AMOUNT_BET)] += 25
    stats.stats[(1, StatsCategory.NET_WINNINGS)] -= 25
    stats.stats[(2, StatsCategory.INSURANCE_AMOUNT_BET)] += 12.5
    stats.stats[(2, StatsCategory.INSURANCE_NET_WINNINGS)] += 25
    stats.stats[(3, StatsCategory.TOTAL_ROUNDS_PLAYED)] += 1
    stats.stats[(3, StatsCategory.TOTAL_HANDS_PLAYED)] += 1
    stats.stats[(3, StatsCategory.PLAYER_HANDS_LOST)] += 1
    stats.stats[(3, StatsCategory.AMOUNT_BET)] += 10
    stats.stats[(3, StatsCategory.NET_WINNINGS)] -= 10
    return stats


@pytest.fixture
def table(rules):
    return Table(rules=rules)
