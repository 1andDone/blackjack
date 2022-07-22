import random
from blackjack import CardCounter, BackCounter, CountingStrategy
from blackjack.dealer import Dealer
from blackjack.shoe import Shoe
from blackjack.hand import HandStatus
from blackjack.simulation_stats import StatsCategory


def _get_player_count(player, shoe):
    if player.counting_strategy == CountingStrategy.KO:
        return shoe.running_count(strategy=player.counting_strategy)
    return shoe.true_count(strategy=player.counting_strategy)


def _get_initial_count(table, shoe):
    count_dict = {}
    for player in table.players + table.waiting_players:
        if isinstance(player, CardCounter):
            count_dict[player] = _get_player_count(player=player, shoe=shoe)
        else:
            count_dict[player] = None
    return count_dict


def _get_insurance_count(table, shoe):
    count_dict = {}
    for player in table.players:
        if isinstance(player, CardCounter) and player.insurance:
            count_dict[player] = _get_player_count(player=player, shoe=shoe)
        else:
            count_dict[player] = None
    return count_dict


def _can_place_wager(player, wager):
    return player.has_sufficient_bankroll(amount=wager)
    

def _place_initial_wager(player, initial_wager, count):
    player.first_hand.total_bet += initial_wager
    player.edit_bankroll(amount=initial_wager * -1)
    player.stats.add_amount(
        count=count,
        category=StatsCategory.AMOUNT_WAGERED,
        increment=initial_wager
    )  
    

def initialize_hands(table, dealer, shoe):
    for seen in [False, True]:
        for player in table.players:
            player.hit(hand=player.hands[0], card=dealer.deal_card(shoe=shoe))
        dealer.hit(card=dealer.deal_card(shoe=shoe, seen=seen))


def _place_insurance_wager(player, insurance_wager, insurance_count):
    player.first_hand.side_bet = insurance_wager
    player.edit_bankroll(amount=insurance_wager * -1)
    player.stats.add_amount(
        count=insurance_count,
        category=StatsCategory.AMOUNT_WAGERED,
        increment=insurance_wager
    )


def _update_insurance_stats(dealer, player, insurance_wager, insurance_count):
    if dealer.hand.is_blackjack():
        player.edit_bankroll(amount=insurance_wager * 2)
        player.stats.add_amount(
            count=insurance_count,
            category=StatsCategory.AMOUNT_EARNED,
            increment=insurance_wager
        )
    else:
        player.stats.add_amount(
            count=insurance_count,
            category=StatsCategory.AMOUNT_EARNED,
            increment=insurance_wager * -1
        )
            

def _update_blackjack_stats(dealer, player, initial_wager, blackjack_payout, count):
    if player.first_hand.is_blackjack():
        if dealer.hand.is_blackjack():
            player.edit_bankroll(amount=initial_wager)
            player.stats.add_hand(count=count, category=StatsCategory.HANDS_PUSHED)
        else:
            player.edit_bankroll(amount=initial_wager * (1 + blackjack_payout))
            player.stats.add_hand(count=count, category=StatsCategory.HANDS_WON)
            player.stats.add_amount(
                count=count,
                category=StatsCategory.AMOUNT_EARNED,
                increment=initial_wager * blackjack_payout
            )
    else:
        player.stats.add_hand(count=count, category=StatsCategory.HANDS_LOST)
        player.stats.add_amount(
            count=count,
            category=StatsCategory.AMOUNT_EARNED,
            increment=initial_wager * -1
        )


def _update_late_surrender_stats(player, initial_wager, count):
    player.edit_bankroll(amount=initial_wager * 0.5)
    player.stats.add_hand(count=count, category=StatsCategory.HANDS_LOST)
    player.stats.add_amount(
        count=count,
        category=StatsCategory.AMOUNT_EARNED,
        increment=initial_wager * -0.5
    )


def _update_increase_wager_stats(player, hand_wager, count):
    player.edit_bankroll(amount=hand_wager * -1)
    player.stats.add_amount(
        count=count,
        category=StatsCategory.AMOUNT_WAGERED,
        increment=hand_wager
    )


def _update_win_stats(player, hand_wager, count):
    player.edit_bankroll(amount=hand_wager * 2)
    player.stats.add_hand(count=count, category=StatsCategory.HANDS_WON)
    player.stats.add_amount(
            count=count,
            category=StatsCategory.AMOUNT_EARNED,
            increment=hand_wager
    )
    

def _update_push_stats(player, hand_wager, count):
    player.edit_bankroll(amount=hand_wager)
    player.stats.add_hand(count=count, category=StatsCategory.HANDS_PUSHED)
    

