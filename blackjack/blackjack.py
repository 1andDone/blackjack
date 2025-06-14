from pathlib import Path
import random
import sys
import time
from typing import Generator
from blackjack.dealer import Dealer
from blackjack.gameplay import play_round
from blackjack.player import Player
from blackjack.playing_strategy import PlayingStrategy
from blackjack.rules import Rules
from blackjack.shoe import Shoe
from blackjack.table import Table


def _shoe_progress_bar(shoe_range: range, size: int = 60) -> Generator[int, None, None]:
    total_shoes = len(shoe_range)
    start = time.time()

    def _show(shoe_number: int) -> None:
        x = int(size * shoe_number / total_shoes)
        remaining = ((time.time() - start) / shoe_number) * (total_shoes - shoe_number)
        minutes, seconds = divmod(remaining, 60)
        minutes = int(minutes)
        seconds = int(seconds)
        time_str = f'{minutes if minutes > 10 else minutes:02}:{seconds if seconds > 10 else seconds:02}'
        print(f"Shoes Simulated: [{'█' * x}{('.' * (size - x))}] {shoe_number}/{total_shoes} Estimated wait: {time_str}", end='\r', file=sys.stdout, flush=True)

    for shoe_number in shoe_range:
        _show(shoe_number=shoe_number + 1)
        yield shoe_number

    print(flush=True, file=sys.stdout)


class Blackjack:
    """
    Represents the simulation of one or more
    games of blackjack.

    """
    def __init__(
        self,
        min_bet: int,
        max_bet: int,
        s17: bool = True,
        blackjack_payout: int | float = 1.5,
        max_hands: int = 4,
        double_down: bool = True,
        double_after_split: bool = False,
        resplit_aces: bool = False,
        insurance: bool = True,
        late_surrender: bool = True,
        dealer_shows_hole_card: bool = False
    ):
        """
        Parameters
        ----------
        min_bet
            Minimum bet allowed at the table
        max_bet
            Maximum bet allowed at the table
        s17
            True if dealer stands on a soft 17, False otherwise
        blackjack_payout
            Payout for a player receiving a natural blackjack (i.e. 3:2 is 1.5, 6:5 is 1.2)
        max_hands
            Maximum number of hands that a player can play at once after splitting
        double_down
            True if doubling is allowed on any first two cards, False otherwise
        double_after_split
            True if doubling after splits is allowed, False otherwise
        resplit_aces
            True if re-splitting aces is allowed, False otherwise
        insurance
            True if insurance bet is allowed, False otherwise
        late_surrender
            True if late surrender is allowed, False otherwise
        dealer_shows_hole_card
            True if the dealer shows his hole card regardless of whether or
            not all players bust, False otherwise

        """
        self._rules = Rules(
            min_bet=min_bet,
            max_bet=max_bet,
            s17=s17,
            blackjack_payout=blackjack_payout,
            max_hands=max_hands,
            double_down=double_down,
            double_after_split=double_after_split,
            resplit_aces=resplit_aces,
            insurance=insurance,
            late_surrender=late_surrender,
            dealer_shows_hole_card=dealer_shows_hole_card
        )
        self._table = Table(rules=self._rules)
        self._playing_strategy = PlayingStrategy(s17=s17)
        self._dealer = Dealer()

    def add_player(self, player: Player) -> None:
        """Add a player to the table."""
        return self._table.add_player(player=player)

    def _play_shoe(self, penetration: float, shoe_size: int, reset_bankroll: bool, _logfile: Path) -> None:
        if penetration > 0.9:
            raise ValueError('Penetration must be less than or equal to 0.9.')

        shoe = Shoe(shoe_size=shoe_size, penetration=penetration)
        shoe.shuffle()

        while not shoe.cut_card_reached and self._table.players:
            play_round(
                table=self._table,
                dealer=self._dealer,
                rules=self._rules,
                shoe=shoe,
                playing_strategy=self._playing_strategy,
                _logfile=_logfile
            )

            if reset_bankroll:
                for player in self._table.players + self._table.observers:
                    player.reset_bankroll()

    def simulate(
        self,
        penetration: float,
        number_of_shoes: int,
        shoe_size: int, seed: int | None = None,
        reset_bankroll: bool = False,
        progress_bar: bool = True,
        _logfile: Path = None
    ) -> None:
        """Simulates a series of blackjack games across multiple shoes."""
        if seed:
            random.seed(seed)

        if progress_bar:
            for _ in _shoe_progress_bar(shoe_range=range(number_of_shoes)):
                self._play_shoe(penetration=penetration, shoe_size=shoe_size, reset_bankroll=reset_bankroll, _logfile=_logfile)
        else:
            for _ in range(number_of_shoes):
                self._play_shoe(penetration=penetration, shoe_size=shoe_size, reset_bankroll=reset_bankroll, _logfile=_logfile)
