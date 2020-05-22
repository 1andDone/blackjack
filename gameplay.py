from helper import count_hand, max_count_hand


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
    for p in table.get_players():
        p.create_hand()  # added
        p.hit(key=1, new_card=cards.deal_card())  # dealing a card is effectively the same as hitting

    dealer_hand = [cards.deal_card(visible=False)]

    for p in table.get_players():
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
    dealer_total = max_count_hand(hand=dealer_hand)

    for p in table.get_players():

        player_total = max_count_hand(hand=p.get_hand(key=1))

        # insurance option
        if rules.insurance and dealer_up_card == 'A':
            if p.get_insurance_count() is not None:
                if p.get_count() >= p.get_insurance_count():
                    p.insurance()

        # dealer and players check for natural 21
        if player_total == 21 or dealer_total == 21:
            if player_total == 21:
                p.natural_blackjack()
            p.stand(key=1)
            continue

        # late surrender option
        # only available if dealer doesn't have natural 21
        if rules.late_surrender and dealer_total != 21:
            hand = p.get_hand(key=1)
            if p.decision(hand=hand, dealer_up_card=dealer_up_card, num_hands=1) in ['Rh', 'Rs', 'Rp']:
                p.surrender()
                continue

        processed = set()

        # plays out each hand before moving to next hand
        while True:
            keys = set(p.get_hands_dict()) - processed

            if not keys:
                break

            for k in keys:
                processed.add(k)

                while not p.get_stand(key=k):

                    num_hands = max(p.get_hands_dict().keys())
                    hand = p.get_hand(key=k)
                    hand_length = len(p.get_hand(key=k))
                    decision = p.decision(dealer_up_card=dealer_up_card, hand=hand, num_hands=num_hands)

                    # split cards
                    if decision in ['P', 'Rp']:

                        # if unable to re-split aces, player only gets 1 card on each split pair
                        if not rules.resplit_aces and 'A' in hand:
                            p.split(key=k, new_key=num_hands + 1)
                            p.hit(key=k, new_card=cards.deal_card())
                            p.stand(key=k)
                            p.hit(key=num_hands + 1, new_card=cards.deal_card())
                            p.stand(key=num_hands + 1)

                        else:
                            p.split(key=k, new_key=num_hands + 1)

                    # split cards if double after split available
                    elif rules.double_after_split and decision == 'Ph':
                        p.split(key=k, new_key=num_hands + 1)

                    # double down
                    elif rules.double_down and decision in ['Dh', 'Ds'] and \
                            hand_length == 2 and not p.get_split(key=k):
                        p.double_down(key=k, new_card=cards.deal_card())

                    # double after split
                    elif rules.double_after_split and decision in ['Dh', 'Ds'] and \
                            hand_length == 2 and p.get_split(key=k):
                        p.double_down(key=k, new_card=cards.deal_card())

                    # hit
                    elif decision in ['Rh', 'Dh', 'Ph', 'H']:
                        if hand_length == 1 and 'A' in hand:  # when aces are split, only allowed 1 card
                            p.hit(key=k, new_card=cards.deal_card())
                            if p.get_hand(key=k)[1] != 'A':  # check if split aces can be re-split again
                                p.stand(key=k)
                        else:
                            p.hit(key=k, new_card=cards.deal_card())

                    # stand
                    elif decision in ['Rs', 'Ds', 'S']:
                        p.stand(key=k)

                    # bust
                    elif decision == 'B':
                        p.busted(key=k)

                    else:
                        raise NotImplementedError('No implementation for flag.')


def dealer_turn(table):
    """
    Determines whether or not a dealer needs to take his turn. If any player at the table
    does not have a natural blackjack and does not surrender their hand or bust, the dealer
    will need to play out their turn in its entirety.

    Parameters
    ----------
    table : Table
        Table class instance

    Return
    ------
    bool
        True if any player at the table does not have a natural blackjack and does not
        surrender their hand or bust, false otherwise

    """
    completed_hands, total_hands = 0, 0

    for p in table.get_players():

        if p.get_natural_blackjack() or p.get_surrender():
            completed_hands += 1

        for k in p.get_hands_dict().keys():

            if p.get_busted(key=k):
                completed_hands += 1

            if p.get_stand(key=k):
                total_hands += 1

        if completed_hands < total_hands:
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
    while True:
        soft_total, hard_total = count_hand(hand=dealer_hand)

        if rules.s17:  # dealer must stay on soft 17 (ace counted as 11)

            if 17 <= soft_total <= 21 or hard_total >= 17:
                cards.update_visible_cards(dealer_hole_card)  # add hole card to visible card list
                return dealer_hand

            else:
                dealer_hand.append(cards.deal_card())

        else:  # dealer must hit on soft 17

            if 17 < soft_total <= 21 or hard_total >= 17:
                cards.update_visible_cards(dealer_hole_card)  # add hole card to visible card list
                return dealer_hand

            else:
                dealer_hand.append(cards.deal_card())


