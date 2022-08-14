from blackjack import CardCounter, BackCounter, CountingStrategy
from blackjack.hand import HandStatus
from blackjack.simulation_stats import StatsCategory


def _get_player_count(player, shoe):
    if player.counting_strategy == CountingStrategy.KO:
        return shoe.running_count(strategy=player.counting_strategy)
    return shoe.true_count(strategy=player.counting_strategy)


def get_initial_count(table, shoe):
    """
    Gets the count for every player at
    the table before hands are dealt and
    stores it in a dictionary.
    """
    count_dict = {}
    for player in table.players + table.waiting_players:
        if isinstance(player, CardCounter):
            count_dict[player] = _get_player_count(player=player, shoe=shoe)
        else:
            count_dict[player] = None
    return count_dict


def get_insurance_count(table, shoe):
    """
    Gets the count for every player at
    the table before an insurance bet is
    made and stores it in a dictionary.
    """
    count_dict = {}
    for player in table.players:
        if isinstance(player, CardCounter) and player.insurance:
            count_dict[player] = _get_player_count(player=player, shoe=shoe)
        else:
            count_dict[player] = None
    return count_dict


def get_initial_wager(table, count_dict):
    """
    Gets the initial wager for every player
    at the table and stores it in a dictionary.
    """
    initial_wager_dict = {}
    for player in table.players.copy():
        initial_wager = player.initial_wager(count=count_dict[player])
        if player.has_sufficient_bankroll(amount=initial_wager):
            initial_wager_dict[player] = initial_wager
        else:
            table.remove_player(player=player)
            del count_dict[player]
    return initial_wager_dict


