from blackjack.back_counter import BackCounter
from blackjack.card_counter import CardCounter
from blackjack.player import Player
from blackjack.rules import Rules


class Table:
    """
    Represents a table where one or more players play blackjack.

    """
    def __init__(self, rules: Rules):
        """
        Parameters
        ----------
        rules: Rules
            Rules class instance

        """
        self._rules = rules
        self._players: list[Player] = []
        self._observers: list[Player] = []

    @property
    def players(self):
        return self._players

    @property
    def observers(self) -> list[Player]:
        return self._observers

    def _validate_player(self, player: Player) -> None:
        if not isinstance(player, Player):
            raise TypeError('Expected a Player, CardCounter, or BackCounter object.')
        if isinstance(player, CardCounter):
            if (player.min_bet_ramp < self._rules.min_bet) or (player.max_bet_ramp > self._rules.max_bet):
                raise ValueError(f"{player.name}'s desired bet is not allowed according to the table rules.")
            if not self._rules.insurance and player.insurance:
                raise ValueError(f"{player.name}'s insurance is not allowed according to the table rules.")
        else:
            if (player.initial_wager() < self._rules.min_bet) or (player.initial_wager() > self._rules.max_bet):
                raise ValueError(f"{player.name}'s desired bet is not allowed according to the table rules.")

    def add_player(self, player: Player) -> None:
        self._validate_player(player=player)
        if isinstance(player, BackCounter):
            self._observers.append(player)
        else:
            self._players.append(player)

    def remove_player(self, player: Player) -> None:
        if player not in self._players:
            raise ValueError(f'{player.name} is not seated at the table or a back counter.')
        self._players.remove(player)

    def remove_back_counter(self, back_counter: BackCounter) -> None:
        if not isinstance(back_counter, BackCounter):
            raise TypeError('Expected a BackCounter object.')
        self._players.remove(back_counter)
        self._observers.append(back_counter)

    def add_back_counter(self, back_counter: BackCounter) -> None:
        if not isinstance(back_counter, BackCounter):
            raise TypeError('Expected a BackCounter object.')
        self._observers.remove(back_counter)
        self._players.append(back_counter)
