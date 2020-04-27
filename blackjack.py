import random
import matplotlib.pyplot as plt
import numpy as np

import basic_strategy
import counting_strategies
from helper import count_hand, max_count_hand, splittable

random.seed(78)

# TODO make plot size bigger -- figsize
# TODO plot distribution of end bankroll amounts
# TODO clean up classes - Player may be too large, may need Game class
# TODO Kelly Criterion?
# TODO run simulations and make plots for more than one player -- may need to include player in dict
# TODO use actual chip amounts -- only allow bets using chip increments?
# TODO tests -- test out every type of hand, multiple ways to get blackjack, bust, etc.
# TODO add additional counting systems from https://en.wikipedia.org/wiki/Card_counting
# TODO some counting systems require the type of card (spade, diamond, etc.)
# TODO composition dependent strategy https://wizardofodds.com/gambling/glossary/

class HouseRules(object):
    """
    HouseRules is an object where all of the table rules are set.

    """
    def __init__(
            self, min_bet, max_bet, s17, blackjack_payout=1.5, max_hands=4, double_down=True,
            double_after_split=True, resplit_aces=False, insurance=True, late_surrender=True,
            dealer_shows_hole_card=False
    ):
        """
        Parameters
        ----------
        min_bet : int
            Minimum bet allowed at the table
        max_bet : int
            Maximum bet allowed at the table
        s17 : bool
            True if dealer stands on a soft 17, false otherwise
        blackjack_payout : float
            The payout for a player receiving a natural blackjack (default is 1.5, which implies
            a 3:2 payout)
        max_hands : int, optional
            The maximum number of hands that a player can play (default is 4)
        double_down : bool, optional
            True if doubling is allowed on any first two cards, false otherwise (default is True)
        double_after_split : bool, optional
            True if doubling after splits is allowed, false otherwise (default is True)
        resplit_aces : bool, optional
            True if re-splitting aces is allowed, false otherwise (default is False)
        insurance : bool, optional
            True if insurance bet is allowed, false otherwise (default is True)
        late_surrender : bool, optional
            True if late surrender is allowed, false otherwise (default is True)
        dealer_shows_hole_card : bool, optional
            True if the dealer shows his hole card regardless of whether or not all players bust,
            surrender, or have natural 21, false otherwise (default is False)
        """
        if max_bet < min_bet:
            raise ValueError('Maximum bet at table must be greater than minimum bet.')
        if max_hands not in [2, 3, 4]:
            raise ValueError('Maximum number of hands must be 2, 3, or 4.')
        if blackjack_payout <= 1:
            raise ValueError('Blackjack payout must be greater than 1.')
        self.min_bet = int(min_bet)
        self.max_bet = int(max_bet)
        self.s17 = s17
        self.blackjack_payout = float(blackjack_payout)
        self.max_hands = int(max_hands)
        self.double_down = double_down
        self.double_after_split = double_after_split
        self.resplit_aces = resplit_aces
        self.insurance = insurance
        self.late_surrender = late_surrender
        self.dealer_shows_hole_card = dealer_shows_hole_card


class Cards(object):
    """
    Cards is an object that deals with a shoe at a table.

    """
    def __init__(self, shoe_size):
        """
        Parameters
        ----------
        shoe_size: int
            Number of decks used during a blackjack game
        """
        if shoe_size not in [4, 6, 8]:
            raise ValueError('Shoe size must be 4, 6, or 8.')
        self.shoe_size = int(shoe_size)
        self.deck = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'] * 4 * int(shoe_size)
        self.visible_cards = []

    def burn_card(self):
        return self.deck.pop()

    def shuffle(self):
        random.shuffle(self.deck)
        self.burn_card()

    def deal_card(self, visible=True):
        card = self.deck.pop()
        if visible:
            self.visible_cards.append(card)
        return card

    def set_visible_cards(self):
        self.visible_cards = []

    def get_visible_cards(self):
        return self.visible_cards

    def update_visible_cards(self, card):
        self.visible_cards.append(card)

    def remaining_decks(self):
        return len(self.deck)/52

    def cut_card_reached(self, penetration):
        if penetration < 0.5 or penetration > 0.9:
            raise ValueError('Penetration must be between 0.5 and 0.9.')
        total_cards = 52 * self.shoe_size
        remaining_cards = total_cards - len(self.deck)
        return remaining_cards/total_cards >= float(penetration)


class BettingStrategy(object):
    """
    BettingStrategy is a class that determines the betting strategy used by
    a player at the table.

    """
    def __init__(self, strategy):
        """
        Parameters
        ----------
        strategy : str
            Name of the betting strategy used by a player at the table
        """
        if strategy not in ['Fixed', 'Variable']:
            raise ValueError('Betting strategy must be either "Fixed" or "Variable".')
        self.strategy = strategy

    def get_strategy(self):
        return self.strategy

    def initial_bet(self, min_bet, bet_spread, count=None, count_strategy=None):
        if self.strategy == 'Fixed':
            return min_bet
        elif self.strategy == 'Variable':
            if count_strategy in ['Hi-Lo', 'Omega II', 'Halves', 'Zen Count']:
                if count < 1:
                    return min_bet
                elif count < 3:
                    return min_bet * (1 + (0.25 * (bet_spread - 1)))
                elif count < 5:
                    return min_bet * (1 + (0.5 * (bet_spread - 1)))
                elif count < 10:
                    return min_bet * (1 + (0.75 * (bet_spread - 1)))
                else:
                    return min_bet * bet_spread
            else:
                raise NotImplementedError('No implementation for running counts.')


