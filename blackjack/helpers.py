from blackjack.back_counter import BackCounter
from blackjack.card_counter import CardCounter
from blackjack.dealer import Dealer
from blackjack.enums import CountingStrategy, HandStatus
from blackjack.house_rules import HouseRules
from blackjack.player import Player
from blackjack.shoe import Shoe
from blackjack.stats import StatsCategory
from blackjack.table import Table


def _get_card_counter_count(card_counter: CardCounter, shoe: Shoe) -> float | int | None:
    if card_counter.counting_strategy == CountingStrategy.KO:
        return shoe.running_count(strategy=card_counter.counting_strategy)
    return shoe.true_count(strategy=card_counter.counting_strategy)


def get_initial_count(table: Table, shoe: Shoe) -> dict[Player, float | int | None]:
    """
    Gets the count for every player at
    the table before hands are dealt and
    stores it in a dictionary.

    """
    count_dict: dict[Player, float | int | None] = {}
    for player in table.players + table.observers:
        if isinstance(player, CardCounter):
            count_dict[player] = _get_card_counter_count(card_counter=player, shoe=shoe)
        else:
            count_dict[player] = None
    return count_dict


def get_insurance_count(table: Table, shoe: Shoe) -> dict[Player, float | int | None]:
    """
    Gets the count for every player at
    the table before an insurance bet is
    made and stores it in a dictionary.

    """
    count_dict: dict[Player, float | int | None] = {}
    for player in table.players:
        if isinstance(player, CardCounter) and player.insurance:
            count_dict[player] = _get_card_counter_count(card_counter=player, shoe=shoe)
        else:
            count_dict[player] = None
    return count_dict


def get_initial_wager(table: Table, count_dict: dict[Player, float | int | None]) -> dict[Player, float | int]:
    """
    Gets the initial wager for every player
    at the table and stores it in a dictionary.

    """
    initial_wager_dict: dict[Player, float | int] = {}
    for player in table.players.copy():
        initial_wager = player.initial_wager(count=count_dict[player])
        if player.has_sufficient_bankroll(amount=initial_wager):
            initial_wager_dict[player] = initial_wager
        else:
            table.remove_player(player=player)
            del count_dict[player]
    return initial_wager_dict


def _update_insurance_stats(
    dealer: Dealer,
    player: Player,
    insurance_wager: float | int,
    insurance_count: float | int | None
) -> None:
    if dealer.hand.is_blackjack:
        player.update_bankroll(amount=insurance_wager * 2)
        player.stats.update_amount(
            count=insurance_count,
            category=StatsCategory.INSURANCE_AMOUNT_EARNED,
            increment=insurance_wager
        )
    else:
        player.stats.update_amount(
            count=insurance_count,
            category=StatsCategory.INSURANCE_AMOUNT_EARNED,
            increment=insurance_wager * -1
        )


def _update_blackjack_stats(
    dealer: Dealer,
    player: Player,
    initial_wager: float | int,
    blackjack_payout: float | int,
    count: float | int | None
) -> None:
    if player.first_hand.is_blackjack:
        if dealer.hand.is_blackjack:
            player.update_bankroll(amount=initial_wager)
            player.stats.add_hand(count=count, category=StatsCategory.HANDS_PUSHED)
        else:
            player.update_bankroll(amount=initial_wager * (1 + blackjack_payout))
            player.stats.add_hand(count=count, category=StatsCategory.HANDS_WON)
            player.stats.update_amount(
                count=count,
                category=StatsCategory.AMOUNT_EARNED,
                increment=initial_wager * blackjack_payout
            )
    else:
        player.stats.add_hand(count=count, category=StatsCategory.HANDS_LOST)
        player.stats.update_amount(
            count=count,
            category=StatsCategory.AMOUNT_EARNED,
            increment=initial_wager * -1
        )


def _update_late_surrender_stats(player: Player, initial_wager: float | int, count: float | int | None) -> None:
    player.update_bankroll(amount=initial_wager * 0.5)
    player.stats.add_hand(count=count, category=StatsCategory.HANDS_LOST)
    player.stats.update_amount(
        count=count,
        category=StatsCategory.AMOUNT_EARNED,
        increment=initial_wager * -0.5
    )


def _update_wager_stats(player: Player, hand_wager: float | int, count: float | int | None) -> None:
    player.update_bankroll(amount=hand_wager * -1)
    player.stats.update_amount(
        count=count,
        category=StatsCategory.AMOUNT_WAGERED,
        increment=hand_wager
    )


