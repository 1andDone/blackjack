import random
import matplotlib.pyplot as plt
import numpy as np

import basic_strategy
import counting_strategies
from helper import count_hand, max_count_hand, splittable

random.seed(10)

# TODO clean up classes - Player may be too large, may need Game class
# TODO BettingStrategy class -- Kelly Criterion
# TODO PlayStrategy should be a class that includes basicstrategy
# TODO run simulations and make plots -- for more than one player -- may need to include player in dict
# TODO use actual chip amounts -- only allow bets using chip increments
# TODO tests -- test out every type of hand, situation

class HouseRules(object):
    """
    HouseRules is an object where all of the table rules are set.

    Parameters
    ----------
    min_bet : int
        Minimum bet allowed at the table
    max_bet : int
        Maximum bet allowed at the table
    s17 : boolean
        True if dealer stands on a soft 17, false otherwise
    resplit_pairs : boolean
        True if split pairs can be re-split, false otherwise
    resplit_limit : int
        Number of times a split pair can be re-split. The maximum number of hands that a player
        can play is re-split limit + 2.
    blackjack_payout : float
        The payout for a player receiving a natural blackjack (2 cards)
    double_down : boolean
        True if double downs are allowed, false otherwise
    double_after_split : boolean
        True if double downs after splits are allowed, false otherwise
    insurance : boolean
        True if insurance bet is allowed, false otherwise
    late_surrender : boolean
        True if late surrender is available, false otherwise

    """
    def __init__(
            self, min_bet=5, max_bet=500, s17=True, resplit_pairs=True, resplit_limit=2, blackjack_payout=1.5,
            double_down=True, double_after_split=True, insurance=True, late_surrender=True
    ):
        self.min_bet = int(min_bet)
        self.max_bet = int(max_bet)
        self.s17 = s17
        self.resplit_pairs = resplit_pairs
        if resplit_pairs and resplit_limit <= 0:
            raise ValueError('Re-split limit be a positive integer.')
        self.resplit_limit = int(resplit_limit)  # naturally bounded by 4 * shoe size
        self.blackjack_payout = blackjack_payout
        self.double_down = double_down
        self.double_after_split = double_after_split
        self.insurance = insurance
        self.late_surrender = late_surrender


class Cards(object):
    """
    Cards is an object that deals with a shoe at a table.

    Parameters
    ----------
    shoe_size : int
        Number of decks that will be used during blackjack game

    """
    def __init__(self, shoe_size=4):
        if shoe_size not in [4, 6, 8]:
            raise ValueError('Shoe size must be 4, 6, or 8.')
        self.shoe_size = int(shoe_size)
        self.deck = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'] * int(shoe_size) * 4
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

    def add_to_visible_cards(self, card):
        self.visible_cards.append(card)

    def remaining_decks(self):
        return len(self.deck)/52

    def cut_card_reached(self, penetration):
        if float(penetration) < 0.5 or float(penetration) > 0.9:
            raise ValueError('Penetration must be between 0.5 and 0.9')
        total_cards = 52 * self.shoe_size
        remaining_cards = total_cards - len(self.deck)
        return remaining_cards/total_cards >= float(penetration)


class BettingStrategy(object):

    def __init__(self, strategy):
        if strategy not in ['Fixed', 'Variable']:
            raise ValueError('Betting strategy must be either Fixed or Variable.')
        self.strategy = strategy

    def get_strategy(self):
        return self.strategy()

    def bet(self, min_bet, bet_spread, count=None, count_strategy=None):
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
                raise NotImplementedError('Betting strategy is not implemented for running counts.')