class CountingStrategy(object):
    """
    CountingStrategy is an object that represents the card counting strategy used by
    a player at the table in order to make informed betting decisions.

    """
    def __init__(self, cards):
        """
        Parameters
        ----------
        cards : Cards
            Cards class instance

        """
        self.cards = cards
        running_count_dict = {}
        for strategy in ['Hi-Lo', 'Hi-Opt I', 'Hi-Opt II', 'Omega II', 'Halves', 'Zen Count']:
            running_count_dict[strategy] = 0
        self.running_count_dict = running_count_dict

    def update_running_count(self):
        for strategy in ['Hi-Lo', 'Hi-Opt I', 'Hi-Opt II', 'Omega II', 'Halves', 'Zen Count']:
            for card in self.cards.get_visible_cards():
                self.running_count_dict[strategy] += counting_strategies.count_dict[strategy].get(card)

    def running_count(self, strategy):
        if strategy not in ['Hi-Lo', 'Hi-Opt I', 'Hi-Opt II', 'Omega II', 'Halves', 'Zen Count']:
            raise ValueError('Strategy must be "Hi-Lo", "Hi-Opt I", "Hi-Opt II", "Omega II", "Halves", or "Zen Count".')
        return self.running_count_dict[strategy]

    def true_count(self, strategy, accuracy=0.5):
        if strategy not in ['Hi-Lo', 'Omega II', 'Halves', 'Zen Count']:
            raise ValueError('Strategy must be "Hi-Lo", "Omega II", "Halves", or "Zen Count".')
        if accuracy not in [0.1, 0.5, 1]:
            raise ValueError('Accuracy of true count must be to the nearest 0.1, 0.5, or 1.')
        if accuracy == 0.1:
            return round(self.running_count(strategy=strategy)/self.cards.remaining_decks(), 1)
        elif accuracy == 0.5:
            return round((self.running_count(strategy=strategy)/self.cards.remaining_decks()) * 2, 0)/2
        else:
            return round(self.running_count(strategy=strategy)/self.cards.remaining_decks(), 0)


class PlayingStrategy(object):
    """
    PlayingStrategy is an object that represents the decisions a player will make when
    faced with a split situation or a certain soft/hard count. Decisions are typically based
    on whether or not a dealer stands or hits on a soft 17.

    """
    def __init__(self, rules, strategy):
        """
        Parameters
        ----------
        rules : HouseRules
            HouseRules class instance
        strategy : str
            Name of the playing strategy used by a player at the table
        """
        if strategy not in ['Basic']:
            raise ValueError('Strategy must be "Basic".')
        self.rules = rules
        self.strategy = strategy

    def splits(self):
        if self.strategy == 'Basic':
            if self.rules.s17:
                return basic_strategy.s17_splits
            return basic_strategy.h17_splits

    def soft(self):
        if self.strategy == 'Basic':
            if self.rules.s17:
                return basic_strategy.s17_soft
            return basic_strategy.h17_soft

    def hard(self):
        if self.strategy == 'Basic':
            if self.rules.s17:
                return basic_strategy.s17_hard
            return basic_strategy.h17_hard


