from helper import count_hand, splittable, add_card_to_total


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
    for p in table.players:
        p.set_hand()
        p.hit(key=1, new_card=cards.deal_card())  # hitting is effectively the same thing as dealing

    dealer_hand = [cards.deal_card(seen=False)]

    for p in table.players:
        p.hit(key=1, new_card=cards.deal_card())

    dealer_hand.append(cards.deal_card())

    return dealer_hand


def players_play_hands(table, rules, cards, stats, dealer_hand, dealer_up_card):
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
    stats : SimulationStats
        SimulationStats class instance
    dealer_hand : list of int
        List of integer card elements representing the dealer's hand
    dealer_up_card : str
        Dealer's card that is face up after each player receives two cards

    """
    dealer_total, _ = count_hand(hand=dealer_hand)

    for p in table.players:

        # initial hand
        hand = p.get_hand(key=1)
        total, soft_hand = count_hand(hand=hand)

        # insurance option
        if rules.insurance and dealer_up_card == 1:
            if p.insurance is not None:
                if p.pre_insurance_count >= p.insurance_count:
                    p.set_insurance()
                    if dealer_total == 21:  # dealer has natural blackjack
                        stats.insurance(
                            player_key=p.name,
                            count_key=p.pre_insurance_count,
                            outcome_key='win'
                        )
                    else:  # dealer does not have natural blackjack
                        stats.insurance(
                            player_key=p.name,
                            count_key=p.pre_insurance_count,
                            outcome_key='loss'
                        )

        # players and dealer check for natural blackjack
        if total == 21 or dealer_total == 21:
            if total == 21 and dealer_total == 21:
                p.set_natural_blackjack()
                stats.other(
                    player_key=p.name,
                    count_key=p.bet_count,
                    outcome_key='push'
                )
            elif total == 21:
                p.set_natural_blackjack()
                stats.natural_blackjack(
                    player_key=p.name,
                    count_key=p.bet_count
                )
            else:
                stats.other(
                    player_key=p.name,
                    count_key=p.bet_count,
                    outcome_key='loss'
                )
            p.set_settled_natural_blackjack()  # settle all bets when dealer has natural blackjack
            continue

        # late surrender
        if rules.late_surrender:

            decision = p.decision(
                total=total,
                hand=hand,
                pair=splittable(rules=rules, hand=hand, num_hands=1),
                soft_hand=soft_hand,
                dealer_up_card=dealer_up_card
            )

            if decision in ['Rh', 'Rs', 'Rp']:
                p.set_surrender()
                stats.surrender(
                    player_key=p.name,
                    count_key=p.bet_count
                )
                continue

        first_decision = True
        processed = set()

        # plays out each hand before moving onto next hand
        while True:
            keys = set(p.hands_dict) - processed

            if not keys:
                break

            for k in keys:
                processed.add(k)

                while not p.get_stand(key=k):

                    if len(p.get_hand(key=k)) == 1:  # hands of length 1 are hands that have just been split
                        p.hit(key=k, new_card=cards.deal_card())  # always hit after splitting
                        if p.get_hand(key=k)[0] == 1:
                            if p.get_hand(key=k)[1] != 1:  # when aces are split, only allowed 1 card, unless...
                                p.set_stand(key=k)
                                continue
                            else:
                                if rules.resplit_aces:  # the rules allow a player to re-split aces once again
                                    if max(p.hands_dict) == rules.max_hands:  # must stand if split limit reached
                                        p.set_stand(key=k)
                                        continue
                                else:  # or if players are not allowed to re-split aces
                                    p.set_stand(key=k)
                                    continue

                    hand = p.get_hand(key=k)
                    hand_length = len(hand)

                    if rules.late_surrender and first_decision:  # no need to re-compute earlier decision made
                        num_hands = max(p.hands_dict)
                        first_decision = False

                    else:
                        if hand_length == 2:
                            num_hands = max(p.hands_dict)
                            pair = splittable(rules=rules, hand=hand, num_hands=num_hands)  # check for pair
                            if not pair:
                                total, soft_hand = count_hand(hand=hand)

                        else:
                            pair = False
                            total, soft_hand = count_hand(hand=hand)
                            if total > 21:  # player busts
                                p.set_busted(key=k)
                                stats.other(
                                    player_key=p.name,
                                    count_key=p.bet_count,
                                    outcome_key='loss',
                                    hand_key=k,
                                    double_down=p.get_double_down(key=k)
                                )
                                continue

                        # player makes decision
                        decision = p.decision(
                            total=total,
                            hand=hand,
                            pair=pair,
                            soft_hand=soft_hand,
                            dealer_up_card=dealer_up_card
                        )

                    # split cards
                    if decision in ['P', 'Rp'] or (rules.double_after_split and decision == 'Ph'):
                        p.set_split(key=k, new_key=num_hands + 1)

                    # double down
                    elif rules.double_down and decision in ['Dh', 'Ds'] and \
                            hand_length == 2 and not p.get_split(key=k):
                        p.set_double_down(key=k, new_card=cards.deal_card())

                    # double after split
                    elif rules.double_after_split and decision in ['Dh', 'Ds'] and \
                            hand_length == 2 and p.get_split(key=k):
                        p.set_double_down(key=k, new_card=cards.deal_card())

                    # hit
                    elif decision in ['Rh', 'Dh', 'Ph', 'H']:
                        p.hit(key=k, new_card=cards.deal_card())

                    # stand
                    elif decision in ['Rs', 'Ds', 'S']:
                        p.set_stand(key=k)

                    else:
                        raise NotImplementedError('No implementation for flag.')


def dealer_turn(table):
    """
    Determines whether or not a dealer needs to take their turn. If any player at the table
    does not have a natural blackjack and does not surrender their hand or bust, the dealer
    will need to play out their turn in its entirety, so long as the dealer does not have
    a natural blackjack.

    Parameters
    ----------
    table : Table
        Table class instance

    Return
    ------
    bool
        True if any player at the table has a live hand, so long as the dealer does not have
        a natural blackjack

    """
    for p in table.players:
        for k in p.hands_dict:
            if not p.get_settled_natural_blackjack() and not p.get_surrender() and not p.get_busted(key=k):
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
    dealer_hand : list of int
        List of integer card elements representing the dealer's hand

    Return
    ------
    int
        Maximum hard or soft total for the dealer's hand

    """
    total, soft_hand = count_hand(hand=dealer_hand)
    cards.add_to_seen_cards(card=dealer_hole_card)  # add hole card to seen card list

    if rules.s17:  # dealer must stay on soft 17 (ace counted as 11)

        while total < 17:
            card = cards.deal_card()
            dealer_hand.append(card)
            total, soft_hand = add_card_to_total(total=total, soft_hand=soft_hand, card=card)

    else:  # dealer must hit on soft 17

        while total < 17 or (total == 17 and soft_hand):
            card = cards.deal_card()
            dealer_hand.append(card)
            total, soft_hand = add_card_to_total(total=total, soft_hand=soft_hand, card=card)

    return total