class CountingStrategy(object):
    """
    CountingStrategy is an object that represents the card counting strategy used by
    a player to make betting decisions.

    Parameters
    ----------
    cards : class
        Cards class instance
    strategy : str
        Name of the card counting strategy using either running count or true count

    """
    def __init__(self, cards, strategy):
        if strategy not in ['Hi-Lo', 'Hi-Opt I', 'Hi-Opt II', 'Omega II', 'Halves', 'Zen Count']:
            raise ValueError('Strategy must be Hi-Lo, Hi-Opt I, Hi-Opt II, Omega II, Halves, or Zen Count')
        self.cards = cards
        self.strategy = strategy
        self.count_dict = counting_strategies.count_dict[strategy]

    def get_strategy(self):
        return self.strategy

    def running_count(self):
        # TODO add additional counting systems from https://en.wikipedia.org/wiki/Card_counting
        # TODO some counting systems require the type of card (spade, diamond, etc.)
        return sum([self.count_dict.get(card) for card in self.cards.visible_cards])

    def true_count(self, accuracy=1):
        if self.strategy in ['Hi-Lo', 'Omega II', 'Halves', 'Zen Count']:
            return round(self.running_count()/self.cards.remaining_decks(), accuracy)
        raise ValueError('True count not used for this counting strategy.')


class BasicStrategy(object):
    """
    BasicStrategy is an object that represents the decisions a player would make
    when following basic strategy. Decisions are based on whether or not a dealer
    stands or hits on a soft 17.

    Parameters
    ----------
    rules : class
        HouseRules class instance

    """
    def __init__(self, rules):
        self.rules = rules

    def splits(self):
        if self.rules.s17:
            return basic_strategy.s17_splits
        return basic_strategy.h17_splits

    def soft(self):
        if self.rules.s17:
            return basic_strategy.s17_soft
        return basic_strategy.h17_soft

    def hard(self):
        if self.rules.s17:
            return basic_strategy.s17_hard
        return basic_strategy.h17_hard


# TODO min bet must be some combination of chips
class Player(object):
    """
    Player is an object that represents a single player at the table.

    Parameters
    ----------
    name : str
        Name of the player
    rules : class
        HouseRules class instance
    bankroll : float
        Amount of money a player starts out with when sitting down at a table
    min_bet : float
        Minimum amount of money a player would like to bet when playing a hand
    bet_spread : float
        Ratio of maximum bet to minimum bet
    play_strategy : class
        BasicStrategy class instance
    bet_strategy : class
        Name of the bet strategy used by the player
    count_strategy : string
        Name of the card counting strategy used by the player

    """
    def __init__(self, name, rules, bankroll, min_bet, play_strategy, bet_spread=1,
                 bet_strategy='Fixed', count_strategy=None):
        if count_strategy is not None:
            if count_strategy not in ['Hi-Lo', 'Hi-Opt I', 'Hi-Opt II', 'Omega II', 'Halves', 'Zen Count']:
                raise ValueError('Count Strategy must be Hi-Lo, Hi-Opt I, Hi-Opt II, Omega II, Halves, or Zen Count')
        self.name = name
        self.rules = rules
        if bankroll <= rules.min_bet:
            raise ValueError('Bankroll must be greater than minimum bet.')
        self.bankroll = float(bankroll)
        if bet_strategy not in ['Fixed', 'Variable']:
            raise ValueError('Betting strategy must be either Fixed or Variable.')
        if min_bet < rules.min_bet or min_bet > rules.max_bet:
            raise ValueError('Minimum bet is not allowed according to the table rules.')
        self.min_bet = float(min_bet)
        if bet_spread > float(rules.max_bet/rules.min_bet) or bet_spread > float(bankroll/min_bet):
            raise ValueError('Bet spread is too large.')
        if bet_strategy == 'Variable' and bet_spread < 1:
            raise ValueError('Bet spread must be greater than 1.')
        self.bet_spread = float(bet_spread)
        self.play_strategy = play_strategy
        self.bet_strategy = bet_strategy
        if bet_strategy == 'Variable' and count_strategy is None:
            raise ValueError('Count strategy cannot be none with a Variable Bet Strategy.')
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
        if self.bankroll - amount >= 0:
            return True
        return False

    def get_bet_strategy(self):
        return self.bet_strategy

    def get_play_strategy(self):
        return self.play_strategy

    def get_count_strategy(self):
        return self.count_strategy

    def create_hand(self, amount):
        self.hands_dict = {1: {}}
        self.hands_dict[1]['hand'] = []
        self.hands_dict[1]['bet'] = amount
        self.hands_dict[1]['natural blackjack'] = False
        self.hands_dict[1]['surrender'] = False
        self.hands_dict[1]['busted'] = False
        self.hands_dict[1]['stand'] = False

    def bet(self, amount):
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

    def get_bet(self, key):
        return self.hands_dict[key]['bet']

    def get_natural_blackjack(self):
        return self.hands_dict[1]['natural blackjack']

    def get_surrender(self):
        return self.hands_dict[1]['surrender']

    def get_busted(self, key):
        return self.hands_dict[key]['busted']

    def get_stand(self, key):
        return self.hands_dict[key]['stand']

    def hit(self, key, new_card):
        self.hands_dict[key]['hand'].append(new_card)

    def double_down(self, key):
        self.hands_dict[key]['bet'] = 2 * self.hands_dict[key]['bet']
        self.hit(key=key, new_card=c.deal_card())
        self.stand(key=key)

    def split(self, amount, key, new_key):
        if splittable(hand=self.hands_dict[key]['hand']):
            self.hands_dict[new_key] = {}
            self.hands_dict[new_key]['hand'] = [self.get_hand(key=key).pop()]
            self.hands_dict[new_key]['bet'] = amount
            self.hands_dict[new_key]['busted'] = False
            self.hands_dict[new_key]['stand'] = False

    def decision(self, hand, dealer_up_card, num_hands, amount):
        if splittable(hand=hand) and num_hands < (r.resplit_limit + 2) and self.sufficient_funds(amount=amount):
            return self.play_strategy.splits()[hand[0]][dealer_up_card]
        else:
            soft_total, hard_total = count_hand(hand=hand)
            if soft_total > hard_total and 13 <= soft_total <= 21:  # must contain an Ace
                return self.play_strategy.soft()[soft_total][dealer_up_card]
            elif 4 <= hard_total <= 21:
                return self.play_strategy.hard()[hard_total][dealer_up_card]
            else:
                return 'B'  # player is busted


