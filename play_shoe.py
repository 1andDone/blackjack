import random
import numpy as np
from house_rules import HouseRules
from cards import Cards
from counting_strategy import CountingStrategy
from table import Table
from gameplay import deal_hands, players_play_hands, dealer_turn, dealer_plays_hand, compare_hands
from figures import net_winnings_figure


class PlayShoe(object):
    """
    PlayShoe is an object that simulates the playing of a shoe between
    players and dealer.

    """
    def __init__(
            self, rules, players, seed_number=None, penetration=0.75,
            simulations=10000, figures=False
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
        penetration : float, optional
            Percentage of shoe played before the deck is re-shuffled (default is 0.75)
        simulations : int, optional
            Number of shoes played (default is 10,000)
        figures : bool, optional
            True if default plots are created, false otherwise (default is False)
        """
        if not isinstance(rules, HouseRules):
            raise TypeError('Rules must be of type HouseRules.')
        self._rules = rules
        self._players = players
        self._seed_number = seed_number
        self._penetration = penetration
        self._simulations = simulations
        self._figures = figures

    @property
    def rules(self):
        return self._rules

    @property
    def players(self):
        return self._players

    @property
    def seed_number(self):
        return self._seed_number

    @property
    def shoe_size(self):
        return self._shoe_size

    @property
    def penetration(self):
        return self._penetration

    @property
    def simulations(self):
        return self._simulations

    @property
    def figures(self):
        return self._figures

    def main(self):

        # set seed to replicate results
        if self._seed_number is not None:
            random.seed(self._seed_number)

        # set up table
        t = Table()

        # add players to table
        for p in self._players:
            if not p.back_counting:
                t.add_player(player=p)

        # balanced and unbalanced card counting systems
        balanced_card_counting_systems = ['Hi-Lo', 'Hi-Opt I', 'Hi-Opt II', 'Omega II', 'Halves', 'Zen Count']

        for sim in range(0, self._simulations):

            # set up cards and shuffle
            c = Cards(rules=self._rules)
            c.shuffle()

            # keep track of card counts
            cs = CountingStrategy(rules=self._rules, cards=c)

            # re-shuffle when desired deck penetration is reached
            while not c.cut_card_reached(penetration=self._penetration):

                for p in self._players:

                    # compute counts for betting decision
                    if p.count_strategy is not None:
                        if p.count_strategy in balanced_card_counting_systems:
                            p.bet_count = cs.true_count(strategy=p.count_strategy)
                        else:
                            p.bet_count = cs.running_count(strategy=p.count_strategy)

                    if p.back_counting:

                        # add back counters
                        if p.bet_count >= p.back_counting_entry and p not in t.players:
                            t.add_player(player=p)

                        # remove back counters
                        if p.bet_count < p.back_counting_exit and p in t.players:
                            t.remove_player(player=p)

                    # non-card counters will have bet_count = 0
                    p.stats.create_count_key(count_key=p.bet_count)

                # only deal hands if there are players (cannot have a table with just a back counter)
                if len(t.players) > 0:

                    # deal hands to all players and dealer
                    dealer_hand = deal_hands(table=t, cards=c)

                    # dealers cards
                    dealer_hole_card = dealer_hand[0]
                    dealer_up_card = dealer_hand[1]

                    # re-compute counts before insurance bet
                    if self._rules.insurance:

                        for p in self._players:
                            if p.insurance is not None:
                                if p.count_strategy in balanced_card_counting_systems:
                                    p.pre_insurance_count = cs.true_count(strategy=p.count_strategy)
                                else:
                                    p.pre_insurance_count = cs.running_count(strategy=p.count_strategy)

                                # create separate key for current count before making insurance bet
                                p.stats.create_count_key(count_key=p.pre_insurance_count)

                    # players play out each of their hands
                    # player and dealer blackjacks, player surrenders or busts are settled
                    players_play_hands(
                        table=t,
                        rules=self._rules,
                        cards=c,
                        dealer_hand=dealer_hand,
                        dealer_up_card=dealer_up_card
                    )

                    # dealer acts if one or more players have a live hand
                    if dealer_turn(table=t):
                        dealer_total = dealer_plays_hand(
                            rules=self._rules,
                            cards=c,
                            dealer_hole_card=dealer_hole_card,
                            dealer_hand=dealer_hand
                        )

                        # compare players hand(s) to dealer and pay out to players, house
                        compare_hands(
                            table=t,
                            dealer_total=dealer_total
                        )

                    # dealer reveals hole card when all players bust, surrender, or have natural 21
                    else:
                        if self._rules.dealer_shows_hole_card:
                            c.add_to_seen_cards(card=dealer_hole_card)

        # print out rules used for simulation
        print('\n')
        print('Rules:', self._rules.__str__())
        print('-------' + '-' * self.rules.__str__().__len__())
        print('\n')

        # unpacked nested dictionary
        for p in self._players:

            # create empty arrays
            count = np.array([])
            net_winnings = np.array([])
            overall_bet = np.array([])
            num_rounds = np.array([])
            split_hands = np.array([])

            for count_key, count_values in sorted(p.stats.results_dict.items()):
                count = np.append(count, count_key)
                net_winnings = np.append(net_winnings, count_values['net winnings'])
                overall_bet = np.append(overall_bet, count_values['overall bet'])
                num_rounds = np.append(num_rounds, count_values['number of rounds'])
                split_hands = np.append(split_hands, count_values['number of split hands'])

            # get initial bet for each count played
            initial_bet_count = np.array([])

            if p.bet_strategy == 'Spread':
                for c in count:
                    amount = p.bet_spread * p.min_bet
                    for key, value in p.bet_ramp.items():
                        if c < key:
                            amount = value
                            break
                    initial_bet_count = np.append(initial_bet_count, amount)
            else:
                initial_bet_count = p.min_bet

            # compute totals
            net_winnings_total = np.sum(net_winnings * initial_bet_count)
            overall_bet_total = np.sum(overall_bet * initial_bet_count)
            initial_bet_total = np.sum(num_rounds * initial_bet_count)

            # overall statistics
            print('Player:', p.name)
            print('--------' + '-' * len(p.name))
            print('Total rounds played:', np.sum(num_rounds))
            print('Split hands:', np.sum(split_hands))
            if np.sum(num_rounds) > 0:  # prevents divide by zero issues
                print('Total amount bet:', overall_bet_total)
                print('Total initial bet:', initial_bet_total)
                print('Total net winnings:', net_winnings_total)
                print('House edge:', 100 * (net_winnings_total/initial_bet_total))
                print('Element of risk:', 100 * (net_winnings_total/overall_bet_total))
                print('\n')

            # figures are only created for players that are counting cards
            if self._figures:
                if p.count_strategy is not None:
                    if np.sum(num_rounds) > 0:
                        net_winnings_figure(
                            count=count,
                            net_winnings=net_winnings * initial_bet_count,
                            name=p.name,
                            shoe_size=self.rules.shoe_size,
                            penetration=self._penetration,
                            blackjack_payout=self._rules.blackjack_payout,
                            count_strategy=p.count_strategy,
                            play_strategy=p.play_strategy.strategy,
                            bet_strategy=p.bet_strategy,
                            bet_spread=p.bet_spread,
                            initial_bankroll=p.bankroll,
                            min_bet=p.min_bet,
                            simulations=self._simulations
                        )