def _update_insurance_stats(dealer, player, insurance_wager, insurance_count):
    if dealer.hand.is_blackjack():
        player.edit_bankroll(amount=insurance_wager * 2)
        player.stats.add_amount(
            count=insurance_count,
            category=StatsCategory.INSURANCE_AMOUNT_EARNED,
            increment=insurance_wager
        )
    else:
        player.stats.add_amount(
            count=insurance_count,
            category=StatsCategory.INSURANCE_AMOUNT_EARNED,
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
    

def _update_loss_stats(player, hand_wager, count):
    player.stats.add_hand(count=count, category=StatsCategory.HANDS_LOST)
    player.stats.add_amount(
            count=count,
            category=StatsCategory.AMOUNT_EARNED,
            increment=hand_wager * -1
    )
    

def _update_push_stats(player, hand_wager, count):
    player.edit_bankroll(amount=hand_wager)
    player.stats.add_hand(count=count, category=StatsCategory.HANDS_PUSHED)
    

def place_initial_wager(player, initial_wager, count):
    """
    Adjusts the total bet based on a player's initial wager.
    """
    player.first_hand.total_bet = initial_wager
    _update_increase_wager_stats(player=player, hand_wager=initial_wager, count=count)


def place_insurance_wager(player, insurance_wager, insurance_count):
    """
    Adjusts the side bet based on a player's insurance wager.
    """
    player.first_hand.side_bet = insurance_wager
    player.edit_bankroll(amount=insurance_wager * -1)
    player.stats.add_amount(
        count=insurance_count,
        category=StatsCategory.INSURANCE_AMOUNT_WAGERED,
        increment=insurance_wager
    )


def initialize_hands(table, dealer, shoe):
    """
    Initializes the hands for the dealer
    and each player at the table.
    """
    for seen in [False, True]:
        for player in table.players:
            player.first_hand.add_card(card=dealer.deal_card(shoe=shoe))
        dealer.hand.add_card(card=dealer.deal_card(shoe=shoe, seen=seen))
        

def add_back_counters(table, count_dict):
    """
    Adds back counters to the table.
    """
    for player in table.waiting_players.copy():
        if player.can_enter(count=count_dict[player]) and player.partner in table.players.copy():
            table.add_back_counter(player=player)


def remove_back_counters(table, count_dict):
    """
    Removes back counter from the table.
    """
    for player in table.players.copy():
        if type(player) == BackCounter and player.can_exit(count=count_dict[player]):
            table.remove_back_counter(player=player)


def player_initial_decision(player, count, insurance_count, rules, dealer):
    """
    Determines a player's initial decision based on the
    first two cards dealt to them by the dealer.
    """
    if rules.insurance and dealer.up_card() == 'A':
        if isinstance(player, CardCounter) and player.insurance and insurance_count >= player.insurance:
            insurance_wager = player.first_hand.total_bet * 0.5
            place_insurance_wager(player=player, insurance_wager=insurance_wager, insurance_count=insurance_count)
            _update_insurance_stats(
                dealer=dealer,
                player=player,
                insurance_wager=insurance_wager,
                insurance_count=insurance_count
            )
    
    if player.first_hand.is_blackjack() or dealer.hand.is_blackjack():
        _update_blackjack_stats(
            dealer=dealer,
            player=player,
            initial_wager=player.first_hand.total_bet,
            blackjack_payout=rules.blackjack_payout,
            count=count
        )
        player.first_hand.status = HandStatus.SETTLED
        return
    
    decision = player.decision(
            hand=player.first_hand,
            dealer_up_card=dealer.up_card(),
            rules=rules
    )
    
    if rules.late_surrender and decision in {'Rh', 'Rs', 'Rp'}:
        _update_late_surrender_stats(player=player, initial_wager=player.first_hand.total_bet, count=count)
        player.first_hand.status = HandStatus.SETTLED
        return
    
    return decision


def player_plays_hands(player, shoe, count, insurance_count, dealer, rules):
    """
    Player plays out their hand(s).
    """
    decision = player_initial_decision(
            player=player,
            count=count,
            insurance_count=insurance_count,
            dealer=dealer,
            rules=rules
    )
    
    if not decision:
        return
    
    hand_number = 0
    another_hand = 0
    while True:
        
        current_hand = player.hands[hand_number]

        if current_hand.number_of_cards() == 1:
            current_hand.add_card(card=dealer.deal_card(shoe=shoe))
            if not rules.resplit_aces and current_hand.cards[0] == 'A':
                current_hand.status = HandStatus.SHOWDOWN
            
        elif decision in {'P', 'Rp'} or (decision == 'Ph' and rules.double_after_split and \
            player.has_sufficient_bankroll(amount=current_hand.total_bet * 3)):
            _update_increase_wager_stats(player=player, hand_wager=current_hand.total_bet, count=count)
            player.hands.append(current_hand.split())
            current_hand.add_card(card=dealer.deal_card(shoe=shoe))
            another_hand += 1
            if not rules.resplit_aces and current_hand.cards[0] == 'A':
                current_hand.status = HandStatus.SHOWDOWN
        
        elif rules.double_down and decision in {'Dh', 'Ds'} and current_hand.number_of_cards() == 2 and \
            not current_hand.is_previous_hand_split and not current_hand.is_current_hand_split and \
            player.has_sufficient_bankroll(amount=current_hand.total_bet):
            _update_increase_wager_stats(player=player, hand_wager=current_hand.total_bet, count=count)
            current_hand.add_card(card=dealer.deal_card(shoe=shoe))
            current_hand.total_bet = current_hand.total_bet
            current_hand.status = HandStatus.SHOWDOWN
        
        elif rules.double_after_split and decision in {'Dh', 'Ds'} and current_hand.number_of_cards() == 2 and \
            (current_hand.is_previous_hand_split or current_hand.is_current_hand_split) and \
            player.has_sufficient_bankroll(amount=current_hand.total_bet):
            _update_increase_wager_stats(player=player, hand_wager=current_hand.total_bet, count=count)
            current_hand.add_card(card=dealer.deal_card(shoe=shoe))
            current_hand.total_bet = current_hand.total_bet
            current_hand.status = HandStatus.SHOWDOWN
            
        elif decision in {'Rh', 'Dh', 'Ph', 'H'}:
            current_hand.add_card(card=dealer.deal_card(shoe=shoe))
        
        else:
            current_hand.status = HandStatus.SHOWDOWN
        
        if current_hand.is_busted():
            _update_loss_stats(player=player, hand_wager=current_hand.total_bet, count=count)
            current_hand.status = HandStatus.SETTLED

        if current_hand.status == HandStatus.IN_PLAY:
            decision = player.decision(
                    hand=current_hand,
                    dealer_up_card=dealer.up_card(),
                    rules=rules
            )
        elif another_hand > 0:
            another_hand -= 1
            hand_number += 1
        else:
            break
        

def dealer_turn(table):
    """
    Determines if any of the hands played
    by players at the table were not previously
    settled.
    """
    return any(
        hand.status == HandStatus.SHOWDOWN
        for player in table.players
        for hand in player.hands
    )


def all_hands_busted(table):
    """
    Determines if all player's hands
    at the table are busted.
    """
    return all(
        hand.is_busted()
        for player in table.players
        for hand in player.hands
    )
    

def dealer_plays_hand(shoe, dealer, rules):
    """
    Dealer plays out their hand.
    """
    while dealer.hand.total() < 17 or (dealer.hand.total() == 17 and dealer.hand.is_soft() and not rules.s17):
        dealer.hand.add_card(card=dealer.deal_card(shoe=shoe))
        

def compare_hands(player, count, dealer):
    """
    Compares the dealer's hand to any hands
    played by players at the table that were not
    previously settled.
    """
    showdown_hands = [hand for hand in player.hands if hand.status == HandStatus.SHOWDOWN]
    for hand in showdown_hands:
        if dealer.hand.is_busted() or (hand.total() > dealer.hand.total()):
            _update_win_stats(player=player, hand_wager=hand.total_bet, count=count)
        elif hand.total() == dealer.hand.total():
            _update_push_stats(player=player, hand_wager=hand.total_bet, count=count)
        else:
            _update_loss_stats(player=player, hand_wager=hand.total_bet, count=count)
        hand.status = HandStatus.SETTLED
        

def clear_hands(dealer, table):
    """
    Clears the dealer's hand as well as
    any hands played by players at the table
    when the outcome has been decided.
    """
    dealer.reset_hand()
    for player in table.players:
        player.reset_hands()
        

def play_round(table, dealer, rules, shoe):
    """
    Plays a round of blackjack between a
    dealer and players at a table.
    """
    count_dict = get_initial_count(table=table, shoe=shoe)
    add_back_counters(table=table, count_dict=count_dict)
    remove_back_counters(table=table, count_dict=count_dict)
    initial_wager_dict = get_initial_wager(table=table, count_dict=count_dict)
    
    for player in table.players:
        place_initial_wager(
            player=player,
            initial_wager=initial_wager_dict[player],
            count=count_dict[player]
        )
    
    if table.players:
        initialize_hands(table=table, dealer=dealer, shoe=shoe)
        insurance_count_dict = get_insurance_count(table=table, shoe=shoe)
        
        for player in table.players:
            player_plays_hands(
                player=player,
                shoe=shoe,
                count=count_dict[player],
                insurance_count=insurance_count_dict[player],
                dealer=dealer,
                rules=rules
            )
        
        if (all_hands_busted(table=table) and rules.dealer_shows_hole_card) or not all_hands_busted(table=table):
            shoe.add_to_seen_cards(card=dealer.hole_card())

        if dealer_turn(table=table):
            dealer_plays_hand(shoe=shoe, dealer=dealer, rules=rules)
            for player in table.players:
                compare_hands(player=player, count=count_dict[player], dealer=dealer)

        clear_hands(dealer=dealer, table=table)