class Table(object):
    """
    Table is an object that represents an area where one or many players can play.

    Parameters
    ----------
    size_limit : int
        Number of players that can play at a table at any given time

    """
    def __init__(self, size_limit=7):
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
            NotImplementedError('Did not expect this data type')

    def remove_player(self, player):
        if player in self.players:
            self.players.remove(player)
        return 'Player cannot be removed. Player is not at the table.'


class SimulationStats(object):
    """
    SimulationStats is an object that stores results from one or many
    simulations being run

    """
    def __init__(self):
        self.stats_dict = {}

    def get_stats_dict(self):
        return self.stats_dict

    def create_key(self, key):
        if key not in self.stats_dict.keys():
            self.stats_dict[key] = {}
            self.stats_dict[key]['net winnings'] = 0
            self.stats_dict[key]['player win'] = 0
            self.stats_dict[key]['push'] = 0
            self.stats_dict[key]['player surrender'] = 0
            self.stats_dict[key]['player bust'] = 0
            self.stats_dict[key]['dealer bust'] = 0
            self.stats_dict[key]['player natural blackjack'] = 0
            self.stats_dict[key]['dealer natural blackjack'] = 0
            self.stats_dict[key]['number of hands'] = 0

    def net_winnings(self, key, amount):
        self.stats_dict[key]['net winnings'] += amount

    def number_of_hands(self, key):
        self.stats_dict[key]['number of hands'] += 1

    def player_win(self, key):
        self.stats_dict[key]['player win'] += 1
        self.stats_dict[key]['number of hands'] += 1

    def push(self, key):
        self.stats_dict[key]['push'] += 1
        self.stats_dict[key]['number of hands'] += 1

    def player_surrender(self, key):
        self.stats_dict[key]['player surrender'] += 1
        self.stats_dict[key]['number of hands'] += 1

    def dealer_bust(self, key):
        self.stats_dict[key]['dealer bust'] += 1
        self.stats_dict[key]['number of hands'] += 1

    def player_bust(self, key):
        self.stats_dict[key]['player bust'] += 1
        self.stats_dict[key]['number of hands'] += 1

    def dealer_natural_blackjack(self, key):
        self.stats_dict[key]['dealer natural blackjack'] += 1
        self.stats_dict[key]['number of hands'] += 1

    def player_natural_blackjack(self, key):
        self.stats_dict[key]['player natural blackjack'] += 1
        self.stats_dict[key]['number of hands'] += 1