class Player(object):
    """
    Player is an object that represents an individual player at the table.

    """
    def __init__(self, name, rules, bankroll, min_bet, bet_spread=1, play_strategy='Basic',
                 bet_strategy='Fixed', count_strategy=None):
        """
        Parameters
        ----------
        name : str
            Name of the player
        rules : HouseRules
            HouseRules class instance
        bankroll : float
            Amount of money a player starts out with when sitting down at a table
        min_bet : float
            Minimum amount of money a player is willing to wager when playing a hand
        bet_spread : float, optional
            Ratio of maximum bet to minimum bet (default is 1)
        play_strategy : str, optional
            Name of the play strategy used by the player (default is 'Basic', which implies
            the player plays optimally)
        bet_strategy : str, optional
            Name of the bet strategy used by the player (default is 'Fixed', which implies
            the player bets the same amount every hand)
        count_strategy : str, optional
            Name of the card counting strategy used by the player (default is None, which implies
            the player does not count cards)
        """
        if bankroll <= rules.min_bet:
            raise ValueError('Initial bankroll must be greater than minimum bet.')
        if bet_strategy == 'Variable' and bet_spread < 1:
            raise ValueError('Bet spread must be greater than 1.')
        if min_bet < rules.min_bet or min_bet > rules.max_bet:
            raise ValueError('Minimum bet is not allowed according to the table rules.')
        if bet_spread > float(rules.max_bet/rules.min_bet) or bet_spread > float(bankroll/min_bet):
            raise ValueError('Bet spread is too large.')
        if bet_strategy == 'Variable' and count_strategy is None:
            raise ValueError('Count strategy cannot be None with a Variable betting strategy.')
        if play_strategy not in ['Basic']:
            raise ValueError('Playing strategy must be "Basic".')
        if bet_strategy not in ['Fixed', 'Variable']:
            raise ValueError('Betting strategy must be either "Fixed" or "Variable".')
        if count_strategy is not None:
            if count_strategy not in ['Hi-Lo', 'Hi-Opt I', 'Hi-Opt II', 'Omega II', 'Halves', 'Zen Count']:
                raise ValueError('Count Strategy must be "Hi-Lo", "Hi-Opt I", "Hi-Opt II", "Omega II", '
                                 '"Halves", or "Zen Count".')
        self.name = name
        self.rules = rules
        self.bankroll = float(bankroll)
        self.min_bet = float(min_bet)
        self.bet_spread = float(bet_spread)
        self.play_strategy = PlayingStrategy(rules=rules, strategy=play_strategy)
        self.bet_strategy = BettingStrategy(strategy=bet_strategy)
        self.count_strategy = count_strategy
        self.hands_dict = {}

    def get_name(self):
        return self.name

    def get_bankroll(self):
        return self.bankroll

    def get_min_bet(self):
        return self.min_bet

    def get_bet_spread(self):
        return self.bet_spread

    def set_bankroll(self, amount):
        self.bankroll = self.bankroll + amount

    def sufficient_funds(self, amount):
        return self.bankroll - amount >= 0

    def get_count_strategy(self):
        return self.count_strategy

    def create_hand(self, amount):
        self.hands_dict = {1: {}}
        self.hands_dict[1]['hand'] = []
        self.hands_dict[1]['initial bet'] = amount
        self.hands_dict[1]['bet'] = amount
        self.hands_dict[1]['natural blackjack'] = False
        self.hands_dict[1]['surrender'] = False
        self.hands_dict[1]['busted'] = False
        self.hands_dict[1]['split'] = False
        self.hands_dict[1]['stand'] = False

    def initial_bet(self, amount):
        if amount < self.rules.min_bet:
            raise ValueError('Initial bet must exceed table minimum.')
        if amount > self.rules.max_bet:
            raise ValueError('Initial bet must not exceed table maximum.')
        self.set_bankroll(-amount)
        self.create_hand(amount)

    def natural_blackjack(self):
        self.hands_dict[1]['natural blackjack'] = True

    def surrender(self):
        self.hands_dict[1]['surrender'] = True

    def busted(self, key):
        self.hands_dict[key]['busted'] = True
        self.stand(key=key)

    def stand(self, key):
        self.hands_dict[key]['stand'] = True

    def get_hand(self, key):
        return self.hands_dict[key]['hand']

    def get_initial_bet(self, key):
        return self.hands_dict[key]['initial bet']

    def get_bet(self, key):
        return self.hands_dict[key]['bet']

    def get_natural_blackjack(self):
        return self.hands_dict[1]['natural blackjack']

    def get_surrender(self):
        return self.hands_dict[1]['surrender']

    def get_busted(self, key):
        return self.hands_dict[key]['busted']

    def get_split(self, key):
        return self.hands_dict[key]['split']

    def get_stand(self, key):
        return self.hands_dict[key]['stand']

    def hit(self, key, new_card):
        self.hands_dict[key]['hand'].append(new_card)

    def double_down(self, key, new_card):
        self.hands_dict[key]['bet'] = 2 * self.hands_dict[key]['bet']
        self.hit(key=key, new_card=new_card)
        self.stand(key=key)

    def split(self, amount, key, new_key):
        if splittable(hand=self.hands_dict[key]['hand']):
            self.hands_dict[key]['split'] = True
            self.hands_dict[new_key] = {}
            self.hands_dict[new_key]['hand'] = [self.get_hand(key=key).pop()]
            self.hands_dict[new_key]['bet'] = amount
            self.hands_dict[new_key]['busted'] = False
            self.hands_dict[new_key]['split'] = True
            self.hands_dict[new_key]['stand'] = False

    def decision(self, hand, dealer_up_card, num_hands, amount):
        if len(hand) == 1:  # if card is split, first action is always to hit
            return 'H'
        elif splittable(hand=hand) and num_hands < self.rules.max_hands and self.sufficient_funds(amount=amount):
            return self.play_strategy.splits()[hand[0]][dealer_up_card]
        else:
            soft_total, hard_total = count_hand(hand=hand)
            if soft_total > hard_total and 12 <= soft_total <= 21:  # must contain an Ace
                return self.play_strategy.soft()[soft_total][dealer_up_card]
            elif 2 <= hard_total <= 21:
                return self.play_strategy.hard()[hard_total][dealer_up_card]
            else:  # player is busted
                return 'B'


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
        if size_limit > 7:
            raise ValueError('Table cannot have more than 7 seats.')
        self.size_limit = int(size_limit)
        self.players = []

    def get_players(self):
        return self.players

    def add_player(self, player):
        if isinstance(player, Player):
            if len(self.players) + len([player]) > self.size_limit:
                raise ValueError('Table is at maximum capacity.')
            self.players.append(player)
        elif isinstance(player, list):
            if len(self.players) + len(player) > self.size_limit:
                raise ValueError('Table is at maximum capacity.')
            self.players.extend(player)
        else:
            raise ValueError('Expected a list or "Player" class object.')

    def remove_player(self, player):
        if player in self.players:
            self.players.remove(player)
        return 'Player cannot be removed because the player is not at the table.'


