from blackjack.back_counter import BackCounter
from blackjack.card_counter import CardCounter
from blackjack.dealer import Dealer
from blackjack.enums import CardCountingSystem, HandStatus
from blackjack.hand import Hand
from blackjack.player import Player
from blackjack.playing_strategy import PlayingStrategy
from blackjack.rules import Rules
from blackjack.shoe import Shoe
from blackjack.stats import StatsCategory
from blackjack.table import Table


def _get_count(card_counter: CardCounter, shoe: Shoe) -> float | int | None:
    if card_counter.card_counting_system == CardCountingSystem.KO:
        return shoe.running_count(card_counting_system=card_counter.card_counting_system)
    return shoe.true_count(card_counting_system=card_counter.card_counting_system)


def get_count(table: Table, shoe: Shoe) -> dict[Player, float | int | None]:
    """
    Gets the count for every player at the table before
    bets are placed and stores it in a dictionary.

    """
    count_dict: dict[Player, float | int | None] = {}
    for player in table.players + table.observers:
        if isinstance(player, CardCounter):
            count_dict[player] = _get_count(card_counter=player, shoe=shoe)
        else:
            count_dict[player] = None
    return count_dict


def get_insurance_count(players: list[Player], shoe: Shoe) -> dict[Player, float | int | None]:
    """
    Gets the count for every player at the table before
    an insurance bet is made and stores it in a dictionary.

    """
    count_dict: dict[Player, float | int | None] = {}
    for player in players:
        if isinstance(player, CardCounter) and player.insurance:
            count_dict[player] = _get_count(card_counter=player, shoe=shoe)
        else:
            count_dict[player] = None
    return count_dict


def get_placed_bet(table: Table, count_dict: dict[Player, float | int | None]) -> dict[Player, float | int]:
    """
    Gets the placed bet for every player at the table and stores
    it in a dictionary.

    """
    placed_bet_dict: dict[Player, float | int] = {}
    for player in table.players.copy():
        placed_bet = player.placed_bet(count=count_dict[player])
        if player.has_sufficient_bankroll(amount=placed_bet):
            placed_bet_dict[player] = placed_bet
        else:
            table.remove_player(player=player)
    return placed_bet_dict


def _update_insurance_stats(
    dealer: Dealer,
    player: Player,
    insurance_bet: float | int,
    insurance_count: float | int | None
) -> None:
    if dealer.hand.is_blackjack:
        player.adjust_bankroll(amount=insurance_bet * 2)
        player.stats.add_value(
            count=insurance_count,
            category=StatsCategory.INSURANCE_NET_WINNINGS,
            value=insurance_bet
        )
    else:
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
            player.adjust_bankroll(amount=placed_bet)
            player.stats.add_hand(count=count, category=StatsCategory.PLAYER_HANDS_PUSHED)
            player.stats.add_value(count=count, category=StatsCategory.PLAYER_BLACKJACKS)
            player.stats.add_value(count=count, category=StatsCategory.DEALER_BLACKJACKS)
        else:
            player.adjust_bankroll(amount=placed_bet * (1 + blackjack_payout))
            player.stats.add_hand(count=count, category=StatsCategory.PLAYER_HANDS_WON)
            player.stats.add_value(count=count, category=StatsCategory.PLAYER_BLACKJACKS)
            player.stats.add_value(
                count=count,
                category=StatsCategory.NET_WINNINGS,
                value=placed_bet * blackjack_payout
            )
    else:
        player.stats.add_hand(count=count, category=StatsCategory.PLAYER_HANDS_LOST)
        player.stats.add_value(count=count, category=StatsCategory.DEALER_BLACKJACKS)
        player.stats.add_value(
            count=count,
            category=StatsCategory.NET_WINNINGS,
            value=placed_bet * -1
        )


def _update_late_surrender_stats(player: Player, placed_bet: float | int, count: float | int | None) -> None:
    player.adjust_bankroll(amount=placed_bet * 0.5)
    player.stats.add_hand(count=count, category=StatsCategory.PLAYER_HANDS_LOST)
    player.stats.add_value(count=count, category=StatsCategory.PLAYER_SURRENDERS)
    player.stats.add_value(
        count=count,
        category=StatsCategory.NET_WINNINGS,
        value=placed_bet * -0.5
    )


def _update_betting_stats(player: Player, hand_bet: float | int, count: float | int | None) -> None:
    player.adjust_bankroll(amount=hand_bet * -1)
    player.stats.add_value(
        count=count,
        category=StatsCategory.AMOUNT_BET,
        value=hand_bet
    )


def _update_win_stats(player: Player, hand_bet: float | int, count: float | int | None) -> None:
    player.adjust_bankroll(amount=hand_bet * 2)
    player.stats.add_hand(count=count, category=StatsCategory.PLAYER_HANDS_WON)
    player.stats.add_value(
        count=count,
        category=StatsCategory.NET_WINNINGS,
        value=hand_bet
    )


