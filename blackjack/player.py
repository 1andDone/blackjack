from typing import Any
from blackjack.hand import Hand
from blackjack.playing_strategy import PlayingStrategy
from blackjack.stats import Stats


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
            raise ValueError(f"Insufficient bankroll to place {name}'s desired bet.")

        self._name = name
        self._bankroll = bankroll
        self._min_bet = min_bet
        self._hands = [Hand()]
        self._stats = Stats()

    @property
    def name(self) -> str:
        return self._name

    @property
    def bankroll(self) -> float | int:
        return self._bankroll

    def placed_bet(self, **kwargs: Any) -> float | int:
        return self._min_bet

    @property
    def hands(self) -> list[Hand]:
        return self._hands

    def get_first_hand(self) -> Hand:
        return self._hands[0]

    @property
    def number_of_hands(self) -> int:
        return len(self._hands)

    @property
    def stats(self) -> Stats:
        return self._stats

    def adjust_bankroll(self, amount: float | int) -> None:
        self._bankroll += amount

    def has_sufficient_bankroll(self, amount: float | int) -> bool:
        return amount <= self._bankroll

    def _is_split_allowed(self, hand: Hand, max_hands: int) -> bool:
        return hand.number_of_cards == 2 and (hand.cards[0] == hand.cards[1]) and \
            len(self._hands) < max_hands and self.has_sufficient_bankroll(amount=hand.total_bet)

    def decision(self, playing_strategy: PlayingStrategy, hand: Hand, dealer_up_card: str, max_hands: int) -> str:
        if self._is_split_allowed(hand=hand, max_hands=max_hands):
            return playing_strategy.pair(card=hand.cards[0], dealer_up_card=dealer_up_card)
        if hand.is_soft:
            return playing_strategy.soft(total=hand.total, dealer_up_card=dealer_up_card)
        return playing_strategy.hard(total=hand.total, dealer_up_card=dealer_up_card)

    def reset_hands(self) -> None:
        self._hands = [Hand()]
