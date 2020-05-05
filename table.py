from player import Player


class Table(object):
    """
    Table is an object that represents an area where one or many players can play.

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
        self.size_limit = int(size_limit)
        self.players = []

    def get_players(self):
        return self.players

    def add_player(self, player):
        if isinstance(player, Player):
            if len(self.players) + len([player]) > self.size_limit:
                raise ValueError('Table is at maximum capacity.')
            for p in self.players:
                if p.get_name() == player.get_name():
                    raise ValueError('Already a player with that name at table.')
            self.players.append(player)
        else:
            raise AttributeError('Expected a Player class object.')

    def remove_player(self, player):
        if player in self.players:
            self.players.remove(player)
        else:
            raise ValueError('Player cannot be removed because that player is not at the table.')
