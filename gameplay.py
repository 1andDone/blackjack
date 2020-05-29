from helper import count_hand, splittable


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


def players_play_hands(table, rules, cards, dealer_hand, dealer_up_card):
    """
    Players at the table play out their individual hands.

    Parameters
    ----------
    table : Table
        Table class instance
    rules : HouseRules
        HouseRules class instance
    cards : Cards
        Cards class instance
    dealer_hand : list of int
        List of integer card elements representing the dealer's hand
    dealer_up_card : int
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
                if p.pre_insurance_count >= p.insurance:
                    p.set_insurance()
                    if dealer_total == 21:  # dealer has natural blackjack
                        p.stats.update_results(
                            count_key=p.pre_insurance_count,
                            net_winnings=0.5,
                            overall_bet=0.5,
                            increment=0
                        )
                    else:  # dealer does not have natural blackjack
                        p.stats.update_results(
                            count_key=p.pre_insurance_count,
                            net_winnings=-0.5,
                            overall_bet=0.5,
                            increment=0
                        )

        # players and dealer check for natural blackjack
        if total == 21 or dealer_total == 21:
            if total == 21 and dealer_total == 21:  # push
                p.set_natural_blackjack()
                p.stats.update_results(
                    count_key=p.bet_count,
                    overall_bet=1
                )
            elif total == 21:  # player natural blackjack
                p.set_natural_blackjack()
                p.stats.update_results(
                    count_key=p.bet_count,
                    net_winnings=rules.blackjack_payout,
                    overall_bet=1
                )
            else:  # dealer natural blackjack
                p.stats.update_results(
                    count_key=p.bet_count,
                    net_winnings=-1,
                    overall_bet=1
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
                p.stats.update_results(
                    count_key=p.bet_count,
                    net_winnings=-0.5,
                    overall_bet=1
                )
                continue

        first_decision = True
        processed = set()
        num_hands = 1

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

                    if rules.late_surrender and first_decision:  # no need to re-compute earlier made decision
                        first_decision = False

                    else:
                        if splittable(rules=rules, hand=hand, num_hands=num_hands):  # check for pair
                            pair = True

                        else:
                            pair = False
                            total, soft_hand = count_hand(hand=hand)
                            if total > 21:  # player busts
                                p.set_busted(key=k)
                                p.stats.update_results(
                                    count_key=p.bet_count,
                                    hand_key=k,
                                    net_winnings=-2 if p.get_double_down(key=k) else -1,
                                    overall_bet=2 if p.get_double_down(key=k) else 1
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
                    if decision in ['P', 'Rp'] or (decision == 'Ph' and rules.double_after_split):
                        num_hands += 1
                        p.set_split(key=k, new_key=num_hands)

                    # double down or double after split
                    elif decision in ['Dh', 'Ds'] and hand_length == 2 and \
                            ((rules.double_down and not p.get_split(key=k)) or
                             (rules.double_after_split and p.get_split(key=k))):
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
    Determines whether or not a dealer needs to take their turn. If a player at the table
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
    dealer_hole_card : int
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
            dealer_hand.append(cards.deal_card())
            total, soft_hand = count_hand(hand=dealer_hand)

    else:  # dealer must hit on soft 17

        while total < 17 or (total == 17 and soft_hand):
            dealer_hand.append(cards.deal_card())
            total, soft_hand = count_hand(hand=dealer_hand)

    return total


def compare_hands(table, dealer_total):
    """
    Players compare remaining unsettled hands against the dealer.

    Parameters
    ----------
    table : Table
        Table class instance
    dealer_total : int
        Dealer's soft or hard hand total

    """
    for p in table.players:

        for k in p.hands_dict:

            total, _ = count_hand(hand=p.get_hand(key=k))

            if p.get_settled_natural_blackjack() or p.get_surrender() or p.get_busted(key=k):
                continue

            elif dealer_total > 21 or (total > dealer_total):  # dealer busts or player beats dealer
                p.stats.update_results(
                    count_key=p.bet_count,
                    hand_key=k,
                    net_winnings=2 if p.get_double_down(key=k) else 1,
                    overall_bet=2 if p.get_double_down(key=k) else 1
                )

            elif total == dealer_total:  # push
                p.stats.update_results(
                    count_key=p.bet_count,
                    hand_key=k,
                    overall_bet=2 if p.get_double_down(key=k) else 1
                )

            else:  # dealer beats player
                p.stats.update_results(
                    count_key=p.bet_count,
                    hand_key=k,
                    net_winnings=-2 if p.get_double_down(key=k) else -1,
                    overall_bet=2 if p.get_double_down(key=k) else 1
                )