def _update_loss_stats(player: Player, hand_bet: float | int, count: float | int | None) -> None:
    player.stats.add_hand(count=count, category=StatsCategory.PLAYER_HANDS_LOST)
    player.stats.add_value(
        count=count,
        category=StatsCategory.NET_WINNINGS,
        value=hand_bet * -1
    )


def _update_push_stats(player: Player, hand_bet: float | int, count: float | int | None) -> None:
    player.adjust_bankroll(amount=hand_bet)
    player.stats.add_hand(count=count, category=StatsCategory.PLAYER_HANDS_PUSHED)


def place_bet(player: Player, amount: float | int, count: float | int | None) -> None:
    """Adjusts the total bet based on a player's placed bet."""
    player.get_first_hand().add_to_total_bet(amount=amount)
    _update_betting_stats(player=player, hand_bet=amount, count=count)


def place_insurance_bet(player: Player, amount: float | int, count: float | int | None) -> None:
    """Adjusts the side bet based on a player's insurance bet."""
    player.get_first_hand().add_to_side_bet(amount=amount)
    player.adjust_bankroll(amount=amount * -1)
    player.stats.add_value(
        count=count,
        category=StatsCategory.INSURANCE_AMOUNT_BET,
        value=amount
    )


def initialize_hands(dealer: Dealer, players: list[Player], shoe: Shoe) -> None:
    """Initializes the hands for the dealer and each player at the table."""
    for seen in [False, True]:
        for player in players:
            player.get_first_hand().add_card(card=dealer.deal_card(shoe=shoe))
        dealer.hand.add_card(card=dealer.deal_card(shoe=shoe, seen=seen))


def add_back_counters(table: Table, count_dict: dict[Player, float | int | None]) -> None:
    """Adds back counters to the table."""
    for observer in table.observers.copy():
        count = count_dict[observer]
        if isinstance(observer, BackCounter) and count is not None and observer.can_enter(count=count):
            table.add_back_counter(back_counter=observer)


def remove_back_counters(table: Table, count_dict: dict[Player, float | int | None]) -> None:
    """Removes back counter from the table."""
    for player in table.players.copy():
        count = count_dict[player]
        if isinstance(player, BackCounter) and count is not None and player.can_exit(count=count):
            table.remove_back_counter(back_counter=player)


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
    if rules.insurance and dealer.up_card == 'A' and not first_hand.is_blackjack:
        if isinstance(player, CardCounter) and player.insurance and insurance_count and \
            insurance_count >= player.insurance:
            insurance_bet = first_hand.total_bet * 0.5
            place_insurance_bet(player=player, amount=insurance_bet, count=insurance_count)
            _update_insurance_stats(
                dealer=dealer,
                player=player,
                insurance_bet=insurance_bet,
                insurance_count=insurance_count
            )

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

    decision = player.decision(
            hand=first_hand,
            dealer_up_card=dealer.up_card,
            max_hands=rules.max_hands,
            playing_strategy=playing_strategy
    )

    if rules.late_surrender and decision in {'Rh', 'Rs', 'Rp'}:
        _update_late_surrender_stats(player=player, placed_bet=first_hand.total_bet, count=count)
        first_hand.status = HandStatus.SETTLED
        return None

    return decision