class SimulationStats(object):
    """
    SimulationStats is an object that stores results from simulating
    games of blackjack.

    """
    def __init__(self, rules):
        """
        Parameters
        ----------
        rules : HouseRules
            HouseRules class instance
        """
        self.rules = rules
        self.stats_dict = {}

    def get_stats_dict(self):
        return self.stats_dict

    def create_key(self, key):
        if key not in self.stats_dict.keys():
            self.stats_dict[key] = {}
            self.stats_dict[key]['initial bet'] = 0
            self.stats_dict[key]['overall bet'] = 0
            self.stats_dict[key]['net winnings'] = 0
            self.stats_dict[key]['player showdown win'] = 0
            self.stats_dict[key]['dealer showdown win'] = 0
            self.stats_dict[key]['push'] = 0
            self.stats_dict[key]['player surrender'] = 0
            self.stats_dict[key]['player bust'] = 0
            self.stats_dict[key]['dealer bust'] = 0
            self.stats_dict[key]['player natural blackjack'] = 0
            self.stats_dict[key]['dealer natural blackjack'] = 0
            self.stats_dict[key]['number of hands'] = 0

    def player_bets(self, key, amount, initial_amount):
        self.stats_dict[key]['initial bet'] += initial_amount
        self.stats_dict[key]['overall bet'] += amount

    def player_showdown_win(self, key, amount, initial_amount):
        self.stats_dict[key]['player showdown win'] += 1
        self.stats_dict[key]['number of hands'] += 1
        self.stats_dict[key]['net winnings'] += amount
        self.player_bets(key=key, amount=amount, initial_amount=initial_amount)

    def dealer_showdown_win(self, key, amount, initial_amount):
        self.stats_dict[key]['dealer showdown win'] += 1
        self.stats_dict[key]['number of hands'] += 1
        self.stats_dict[key]['net winnings'] += -amount
        self.player_bets(key=key, amount=amount, initial_amount=initial_amount)

    def push(self, key, amount, initial_amount):
        self.stats_dict[key]['push'] += 1
        self.stats_dict[key]['number of hands'] += 1
        self.player_bets(key=key, amount=amount, initial_amount=initial_amount)

    def player_surrender(self, key, amount, initial_amount):
        self.stats_dict[key]['player surrender'] += 1
        self.stats_dict[key]['number of hands'] += 1
        self.stats_dict[key]['net winnings'] += -0.5 * amount
        self.player_bets(key=key, amount=amount, initial_amount=initial_amount)

    def dealer_bust(self, key, amount, initial_amount):
        self.stats_dict[key]['dealer bust'] += 1
        self.stats_dict[key]['number of hands'] += 1
        self.stats_dict[key]['net winnings'] += amount
        self.player_bets(key=key, amount=amount, initial_amount=initial_amount)

    def player_bust(self, key, amount, initial_amount):
        self.stats_dict[key]['player bust'] += 1
        self.stats_dict[key]['number of hands'] += 1
        self.stats_dict[key]['net winnings'] += -amount
        self.player_bets(key=key, amount=amount, initial_amount=initial_amount)

    def dealer_natural_blackjack(self, key, amount, initial_amount):
        self.stats_dict[key]['dealer natural blackjack'] += 1
        self.stats_dict[key]['number of hands'] += 1
        self.stats_dict[key]['net winnings'] += -amount
        self.player_bets(key=key, amount=amount, initial_amount=initial_amount)

    def player_natural_blackjack(self, key, amount, initial_amount):
        self.stats_dict[key]['player natural blackjack'] += 1
        self.stats_dict[key]['number of hands'] += 1
        self.stats_dict[key]['net winnings'] += self.rules.blackjack_payout * amount
        self.player_bets(key=key, amount=amount, initial_amount=initial_amount)


