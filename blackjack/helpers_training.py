from collections import OrderedDict
from blackjack.back_counter import BackCounter
from blackjack.card_counter import CardCounter
from blackjack.dealer import Dealer
from blackjack.enums import CardCountingSystem, HandStatus
from blackjack.helpers_simulation import get_count, get_insurance_count, get_placed_bet
from blackjack.helpers_simulation import _update_betting_stats, _update_win_stats
from blackjack.helpers_simulation import _update_push_stats, _update_loss_stats
from blackjack.helpers_simulation import place_insurance_bet, initialize_hands
from blackjack.helpers_simulation import _finished_splitting_aces, dealer_turn, clear_hands
from blackjack.helpers_simulation import place_bet as place_bet_simulation
from blackjack.helpers_simulation import player_plays_hands as player_plays_hands_simulation
from blackjack.helpers_simulation import compare_hands as compare_hands_simulation
from blackjack.player import Player
from blackjack.playing_strategy import PlayingStrategy
from blackjack.rules import Rules
from blackjack.shoe import Shoe
from blackjack.stats import StatsCategory
from blackjack.table import Table


def _update_insurance_stats(
    dealer: Dealer,
    player: Player,
    insurance_bet: float | int,
    insurance_count: float | int | None
) -> None:
    if dealer.hand.is_blackjack:
        print('Insurance bet won! Dealer has Blackjack.')
        player.adjust_bankroll(amount=insurance_bet * 2)
        player.stats.add_value(
            count=insurance_count,
            category=StatsCategory.INSURANCE_NET_WINNINGS,
            value=insurance_bet
        )
    else:
        print('Insurance bet lost! Dealer does not have Blackjack.')
        player.stats.add_value(
            count=insurance_count,
            category=StatsCategory.INSURANCE_NET_WINNINGS,
            value=insurance_bet * -1
        )


def _update_blackjack_stats(
    dealer: Dealer,
    player: Player,
    placed_bet: float | int,
    blackjack_payout: float | int,
    count: float | int | None
) -> None:
    if player.get_first_hand().is_blackjack:
        if dealer.hand.is_blackjack:
            print(f'Hand pushed! Both {player.name} and dealer have Blackjack.')
            player.adjust_bankroll(amount=placed_bet)
            player.stats.add_hand(count=count, category=StatsCategory.PLAYER_HANDS_PUSHED)
            player.stats.add_value(count=count, category=StatsCategory.PLAYER_BLACKJACKS)
            player.stats.add_value(count=count, category=StatsCategory.DEALER_BLACKJACKS)
        else:
            print(f'Hand won! {player.name} has Blackjack.')
            player.adjust_bankroll(amount=placed_bet * (1 + blackjack_payout))
            player.stats.add_hand(count=count, category=StatsCategory.PLAYER_HANDS_WON)
            player.stats.add_value(count=count, category=StatsCategory.PLAYER_BLACKJACKS)
            player.stats.add_value(
                count=count,
                category=StatsCategory.NET_WINNINGS,
                value=placed_bet * blackjack_payout
            )
    else:
        print('Hand lost! Dealer has Blackjack.')
        player.stats.add_hand(count=count, category=StatsCategory.PLAYER_HANDS_LOST)
        player.stats.add_value(count=count, category=StatsCategory.DEALER_BLACKJACKS)
        player.stats.add_value(
            count=count,
            category=StatsCategory.NET_WINNINGS,
            value=placed_bet * -1
        )


def _update_late_surrender_stats(player: Player, placed_bet: float | int, count: float | int | None) -> None:
    print(f'Hand lost! {player.name} surrenders.')
    player.adjust_bankroll(amount=placed_bet * 0.5)
    player.stats.add_hand(count=count, category=StatsCategory.PLAYER_HANDS_LOST)
    player.stats.add_value(count=count, category=StatsCategory.PLAYER_SURRENDERS)
    player.stats.add_value(
        count=count,
        category=StatsCategory.NET_WINNINGS,
        value=placed_bet * -0.5
    )