def compare_hands(table, stats, dealer_total):
    """
    Players compare remaining hands against the dealer. Instances where the player
    beats the dealer are paid out 1:1. Pushes allow the player to re-coup their
    initial wager.

    Parameters
    ----------
    table : Table
        Table class instance
    stats : SimulationStats
        SimulationStats class instance
    dealer_total : int
        Dealer's soft or hard hand total

    """
    for p in table.players:

        for k in p.hands_dict:

            total, _ = count_hand(hand=p.get_hand(key=k))

            if p.get_settled_natural_blackjack() or p.get_surrender() or p.get_busted(key=k):
                continue

            elif dealer_total > 21 or (total > dealer_total):  # dealer busts or player beats dealer
                stats.other(
                    player_key=p.name,
                    count_key=p.bet_count,
                    outcome_key='win',
                    hand_key=k,
                    double_down=p.get_double_down(key=k)
                )

            elif total == dealer_total:  # push
                stats.other(
                    player_key=p.name,
                    count_key=p.bet_count,
                    outcome_key='push',
                    hand_key=k,
                    double_down=p.get_double_down(key=k)
                )

            else:  # dealer beats player
                stats.other(
                    player_key=p.name,
                    count_key=p.bet_count,
                    outcome_key='loss',
                    hand_key=k,
                    double_down=p.get_double_down(key=k)
                )
