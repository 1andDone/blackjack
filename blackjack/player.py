from typing import Any
from blackjack.hand import Hand
from blackjack.playing_strategy import PlayingStrategy
from blackjack.house_rules import HouseRules
from blackjack.simulation_stats import SimulationStats


class Player:
    """
    Represents an individual player at a blackjack
    table that bets a flat amount.

    """
    def __init__(self, name: str, bankroll: float | int, min_bet: float | int):
        """
        Parameters
        ----------
        name
            Name of the player
        bankroll
            Amount of money a player starts out with at a table
        min_bet
            Amount of money a player wagers when playing a hand

        """
        if bankroll < min_bet:
            raise ValueError("Insufficient bankroll to place the player's desired bet.")

        self._name = name
        self._bankroll = bankroll
        self._min_bet = min_bet
        self._hands = [Hand()]
        self._stats = SimulationStats()

    @property
    def name(self) -> str:
        return self._name

    @property
    def bankroll(self) -> float | int:
        return self._bankroll

    def initial_wager(self, **kwargs: Any) -> float | int:
        return self._min_bet

    @property
    def hands(self) -> list[Hand]:
        return self._hands

    @property
    def stats(self) -> SimulationStats:
        return self._stats

    @property
    def first_hand(self) -> Hand:
        return self._hands[0]

    # TODO: change to increase?
    def edit_bankroll(self, amount: float | int) -> None:
        self._bankroll += amount

    def has_sufficient_bankroll(self, amount: float | int) -> bool:
        return amount <= self._bankroll

    def _can_split(self, hand: Hand, rules: HouseRules) -> bool:
        if self.has_sufficient_bankroll(amount=hand.total_bet):
            return hand.number_of_cards() == 2 and ((hand.cards[0] == hand.cards[1]) or
                (rules.split_unlike_tens and all(card in {'10', 'J', 'Q', 'K'} for card in hand.cards))) and \
                len(self._hands) < rules.max_hands
        return False

    def decision(self, hand: Hand, dealer_up_card: str, rules: HouseRules) -> str:
        playing_strategy = PlayingStrategy(s17=rules.s17)
        if self._can_split(hand=hand, rules=rules):
            return playing_strategy.pair(card=hand.cards[0], dealer_up_card=dealer_up_card)
        if hand.is_soft():
            return playing_strategy.soft(total=hand.total(), dealer_up_card=dealer_up_card)
        return playing_strategy.hard(total=hand.total(), dealer_up_card=dealer_up_card)

    def reset_hands(self) -> None:
        self._hands = [Hand()]