def place_bet(player: Player, rules: Rules, recommended_amount: float | int, count: float | int | None) -> None:
    """Adjusts the total bet based on a player's placed bet."""
    while True:
        try:
            amount = float(input(f'> What amount would {player.name} like to bet (min ${rules.min_bet:,.2f}, max ${rules.max_bet:,.2f})?: '))
            if rules.min_bet <= amount <= rules.max_bet and amount <= player.bankroll:
                print(f'{player.name} placed a ${amount:,.2f} bet (recommended amount: ${recommended_amount:,.2f})')
                break
            print('Placed bet amount is not allowed. Please enter a different amount.')
        except ValueError:
            print('Incorrect value. Please enter a float or integer.')

    player.get_first_hand().add_to_total_bet(amount=amount)
    _update_betting_stats(player=player, hand_bet=amount, count=count)


def add_back_counters(table: Table, rules: Rules, count_dict: dict[Player, float | int | None], removed_training_player: bool) -> bool:
    """Adds back counters to the table."""
    table_changes = False
    for observer in table.observers.copy():
        count = count_dict[observer]
        if isinstance(observer, BackCounter) and count is not None and observer.can_enter(count=count) and not observer.training:
            table.add_back_counter(back_counter=observer)
            print(f'{observer.name} joined the table')
            table_changes = True
        elif isinstance(observer, BackCounter) and observer.has_sufficient_bankroll(amount=rules.min_bet) and observer.training and not removed_training_player:
            while True:
                add_choice = input(f'> Would {observer.name} like to be added to the table (Y = yes, N = no)?: ').upper()
                if add_choice == 'Y':
                    table.add_back_counter(back_counter=observer)
                    print(f'{observer.name} joined the table')
                    table_changes = True
                    break
                if add_choice == 'N':
                    break
                print('Incorrect option. Please enter "Y" or "N".')
    return table_changes


def remove_back_counters(table: Table, count_dict: dict[Player, float | int | None]) -> tuple[bool, bool]:
    """Removes back counter from the table."""
    table_changes = False
    removed_training_player = False
    for player in table.players.copy():
        count = count_dict[player]
        if isinstance(player, BackCounter) and count is not None and player.can_exit(count=count) and not player.training:
            table.remove_back_counter(back_counter=player)
            print(f'{player.name} left the table')
            table_changes = True
        elif isinstance(player, BackCounter) and player.training:
            while True:
                remove_choice = input(f'> Would {player.name} like to be removed from the table (Y = yes, N = no)?: ').upper()
                if remove_choice == 'Y':
                    table.remove_back_counter(back_counter=player)
                    print(f'{player.name} left the table')
                    removed_training_player = True
                    break
                if remove_choice == 'N':
                    break
                print('Incorrect option. Please enter "Y" or "N".')
    return table_changes, removed_training_player


