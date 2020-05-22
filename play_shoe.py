import random
import numpy as np

from house_rules import HouseRules
from cards import Cards
from counting_strategy import CountingStrategy
from table import Table
from simulation_stats import SimulationStats
from gameplay import deal_hands, players_play_hands, dealer_turn, dealer_plays_hand, compare_hands
from figures import net_winnings_figure


class PlayShoe(object):
    """
    PlayShoe is an object that simulates the playing of a shoe between
    players and dealer.

    """
    def __init__(
            self, rules, players, seed_number=None, shoe_size=6,
            penetration=0.75, simulations=10000, figures=False
    ):
        """
        Parameters
        ----------
        rules : HouseRules
            HouseRules class instance
        players : list of Player
            List of Player class instances
        seed_number : int, optional
            Initializes the pseudorandom number generator to replicate the ordering of the
            shoe from run-to-run (default is None)
        shoe_size : int, optional
            Number of decks used during a blackjack game (default is 6)
        penetration : float, optional
            Percentage of shoe played before the deck is re-shuffled (default is 0.75)
        simulations : int, optional
            Number of shoes played (default is 10,000)
        figures : bool, optional
            True if default plots are created, false otherwise (default is False)
        """
        if not isinstance(rules, HouseRules):
            raise TypeError('Rules must be of type HouseRules.')
        self.rules = rules
        self.players = players
        self.seed_number = seed_number
        self.shoe_size = shoe_size
        self.penetration = penetration
        self.simulations = simulations
        self.figures = figures
        self.stats = SimulationStats()

    def main(self):

        # set seed to replicate results
        if self.seed_number is not None:
            random.seed(self.seed_number)

        # set up table
        t = Table()

        for p in self.players:

            # create player key
            self.stats.create_player_key(player_key=p.get_name())

            # add players to table
            if not p.get_back_counting():
                t.add_player(player=p)

        # balanced and unbalanced card counting systems
        balanced_card_counting_systems = ['Hi-Lo', 'Hi-Opt I', 'Hi-Opt II', 'Omega II', 'Halves', 'Zen Count']
        unbalanced_card_counting_systems = ['KO']

        for sim in range(1, self.simulations + 1):

            # set up cards and shuffle
            c = Cards(shoe_size=self.shoe_size)
            c.shuffle()

            # keep track of card counts
            cs = CountingStrategy(cards=c)

            while not c.cut_card_reached(penetration=self.penetration):

                # add back counters to the table if the count is favorable
                for p in self.players:
                    if p.get_back_counting() and p not in t.get_players():
                        if p.get_count_strategy() in balanced_card_counting_systems:
                            if cs.true_count(strategy=p.get_count_strategy(), accuracy=p.get_true_count_accuracy()) >= \
                                 p.get_back_counting_entry_exit()[0]:
                                t.add_player(player=p)
                        else:
                            if cs.running_count(strategy=p.get_count_strategy()) >= p.get_back_counting_entry_exit()[0]:
                                t.add_player(player=p)

                # remove back counters from the table if the count is not favorable
                for p in self.players:
                    if p.get_back_counting() and p in t.get_players():
                        if p.get_count_strategy() in balanced_card_counting_systems:
                            if cs.true_count(strategy=p.get_count_strategy(), accuracy=p.get_true_count_accuracy()) < \
                                 p.get_back_counting_entry_exit()[1]:
                                t.remove_player(player=p)
                        else:
                            if cs.running_count(strategy=p.get_count_strategy()) < p.get_back_counting_entry_exit()[1]:
                                t.remove_player(player=p)

                for p in t.get_players():

                    # get true count
                    if p.get_count_strategy() in balanced_card_counting_systems:
                        p.set_count(
                            count=cs.true_count(
                                    strategy=p.get_count_strategy(),
                                    accuracy=p.get_true_count_accuracy()
                            )
                        )

                    # get running count
                    elif p.get_count_strategy() in unbalanced_card_counting_systems:
                        p.set_count(
                            count=cs.running_count(
                                    strategy=p.get_count_strategy()
                            )
                        )

                    else:
                        p.set_count(count=0)

                    # create count and outcome keys
                    self.stats.create_count_key(player_key=p.get_name(), count_key=p.get_count())
                    self.stats.create_outcome_key(player_key=p.get_name(), count_key=p.get_count())

                # only deal hands if there are players
                if len(t.get_players()) > 0:

                    # deal hands to all players and dealer
                    dealer_hand = deal_hands(table=t, cards=c)

                    # dealers cards
                    dealer_hole_card = dealer_hand[0]
                    dealer_up_card = dealer_hand[1]

                    # players play out each of their hands
                    players_play_hands(
                        table=t,
                        rules=self.rules,
                        cards=c,
                        dealer_hand=dealer_hand,
                        dealer_up_card=dealer_up_card
                    )

                    # dealer shows hole card when all players bust, surrender, or have natural 21
                    if not dealer_turn(table=t) and self.rules.dealer_shows_hole_card:
                        c.update_visible_cards(card=dealer_hole_card)

                    # dealer acts if one or more players have a live hand
                    if dealer_turn(table=t):
                        dealer_hand = dealer_plays_hand(
                            rules=self.rules,
                            cards=c,
                            dealer_hole_card=dealer_hole_card,
                            dealer_hand=dealer_hand
                        )

                    # compare players hand(s) to dealer and pay out to players, house
                    compare_hands(
                        table=t,
                        rules=self.rules,
                        stats=self.stats,
                        dealer_hand=dealer_hand
                    )

                    # update count and reset visible cards
                    cs.update_running_count()
                    c.set_visible_cards()

        # unpack nested dictionary
        for player_key, player_values in self.stats.get_stats_dict().items():
            print('Player:', player_key)
            print('--------' + '-' * len(player_key))

            # create arrays
            count = np.array([])
            net_winnings = np.array([])
            overall_bet = np.array([])
            num_hands = np.array([])
            split_hands = np.array([])

            for count_key, count_values in sorted(player_values.items()):
                count = np.append(count, count_key)

                # net winnings and overall bet are in terms of initial bet
                net_winnings = np.append(
                    net_winnings,
                    (count_values['win']['natural blackjack'] * self.rules.blackjack_payout) +
                    (count_values['win']['insurance'] * 0.5) +
                    (count_values['win']['double down'] * 2) +
                    (count_values['win']['double after split'] * 2) +
                    count_values['win']['split'] +
                    count_values['win']['other'] +
                    (count_values['loss']['surrender'] * -0.5) +
                    (count_values['loss']['insurance'] * -0.5) +
                    (count_values['loss']['double down'] * -2) +
                    (count_values['win']['double after split'] * -2) +
                    (count_values['loss']['split'] * -1) +
                    (count_values['loss']['other'] * -1)
                )
                overall_bet = np.append(
                    overall_bet,
                    count_values['win']['natural blackjack'] +
                    (count_values['win']['insurance'] * 0.5) +
                    (count_values['win']['double down'] * 2) +
                    (count_values['win']['double after split'] * 2) +
                    count_values['win']['split'] +
                    count_values['win']['other'] +
                    count_values['loss']['surrender'] +
                    (count_values['loss']['insurance'] * 0.5) +
                    (count_values['loss']['double down'] * 2) +
                    (count_values['win']['double after split'] * -2) +
                    count_values['loss']['split'] +
                    count_values['loss']['other'] +
                    (count_values['push']['double down'] * 2) +
                    (count_values['push']['double after split'] * 2) +
                    count_values['push']['split'] +
                    count_values['push']['other']
                )
                num_hands = np.append(
                    num_hands,
                    count_values['win']['number of hands'] +
                    count_values['loss']['number of hands'] +
                    count_values['push']['number of hands']
                )
                split_hands = np.append(
                    split_hands,
                    count_values['win']['double after split'] +
                    count_values['win']['split'] +
                    count_values['loss']['double after split'] +
                    count_values['loss']['split'] +
                    count_values['push']['double after split'] +
                    count_values['push']['split']
                )

            # get initial bet for each count played
            for p in self.players:
                if p.get_name() == player_key:
                    if p.get_bet_strategy() == 'Spread':
                        initial_bet_count = np.array([])
                        for c in count:
                            amount = p.get_bet_spread() * p.get_min_bet()
                            for key, value in p.get_bet_scale().items():
                                if c < key:
                                    amount = value
                                    break
                            initial_bet_count = np.append(initial_bet_count, amount)
                    else:
                        initial_bet_count = p.get_min_bet()

            net_winnings = net_winnings * initial_bet_count
            overall_bet = overall_bet * initial_bet_count
            initial_bet = (num_hands * initial_bet_count) - (split_hands * initial_bet_count)

            # overall statistics
            print('Total hands:', np.sum(num_hands))
            print('Split hands:', np.sum(split_hands))
            if np.sum(num_hands) > 0:  # prevents divide by zero issues
                print('Total amount bet:', np.sum(overall_bet))
                print('Total initial bet:', np.sum(initial_bet))
                print('Total net winnings:', np.sum(net_winnings))
                print('House edge:', 100 * (np.sum(net_winnings) / np.sum(initial_bet)))
                print('Element of risk:', 100 * (np.sum(net_winnings) / np.sum(overall_bet)))
                print('\n')
        #
        #     # figures are only created for players that are counting cards
        #     if self.figures:
        #         for p in self.players:
        #             if p.get_name() == player_key:
        #                 if p.get_count_strategy() is not None:
        #                     net_winnings_figure(
        #                         count=count,
        #                         true_count_accuracy=p.get_true_count_accuracy(),
        #                         net_winnings=net_winnings,
        #                         name=p.get_name(),
        #                         shoe_size=self.shoe_size,
        #                         penetration=self.penetration,
        #                         blackjack_payout=self.rules.blackjack_payout,
        #                         count_strategy=p.get_count_strategy(),
        #                         play_strategy=p.play_strategy.get_strategy(),
        #                         bet_strategy=p.bet_strategy.get_strategy(),
        #                         bet_spread=p.get_bet_spread(),
        #                         initial_bankroll=ending_bankroll[p.get_name()][0],
        #                         min_bet=p.get_min_bet(),
        #                         simulations=self.simulations
        #                     )