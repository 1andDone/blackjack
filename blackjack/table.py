from blackjack import Player, CardCounter, BackCounter


class Table:
    """
    Represents a table where one or more players play blackjack.

    """
    def __init__(self, rules):
        """
        Parameters
        ----------
        rules: HouseRules
            HouseRules class instance
        
        """
        self._rules = rules
        self._players = []
        self._waiting_players = []

    @property
    def players(self):
        return self._players
    
    @property
    def waiting_players(self):
        return self._waiting_players
    
    def _validate_player(self, player):
        if not isinstance(player, Player):
            raise TypeError('Expected a Player object instance.')
        if isinstance(player, CardCounter):
            if (player.min_bet_ramp < self._rules.min_bet) or (player.max_bet_ramp > self._rules.max_bet):
                raise ValueError("The player's desired bet is not allowed according to the table rules.")
            if not self._rules.insurance and player.insurance:
                raise ValueError("The player's insurance is not allowed according to table rules.")
        else:
            if (player.initial_wager() < self._rules.min_bet) or (player.initial_wager() > self._rules.max_bet):
                raise ValueError("The player's desired bet is not allowed according to the table rules.")
    
    def add_player(self, player):
        self._validate_player(player=player)
        if type(player) == BackCounter:
            self._waiting_players.append(player)
        else:
            self._players.append(player)
    
    def remove_player(self, player):
        if player in self._players:
            self._players.remove(player)
        else:
            raise ValueError('The player is neither seated at the table or an out of play back counter.')

    def remove_back_counter(self, player):
        self._players.remove(player)
        self._waiting_players.append(player)
        
    def add_back_counter(self, player):
        self._waiting_players.remove(player)
        self._players.append(player)