def player_initial_decision(
    player: Player,
    count: float | int | None,
    insurance_count: float | int | None,
    rules: Rules,
    dealer: Dealer,
    playing_strategy: PlayingStrategy
) -> str | None:
    """
    Determines a player's initial decision based on the first two cards dealt
    to them by the dealer.

    """
    first_hand = player.get_first_hand()
    print(f"{player.name}'s hand: {' '.join(first_hand.cards)} (Total: {first_hand.total})")
    if rules.insurance and dealer.up_card == 'A' and not first_hand.is_blackjack and isinstance(player, CardCounter) and \
        player.insurance and player.has_sufficient_bankroll(amount=first_hand.total_bet * 0.5):
        while True:
            insurance_choice = input(f'> Would {player.name} like to purchase insurance (Y = yes, N = no)?: ').upper()
            if insurance_choice == 'Y':
                insurance_bet = first_hand.total_bet * 0.5
                place_insurance_bet(player=player, amount=insurance_bet, count=insurance_count)
                _update_insurance_stats(
                    dealer=dealer,
                    player=player,
                    insurance_bet=insurance_bet,
                    insurance_count=insurance_count
                )
                break
            if insurance_choice == 'N':
                break
            print('Incorrect option. Please enter "Y" or "N".')

    if first_hand.is_blackjack or dealer.hand.is_blackjack:
        _update_blackjack_stats(
            dealer=dealer,
            player=player,
            placed_bet=first_hand.total_bet,
            blackjack_payout=rules.blackjack_payout,
            count=count
        )
        first_hand.status = HandStatus.SETTLED
        return None

    valid_decisions = OrderedDict({'H': 'hit', 'S': 'stand'})
    if player._is_split_allowed(hand=first_hand, max_hands=rules.max_hands):
        valid_decisions['P'] = 'split'
    if rules.double_down and player.has_sufficient_bankroll(amount=first_hand.total_bet):
        valid_decisions['D'] = 'double down'
    if rules.late_surrender:
        valid_decisions['R'] = 'late surrender'

    while True:
        verbose_options = ', '.join(f'{symbol} = {description}' for symbol, description in valid_decisions.items())
        decision = input(f"> What decision would {player.name} like to make ({verbose_options})?: ").upper()

        if decision in valid_decisions:
            break
        valid_symbols = ', '.join('"' + symbol + '"' for symbol in valid_decisions)
        print(f'Incorrect option. Please enter one of the following options: {valid_symbols}')

    optimal_decision = player.decision(
        hand=first_hand,
        dealer_up_card=dealer.up_card,
        max_hands=rules.max_hands,
        playing_strategy=playing_strategy
    )

    if len(optimal_decision) == 2:
        if optimal_decision[0] in valid_decisions:
            optimal_decision = optimal_decision[0]
        else:
            optimal_decision = optimal_decision[1].upper()

    if decision != optimal_decision:
        print(f"Incorrect decision! Basic strategy recommends to {valid_decisions[optimal_decision]} with a total of {first_hand.total} versus a dealer's {dealer.up_card}.")

    if decision == 'R':
        _update_late_surrender_stats(player=player, placed_bet=first_hand.total_bet, count=count)
        first_hand.status = HandStatus.SETTLED
        return None

    return decision