def players_place_bets(table, rules, counting_strategy):
    """
    Players at table place bets. If they're unable to bet the desired
    amount, they place a bet closest to that amount, while staying within
    the betting constraints of the table. If they are unable to make the
    minimum bet, they are removed from the table.

    Parameters
    ----------
    table : Table
        Table class instance
    rules : HouseRules
        HouseRules class instance
    counting_strategy : CountingStrategy
        CountingStrategy class instance

    """
    for p in table.get_players():

        if p.get_count_strategy() is None:
            amount = p.bet_strategy.initial_bet(
                                        min_bet=p.get_min_bet(),
                                        bet_spread=p.get_bet_spread()
            )

        elif p.get_count_strategy() in ['Hi-Lo', 'Omega II', 'Halves', 'Zen Count']:
            amount = p.bet_strategy.initial_bet(
                                        min_bet=p.get_min_bet(),
                                        bet_spread=p.get_bet_spread(),
                                        count=counting_strategy.true_count(strategy=p.get_count_strategy()),
                                        count_strategy=p.get_count_strategy()
            )

        else:
            raise NotImplementedError('No implementation for running counts')

        # amount is within the allowed range of the table
        if p.sufficient_funds(amount=amount) and rules.min_bet <= amount <= rules.max_bet:
            p.initial_bet(amount=amount)

        # amount did not meet the minimum bet
        elif amount < rules.min_bet:
            if p.sufficient_funds(amount=rules.min_bet):
                p.initial_bet(amount=rules.min_bet)
            else:
                table.remove_player(player=p)
                break

        # amount exceeded maximum bet
        elif amount > rules.max_bet:
            if p.sufficient_funds(amount=rules.max_bet):
                p.initial_bet(rules.max_bet)
            elif rules.min_bet <= p.get_bankroll() <= rules.max_bet:
                p.initial_bet(amount=p.get_bankroll())
            else:
                table.remove_player(player=p)
                break

        # player does not have sufficient funds
        elif not p.sufficient_funds(amount=amount):
            if rules.min_bet <= p.get_bankroll() <= rules.max_bet:
                p.initial_bet(amount=p.get_bankroll())
            else:
                table.remove_player(player=p)
                break

        else:
            raise NotImplementedError('No implementation for this betting situation.')


def deal_hands(table, cards):
    """
    Deal first and second cards to each player seated at the table
    and the dealer.

    Parameters
    ----------
    table : Table
        Table class instance
    cards : Cards
        Cards class instance

    Returns
    -------
    list of str
        List of string card elements representing the dealer's initial hand

    """
    for p in table.get_players():
        p.hit(key=1, new_card=cards.deal_card())  # dealing a card is effectively the same as hitting

    dealer_hand = [cards.deal_card(visible=False)]

    for p in table.get_players():
        p.hit(key=1, new_card=cards.deal_card())

    dealer_hand.append(cards.deal_card())

    return dealer_hand


def players_play_hands(table, rules, cards, dealer_hand, dealer_up_card):
    """
    Players at the table play their individual hands.

    Parameters
    ----------
    table : Table
        Table class instance
    rules : HouseRules
        HouseRules class instance
    cards : Cards
        Cards class instance
    dealer_hand : list of str
        List of string card elements representing the dealer's hand
    dealer_up_card : str
        Dealer's card that is face up after each player receives two cards

    """
    dealer_total = max_count_hand(hand=dealer_hand)

    for p in table.get_players():

        player_total = max_count_hand(hand=p.get_hand(key=1))

        # insurance option
        # basic strategy advises against it
        # however, may be favorable to take at large counts
        if rules.insurance and dealer_up_card == 'A':
            pass

        # dealer and players check for natural 21
        if player_total == 21 or dealer_total == 21:
            if player_total == 21:
                p.natural_blackjack()
            p.stand(key=1)
            continue

        # late surrender option
        # only available if dealer doesn't have natural 21
        if rules.late_surrender and dealer_total != 21:
            hand = p.get_hand(key=1)
            bet = p.get_bet(key=1)
            if p.decision(hand=hand, dealer_up_card=dealer_up_card, num_hands=1, amount=bet) in ['Rh', 'Rs', 'Rp']:
                p.surrender()
                p.stand(key=1)
                continue

        processed = set()

        # plays out each hand before moving to next hand
        while True:
            keys = set(p.hands_dict) - processed

            if not keys:
                break

            for k in keys:
                processed.add(k)

                while not p.get_stand(key=k):

                    num_hands = max(p.hands_dict.keys())
                    hand = p.get_hand(key=k)
                    hand_length = len(p.get_hand(key=k))
                    bet = p.get_bet(key=k)
                    decision = p.decision(dealer_up_card=dealer_up_card, hand=hand, num_hands=num_hands, amount=bet)

                    # split cards
                    if decision in ['P', 'Rp'] and p.sufficient_funds(amount=bet):
                        p.set_bankroll(amount=-bet)

                        # if unable to re-split aces, player only gets 1 card on each split pair
                        if not rules.resplit_aces and 'A' in hand:
                            p.split(amount=bet, key=k, new_key=num_hands + 1)
                            p.hit(key=k, new_card=cards.deal_card())
                            p.stand(key=k)
                            p.hit(key=num_hands + 1, new_card=cards.deal_card())
                            p.stand(key=num_hands + 1)

                        else:
                            p.split(amount=bet, key=k, new_key=num_hands + 1)

                    # split cards if double after split available
                    elif rules.double_after_split and decision == 'Ph' and p.sufficient_funds(amount=bet):
                        p.set_bankroll(amount=-bet)
                        p.split(amount=bet, key=k, new_key=num_hands + 1)

                    # double down
                    elif rules.double_down and decision in ['Dh', 'Ds'] and hand_length == 2 and \
                            not p.get_split(key=k) and p.sufficient_funds(amount=bet):
                        p.set_bankroll(amount=-bet)
                        p.double_down(key=k, new_card=cards.deal_card())

                    # double after split
                    elif rules.double_after_split and decision in ['Dh', 'Ds'] and hand_length == 2 and \
                            p.get_split(key=k) and p.sufficient_funds(amount=bet):
                        p.set_bankroll(amount=-bet)
                        p.double_down(key=k, new_card=cards.deal_card())

                    # hit
                    elif decision in ['Rh', 'Dh', 'Ph', 'H']:
                        if hand_length == 1 and 'A' in hand:  # when aces are split, only allowed 1 card
                            p.hit(key=k, new_card=cards.deal_card())
                            if p.get_hand(key=k)[1] != 'A':  # check if split aces can be re-split again
                                p.stand(key=k)
                        else:
                            p.hit(key=k, new_card=cards.deal_card())

                    # stand
                    elif decision in ['Rs', 'Ds', 'S']:
                        p.stand(key=k)

                    # bust
                    elif decision == 'B':
                        p.busted(key=k)

                    else:
                        raise NotImplementedError('No implementation for flag.')