def compare_hands(table, rules, stats, dealer_hand):
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
    rules : HouseRules
        HouseRules class instance
    stats : SimulationStats
        SimulationStats class instance
    dealer_hand : list of str
        List of string card elements representing the dealer's hand

    """
    dealer_total = max_count_hand(hand=dealer_hand)
    dealer_hand_length = len(dealer_hand)

    for p in table.get_players():

        for k in p.get_hands_dict().keys():

            player_total = max_count_hand(hand=p.get_hand(key=k))

            if p.get_insurance():  # player took insurance side bet
                if dealer_total == 21 and dealer_hand_length == 2:  # dealer has natural 21
                    stats.insurance(
                        player_key=p.get_name(),
                        count_key=p.get_count(),
                        outcome_key='win'
                    )
                else:  # dealer does not have natural 21
                    stats.insurance(
                        player_key=p.get_name(),
                        count_key=p.get_count(),
                        outcome_key='loss'
                    )

            if p.get_surrender():  # player surrenders
                stats.surrender(
                    player_key=p.get_name(),
                    count_key=p.get_count()
                )

            elif player_total == 21 and dealer_total == 21:

                if p.get_natural_blackjack() and dealer_hand_length == 2:  # push - both dealer/player have natural 21
                    stats.other(
                        player_key=p.get_name(),
                        count_key=p.get_count(),
                        outcome_key='push'
                    )

                elif p.get_natural_blackjack() and dealer_hand_length > 2:  # player has natural 21
                    if len(table.get_players()) > 1:
                        stats.natural_blackjack(
                            player_key=p.get_name(),
                            count_key=p.get_count()
                        )
                    else:
                        raise ValueError('Impossible when playing heads up against dealer.')

                elif not p.get_natural_blackjack() and dealer_hand_length > 2:  # push - both dealer/player have 21
                    stats.other(
                        player_key=p.get_name(),
                        count_key=p.get_count(),
                        outcome_key='push'
                    )

                else:
                    raise ValueError('Impossible for a dealer to have a natural 21 and a player to have 3+ cards.')

            elif p.get_natural_blackjack():  # player has natural 21
                stats.natural_blackjack(
                    player_key=p.get_name(),
                    count_key=p.get_count()
                )

            elif dealer_total == 21 and dealer_hand_length == 2:  # dealer has natural 21
                stats.other(
                    player_key=p.get_name(),
                    count_key=p.get_count(),
                    outcome_key='loss',
                    hand_key=k,
                    double_down=p.get_double_down(key=k)
                )

            elif player_total > 21:  # player busts
                stats.other(
                    player_key=p.get_name(),
                    count_key=p.get_count(),
                    outcome_key='loss',
                    hand_key=k,
                    double_down=p.get_double_down(key=k)
                )

            elif dealer_total > 21:  # dealer busts
                stats.other(
                    player_key=p.get_name(),
                    count_key=p.get_count(),
                    outcome_key='win',
                    hand_key=k,
                    double_down=p.get_double_down(key=k)
                )

            elif dealer_total == player_total:  # push
                stats.other(
                    player_key=p.get_name(),
                    count_key=p.get_count(),
                    outcome_key='push',
                    hand_key=k,
                    double_down=p.get_double_down(key=k)
                )

            elif player_total > dealer_total:  # player beats dealer
                stats.other(
                    player_key=p.get_name(),
                    count_key=p.get_count(),
                    outcome_key='win',
                    hand_key=k,
                    double_down=p.get_double_down(key=k)
                )

            else:  # dealer beats player
                stats.other(
                    player_key=p.get_name(),
                    count_key=p.get_count(),
                    outcome_key='loss',
                    hand_key=k,
                    double_down=p.get_double_down(key=k)
                )