def player_plays_hands(
    player: Player,
    shoe: Shoe,
    count: float | int | None,
    insurance_count: float | int | None,
    dealer: Dealer,
    rules: Rules,
    playing_strategy: PlayingStrategy
) -> None:
    """Player plays out their hand(s)."""
    decision = player_initial_decision(
        player=player,
        count=count,
        insurance_count=insurance_count,
        dealer=dealer,
        rules=rules,
        playing_strategy=playing_strategy
    )

    if not decision:
        return

    if decision == 'P':
        print('Playing hand #1...')

    hand_number = 0
    another_hand = 0
    while True:

        current_hand = player.hands[hand_number]
        current_hand_total_bet = current_hand.total_bet

        if current_hand.number_of_cards == 1:
            current_hand.add_card(card=dealer.deal_card(shoe=shoe))
            print(f'{player.name} hits: {current_hand.cards[-1]} (Total: {current_hand.total})')
            if _finished_splitting_aces(current_hand=current_hand, player=player, rules=rules):
                current_hand.status = HandStatus.SHOWDOWN

        elif decision == 'P':
            _update_betting_stats(player=player, hand_bet=current_hand_total_bet, count=count)
            player.hands.append(current_hand.split())
            current_hand.add_card(card=dealer.deal_card(shoe=shoe))
            print(f'{player.name} hits: {current_hand.cards[-1]} (Total: {current_hand.total})')
            another_hand += 1
            if _finished_splitting_aces(current_hand=current_hand, player=player, rules=rules):
                current_hand.status = HandStatus.SHOWDOWN

        elif decision == 'D':
            _update_betting_stats(player=player, hand_bet=current_hand_total_bet, count=count)
            player.stats.add_value(count=count, category=StatsCategory.PLAYER_DOUBLE_DOWNS)
            current_hand.add_card(card=dealer.deal_card(shoe=shoe))
            print(f'{player.name} hits: {current_hand.cards[-1]} (Total: {current_hand.total})')
            current_hand.add_to_total_bet(amount=current_hand_total_bet)
            current_hand.status = HandStatus.SHOWDOWN

        elif decision == 'H':
            current_hand.add_card(card=dealer.deal_card(shoe=shoe))
            print(f'{player.name} hits: {current_hand.cards[-1]} (Total: {current_hand.total})')

        else:
            current_hand.status = HandStatus.SHOWDOWN

        if current_hand.is_busted:
            print(f"Hand lost! {player.name} busted with {current_hand.total}.")
            _update_loss_stats(player=player, hand_bet=current_hand_total_bet, count=count)
            current_hand.status = HandStatus.SETTLED

        if current_hand.status == HandStatus.IN_PLAY:
            valid_decisions = OrderedDict({'H': 'hit', 'S': 'stand'})
            if player._is_split_allowed(hand=current_hand, max_hands=rules.max_hands):
                valid_decisions['P'] = 'split'
            if player.has_sufficient_bankroll(amount=current_hand_total_bet) and current_hand.number_of_cards == 2 and \
                ((rules.double_down and not current_hand.was_split and not current_hand.is_split) or \
                (rules.double_after_split and (current_hand.was_split or current_hand.is_split))):
                valid_decisions['D'] = 'double down'

            while True:
                verbose_options = ', '.join(f'{symbol} = {description}' for symbol, description in valid_decisions.items())
                decision = input(f"> What decision would {player.name} like to make ({verbose_options})?: ").upper()

                if decision in valid_decisions:
                    break
                valid_symbols = ', '.join('"' + symbol + '"' for symbol in valid_decisions)
                print(f'Incorrect option. Please enter one of the following options: {valid_symbols}')

            optimal_decision = player.decision(
                hand=current_hand,
                dealer_up_card=dealer.up_card,
                max_hands=rules.max_hands,
                playing_strategy=playing_strategy
            )

            if len(optimal_decision) == 2:
                if optimal_decision[0] in valid_decisions:
                    optimal_decision = optimal_decision[0]
                else:
                    optimal_decision = optimal_decision[1].upper()

            if decision != optimal_decision:
                print(f"Incorrect decision! Basic strategy recommends to {valid_decisions[optimal_decision]} with a total of {current_hand.total} versus a dealer's {dealer.up_card}.")

        elif another_hand > 0:
            another_hand -= 1
            hand_number += 1
            print(f'\nPlaying hand #{hand_number + 1}...')
        else:
            break


def dealer_plays_hand(shoe: Shoe, dealer: Dealer, s17: bool, verbose: bool) -> None:
    """Dealer plays out their hand."""
    while dealer.hand.total < 17 or (dealer.hand.total == 17 and dealer.hand.is_soft and not s17):
        dealer.hand.add_card(card=dealer.deal_card(shoe=shoe))
        if verbose:
            print(f'Dealer hits: {dealer.hand.cards[-1]} (Total: {dealer.hand.total})')


