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
        p.hit(key=1, new_card=cards.deal_card())

    dealer_hand = [cards.deal_card(visible=False)]

    for p in table.players:
        p.hit(key=1, new_card=cards.deal_card())

    dealer_hand.append(cards.deal_card())

    return dealer_hand


def players_play_hands(table, rules, cards, dealer_hand, dealer_up_card):
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
    dealer_hand : list of str
        List of string card elements representing the dealer's hand
    dealer_up_card : str
        Dealer's card that is face up after each player receives two cards

    """
    dealer_total, _ = count_hand(hand=dealer_hand)

    for p in table.players:

        hand = p.get_hand(key=1)
        player_total, soft_hand = count_hand(hand=hand)
        p.set_total(key=1, total=player_total)

        # insurance option
        if rules.insurance and dealer_up_card == 'A':
            if p.insurance_count is not None:
                if p.count >= p.insurance_count:
                    p.set_insurance()

        # players and dealer check for natural 21
        if player_total == 21 or dealer_total == 21:
            if player_total == 21:
                p.set_natural_blackjack()
            p.set_stand(key=1)
            continue

        # late surrender option
        # only available if dealer doesn't have natural 21
        if rules.late_surrender and dealer_total != 21:

            decision = p.decision(
                            rules=rules,
                            hand=p.get_hand(key=1),
                            num_hands=1,
                            dealer_up_card=dealer_up_card
            )

            if decision in ['Rh', 'Rs', 'Rp']:
                p.set_surrender()
                continue

        # determine hand type
        if splittable(rules=rules, hand=hand):
            p.set_hand_type(key=1, hand_type='pair')
        elif soft_hand:
            p.set_hand_type(key=1, hand_type='soft')
        else:
            p.set_hand_type(key=1, hand_type='hard')

        processed = set()

        # plays out each hand before moving onto next hand
        while True:
            keys = set(p.hands_dict) - processed

            if not keys:
                break

            for k in keys:
                processed.add(k)

                while not p.get_stand(key=k):

                    if len(p.get_hand(key=k)) == 1:  # always hit after splitting
                        p.hit(key=k, new_card=cards.deal_card())
                        # when aces are split, only allowed 1 card
                        if not rules.resplit_aces or (p.get_hand(key=k)[0] == 'A' and p.get_hand(key=k) != 'A') or \
                                max(p.hands_dict) >= rules.max_hands:
                            p.set_stand(key=k)

                    num_hands = max(p.hands_dict)
                    hand = p.get_hand(key=k)
                    hand_length = len(hand)

                    # player makes decision
                    decision = p.decision(
                                    rules=rules,
                                    hand=hand,
                                    num_hands=num_hands,
                                    dealer_up_card=dealer_up_card
                    )

                    # split cards
                    if decision in ['P', 'Rp']:

                        # if unable to re-split aces, player only gets 1 card on each split pair
                        if not rules.resplit_aces and 'A' in hand:
                            p.set_split(key=k, new_key=num_hands + 1)
                            p.hit(key=k, new_card=cards.deal_card())
                            p.set_stand(key=k)
                            p.hit(key=num_hands + 1, new_card=cards.deal_card())
                            p.set_stand(key=num_hands + 1)

                        else:
                            p.set_split(key=k, new_key=num_hands + 1)

                    # split cards if double after split available
                    elif rules.double_after_split and decision == 'Ph':
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

                    # bust
                    elif decision == 'B':
                        p.set_busted(key=k)

                    else:
                        raise NotImplementedError('No implementation for flag.')


def dealer_turn(table):
    """
    Determines whether or not a dealer needs to take their turn. If any player at the table
    does not have a natural blackjack and does not surrender their hand or bust, the dealer
    will need to play out their turn in its entirety.

    Parameters
    ----------
    table : Table
        Table class instance

    Return
    ------
    bool
        True if any player at the table has a live hand

    """
    for p in table.players:
        for k in p.hands_dict:
            if not any([p.get_natural_blackjack(), p.get_surrender(), p.get_busted(key=k)]):
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
    dealer_hand : list of str
        List of string card elements representing the dealer's hand

    Return
    ------
    list of str
        List of string card elements representing the dealer's final hand

    """
    total, soft_hand = count_hand(hand=dealer_hand)
    cards.update_visible_cards(card=dealer_hole_card)  # add hole card to visible card list

    if rules.s17:  # dealer must stay on soft 17 (ace counted as 11)

        while total < 17:
            dealer_hand.append(cards.deal_card())
            total, soft_hand = count_hand(hand=dealer_hand)

    else:  # dealer must hit on soft 17

        while total < 17 or (total == 17 and soft_hand):
            dealer_hand.append(cards.deal_card())
            total, soft_hand = count_hand(hand=dealer_hand)

    return dealer_hand


