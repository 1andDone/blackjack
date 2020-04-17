import random

import basic_strategy
import counting_strategies
from helper import count_hand, max_count_hand, splittable


# TODO clean up classes and put in separate files
# TODO Kelly Criterion for betting
# TODO make poor players
# TODO run simulations
# TODO Player and Dealer classes can't take a Cards input because that value changes when shoe is run dry
# TODO Player class is fixed once at the table

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
        can play is resplit_limit + 2.
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


# TODO stack cards to be a certain count
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


class CountingStrategy(object):
    """
    CountingStrategy is an object that represents the card counting strategy used by
    a player to make betting decisions.

    Parameters
    ----------
    cards : class
        Cards class instance
    strategy : str
        Name of the strategy that uses either running count or true count

    """
    def __init__(self, cards, strategy):
        if strategy not in ['Hi-Lo', 'Hi-Opt I', 'Hi-Opt II', 'Omega II', 'Halves', 'Zen Count']:
            raise ValueError('Strategy must be Hi-Lo, Hi-Opt I, Hi-Opt II, Omega II, Halves, or Zen Count')
        self.cards = cards
        self.strategy = strategy
        self.count_dict = counting_strategies.count_dict[strategy]

    def running_count(self):
        # TODO add additional counting systems from https://en.wikipedia.org/wiki/Card_counting
        # TODO some counting systems require the type of card (spade, diamond, etc.)
        return sum([self.count_dict.get(card) for card in self.cards.visible_cards])

    def true_count(self):
        # TODO may want to tweak accuracy -- players have to eyeball remaining decks while playing
        if self.strategy in ['Hi-Lo', 'Omega II', 'Halves', 'Zen Count']:
            return round(self.running_count()/self.cards.remaining_decks(), 1)
        raise ValueError('True count not used for this counting strategy.')


class Dealer(object):
    """
    Dealer is an object that represents the dealer at the table.

    Parameters
    ----------
    cards : class
        Cards class instance

    """
    def __init__(self, cards):
        self.cards = cards

    def hit(self, hand):
        hand.append(self.cards.deal_card())
        return hand


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


class Bank(object):
    """
    Bank is an object that represents the amount of money a player
    has access to at the table.

    Parameters
    ----------
    rules : class
        HouseRules class instance
    bankroll : float
        Amount of money a player has access to at the table

    """
    def __init__(self, rules, bankroll):
        self.rules = rules
        if bankroll <= rules.min_bet:
            raise ValueError('Bankroll must be greater than minimum bet.')
        self.bankroll = float(bankroll)


class Player(object):
    """
    Player is an object that represents a single player at the table.

    Parameters
    ----------
    name : str
        Name of the player
    bank : class
        Bank class instance
    cards : class
        Cards class instance
    rules : class
        HouseRules class instance
    play_strategy : class
        BasicStrategy class instance
    count_strategy : class
        CountingStrategy class instance

    """
    def __init__(self, name, bank, cards, rules, play_strategy, count_strategy=None):
        self.name = name
        self.bank = bank
        self.cards = cards
        self.rules = rules
        self.play_strategy = play_strategy
        self.count_strategy = count_strategy
        self.hands_dict = {}

    def get_name(self):
        return self.name

    def sufficient_funds(self, amount):
        if self.bank.bankroll - amount >= 0:
            return True
        return False

    def get_bankroll(self):
        return self.bank.bankroll

    def set_bankroll(self, amount):
        self.bank.bankroll = self.bank.bankroll + amount

    def initial_bet(self, amount):
        if amount < self.rules.min_bet:
            raise ValueError('Initial bet must exceed table minimum.')
        if amount > self.rules.max_bet:
            raise ValueError('Initial bet must not exceed table maximum.')
        self.set_bankroll(-amount)
        return amount

    def create_hand(self, hand, amount):
        self.hands_dict = {1: {}}
        self.hands_dict[1]['hand'] = hand
        self.hands_dict[1]['bet'] = amount
        self.hands_dict[1]['surrender'] = False
        self.hands_dict[1]['busted'] = False
        self.hands_dict[1]['stand'] = False

    def get_hand(self, key):
        return self.hands_dict[key]['hand']

    def get_bet(self, key):
        return self.hands_dict[key]['bet']

    def get_surrender(self):
        return self.hands_dict[1]['surrender']

    def get_busted(self, key):
        return self.hands_dict[key]['busted']

    def get_stand(self, key):
        return self.hands_dict[key]['stand']

    def hit(self, key):
        self.hands_dict[key]['hand'].append(self.cards.deal_card())

    def stand(self, key):
        self.hands_dict[key]['stand'] = True

    def surrender(self):
        self.hands_dict[1]['surrender'] = True

    def busted(self, key):
        self.hands_dict[key]['busted'] = True
        self.stand(key=key)

    def double_down(self, key):
        self.hands_dict[key]['bet'] = self.hands_dict[key]['bet'] * 2
        self.hit(key=key)
        self.stand(key=key)

    def split(self, key, new_key):
        if splittable(self.hands_dict[key]['hand']):
            self.hands_dict[new_key] = {}
            self.hands_dict[new_key]['hand'] = [self.get_hand(key=key).pop()]
            self.hands_dict[new_key]['bet'] = bet
            self.hands_dict[new_key]['busted'] = False
            self.hands_dict[new_key]['stand'] = False

    def decision(self, hand, dealer_up_card, num_hands, amount):
        if splittable(hand) and num_hands < (r.resplit_limit + 2) and self.sufficient_funds(amount):
            return self.play_strategy.splits()[hand[0]][dealer_up_card]
        else:
            soft_total, hard_total = count_hand(hand)
            if soft_total > hard_total and 13 <= soft_total <= 21:  # must contain an Ace
                return self.play_strategy.soft()[soft_total][dealer_up_card]
            elif 4 <= hard_total <= 21:
                return self.play_strategy.hard()[hard_total][dealer_up_card]
            else:
                return 'B'  # player is busted