def compare_hands(player: Player, count: float | int | None, dealer: Dealer) -> None:
    """
    Compares the dealer's hand to any hands played by players at the
    table that were not previously settled.

    """
    if any(hand for hand in player.hands if hand.status == HandStatus.SHOWDOWN):
        input('> Press Enter when ready to advance')
        print('\n----- COMPARE HANDS -----')

        for hand in (hand for hand in player.hands if hand.status == HandStatus.SHOWDOWN):
            if dealer.hand.is_busted:
                print(f'Hand won! Dealer busted with {dealer.hand.total}.' )
                _update_win_stats(player=player, hand_bet=hand.total_bet, count=count)
            elif hand.total > dealer.hand.total:
                print(f"Hand won! {player.name}'s hand ({hand.total}) beats the dealer's ({dealer.hand.total}).")
                _update_win_stats(player=player, hand_bet=hand.total_bet, count=count)
            elif hand.total == dealer.hand.total:
                print(f'Hand pushed! {player.name} and dealer both have {hand.total}.')
                _update_push_stats(player=player, hand_bet=hand.total_bet, count=count)
            else:
                print(f"Hand lost! {player.name}'s hand ({hand.total}) loses to the dealer's ({dealer.hand.total}).")
                _update_loss_stats(player=player, hand_bet=hand.total_bet, count=count)
            hand.status = HandStatus.SETTLED


