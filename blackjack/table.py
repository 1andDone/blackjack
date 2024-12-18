from blackjack.back_counter import BackCounter
from blackjack.card_counter import CardCounter
from blackjack.player import Player
from blackjack.house_rules import HouseRules


class Table:
    """
    Represents a table where one or more players play blackjack.

    """
    def __init__(self, rules: HouseRules):
        """
        Parameters
        ----------
        rules: HouseRules
            HouseRules class instance

        """
        self._rules = rules
        self._players: list[Player] = []
        self._waiting_players: list[Player] = []

    @property
    def players(self):
        return self._players

    @property
    def waiting_players(self) -> list[Player]:
        return self._waiting_players

    def _validate_player(self, player: Player) -> None:
        if not isinstance(player, Player):
            raise TypeError('Expected a Player object instance.')
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
            self._waiting_players.append(player)
        else:
            self._players.append(player)

    def remove_player(self, player: Player) -> None:
        if player not in self._players:
            raise ValueError(f'{player.name} is not seated at the table or a back counter.')
        self._players.remove(player)

    def remove_back_counter(self, player: Player) -> None:
        self._players.remove(player)
        if isinstance(player, CardCounter) and player.has_sufficient_bankroll(amount=player.max_bet_ramp):
            self._waiting_players.append(player)

    def add_back_counter(self, player: Player) -> None:
        self._waiting_players.remove(player)
        self._players.append(player)
