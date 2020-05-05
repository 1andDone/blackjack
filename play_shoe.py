import random
import numpy as np

from cards import Cards
from counting_strategy import CountingStrategy
from table import Table
from simulation_stats import SimulationStats
from gameplay import players_place_bets, deal_hands, players_play_hands, dealer_turn, dealer_plays_hand, compare_hands
from figures import net_winnings_per_shoe, cumulative_net_winnings_per_shoe, bankroll_growth


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
            Seed number used to replicate results (default is None)
        shoe_size : int, optional
            Number of decks used during a blackjack game (default is 6)
        penetration : float, optional
            Percentage of shoe played before the deck is re-shuffled (default is 0.75)
        simulations : int, optional
            Number of shoes played (default is 10,000)
        figures : bool, optional
            True if plots are created, false otherwise (default is False)
        """
        self.rules = rules
        self.players = players
        self.seed_number = seed_number
        self.shoe_size = shoe_size
        self.penetration = penetration
        self.simulations = simulations
        self.figures = figures
        self.stats = SimulationStats(rules=rules)

    def main(self):

        # set seed to replicate results
        if self.seed_number is not None:
            random.seed(self.seed_number)

        # set up table
        t = Table()

        # dictionary that stores current bankroll at the end of each hand
        current_bankroll = {}

        # dictionary that stores bankroll at the end of each shoe
        ending_bankroll = {}

        for p in self.players:

            # add players to table
            if not p.get_back_counting():
                t.add_player(player=p)

            # update current bankroll
            current_bankroll[p.get_name()] = p.get_bankroll()
            ending_bankroll[p.get_name()] = {}

            # update ending bankroll
            ending_bankroll[p.get_name()][0] = p.get_bankroll()

        for sim in range(1, self.simulations + 1):

            # set up cards and shuffle
            c = Cards(shoe_size=self.shoe_size)
            c.shuffle()

            # keep track of card counts
            cs = CountingStrategy(cards=c)

            while not c.cut_card_reached(penetration=self.penetration) and len(t.get_players()) > 0:

                # add back counters to the table if the count is favorable
                for p in self.players:
                    if p.get_back_counting() and p not in t.get_players() and current_bankroll[p.get_name()] >= \
                            self.rules.min_bet and p.get_count_strategy() is not None:
                        if cs.true_count(strategy=p.get_count_strategy(), accuracy=p.get_count_accuracy()) >= \
                                p.get_back_counting_entry_exit()[0]:
                            t.add_player(player=p)

                # remove back counters from the table if the count is not favorable
                for p in self.players:
                    if p.get_back_counting() and p in t.get_players() and p.get_count_strategy() is not None:
                        if cs.true_count(strategy=p.get_count_strategy(), accuracy=p.get_count_accuracy()) < \
                                p.get_back_counting_entry_exit()[1]:
                            t.remove_player(player=p)

                for p in t.get_players():

                    # get true count
                    if p.get_count_strategy() is not None:
                        p.set_count(
                            count=cs.true_count(
                                    strategy=p.get_count_strategy(),
                                    accuracy=p.get_count_accuracy()
                            )
                        )

                    else:
                        p.set_count(count=0)

                    # create player key in stats dictionary
                    self.stats.create_player_key(player_key=p.get_name())

                    # create count key in stats dictionary
                    self.stats.create_count_key(player_key=p.get_name(), count_key=p.get_count())

                # players place initial bets and an empty hand is created
                players_place_bets(table=t, rules=self.rules, counting_strategy=cs)

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

                    # dealer acts if one or more players do not bust, surrender, or have natural 21
                    if dealer_turn(table=t):
                        dealer_hand = dealer_plays_hand(
                            rules=self.rules,
                            cards=c,
                            dealer_hole_card=dealer_hole_card,
                            dealer_hand=dealer_hand
                        )

                    # compare players hand(s) to dealer and pay out to winning players
                    compare_hands(
                        table=t,
                        rules=self.rules,
                        stats=self.stats,
                        dealer_hand=dealer_hand
                    )

                    # update count and reset visible cards
                    cs.update_running_count()
                    c.set_visible_cards()

                    # update current bankroll for each player
                    for p in self.players:
                        current_bankroll[p.get_name()] = p.get_bankroll()

                    # update ending bankroll for only players involved in that shoe
                    for p in t.get_players():
                        ending_bankroll[p.get_name()][sim] = p.get_bankroll()

        # unpack nested dictionary
        for player_key, player_values in self.stats.get_stats_dict().items():
            print('Player:', player_key)
            print('--------' + '-' * len(player_key))

            # create arrays
            count = np.array([])
            initial_bet = np.array([])
            overall_bet = np.array([])
            net_winnings = np.array([])
            player_insurance_win = np.array([])
            dealer_insurance_win = np.array([])
            push = np.array([])
            player_surrender = np.array([])
            player_bust = np.array([])
            dealer_bust = np.array([])
            player_natural_blackjack = np.array([])
            dealer_natural_blackjack = np.array([])
            player_showdown_win = np.array([])
            dealer_showdown_win = np.array([])
            num_hands = np.array([])

            for count_key, count_values in sorted(player_values.items()):
                count = np.append(count, count_key)
                for i in count_values.items():
                    if i[0] == 'overall bet':
                        overall_bet = np.append(overall_bet, i[1])
                    elif i[0] == 'initial bet':
                        initial_bet = np.append(initial_bet, i[1])
                    elif i[0] == 'net winnings':
                        net_winnings = np.append(net_winnings, i[1])
                    elif i[0] == 'player insurance win':
                        player_insurance_win = np.append(player_insurance_win, i[1])
                    elif i[0] == 'dealer insurance win':
                        dealer_insurance_win = np.append(dealer_insurance_win, i[1])
                    elif i[0] == 'player showdown win':
                        player_showdown_win = np.append(player_showdown_win, i[1])
                    elif i[0] == 'dealer showdown win':
                        dealer_showdown_win = np.append(dealer_showdown_win, i[1])
                    elif i[0] == 'push':
                        push = np.append(push, i[1])
                    elif i[0] == 'player surrender':
                        player_surrender = np.append(player_surrender, i[1])
                    elif i[0] == 'player bust':
                        player_bust = np.append(player_bust, i[1])
                    elif i[0] == 'dealer bust':
                        dealer_bust = np.append(dealer_bust, i[1])
                    elif i[0] == 'player natural blackjack':
                        player_natural_blackjack = np.append(player_natural_blackjack, i[1])
                    elif i[0] == 'dealer natural blackjack':
                        dealer_natural_blackjack = np.append(dealer_natural_blackjack, i[1])
                    elif i[0] == 'number of hands':
                        num_hands = np.append(num_hands, i[1])
                    else:
                        raise NotImplementedError('No implementation for array.')

            # overall statistics
            print('Total hands:', np.sum(num_hands))
            print('Total amount bet:', np.sum(overall_bet))
            print('Total initial bet:', np.sum(initial_bet))
            print('Total net winnings:', np.sum(net_winnings))
            print('House edge:', 100 * (np.sum(net_winnings) / np.sum(initial_bet)))
            print('Element of risk:', 100 * (np.sum(net_winnings) / np.sum(overall_bet)))
            print('\n')

            # figures for players that are counting cards
            if self.figures:
                for p in self.players:
                    if p.get_name() == player_key:
                        if p.get_count_strategy() is not None:
                            net_winnings_per_shoe(
                                count=count,
                                count_accuracy=p.get_count_accuracy(),
                                net_winnings=net_winnings,
                                name=p.get_name(),
                                shoe_size=self.shoe_size,
                                penetration=self.penetration,
                                blackjack_payout=self.rules.blackjack_payout,
                                count_strategy=p.get_count_strategy(),
                                play_strategy=p.play_strategy.get_strategy(),
                                bet_strategy=p.bet_strategy.get_strategy(),
                                bet_spread=p.get_bet_spread(),
                                initial_bankroll=ending_bankroll[p.get_name()][0],
                                min_bet=p.get_min_bet(),
                                simulations=self.simulations
                            )
                            cumulative_net_winnings_per_shoe(
                                    count=count,
                                    net_winnings=net_winnings,
                                    name=p.get_name(),
                                    shoe_size=self.shoe_size,
                                    penetration=self.penetration,
                                    blackjack_payout=self.rules.blackjack_payout,
                                    count_strategy=p.get_count_strategy(),
                                    play_strategy=p.play_strategy.get_strategy(),
                                    bet_strategy=p.bet_strategy.get_strategy(),
                                    bet_spread=p.get_bet_spread(),
                                    initial_bankroll=ending_bankroll[p.get_name()][0],
                                    min_bet=p.get_min_bet(),
                                    simulations=self.simulations
                            )

        # figures for all players
        if self.figures:
            for player_key, player_values in ending_bankroll.items():
                shoe_num = np.array([])
                bankroll = np.array([])

                for shoe_key, shoe_values in sorted(player_values.items()):
                    shoe_num = np.append(shoe_num, shoe_key)
                    bankroll = np.append(bankroll, shoe_values)

                for p in self.players:
                    if p.get_name() == player_key:
                        bankroll_growth(
                            bankroll=bankroll,
                            shoe_num=shoe_num,
                            name=p.get_name(),
                            shoe_size=self.shoe_size,
                            penetration=self.penetration,
                            blackjack_payout=self.rules.blackjack_payout,
                            count_strategy=p.get_count_strategy(),
                            play_strategy=p.play_strategy.get_strategy(),
                            bet_strategy=p.bet_strategy.get_strategy(),
                            bet_spread=p.get_bet_spread(),
                            initial_bankroll=ending_bankroll[p.get_name()][0],
                            min_bet=p.get_min_bet(),
                            simulations=self.simulations
                        )