def _update_win_stats(player: Player, hand_wager: float | int, count: float | int | None) -> None:
    player.update_bankroll(amount=hand_wager * 2)
    player.stats.add_hand(count=count, category=StatsCategory.HANDS_WON)
    player.stats.update_amount(
        count=count,
        category=StatsCategory.AMOUNT_EARNED,
        increment=hand_wager
    )


def _update_loss_stats(player: Player, hand_wager: float | int, count: float | int | None) -> None:
    player.stats.add_hand(count=count, category=StatsCategory.HANDS_LOST)
    player.stats.update_amount(
        count=count,
        category=StatsCategory.AMOUNT_EARNED,
        increment=hand_wager * -1
    )


def _update_push_stats(player: Player, hand_wager: float | int, count: float | int | None) -> None:
    player.update_bankroll(amount=hand_wager)
    player.stats.add_hand(count=count, category=StatsCategory.HANDS_PUSHED)


def place_initial_wager(player: Player, initial_wager: float | int, count: float | int | None) -> None:
    """Adjusts the total bet based on a player's initial wager."""
    player.first_hand.update_total_bet(amount=initial_wager)
    _update_wager_stats(player=player, hand_wager=initial_wager, count=count)


def place_insurance_wager(player: Player, insurance_wager: float | int, insurance_count: float | int | None) -> None:
    """Adjusts the side bet based on a player's insurance wager."""
    player.first_hand.update_side_bet(amount=insurance_wager)
    player.update_bankroll(amount=insurance_wager * -1)
    player.stats.update_amount(
        count=insurance_count,
        category=StatsCategory.INSURANCE_AMOUNT_WAGERED,
        increment=insurance_wager
    )


def initialize_hands(table: Table, dealer: Dealer, shoe: Shoe) -> None:
    """Initializes the hands for the dealer and each player at the table."""
    for seen in [False, True]:
        for player in table.players:
            player.first_hand.add_card(card=dealer.deal_card(shoe=shoe))
        dealer.hand.add_card(card=dealer.deal_card(shoe=shoe, seen=seen))


def add_back_counters(table: Table, count_dict: dict[Player, float | int | None]) -> None:
    """Adds back counters to the table."""
    for player in table.observers.copy():
        count = count_dict[player]
        if isinstance(player, BackCounter) and count is not None and player.can_enter(count=count):
            table.add_back_counter(player=player)


def remove_back_counters(table: Table, count_dict: dict[Player, float | int | None]) -> None:
    """Removes back counter from the table."""
    for player in table.players.copy():
        count = count_dict[player]
        if isinstance(player, BackCounter) and count is not None and player.can_exit(count=count):
            table.remove_back_counter(player=player)


def player_initial_decision(
    player: Player,
    count: float | int | None,
    insurance_count: float | int | None,
    rules: HouseRules,
    dealer: Dealer
) -> str | None:
    """
    Determines a player's initial decision based on the
    first two cards dealt to them by the dealer.

    """
    if rules.insurance and dealer.up_card == 'A':
        if isinstance(player, CardCounter) and player.insurance and insurance_count and insurance_count >= player.insurance:
            insurance_wager = player.first_hand.total_bet * 0.5
            place_insurance_wager(player=player, insurance_wager=insurance_wager, insurance_count=insurance_count)
            _update_insurance_stats(
                dealer=dealer,
                player=player,
                insurance_wager=insurance_wager,
                insurance_count=insurance_count
            )

    if player.first_hand.is_blackjack or dealer.hand.is_blackjack:
        _update_blackjack_stats(
            dealer=dealer,
            player=player,
            initial_wager=player.first_hand.total_bet,
            blackjack_payout=rules.blackjack_payout,
            count=count
        )
        player.first_hand.status = HandStatus.SETTLED
        return None

    decision = player.decision(
            hand=player.first_hand,
            dealer_up_card=dealer.up_card,
            rules=rules
    )

    if rules.late_surrender and decision in {'Rh', 'Rs', 'Rp'}:
        _update_late_surrender_stats(player=player, initial_wager=player.first_hand.total_bet, count=count)
        player.first_hand.status = HandStatus.SETTLED
        return None

    return decision