def dealer_turn(table):
    """
    Determines whether or not a dealer needs to take his turn. If any player at the table
    does not have a natural blackjack and does not surrender their hand or bust, the dealer
    will need to play out their turn in its entirety.

    Parameters
    ----------
    table : Table
        Table class instance

    Return
    ------
    bool
        True if any player at the table does not have a natural blackjack and does not
        surrender their hand or bust, false otherwise

    """
    num_natural_blackjack, num_surrender, num_busted, num_stand = 0, 0, 0, 0

    for p in table.get_players():

        if p.get_natural_blackjack():
            num_natural_blackjack += 1

        if p.get_surrender():
            num_surrender += 1

        for k in p.hands_dict.keys():

            if p.get_busted(key=k):
                num_busted += 1

            if p.get_stand(key=k):
                num_stand += 1

        if num_natural_blackjack + num_surrender + num_busted < num_stand:
            return True
    return False


def dealer_plays_hand(rules, cards, dealer_hole_card, dealer_hand):
    """
    Dealer plays out hand. Depending on the rules of the table, the dealer
    will either stand or hit on a soft 17. When the dealer plays out their
    hand, the hole card will be revealed.

    Parameters
    ----------
    rules : HouseRules
        HouseRules class instance
    cards : Cards
        Cards class instance
    dealer_hole_card : str
        Dealer's card that is face down after each player receives two cards
    dealer_hand : list of str
        List of string card elements representing the dealer's hand

    Return
    ------
    list of str
        List of string card elements representing the dealer's final hand

    """
    while True:
        soft_total, hard_total = count_hand(hand=dealer_hand)

        if rules.s17:  # dealer must stay on soft 17 (ace counted as 11)

            if 17 <= soft_total <= 21 or hard_total >= 17:
                cards.update_visible_cards(dealer_hole_card)  # add hole card to visible card list
                return dealer_hand

            else:
                dealer_hand.append(cards.deal_card())

        else:  # dealer must hit on soft 17

            if 17 < soft_total <= 21 or hard_total >= 17:
                cards.update_visible_cards(dealer_hole_card)  # add hole card to visible card list
                return dealer_hand

            else:
                dealer_hand.append(cards.deal_card())


def compare_hands(table, rules, stats, key, dealer_hand):
    """
    Players compare their hands against the dealer. If a player surrenders
    their hand, the player receives half of their initial wager back. If a
    player has a natural blackjack, the player is paid according to the blackjack
    payout for the table. All other instances where the player beats the dealer
    are paid out 1:1. Pushes allow the player to re-coup their initial wager.

    Parameters
    ----------
    table : Table
        Table class instance
    rules : HouseRules
        HouseRules class instance
    stats : SimulationStats
        SimulationStats class instance
    key : float
        Key to SimulationStats dictionary
    dealer_hand : list of str
        List of string card elements representing the dealer's hand

    """
    dealer_total = max_count_hand(hand=dealer_hand)
    dealer_hand_length = len(dealer_hand)

    for p in table.get_players():

        for k in p.hands_dict.keys():

            player_total = max_count_hand(hand=p.get_hand(key=k))
            player_bet = p.get_bet(key=k)

            # only want the initial bet for the first hand
            if k == 1:
                player_initial_bet = p.get_initial_bet(key=k)
            else:
                player_initial_bet = 0

            if p.get_surrender():  # player surrenders
                p.set_bankroll(amount=0.5 * player_bet)
                stats.player_surrender(key=key, amount=player_bet, initial_amount=player_initial_bet)

            elif player_total == 21 and dealer_total == 21:

                if p.get_natural_blackjack() and dealer_hand_length == 2:  # push - both dealer/player have natural 21
                    p.set_bankroll(amount=player_bet)
                    stats.push(key=key, amount=player_bet, initial_amount=player_initial_bet)

                elif p.get_natural_blackjack() and dealer_hand_length > 2:  # player has natural 21
                    if len(table.get_players()) > 1:
                        p.set_bankroll(amount=(1 + rules.blackjack_payout) * player_bet)
                        stats.player_natural_blackjack(key=key, amount=player_bet, initial_amount=player_initial_bet)
                    else:
                        raise ValueError('Impossible scenario when playing heads up against dealer.')

                elif not p.get_natural_blackjack() and dealer_hand_length > 2:  # push - both dealer/player have 21
                    p.set_bankroll(amount=player_bet)
                    stats.push(key=key, amount=player_bet, initial_amount=player_initial_bet)

                else:
                    raise ValueError('Impossible for a dealer to get a natural 21 and a player to have 3+ cards.')

            elif p.get_natural_blackjack() and player_total == 21:  # player has natural 21
                p.set_bankroll(amount=(1 + rules.blackjack_payout) * player_bet)
                stats.player_natural_blackjack(key=key, amount=player_bet, initial_amount=player_initial_bet)

            elif dealer_total == 21 and dealer_hand_length == 2:  # dealer has natural 21
                stats.dealer_natural_blackjack(key=key, amount=player_bet, initial_amount=player_initial_bet)

            elif player_total > 21:  # player busts
                stats.player_bust(key=key, amount=player_bet, initial_amount=player_initial_bet)

            elif dealer_total > 21:  # dealer busts
                p.set_bankroll(amount=2 * player_bet)
                stats.dealer_bust(key=key, amount=player_bet, initial_amount=player_initial_bet)

            elif dealer_total == player_total:  # push
                p.set_bankroll(amount=player_bet)
                stats.push(key=key, amount=player_bet, initial_amount=player_initial_bet)

            elif player_total > dealer_total:  # player beats dealer
                p.set_bankroll(amount=2 * player_bet)
                stats.player_showdown_win(key=key, amount=player_bet, initial_amount=player_initial_bet)

            else:  # dealer beats player
                stats.dealer_showdown_win(key=key, amount=player_bet, initial_amount=player_initial_bet)


