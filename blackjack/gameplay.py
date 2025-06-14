import json
from pathlib import Path
from collections import defaultdict
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


def log_blackjack_round(
        blackjack_log_json: Path, 
        shoe: Shoe,
        players: list[Player], 
        dealer: Dealer, 
        dealer_hand_is_blackjack: bool, 
        count_dict: dict,
        insurance_count_dict: dict, 
        placed_bet_dict: dict, 
        begining_bankroll_dict: dict
):
    logs = []
    for player in players:
        logs.append({
            "shoe_id": shoe.shoe_id,
            "player": player.name,
            "dealer_hand": dealer.hand.cards,
            "dealer_blackjack": dealer_hand_is_blackjack,
            "count": count_dict.get(player, None),
            "insurance_count": insurance_count_dict.get(player, None),
            "player_hands": [hand.cards for hand in player.hands],
            "bet": placed_bet_dict.get(player, None),
            "bankroll_start": begining_bankroll_dict[player],
            "bankroll_end": player.bankroll
        })
    with open(blackjack_log_json, "a") as f:
        for entry in logs:
            f.write(json.dumps(entry) + "\n")

def get_count(table: Table, shoe: Shoe) -> dict[CardCounter, float | int]:
    """
    Gets the count for every player at the table before
    bets are placed and stores it in a dictionary.

    """
    count_dict = {}
    for player in table.players + table.observers:
        if isinstance(player, CardCounter):
            card_counting_system = player.card_counting_system
            count_dict[player] = (
                shoe.running_count(card_counting_system=card_counting_system)
                if card_counting_system == CardCountingSystem.KO
                else shoe.true_count(card_counting_system=card_counting_system)
            )
    return count_dict


def get_insurance_count(players: list[Player], shoe: Shoe) -> dict[CardCounter, float | int]:
    """
    Gets the count for every player at the table before
    an insurance bet is made and stores it in a dictionary.

    """
    insurance_count_dict = {}
    for player in players:
        if isinstance(player, CardCounter) and player.insurance is not None:
            card_counting_system = player.card_counting_system
            insurance_count_dict[player] = (
                shoe.running_count(card_counting_system=card_counting_system)
                if card_counting_system == CardCountingSystem.KO
                else shoe.true_count(card_counting_system=card_counting_system)
            )
    return insurance_count_dict


def initialize_hands(dealer: Dealer, players: list[Player], shoe: Shoe) -> None:
    """Initializes the hands for the dealer and each player at the table."""
    first_hands = [player.get_first_hand() for player in players]
    dealer_hand = dealer.hand
    for seen in [False, True]:
        for first_hand in first_hands:
            first_hand.add_card(card=shoe.deal_card())
        dealer_hand.add_card(card=shoe.deal_card(seen=seen))


def player_initial_decision(
    player: Player,
    player_stats: defaultdict[tuple[float | int | None, StatsCategory], float],
    placed_bet: float | int,
    count: float | int | None,
    insurance_count: float | int | None,
    dealer_hand_is_blackjack: bool,
    dealer_up_card: str,
    rules: Rules,
    playing_strategy: PlayingStrategy
) -> str | None:
    """
    Determines a player's initial decision based on the first two cards dealt
    to them by the dealer.

    """
    first_hand = player.get_first_hand()

    # place bet
    first_hand.add_to_total_bet(amount=placed_bet)
    player.adjust_bankroll(amount=-placed_bet)
    player_stats[(count, StatsCategory.AMOUNT_BET)] += placed_bet

    total_bet = first_hand.total_bet
    half_bet = total_bet * 0.5
    player_hand_is_blackjack = first_hand.is_blackjack

    if (
        rules.insurance
        and dealer_up_card == 'A'
        and isinstance(player, CardCounter)
        and player.insurance is not None
        and insurance_count is not None
        and insurance_count >= player.insurance
        and player.has_sufficient_bankroll(amount=half_bet)
    ):
        # place insurance bet
        player_stats[(insurance_count, StatsCategory.INSURANCE_AMOUNT_BET)] += half_bet

        if dealer_hand_is_blackjack:
            player_stats[(insurance_count, StatsCategory.INSURANCE_NET_WINNINGS)] += total_bet
            player_stats[(count, StatsCategory.TOTAL_HANDS_PLAYED)] += 1
            player_stats[(count, StatsCategory.DEALER_BLACKJACKS)] += 1
            first_hand.status = HandStatus.SETTLED

            if player_hand_is_blackjack:
                player.adjust_bankroll(amount=2 * total_bet)
                player_stats[(count, StatsCategory.PLAYER_HANDS_PUSHED)] += 1
                player_stats[(count, StatsCategory.PLAYER_BLACKJACKS)] += 1
                return

            player.adjust_bankroll(amount=total_bet)
            player_stats[(count, StatsCategory.PLAYER_HANDS_LOST)] += 1
            player_stats[(count, StatsCategory.NET_WINNINGS)] -= total_bet
            return

        player.adjust_bankroll(amount=-half_bet)
        player_stats[(insurance_count, StatsCategory.INSURANCE_NET_WINNINGS)] -= half_bet

    if player_hand_is_blackjack:

        player_stats[(count, StatsCategory.TOTAL_HANDS_PLAYED)] += 1
        player_stats[(count, StatsCategory.PLAYER_BLACKJACKS)] += 1
        first_hand.status = HandStatus.SETTLED

        if dealer_hand_is_blackjack:
            player.adjust_bankroll(amount=total_bet)
            player_stats[(count, StatsCategory.PLAYER_HANDS_PUSHED)] += 1
            player_stats[(count, StatsCategory.DEALER_BLACKJACKS)] += 1
            return

        blackjack_winnings = total_bet * rules.blackjack_payout
        player.adjust_bankroll(amount=total_bet + blackjack_winnings)
        player_stats[(count, StatsCategory.PLAYER_HANDS_WON)] += 1
        player_stats[(count, StatsCategory.NET_WINNINGS)] += blackjack_winnings
        return

    if dealer_hand_is_blackjack:
        player_stats[(count, StatsCategory.TOTAL_HANDS_PLAYED)] += 1
        player_stats[(count, StatsCategory.PLAYER_HANDS_LOST)] += 1
        player_stats[(count, StatsCategory.DEALER_BLACKJACKS)] += 1
        player_stats[(count, StatsCategory.NET_WINNINGS)] -= total_bet
        first_hand.status = HandStatus.SETTLED
        return

    decision = player.decision(
        hand=first_hand,
        dealer_up_card=dealer_up_card,
        max_hands=rules.max_hands,
        playing_strategy=playing_strategy
    )

    if rules.late_surrender and decision in {'Rh', 'Rp', 'Rs'}:
        player.adjust_bankroll(amount=half_bet)
        player_stats[(count, StatsCategory.TOTAL_HANDS_PLAYED)] += 1
        player_stats[(count, StatsCategory.PLAYER_HANDS_LOST)] += 1
        player_stats[(count, StatsCategory.PLAYER_SURRENDERS)] += 1
        player_stats[(count, StatsCategory.NET_WINNINGS)] -= half_bet
        first_hand.status = HandStatus.SETTLED
        return

    return decision