def players_place_bets(table, rules):
    """
    Players at table place bets. If they're unable to bet that amount
    they place a bet closest to that amount, while staying within the
    betting constraints of the table. If they are unable to make the
    minimum bet, they are removed from the table.

    Parameters
    ----------
    table : class
        Table class instance
    rules : class
        HouseRules class instance

    """
    for p in table.get_players():

        bs = BettingStrategy(strategy=p.get_bet_strategy())

        if p.get_bet_strategy() == 'Variable':
            cs = CountingStrategy(cards=c, strategy=p.get_count_strategy())

            if p.get_count_strategy() in ['Hi-Lo', 'Omega II', 'Halves', 'Zen Count']:
                amount = bs.bet(
                            min_bet=p.get_min_bet(),
                            bet_spread=p.get_bet_spread(),
                            count=cs.true_count(),
                            count_strategy=p.get_count_strategy()
                )

            else:
                raise NotImplementedError('Have not implemented for running counts')

        else:
            amount = bs.bet(
                        min_bet=p.get_min_bet(),
                        bet_spread=p.get_bet_spread()
            )

        # rules once you have the amount
        if p.sufficient_funds(amount=amount) and rules.min_bet <= amount <= rules.max_bet:
            p.bet(amount=amount)

        # amount did not meet the minimum bet
        elif amount < rules.min_bet:
            if p.sufficient_funds(amount=rules.min_bet):
                p.bet(amount=rules.min_bet)
            else:
                t.remove_player(p)
                break

        # amount exceeded maximum bet
        elif amount > rules.max_bet:
            if p.sufficient_funds(amount=rules.max_bet):
                p.bet(rules.max_bet)
            elif rules.min_bet <= p.get_bankroll() <= rules.max_bet:
                p.bet(amount=p.get_bankroll())
            else:
                t.remove_player(p)
                break

        # player does not have sufficient funds
        elif not p.sufficient_funds(amount=amount):
            if rules.min_bet <= p.get_bankroll() <= rules.max_bet:
                p.bet(amount=p.get_bankroll())
            else:
                t.remove_player(p)
                break