class Table(object):
    """
    Table is an object that represents an area where one or many players can play.

    """
    def __init__(self):
        self.players = []

    def get_players(self):
        return self.players

    # TODO fix assert statements
    def add_player(self, player):
        if isinstance(player, Player):
            assert len(self.players) < 7, 'Table is at maximum capacity'
            self.players.append(player)
        elif isinstance(player, list):
            assert len(self.players) + len(player) <= 7, 'Table is at maximum capacity'
            self.players.extend(player)
        else:
            NotImplementedError('Did not expect this data type')

    def remove_player(self, player):
        if player in self.players:
            self.players.remove(player)
        return 'Player cannot be removed. Player is not at the table.'


if __name__ == "__main__":

    simulations = 1

    # initialize classes that only need to be set once

    # set up table
    t = Table()

    # set up rules of table
    r = HouseRules(
        min_bet=5,
        max_bet=500,
        s17=True,
        resplit_pairs=True,
        resplit_limit=2,
        blackjack_payout=1.5,
        double_down=True,
        double_after_split=True,
        insurance=True,
        late_surrender=True
    )

    # basic strategy based on rules
    ps = BasicStrategy(rules=r)

    # set bankrolls of players
    b1 = Bank(rules=r, bankroll=1000)
    b2 = Bank(rules=r, bankroll=1000)

    for _ in range(0, simulations):

        # set up cards
        c = Cards(shoe_size=6)

        # pick a counting strategy
        cs = CountingStrategy(cards=c, strategy='Hi-Lo')

        # set up dealer
        d = Dealer(cards=c)

        if _ == 0:
            # set up players
            player1 = Player(name='P1', cards=c, rules=r, play_strategy=ps, count_strategy=cs, bank=b1)
            player2 = Player(name='P2', cards=c, rules=r, play_strategy=ps, bank=b2)

            # add players to table
            # players are dealt in the same order that they are added to the table
            t.add_player([player1, player2])

        # shuffle cards
        c.shuffle()

        while not c.cut_card_reached(penetration=0.75) and len(t.get_players()) > 0:
            dealer_turn = False

            dealer_hand = []

            print('True count:', cs.true_count())

            for p in t.get_players():

                print(p.get_name(), 'starting bankroll:', p.get_bankroll())

                # TODO Change amount wagered based on card counting
                # TODO make sure the bet is within the min/max bounds
                if p.sufficient_funds(5):
                    wager = p.initial_bet(5)  # place initial wager
                else:
                    print('**', p.get_name(), 'ran out of money **')
                    t.remove_player(p)  # remove player from table
                    break  # insufficient funds to place a bet

                # first cards are dealt - players are dealt before dealer
                p.create_hand(hand=[c.deal_card()], amount=wager)

            dealer_hand.append(c.deal_card(visible=False))

            for p in t.get_players():

                # second cards are dealt
                # dealing a card is effectively the same as hitting
                p.hit(key=1)

            dealer_hand.append(c.deal_card())

            # dealer cards
            dealer_hole_card = dealer_hand[0]
            dealer_up_card = dealer_hand[1]

            dealer_total = max_count_hand(dealer_hand)

            for p in t.get_players():

                player_total = max_count_hand(p.get_hand(key=1))

                # insurance option - basic strategy advises against it
                # however, may be favorable to use at large counts
                if r.insurance and dealer_up_card == 'A':
                    pass

                # dealer and players check for 21
                if player_total == 21 or dealer_total == 21:
                    p.stand(key=1)

                # late surrender option
                if r.late_surrender:
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

                            num_hands = max(p.hands_dict.keys())  # current number of hands
                            hand = p.get_hand(key=k)
                            bet = p.get_bet(key=k)
                            decision = p.decision(dealer_up_card=dealer_up_card, hand=hand, num_hands=num_hands, amount=bet)
                            # check if hand is splittable
                            # determine if re-splitting limit has been reached
                            # i.e. if the re-split limit is 2, a maximum of 4 hands can be played by the player
                            if splittable(hand) and num_hands < (r.resplit_limit + 2):

                                # split cards
                                if decision in ['P', 'Rp'] and p.sufficient_funds(bet):
                                    p.set_bankroll(-bet)

                                    # if splitting aces, player only gets 1 card
                                    if 'A' in hand:
                                        p.split(key=k, new_key=num_hands + 1)
                                        p.hit(key=k)
                                        p.hit(key=num_hands + 1)
                                        p.stand(key=k)
                                        p.stand(key=num_hands + 1)

                                    else:
                                        p.split(key=k, new_key=num_hands + 1)

                                # split cards and double down
                                elif r.double_after_split and decision == 'Ph' and p.sufficient_funds(3*bet):
                                    p.set_bankroll(-3*bet)
                                    p.split(key=k, new_key=num_hands + 1)
                                    p.double_down(key=k)
                                    p.double_down(key=num_hands + 1)

                                # do not split cards - double down
                                elif r.double_down and decision == 'Dh' and p.sufficient_funds(bet):
                                    p.set_bankroll(-bet)
                                    p.double_down(key=k)

                                # do not split cards - hit
                                elif decision in ['Ph', 'Dh', 'H']:
                                    p.hit(key=k)

                                # do not split cards - stand
                                elif decision == 'S':
                                    p.stand(key=k)

                                else:
                                    raise NotImplementedError('No implementation for that flag')

                            else:

                                # double down
                                if r.double_down and decision in ['Dh', 'Ds'] and p.sufficient_funds(bet):
                                    p.set_bankroll(-bet)
                                    p.double_down(key=k)

                                # hit
                                elif decision in ['Rh', 'Dh', 'H']:
                                    p.hit(key=k)

                                # stand
                                elif decision in ['Rs', 'Ds', 'S']:
                                    p.stand(key=k)

                                elif decision == 'B':
                                    p.busted(key=k)

                                else:
                                    raise NotImplementedError('No implementation for that flag')

                # if a single player does not have a busted or surrendered hand, dealer has to play out hand
                num_surrender = sum([p.get_surrender()])
                num_busted = sum([p.get_busted(key=k) for k in p.hands_dict.keys()])
                num_stand = sum([p.get_stand(key=k) for k in p.hands_dict.keys()])

                if num_surrender + num_busted < num_stand:
                    dealer_turn = True

            while dealer_turn:
                soft_total, hard_total = count_hand(dealer_hand)

                if r.s17:  # dealer must stay on soft 17 (ace counted as 11)

                    if 17 <= soft_total <= 21 or hard_total >= 17:
                        dealer_total = max_count_hand(dealer_hand)
                        c.add_to_visible_cards(dealer_hole_card)  # add hole card to visible card list
                        dealer_turn = False

                    else:
                        d.hit(hand=dealer_hand)

                else:  # dealer must hit on soft 17

                    if 17 < soft_total <= 21 or hard_total >= 17:
                        dealer_total = max_count_hand(dealer_hand)
                        c.add_to_visible_cards(dealer_hole_card)  # add hole card to visible card list
                        dealer_turn = False

                    else:
                        d.hit(hand=dealer_hand)

            print('Dealer up card:', dealer_up_card)

            while True:

                # get dealer total
                dealer_total = max_count_hand(dealer_hand)
                print('Dealers hand:', dealer_hand)
                print('Dealer total:', dealer_total)

                for p in t.get_players():

                    # get player totals
                    for k in p.hands_dict.keys():
                        print(p.get_name(), 'hand #', k, ':', p.get_hand(key=k))
                        player_total = max_count_hand(p.get_hand(key=k))
                        player_bet = p.get_bet(key=k)
                        print(p.get_name(), 'total on hand #', k, ':', player_total)

                        if p.get_surrender():
                            print('**', p.get_name(), 'surrenders hand **')
                            p.set_bankroll(0.5 * player_bet)  # player receives half of original wager back

                        elif player_total == 21 and dealer_total == 21:
                            print('** Push -', p.get_name(), 'and dealer both have 21 **')
                            p.set_bankroll(player_bet)  # pushes

                        elif player_total == 21:
                            print('**', p.get_name(), 'has blackjack **')
                            p.set_bankroll(player_bet + (player_bet * r.blackjack_payout))  # player receives blackjack payout

                        elif dealer_total == 21:
                            print('** Dealer has blackjack **')
                            pass  # player loses wager

                        elif player_total > 21:
                            print('**', p.get_name(), 'busts on hand #', k, '**')
                            pass  # busted and dealer wins automatically

                        elif dealer_total > 21:
                            print('** Dealer busts on hand #', k, '**')
                            p.set_bankroll(2 * player_bet)  # dealer busted and player wins bet amount

                        else:
                            if dealer_total == player_total:
                                print('** Push on hand #', k, '**')
                                p.set_bankroll(player_bet)  # push

                            elif player_total > dealer_total:
                                print('**', p.get_name(), 'beats dealer on hand #', k, '**')
                                p.set_bankroll(2 * player_bet)  # player beats dealer

                            else:
                                print('** Dealer beats', p.get_name(), 'on hand #', k, '**')
                                pass  # dealer beats player

                    print(p.get_name(), 'ending bankroll:', p.get_bankroll())
                    print('Remaining decks:', c.remaining_decks())

                break

            print('------------------------------------------------------------------')