def _finished_splitting_aces(hand: Hand, player: Player, rules: Rules) -> bool:
    """Determines if a player is finished splitting Aces."""
    cards = hand.cards
    return cards[0] == 'A' and (player.number_of_hands == rules.max_hands or \
        not rules.resplit_aces or cards[1] != 'A')


def player_plays_hands(
    player: Player,
    player_stats: defaultdict[tuple[float | int | None, StatsCategory], float],
    placed_bet: float | int,
    shoe: Shoe,
    count: float | int | None,
    insurance_count: float | int | None,
    dealer_hand_is_blackjack: bool,
    dealer_up_card: str,
    rules: Rules,
    playing_strategy: PlayingStrategy
) -> None:
    """Player plays out their hand(s)."""
    decision = player_initial_decision(
        player=player,
        player_stats=player_stats,
        placed_bet=placed_bet,
        count=count,
        insurance_count=insurance_count,
        dealer_hand_is_blackjack=dealer_hand_is_blackjack,
        dealer_up_card=dealer_up_card,
        rules=rules,
        playing_strategy=playing_strategy
    )

    if decision is None:
        return

    hand_number = 0
    another_hand = 0

    while True:

        hand = player.hands[hand_number]
        total_bet = hand.total_bet
        number_of_cards = hand.number_of_cards

        if number_of_cards == 1:
            hand.add_card(card=shoe.deal_card())
            if _finished_splitting_aces(hand=hand, player=player, rules=rules):
                hand.status = HandStatus.SHOWDOWN

        # a sufficient bankroll check for the 'Rp' and 'P' decisions is performed in Player class
        elif (
            decision in {'Rp', 'P'}
            or (decision == 'Ph'
            and rules.double_after_split
            and player.has_sufficient_bankroll(amount=total_bet * 3))
        ):
            player.adjust_bankroll(amount=-total_bet)
            player_stats[(count, StatsCategory.AMOUNT_BET)] += total_bet
            player.hands.append(hand.split())
            hand.add_card(card=shoe.deal_card())
            another_hand += 1
            if _finished_splitting_aces(hand=hand, player=player, rules=rules):
                hand.status = HandStatus.SHOWDOWN

        elif (
            decision in {'Dh', 'Ds'}
            and number_of_cards == 2
            and ((rules.double_down
            and not (hand.is_split
            or hand.was_split))
            or (rules.double_after_split
            and (hand.is_split
            or hand.was_split)))
            and player.has_sufficient_bankroll(amount=total_bet)
        ):
            player.adjust_bankroll(amount=-total_bet)
            player_stats[(count, StatsCategory.AMOUNT_BET)] += total_bet
            player_stats[(count, StatsCategory.PLAYER_DOUBLE_DOWNS)] += 1
            hand.add_card(card=shoe.deal_card())
            hand.add_to_total_bet(amount=total_bet)
            hand.status = HandStatus.SHOWDOWN

        elif decision in {'Rh', 'Dh', 'Ph', 'H'}:
            hand.add_card(card=shoe.deal_card())

        else:
            hand.status = HandStatus.SHOWDOWN
            if another_hand > 0:
                another_hand -= 1
                hand_number += 1
                continue
            break

        if hand.is_busted:
            player_stats[(count, StatsCategory.TOTAL_HANDS_PLAYED)] += 1
            player_stats[(count, StatsCategory.PLAYER_HANDS_LOST)] += 1
            player_stats[(count, StatsCategory.NET_WINNINGS)] -= total_bet
            hand.status = HandStatus.SETTLED

        if hand.status == HandStatus.IN_PLAY:
            decision = player.decision(
                hand=hand,
                dealer_up_card=dealer_up_card,
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
        dealer.hand.add_card(card=shoe.deal_card())


def compare_hands(
    player: Player,
    player_stats: defaultdict[tuple[float | int | None, StatsCategory], float],
    count: float | int | None,
    dealer_hand_is_busted: bool,
    dealer_hand_total: int
) -> None:
    """
    Compares the dealer's hand to any hands played by players at the
    table that were not previously settled.

    """
    for hand in (hand for hand in player.hands if hand.status == HandStatus.SHOWDOWN):
        total = hand.total
        total_bet = hand.total_bet

        if dealer_hand_is_busted or (total > dealer_hand_total):
            player.adjust_bankroll(amount=total_bet * 2)
            player_stats[(count, StatsCategory.PLAYER_HANDS_WON)] += 1
            player_stats[(count, StatsCategory.NET_WINNINGS)] += total_bet
        elif total == dealer_hand_total:
            player.adjust_bankroll(amount=total_bet)
            player_stats[(count, StatsCategory.PLAYER_HANDS_PUSHED)] += 1
        else:
            player_stats[(count, StatsCategory.PLAYER_HANDS_LOST)] += 1
            player_stats[(count, StatsCategory.NET_WINNINGS)] -= total_bet

        player_stats[(count, StatsCategory.TOTAL_HANDS_PLAYED)] += 1
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
    playing_strategy: PlayingStrategy,
    _logfile: Path = None
) -> None:
    """Plays a round of blackjack between a dealer and players at a table."""
    player_stats_dict = {}
    placed_bet_dict = {}
    count_dict = get_count(table=table, shoe=shoe)

    players_and_observers = table.players + table.observers
    for player in players_and_observers:
        count = count_dict.get(player, None)

        if isinstance(player, BackCounter) and count is not None:
            if player.is_seated:
                if player.can_exit(count=count):
                    table.remove_back_counter(back_counter=player)
                    continue
            else:
                if not player.can_enter(count=count):
                    continue

                table.add_back_counter(back_counter=player)
                placed_bet = player.placed_bet(count=count)
        else:
            placed_bet = player.placed_bet(count=count)
            if not player.has_sufficient_bankroll(amount=placed_bet):
                table.remove_player(player=player)
                continue

        player_stats = player.stats.stats
        player_stats[(count, StatsCategory.TOTAL_ROUNDS_PLAYED)] += 1
        player_stats_dict[player] = player_stats
        placed_bet_dict[player] = placed_bet

    players = table.players
    begining_bankroll_dict = {}
    if players:
        if _logfile:
            for player in players:
                begining_bankroll_dict[player] = player.bankroll

        initialize_hands(dealer=dealer, players=players, shoe=shoe)
        dealer_hand_is_blackjack = dealer.hand.is_blackjack
        dealer_up_card = dealer.up_card
        insurance_count_dict = get_insurance_count(players=players, shoe=shoe)

        for player in players:
            player_plays_hands(
                player=player,
                player_stats=player_stats_dict[player],
                placed_bet=placed_bet_dict[player],
                shoe=shoe,
                count=count_dict.get(player, None),
                insurance_count=insurance_count_dict.get(player, None),
                dealer_hand_is_blackjack=dealer_hand_is_blackjack,
                dealer_up_card=dealer_up_card,
                rules=rules,
                playing_strategy=playing_strategy
            )

        if dealer_turn(players=players):
            shoe.add_to_seen_cards(card=dealer.hole_card)
            dealer_plays_hand(shoe=shoe, dealer=dealer, s17=rules.s17)
            dealer_hand_is_busted = dealer.hand.is_busted
            dealer_hand_total = dealer.hand.total

            for player in players:
                compare_hands(
                    player=player,
                    player_stats=player_stats_dict[player],
                    count=count_dict.get(player, None),
                    dealer_hand_is_busted=dealer_hand_is_busted,
                    dealer_hand_total=dealer_hand_total
                )
        elif dealer_hand_is_blackjack or rules.dealer_shows_hole_card:
            shoe.add_to_seen_cards(card=dealer.hole_card)

        if _logfile:
            log_blackjack_round(
                blackjack_log_json=_logfile,
                shoe=shoe,
                players=players,
                dealer=dealer,
                dealer_hand_is_blackjack=dealer_hand_is_blackjack,
                count_dict=count_dict,
                insurance_count_dict=insurance_count_dict,
                placed_bet_dict=placed_bet_dict,
                begining_bankroll_dict=begining_bankroll_dict
            )        
        
        clear_hands(dealer=dealer, players=players)