def deal_hands(table, cards):
    """
    Deal first and second cards to each player seated at the table
    and the dealer

    Parameters
    ----------
    table : class
        Table class instance
    cards : class
        Cards class instance

    Returns
    -------
    return : list

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
    Players at the table play their individual hands

    Parameters
    ----------
    table : class
        Table class instance
    rules : class
        HouseRules class instance
    cards : class
        Cards class instance
    dealer_hand : list
        List of string card elements representing the dealer's hand
    dealer_up_card : str
        Dealer's card that is face up after each player receives two cards

    """
    dealer_total = max_count_hand(dealer_hand)

    for p in table.get_players():

        player_total = max_count_hand(p.get_hand(key=1))

        # insurance option - basic strategy advises against it
        # however, may be favorable to use at large counts
        if rules.insurance and dealer_up_card == 'A':
            pass

        # dealer and players check for 21
        if player_total == 21 or dealer_total == 21:
            p.natural_blackjack()
            p.stand(key=1)

        # late surrender option
        if rules.late_surrender:
            hand = p.get_hand(key=1)
            bet = p.get_bet(key=1)
            if p.decision(hand=hand, dealer_up_card=dealer_up_card, num_hands=1, amount=bet) in ['Rh', 'Rs', 'Rp']:
                p.surrender()
                p.stand(key=1)

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
                    bet = p.get_bet(key=k)
                    decision = p.decision(dealer_up_card=dealer_up_card, hand=hand, num_hands=num_hands, amount=bet)
                    # check if hand is splittable
                    # determine if re-splitting limit has been reached
                    # i.e. if the re-split limit is 2, a maximum of 4 hands can be played by the player
                    if splittable(hand=hand) and num_hands < (rules.resplit_limit + 2):

                        # split cards
                        if decision in ['P', 'Rp'] and p.sufficient_funds(amount=bet):
                            p.set_bankroll(amount=-bet)

                            # if splitting aces, player only gets 1 card
                            if 'A' in hand:
                                p.split(amount=bet, key=k, new_key=num_hands + 1)
                                p.hit(key=k, new_card=cards.deal_card())
                                p.hit(key=num_hands + 1, new_card=cards.deal_card())
                                p.stand(key=k)
                                p.stand(key=num_hands + 1)

                            else:
                                p.split(amount=bet, key=k, new_key=num_hands + 1)

                        # split cards and double down
                        elif rules.double_after_split and decision == 'Ph' and p.sufficient_funds(amount=3 * bet):
                            p.set_bankroll(amount=-3 * bet)
                            p.split(amount=bet, key=k, new_key=num_hands + 1)
                            p.double_down(key=k)
                            p.double_down(key=num_hands + 1)

                        # do not split cards - double down
                        elif rules.double_down and decision == 'Dh' and p.sufficient_funds(amount=bet):
                            p.set_bankroll(amount=-bet)
                            p.double_down(key=k)

                        # do not split cards - hit
                        elif decision in ['Ph', 'Dh', 'H']:
                            p.hit(key=k, new_card=cards.deal_card())

                        # do not split cards - stand
                        elif decision == 'S':
                            p.stand(key=k)

                        else:
                            raise NotImplementedError('No implementation for that flag')

                    else:

                        # double down
                        if rules.double_down and decision in ['Dh', 'Ds'] and p.sufficient_funds(amount=bet):
                            p.set_bankroll(amount=-bet)
                            p.double_down(key=k)

                        # hit
                        elif decision in ['Rh', 'Dh', 'H']:
                            p.hit(key=k, new_card=cards.deal_card())

                        # stand
                        elif decision in ['Rs', 'Ds', 'S']:
                            p.stand(key=k)

                        elif decision == 'B':
                            p.busted(key=k)

                        else:
                            raise NotImplementedError('No implementation for that flag')


