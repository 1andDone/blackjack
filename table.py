from player import Player


class Table(object):
    """
    Table is an object that represents an area where one or many players play
    blackjack.

    """
    def __init__(self, size_limit=7):
        """
        Parameters
        ----------
        size_limit : int, optional
            Number of players that can play at a table at any given time (default
            is 7)
        """
        if size_limit < 1 or size_limit > 7:
            raise ValueError('Table cannot have less than 1 or more than 7 seats.')
        if not isinstance(size_limit, int):
            raise TypeError('Size limit needs to be an integer value.')
        self._size_limit = size_limit
        self._players = []

    @property
    def size_limit(self):
        return self._size_limit

    @property
    def players(self):
        return self._players

    def add_player(self, player):
        if isinstance(player, Player):
            if len(self._players) + len([player]) > self._size_limit:
                raise ValueError('Table is at maximum capacity.')
            for p in self._players:
                if p.name == player.name:
                    raise ValueError('Already a player with that name at table.')
            self._players.append(player)
        else:
            raise TypeError('Expected a Player class object.')

    def remove_player(self, player):
        if player in self._players:
            self._players.remove(player)
        else:
            raise ValueError('Player cannot be removed because that player is not at the table.')