def play_round(
    table: Table,
    dealer: Dealer,
    rules: Rules,
    shoe: Shoe,
    playing_strategy: PlayingStrategy
) -> None:
    """Plays a round of blackjack between a dealer and players at a table."""
    print('~' * 100)
    count_dict = get_count(table=table, shoe=shoe)


    if any(player for player in table.players + table.observers if isinstance(player, BackCounter) and player.has_sufficient_bankroll(amount=rules.min_bet)):
        print('\n----- BACK COUNTER CHANGES -----')
        table_changes_remove, removed_training_player = remove_back_counters(table=table, count_dict=count_dict)
        table_changes_add = add_back_counters(table=table, rules=rules, count_dict=count_dict, removed_training_player=removed_training_player)
        if not (table_changes_remove or table_changes_add):
            print('No back counters were added to/removed from the table prior to the round')

    placed_bet_dict = get_placed_bet(table=table, count_dict=count_dict)

    print('\n------ PLACE BETS -----')
    for player in table.players:
        player.stats.add_value(count=count_dict[player], category=StatsCategory.TOTAL_ROUNDS_PLAYED)
        if isinstance(player, CardCounter) and player.training:
            print(f'{player.name} has an available bankroll of ${player.bankroll:,.2f}')
            place_bet(player=player, rules=rules, recommended_amount=placed_bet_dict[player], count=count_dict[player])
        else:
            place_bet_simulation(player=player, amount=placed_bet_dict[player], count=count_dict[player])

    players = table.players
    if players:
        initialize_hands(dealer=dealer, players=players, shoe=shoe)
        input('> Press Enter when ready to advance')
        print(f'\n----- INITIAL DEAL TO DEALER{"/OTHER PLAYERS" if len(players) > 1 else ""} -----')
        initial_hands = {}
        for player in table.players:
            if (isinstance(player, CardCounter) and not player.training) or not isinstance(player, CardCounter):
                print(f"{player.name}'s initial cards: {' '.join(player.get_first_hand().cards)}")
                initial_hands[player.name] = player.get_first_hand().cards.copy()
        print(f"Dealer's up card: {dealer.up_card}")

        insurance_count_dict = get_insurance_count(players=players, shoe=shoe)

        for player in players:
            if isinstance(player, CardCounter) and player.training:
                input('> Press Enter when ready to advance')
                print(f'\n----- PLAY HAND VS. DEALER {dealer.up_card}-----')
                player_plays_hands(
                    player=player,
                    shoe=shoe,
                    count=count_dict[player],
                    insurance_count=insurance_count_dict[player],
                    dealer=dealer,
                    rules=rules,
                    playing_strategy=playing_strategy
                )
            else:
                player_plays_hands_simulation(
                    player=player,
                    shoe=shoe,
                    count=count_dict[player],
                    insurance_count=insurance_count_dict[player],
                    dealer=dealer,
                    rules=rules,
                    playing_strategy=playing_strategy
                )

        other_cards_seen = False
        if dealer_turn(players=players):
            verbose = False
            for player in players:
                if isinstance(player, CardCounter) and player.training and any(hand for hand in player.hands if hand.status == HandStatus.SHOWDOWN):
                    input('> Press Enter when ready to advance')
                    print(f'\n----- DEALER PLAYS HAND (UP CARD {dealer.up_card}) -----')
                    print(f"Dealer's hole card: {dealer.hole_card} (Total: {dealer.hand.total})")
                    verbose = True

            shoe.add_to_seen_cards(card=dealer.hole_card)
            dealer_plays_hand(shoe=shoe, dealer=dealer, s17=rules.s17, verbose=verbose)
            for player in players:
                if isinstance(player, CardCounter) and player.training:
                    compare_hands(player=player, count=count_dict[player], dealer=dealer)
                else:
                    compare_hands_simulation(player=player, count=count_dict[player], dealer=dealer)

            input('> Press Enter when ready to advance')
            print('\n----- OTHER CARDS SEEN -----')
            if not verbose:
                dealer_cards = [dealer.hole_card]
                if dealer.hand.number_of_cards > 2:
                    dealer_cards.extend(dealer.hand.cards[2:])
                print(f"Dealer's added cards: {' '.join(dealer_cards)}")
                other_cards_seen = True
        elif dealer.hand.is_blackjack or rules.dealer_shows_hole_card:
            input('> Press Enter when ready to advance')
            print('\n----- OTHER CARDS SEEN -----')
            dealer_cards = [dealer.hole_card]
            if dealer.hand.number_of_cards > 2:
                dealer_cards.extend(dealer.hand.cards[2:])
            print(f"Dealer's added cards: {' '.join(dealer_cards)}")
            shoe.add_to_seen_cards(card=dealer.hole_card)
            other_cards_seen = True
        else:
            input('> Press Enter when ready to advance')
            print('\n----- OTHER CARDS SEEN -----')

        for player in players:
            if (isinstance(player, CardCounter) and not player.training) or not isinstance(player, CardCounter):
                player_cards: list[str] = []
                for hand in player.hands:
                    player_cards.extend(hand.cards)

                for card in initial_hands[player.name]:
                    if card in player_cards:
                        player_cards.remove(card)

                if player_cards:
                    print(f"{player.name}'s added cards: {' '.join(player_cards)}")
                    other_cards_seen = True

        if not other_cards_seen:
            print('No other cards seen during round')

        clear_hands(dealer=dealer, players=players)

        input('> Press Enter when ready to advance')
        print('\n----- CURRENT COUNT -----')
        for player in players + table.observers:
            if isinstance(player, CardCounter) and player.training:
                print(f'The {player.card_counting_system.value} running count after this round is {shoe.running_count(card_counting_system=player.card_counting_system)}')
                if player.card_counting_system != CardCountingSystem.KO:
                    remaining_decks = shoe.remaining_decks
                    if abs(int(remaining_decks) - remaining_decks) < 0.01:
                        remaining_decks = int(remaining_decks)

                    true_count = shoe.true_count(card_counting_system=player.card_counting_system)
                    if abs(int(true_count) - true_count) < 0.01:
                        true_count = int(true_count)

                    print(f'The {player.card_counting_system.value} true count after this round (assuming {remaining_decks} remaining decks) is {true_count} (rounded to the nearest integer value)')

        while True:
            continue_training = input('> Would you like to continue playing (Y or Enter = yes, N = no)?: ').upper()
            if continue_training in {'Y', ''}:
                for player in players.copy():
                    if isinstance(player, CardCounter) and player.training and not player.has_sufficient_bankroll(amount=rules.min_bet):
                        print(f'{player.name} has insufficient bankroll to continue training. Exiting.')
                        for player in players.copy():
                            table.remove_player(player)
                break
            if continue_training == 'N':
                for player in players.copy():
                    table.remove_player(player)
                break
            print('Incorrect option. Please enter "Y" or "N".')
