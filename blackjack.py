import random
import basic_strategy as bs
from counting_strategies import *
from helper import *

# TODO clean up classes and put in separate files
# TODO Kelly Criterion for betting
# TODO make poor players
# TODO run simulations

class HouseRules(object):

    def __init__(
            self, min_bet, max_bet, s17, resplit_pairs, resplit_limit, blackjack_payout,
            double_down, double_after_split, insurance, late_surrender
    ):
        self.min_bet = int(min_bet)
        self.max_bet = int(max_bet)
        self.s17 = s17
        self.resplit_pairs = resplit_pairs
        if resplit_pairs:
            assert resplit_limit > 0, 'Re-split limit be a positive integer'
        self.resplit_limit = int(resplit_limit)  # bounded by 4 * shoe size
        self.blackjack_payout = blackjack_payout
        self.double_down = double_down
        self.double_after_split = double_after_split
        self.insurance = insurance
        self.late_surrender = late_surrender


# TODO stack cards to be a certain count
class Cards(object):

    def __init__(self, shoe_size):
        assert shoe_size in [4, 6, 8], 'Shoe size must be either 4, 6, or 8 decks'
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
        assert 0.5 <= float(penetration) <= 0.9, 'Penetration must be a float between 0.5 and 0.9'
        if ((52 * self.shoe_size) - len(self.deck))/(52 * self.shoe_size) >= float(penetration):
            return True
        return False


class CountingStrategy(object):

    def __init__(self, cards, strategy):
        assert isinstance(cards, Cards), 'cards must be an instance of Cards'
        assert strategy in ['Hi-Lo', 'Hi-Opt I', 'Hi-Opt II', 'Omega II', 'Halves', 'Zen Count']
        self.cards = cards
        self.strategy = strategy

    def running_count(self):
        # TODO add additional counting systems from https://en.wikipedia.org/wiki/Card_counting
        # TODO some counting systems require the type of card (spade, diamond, etc.)
        if self.strategy == 'Hi-Lo':
            return sum([hi_lo.get(card) for card in self.cards.visible_cards])
        elif self.strategy == 'Hi-Opt I':
            return sum([hi_opt_1.get(card) for card in self.cards.visible_cards])
        elif self.strategy == 'Hi-Opt II':
            return sum([hi_opt_2.get(card) for card in self.cards.visible_cards])
        elif self.strategy == 'Omega II':
            return sum([omega_2.get(card) for card in self.cards.visible_cards])
        elif self.strategy == 'Halves':
            return sum([halves.get(card) for card in self.cards.visible_cards])
        elif self.strategy == 'Zen Count':
            return sum([zen_count.get(card) for card in self.cards.visible_cards])

    def true_count(self):
        # TODO may want to tweak accuracy -- players have to eyeball remaining decks while playing
        if self.strategy in ['Hi-Lo', 'Omega II', 'Halves', 'Zen Count']:
            return round(self.running_count()/self.cards.remaining_decks(), 1)
        raise ValueError('True count not used for this counting strategy')


class Dealer(object):

    def __init__(self, cards):
        assert isinstance(cards, Cards), 'cards must be an instance of Cards'
        self.cards = cards

    def hit(self, hand):
        hand.append(self.cards.deal_card())
        return hand


class BasicStrategy(object):

    def __init__(self, rules):
        assert isinstance(rules, HouseRules), 'rules must be an instance of HouseRules'
        self.rules = rules

    def splits(self):
        if self.rules.s17:
            return bs.s17_splits
        return bs.h17_splits

    def soft(self):
        if self.rules.s17:
            return bs.s17_soft
        return bs.h17_soft

    def hard(self):
        if self.rules.s17:
            return bs.s17_hard
        return bs.h17_hard


class Player(object):

    def __init__(self, name, cards, rules, play_strategy, count_strategy, bankroll):
        assert isinstance(cards, Cards), 'cards must be an instance of Cards'
        assert isinstance(rules, HouseRules), 'rules must be an instance of HouseRules'
        assert isinstance(play_strategy, BasicStrategy), 'strategy must be an instance of BasicStrategy'
        assert isinstance(count_strategy, CountingStrategy), 'strategy must be an instance of CountingStrategy'
        assert bankroll >= rules.min_bet, 'Bankroll must be greater than minimum bet'
        self.name = name
        self.cards = cards
        self.rules = rules
        self.play_strategy = play_strategy
        self.count_strategy = count_strategy
        self.bankroll = float(bankroll)
        self.hands_dict = {}

    def get_name(self):
        return self.name

    def sufficient_funds(self, amount):
        if self.bankroll - amount >= 0:
            return True
        return False

    def set_bankroll(self, amount):
        self.bankroll = self.bankroll + amount

    def initial_bet(self, amount):
        assert amount >= self.rules.min_bet, 'Initial bet must exceed table minimum'
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

    def __init__(self):
        self.players = []

    def get_players(self):
        return self.players

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
        return 'Player is not at table'


if __name__ == "__main__":

    # Initialize classes
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
    c = Cards(shoe_size=6)
    ps = BasicStrategy(rules=r)
    cs = CountingStrategy(cards=c, strategy='Hi-Lo')
    t = Table()

    # dealer
    d = Dealer(cards=c)

    # players at table - players are dealt in order of being added to the table
    player1 = Player(name='P1', cards=c, rules=r, play_strategy=ps, count_strategy=cs, bankroll=100000)
    player2 = Player(name='P2', cards=c, rules=r, play_strategy=ps, count_strategy=cs, bankroll=100000)
    player3 = Player(name='P3', cards=c, rules=r, play_strategy=ps, count_strategy=cs, bankroll=100000)

    # add players to table
    t.add_player([player1, player2, player3])

    # shuffle cards
    c.shuffle()

    while not c.cut_card_reached(penetration=0.75) and len(t.get_players()) > 0:
        dealer_turn = False

        dealer_hand = []

        for p in t.get_players():

            print(p.get_name(), 'starting bankroll:', p.bankroll)

            # TODO Change amount wagered based on card counting
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
                        p.set_bankroll(0.5 * wager)  # player receives half of original wager back

                    elif player_total == 21 and dealer_total == 21:
                        print('** Push -', p.get_name(), 'and dealer both have 21 **')
                        p.set_bankroll(wager)  # pushes

                    elif player_total == 21:
                        print('**', p.get_name(), 'has blackjack **')
                        p.set_bankroll(wager + (wager * r.blackjack_payout))  # player receives blackjack payout

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

                print(p.get_name(), 'ending bankroll:', p.bankroll)

            break

        print('------------------------------------------------------------------')