def _finished_splitting_aces(current_hand: Hand, player: Player, rules: Rules) -> bool:
    """Determines if a player is finished splitting Aces."""
    return current_hand.cards[0] == 'A' and (player.number_of_hands == rules.max_hands or \
        not rules.resplit_aces or current_hand.cards[1] != 'A')


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

    hand_number = 0
    another_hand = 0
    while True:

        current_hand = player.hands[hand_number]
        current_hand_total_bet = current_hand.total_bet

        if current_hand.number_of_cards == 1:
            current_hand.add_card(card=dealer.deal_card(shoe=shoe))
            if _finished_splitting_aces(current_hand=current_hand, player=player, rules=rules):
                current_hand.status = HandStatus.SHOWDOWN

        # a sufficient bankroll check for the 'Rp' and 'P' decisions is performed in Player class
        elif decision in {'Rp', 'P'} or (decision == 'Ph' and rules.double_after_split and \
            player.has_sufficient_bankroll(amount=current_hand_total_bet * 3)):
            _update_betting_stats(player=player, hand_bet=current_hand_total_bet, count=count)
            player.hands.append(current_hand.split())
            current_hand.add_card(card=dealer.deal_card(shoe=shoe))
            another_hand += 1
            if _finished_splitting_aces(current_hand=current_hand, player=player, rules=rules):
                current_hand.status = HandStatus.SHOWDOWN

        elif rules.double_down and decision in {'Dh', 'Ds'} and current_hand.number_of_cards == 2 and \
            not current_hand.was_split and not current_hand.is_split and \
            player.has_sufficient_bankroll(amount=current_hand_total_bet):
            _update_betting_stats(player=player, hand_bet=current_hand_total_bet, count=count)
            player.stats.add_value(count=count, category=StatsCategory.PLAYER_DOUBLE_DOWNS)
            current_hand.add_card(card=dealer.deal_card(shoe=shoe))
            current_hand.add_to_total_bet(amount=current_hand_total_bet)
            current_hand.status = HandStatus.SHOWDOWN

        elif rules.double_after_split and decision in {'Dh', 'Ds'} and current_hand.number_of_cards == 2 and \
            (current_hand.was_split or current_hand.is_split) and \
            player.has_sufficient_bankroll(amount=current_hand_total_bet):
            _update_betting_stats(player=player, hand_bet=current_hand_total_bet, count=count)
            player.stats.add_value(count=count, category=StatsCategory.PLAYER_DOUBLE_DOWNS)
            current_hand.add_card(card=dealer.deal_card(shoe=shoe))
            current_hand.add_to_total_bet(amount=current_hand_total_bet)
            current_hand.status = HandStatus.SHOWDOWN

        elif decision in {'Rh', 'Dh', 'Ph', 'H'}:
            current_hand.add_card(card=dealer.deal_card(shoe=shoe))

        else:
            current_hand.status = HandStatus.SHOWDOWN

        if current_hand.is_busted:
            _update_loss_stats(player=player, hand_bet=current_hand_total_bet, count=count)
            current_hand.status = HandStatus.SETTLED

        if current_hand.status == HandStatus.IN_PLAY:
            decision = player.decision(
                hand=current_hand,
                dealer_up_card=dealer.up_card,
                max_hands=rules.max_hands,
                playing_strategy=playing_strategy
            )
        elif another_hand > 0:
            another_hand -= 1
            hand_number += 1
        else:
            break


def dealer_turn(players: list[Player]) -> bool:
    """
    Determines if any of the hands played by players at the table were
    not previously settled.

    """
    return any(hand.status == HandStatus.SHOWDOWN for player in players for hand in player.hands)


def dealer_plays_hand(shoe: Shoe, dealer: Dealer, s17: bool) -> None:
    """Dealer plays out their hand."""
    while dealer.hand.total < 17 or (dealer.hand.total == 17 and dealer.hand.is_soft and not s17):
        dealer.hand.add_card(card=dealer.deal_card(shoe=shoe))


def compare_hands(player: Player, count: float | int | None, dealer: Dealer) -> None:
    """
    Compares the dealer's hand to any hands played by players at the
    table that were not previously settled.

    """
    for hand in (hand for hand in player.hands if hand.status == HandStatus.SHOWDOWN):
        if dealer.hand.is_busted or (hand.total > dealer.hand.total):
            _update_win_stats(player=player, hand_bet=hand.total_bet, count=count)
        elif hand.total == dealer.hand.total:
            _update_push_stats(player=player, hand_bet=hand.total_bet, count=count)
        else:
            _update_loss_stats(player=player, hand_bet=hand.total_bet, count=count)
        hand.status = HandStatus.SETTLED


def clear_hands(dealer: Dealer, players: list[Player]) -> None:
    """
    Clears the dealer's hand as well as any hands played by players at
    the table when the outcome has been decided.

    """
    dealer.reset_hand()
    for player in players:
        player.reset_hands()


def play_round(
    table: Table,
    dealer: Dealer,
    rules: Rules,
    shoe: Shoe,
    playing_strategy: PlayingStrategy
) -> None:
    """Plays a round of blackjack between a dealer and players at a table."""
    count_dict = get_count(table=table, shoe=shoe)
    remove_back_counters(table=table, count_dict=count_dict)
    add_back_counters(table=table, count_dict=count_dict)
    placed_bet_dict = get_placed_bet(table=table, count_dict=count_dict)

    for player in table.players:
        player.stats.add_value(count=count_dict[player], category=StatsCategory.TOTAL_ROUNDS_PLAYED)
        place_bet(
            player=player,
            amount=placed_bet_dict[player],
            count=count_dict[player]
        )

    players = table.players
    if players:
        initialize_hands(dealer=dealer, players=players, shoe=shoe)
        insurance_count_dict = get_insurance_count(players=players, shoe=shoe)

        for player in players:
            player_plays_hands(
                player=player,
                shoe=shoe,
                count=count_dict[player],
                insurance_count=insurance_count_dict[player],
                dealer=dealer,
                rules=rules,
                playing_strategy=playing_strategy
            )

        if dealer_turn(players=players):
            shoe.add_to_seen_cards(card=dealer.hole_card)
            dealer_plays_hand(shoe=shoe, dealer=dealer, s17=rules.s17)
            for player in players:
                compare_hands(player=player, count=count_dict[player], dealer=dealer)
        elif dealer.hand.is_blackjack or rules.dealer_shows_hole_card:
            shoe.add_to_seen_cards(card=dealer.hole_card)

        clear_hands(dealer=dealer, players=players)