def dealer_turn(table):
    """
    Determines whether or not a dealer needs to take his turn. If any player at the table
    does not have a natural blackjack and does not surrender their hand or bust, the dealer
    will need to play out their turn in its entirety.

    Parameters
    ----------
    table : class
        Table class instance

    Return
    ------
    return : boolean

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
    return num_natural_blackjack + num_surrender + num_busted < num_stand


def dealer_plays_hand(rules, cards, dealer_hole_card, dealer_hand):
    """
    Dealer plays out hand. Depending on the rules of the table, the dealer
    will either stand or hit on a soft 17. When the dealer plays out their
    hand, the hole card will be revealed.

    Parameters
    ----------
    rules : class
        HouseRules class instance
    cards : class
        Cards class instance
    dealer_hole_card : str
        Dealer's card that is face down after each player receives two cards
    dealer_hand : list
        List of string card elements representing the dealer's hand

    Return
    ------
    return : list

    """
    while True:
        soft_total, hard_total = count_hand(dealer_hand)

        if rules.s17:  # dealer must stay on soft 17 (ace counted as 11)

            if 17 <= soft_total <= 21 or hard_total >= 17:
                cards.add_to_visible_cards(dealer_hole_card)  # add hole card to visible card list
                return dealer_hand

            else:
                dealer_hand.append(cards.deal_card())

        else:  # dealer must hit on soft 17

            if 17 < soft_total <= 21 or hard_total >= 17:
                cards.add_to_visible_cards(dealer_hole_card)  # add hole card to visible card list
                return dealer_hand

            else:
                dealer_hand.append(cards.deal_card())


def compare_hands(table, stats, key, dealer_hand):
    """
    Players compare their hands against the dealer

    Parameters
    ----------
    table : class
        Table class instance
    stats : class
        SimulationStats class instance
    key : int
        Key to SimulationStats dictionary
    dealer_hand : list
        List of string card elements representing the dealer's hand

    """
    dealer_total = max_count_hand(hand=dealer_hand)
    dealer_hand_length = len(dealer_hand)

    for p in table.get_players():

        # get player totals
        for k in p.hands_dict.keys():
            player_total = max_count_hand(hand=p.get_hand(key=k))
            player_bet = p.get_bet(key=k)
            player_hand_length = len(p.get_hand(key=k))

            if p.get_surrender():
                p.set_bankroll(amount=0.5 * player_bet)  # player receives half of original wager back
                stats.player_surrender(key=key)
                stats.net_winnings(key=key, amount=-0.5 * player_bet)

            elif player_total == 21 and dealer_total == 21:
                # case where dealer has natural blackjack and player has blackjack is impossible
                if player_hand_length > 2 and dealer_hand_length > 2:
                    p.set_bankroll(amount=player_bet)  # pushes - player and dealer both have 21
                    stats.push(key=key)
                elif p.get_natural_blackjack() and dealer_hand_length == 2:
                    p.set_bankroll(amount=player_bet)  # pushes - player and dealer both have natural 21
                    stats.push(key=key)
                else:
                    p.set_bankroll(amount=player_bet + (player_bet * r.blackjack_payout))  # player has natural 21
                    stats.player_natural_blackjack(key=key)
                    stats.net_winnings(key=key, amount=player_bet * r.blackjack_payout)

            elif player_total == 21:
                if p.get_natural_blackjack():
                    p.set_bankroll(amount=player_bet + (player_bet * r.blackjack_payout))  # player has natural 21
                    stats.player_natural_blackjack(key=key)
                    stats.net_winnings(key=key, amount=player_bet * r.blackjack_payout)

                else:
                    p.set_bankroll(amount=2 * player_bet)  # player has 21
                    stats.player_win(key=key)
                    stats.net_winnings(key=key, amount=player_bet)

            elif dealer_total == 21:
                stats.number_of_hands(key=key)
                stats.net_winnings(key=key, amount=-player_bet)

                if dealer_hand_length == 2:
                    stats.dealer_natural_blackjack(key=key)
                    pass  # dealer has natural 21

                else:
                    pass  # dealer has 21

            elif p.get_busted(key=k):
                stats.player_bust(key=key)
                stats.net_winnings(key=key, amount=-player_bet)
                pass  # player busts

            elif dealer_total > 21:
                p.set_bankroll(amount=2 * player_bet)  # dealer busts
                stats.number_of_hands(key=key)
                stats.dealer_bust(key=key)
                stats.net_winnings(key=key, amount=player_bet)

            elif dealer_total == player_total:
                p.set_bankroll(amount=player_bet)  # push
                stats.push(key=key)

            elif player_total > dealer_total:
                p.set_bankroll(amount=2 * player_bet)  # player beats dealer
                stats.player_win(key=key)
                stats.net_winnings(key=key, amount=player_bet)

            else:
                stats.number_of_hands(key=key)
                stats.net_winnings(key=key, amount=-player_bet)
                pass  # dealer beats player


def make_one_curve_plot(x_coords, y_coords, x_label, y_label, title):
    """
    Makes a plot of the x-coordinates and the y-coordinates with the labels
    and title provided.

    Parameters
    ----------
    x_coords : list or array
        x-coordinates of graph
    y_coords : list or array
        y-coordinates of graph
    x_label : str
        Label for x-axis
    y_label : str
        Label for y-axis
    title : str
        Title for the graph

    """
    plt.figure()
    plt.plot(x_coords, y_coords)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.show()


def make_two_color_bar_chart(x_coords1, x_coords2, y_coords1, y_coords2, x_label, y_label, title):
    """
    Makes a bar plot of the x-coordinates and y-coordinates with the labels
    and title provided.

    Parameters
    ----------
    x_coords1 : list or array
        x-coordinates of graph
    x_coords2 : list or array
        x-coordinates of graph
    y_coords1 : list or array
        y-coordinates of graph
    y_coords2 : list or array
        y-coordinates of graph
    x_label : str
        Label for x-axis
    y_label : str
        Label for y-axis
    title : str
        Title for the graph

    """
    plt.figure()
    plt.bar(x=x_coords1, height=y_coords1, color='b', width=0.2)
    plt.bar(x=x_coords2, height=y_coords2, color='r', width=0.2)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.show()


if __name__ == "__main__":

    # number of simulations (i.e. number of shoes played)
    simulations = 10000

    # initialize classes that can be set up once

    # set up rules of table
    r = HouseRules(
        min_bet=5,
        max_bet=500,
        s17=True,
        blackjack_payout=1.5
    )

    # basic strategy based on rules
    ps = BasicStrategy(rules=r)

    # keeps track of statistics during simulations
    s = SimulationStats()

    for _ in range(0, simulations):

        # set up table
        t = Table()

        # set up players each simulation in case no funds remain
        p1 = Player(
                name='P1',
                rules=r,
                play_strategy=ps,
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

        while not c.cut_card_reached(penetration=0.75) and len(t.get_players()) > 0:

            # get true count using Hi-Lo strategy
            true_count = CountingStrategy(cards=c, strategy='Hi-Lo').true_count()

            # create stats dictionary to store results
            s.create_key(key=true_count)

            # players place bets and empty hand with wager is created
            players_place_bets(table=t, rules=r)

            # only deal hands if there are players
            if len(t.get_players()) > 0:

                # deal hand to all players and dealer
                dealer_hand = deal_hands(table=t, cards=c)

                # dealers cards
                dealer_hole_card = dealer_hand[0]
                dealer_up_card = dealer_hand[1]

                # players play out each of their hands
                players_play_hands(table=t, rules=r, cards=c, dealer_hand=dealer_hand, dealer_up_card=dealer_up_card)

                # only show dealer cards if one or more players do not bust or surrender
                if dealer_turn(table=t):
                    dealer_hand = dealer_plays_hand(
                                                rules=r,
                                                cards=c,
                                                dealer_hole_card=dealer_hole_card,
                                                dealer_hand=dealer_hand
                    )

                # compare players hands to dealer and pay out to winning players
                compare_hands(table=t, stats=s, key=true_count, dealer_hand=dealer_hand)

    # analysis
    true_count = np.array([])
    net_winnings = np.array([])
    player_win = np.array([])
    push = np.array([])
    player_surrender = np.array([])
    player_bust = np.array([])
    dealer_bust = np.array([])
    player_natural_blackjack = np.array([])
    dealer_natural_blackjack = np.array([])
    num_hands = np.array([])

    # unpack nested dictionary
    for x, y in sorted(s.get_stats_dict().items()):
        true_count = np.append(true_count, x)
        for z in y.items():
            if z[0] == 'net winnings':
                net_winnings = np.append(net_winnings, z[1])
            elif z[0] == 'player win':
                player_win = np.append(player_win, z[1])
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
                raise NotImplementedError('Need to add numpy array')

    # TODO Make titles automatic
    make_two_color_bar_chart(
        x_coords1=true_count[net_winnings > 0],
        x_coords2=true_count[net_winnings < 0],
        y_coords1=net_winnings[net_winnings > 0],
        y_coords2=net_winnings[net_winnings < 0],
        x_label='True Count',
        y_label='Net Winnings',
        title='Player vs. Dealer Bar Plot: \n'
              'Shoe Size 6, 75% Deck Penetration, \n'
              'Variable $10, ' + str(r.blackjack_payout) + ' Blackjack Payout, \n' +
              str(simulations) + ' Shoe Simulations'
    )

    # TODO Make titles automatic
    make_one_curve_plot(
        x_coords=true_count,
        y_coords=np.cumsum(net_winnings),
        x_label='True Count',
        y_label='Net Winnings',
        title='Player vs. Dealer Cumulative Sum: \n'
              'Shoe Size 6, 75% Deck Penetration, \n'
              'Variable $10, ' + str(r.blackjack_payout) + ' Blackjack Payout, \n' +
              str(simulations) + ' Shoe Simulations'
    )