def compare_hands(table, stats, dealer_hand):
    """
    Players compare their hands against the dealer. If a player surrenders
    their hand, the player receives half of their initial wager back. If a
    player has a natural blackjack, the player is paid according to the blackjack
    payout for the table. All other instances where the player beats the dealer
    are paid out 1:1. Pushes allow the player to re-coup their initial wager.

    Parameters
    ----------
    table : Table
        Table class instance
    stats : SimulationStats
        SimulationStats class instance
    dealer_hand : list of str
        List of string card elements representing the dealer's hand

    """
    dealer_total, _ = count_hand(hand=dealer_hand)
    dealer_hand_length = len(dealer_hand)

    for p in table.players:

        for k in p.hands_dict:

            player_total, _ = count_hand(hand=p.get_hand(key=k))

            if p.get_insurance():  # player took insurance side bet
                if dealer_total == 21 and dealer_hand_length == 2:  # dealer has natural 21
                    stats.insurance(
                        player_key=p.name,
                        count_key=p.count,
                        outcome_key='win'
                    )
                else:  # dealer does not have natural 21
                    stats.insurance(
                        player_key=p.name,
                        count_key=p.count,
                        outcome_key='loss'
                    )

            if p.get_surrender():  # player surrenders
                stats.surrender(
                    player_key=p.name,
                    count_key=p.count
                )

            elif player_total == 21 and dealer_total == 21:

                if p.get_natural_blackjack() and dealer_hand_length > 2:  # player has natural 21, dealer has 21
                    stats.natural_blackjack(
                        player_key=p.name,
                        count_key=p.count
                    )

                else:  # player and dealer have natural 21 or 21
                    stats.other(
                        player_key=p.name,
                        count_key=p.count,
                        outcome_key='push'
                    )

            elif p.get_natural_blackjack():  # player has natural 21
                stats.natural_blackjack(
                    player_key=p.name,
                    count_key=p.count
                )

            elif dealer_total == 21 and dealer_hand_length == 2:  # dealer has natural 21
                stats.other(
                    player_key=p.name,
                    count_key=p.count,
                    outcome_key='loss'
                )

            elif player_total > 21:  # player busts
                stats.other(
                    player_key=p.name,
                    count_key=p.count,
                    outcome_key='loss',
                    hand_key=k,
                    double_down=p.get_double_down(key=k)
                )

            elif dealer_total > 21:  # dealer busts
                stats.other(
                    player_key=p.name,
                    count_key=p.count,
                    outcome_key='win',
                    hand_key=k,
                    double_down=p.get_double_down(key=k)
                )

            elif dealer_total == player_total:  # push
                stats.other(
                    player_key=p.name,
                    count_key=p.count,
                    outcome_key='push',
                    hand_key=k,
                    double_down=p.get_double_down(key=k)
                )

            elif player_total > dealer_total:  # player beats dealer
                stats.other(
                    player_key=p.name,
                    count_key=p.count,
                    outcome_key='win',
                    hand_key=k,
                    double_down=p.get_double_down(key=k)
                )

            else:  # dealer beats player
                stats.other(
                    player_key=p.name,
                    count_key=p.count,
                    outcome_key='loss',
                    hand_key=k,
                    double_down=p.get_double_down(key=k)
                )