def player_plays_hands(
    player: Player,
    shoe: Shoe,
    count: float | int | None,
    insurance_count: float | int | None,
    dealer: Dealer,
    rules: HouseRules
) -> None:
    """Player plays out their hand(s)."""
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

        if current_hand.number_of_cards == 1:
            current_hand.add_card(card=dealer.deal_card(shoe=shoe))
            if current_hand.cards[0] == 'A' and (len(player.hands) == rules.max_hands or \
                not rules.resplit_aces or current_hand.cards[1] != 'A'):
                current_hand.status = HandStatus.SHOWDOWN

        # a sufficient bankroll check for the 'Rp' and 'P' decisions is performed in Player._can_split
        elif decision in {'Rp', 'P'} or (decision == 'Ph' and rules.double_after_split and \
            player.has_sufficient_bankroll(amount=current_hand.total_bet * 3)):
            _update_wager_stats(player=player, hand_wager=current_hand.total_bet, count=count)
            player.hands.append(current_hand.split())
            current_hand.add_card(card=dealer.deal_card(shoe=shoe))
            another_hand += 1
            if current_hand.cards[0] == 'A' and (len(player.hands) == rules.max_hands or \
                not rules.resplit_aces or current_hand.cards[1] != 'A'):
                current_hand.status = HandStatus.SHOWDOWN

        elif rules.double_down and decision in {'Dh', 'Ds'} and current_hand.number_of_cards == 2 and \
            not current_hand.is_previous_hand_split and not current_hand.is_current_hand_split and \
            player.has_sufficient_bankroll(amount=current_hand.total_bet):
            _update_wager_stats(player=player, hand_wager=current_hand.total_bet, count=count)
            current_hand.add_card(card=dealer.deal_card(shoe=shoe))
            current_hand.update_total_bet(amount=current_hand.total_bet)
            current_hand.status = HandStatus.SHOWDOWN

        elif rules.double_after_split and decision in {'Dh', 'Ds'} and current_hand.number_of_cards == 2 and \
            (current_hand.is_previous_hand_split or current_hand.is_current_hand_split) and \
            player.has_sufficient_bankroll(amount=current_hand.total_bet):
            _update_wager_stats(player=player, hand_wager=current_hand.total_bet, count=count)
            current_hand.add_card(card=dealer.deal_card(shoe=shoe))
            current_hand.update_total_bet(amount=current_hand.total_bet)
            current_hand.status = HandStatus.SHOWDOWN

        elif decision in {'Rh', 'Dh', 'Ph', 'H'}:
            current_hand.add_card(card=dealer.deal_card(shoe=shoe))

        else:
            current_hand.status = HandStatus.SHOWDOWN

        if current_hand.is_busted:
            _update_loss_stats(player=player, hand_wager=current_hand.total_bet, count=count)
            current_hand.status = HandStatus.SETTLED

        if current_hand.status == HandStatus.IN_PLAY:
            decision = player.decision(
                    hand=current_hand,
                    dealer_up_card=dealer.up_card,
                    rules=rules
            )
        elif another_hand > 0:
            another_hand -= 1
            hand_number += 1
        else:
            break


def dealer_turn(table: Table) -> bool:
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


def all_hands_busted(table: Table) -> bool:
    """Determines if all player's hands at the table are busted."""
    return all(
        hand.is_busted
        for player in table.players
        for hand in player.hands
    )


def dealer_plays_hand(shoe: Shoe, dealer: Dealer, rules: HouseRules) -> None:
    """Dealer plays out their hand."""
    while dealer.hand.total < 17 or (dealer.hand.total == 17 and dealer.hand.is_soft and not rules.s17):
        dealer.hand.add_card(card=dealer.deal_card(shoe=shoe))


def compare_hands(player: Player, count: float | int | None, dealer: Dealer) -> None:
    """
    Compares the dealer's hand to any hands
    played by players at the table that were not
    previously settled.

    """
    showdown_hands = [hand for hand in player.hands if hand.status == HandStatus.SHOWDOWN]
    for hand in showdown_hands:
        if dealer.hand.is_busted or (hand.total > dealer.hand.total):
            _update_win_stats(player=player, hand_wager=hand.total_bet, count=count)
        elif hand.total == dealer.hand.total:
            _update_push_stats(player=player, hand_wager=hand.total_bet, count=count)
        else:
            _update_loss_stats(player=player, hand_wager=hand.total_bet, count=count)
        hand.status = HandStatus.SETTLED


def clear_hands(dealer: Dealer, table: Table) -> None:
    """
    Clears the dealer's hand as well as
    any hands played by players at the table
    when the outcome has been decided.

    """
    dealer.reset_hand()
    for player in table.players:
        player.reset_hands()


def play_round(table: Table, dealer: Dealer, rules: HouseRules, shoe: Shoe) -> None:
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
            shoe.add_to_seen_cards(card=dealer.hole_card)

        if dealer_turn(table=table):
            dealer_plays_hand(shoe=shoe, dealer=dealer, rules=rules)
            for player in table.players:
                compare_hands(player=player, count=count_dict[player], dealer=dealer)

        clear_hands(dealer=dealer, table=table)