def _update_loss_stats(player, hand_wager, count):
    player.stats.add_hand(count=count, category=StatsCategory.HANDS_LOST)
    player.stats.add_amount(
            count=count,
            category=StatsCategory.AMOUNT_EARNED,
            increment=hand_wager * -1
    )


def _add_back_counters(table, count_dict):
    if any(player for player in table.waiting_players.copy() if type(player) == BackCounter):
        for player in table.waiting_players.copy():
            if player.can_enter(count=count_dict[player]) and player.partner in table.players.copy():
                table.add_back_counter(player=player)


def _get_initial_wager(table, count_dict):
    initial_wager_dict = {}
    for player in table.players.copy():
        initial_wager = player.initial_wager(count=count_dict[player])
        if _can_place_wager(player=player, wager=initial_wager):
            initial_wager_dict[player] = initial_wager
        else:
            table.remove_player(player=player)
            del count_dict[player]
    return initial_wager_dict


def _remove_back_counters(table, count_dict):
    if any(player for player in table.players.copy() if type(player) == BackCounter):
        for player in table.players.copy():
            if type(player) == BackCounter and (player.can_exit(count=count_dict[player]) or player.partner not in table.players.copy()):
                table.remove_back_counter(player=player)


class Blackjack:
    """
    Represents the simulation of one or more
    games of blackjack.
    
    """
    def __init__(self, rules, table):
        """
        Parameters
        ----------
        rules: HouseRules
            HouseRules class instance
        table: Table
            Table class instance
        
        """
        self._rules = rules
        self._table = table
        self._dealer = Dealer()
    
    def _player_plays_hands(self, player, shoe, count, insurance_count):

        if self._rules.insurance and self._dealer.up_card() == 'A':
            if isinstance(player, CardCounter) and player.insurance and insurance_count >= player.insurance:
                insurance_wager = player.first_hand.total_bet * 0.5
                _place_insurance_wager(player=player, insurance_wager=insurance_wager, insurance_count=insurance_count)
                _update_insurance_stats(
                    dealer=self._dealer,
                    player=player,
                    insurance_wager=insurance_wager,
                    insurance_count=insurance_count
                )
        
        if player.first_hand.is_blackjack() or self._dealer.hand.is_blackjack():
            _update_blackjack_stats(dealer=self._dealer, player=player, initial_wager=player.first_hand.total_bet, blackjack_payout=self._rules.blackjack_payout, count=count)
            player.first_hand.status = HandStatus.SETTLED
            return
        
        decision = player.decision(
                hand=player.first_hand,
                dealer_up_card=self._dealer.up_card(),
                rules=self._rules
        )
        
        if self._rules.late_surrender and decision in {'Rh', 'Rs', 'Rp'}:
            _update_late_surrender_stats(player=player, initial_wager=player.first_hand.total_bet, count=count)
            player.first_hand.status = HandStatus.SETTLED
            return
        
        hand_number = 0
        another_hand = 0
        while True:
            
            current_hand = player.hands[hand_number]

            if current_hand.number_of_cards() == 1:
                player.hit(hand=current_hand, card=self._dealer.deal_card(shoe=shoe))
                if not self._rules.resplit_aces and current_hand.cards[0] == 'A':
                    current_hand.status = HandStatus.SHOWDOWN
                
            elif decision in {'P', 'Rp'} or (decision == 'Ph' and self._rules.double_after_split) and \
                _can_place_wager(player=player, wager=current_hand.total_bet):
                _update_increase_wager_stats(player=player, hand_wager=current_hand.total_bet, count=count)
                player.split(hand=current_hand)
                player.hit(hand=current_hand, card=self._dealer.deal_card(shoe=shoe))
                another_hand += 1
                if not self._rules.resplit_aces and current_hand.cards[0] == 'A':
                    current_hand.status = HandStatus.SHOWDOWN
            
            elif self._rules.double_down and decision in {'Dh', 'Ds'} and current_hand.number_of_cards() == 2 and \
                not current_hand.is_previous_hand_split and not current_hand.is_current_hand_split and \
                _can_place_wager(player=player, wager=current_hand.total_bet):
                _update_increase_wager_stats(player=player, hand_wager=current_hand.total_bet, count=count)
                player.hit(hand=current_hand, card=self._dealer.deal_card(shoe=shoe))
                current_hand.total_bet = current_hand.total_bet
                current_hand.status = HandStatus.SHOWDOWN
            
            elif self._rules.double_after_split and decision in {'Dh', 'Ds'} and current_hand.number_of_cards() == 2 and \
                current_hand.is_current_hand_split:
                _update_increase_wager_stats(player=player, hand_wager=current_hand.total_bet, count=count)
                player.hit(hand=current_hand, card=self._dealer.deal_card(shoe=shoe))
                current_hand.total_bet = current_hand.total_bet
                current_hand.status = HandStatus.SHOWDOWN
                
            elif decision in {'Rh', 'Dh', 'Ph', 'H'}:
                current_hand.add_card(card=self._dealer.deal_card(shoe=shoe))
            
            elif decision in {'Rs', 'Ds', 'S'}:
                current_hand.status = HandStatus.SHOWDOWN
                
            else:
                raise Exception
            
            if current_hand.is_busted():
                _update_loss_stats(player=player, hand_wager=current_hand.total_bet, count=count)
                current_hand.status = HandStatus.SETTLED
            
            if current_hand.status == HandStatus.IN_PLAY:
                decision = player.decision(
                        hand=current_hand,
                        dealer_up_card=self._dealer.up_card(),
                        rules=self._rules
                )
            elif another_hand > 0:
                another_hand -= 1
                hand_number += 1
            else:
                break
    
    def _dealer_turn(self):
        for player in self._table.players:
            for hand in player.hands:
                if hand.status == HandStatus.SHOWDOWN:
                    return True
        return False
    
    def _dealer_plays_hand(self, shoe):
        total = self._dealer.hand.total()
        shoe.add_to_seen_cards(card=self._dealer.hole_card())
        
        while total < 17 or (total == 17 and self._dealer.hand.is_soft() and not self._rules.s17):
            card = self._dealer.deal_card(shoe=shoe)
            self._dealer.hand.add_card(card=card)
            total = self._dealer.hand.total()
        
    def _compare_hands(self, player, count):
        showdown_hands = [hand for hand in player.hands if hand.status == HandStatus.SHOWDOWN]
        for hand in showdown_hands:
            if not hand.is_busted() and (self._dealer.hand.is_busted() or (hand.total() > self._dealer.hand.total())):
                _update_win_stats(player=player, hand_wager=hand.total_bet, count=count)
            elif not self._dealer.hand.is_busted() and hand.total() == self._dealer.hand.total():
                _update_push_stats(player=player, hand_wager=hand.total_bet, count=count)
            else:
                _update_loss_stats(player=player, hand_wager=hand.total_bet, count=count)
            hand.status = HandStatus.SETTLED
    
    def _clear_hands(self):
        self._dealer.reset_hand()
        for player in self._table.players:
            player.reset_hands()
    
    def _play_round(self, shoe):
        # get count for each player before initial wager
        count_dict = _get_initial_count(table=self._table, shoe=shoe)
        
        # add back counters
        _add_back_counters(table=self._table, count_dict=count_dict)
        
        # remove players with insufficient funds
        initial_wager_dict = _get_initial_wager(table=self._table, count_dict=count_dict)
        
        # remove back counters
        _remove_back_counters(table=self._table, count_dict=count_dict)
        
        for player in self._table.players:
            _place_initial_wager(
                player=player,
                initial_wager=initial_wager_dict[player],
                count=count_dict[player]
            )
            
        initialize_hands(table=self._table, dealer=self._dealer, shoe=shoe)
        
        # get count for each player before insurance wager
        insurance_count_dict = _get_insurance_count(table=self._table, shoe=shoe)
        
        for player in self._table.players:
            self._player_plays_hands(
                    player=player,
                    shoe=shoe,
                    count=count_dict[player],
                    insurance_count=insurance_count_dict[player]
            )
            
        if self._dealer_turn():
            shoe.add_to_seen_cards(card=self._dealer.hole_card())
            self._dealer_plays_hand(shoe=shoe)
            for player in self._table.players:
                self._compare_hands(player=player, count=count_dict[player])
        else:
            if self._rules.dealer_shows_hole_card:
                shoe.add_to_seen_cards(card=self._dealer.hole_card())
                
        self._clear_hands()
    
    def _play_shoe(self, penetration):
        shoe = Shoe(size=self._rules.shoe_size)
        shoe.shuffle()
        
        while not shoe.cut_card_reached(penetration=penetration):
           self._play_round(shoe=shoe)
        
    def simulate(self, penetration, number_of_shoes, seed=None):
        if seed:
            random.seed(seed)
        
        for _ in range(0, number_of_shoes):
            self._play_shoe(penetration=penetration)