if __name__ == "__main__":

    # number of simulations (i.e. number of shoes played)
    simulations = 10000

    # initialize classes that can be set up once
    # set up rules of table
    r = HouseRules(
        min_bet=5,
        max_bet=500,
        s17=True,
        late_surrender=True,
        double_after_split=True,
        resplit_aces=False,
        blackjack_payout=1.5,
        dealer_shows_hole_card=False
    )

    # keeps track of statistics during simulations
    s = SimulationStats(rules=r)

    for _ in range(0, simulations):

        # set up table
        t = Table()

        # player created in each iteration
        p1 = Player(
                name='P1',
                rules=r,
                play_strategy='Basic',
                bet_strategy='Variable',
                count_strategy='Hi-Lo',
                min_bet=10,
                bet_spread=10,
                bankroll=10000
        )

        # add players to table
        # players are dealt in the same order that they are added to the table
        t.add_player(p1)

        # set up cards
        c = Cards(shoe_size=6)

        # shuffle cards
        c.shuffle()

        # keep track of card counts
        cs = CountingStrategy(cards=c)

        while not c.cut_card_reached(penetration=0.75) and len(t.get_players()) > 0:

            # get true count using Hi-Lo strategy
            true_count = cs.true_count(strategy='Hi-Lo', accuracy=0.1)

            # create stats dictionary to store results
            s.create_key(key=true_count)

            # players place initial bets and an empty hand is created
            players_place_bets(table=t, rules=r, counting_strategy=cs)

            # only deal hands if there are players
            if len(t.get_players()) > 0:

                # deal hands to all players and dealer
                dealer_hand = deal_hands(table=t, cards=c)

                # dealers cards
                dealer_hole_card = dealer_hand[0]
                dealer_up_card = dealer_hand[1]

                # players play out each of their hands
                players_play_hands(table=t, rules=r, cards=c, dealer_hand=dealer_hand, dealer_up_card=dealer_up_card)

                # dealer shows hole card when all players bust, surrender, or have natural 21
                if not dealer_turn(table=t) and r.dealer_shows_hole_card:
                    c.update_visible_cards(dealer_hole_card)

                # dealer only has to act if one or more players do not have a natural 21 and do not bust or surrender
                if dealer_turn(table=t):
                    dealer_hand = dealer_plays_hand(
                                                rules=r,
                                                cards=c,
                                                dealer_hole_card=dealer_hole_card,
                                                dealer_hand=dealer_hand
                    )

                # compare players hands to dealer and pay out to winning players
                compare_hands(table=t, rules=r, stats=s, key=true_count, dealer_hand=dealer_hand)

                # update count and reset visible cards
                cs.update_running_count()
                c.set_visible_cards()

    # analysis
    true_count = np.array([])
    initial_bet = np.array([])
    overall_bet = np.array([])
    net_winnings = np.array([])
    push = np.array([])
    player_surrender = np.array([])
    player_bust = np.array([])
    dealer_bust = np.array([])
    player_natural_blackjack = np.array([])
    dealer_natural_blackjack = np.array([])
    player_showdown_win = np.array([])
    dealer_showdown_win = np.array([])
    num_hands = np.array([])

    # unpack nested dictionary
    for x, y in sorted(s.get_stats_dict().items()):
        true_count = np.append(true_count, x)
        for z in y.items():
            if z[0] == 'overall bet':
                overall_bet = np.append(overall_bet, z[1])
            elif z[0] == 'initial bet':
                initial_bet = np.append(initial_bet, z[1])
            elif z[0] == 'net winnings':
                net_winnings = np.append(net_winnings, z[1])
            elif z[0] == 'player showdown win':
                player_showdown_win = np.append(player_showdown_win, z[1])
            elif z[0] == 'dealer showdown win':
                dealer_showdown_win = np.append(dealer_showdown_win, z[1])
            elif z[0] == 'push':
                push = np.append(push, z[1])
            elif z[0] == 'player surrender':
                player_surrender = np.append(player_surrender, z[1])
            elif z[0] == 'player bust':
                player_bust = np.append(player_bust, z[1])
            elif z[0] == 'dealer bust':
                dealer_bust = np.append(dealer_bust, z[1])
            elif z[0] == 'player natural blackjack':
                player_natural_blackjack = np.append(player_natural_blackjack, z[1])
            elif z[0] == 'dealer natural blackjack':
                dealer_natural_blackjack = np.append(dealer_natural_blackjack, z[1])
            elif z[0] == 'number of hands':
                num_hands = np.append(num_hands, z[1])
            else:
                raise NotImplementedError('No implementation for array.')

    print('Total hands:', np.sum(num_hands))
    print('Total amount bet:', np.sum(overall_bet))
    print('Total initial bet:', np.sum(initial_bet))
    print('Total net winnings:', np.sum(net_winnings))
    print('House edge:', 100 * (np.sum(net_winnings) / np.sum(initial_bet)))
    print('Element of risk:', 100 * (np.sum(net_winnings) / np.sum(overall_bet)))

    # TODO Make titles automatic
    # figure 1
    plt.figure()
    plt.bar(x=true_count[net_winnings > 0], height=net_winnings[net_winnings > 0]/simulations, color='b', width=0.2)
    plt.bar(x=true_count[net_winnings < 0], height=net_winnings[net_winnings < 0]/simulations, color='r', width=0.2)
    plt.xlabel('Hi-Lo True count')
    plt.ylabel('Net Winnings per Shoe (Dollars)')
    plt.title('Player vs. Dealer Bar Plot: \n'
              'Shoe Size 6, 75% Deck Penetration, \n'
              'Variable $10, ' + str(r.blackjack_payout) + ' Blackjack Payout, \n' +
              str(simulations) + ' Shoe Simulations')
    plt.grid()
    plt.show()

    # figure 2
    plt.figure()
    plt.plot(true_count, np.cumsum(net_winnings)/simulations)
    plt.xlabel('Hi-Lo True Count')
    plt.ylabel('Net Winnings per Shoe (Dollars)')
    plt.title('Player vs. Dealer Cumulative Sum: \n'
              'Shoe Size 6, 75% Deck Penetration, \n'
              'Variable $10, ' + str(r.blackjack_payout) + ' Blackjack Payout, \n' +
              str(simulations) + ' Shoe Simulations')
    plt.grid()
    plt.show()

    # figure 3
    plt.figure()
    plt.plot(true_count[num_hands > 10000],
             (player_natural_blackjack[num_hands > 10000] +
              player_showdown_win[num_hands > 10000] +
              dealer_bust[num_hands > 10000]) /
             (num_hands[num_hands > 10000] - push[num_hands > 10000]))
    plt.xlabel('Hi-Lo True Count')
    plt.ylabel('Player Win Percentage')
    plt.title('Player vs. Dealer Win Percentage: \n'
              'Shoe Size 6, 75% Deck Penetration, \n'
              'Variable $10, ' + str(r.blackjack_payout) + ' Blackjack Payout, \n' +
              str(simulations) + ' Shoe Simulations')
    plt.grid(axis='y')
    plt.show()

    # figure 4
    plt.figure()
    x = [1, 2, 3, 4, 5, 6, 7, 8]
    y = [np.sum(player_natural_blackjack + player_showdown_win + dealer_bust)/np.sum(num_hands),
         np.sum(dealer_natural_blackjack + dealer_showdown_win + player_bust + player_surrender)/np.sum(num_hands),
         np.sum(push)/np.sum(num_hands),
         np.sum(dealer_bust)/np.sum(num_hands),
         np.sum(player_bust)/np.sum(num_hands),
         np.sum(player_surrender)/np.sum(num_hands),
         np.sum(dealer_natural_blackjack)/np.sum(num_hands),
         np.sum(player_natural_blackjack)/np.sum(num_hands)]
    plt.bar(x=x, height=y, width=0.2, color='b')
    plt.xticks([1, 2, 3, 4, 5, 6, 7, 8], ['Player Win', 'Dealer Win', 'Push', 'Dealer Bust', 'Player Bust', 'Surrender',
                                          'Dealer Natural', 'Player Natural'])
    plt.ylabel('Percentage')
    plt.title('Overall Winning Percentages for Player vs. Dealer over \n' +
              str(simulations) + ' Shoe Simulations')
    for i in range(len(y)):
        plt.annotate('{:.2%}'.format(y[i]), xy=(x[i] - 0.1, y[i] + 0.005))
    plt.grid(axis='y')
    plt.show()
